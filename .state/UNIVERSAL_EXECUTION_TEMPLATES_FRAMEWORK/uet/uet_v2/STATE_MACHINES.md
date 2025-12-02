---
doc_id: DOC-GUIDE-STATE-MACHINES-1666
---

# UET V2 State Machines

**Purpose**: Define all state machines for UET V2 components with transition rules and invariants  
**Status**: DRAFT  
**Last Updated**: 2025-11-23

---

## Table of Contents

- [Worker State Machine](#worker-state-machine)
- [Patch Ledger State Machine](#patch-ledger-state-machine)
- [Test Gate State Machine](#test-gate-state-machine)
- [State Transition Rules](#state-transition-rules)
- [Database Constraints](#database-constraints)

---

## Worker State Machine

### States

```
SPAWNING → IDLE → BUSY → DRAINING → TERMINATED
    ↓               ↓
TERMINATED   TERMINATED
```

| State | Description | Terminal |
|-------|-------------|----------|
| **SPAWNING** | Worker being created/initialized | No |
| **IDLE** | Worker ready and waiting for tasks | No |
| **BUSY** | Worker actively executing a task | No |
| **DRAINING** | Worker finishing current task before shutdown | No |
| **TERMINATED** | Worker stopped and removed from pool | Yes |

### Valid Transitions

| From | To | Trigger | Notes |
|------|-----|---------|-------|
| SPAWNING | IDLE | Worker initialization complete | Normal spawn |
| SPAWNING | TERMINATED | Spawn failed | Error during init |
| IDLE | BUSY | Task assigned to worker | Normal operation |
| IDLE | TERMINATED | Shutdown requested | Immediate shutdown |
| BUSY | IDLE | Task completed successfully | Return to pool |
| BUSY | DRAINING | Shutdown requested while busy | Graceful shutdown |
| BUSY | TERMINATED | Worker crashed | Abnormal termination |
| DRAINING | TERMINATED | Current task finished | Graceful completion |

### Invalid Transitions

These transitions will raise `ValueError`:

- **TERMINATED → any state** (terminal state, cannot restart)
- **IDLE → SPAWNING** (cannot go backward)
- **BUSY → SPAWNING** (cannot go backward)
- **DRAINING → IDLE** (must complete shutdown)
- **DRAINING → BUSY** (no new tasks while draining)

### State Invariants

1. **Heartbeat Required**: Workers in IDLE or BUSY must send heartbeat every 60s
2. **Timeout Detection**: Workers missing 2 consecutive heartbeats → quarantine → TERMINATED
3. **Affinity Immutable**: `worker.affinity` cannot change after SPAWNING
4. **Timestamp Accuracy**: `terminated_at` only set in TERMINATED state

### Database Representation

```sql
CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    worker_type TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED')),
    affinity TEXT,  -- JSON
    last_heartbeat TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TEXT,
    CHECK ((state = 'TERMINATED' AND terminated_at IS NOT NULL) OR (state != 'TERMINATED' AND terminated_at IS NULL))
);
```

### State Change Examples

**Normal Workflow**:
```
SPAWNING (worker created)
    ↓
IDLE (initialization complete, waiting)
    ↓
BUSY (assigned task: "fix linting errors in core/engine/executor.py")
    ↓
IDLE (task complete, returned to pool)
    ↓
BUSY (assigned task: "run unit tests")
    ↓
IDLE (tests passed)
    ↓
TERMINATED (shutdown requested)
```

**Graceful Shutdown While Busy**:
```
BUSY (task running: 50% complete)
    ↓
DRAINING (shutdown requested, finish current task)
    ↓ (task completes)
TERMINATED
```

**Crash Scenario**:
```
BUSY (task running)
    ↓ (worker process dies)
TERMINATED (abnormal termination)
```

---

## Patch Ledger State Machine

### States

```
created → validated → queued → applied → verified → committed
   ↓         ↓          ↓         ↓         ↓
quarantined, apply_failed → quarantined/dropped
committed → rolled_back
```

| State | Description | Terminal |
|-------|-------------|----------|
| **created** | Patch artifact created, not yet validated | No |
| **validated** | Passed format/scope/constraint checks | No |
| **queued** | Accepted for merge, awaiting application | No |
| **applied** | Git apply succeeded, awaiting test verification | No |
| **apply_failed** | Git apply failed (conflicts, errors) | No |
| **verified** | Applied patch passed all tests | No |
| **committed** | Git committed to main branch | No |
| **rolled_back** | Previously committed patch was reverted | Yes |
| **quarantined** | Patch failed validation or tests | Yes |
| **dropped** | Patch discarded without application | Yes |

### Valid Transitions

| From | To | Trigger | Validation Required |
|------|-----|---------|---------------------|
| created | validated | All validation checks pass | ✅ Format, Scope, Constraints |
| created | quarantined | Validation failed | ❌ |
| validated | queued | Accepted for merge | ✅ Phase policy check |
| validated | quarantined | Policy violation detected | ❌ |
| queued | applied | `git apply` succeeded | ✅ Git operations |
| queued | apply_failed | `git apply` failed | ❌ |
| applied | verified | All tests passed | ✅ Test gates |
| applied | quarantined | Tests failed | ❌ |
| apply_failed | quarantined | Auto-quarantine after failure | ❌ |
| apply_failed | dropped | Manual discard decision | ❌ |
| verified | committed | `git commit` succeeded | ✅ Final commit |
| committed | rolled_back | Rollback requested | ✅ Compensation logic |

### Invalid Transitions

These transitions are **forbidden** (raise `ValueError`):

- **committed → created** (cannot un-commit to re-create)
- **committed → queued** (cannot re-queue committed patch)
- **quarantined → any state except dropped** (terminal, must create new patch)
- **dropped → any state** (terminal)
- **rolled_back → any state** (terminal)

### State Invariants

1. **State History Append-Only**: Never delete from `state_history`, only append
2. **Quarantine Reason Required**: If state=quarantined, `quarantine_reason` must be set
3. **Validation Flags**: Format/scope/constraint/test flags match current state
4. **Timestamp Monotonicity**: `updated_at` always ≥ `created_at`

### Database Representation

```sql
CREATE TABLE IF NOT EXISTS patch_ledger_entries (
    ledger_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN (
        'created', 'validated', 'queued', 'applied', 'apply_failed',
        'verified', 'committed', 'rolled_back', 'quarantined', 'dropped'
    )),
    phase_id TEXT,
    workstream_id TEXT,
    validation_format_passed BOOLEAN DEFAULT FALSE,
    validation_scope_passed BOOLEAN DEFAULT FALSE,
    validation_constraints_passed BOOLEAN DEFAULT FALSE,
    validation_tests_passed BOOLEAN DEFAULT FALSE,
    quarantine_reason TEXT,
    state_history TEXT NOT NULL,  -- JSON array
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (patch_id) REFERENCES patches(patch_id),
    CHECK ((state = 'quarantined' AND quarantine_reason IS NOT NULL) OR state != 'quarantined')
);
```

### State Change Examples

**Happy Path (Success)**:
```
created (patch generated by aider)
    ↓ [validate: format=✅, scope=✅, constraints=✅]
validated
    ↓ [policy check: phase constraints satisfied]
queued
    ↓ [git apply patch.diff]
applied
    ↓ [pytest tests/ → all pass]
verified
    ↓ [git commit -m "Applied patch XYZ"]
committed
```

**Validation Failure**:
```
created (patch modifies .git/config - forbidden)
    ↓ [validate: constraints=❌ (forbidden path)]
quarantined (reason: "Attempted to modify .git/config")
```

**Test Failure**:
```
created
    ↓ [validate: all pass]
validated
    ↓
queued
    ↓ [git apply succeeded]
applied
    ↓ [pytest tests/ → 3 failures]
quarantined (reason: "Tests failed: test_executor.py::test_timeout, ...")
```

**Apply Failure (Conflict)**:
```
created
    ↓
validated
    ↓
queued
    ↓ [git apply → CONFLICT in core/engine/executor.py]
apply_failed
    ↓ [auto-quarantine after 3 retry attempts]
quarantined (reason: "Merge conflict in executor.py line 45")
```

**Rollback Scenario**:
```
committed (patch applied 2 hours ago)
    ↓ [regression detected: gate failures in subsequent workstream]
rolled_back (compensation action executed)
```

---

## Test Gate State Machine

### States

```
PENDING → RUNNING → PASSED
            ↓
         FAILED → BLOCKED (dependent tasks)
```

| State | Description | Terminal |
|-------|-------------|----------|
| **PENDING** | Gate defined but not yet executed | No |
| **RUNNING** | Gate command currently executing | No |
| **PASSED** | Gate command returned expected exit code (0) | Yes |
| **FAILED** | Gate command returned non-zero exit code | Yes |
| **BLOCKED** | Gate cannot run (dependencies not met) | No |

### Valid Transitions

| From | To | Trigger | Notes |
|------|-----|---------|-------|
| PENDING | RUNNING | Gate executor starts command | Normal execution |
| PENDING | BLOCKED | Dependency gate failed | Wait for fix |
| RUNNING | PASSED | Exit code = expected (usually 0) | Success |
| RUNNING | FAILED | Exit code ≠ expected | Failure |
| BLOCKED | PENDING | Dependency gate now passed | Unblock |

### Invalid Transitions

- **PASSED → any state** (terminal success)
- **FAILED → PASSED** (cannot change result, must re-run)
- **RUNNING → PENDING** (cannot restart mid-execution)

### State Invariants

1. **Timeout Enforcement**: Gates in RUNNING state for > timeout_sec → FAILED
2. **Blocking Cascades**: If gate fails, all dependent tasks → BLOCKED
3. **Exit Code Recorded**: PASSED/FAILED states must have `exit_code` set
4. **Stdout/Stderr Captured**: PASSED/FAILED states must have output captured

### Database Representation

```sql
CREATE TABLE IF NOT EXISTS test_gates (
    gate_id TEXT PRIMARY KEY,
    gate_type TEXT NOT NULL CHECK(gate_type IN ('LINT', 'UNIT', 'INTEGRATION', 'SECURITY')),
    phase_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'BLOCKED')),
    command TEXT NOT NULL,
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    duration_sec REAL,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id),
    CHECK ((state IN ('PASSED', 'FAILED') AND exit_code IS NOT NULL) OR state NOT IN ('PASSED', 'FAILED'))
);
```

### State Change Examples

**Successful Gate**:
```
PENDING (gate: LINT, command: "ruff check core/")
    ↓ [executor starts]
RUNNING
    ↓ [ruff exits with 0]
PASSED (exit_code=0, duration=2.3s)
```

**Failed Gate**:
```
PENDING (gate: UNIT, command: "pytest tests/")
    ↓
RUNNING
    ↓ [pytest exits with 1, 3 tests failed]
FAILED (exit_code=1, stderr="3 failed, 45 passed")
    ↓ [dependent tasks blocked]
BLOCKED → Task A, Task B, Task C
```

**Blocked Then Unblocked**:
```
PENDING (gate: INTEGRATION, depends_on: UNIT gate)
    ↓ [UNIT gate fails]
BLOCKED (waiting for UNIT to pass)
    ↓ [fixes applied, UNIT gate re-run and passes]
PENDING (dependency satisfied)
    ↓
RUNNING
    ↓
PASSED
```

---

## State Transition Rules

### General Principles

1. **Monotonic Progress**: States generally move forward (created → validated → committed)
2. **Terminal States**: Once reached, no further transitions (except rollback for committed patches)
3. **Validation Required**: All forward transitions require validation checks to pass
4. **Reason Tracking**: Failed transitions must record reason in state_history
5. **Timestamp Tracking**: All transitions record timestamp

### Concurrent State Changes

**Problem**: Two workers try to transition same patch simultaneously

**Solution**: Database-level locking with optimistic concurrency control

```python
def transition_state(self, ledger_id: str, new_state: PatchState, reason: str = "") -> bool:
    # Read current state with version
    entry = self.db.execute(
        "SELECT state, updated_at FROM patch_ledger_entries WHERE ledger_id = ?",
        (ledger_id,)
    ).fetchone()
    
    original_updated_at = entry['updated_at']
    
    # Validate transition
    if not self._is_valid_transition(entry['state'], new_state):
        raise ValueError(f"Invalid transition: {entry['state']} → {new_state}")
    
    # Update with optimistic locking
    result = self.db.execute(
        """
        UPDATE patch_ledger_entries
        SET state = ?, updated_at = ?
        WHERE ledger_id = ? AND updated_at = ?
        """,
        (new_state.value, datetime.now().isoformat(), ledger_id, original_updated_at)
    )
    
    if result.rowcount == 0:
        # Someone else modified this patch - retry
        return self.transition_state(ledger_id, new_state, reason)
    
    return True
```

---

## Database Constraints

### CHECK Constraints

**Worker State**:
```sql
CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED'))
```

**Patch State**:
```sql
CHECK(state IN ('created', 'validated', 'queued', 'applied', 'apply_failed', 
                'verified', 'committed', 'rolled_back', 'quarantined', 'dropped'))
```

**Gate State**:
```sql
CHECK(state IN ('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'BLOCKED'))
```

### Conditional Constraints

**Worker Termination Timestamp**:
```sql
CHECK (
    (state = 'TERMINATED' AND terminated_at IS NOT NULL) OR 
    (state != 'TERMINATED' AND terminated_at IS NULL)
)
```

**Patch Quarantine Reason**:
```sql
CHECK (
    (state = 'quarantined' AND quarantine_reason IS NOT NULL) OR 
    state != 'quarantined'
)
```

**Gate Exit Code**:
```sql
CHECK (
    (state IN ('PASSED', 'FAILED') AND exit_code IS NOT NULL) OR 
    state NOT IN ('PASSED', 'FAILED')
)
```

---

## State Machine Validation

### Unit Test Requirements

Every state machine must have tests for:

1. **All Valid Transitions** (one test per transition)
2. **All Invalid Transitions** (verify ValueError raised)
3. **Invariant Enforcement** (check database constraints)
4. **Concurrent Modifications** (optimistic locking)
5. **State History Tracking** (append-only, timestamps)

### Example Test (Patch Ledger)

```python
def test_patch_ledger_valid_transition_created_to_validated():
    ledger = PatchLedger(db)
    entry = ledger.create_entry(patch, "PH-007", "WS-007-001")
    
    # Transition to validated
    result = ledger.transition_state(entry.ledger_id, PatchState.VALIDATED, "All checks passed")
    
    assert result is True
    updated_entry = ledger.get_entry(entry.ledger_id)
    assert updated_entry.state == PatchState.VALIDATED
    assert len(updated_entry.state_history) == 2  # created + validated

def test_patch_ledger_invalid_transition_committed_to_queued():
    ledger = PatchLedger(db)
    entry = ledger.create_entry(patch, "PH-007", "WS-007-001")
    
    # Fast-forward to committed
    ledger.transition_state(entry.ledger_id, PatchState.VALIDATED)
    ledger.transition_state(entry.ledger_id, PatchState.QUEUED)
    ledger.transition_state(entry.ledger_id, PatchState.APPLIED)
    ledger.transition_state(entry.ledger_id, PatchState.VERIFIED)
    ledger.transition_state(entry.ledger_id, PatchState.COMMITTED)
    
    # Try invalid transition
    with pytest.raises(ValueError, match="Invalid transition"):
        ledger.transition_state(entry.ledger_id, PatchState.QUEUED)
```

---

## State Machine Diagrams

### Visual Diagrams (ASCII Art)

**Worker Lifecycle**:
```
┌──────────┐
│ SPAWNING │
└────┬─────┘
     │ init complete
     ▼
┌──────┐      task assigned      ┌──────┐
│ IDLE │─────────────────────────▶│ BUSY │
└───┬──┘                          └───┬──┘
    │                                 │
    │ shutdown                        │ task complete
    │                                 │
    ▼                                 ▼
┌────────────┐                   ┌──────┐
│ TERMINATED │◀──────────────────│ IDLE │
└────────────┘                   └──────┘
                                      │
                                      │ shutdown while busy
                                      ▼
                                 ┌──────────┐
                                 │ DRAINING │
                                 └─────┬────┘
                                       │
                                       │ task complete
                                       ▼
                                 ┌────────────┐
                                 │ TERMINATED │
                                 └────────────┘
```

**Patch Ledger** (Success Path):
```
created → validated → queued → applied → verified → committed
```

**Patch Ledger** (Failure Paths):
```
created → quarantined (validation failed)
validated → quarantined (policy violation)
queued → apply_failed → quarantined (git conflict)
applied → quarantined (tests failed)
committed → rolled_back (regression)
```

---

## References

- **Component Contracts**: [COMPONENT_CONTRACTS.md](COMPONENT_CONTRACTS.md)
- **Integration Points**: [INTEGRATION_POINTS.md](INTEGRATION_POINTS.md)
- **Database Migrations**: [DATABASE_MIGRATIONS.md](DATABASE_MIGRATIONS.md)

---

**Last Updated**: 2025-11-23  
**Next Review**: Before Phase A starts
