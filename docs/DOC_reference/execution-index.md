---
doc_id: DOC-GUIDE-EXECUTION-INDEX-856
---

# Execution Index – How Things Run

**Purpose**: Map execution flows, entry points, and runtime behavior.

## Execution Entry Points

### 1. Primary Orchestrator Flow
```
Entry: python -m core.orchestrator run --plan <file>
├─ core.orchestrator.Orchestrator.run_plan()
├─ core.planner.Planner.load_plan()
├─ core.scheduler.Scheduler.schedule_tasks()
└─ core.executor.Executor.execute_batch()
```

### 2. Error Detection Flow
```
Entry: python -m error.engine.error_engine detect
├─ error.engine.ErrorEngine.detect()
├─ error.plugins.*.parse() [plugin detection]
└─ error.engine.ErrorEngine.log_errors()
```

### 3. Specification Validation Flow
```
Entry: python -m specifications.tools.validator validate
├─ specifications.tools.validator.load_spec()
├─ specifications.tools.validator.validate_structure()
└─ specifications.tools.validator.report()
```

### 4. Project Management Flow
```
Entry: python -m pm.cli workstream create
├─ pm.workstream_manager.create_workstream()
├─ core.state.db.insert_workstream()
└─ pm.checkpoint.create_initial_checkpoint()
```

## State Transitions

### Workstream Lifecycle
```
PLANNED → IN_PROGRESS → PAUSED → IN_PROGRESS → COMPLETED
                    ↓
                  FAILED → RETRYING → IN_PROGRESS
```

### Task Execution States
```
PENDING → RUNNING → SUCCESS
              ↓
            FAILED → RETRYING → SUCCESS
                           ↓
                         FAILED (max retries)
```

## Execution DAG Pattern

All orchestration follows this DAG structure:

```
Plan Load → Validation → Scheduling → Execution → State Persistence
                                          ↓
                                    Circuit Breaker Check
                                          ↓
                                    Retry Logic (if failed)
```

## Checkpoint System

```
Before Task Execution:
  └─ Create checkpoint (append-only JSONL)

After Task Execution:
  ├─ Log result (ULID-based identity)
  └─ Update workstream state
```

## Retry & Recovery

**Circuit Breaker Pattern**:
- 3 failures → OPEN (block execution)
- 30s timeout → HALF_OPEN (test retry)
- Success → CLOSED (resume)

**Retry Strategy**:
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Idempotency: Required for all tasks

## Execution Logs

**Location**: `.runs/<run-id>/execution.jsonl`

**Format**: Append-only JSONL with ULID timestamps

```json
{"ulid": "01ARZ...", "task_id": "T-001", "status": "running", "ts": "..."}
{"ulid": "01ARZ...", "task_id": "T-001", "status": "success", "ts": "..."}
```

## Configuration Loading Order

1. `PROJECT_PROFILE.yaml` (project-level config)
2. `QUALITY_GATE.yaml` (validation rules)
3. `ai_policies.yaml` (governance policies)
4. Workstream-specific config (if present)

**Reference**: See `core/README.md` for detailed orchestrator architecture.
