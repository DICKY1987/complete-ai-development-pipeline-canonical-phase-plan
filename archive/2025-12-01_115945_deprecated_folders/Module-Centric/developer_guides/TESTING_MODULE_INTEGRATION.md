---
doc_id: DOC-GUIDE-TESTING-MODULE-INTEGRATION-1452
---

# Testing Module Integration

How to test modules in isolation and together after the module-centric migration.

## Isolated Module Tests
- Keep tests colocated under the module (ULID-prefixed).
- Run targeted tests (example): `pytest modules/<module>` if test discovery supports it.
- Validate imports: `python -m py_compile $(rg --files -g '01????_*.py' modules/<module>)`

## Cross-Module Integration
- Use pipeline DAG tasks to stage dependencies; execute in topological order from
  `.state/dag/repo_modules.dag.json`.
- For pipelines, ensure `.state/dag/pipelines/<pipeline>.dag.json` aligns with test ordering.

## Preconditions
- Regenerate DAGs: `python scripts/refresh_repo_dag.py --force`
- Validate DAGs: `python scripts/validate_dag_freshness.py`
- Verify manifests: `python scripts/validate_modules.py modules`

## Recommended Practices
- Avoid mocking other modules’ internals; consume via public exports defined in `__init__.py`.
- Prefer fixture data stored in the same module directory.
- Keep tests deterministic; avoid network/external state unless explicitly marked/guarded.

## Failure Triage
- If import errors: rerun `scripts/rewrite_imports.py` and check `__init__.py` exports.
- If DAG mismatch: rerun refresh/validate; check manifest dependencies.
- If order-dependent failures: inspect `topo_levels` in the global DAG and align test setup.
