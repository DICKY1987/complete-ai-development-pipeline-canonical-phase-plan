---
doc_id: DOC-GUIDE-COMPONENT-CONTRACTS-1662
---

# UET V2 Component Contracts

**Purpose**: Define API contracts for all UET V2 components to enable parallel development  
**Status**: DRAFT  
**Last Updated**: 2025-11-23

> **Critical**: These contracts are stable interfaces. Changes require team approval and migration plan.

---

## Table of Contents

- [Worker Lifecycle](#worker-lifecycle)
- [Integration Worker](#integration-worker)
- [Patch Ledger](#patch-ledger)
- [Patch Validator](#patch-validator)
- [Patch Policy Engine](#patch-policy-engine)
- [Test Gate Executor](#test-gate-executor)
- [Merge Orchestrator](#merge-orchestrator)
- [Context Manager](#context-manager)
- [Feedback Loop](#feedback-loop)
- [Compensation Engine](#compensation-engine)

---

## Worker Lifecycle

**Module**: `core/engine/worker_lifecycle.py`  
**Status**: Not Implemented  
**Owner**: TBD

### Interface

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

class WorkerState(Enum):
    SPAWNING = "SPAWNING"
    IDLE = "IDLE"
    BUSY = "BUSY"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"

@dataclass
class WorkerRecord:
    worker_id: str
    worker_type: str  # "code_edit", "testing", "linting"
    state: WorkerState
    affinity: Dict[str, str]  # {"language": "python", "tool": "aider"}
    last_heartbeat: datetime
    created_at: datetime
    terminated_at: Optional[datetime] = None

class WorkerLifecycle:
    """Manages worker lifecycle from spawn to termination."""
    
    def spawn_worker(self, worker_id: str, worker_type: str, affinity: Dict[str, str]) -> WorkerRecord:
        """
        Spawn a new worker.
        
        Args:
            worker_id: Unique identifier for worker
            worker_type: Type of worker (code_edit, testing, linting)
            affinity: Worker capabilities/preferences
        
        Returns:
            WorkerRecord with state=SPAWNING
        
        Raises:
            ValueError: If worker_id already exists
        """
        pass
    
    def transition_state(self, worker_id: str, new_state: WorkerState) -> bool:
        """
        Transition worker to new state.
        
        Args:
            worker_id: Worker to transition
            new_state: Target state
        
        Returns:
            True if transition successful
        
        Raises:
            ValueError: If transition is invalid
        """
        pass
    
    def heartbeat(self, worker_id: str) -> None:
        """
        Record worker heartbeat.
        
        Args:
            worker_id: Worker reporting heartbeat
        
        Raises:
            ValueError: If worker doesn't exist
        """
        pass
    
    def terminate_worker(self, worker_id: str) -> None:
        """
        Terminate worker (graceful shutdown).
        
        Args:
            worker_id: Worker to terminate
        
        Side Effects:
            - Transitions to DRAINING, then TERMINATED
            - Records termination timestamp
        """
        pass
    
    def get_worker(self, worker_id: str) -> WorkerRecord:
        """Retrieve worker record."""
        pass
    
    def get_workers_by_state(self, state: WorkerState) -> List[WorkerRecord]:
        """Get all workers in given state."""
        pass
    
    def get_idle_workers(self, worker_type: Optional[str] = None) -> List[WorkerRecord]:
        """Get workers available for work."""
        pass
```

### State Machine

```
SPAWNING → IDLE → BUSY → DRAINING → TERMINATED
    ↓               ↓
TERMINATED   TERMINATED
```

**Valid Transitions**:
- SPAWNING → IDLE (worker ready)
- SPAWNING → TERMINATED (spawn failed)
- IDLE → BUSY (task assigned)
- IDLE → TERMINATED (shutdown requested)
- BUSY → IDLE (task completed)
- BUSY → DRAINING (shutdown requested while busy)
- BUSY → TERMINATED (crash)
- DRAINING → TERMINATED (current task done)

**Invalid Transitions** (raise ValueError):
- TERMINATED → any state (terminal)
- IDLE → SPAWNING (can't go backward)
- BUSY → SPAWNING (can't go backward)

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    worker_type TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED')),
    affinity TEXT,  -- JSON
    last_heartbeat TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TEXT
);

CREATE INDEX idx_workers_state ON workers(state);
CREATE INDEX idx_workers_type ON workers(worker_type);
```

### Events Emitted

- `WORKER_SPAWNED` - Worker created
- `WORKER_STATE_CHANGED` - State transition occurred
- `WORKER_HEARTBEAT` - Heartbeat received
- `WORKER_TERMINATED` - Worker shut down

### Dependencies

- **Requires**: `core/state/db.py` (database connection)
- **Provides**: Worker state management

---

## Integration Worker

**Module**: `core/engine/integration_worker.py`  
**Status**: Not Implemented  
**Owner**: TBD

### Interface

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class MergeResult:
    success: bool
    merged_patch_ids: List[str]
    conflicts: List[MergeConflict]
    rollback_required: bool = False

@dataclass
class MergeConflict:
    file_path: str
    patch_id_1: str
    patch_id_2: str
    conflict_type: str  # "line_overlap", "deleted_modified", "both_modified"
    resolution: Optional[str] = None

class IntegrationWorker:
    """Dedicated worker for merging parallel workstream results."""
    
    def collect_patches(self, worker_ids: List[str]) -> List[PatchArtifact]:
        """
        Collect validated patches from multiple workers.
        
        Args:
            worker_ids: Workers that produced patches
        
        Returns:
            List of patches in validated state
        """
        pass
    
    def orchestrate_merge(self, patches: List[PatchArtifact]) -> MergeResult:
        """
        Merge patches in deterministic order.
        
        Args:
            patches: Validated patches to merge
        
        Returns:
            MergeResult with success status and conflicts
        
        Process:
            1. Order patches (priority, dependencies, age)
            2. Apply patches sequentially
            3. Validate after each merge
            4. Rollback on failure
        """
        pass
    
    def handle_conflict(self, conflict: MergeConflict) -> ConflictResolution:
        """
        Handle merge conflict.
        
        Args:
            conflict: Detected conflict
        
        Returns:
            Resolution strategy (auto-resolve, escalate, rollback)
        """
        pass
```

### Integration Points

**Calls**:
- `PatchLedger.get_patches_by_state('validated')` - Collect ready patches
- `MergeOrchestrator.order_candidates(patches)` - Determine merge order
- `MergeOrchestrator.merge(patch)` - Apply single patch
- `TestGateExecutor.validate_merge(patch_id)` - Run tests after merge
- `CompensationEngine.rollback_on_failure()` - Undo failed merge

**Emits**:
- `MERGE_STARTED` - Merge process beginning
- `MERGE_COMPLETED` - All patches merged successfully
- `MERGE_FAILED` - Merge failed, rollback triggered
- `MERGE_CONFLICT` - Conflict detected, needs resolution

### Dependencies

- **Requires**: PatchLedger, MergeOrchestrator, TestGateExecutor, CompensationEngine
- **Provides**: Deterministic merge coordination

---

## Patch Ledger

**Module**: `core/patches/ledger.py`  
**Status**: Not Implemented  
**Owner**: TBD

### Interface

```python
from enum import Enum

class PatchState(Enum):
    CREATED = "created"
    VALIDATED = "validated"
    QUEUED = "queued"
    APPLIED = "applied"
    APPLY_FAILED = "apply_failed"
    VERIFIED = "verified"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    QUARANTINED = "quarantined"
    DROPPED = "dropped"

@dataclass
class PatchLedgerEntry:
    ledger_id: str
    patch_id: str
    state: PatchState
    phase_id: str
    workstream_id: str
    validation_format_passed: bool = False
    validation_scope_passed: bool = False
    validation_constraints_passed: bool = False
    validation_tests_passed: bool = False
    quarantine_reason: Optional[str] = None
    state_history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class PatchLedger:
    """Tracks complete lifecycle of patches from creation to commit."""
    
    def create_entry(self, patch: PatchArtifact, phase_id: str, workstream_id: str) -> PatchLedgerEntry:
        """
        Create new ledger entry.
        
        Args:
            patch: Patch artifact to track
            phase_id: Phase context
            workstream_id: Workstream context
        
        Returns:
            PatchLedgerEntry with state=CREATED
        """
        pass
    
    def transition_state(self, ledger_id: str, new_state: PatchState, reason: str = "") -> bool:
        """
        Transition patch to new state.
        
        Args:
            ledger_id: Ledger entry to update
            new_state: Target state
            reason: Reason for transition
        
        Returns:
            True if transition successful
        
        Raises:
            ValueError: If transition invalid per state machine
        """
        pass
    
    def validate(self, ledger_id: str) -> ValidationResult:
        """Run validation pipeline and update entry."""
        pass
    
    def quarantine(self, ledger_id: str, reason: str) -> None:
        """Quarantine patch with reason."""
        pass
    
    def get_patches_by_state(self, state: PatchState, phase_id: Optional[str] = None) -> List[PatchLedgerEntry]:
        """Query patches by state, optionally filtered by phase."""
        pass
```

### State Machine

```
created → validated → queued → applied → verified → committed
   ↓         ↓          ↓         ↓         ↓
quarantined, apply_failed → quarantined/dropped
committed → rolled_back
```

**Valid Transitions**:
- created → validated (validation passed)
- created → quarantined (validation failed)
- validated → queued (accepted for merge)
- queued → applied (git apply succeeded)
- queued → apply_failed (git apply failed)
- applied → verified (tests passed)
- applied → quarantined (tests failed)
- verified → committed (git commit succeeded)
- committed → rolled_back (rollback requested)
- apply_failed → quarantined / dropped

**Invariants**:
- Cannot transition from committed back to queued
- Quarantined patches must have quarantine_reason set
- rolled_back patches must reference original patch_id
- State history never deleted, only appended

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS patch_ledger_entries (
    ledger_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    state TEXT NOT NULL,
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
    FOREIGN KEY (patch_id) REFERENCES patches(patch_id)
);
```

### Events Emitted

- `PATCH_CREATED` - New patch ledger entry
- `PATCH_VALIDATED` - Validation completed
- `PATCH_QUARANTINED` - Patch quarantined
- `PATCH_COMMITTED` - Patch committed to main

### Dependencies

- **Requires**: `core/patches/validator.py`, `core/state/db.py`
- **Provides**: Patch lifecycle tracking

---

## Summary of Contracts

| Component | Module | Key Methods | State Machine | Events Emitted |
|-----------|--------|-------------|---------------|----------------|
| Worker Lifecycle | `core/engine/worker_lifecycle.py` | spawn, transition_state, heartbeat, terminate | SPAWNING→IDLE→BUSY→DRAINING→TERMINATED | WORKER_* |
| Integration Worker | `core/engine/integration_worker.py` | collect_patches, orchestrate_merge, handle_conflict | N/A | MERGE_* |
| Patch Ledger | `core/patches/ledger.py` | create_entry, transition_state, validate, quarantine | created→validated→queued→applied→verified→committed | PATCH_* |

---

## Contract Stability

**Stable** (safe to implement against):
- All interfaces defined above
- State machines (transitions locked)
- Database schemas
- Event types

**Unstable** (may change):
- Internal implementation details
- Performance optimizations
- Error messages

**Changes Require**:
- Team review
- Version bump
- Migration plan
- Update all consumers

---

**Last Updated**: 2025-11-23  
**Next Review**: Before Phase A starts
