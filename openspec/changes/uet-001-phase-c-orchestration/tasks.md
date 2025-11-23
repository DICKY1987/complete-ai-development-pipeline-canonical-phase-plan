# Phase C Tasks - Orchestration

## DAG Scheduler

- [ ] Create `core/engine/scheduler_dag.py`
- [ ] Implement dependency parsing
- [ ] Implement topological sort
- [ ] Add cycle detection
- [ ] Implement parallel execution
- [ ] Add `parallel_strategy` config
- [ ] Write tests

## Merge Orchestration

- [ ] Create `core/engine/merge_strategy.py`
- [ ] Implement deterministic merge order
- [ ] Add conflict detection
- [ ] Add rollback on failure
- [ ] Add merge preview
- [ ] Write tests

## Context Manager

- [ ] Create `core/engine/context_manager.py`
- [ ] Implement token estimation
- [ ] Implement pruning
- [ ] Implement summarization
- [ ] Implement chunking
- [ ] Write tests

## Integration

- [ ] Enhance `core/engine/integration_worker.py`
- [ ] Integrate merge orchestration
- [ ] Add partial merge support
- [ ] Write integration tests
