# Phase 1 – Planning & Spec Alignment

## Purpose

Take OpenSpec + PM epics + plan docs → workstreams + phase plans.

## System Position

upstream_phases:
  - phase0_bootstrap
downstream_phases:
  - phase2_request_building
hard_blockers:
  - PROJECT_PROFILE.yaml must exist
  - Valid specs must be available
  - Spec index must be buildable
soft_dependencies:
  - CCPM/PM system sync (optional)
  - OpenSpec proposals (optional)

## Phase Contracts

entry_requirements:
  required_files:
    - PROJECT_PROFILE.yaml
    - specifications/*.md (core specs)
  required_db_tables:
    - bootstrap_state (from phase0)
  required_state_flags:
    - BOOTSTRAP_COMPLETE
exit_artifacts:
  produced_files:
    - workstreams/*.json
    - .state/spec_index.json
    - .state/workstream_registry.json
  updated_db_tables:
    - workstreams (created)
    - spec_index (created)
  emitted_events:
    - PLANNING_COMPLETE
    - WORKSTREAMS_GENERATED

## Phase Contents

Located in: `phase1_planning/`

- `specifications/` - Spec content and OpenSpec files
- `SPEC_tools/` - Spec processing tools
- `plans/` - Phase plans and CCPM integration
- `README.md` - This file

## Current Components

### Specifications (`specifications/`)
- Core specs (10 production specs):
  - UET_BOOTSTRAP_SPEC.md
  - UET_COOPERATION_SPEC.md
  - UET_PHASE_SPEC_MASTER.md
  - UET_WORKSTREAM_SPEC.md
  - UET_TASK_ROUTING_SPEC.md
  - UET_PROMPT_RENDERING_SPEC.md
  - UET_PATCH_MANAGEMENT_SPEC.md
  - UET_CLI_TOOL_EXECUTION_SPEC.md
  - UTE_ID_SYSTEM_SPEC.md
  - UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md

### Spec Tools (`SPEC_tools/`)
- Spec processing and validation utilities

### Plans (`plans/`)
- Phase plans
- CCPM integration files

### Implementation (`core/planning/`)
Located in cross-cutting `core/` directory:
- `planner.py` - Workstream planner ⚠️ (STUB - partial implementation)
- `ccpm_integration.py` - CCPM/PM integration ⚠️ (partial)
- `archive.py` - Historical archival ✅

## Main Operations

- Ingest OpenSpec, PM epics, phase docs
- Validate specs & build spec index + dependency graph
- Convert accepted specs into workstream JSON
- Link specs and workstreams back to CCPM/PM issues

## Source of Truth

authoritative_sources:
  - specifications/*.md (10 core specs)
  - core/planning/planner.py
  - schema/workstream_spec.v1.json
derived_artifacts:
  - workstreams/*.json
  - .state/spec_index.json
  - .state/workstream_registry.json
do_not_edit_directly:
  - .state/**
  - .ledger/**
  - workstreams/*.json (generated from specs)

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute workstreams
  - Schedule tasks
  - Route to tools
  - Create execution requests
  - Validate code changes

## Invocation & Control

invocation_mode:
  - automatic_on_phase0_success
entrypoints:
  cli:
    - orchestrator plan
    - python -m core.planning.planner
  python:
    - core.planning.planner.run()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/planner.jsonl
  - logs/spec_validation.jsonl
metrics:
  - specs_processed_total
  - workstreams_generated_total
  - spec_validation_errors_total
health_checks:
  - spec_index_integrity_check
  - workstream_schema_validation

## AI Operational Rules

ai_may_modify:
  - core/planning/planner.py (STUB - needs implementation)
  - core/planning/ccpm_integration.py
ai_must_not_modify:
  - specifications/** (source specs)
  - schema/**
  - .state/**
  - workstreams/*.json (generated)
ai_escalation_triggers:
  - Spec validation failure
  - Circular dependency in specs
  - Missing required spec sections
  - Workstream generation failure
ai_safe_mode_conditions:
  - No valid specs found
  - Spec index build failure
  - CCPM sync failure (if required)

## Test Coverage

0 tests (implementation incomplete)
Critical gap: planner.py is STUB
Needed:
  - Spec parsing tests
  - Workstream generation tests
  - Dependency graph tests
  - CCPM integration tests

## Known Failure Modes

- planner.py STUB → Cannot generate workstreams (CRITICAL)
- Invalid spec format → Planning cannot proceed (HIGH)
- Circular spec dependencies → DAG build failure (MEDIUM)
- CCPM sync failure → Planning proceeds but no PM tracking (LOW)

## Readiness Model

maturity_level: OPERATIONAL_BETA
risk_profile:
  execution_risk: HIGH
  data_loss_risk: LOW
  deadlock_risk: MEDIUM
  external_dependency_risk: MEDIUM
production_gate: DISALLOWED

## Status

⚠️ Partial (40%) - Planner needs implementation
