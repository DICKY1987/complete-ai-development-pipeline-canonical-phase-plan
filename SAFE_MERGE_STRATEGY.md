---
doc_id: DOC-GUIDE-SAFE-MERGE-STRATEGY-176
---

# Safe Merge Strategy & Consolidation Plan

**Document ID**: PLAN-MERGE-CONSOLIDATION-001  
**Created**: 2025-11-27T09:00:00Z  
**Status**: READY FOR EXECUTION  
**Priority**: CRITICAL  

---

## Executive Summary

**Objective**: Safely consolidate 6 commits from `feature/uet-compat-shims` to `main`, with rollback capability and bidirectional sync between local directory and repository.

**Current State Analysis**:
- **Active Branch**: `feature/uet-compat-shims` (6 commits ahead of `main`)
- **Main Branch**: `origin/main` at commit `7f69f03`
- **Changes**: 148 files (+10,485 insertions, -1,436 deletions)
- **Submodule Issues**: 2 detected (`ccpm`, `AI_MANGER_archived_2025-11-22`)
- **Stashed Changes**: 1 autostash present
- **Uncommitted**: Submodule pointer changes only

**Risk Level**: MEDIUM
- Large changeset (10k+ lines)
- Submodule complications
- Multiple feature branches to reconcile

---

## Phase 0: Pre-Flight Checks (5 minutes)

### Checkpoint 0.1: Verify Ground Truth

```powershell
# Current branch and commit
git branch --show-current
# Expected: feature/uet-compat-shims

git rev-parse HEAD
# Expected: 0daf2339f514da8a5763a68543dc98e4fac8bc52

# Commits ahead of main
git rev-list --count main..HEAD
# Expected: 6

# Working directory status
git status --short
# Expected: m archive/legacy/AI_MANGER_archived_2025-11-22
#           m ccpm
```

**Success Criteria**: ✅ All outputs match expected values

### Checkpoint 0.2: Backup Current State

```powershell
# Create pre-merge snapshot tag
git tag -a "pre-merge-snapshot-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -m "Snapshot before main merge"

# Backup stash
git stash list > .merge-backup/stash-list.txt

# Export current branch state
git log HEAD~6..HEAD --oneline > .merge-backup/commits-to-merge.txt
```

**Success Criteria**: ✅ Tag created, backup files exist

---

## Phase 1: Submodule Resolution (10 minutes)

### Issue Analysis

**Problem**: Git detects submodule pointer changes but `.gitmodules` doesn't exist
- `archive/legacy/AI_MANGER_archived_2025-11-22/.git` exists (is a git repo)
- `ccpm/.git` exists (is a git repo)
- These are **nested repos**, not proper submodules

**Impact**: Will block clean merge if not resolved

### Resolution Strategy: Convert to Submodules (RECOMMENDED)

```powershell
# Step 1: Check if these should be submodules
git ls-tree HEAD archive/legacy/AI_MANGER_archived_2025-11-22
git ls-tree HEAD ccpm

# Step 2: If they're submodules, initialize them
git submodule init
git submodule update

# Step 3: Commit submodule state
git add archive/legacy/AI_MANGER_archived_2025-11-22 ccpm
git commit -m "chore: sync submodule pointers"
```

### Alternative: Remove Nested Repos (If Not Needed)

```powershell
# Only if these are accidental nested repos
Remove-Item -Recurse -Force archive\legacy\AI_MANGER_archived_2025-11-22\.git
Remove-Item -Recurse -Force ccpm\.git

# Convert to regular directories
git add -A archive/legacy/AI_MANGER_archived_2025-11-22
git add -A ccpm
git commit -m "chore: convert nested repos to regular directories"
```

**Decision Point**: Choose strategy based on whether `ccpm` and `AI_MANGER` should be tracked externally.

**Success Criteria**: ✅ `git status` shows clean working directory

---

## Phase 2: Create Rollback Branch (2 minutes)

**Purpose**: Safety net - if merge causes issues, rollback branch preserves working state

```powershell
# Create rollback branch from current HEAD
git branch rollback/pre-main-merge-20251127 HEAD

# Verify creation
git branch --list "rollback/*"
# Expected: rollback/pre-main-merge-20251127

# Push rollback branch to remote (backup to cloud)
git push origin rollback/pre-main-merge-20251127
```

**Success Criteria**: ✅ Branch created locally and pushed to remote

**Rollback Command** (if needed later):
```powershell
git reset --hard rollback/pre-main-merge-20251127
```

---

## Phase 3: Merge to Main (15 minutes)

### Step 3.1: Update Main Branch

```powershell
# Fetch latest from remote
git fetch origin main

# Check if main has diverged
git log main..origin/main --oneline
# Expected: (empty - no divergence)

# If diverged, pull changes
git checkout main
git pull origin main --ff-only
```

**Success Criteria**: ✅ Main is up-to-date with `origin/main`

### Step 3.2: Merge Feature Branch

```powershell
# Switch to main
git checkout main

# Merge feature branch with merge commit (preserves history)
git merge --no-ff feature/uet-compat-shims -m "Merge feature/uet-compat-shims: Module migration and pattern automation

Includes:
- Module-centric architecture migration (33 modules)
- Import path rewriting and compatibility shims
- Pattern automation system activation
- 5 execution patterns + Codex instructions
- Anti-pattern guards and validation framework

Commits: 6
Files: 148 (+10,485, -1,436)
Ref: PLAN-MERGE-CONSOLIDATION-001"
```

**If Conflicts Occur**:
```powershell
# Check conflict files
git diff --name-only --diff-filter=U

# Resolve manually or abort
git merge --abort  # Rollback to pre-merge state
git checkout rollback/pre-main-merge-20251127  # Full rollback
```

**Success Criteria**: ✅ Merge completes without conflicts OR conflicts resolved

### Step 3.3: Post-Merge Validation

```powershell
# Verify compilation
python -m compileall modules/ -q
# Expected: exit code 0

# Verify imports
python scripts/test_imports.py
# Expected: "All imports successful!"

# Run critical tests
pytest tests/core/ tests/engine/ -q
# Expected: Most tests pass (baseline)

# Check module structure
python scripts/validate_acs_conformance.py
# Expected: No critical violations
```

**Success Criteria**: ✅ All validation gates pass

---

## Phase 4: Reconcile Other Feature Branches (10 minutes)

**Current Feature Branches**:
1. `feature/hybrid-gui-plan-v1` (merged already)
2. `feature/module-import-stabilization` (ancestor of current)
3. `migration/*` branches (4 branches - likely stale)

### Step 4.1: Check Branch Status

```powershell
# Check which branches are merged
git branch --merged main

# Check which branches are not merged
git branch --no-merged main
```

### Step 4.2: Clean Up Merged Branches

```powershell
# Delete local merged branches (except main)
git branch --merged main | Where-Object { $_ -notmatch "main" } | ForEach-Object { git branch -d $_.Trim() }

# Delete remote merged branches (CAREFUL - review first)
git branch -r --merged main | Where-Object { $_ -match "migration/" } | ForEach-Object {
    $branch = $_ -replace "origin/", ""
    git push origin --delete $branch
}
```

**Success Criteria**: ✅ Only active branches remain

---

## Phase 5: Push to Remote (5 minutes)

```powershell
# Push updated main to remote
git push origin main

# Verify push
git log origin/main..main
# Expected: (empty - local and remote are synced)

# Update feature branch pointer (optional - mark as merged)
git push origin :feature/uet-compat-shims  # Delete remote feature branch
git branch -d feature/uet-compat-shims     # Delete local feature branch
```

**Success Criteria**: ✅ Remote main matches local main

---

## Phase 6: Local Directory Sync (20 minutes)

### Issue: Bidirectional Sync Between Repo and Local Dir

**Scenario 1**: Local directory has uncommitted work  
**Scenario 2**: Repository has updates not reflected locally

### Step 6.1: Analyze Local Directory State

```powershell
# Check for uncommitted changes
git status --porcelain > .merge-backup/local-changes.txt

# Check for untracked files
git ls-files --others --exclude-standard > .merge-backup/untracked-files.txt

# Analyze local modifications
git diff > .merge-backup/local-modifications.diff
git diff --cached > .merge-backup/staged-modifications.diff
```

### Step 6.2: Categorize Local Changes

```powershell
# Run categorization script
python scripts/analyze_local_changes.py --output .merge-backup/change-analysis.yaml
```

**Expected Categories**:
- **Keep Local**: User edits, WIP features
- **Discard**: Generated files, temp files, cache
- **Merge**: Config updates, documentation

### Step 6.3: Apply Local Changes to Repo

```powershell
# Stash current work
git stash push -u -m "Local directory changes before merge sync"

# Pull latest main
git pull origin main --ff-only

# Pop stash and resolve conflicts
git stash pop

# Review changes
git diff

# Commit keeper changes
git add <files-to-keep>
git commit -m "chore: sync local directory changes

- <describe changes>
- <describe changes>"

# Push to remote
git push origin main
```

**Success Criteria**: ✅ Local and remote are synchronized

---

## Phase 7: Final Validation (10 minutes)

### Comprehensive Test Suite

```powershell
# Full test suite
pytest tests/ -v --tb=short > .merge-backup/test-results.txt

# Import validation
python scripts/analyze_imports.py modules/ > .merge-backup/import-analysis-final.yaml

# ACS conformance
python scripts/validate_acs_conformance.py

# Quality gates
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

### Success Metrics

| Metric | Baseline | Target | Actual |
|--------|----------|--------|--------|
| Tests Passing | 196 | ≥ 180 | ___ |
| Import Errors | 0 | 0 | ___ |
| ACS Violations | 0 | 0 | ___ |
| Coverage | 77% | ≥ 75% | ___ |

**Success Criteria**: ✅ All targets met or exceeded

---

## Phase 8: Documentation & Cleanup (10 minutes)

### Update Documentation

```powershell
# Update migration status
# Edit: REMAINING_MODULE_CENTRIC_PLAN.md → Mark Phase 2 complete

# Update progress report
# Edit: PROGRESS_REPORT.md → Add merge completion

# Create completion report
python scripts/generate_completion_report.py --output MERGE_COMPLETION_REPORT.md
```

### Cleanup

```powershell
# Remove temporary files
Remove-Item -Recurse .merge-backup

# Clean up worktrees
python scripts/cleanup_unused_worktrees.ps1

# Clean pycache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Commit cleanup
git add -A
git commit -m "chore: post-merge cleanup"
git push origin main
```

**Success Criteria**: ✅ Clean repository state

---

## Rollback Procedures

### Scenario A: Merge Conflicts (During Phase 3)

```powershell
# Abort merge
git merge --abort

# Return to feature branch
git checkout feature/uet-compat-shims

# Action: Investigate conflicts, resolve manually, retry
```

### Scenario B: Failed Validation (During Phase 7)

```powershell
# Soft rollback - keep changes
git reset --soft rollback/pre-main-merge-20251127

# Review changes
git diff HEAD

# Fix issues, recommit
```

### Scenario C: Critical Failure (Nuclear Option)

```powershell
# Hard reset to rollback branch
git reset --hard rollback/pre-main-merge-20251127

# Force push (if already pushed to remote - DANGEROUS)
git push origin main --force-with-lease

# Alert team, document incident
```

---

## Execution Checklist

### Pre-Merge
- [ ] Phase 0.1: Verify ground truth (branch, commit, changes)
- [ ] Phase 0.2: Create backup tag and snapshot
- [ ] Phase 1: Resolve submodule issues
- [ ] Phase 2: Create rollback branch and push to remote

### Merge
- [ ] Phase 3.1: Update main from remote
- [ ] Phase 3.2: Merge feature branch (no conflicts)
- [ ] Phase 3.3: Post-merge validation passes

### Consolidation
- [ ] Phase 4: Clean up merged feature branches
- [ ] Phase 5: Push main to remote
- [ ] Phase 6: Sync local directory changes
- [ ] Phase 7: Final validation (all gates pass)
- [ ] Phase 8: Update docs and cleanup

### Sign-Off
- [ ] All tests passing (≥180/196)
- [ ] No import errors
- [ ] No ACS violations
- [ ] Local and remote synchronized
- [ ] Rollback branch available
- [ ] Documentation updated

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Pre-flight | 5 min | 5 min |
| Phase 1: Submodules | 10 min | 15 min |
| Phase 2: Rollback | 2 min | 17 min |
| Phase 3: Merge | 15 min | 32 min |
| Phase 4: Branch cleanup | 10 min | 42 min |
| Phase 5: Push remote | 5 min | 47 min |
| Phase 6: Local sync | 20 min | 67 min |
| Phase 7: Validation | 10 min | 77 min |
| Phase 8: Docs/cleanup | 10 min | 87 min |
| **Total** | **~90 minutes** | **1.5 hours** |

**Buffer for issues**: +30 minutes  
**Total with buffer**: **2 hours**

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Merge conflicts | Medium | High | Rollback branch + abort option |
| Test failures | Medium | Medium | Phase 7 validation catches early |
| Submodule issues | High | Low | Phase 1 resolution |
| Lost local work | Low | High | Phase 0 backup + stash |
| Remote push fails | Low | Medium | Force-with-lease protection |

---

## Success Criteria Summary

**Merge is successful when**:
1. ✅ Main branch includes all 6 commits from feature branch
2. ✅ Rollback branch exists and is pushed to remote
3. ✅ All validation gates pass (compile, import, tests)
4. ✅ Local directory synchronized with repository
5. ✅ No uncommitted changes (clean `git status`)
6. ✅ Remote main matches local main
7. ✅ Documentation updated

**Ground Truth Verification**:
```powershell
git log --oneline -7 main | Select-String "auto-generate pattern drafts"
# Expected: Match found (commit is in main)

python scripts/test_imports.py
# Expected: "All imports successful!"

git status --short
# Expected: (empty)
```

---

## Next Steps After Merge

1. **Complete Phase 1 of Core Module Functionality** (from previous analysis):
   - Migrate missing adapters (`engine/adapters/` → `modules/core-engine/`)
   - Rewrite test imports (16 files)
   - Install missing dependencies

2. **Continue Module-Centric Plan**:
   - Phase 2: Validation & Testing
   - Phase 3: Archive Old Structure
   - Phase 4: Final Validation

3. **Activate Pattern Automation**:
   - Execute pattern activation plan
   - Integrate with orchestrator
   - Enable auto-detection

---

**Document Status**: READY FOR EXECUTION  
**Approval Required**: NO (safe operations with rollback)  
**Execution Pattern**: Manual (high-stakes merge)  
**Anti-Pattern Guards**: Active (all 11 enabled)

**Execute when ready**: Start with Phase 0 checkpoint verification
