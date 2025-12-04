# Phase 6 – Error Analysis, Auto-Fix & Escalation

## Purpose

Detect errors, classify, auto-fix, and escalate as needed.

## System Position

upstream_phases:
  - phase5_execution
downstream_phases:
  - phase5_execution (retry loop)
  - phase7_monitoring
hard_blockers:
  - Task must have failed or timed out
  - Error plugins must be available
  - Error detection must complete
soft_dependencies:
  - Circuit breaker state (from resilience layer)
  - Monitoring hooks (phase7)

## Phase Contracts

entry_requirements:
  required_files:
    - .state/execution_results.json (from phase5)
    - error/plugins/**/plugin.py (21 plugins)
  required_db_tables:
    - tasks (status = FAILED/TIMEOUT)
    - execution_log
  required_state_flags:
    - TASK_FAILED or TASK_TIMEOUT
exit_artifacts:
  produced_files:
    - .state/error_analysis.json
    - .state/fix_patches.json
    - logs/error_recovery/*.jsonl
  updated_db_tables:
    - error_log (created)
    - recovery_attempts (created)
    - tasks (status updated after fix attempt)
  emitted_events:
    - ERROR_DETECTED
    - ERROR_CLASSIFIED
    - FIX_APPLIED
    - ERROR_ESCALATED

## Phase Contents

Located in: `phase6_error_recovery/`

- `error/` - Error engine and 21 error detection/fix plugins
  - `error/engine/` - Error detection and orchestration
  - `error/plugins/` - Language-specific and cross-cutting plugins
  - `error/shared/` - Shared utilities
- `README.md` - This file

## Current Components

### Error Engine (`error/engine/`)
- `error_engine.py` - Main error engine ⚠️ (SHIM - imports from UET framework)
- `error_state_machine.py` - Error lifecycle states ✅
- `error_context.py` - Error context capture ✅
- `pipeline_engine.py` - Error pipeline orchestration ✅
- `plugin_manager.py` - Plugin discovery/loading ✅
- `file_hash_cache.py` - Change detection ✅

### Error Plugins (`error/plugins/`) - 21 Plugins ✅
**Python:**
- python_ruff/, python_mypy/, python_pylint/, python_pyright/
- python_bandit/, python_safety/
- python_black_fix/, python_isort_fix/

**JavaScript:**
- js_eslint/, js_prettier_fix/

**Markdown:**
- md_markdownlint/, md_mdformat_fix/

**Other:**
- yaml_yamllint/, powershell_pssa/
- semgrep/, gitleaks/
- path_standardizer/, test_runner/
- codespell/, json_jq/

### Shared Utilities (`error/shared/`)
- Common error handling functions
- Plugin base classes and utilities

### Supporting Components (`core/engine/resilience/`)
Located in cross-cutting `core/` directory:
- `circuit_breaker.py` - Circuit breaker (CLOSED/OPEN/HALF_OPEN) ✅
- `retry.py` - Exponential backoff, retry logic ✅
- `recovery.py` - Recovery handlers ✅

## Main Operations

- Collect outputs/logs on FAILED/TIMEOUT
- Run error plugins (ruff, mypy, pytest, semgrep, etc.)
- Classify errors (transient vs permanent vs unknown)
- Generate patches for auto-fixable errors
- Apply patches and re-validate
- Circuit breaker protection
- Escalation for manual intervention

## Source of Truth

authoritative_sources:
  - error/engine/error_engine.py (SHIM - imports from UET)
  - error/engine/pipeline_engine.py
  - error/plugins/**/plugin.py (21 plugins)
  - core/engine/resilience/ (circuit breaker, retry)
derived_artifacts:
  - .state/error_analysis.json
  - .state/fix_patches.json
  - logs/error_recovery/*.jsonl
do_not_edit_directly:
  - .state/**
  - .ledger/**
  - logs/error_recovery/** (generated)

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute tasks (phase5 responsibility)
  - Route tasks (phase4 responsibility)
  - Provide monitoring UI (phase7 responsibility)
  - Make architectural decisions (escalates instead)
  - Modify working code outside error scope

## Invocation & Control

invocation_mode:
  - automatic_on_task_failure
  - triggered_by_phase5
entrypoints:
  cli:
    - orchestrator recover --task <id>
    - python -m error.engine.pipeline_engine
  python:
    - error.engine.pipeline_engine.analyze_and_fix()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/error_engine.jsonl
  - logs/error_recovery/*.jsonl (per-error)
  - logs/plugin_execution.jsonl
metrics:
  - errors_detected_total
  - errors_classified_total
  - fixes_applied_total
  - fix_success_rate
  - escalations_total
  - plugin_execution_duration_seconds
health_checks:
  - error_engine_health
  - plugin_availability_check
  - circuit_breaker_status

## AI Operational Rules

ai_may_modify:
  - error/plugins/**/plugin.py (add new plugins)
  - error/engine/pipeline_engine.py
  - error/engine/error_context.py
ai_must_not_modify:
  - schema/**
  - .state/**
  - error/engine/error_engine.py (SHIM - UET dependency)
  - core/engine/resilience/** (production-proven)
ai_escalation_triggers:
  - Unknown error type (no plugin match)
  - Auto-fix fails after max retries
  - Circuit breaker opens
  - Error classified as architectural
ai_safe_mode_conditions:
  - All error plugins unavailable
  - Error analysis loop detected
  - Fix application causes new critical error

## Test Coverage

~50+ tests for plugins and pipeline
- Python plugin tests (ruff, mypy, pylint, etc.)
- JavaScript plugin tests (eslint, prettier)
- Error classification tests
- Pipeline orchestration tests
- Circuit breaker integration tests

## Known Failure Modes

- error_engine.py SHIM → Depends on external UET framework (MEDIUM)
- Unknown error type → Cannot auto-fix, escalates (MEDIUM)
- Fix creates new error → Rollback and escalate (HIGH)
- Plugin unavailable → Skips that detection, may miss errors (LOW)
- Circuit breaker open → Recovery paused (MEDIUM)

## Readiness Model

maturity_level: OPERATIONAL_BETA
risk_profile:
  execution_risk: MEDIUM
  data_loss_risk: LOW
  deadlock_risk: LOW
  external_dependency_risk: HIGH
production_gate: ALLOWED_WITH_MONITORING

## Status

⚠️ Partial (60%) - Engine is a shim; needs full implementation
