# Phase 2 – Request Building & Run Creation

## Purpose

Build ExecutionRequest, validate schema, create run records in DB.

## System Position

upstream_phases:
  - phase1_planning
downstream_phases:
  - phase3_scheduling
hard_blockers:
  - Valid workstream JSON must exist
  - Database must be initialized
  - Schemas must be available for validation
soft_dependencies:
  - None

## Phase Contracts

entry_requirements:
  required_files:
    - workstreams/*.json (from phase1)
    - schema/execution_request.v1.json
    - schema/run_record.v1.json
  required_db_tables:
    - workstreams (from phase1)
  required_state_flags:
    - PLANNING_COMPLETE
exit_artifacts:
  produced_files:
    - .state/orchestration.db (updated)
    - .state/transitions.jsonl (appended)
    - .ledger/framework.db (audit trail)
  updated_db_tables:
    - runs (created)
    - workstreams (status updated)
    - audit_log (created)
  emitted_events:
    - RUN_CREATED
    - EXECUTION_REQUEST_VALIDATED

## Phase Contents

Located in: `phase2_request_building/`
- Cross-cutting implementation in `core/engine/` and `core/state/`
- Schema validation in `schema/`
- State storage in `.state/`, `.ledger/`

## Current Components

- See `core/state/` for state management
- See `core/engine/execution_request_builder.py` for request building
- See `schema/` for validation schemas

## Main Operations

- User/CLI selects a plan/workstream and requests "run this"
- Build normalized execution request (what, where, tools, patterns, IDs)
- Validate against `request.schema.json`
- Create run record and initial workstream rows in SQLite

## Source of Truth

authoritative_sources:
  - core/engine/execution_request_builder.py
  - schema/execution_request.v1.json
  - schema/run_record.v1.json
  - core/state/db.py, db_unified.py
derived_artifacts:
  - .state/orchestration.db
  - .state/transitions.jsonl
  - .ledger/framework.db
do_not_edit_directly:
  - .state/**
  - .ledger/**

## Explicit Non-Responsibilities

this_phase_does_not:
  - Generate workstreams (phase1 responsibility)
  - Schedule tasks (phase3 responsibility)
  - Execute tasks (phase5 responsibility)
  - Route to tools (phase4 responsibility)
  - Handle errors (phase6 responsibility)

## Invocation & Control

invocation_mode:
  - automatic_on_phase1_success
  - manual (CLI: user requests run)
entrypoints:
  cli:
    - orchestrator request --workstream <id>
    - python -m core.engine.execution_request_builder
  python:
    - ExecutionRequestBuilder().build()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/request_builder.jsonl
  - logs/db_operations.jsonl
  - .state/transitions.jsonl
metrics:
  - requests_created_total
  - requests_validated_total
  - db_write_duration_seconds
  - validation_errors_total
health_checks:
  - db_connection_check
  - schema_availability_check
  - run_record_integrity_check

## AI Operational Rules

ai_may_modify:
  - core/engine/execution_request_builder.py
  - core/state/crud.py
  - core/state/bundles.py
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
  - core/state/db.py (schema definitions)
ai_escalation_triggers:
  - Schema validation failure
  - Database write failure
  - Duplicate run ID
  - Invalid workstream reference
ai_safe_mode_conditions:
  - Database unavailable
  - Missing required schemas
  - Workstream not found

## Test Coverage

Implied via state management tests
- Database CRUD tests in tests/state/
- Schema validation tests
- Audit logging tests
- Request builder fluent API tests

## Known Failure Modes

- Schema validation failure → Request rejected (MEDIUM)
- Database write failure → Transaction rollback (MEDIUM)
- Duplicate run ID → Request rejected with clear error (LOW)
- Missing workstream → Request cannot be created (MEDIUM)

## Readiness Model

maturity_level: PRODUCTION_READY
risk_profile:
  execution_risk: LOW
  data_loss_risk: LOW
  deadlock_risk: LOW
  external_dependency_risk: LOW
production_gate: ALLOWED

## Status

✅ Complete (100%)
