---
doc_id: DOC-GUIDE-STATE-MACHINES-397
---

# State Machine Documentation

**Purpose:** Document state machines with visual diagrams, transition rules, and recovery procedures.

**Last Updated:** 2025-11-22  
**Maintainer:** System Architecture Team

---

## Overview

This document provides:
- **Visual State Diagrams:** ASCII art representation of states and transitions
- **Transition Rules:** Valid and invalid state changes
- **Recovery Procedures:** How to recover from invalid states
- **State Semantics:** What each state means

---

## Workstream State Machine

### State Diagram

```
                    ┌──────────────┐
                    │  S_PENDING   │ (Initial state)
                    └──────┬───────┘
                           │
                           │ start_execution()
                           ↓
                    ┌──────────────┐
           ┌────────│  S_RUNNING   │────────┐
           │        └──────┬───────┘        │
           │               │                │
           │               │                │
    all_steps_succeed()  step_fails()     abandon()
           │               │                │
           ↓               ↓                ↓
    ┌──────────┐    ┌──────────┐    ┌─────────────┐
    │S_SUCCESS │    │ S_FAILED │    │ S_ABANDONED │
    └──────────┘    └────┬─────┘    └─────────────┘
                         │
                         │ retry_eligible()
                         ↓
                   ┌────────────┐
                   │S_RETRYING  │
                   └────┬───────┘
                        │
                        │ retry_attempt()
                        ↓
                  (back to S_RUNNING)
```

### State Definitions

| State | Code | Meaning | Terminal? |
|-------|------|---------|-----------|
| **Pending** | `S_PENDING` | Workstream created, not yet started | No |
| **Running** | `S_RUNNING` | Workstream is actively executing steps | No |
| **Success** | `S_SUCCESS` | All steps completed successfully | Yes |
| **Failed** | `S_FAILED` | One or more steps failed | No (can retry) |
| **Retrying** | `S_RETRYING` | Waiting before retry attempt | No |
| **Abandoned** | `S_ABANDONED` | Manually stopped or max retries exceeded | Yes |

**Terminal States:** Once reached, workstream cannot transition to another state (immutable).

---

### Valid Transitions

| From State | To State | Trigger | Conditions |
|------------|----------|---------|------------|
| `S_PENDING` | `S_RUNNING` | Orchestrator starts execution | None |
| `S_RUNNING` | `S_SUCCESS` | All steps complete | All steps in `S_SUCCESS` |
| `S_RUNNING` | `S_FAILED` | Step fails | Any step enters `S_FAILED` |
| `S_RUNNING` | `S_ABANDONED` | User cancels | Manual intervention |
| `S_FAILED` | `S_RETRYING` | Retry logic activates | `retry_count < max_retries` |
| `S_FAILED` | `S_ABANDONED` | Max retries exceeded | `retry_count >= max_retries` |
| `S_RETRYING` | `S_RUNNING` | Retry delay expires | After backoff period |

### Invalid Transitions (Will Raise Error)

| From State | To State | Why Invalid |
|------------|----------|-------------|
| `S_SUCCESS` | Any | Terminal state, cannot change |
| `S_ABANDONED` | Any | Terminal state, cannot change |
| `S_PENDING` | `S_SUCCESS` | Must run before succeeding |
| `S_PENDING` | `S_FAILED` | Must run before failing |
| `S_RUNNING` | `S_PENDING` | Cannot go back to pending |
| `S_SUCCESS` | `S_RUNNING` | Cannot restart completed workstream |

**Attempting invalid transitions raises:** `InvalidTransitionError`

---

### Transition Code Example

```python
# core/state/workstreams.py
from enum import Enum

class WorkstreamState(Enum):
    S_PENDING = "S_PENDING"
    S_RUNNING = "S_RUNNING"
    S_SUCCESS = "S_SUCCESS"
    S_FAILED = "S_FAILED"
    S_RETRYING = "S_RETRYING"
    S_ABANDONED = "S_ABANDONED"

# Valid transitions map
VALID_TRANSITIONS = {
    WorkstreamState.S_PENDING: [WorkstreamState.S_RUNNING],
    WorkstreamState.S_RUNNING: [
        WorkstreamState.S_SUCCESS,
        WorkstreamState.S_FAILED,
        WorkstreamState.S_ABANDONED
    ],
    WorkstreamState.S_FAILED: [
        WorkstreamState.S_RETRYING,
        WorkstreamState.S_ABANDONED
    ],
    WorkstreamState.S_RETRYING: [WorkstreamState.S_RUNNING],
    WorkstreamState.S_SUCCESS: [],  # Terminal
    WorkstreamState.S_ABANDONED: []  # Terminal
}

def transition_workstream(conn, ws_id, to_state, metadata=None):
    """Transition workstream to new state with validation."""
    # Get current state
    cur = conn.execute(
        "SELECT state FROM workstreams WHERE ws_id = ?", (ws_id,)
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Workstream {ws_id} not found")
    
    from_state = WorkstreamState(row[0])
    to_state_enum = WorkstreamState(to_state)
    
    # Validate transition
    if to_state_enum not in VALID_TRANSITIONS[from_state]:
        raise InvalidTransitionError(
            f"Cannot transition from {from_state.value} to {to_state_enum.value}"
        )
    
    # Perform transition
    conn.execute(
        "UPDATE workstreams SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE ws_id = ?",
        (to_state, ws_id)
    )
    
    # Log transition
    conn.execute(
        """INSERT INTO state_transitions 
           (ws_id, from_state, to_state, transitioned_at, metadata)
           VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)""",
        (ws_id, from_state.value, to_state_enum.value, json.dumps(metadata or {}))
    )
    
    conn.commit()
```

---

## Step State Machine

### State Diagram

```
            ┌──────────────┐
            │  S_PENDING   │ (Initial)
            └──────┬───────┘
                   │
                   │ dependencies_met()
                   ↓
            ┌──────────────┐
       ┌────│  S_RUNNING   │────┐
       │    └──────────────┘    │
       │                        │
   success()                 failure()
       │                        │
       ↓                        ↓
┌────────────┐          ┌────────────┐
│ S_SUCCESS  │          │  S_FAILED  │
└────────────┘          └──────┬─────┘
                               │
                               │ retry_eligible()
                               ↓
                        ┌─────────────┐
                        │ S_RETRYING  │
                        └──────┬──────┘
                               │
                               │ retry_attempt()
                               └───► (back to S_RUNNING)
```

### State Definitions

| State | Code | Meaning | Blocks Dependents? |
|-------|------|---------|-------------------|
| **Pending** | `S_PENDING` | Step created, waiting for dependencies | Yes |
| **Running** | `S_RUNNING` | Step is actively executing | Yes |
| **Success** | `S_SUCCESS` | Step completed successfully | No |
| **Failed** | `S_FAILED` | Step failed execution | Yes |
| **Retrying** | `S_RETRYING` | Waiting before retry | Yes |

**Dependents blocked when:** Step is not in `S_SUCCESS` state

---

### Valid Transitions

| From State | To State | Trigger | Conditions |
|------------|----------|---------|------------|
| `S_PENDING` | `S_RUNNING` | Dependencies met | All `depends_on` steps in `S_SUCCESS` |
| `S_RUNNING` | `S_SUCCESS` | Tool exits successfully | Exit code in `expected_exit_codes` |
| `S_RUNNING` | `S_FAILED` | Tool fails | Exit code not expected |
| `S_FAILED` | `S_RETRYING` | Retry logic | `retry_count < max_retries` |
| `S_RETRYING` | `S_RUNNING` | Retry delay done | After exponential backoff |

### Dependency Resolution

```python
def can_execute_step(conn, step_id):
    """Check if step's dependencies are met."""
    # Get step dependencies
    step = get_step(conn, step_id)
    depends_on = step.get('depends_on', [])
    
    if not depends_on:
        return True  # No dependencies
    
    # Check each dependency is successful
    for dep_step_id in depends_on:
        dep_step = get_step(conn, dep_step_id)
        if dep_step['state'] != 'S_SUCCESS':
            return False  # Dependency not met
    
    return True  # All dependencies met
```

---

## Circuit Breaker State Machine

### State Diagram

```
      ┌───────────┐
      │  CLOSED   │ (Healthy - requests allowed)
      └─────┬─────┘
            │
            │ failure_threshold_exceeded()
            │ (e.g., 5 consecutive failures)
            ↓
      ┌───────────┐
      │   OPEN    │ (Unhealthy - requests rejected)
      └─────┬─────┘
            │
            │ cooldown_expires()
            │ (e.g., after 60 seconds)
            ↓
      ┌───────────┐
      │ HALF_OPEN │ (Testing - single request allowed)
      └─────┬─────┘
            │
       ┌────┴────┐
       │         │
   success()  failure()
       │         │
       ↓         ↓
   CLOSED      OPEN
```

### State Definitions

| State | Requests Allowed? | Failure Count | Purpose |
|-------|------------------|---------------|---------|
| **CLOSED** | Yes | Reset to 0 on success | Normal operation |
| **OPEN** | No (fast fail) | N/A | Protection from cascading failures |
| **HALF_OPEN** | One test request | N/A | Testing if service recovered |

### Configuration

```python
# config/circuit_breaker.json
{
  "tool_id": "aider",
  "failure_threshold": 5,      # Open after 5 failures
  "cooldown_seconds": 60,      # Stay open for 60s
  "success_threshold": 1       # Close after 1 success in HALF_OPEN
}
```

---

## State Recovery Procedures

### Recovery 1: Workstream Stuck in S_RUNNING

**Symptoms:**
```sql
SELECT * FROM workstreams WHERE state = 'S_RUNNING' AND updated_at < datetime('now', '-1 hour');
```

**Diagnosis:**
- Orchestrator crashed mid-execution
- Long-running step never completed
- Database not updated after completion

**Recovery:**
```bash
# 1. Check step states
sqlite3 .worktrees/pipeline_state.db "
  SELECT step_id, state, updated_at 
  FROM steps 
  WHERE ws_id = 'WS-001'
  ORDER BY step_id;
"

# 2. If all steps succeeded, manually mark workstream success
sqlite3 .worktrees/pipeline_state.db "
  UPDATE workstreams 
  SET state = 'S_SUCCESS', updated_at = CURRENT_TIMESTAMP 
  WHERE ws_id = 'WS-001';
"

# 3. Or restart execution
python scripts/run_workstream.py --resume WS-001
```

---

### Recovery 2: Step in S_FAILED, No Retry

**Symptoms:**
```
Step s1 is in S_FAILED state but not retrying
```

**Diagnosis:**
- Retry count exceeded
- Tool profile has `retry_on_failure: false`
- Circuit breaker is OPEN

**Recovery:**
```bash
# 1. Check retry settings
cat config/tool_profiles.json | jq '.[] | select(.tool_id=="aider")'

# 2. If retry count exceeded, manually reset
sqlite3 .worktrees/pipeline_state.db "
  UPDATE steps 
  SET retry_count = 0, state = 'S_PENDING'
  WHERE step_id = 's1';
"

# 3. Or skip failed step
python scripts/run_workstream.py --skip-step s1 WS-001
```

---

### Recovery 3: Circuit Breaker Stuck OPEN

**Symptoms:**
```
CircuitBreakerOpen: aider circuit is open, retry in 58 seconds
```

**Diagnosis:**
- Tool had 5+ consecutive failures
- Cooldown period (60s) hasn't elapsed
- Service is actually still unhealthy

**Recovery:**
```bash
# 1. Wait for cooldown (recommended)
sleep 60

# 2. Or manually reset circuit breaker
python -c "
from core.engine.circuit_breaker import reset_circuit
reset_circuit('aider')
print('Circuit breaker reset to CLOSED')
"

# 3. Verify tool is healthy before resetting
aider --version  # Should work without error
```

---

### Recovery 4: Invalid State Detected

**Symptoms:**
```
Data integrity error: Workstream in S_SUCCESS but step in S_FAILED
```

**Diagnosis:**
- Database corruption
- Manual state modification
- Concurrent update conflict

**Recovery:**
```bash
# 1. Identify inconsistency
sqlite3 .worktrees/pipeline_state.db "
  SELECT w.ws_id, w.state AS ws_state, s.step_id, s.state AS step_state
  FROM workstreams w
  JOIN steps s ON w.ws_id = s.ws_id
  WHERE w.state = 'S_SUCCESS' 
    AND s.state != 'S_SUCCESS';
"

# 2. Determine correct state
# If all steps actually succeeded:
sqlite3 .worktrees/pipeline_state.db "
  UPDATE steps SET state = 'S_SUCCESS' WHERE step_id = 's2';
"

# If some steps failed:
sqlite3 .worktrees/pipeline_state.db "
  UPDATE workstreams SET state = 'S_FAILED' WHERE ws_id = 'WS-001';
"

# 3. Run validation
python scripts/validate_state_consistency.py
```

---

## State Audit Trail

### State Transitions Table

```sql
CREATE TABLE state_transitions (
    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ws_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,  -- JSON blob with additional context
    FOREIGN KEY (ws_id) REFERENCES workstreams(ws_id)
);
```

### Query Transition History

```sql
-- Get all transitions for a workstream
SELECT 
    from_state,
    to_state,
    transitioned_at,
    json_extract(metadata, '$.reason') AS reason
FROM state_transitions
WHERE ws_id = 'WS-001'
ORDER BY transitioned_at;

-- Output:
-- S_PENDING → S_RUNNING (2025-11-22 20:00:00) reason: orchestrator start
-- S_RUNNING → S_FAILED  (2025-11-22 20:05:30) reason: step s2 failed
-- S_FAILED → S_RETRYING (2025-11-22 20:05:31) reason: retry attempt 1
-- S_RETRYING → S_RUNNING (2025-11-22 20:05:33) reason: retry delay expired
-- S_RUNNING → S_SUCCESS (2025-11-22 20:08:15) reason: all steps succeeded
```

---

## State Machine Best Practices

### ✅ DO

- **Validate transitions** before applying state changes
- **Log all transitions** to state_transitions table
- **Use transactions** when updating state
- **Check dependencies** before transitioning steps to S_RUNNING
- **Implement timeouts** for states that shouldn't be long-lived

### ❌ DON'T

- **Bypass state machine** with direct SQL UPDATE
- **Create invalid states** (e.g., S_SUCCESS with failed steps)
- **Skip transition logging**
- **Modify terminal states** (S_SUCCESS, S_ABANDONED)
- **Allow circular transitions** (e.g., S_SUCCESS → S_RUNNING)

---

## Related Documentation

- [Error Catalog: ERR-DB-03](../reference/ERROR_CATALOG.md#err-db-03-invalid-state-transition) - Invalid state transitions
- [Execution Traces](../EXECUTION_TRACES_SUMMARY.md) - State transitions in action
- [Data Flows](../reference/DATA_FLOWS.md) - State propagation
- [Anti-Pattern AP-CS-03](../guidelines/ANTI_PATTERNS.md#ap-cs-03-state-machine-state-pollution) - State pollution

---

**State Machines Documented:** 3 (Workstream, Step, Circuit Breaker)  
**Total States:** 12  
**Valid Transitions:** 15  
**Recovery Procedures:** 4  
**Last Updated:** 2025-11-22
