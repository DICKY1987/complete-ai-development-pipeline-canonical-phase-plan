<#
.SYNOPSIS
    MERGE-006: Safe Pull and Push

.DESCRIPTION
    Guards every push with strict pull + divergence check.
    Prevents blind overwrites in multi-clone environments.

.PARAMETER WorkDir
    Repository root path (default: current directory)

.PARAMETER Branch
    Branch to push (default: current branch)

.PARAMETER RemoteName
    Remote name (default: "origin")

.PARAMETER RebaseMode
    Pull strategy: "ff-only" or "rebase" (default: "rebase")

.OUTPUTS
    Push to remote (if successful)
    Event logged to safe_push_events.jsonl
#>

param(
    [string]$WorkDir = ".",
    [string]$Branch = "",
    [string]$RemoteName = "origin",
    [ValidateSet("ff-only", "rebase")]
    [string]$RebaseMode = "rebase"
)

$ErrorActionPreference = "Stop"
Set-Location $WorkDir

Write-Host "🔒 MERGE-006: Safe Pull and Push" -ForegroundColor Cyan
Write-Host ""

# Get current branch if not specified
if (-not $Branch) {
    $Branch = git branch --show-current
    Write-Host "🔍 Using current branch: $Branch" -ForegroundColor Cyan
}

# Step 1: Check dirty state
Write-Host "📋 Checking working directory..." -ForegroundColor Cyan
$status = git status --porcelain

if ($status) {
    Write-Error "⚠️ Working directory is dirty - cannot pull/push"
    Write-Host "   Uncommitted changes detected. Commit or stash them first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Working directory is clean" -ForegroundColor Green

# Step 2: Fetch from remote
Write-Host "📥 Fetching from remote..." -ForegroundColor Cyan
git fetch $RemoteName
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Fetch failed"
    exit 1
}

# Step 3: Check ahead/behind
$tracking = "$RemoteName/$Branch"
Write-Host "📊 Checking divergence vs $tracking..." -ForegroundColor Cyan

try {
    $ahead = [int](git rev-list --count "$tracking..$Branch" 2>$null)
} catch {
    $ahead = 0
}

try {
    $behind = [int](git rev-list --count "$Branch..$tracking" 2>$null)
} catch {
    $behind = 0
}

Write-Host "   Ahead: $ahead commits" -ForegroundColor Yellow
Write-Host "   Behind: $behind commits" -ForegroundColor Yellow

# Step 4: Pull if behind
if ($behind -gt 0) {
    Write-Host "📥 Pulling changes from remote..." -ForegroundColor Cyan
    
    if ($RebaseMode -eq "ff-only") {
        git pull --ff-only $RemoteName $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Error "⚠️ Cannot fast-forward - manual merge required"
            Write-Host "   Remote has diverged. You may need to merge manually." -ForegroundColor Red
            exit 1
        }
    } elseif ($RebaseMode -eq "rebase") {
        git pull --rebase --autostash $RemoteName $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Error "⚠️ Rebase failed - manual resolution required"
            Write-Host "   Conflicts detected during rebase. Resolve them manually." -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ Pull successful" -ForegroundColor Green
} else {
    Write-Host "✅ Already up-to-date with remote" -ForegroundColor Green
}

# Step 5: Push
Write-Host "📤 Pushing to remote..." -ForegroundColor Cyan
git push $RemoteName $Branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push successful" -ForegroundColor Green
    
    # Emit event
    $event = @{
        pattern_id = "MERGE-006"
        timestamp = (Get-Date -Format "o")
        event = "safe_push"
        branch = $Branch
        remote = $RemoteName
        ahead = $ahead
        behind = $behind
        rebase_mode = $RebaseMode
    } | ConvertTo-Json -Compress
    
    Add-Content -Path "safe_push_events.jsonl" -Value $event
    
    exit 0
} else {
    Write-Error "❌ Push failed"
    Write-Host "   Check remote permissions and network connection." -ForegroundColor Red
    exit 1
}
