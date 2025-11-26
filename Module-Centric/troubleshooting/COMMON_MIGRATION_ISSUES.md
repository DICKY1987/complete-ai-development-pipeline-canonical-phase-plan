# Common Migration Issues

- Missing manifest: `validate_modules.py` fails or DAG generation skips a module.
  - Fix: add `module.manifest.*`, rerun validator, refresh DAGs.
- Stale DAG: `validate_dag_freshness.py` exit 1.
  - Fix: `refresh_repo_dag.py --force`.
- Import errors due to numeric filenames:
  - Fix: ensure `__init__.py` re-exports; run `create_init_files_v3.py` and `rewrite_imports.py`.
- ULID prefix mismatch:
  - Fix: align filenames and manifest `ulid_prefix`; avoid regenerating ULID unless creating a new module.
- Pipeline DAG missing tasks:
  - Fix: ensure pipeline specs reference valid module operations; regenerate DAGs.
