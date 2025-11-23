# UET V2 Specifications Patch Analysis

**Generated**: 2025-11-23T11:12:14Z  
**Purpose**: Analyze UET V2 specification files for master plan patches  
**Status**: CRITICAL - Core UET V2 technical specifications identified

---

## Executive Summary

**5 UET V2 specification files analyzed** - **ALL contain CRITICAL technical details**:

| File | Priority | Content | Impact |
|------|----------|---------|--------|
| **STATE_MACHINES.md** | CRITICAL | 3 state machines with transitions | Defines component behavior |
| **COMPONENT_CONTRACTS.md** | CRITICAL | 10 component API contracts | Enables parallel development |
| **DAG_SCHEDULER.md** | CRITICAL | Task dependency model | Parallel execution foundation |
| **FILE_SCOPE.md** | CRITICAL | File isolation rules | Conflict prevention |
| **INTEGRATION_POINTS.md** | CRITICAL | Component call graph | Prevents circular dependencies |

**Total New Information**: Complete UET V2 technical specification

---

## Critical Findings

### 1. STATE_MACHINES.md - CRITICAL

**Defines 3 Core State Machines**:

#### Worker State Machine
```
SPAWNING → IDLE → BUSY → DRAINING → TERMINATED
    ↓               ↓
TERMINATED   TERMINATED
```

**States**: SPAWNING, IDLE, BUSY, DRAINING, TERMINATED  
**Transitions**: 9 valid, 5 invalid (raise ValueError)  
**Invariants**: 
- Heartbeat required every 60s
- Missing 2 heartbeats → TERMINATED
- Affinity immutable after SPAWNING

#### Patch Ledger State Machine
```
created → validated → queued → applied → verified → committed
   ↓         ↓          ↓         ↓         ↓
quarantined, apply_failed → quarantined/dropped
committed → rolled_back
```

**States**: 10 states (created → committed/rolled_back/quarantined/dropped)  
**Terminal States**: rolled_back, quarantined, dropped  
**Validation Points**: created → validated, validated → queued

#### Test Gate State Machine
```
PENDING → RUNNING → PASSED/FAILED
```

**Impact**: Every component needs state machine implementation!

---

### 2. COMPONENT_CONTRACTS.md - CRITICAL

**Defines 10 Component APIs**:

1. **WorkerLifecycle**
   ```python
   spawn_worker(worker_id, worker_type, affinity) -> WorkerRecord
   transition_state(worker_id, new_state) -> bool
   heartbeat(worker_id) -> None
   terminate_worker(worker_id) -> None
   get_idle_workers(worker_type) -> List[WorkerRecord]
   ```

2. **IntegrationWorker**
3. **PatchLedger**
4. **PatchValidator**
5. **PatchPolicyEngine**
6. **TestGateExecutor**
7. **MergeOrchestrator**
8. **ContextManager**
9. **FeedbackLoop**
10. **CompensationEngine**

**Impact**: Each component needs stub implementation with contracts!

---

### 3. DAG_SCHEDULER.md - CRITICAL

**Task Dependency Model**:

#### 4 Dependency Types
1. **Direct**: `depends_on` - explicit task dependencies
2. **Resource**: `files` - auto-inferred from file access
3. **Gate**: `gates` - blocked until tests pass
4. **Phase**: `phase_id` - phase boundaries are sync points

#### Auto-Inference Example
```python
# Task A produces file
{"step_id": "A", "files": ["core/executor.py"], "mode": "edit"}

# Task B reads same file → auto-dependency
{"step_id": "B", "files": ["core/executor.py"], "mode": "read"}

# Scheduler infers: B.depends_on = ["A"]
```

**Impact**: Scheduler needs dependency resolver algorithm!

---

### 4. FILE_SCOPE.md - CRITICAL

**File Access Modes**:

| Mode | Lock Type | Concurrency |
|------|-----------|-------------|
| **read** | None | ∞ readers |
| **edit** | Exclusive | 1 writer |
| **create** | Exclusive | 1 creator |
| **delete** | Exclusive | 1 deleter |
| **append** | Shared | N appenders |

**Scope Granularity**:
- **File-level**: Lock entire file
- **Line-level**: Lock specific lines (e.g., "lines:45-55")
- **Function-level**: Lock via AST (e.g., "function:execute")

**Isolation Strategy**: Git worktrees per worker

```
.worktrees/
├── worker-001/  # Worker 1's isolated copy
├── worker-002/  # Worker 2's isolated copy
└── worker-003/  # Worker 3's isolated copy
```

**Impact**: File scope enforcement needed in all tasks!

---

### 5. INTEGRATION_POINTS.md - CRITICAL

**Component Call Graph**:

```
Orchestrator (root)
  ├─> WorkerLifecycle
  ├─> PatchLedger
  ├─> TestGateExecutor
  ├─> IntegrationWorker
  │     ├─> MergeOrchestrator
  │     │     ├─> PatchValidator
  │     │     │     └─> PatchPolicyEngine
  │     │     └─> LanguageValidator
  │     ├─> CompensationEngine
  │     └─> EventBus
  ├─> ContextManager
  ├─> FeedbackLoop
  └─> EventBus
```

**Circular Dependency Prevention**:
- EventBus: No outbound calls (pure sink)
- PatchValidator: No database calls (pure function)
- ContextManager: No orchestrator calls

**Impact**: Dependency injection pattern required!

---

## Required Patches

### Patch 003: UET V2 State Machines

```json
[
  {
    "op": "add",
    "path": "/meta/state_machines",
    "value": {
      "worker_lifecycle": {
        "states": ["SPAWNING", "IDLE", "BUSY", "DRAINING", "TERMINATED"],
        "transitions": {
          "SPAWNING": ["IDLE", "TERMINATED"],
          "IDLE": ["BUSY", "TERMINATED"],
          "BUSY": ["IDLE", "DRAINING", "TERMINATED"],
          "DRAINING": ["TERMINATED"],
          "TERMINATED": []
        },
        "invariants": [
          "Heartbeat required every 60s for IDLE/BUSY",
          "Missing 2 heartbeats → TERMINATED",
          "Affinity immutable after SPAWNING"
        ],
        "database_table": "workers"
      },
      "patch_ledger": {
        "states": ["created", "validated", "queued", "applied", "apply_failed", "verified", "committed", "rolled_back", "quarantined", "dropped"],
        "terminal_states": ["committed", "rolled_back", "quarantined", "dropped"],
        "transitions": {
          "created": ["validated", "quarantined"],
          "validated": ["queued", "quarantined"],
          "queued": ["applied", "dropped"],
          "applied": ["verified", "apply_failed"],
          "apply_failed": ["quarantined"],
          "verified": ["committed", "quarantined"],
          "committed": ["rolled_back"],
          "rolled_back": [],
          "quarantined": [],
          "dropped": []
        },
        "database_table": "patch_ledger"
      },
      "test_gate": {
        "states": ["PENDING", "RUNNING", "PASSED", "FAILED"],
        "transitions": {
          "PENDING": ["RUNNING"],
          "RUNNING": ["PASSED", "FAILED"],
          "PASSED": [],
          "FAILED": []
        },
        "database_table": "test_gates"
      }
    }
  }
]
```

### Patch 004: Component Contracts

```json
[
  {
    "op": "add",
    "path": "/meta/component_contracts",
    "value": {
      "WorkerLifecycle": {
        "module": "core/engine/worker_lifecycle.py",
        "status": "not_implemented",
        "methods": [
          "spawn_worker(worker_id, worker_type, affinity) -> WorkerRecord",
          "transition_state(worker_id, new_state) -> bool",
          "heartbeat(worker_id) -> None",
          "terminate_worker(worker_id) -> None",
          "get_idle_workers(worker_type) -> List[WorkerRecord]"
        ]
      },
      "PatchLedger": {
        "module": "core/patches/patch_ledger.py",
        "status": "partially_implemented",
        "methods": [
          "create_entry(patch) -> str",
          "transition_state(ledger_id, new_state) -> bool",
          "get_patches_by_state(state) -> List[PatchLedgerEntry]",
          "quarantine_patch(ledger_id, reason) -> None"
        ]
      },
      "MergeOrchestrator": {
        "module": "core/engine/merge_orchestrator.py",
        "status": "not_implemented",
        "methods": [
          "order_candidates(patches) -> List[Patch]",
          "merge(patch) -> MergeResult",
          "detect_conflicts(patch) -> List[Conflict]"
        ]
      },
      "TestGateExecutor": {
        "module": "core/engine/test_gates.py",
        "status": "partially_implemented",
        "methods": [
          "evaluate_gates(phase_id) -> bool",
          "validate_merge(patch_id) -> GateResult"
        ]
      }
    }
  }
]
```

### Patch 005: DAG Scheduler

```json
[
  {
    "op": "add",
    "path": "/meta/dag_scheduler",
    "value": {
      "dependency_types": {
        "direct": {
          "field": "depends_on",
          "description": "Explicit task dependencies"
        },
        "resource": {
          "field": "files",
          "description": "Auto-inferred from file access",
          "auto_inference": true
        },
        "gate": {
          "field": "gates",
          "description": "Blocked until tests pass"
        },
        "phase": {
          "field": "phase_id",
          "description": "Phase boundaries are sync points"
        }
      },
      "algorithms": {
        "dependency_resolution": "Topological sort with cycle detection",
        "parallel_execution": "Wave-based scheduling",
        "deadlock_detection": "Tarjan's strongly connected components"
      }
    }
  }
]
```

### Patch 006: File Scope

```json
[
  {
    "op": "add",
    "path": "/meta/file_scope",
    "value": {
      "access_modes": {
        "read": {"lock": "none", "concurrency": "unlimited"},
        "edit": {"lock": "exclusive", "concurrency": 1},
        "create": {"lock": "exclusive", "concurrency": 1},
        "delete": {"lock": "exclusive", "concurrency": 1},
        "append": {"lock": "shared", "concurrency": "unlimited"}
      },
      "scope_granularity": ["file_level", "line_level", "function_level"],
      "isolation_strategy": {
        "method": "git_worktrees",
        "directory": ".worktrees",
        "per_worker": true
      }
    }
  },
  {
    "op": "add",
    "path": "/validation/file_scope_enforcement",
    "value": {
      "check_overlaps": true,
      "enforce_exclusive_locks": true,
      "validate_scope_syntax": true
    }
  }
]
```

### Patch 007: Integration Points

```json
[
  {
    "op": "add",
    "path": "/meta/integration_points",
    "value": {
      "component_call_graph": {
        "Orchestrator": ["WorkerLifecycle", "PatchLedger", "TestGateExecutor", "IntegrationWorker", "ContextManager", "FeedbackLoop", "EventBus"],
        "IntegrationWorker": ["PatchLedger", "MergeOrchestrator", "TestGateExecutor", "CompensationEngine", "EventBus"],
        "MergeOrchestrator": ["PatchValidator", "LanguageValidator", "PatchLedger", "EventBus"],
        "PatchLedger": ["PatchValidator", "EventBus"],
        "PatchValidator": ["PatchPolicyEngine"],
        "TestGateExecutor": ["Scheduler", "EventBus"],
        "EventBus": [],
        "ContextManager": [],
        "FeedbackLoop": ["Orchestrator"]
      },
      "circular_dependency_prevention": {
        "EventBus": "No outbound calls (pure sink)",
        "PatchValidator": "No database calls (pure function)",
        "ContextManager": "No orchestrator calls"
      },
      "dependency_injection_required": true
    }
  }
]
```

---

## Summary

### Must Patch Immediately (Priority 1)

1. **State Machines** (Patch 003)
   - 3 state machines defined
   - 24 states total
   - Database constraints included

2. **Component Contracts** (Patch 004)
   - 10 component APIs
   - Method signatures defined
   - Implementation status tracked

3. **DAG Scheduler** (Patch 005)
   - 4 dependency types
   - Auto-inference algorithm
   - Parallel execution strategy

4. **File Scope** (Patch 006)
   - 5 access modes
   - 3 granularity levels
   - Git worktree isolation

5. **Integration Points** (Patch 007)
   - Component call graph
   - Circular dependency prevention
   - Dependency injection pattern

---

## Impact on Master Plan

### New Phases Required

Based on these specs, we need **detailed implementation phases**:

- **Phase 2A**: Patch Ledger State Machine (from STATE_MACHINES.md)
- **Phase 2B**: Patch Validator (from COMPONENT_CONTRACTS.md)
- **Phase 3A**: Worker Lifecycle State Machine (from STATE_MACHINES.md)
- **Phase 3B**: DAG Scheduler (from DAG_SCHEDULER.md)
- **Phase 3C**: File Scope Enforcement (from FILE_SCOPE.md)
- **Phase 4**: Integration Points (from INTEGRATION_POINTS.md)

### New Metadata Sections
- `state_machines` (3 machines)
- `component_contracts` (10 components)
- `dag_scheduler` (dependency model)
- `file_scope` (access rules)
- `integration_points` (call graph)

### New Validation
- State transition validation
- File scope overlap detection
- Circular dependency checking
- Contract compliance testing

---

**These specifications are the FOUNDATION of UET V2!**

All phases must implement these contracts.
