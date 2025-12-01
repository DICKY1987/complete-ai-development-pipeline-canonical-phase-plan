---
doc_id: DOC-GUIDE-ROLLBACK-PROCEDURES-1459
---

# Rollback Procedures (Module-Centric Migration)

Principles: favor minimal scope rollback (single module or DAG set) before repo-wide revert. Never
delete data; restore from git or snapshots.

## Quick Triage
- Identify failing phase (manifests, DAGs, imports, tests).
- Capture state: `git status -sb`; copy `.execution/telemetry.jsonl` tail if relevant.

## Rollback by Phase
- Manifests/ULID prep:
  - Revert module directory: `git checkout -- modules/<module>` (or reset file-by-file).
  - Re-run `python scripts/validate_modules.py modules`.
- DAG generation:
  - Restore DAGs: `git checkout -- .state/dag modules/*/.state`.
  - Re-run: `python scripts/refresh_repo_dag.py --force` then `python scripts/validate_dag_freshness.py`.
- Import rewrite:
  - Revert affected module(s) only: `git checkout -- modules/<module>`.
  - Re-run `python scripts/rewrite_imports.py` (optionally `--dry-run` first).
- Tests:
  - Revert the failing module; leave other modules intact.
  - Re-run targeted tests (e.g., `pytest modules/<module>` if structured).

## Full Rollback (last resort)
- Hard revert working tree to last known good commit:
  - `git checkout .`
  - `git clean -fd` (only if you intend to drop untracked; use sparingly)
- If a migration commit exists: `git revert <commit_sha>`

## Snapshots (recommended)
- Before migration: `Get-ChildItem -Recurse > .state/snapshots/tree_before.txt`
- After migration: `Get-ChildItem -Recurse > .state/snapshots/tree_after.txt`
- Use these to diff scope and confirm restoration.

## Post-Rollback Verification
- `python scripts/validate_modules.py modules`
- `python scripts/validate_dag_freshness.py`
- `python -m py_compile $(rg --files -g '*.py')`
- `pytest -q` (if tests exist)
