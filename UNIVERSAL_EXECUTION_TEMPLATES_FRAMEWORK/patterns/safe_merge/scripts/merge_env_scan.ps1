<#
.SYNOPSIS
    MERGE-001: Safe Merge Environment Scan

.DESCRIPTION
    Scans repository state, branch topology, and divergence.
    Detects issues that would block safe merge.

.PARAMETER WorkDir
    Repository root path (default: current directory)

.PARAMETER BaseBranch
    Target branch (e.g., "main")

.PARAMETER FeatureBranch
    Source branch (e.g., "feature/xyz")

.PARAMETER RemoteName
    Remote name (default: "origin")

.OUTPUTS
    env_scan.safe_merge.json - Structured report
#>

param(
    [string]$WorkDir = ".",
    [Parameter(Mandatory=$true)]
    [string]$BaseBranch,
    [Parameter(Mandatory=$true)]
    [string]$FeatureBranch,
    [string]$RemoteName = "origin"
)

$ErrorActionPreference = "Stop"
Set-Location $WorkDir

Write-Host "🔍 MERGE-001: Safe Merge Environment Scan" -ForegroundColor Cyan
Write-Host "   Base: $BaseBranch | Feature: $FeatureBranch | Remote: $RemoteName" -ForegroundColor Gray
Write-Host ""

# Step 1: Check dirty state
Write-Host "📋 Checking working directory state..." -ForegroundColor Cyan
$dirty = git status --porcelain=v1
$hasDirtyFiles = $dirty.Length -gt 0

if ($hasDirtyFiles) {
    Write-Warning "⚠️ Working directory has uncommitted changes"
    $abortReasons = @("dirty_working_tree")
    $status = "abort"
} else {
    Write-Host "✅ Working directory is clean" -ForegroundColor Green
    $abortReasons = @()
    $status = "ready"
}

# Step 2: Inventory branches and remotes
Write-Host "📋 Inventorying branches and remotes..." -ForegroundColor Cyan
$branches = git branch -vv
$remotes = git remote -v

# Step 3: Calculate ahead/behind counts
Write-Host "📊 Calculating divergence..." -ForegroundColor Cyan

try {
    $ahead = [int](git rev-list --count "$BaseBranch..$FeatureBranch" 2>$null)
} catch {
    $ahead = 0
}

try {
    $behind = [int](git rev-list --count "$FeatureBranch..$BaseBranch" 2>$null)
} catch {
    $behind = 0
}

$diverged = ($ahead -gt 0) -and ($behind -gt 0)

Write-Host "  Ahead: $ahead commits" -ForegroundColor Yellow
Write-Host "  Behind: $behind commits" -ForegroundColor Yellow
Write-Host "  Diverged: $diverged" -ForegroundColor $(if ($diverged) { "Red" } else { "Green" })

# Step 4: Get commit SHAs
try {
    $baseCommit = git rev-parse $BaseBranch 2>$null
} catch {
    $baseCommit = "unknown"
}

try {
    $featureCommit = git rev-parse $FeatureBranch 2>$null
} catch {
    $featureCommit = "unknown"
}

try {
    $tracking = git rev-parse --abbrev-ref "$BaseBranch@{upstream}" 2>$null
} catch {
    $tracking = $null
}

# Step 5: Emit JSON summary
$report = @{
    timestamp = (Get-Date -Format "o")
    pattern_id = "MERGE-001"
    status = $status
    branches = @{
        base = @{
            name = $BaseBranch
            commit = $baseCommit
            tracking = $tracking
        }
        feature = @{
            name = $FeatureBranch
            commit = $featureCommit
            ahead = $ahead
            behind = $behind
            diverged = $diverged
        }
    }
    remotes = @($remotes -split "`n" | Where-Object { $_ })
    abort_reasons = $abortReasons
}

$jsonPath = "env_scan.safe_merge.json"
$report | ConvertTo-Json -Depth 5 | Out-File $jsonPath -Encoding utf8

Write-Host ""
Write-Host "📄 Report saved: $jsonPath" -ForegroundColor Green
Write-Host ""

# Final status
if ($status -eq "abort") {
    Write-Host "❌ ABORT: Cannot proceed with merge" -ForegroundColor Red
    Write-Host "   Reasons: $($abortReasons -join ', ')" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ READY: Safe to proceed with merge" -ForegroundColor Green
    exit 0
}
