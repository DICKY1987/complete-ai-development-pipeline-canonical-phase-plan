---
doc_id: DOC-GUIDE-README-502
---

# Phase 2 – Request Building & Run Creation

**Purpose**: Build ExecutionRequest, validate schema, create run records in DB.

## Current Components
- See `core/state/` for state management
- See `core/engine/execution_request_builder.py` for request building
- See `schema/` for validation schemas

## Main Operations
- User/CLI selects a plan/workstream and requests "run this"
- Build normalized execution request (what, where, tools, patterns, IDs)
- Validate against `request.schema.json`
- Create run record and initial workstream rows in SQLite

## Related Code
- `core/engine/execution_request_builder.py` - Fluent API for requests
- `core/state/db.py`, `db_unified.py`, `crud.py` - Database operations
- `core/state/bundles.py` - Run/workstream bundles
- `core/state/task_queue.py` - Task queue
- `core/state/audit_logger.py` - Audit trail

## Schema Files
- `schema/execution_request.v1.json`
- `schema/run_record.v1.json`
- `schema/workstream_spec.v1.json`
- `schema/step_attempt.v1.json`
- `schema/run_event.v1.json`

## State Storage
- `.state/orchestrator.db`, `.state/orchestration.db`
- `.state/transitions.jsonl`
- `.ledger/framework.db` - Audit ledger

## Status
✅ Complete (100%)
