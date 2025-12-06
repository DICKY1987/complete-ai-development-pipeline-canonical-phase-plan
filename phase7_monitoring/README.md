---
doc_id: DOC-GUIDE-README-149
---

# Phase 7 – Monitoring, Completion & Archival

## Purpose

Live monitoring, dashboards, run completion, artifact archival, reporting.

## System Position

upstream_phases:
  - phase5_execution
  - phase6_error_recovery
downstream_phases:
  - None (terminal phase)
hard_blockers:
  - Run must exist
  - State database must be accessible
soft_dependencies:
  - GUI components (optional)
  - Web UI (optional)

## Phase Contracts

entry_requirements:
  required_files:
    - .state/orchestration.db
  required_db_tables:
    - runs
    - tasks
    - workstreams
  required_state_flags:
    - RUN_CREATED
exit_artifacts:
  produced_files:
    - .archive/<run_id>/ (archived artifacts)
    - reports/<run_id>_summary.json
    - reports/<run_id>_metrics.json
  updated_db_tables:
    - runs (status = COMPLETED/FAILED/PARTIAL)
    - archival_log (created)
  emitted_events:
    - RUN_COMPLETED
    - RUN_ARCHIVED
    - REPORT_GENERATED

## Phase Contents

Located in: `phase7_monitoring/`

- `gui/` - UI components and dashboards
- `state/` - State persistence and databases
- `README.md` - This file

## Current Components

### GUI Components (`gui/`)
- `ui_infrastructure_usage.py` - Infrastructure dashboard ⚠️ (partial)
- `ui_tool_selection_demo.py` - Tool selection UI ⚠️ (partial)

### State Persistence (`state/`)
- Working state directory
- Alternative to `.state/` for state files

### Implementation (`core/`)
Located in cross-cutting `core/` directory:
- `core/ui_cli.py` - CLI dashboard interface ⚠️ (minimal)
- `core/ui_models.py` - UI data models ✅
- `core/ui_settings.py` - UI configuration ✅
- `core/ui_settings_cli.py` - CLI settings ✅
- `core/engine/monitoring/progress_tracker.py` - Progress visualization ✅
- `core/engine/monitoring/run_monitor.py` - Run status tracking ✅
- `core/planning/archive.py` - Artifact archival ✅

## Main Operations

- Show runs/workstreams/tasks status in CLI dashboard, UI, or JSON
- Surface tool health metrics and error counts
- Mark runs as COMPLETED/FAILED/PARTIAL
- Archive artifacts, logs, final DB snapshot

## Source of Truth

authoritative_sources:
  - core/engine/monitoring/progress_tracker.py
  - core/engine/monitoring/run_monitor.py
  - core/planning/archive.py
  - core/ui_models.py
derived_artifacts:
  - .archive/<run_id>/
  - reports/*.json
  - gui/dashboards (if generated)
do_not_edit_directly:
  - .state/**
  - .ledger/**
  - .archive/** (archived immutable)

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute tasks (phase5 responsibility)
  - Classify errors (phase6 responsibility)
  - Make execution decisions (observes only)
  - Modify run state (read-only except completion marking)
  - Retry failed tasks (phase6 responsibility)

## Invocation & Control

invocation_mode:
  - continuous (background monitoring)
  - manual (dashboard/report generation)
entrypoints:
  cli:
    - orchestrator monitor --run <id>
    - orchestrator archive --run <id>
    - orchestrator report --run <id>
  python:
    - core.engine.monitoring.run_monitor.monitor()
    - core.planning.archive.archive_run()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/monitor.jsonl
  - logs/archival.jsonl
metrics:
  - runs_completed_total
  - runs_failed_total
  - artifacts_archived_total
  - archive_size_bytes
  - dashboard_requests_total
health_checks:
  - monitor_heartbeat
  - db_connection_check
  - archival_storage_check

## AI Operational Rules

ai_may_modify:
  - gui/*.py (dashboard implementations)
  - core/ui_cli.py
  - core/engine/monitoring/*.py
  - reporting templates
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
  - .archive/** (immutable)
  - core/planning/archive.py (archival logic)
ai_escalation_triggers:
  - Database corruption detected
  - Archival storage unavailable
  - Report generation failure
ai_safe_mode_conditions:
  - Database read-only mode
  - Archive storage full
  - Monitoring loop detected

## Test Coverage

~15 tests for monitoring components
- Progress tracker tests
- Run monitor tests
- Archive utility tests
- Missing: UI component tests, dashboard rendering tests, report generation tests

## Known Failure Modes

- Dashboard/TUI not implemented → CLI-only monitoring (MEDIUM)
- Archive storage full → Cannot complete archival (HIGH)
- Database connection lost → Cannot update run status (MEDIUM)
- Report template missing → Generic report generated (LOW)

## Readiness Model

maturity_level: OPERATIONAL_BETA
risk_profile:
  execution_risk: LOW
  data_loss_risk: MEDIUM
  deadlock_risk: LOW
  external_dependency_risk: MEDIUM
production_gate: ALLOWED_WITH_MONITORING

## Status

⚠️ Partial (30%) - UI components need implementation
