# Module Interface Contracts

Defines what each module exposes and how consumers should depend on it.

## Contract Elements
- Public API surface: functions/classes re-exported in `__init__.py`.
- Entry points: `entry_points` in the manifest (`cli`, `api`, `task`, `worker`).
- Dependencies: `dependencies.modules` in manifest; must align with DAG edges.
- Schemas: input/output contracts under `artifacts.schemas`.
- State: `.state/current.json` path declared in manifest.

## Consumer Rules
- Import via module package name (not ULID filenames).
- Depend only on declared public symbols; avoid reaching into private files.
- Respect dependency order from the module DAG.

## Provider Rules
- Keep `__init__.py` aligned with intended public surface.
- Update manifest when adding/removing public entry points or dependencies.
- Regenerate DAGs after manifest changes.

## Validation
- Ensure `module.manifest.*` lists all public entry points.
- CI: `validate_dag_freshness.py` ensures dependencies align with manifests.
- Consider static checks to flag imports of non-exported symbols.
