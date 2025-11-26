# DAG Refresh Guide

DAGs are derived artifacts. Regenerate them whenever manifests, inventory, pattern registry, or
pipeline specs change.

## When to Regenerate
- Module manifests change (`modules/*/module.manifest.*`, `MODULES_INVENTORY.yaml`)
- Pattern registry changes (operation applicability)
- Pipeline specs change (`pipelines/*.pipeline.yaml`)
- Import rewrites or ULID renames within modules

## Commands
- Full refresh: `python scripts/refresh_repo_dag.py --force`
- Validate freshness: `python scripts/validate_dag_freshness.py`
- Optional: validate module manifests first: `python scripts/validate_modules.py modules`

## Expected Outputs
- Tier 1: `.state/dag/repo_modules.dag.json`
- Tier 2: `modules/*/.state/module_tasks.dag.json`
- Tier 3: `.state/dag/pipelines/*.dag.json`
- Optional index: `.state/dag/index.json`

## Staleness Detection
- Scripts compute `source_hash` (SHA256 over inputs). Hash mismatch => stale => rebuild.
- CI/pre-commit should run `validate_dag_freshness.py`; on failure, rerun the refresh script.

## Validation Checks
- JSON schema per tier (see `DAG_SCHEMA_REFERENCE.md`)
- No cycles
- All inventory modules present in Tier 1 nodes
- Per-module DAG nodes match declared operations/pattern applicability
- Pipeline DAG nodes match pipeline specs and module DAG operations

## Git Hooks / CI (recommended)
- post-merge, post-checkout: refresh
- pre-commit: validate
- CI workflow: validate; regenerate on failure and fail if changes appear
