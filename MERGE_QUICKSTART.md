# Safe Merge Strategy - Quick Start Guide

**Document**: Quick reference for executing safe merge strategy  
**Created**: 2025-11-27  
**Status**: READY TO EXECUTE

---

## TL;DR - Execute Now

```powershell
# Review the plan first
Get-Content SAFE_MERGE_STRATEGY.md

# Execute automated merge (with confirmations)
.\scripts\execute_safe_merge.ps1

# Or execute with dry run first
.\scripts\execute_safe_merge.ps1 -DryRun

# Or fully automated (no confirmations)
.\scripts\execute_safe_merge.ps1 -AutoYes
```

---

## What This Does

**Objective**: Safely merge 6 commits from `feature/uet-compat-shims` into `main` with rollback capability.

**Changes Being Merged**:
- 148 files modified
- +10,485 insertions
- -1,436 deletions
- 6 commits including:
  - Module-centric architecture migration
  - Pattern automation activation
  - Import compatibility shims

**Time Required**: ~90 minutes (or ~10 minutes automated)

---

## Pre-Execution Checklist

Before running the merge script:

- [ ] You're on `feature/uet-compat-shims` branch
- [ ] You have no critical uncommitted work
- [ ] You have ~90 minutes available (or can run automated)
- [ ] You have network access (for pushing to remote)
- [ ] You understand rollback procedure

---

## Execution Options

### Option 1: Fully Automated (Recommended)

```powershell
# Execute with automatic confirmations
.\scripts\execute_safe_merge.ps1 -AutoYes

# Time: ~10 minutes
# Risk: Low (rollback branch created automatically)
```

### Option 2: Interactive (Safer)

```powershell
# Execute with confirmation prompts
.\scripts\execute_safe_merge.ps1

# Time: ~15 minutes
# Risk: Very Low (you approve each phase)
```

### Option 3: Manual (Full Control)

Follow the phases in `SAFE_MERGE_STRATEGY.md` manually.

```powershell
# Time: ~90 minutes
# Risk: Very Low (maximum control)
```

---

## What Gets Created

**Rollback Branch**: `rollback/pre-main-merge-YYYYMMDD-HHMMSS`
- Pushed to remote
- Can restore with: `git reset --hard rollback/pre-main-merge-YYYYMMDD-HHMMSS`

**Backup Directory**: `.merge-backup/`
- Stash list
- Commits being merged
- Local change analysis
- Test results

**Snapshot Tag**: `pre-merge-snapshot-YYYYMMDD-HHMMSS`
- Additional safety point

---

## Phases Executed

| Phase | What It Does | Time |
|-------|--------------|------|
| 0 | Pre-flight checks & backups | 5 min |
| 1 | Resolve submodule issues | 10 min |
| 2 | Create rollback branch | 2 min |
| 3 | Merge to main + validate | 15 min |
| 5 | Push to remote | 5 min |

**Skipped in automation** (do manually later):
- Phase 4: Branch cleanup
- Phase 6: Local directory sync
- Phase 7: Full validation
- Phase 8: Documentation

---

## Success Indicators

After successful merge:

```powershell
# Check merge completed
git log --oneline -7 main | Select-String "auto-generate pattern drafts"
# Expected: Match found

# Check imports work
python scripts/test_imports.py
# Expected: "All imports successful!"

# Check compilation
python -m compileall modules/ -q
# Expected: Exit code 0 (no output)

# Check clean status
git status --short
# Expected: (empty or only submodule changes)
```

---

## If Something Goes Wrong

### During Merge (Conflicts)

```powershell
# Abort merge
git merge --abort

# Return to feature branch
git checkout feature/uet-compat-shims

# Review conflicts, fix manually
```

### After Merge (Tests Failing)

```powershell
# Soft rollback (keeps changes for inspection)
git reset --soft rollback/pre-main-merge-YYYYMMDD-HHMMSS

# Review what went wrong
git diff HEAD

# Fix and recommit
```

### Nuclear Option (Critical Failure)

```powershell
# Hard reset to pre-merge state
git reset --hard rollback/pre-main-merge-YYYYMMDD-HHMMSS

# If already pushed to remote (DANGEROUS)
git push origin main --force-with-lease
```

---

## After Merge - Next Steps

### Immediate (Do Today)

1. **Verify tests pass**:
   ```powershell
   pytest tests/ -v
   ```

2. **Check for missing adapters**:
   ```powershell
   # Follow Phase 1 of core module functionality plan
   # (see previous analysis)
   ```

3. **Install missing dependencies**:
   ```powershell
   pip install filelock pyyaml jinja2 psutil
   ```

### Soon (This Week)

4. **Clean up feature branches**:
   ```powershell
   git branch --merged main
   git branch -d feature/uet-compat-shims
   git push origin --delete feature/uet-compat-shims
   ```

5. **Update documentation**:
   - Mark migration complete in `REMAINING_MODULE_CENTRIC_PLAN.md`
   - Update `PROGRESS_REPORT.md`

6. **Complete core module functionality**:
   - Migrate adapters
   - Rewrite test imports
   - Run validation gates

### Later (This Month)

7. **Activate pattern automation** (from merged code)
8. **Archive old structure** (Phase 3 of Module-Centric plan)
9. **Final validation** (Phase 4 of Module-Centric plan)

---

## FAQ

**Q: Is this safe?**  
A: Yes. Rollback branch and snapshot tag provide two safety nets.

**Q: Can I undo the merge?**  
A: Yes. Use `git reset --hard rollback/pre-main-merge-YYYYMMDD-HHMMSS`

**Q: What if tests fail after merge?**  
A: Expected - 24 test files need import path updates. That's the next task.

**Q: Will this affect my local work?**  
A: No uncommitted work detected. Submodule pointers will update (safe).

**Q: Should I use -AutoYes?**  
A: Yes if you trust the automation. No if you want to review each step.

**Q: How long does this take?**  
A: Automated: ~10 min. Interactive: ~15 min. Manual: ~90 min.

**Q: What if I see merge conflicts?**  
A: Unlikely (all changes are in feature branch). But if they occur, script aborts safely.

---

## Command Reference

```powershell
# Dry run (see what would happen)
.\scripts\execute_safe_merge.ps1 -DryRun

# Interactive (confirm each phase)
.\scripts\execute_safe_merge.ps1

# Automated (no confirmations)
.\scripts\execute_safe_merge.ps1 -AutoYes

# Skip tests (faster)
.\scripts\execute_safe_merge.ps1 -AutoYes -SkipTests

# Rollback
git reset --hard rollback/pre-main-merge-YYYYMMDD-HHMMSS

# Check merge status
git log --oneline --graph --all --decorate -20

# Verify imports
python scripts/test_imports.py

# Run tests
pytest tests/ -v
```

---

## Decision Matrix

| Scenario | Recommended Action |
|----------|-------------------|
| I want fastest merge | `-AutoYes -SkipTests` |
| I want safest merge | Interactive (no flags) |
| I want to review first | `-DryRun` then decide |
| I'm not sure | Read `SAFE_MERGE_STRATEGY.md` first |
| Tests are failing | Normal - fix in next phase |
| Merge conflicts | `git merge --abort`, review manually |

---

## Ground Truth Verification

**Before merge**:
```powershell
git branch --show-current
# Expected: feature/uet-compat-shims

git rev-list --count main..HEAD
# Expected: 6
```

**After merge**:
```powershell
git branch --show-current
# Expected: main

git log --oneline -1
# Expected: "Merge feature/uet-compat-shims..."

python scripts/test_imports.py
# Expected: "All imports successful!"
```

---

## Ready to Execute?

```powershell
# Review plan one more time
Get-Content SAFE_MERGE_STRATEGY.md | Select-Object -First 50

# Execute when ready
.\scripts\execute_safe_merge.ps1 -AutoYes

# Or start with dry run
.\scripts\execute_safe_merge.ps1 -DryRun
```

---

**Status**: READY  
**Risk Level**: LOW (with rollback)  
**Approval**: NOT REQUIRED (automated safety)  
**Execution Time**: 10-15 minutes  
**Rollback Time**: 2 minutes

**GO/NO-GO**: ✅ GO when ready
