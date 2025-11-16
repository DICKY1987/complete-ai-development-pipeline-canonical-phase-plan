# Architecture overview

This repository implements a multi‑phase AI development pipeline with clear
workstreams. The code is organized under `src/pipeline/` with supporting
scripts in `scripts/`, schema in `schema/`, and documentation in `docs/`.

## Components

- Pipeline core: `src/pipeline/` modules (orchestrator, scheduler, executor).
- Persistence: SQLite state store defined in `schema/schema.sql`.
- Tooling: profile-driven adapter in `src/pipeline/tools.py` (PH-03).
- Utilities: prompts, worktree helpers, circuit breakers, recovery, bundles.

## Workstream Bundles & Validation

- Purpose: Define inputs for orchestration — each workstream declares its id, files scope, tasks, and dependencies.
- Schema: `schema/workstream.schema.json` specifies required fields and constraints (strict, no unknown fields).
- Loader: `src/pipeline/bundles.py` resolves the workstream directory, loads JSON (per-file object or list), validates against the schema (using `jsonschema` if available; strict manual checks otherwise), builds a dependency DAG, detects cycles, and finds file-scope overlaps.
- CLI: `python scripts/validate_workstreams.py` validates all bundles, reports cycles/overlaps, and optionally syncs them into the DB (`workstreams` table) with `--run-id`.
- Directory: default `workstreams/` at repo root; override with env `PIPELINE_WORKSTREAM_DIR`.

## Workstream Authoring & Generation (PH-05.5)

This phase introduces tools and documentation to make authoring workstream bundles easier and safer.

- **Authoring Guide:** `docs/workstream_authoring_guide.md` provides comprehensive instructions for humans and AI on how to create valid workstream bundles, including purpose, required fields, rules, and a step-by-step workflow.
- **Canonical Template:** `templates/workstream_template.json` offers a pre-filled JSON structure that aligns with `schema/workstream.schema.json`, serving as a starting point for new bundles.
- **Authoring Validator:** `scripts/validate_workstreams_authoring.py` is a dedicated CLI tool for authors to validate their workstream bundles. It wraps the core validation logic from `src/pipeline/bundles.py` (schema, dependency, cycle, and file-scope overlap checks) and provides clear, human-readable error messages or machine-readable JSON output. This ensures that bundles are correct before being committed or used by the orchestrator.
- **Automated Planner (Stub):** `src/pipeline/planner.py` and `config/decomposition_rules.yaml` provide a stub for future v2.0 automation, allowing for the programmatic generation of draft workstreams from higher-level specifications. `scripts/generate_workstreams.py` is a CLI stub for this functionality.

This authoring system directly supports the PH-04 validation pipeline by ensuring that manually created bundles conform to the defined schema and rules, and feeds into the PH-05 orchestrator which relies on valid workstream definitions.

## Flow

1. Plan workstreams (docs, plans).
2. Execute workstreams via orchestrator/scheduler/executor.
3. Record events/errors/steps in SQLite.
4. Generate artifacts and reports.

See also:
- State machine details in `docs/state_machine.md` (run/workstream transitions).
- Phase plan in `docs/PHASE_PLAN.md` (PH-01 to PH-03 scope and artifacts).
  PH-04 adds schema, loader/validator, examples, CLI, and tests.

## Aider Integration & Prompt Engine

- Contract: documented in `docs/aider_contract.md` (CONTRACT_VERSION: AIDER_CONTRACT_V1).
- Tool profile: `config/tool_profiles.json` contains an `aider` entry invoked via the adapter.
- Prompt engine: `src/pipeline/prompts.py` renders EDIT and FIX prompts from `templates/prompts/*.txt.j2` and writes them under `<worktree>/.aider/prompts/`.
- Helpers: `run_aider_edit` and `run_aider_fix` build prompts, persist them, call `run_tool("aider", ...)`, and record `tool_run` events when `run_id`/`ws_id` are provided.
- Sandbox: `sandbox_repos/sandbox_python` provides a tiny repo for integration tests.

## Conventions

- Git worktrees for isolated branches per workstream.
- Python 3.12+, PowerShell 7; tests with `pytest`.
- JSON uses two‑space indent and kebab‑case keys.

## State & persistence

- Database path: `state/pipeline_state.db` (override with `PIPELINE_DB_PATH`).
- Initialization: `python scripts/init_db.py` (idempotent; applies `schema/schema.sql`).
- Core tables:
  - `runs` - lifecycle of an orchestrated run.
  - `workstreams` - individual work units within a run, with dependencies.
  - `step_attempts` - execution attempts with timestamps and results.
  - `errors` - deduplicated errors with signatures and counts.
  - `events` - append-only event log for traceability.

## Tool profiles & adapter layer

- Location: `config/tool_profiles.json` contains declarative profiles for tools.
- Purpose: enable consistent, configurable execution of utilities, tests, and
  static analyzers via a common adapter.
- Types: `ai`, `static-check`, `test`, `utility` (see profiles JSON).
- Adapter: `src/pipeline/tools.py` loads profiles, renders commands with
  template vars like `{cwd}` and `{repo_root}`, executes with timeouts, and
  captures stdout/stderr and exit codes. DB integration records events/errors
  in PH-03 follow-up workstreams.
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
