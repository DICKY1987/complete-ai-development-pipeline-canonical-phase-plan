---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1596
---

# core/engine

**Purpose**: Task orchestration engine providing scheduling, routing, resilient execution, and real-time monitoring for autonomous workflows.

## Overview

The engine is the heart of UET, responsible for:
1. **Routing** - Matching tasks to capable tools
2. **Scheduling** - Resolving dependencies and creating execution DAGs
3. **Execution** - Running tasks with fault tolerance
4. **Monitoring** - Tracking progress and calculating metrics

## Key Files

- **`router.py`** - Routes tasks to appropriate tools based on capabilities
- **`scheduler.py`** - Dependency resolution and topological task ordering
- **`executor.py`** - Coordinates task execution across tool adapters
- **`orchestrator.py`** - High-level workflow orchestration
- **`monitoring/`** - Progress tracking and metrics collection
- **`resilience/`** - Circuit breakers, retry logic, fault tolerance

## Dependencies

**Depends on:**
- `core/adapters/` - For tool execution
- `core/engine/resilience/` - For fault tolerance patterns
- `core/engine/monitoring/` - For progress tracking
- `core/state/` - For run state persistence
- `schema/` - For task_spec.v1.json and phase_spec.v1.json

**Used by:**
- `core/bootstrap/` - For executing bootstrap workflows
- External orchestration systems
- CLI entry points

## Architecture

```
┌─────────────────────────────────────┐
│       Orchestrator                  │
│  (High-level workflow control)      │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬─────────────┐
    ▼                 ▼              ▼             ▼
┌─────────┐   ┌──────────────┐  ┌─────────┐  ┌─────────┐
│ Router  │   │  Scheduler   │  │Executor │  │ Monitor │
│         │   │              │  │         │  │         │
│ Task→   │   │ DAG creation │  │ Runs    │  │ Tracks  │
│ Tool    │   │ Topo sort    │  │ tasks   │  │progress │
└─────────┘   └──────────────┘  └─────────┘  └─────────┘
     │                │               │            │
     └────────────────┴───────────────┴────────────┘
                      │
              ┌───────┴────────┐
              ▼                ▼
       ┌──────────┐    ┌──────────────┐
       │ Adapters │    │  Resilience  │
       │          │    │  (Circuit    │
       │ Subprocess│    │  Breaker,   │
       │ API      │    │  Retry)     │
       │ Custom   │    └──────────────┘
       └──────────┘
```

## Task Router

Routes tasks to tools based on capability matching.

### Usage
```python
from core.engine.router import TaskRouter

router = TaskRouter("router_config.json")

# Find tools for a task
request = ExecutionRequest(
    action="code_edit",
    domain="python",
    context={"file": "main.py"}
)

capable_tools = router.find_capable_tools(request)
# Returns: ["aider", "cursor"]

# Get best tool (first match by priority)
best_tool = router.route(request)
# Returns: "aider"
```

### Routing Logic
1. Match task domain with tool capabilities
2. Match task action with tool capabilities
3. Apply priority ordering (first in config = highest priority)
4. Return ordered list of capable tools

## Task Scheduler

Resolves dependencies and creates execution order.

### Usage
```python
from core.engine.scheduler import ExecutionScheduler, Task

scheduler = ExecutionScheduler()

# Define tasks with dependencies
tasks = [
    Task(id='analyze', action='analysis'),
    Task(id='implement', action='code_edit', depends_on=['analyze']),
    Task(id='test', action='testing', depends_on=['implement']),
    Task(id='lint', action='linting', depends_on=['implement']),
    Task(id='integrate', action='integration', depends_on=['test', 'lint'])
]

scheduler.add_tasks(tasks)

# Get execution order (topological sort)
order = scheduler.get_execution_order()
# Returns: ['analyze', 'implement', 'test', 'lint', 'integrate']

# Get parallel batches (max 3 concurrent)
batches = scheduler.get_parallel_batches(max_parallel=3)
# Returns: [
#   ['analyze'],
#   ['implement'],
#   ['test', 'lint'],
#   ['integrate']
# ]

# Detect circular dependencies
cycle = scheduler.detect_cycles()
if cycle:
    print(f"Circular dependency: {' -> '.join(cycle)}")
```

### Scheduling Algorithm
1. Build dependency graph (adjacency list)
2. Perform topological sort (Kahn's algorithm)
3. Detect cycles (DFS with visited tracking)
4. Generate parallel batches (level-based grouping)

### Complexity
- Dependency resolution: O(V + E) where V=tasks, E=dependencies
- Cycle detection: O(V + E)
- Parallel batching: O(V)

## Executor

Coordinates task execution with resilience patterns.

### Usage
```python
from core.engine.executor import Executor
from core.engine.resilience import ResilientExecutor

executor = Executor()

# Basic execution
result = executor.execute_task(task, adapter)

# With resilience (recommended)
resilient = ResilientExecutor()
resilient.register_tool("aider", max_retries=3, failure_threshold=5)

result = resilient.execute("aider", lambda: task.run())
```

### Execution Flow
1. Select tool via router
2. Get adapter for tool
3. Wrap execution in resilience layer
4. Update state before/after execution
5. Track progress in monitoring
6. Handle errors with retry logic

## Orchestrator

High-level workflow coordination.

### Usage
```python
from core.engine.orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    router_config="router_config.json",
    state_db="run_state.db"
)

# Define workflow
workflow = {
    "phases": [
        {
            "name": "analyze",
            "workstreams": [
                {"name": "code_analysis", "tasks": [...]}
            ]
        },
        {
            "name": "implement",
            "depends_on": ["analyze"],
            "workstreams": [...]
        }
    ]
}

# Execute workflow
run_id = orchestrator.execute_workflow(workflow)

# Get status
status = orchestrator.get_run_status(run_id)
print(f"Progress: {status.completion_percent}%")
```

## Monitoring

Real-time progress tracking and metrics.

See: `core/engine/monitoring/README.md`

**Key features:**
- Task-level progress tracking
- Run-level metrics aggregation
- ETA calculation
- Real-time snapshots

## Resilience

Fault tolerance patterns for external tool execution.

See: `core/engine/resilience/README.md`

**Key features:**
- Circuit breaker pattern
- Exponential backoff retry
- Timeout handling
- Failure threshold tracking

## State Management

The engine persists state at multiple levels:

### Run State
```python
from core.state import RunManager

manager = RunManager()

# Create run
run_id = manager.create_run(workflow_id="wf-123")

# Update status
manager.update_run_status(run_id, "RUNNING")

# Track progress
manager.update_run_progress(
    run_id,
    completed_tasks=5,
    total_tasks=10
)

# Get run info
run = manager.get_run(run_id)
```

### Task State
```python
# Task states: PENDING, SCHEDULED, RUNNING, COMPLETED, FAILED, RETRYING

manager.create_task(run_id, task_id="task-1", status="PENDING")
manager.update_task_status(run_id, "task-1", "RUNNING")
manager.complete_task(run_id, "task-1", result_data={...})
```

## Error Handling

The engine handles errors at multiple levels:

### Task-level Errors
```python
try:
    result = executor.execute_task(task, adapter)
except TaskExecutionError as e:
    # Automatic retry if retries remaining
    # Log to audit trail
    # Update task state to FAILED
    # Continue with other tasks
```

### Run-level Errors
```python
try:
    orchestrator.execute_workflow(workflow)
except WorkflowExecutionError as e:
    # Determine if recoverable
    # Save checkpoint for recovery
    # Update run state to FAILED
    # Generate error report
```

## Performance Optimization

### Parallel Execution
```python
# Execute independent tasks concurrently
batches = scheduler.get_parallel_batches(max_parallel=4)

for batch in batches:
    # Run all tasks in batch concurrently
    with ThreadPoolExecutor(max_workers=len(batch)) as pool:
        futures = [pool.submit(execute_task, t) for t in batch]
        results = [f.result() for f in futures]
```

### Caching
```python
# Router caches capability lookups
router = TaskRouter("config.json", enable_cache=True)

# Scheduler caches dependency graphs
scheduler = ExecutionScheduler(cache_enabled=True)
```

### Lazy Loading
```python
# Load adapters on-demand
registry = AdapterRegistry("config.json", lazy_load=True)
adapter = registry.get("aider")  # Loaded on first access
```

## Testing

Test coverage: 92/92 tests passing

```bash
# Run engine tests
pytest tests/engine/ -v

# Specific components
pytest tests/engine/test_router.py -v
pytest tests/engine/test_scheduler.py -v
pytest tests/engine/test_executor.py -v

# Integration tests
pytest tests/engine/test_integration.py -v
```

## Common Patterns

### Pattern 1: Simple Linear Workflow
```python
tasks = [
    Task('step1', 'action1'),
    Task('step2', 'action2', depends_on=['step1']),
    Task('step3', 'action3', depends_on=['step2'])
]

scheduler.add_tasks(tasks)
order = scheduler.get_execution_order()
# Returns: ['step1', 'step2', 'step3']
```

### Pattern 2: Parallel Workflow
```python
tasks = [
    Task('analyze', 'analysis'),
    Task('lint', 'linting', depends_on=['analyze']),
    Task('test', 'testing', depends_on=['analyze']),
    Task('build', 'building', depends_on=['analyze']),
    Task('deploy', 'deployment', depends_on=['lint', 'test', 'build'])
]

batches = scheduler.get_parallel_batches(max_parallel=3)
# Returns: [
#   ['analyze'],
#   ['lint', 'test', 'build'],  # Parallel execution
#   ['deploy']
# ]
```

### Pattern 3: Conditional Execution
```python
# Route different tasks based on project type
if project_type == "python":
    tasks = [
        Task('lint', 'linting', tool='ruff'),
        Task('test', 'testing', tool='pytest')
    ]
else:
    tasks = [
        Task('lint', 'linting', tool='eslint'),
        Task('test', 'testing', tool='jest')
    ]
```

## References

- **Specification**: `specs/UET_PHASE_SPEC_MASTER.md`
- **Task routing**: `specs/UET_TASK_ROUTING_SPEC.md`
- **Schemas**: `schema/task_spec.v1.json`, `schema/phase_spec.v1.json`
- **Resilience**: `core/engine/resilience/README.md`
- **Monitoring**: `core/engine/monitoring/README.md`
