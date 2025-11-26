# DAG Query API (Usage Patterns)

Lightweight guidance for consuming precomputed DAG JSON from Python or tools. Aim: fast lookup for
“what depends on X?” without rebuilding graphs.

## Loading Helpers (example)
```python
import json
from pathlib import Path

def load_dag(path: Path):
    dag = json.loads(path.read_text())
    edges = {k: set(v) for k, v in dag.get("edges", {}).items()}
    reverse = {k: set(v) for k, v in dag.get("reverse_edges", {}).items()}
    return dag, edges, reverse
```

## Common Queries
- Reverse dependencies: `reverse_edges.get(node, set())`
- Forward dependencies: `edges.get(node, set())`
- Topological levels: `dag["topo_levels"]` for scheduling waves
- Critical path: `dag.get("critical_path", [])`
- Staleness hint: verify `source_hash` vs current manifest/pipeline hash

## Global Module DAG (Tier 1)
Path: `.state/dag/repo_modules.dag.json`
- Query module order: iterate `topo_levels`
- Impact analysis: `reverse_edges[module_id]` yields dependents

## Per-Module Task DAG (Tier 2)
Path: `modules/<module>/.state/module_tasks.dag.json`
- Operation order inside a module: `topo_levels`
- Dependencies between ops: `edges[op_id]`
- Applicable operations: `operations[*].operation_kind`

## Pipeline DAG (Tier 3)
Path: `.state/dag/pipelines/<pipeline>.dag.json`
- Stage grouping: `stages[*].nodes`
- Cross-module execution waves: `topo_levels`
- Validate referenced tasks: ensure each node matches an operation from module task DAGs

## Error Handling / Fallbacks
- If DAG JSON missing: fall back to on-demand builder (if available), then regenerate via
  `refresh_repo_dag.py`.
- If cycles present: treat as invalid; require regeneration or manifest fix.
- If hash mismatch: mark stale and rebuild before execution.
