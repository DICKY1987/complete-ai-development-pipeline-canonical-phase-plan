# DOC_LINK: DOC-SCRIPT-SAFE-MERGE-ORCHESTRATOR-748
# Safe Merge Orchestrator
# Entry: pwsh ./scripts/safe_merge_orchestrator.ps1 --branch <branch> [--mode ci] [--dryrun] [--from-phase N]

param(
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [string]$Mode = "human",
    [int]$FromPhase = 0,
    [int]$ToPhase = 6,
    [int[]]$Phases = @(),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$stateDir = Join-Path $repoRoot ".state\safe_merge"
$logDir = Join-Path $repoRoot "logs"
$locksDir = Join-Path $repoRoot ".git\locks"

New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
New-Item -ItemType Directory -Force -Path $locksDir | Out-Null

function Write-Info { param($msg) Write-Host "INFO  $msg" -ForegroundColor Cyan }
function Write-Ok { param($msg) Write-Host "OK    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "WARN  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "FAIL  $msg" -ForegroundColor Red }

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [int]$Retries = 0,
        [int]$DelaySeconds = 5
    )

    Write-Info "Running $Name"
    if ($DryRun) { Write-Warn "[dry-run] Skipped execution"; return @{ name = $Name; status = "skipped"; duration_seconds = 0 } }

    $start = Get-Date
    for ($i = 0; $i -le $Retries; $i++) {
        try {
            & $Action
            $code = $LASTEXITCODE
            if ($code -eq 0) {
                $duration = (Get-Date) - $start
                Write-Ok "$Name succeeded in $([int]$duration.TotalSeconds)s"
                return @{ name = $Name; status = "ok"; duration_seconds = [int]$duration.TotalSeconds }
            }
            else {
                throw "$Name failed with exit code $code"
            }
        } catch {
            if ($i -lt $Retries) {
                Write-Warn "$Name failed (attempt $($i+1)/$($Retries+1)): $_"
                Start-Sleep -Seconds $DelaySeconds
            }
            else {
                Write-Fail "$Name failed: $_"
                throw
            }
        }
    }
}

function Acquire-Lock {
    param([string]$LockId, [int]$TimeoutSeconds = 900)
    $lockPath = Join-Path $locksDir "$LockId.lock"
    $start = Get-Date

    while ($true) {
        try {
            $fs = [System.IO.File]::Open(
                $lockPath,
                [System.IO.FileMode]::CreateNew,
                [System.IO.FileAccess]::Write,
                [System.IO.FileShare]::None
            )
            $metadata = @{ held_at = (Get-Date -Format "o"); pid = $PID; branch = $Branch }
            $bytes = [System.Text.Encoding]::UTF8.GetBytes(($metadata | ConvertTo-Json))
            $fs.Write($bytes, 0, $bytes.Length)
            $fs.Close()
            $env:SAFE_MERGE_PIPELINE_LOCKED = "1"
            return $lockPath
        } catch {
            $age = 0
            if (Test-Path $lockPath) {
                $age = ((Get-Date) - (Get-Item $lockPath).LastWriteTime).TotalSeconds
                if ($age -gt ($TimeoutSeconds * 2)) {
                    Write-Warn "Removing stale lock $lockPath (age ${age}s)"
                    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
                    continue
                }
            }

            $elapsed = ((Get-Date) - $start).TotalSeconds
            if ($elapsed -gt $TimeoutSeconds) {
                throw "Timeout acquiring lock $LockId"
            }
            Start-Sleep -Seconds 2
        }
    }
}

function Release-Lock {
    param([string]$LockPath)
    if ($LockPath -and (Test-Path $LockPath)) {
        Remove-Item $LockPath -Force -ErrorAction SilentlyContinue
    }
    Remove-Item Env:SAFE_MERGE_PIPELINE_LOCKED -ErrorAction SilentlyContinue
}

# Guard required config
$policyPath = Join-Path $repoRoot "config\merge_policy.yaml"
if (-not (Test-Path $policyPath)) {
    Write-Fail "Missing merge policy at $policyPath"
    exit 2
}

$pipelineLock = $null
try {
    $pipelineLock = Acquire-Lock -LockId "merge_pipeline_$Branch" -TimeoutSeconds 900
    Write-Ok "Pipeline lock acquired: $pipelineLock"

    $pipelineStart = Get-Date
    $phaseSummaries = @()
    $phaseRange = if ($Phases.Count -gt 0) { $Phases } else { $FromPhase..$ToPhase }

    $envScanPath = Join-Path $stateDir "env_scan_$Branch.json"
    $syncSummaryPath = Join-Path $stateDir "sync_summary_$Branch.json"
    $nestedPath = Join-Path $stateDir "nested_repos_$Branch.json"
    $nestedNormPath = Join-Path $stateDir "nested_repo_normalization_$Branch.json"
    $classesPath = Join-Path $stateDir "merge_file_classes_$Branch.json"
    $conflictFlag = Join-Path $stateDir "conflicts_$Branch.flag"

    if (0 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase0_env_scan" -Action {
            & pwsh -ExecutionPolicy Bypass -File (Join-Path $scriptDir "merge_env_scan.ps1") -Branch $Branch -OutputPath $envScanPath
        }
    }

    if (1 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase1_sync_health" -Action {
            & python (Join-Path $scriptDir "sync_log_summary.py") --output $syncSummaryPath --lookback-minutes 30 --max-errors 5 --max-high-activity 0
        }
    }

    if (2 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase2_nested_repos_detect" -Action {
            & python (Join-Path $scriptDir "nested_repo_detector.py") --output $nestedPath --max-stray 0
        }
        $phaseSummaries += Invoke-Step -Name "phase2_nested_repos_normalize" -Action {
            & python (Join-Path $scriptDir "nested_repo_normalizer.py") --input $nestedPath --output $nestedNormPath
        }
    }

    if (3 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase3_file_classification" -Action {
            & python (Join-Path $scriptDir "merge_file_classifier.py") --policy $policyPath --output $classesPath
        }
    }

    if (4 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase4_fetch" -Retries 2 -Action {
            & git fetch origin $Branch
        }

        $mergeStart = Get-Date
        if ($DryRun) {
            Write-Warn "[dry-run] Skip merge"
            $phaseSummaries += @{ name = "phase4_merge"; status = "skipped"; duration_seconds = 0 }
        }
        else {
            & git merge --no-ff origin/$Branch
            $mergeCode = $LASTEXITCODE
            $mergeDuration = [int]((Get-Date) - $mergeStart).TotalSeconds
            if ($mergeCode -ne 0) {
                Set-Content -Path $conflictFlag -Value "merge_conflicts"
                Write-Warn "Merge returned $mergeCode; conflicts flagged at $conflictFlag"
                $phaseSummaries += @{ name = "phase4_merge"; status = "conflicted"; duration_seconds = $mergeDuration }
            }
            else {
                $phaseSummaries += @{ name = "phase4_merge"; status = "ok"; duration_seconds = $mergeDuration }
            }
        }

        $phaseSummaries += Invoke-Step -Name "phase4_timestamp_guard" -Action {
            & python (Join-Path $scriptDir "merge_timestamp_resolver.py") --input $classesPath --branch $Branch --restrict-classes
        }
        $phaseSummaries += Invoke-Step -Name "phase4_conflict_guard" -Action {
            & python (Join-Path $scriptDir "ai_conflict_resolver.py") --branch $Branch --file-classes $classesPath --max-files 20
        }

        $unresolved = git diff --name-only --diff-filter=U
        if ($unresolved) {
            Write-Fail "Unresolved conflicts detected:`n$unresolved"
            throw "Conflicts remain after phase 4"
        }
    }

    if (5 -in $phaseRange) {
        $safePushCommand = "pwsh -ExecutionPolicy Bypass -File `"$scriptDir\safe_pull_and_push.ps1`" -Branch $Branch"
        $phaseSummaries += Invoke-Step -Name "phase5_guarded_push" -Retries 1 -DelaySeconds 10 -Action {
            & python (Join-Path $scriptDir "multi_clone_guard.py") --branch $Branch --lock-type push_only --command $safePushCommand --timeout 900
        }
    }

    if (6 -in $phaseRange) {
        $phaseSummaries += Invoke-Step -Name "phase6_event_emit" -Action {
            & python (Join-Path $scriptDir "safe_merge_emit_event.py") --branch $Branch --status success --events-file (Join-Path $stateDir "merge_events.jsonl")
        }
    }

    $runSummary = @{
        branch = $Branch
        mode = $Mode
        dry_run = [bool]$DryRun
        started_at = ($pipelineStart -Format "o")
        finished_at = (Get-Date -Format "o")
        phases = $phaseSummaries
    }
    $runSummaryPath = Join-Path $stateDir "run_summary_$Branch.json"
    $runSummary | ConvertTo-Json -Depth 8 | Out-File -FilePath $runSummaryPath -Encoding utf8
    Write-Ok "Pipeline complete -> $runSummaryPath"
}
finally {
    Release-Lock -LockPath $pipelineLock
}
