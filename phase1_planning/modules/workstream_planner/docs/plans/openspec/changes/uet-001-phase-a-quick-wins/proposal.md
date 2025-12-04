---
doc_id: DOC-GUIDE-PROPOSAL-1507
---

# Phase A: Quick Wins - UET Implementation

**Change ID**: uet-001-phase-a-quick-wins
**Parent**: uet-001-complete-implementation
**Type**: Infrastructure Enhancement
**Priority**: HIGH (Critical Path)
**Status**: Ready for Implementation
**Estimated Duration**: 1-2 weeks
**Effort**: 18 hours

---

## Problem Statement

This is the **foundation phase** for UET alignment. Currently:

- UET schemas exist in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` but are not available to production code
- Worker health is not monitored (workers can fail silently)
- Events are emitted but not persisted (no replay/debugging capability)
- Test failures don't automatically create fix tasks (manual intervention required)
- Context estimator exists but lacks pruning/summarization

**Risk**: All subsequent phases depend on this foundation. Failure here blocks entire UET migration.

---

## Proposed Solution

Implement **low-risk, high-value** enhancements that immediately improve system reliability and enable future phases.

### Key Deliverables

1. **Schema Foundation**: Copy all 17 UET schemas to production
2. **Worker Health**: Heartbeat monitoring with quarantine
3. **Event Persistence**: Database-backed event sourcing
4. **Feedback Loop**: Automatic fix task creation
5. **Context Manager**: Token-aware operations

---

## Requirements

### Functional Requirements

**Schema Foundation**:
- SHALL copy all 17 UET schemas from `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/` to `schema/uet/`
- SHALL validate all copied schemas with JSON Schema validator
- SHALL document each schema in `schema/uet/README.md`

**Worker Health**:
- SHALL implement heartbeat monitoring (30-second intervals)
- SHALL quarantine workers failing 3 consecutive health checks
- SHALL emit `WORKER_HEALTH_CHECK_FAILED` event on failure
- SHALL integrate health checks into WorkerPool lifecycle

**Event Persistence**:
- SHALL create `run_events` table in database
- SHALL persist all events emitted by EventBus
- SHALL support event replay for debugging
- SHALL provide event subscribers for orchestrator

**Feedback Loop**:
- SHALL auto-create fix tasks when tests fail
- SHALL prioritize fix tasks by failure impact (blocking > warning)
- SHALL block dependent tasks until failures resolved
- SHALL emit `FEEDBACK_TASK_CREATED` events

**Context Manager**:
- SHALL enhance context_estimator with token counting per model
- SHALL implement pruning strategy (remove low-value sections)
- SHALL add summarization (first/last N lines for large files)
- SHALL implement chunking for tasks exceeding token limits

### Non-Functional Requirements

**Performance**:
- Health checks SHALL NOT add >100ms overhead per worker
- Event persistence SHALL be asynchronous (non-blocking)
- Context operations SHALL complete in <200ms

**Reliability**:
- Health check failures SHALL NOT crash workers
- Event persistence failures SHALL log errors but continue execution
- All operations SHALL have rollback/recovery paths

---

## Implementation Tasks

### 1. Schema Foundation (2 hours)

```powershell
# Copy schemas
Copy-Item -Recurse `
  "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json" `
  "schema\uet\"

# Validate
python -c "
import json
from pathlib import Path
for schema in Path('schema/uet').glob('*.json'):
    json.loads(schema.read_text())
    print(f'✅ {schema.name}')
"
```

- [ ] Copy all 17 schemas
- [ ] Validate JSON syntax
- [ ] Create `schema/uet/README.md` documenting each schema
- [ ] Update `.gitignore` if needed

### 2. Worker Health System (4 hours)

**File**: `core/engine/worker_health.py`

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    worker_id: str
    timestamp: datetime
    status: HealthStatus
    last_heartbeat: datetime
    consecutive_failures: int

class WorkerHealthMonitor:
    HEARTBEAT_INTERVAL = 30  # seconds
    MAX_FAILURES = 3

    def check_health(self, worker_id: str) -> HealthCheck:
        """Check worker health via heartbeat."""
        last_heartbeat = self._get_last_heartbeat(worker_id)
        age = (datetime.utcnow() - last_heartbeat).total_seconds()

        if age < self.HEARTBEAT_INTERVAL:
            return HealthCheck(worker_id, datetime.utcnow(),
                             HealthStatus.HEALTHY, last_heartbeat, 0)
        elif age < self.HEARTBEAT_INTERVAL * 2:
            return HealthCheck(worker_id, datetime.utcnow(),
                             HealthStatus.DEGRADED, last_heartbeat, 1)
        else:
            failures = self._increment_failures(worker_id)
            if failures >= self.MAX_FAILURES:
                self._quarantine_worker(worker_id)
            return HealthCheck(worker_id, datetime.utcnow(),
                             HealthStatus.UNHEALTHY, last_heartbeat, failures)
```

- [ ] Create module
- [ ] Implement heartbeat monitoring
- [ ] Add quarantine logic
- [ ] Integrate with WorkerPool
- [ ] Add tests

### 3. Event Persistence (4 hours)

**Migration**: `schema/migrations/001_add_run_events.sql`

```sql
CREATE TABLE run_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload TEXT,  -- JSON
    source TEXT,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE INDEX idx_run_events_run_id ON run_events(run_id);
CREATE INDEX idx_run_events_type ON run_events(event_type);
CREATE INDEX idx_run_events_timestamp ON run_events(timestamp);
```

**Code**: Modify `core/engine/event_bus.py`

```python
def emit(self, event: Event):
    """Emit event and persist to database."""
    # Existing in-memory notification
    for subscriber in self._subscribers[event.event_type]:
        subscriber(event)

    # NEW: Persist to database
    self._persist_event(event)

def _persist_event(self, event: Event):
    """Persist event to database for replay."""
    from core.state import db
    db.insert_event(
        run_id=event.run_id,
        event_type=event.event_type.value,
        timestamp=event.timestamp.isoformat(),
        payload=event.payload,
        source=event.source
    )
```

- [ ] Create migration
- [ ] Modify EventBus
- [ ] Add db.insert_event()
- [ ] Implement event replay
- [ ] Add tests

### 4. Feedback Loop (4 hours)

**File**: `core/engine/feedback_loop.py`

```python
from dataclasses import dataclass
from typing import List

@dataclass
class FeedbackTask:
    task_id: str
    trigger_event: str  # Original failure event
    priority: int  # 1=critical, 2=high, 3=medium
    description: str
    blocked_tasks: List[str]

class FeedbackLoop:
    def on_test_failure(self, event):
        """Create fix task when test fails."""
        priority = self._calculate_priority(event)
        blocked = self._find_dependent_tasks(event)

        fix_task = FeedbackTask(
            task_id=f"fix-{event.source}",
            trigger_event=event.event_type.value,
            priority=priority,
            description=f"Fix test failure: {event.payload.get('error')}",
            blocked_tasks=blocked
        )

        self._create_task(fix_task)
        self.event_bus.emit(Event(
            EventType.FEEDBACK_TASK_CREATED,
            payload={'task_id': fix_task.task_id}
        ))
```

- [ ] Create module
- [ ] Implement task creation logic
- [ ] Add priority calculation
- [ ] Add dependency blocking
- [ ] Add tests

### 5. Context Manager (4 hours)

**File**: Enhance `core/engine/context_estimator.py` → `core/engine/context_manager.py`

```python
class ContextManager:
    MODEL_TOKEN_LIMITS = {
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'claude-2': 100000,
        'claude-3': 200000
    }

    def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for given model."""
        # Rough estimate: 1 token ≈ 4 chars
        return len(text) // 4

    def prune_context(self, context: str, max_tokens: int) -> str:
        """Remove low-value sections to fit token limit."""
        sections = self._split_sections(context)
        scores = [self._calculate_importance(s) for s in sections]

        # Sort by importance, keep highest-scoring
        kept = []
        tokens = 0
        for section, score in sorted(zip(sections, scores),
                                    key=lambda x: x[1], reverse=True):
            section_tokens = self.estimate_tokens(section, 'gpt-4')
            if tokens + section_tokens <= max_tokens:
                kept.append(section)
                tokens += section_tokens

        return '\n'.join(kept)

    def summarize(self, text: str, max_lines: int = 50) -> str:
        """Summarize large text to N lines."""
        lines = text.splitlines()
        if len(lines) <= max_lines:
            return text

        # Keep first and last sections
        first_n = max_lines // 2
        last_n = max_lines - first_n
        return '\n'.join(lines[:first_n] +
                        [f'... ({len(lines) - max_lines} lines omitted) ...'] +
                        lines[-last_n:])
```

- [ ] Rename/enhance module
- [ ] Add token estimation
- [ ] Implement pruning
- [ ] Implement summarization
- [ ] Implement chunking
- [ ] Add tests

---

## Success Criteria

### Acceptance Tests

```bash
# Schema validation
python scripts/validate_uet_schemas.py
# Expected: 17/17 schemas valid

# Worker health
pytest tests/engine/test_worker_health.py -v
# Expected: All health check tests pass

# Event persistence
pytest tests/engine/test_event_persistence.py -v
# Expected: Events persisted and replayed correctly

# Feedback loop
pytest tests/engine/test_feedback_loop.py -v
# Expected: Fix tasks created on test failure

# Context manager
pytest tests/engine/test_context_manager.py -v
# Expected: Pruning/summarization working
```

### Quality Gates

- ✅ All 17 UET schemas copied and validated
- ✅ Worker health tests passing (>= 80% coverage)
- ✅ Events persisted to database
- ✅ Event replay working
- ✅ Feedback loop creating fix tasks
- ✅ Context manager estimating tokens accurately
- ✅ No regressions in existing tests
- ✅ Performance overhead <5% vs baseline

---

## Dependencies

**Depends On**:
- None (this is Phase A - foundation)

**Required By**:
- Phase B (needs schemas for patch validation)
- Phase C (needs event persistence for orchestration)
- Phase D (needs context manager for adapters)
- Phase E (needs feedback loop for human review)

---

## Risks

**Risk 1: Schema copy conflicts with existing files**
**Mitigation**: Check for conflicts before copy, use `schema/uet/` subdirectory

**Risk 2: Event persistence slows down execution**
**Mitigation**: Async writes, batch inserts, performance tests

**Risk 3: Health checks create noise (false positives)**
**Mitigation**: Tunable thresholds, grace period before quarantine

---

## Rollback Plan

If Phase A fails:

```powershell
# Remove copied schemas
Remove-Item -Recurse schema\uet\

# Revert code changes
git checkout core/engine/worker_health.py
git checkout core/engine/event_bus.py
git checkout core/engine/feedback_loop.py
git checkout core/engine/context_manager.py

# Revert database
sqlite3 .worktrees/pipeline_state.db < schema/migrations/001_rollback.sql
```

All changes are **additive** - rollback is safe.

---

## Files Created/Modified

### Created
- `schema/uet/` (17 schema files)
- `schema/uet/README.md`
- `core/engine/worker_health.py`
- `core/engine/feedback_loop.py`
- `core/engine/context_manager.py`
- `schema/migrations/001_add_run_events.sql`
- `tests/engine/test_worker_health.py`
- `tests/engine/test_feedback_loop.py`
- `tests/engine/test_context_manager.py`

### Modified
- `core/engine/event_bus.py` (add persistence)
- `core/engine/worker.py` (integrate health checks)
- `core/state/db.py` (add insert_event())

---

## Next Steps

After Phase A completion:
1. Validate all success criteria met
2. Generate alignment report
3. Proceed to Phase B (Patch System)
4. Begin Phase C (Orchestration) in parallel if resources allow
