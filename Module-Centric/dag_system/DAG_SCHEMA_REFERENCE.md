# DAG Schema Reference (v1.0.0)

Baseline JSON fields for all DAG tiers. Extend `metadata` as needed; keep `schema_version` to allow
evolution.

## Shared Shape (all tiers)
```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-01-01T00:00:00Z",
  "generated_by": "scripts/refresh_repo_dag.py",
  "dag_type": "module_dependency | module_tasks | pipeline",
  "source_hash": "sha256:...",
  "nodes": ["string"],
  "edges": {"string": ["string"]},
  "reverse_edges": {"string": ["string"]},
  "topo_levels": [["string"]],
  "cycles": [],
  "critical_path": ["string"],
  "critical_path_weight": 0,
  "metadata": {}
}
```

## Tier 1 (Global Module Dependency)
```json
{
  "dag_type": "module_dependency",
  "metadata": {
    "total_modules": 0,
    "layers": {"infra":0,"domain":0,"api":0,"ui":0},
    "avg_dependencies": 0.0
  }
}
```

## Tier 2 (Per-Module Task DAG)
```json
{
  "dag_type": "module_tasks",
  "module_id": "core-engine",
  "ulid_prefix": "010001",
  "operations": [
    {
      "operation_id": "core-engine.build",
      "pattern_id": "PAT-...",
      "operation_kind": "build",
      "depends_on": ["core-engine.lint"],
      "estimated_duration_seconds": 30
    }
  ],
  "metadata": {
    "applicability": ["has_python_files", "has_tests"]
  }
}
```

## Tier 3 (Pipeline DAG)
```json
{
  "dag_type": "pipeline",
  "pipeline_id": "full_build",
  "source_pipelines": ["pipelines/full_build.pipeline.yaml"],
  "stages": [
    {"stage_id": "infra_layer", "nodes": ["core-state.build","core-state.test"]}
  ],
  "metadata": {
    "total_tasks": 0,
    "estimated_duration_seconds": 0,
    "max_parallelism": 0
  }
}
```

## Validation Rules
- `schema_version` must match validator expectation; bump on breaking changes.
- `nodes` must include all keys present in `edges` and `reverse_edges`.
- `topo_levels` must contain each node exactly once; `cycles` must be empty for execution DAGs.
- `source_hash` must be recomputed from the exact inputs used for generation.
