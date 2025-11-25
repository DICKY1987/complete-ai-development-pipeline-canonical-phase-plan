#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-CREATE-DOCID-WORKTREES-001
# Create git worktrees for parallel doc_id registration
# Usage: .\doc_id\create_docid_worktrees.ps1

param(
    [switch]$Cleanup,
    [switch]$List
)

$ErrorActionPreference = "Stop"

# Repository root (script now lives in doc_id/, so go up one level)
$repoRoot = Split-Path -Parent $PSScriptRoot
$worktreeBase = Join-Path $repoRoot ".worktrees"

# Define worktrees
$worktrees = @(
    @{
        Name = "wt-docid-specs"
        Branch = "feature/docid-specs"
        Description = "Specifications & Schemas (25 files)"
        Categories = @("spec", "config")
    },
    @{
        Name = "wt-docid-scripts"
        Branch = "feature/docid-scripts"
        Description = "Scripts & Tools (26 files)"
        Categories = @("script")
    },
    @{
        Name = "wt-docid-tests-docs"
        Branch = "feature/docid-tests-docs"
        Description = "Tests & Documentation (70 files)"
        Categories = @("test", "guide")
    },
    @{
        Name = "wt-docid-modules"
        Branch = "feature/docid-modules"
        Description = "Remaining Modules (107 files)"
        Categories = @("core", "error", "aim", "pm", "infra")
    }
)

function Show-WorktreeList {
    Write-Host "`n📋 Current Worktrees:" -ForegroundColor Yellow
    Push-Location $repoRoot
    git worktree list
    Pop-Location
}

function Remove-Worktrees {
    Write-Host "`n🧹 Cleaning up worktrees..." -ForegroundColor Yellow
    
    Push-Location $repoRoot
    
    foreach ($wt in $worktrees) {
        $path = Join-Path $worktreeBase $wt.Name
        
        if (Test-Path $path) {
            Write-Host "  Removing: $($wt.Name)" -ForegroundColor Gray
            git worktree remove $path --force 2>$null
        }
        
        # Delete branch if exists
        $branchExists = git branch --list $wt.Branch
        if ($branchExists) {
            Write-Host "  Deleting branch: $($wt.Branch)" -ForegroundColor Gray
            git branch -D $wt.Branch 2>$null
        }
    }
    
    Pop-Location
    
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

function New-Worktrees {
    Write-Host "`n🚀 Creating DOC_ID Worktrees for Parallel Execution" -ForegroundColor Cyan
    Write-Host "=" * 60
    
    # Ensure we're in repo root
    Push-Location $repoRoot
    
    # Check if repo is clean
    $status = git status --porcelain
    if ($status) {
        Write-Host "⚠️  Warning: Repository has uncommitted changes" -ForegroundColor Yellow
        Write-Host "   Commit or stash changes before creating worktrees" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y") {
            Pop-Location
            exit 1
        }
    }
    
    # Create worktree directory
    if (-not (Test-Path $worktreeBase)) {
        New-Item -ItemType Directory -Path $worktreeBase -Force | Out-Null
        Write-Host "✅ Created worktree directory: $worktreeBase" -ForegroundColor Green
    }
    
    # Create each worktree
    Write-Host "`nCreating worktrees..." -ForegroundColor Yellow
    
    $created = 0
    foreach ($wt in $worktrees) {
        $path = Join-Path $worktreeBase $wt.Name
        $branch = $wt.Branch
        
        Write-Host "`n📁 Worktree: $($wt.Name)" -ForegroundColor Cyan
        Write-Host "   Branch: $branch" -ForegroundColor Gray
        Write-Host "   Scope: $($wt.Description)" -ForegroundColor Gray
        Write-Host "   Categories: $($wt.Categories -join ', ')" -ForegroundColor Gray
        
        # Remove if already exists
        if (Test-Path $path) {
            Write-Host "   (Removing existing worktree)" -ForegroundColor Yellow
            git worktree remove $path --force 2>$null
        }
        
        # Create worktree
        $result = git worktree add $path $branch 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Created successfully" -ForegroundColor Green
            $created++
        } else {
            Write-Host "   ❌ Failed to create: $result" -ForegroundColor Red
        }
    }
    
    Pop-Location
    
    # Summary
    Write-Host "`n" + ("=" * 60)
    Write-Host "📊 Summary:" -ForegroundColor Cyan
    Write-Host "   Created: $created/$($worktrees.Count) worktrees" -ForegroundColor Green
    
    if ($created -eq $worktrees.Count) {
        Write-Host "`n✅ All worktrees created successfully!" -ForegroundColor Green
        
        Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
        Write-Host "   1. Open 4 terminal windows"
        Write-Host "   2. Navigate to each worktree:"
        
        foreach ($wt in $worktrees) {
            $relativePath = ".worktrees\$($wt.Name)"
            Write-Host "      cd $relativePath" -ForegroundColor Gray
        }
        
        Write-Host "`n   3. Run parallel doc_id registration in each terminal"
        Write-Host "   4. Commit changes to respective branches"
        Write-Host "   5. Merge all branches back to main"
        
        Write-Host "`n💡 Tip: Use 'git worktree list' to see all worktrees" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠️  Some worktrees failed to create" -ForegroundColor Yellow
        Write-Host "   Check error messages above" -ForegroundColor Yellow
    }
}

# Main execution
if ($List) {
    Show-WorktreeList
}
elseif ($Cleanup) {
    Remove-Worktrees
}
else {
    New-Worktrees
}

Write-Host ""
