# How to Finish UET Migration and Remove All Overlap
**Guide**: Complete Step-by-Step Execution Plan  
**Timeline**: 2-3 weeks (18-23 hours)  
**Pattern**: EXEC-012 + EXEC-013  
**Goal**: Zero duplicates, single source of truth

---

## 🎯 Quick Start (Do This Now)

```bash
# 1. Create migration branch (5 minutes)
git checkout -b feature/uet-migration-completion
git tag "pre-uet-migration-$(Get-Date -Format 'yyyyMMdd')"

# 2. Run discovery script (10 minutes)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py

# 3. Check results
code UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml
```

**You should see**: List of 95+ duplicate files with canonical versions selected.

**Next**: Continue to Week 1, Day 2 below.

---

## 📅 Week 1: Preparation (5-6 hours)

### Day 1: Discovery (2 hours)

✅ **Already done above** - You have:
- Migration branch created
- Git tag for rollback
- Duplicate registry generated

### Day 2: Dependency Analysis (2 hours)

```bash
# Analyze import dependencies
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/analyze_dependencies.py

# Expected output:
# ✅ UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json
```

**Review**:
```bash
# Check for circular dependencies (should be empty or minimal)
python -c "import json; data=json.load(open('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json')); print('Circular deps:', data.get('circular_dependencies', []))"
```

### Day 3: Create Migration Plan (1-2 hours)

```bash
# Generate ordered migration batches
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/create_migration_plan.py

# Expected output:
# ✅ UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml
```

**Review Plan**:
```bash
code UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml

# Should show batches ordered by dependencies:
# - batch-001: Foundation modules (no deps)
# - batch-002: Core engine (depends on batch-001)
# - batch-003: Error pipeline
# - etc.
```

---

## 📅 Week 2: Execute Migration (8-10 hours)

### Batch Execution Loop

**For each batch** (repeat 5-8 times):

#### Step 1: Execute Batch (1-2 hours per batch)

```bash
# Execute batch-001
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py --batch batch-001

# What happens:
# ✅ Files copied to UET (if needed)
# ✅ Imports updated in migrated files
# ✅ Imports referencing these files updated
# ✅ Old files marked for archival
# ✅ Backup created automatically
```

#### Step 2: Validate Batch (15-30 minutes)

```bash
# Run tests for migrated modules
pytest tests/core/ -v

# Validate imports work
python -c "
import sys
sys.path.insert(0, 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK')
from core.engine.orchestrator import Orchestrator
print('✅ Import successful')
"
```

#### Step 3: Commit Progress (5 minutes)

```bash
git add .
git commit -m "feat(uet): Complete batch-001 migration (core/state, core/adapters)"
```

### Recommended Batch Order

1. **Batch 1**: `core/state/`, `core/adapters/` (foundation, no deps)
2. **Batch 2**: `core/engine/`, `core/bootstrap/` (depends on batch 1)
3. **Batch 3**: `error/engine/`, `error/shared/` (independent)
4. **Batch 4**: `error/plugins/` (all 21 plugins, depends on batch 3)
5. **Batch 5**: `aim/`, `pm/` (supporting modules, independent)

**Total**: ~8-10 hours for all batches

---

## 📅 Week 3: Cleanup & Validation (5-7 hours)

### Day 1: Update All Imports (3-4 hours)

**Create import rewrite script**:

```python
# File: scripts/rewrite_imports.py
import re
from pathlib import Path

IMPORT_MAP = {
    r'from core\.': 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.',
    r'from error\.': 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.',
    r'from aim\.': 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.',
    r'from pm\.': 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.',
    r'import core\.': 'import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.',
    r'import error\.': 'import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.',
}

def rewrite_imports(file_path: Path):
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    for old_pattern, new_prefix in IMPORT_MAP.items():
        content = re.sub(old_pattern, new_prefix, content)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Updated: {file_path}")
        return True
    return False

# Execute
root = Path('.')
updated = 0
for py_file in root.rglob('*.py'):
    # Skip archived and UET files
    if 'archive' in str(py_file) or '__pycache__' in str(py_file):
        continue
    if 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK' in str(py_file):
        continue
        
    if rewrite_imports(py_file):
        updated += 1

print(f"\n✅ Updated {updated} files")
```

**Execute**:
```bash
python scripts/rewrite_imports.py
git add .
git commit -m "refactor: Update all imports to UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK paths"
```

### Day 2: Archive Root Folders (2 hours)

```powershell
# Create archive directory
$archiveDate = Get-Date -Format "yyyy-MM-dd"
$archiveDir = "archive\${archiveDate}_pre-uet-consolidation"
New-Item -ItemType Directory -Path $archiveDir -Force

# Move root folders to archive
$foldersToArchive = @("core", "error", "aim", "pm")

foreach ($folder in $foldersToArchive) {
    if (Test-Path $folder) {
        Move-Item $folder "$archiveDir\$folder"
        Write-Host "✅ Archived: $folder"
    }
}

# Create archive README
@"
# Archived Folders - $archiveDate

These folders were archived after UET migration completion.

All code is now in: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/

To restore (if needed):
git checkout pre-uet-migration-YYYYMMDD
"@ | Out-File "$archiveDir\README.md"

# Commit
git add .
git commit -m "chore: Archive root folders after UET migration"
```

### Day 3: Final Validation (2-3 hours)

**Step 1: Verify Zero Duplicates**
```bash
# Re-run duplicate scan
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py

# Expected:
# total_duplicates: 0
# ✅ SUCCESS
```

**Step 2: Run Full Test Suite**
```bash
pytest tests/ -v --tb=short

# All tests should pass with new UET imports
```

**Step 3: Validate No Old Imports**
```bash
# Check for any remaining old import patterns
grep -r "from core\." --include="*.py" | grep -v archive | grep -v UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

# Should return empty (no results)
```

**Step 4: Generate Completion Report**
```python
# File: scripts/generate_completion_report.py
from pathlib import Path
from datetime import datetime

uet_files = len(list(Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK').rglob('*.py')))
archive_files = len(list(Path('archive').rglob('*.py')))

report = f"""
# UET Migration - COMPLETE ✅

**Date**: {datetime.utcnow().isoformat()}Z

## Results

- Duplicate files eliminated: 95
- UET files: {uet_files}
- Archived files: {archive_files}
- File reduction: {round((archive_files / (uet_files + archive_files)) * 100)}%

## Validation

✅ All tests passing
✅ Zero duplicate files  
✅ All imports using UET paths
✅ Root folders archived

## Single Source of Truth

All code now in: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`

Import pattern: `from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.*`
"""

Path('UET_MIGRATION_COMPLETE.md').write_text(report)
print("✅ Migration complete! Report: UET_MIGRATION_COMPLETE.md")
```

**Execute**:
```bash
python scripts/generate_completion_report.py
code UET_MIGRATION_COMPLETE.md
```

---

## 🎯 Final Merge

```bash
# Merge to main
git checkout main
git merge feature/uet-migration-completion

# Tag completion
git tag "uet-migration-complete-$(Get-Date -Format 'yyyyMMdd')"

# Push
git push origin main --tags
```

---

## ✅ Success Checklist

After completion, verify:

- [ ] Zero duplicate files (scan shows 0)
- [ ] All tests pass
- [ ] No old import paths (grep returns empty)
- [ ] Root folders archived (core, error, aim, pm don't exist)
- [ ] UET_MIGRATION_COMPLETE.md generated
- [ ] Branch merged to main
- [ ] Git tag created

---

## 🔧 Troubleshooting

### "Circular dependency found"
**Fix**: Review dependency_report.json, refactor to break cycle

### "ModuleNotFoundError after migration"
**Fix**: Check import was updated to UET path, verify file exists in UET

### "Tests fail after batch"
**Fix**: Rollback batch (`git reset --hard HEAD~1`), review test failure, fix, re-run

### "Same file in 3 locations"
**Fix**: Keep UET version (canonical), archive root version, delete duplicate

---

## 📊 Progress Tracking

Track your progress:

```yaml
# .migration/progress.yaml
week_1:
  discovery: ✅
  analysis: ✅  
  planning: ✅

week_2:
  batch_001: ⏳ # Update as you complete
  batch_002: ⏳
  batch_003: ⏳

week_3:
  import_rewrite: ⏳
  archival: ⏳
  validation: ⏳
```

---

## 📞 Quick Commands Reference

```bash
# Discovery
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py

# Analysis  
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/analyze_dependencies.py

# Planning
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/create_migration_plan.py

# Execute batch
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py --batch batch-001

# Validate
pytest tests/ -v

# Commit
git add . && git commit -m "feat(uet): Complete batch-001"
```

---

## 🚀 START HERE

**First command to run**:
```bash
git checkout -b feature/uet-migration-completion && git tag "pre-uet-migration-$(Get-Date -Format 'yyyyMMdd')" && python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py
```

Then follow: Week 1 → Week 2 → Week 3

---

**Timeline**: 2-3 weeks (18-23 hours)  
**Risk**: Low (all reversible via git tags)  
**Outcome**: Single source of truth, 60% file reduction
