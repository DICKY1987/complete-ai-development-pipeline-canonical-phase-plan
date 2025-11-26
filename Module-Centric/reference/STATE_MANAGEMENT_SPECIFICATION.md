# State Management Specification

Defines how module and global state are stored and referenced.

## Locations
- Per-module state: `modules/<module>/.state/`
  - `current.json` (required): current state snapshot for the module.
  - Optional: `snapshots/`, `transitions/` for history.
- Global state: `.state/` (root)
  - `current.json`, `health.json`, `orchestrator.db`, `transitions.jsonl`
  - DAG storage: `.state/dag/` (derived; see DAG docs)

## Manifest Requirements
- `state.current` must point to the module’s `.state/current.json`.
- State files must not be ULID-prefixed; they are runtime artifacts.

## Invariants
- No code writes into other modules’ `.state/` directories.
- Runtime state is append-only or versioned; avoid destructive rewrites without backup.
- Derived DAGs are regenerated, not edited manually.

## Validation
- Presence: `.state/current.json` exists per module.
- Access: tests should not require mutation of global state; prefer module-local state.
- Backup: optional snapshots before major migration (`tree_before.txt`, `tree_after.txt`).
