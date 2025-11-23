#Requires -Version 5.1
<#
.SYNOPSIS
    Auto-remediation engine that fixes validation failures automatically.

.DESCRIPTION
    This script analyzes validation failures and attempts to fix them automatically.
    It reads validation results, dispatches fix actions based on requirement type,
    logs all fixes to audit trail, and updates state.

.PARAMETER ValidationResultsJson
    Path to JSON file containing validation results. If not provided, runs validator first.

.PARAMETER DryRun
    Show what would be fixed without making changes.

.PARAMETER Interactive
    Prompt for confirmation before each fix.

.PARAMETER RequirementFilter
    Only attempt to fix specific requirement IDs (comma-separated).

.EXAMPLE
    .\auto_remediate.ps1
    Run validator and auto-fix all failures.

.EXAMPLE
    .\auto_remediate.ps1 -DryRun
    Show what would be fixed without making changes.

.EXAMPLE
    .\auto_remediate.ps1 -Interactive
    Prompt before each fix.

.EXAMPLE
    .\auto_remediate.ps1 -RequirementFilter "WS-BUNDLE-001,TEST-PYTEST-001"
    Only fix specific requirements.
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ValidationResultsJson,
    
    [Parameter()]
    [switch]$DryRun,
    
    [Parameter()]
    [switch]$Interactive,
    
    [Parameter()]
    [string]$RequirementFilter
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName

# ============================================================================
# REMEDIATION ACTIONS
# ============================================================================

function Fix-WorkstreamBundle {
    <#
    .SYNOPSIS
        Fix workstream bundle schema issues.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$RepoRoot,
        
        [Parameter()]
        [switch]$DryRun
    )
    
    Write-Host "  🔧 Analyzing workstream bundles..." -ForegroundColor Yellow
    
    # Find workstream bundles with schema issues
    $workstreamsDir = Join-Path $RepoRoot "workstreams"
    if (-not (Test-Path $workstreamsDir)) {
        return @{
            Success = $false
            Message = "Workstreams directory not found"
        }
    }
    
    $bundleFiles = Get-ChildItem -Path $workstreamsDir -Filter "*.json" -File
    $issues = @()
    $fixes = @()
    
    foreach ($file in $bundleFiles) {
        try {
            $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
            
            # Check for old schema fields that need migration
            $oldFields = @('bundle_id', 'bundle_name', 'estimated_duration_hours', 'validation', 'version')
            $hasOldFields = $false
            
            foreach ($field in $oldFields) {
                if ($content.PSObject.Properties.Name -contains $field) {
                    $hasOldFields = $true
                    break
                }
            }
            
            if ($hasOldFields) {
                $issues += "Old schema in $($file.Name)"
                
                if (-not $DryRun) {
                    # Create backup
                    $backupPath = "$($file.FullName).backup"
                    Copy-Item $file.FullName $backupPath
                    
                    # Migrate to new schema (preserve essential fields)
                    $newContent = @{
                        workstream_id = if ($content.bundle_id) { $content.bundle_id } else { $content.workstream_id }
                        name = if ($content.bundle_name) { $content.bundle_name } else { $content.name }
                        description = $content.description
                        phase = $content.phase
                        tasks = $content.tasks
                        dependencies = $content.dependencies
                        file_scope = $content.file_scope
                    }
                    
                    # Write migrated content
                    $newContent | ConvertTo-Json -Depth 10 | Set-Content $file.FullName
                    
                    $fixes += "Migrated $($file.Name) to new schema (backup: $backupPath)"
                }
                else {
                    $fixes += "[DRY RUN] Would migrate $($file.Name) to new schema"
                }
            }
        }
        catch {
            $issues += "Error reading $($file.Name): $($_.Exception.Message)"
        }
    }
    
    if ($issues.Count -eq 0) {
        return @{
            Success = $true
            Message = "No workstream schema issues found"
            Fixes = @()
        }
    }
    
    return @{
        Success = $fixes.Count -gt 0
        Message = "$($issues.Count) schema issues found, $($fixes.Count) fixes applied"
        Fixes = $fixes
        Issues = $issues
    }
}

function Fix-PytestImports {
    <#
    .SYNOPSIS
        Fix pytest import conflicts (tests/ast conflicts with stdlib).
    #>
    param(
        [Parameter(Mandatory)]
        [string]$RepoRoot,
        
        [Parameter()]
        [switch]$DryRun
    )
    
    Write-Host "  🔧 Analyzing pytest import conflicts..." -ForegroundColor Yellow
    
    $testsAstPath = Join-Path $RepoRoot "tests\ast"
    
    if (-not (Test-Path $testsAstPath)) {
        return @{
            Success = $true
            Message = "tests/ast directory not found (already fixed or doesn't exist)"
            Fixes = @()
        }
    }
    
    $newPath = Join-Path $RepoRoot "tests\syntax_analysis"
    
    if (-not $DryRun) {
        # Rename directory
        Move-Item -Path $testsAstPath -Destination $newPath
        
        # Update any references in test files
        $testFiles = Get-ChildItem -Path $newPath -Filter "*.py" -Recurse
        foreach ($file in $testFiles) {
            $content = Get-Content $file.FullName -Raw
            $updated = $content -replace 'tests\.ast\.', 'tests.syntax_analysis.'
            
            if ($content -ne $updated) {
                Set-Content -Path $file.FullName -Value $updated
            }
        }
        
        return @{
            Success = $true
            Message = "Renamed tests/ast to tests/syntax_analysis to avoid stdlib conflict"
            Fixes = @(
                "Renamed directory: tests\ast → tests\syntax_analysis"
                "Updated imports in test files"
            )
        }
    }
    else {
        return @{
            Success = $true
            Message = "[DRY RUN] Would rename tests/ast to tests/syntax_analysis"
            Fixes = @(
                "[DRY RUN] Would rename directory: tests\ast → tests\syntax_analysis"
                "[DRY RUN] Would update imports in test files"
            )
        }
    }
}

function Fix-MissingFiles {
    <#
    .SYNOPSIS
        Create missing required files with default content.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$RepoRoot,
        
        [Parameter(Mandatory)]
        [array]$MissingFiles,
        
        [Parameter()]
        [switch]$DryRun
    )
    
    Write-Host "  🔧 Creating missing required files..." -ForegroundColor Yellow
    
    $fixes = @()
    
    foreach ($filePath in $MissingFiles) {
        $fullPath = Join-Path $RepoRoot $filePath
        $directory = Split-Path $fullPath -Parent
        
        if (-not $DryRun) {
            # Ensure directory exists
            if (-not (Test-Path $directory)) {
                New-Item -ItemType Directory -Path $directory -Force | Out-Null
            }
            
            # Create file with appropriate default content
            $defaultContent = "# $filePath`n`nCreated by auto-remediation: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
            
            Set-Content -Path $fullPath -Value $defaultContent
            $fixes += "Created: $filePath"
        }
        else {
            $fixes += "[DRY RUN] Would create: $filePath"
        }
    }
    
    return @{
        Success = $true
        Message = "Created $($fixes.Count) missing files"
        Fixes = $fixes
    }
}

# ============================================================================
# MAIN REMEDIATION ENGINE
# ============================================================================

function Invoke-AutoRemediation {
    param(
        [Parameter(Mandatory)]
        [array]$FailedRequirements,
        
        [Parameter(Mandatory)]
        [string]$RepoRoot,
        
        [Parameter()]
        [switch]$DryRun,
        
        [Parameter()]
        [switch]$Interactive
    )
    
    $results = @()
    
    foreach ($requirement in $FailedRequirements) {
        Write-Host "`n🔍 Analyzing: [$($requirement.requirement_id)] $($requirement.message)" -ForegroundColor Cyan
        
        # Dispatch to appropriate fix function
        $fixResult = $null
        
        switch ($requirement.requirement_id) {
            "WS-BUNDLE-001" {
                if ($Interactive) {
                    $response = Read-Host "  Fix workstream bundle schema issues? (y/n)"
                    if ($response -ne 'y') {
                        Write-Host "  ⏭️  Skipped by user" -ForegroundColor Yellow
                        continue
                    }
                }
                $fixResult = Fix-WorkstreamBundle -RepoRoot $RepoRoot -DryRun:$DryRun
            }
            
            "TEST-PYTEST-001" {
                if ($Interactive) {
                    $response = Read-Host "  Fix pytest import conflicts? (y/n)"
                    if ($response -ne 'y') {
                        Write-Host "  ⏭️  Skipped by user" -ForegroundColor Yellow
                        continue
                    }
                }
                $fixResult = Fix-PytestImports -RepoRoot $RepoRoot -DryRun:$DryRun
            }
            
            default {
                Write-Host "  ⚠️  No auto-fix available for this requirement" -ForegroundColor Yellow
                $fixResult = @{
                    Success = $false
                    Message = "No auto-fix implemented"
                    Fixes = @()
                }
            }
        }
        
        if ($fixResult) {
            $resultObj = [PSCustomObject]@{
                RequirementId = $requirement.requirement_id
                Success = $fixResult.Success
                Message = $fixResult.Message
                Fixes = if ($fixResult.Fixes) { $fixResult.Fixes } else { @() }
            }
            
            if ($fixResult.PSObject.Properties.Name -contains 'Issues') {
                $resultObj | Add-Member -MemberType NoteProperty -Name Issues -Value $fixResult.Issues
            }
            
            $results += $resultObj
            
            if ($fixResult.Success -and $fixResult.Fixes.Count -gt 0) {
                Write-Host "  ✅ Fix applied:" -ForegroundColor Green
                foreach ($fix in $fixResult.Fixes) {
                    Write-Host "    • $fix" -ForegroundColor Gray
                }
            }
            elseif ($fixResult.Success) {
                Write-Host "  ℹ️  $($fixResult.Message)" -ForegroundColor Cyan
            }
            else {
                Write-Host "  ❌ Fix failed: $($fixResult.Message)" -ForegroundColor Red
            }
        }
    }
    
    return $results
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              AUTO-REMEDIATION ENGINE                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    if ($DryRun) {
        Write-Host "🔍 DRY RUN MODE - No changes will be made`n" -ForegroundColor Yellow
    }
    
    # Step 1: Get validation results
    if (-not $ValidationResultsJson) {
        Write-Host "📊 Running validator to get current failures...`n" -ForegroundColor Cyan
        
        $validatorPath = Join-Path $repoRoot "scripts\validate\validate_repo_checklist.ps1"
        $tempResults = Join-Path $env:TEMP "validation_results.json"
        
        & $validatorPath -JsonOutput | Out-File -FilePath $tempResults -Encoding UTF8
        $ValidationResultsJson = $tempResults
    }
    
    # Step 2: Parse validation results
    $validationData = Get-Content $ValidationResultsJson -Raw | ConvertFrom-Json
    
    $failedRequirements = $validationData.results | Where-Object { $_.status -eq "FAIL" }
    
    if ($RequirementFilter) {
        $filterIds = $RequirementFilter -split ','
        $failedRequirements = $failedRequirements | Where-Object { $filterIds -contains $_.requirement_id }
    }
    
    if ($failedRequirements.Count -eq 0) {
        Write-Host "✅ No failures to remediate!`n" -ForegroundColor Green
        exit 0
    }
    
    Write-Host "Found $($failedRequirements.Count) failed requirement(s):`n" -ForegroundColor Yellow
    foreach ($req in $failedRequirements) {
        Write-Host "  ❌ [$($req.requirement_id)] $($req.message)" -ForegroundColor Red
    }
    
    # Step 3: Attempt remediation
    Write-Host "`n🔧 Starting auto-remediation...`n" -ForegroundColor Cyan
    
    $remediationResults = Invoke-AutoRemediation `
        -FailedRequirements $failedRequirements `
        -RepoRoot $repoRoot `
        -DryRun:$DryRun `
        -Interactive:$Interactive
    
    # Step 4: Log to audit trail
    if (-not $DryRun -and $remediationResults.Count -gt 0) {
        $timestamp = (Get-Date).ToUniversalTime().ToString("o")
        
        $successfulFixes = $remediationResults | Where-Object { $_.Success -and $_.Fixes.Count -gt 0 }
        
        if ($successfulFixes.Count -gt 0) {
            $transition = @{
                transition_id = "TRANS-REMED-$(Get-Date -Format 'yyyyMMddHHmmss')"
                from_state = "STATE-VALIDATED-001"
                to_state = "STATE-REMEDIATED-001"
                timestamp = $timestamp
                trigger = "auto_remediation"
                actor = "auto_remediation_engine"
                metadata = @{
                    reason = "Auto-fixed validation failures"
                    fixes_applied = $successfulFixes.Count
                    requirements_fixed = @($successfulFixes | ForEach-Object { $_.RequirementId })
                }
            } | ConvertTo-Json -Compress
            
            $transitionsFile = Join-Path $repoRoot ".state\transitions.jsonl"
            Add-Content -Path $transitionsFile -Value $transition
            
            Write-Host "`n✅ Logged remediation to audit trail" -ForegroundColor Green
        }
    }
    
    # Step 5: Summary
    Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
    Write-Host "REMEDIATION SUMMARY" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
    
    $successful = @($remediationResults | Where-Object { $_.Success -and $_.Fixes.Count -gt 0 })
    $failed = @($remediationResults | Where-Object { -not $_.Success })
    $skipped = @($remediationResults | Where-Object { $_.Success -and $_.Fixes.Count -eq 0 })
    
    Write-Host "Total Requirements: $($remediationResults.Count)" -ForegroundColor White
    Write-Host "✓ Fixed:   $($successful.Count)" -ForegroundColor Green
    Write-Host "✗ Failed:  $($failed.Count)" -ForegroundColor Red
    Write-Host "⚠ Skipped: $($skipped.Count)" -ForegroundColor Yellow
    
    if ($successful.Count -gt 0) {
        Write-Host "`nFixed Requirements:" -ForegroundColor Green
        foreach ($fix in $successful) {
            Write-Host "  ✓ $($fix.RequirementId): $($fix.Message)" -ForegroundColor Green
        }
    }
    
    if (-not $DryRun -and $successful.Count -gt 0) {
        Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Review changes made by auto-remediation" -ForegroundColor White
        Write-Host "  2. Run validator again to confirm fixes:" -ForegroundColor White
        Write-Host "     .\scripts\validate\validate_repo_checklist.ps1" -ForegroundColor Gray
        Write-Host "  3. Commit changes if satisfied:" -ForegroundColor White
        Write-Host "     git add .; git commit -m 'fix: Auto-remediation applied'" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # Exit code
    if ($DryRun) {
        exit 0
    }
    elseif ($successful.Count -gt 0) {
        exit 0
    }
    else {
        exit 1
    }
}
catch {
    Write-Host "`n❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
