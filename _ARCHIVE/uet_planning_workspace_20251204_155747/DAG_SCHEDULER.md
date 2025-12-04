---
doc_id: DOC-GUIDE-DAG-SCHEDULER-747
---

# UET V2 DAG Scheduler & Task Dependencies

**Purpose**: Define DAG-based task scheduling with dependency resolution
**Status**: DRAFT
**Last Updated**: 2025-11-23

---

## Table of Contents

- [DAG Scheduler Overview](#dag-scheduler-overview)
- [Task Dependency Model](#task-dependency-model)
- [Dependency Resolution Algorithm](#dependency-resolution-algorithm)
- [Parallel Execution Strategy](#parallel-execution-strategy)
- [Deadlock Detection](#deadlock-detection)
- [Task Priority & Ordering](#task-priority--ordering)

---

## DAG Scheduler Overview

### Purpose

Replace sequential task execution with **Directed Acyclic Graph (DAG)** scheduling to enable:
- Parallel task execution (multiple workers)
- Dependency-aware ordering
- Deadlock detection
- Dynamic task addition (feedback loop)

### Architecture

```
WorkstreamBundle
    ↓
DAG Scheduler
    ├─> Dependency Resolver (builds DAG)
    ├─> Topological Sort (execution order)
    ├─> Worker Pool (parallel execution)
    └─> Integration Worker (merge results)
```

---

## Task Dependency Model

### Dependency Types

#### 1. **Direct Dependencies** (`depends_on`)

Tasks explicitly depend on other tasks completing first.

```json
{
  "step_id": "WS-007-003",
  "name": "Run unit tests",
  "depends_on": ["WS-007-001", "WS-007-002"],
  "description": "Cannot run tests until code is written (001) and linted (002)"
}
```

**Visualization**:
```
WS-007-001 (Write code)
    ↓
WS-007-002 (Lint code) ──┐
    ↓                    │
WS-007-003 (Run tests) ←─┘
```

#### 2. **Resource Dependencies** (`files`)

Tasks depend on files being created/modified by prior tasks.

```json
{
  "step_id": "WS-007-002",
  "files": ["core/engine/executor.py"],
  "depends_on": []  // Auto-inferred from file producer
}
```

**Auto-Inference**:
```python
# Task A produces file
{"step_id": "A", "files": ["core/executor.py"], "mode": "edit"}

# Task B reads same file → auto-dependency
{"step_id": "B", "files": ["core/executor.py"], "mode": "read"}

# Scheduler infers: B.depends_on = ["A"]
```

#### 3. **Gate Dependencies** (`gates`)

Tasks blocked until test gates pass.

```json
{
  "step_id": "WS-007-004",
  "name": "Deploy to staging",
  "gates": ["GATE_UNIT", "GATE_INTEGRATION"],
  "description": "Cannot deploy until all tests pass"
}
```

**Blocking Behavior**:
```
GATE_UNIT (PENDING) → Task WS-007-004 (BLOCKED)
GATE_UNIT (PASSED)  → Task WS-007-004 (READY)
```

#### 4. **Phase Dependencies** (`phase_id`)

Tasks within same phase execute in parallel; next phase waits for all tasks.

```json
{
  "phases": [
    {
      "phase_id": "PH-001-IMPLEMENT",
      "steps": ["A", "B", "C"]  // Parallel
    },
    {
      "phase_id": "PH-002-TEST",
      "steps": ["D", "E"]  // Wait for PH-001 complete
    }
  ]
}
```

**Phase Boundary**:
```
Phase 1: A, B, C (all complete)
    ↓ (phase boundary = synchronization point)
Phase 2: D, E (start)
```

---

## Dependency Resolution Algorithm

### Step 1: Build Dependency Graph

```python
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class TaskNode:
    step_id: str
    depends_on: List[str]  # Explicit dependencies
    files: List[str]       # File dependencies
    gates: List[str]       # Gate dependencies
    phase_id: str

class DependencyResolver:
    def build_dag(self, workstream: dict) -> Dict[str, TaskNode]:
        """Build DAG from workstream steps."""
        nodes = {}
        file_producers = {}  # file -> step_id mapping

        # First pass: Create nodes
        for step in workstream['steps']:
            node = TaskNode(
                step_id=step['step_id'],
                depends_on=step.get('depends_on', []),
                files=step.get('files', []),
                gates=step.get('gates', []),
                phase_id=step.get('phase_id', 'default')
            )
            nodes[step['step_id']] = node

            # Track file producers
            for file in step.get('files', []):
                if step.get('mode') in ['edit', 'create']:
                    file_producers[file] = step['step_id']

        # Second pass: Infer file dependencies
        for step_id, node in nodes.items():
            for file in node.files:
                if file in file_producers:
                    producer = file_producers[file]
                    if producer != step_id and producer not in node.depends_on:
                        node.depends_on.append(producer)

        # Third pass: Add phase dependencies
        phases = self._group_by_phase(nodes)
        for i, (phase_id, steps) in enumerate(phases.items()):
            if i > 0:
                prev_phase_steps = list(phases.values())[i-1]
                for step_id in steps:
                    for prev_step in prev_phase_steps:
                        if prev_step not in nodes[step_id].depends_on:
                            nodes[step_id].depends_on.append(prev_step)

        return nodes

    def _group_by_phase(self, nodes: Dict[str, TaskNode]) -> Dict[str, List[str]]:
        """Group tasks by phase_id."""
        phases = {}
        for step_id, node in nodes.items():
            phase = node.phase_id
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(step_id)
        return phases
```

### Step 2: Topological Sort

```python
class TopologicalSorter:
    def sort(self, dag: Dict[str, TaskNode]) -> List[List[str]]:
        """
        Return tasks in topological order (levels for parallelism).

        Returns:
            List of levels, where each level can execute in parallel.
            Example: [["A"], ["B", "C"], ["D"]]
        """
        # Calculate in-degree (number of dependencies)
        in_degree = {step_id: len(node.depends_on) for step_id, node in dag.items()}

        levels = []
        visited = set()

        while len(visited) < len(dag):
            # Find all tasks with in_degree = 0 (ready to execute)
            ready = [
                step_id for step_id, degree in in_degree.items()
                if degree == 0 and step_id not in visited
            ]

            if not ready:
                # Deadlock: circular dependency detected
                raise ValueError("Circular dependency detected in DAG")

            levels.append(ready)
            visited.update(ready)

            # Decrease in_degree for dependent tasks
            for step_id in ready:
                for other_id, other_node in dag.items():
                    if step_id in other_node.depends_on:
                        in_degree[other_id] -= 1

        return levels
```

### Step 3: Deadlock Detection

```python
class DeadlockDetector:
    def detect_cycles(self, dag: Dict[str, TaskNode]) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.

        Returns:
            List of cycles (each cycle is a list of step_ids).
        """
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(step_id: str, path: List[str]):
            visited.add(step_id)
            rec_stack.add(step_id)
            path.append(step_id)

            for dep in dag[step_id].depends_on:
                if dep not in visited:
                    dfs(dep, path.copy())
                elif dep in rec_stack:
                    # Cycle found
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])

            rec_stack.remove(step_id)

        for step_id in dag.keys():
            if step_id not in visited:
                dfs(step_id, [])

        return cycles
```

---

## Parallel Execution Strategy

### Level-Based Parallelism

```python
class DAGScheduler:
    def __init__(self, worker_pool: WorkerPool, max_parallel: int = 4):
        self.worker_pool = worker_pool
        self.max_parallel = max_parallel

    def execute(self, workstream: dict) -> RunResult:
        """Execute workstream using DAG scheduler."""
        # Build DAG
        resolver = DependencyResolver()
        dag = resolver.build_dag(workstream)

        # Check for cycles
        detector = DeadlockDetector()
        cycles = detector.detect_cycles(dag)
        if cycles:
            raise ValueError(f"Circular dependencies: {cycles}")

        # Sort topologically
        sorter = TopologicalSorter()
        levels = sorter.sort(dag)

        # Execute level by level
        results = {}
        for level_idx, level in enumerate(levels):
            print(f"Executing level {level_idx}: {len(level)} tasks")

            # Execute tasks in parallel (up to max_parallel)
            level_results = self._execute_level(level, dag)
            results.update(level_results)

            # Check if all tasks passed
            if not all(r.success for r in level_results.values()):
                # Level failed, stop execution
                raise ExecutionError(f"Level {level_idx} failed")

        return RunResult(success=True, results=results)

    def _execute_level(self, tasks: List[str], dag: Dict[str, TaskNode]) -> Dict[str, TaskResult]:
        """Execute tasks in parallel within a level."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self._execute_task, task_id, dag[task_id]): task_id
                for task_id in tasks
            }

            # Collect results
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    results[task_id] = future.result()
                except Exception as e:
                    results[task_id] = TaskResult(success=False, error=str(e))

        return results

    def _execute_task(self, task_id: str, node: TaskNode) -> TaskResult:
        """Execute a single task."""
        # Get idle worker
        worker = self.worker_pool.get_idle_worker(worker_type="code_edit")

        # Execute task
        result = worker.execute(task_id, node)

        # Return worker to pool
        self.worker_pool.return_worker(worker)

        return result
```

### Example: Parallel Execution

**Input Workstream**:
```json
{
  "steps": [
    {"step_id": "A", "depends_on": []},
    {"step_id": "B", "depends_on": ["A"]},
    {"step_id": "C", "depends_on": ["A"]},
    {"step_id": "D", "depends_on": ["B", "C"]}
  ]
}
```

**DAG Visualization**:
```
    A
   / \
  B   C
   \ /
    D
```

**Execution Levels**:
```
Level 0: [A]          (1 task, sequential)
Level 1: [B, C]       (2 tasks, parallel)
Level 2: [D]          (1 task, sequential)
```

**Timeline**:
```
Time: 0s  - Start A
Time: 2s  - A complete, start B and C (parallel)
Time: 5s  - B and C complete, start D
Time: 7s  - D complete, workstream done
```

---

## Task Priority & Ordering

### Priority Calculation

When multiple tasks are ready (in_degree=0), prioritize by:

```python
@dataclass
class TaskPriority:
    critical_path_length: int    # Longest path to end (higher = higher priority)
    dependency_count: int         # Number of tasks depending on this (higher = higher priority)
    file_contention: int          # Number of tasks touching same files (higher = lower priority)
    explicit_priority: int        # User-defined priority (1-10)

    def score(self) -> float:
        """Calculate priority score (higher = execute first)."""
        return (
            self.critical_path_length * 10 +
            self.dependency_count * 5 +
            self.explicit_priority * 20 -
            self.file_contention * 3
        )

class PriorityCalculator:
    def calculate_priorities(self, dag: Dict[str, TaskNode]) -> Dict[str, TaskPriority]:
        """Calculate priority for each task."""
        priorities = {}

        for step_id, node in dag.items():
            priorities[step_id] = TaskPriority(
                critical_path_length=self._calc_critical_path(step_id, dag),
                dependency_count=self._count_dependents(step_id, dag),
                file_contention=self._calc_file_contention(step_id, dag),
                explicit_priority=node.priority if hasattr(node, 'priority') else 5
            )

        return priorities

    def _calc_critical_path(self, step_id: str, dag: Dict[str, TaskNode]) -> int:
        """Calculate longest path from this task to end."""
        if not dag[step_id].depends_on:
            return 0

        max_depth = 0
        for dep in dag[step_id].depends_on:
            depth = 1 + self._calc_critical_path(dep, dag)
            max_depth = max(max_depth, depth)

        return max_depth

    def _count_dependents(self, step_id: str, dag: Dict[str, TaskNode]) -> int:
        """Count how many tasks depend on this task."""
        count = 0
        for other_id, other_node in dag.items():
            if step_id in other_node.depends_on:
                count += 1
        return count

    def _calc_file_contention(self, step_id: str, dag: Dict[str, TaskNode]) -> int:
        """Count how many other tasks touch the same files."""
        my_files = set(dag[step_id].files)
        count = 0
        for other_id, other_node in dag.items():
            if other_id != step_id:
                other_files = set(other_node.files)
                if my_files & other_files:  # Intersection
                    count += 1
        return count
```

### Priority-Based Ordering

```python
class DAGScheduler:
    def _execute_level(self, tasks: List[str], dag: Dict[str, TaskNode]) -> Dict[str, TaskResult]:
        """Execute tasks in priority order within a level."""
        # Calculate priorities
        calculator = PriorityCalculator()
        priorities = calculator.calculate_priorities(dag)

        # Sort by priority (descending)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: priorities[t].score(),
            reverse=True
        )

        # Execute in priority order (still parallel, but start high-priority first)
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            futures = {}
            for task_id in sorted_tasks:
                future = executor.submit(self._execute_task, task_id, dag[task_id])
                futures[future] = task_id

            for future in as_completed(futures):
                task_id = futures[future]
                results[task_id] = future.result()

        return results
```

---

## Dynamic Task Addition (Feedback Loop)

### Adding Tasks During Execution

```python
class DAGScheduler:
    def add_fix_task(self, failed_task_id: str, error_msg: str) -> str:
        """
        Add a fix task dynamically when a task fails.

        Returns:
            New task ID
        """
        fix_task_id = f"fix-{failed_task_id}"

        # Create fix task node
        fix_node = TaskNode(
            step_id=fix_task_id,
            depends_on=[],  # No dependencies (can start immediately)
            files=self.dag[failed_task_id].files,  # Same files as failed task
            gates=[],
            phase_id=self.dag[failed_task_id].phase_id
        )

        # Add to DAG
        self.dag[fix_task_id] = fix_node

        # Update failed task to depend on fix
        self.dag[failed_task_id].depends_on.append(fix_task_id)

        # Recalculate topological order
        sorter = TopologicalSorter()
        self.levels = sorter.sort(self.dag)

        return fix_task_id
```

---

## Workstream Examples

### Example 1: Simple Linear

```json
{
  "steps": [
    {"step_id": "A", "name": "Write code", "depends_on": []},
    {"step_id": "B", "name": "Lint code", "depends_on": ["A"]},
    {"step_id": "C", "name": "Run tests", "depends_on": ["B"]}
  ]
}
```

**DAG**: `A → B → C` (sequential)
**Levels**: `[[A], [B], [C]]`

### Example 2: Parallel Branches

```json
{
  "steps": [
    {"step_id": "A", "name": "Write executor.py", "depends_on": []},
    {"step_id": "B", "name": "Write scheduler.py", "depends_on": []},
    {"step_id": "C", "name": "Write tests", "depends_on": ["A", "B"]}
  ]
}
```

**DAG**:
```
A  B
 \/
  C
```
**Levels**: `[[A, B], [C]]` (A and B parallel)

### Example 3: Diamond Pattern

```json
{
  "steps": [
    {"step_id": "A", "name": "Setup", "depends_on": []},
    {"step_id": "B", "name": "Feature 1", "depends_on": ["A"]},
    {"step_id": "C", "name": "Feature 2", "depends_on": ["A"]},
    {"step_id": "D", "name": "Integration", "depends_on": ["B", "C"]}
  ]
}
```

**DAG**:
```
    A
   / \
  B   C
   \ /
    D
```
**Levels**: `[[A], [B, C], [D]]`

### Example 4: Complex Multi-Phase

```json
{
  "phases": [
    {
      "phase_id": "PH-001-IMPLEMENT",
      "steps": [
        {"step_id": "A", "files": ["core/executor.py"], "depends_on": []},
        {"step_id": "B", "files": ["core/scheduler.py"], "depends_on": []},
        {"step_id": "C", "files": ["core/router.py"], "depends_on": []}
      ]
    },
    {
      "phase_id": "PH-002-TEST",
      "gates": ["GATE_LINT"],
      "steps": [
        {"step_id": "D", "files": ["tests/test_executor.py"], "depends_on": []},
        {"step_id": "E", "files": ["tests/test_scheduler.py"], "depends_on": []}
      ]
    }
  ]
}
```

**DAG**:
```
A  B  C  (Phase 1, parallel)
 \ | /
   ↓ (phase boundary)
  D  E  (Phase 2, parallel after GATE_LINT passes)
```

**Levels**: `[[A, B, C], [GATE_LINT], [D, E]]`

---

## Database Schema

### Task Execution Tracking

```sql
CREATE TABLE IF NOT EXISTS task_executions (
    execution_id TEXT PRIMARY KEY,
    step_id TEXT NOT NULL,
    run_id INTEGER NOT NULL,
    level INTEGER NOT NULL,           -- Which level in topological sort
    priority_score REAL NOT NULL,     -- Calculated priority
    state TEXT NOT NULL CHECK(state IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'BLOCKED')),
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE INDEX idx_task_executions_run ON task_executions(run_id);
CREATE INDEX idx_task_executions_state ON task_executions(state);
CREATE INDEX idx_task_executions_level ON task_executions(level);
```

---

## Testing Strategy

### Unit Tests

```python
def test_dependency_resolver_builds_dag():
    workstream = {
        "steps": [
            {"step_id": "A", "depends_on": []},
            {"step_id": "B", "depends_on": ["A"]}
        ]
    }
    resolver = DependencyResolver()
    dag = resolver.build_dag(workstream)

    assert len(dag) == 2
    assert "A" in dag["B"].depends_on

def test_topological_sort_correct_order():
    dag = {
        "A": TaskNode("A", [], [], [], "ph1"),
        "B": TaskNode("B", ["A"], [], [], "ph1"),
        "C": TaskNode("C", ["B"], [], [], "ph1")
    }
    sorter = TopologicalSorter()
    levels = sorter.sort(dag)

    assert levels == [["A"], ["B"], ["C"]]

def test_deadlock_detector_finds_cycle():
    dag = {
        "A": TaskNode("A", ["B"], [], [], "ph1"),
        "B": TaskNode("B", ["A"], [], [], "ph1")  # Circular!
    }
    detector = DeadlockDetector()
    cycles = detector.detect_cycles(dag)

    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}
```

---

## References

- **Component Contracts**: [COMPONENT_CONTRACTS.md](COMPONENT_CONTRACTS.md)
- **State Machines**: [STATE_MACHINES.md](STATE_MACHINES.md)
- **Integration Points**: [INTEGRATION_POINTS.md](INTEGRATION_POINTS.md)

---

**Last Updated**: 2025-11-23
**Next Review**: Before Phase A starts
