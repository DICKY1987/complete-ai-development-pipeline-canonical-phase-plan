# Phase Plans: Automation Completion

## Phase A — Planner Wiring (core/planning/planner.py)
- Outcome: Planner consumes real spec inputs and outputs deterministic workstream bundles (no placeholders).
- Steps:
  1) Define input contract (path/JSON) and minimal schema for bundles; add validation and error paths.
  2) Implement decomposition: derive files_scope from spec changes or repo diff; map tasks with gates/tool hints.
  3) Add unit tests for happy path + invalid inputs; run `python -m pytest tests/planning -k planner`.
  4) Update related docs/spec references to mark planner wired (no stub messaging).
- Exit Criteria: No placeholder print/returns; tests passing; doc note moved from “stub” to “implemented”.

## Phase B — Router Strategies (core/engine/router.py)
- Outcome: Routing uses configurable strategies beyond “first capable” and records decisions.
- Steps:
  1) Implement round-robin with persisted state (in-memory first, injectable store for later).
  2) Add metrics-based fallback (pick highest success_score/lowest latency when provided).
  3) Expand config schema validation and tests: missing fields, strategy selection, state rotation.
  4) Expose minimal tracing hook (decision log) for observability.
- Exit Criteria: TODOs removed; tests cover round-robin/metrics paths; default behavior unchanged for simple configs.

## Phase C — Execution Loop & Executors (process_spawner, fix_generator, patterns/executors)
- Outcome: Worker processes invoke real adapters, and pattern executors run end-to-end without TODOs.
- Steps:
  1) Replace dummy sleeper in `process_spawner` with adapter entry (aider/codex/claude), passing env + repo root; add shutdown/cleanup.
  2) Implement `fix_generator` integration with patch application (use existing patch engine); add tests for generated patches applied to failing cases.
  3) For top-priority patterns (`module_creation_*`, `config_setup_001`, `automation_enabled_status`, `implementation_status`), fill executor bodies to call shared libs and respect schema validation.
  4) Add fast tests for executors (happy path + missing inputs) and wire into `pre-commit` optional hook if runtime permits.
- Exit Criteria: No TODO placeholders in target executors; spawning runs real adapter commands (configurable); executor tests passing.
