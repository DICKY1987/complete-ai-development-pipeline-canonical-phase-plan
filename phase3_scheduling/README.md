---
doc_id: DOC-GUIDE-README-503
---

# Phase 3 – Scheduling & Task Graph

**Purpose**: Load workstreams, build DAG, resolve dependencies, fill task queue.

## Current Components
- See `core/engine/` for scheduling logic
- See `core/state/` for DAG utilities and task queue

## Main Operations
- Load workstream + tasks
- Build DAG based on dependencies (spec-driven + author-defined)
- Determine parallel vs sequential execution
- Populate task queue with PENDING tasks

## Related Code
- `core/engine/scheduler.py` - DAG-based task scheduler
- `core/engine/dag_builder.py` - DAG construction
- `core/engine/state_machine.py` - Task lifecycle states
- `core/state/dag_utils.py` - Cycle detection, topological sort
- `core/state/task_queue.py` - FIFO queue for tasks

## Task Lifecycle States
PENDING → IN_PROGRESS → VALIDATING → COMPLETED/FAILED/TIMEOUT/...

## Specifications
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/DAG_SCHEDULER.md`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/STATE_MACHINES.md`
- `specifications/specs/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`

## Test Coverage
~92 tests for engine components

## Status
✅ Complete (100%)
