---
doc_id: DOC-GUIDE-DETERMINISTIC-EXECUTION-DESIGN-1443
---

# Deterministic Execution Design

How ULID identity + manifests + derived DAGs produce reproducible, verifiable execution plans.

## Determinism Inputs
- ULID identity: stable, collision-resistant prefixes tie related artifacts.
- Module manifests: single source of truth for artifacts, dependencies, entry points.
- Pattern registry: defines operation applicability for module task DAGs.
- Pipeline specs: define stage/task composition.

## Derived Artifacts
- DAGs (tiers 1–3) regenerated from the inputs with stable sorting and hashing.
- `source_hash` (SHA256) on DAGs binds outputs to exact inputs.
- `topo_levels` and `critical_path` computed from canonical graphs.

## Process
1) Author/update manifest and specs.
2) `refresh_repo_dag.py` builds DAGs deterministically (stable ordering, no randomness).
3) `validate_dag_freshness.py` checks schema, cycles, and `source_hash`.
4) Schedulers/orchestrators consume DAG JSON; no on-the-fly graph mutation.

## Guarantees
- Repeatable builds: same inputs → same DAGs → same ordering.
- Drift detection: any input change flips `source_hash`; validators fail stale DAGs.
- Debuggability: provenance (`generated_at`, `generated_by`, hashes) attached to each DAG.

## Practices
- Avoid hand-editing DAG JSON; regenerate instead.
- Keep ULID prefixes stable; avoid renames unless creating new modules.
- Commit manifests and DAGs together when inputs change.

## Example: Input → DAG → Execution
```
Manifests + Inventory + Pipeline Specs
            │
            ▼
    refresh_repo_dag.py (stable order + hashes)
            │
            ▼
 .state/dag/repo_modules.dag.json
 .state/dag/pipelines/full_build.dag.json
 modules/<module>/.state/module_tasks.dag.json
            │
            ▼
 Schedulers/Orchestrators (consume topo_levels, critical_path)
```

### Minimal Code Snippet (hash check)
```python
import json, hashlib, pathlib
p = pathlib.Path(".state/dag/repo_modules.dag.json")
dag = json.loads(p.read_text())
inputs_hash = dag["source_hash"]
# recompute current hash of manifests to confirm freshness
```
