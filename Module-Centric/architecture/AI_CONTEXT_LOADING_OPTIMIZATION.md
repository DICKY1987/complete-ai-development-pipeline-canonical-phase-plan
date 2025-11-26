# AI Context Loading Optimization

Goal: minimize context size and ambiguity for AI tools by aligning repository structure with module
boundaries.

## Principles
- Atomic context = one module directory (code, tests, schemas, docs, state).
- ULID-prefixed artifacts give machine-verifiable grouping; manifests enumerate all artifacts.
- Precomputed DAGs provide dependency answers without scanning the repo.

## Loading Pattern
- To work on a module: load `modules/<module_id>/` only.
- To understand dependencies: load `.state/dag/repo_modules.dag.json` and per-module DAGs as needed.
- Avoid global “all docs/all tests” scans; module folders co-locate everything relevant.

## Benefits
- Smaller, more relevant AI prompts; faster grounding.
- Reduced hallucination risk: boundaries are explicit, imports are clean.
- Deterministic provenance: ULID + manifest + DAG hash tell the tool exactly what is current.

## Hygiene
- Keep manifests up to date; regenerate DAGs on change.
- Ensure `__init__.py` exports match intended public surface.
- Use inventory and DAGs for “who depends on X?” instead of repo-wide greps.

## Examples
- Load single module for editing:
  ```
  modules/core-engine/
    010001_orchestrator.py
    010001_orchestrator.test.py
    module.manifest.json
    __init__.py
    .state/current.json
  ```
  Context load = this directory only; dependencies come from `repo_modules.dag.json`.
- Dependency lookup without scanning code:
  ```python
  import json
  dag = json.load(open(".state/dag/repo_modules.dag.json"))
  dependents = dag["reverse_edges"].get("core-engine", [])
  ```
