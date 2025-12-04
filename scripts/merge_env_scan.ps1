# Safe Merge Environment Scan (wrapper for MERGE-001)
# Collects repo hygiene signals and emits .state/safe_merge/env_scan_<branch>.json

param(
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [string]$WorkDir = ".",
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
Set-Location $WorkDir

$stateDir = ".state/safe_merge"
if (-not $OutputPath) {
    $OutputPath = Join-Path $stateDir "env_scan_$Branch.json"
}

if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
}

# Basic guards
$workingTreeClean = (git status --porcelain=v1).Length -eq 0
$rebaseInProgress = Test-Path ".git\rebase-apply" -or Test-Path ".git\rebase-merge"
$mergeInProgress = Test-Path ".git\MERGE_HEAD"
$currentBranch = git branch --show-current

# Divergence
$ahead = 0
$behind = 0
try { $ahead = [int](git rev-list --count "$Branch..$currentBranch" 2>$null) } catch { $ahead = 0 }
try { $behind = [int](git rev-list --count "$currentBranch..$Branch" 2>$null) } catch { $behind = 0 }
$diverged = ($ahead -gt 0) -and ($behind -gt 0)

# Compose report
$status = "ready"
$abortReasons = @()
if (-not $workingTreeClean) { $status = "abort"; $abortReasons += "dirty_working_tree" }
if ($rebaseInProgress) { $status = "abort"; $abortReasons += "rebase_in_progress" }
if ($mergeInProgress) { $status = "abort"; $abortReasons += "merge_in_progress" }

$report = [ordered]@{
    pattern_id           = "MERGE-001-ENV-SCAN"
    timestamp            = (Get-Date -Format "o")
    branch               = $Branch
    feature_branch       = $currentBranch
    status               = $status
    checks               = @{
        working_tree_clean  = $workingTreeClean
        no_rebase_in_progress = -not $rebaseInProgress
        no_merge_in_progress  = -not $mergeInProgress
    }
    divergence           = @{
        ahead  = $ahead
        behind = $behind
        diverged = $diverged
    }
    abort_reasons        = $abortReasons
}

$report | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutputPath -Encoding utf8

if ($status -eq "abort") {
    Write-Error "Environment scan failed: $($abortReasons -join ', ')"
    exit 1
}

Write-Host "OK: Environment scan ready. Report: $OutputPath"
exit 0
