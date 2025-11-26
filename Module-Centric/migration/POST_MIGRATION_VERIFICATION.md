# Post-Migration Verification

Use this checklist after completing the migration to confirm the repo is in a stable module-centric
state.

## Structural
- `modules/` exists with one folder per `module_id`.
- Each module folder contains ULID-prefixed artifacts, manifest, `__init__.py`, and `.state/`.
- Legacy top-level code/tests/docs have been migrated or archived.

## Manifests and Inventory
- All modules listed in `MODULES_INVENTORY.yaml` have manifests in place.
- `python scripts/validate_modules.py modules` passes.

## DAGs
- Regenerated DAGs present:
  - `.state/dag/repo_modules.dag.json`
  - `modules/*/.state/module_tasks.dag.json`
  - `.state/dag/pipelines/*.dag.json`
- `python scripts/validate_dag_freshness.py` exits 0.

## Imports
- Import smoke test (PowerShell):
  ```powershell
  python - <<'PY'
  import importlib
  import sys
  mods = ["modules.core_engine", "modules.core_state"]
  for m in mods:
      try:
          importlib.import_module(m)
          print(f"OK {m}")
      except Exception as e:
          print(f"FAIL {m}: {e}", file=sys.stderr)
  PY
  ```

## Tests
- Run: `pytest -q` or `pwsh ./scripts/test.ps1` (if available) with no new failures.

## Git/Artifacts
- `git status -sb` clean after intended changes committed.
- DAGs and manifests under version control; no untracked surprises in `.state/`.

## Sign-off
- Record final snapshot: `Get-ChildItem -Recurse > .state/snapshots/tree_after.txt`
- Tag or note commit hash for the completed migration.
