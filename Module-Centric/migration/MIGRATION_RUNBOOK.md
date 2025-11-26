# Migration Runbook (Module-Centric Refactor)

Windows-first commands shown (PowerShell). Run from repo root. Each step ends with a validation
check; commit only after green checks.

## Phase 1 — Inventory & Baseline
1) Create venv (if needed): `python -m venv .venv; . .\.venv\Scripts\Activate.ps1`
2) Capture current tree snapshot: `pwsh -c "Get-ChildItem -Recurse > .state/snapshots/tree_before.txt"`
3) Validate modules inventory: `python scripts/validate_modules.py MODULES_INVENTORY.yaml`
4) Record git status: `git status -sb`

## Phase 2 — Prepare Module Manifests and ULIDs
1) Ensure every module has `module.manifest.json|yaml`:
   - Template: `docs/examples/module.manifest.example.json`
   - Spec: `docs/developer_guides/MODULE_MANIFEST_SPECIFICATION.md`
2) Normalize ULID filenames and add `__init__.py` re-exports where needed:
   `python scripts/create_init_files_v3.py`
3) Validate manifests: `python scripts/validate_modules.py modules`

## Phase 3 — Generate DAGs (Derived State)
1) Regenerate DAGs: `python scripts/refresh_repo_dag.py --force`
2) Validate freshness: `python scripts/validate_dag_freshness.py`
3) Inspect outputs:
   - Global: `.state/dag/repo_modules.dag.json`
   - Per-module: `modules/*/.state/module_tasks.dag.json`
   - Pipelines: `.state/dag/pipelines/*.dag.json`

## Phase 4 — Rewrite Imports (Hybrid Strategy)
1) Rewrite imports to module-centric paths: `python scripts/rewrite_imports.py`
2) Re-run DAG validation (catches missing modules): `python scripts/validate_dag_freshness.py`
3) Sanity import check (Python): `python -m py_compile $(rg --files -g '*.py')`

## Phase 5 — Tests and Validation
1) Targeted tests (if present): `pytest -q` or `pwsh ./scripts/test.ps1`
2) Validation checklist: see `docs/migration/VALIDATION_CHECKLIST.md`
3) Confirm status clean: `git status -sb`

## Phase 6 — Commit and Snapshot
1) Create snapshot after migration: `pwsh -c "Get-ChildItem -Recurse > .state/snapshots/tree_after.txt"`
2) Commit with conventional message: `git commit -am "chore: apply module-centric migration step"`

## Rollback Hooks
- If DAG validation fails: rerun Phase 3; if still failing, restore `.state/dag` from git.
- If imports fail: re-run `scripts/rewrite_imports.py --dry-run` to locate offenders.
- If tests fail after imports: revert that module dir only, then re-run Phase 4–5.
