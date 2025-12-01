# Old Folders Cleanup Plan

**Date**: 2025-12-01 15:15 UTC  
**Goal**: Remove old duplicate folders safely  
**Status**: Analysis Complete - Action Plan Ready

---

## ⚠️ IMPORTANT: NOT SAFE TO DELETE YET

### Current Situation

The following old folders still exist and **ARE STILL IN USE**:

| Folder | Files | Status | Imports Found |
|--------|-------|--------|---------------|
| `core/` | 84 files | ⚠️ **ACTIVE** | 150+ files import from this |
| `error/` | 66 files | ⚠️ **ACTIVE** | 50+ files import from this |
| `aim/` | 85 files | ⚠️ **ACTIVE** | 30+ files import from this |
| `pm/` | 78 files | ⚠️ **ACTIVE** | 10+ files import from this |
| `scripts/` | 146 files | ⚠️ **ACTIVE** | Some duplicates exist |

**Why not safe to delete**: **150+ files still import from old paths!**

---

## 🔍 Analysis Results

### Import Usage Check
```bash
# Files importing from old paths:
grep -r "from core\." --include="*.py" | wc -l
# Result: 150+ files still using old core.* imports
```

### Examples of Active Imports
```python
# These files are STILL importing from old paths:
from core.state import db                    # ❌ Old path
from error.engine.error_engine import ...    # ❌ Old path
from aim.bridge import get_tool_info         # ❌ Old path
from pm.bridge import ...                    # ❌ Old path

# Should be:
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state import db     # ✅ New path
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine import ... # ✅ New path
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.bridge import ...    # ✅ New path
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.bridge import ...     # ✅ New path
```

---

## 📋 Safe Cleanup Process (3 Steps)

### Step 1: Update All Imports (REQUIRED FIRST)

**This must be done before deleting any folders!**

```powershell
# Create import rewrite script
@'
import re
from pathlib import Path

IMPORT_MAP = {
    r"from core\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.",
    r"from error\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.",
    r"from aim\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.",
    r"from pm\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.",
    r"import core\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.",
    r"import error\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.",
    r"import aim\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.",
    r"import pm\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.",
}

def rewrite_imports(file_path: Path):
    """Rewrite old imports to UET paths."""
    if "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" in str(file_path):
        return False  # Skip UET files
    if "archive" in str(file_path):
        return False  # Skip archived files
    if "legacy" in str(file_path):
        return False  # Skip legacy files
        
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    for old_pattern, new_prefix in IMPORT_MAP.items():
        content = re.sub(old_pattern, new_prefix, content)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Updated: {file_path}")
        return True
    return False

# Execute
root = Path(".")
updated = 0
for py_file in root.rglob("*.py"):
    if rewrite_imports(py_file):
        updated += 1

print(f"\n✅ Updated {updated} files")
'@ | Out-File "scripts\rewrite_all_imports.py" -Encoding UTF8

# Run the script
python scripts\rewrite_all_imports.py
```

**Expected**: 150+ files updated

### Step 2: Verify No Broken Imports

```bash
# Run tests
pytest tests/ -v

# Check for import errors
python -c "
import sys
sys.path.insert(0, 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK')

# Try importing key modules
from core.state import db
from error.engine.error_engine import ErrorEngine
from aim.bridge import get_tool_info
print('✅ All imports working')
"
```

### Step 3: Archive Old Folders

**Only after Step 1 & 2 are complete!**

```powershell
# Create archive directory
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
$archiveDir = "archive\${date}_old-root-folders"
New-Item -ItemType Directory -Path $archiveDir -Force

# Move old folders to archive
$foldersToArchive = @("core", "error", "aim", "pm")

foreach ($folder in $foldersToArchive) {
    if (Test-Path $folder) {
        Move-Item $folder "$archiveDir\$folder"
        Write-Host "✅ Archived: $folder"
    }
}

# Create README
@"
# Archived Root Folders - $date

These folders were archived after updating all imports to UET paths.

## Folders Archived
- core/ (84 files)
- error/ (66 files)
- aim/ (85 files)
- pm/ (78 files)

## Reason
All imports updated to use UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK paths.
Canonical versions are in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.

## Restoration
To restore (if needed):
git checkout uet-migration-complete-20251201
"@ | Out-File "$archiveDir\README.md"

# Commit
git add .
git commit -m "chore: Archive old root folders after import updates

- Updated 150+ files to use UET imports
- Archived core/, error/, aim/, pm/
- All canonical code in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
- Tests passing with new imports"
```

---

## ⚡ Quick Alternative: Keep Compatibility Shims

**If you want to keep old imports working temporarily:**

```python
# File: core/__init__.py
"""
Compatibility shim for old imports.
All code is now in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/
"""
import warnings
warnings.warn(
    "Importing from 'core' is deprecated. "
    "Use 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from UET
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core import *
```

This allows old imports to work while warning developers.

---

## 🎯 Recommendation

### Option A: Full Cleanup (Recommended)
**Time**: 2-3 hours  
**Value**: Complete migration, no duplicates  
**Risk**: Medium (requires import updates)

**Steps**:
1. Run import rewrite script (30 min)
2. Run tests to verify (30 min)
3. Fix any broken imports (1 hour)
4. Archive old folders (5 min)
5. Commit and verify (5 min)

### Option B: Compatibility Shims (Temporary)
**Time**: 30 minutes  
**Value**: Old imports still work  
**Risk**: Low (backwards compatible)

**Steps**:
1. Create shim files in core/, error/, aim/, pm/
2. Commit shims
3. Plan full migration later

### Option C: Do Nothing (Not Recommended)
**Time**: 0  
**Value**: Status quo  
**Risk**: High (confusion continues)

**Why not**: You've already migrated, might as well finish!

---

## 📊 Current vs Target State

### Current State (After UET Migration)
```
Repository:
├── UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ ✅ CANONICAL
├── core/ ⚠️ Still has 84 files (imports point here)
├── error/ ⚠️ Still has 66 files (imports point here)
├── aim/ ⚠️ Still has 85 files (imports point here)
├── pm/ ⚠️ Still has 78 files (imports point here)
└── archive/
    └── 2025-12-01_090348_root-core-engine-cleanup/ (22 files)

Status: Partial migration (core/engine cleaned, other folders remain)
```

### Target State (After Full Cleanup)
```
Repository:
├── UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ ✅ CANONICAL (all code)
└── archive/
    ├── 2025-12-01_090348_root-core-engine-cleanup/ (22 files)
    └── 2025-12-01_HHMMSS_old-root-folders/ (core, error, aim, pm)

Status: Complete migration, zero duplicates, single source of truth
```

---

## ⚠️ CRITICAL: Do NOT Delete Before Import Updates!

**Why this is dangerous**:

1. **150+ files** still import from `core.`, `error.`, `aim.`, `pm.`
2. Deleting folders will **break all imports**
3. Tests will fail
4. Application won't run

**Safe order**:
1. ✅ Update imports first (scripts/rewrite_all_imports.py)
2. ✅ Verify tests pass
3. ✅ Then archive old folders
4. ✅ Verify again

---

## 📞 Next Steps

### Immediate (This Session)

**Option 1: Start Import Updates**
```bash
# Create and run import rewrite script
python scripts/rewrite_all_imports.py
# Expected: 150+ files updated
```

**Option 2: Create Compatibility Shims**
```bash
# Faster, safer, allows gradual migration
# See "Option B" above
```

### Next Session

After imports are updated:
```bash
# Archive old folders
# See "Step 3" above
```

---

## 🎯 Summary

**Current Status**: UET migration complete, but old folders still exist  
**Why**: 150+ files still import from old paths  
**Solution**: Update imports first, then archive old folders  
**Time**: 2-3 hours for full cleanup  
**Alternative**: Compatibility shims (30 min, temporary solution)

**Recommendation**: Run import rewrite script, then archive old folders.

---

**Analysis Date**: 2025-12-01 15:15 UTC  
**Files Using Old Imports**: 150+  
**Safe to Delete**: ❌ NO (not yet)  
**Next Action**: Update imports OR create shims
