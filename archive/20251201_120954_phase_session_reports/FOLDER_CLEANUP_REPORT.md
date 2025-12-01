# Folder Overlap and Cleanup Report

**Generated**: 2025-12-01
**Purpose**: Identify and safely remove deprecated/overlapping folders

---

## Executive Summary

✅ **Found 8 deprecated folders** consuming disk space and causing confusion  
✅ **6 folders safe to archive** (no active Python code)  
⚠️  **2 folders need review** (contains Python files still referenced)  
✅ **UET overlaps already resolved** (core/, error/, aim/, pm/ already archived)

---

## Category 1: Safe to Archive (6 folders)

These folders contain **only documentation and planning files** - no active Python code.

### 1. `Module-Centric/` (34 files)
- **Content**: Architecture docs, migration guides, developer guides
- **Status**: Documentation migrated to `docs/`
- **Safe**: Yes - all markdown files

### 2. `REFACTOR_2/` (39 files)
- **Content**: Planning and architecture documents for refactor
- **Status**: Completed refactor, docs archived
- **Safe**: Yes - planning materials only

### 3. `bring_back_docs_/` (10 files)
- **Content**: Recovered documentation, consolidation manifests
- **Status**: Content should be in `docs/` folder
- **Safe**: Yes - recovery documents

### 4. `ToDo_Task/` (74 files)
- **Content**: Task planning, tracking materials, Claude plans
- **Status**: Experimental/sandbox content
- **Safe**: Yes - no active code

### 5. `AI_SANDBOX/` (4 files)
- **Content**: AI experimentation sandbox with template structures
- **Status**: Experimental area with minimal content
- **Safe**: Yes - sandbox only

### 6. `ai-logs-analyzer/` (20 files)
- **Content**: Config and documentation for log analysis
- **Status**: No Python implementation found
- **Safe**: Yes - config files only

---

## Category 2: Needs Manual Review (2 folders)

### 1. `src/` (3 Python files) ⚠️

**Status**: DEPRECATED - superseded by `core.*`, `error.*` imports

**Python Files**:
- `orchestrator.py`
- `path_registry.py`  
- `plugins/` directory

**Referenced By** (10 files still import from src):
```python
./aider/engine.py:1
./tests/test_path_registry.py:3
./tests/test_parallel_orchestrator.py:1
./tests/test_parallel_dependencies.py:1
./tests/orchestrator/test_parallel_src.py:3
./scripts/auto_migrate_imports.py:1
./scripts/gh_issue_update.py:1
./scripts/gh_epic_sync.py:1
./scripts/dev/paths_resolve_cli.py:1
```

**Action Required**:
1. Update imports from `from src.*` to `from core.*` or `from error.*`
2. Run tests to verify no breakage
3. Then archive `src/` folder

**Estimated Time**: 30 minutes

---

### 2. `abstraction/` (20 files, 1 Python) ⚠️

**Status**: Old workstream generation system, superseded by UET

**Python File**:
- `implement_all_phases.py` - Workstream generation script

**Content**:
- Workstream specs (JSON)
- Phase planning docs
- Generation reports

**Referenced By**: No imports found (safe from import perspective)

**Action Required**:
1. Review `implement_all_phases.py` to see if logic needed
2. Check if workstream generation moved to UET
3. Archive if no longer needed

**Estimated Time**: 15 minutes

---

## Category 3: Already Resolved ✅

These overlaps were already handled by previous cleanup:

### UET Migration (Already Archived)

| Old Folder | New Location | Status |
|------------|-------------|--------|
| `core/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/` | ✅ Archived |
| `error/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/` | ✅ Archived |
| `aim/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/aim/` | ✅ Archived |
| `pm/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/pm/` | ✅ Archived |

**Archive Location**: `archive/2025-12-01_091928_old-root-folders/`

---

## Cleanup Execution Plan

### Step 1: Run Safe Cleanup (10 minutes)

Archive the 6 safe folders with no Python code:

```bash
# This script archives safe folders automatically
python safe_cleanup_deprecated_folders.py
```

**What it does**:
- Creates timestamped archive: `archive/{timestamp}_deprecated_folders_cleanup/`
- Moves 6 folders to archive
- Creates README.md explaining what was archived
- Generates cleanup_summary.json

**Result**: 
- Removes 181 files (docs/planning only)
- Reduces root folder clutter by 6 folders

---

### Step 2: Fix src/ Imports (30 minutes)

Update the 10 files that import from `src/`:

```python
# Create import update script
python -c "
import re
from pathlib import Path

IMPORT_MAP = {
    r'from src\.orchestrator': 'from core.engine.orchestrator',
    r'from src\.path_registry': 'from core.state.path_registry',
    r'from src\.plugins': 'from error.plugins',
    r'import src\.': 'import core.',
}

def fix_imports(file_path):
    content = file_path.read_text()
    original = content
    
    for old, new in IMPORT_MAP.items():
        content = re.sub(old, new, content)
    
    if content != original:
        file_path.write_text(content)
        print(f'✅ Updated: {file_path}')

# Fix files
for f in [
    'aider/engine.py',
    'tests/test_path_registry.py',
    'tests/test_parallel_orchestrator.py',
    'tests/test_parallel_dependencies.py',
    'tests/orchestrator/test_parallel_src.py',
    'scripts/auto_migrate_imports.py',
    'scripts/gh_issue_update.py',
    'scripts/gh_epic_sync.py',
    'scripts/dev/paths_resolve_cli.py',
]:
    fix_imports(Path(f))
"
```

Then verify:
```bash
# Run tests
pytest tests/ -v

# Check for remaining src imports
grep -r "from src\." --include="*.py" | wc -l
# Should be 0
```

---

### Step 3: Review abstraction/ (15 minutes)

Check if `implement_all_phases.py` is still needed:

```bash
# View the file
cat abstraction/implement_all_phases.py

# Check if similar functionality exists in UET
ls -la UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/
```

If not needed, archive:
```bash
mv abstraction archive/{timestamp}_deprecated_folders_cleanup/
```

---

### Step 4: Verify and Commit (10 minutes)

```bash
# Check no imports broken
pytest tests/ -k "not slow"

# Verify folder count
ls -ld */ | wc -l
# Should be 8 fewer than before

# Commit
git add .
git commit -m "chore: Archive 8 deprecated folders

- Archived: Module-Centric, REFACTOR_2, bring_back_docs_, ToDo_Task, AI_SANDBOX, ai-logs-analyzer
- Fixed imports from src/ to core.*/error.*
- Archived abstraction/ and src/ after review
- All code migrated to UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
- Archive location: archive/{timestamp}_deprecated_folders_cleanup/"

git push
```

---

## Expected Results

### Before Cleanup
```
Repository structure:
├── Module-Centric/          (34 files - docs)
├── REFACTOR_2/              (39 files - planning)
├── bring_back_docs_/        (10 files - recovery)
├── ToDo_Task/               (74 files - sandbox)
├── AI_SANDBOX/              (4 files - experimental)
├── ai-logs-analyzer/        (20 files - config)
├── src/                     (3 files - deprecated code)
├── abstraction/             (20 files - old system)
└── archive/
```

### After Cleanup
```
Repository structure:
├── UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/  (canonical code)
├── docs/                                     (all documentation)
├── tests/                                    (updated imports)
└── archive/
    ├── 2025-12-01_091928_old-root-folders/   (UET migration)
    └── {timestamp}_deprecated_folders_cleanup/  (8 folders)
        ├── Module-Centric/
        ├── REFACTOR_2/
        ├── bring_back_docs_/
        ├── ToDo_Task/
        ├── AI_SANDBOX/
        ├── ai-logs-analyzer/
        ├── src/
        ├── abstraction/
        └── README.md (explains archive)
```

### Benefits
- ✅ **204 files archived** (8 deprecated folders)
- ✅ **8 fewer root folders** to navigate
- ✅ **Clear separation**: active code vs archived
- ✅ **Single source of truth**: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
- ✅ **Easier onboarding**: less confusion about folder purpose

---

## Rollback Plan

If you need to restore any folder:

```bash
# Restore specific folder
cp -r archive/{timestamp}_deprecated_folders_cleanup/{folder} ./

# Or restore all
cp -r archive/{timestamp}_deprecated_folders_cleanup/* ./

# Or use git
git revert HEAD
```

---

## Tools Created

### 1. `analyze_overlap.py`
**Purpose**: Analyze deprecated folders and identify overlaps  
**Output**: `overlap_analysis_report.json`

```bash
python analyze_overlap.py
```

### 2. `safe_cleanup_deprecated_folders.py`
**Purpose**: Safely archive deprecated folders with full documentation  
**Output**: Archive directory with README and summary

```bash
python safe_cleanup_deprecated_folders.py
```

### 3. `overlap_analysis_report.json`
**Purpose**: Machine-readable report of all findings  
**Contains**: Folder stats, recommendations, file counts

---

## Timeline

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Run analysis | 5 min | ✅ Complete |
| 2 | Run safe cleanup | 10 min | ⏸️ Ready |
| 3 | Fix src/ imports | 30 min | ⏸️ Pending |
| 4 | Review abstraction/ | 15 min | ⏸️ Pending |
| 5 | Verify & commit | 10 min | ⏸️ Pending |
| **Total** | | **70 min** | |

---

## References

- `FOLDER_OVERLAP_ANALYSIS.md` - Original UET overlap analysis
- `OLD_FOLDERS_CLEANUP_PLAN.md` - Detailed cleanup recommendations
- `FOLDER_CLASSIFICATION.yaml` - Module classification system
- `overlap_analysis_report.json` - Automated analysis output

---

## Conclusion

**Ready to proceed**: Run `python safe_cleanup_deprecated_folders.py` to archive 6 safe folders immediately.

**Action required**: Review and fix `src/` imports (30 min) and `abstraction/` (15 min) before archiving those.

**Total time**: ~70 minutes to complete full cleanup.
