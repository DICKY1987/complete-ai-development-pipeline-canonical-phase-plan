# DAG Architecture (Three-Tier, Derived State)

This repository treats all DAG artifacts as **derived state** built from manifests, patterns, and
pipeline specs. No DAG JSON is hand-edited; freshness is enforced by regeneration.

## Tiers and Locations
- Tier 1 (Global module deps): `.state/dag/repo_modules.dag.json`
- Tier 2 (Per-module task DAGs): `modules/<module>/.state/module_tasks.dag.json`
- Tier 3 (Pipeline workflows): `.state/dag/pipelines/<pipeline>.dag.json`
- Index (optional): `.state/dag/index.json` pointing to all DAG artifacts with versions and hashes

## Provenance and Metadata (required in all tiers)
- `schema_version`: semantic version for the DAG schema
- `generated_at` (ISO-8601 UTC) and `generated_by` (script name)
- `dag_type`: `module_dependency` | `module_tasks` | `pipeline`
- `source_hash`: SHA256 over source inputs (manifests, patterns, pipeline specs)
- `nodes`, `edges`, `reverse_edges`, `topo_levels`, `cycles`
- Optional analytics: `critical_path`, `critical_path_weight`, `metadata` (counts, layers, durations)

## Inputs by Tier
- Tier 1: `MODULES_INVENTORY.yaml` + `modules/*/module.manifest.*` dependencies
- Tier 2: Module manifest artifacts + pattern registry + applicability rules
- Tier 3: Pipeline specs (`pipelines/*.pipeline.yaml`) + per-module task DAGs + module DAG

## Freshness Model
- Regenerate on changes to manifests, inventory, pattern registry, or pipeline specs.
- Staleness check: recompute `source_hash`; mismatch => rebuild.
- Validation: JSON schema per tier + cycle detection + node coverage against inventory/specs.

## Generation/Validation Flow (scripts)
1) `python scripts/refresh_repo_dag.py` — builds all three tiers, writes hashes, creates missing
   `.state/` dirs.
2) `python scripts/validate_dag_freshness.py` — schema check, hash check, cycle check.
3) CI/git hooks call (2), and fall back to (1) on mismatch.

## Consumption Patterns
- Schedulers load Tier 1 for module ordering; orchestrators load Tier 3 for pipeline execution.
- AI tools query DAG JSON for reverse edges (“what depends on X?”) without re-building graphs.
- On missing DAGs, systems may fall back to on-demand computation, but regeneration is preferred.

## Determinism
- Stable sort inputs before hashing.
- Write JSON with consistent ordering.
- Never commit hand-edited DAG JSON; always regenerate from sources.
