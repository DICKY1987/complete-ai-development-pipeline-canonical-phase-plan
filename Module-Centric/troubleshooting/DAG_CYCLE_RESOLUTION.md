# DAG Cycle Resolution

How to detect and resolve dependency cycles in module and pipeline DAGs.

## Detection
- `python scripts/validate_dag_freshness.py` (fails if cycles present)
- Inspect `cycles` field in `.state/dag/*.json` outputs.

## Resolution Steps
- For module DAG (Tier 1): remove circular module dependencies in manifests; split shared concerns
  into a lower-layer module.
- For module task DAG (Tier 2): adjust operation applicability/ordering to break cycles.
- For pipeline DAG (Tier 3): re-order stages or remove cross-stage back edges.

## Re-validate
- After changes: `python scripts/refresh_repo_dag.py --force` then `python scripts/validate_dag_freshness.py`
- Confirm `cycles` is empty and `topo_levels` covers all nodes.
