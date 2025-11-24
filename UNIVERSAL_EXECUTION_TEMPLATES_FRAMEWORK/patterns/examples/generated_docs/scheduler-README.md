# Module Documentation Template
# TEMPLATE: module-readme
# Variables: Scheduler, Schedule and prioritize workstream steps based on dependencies and resources, Domain (core.engine), - Dependency resolution
- Cycle detection
- Priority-based ordering
- Resource-aware scheduling, from core.engine.scheduler import Scheduler

scheduler = Scheduler()
steps = scheduler.schedule_workstream('WS-001')
# Pattern: EXEC-004 (Doc Standardizer)
# Time savings: 60-65% vs manual docs

---
doc_id: DOC-SCHEDULER-README-001
module: Scheduler
status: active
---

# Scheduler

## Purpose

Schedule and prioritize workstream steps based on dependencies and resources

## Architecture

- **Layer**: Domain (core.engine)
- **Dependencies**: core.state
- **Responsibilities**: Build dependency DAG, topological sort, priority scheduling

## Key Features

- Dependency resolution
- Cycle detection
- Priority-based ordering
- Resource-aware scheduling

## Quick Start

```python
from core.engine.scheduler import Scheduler

scheduler = Scheduler()
steps = scheduler.schedule_workstream('WS-001')
```

## API Reference

### Main Classes

#### Scheduler

Workstream step scheduler with dependency resolution

**Methods:**
- `schedule_workstream(workstream_id: str)`: Get ordered list of steps to execute
- `build_dag(workstream_id: str)`: Build dependency directed acyclic graph

## Configuration

No configuration required (uses workstream JSON)

## Common Tasks

### Schedule a Workstream

```python
scheduler = Scheduler()
ordered_steps = scheduler.schedule_workstream('WS-001')
```

### Check for Cycles

```python
scheduler = Scheduler()
has_cycle = scheduler.has_cycle('WS-001')
```

## Gotchas

- Throws CyclicDependencyError if cycle detected
- Returns empty list if workstream has no steps

## Testing

```bash
pytest tests/engine/test_scheduler.py
```

## Related Modules

- Orchestrator
- Executor

---

**Status**: stable  
**Owner**: @core-team  
**Last Updated**: 2025-11-24
