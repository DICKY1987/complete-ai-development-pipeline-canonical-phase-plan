# ADR-012: DAG-as-Derived-State

## Context
Manual DAG maintenance drifts from manifests and pipeline specs, causing stale execution plans and
unreliable AI context. Two DAG implementations existed; drift risk was high.

## Decision
- Treat all DAGs (global modules, per-module tasks, pipelines) as derived artifacts regenerated from
  manifests, patterns, and pipeline specs.
- Canonicalize DAG building in a single script (`scripts/refresh_repo_dag.py`) and validator
  (`scripts/validate_dag_freshness.py`).
- Store DAG outputs under `.state/dag/` and per-module `.state/`; forbid hand-edited DAG JSON.

## Rationale
- Determinism: single source of truth yields reproducible graphs and stable ordering.
- Freshness: hash-based staleness checks and CI/hooks prevent drift.
- Efficiency: AI/schedulers can query precomputed DAGs without recomputing.

## Consequences
- Any manifest/pipeline change requires DAG regeneration.
- CI and pre-commit should fail on stale DAGs.
- Legacy DAG builders should be removed or delegated to the canonical utilities.
