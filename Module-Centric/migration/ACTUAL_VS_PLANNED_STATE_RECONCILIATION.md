# Actual vs Planned State Reconciliation

Goal: reconcile the real repository layout (`repo_tree.txt`) with the planned module-centric “after”
layout (`asafterthemoverepo.txt`, known to be inaccurate), and set corrected expectations.

## Observations
- `repo_tree.txt` shows the current structure with many top-level domains (core/, engine/, error/,
  aim/, pm/, specifications/, scripts/, docs/, etc.) and no unified `modules/` tree.
- `asafterthemoverepo.txt` describes a fully migrated `modules/` tree with ULID-prefixed files and
  per-module `.state/` directories, but it does not match the current filesystem.
- Several module-centric docs exist (MODULE_CENTRIC_*), but the physical layout has not been
  migrated; DAG/state files in `.state/` reflect pre-migration state.

## Likely Causes of Drift
- The “after” tree was drafted ahead of actual moves.
- Manifests and DAGs were planned but not generated against the live tree.
- Import rewrite and ULID renames have not been applied across code/tests/docs.

## Corrected Target (high level)
- Create `modules/` with one folder per module_id (e.g., `core-engine/`, `core-state/`,
  `core-planning/`, `aim-cli/`, `error-engine/`, plugins, etc.).
- Inside each module: ULID-prefixed code, tests, schemas, docs, `module.manifest.json|yaml`,
  `__init__.py` for import-safe names, and `.state/current.json`.
- Global DAGs in `.state/dag/`; per-module DAGs in `modules/*/.state/`; pipeline DAGs in
  `.state/dag/pipelines/`.
- Legacy top-level code/docs/tests either migrated or archived; imports rewritten to module paths.

## Next Checks
- Confirm actual module candidates from `MODULES_INVENTORY.yaml` and `docs/examples/module.manifest.example.json`.
- Enumerate current code owners by directory to map into `modules/` destinations.
- After manifest authoring, run: `python scripts/refresh_repo_dag.py` then
  `python scripts/validate_dag_freshness.py` to align derived state with reality.
