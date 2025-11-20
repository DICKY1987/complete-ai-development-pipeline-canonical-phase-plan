# Specification Folder Migration Guide

## Overview

This migration consolidates `openspec/` and `spec/` into a single unified `specifications/` directory with logical organization.

## What Gets Moved

### From `openspec/`
- `openspec/specs/` → `specifications/content/`
- `openspec/changes/` → `specifications/changes/`
- `openspec/archive/` → `specifications/archive/`
- `openspec/OPENSPEC_BRIDGE_SUMMARY.md` → `specifications/bridge/BRIDGE_SUMMARY.md`
- `openspec/project.md` → `specifications/bridge/project_conventions.md`

### From `spec/`
- `spec/tools/spec_indexer/` → `specifications/tools/indexer/`
- `spec/tools/spec_resolver/` → `specifications/tools/resolver/`
- `spec/tools/spec_guard/` → `specifications/tools/guard/`
- `spec/tools/spec_patcher/` → `specifications/tools/patcher/`
- `spec/tools/spec_renderer/` → `specifications/tools/renderer/`

## New Structure

```
specifications/
├── README.md                          # Overview and usage guide
│
├── content/                           # Specification documents
│   ├── orchestration/spec.md
│   ├── plugin-system/spec.md
│   └── validation-pipeline/spec.md
│
├── changes/                           # Active change proposals
│   └── test-001/
│
├── archive/                           # Completed changes
│
├── tools/                             # Processing utilities
│   ├── indexer/
│   ├── resolver/
│   ├── guard/
│   ├── patcher/
│   └── renderer/
│
├── .index/                            # Generated files (gitignored)
│
├── bridge/                            # OpenSpec integration docs
│
└── schemas/                           # Validation schemas
```

## Import Changes

**Before:**
```python
from spec.tools.spec_indexer.indexer import generate_index
from spec.tools.spec_resolver.resolver import resolve_spec_uri
```

**After:**
```python
from specifications.tools.indexer.indexer import generate_index
from specifications.tools.resolver.resolver import resolve_spec_uri
```

## Usage

### Dry Run (Preview Changes)
```bash
# Python
python scripts/migrate_spec_folders.py --dry-run

# PowerShell
pwsh scripts/migrate_spec_folders.ps1 -DryRun
```

### Execute Migration (With Backup)
```bash
# Python
python scripts/migrate_spec_folders.py --backup

# PowerShell
pwsh scripts/migrate_spec_folders.ps1 -Backup
```

### Execute Migration (No Backup)
```bash
# Python
python scripts/migrate_spec_folders.py

# PowerShell
pwsh scripts/migrate_spec_folders.ps1
```

## What the Script Does

1. ✅ Creates new `specifications/` directory structure
2. ✅ Copies all content from old locations to new locations
3. ✅ Updates all Python import statements automatically
4. ✅ Creates README.md and supporting files
5. ✅ Creates .gitignore for generated index files
6. ✅ Generates migration report
7. ✅ Optionally creates backup of old directories

## Post-Migration Steps

1. **Review**: Check the `specifications/` directory structure
2. **Test**: Run `pytest -q` to verify everything works
3. **Verify**: Check that imports are correct
4. **Update Docs**: Update any documentation that references old paths
5. **Clean Up**: Delete old `openspec/` and `spec/` directories (after verification)
6. **Commit**: Commit changes to git

## Rollback

If you used `--backup`, rollback by:
```bash
# Delete specifications/
rm -rf specifications/

# Restore from backup
cp -r .migration_backup_TIMESTAMP/openspec ./
cp -r .migration_backup_TIMESTAMP/spec ./
```

## Files Affected

The script will automatically update imports in:
- `tools/spec_guard/__init__.py`
- `tools/spec_indexer/__init__.py`
- `tools/spec_patcher/__init__.py`
- `tools/spec_renderer/__init__.py`
- `tools/spec_resolver/__init__.py`
- Any other Python files using old import paths

## Benefits of New Structure

1. **Clarity**: Clear separation of content vs tools
2. **Discoverability**: Logical folder names
3. **Scalability**: Easy to add new specs
4. **Maintainability**: Tools isolated and testable
5. **Consistency**: Follows repository conventions

## Questions?

See:
- `specifications/README.md` (after migration)
- `specifications/bridge/BRIDGE_SUMMARY.md` (OpenSpec integration)
- Original docs: `docs/openspec_bridge.md`
