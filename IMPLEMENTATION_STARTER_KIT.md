# State Machine Implementation Starter Kit

**Purpose**: Quick-start guide and code templates for implementing state machines from SSOT  
**Reference**: DOC-SSOT-STATE-MACHINES-001  
**Created**: 2025-12-08

---

## Quick Start

### 1. Choose Your State Machine

| State Machine | Complexity | Start Here |
|--------------|------------|------------|
| Circuit Breaker | ⭐ Simple | Best for learning |
| Run | ⭐⭐ Medium | Orchestration basics |
| Worker | ⭐⭐ Medium | Worker lifecycle |
| Task | ⭐⭐⭐ Complex | Full orchestration |
| Workstream | ⭐⭐⭐⭐ Advanced | Complete system |
| Patch Ledger | ⭐⭐⭐⭐ Advanced | UET V2 core |

### 2. Implementation Checklist

For each state machine:
- [ ] Define state enum
- [ ] Create transition map
- [ ] Implement validation logic
- [ ] Add database constraints
- [ ] Implement event logging
- [ ] Write unit tests (100% coverage)
- [ ] Add integration tests
- [ ] Document edge cases

---

## Code Templates

### Template 1: Basic State Enum

```python
# File: core/state/base.py

from enum import Enum
from typing import Dict, Set, Optional
from datetime import datetime, timezone

class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass

class BaseState(Enum):
    """Base class for all state enums."""
    
    @classmethod
    def is_terminal(cls, state) -> bool:
        """Check if a state is terminal."""
        return state in cls.get_terminal_states()
    
    @classmethod
    def get_terminal_states(cls) -> Set:
        """Override in subclass to define terminal states."""
        raise NotImplementedError
    
    @classmethod
    def get_valid_transitions(cls) -> Dict:
        """Override in subclass to define valid transitions."""
        raise NotImplementedError
```

### Template 2: Task State Machine (Example Implementation)

```python
# File: core/state/task.py

from enum import Enum
from typing import Dict, Set
from .base import BaseState, StateTransitionError

class TaskState(BaseState):
    """Task lifecycle states (SSOT §1.4)"""
    
    PENDING = "pending"
    QUEUED = "queued"
    BLOCKED = "blocked"
    RUNNING = "running"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    
    @classmethod
    def get_terminal_states(cls) -> Set:
        return {cls.COMPLETED, cls.FAILED, cls.CANCELLED}
    
    @classmethod
    def get_valid_transitions(cls) -> Dict[str, Set]:
        """Valid state transitions per SSOT §1.4.4"""
        return {
            cls.PENDING: {cls.QUEUED, cls.BLOCKED},
            cls.QUEUED: {cls.RUNNING},
            cls.BLOCKED: {cls.PENDING},
            cls.RUNNING: {cls.VALIDATING, cls.RETRYING, cls.FAILED, cls.CANCELLED},
            cls.VALIDATING: {cls.COMPLETED, cls.FAILED},
            cls.RETRYING: {cls.QUEUED},
            cls.COMPLETED: set(),  # Terminal
            cls.FAILED: set(),     # Terminal
            cls.CANCELLED: set()   # Terminal
        }

class TaskStateMachine:
    """Task state machine with transition validation (SSOT §1.4)"""
    
    def __init__(self, task_id: str, initial_state: TaskState = TaskState.PENDING):
        self.task_id = task_id
        self.current_state = initial_state
        self.history = [(initial_state, datetime.now(timezone.utc), "created")]
    
    def transition(self, to_state: TaskState, reason: str = "") -> bool:
        """
        Transition to new state with validation.
        
        Args:
            to_state: Target state
            reason: Reason for transition (for audit trail)
            
        Returns:
            True if transition succeeded
            
        Raises:
            StateTransitionError: If transition is invalid
        """
        # Validate transition
        if not self._is_valid_transition(to_state):
            raise StateTransitionError(
                f"Invalid transition: {self.current_state.value} → {to_state.value}"
            )
        
        # Record transition
        old_state = self.current_state
        self.current_state = to_state
        self.history.append((to_state, datetime.now(timezone.utc), reason))
        
        # Log event
        self._log_transition(old_state, to_state, reason)
        
        return True
    
    def _is_valid_transition(self, to_state: TaskState) -> bool:
        """Check if transition from current_state to to_state is valid."""
        valid_next_states = TaskState.get_valid_transitions()[self.current_state]
        return to_state in valid_next_states
    
    def _log_transition(self, from_state: TaskState, to_state: TaskState, reason: str):
        """Log state transition event (SSOT §7.2)"""
        from core.events import emit_event
        
        emit_event({
            'event_type': 'task_state_transition',
            'entity_type': 'task',
            'entity_id': self.task_id,
            'from_state': from_state.value,
            'to_state': to_state.value,
            'reason': reason,
            'severity': self._get_severity(to_state),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def _get_severity(self, state: TaskState) -> str:
        """Get event severity based on state (SSOT §7.2.2)"""
        if state in {TaskState.COMPLETED}:
            return 'info'
        elif state in {TaskState.RETRYING}:
            return 'warning'
        elif state in {TaskState.FAILED, TaskState.CANCELLED}:
            return 'error'
        else:
            return 'info'
    
    def can_transition_to(self, to_state: TaskState) -> bool:
        """Check if transition is possible without attempting it."""
        return self._is_valid_transition(to_state)
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal."""
        return TaskState.is_terminal(self.current_state)
```

### Template 3: Database Schema

```python
# File: core/db/migrations/001_create_tasks_table.py

"""
Create tasks table with state machine constraints
Reference: SSOT §6.3
"""

def upgrade(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            workstream_id TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN (
                'pending', 'queued', 'running', 'validating', 
                'completed', 'failed', 'retrying', 'cancelled', 'blocked'
            )),
            worker_id TEXT,
            is_critical BOOLEAN DEFAULT FALSE,
            depends_on TEXT,  -- JSON array of task_ids
            gate_dependencies TEXT,  -- JSON array of gate_ids
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            timeout_sec INTEGER DEFAULT 1800,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            started_at TEXT,
            completed_at TEXT,
            last_error TEXT,
            metadata TEXT,  -- JSON
            
            -- Constraints from SSOT §1.4.5 (Task Invariants)
            FOREIGN KEY (workstream_id) REFERENCES workstreams(ws_id),
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
            
            -- Worker assignment constraint
            CHECK (
                (state = 'running' AND worker_id IS NOT NULL) OR 
                (state != 'running' AND worker_id IS NULL)
            ),
            
            -- Terminal state timestamp constraint
            CHECK (
                (state IN ('completed', 'failed', 'cancelled') AND completed_at IS NOT NULL) OR 
                (state NOT IN ('completed', 'failed', 'cancelled') AND completed_at IS NULL)
            ),
            
            -- Retry limit constraint
            CHECK (retry_count <= max_retries),
            
            -- Timestamp ordering constraint
            CHECK (
                (started_at IS NULL) OR (started_at >= created_at)
            ),
            CHECK (
                (completed_at IS NULL) OR (completed_at >= started_at)
            )
        );
        
        -- Indexes for performance
        CREATE INDEX idx_tasks_workstream ON tasks(workstream_id);
        CREATE INDEX idx_tasks_state ON tasks(state);
        CREATE INDEX idx_tasks_worker ON tasks(worker_id);
    """)

def downgrade(db):
    db.execute("DROP TABLE IF EXISTS tasks;")
```

### Template 4: Unit Tests

```python
# File: tests/state/test_task_state_machine.py

import pytest
from datetime import datetime, timezone
from core.state.task import TaskState, TaskStateMachine, StateTransitionError

class TestTaskStateTransitions:
    """Test all valid and invalid task state transitions (SSOT §4.1)"""
    
    def test_pending_to_queued_valid(self):
        """Test valid transition: pending → queued"""
        sm = TaskStateMachine("task-001")
        assert sm.current_state == TaskState.PENDING
        
        sm.transition(TaskState.QUEUED, reason="dependencies met")
        assert sm.current_state == TaskState.QUEUED
    
    def test_pending_to_blocked_valid(self):
        """Test valid transition: pending → blocked"""
        sm = TaskStateMachine("task-001")
        sm.transition(TaskState.BLOCKED, reason="dependency failed")
        assert sm.current_state == TaskState.BLOCKED
    
    def test_queued_to_running_valid(self):
        """Test valid transition: queued → running"""
        sm = TaskStateMachine("task-001", TaskState.QUEUED)
        sm.transition(TaskState.RUNNING, reason="worker assigned")
        assert sm.current_state == TaskState.RUNNING
    
    def test_running_to_completed_invalid_must_validate(self):
        """Test invalid transition: running → completed (must go through validating)"""
        sm = TaskStateMachine("task-001", TaskState.RUNNING)
        
        with pytest.raises(StateTransitionError):
            sm.transition(TaskState.COMPLETED)
    
    def test_completed_to_any_invalid_terminal(self):
        """Test terminal state cannot transition"""
        sm = TaskStateMachine("task-001", TaskState.COMPLETED)
        
        with pytest.raises(StateTransitionError):
            sm.transition(TaskState.RUNNING)
    
    def test_transition_history_recorded(self):
        """Test all transitions are recorded in history"""
        sm = TaskStateMachine("task-001")
        
        sm.transition(TaskState.QUEUED)
        sm.transition(TaskState.RUNNING)
        sm.transition(TaskState.VALIDATING)
        sm.transition(TaskState.COMPLETED)
        
        assert len(sm.history) == 5  # Initial + 4 transitions
        assert sm.history[-1][0] == TaskState.COMPLETED
    
    def test_terminal_state_check(self):
        """Test terminal state detection"""
        sm = TaskStateMachine("task-001")
        assert not sm.is_terminal()
        
        sm.current_state = TaskState.COMPLETED
        assert sm.is_terminal()
    
    def test_can_transition_to_check(self):
        """Test transition possibility check without executing"""
        sm = TaskStateMachine("task-001", TaskState.RUNNING)
        
        assert sm.can_transition_to(TaskState.VALIDATING)
        assert sm.can_transition_to(TaskState.FAILED)
        assert not sm.can_transition_to(TaskState.PENDING)

class TestTaskInvariants:
    """Test task state machine invariants (SSOT §1.4.5)"""
    
    def test_retry_count_never_exceeds_max(self):
        """Invariant: retry_count ≤ max_retries"""
        # This would be tested at database level
        # See migration template for CHECK constraint
        pass
    
    def test_timestamp_ordering(self):
        """Invariant: created_at ≤ started_at ≤ completed_at"""
        # Database constraint enforcement test
        pass
```

### Template 5: Integration Test

```python
# File: tests/integration/test_task_workflow.py

import pytest
from core.state.task import TaskStateMachine, TaskState
from core.db import get_db
from core.workers import WorkerPool

class TestTaskWorkflow:
    """Integration tests for complete task lifecycle (SSOT §3.1)"""
    
    def test_happy_path_task_execution(self, db, worker_pool):
        """Test complete task execution: pending → completed"""
        # Create task
        task_id = "task-001"
        sm = TaskStateMachine(task_id)
        
        # Check dependencies (all satisfied)
        assert sm.can_transition_to(TaskState.QUEUED)
        sm.transition(TaskState.QUEUED, "dependencies satisfied")
        
        # Worker picks up task
        worker = worker_pool.get_available_worker()
        sm.transition(TaskState.RUNNING, f"assigned to {worker.id}")
        
        # Task executes successfully
        # ... worker execution ...
        sm.transition(TaskState.VALIDATING, "execution complete")
        
        # Validation passes
        # ... validation logic ...
        sm.transition(TaskState.COMPLETED, "validation passed")
        
        # Verify final state
        assert sm.current_state == TaskState.COMPLETED
        assert sm.is_terminal()
    
    def test_task_retry_workflow(self, db):
        """Test task retry: running → retrying → queued → running → completed"""
        sm = TaskStateMachine("task-001", TaskState.RUNNING)
        
        # First attempt fails
        sm.transition(TaskState.RETRYING, "execution failed, retry 1/3")
        
        # Wait for backoff
        sm.transition(TaskState.QUEUED, "retry scheduled")
        
        # Second attempt
        sm.transition(TaskState.RUNNING, "retry attempt")
        sm.transition(TaskState.VALIDATING, "execution complete")
        sm.transition(TaskState.COMPLETED, "success on retry")
        
        assert sm.current_state == TaskState.COMPLETED
```

---

## Implementation Checklist by State Machine

### ✅ Circuit Breaker (Start Here - Simplest)

**Files to create**:
- [ ] `core/state/circuit_breaker.py` - State machine
- [ ] `tests/state/test_circuit_breaker.py` - Unit tests
- [ ] `tests/integration/test_circuit_breaker_workflow.py` - Integration tests

**Reference**: SSOT §2.4

### ✅ Run State Machine

**Files to create**:
- [ ] `core/state/run.py` - State machine
- [ ] `core/db/migrations/002_create_runs_table.py` - Schema
- [ ] `tests/state/test_run_state.py` - Unit tests

**Reference**: SSOT §1.2, §6.1

### ✅ Worker State Machines

**Files to create**:
- [ ] `core/state/orchestration_worker.py` - Orchestration worker
- [ ] `core/state/uet_worker.py` - UET worker
- [ ] `core/db/migrations/003_create_workers_table.py` - Schema
- [ ] `tests/state/test_worker_states.py` - Unit tests

**Reference**: SSOT §1.5, §2.1, §6.4

### ✅ Task State Machine

**Files to create**:
- [ ] `core/state/task.py` - State machine (see template above)
- [ ] `core/db/migrations/004_create_tasks_table.py` - Schema
- [ ] `tests/state/test_task_state.py` - Unit tests
- [ ] `tests/integration/test_task_workflow.py` - Integration tests

**Reference**: SSOT §1.4, §6.3

### ✅ Workstream State Machine

**Files to create**:
- [ ] `core/state/workstream.py` - State machine
- [ ] `core/db/migrations/005_create_workstreams_table.py` - Schema
- [ ] `tests/state/test_workstream_state.py` - Unit tests
- [ ] `tests/integration/test_workstream_workflow.py` - Integration tests

**Reference**: SSOT §1.3, §6.2

### ✅ UET V2 State Machines

**Files to create**:
- [ ] `core/uet/state/patch_ledger.py` - Patch ledger
- [ ] `core/uet/state/test_gate.py` - Test gate
- [ ] `core/db/migrations/006_create_patch_ledger_table.py` - Schema
- [ ] `core/db/migrations/007_create_test_gates_table.py` - Schema
- [ ] `tests/uet/test_patch_ledger.py` - Unit tests
- [ ] `tests/uet/test_test_gates.py` - Unit tests

**Reference**: SSOT §2.2, §2.3, §6.5, §6.6

---

## Development Workflow

### Phase 1: Foundation (Week 1)
1. Implement base state machine classes
2. Create Circuit Breaker (simplest)
3. Set up event logging infrastructure
4. Create database migration framework

### Phase 2: Orchestration (Weeks 2-3)
1. Implement Run state machine
2. Implement Worker state machines
3. Implement Task state machine
4. Implement Workstream state machine

### Phase 3: UET V2 (Weeks 4-5)
1. Implement Patch Ledger
2. Implement Test Gates
3. Integrate with UET worker

### Phase 4: Integration (Week 6)
1. Cross-system derivation logic (SSOT §3)
2. End-to-end workflow tests
3. Performance optimization
4. Monitoring setup (SSOT §7.3)

---

## Testing Strategy

### Unit Tests (100% Coverage Required)
- ✅ All valid transitions
- ✅ All invalid transitions (raise errors)
- ✅ Terminal state enforcement
- ✅ Invariant checking

### Integration Tests
- ✅ Complete workflows (happy path)
- ✅ Retry scenarios
- ✅ Failure recovery
- ✅ Cross-system state propagation

### Concurrency Tests (SSOT §4.3)
- ✅ Optimistic locking
- ✅ Race conditions
- ✅ Simultaneous state changes

---

## Quick Reference

**SSOT Sections**:
- §1: Orchestration Layer (Run, Workstream, Task, Worker)
- §2: UET V2 (Worker, Patch Ledger, Test Gate, Circuit Breaker)
- §3: Cross-System Derivations
- §4: Test Requirements
- §6: Database Schemas
- §7: Event & Audit Model
- §8: Global Invariants

**Key Files**:
- Main SSOT: `doc_ssot_state_machines.md`
- This starter kit: `IMPLEMENTATION_STARTER_KIT.md`
- Next actions: `NEXT_ACTIONS.md`

---

**Last Updated**: 2025-12-08  
**Version**: 1.0.0
