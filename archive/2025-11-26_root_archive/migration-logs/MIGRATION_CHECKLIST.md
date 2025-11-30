---
doc_id: DOC-GUIDE-MIGRATION-CHECKLIST-1141
---

# Documentation Migration Checklist

> **Date**: 2025-11-22  
> **Purpose**: Migrate development process documentation from `docs/` to `devdocs/`  
> **Script**: `scripts/migrate_docs_to_devdocs.ps1`

---

## Pre-Migration

- [ ] Review current `docs/` contents: `ls docs/*.md | measure`
- [ ] Verify `devdocs/` structure exists
- [ ] Ensure Git working directory is clean: `git status`
- [ ] Create backup branch: `git checkout -b backup/pre-docs-migration`
- [ ] Return to main branch: `git checkout main`

---

## Migration Execution

### 1. Dry Run (Preview Changes)

```powershell
.\scripts\migrate_docs_to_devdocs.ps1 -DryRun
```

**Review output for:**
- [ ] All expected files are found
- [ ] Target paths look correct
- [ ] No unexpected errors

### 2. Execute Migration

```powershell
.\scripts\migrate_docs_to_devdocs.ps1
```

**Expected results:**
- [ ] ~42 files moved to `devdocs/`
- [ ] ~3 stale files deleted
- [ ] 0 errors reported

### 3. Verify Git Status

```powershell
git status
```

**Should show:**
- [ ] Files renamed (moved) - Git preserves history
- [ ] Files deleted
- [ ] No untracked files

---

## Post-Migration Validation

### 1. Check File Counts

```powershell
# Before: ~75 files in docs/
(Get-ChildItem docs/*.md).Count

# After: ~33 files in docs/ (user-facing only)
# After: ~45+ files in devdocs/ (dev artifacts)
(Get-ChildItem devdocs -Recurse -Filter *.md).Count
```

### 2. Verify History Preservation

```powershell
# Pick a moved file and verify history is intact
git log --follow devdocs/phases/aim/PHASE_1AB_COMPLETE.md
```

### 3. Check for Broken Links

```powershell
# Run link checker (if available)
python scripts/validate_documentation.py --check-links

# Or manually search for old paths
rg "docs/AIM_PLUS_" docs/
rg "docs/PHASE_K" docs/
rg "docs/UET_INTEGRATION_PLAN" .
```

---

## Link Updates

### Common Patterns to Fix

**Old pattern:**
```markdown
[Phase K Plan](docs/PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md)
```

**New pattern:**
```markdown
[Phase K Plan](devdocs/phases/phase-k/PLAN.md)
```

### Files Likely Needing Updates

- [ ] `README.md` - Update links to phase plans
- [ ] `DIRECTORY_GUIDE.md` - Update documentation section
- [ ] `docs/DOCUMENTATION_INDEX.md` - Update links to moved files
- [ ] `docs/ARCHITECTURE.md` - Update references to phase completions
- [ ] `QUICK_START.md` - Update workflow links

### Automated Link Update

```powershell
# Search for broken links
rg --files-with-matches "docs/(AIM_PLUS_|PHASE_K|UET_INTEGRATION|PHASE_PLAN|PHASE_ROADMAP)" .

# Update with sed/PowerShell as needed
```

---

## Commit Strategy

### Option A: Single Commit (Recommended)

```powershell
git add -A
git commit -m "docs: migrate development artifacts to devdocs/

- Move 42 phase plans, completion reports, and execution summaries
- Move analysis reports and planning documents
- Delete 3 stale auto-generated index files
- Preserve Git history with git mv

Follows FILE_ORGANIZATION_SYSTEM.md specification:
- docs/ now contains only user-facing documentation
- devdocs/ contains all development process records

Files moved:
- AIM phase completions → devdocs/phases/aim/
- Phase K docs → devdocs/phases/phase-k/
- UET integration → devdocs/phases/phase-h/
- Analysis reports → devdocs/analysis/
- Planning docs → devdocs/planning/
- Execution summaries → devdocs/execution/

See MIGRATION_CHECKLIST.md for details."
```

### Option B: Staged Commits

```powershell
# Commit 1: Move files
git add -A
git commit -m "docs: move development artifacts to devdocs/ (file moves only)"

# Commit 2: Update links (after fixing)
git add -A
git commit -m "docs: update links after devdocs migration"
```

---

## Validation Tests

### 1. Documentation Index Still Works

```powershell
# Check main index still loads
cat docs/DOCUMENTATION_INDEX.md

# Verify implementation locations still valid
cat docs/IMPLEMENTATION_LOCATIONS.md
```

### 2. Critical Docs Still Accessible

- [ ] `docs/ARCHITECTURE.md` exists
- [ ] `docs/CONFIGURATION_GUIDE.md` exists
- [ ] `docs/workstream_authoring_guide.md` exists
- [ ] `docs/adr/` directory intact

### 3. No Duplicate Files

```powershell
# Check for any duplicates
Get-ChildItem -Recurse -Filter "*.md" | Group-Object Name | Where-Object { $_.Count -gt 1 }
```

---

## Rollback Plan (If Needed)

```powershell
# If migration fails, reset to backup branch
git reset --hard HEAD
git checkout backup/pre-docs-migration

# Or revert the commit
git revert HEAD
```

---

## Files Moved (Reference)

### Phase Completions (18 files)
- AIM_PLUS_INTEGRATION_PLAN.md → devdocs/execution/
- AIM_PLUS_PHASE_*.md (8 files) → devdocs/phases/aim/
- AIM_PLUS_*_SUMMARY.md (3 files) → devdocs/execution/
- PHASE_K*.md (4 files) → devdocs/phases/phase-k/
- UET_*.md (5 files) → devdocs/phases/phase-h/ and devdocs/execution/

### Planning & Analysis (11 files)
- PHASE_PLAN.md → devdocs/planning/
- PHASE_ROADMAP.md → devdocs/planning/
- DEPRECATION_PLAN.md → devdocs/planning/
- FILE_ORGANIZATION_VISUAL.md → devdocs/planning/
- *_ANALYSIS.md (3 files) → devdocs/analysis/
- *_INVENTORY.md → devdocs/analysis/
- *_ASSESSMENT.md → devdocs/analysis/

### Execution Summaries (4 files)
- COMPLETE_IMPLEMENTATION_SUMMARY.md → devdocs/execution/
- ENGINE_STATUS.md → devdocs/execution/
- FILE_ORGANIZATION_IMPLEMENTATION_SUMMARY.md → devdocs/execution/
- phase-github-issues-resolution.md → devdocs/execution/

### Archive (2 files)
- ARCHIVE_2025-11-22_SUMMARY.md → devdocs/archive/2025-11/
- DOCUMENTATION_INDEX_OLD.md → devdocs/archive/2025-11/

### Deleted (3 files)
- DOCUMENTATION_INDEX_AUTO.md
- DOCUMENTATION_INDEX_GENERATED.md
- IMPLEMENTATION_LOCATIONS_AUTO.md

---

## Success Criteria

- [ ] All 42 files successfully moved with `git mv`
- [ ] All 3 stale files deleted
- [ ] Git history preserved (verify with `git log --follow`)
- [ ] No broken internal links in remaining `docs/` files
- [ ] `docs/DOCUMENTATION_INDEX.md` updated to reflect new structure
- [ ] CI/build passes (if applicable)
- [ ] Migration committed with descriptive message

---

## Post-Migration Tasks

- [ ] Update `docs/FILE_ORGANIZATION_SYSTEM.md` examples (if needed)
- [ ] Update `DIRECTORY_GUIDE.md` to reflect new structure
- [ ] Regenerate `docs/DOCUMENTATION_INDEX.md` (if automated)
- [ ] Update any CI/CD scripts that reference moved files
- [ ] Notify team of new file locations

---

## Notes

**Why Git mv?**
- Preserves full file history
- GitHub/Git UI shows renames properly
- Easier to track changes across the move

**Why not delete phase completions?**
- Historical record of what was built
- Useful for understanding architecture decisions
- Kept in `devdocs/` for reference but excluded from releases

**Reference:**
- `docs/FILE_ORGANIZATION_SYSTEM.md` - Full specification
- `docs/FILE_ORGANIZATION_QUICK_REF.md` - Quick reference guide
