# Speed Demon Integration with Modules

How the Speed Demon orchestration system should use the module-centric layout.

## Principles
- Use precomputed DAGs for ordering instead of ad-hoc dependency resolution.
- Operate at module/task granularity; avoid cross-module internal calls.

## Inputs
- Global DAG: `.state/dag/repo_modules.dag.json`
- Module task DAGs: `modules/*/.state/module_tasks.dag.json`
- Pipeline DAGs: `.state/dag/pipelines/*.dag.json` (if running pipelines)

## Flow
1) Load global DAG; schedule modules in topological waves.
2) For each module, load its task DAG to order operations (build/lint/test/etc.).
3) Respect pipeline DAG stage constraints when running pipelines.
4) Fail fast on hash mismatch (stale DAG) and request refresh.

## Best Practices
- Cache DAG JSON in memory per run; refresh from disk when hashes change.
- Log DAG hashes in telemetry to correlate runs.
- Do not execute tasks not present in module task DAG.
