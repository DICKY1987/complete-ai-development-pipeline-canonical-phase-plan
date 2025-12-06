---
doc_id: DOC-SCRIPT-WORKSTREAM-EXECUTORS-DEPRECATED-821
---

# DEPRECATED: Workstream Executor Scripts

**Date:** 2025-12-04
**Status:** CONSOLIDATED

## Summary

Multiple legacy workstream executor scripts have been consolidated.
The canonical orchestration engine is: **`core.engine.orchestrator`**

## Archived Scripts

The following scripts have been archived as they reimplemented orchestration logic:

1. **`simple_workstream_executor.py`** - Basic sequential executor
2. **`uet_execute_workstreams.py`** - UET framework executor
3. **`multi_agent_workstream_coordinator.py`** - Multi-agent coordinator
4. **`uet_workstream_loader.py`** - Workstream loader

## Archive Location

```
_ARCHIVE/workstream_executors_legacy_20251204_*/
```

## Migration Guide

### Old Approach (DEPRECATED)
```bash
# Legacy executors
python scripts/simple_workstream_executor.py
python scripts/uet_execute_workstreams.py
python scripts/multi_agent_workstream_coordinator.py
```

### New Approach (USE THIS)
```bash
# Use canonical core.engine orchestrator
python -m core.engine plans/your_plan.json --var KEY=VALUE

# Or use run_workstream.py CLI wrapper (updated to use core.engine)
python scripts/run_workstream.py --ws-id ws-001
```

## Canonical Entry Points

### 1. **core.engine Module** (Primary)
```bash
# Execute JSON plan
python -m core.engine plans/safe_merge.json --var BRANCH=main

# Database stored at: .ledger/framework.db
```

### 2. **scripts/run_workstream.py** (Convenience CLI)
```bash
# Run single workstream
python scripts/run_workstream.py --ws-id ws-hello-world

# Dry run mode
python scripts/run_workstream.py --ws-id ws-001 --dry-run

# Parallel execution
python scripts/run_workstream.py --parallel --max-workers 4
```

### 3. **scripts/execute_next_workstreams.py** (Project-specific)
```bash
# Execute specific next-gen workstreams with dependency tracking
python scripts/execute_next_workstreams.py --dry-run
python scripts/execute_next_workstreams.py --workstream ws-next-001
```

## Remaining Active Scripts

These scripts are **still active** and serve specific purposes:

- ✅ **`run_workstream.py`** - CLI wrapper (needs update to use core.engine)
- ✅ **`execute_next_workstreams.py`** - Project-specific automation
- ✅ **`sync_workstreams_to_github.py`** - GitHub sync tool
- ✅ **`track_workstream_status.py`** - Status tracking
- ✅ **`spec_to_workstream.py`** - Spec conversion tool

## Rationale

**Problem:** Multiple reimplementations of workstream execution logic led to:
- Inconsistent behavior across scripts
- Duplicate code maintenance
- Feature fragmentation
- Testing complexity

**Solution:** Consolidate to single canonical orchestrator:
- `core.engine.orchestrator.Orchestrator` - Main orchestration class
- `core.engine.__main__.py` - CLI entry point
- `core.state.db` - Unified state management
- `core.engine.state_machine` - State transitions
- `core.engine.scheduler` - Execution scheduling

## Benefits

✅ Single source of truth for orchestration
✅ Consistent state management via `core.state.db`
✅ Proper lifecycle events and logging
✅ Circuit breakers and resilience patterns
✅ Testable and maintainable

## References

- **Orchestrator:** `core/engine/orchestrator.py`
- **CLI:** `core/engine/__main__.py`
- **Tests:** `tests/engine/test_plan_execution.py`
- **Documentation:** `core/engine/README.md`
