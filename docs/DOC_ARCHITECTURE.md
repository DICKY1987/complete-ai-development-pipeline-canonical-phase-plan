---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-ARCHITECTURE-076
---

# Architecture Overview

**Last Updated**: 2025-11-19  
**Phase**: Post-Phase E Refactor  

This repository implements a multi-phase AI development pipeline with section-based organization. The codebase was refactored in Phase E to organize functionality by domain (core, error, aim, pm, spec) rather than a flat structure.

> 📊 **Visual Documentation**: See [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) for detailed visual diagrams of the system architecture, module dependencies, and data flows.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Workstream Bundles                        │
│                    (workstreams/*.json)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Core Engine (core/engine/)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Orchestrator │→ │  Scheduler   │→ │   Executor   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                   ↓                  ↓             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Tools     │  │Circuit Break.│  │   Recovery   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ↓                                ↓
┌────────────────────────┐      ┌────────────────────────────┐
│ Core State             │      │ Error Detection            │
│ (core/state/)          │      │ (error/)                   │
│  • Database (SQLite)   │      │  • Engine (error/engine/)  │
│  • CRUD Operations     │      │  • Plugins (error/plugins/)│
│  • Bundles & Worktrees │      │  • State Machine           │
└────────────────────────┘      └────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│              External Integrations                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   AIM    │  │    PM    │  │   Spec   │  │  Aider   │   │
│  │  (aim/)  │  │  (pm/)   │  │ (spec/)  │  │ (aider/) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Section-Based Organization

### Core Sections
**Purpose**: Database operations, state persistence, bundle management

**Key Components**:
- `db.py` - SQLite connection management and initialization
- `db_sqlite.py` - SQLite-specific backend implementation
- `crud.py` - CRUD operations for runs, workstreams, steps, errors, events
- `bundles.py` - Workstream JSON loading, validation, dependency DAG building
- `worktree.py` - Git worktree creation and file scope validation

**Responsibilities**:
- Manage pipeline state in SQLite database
- Load and validate workstream bundles
- Build dependency graphs and detect cycles
- Create isolated worktrees for workstream execution

### Core: Engine (`core/engine/`)
**Purpose**: Orchestration, execution, and recovery logic

**Key Components**:
- `orchestrator.py` - Single-workstream execution loop (EDIT → STATIC → RUNTIME)
- `scheduler.py` - Multi-workstream dependency resolution and scheduling
- `executor.py` - Step execution with retry logic
- `tools.py` - Tool profile adapter with templating and timeout handling
- `circuit_breakers.py` - Failure threshold logic to prevent runaway retries
- `recovery.py` - Error recovery strategies

**Responsibilities**:
- Execute workstream steps in correct order
- Manage tool invocations via profiles
- Handle failures with retry and circuit breaker patterns
- Coordinate parallel workstream execution

### Core: Planning (`core/planning/`)
**Purpose**: Workstream generation and archiving

**Key Components**:
- `planner.py` - Automated workstream generation (stub for v2.0)
- `archive.py` - Archive utilities for completed workstreams

**Responsibilities**:
- Generate workstreams from high-level specs
- Archive completed work

### Core: Shared Utilities (`core/`)
**Purpose**: Cross-cutting utilities used by multiple components

**Key Components**:
- `openspec_parser.py` - OpenSpec parsing and validation
- `openspec_convert.py` - OpenSpec-to-workstream conversion
- `spec_index.py` - Spec indexing and cross-referencing
- `agent_coordinator.py` - Multi-agent coordination

### Error: Detection Engine (`error/engine/`)
**Purpose**: Error detection, analysis, and lifecycle management

**Key Components**:
- `error_engine.py` - Core error detection orchestration
- `error_state_machine.py` - State transitions (NEW → ANALYZED → FIXED → VERIFIED)
- `error_context.py` - Error context tracking with history and metadata
- `error_pipeline_cli.py` - CLI for error pipeline operations
- `error_pipeline_service.py` - Service layer for error operations
- `pipeline_engine.py` - Pipeline integration for error detection
- `plugin_manager.py` - Plugin discovery and lifecycle management
- `file_hash_cache.py` - File hashing for incremental detection

**Responsibilities**:
- Discover and load detection plugins
- Run plugins against codebase
- Track error lifecycle through state machine
- Provide incremental detection via file hashing

### Error: Detection Plugins (`error/plugins/`)
**Purpose**: Language and tool-specific error detection

**Plugin Categories**:
- **Python**: ruff, black, isort, pylint, mypy, pyright, bandit, safety
- **PowerShell**: PSScriptAnalyzer (pssa)
- **JavaScript**: prettier, eslint
- **Markup/Data**: yamllint, mdformat, markdownlint, jq
- **Cross-cutting**: codespell, semgrep, gitleaks
- **Utilities**: path_standardizer, test_runner

**Plugin Structure** (each plugin has):
- `manifest.json` - Metadata (ID, name, version, type, tool, capabilities)
- `plugin.py` - `parse()` and optional `fix()` implementations
- `__init__.py` - Package marker

### Domain-Specific Sections

#### AIM Integration (`aim/`)
**Purpose**: Integration with AIM (AI-tools Inventory Manager)

**Key Components**:
- `bridge.py` - Python-to-PowerShell bridge
  - Registry loading and tool detection
  - Version checking and capability routing
  - Audit logging to `aim/.AIM_ai-tools-registry/AIM_audit/`

#### Project Management (`pm/`)
**Purpose**: CCPM and project management integrations

#### Spec Tooling (`spec/`)
**Purpose**: Specification validation and tooling

#### Aider Integration (`aider/`)
**Purpose**: Integration with Aider AI coding assistant

**Key Components**:
- Prompt templates for EDIT/FIX operations
- Integration scripts

## Workstream Bundles & Validation

**Purpose**: Define inputs for orchestration — each workstream declares its id, files scope, tasks, and dependencies.

**Schema**: `schema/workstream.schema.json` specifies required fields and constraints (strict, no unknown fields).

**Loader**: `core/state/bundles.py` resolves the workstream directory, loads JSON (per-file object or list), validates against the schema (using `jsonschema` if available; strict manual checks otherwise), builds a dependency DAG, detects cycles, and finds file-scope overlaps.

**CLI**: `python scripts/validate_workstreams.py` validates all bundles, reports cycles/overlaps, and optionally syncs them into the DB (`workstreams` table) with `--run-id`.

**Directory**: default `workstreams/` at repo root; override with env `PIPELINE_WORKSTREAM_DIR`.

## Workstream Authoring & Generation

- **Authoring Guide**: `docs/workstream_authoring_guide.md` provides comprehensive instructions
- **Canonical Template**: `aider/templates/workstream_template.json` offers a pre-filled JSON structure
- **Authoring Validator**: `scripts/validate_workstreams_authoring.py` provides clear error messages
- **Automated Planner (Stub)**: `core/planning/planner.py` and `config/decomposition_rules.yaml` for future v2.0 automation

## Data Flow

1. **Authoring** → `workstreams/`, `openspec/`, `aider/templates/`, `docs/`
2. **Validation** → `scripts/validate_workstreams.py`, using `schema/`
3. **Orchestration** → `scripts/run_workstream.py` invoking `core.engine.*` and writing to `.worktrees/`
4. **State Management** → `core.state.crud` → `state/` DB and events
5. **Error Detection** → `error.engine.error_engine` → error reports
6. **External Integrations** → `aim.bridge`, `pm.*`, `spec.*`, `aider.*`

**Execution Flow**:
```
Workstream Bundle → Validation → Scheduler → Orchestrator → Executor
                                      ↓           ↓            ↓
                                   Database ← State Mgmt → Worktree
                                      ↓
                                Error Detection (optional)
```

## State & Persistence

**Database Path**: `state/pipeline_state.db` (override with `PIPELINE_DB_PATH`)

**Initialization**: `python scripts/init_db.py` (idempotent; applies `schema/schema.sql`)

**Core Tables**:
- `runs` - Lifecycle of an orchestrated run
- `workstreams` - Individual work units within a run, with dependencies
- `step_attempts` - Execution attempts with timestamps and results
- `errors` - Deduplicated errors with signatures and counts
- `events` - Append-only event log for traceability

**Managed By**: `core/state/` modules (db.py, crud.py, db_sqlite.py)

## Tool Profiles & Adapter Layer

**Location**: `config/tool_profiles.json` contains declarative profiles for tools

**Purpose**: Enable consistent, configurable execution of utilities, tests, and static analyzers via a common adapter

**Types**: `ai`, `static-check`, `test`, `utility`

**Adapter**: `core/engine/tools.py` loads profiles, renders commands with template vars like `{cwd}` and `{repo_root}`, executes with timeouts, and captures stdout/stderr and exit codes

**Integration**: Records events/errors via `core/state/crud` when `run_id`/`ws_id` are provided

## Legacy Compatibility & Deprecation

### Shim Layer

**Purpose**: Maintain backward compatibility during transition period

**Location**:
- `src/pipeline/*.py` - Forward imports to `core.*` modules
- `MOD_ERROR_PIPELINE/*.py` - Forward imports to `error.*` modules

**Example Shim** (`src/pipeline/db.py`):
```python
"""
DEPRECATED: Use core.state.db instead
This shim will be removed in a future version
"""
from core.state.db import *  # noqa: F401, F403
```

### CI Enforcement

**Workflow**: `.github/workflows/path_standards.yml`

**Checks**:
- Detects `src.pipeline.*` imports → FAILS BUILD
- Detects `MOD_ERROR_PIPELINE.*` imports → FAILS BUILD

**Documentation**: See [docs/CI_PATH_STANDARDS.md](CI_PATH_STANDARDS.md)

### Migration Path

**Mapping Document**: [docs/SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md)

**Timeline**: Shims will be removed in a future major version after deprecation period

## Repository Map

### Infrastructure
- `docs/` - Architecture notes, ADRs, specifications, refactor mapping
- `plans/` - Phase checklists and templates
- `meta/` - Phase development docs and planning
- `scripts/` - Operational CLIs (bootstrap, validate, generate, run pipeline, inspect DB)
- `schema/` - JSON/YAML/SQL schemas (single source of truth)
- `config/` - Tool profiles, breaker settings, decomposition rules, AIM config
- `tools/` - Internal utilities (spec indexer, path indexer)
- `tests/` - Unit/integration tests for scripts/tools/pipeline
- `openspec/` - OpenSpec project and specifications
- `sandbox_repos/` - Toy repos for integration testing
- `assets/` - Diagrams and images

### Runtime
- `.worktrees/` - Per-workstream working directories (created at runtime, gitignored)
- `state/` and `.state/` - Local state, reports, and DB files (gitignored)

## Conventions

- **Git worktrees** for isolated branches per workstream
- **Python 3.12+**, PowerShell 7; tests with `pytest`
- **JSON** uses two-space indent and kebab-case keys
- **Imports** use section-based paths (e.g., `from core.state.db import init_db`)

## See Also

- **Section Refactor Mapping**: [docs/SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md)
- **CI Path Standards**: [docs/CI_PATH_STANDARDS.md](CI_PATH_STANDARDS.md)
- **State Machine**: [docs/state_machine.md](state_machine.md) (run/workstream transitions)
- **Aider Contract**: [docs/aider_contract.md](aider_contract.md) (CONTRACT_VERSION: AIDER_CONTRACT_V1)
- **Workstream Authoring**: [docs/workstream_authoring_guide.md](workstream_authoring_guide.md)

---

**Architecture Version**: 2.0 (Post-Phase E Refactor)  
**Last Major Change**: Phase E - Section-based reorganization  
**Migration Status**: Shims active, CI enforcement enabled
  - Profiles live in `config/tool_profiles.json` and include core tools:
    `pytest`, `psscriptanalyzer`, and recommended linters/formatters
    (`ruff`, `black`, `mypy`), plus optional scanners (`yamllint`, `codespell`,
    `gitleaks`) and integration utilities (`aider`, `gh`).

## Orchestrator Core Loop (PH-05)

- Scope: Single-workstream pipeline executing steps in order: EDIT → STATIC → RUNTIME.
- Integration:
  - Uses `src/pipeline/worktree.py` to create a per-workstream directory under `.worktrees/<ws-id>`.
  - Invokes Aider via `src/pipeline/prompts.py::run_aider_edit` for EDIT.
  - Runs static tools via `src/pipeline/tools.py` (configurable via context `static_tools`).
  - Runs runtime checks via a configurable `runtime_tool` (PH-05 keeps this simple).
  - Validates file scope at the end via `worktree.validate_scope` (stubbed OK in PH-05).
- State & events:
  - Records step attempts in `step_attempts` and lifecycle events in `events`.
  - Updates `workstreams.status` deterministically: `editing` → `static_check` → `runtime_tests` → `done` or `failed`.
- CLI:
  - `python scripts/run_workstream.py --ws-id <id> [--run-id <run>] [--dry-run]` runs one workstream.
  - `--dry-run` simulates steps without invoking external tools (useful for CI/tests).

## AIM Tool Registry Integration (PH-08)

The AIM (AI Tools Registry) integration provides capability-based routing for AI coding tools with fallback chains and audit logging.

### Architecture

- **Registry Location**: `.AIM_ai-tools-registry/` contains PowerShell-based tool adapters and coordination rules.
- **Bridge Module**: `src/pipeline/aim_bridge.py` provides Python-to-PowerShell bridge with 8 core functions:
  - `get_aim_registry_path()` - Resolves AIM registry directory (env var or auto-detect)
  - `load_aim_registry()` - Loads tool metadata from `AIM_registry.json`
  - `load_coordination_rules()` - Loads capability routing rules
  - `invoke_adapter()` - Invokes PowerShell adapter via subprocess
  - `route_capability()` - Routes capability to primary tool with fallback chain
  - `detect_tool()` - Detects if tool is installed
  - `get_tool_version()` - Gets tool version
  - `record_audit_log()` - Writes audit log to `AIM_audit/<date>/`

### Capability-Based Routing

Instead of calling tools directly, the pipeline routes tasks by **capability** (e.g., "code_generation"):

```python
from src.pipeline.aim_bridge import route_capability

result = route_capability(
    capability="code_generation",
    payload={"prompt": "Add error handling"}
)
```

Coordination rules define routing chains:
- **Primary tool**: First choice (e.g., jules for code_generation)
- **Fallback chain**: Tried in order if primary fails (e.g., aider → claude-cli)
- **Load balancing**: Optional (future feature)

### PowerShell Adapter Pattern

Each tool has a PowerShell adapter in `.AIM_ai-tools-registry/AIM_adapters/`:
- **Input**: JSON via stdin with `{"capability": "...", "payload": {...}}`
- **Output**: JSON via stdout with `{"success": bool, "message": "...", "content": {...}}`
- **Invocation**: `echo '<json>' | pwsh -File adapter.ps1`

### Audit Logging

All tool invocations are logged to `.AIM_ai-tools-registry/AIM_audit/<YYYY-MM-DD>/<timestamp>_<tool>_<capability>.json` with:
- ISO 8601 UTC timestamp
- Actor (always "pipeline")
- Tool ID and capability
- Input payload and output result

### Configuration & Extension

- **Config**: `config/aim_config.yaml` controls enable flags, timeouts, and audit retention
- **Tool Profiles**: `config/tool_profiles.json` extended with optional `aim_tool_id` and `aim_capabilities` fields
- **Environment**: `AIM_REGISTRY_PATH` env var overrides default registry location

### Backward Compatibility

AIM is an **optional enhancement layer**:
- Pipeline functions normally if AIM disabled or unavailable
- Existing `tool_profiles.json` entries work unchanged
- Graceful degradation if registry not found (logs warning, uses direct tool invocation)

### CLI Utilities

- `python scripts/aim_status.py` - Shows tool detection status and capability routing
- `python scripts/aim_audit_query.py` - Queries audit logs with filters (tool, capability, date)

### Documentation

- **Contract**: `docs/AIM_INTEGRATION_CONTRACT.md` (AIM_INTEGRATION_V1)
- **Capabilities**: `docs/AIM_CAPABILITIES_CATALOG.md` lists known capabilities with schemas

