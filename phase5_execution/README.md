---
doc_id: DOC-GUIDE-README-506
---

# Phase 5 – Execution & Validation

**Purpose**: Invoke adapter, run tool, capture output, run acceptance tests, update state.

## Current Components
- See `core/engine/` for execution logic
- See `core/engine/resilience/` for fault tolerance
- See `core/engine/monitoring/` for progress tracking

## Main Operations
- Executor pulls next task from queue
- Invoke correct adapter (spawn process / call API / manual instructions)
- Stream output, track duration, capture files changed
- Run acceptance tests (linting, unit tests, import checks)
- Update task state (IN_PROGRESS → VALIDATING → COMPLETED/FAILED/...)

## Related Code
- `core/engine/executor.py` - Main executor ⚠️ (STUB - needs implementation)
- `core/engine/process_spawner.py` - Subprocess management ✅
- `core/engine/integration_worker.py` - Worker integration ✅
- `core/engine/test_gate.py` - Acceptance test framework ✅
- `core/engine/recovery.py` - Recovery handlers ✅
- `core/engine/patch_ledger.py` - Patch tracking ✅
- `core/engine/patch_converter.py` - Patch conversion ✅

## Resilience Components (Complete)
- `core/engine/resilience/circuit_breaker.py` - Circuit breaker (CLOSED/OPEN/HALF_OPEN)
- `core/engine/resilience/retry.py` - Exponential backoff, retry logic
- `core/engine/resilience/resilient_executor.py` - Resilient execution wrapper

## Monitoring Components (Complete)
- `core/engine/monitoring/progress_tracker.py` - Task progress tracking
- `core/engine/monitoring/run_monitor.py` - Run-level monitoring

## Supporting Components
- `error/engine/error_engine.py` - Error detection hooks
- `error/engine/plugin_manager.py` - Plugin orchestration
- `core/state/audit_logger.py` - Execution audit

## Test Coverage
~32 tests for resilience patterns

## Status
⚠️ Partial (50%) - executor.py is a STUB; needs implementation
