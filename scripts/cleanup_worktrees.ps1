# DOC_LINK: DOC-SCRIPT-CLEANUP-WORKTREES-057
# Cleanup Unused Worktrees
# Auto-removes git worktrees that have no unique commits
# Prevents worktree contamination

Write-Host "🧹 Checking for unused worktrees..." -ForegroundColor Cyan
Write-Host ""

$removed = 0
$kept = 0

# Get list of worktrees (skip first line which is main)
$worktrees = git worktree list --porcelain

$currentWorktree = $null
$currentBranch = $null

foreach ($line in $worktrees) {
    if ($line -match "^worktree (.+)$") {
        $currentWorktree = $matches[1]
    }
    elseif ($line -match "^branch refs/heads/(.+)$") {
        $currentBranch = $matches[1]

        # Skip main branch
        if ($currentBranch -eq "main" -or $currentBranch -eq "master") {
            continue
        }

        # Check if branch has unique commits
        $uniqueCommits = (git log "main..$currentBranch" --oneline 2>$null | Measure-Object).Count

        if ($uniqueCommits -eq 0) {
            Write-Host "❌ Removing unused worktree: $currentWorktree (branch: $currentBranch)" -ForegroundColor Red
            Write-Host "   No unique commits found" -ForegroundColor Gray

            git worktree remove $currentWorktree 2>&1 | Out-Null
            git branch -d $currentBranch 2>&1 | Out-Null

            $removed++
        }
        else {
            Write-Host "✅ Keeping worktree with $uniqueCommits unique commits: $currentWorktree (branch: $currentBranch)" -ForegroundColor Green
            $kept++
        }
    }
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Removed: $removed worktrees" -ForegroundColor $(if ($removed -gt 0) { "Yellow" } else { "Green" })
Write-Host "  Kept: $kept worktrees" -ForegroundColor Green
Write-Host ""

if ($removed -gt 0) {
    Write-Host "✅ Cleanup complete - contamination prevented" -ForegroundColor Green
}
else {
    Write-Host "✅ No unused worktrees found" -ForegroundColor Green
}
