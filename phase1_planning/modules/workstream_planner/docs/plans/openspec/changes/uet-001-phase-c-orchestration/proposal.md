---
doc_id: DOC-GUIDE-PROPOSAL-1511
---

# Phase C: Orchestration - UET Implementation

**Change ID**: uet-001-phase-c-orchestration
**Parent**: uet-001-complete-implementation
**Depends On**: uet-001-phase-b-patch-system
**Type**: Execution Enhancement
**Priority**: MEDIUM
**Estimated Duration**: 2-3 weeks
**Effort**: 30 hours

---

## Problem Statement

Current scheduler is sequential or simple parallel - no true DAG-based dependency resolution. Missing:

- **DAG Scheduler**: No topological sort for parallel execution
- **Merge Orchestration**: No deterministic merge order
- **Context Management**: Token estimation exists but lacks pruning/chunking
- **Integration Worker**: Basic merge conflict detection, needs full orchestration

---

## Requirements

**DAG Scheduler**:
- SHALL parse task dependencies from workstream specs
- SHALL perform topological sort for execution order
- SHALL detect cycles (prevent circular dependencies)
- SHALL execute independent tasks in parallel
- SHALL support opt-in via `parallel_strategy: dag` config flag

**Merge Orchestration**:
- SHALL implement deterministic merge order (priority → dependency → age)
- SHALL detect merge conflicts via `E_MERGE_CONFLICT` event
- SHALL rollback on merge failure
- SHALL support merge preview mode

**Context Manager**:
- SHALL estimate tokens per model (GPT-4, Claude, etc.)
- SHALL implement intelligent pruning (remove boilerplate)
- SHALL implement summarization (compress large files)
- SHALL implement chunking for tasks exceeding token limits

---

## Implementation Tasks

### DAG Scheduler (12 hours)

```python
class DAGScheduler:
    def build_dag(self, workstream: Dict) -> nx.DiGraph:
        """Build dependency graph from workstream tasks."""
        graph = nx.DiGraph()
        for task in workstream['tasks']:
            graph.add_node(task['id'])
            for dep in task.get('depends_on', []):
                graph.add_edge(dep, task['id'])

        # Cycle detection
        if not nx.is_directed_acyclic_graph(graph):
            raise CyclicDependencyError("Tasks have circular dependencies")

        return graph

    def execute(self, graph: nx.DiGraph):
        """Execute tasks in topological order with parallelism."""
        for layer in nx.topological_generations(graph):
            # Execute all tasks in this layer in parallel
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self._run_task, task)
                          for task in layer]
                wait(futures)
```

### Merge Orchestration (10 hours)

### Context Manager (8 hours)

---

## Success Criteria

- ✅ DAG scheduler executing parallel tasks correctly
- ✅ Cycle detection preventing circular dependencies
- ✅ Merge orchestration handling conflicts gracefully
- ✅ Context manager preventing token overflow

---

## Dependencies

**Requires**: Phase B complete (patch system needed)
**Blocks**: Phase E (compensation needs orchestration)

---

## Files Created

- `core/engine/scheduler_dag.py`
- `core/engine/merge_strategy.py`
- `core/engine/context_manager.py`
- `docs/DAG_SCHEDULER.md`
