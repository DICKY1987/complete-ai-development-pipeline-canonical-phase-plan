# Script Reference (Migration & Validation)

Purpose and usage for key scripts used in the module-centric migration.

## scripts/create_init_files_v3.py
- Ensures each module has `__init__.py` re-exporting ULID-prefixed files under import-safe names.
- Run when adding new ULID files or scaffolding modules.

## scripts/rewrite_imports.py
- Rewrites Python imports to use module-centric, import-safe paths (not numeric filenames).
- Supports dry-run; run after `create_init_files_v3.py`.

## scripts/validate_modules.py
- Validates module manifests against the spec.
- Inputs: `MODULES_INVENTORY.yaml` or module directories.
- Run before DAG refresh.

## scripts/refresh_repo_dag.py
- Generates Tier 1–3 DAGs (global/module/pipeline) as derived state.
- Writes hashes and metadata; creates missing `.state/` dirs.

## scripts/validate_dag_freshness.py
- Checks DAG existence, schema validity, source hash freshness, and cycles.
- Exit codes: 0 fresh, 1 stale, 2 invalid.

## scripts/install_git_hooks.py
- Installs post-merge/post-checkout hooks to refresh DAGs and pre-commit hook to validate DAGs.
- Regenerate hooks after updates to refresh/validate scripts.
