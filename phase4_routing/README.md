# Phase 4 – Tool Routing & Adapter Selection

## Purpose

Match tasks to tool profiles and select adapters (Aider/Codex/Custom).

## System Position

upstream_phases:
  - phase3_scheduling
downstream_phases:
  - phase5_execution
hard_blockers:
  - Task queue must exist
  - Tool profiles must be configured
  - Adapter registry must be initialized
soft_dependencies:
  - AIM capability bridge (optional)
  - Cluster manager (for parallel execution)

## Phase Contracts

entry_requirements:
  required_files:
    - .state/task_queue.json (from phase3)
    - config/tool_profiles/*.yaml
    - PROJECT_PROFILE.yaml
  required_db_tables:
    - tasks (from phase3)
    - adapters (registry)
  required_state_flags:
    - TASKS_QUEUED
exit_artifacts:
  produced_files:
    - .state/routing_decisions.json
    - .state/adapter_assignments.json
  updated_db_tables:
    - tasks (adapter_id assigned)
    - routing_log (created)
  emitted_events:
    - ROUTING_COMPLETE
    - ADAPTERS_ASSIGNED

## Phase Contents

Located in: `phase4_routing/`

- `tools/` - Tool implementations (guard, indexer, patcher, renderer, resolver)
- `aider/` - Aider adapter configuration
- `aim/` - AIM environment manager and tool capability matching
- `README.md` - This file

## Current Components

### Tools (`tools/`)
- `guard/` - Schema validation tools
- `indexer/` - Index generation
- `patcher/` - Patch application
- `renderer/` - Template rendering
- `resolver/` - Dependency resolution

### Aider (`aider/`)
- Aider CLI adapter configuration
- Multi-instance support

### AIM - AI Tool Matching (`aim/`)
- `bridge/` - Capability matching algorithms
- `capabilities/` - Tool capability definitions
- Tool selection and routing logic

### Implementation (`core/engine/`, `core/adapters/`)
Located in cross-cutting `core/` directory:
- `core/engine/router.py` - Task routing logic ⚠️ (partial)
- `core/engine/tools.py` - Tool registry and selection ⚠️ (partial)
- `core/adapters/base.py` - ToolAdapter base class ✅
- `core/adapters/registry.py` - AdapterRegistry ✅
- `core/adapters/subprocess_adapter.py` - Basic subprocess adapter ✅

## Main Operations

- Match tasks by language, task type, environment
- Select best tool adapter with fallbacks
- Validate adapter configuration (commands, paths, env, timeouts)
- Manage multi-instance pools for Aider/Codex

## Source of Truth

authoritative_sources:
  - core/engine/router.py
  - core/engine/tools.py
  - core/adapters/base.py
  - core/adapters/registry.py
  - aim/bridge/ (capability matching)
derived_artifacts:
  - .state/routing_decisions.json
  - .state/adapter_assignments.json
do_not_edit_directly:
  - .state/**
  - .ledger/**

## Explicit Non-Responsibilities

this_phase_does_not:
  - Execute tasks (phase5 responsibility)
  - Schedule tasks (phase3 responsibility)
  - Handle execution errors (phase6 responsibility)
  - Monitor task progress (phase7 responsibility)
  - Generate workstreams (phase1 responsibility)

## Invocation & Control

invocation_mode:
  - automatic_on_phase3_success
entrypoints:
  cli:
    - orchestrator route --run <id>
    - python -m core.engine.router
  python:
    - core.engine.router.route_tasks()
resumable: true
idempotent: true
retry_safe: true

## Observability

log_streams:
  - logs/router.jsonl
  - logs/adapter_selection.jsonl
metrics:
  - tasks_routed_total
  - adapter_assignments_total
  - routing_fallbacks_total
  - adapter_selection_duration_seconds
health_checks:
  - adapter_registry_check
  - tool_profile_availability_check
  - routing_decision_integrity_check

## AI Operational Rules

ai_may_modify:
  - core/engine/router.py (partial implementation)
  - core/engine/tools.py (partial implementation)
  - core/adapters/*.py (adapter implementations)
  - aim/bridge/*.py (capability matching)
ai_must_not_modify:
  - schema/**
  - .state/**
  - config/tool_profiles/** (user configuration)
ai_escalation_triggers:
  - No suitable adapter found for task
  - Adapter validation failure
  - Tool capability mismatch
  - Routing decision conflict
ai_safe_mode_conditions:
  - Adapter registry unavailable
  - All adapters unhealthy
  - Tool profile missing

## Test Coverage

~27 tests for adapters
- Adapter base class tests
- Registry tests
- Subprocess adapter tests
- Missing: Router tests, pool management tests, capability matching tests

## Known Failure Modes

- No adapter available → Task cannot execute (CRITICAL)
- Adapter health check fails → Fallback to next adapter (MEDIUM)
- Tool capability mismatch → Task routed to wrong tool (HIGH)
- Pool exhaustion → Tasks queued waiting for instances (MEDIUM)

## Readiness Model

maturity_level: OPERATIONAL_BETA
risk_profile:
  execution_risk: MEDIUM
  data_loss_risk: LOW
  deadlock_risk: MEDIUM
  external_dependency_risk: HIGH
production_gate: ALLOWED_WITH_MONITORING

## Status

⚠️ Partial (60%) - Router and pooling need implementation
