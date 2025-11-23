# Additional Cleanup Recommendations - Round 2

**Analysis Date**: 2025-11-23  
**Current Repo Size**: ~14.4 MB (after first cleanup)  
**Additional Cleanup Potential**: ~3.5 MB (24%)

---

## 🎯 High-Priority Cleanup Targets

### 1. `.worktrees/` - 0.33 MB (35+ old worktrees)

**What**: Git worktree working directories from previous refactoring sessions  
**Status**: STALE - Most workstreams completed  
**Risk**: LOW - Git metadata remains, can be pruned

```powershell
# Check worktree status
git worktree list

# Prune old worktrees
git worktree prune

# Remove directory
Remove-Item -Recurse -Force .worktrees
```

**Recommendation**: ✅ **DELETE** - Completed workstreams, no longer needed

---

### 2. `QFT_updated/` - 0.17 MB (53 files)

**What**: "Quick Fix Template" system (appears to be old testing framework)  
**Last Modified**: 2025-11-13 (11 days ago)  
**Contents**: config, docs, examples, logs, scripts, src, tests

**Recommendation**: 🔍 **INVESTIGATE FIRST** - May be active development

**If inactive**:
```powershell
tar -czf legacy/QFT_updated_archived_2025-11-23.tar.gz QFT_updated/
Remove-Item -Recurse -Force QFT_updated
```

---

### 3. `.pytest_cache/` - 0.09 MB (5 files)

**What**: Pytest cache directory  
**Status**: Auto-generated, safe to delete

```powershell
Remove-Item -Recurse -Force .pytest_cache
```

**Recommendation**: ✅ **DELETE** - Add to `.gitignore`

---

### 4. `.claude/` - 0.14 MB (38 files)

**What**: Claude CLI cache/configuration  
**Status**: Tool-specific cache

**Recommendation**: ⚠️ **CONDITIONAL DELETE** - Check if actively using Claude CLI
- If yes: Keep
- If no: Delete and add to `.gitignore`

---

### 5. "bad excution" / "pipeline_plus" / "REFACTOR_PROJECT" - 0.08 MB

**What**: Typo directory + leftover project markers  
**Status**: Appears to be accidental/temporary

```powershell
# Investigate contents first
Get-ChildItem "bad excution" -Recurse
Get-ChildItem pipeline_plus -Recurse
Get-ChildItem REFACTOR_PROJECT -Recurse

# If junk, delete
Remove-Item -Recurse -Force "bad excution"
Remove-Item -Recurse -Force pipeline_plus
Remove-Item -Recurse -Force REFACTOR_PROJECT
```

**Recommendation**: ✅ **DELETE** - Clean up typos and markers

---

### 6. "What's working so well in `fastdev.md`" - 0.08 MB

**What**: Directory with backtick in name (Windows issue)  
**Status**: Improperly named directory

**Recommendation**: 🔄 **RENAME** or archive
```powershell
# Rename to valid directory name
Rename-Item "What's working so well in `fastdev.md" "whats-working-fastdev"
# OR move content to docs/
```

---

### 7. Hidden State Directories - 0.05 MB total

**Directories**:
- `.tasks/` (0 MB, 6 files)
- `.runs/` (0 MB, 2 files)
- `.ledger/` (0 MB, 1 file)
- `.quarantine/` (0 MB, 0 files)
- `.ai-orch/` (0.02 MB, 2 files)
- `.meta/` (0.03 MB, 5 files)
- `.aider/` (0 MB, 1 file)

**What**: Old execution state directories from AGENTIC_DEV_PROTOTYPE era  
**Status**: Superseded by current `.state/` directory

**Recommendation**: ✅ **DELETE** - Old state model, no longer used

```powershell
Remove-Item -Recurse -Force .tasks, .runs, .ledger, .quarantine, .ai-orch, .meta, .aider
```

---

### 8. `devdocs/archive/` - 0.51 MB (35 files)

**What**: Archived development documentation  
**Status**: Historical content, already archived

**Recommendation**: ⏭️ **COMPRESS** further
```powershell
cd devdocs
tar -czf ../legacy/devdocs_archive_2025-11-23.tar.gz archive/
Remove-Item -Recurse -Force archive
```

---

## 📊 Estimated Impact

### If All Recommended Deletions Applied:

| Item | Size | Action |
|------|------|--------|
| `.worktrees/` | 0.33 MB | Delete |
| `.pytest_cache/` | 0.09 MB | Delete + gitignore |
| `.claude/` | 0.14 MB | Delete (if unused) |
| Old state dirs | 0.05 MB | Delete |
| Junk dirs | 0.08 MB | Delete |
| `devdocs/archive/` | 0.51 MB | Compress to legacy |
| **Total Savings** | **~1.2 MB** | **(8% reduction)** |

### Conservative Cleanup (Safe Only):

```
.worktrees/         0.33 MB
.pytest_cache/      0.09 MB
bad excution/       0.04 MB
Old state dirs      0.05 MB
Total:              0.51 MB (3.5% reduction)
```

---

## 🔍 Investigation Needed

### 1. `QFT_updated/` (0.17 MB)
**Action**: Check with user if this is active development
```powershell
# View README
Get-Content QFT_updated\README.md

# Check recent git activity
git log --oneline --since="2 weeks ago" -- QFT_updated/
```

### 2. `engine/` (0.22 MB, 49 files)
**Question**: Is this separate from `core/engine/`?
```powershell
# Compare
Get-ChildItem engine -Recurse -File | Select-Object Name
Get-ChildItem core\engine -Recurse -File | Select-Object Name
```

### 3. `devdocs/sessions/` (0.71 MB, 20 files)
**Question**: Are old session transcripts needed?
**Recommendation**: Archive sessions older than 30 days

---

## 🎯 Recommended Execution Plan

### Phase 1: Safe Deletions (No Risk)
```powershell
# Delete caches and temp directories
Remove-Item -Recurse -Force .pytest_cache
Remove-Item -Recurse -Force .worktrees

# Delete old state directories
Remove-Item -Recurse -Force .tasks, .runs, .ledger, .quarantine, .ai-orch, .meta, .aider

# Delete junk directories
Remove-Item -Recurse -Force "bad excution"
Remove-Item -Recurse -Force pipeline_plus
Remove-Item -Recurse -Force REFACTOR_PROJECT

git add -A
git commit -m "chore: Clean up caches, old state dirs, and junk folders

- Removed .pytest_cache/ (auto-generated)
- Removed .worktrees/ (old git worktrees)
- Removed old state dirs (.tasks/, .runs/, .ledger/, etc.)
- Removed junk dirs (bad excution/, pipeline_plus/, REFACTOR_PROJECT/)

Space saved: ~0.5 MB"
```

### Phase 2: Conditional Cleanup (Check First)
```powershell
# 1. Check if Claude CLI is actively used
if (-not (Test-Path .claude\config.json)) {
    Remove-Item -Recurse -Force .claude
}

# 2. Investigate QFT_updated
# (Manual review needed)

# 3. Fix naming issue
Rename-Item "What's working so well in `fastdev.md" "whats-working-fastdev"
```

### Phase 3: Archive Old Sessions (Compress)
```powershell
# Archive old dev sessions
cd devdocs
tar -czf ../legacy/devdocs_archive_2025-11-23.tar.gz archive/
Remove-Item -Recurse -Force archive

# Archive old session transcripts (>30 days)
# (Need to identify which sessions)
```

---

## 📝 .gitignore Additions

After cleanup, add to `.gitignore`:
```gitignore
# Cache directories
.pytest_cache/
.aider.tags.cache.v4/
__pycache__/
*.pyc

# Tool caches
.aider/
.claude/
.ai-orch/

# Old state directories
.tasks/
.runs/
.ledger/
.quarantine/
.meta/

# Worktrees (managed separately)
.worktrees/

# Build artifacts
dist/
build/
*.egg-info/
```

---

## 🚨 DO NOT DELETE (Active)

These directories are **actively used**:
- ✅ `core/` - Production code
- ✅ `tests/` - Test suite
- ✅ `docs/` - Documentation
- ✅ `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` - Active framework
- ✅ `aim/`, `pm/`, `ccpm/` - Active modules
- ✅ `error/` - Error detection
- ✅ `specifications/` - Spec content
- ✅ `meta/` - Phase development docs
- ✅ `scripts/` - Utility scripts
- ✅ `devdocs/` - Development documentation (keep structure)
- ✅ `.state/` - Current state directory
- ✅ `legacy/` - Archive location

---

## Summary

### Conservative Cleanup (Recommended Now)
- **Size**: 0.51 MB saved (3.5%)
- **Risk**: None
- **Time**: 2 minutes
- **Items**: 
  - Delete caches
  - Delete old state dirs
  - Delete junk folders
  - Git commit

### Aggressive Cleanup (After Investigation)
- **Size**: 1.2 MB saved (8%)
- **Risk**: Low
- **Time**: 10 minutes
- **Items**:
  - All conservative items
  - Archive `QFT_updated/` (if inactive)
  - Archive `devdocs/archive/`
  - Delete `.claude/` (if unused)
  - Fix naming issues

---

**Next Action**: Proceed with conservative cleanup or investigate specific directories first?
