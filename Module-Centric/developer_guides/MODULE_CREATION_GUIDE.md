# Module Creation Guide

Steps to create a new module following the module-centric pattern.

## 1) Choose Identity
- Pick `module_id` (import-safe, kebab-case) and generate ULID prefix (6 chars).
- Directory: `modules/<module_id>/`.

## 2) Scaffold Structure
- Create files with ULID prefix: code, tests, schemas, docs.
- Add `.state/` with `current.json` (even if minimal).
- Add `__init__.py` re-exporting public symbols from ULID files.

Example:
```
modules/core-example/
  01ABCD_logic.py
  01ABCD_logic.test.py
  01ABCD_logic.schema.json
  01ABCD_README.md
  module.manifest.json
  __init__.py
  .state/current.json
```

## 3) Author Manifest
- Follow `docs/developer_guides/MODULE_MANIFEST_SPECIFICATION.md`.
- Include dependencies, artifacts, entry_points, owners, tags.

## 4) Validate
- `python scripts/validate_modules.py modules`

## 5) Register in Inventory
- Add to `MODULES_INVENTORY.yaml`.

## 6) Generate Derived State
- `python scripts/refresh_repo_dag.py --force`
- `python scripts/validate_dag_freshness.py`

## 7) Import Hygiene
- Ensure `__init__.py` exports clean names.
- If needed, run `python scripts/create_init_files_v3.py` and `python scripts/rewrite_imports.py`.

## 8) Tests
- Add module-local tests; run `pytest -q` or targeted tests.

## 9) Commit
- Check `git status -sb`; commit with conventional message.
