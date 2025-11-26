# Module Conflict Resolution

Handling merge conflicts and overlapping changes in module-centric structure.

## Typical Conflicts
- DAG JSON conflicts from parallel branches.
- Manifest edits overlapping on dependencies or artifacts.
- Import rewrites colliding with manual edits.

## Resolution Patterns
- DAG conflicts: discard manual merges; rerun `refresh_repo_dag.py` to regenerate deterministically.
- Manifest conflicts: merge fields carefully, then rerun `validate_modules.py` and regenerate DAGs.
- Import conflicts: prefer regenerated imports from `rewrite_imports.py`; re-run script if needed.

## Post-Resolution Checks
- `python scripts/validate_modules.py modules`
- `python scripts/refresh_repo_dag.py --force`
- `python scripts/validate_dag_freshness.py`
- `python -m py_compile $(rg --files -g '*.py')`
