# Execution Model Overview

## Purpose
This document provides a high-level overview of the orchestration execution model, describing how tasks flow through the system from definition to completion.

## Architecture

### Components

```
┌─────────────────┐
│   Orchestrator  │ ← Entry point, coordinates all components
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│Schedu-│ │  Workers  │ ← Execute tasks
│ler    │ └───────────┘
└───┬───┘
    │
┌───▼────────┐
│ State Mgr  │ ← Maintains .state/ files
└────────────┘
```

#### Orchestrator
- **Purpose**: Main coordination component
- **Responsibilities**:
  - Accept workstream definitions
  - Initialize workstream state
  - Coordinate scheduler and workers
  - Handle workstream lifecycle
- **Location**: `core/engine/orchestrator.py`

#### Scheduler
- **Purpose**: Task scheduling and dependency resolution
- **Responsibilities**:
  - Build DAG from task dependencies
  - Compute execution plan (stages, parallelism)
  - Calculate critical path
  - Assign tasks to workers based on capabilities
- **Location**: `core/engine/scheduler.py`

#### Workers
- **Purpose**: Task execution
- **Responsibilities**:
  - Register capabilities with orchestrator
  - Execute assigned tasks
  - Report progress and results
  - Handle timeouts and retries
- **Types**:
  - AiderWorker: Code editing tasks
  - PytestWorker: Test execution
  - LintWorker: Static analysis
  - CustomWorker: User-defined tasks

#### State Manager
- **Purpose**: State persistence and querying
- **Responsibilities**:
  - Maintain `.state/current.json` atomically
  - Append to `.state/transitions.jsonl`
  - Generate index files
  - Provide state query API
- **Location**: `core/state/`

## Data Flow

### Task Lifecycle

```
1. Definition
   └─> Task JSON created in tasks/{workstream_id}/{task_id}.json

2. Scheduling
   └─> Scheduler builds DAG, creates execution plan
   └─> Task moves to 'queued' state

3. Execution
   └─> Worker picks up task (state: 'running')
   └─> Worker executes command within timeout
   └─> Worker reports result

4. Validation
   └─> Post-execution validation runs
   └─> State moves to 'validating'

5. Completion
   └─> Task marked 'completed' or 'failed'
   └─> Dependent tasks unblocked
```

### State Updates

All state changes flow through State Manager:

```
Component → State Manager → Atomic Write → Index Update → Event Log
```

This ensures:
- No partial state visible to observers
- Complete audit trail in transitions.jsonl
- Indices stay synchronized with current state

## Performance Characteristics

### Scalability
- **Task parallelism**: Limited by worker count and resource availability
- **Worker scalability**: Workers can run on separate processes/machines
- **State I/O**: Optimized for frequent small updates (<1ms typical)

### Latency
- **Task scheduling**: O(n log n) where n = task count
- **State query**: O(1) for current state, O(log n) for index lookups
- **Worker assignment**: O(w × c) where w = workers, c = capabilities

### Throughput
- **Tasks/second**: 10-100 depending on task complexity
- **State updates/second**: 1000+ (limited by disk I/O)
- **Concurrent workstreams**: 10-50 recommended

## External Dependencies

### Required
- **Git**: Worktree creation and management
- **SQLite**: State database (optional, uses JSON files if unavailable)
- **Python 3.10+**: Runtime environment

### Optional
- **Aider**: For AI-assisted code editing tasks
- **Pytest**: For test execution tasks
- **Ruff/Black**: For linting tasks

### Network
- **No network required**: System operates entirely offline
- **AI tools**: May require network (Aider, OpenAI API)

## Configuration

### Orchestrator Config
```json
{
  "max_parallel_workstreams": 10,
  "max_parallel_tasks_per_workstream": 5,
  "state_update_interval_seconds": 1,
  "worker_health_check_interval_seconds": 30
}
```

### Worker Config
```json
{
  "worker_id": "worker-001",
  "capabilities": ["aider", "pytest"],
  "max_concurrent_tasks": 3,
  "heartbeat_interval_seconds": 10
}
```

## Error Handling

### Levels
1. **Task-level**: Retries with exponential backoff
2. **Worker-level**: Worker marked unresponsive, tasks reassigned
3. **Workstream-level**: Workstream marked failed, state preserved
4. **System-level**: Orchestrator logs error, continues with other workstreams

See `docs/failure_modes/` for detailed failure mode documentation.

## Monitoring

### Metrics
Exported to `.state/metrics.json` every 60 seconds:
- Active workstreams
- Task completion rates
- Worker utilization
- Error rates by type

### Health Checks
- Worker heartbeats every 10 seconds
- State file integrity checks
- Resource availability monitoring

## See Also
- [State Machine](./STATE_MACHINE.md): State transitions
- [Scheduling](./SCHEDULING.md): DAG and execution planning
- [Workers](./WORKERS.md): Worker lifecycle
- [Recovery](./RECOVERY.md): Failure recovery procedures
