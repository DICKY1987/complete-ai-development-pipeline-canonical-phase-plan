# DOC_LINK: DOC-PAT-WORKTREE-LIFECYCLE-001-EXECUTOR-232
# Pattern Executor: worktree_lifecycle
# Pattern ID: PAT-WORKTREE-LIFECYCLE-001
# Auto-generated: 2025-11-27T10:14:13.730476

param(
    [Parameter(Mandatory=$true)]
    [string]$InstanceFile
)

$ErrorActionPreference = "Stop"

# Read instance
$instance = Get-Content $InstanceFile -Raw | ConvertFrom-Json

Write-Host "[EXEC] Running worktree_lifecycle..." -ForegroundColor Cyan

# Parse inputs
$inputs = $instance.pattern.inputs
$repoRoot = if ($inputs.repository_root) { $inputs.repository_root } else { "." }
$operation = if ($inputs.operation) { $inputs.operation } else { "list" }
$branchName = $inputs.branch_name
$worktreeName = $inputs.worktree_name

Push-Location $repoRoot
try {
    # Validate git repository
    git status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Not a git repository"
    }

    # Execute operation
    switch ($operation) {
        "list" {
            $worktrees = git worktree list --porcelain 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Worktrees:" -ForegroundColor Cyan
                Write-Host $worktrees
            } else {
                throw "Failed to list worktrees"
            }
        }

        "create" {
            if (-not $worktreeName) { throw "Missing worktree_name for create operation" }
            if (-not $branchName) { throw "Missing branch_name for create operation" }

            $worktreePath = Join-Path $repoRoot $worktreeName
            if (Test-Path $worktreePath) {
                Write-Warning "Worktree path already exists: $worktreePath"
            } else {
                git worktree add $worktreePath $branchName 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Created worktree: $worktreePath on branch $branchName" -ForegroundColor Green
                } else {
                    throw "Failed to create worktree"
                }
            }
        }

        "remove" {
            if (-not $worktreeName) { throw "Missing worktree_name for remove operation" }

            git worktree remove $worktreeName 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Removed worktree: $worktreeName" -ForegroundColor Green
            } else {
                Write-Warning "Failed to remove worktree (may not exist)"
            }
        }

        default {
            throw "Unknown operation: $operation (use list, create, or remove)"
        }
    }
} finally {
    Pop-Location
}

Write-Host "[OK] Worktree lifecycle operation complete" -ForegroundColor Green
