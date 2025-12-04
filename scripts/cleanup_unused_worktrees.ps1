# DOC_LINK: DOC-SCRIPT-CLEANUP-UNUSED-WORKTREES-056
# Cleanup Unused Worktrees Script
# Anti-Pattern Guard #11: Worktree contamination
# Auto-cleanup worktrees older than 24 hours

$ErrorActionPreference = "Stop"

Write-Host "Cleaning up unused worktrees..." -ForegroundColor Cyan
Write-Host "=" * 60

# Get all worktrees
$worktrees = git worktree list --porcelain | Out-String

# Parse worktree information
$wtList = @()
$currentWt = @{}

foreach ($line in $worktrees -split "`n") {
    if ($line -match "^worktree (.+)$") {
        if ($currentWt.Count -gt 0) {
            $wtList += $currentWt
        }
        $currentWt = @{Path = $matches[1]}
    }
    elseif ($line -match "^branch (.+)$") {
        $currentWt.Branch = $matches[1]
    }
}

if ($currentWt.Count -gt 0) {
    $wtList += $currentWt
}

Write-Host "Found $($wtList.Count) worktrees (including main)"

# Check each worktree (except main)
$cleaned = 0
foreach ($wt in $wtList) {
    if ($wt.Path -match "\.worktrees") {
        Write-Host "`nChecking: $($wt.Path)"

        # Check if directory exists
        if (Test-Path $wt.Path) {
            # Check last modified time
            $lastModified = (Get-Item $wt.Path).LastWriteTime
            $age = (Get-Date) - $lastModified

            Write-Host "  Age: $([Math]::Round($age.TotalHours, 1)) hours"

            if ($age.TotalHours -gt 24) {
                Write-Host "  ⚠️  Worktree older than 24 hours" -ForegroundColor Yellow

                # Check if it has uncommitted changes
                Push-Location $wt.Path
                $status = git status --short
                Pop-Location

                if ($status) {
                    Write-Host "  ⚠️  Has uncommitted changes - skipping" -ForegroundColor Yellow
                } else {
                    Write-Host "  🗑️  Removing unused worktree..." -ForegroundColor Red
                    git worktree remove $wt.Path --force
                    $cleaned++
                }
            } else {
                Write-Host "  ✓ Active worktree" -ForegroundColor Green
            }
        } else {
            Write-Host "  ⚠️  Path not found - pruning..." -ForegroundColor Yellow
            git worktree prune
        }
    }
}

Write-Host "`n" + "=" * 60
Write-Host "✅ Cleanup complete: removed $cleaned worktrees" -ForegroundColor Green
