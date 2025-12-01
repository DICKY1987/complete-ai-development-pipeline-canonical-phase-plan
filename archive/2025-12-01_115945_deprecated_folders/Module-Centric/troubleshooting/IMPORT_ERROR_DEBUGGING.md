---
doc_id: DOC-GUIDE-IMPORT-ERROR-DEBUGGING-1469
---

# Import Error Debugging

Checklist for "cannot import name" or similar issues after the module-centric migration.

## Quick Checks
- `python -m py_compile $(rg --files -g '*.py')`
- Ensure module has `__init__.py` and exports the symbol.
- Confirm import paths use module names, not ULID filenames.

## Common Causes
- Missing re-export in `__init__.py`.
- Import still pointing to numeric filename.
- Circular import introduced by rewritten paths.
- Module not in `MODULES_INVENTORY.yaml` but referenced.

## Fix Steps
1) Regenerate `__init__.py` exports: `python scripts/create_init_files_v3.py`
2) Rewrite imports: `python scripts/rewrite_imports.py`
3) If cycles suspected: check DAG `cycles` and adjust dependencies.
4) Re-run compile and targeted tests.
