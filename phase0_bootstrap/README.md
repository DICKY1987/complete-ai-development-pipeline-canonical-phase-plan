# Phase 0 – Bootstrap & Initialization

## Purpose

Detect repo, pick profile, validate baseline, generate project profile/router config.

## System Position

upstream_phases:
  - None (entry point)
downstream_phases:
  - phase1_planning
hard_blockers:
  - Valid git repository must exist
  - At least one profile must match repo characteristics
soft_dependencies:
  - None

## Phase Contracts

entry_requirements:
  required_files:
    - .git/ (git repository)
  required_db_tables:
    - None (initializes database)
  required_state_flags:
    - None (first phase)
exit_artifacts:
  produced_files:
    - PROJECT_PROFILE.yaml
    - router_config.json
    - .state/orchestration.db
  updated_db_tables:
    - bootstrap_state (created)
  emitted_events:
    - BOOTSTRAP_COMPLETE

## Phase Contents

Located in: `phase0_bootstrap/`

- `config/` - Configuration files and profiles
- `schema/` - 17 JSON validation schemas
- `README.md` - This file

## Current Components

### Configuration (`config/`)
- Profile configurations
- Tool profiles
- Quality gates (UTE_QUALITY_GATE.yaml)
- AI policies (UTE_ai_policies.yaml)

### Validation Schemas (`schema/`)
- 17 JSON schemas for data contracts
- Zero dependencies foundation layer

### Implementation (`core/bootstrap/`)
Located in cross-cutting `core/` directory:
- `orchestrator.py` - 4-step bootstrap orchestrator ✅
- `discovery.py` - ProjectScanner (repo detection) ✅
- `selector.py` - Profile selection (5 profiles) ✅
- `generator.py` - Artifact generation ✅
- `validator.py` - Baseline validation ✅

## Main Operations

- Detect repo + environment
- Pick correct project profile (patterns, tools, configs)
- Validate repo against schemas (IDs, patterns, layout)
- Generate `PROJECT_PROFILE.yaml` and `router_config.json`

## Source of Truth

authoritative_sources:
  - core/bootstrap/orchestrator.py
  - schema/*.json (17 validation schemas)
  - config/profiles/*.yaml
derived_artifacts:
  - PROJECT_PROFILE.yaml
  - router_config.json
  - .state/orchestration.db
do_not_edit_directly:
  - .state/**
  - .ledger/**
  - PROJECT_PROFILE.yaml (generated)

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute workstreams
  - Plan task execution
  - Modify source code
  - Run validation tests
  - Handle runtime errors

## Invocation & Control

invocation_mode:
  - manual (entry point for pipeline)
entrypoints:
  cli:
    - orchestrator bootstrap
    - python -m core.bootstrap.orchestrator
  python:
    - core.bootstrap.orchestrator.run()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/bootstrap.jsonl
  - logs/discovery.jsonl
metrics:
  - bootstrap_duration_seconds
  - profiles_scanned_total
  - schemas_validated_total
health_checks:
  - profile_match_check
  - schema_validation_check
  - db_initialization_check

## AI Operational Rules

ai_may_modify:
  - core/bootstrap/*.py (implementation)
  - config/profiles/*.yaml (profile definitions)
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
  - PROJECT_PROFILE.yaml (generated artifact)
ai_escalation_triggers:
  - Profile selection ambiguity (multiple matches)
  - Schema validation failure
  - Database initialization failure
ai_safe_mode_conditions:
  - No matching profile found
  - Invalid git repository
  - Missing required schemas

## Test Coverage

8 passing tests in `tests/bootstrap/`
- Discovery tests: repo detection, environment scanning
- Selector tests: profile matching logic
- Validator tests: schema validation
- Generator tests: artifact creation
- Orchestrator tests: end-to-end bootstrap flow

## Known Failure Modes

- No matching profile → System cannot proceed (CRITICAL)
- Schema validation failure → Invalid repo structure (HIGH)
- Database creation failure → State tracking unavailable (MEDIUM)
- Profile ambiguity → Multiple profiles match (LOW - uses priority)

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
