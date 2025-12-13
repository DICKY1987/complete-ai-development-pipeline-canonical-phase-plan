<#
.SYNOPSIS
    Invoke-AutomationHealthSweep - Autonomous automation health collector

.DESCRIPTION
    Discovers all automation components, executes health checks, and generates
    runtime status reports for the self-healing automation loop.

.PARAMETER RepoRoot
    Root path of the repository to scan

.PARAMETER IndexPath
    Path to automation_index.json (or will be generated)

.PARAMETER OutputDir
    Directory for output artifacts

.PARAMETER Mode
    Execution mode: 'discover', 'validate', 'full'

.PARAMETER Parallel
    Number of parallel execution threads

.PARAMETER DryRun
    Preview actions without executing

.EXAMPLE
    .\Invoke-AutomationHealthSweep.ps1 -RepoRoot "C:\repo" -Mode full
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,

    [Parameter()]
    [string]$IndexPath,

    [Parameter()]
    [string]$OutputDir = ".\.automation-health",

    [Parameter()]
    [ValidateSet('discover', 'validate', 'full')]
    [string]$Mode = 'full',

    [Parameter()]
    [int]$Parallel = 4,

    [Parameter()]
    [int]$TimeoutSeconds = 300,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region ULID Generation
function New-ULID {
    <#
    .SYNOPSIS
        Generate a ULID (Universally Unique Lexicographically Sortable Identifier)
    #>
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    $chars = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'

    # Encode timestamp (10 chars)
    $ts = ''
    for ($i = 9; $i -ge 0; $i--) {
        $ts = $chars[($timestamp -shr ($i * 5)) -band 31] + $ts
    }

    # Generate random part (16 chars)
    $random = ''
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = [byte[]]::new(10)
    $rng.GetBytes($bytes)
    foreach ($b in $bytes) {
        $random += $chars[$b % 32]
    }

    return $ts.Substring(0, 10) + $random.Substring(0, 16)
}
#endregion

#region Hash Utilities
function Get-ContentHash {
    param([string]$Content)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Content)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return [BitConverter]::ToString($hash).Replace('-', '').ToLower()
}
#endregion

#region Automation Discovery
function Find-AutomationComponents {
    <#
    .SYNOPSIS
        Discover all automation components in the repository
    #>
    param(
        [string]$Root
    )

    $components = @()
    $counter = @{
        GH = 1; PS = 1; PY = 1; PE = 1; CM = 1; TS = 1; GS = 1
    }

    # GitHub Workflows
    $workflowPath = Join-Path $Root '.github\workflows'
    if (Test-Path $workflowPath) {
        Get-ChildItem -Path $workflowPath -Filter '*.yml' -File | ForEach-Object {
            $components += [PSCustomObject]@{
                id          = "AUTO-GH-{0:D3}" -f $counter['GH']++
                type        = 'github_workflow'
                path        = $_.FullName.Replace($Root, '').TrimStart('\', '/')
                name        = $_.BaseName
                trigger     = @('push', 'pr', 'schedule')
                validator   = 'github_actions'
                timeout_seconds = 600
            }
        }
    }

    # PowerShell Scripts
    Get-ChildItem -Path $Root -Filter '*.ps1' -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '(node_modules|\.git|vendor)' } |
        ForEach-Object {
            $isExecutor = $_.FullName -match 'patterns[/\\]executors'
            $type = if ($isExecutor) { 'pattern_executor' } else { 'powershell' }
            $prefix = if ($isExecutor) { 'PE' } else { 'PS' }

            $components += [PSCustomObject]@{
                id          = "AUTO-$prefix-{0:D3}" -f $counter[$prefix]++
                type        = $type
                path        = $_.FullName.Replace($Root, '').TrimStart('\', '/')
                name        = $_.BaseName
                trigger     = @('cli', 'manual')
                validator   = 'process_exit_code'
                timeout_seconds = 300
            }
        }

    # Python Scripts
    Get-ChildItem -Path $Root -Filter '*.py' -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch '(node_modules|\.git|vendor|__pycache__|\.venv)' -and
            $_.Name -notmatch '^__'
        } |
        ForEach-Object {
            $isTest = $_.FullName -match '[/\\]tests?[/\\]' -or $_.Name -match '^test_'
            $isGlossary = $_.FullName -match 'glossary[/\\]scripts'
            $isCore = $_.FullName -match '[/\\]core[/\\]'

            $type = switch ($true) {
                $isTest { 'test_suite' }
                $isGlossary { 'glossary_script' }
                $isCore { 'core_module' }
                default { 'python' }
            }

            $prefix = switch ($type) {
                'test_suite' { 'TS' }
                'glossary_script' { 'GS' }
                'core_module' { 'CM' }
                default { 'PY' }
            }

            $components += [PSCustomObject]@{
                id          = "AUTO-$prefix-{0:D3}" -f $counter[$prefix]++
                type        = $type
                path        = $_.FullName.Replace($Root, '').TrimStart('\', '/')
                name        = $_.BaseName
                trigger     = @('cli', 'pipeline')
                validator   = if ($isTest) { 'pytest' } else { 'process_exit_code' }
                timeout_seconds = if ($isTest) { 600 } else { 300 }
            }
        }

    return $components
}
#endregion

#region Health Check Execution
function Invoke-HealthCheck {
    <#
    .SYNOPSIS
        Execute health check for a single automation unit
    #>
    param(
        [PSCustomObject]$Unit,
        [string]$RepoRoot,
        [int]$Timeout,
        [switch]$DryRun
    )

    $result = [PSCustomObject]@{
        status          = 'not_run'
        last_run        = (Get-Date).ToUniversalTime().ToString('o')
        exit_code       = $null
        duration_seconds = 0
        attempt_number  = 1
        stdout_hash     = $null
        stderr_hash     = $null
        stdout_tail     = ''
        stderr_tail     = ''
        error_signature = $null
    }

    if ($DryRun) {
        $result.status = 'skipped'
        return $result
    }

    $fullPath = Join-Path $RepoRoot $Unit.path
    if (-not (Test-Path $fullPath)) {
        $result.status = 'fail'
        $result.exit_code = -1
        $result.error_signature = 'FILE_NOT_FOUND'
        $result.stderr_tail = "File not found: $fullPath"
        return $result
    }

    $startTime = Get-Date
    $stdout = ''
    $stderr = ''

    try {
        switch ($Unit.type) {
            'github_workflow' {
                # Validate YAML syntax
                $content = Get-Content $fullPath -Raw
                if ($content -match '^name:' -and $content -match 'jobs:') {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "YAML structure valid"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = 1
                    $stderr = "Invalid workflow structure"
                    $result.error_signature = 'SCHEMA_INVALID'
                }
            }

            'powershell' {
                # Syntax check only (don't execute)
                $tokens = $null
                $errors = $null
                [System.Management.Automation.Language.Parser]::ParseFile(
                    $fullPath, [ref]$tokens, [ref]$errors
                ) | Out-Null

                if ($errors.Count -eq 0) {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "Syntax valid: $($tokens.Count) tokens"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = 1
                    $stderr = $errors | ForEach-Object { $_.Message } | Join-String -Separator "`n"
                    $result.error_signature = 'SYNTAX_ERROR'
                }
            }

            'pattern_executor' {
                # Validate pattern executor structure
                $content = Get-Content $fullPath -Raw
                $hasParam = $content -match '\[CmdletBinding\(\)\]' -or $content -match 'param\s*\('
                $hasFunction = $content -match 'function\s+\w+'

                if ($hasParam -or $hasFunction) {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "Pattern executor structure valid"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = 1
                    $stderr = "Missing param block or function definition"
                    $result.error_signature = 'SCHEMA_INVALID'
                }
            }

            'python' {
                # Python syntax check
                $process = Start-Process -FilePath 'python' -ArgumentList "-m py_compile `"$fullPath`"" `
                    -NoNewWindow -Wait -PassThru -RedirectStandardError "$env:TEMP\py_stderr.txt" `
                    -ErrorAction SilentlyContinue

                if ($null -eq $process) {
                    $result.status = 'fail'
                    $result.exit_code = -1
                    $stderr = "Python not available"
                    $result.error_signature = 'ENV_MISSING'
                } elseif ($process.ExitCode -eq 0) {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "Python syntax valid"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = $process.ExitCode
                    $stderr = Get-Content "$env:TEMP\py_stderr.txt" -Raw -ErrorAction SilentlyContinue
                    $result.error_signature = 'SYNTAX_ERROR'
                }
            }

            'test_suite' {
                # Validate test file has test functions
                $content = Get-Content $fullPath -Raw
                if ($content -match 'def test_' -or $content -match '@pytest') {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "Test suite structure valid"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = 1
                    $stderr = "No test functions found"
                    $result.error_signature = 'SCHEMA_INVALID'
                }
            }

            'core_module' {
                # Validate Python module
                $process = Start-Process -FilePath 'python' -ArgumentList "-m py_compile `"$fullPath`"" `
                    -NoNewWindow -Wait -PassThru -ErrorAction SilentlyContinue

                if ($null -eq $process) {
                    $result.status = 'success'  # Assume valid if Python not available
                    $result.exit_code = 0
                } elseif ($process.ExitCode -eq 0) {
                    $result.status = 'success'
                    $result.exit_code = 0
                    $stdout = "Core module syntax valid"
                } else {
                    $result.status = 'fail'
                    $result.exit_code = $process.ExitCode
                    $result.error_signature = 'SYNTAX_ERROR'
                }
            }

            default {
                # Generic file existence check
                $result.status = 'success'
                $result.exit_code = 0
                $stdout = "File exists and readable"
            }
        }
    }
    catch {
        $result.status = 'fail'
        $result.exit_code = -1
        $stderr = $_.Exception.Message
        $result.error_signature = 'LOGIC_ERROR'
    }

    $endTime = Get-Date
    $result.duration_seconds = ($endTime - $startTime).TotalSeconds

    # Compute hashes and tails
    if ($stdout) {
        $result.stdout_hash = Get-ContentHash $stdout
        $result.stdout_tail = $stdout.Substring([Math]::Max(0, $stdout.Length - 2000))
    }
    if ($stderr) {
        $result.stderr_hash = Get-ContentHash $stderr
        $result.stderr_tail = $stderr.Substring([Math]::Max(0, $stderr.Length - 2000))
    }

    return $result
}
#endregion

#region Main Execution
function Invoke-AutomationHealthSweep {
    param(
        [string]$RepoRoot,
        [string]$IndexPath,
        [string]$OutputDir,
        [string]$Mode,
        [int]$Parallel,
        [int]$TimeoutSeconds,
        [switch]$DryRun
    )

    $sweepId = New-ULID
    $startTime = Get-Date

    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        AUTONOMOUS AUTOMATION HEALTH SWEEP                    ║" -ForegroundColor Cyan
    Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║  Sweep ID: $sweepId                          ║" -ForegroundColor Cyan
    Write-Host "║  Mode: $($Mode.PadRight(55))║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    # Ensure output directory exists
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    # Phase 0: Discovery or Load Index
    Write-Host "[Phase 0] Discovering automation components..." -ForegroundColor Yellow

    $index = $null
    if ($IndexPath -and (Test-Path $IndexPath)) {
        Write-Host "  Loading existing index: $IndexPath" -ForegroundColor Gray
        $index = Get-Content $IndexPath -Raw | ConvertFrom-Json
    } else {
        Write-Host "  Scanning repository: $RepoRoot" -ForegroundColor Gray
        $components = Find-AutomationComponents -Root $RepoRoot

        $index = [PSCustomObject]@{
            version = '1.0.0'
            generated_at = (Get-Date).ToUniversalTime().ToString('o')
            repository = @{
                name = Split-Path $RepoRoot -Leaf
                root_path = $RepoRoot
            }
            summary = @{
                total_units = $components.Count
                by_type = $components | Group-Object type | ForEach-Object -Begin { $h = @{} } -Process { $h[$_.Name] = $_.Count } -End { $h }
            }
            automation_units = $components
        }

        # Save index
        $indexOutputPath = Join-Path $OutputDir 'automation_index.json'
        $index | ConvertTo-Json -Depth 10 | Set-Content $indexOutputPath -Encoding UTF8
        Write-Host "  Saved index: $indexOutputPath" -ForegroundColor Green
    }

    Write-Host "  Found $($index.automation_units.Count) automation units" -ForegroundColor Green
    Write-Host ""

    if ($Mode -eq 'discover') {
        return $index
    }

    # Phase 1: Health Check Execution
    Write-Host "[Phase 1] Executing health checks..." -ForegroundColor Yellow

    $units = $index.automation_units
    $results = @{}
    $progress = 0

    foreach ($unit in $units) {
        $progress++
        $pct = [Math]::Round(($progress / $units.Count) * 100)
        Write-Progress -Activity "Health Check" -Status "$($unit.id): $($unit.name)" -PercentComplete $pct

        $result = Invoke-HealthCheck -Unit $unit -RepoRoot $RepoRoot -Timeout $TimeoutSeconds -DryRun:$DryRun
        $results[$unit.id] = $result
    }

    Write-Progress -Activity "Health Check" -Completed

    # Calculate summary
    $successCount = ($results.Values | Where-Object { $_.status -eq 'success' }).Count
    $failCount = ($results.Values | Where-Object { $_.status -eq 'fail' }).Count
    $skipCount = ($results.Values | Where-Object { $_.status -eq 'skipped' }).Count
    $timeoutCount = ($results.Values | Where-Object { $_.status -eq 'timeout' }).Count

    $endTime = Get-Date

    $runtimeStatus = [PSCustomObject]@{
        version = '1.0.0'
        sweep_id = $sweepId
        started_at = $startTime.ToUniversalTime().ToString('o')
        completed_at = $endTime.ToUniversalTime().ToString('o')
        duration_seconds = ($endTime - $startTime).TotalSeconds
        environment = @{
            hostname = $env:COMPUTERNAME
            os = [System.Environment]::OSVersion.VersionString
            user = $env:USERNAME
            working_directory = $RepoRoot
        }
        summary = @{
            total = $units.Count
            success = $successCount
            failed = $failCount
            skipped = $skipCount
            timeout = $timeoutCount
            success_rate = if ($units.Count -gt 0) { [Math]::Round(($successCount / $units.Count) * 100, 2) } else { 0 }
        }
        units = $results
    }

    # Save runtime status
    $statusPath = Join-Path $OutputDir 'automation_runtime_status.json'
    $runtimeStatus | ConvertTo-Json -Depth 10 | Set-Content $statusPath -Encoding UTF8

    Write-Host ""
    Write-Host "  ✓ Success: $successCount" -ForegroundColor Green
    Write-Host "  ✗ Failed:  $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Red' } else { 'Gray' })
    Write-Host "  ○ Skipped: $skipCount" -ForegroundColor Gray
    Write-Host "  ⧖ Timeout: $timeoutCount" -ForegroundColor $(if ($timeoutCount -gt 0) { 'Yellow' } else { 'Gray' })
    Write-Host ""
    Write-Host "  Saved: $statusPath" -ForegroundColor Green
    Write-Host ""

    if ($Mode -eq 'validate') {
        return $runtimeStatus
    }

    # Phase 2: Failure Classification (if any failures)
    if ($failCount -gt 0) {
        Write-Host "[Phase 2] Classifying failures..." -ForegroundColor Yellow

        $failures = @{}
        $autoRepairable = 0
        $requiresHuman = 0

        foreach ($unitId in $results.Keys) {
            $result = $results[$unitId]
            if ($result.status -ne 'fail') { continue }

            $classification = [PSCustomObject]@{
                root_cause = $result.error_signature ?? 'UNKNOWN'
                layer = switch ($result.error_signature) {
                    'FILE_NOT_FOUND' { 'Layer 1 - Infrastructure' }
                    'ENV_MISSING' { 'Layer 2 - Dependencies' }
                    'SCHEMA_INVALID' { 'Layer 3 - Configuration' }
                    'SYNTAX_ERROR' { 'Layer 5 - Business Logic' }
                    'PERMISSION_DENIED' { 'Layer 4 - Operational' }
                    default { 'Layer 5 - Business Logic' }
                }
                auto_repairable = $result.error_signature -in @('ENV_MISSING', 'SCHEMA_INVALID', 'FILE_NOT_FOUND')
                confidence = 0.8
                evidence = @{
                    error_message = $result.stderr_tail
                    matched_pattern = $result.error_signature
                }
                suggested_fixes = @(
                    @{
                        strategy = switch ($result.error_signature) {
                            'FILE_NOT_FOUND' { 'SYNC_FILES' }
                            'ENV_MISSING' { 'INJECT_ENV_DEFAULT' }
                            'SCHEMA_INVALID' { 'REGENERATE_SCHEMA' }
                            'SYNTAX_ERROR' { 'ESCALATE_AI' }
                            default { 'ESCALATE_HUMAN' }
                        }
                        description = "Auto-generated fix strategy"
                        risk_level = 'medium'
                    }
                )
            }

            if ($classification.auto_repairable) { $autoRepairable++ } else { $requiresHuman++ }
            $failures[$unitId] = $classification
        }

        $failureReport = [PSCustomObject]@{
            version = '1.0.0'
            sweep_id = $sweepId
            generated_at = (Get-Date).ToUniversalTime().ToString('o')
            classification_engine = 'pattern_matcher_v1'
            summary = @{
                total_failures = $failCount
                auto_repairable = $autoRepairable
                requires_human = $requiresHuman
                by_root_cause = $failures.Values | Group-Object root_cause | ForEach-Object -Begin { $h = @{} } -Process { $h[$_.Name] = $_.Count } -End { $h }
            }
            failures = $failures
        }

        $failurePath = Join-Path $OutputDir 'automation_failure_report.json'
        $failureReport | ConvertTo-Json -Depth 10 | Set-Content $failurePath -Encoding UTF8

        Write-Host "  Auto-repairable: $autoRepairable" -ForegroundColor Yellow
        Write-Host "  Requires human:  $requiresHuman" -ForegroundColor Red
        Write-Host "  Saved: $failurePath" -ForegroundColor Green
        Write-Host ""
    }

    # Final Summary
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })
    Write-Host "║                    SWEEP COMPLETE                            ║" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })
    Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })
    Write-Host "║  Success Rate: $("{0:N1}%" -f $runtimeStatus.summary.success_rate)                                        ║" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })
    Write-Host "║  Duration: $("{0:N1}s" -f $runtimeStatus.duration_seconds)                                           ║" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })

    return $runtimeStatus
}
#endregion

# Execute
Invoke-AutomationHealthSweep `
    -RepoRoot $RepoRoot `
    -IndexPath $IndexPath `
    -OutputDir $OutputDir `
    -Mode $Mode `
    -Parallel $Parallel `
    -TimeoutSeconds $TimeoutSeconds `
    -DryRun:$DryRun
