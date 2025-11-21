# UET Integration Plan: Universal Execution Templates Framework

**Created**: 2025-11-21  
**Status**: Draft  
**Target**: Phase H (Post Phase G)  
**Estimated Duration**: 14 weeks (70-90 hours)  
**Expected ROI**: 40-50% execution speedup, production-grade orchestration  

---

## Executive Summary

This plan integrates the **Universal Execution Templates (UET) Execution Kernel** concepts from `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md` into the existing pipeline system.

**Key Achievements:**
- ✅ DAG-based parallel workstream execution
- ✅ Multi-worker orchestration with conflict resolution
- ✅ Production-grade crash recovery and state persistence
- ✅ Cost/context tracking and budget enforcement
- ✅ Formal test gates and merge strategies

**Integration Approach:** Phased, backward-compatible enhancement of existing architecture

---

## Phase Overview

```
Phase 1: Foundation (2 weeks)  →  Phase 2: Parallelism (4 weeks)
         ↓                                    ↓
Phase 3: Robustness (4 weeks)  →  Phase 4: Intelligence (4 weeks)
                                             ↓
                                    Production Ready
```

---

## Phase 1: Foundation Enhancement

**Duration**: 2 weeks (10-12 hours)  
**Risk**: Low  
**Goal**: Add UET metadata structures without breaking existing functionality  

### Workstream WS-H1: Schema & Data Model Extension

**Priority**: Critical Path  
**Estimated Time**: 6-8 hours  

#### Tasks

1. **Extend Workstream Schema** (`schema/workstream.schema.json`)
   ```json
   {
     "parallel_ok": {
       "type": "boolean",
       "default": true,
       "description": "Whether this workstream can run in parallel with others"
     },
     "conflict_group": {
       "type": "string",
       "description": "Serialization group for mutually exclusive workstreams"
     },
     "kind": {
       "type": "string",
       "enum": ["design", "impl", "test", "docs", "infra", "refactor", "background", "spike"],
       "default": "impl"
     },
     "priority": {
       "type": "string",
       "enum": ["foreground", "background"],
       "default": "foreground"
     },
     "estimated_context_tokens": {
       "type": "integer",
       "minimum": 0,
       "description": "Estimated token count for AI context"
     },
     "max_cost_usd": {
       "type": "number",
       "minimum": 0,
       "description": "Maximum allowed API cost for this workstream"
     },
     "compensation_actions": {
       "type": "array",
       "items": {"type": "string"},
       "description": "Rollback/undo steps for Saga pattern"
     },
     "test_gates": {
       "type": "array",
       "items": {
         "type": "object",
         "properties": {
           "type": {"enum": ["GATE_LINT", "GATE_UNIT", "GATE_INTEGRATION", "GATE_SECURITY"]},
           "required": {"type": "boolean"},
           "blocking": {"type": "boolean"}
         }
       },
       "description": "Test gates that must pass before completion"
     }
   }
   ```

2. **Database Schema Extension** (`schema/schema.sql`)
   - Add `workers` table:
     ```sql
     CREATE TABLE IF NOT EXISTS workers (
       worker_id TEXT PRIMARY KEY,
       adapter_type TEXT NOT NULL,
       state TEXT NOT NULL CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED')),
       current_task_id TEXT,
       sandbox_path TEXT,
       heartbeat_at TEXT,
       spawned_at TEXT NOT NULL,
       terminated_at TEXT,
       metadata JSON,
       FOREIGN KEY (current_task_id) REFERENCES steps(id)
     );
     ```
   - Add `events` table for event bus:
     ```sql
     CREATE TABLE IF NOT EXISTS events (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       event_type TEXT NOT NULL,
       worker_id TEXT,
       task_id TEXT,
       run_id TEXT,
       workstream_id TEXT,
       timestamp TEXT NOT NULL,
       payload JSON,
       FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
       FOREIGN KEY (task_id) REFERENCES steps(id)
     );
     CREATE INDEX idx_events_timestamp ON events(timestamp);
     CREATE INDEX idx_events_type ON events(event_type);
     ```
   - Add `cost_tracking` table:
     ```sql
     CREATE TABLE IF NOT EXISTS cost_tracking (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       run_id TEXT NOT NULL,
       workstream_id TEXT,
       step_id TEXT,
       worker_id TEXT,
       input_tokens INTEGER DEFAULT 0,
       output_tokens INTEGER DEFAULT 0,
       estimated_cost_usd REAL DEFAULT 0.0,
       actual_cost_usd REAL,
       model_name TEXT,
       timestamp TEXT NOT NULL,
       FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
       FOREIGN KEY (step_id) REFERENCES steps(id)
     );
     CREATE INDEX idx_cost_run ON cost_tracking(run_id);
     ```
   - Add `merge_conflicts` table:
     ```sql
     CREATE TABLE IF NOT EXISTS merge_conflicts (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       run_id TEXT NOT NULL,
       workstream_a TEXT NOT NULL,
       workstream_b TEXT NOT NULL,
       conflicted_files JSON NOT NULL,
       resolution_status TEXT CHECK(resolution_status IN ('PENDING', 'AUTO_RESOLVED', 'AGENT_RESOLVED', 'HUMAN_RESOLVED', 'QUARANTINED')),
       resolution_details JSON,
       created_at TEXT NOT NULL,
       resolved_at TEXT
     );
     ```

3. **Migration Script** (`schema/migrations/001_uet_foundation.sql`)
   - Create migration for existing databases
   - Safe idempotent upgrade path

4. **Update Validation**
   - Extend `scripts/validate_workstreams.py` to handle new fields
   - Make all new fields optional (backward compatibility)
   - Add warnings for missing UET metadata

#### Acceptance Criteria
- [ ] Schema validates with new optional fields
- [ ] Existing workstreams load without modification
- [ ] Database migration runs idempotently
- [ ] Validation script passes on legacy and UET-enhanced bundles

#### Files Changed
- `schema/workstream.schema.json`
- `schema/schema.sql`
- `schema/migrations/001_uet_foundation.sql`
- `scripts/validate_workstreams.py`
- `core/state/bundles.py` (extend WorkstreamBundle dataclass)

---

### Workstream WS-H2: Detection & Dry-Run Validator

**Priority**: High  
**Estimated Time**: 4-5 hours  
**Depends On**: WS-H1  

#### Tasks

1. **Create Parallelism Detector** (`core/planning/parallelism_detector.py`)
   ```python
   from typing import Dict, List, Set, Tuple
   from core.state.bundles import WorkstreamBundle
   
   class ParallelismProfile:
       def __init__(self):
           self.waves: List[Set[str]] = []  # Execution waves
           self.bottlenecks: List[str] = []
           self.max_parallelism: int = 1
           self.estimated_speedup: float = 1.0
           self.conflicts: List[Tuple[str, str, str]] = []  # (ws_a, ws_b, reason)
   
   def detect_parallel_opportunities(
       bundles: List[WorkstreamBundle],
       max_workers: int = 4
   ) -> ParallelismProfile:
       """Analyze DAG and file scopes to identify parallelism."""
       # Topological sort into waves
       # Detect file scope conflicts
       # Calculate theoretical speedup
       pass
   
   def detect_conflict_groups(bundles: List[WorkstreamBundle]) -> Dict[str, List[str]]:
       """Group workstreams by conflict_group metadata."""
       pass
   ```

2. **Dry-Run Validation Mode** (`core/engine/plan_validator.py`)
   ```python
   from enum import Enum
   from typing import Dict, Any, List
   
   class ValidationMode(Enum):
       VALIDATE_ONLY = "validate_only"
       EXECUTE = "execute"
   
   class ValidationReport:
       def __init__(self):
           self.valid: bool = True
           self.errors: List[str] = []
           self.warnings: List[str] = []
           self.parallelism_profile: ParallelismProfile = None
           self.estimated_duration_seq: float = 0.0
           self.estimated_duration_par: float = 0.0
           self.bottlenecks: List[str] = []
   
   def validate_phase_plan(
       bundles: List[WorkstreamBundle],
       mode: ValidationMode = ValidationMode.VALIDATE_ONLY
   ) -> ValidationReport:
       """UET Section 6: Plan validation and simulation."""
       report = ValidationReport()
       
       # Schema validation (already exists)
       # DAG validation (cycle detection - already exists)
       # File scope validation (already exists)
       # NEW: Parallelism analysis
       # NEW: Cost estimation
       # NEW: Resource simulation
       
       return report
   ```

3. **CLI Integration** (`scripts/validate_plan.py`)
   ```python
   #!/usr/bin/env python3
   """Dry-run validator for phase plans."""
   
   import argparse
   from pathlib import Path
   from core.state.bundles import load_and_validate_bundles
   from core.engine.plan_validator import validate_phase_plan
   
   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--workstreams-dir', default='workstreams')
       parser.add_argument('--max-workers', type=int, default=4)
       parser.add_argument('--output', choices=['text', 'json'], default='text')
       args = parser.parse_args()
       
       bundles = load_and_validate_bundles(Path(args.workstreams_dir))
       report = validate_phase_plan(bundles)
       
       if args.output == 'json':
           print(report.to_json())
       else:
           print(report.to_text())
   
   if __name__ == '__main__':
       main()
   ```

#### Acceptance Criteria
- [ ] Detector identifies parallel opportunities in Phase G workstreams
- [ ] Dry-run reports theoretical 40-50% speedup (matches manual analysis)
- [ ] CLI tool outputs human-readable validation report
- [ ] Zero false positives on conflict detection

#### Files Changed
- `core/planning/parallelism_detector.py` (new)
- `core/engine/plan_validator.py` (new)
- `scripts/validate_plan.py` (new)
- `tests/test_parallelism_detection.py` (new)

---

## Phase 2: Parallel Execution Engine

**Duration**: 4 weeks (20-24 hours)  
**Risk**: Medium  
**Goal**: Implement multi-worker DAG-based orchestration  

### Workstream WS-H3: Worker Lifecycle Management

**Priority**: Critical Path  
**Estimated Time**: 8-10 hours  
**Depends On**: WS-H1  

#### Tasks

1. **Worker State Machine** (`core/engine/worker.py`)
   ```python
   from dataclasses import dataclass
   from datetime import datetime, timezone
   from enum import Enum
   from typing import Optional
   
   class WorkerState(Enum):
       SPAWNING = "SPAWNING"
       IDLE = "IDLE"
       BUSY = "BUSY"
       DRAINING = "DRAINING"
       TERMINATED = "TERMINATED"
   
   @dataclass
   class Worker:
       worker_id: str
       adapter_type: str  # 'aider', 'codex', 'claude'
       state: WorkerState
       current_task_id: Optional[str] = None
       sandbox_path: Optional[str] = None
       heartbeat_at: Optional[datetime] = None
       spawned_at: datetime = None
       terminated_at: Optional[datetime] = None
       metadata: dict = None
       
       def __post_init__(self):
           if self.spawned_at is None:
               self.spawned_at = datetime.now(timezone.utc)
   
   class WorkerPool:
       """Manages lifecycle of N workers."""
       
       def __init__(self, max_workers: int = 4):
           self.max_workers = max_workers
           self.workers: Dict[str, Worker] = {}
           self.idle_queue: List[str] = []
       
       def spawn_worker(self, adapter_type: str) -> Worker:
           """Create new worker instance."""
           pass
       
       def assign_task(self, worker_id: str, task_id: str) -> None:
           """Transition worker IDLE → BUSY."""
           pass
       
       def release_worker(self, worker_id: str) -> None:
           """Transition worker BUSY → IDLE."""
           pass
       
       def drain_worker(self, worker_id: str) -> None:
           """Transition worker to DRAINING (no new tasks)."""
           pass
       
       def terminate_worker(self, worker_id: str) -> None:
           """Transition worker to TERMINATED."""
           pass
       
       def get_idle_worker(self, adapter_type: Optional[str] = None) -> Optional[Worker]:
           """Get next available idle worker."""
           pass
       
       def check_heartbeats(self, timeout_sec: int = 300) -> List[str]:
           """Return worker_ids with stale heartbeats."""
           pass
   ```

2. **Heartbeat & Health Monitoring** (`core/engine/worker.py`)
   ```python
   def heartbeat(self, worker_id: str) -> None:
       """Update worker heartbeat timestamp."""
       if worker_id in self.workers:
           self.workers[worker_id].heartbeat_at = datetime.now(timezone.utc)
           # Persist to DB
           from core.state.db import get_connection
           conn = get_connection()
           conn.execute(
               "UPDATE workers SET heartbeat_at = ? WHERE worker_id = ?",
               (self.workers[worker_id].heartbeat_at.isoformat(), worker_id)
           )
           conn.commit()
           conn.close()
   ```

3. **Worker Persistence** (`core/state/crud.py`)
   ```python
   def create_worker(conn, worker: Worker) -> None:
       """Insert worker record."""
       pass
   
   def update_worker_state(conn, worker_id: str, state: WorkerState) -> None:
       """Update worker state."""
       pass
   
   def get_workers(conn, state: Optional[WorkerState] = None) -> List[Worker]:
       """Retrieve workers, optionally filtered by state."""
       pass
   ```

#### Acceptance Criteria
- [ ] Worker pool manages up to N workers
- [ ] State transitions enforced (e.g., can't go TERMINATED → BUSY)
- [ ] Heartbeats persisted to database
- [ ] Stale worker detection (5 min timeout)

#### Files Changed
- `core/engine/worker.py` (new)
- `core/state/crud.py` (extend)
- `tests/test_worker_lifecycle.py` (new)

---

### Workstream WS-H4: Parallel Scheduler Implementation

**Priority**: Critical Path  
**Estimated Time**: 10-12 hours  
**Depends On**: WS-H3  

#### Tasks

1. **Complete DAG Scheduler** (`core/engine/scheduler.py`)
   ```python
   from typing import Dict, List, Set
   from core.state.bundles import WorkstreamBundle
   from core.engine.worker import WorkerPool
   
   class SchedulingWave:
       """One wave of parallel execution."""
       def __init__(self):
           self.workstream_ids: Set[str] = set()
           self.estimated_duration: float = 0.0
   
   class ExecutionPlan:
       """Multi-wave execution plan."""
       def __init__(self):
           self.waves: List[SchedulingWave] = []
           self.critical_path: List[str] = []
           self.total_duration_seq: float = 0.0
           self.total_duration_par: float = 0.0
   
   def build_execution_plan(
       bundles: List[WorkstreamBundle],
       max_workers: int = 4
   ) -> ExecutionPlan:
       """Generate multi-wave execution plan.
       
       Algorithm:
       1. Topological sort (detect cycles - already exists)
       2. For each level in DAG:
          - Group workstreams by file scope conflicts
          - Assign to waves respecting conflict_group
          - Limit wave size to max_workers
       3. Calculate critical path
       """
       pass
   
   def can_run_parallel(ws_a: WorkstreamBundle, ws_b: WorkstreamBundle) -> bool:
       """Check if two workstreams can run in parallel.
       
       Conditions:
       - No dependency relationship (direct or transitive)
       - No file scope write overlap
       - Not in same conflict_group
       - Both have parallel_ok=True
       """
       pass
   ```

2. **Task Assignment Logic** (`core/engine/scheduler.py`)
   ```python
   class TaskScheduler:
       """Assigns tasks to workers from execution plan."""
       
       def __init__(self, worker_pool: WorkerPool):
           self.worker_pool = worker_pool
           self.ready_queue: List[str] = []  # workstream_ids ready to execute
           self.running: Dict[str, str] = {}  # workstream_id → worker_id
       
       def get_next_tasks(self, plan: ExecutionPlan) -> List[str]:
           """Get workstream_ids ready for execution.
           
           Rules:
           - All dependencies completed
           - File scopes available (no conflicts with running tasks)
           - Worker available with required capability
           """
           pass
       
       def assign_task(self, workstream_id: str) -> Optional[str]:
           """Assign workstream to idle worker, return worker_id."""
           pass
   ```

3. **Conflict Group Enforcement** (`core/engine/scheduler.py`)
   ```python
   def check_conflict_groups(
       workstream: WorkstreamBundle,
       running: List[WorkstreamBundle]
   ) -> bool:
       """Ensure conflict_group serialization."""
       if not workstream.conflict_group:
           return True  # No conflict group = can run
       
       for ws in running:
           if ws.conflict_group == workstream.conflict_group:
               return False  # Same group already running
       
       return True
   ```

4. **Integration with Orchestrator** (`core/engine/orchestrator.py`)
   ```python
   def execute_parallel(
       bundles: List[WorkstreamBundle],
       max_workers: int = 4
   ) -> Dict[str, Any]:
       """Execute workstreams in parallel.
       
       High-level flow:
       1. Build execution plan
       2. Spawn worker pool
       3. For each wave:
          - Assign tasks to workers
          - Monitor completion
          - Collect results
       4. Tear down workers
       """
       pass
   ```

#### Acceptance Criteria
- [ ] Scheduler generates correct execution waves for Phase G workstreams
- [ ] File scope conflicts prevent parallel execution
- [ ] conflict_group enforces serialization
- [ ] Critical path identified correctly
- [ ] Integration test: run 2 independent workstreams in parallel

#### Files Changed
- `core/engine/scheduler.py` (complete implementation)
- `core/engine/orchestrator.py` (add parallel execution)
- `tests/test_scheduler.py` (new)
- `tests/test_parallel_execution.py` (new)

---

### Workstream WS-H5: Event Bus & Observability

**Priority**: Medium  
**Estimated Time**: 4-5 hours  
**Depends On**: WS-H3  

#### Tasks

1. **Event Bus Implementation** (`core/engine/event_bus.py`)
   ```python
   from dataclasses import dataclass
   from datetime import datetime, timezone
   from enum import Enum
   from typing import Any, Dict, Optional
   
   class EventType(Enum):
       WORKER_SPAWNED = "worker_spawned"
       WORKER_TERMINATED = "worker_terminated"
       TASK_ASSIGNED = "task_assigned"
       TASK_STARTED = "task_started"
       TASK_PROGRESS = "task_progress"
       TASK_COMPLETED = "task_completed"
       TASK_FAILED = "task_failed"
       HEARTBEAT = "heartbeat"
       MERGE_CONFLICT = "merge_conflict"
       RESOURCE_LIMIT = "resource_limit"
   
   @dataclass
   class Event:
       event_type: EventType
       timestamp: datetime
       worker_id: Optional[str] = None
       task_id: Optional[str] = None
       run_id: Optional[str] = None
       workstream_id: Optional[str] = None
       payload: Optional[Dict[str, Any]] = None
   
   class EventBus:
       """Centralized event logging and routing."""
       
       def emit(self, event: Event) -> None:
           """Persist event to database and notify listeners."""
           from core.state.db import get_connection
           conn = get_connection()
           conn.execute("""
               INSERT INTO events (event_type, worker_id, task_id, run_id, workstream_id, timestamp, payload)
               VALUES (?, ?, ?, ?, ?, ?, ?)
           """, (
               event.event_type.value,
               event.worker_id,
               event.task_id,
               event.run_id,
               event.workstream_id,
               event.timestamp.isoformat(),
               json.dumps(event.payload) if event.payload else None
           ))
           conn.commit()
           conn.close()
       
       def query(
           self,
           event_type: Optional[EventType] = None,
           run_id: Optional[str] = None,
           since: Optional[datetime] = None
       ) -> List[Event]:
           """Query events from database."""
           pass
   ```

2. **Instrumentation Points**
   - Worker lifecycle events: spawn, terminate, state changes
   - Task events: assign, start, progress, complete, fail
   - Heartbeats: periodic health checks
   - Resource events: circuit breaker triggers

3. **Event Viewer CLI** (`scripts/view_events.py`)
   ```python
   #!/usr/bin/env python3
   """View execution events from database."""
   
   import argparse
   from core.engine.event_bus import EventBus, EventType
   
   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--run-id')
       parser.add_argument('--event-type')
       parser.add_argument('--tail', type=int, default=50)
       args = parser.parse_args()
       
       bus = EventBus()
       events = bus.query(
           event_type=EventType[args.event_type] if args.event_type else None,
           run_id=args.run_id
       )
       
       for e in events[-args.tail:]:
           print(f"[{e.timestamp}] {e.event_type.value}: {e.payload}")
   ```

#### Acceptance Criteria
- [ ] Events persisted to database
- [ ] All worker lifecycle transitions emit events
- [ ] Task execution emits start/complete/fail events
- [ ] CLI can query and display events

#### Files Changed
- `core/engine/event_bus.py` (new)
- `core/engine/worker.py` (instrument with events)
- `core/engine/orchestrator.py` (instrument with events)
- `scripts/view_events.py` (new)
- `tests/test_event_bus.py` (new)

---

## Phase 3: Production Robustness

**Duration**: 4 weeks (18-22 hours)  
**Risk**: Medium-High  
**Goal**: Crash recovery, merge strategies, rollback  

### Workstream WS-H6: Crash Recovery Protocol

**Priority**: High  
**Estimated Time**: 6-8 hours  
**Depends On**: WS-H4  

#### Tasks

1. **Recovery Manager** (`core/engine/recovery_manager.py`)
   ```python
   from typing import List, Dict
   from core.engine.worker import Worker, WorkerState
   from core.state.crud import get_steps_by_state
   
   class RecoveryManager:
       """Handles orchestrator restart and crash recovery."""
       
       def recover_from_crash(self) -> Dict[str, Any]:
           """UET Section 3.3: Crash Recovery Protocol.
           
           Steps:
           1. Load last known states from persistence
           2. Identify orphaned tasks (RUNNING with no alive worker)
           3. Mark orphaned tasks as FAILED (E_ORCHESTRATOR_CRASH)
           4. Apply self-heal policy (rerun vs escalate)
           5. Restore workers and resume scheduling
           """
           from core.state.db import get_connection
           conn = get_connection()
           
           # Find RUNNING tasks with terminated/missing workers
           orphaned = self._find_orphaned_tasks(conn)
           
           # Mark as failed
           for task_id in orphaned:
               self._mark_task_failed(conn, task_id, "E_ORCHESTRATOR_CRASH")
           
           # Load workers - terminate any in BUSY state
           workers = get_workers(conn, state=WorkerState.BUSY)
           for w in workers:
               update_worker_state(conn, w.worker_id, WorkerState.TERMINATED)
           
           conn.close()
           
           return {
               'orphaned_tasks': len(orphaned),
               'recovered': True
           }
       
       def _find_orphaned_tasks(self, conn) -> List[str]:
           """Find RUNNING tasks with dead workers."""
           pass
   ```

2. **Checkpoint System** (`core/engine/checkpointing.py`)
   ```python
   def checkpoint_task_state(
       task_id: str,
       state: str,
       worker_id: Optional[str] = None,
       partial_output: Optional[str] = None
   ) -> None:
       """Idempotent checkpoint for task state."""
       from core.state.db import get_connection
       conn = get_connection()
       
       # Update step state
       conn.execute("""
           UPDATE steps 
           SET status = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?
       """, (state, task_id))
       
       # Record checkpoint event
       from core.engine.event_bus import EventBus, Event, EventType
       bus = EventBus()
       bus.emit(Event(
           event_type=EventType.TASK_CHECKPOINT,
           timestamp=datetime.now(timezone.utc),
           task_id=task_id,
           worker_id=worker_id,
           payload={'state': state, 'partial_output': partial_output}
       ))
       
       conn.commit()
       conn.close()
   ```

3. **Auto-Restart Integration** (`scripts/run_with_recovery.py`)
   ```python
   #!/usr/bin/env python3
   """Run orchestrator with automatic crash recovery."""
   
   from core.engine.recovery_manager import RecoveryManager
   from core.engine.orchestrator import execute_parallel
   
   def main():
       # Check for crash recovery needed
       recovery = RecoveryManager()
       result = recovery.recover_from_crash()
       
       if result['orphaned_tasks'] > 0:
           print(f"Recovered from crash: {result['orphaned_tasks']} orphaned tasks")
       
       # Resume execution
       execute_parallel(bundles, max_workers=4)
   ```

#### Acceptance Criteria
- [ ] Orchestrator restart detects orphaned tasks
- [ ] Orphaned tasks marked as failed with correct error type
- [ ] Recovery completes without data loss
- [ ] Integration test: kill orchestrator mid-execution, restart succeeds

#### Files Changed
- `core/engine/recovery_manager.py` (new)
- `core/engine/checkpointing.py` (new)
- `scripts/run_with_recovery.py` (new)
- `tests/test_crash_recovery.py` (new)

---

### Workstream WS-H7: Merge Strategy & Integration Worker

**Priority**: High  
**Estimated Time**: 8-10 hours  
**Depends On**: WS-H4  

#### Tasks

1. **Integration Worker Role** (`core/engine/integration_worker.py`)
   ```python
   from typing import List, Optional
   from dataclasses import dataclass
   
   @dataclass
   class MergeCandidate:
       workstream_id: str
       branch_name: str
       patch_file: Optional[str]
       priority: int
       age_hours: float
   
   class IntegrationWorker:
       """UET Section 2.2: Dedicated merge orchestrator."""
       
       def __init__(self, target_branch: str = 'main'):
           self.target_branch = target_branch
       
       def collect_candidates(self) -> List[MergeCandidate]:
           """Identify completed workstreams ready for merge."""
           # Query database for workstreams with status='completed'
           # All required tests passed
           # No blocking errors
           pass
       
       def prioritize_candidates(self, candidates: List[MergeCandidate]) -> List[MergeCandidate]:
           """UET Section 2.3: Deterministic merge ordering.
           
           Sort by:
           1. Critical path importance
           2. Dependency count (fewer deps = higher priority)
           3. Age (oldest first)
           """
           pass
       
       def merge_candidate(self, candidate: MergeCandidate) -> bool:
           """Attempt merge, return success status."""
           try:
               # Apply patch or merge branch
               self._apply_changes(candidate)
               
               # Run validation (tests, static checks)
               if not self._validate_merge():
                   self._revert_merge()
                   return False
               
               return True
           except MergeConflictError as e:
               self._handle_conflict(candidate, e)
               return False
       
       def _apply_changes(self, candidate: MergeCandidate) -> None:
           """Apply patch or merge branch."""
           pass
       
       def _validate_merge(self) -> bool:
           """Run tests and checks."""
           pass
       
       def _revert_merge(self) -> None:
           """Revert failed merge."""
           pass
       
       def _handle_conflict(self, candidate: MergeCandidate, error: Exception) -> None:
           """Route merge conflict to error pipeline."""
           pass
   ```

2. **Conflict Resolution** (`core/engine/merge_conflict_resolver.py`)
   ```python
   from typing import List, Dict
   
   class MergeConflictError(Exception):
       def __init__(self, files: List[str]):
           self.files = files
   
   class ConflictResolver:
       """UET Section 2.4: Conflict handling."""
       
       def create_conflict_task(
           self,
           workstream_a: str,
           workstream_b: str,
           conflicted_files: List[str]
       ) -> str:
           """Generate merge conflict resolution task.
           
           Returns: task_id for resolution
           """
           from core.state.db import get_connection
           conn = get_connection()
           
           # Insert into merge_conflicts table
           conn.execute("""
               INSERT INTO merge_conflicts 
               (run_id, workstream_a, workstream_b, conflicted_files, resolution_status, created_at)
               VALUES (?, ?, ?, ?, 'PENDING', CURRENT_TIMESTAMP)
           """, (run_id, workstream_a, workstream_b, json.dumps(conflicted_files)))
           
           conflict_id = conn.lastrowid
           conn.commit()
           conn.close()
           
           # Create error pipeline task
           from error.engine.error_pipeline_service import ErrorPipelineService
           svc = ErrorPipelineService()
           task_id = svc.create_merge_conflict_task(conflict_id, conflicted_files)
           
           return task_id
       
       def auto_resolve(self, conflict_id: int) -> bool:
           """Attempt automatic AI-assisted merge."""
           # Use Aider with --ask mode to resolve
           pass
   ```

3. **Integration Phase** (`workstreams/integration_phase.json`)
   ```json
   {
     "id": "ws-integration",
     "openspec_change": "INTEGRATION",
     "ccpm_issue": "N/A",
     "gate": 5,
     "files_scope": ["*"],
     "kind": "integration",
     "priority": "foreground",
     "tasks": [
       "Collect completed workstream branches",
       "Prioritize merge candidates",
       "Execute deterministic merge sequence",
       "Validate each merge with tests",
       "Handle conflicts via error pipeline"
     ],
     "depends_on": ["ws-*"]
   }
   ```

#### Acceptance Criteria
- [ ] Integration worker collects completed workstreams
- [ ] Merge candidates sorted deterministically
- [ ] Conflicts detected and routed to error pipeline
- [ ] Successful merges validated with tests
- [ ] Integration test: merge 3 parallel workstreams

#### Files Changed
- `core/engine/integration_worker.py` (new)
- `core/engine/merge_conflict_resolver.py` (new)
- `workstreams/integration_phase.json` (new)
- `tests/test_integration_worker.py` (new)

---

### Workstream WS-H8: Rollback & Compensation (Saga Pattern)

**Priority**: Medium  
**Estimated Time**: 6-8 hours  
**Depends On**: WS-H4  

#### Tasks

1. **Compensation Engine** (`core/engine/compensation.py`)
   ```python
   from typing import List, Dict, Any
   
   class CompensationEngine:
       """UET Section 10: Logical rollback via Saga pattern."""
       
       def rollback_workstream(self, workstream_id: str) -> bool:
           """Execute compensation actions for a workstream."""
           from core.state.bundles import get_bundle
           bundle = get_bundle(workstream_id)
           
           if not bundle.compensation_actions:
               # Fall back to Git revert
               return self._git_revert(workstream_id)
           
           # Execute compensation actions in reverse order
           for action in reversed(bundle.compensation_actions):
               success = self._execute_compensation(action)
               if not success:
                   # Escalate to human
                   self._escalate_rollback_failure(workstream_id, action)
                   return False
           
           return True
       
       def rollback_phase(self, phase_workstreams: List[str]) -> bool:
           """Rollback multiple workstreams (phase-level)."""
           for ws_id in reversed(phase_workstreams):
               if not self.rollback_workstream(ws_id):
                   return False
           return True
       
       def _execute_compensation(self, action: str) -> bool:
           """Execute single compensation action.
           
           Examples:
           - "revert schema migrations: db_migrate down 001"
           - "restore config: cp backup/config.yaml config/config.yaml"
           - "delete generated files: rm -rf generated/"
           """
           pass
       
       def _git_revert(self, workstream_id: str) -> bool:
           """Simple Git revert as fallback."""
           pass
   ```

2. **Compensation Action Examples**
   - Schema migrations: `compensation_actions: ["db_migrate down 001"]`
   - Config changes: `compensation_actions: ["git checkout HEAD -- config/"]`
   - Generated files: `compensation_actions: ["rm -rf build/", "rm -rf dist/"]`
   - API changes: `compensation_actions: ["git revert <commit>", "run deprecation notices"]`

3. **Rollback Triggers**
   - Manual: `scripts/rollback_workstream.py --workstream ws-id`
   - Automatic: integration test failures in later phases
   - Policy-driven: cost overruns, security findings

#### Acceptance Criteria
- [ ] Compensation actions execute in reverse order
- [ ] Git revert fallback works
- [ ] Partial rollback scoping (task, workstream, phase)
- [ ] Integration test: rollback phase, verify state restored

#### Files Changed
- `core/engine/compensation.py` (new)
- `scripts/rollback_workstream.py` (new)
- `tests/test_compensation.py` (new)

---

## Phase 4: Intelligence & Optimization

**Duration**: 4 weeks (16-20 hours)  
**Risk**: Low  
**Goal**: Cost tracking, context management, metrics  

### Workstream WS-H9: Cost & Token Tracking

**Priority**: Medium  
**Estimated Time**: 6-8 hours  
**Depends On**: WS-H4  

#### Tasks

1. **Cost Tracker** (`core/engine/cost_tracker.py`)
   ```python
   from dataclasses import dataclass
   from typing import Dict, Optional
   
   @dataclass
   class ModelPricing:
       model_name: str
       input_cost_per_1k: float  # USD per 1K tokens
       output_cost_per_1k: float
   
   PRICING_TABLE: Dict[str, ModelPricing] = {
       'gpt-4': ModelPricing('gpt-4', 0.03, 0.06),
       'gpt-3.5-turbo': ModelPricing('gpt-3.5-turbo', 0.0015, 0.002),
       'claude-3-opus': ModelPricing('claude-3-opus', 0.015, 0.075),
       'claude-3-sonnet': ModelPricing('claude-3-sonnet', 0.003, 0.015),
   }
   
   class CostTracker:
       """UET Section 7: Cost & API usage tracking."""
       
       def record_usage(
           self,
           run_id: str,
           workstream_id: str,
           step_id: str,
           worker_id: str,
           model_name: str,
           input_tokens: int,
           output_tokens: int
       ) -> float:
           """Record token usage and calculate cost."""
           pricing = PRICING_TABLE.get(model_name)
           if not pricing:
               # Unknown model, estimate conservatively
               pricing = PRICING_TABLE['gpt-4']
           
           cost = (
               (input_tokens / 1000.0) * pricing.input_cost_per_1k +
               (output_tokens / 1000.0) * pricing.output_cost_per_1k
           )
           
           # Persist to database
           from core.state.db import get_connection
           conn = get_connection()
           conn.execute("""
               INSERT INTO cost_tracking
               (run_id, workstream_id, step_id, worker_id, input_tokens, output_tokens, 
                estimated_cost_usd, model_name, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
           """, (run_id, workstream_id, step_id, worker_id, input_tokens, output_tokens, cost, model_name))
           conn.commit()
           conn.close()
           
           return cost
       
       def get_total_cost(self, run_id: str) -> float:
           """Get total cost for a run."""
           pass
       
       def get_workstream_cost(self, run_id: str, workstream_id: str) -> float:
           """Get cost for specific workstream."""
           pass
   ```

2. **Budget Enforcement** (`core/engine/budget_policy.py`)
   ```python
   from dataclasses import dataclass
   
   @dataclass
   class BudgetPolicy:
       max_cost_total: float = 100.0  # USD
       max_cost_per_phase: float = 20.0
       max_cost_per_task: float = 5.0
       max_parallel_workers_for_budget: int = 4
   
   class BudgetEnforcer:
       """UET Section 7.2: Budget policies."""
       
       def __init__(self, policy: BudgetPolicy):
           self.policy = policy
       
       def check_budget(self, run_id: str) -> Dict[str, Any]:
           """Check if budget thresholds exceeded."""
           tracker = CostTracker()
           total = tracker.get_total_cost(run_id)
           
           if total >= self.policy.max_cost_total * 0.9:
               return {
                   'action': 'WARN',
                   'message': f'Approaching budget limit: ${total:.2f} / ${self.policy.max_cost_total}'
               }
           
           if total >= self.policy.max_cost_total:
               return {
                   'action': 'HALT',
                   'message': f'Budget exceeded: ${total:.2f} / ${self.policy.max_cost_total}'
               }
           
           return {'action': 'CONTINUE'}
       
       def adjust_parallelism(self, run_id: str) -> int:
           """Reduce parallelism when approaching budget."""
           result = self.check_budget(run_id)
           if result['action'] == 'WARN':
               return max(1, self.policy.max_parallel_workers_for_budget - 1)
           return self.policy.max_parallel_workers_for_budget
   ```

3. **Cost Reporting** (`scripts/cost_report.py`)
   ```python
   #!/usr/bin/env python3
   """Generate cost report for run."""
   
   from core.engine.cost_tracker import CostTracker
   
   def main():
       import argparse
       parser = argparse.ArgumentParser()
       parser.add_argument('--run-id', required=True)
       parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text')
       args = parser.parse_args()
       
       tracker = CostTracker()
       # Generate detailed cost breakdown
       # By workstream, by step, by worker, by model
   ```

#### Acceptance Criteria
- [ ] Token usage recorded for each task
- [ ] Cost calculated using pricing table
- [ ] Budget warnings trigger at 90% threshold
- [ ] Budget halt prevents execution at 100%
- [ ] Cost report CLI generates breakdown

#### Files Changed
- `core/engine/cost_tracker.py` (new)
- `core/engine/budget_policy.py` (new)
- `scripts/cost_report.py` (new)
- `tests/test_cost_tracking.py` (new)

---

### Workstream WS-H10: Context Window Management

**Priority**: Medium  
**Estimated Time**: 5-6 hours  
**Depends On**: WS-H9  

#### Tasks

1. **Context Estimator** (`core/engine/context_estimator.py`)
   ```python
   from typing import List, Dict
   from pathlib import Path
   
   class ContextEstimator:
       """UET Section 5: Context window management."""
       
       TOKEN_PER_CHAR = 0.25  # Rough estimate: 4 chars per token
       
       def estimate_tokens(self, files: List[str], additional_context: str = "") -> int:
           """Estimate total token count for context."""
           total_chars = 0
           
           # File contents
           for f in files:
               try:
                   total_chars += len(Path(f).read_text(encoding='utf-8'))
               except Exception:
                   pass
           
           # Additional context (specs, prior outputs)
           total_chars += len(additional_context)
           
           return int(total_chars * self.TOKEN_PER_CHAR)
       
       def check_context_limit(
           self,
           estimated_tokens: int,
           tool: str
       ) -> Dict[str, Any]:
           """Check if context exceeds tool limits."""
           limits = {
               'aider': 128000,  # Claude/GPT-4 limits
               'codex': 8000,    # Older models
               'claude': 200000, # Claude 3 extended
           }
           
           limit = limits.get(tool, 8000)
           
           if estimated_tokens > limit:
               return {
                   'fits': False,
                   'estimated': estimated_tokens,
                   'limit': limit,
                   'overflow': estimated_tokens - limit,
                   'strategy': self._suggest_strategy(estimated_tokens, limit)
               }
           
           return {'fits': True, 'estimated': estimated_tokens, 'limit': limit}
       
       def _suggest_strategy(self, estimated: int, limit: int) -> str:
           """UET Section 5.2: Context strategies."""
           overflow_pct = (estimated - limit) / limit
           
           if overflow_pct < 0.2:
               return 'PRUNE'  # Truncate comments, logs
           elif overflow_pct < 0.5:
               return 'SUMMARIZE'  # Generate summaries
           else:
               return 'CHUNK'  # Split into subtasks
   ```

2. **Context Pruning** (`core/engine/context_pruner.py`)
   ```python
   def prune_context(files: List[str], target_tokens: int) -> List[str]:
       """Prune less relevant sections to fit context limit.
       
       Strategy:
       - Remove comments in order: docstrings, block comments, line comments
       - Truncate old log entries
       - Remove test files if not test-related task
       """
       pass
   
   def summarize_context(files: List[str], target_tokens: int) -> str:
       """Generate summarized version of large files."""
       # Use AI to create compact summaries
       # Keep interface definitions, key functions
       pass
   ```

3. **Context Handoff** (`core/engine/context_handoff.py`)
   ```python
   def create_phase_summary(workstream_id: str) -> str:
       """UET Section 5.3: Compact output for next phase.
       
       Structure:
       - Key decisions made
       - Interface definitions
       - Critical constraints
       - Essential context for continuation
       """
       pass
   ```

#### Acceptance Criteria
- [ ] Token estimation within 10% of actual
- [ ] Context limit detection prevents tool failures
- [ ] Pruning reduces context by 20-30%
- [ ] Phase summaries < 2000 tokens

#### Files Changed
- `core/engine/context_estimator.py` (new)
- `core/engine/context_pruner.py` (new)
- `core/engine/context_handoff.py` (new)
- `tests/test_context_management.py` (new)

---

### Workstream WS-H11: Metrics, Replay & What-If Analysis

**Priority**: Low  
**Estimated Time**: 5-6 hours  
**Depends On**: WS-H5, WS-H9  

#### Tasks

1. **Metrics Aggregator** (`core/engine/metrics.py`)
   ```python
   from dataclasses import dataclass
   from typing import Dict, List
   
   @dataclass
   class ExecutionMetrics:
       run_id: str
       total_duration_sec: float
       total_cost_usd: float
       total_tokens: int
       workstreams_completed: int
       workstreams_failed: int
       parallelism_efficiency: float  # actual vs potential
       bottlenecks: List[str]
       error_frequency: Dict[str, int]  # error_type -> count
   
   class MetricsAggregator:
       """UET Section 13: Metrics and observability."""
       
       def compute_metrics(self, run_id: str) -> ExecutionMetrics:
           """Aggregate all metrics for a run."""
           pass
       
       def compute_parallelism_efficiency(self, run_id: str) -> float:
           """Calculate actual vs theoretical parallelism.
           
           Efficiency = actual_speedup / theoretical_max_speedup
           """
           pass
   ```

2. **Replay Engine** (`core/engine/replay.py`)
   ```python
   class ReplayEngine:
       """UET Section 13.3: Execution replay from events."""
       
       def replay_run(self, run_id: str, checkpoint: Optional[str] = None) -> None:
           """Replay execution from event log for auditing."""
           from core.engine.event_bus import EventBus
           bus = EventBus()
           events = bus.query(run_id=run_id)
           
           # Reconstruct state from events
           for event in events:
               # Re-apply state transitions
               pass
   ```

3. **What-If Simulator** (`core/engine/simulator.py`)
   ```python
   class WhatIfSimulator:
       """Simulate execution with different parameters."""
       
       def simulate(
           self,
           bundles: List[WorkstreamBundle],
           max_workers: int,
           budget: float
       ) -> ExecutionMetrics:
           """Dry-run with different config.
           
           Questions:
           - What if we had N more workers?
           - What if we capped parallelism at M?
           - What if budget was $X?
           """
           # Build execution plan
           # Estimate durations/costs
           # Return projected metrics
           pass
   ```

#### Acceptance Criteria
- [ ] Metrics computed for completed runs
- [ ] Parallelism efficiency calculated correctly
- [ ] Replay reconstructs state from events
- [ ] What-if simulation shows impact of config changes

#### Files Changed
- `core/engine/metrics.py` (new)
- `core/engine/replay.py` (new)
- `core/engine/simulator.py` (new)
- `scripts/simulate_plan.py` (new)
- `tests/test_metrics.py` (new)

---

## Testing Strategy

### Unit Tests
- **Coverage Target**: 80%+
- **Focus Areas**:
  - Worker state transitions
  - DAG scheduling logic
  - Event bus persistence
  - Cost calculations
  - Context estimation

### Integration Tests
- **Test Scenarios**:
  1. **Parallel Execution**: 3 independent workstreams run in parallel
  2. **Conflict Detection**: Overlapping file scopes serialize correctly
  3. **Crash Recovery**: Kill orchestrator, restart recovers state
  4. **Merge Conflicts**: Integration worker handles conflicts
  5. **Budget Enforcement**: Halt execution at cost limit
  6. **Context Overflow**: Large workstream triggers pruning

### Performance Tests
- **Benchmarks**:
  - Scheduler overhead: < 100ms for 20 workstreams
  - Event bus throughput: > 1000 events/sec
  - Database queries: < 50ms for common operations

### Validation Tests
- **Schema Validation**: All new fields optional, backward compatible
- **Data Migration**: Legacy bundles load without errors
- **Dry-Run Validation**: Phase G plan validates correctly

---

## Rollout Plan

### Pre-Production (Weeks 1-10)
1. **Phase 1** (Weeks 1-2): Schema + Validation
   - Deploy to dev environment
   - Validate existing workstreams load
   - Generate dry-run reports

2. **Phase 2** (Weeks 3-6): Parallel Execution
   - Test with synthetic workstreams
   - Run Phase G workstreams in parallel (controlled)
   - Monitor event logs and metrics

3. **Phase 3** (Weeks 7-10): Robustness
   - Chaos testing (kill workers, corrupt state)
   - Merge conflict scenarios
   - Rollback exercises

### Production (Weeks 11-14)
4. **Phase 4** (Weeks 11-14): Intelligence
   - Enable cost tracking on real runs
   - Context management for large phases
   - What-if analysis for planning

### Post-Deployment
- **Week 15+**: Monitor metrics, optimize, iterate
- **Continuous**: What-if simulations for new phases

---

## Success Metrics

### Quantitative
- ✅ **Execution Speedup**: 40-50% reduction in wall-clock time (Phase G baseline)
- ✅ **Parallelism Efficiency**: > 70% of theoretical maximum
- ✅ **Crash Recovery**: < 5 min to restore from crash
- ✅ **Cost Accuracy**: Token estimates within 10% of actual
- ✅ **Test Coverage**: > 80% for new code

### Qualitative
- ✅ **Developer Experience**: Simpler phase planning with dry-run validation
- ✅ **Observability**: Event logs enable debugging
- ✅ **Reliability**: Crash recovery prevents data loss
- ✅ **Cost Control**: Budget enforcement prevents overruns

---

## Risk Mitigation

### High Risks
1. **Complexity Explosion**
   - **Mitigation**: Phased rollout, each phase independently valuable
   - **Fallback**: Disable parallelism, run sequentially

2. **Database Performance**
   - **Mitigation**: Index optimization, connection pooling
   - **Fallback**: PostgreSQL migration if SQLite insufficient

3. **Breaking Changes**
   - **Mitigation**: All new fields optional, extensive testing
   - **Fallback**: Version detection, legacy mode

### Medium Risks
4. **Merge Conflict Handling**
   - **Mitigation**: Conservative conflict detection, human escalation
   - **Fallback**: Manual merge workflow

5. **Context Estimation Accuracy**
   - **Mitigation**: Conservative estimates, gradual tuning
   - **Fallback**: Disable auto-pruning, manual context control

---

## Dependencies

### External
- ✅ **Python 3.10+**: Dataclasses, type hints
- ✅ **SQLite 3.35+**: JSON support, window functions
- ✅ **Git 2.30+**: Worktree support
- ⚠️ **Optional**: PostgreSQL (if SQLite performance insufficient)

### Internal
- ✅ **Phase G Complete**: Invoke integration provides config foundation
- ✅ **Error Pipeline**: Integration with existing error states
- ✅ **AIM Bridge**: Capability routing for workers

---

## Future Enhancements (Post-Phase H)

### Phase H+1: Advanced Features
- **Dynamic Dependencies**: Runtime DAG updates (UET Section 4.3)
- **OS Modes**: Resource management tiers (UET Section 1.4)
- **Security Isolation**: Containerization, sandboxing (UET Section 11)
- **Human Review Workflow**: Structured approval gates (UET Section 9)

### Phase H+2: Enterprise Features
- **Distributed Execution**: Multi-machine worker pool
- **Workflow Engine Integration**: Prefect/Temporal/Dagster backends
- **Advanced Metrics**: ML-based bottleneck prediction
- **Multi-Tenant**: Isolated execution environments

---

## Appendix A: File Inventory

### New Files (Est. 25-30 files)

**Core Engine**
- `core/engine/worker.py`
- `core/engine/scheduler.py` (complete)
- `core/engine/plan_validator.py`
- `core/engine/event_bus.py`
- `core/engine/recovery_manager.py`
- `core/engine/checkpointing.py`
- `core/engine/integration_worker.py`
- `core/engine/merge_conflict_resolver.py`
- `core/engine/compensation.py`
- `core/engine/cost_tracker.py`
- `core/engine/budget_policy.py`
- `core/engine/context_estimator.py`
- `core/engine/context_pruner.py`
- `core/engine/context_handoff.py`
- `core/engine/metrics.py`
- `core/engine/replay.py`
- `core/engine/simulator.py`

**Core Planning**
- `core/planning/parallelism_detector.py`

**Scripts**
- `scripts/validate_plan.py`
- `scripts/view_events.py`
- `scripts/run_with_recovery.py`
- `scripts/rollback_workstream.py`
- `scripts/cost_report.py`
- `scripts/simulate_plan.py`

**Tests** (Est. 15 files)
- `tests/test_*.py` for each new module

**Schema**
- `schema/migrations/001_uet_foundation.sql`

**Workstreams**
- `workstreams/integration_phase.json`

### Modified Files (Est. 10 files)
- `schema/workstream.schema.json`
- `schema/schema.sql`
- `core/state/bundles.py`
- `core/state/crud.py`
- `core/engine/orchestrator.py`
- `scripts/validate_workstreams.py`
- `docs/ARCHITECTURE.md`
- `docs/ENGINE_QUICK_REFERENCE.md`

---

## Appendix B: UET Specification Coverage

| UET Section | Phase | Coverage |
|-------------|-------|----------|
| **1. Core Model** | P1-P2 | ✅ Complete |
| 1.1 Hierarchy | P1 | Schema extension |
| 1.2 DAG | P2 | Scheduler implementation |
| 1.3 Parallelism | P2 | Worker pool, file scope conflicts |
| 1.4 OS Modes | Future | Not implemented |
| **2. Merge Strategy** | P3 | ✅ Complete |
| 2.1 Branch Model | P3 | Existing worktree support |
| 2.2 Integration Worker | P3 | Dedicated merge orchestrator |
| 2.3 Merge Rules | P3 | Deterministic ordering |
| 2.4 Conflict Handling | P3 | Error pipeline integration |
| **3. State Persistence** | P3 | ✅ Complete |
| 3.1 Storage | P1 | Database extension |
| 3.2 Checkpointing | P3 | Task state checkpoints |
| 3.3 Crash Recovery | P3 | Recovery manager |
| **4. Inter-Worker Comm** | P2 | ✅ Complete |
| 4.1 Event Bus | P2 | Event persistence |
| 4.2 Worker Signaling | P2 | Lifecycle events |
| 4.3 Dynamic Dependencies | Future | Not implemented |
| **5. Context Management** | P4 | ✅ Complete |
| 5.1 Estimation | P4 | Token counting |
| 5.2 Strategies | P4 | Pruning, summarization |
| 5.3 Handoff | P4 | Phase summaries |
| **6. Plan Validation** | P1 | ✅ Complete |
| 6.1-6.3 Schema/DAG | P1 | Existing + extension |
| 6.4 Dry-Run | P1 | Validator tool |
| **7. Cost Tracking** | P4 | ✅ Complete |
| 7.1 Metrics | P4 | Token/cost recording |
| 7.2 Budget | P4 | Enforcement policies |
| 7.3 Rate Limiting | Future | Not implemented |
| **8. Test Gates** | P1 | ⚠️ Partial |
| 8.1-8.3 Gates | P1 | Schema support, enforcement TODO |
| **9. Human Review** | Future | ⚠️ Stub only |
| **10. Rollback** | P3 | ✅ Complete |
| 10.1-10.3 Compensation | P3 | Saga pattern |
| **11. Security** | Future | ⚠️ Not implemented |
| **12. Worker Lifecycle** | P2 | ✅ Complete |
| **13. Metrics/Replay** | P4 | ✅ Complete |

**Coverage Summary**: 75% complete, 15% future work, 10% partial

---

## Appendix C: Comparison to Workflow Engines

### vs. Prefect/Temporal/Dagster

**Similarities**:
- DAG-based execution
- State persistence
- Retry/recovery
- Observability

**Key Differences** (Why Custom Implementation):
1. **AI-Specific**: Context window management, cost tracking
2. **File Scope Awareness**: Git worktree integration, conflict detection
3. **Multi-CLI Orchestration**: Heterogeneous tool adapters (Aider, Claude, etc.)
4. **Lightweight**: SQLite-based, no separate server required
5. **Development Pipeline Focus**: Compensation actions, merge strategies

**Future**: Could map onto Prefect/Temporal as backend (UET is tool-agnostic)

---

## Appendix D: Phase Checklist Template

```markdown
## Phase X Checklist

### Pre-Phase
- [ ] Review UET specification sections
- [ ] Design module architecture
- [ ] Write test cases (TDD)
- [ ] Update schema if needed

### Implementation
- [ ] Create module files
- [ ] Implement core logic
- [ ] Add instrumentation (events, logging)
- [ ] Write unit tests (80%+ coverage)
- [ ] Integration tests

### Validation
- [ ] Run existing tests (no regressions)
- [ ] Dry-run validation passes
- [ ] Performance benchmarks meet targets
- [ ] Security review (if applicable)

### Documentation
- [ ] Update ARCHITECTURE.md
- [ ] Add code comments
- [ ] Update ENGINE_QUICK_REFERENCE.md
- [ ] Write migration guide

### Deployment
- [ ] Database migration tested
- [ ] Backward compatibility verified
- [ ] Rollback plan documented
- [ ] Deploy to dev → staging → prod
```

---

**End of UET Integration Plan**

**Next Steps**: Review with team, prioritize phases, create WS-H1 workstream bundle

