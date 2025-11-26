# UET Integration with Modules

How Universal Execution Templates (UET) interact with the module-centric structure.

## Principles
- UET references modules by `module_id` and consumes manifests for inputs/outputs.
- DAGs provide ordering; UET expands steps into module-scoped tasks.

## Inputs
- `MODULES_INVENTORY.yaml` for module ids.
- Module manifests for entry points and schemas.
- Global and pipeline DAGs for execution ordering.

## Flow
1) Resolve module IDs and entry points from manifests.
2) Load DAG (`.state/dag/repo_modules.dag.json`) to order module execution.
3) For pipelines, load `.state/dag/pipelines/<pipeline>.dag.json` to stage module tasks.
4) Execute module tasks using public APIs exported via `__init__.py`.

## Expectations
- UET should not bypass module boundaries; use declared entry points.
- UET can short-circuit if DAG hashes are stale—require refresh before run.
