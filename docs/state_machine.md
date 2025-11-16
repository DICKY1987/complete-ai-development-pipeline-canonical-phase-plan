# State machine

This document describes the canonical states and transitions for runs and
workstreams in the AI development pipeline. The DB layer (`src/pipeline/db.py`)
and subsequent state machine logic enforce these transitions.

Implementation notes:
- Transition validation helpers are introduced in PH-02 in `src/pipeline/db.py`.
- Orchestrator and scheduler (`src/pipeline/orchestrator.py`,
  `src/pipeline/scheduler.py`) call these helpers to persist valid moves.
-
  Events and error deduplication are recorded via the `events` and `errors`
  tables; CRUD helpers are extended in later workstreams.

## Run states

- pending → running → succeeded
- pending → running → failed
- pending → canceled

Valid transitions:

```
pending  -> running
running  -> succeeded | failed | canceled
```

Notes:
- A run becomes `running` when the orchestrator starts scheduling workstreams.
- Terminal states: `succeeded`, `failed`, `canceled`.

## Workstream states

- pending → ready → running → succeeded
- pending → blocked (dependency not met) → ready → running → succeeded
- pending/ready/running → failed
- pending/ready → skipped (explicitly disabled)

Valid transitions:

```
pending -> ready | blocked | skipped
blocked -> ready
ready   -> running | skipped
running -> succeeded | failed
```

Notes:
- `blocked` indicates unmet dependencies; scheduler promotes to `ready` once
  dependencies succeed.
- `skipped` is terminal and indicates intentional omission.
- `failed` is terminal; recovery routines may create a new attempt.

## Enforcement

- The database layer exposes helpers used by the state machine to persist
  transitions and reject invalid moves (via a `validate_state_transition()`
  policy implemented in PH‑02 by the state‑machine workstream).
- Events are recorded for observability; errors are deduplicated via a
  signature in the `errors` table.
