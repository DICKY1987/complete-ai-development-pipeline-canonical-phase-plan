# DOC_LINK: DOC-SCRIPT-CREATE-MIGRATION-WORKTREES-062
# Migration Worktrees Setup Script
# Creates 4 parallel worktrees for module migration
# Pattern: Parallel execution (4x speedup)

$ErrorActionPreference = "Stop"

Write-Host "Creating Migration Worktrees..." -ForegroundColor Cyan
Write-Host "=" * 60

# Define worktrees by layer
$worktrees = @(
    @{
        Name = "wt-infra-modules"
        Branch = "migration/infra-modules"
        Layer = "infra"
        Description = "Infrastructure layer modules"
    },
    @{
        Name = "wt-domain-modules"
        Branch = "migration/domain-modules"
        Layer = "domain"
        Description = "Domain layer modules"
    },
    @{
        Name = "wt-api-modules"
        Branch = "migration/api-modules"
        Layer = "api"
        Description = "API layer modules"
    },
    @{
        Name = "wt-ui-modules"
        Branch = "migration/ui-modules"
        Layer = "ui"
        Description = "UI layer modules (error plugins)"
    }
)

# Create .worktrees directory if it doesn't exist
$worktreesDir = ".worktrees"
if (-not (Test-Path $worktreesDir)) {
    New-Item -ItemType Directory -Path $worktreesDir | Out-Null
}

foreach ($wt in $worktrees) {
    Write-Host "`nSetting up: $($wt.Name)" -ForegroundColor Yellow
    Write-Host "  Description: $($wt.Description)"
    Write-Host "  Branch: $($wt.Branch)"

    # Create branch if it doesn't exist
    $branchExists = git branch --list $wt.Branch
    if (-not $branchExists) {
        Write-Host "  Creating branch..."
        git branch $wt.Branch
    }

    # Create worktree
    $wtPath = "$worktreesDir\$($wt.Name)"
    if (Test-Path $wtPath) {
        Write-Host "  ⚠️  Worktree already exists: $wtPath" -ForegroundColor Yellow
    } else {
        git worktree add $wtPath $wt.Branch
        Write-Host "  ✓ Created: $wtPath" -ForegroundColor Green
    }
}

Write-Host "`n" + "=" * 60
Write-Host "✅ Worktree setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "  1. cd .worktrees\wt-infra-modules"
Write-Host "  2. python ..\..\scripts\batch_migrate_modules.py --layer infra"
Write-Host "  3. Repeat for other worktrees (domain, api, ui)"
Write-Host "`nTo list worktrees: git worktree list"
