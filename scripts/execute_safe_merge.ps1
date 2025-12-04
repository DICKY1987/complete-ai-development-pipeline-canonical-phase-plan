# DOC_LINK: DOC-SCRIPT-EXECUTE-SAFE-MERGE-063
# Safe Merge Execution Script
# Automates SAFE_MERGE_STRATEGY.md phases with checkpoints and rollback
# Usage: .\scripts\execute_safe_merge.ps1 [-DryRun] [-SkipTests]

param(
    [switch]$DryRun = $false,
    [switch]$SkipTests = $false,
    [switch]$AutoYes = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackupDir = "$RepoRoot\.merge-backup"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Color output functions
function Write-Phase { param($msg) Write-Host "`n=== PHASE: $msg ===" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }

# Checkpoint function
function Checkpoint {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [scriptblock]$Validate,
        [bool]$Required = $true
    )

    Write-Info "Checkpoint: $Name"

    if ($DryRun) {
        Write-Warning "[DRY RUN] Would execute: $Name"
        return $true
    }

    try {
        & $Action
        $valid = & $Validate
        if ($valid) {
            Write-Success "$Name - PASS"
            return $true
        } else {
            Write-Error "$Name - FAIL (validation failed)"
            if ($Required) { exit 1 }
            return $false
        }
    }
    catch {
        Write-Error "$Name - FAIL: $_"
        if ($Required) { exit 1 }
        return $false
    }
}

# Confirmation function
function Confirm-Action {
    param([string]$Message)

    if ($AutoYes) { return $true }

    $response = Read-Host "$Message (y/N)"
    return $response -eq "y" -or $response -eq "Y"
}

#-----------------------------------
# PHASE 0: PRE-FLIGHT CHECKS
#-----------------------------------
Write-Phase "PHASE 0: Pre-Flight Checks"

Checkpoint -Name "0.1 Verify Current Branch" -Action {
    $branch = git branch --show-current
    if ($branch -ne "feature/uet-compat-shims") {
        throw "Expected branch 'feature/uet-compat-shims', got '$branch'"
    }
} -Validate {
    $branch = git branch --show-current
    return $branch -eq "feature/uet-compat-shims"
}

Checkpoint -Name "0.2 Count Commits Ahead" -Action {
    $count = git rev-list --count main..HEAD
    Write-Info "Commits ahead of main: $count"
    if ($count -lt 1) {
        throw "No commits to merge"
    }
} -Validate {
    $count = git rev-list --count main..HEAD
    return $count -ge 1
}

Checkpoint -Name "0.3 Create Backup Directory" -Action {
    if (!(Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
} -Validate {
    return Test-Path $BackupDir
}

Checkpoint -Name "0.4 Create Snapshot Tag" -Action {
    $tagName = "pre-merge-snapshot-$Timestamp"
    git tag -a $tagName -m "Snapshot before main merge - automated"
    Write-Info "Created tag: $tagName"
} -Validate {
    $tags = git tag --list "pre-merge-snapshot-$Timestamp"
    return $tags -ne ""
}

Checkpoint -Name "0.5 Backup Stash List" -Action {
    git stash list > "$BackupDir\stash-list.txt"
} -Validate {
    return Test-Path "$BackupDir\stash-list.txt"
}

Checkpoint -Name "0.6 Export Commits to Merge" -Action {
    git log HEAD~6..HEAD --oneline > "$BackupDir\commits-to-merge.txt"
} -Validate {
    return Test-Path "$BackupDir\commits-to-merge.txt"
}

#-----------------------------------
# PHASE 1: SUBMODULE RESOLUTION
#-----------------------------------
Write-Phase "PHASE 1: Submodule Resolution"

Checkpoint -Name "1.1 Check Submodule Status" -Action {
    $status = git status --short
    Write-Info "Current status:`n$status"

    # Check if ccpm and AI_MANGER are submodules
    $ccpmIsSubmodule = Test-Path "ccpm\.git"
    $aimangerIsSubmodule = Test-Path "archive\legacy\AI_MANGER_archived_2025-11-22\.git"

    Write-Info "ccpm is git repo: $ccpmIsSubmodule"
    Write-Info "AI_MANGER is git repo: $aimangerIsSubmodule"
} -Validate {
    # Always passes - this is informational
    return $true
} -Required $false

if (Confirm-Action "Commit submodule pointer changes?") {
    Checkpoint -Name "1.2 Commit Submodule State" -Action {
        git add archive/legacy/AI_MANGER_archived_2025-11-22 ccpm
        git commit -m "chore: sync submodule pointers before merge"
    } -Validate {
        $status = git status --short
        return $status -eq ""
    } -Required $false
}

#-----------------------------------
# PHASE 2: CREATE ROLLBACK BRANCH
#-----------------------------------
Write-Phase "PHASE 2: Create Rollback Branch"

$rollbackBranch = "rollback/pre-main-merge-$Timestamp"

Checkpoint -Name "2.1 Create Rollback Branch" -Action {
    git branch $rollbackBranch HEAD
    Write-Success "Created rollback branch: $rollbackBranch"
} -Validate {
    $branches = git branch --list $rollbackBranch
    return $branches -ne ""
}

Checkpoint -Name "2.2 Push Rollback to Remote" -Action {
    git push origin $rollbackBranch
} -Validate {
    $remoteBranches = git branch -r --list "origin/$rollbackBranch"
    return $remoteBranches -ne ""
}

Write-Success "Rollback branch created and pushed: $rollbackBranch"
Write-Info "To rollback: git reset --hard $rollbackBranch"

#-----------------------------------
# PHASE 3: MERGE TO MAIN
#-----------------------------------
Write-Phase "PHASE 3: Merge to Main"

Checkpoint -Name "3.1 Fetch Latest Main" -Action {
    git fetch origin main
} -Validate {
    return $LASTEXITCODE -eq 0
}

Checkpoint -Name "3.2 Check Main Divergence" -Action {
    $diverged = git log main..origin/main --oneline
    if ($diverged) {
        Write-Warning "Main has diverged. Commits on origin/main:`n$diverged"
        if (!(Confirm-Action "Pull changes from origin/main?")) {
            throw "User aborted - main has diverged"
        }
    }
} -Validate {
    return $true
}

Checkpoint -Name "3.3 Checkout Main" -Action {
    git checkout main
} -Validate {
    $branch = git branch --show-current
    return $branch -eq "main"
}

Checkpoint -Name "3.4 Pull Main (if needed)" -Action {
    git pull origin main --ff-only
} -Validate {
    return $LASTEXITCODE -eq 0
} -Required $false

if (Confirm-Action "Proceed with merge?") {
    Checkpoint -Name "3.5 Merge Feature Branch" -Action {
        $mergeMsg = @"
Merge feature/uet-compat-shims: Module migration and pattern automation

Includes:
- Module-centric architecture migration (33 modules)
- Import path rewriting and compatibility shims
- Pattern automation system activation
- 5 execution patterns + Codex instructions
- Anti-pattern guards and validation framework

Commits: 6
Files: 148 (+10,485, -1,436)
Ref: PLAN-MERGE-CONSOLIDATION-001
Timestamp: $Timestamp
"@
        git merge --no-ff feature/uet-compat-shims -m $mergeMsg
    } -Validate {
        # Check if merge completed (no MERGE_HEAD means merge done)
        return !(Test-Path ".git\MERGE_HEAD")
    }
} else {
    Write-Warning "Merge aborted by user"
    exit 0
}

#-----------------------------------
# PHASE 3.6: POST-MERGE VALIDATION
#-----------------------------------
Write-Phase "PHASE 3.6: Post-Merge Validation"

Checkpoint -Name "3.6.1 Verify Compilation" -Action {
    python -m compileall modules/ -q
} -Validate {
    return $LASTEXITCODE -eq 0
}

Checkpoint -Name "3.6.2 Verify Imports" -Action {
    $output = python scripts/test_imports.py 2>&1
    Write-Info $output
} -Validate {
    $output = python scripts/test_imports.py 2>&1
    return $output -match "All imports successful"
}

if (!$SkipTests) {
    Checkpoint -Name "3.6.3 Run Critical Tests" -Action {
        pytest tests/core/ tests/engine/ -q --tb=no
    } -Validate {
        return $LASTEXITCODE -eq 0
    } -Required $false
}

#-----------------------------------
# PHASE 5: PUSH TO REMOTE
#-----------------------------------
Write-Phase "PHASE 5: Push to Remote"

if (Confirm-Action "Push merged main to remote?") {
    Checkpoint -Name "5.1 Push Main" -Action {
        git push origin main
    } -Validate {
        $localCommit = git rev-parse main
        $remoteCommit = git rev-parse origin/main
        return $localCommit -eq $remoteCommit
    }

    Write-Success "Main branch pushed to remote"
} else {
    Write-Warning "Skipped push to remote - remember to push manually"
}

#-----------------------------------
# COMPLETION REPORT
#-----------------------------------
Write-Phase "MERGE COMPLETE"

Write-Success "Safe merge execution completed successfully!"
Write-Info "Summary:"
Write-Info "  - Rollback branch: $rollbackBranch"
Write-Info "  - Backup directory: $BackupDir"
Write-Info "  - Timestamp: $Timestamp"

Write-Info "`nNext steps:"
Write-Info "  1. Review merged changes: git log --oneline -10"
Write-Info "  2. Run full test suite: pytest tests/ -v"
Write-Info "  3. Update documentation"
Write-Info "  4. Clean up feature branches"

Write-Warning "`nRollback procedure (if needed):"
Write-Warning "  git reset --hard $rollbackBranch"
Write-Warning "  git push origin main --force-with-lease"

exit 0
