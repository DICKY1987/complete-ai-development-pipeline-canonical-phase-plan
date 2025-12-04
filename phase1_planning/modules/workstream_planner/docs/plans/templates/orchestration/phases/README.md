# [TODO: Phase Title]

## Purpose

Purpose to be documented

## System Position

upstream_phases:
  - [TODO: fill with upstream phase IDs, e.g. phase2_request_building]
downstream_phases:
  - [TODO: fill with downstream phase IDs, e.g. phase4_routing]
hard_blockers:
  - [TODO: list conditions that must be true before this phase can run]
soft_dependencies:
  - [TODO: non-blocking dependencies or external syncs]

## Phase Contracts

entry_requirements:
  required_files:
    - [TODO: list required input files]
  required_db_tables:
    - [TODO: list required DB tables, if any]
  required_state_flags:
    - [TODO: list required state flags / readiness signals]
exit_artifacts:
  produced_files:
    - [TODO: list files produced by this phase]
  updated_db_tables:
    - [TODO: list DB tables updated by this phase]
  emitted_events:
    - [TODO: list events emitted to the orchestration/event bus]

## Phase Contents

[TODO: describe folder layout and key subdirectories]

## Current Components

[TODO: fill this section]

## Main Operations

[TODO: fill this section]

## Source of Truth

authoritative_sources:
  - [TODO: list authoritative specs/code for this phase]
derived_artifacts:
  - [TODO: list generated/derived files]
do_not_edit_directly:
  - .state/**
  - .ledger/**

## Explicit Non-Responsibilities

this_phase_does_not:
  - [TODO: list responsibilities explicitly out of scope for this phase]

## Invocation & Control

invocation_mode:
  - [TODO: e.g. automatic_on_previous_phase_success | manual]
entrypoints:
  cli:
    - [TODO: CLI commands to invoke this phase]
  python:
    - [TODO: Python entrypoints to invoke this phase]
resumable: [TODO: true|false]
idempotent: [TODO: true|false]
retry_safe: [TODO: true|false]

## Observability

log_streams:
  - [TODO: list log files/streams for this phase]
metrics:
  - [TODO: list metrics exposed by this phase]
health_checks:
  - [TODO: list health/diagnostic checks for this phase]

## AI Operational Rules

ai_may_modify:
  - [TODO: list files/directories AI may modify in this phase]
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
ai_escalation_triggers:
  - [TODO: conditions that require human review or escalation]
ai_safe_mode_conditions:
  - [TODO: conditions under which execution should be downgraded to safe mode]

## Test Coverage

[TODO: summarize test coverage numbers, files, and gaps]

## Known Failure Modes

[TODO: list typical failure modes and their impact]

## Readiness Model

maturity_level: [TODO: DESIGN_ONLY | OPERATIONAL_BETA | PRODUCTION_READY]
risk_profile:
  execution_risk: [TODO: LOW|MEDIUM|HIGH]
  data_loss_risk: [TODO: LOW|MEDIUM|HIGH]
  deadlock_risk: [TODO: LOW|MEDIUM|HIGH]
  external_dependency_risk: [TODO: LOW|MEDIUM|HIGH]
production_gate: [TODO: DISALLOWED | ALLOWED_WITH_MONITORING | ALLOWED]

## Status

[TODO: e.g. ✅ Complete (100%) or ⚠️ Partial (60%)]
