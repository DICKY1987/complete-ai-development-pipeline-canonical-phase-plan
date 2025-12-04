# Phase 5 – Execution & Validation

## Purpose

Invoke adapter, run tool, capture output, run acceptance tests, update state.

## System Position

upstream_phases:
  - phase4_routing
downstream_phases:
  - phase6_error_recovery
  - phase7_monitoring
hard_blockers:
  - Tasks must be routed with adapter assignments
  - Adapters must be healthy and available
  - Execution environment must be initialized
soft_dependencies:
  - Error detection plugins (phase6)
  - Monitoring hooks (phase7)

## Phase Contracts

entry_requirements:
  required_files:
    - .state/routing_decisions.json (from phase4)
    - .state/task_queue.json
  required_db_tables:
    - tasks (with adapter_id)
    - adapters
  required_state_flags:
    - ROUTING_COMPLETE
exit_artifacts:
  produced_files:
    - .state/execution_results.json
    - .state/patch_ledger.jsonl
    - logs/execution/*.jsonl
  updated_db_tables:
    - tasks (status updated: COMPLETED/FAILED/TIMEOUT)
    - execution_log (created)
    - patch_history (created)
  emitted_events:
    - TASK_STARTED
    - TASK_COMPLETED
    - TASK_FAILED
    - EXECUTION_FINISHED

## Phase Contents

Located in: `phase5_execution/`
- Cross-cutting implementation in `core/engine/` (executor, process_spawner, test_gate)
- Resilience patterns in `core/engine/resilience/` (circuit breaker, retry, recovery)
- Monitoring in `core/engine/monitoring/` (progress tracker, run monitor)
- Error detection hooks in `error/engine/`

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

## Source of Truth

authoritative_sources:
  - core/engine/executor.py (STUB - needs implementation)
  - core/engine/resilience/ (circuit breaker, retry logic)
  - core/engine/test_gate.py (acceptance testing)
  - core/engine/patch_ledger.py
derived_artifacts:
  - .state/execution_results.json
  - .state/patch_ledger.jsonl
  - logs/execution/*.jsonl
do_not_edit_directly:
  - .state/**
  - .ledger/**
  - logs/execution/** (generated)

## Explicit Non-Responsibilities

this_phase_does_not:
  - Route tasks to adapters (phase4 responsibility)
  - Schedule task execution order (phase3 responsibility)
  - Classify or fix errors (phase6 responsibility)
  - Provide monitoring UI (phase7 responsibility)
  - Generate workstreams (phase1 responsibility)

## Invocation & Control

invocation_mode:
  - automatic_on_phase4_success
  - continuous (executor loop)
entrypoints:
  cli:
    - orchestrator execute --run <id>
    - python -m core.engine.executor
  python:
    - core.engine.executor.run_executor_loop()
resumable: true
idempotent: false
retry_safe: true

## Observability

log_streams:
  - logs/executor.jsonl
  - logs/execution/*.jsonl (per-task)
  - logs/resilience.jsonl
metrics:
  - tasks_executed_total
  - task_success_rate
  - task_duration_seconds
  - circuit_breaker_state
  - retry_attempts_total
  - acceptance_test_pass_rate
health_checks:
  - executor_heartbeat
  - adapter_health_check
  - circuit_breaker_status

## AI Operational Rules

ai_may_modify:
  - core/engine/executor.py (STUB - CRITICAL implementation needed)
  - core/engine/process_spawner.py
  - core/engine/integration_worker.py
  - core/engine/test_gate.py
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
  - core/engine/resilience/** (production-proven patterns)
ai_escalation_triggers:
  - Executor STUB called (CRITICAL)
  - Circuit breaker opens
  - Acceptance tests fail repeatedly
  - Task timeout exceeded
  - Adapter crash
ai_safe_mode_conditions:
  - All adapters unhealthy
  - Circuit breaker open for extended period
  - Execution environment unavailable

## Test Coverage

~32 tests for resilience patterns
- Circuit breaker tests (CLOSED/OPEN/HALF_OPEN states)
- Retry logic tests
- Resilient executor wrapper tests
- Missing: executor.py tests (STUB), acceptance test framework tests

## Known Failure Modes

- executor.py STUB → Cannot execute tasks (CRITICAL)
- Adapter process crash → Circuit breaker opens, retry with fallback (HIGH)
- Acceptance tests fail → Task marked FAILED (MEDIUM)
- Timeout exceeded → Task marked TIMEOUT (MEDIUM)
- Circuit breaker open → Execution paused until recovery (HIGH)

## Readiness Model

maturity_level: DESIGN_ONLY
risk_profile:
  execution_risk: VERY_HIGH
  data_loss_risk: MEDIUM
  deadlock_risk: LOW
  external_dependency_risk: VERY_HIGH
production_gate: DISALLOWED

## Status

⚠️ Partial (50%) - executor.py is a STUB; needs implementation
