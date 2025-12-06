---
doc_id: DOC-GUIDE-SAFE-MERGE-STRATEGY-238
---

# Safe Merge Strategy - Preserve Today's Updates

**Date**: 2025-12-05
**Purpose**: Safely merge/commit today's cleanup work while preserving all changes

---

## Current Changes Summary

### 📝 New Files (2)
1. `CACHE_FOLDERS_EXPLAINED.md` - Cache folder documentation
2. `gui/DOC_UI_ARCHITECTURE_OVERVIEW.md` - UI architecture doc (moved from project_knowledge/)

### ✏️ Modified Files (1)
1. `phase1_planning/modules/workstream_planner/docs/plans/ccpm` - Directory change

### 🗑️ Deleted Files (1)
1. `project_knowledge/DOC_UI_ARCHITECTURE_OVERVIEW.md` - Moved to gui/

**Total**: 4 changes to preserve

---

## Safe Merge Strategy - Option 1: Commit All Changes

### Step 1: Stage All Changes
```bash
# Add new documentation files
git add CACHE_FOLDERS_EXPLAINED.md
git add gui/DOC_UI_ARCHITECTURE_OVERVIEW.md

# Add modified directory
git add phase1_planning/modules/workstream_planner/docs/plans/ccpm

# Stage deletion (file was moved)
git add project_knowledge/DOC_UI_ARCHITECTURE_OVERVIEW.md

# Verify staging
git status
```

### Step 2: Commit with Descriptive Message
```bash
git commit -m "chore: cleanup - remove empty directories and reorganize docs

Changes:
- Remove empty project_knowledge/ directory
- Move DOC_UI_ARCHITECTURE_OVERVIEW.md to gui/ (correct location)
- Add CACHE_FOLDERS_EXPLAINED.md documentation
- Update phase1 ccpm directory structure

Rationale:
- project_knowledge/ was empty and unused (0 files)
- UI architecture doc belongs in gui/ directory
- New documentation explains cache folders (.ruff_cache, __pycache__)
"
```

### Step 3: Push Changes (if applicable)
```bash
# Check current branch
git branch --show-current

# Push to remote
git push origin <branch-name>
```

---

## Safe Merge Strategy - Option 2: Stash and Merge

If you need to merge from another branch first:

### Step 1: Stash Current Changes
```bash
# Save all changes with descriptive message
git stash push -m "cleanup: cache docs and project_knowledge removal"

# Verify stash
git stash list
```

### Step 2: Merge or Pull
```bash
# Pull latest from remote
git pull origin main

# OR merge from another branch
git merge <branch-name>
```

### Step 3: Restore Stashed Changes
```bash
# Apply stashed changes
git stash pop

# OR apply without removing from stash
git stash apply
```

### Step 4: Resolve Conflicts (if any)
```bash
# Check for conflicts
git status

# If conflicts exist, resolve manually then:
git add <resolved-files>
git commit
```

---

## Safe Merge Strategy - Option 3: Create Feature Branch

For maximum safety, use a feature branch:

### Step 1: Create Feature Branch
```bash
# Create and switch to new branch
git checkout -b cleanup/remove-empty-directories

# Verify branch
git branch --show-current
```

### Step 2: Commit Changes
```bash
# Stage all changes
git add -A

# Commit
git commit -m "chore: cleanup empty directories and reorganize docs"

# Push feature branch
git push origin cleanup/remove-empty-directories
```

### Step 3: Merge via Pull Request
- Create PR on GitHub/GitLab
- Review changes
- Merge when ready

---

## Verification Checklist

Before committing, verify:

- [ ] All new documentation files are present
  - [ ] `CACHE_FOLDERS_EXPLAINED.md` exists
  - [ ] `gui/DOC_UI_ARCHITECTURE_OVERVIEW.md` exists

- [ ] Moved file tracked correctly
  - [ ] Git recognizes file move (not delete + add)
  - [ ] File content preserved

- [ ] Empty directories removed
  - [ ] `project_knowledge/` no longer exists
  - [ ] No other empty directories accidentally removed

- [ ] Cache directories untouched
  - [ ] `.ruff_cache/` still exists (in .gitignore)
  - [ ] `__pycache__/` still exists (in .gitignore)

---

## Quick Commands Reference

### Check Current Status
```bash
git status
git status --short
```

### Stage Specific Files
```bash
git add <filename>
git add -A                # Add all changes
git add -u                # Add modified/deleted only
```

### Commit with Message
```bash
git commit -m "message"
git commit -am "message"  # Add + commit modified files
```

### Undo Staging (if needed)
```bash
git reset HEAD <file>     # Unstage specific file
git reset HEAD            # Unstage all
```

### View Diff Before Committing
```bash
git diff                  # Unstaged changes
git diff --staged         # Staged changes
```

---

## Recommended Approach

**For this cleanup work, I recommend Option 1 (Direct Commit)**:

1. Changes are well-documented
2. All changes are intentional cleanup
3. Low risk (documentation only, no code changes)
4. Easy to revert if needed

**Execute:**
```bash
# Stage all changes
git add -A

# Commit with clear message
git commit -m "chore: cleanup - remove empty directories and reorganize docs

- Remove empty project_knowledge/ directory (0 files)
- Move DOC_UI_ARCHITECTURE_OVERVIEW.md to gui/ directory
- Add CACHE_FOLDERS_EXPLAINED.md documentation
- Update phase1 planning directory structure

All changes verified safe and intentional from 2025-12-05 cleanup session.
"

# Push (if working on a branch)
git push origin <branch-name>
```

---

## Rollback Plan (If Needed)

If you need to undo after committing:

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)
```bash
git reset --hard HEAD~1
```

### Restore Specific File
```bash
git checkout HEAD~1 -- <filename>
```

---

## Today's Work Summary

### Folder Overlap Analysis ✅
- Created `FOLDER_OVERLAP_ANALYSIS.md`
- Created `FOLDER_OVERLAP_FINAL_REPORT.md`
- Created `CONSOLIDATION_ACTION_PLAN.md`
- Created `CONSOLIDATION_QUICK_SUMMARY.txt`

### UET Directory Archive ✅
- Archived `uet/` to `_ARCHIVE/uet_planning_workspace_20251204_155747/`
- Created `UET_DIRECTORY_ANALYSIS.md`
- Created `UET_ARCHIVE_COMPLETE_REPORT.md`
- Updated `README.md` and `PHASE_DIRECTORY_MAP.md`

### Cache Folders Cleanup ✅
- Analyzed `.ruff_cache/`, `__pycache__/`, `project_knowledge/`
- Created `CACHE_FOLDERS_EXPLAINED.md`
- Removed empty `project_knowledge/` directory
- Moved `DOC_UI_ARCHITECTURE_OVERVIEW.md` to `gui/`

---

## Git Commit Message Template

```
chore(cleanup): remove empty directories and reorganize documentation

Changes:
- Remove empty project_knowledge/ directory
  - Directory was created for AI context but never used (0 files)
  - One file (DOC_UI_ARCHITECTURE_OVERVIEW.md) moved to gui/ before removal

- Add new documentation
  - CACHE_FOLDERS_EXPLAINED.md: Explains .ruff_cache, __pycache__, project_knowledge

- Reorganize UI documentation
  - Move DOC_UI_ARCHITECTURE_OVERVIEW.md from project_knowledge/ to gui/
  - Correct location for UI architecture documentation

- Update phase1 planning structure
  - Minor directory updates in workstream_planner/docs/plans/ccpm

Verification:
- All changes verified safe (no code changes, documentation only)
- Cache directories (.ruff_cache, __pycache__) preserved and in .gitignore
- Empty directories removed, active files preserved

Session: 2025-12-05 cleanup
```

---

## Status: Ready to Commit ✅

All changes are:
- ✅ Documented
- ✅ Verified safe
- ✅ Well-organized
- ✅ Easy to revert if needed

**Next step**: Execute Option 1 (Direct Commit) or choose your preferred strategy above.
