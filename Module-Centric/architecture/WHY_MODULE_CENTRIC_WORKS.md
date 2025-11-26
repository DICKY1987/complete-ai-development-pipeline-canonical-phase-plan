# Why Module-Centric Works

Module-centric organization outperforms artifact-type layouts for AI-first development.

## Key Advantages
- Locality of reference: each module folder holds code, tests, schemas, docs, and state together.
- Atomic context loading: AI tools load one directory to understand/modify a module.
- SafePatch/worktrees align naturally: clone only the module being changed.
- Immutable identity: ULID-prefixed artifacts make relationships machine-verifiable.
- Parallel execution: module boundaries reduce contention; DAGs order modules safely.
- Self-contained portability: a module directory is a portable unit with its contracts and tests.

## Structure
```
modules/<module>/
  01JDEX_code.py
  01JDEX_code.test.py
  01JDEX_code.schema.json
  01JDEX_code.md
  module.manifest.json
  __init__.py
  .state/current.json
```

## Trade-offs
- Lose single “all docs/tests” folders, but gain clarity for automation and AI context.
- Requires import wrappers (`__init__.py`) to hide numeric filenames.
- Requires DAG regeneration and manifest upkeep to stay consistent.

## Integration with Existing Systems
- Global `.state/` remains for shared artifacts; per-module `.state/` for local state.
- DAGs and manifests bridge modules to pipelines, schedulers, and AI tooling.

## Examples
- Per-module context load (AI prompt scope):
  ```
  modules/error-engine/
    010004_error_engine.py
    010004_error_engine.test.py
    010004_error_engine.schema.json
    010004_README.md
    module.manifest.json
    __init__.py
    .state/current.json
  ```
  No need to traverse global docs/tests folders.
- SafePatch/worktree alignment:
  - Work on `modules/error-engine/` in its own worktree; run module DAG + tests locally.

## Diagram (module as portable unit)
```
┌─────────────────────────────┐
│ modules/<module_id>/        │
│  ├─ ULID code/tests/schemas │
│  ├─ module.manifest.*       │
│  ├─ __init__.py (exports)   │
│  └─ .state/current.json     │
└─────────────────────────────┘
            │
            ▼
   DAGs + Inventory + Pipelines
            │
            ▼
   AI tools / Orchestrators
```
