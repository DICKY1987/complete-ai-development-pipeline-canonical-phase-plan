---
doc_id: DOC-GUIDE-README-189
---

# Phase 3 – Scheduling & Task Graph

## Purpose

Load workstreams, build DAG, resolve dependencies, fill task queue.

## System Position

upstream_phases:
  - phase2_request_building
downstream_phases:
  - phase4_routing
hard_blockers:
  - Valid run record must exist
  - Workstreams must be loaded
  - DAG must be acyclic
soft_dependencies:
  - None

## Phase Contracts

entry_requirements:
  required_files:
    - .state/orchestration.db (with run record)
    - workstreams/*.json
  required_db_tables:
    - runs (from phase2)
    - workstreams
  required_state_flags:
    - RUN_CREATED
exit_artifacts:
  produced_files:
    - .state/task_queue.json
    - .state/dag_graph.json
  updated_db_tables:
    - tasks (created)
    - task_dependencies (created)
  emitted_events:
    - DAG_BUILT
    - TASKS_QUEUED
    - SCHEDULING_COMPLETE

## Phase Contents

Located in: `phase3_scheduling/`
- Cross-cutting implementation in `core/engine/` (scheduler, dag_builder, state_machine)
- State management in `core/state/` (dag_utils, task_queue)
- Specifications in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/`

## Current Components

- See `core/engine/` for scheduling logic
- See `core/state/` for DAG utilities and task queue

## Main Operations

- Load workstream + tasks
- Build DAG based on dependencies (spec-driven + author-defined)
- Determine parallel vs sequential execution
- Populate task queue with PENDING tasks

## Source of Truth

authoritative_sources:
  - core/engine/scheduler.py
  - core/engine/dag_builder.py
  - core/state/dag_utils.py
  - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/DAG_SCHEDULER.md
derived_artifacts:
  - .state/task_queue.json
  - .state/dag_graph.json
do_not_edit_directly:
  - .state/**
  - .ledger/**

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute tasks (phase5 responsibility)
  - Route to tools (phase4 responsibility)
  - Create run records (phase2 responsibility)
  - Generate workstreams (phase1 responsibility)
  - Handle runtime errors (phase6 responsibility)

## Invocation & Control

invocation_mode:
  - automatic_on_phase2_success
entrypoints:
  cli:
    - orchestrator schedule --run <id>
    - python -m core.engine.scheduler
  python:
    - core.engine.scheduler.run()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/scheduler.jsonl
  - logs/dag_builder.jsonl
metrics:
  - dag_nodes_total
  - dag_edges_total
  - dag_cycles_detected
  - tasks_queued_total
  - parallel_tasks_count
  - sequential_tasks_count
health_checks:
  - dag_acyclic_check
  - queue_integrity_check
  - scheduler_heartbeat

## AI Operational Rules

ai_may_modify:
  - core/engine/scheduler.py
  - core/engine/dag_builder.py
  - core/state/dag_utils.py
  - core/state/task_queue.py
ai_must_not_modify:
  - schema/**
  - .state/**
  - specifications/** (DAG specs)
ai_escalation_triggers:
  - DAG cycle detected
  - Task dependency resolution failure
  - Queue write failure
  - Invalid task state transition
ai_safe_mode_conditions:
  - Circular dependency detected
  - Missing required task
  - Queue corruption detected

## Test Coverage

~92 tests for engine components
- DAG construction tests
- Cycle detection tests
- Topological sort tests
- Task queue operations tests
- State machine transition tests
- Parallel vs sequential resolution tests

## Known Failure Modes

- DAG cycle detected → Execution deadlock prevented (CRITICAL)
- Missing task dependency → Task starvation (HIGH)
- Queue file corruption → Run abort and recovery (MEDIUM)
- Invalid state transition → Task marked as failed (MEDIUM)

## Readiness Model

maturity_level: PRODUCTION_READY
risk_profile:
  execution_risk: LOW
  data_loss_risk: LOW
  deadlock_risk: MEDIUM
  external_dependency_risk: LOW
production_gate: ALLOWED

## Status

✅ Complete (100%)
