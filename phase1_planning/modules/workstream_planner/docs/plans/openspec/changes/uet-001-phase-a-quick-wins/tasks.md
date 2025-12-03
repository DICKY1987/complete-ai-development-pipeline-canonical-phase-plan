---
doc_id: DOC-GUIDE-TASKS-1508
---

# Phase A Tasks - Quick Wins

## Schema Foundation

- [ ] Copy all 17 UET schemas to `schema/uet/`
- [ ] Validate JSON syntax for all schemas
- [ ] Create `schema/uet/README.md`
- [ ] Test schema loading in Python

## Worker Health System

- [ ] Create `core/engine/worker_health.py`
- [ ] Implement `HealthStatus` enum
- [ ] Implement `HealthCheck` dataclass
- [ ] Implement `WorkerHealthMonitor` class
- [ ] Add heartbeat tracking
- [ ] Add quarantine logic
- [ ] Integrate with `WorkerPool`
- [ ] Add `WORKER_HEALTH_CHECK_FAILED` event
- [ ] Write unit tests

## Event Persistence

- [ ] Create `schema/migrations/001_add_run_events.sql`
- [ ] Add `run_events` table
- [ ] Add indexes (run_id, event_type, timestamp)
- [ ] Modify `core/engine/event_bus.py`
- [ ] Add `_persist_event()` method
- [ ] Add `db.insert_event()` to `core/state/db.py`
- [ ] Implement event replay
- [ ] Write tests

## Feedback Loop

- [ ] Create `core/engine/feedback_loop.py`
- [ ] Implement `FeedbackTask` dataclass
- [ ] Implement `FeedbackLoop` class
- [ ] Add `on_test_failure()` handler
- [ ] Add priority calculation
- [ ] Add dependency blocking
- [ ] Add `FEEDBACK_TASK_CREATED` event
- [ ] Write integration tests

## Context Manager

- [ ] Rename `context_estimator.py` to `context_manager.py`
- [ ] Add `MODEL_TOKEN_LIMITS` constant
- [ ] Implement `estimate_tokens()`
- [ ] Implement `prune_context()`
- [ ] Implement `summarize()`
- [ ] Implement `chunk_if_needed()`
- [ ] Write tests for all operations

## Testing

- [ ] Create `tests/engine/test_worker_health.py`
- [ ] Create `tests/engine/test_event_persistence.py`
- [ ] Create `tests/engine/test_feedback_loop.py`
- [ ] Create `tests/engine/test_context_manager.py`
- [ ] Run full test suite (no regressions)

## Documentation

- [ ] Document worker health in `docs/WORKER_LIFECYCLE.md`
- [ ] Document event persistence in `docs/EVENT_SOURCING.md`
- [ ] Document feedback loop in `docs/FEEDBACK_LOOP.md`
- [ ] Update `AGENTS.md` with new modules
