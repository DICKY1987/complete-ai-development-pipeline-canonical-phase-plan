---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1598
---

# core/state

**Purpose**: State management and persistence for execution runs, tasks, and checkpoints.

## Overview

The state module provides:
- **Run state tracking** - Track execution runs from start to completion
- **Task state management** - Monitor individual task status and progress
- **Checkpoint system** - Time-travel debugging with ULID-based snapshots
- **Audit trail** - Append-only JSONL logs of all state transitions

## Key Files

- **`db.py`** - SQLite database operations for run/task state
- **`run_manager.py`** - High-level run state management
- **`checkpoint.py`** - Checkpoint creation and restoration
- **`audit_log.py`** - Append-only event logging

## Dependencies

**Depends on:**
- `sqlite3` (standard library)
- `json` (standard library)
- `python-ulid` (optional, for ULID generation)

**Used by:**
- `core/engine/` - For tracking execution state
- `core/bootstrap/` - For bootstrap state
- `core/engine/resilience/` - For failure tracking
- `core/engine/monitoring/` - For progress metrics

## Database Schema

### runs table
```sql
CREATE TABLE runs (
    id TEXT PRIMARY KEY,           -- ULID-based run identifier
    workflow_id TEXT,              -- Associated workflow
    status TEXT,                   -- PENDING, RUNNING, COMPLETED, FAILED
    started_at TIMESTAMP,          -- Start time
    completed_at TIMESTAMP,        -- End time (NULL if running)
    total_tasks INTEGER,           -- Total number of tasks
    completed_tasks INTEGER,       -- Completed task count
    failed_tasks INTEGER,          -- Failed task count
    metadata JSON                  -- Additional run metadata
);
```

### tasks table
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,           -- Task identifier
    run_id TEXT,                   -- Associated run
    status TEXT,                   -- PENDING, SCHEDULED, RUNNING, COMPLETED, FAILED
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration REAL,                 -- Execution time in seconds
    retries INTEGER,               -- Retry count
    result JSON,                   -- Execution result
    error TEXT,                    -- Error message if failed
    FOREIGN KEY (run_id) REFERENCES runs(id)
);
```

### checkpoints table
```sql
CREATE TABLE checkpoints (
    id TEXT PRIMARY KEY,           -- ULID identifier (sortable by time)
    run_id TEXT,
    created_at TIMESTAMP,
    state_snapshot JSON,           -- Complete state at checkpoint
    FOREIGN KEY (run_id) REFERENCES runs(id)
);
```

## Run Manager

High-level interface for managing execution runs.

### Usage
```python
from core.state import RunManager

manager = RunManager()

# Create new run
run_id = manager.create_run(
    workflow_id="wf-123",
    total_tasks=10
)

# Update status
manager.update_run_status(run_id, "RUNNING")

# Track progress
manager.update_run_progress(
    run_id,
    completed_tasks=5,
    failed_tasks=1
)

# Complete run
manager.complete_run(
    run_id,
    status="COMPLETED",
    metadata={"duration": 120.5}
)

# Get run info
run = manager.get_run(run_id)
print(f"Status: {run.status}")
print(f"Progress: {run.completed_tasks}/{run.total_tasks}")
```

### Run States

```
PENDING → RUNNING → COMPLETED
            ↓
          FAILED
            ↓
        RETRYING → COMPLETED
                 ↓
               FAILED (terminal)
```

## Task State Management

```python
from core.state import TaskManager

manager = TaskManager()

# Create task
manager.create_task(
    run_id="run-123",
    task_id="task-1",
    status="PENDING"
)

# Update task status
manager.update_task_status(
    run_id="run-123",
    task_id="task-1",
    status="RUNNING"
)

# Complete task
manager.complete_task(
    run_id="run-123",
    task_id="task-1",
    result={"output": "Success"},
    duration=5.2
)

# Fail task
manager.fail_task(
    run_id="run-123",
    task_id="task-1",
    error="Execution timeout",
    retries=2
)

# Get task info
task = manager.get_task("run-123", "task-1")
```

### Task States

```
PENDING → SCHEDULED → RUNNING → COMPLETED
            ↓           ↓
          BLOCKED     FAILED
                        ↓
                    RETRYING → COMPLETED
                               ↓
                             FAILED (terminal)
```

## Checkpoint System

ULID-based snapshots for time-travel debugging and recovery.

### ULID Format
```
01ARZ3NDEKTSV4RRFFQ69G5FAV
|------------|----------|
   Timestamp    Randomness
   (48 bits)    (80 bits)

- Lexicographically sortable
- Timestamp embedded
- Collision-resistant
- URL-safe
```

### Usage
```python
from core.state import CheckpointManager

manager = CheckpointManager()

# Create checkpoint
state_data = {
    "run_id": "run-123",
    "completed_tasks": ["task-1", "task-2"],
    "current_phase": "implement",
    "metadata": {...}
}

checkpoint_id = manager.create_checkpoint(
    run_id="run-123",
    state=state_data
)
print(f"Checkpoint: {checkpoint_id}")
# Output: 01ARZ3NDEKTSV4RRFFQ69G5FAV

# List checkpoints for run (sorted by time)
checkpoints = manager.list_checkpoints("run-123")
for cp in checkpoints:
    print(f"{cp.id} - {cp.created_at}")

# Restore from checkpoint
restored_state = manager.restore_checkpoint(checkpoint_id)

# Get checkpoint at specific time
checkpoint = manager.get_checkpoint_at_time(
    run_id="run-123",
    timestamp="2024-11-23T10:30:00Z"
)
```

### Checkpoint Strategy
- **Automatic**: Created at phase boundaries
- **Manual**: Created by user request
- **Failure**: Created on task failure for recovery
- **Periodic**: Created every N minutes

## Audit Log

Append-only JSONL logging for complete execution history.

### Log Format
```jsonl
{"timestamp": "2024-11-23T10:00:00Z", "event": "run_started", "run_id": "run-123", "workflow_id": "wf-123"}
{"timestamp": "2024-11-23T10:00:01Z", "event": "task_started", "run_id": "run-123", "task_id": "task-1"}
{"timestamp": "2024-11-23T10:00:06Z", "event": "task_completed", "run_id": "run-123", "task_id": "task-1", "duration": 5.2}
{"timestamp": "2024-11-23T10:00:07Z", "event": "task_started", "run_id": "run-123", "task_id": "task-2"}
{"timestamp": "2024-11-23T10:00:12Z", "event": "task_failed", "run_id": "run-123", "task_id": "task-2", "error": "timeout"}
{"timestamp": "2024-11-23T10:00:13Z", "event": "task_retrying", "run_id": "run-123", "task_id": "task-2", "attempt": 2}
```

### Usage
```python
from core.state import AuditLog

log = AuditLog("logs/run-123.jsonl")

# Log event
log.write({
    "event": "task_started",
    "run_id": "run-123",
    "task_id": "task-1",
    "metadata": {...}
})

# Read events
events = log.read_all()
for event in events:
    print(f"{event['timestamp']}: {event['event']}")

# Filter events
task_events = log.filter(task_id="task-1")
failures = log.filter(event="task_failed")
```

### Event Types
- `run_started`, `run_completed`, `run_failed`
- `task_started`, `task_completed`, `task_failed`, `task_retrying`
- `checkpoint_created`, `checkpoint_restored`
- `error_detected`, `error_recovered`
- `tool_invoked`, `tool_completed`, `tool_failed`

## Database Operations

### Initialization
```python
from core.state.db import init_db

# Initialize database with schema
init_db("state.db")
```

### Connection Management
```python
from core.state.db import get_connection

with get_connection("state.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE status = ?", ("RUNNING",))
    rows = cursor.fetchall()
```

### Migrations
```python
from core.state.db import migrate_db

# Apply schema migrations
migrate_db("state.db", target_version=2)
```

## State Queries

### Common Queries
```python
from core.state import RunManager

manager = RunManager()

# Get all running workflows
running = manager.get_runs_by_status("RUNNING")

# Get runs for a workflow
runs = manager.get_runs_by_workflow("wf-123")

# Get failed tasks
failed_tasks = manager.get_failed_tasks("run-123")

# Get run statistics
stats = manager.get_run_stats("run-123")
# Returns: {
#   "total_tasks": 10,
#   "completed": 7,
#   "failed": 2,
#   "pending": 1,
#   "duration": 125.5
# }
```

## Recovery

### Recovering from Failure
```python
from core.state import RunManager, CheckpointManager

run_manager = RunManager()
checkpoint_manager = CheckpointManager()

# Find failed run
run = run_manager.get_run("run-123")

if run.status == "FAILED":
    # Get last successful checkpoint
    checkpoints = checkpoint_manager.list_checkpoints(run.id)
    last_good = checkpoints[-1]
    
    # Restore state
    state = checkpoint_manager.restore_checkpoint(last_good.id)
    
    # Resume execution from checkpoint
    resume_from_checkpoint(state)
```

## Performance Considerations

### Indexing
```sql
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_workflow ON runs(workflow_id);
CREATE INDEX idx_tasks_run ON tasks(run_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_checkpoints_run ON checkpoints(run_id);
```

### Batch Operations
```python
# Batch insert tasks
manager.create_tasks_batch([
    {"run_id": "run-123", "task_id": "task-1", "status": "PENDING"},
    {"run_id": "run-123", "task_id": "task-2", "status": "PENDING"},
    # ... more tasks
])

# Batch update
manager.update_tasks_batch([
    {"run_id": "run-123", "task_id": "task-1", "status": "COMPLETED"},
    {"run_id": "run-123", "task_id": "task-2", "status": "COMPLETED"},
])
```

### Vacuum & Cleanup
```python
# Remove old completed runs
manager.cleanup_old_runs(days=30)

# Vacuum database
manager.vacuum()
```

## Testing

```bash
# Run state tests
pytest tests/state/ -v

# Specific tests
pytest tests/state/test_run_manager.py -v
pytest tests/state/test_checkpoint.py -v
pytest tests/state/test_audit_log.py -v
```

## References

- **Architecture**: `ARCHITECTURE.md` (State Management section)
- **Schemas**: `schema/run_state.v1.json`, `schema/checkpoint.v1.json`
- **Engine usage**: `core/engine/README.md`
