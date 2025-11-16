# Phase plan summary

This document summarizes the PH-01 to PH-03 plan and associated Codex/Claude
workstreams at a high level. See the detailed workstream execution plan in the
root for specifics.

## PH-01

- Module scaffolding for `src/pipeline/*`.
- Spec index scanner to collect `[IDX-...]` tags.
- Initial documentation updates.

## PH-02

- SQLite schema and DB core helpers.
- State machine validation and CRUD.
- Supporting scripts and tests.

## PH-03: Tool Profiles & Adapter Layer

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-03 execution rules, do not implement tool profiles and adapter layer in an alternate path. Complete PH-00 through PH-02 in the target repo first so that the following required components exist:

- `src/pipeline/` directory with module stubs including `tools.py` (from PH-01)
- SQLite state layer with `db.py`, schema, and state machine functions (from PH-02)
- Project skeleton with `tests/pipeline/`, `docs/`, `scripts/`, and CI configuration (from PH-00)

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-02 artifacts, proceed with PH-03 tasks:

**Summary:**
Phase PH-03 introduces a profile-driven tool adapter that executes external tools (utilities, tests, static analyzers, and AI tools) in a consistent, configurable manner. Profiles are defined in `config/tool_profiles.json` and consumed by `src/pipeline/tools.py`, which renders command templates, enforces timeouts, and captures results. The adapter integrates with the DB layer to record events and errors.

**Planned Artifacts:**

- `config/tool_profiles.json` - tool profiles configuration with at least "echo", "pytest", and PowerShell tool profiles
- `src/pipeline/tools.py` - adapter logic implementing:
  - `load_tool_profiles()` - loads and validates JSON config
  - `get_tool_profile(tool_id)` - retrieves specific tool profile
  - `render_command(tool_id, context)` - template substitution
  - `run_tool(tool_id, context, run_id=None, ws_id=None)` - main entry point with DB integration
  - `ToolResult` - data structure for execution results
- `tests/pipeline/test_tools.py` - unit tests covering success, failure, timeout, and DB integration
- `scripts/tool_smoke_test.py` (optional) - CLI smoke test utility
- Recommended profiles include Python quality tools (`ruff`, `black`, `mypy`), PowerShell analyzers/tests (`psscriptanalyzer`, `pester`), core test runner (`pytest`), optional linters/scanners (`yamllint`, `codespell`, `gitleaks`), and integration utilities (`aider`, `gh`)

**Environment Variable Support:**
- `PIPELINE_TOOL_PROFILES_PATH` - override default config/tool_profiles.json location

## PH-04

Workstream Bundle Parsing & Validation is implemented in this repository.

Artifacts added:

- `schema/workstream.schema.json` - JSON Schema for workstream bundles
- `src/pipeline/bundles.py` - loading, validation, DAG/cycle detection, filescope checks, optional DB sync
- `workstreams/example_single.json`, `workstreams/example_multi.json` - sample bundles (example_multi includes an overlap to exercise detection)
- `scripts/validate_workstreams.py` - CLI to validate bundles; `--run-id` to sync to DB; `--json` for machine-readable output
- `tests/pipeline/test_bundles.py` - unit tests for validation and graphs

Commands:

- `python scripts/validate_workstreams.py` - validate bundles and report issues
- `python scripts/validate_workstreams.py --json` - emit JSON summary
- `python scripts/validate_workstreams.py --run-id <RUN>` - validate and sync to DB
- `pytest -q` - run tests for this phase

## PH-03.5

Aider Integration Contract & Prompt Template System is implemented.

Artifacts added:

- `docs/aider_contract.md` - integration contract (CONTRACT_VERSION AIDER_CONTRACT_V1)
- `config/tool_profiles.json` - `aider` profile with flags, env, working dir, timeout
- `src/pipeline/prompts.py` - prompt engine, helpers to run Aider, DB event recording
- `templates/prompts/edit_prompt.txt.j2`, `templates/prompts/fix_prompt.txt.j2` - prompt templates
- `sandbox_repos/sandbox_python/` - small test repo
- `tests/integration/test_aider_sandbox.py` - integration test (skips if Aider missing)

Commands:

- `python -c "import shutil; print(shutil.which('aider'))"` — verify Aider is available
- `pytest -q -m aider` - run only Aider integration tests

## PH-05

Orchestrator core loop (single workstream).

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-05 execution rules, do not implement orchestrator logic in an alternate path. Complete PH-00 through PH-04.5 in the target repo first so that the following required components exist:

- `src/pipeline/` with stubs for `orchestrator.py`, `db.py`, `bundles.py`, `worktree.py`, `tools.py`, and Aider prompt helpers (`prompts.py`).
- Config and schema from prior phases (e.g., `config/tool_profiles.json`, `schema/workstream.schema.json`).
- Workstream bundles under `workstreams/` and a SQLite DB location.

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-04.5 artifacts, proceed with PH-05 tasks:

- Implement `src/pipeline/orchestrator.py` with steps EDIT → STATIC → RUNTIME and DB state/event recording.
- Add CLI `scripts/run_workstream.py` to run one workstream by `--ws-id`.
- Add tests `tests/pipeline/test_orchestrator_single.py` covering success, EDIT/STATIC/RUNTIME failures, and scope violations.
- Update `docs/ARCHITECTURE.md` with an “Orchestrator Core Loop” section and record artifacts here.

Note: FIX/retry loops and multi-workstream scheduling are out of scope for PH-05.

## PH-05.5: Workstream Bundle Generator (Authoring + Validation)

This phase delivers a robust system for authoring and validating workstream bundles, making it easy and safe for both humans and AI agents to define discrete units of work for the pipeline. It focuses on a v1.0 manual authoring and validation workflow, with stubs for future v2.0 automated planning.

**Summary of the Authoring System:**
The system provides a clear, documented process for creating `workstreams/*.json` files. It includes a canonical JSON template to ensure structural correctness and a dedicated validator script that performs comprehensive checks (schema compliance, dependency resolution, cycle detection, and file-scope overlap analysis). This ensures that all workstreams are well-formed and consistent before being processed by the orchestrator.

**Distinction between v1.0 and v2.0:**
-   **v1.0 (Primary Focus):** Emphasizes semi-manual authoring with strong validation. The goal is to provide a user-friendly and error-resistant mechanism for defining workstreams by hand or with minimal AI assistance.
-   **v2.0 (Future Automated Planner):** This phase includes optional stubs for an automated planner. This future component will aim to generate draft workstreams programmatically from higher-level specifications (e.g., OpenSpec/CCPM inputs), leveraging decomposition rules and potentially AI assistance. The current stubs are clearly marked as experimental and not yet fully implemented.

**Artifacts:**

-   `docs/workstream_authoring_guide.md`: Comprehensive guide for authoring workstream bundles.
-   `templates/workstream_template.json`: Canonical JSON template for new workstreams.
-   `scripts/validate_workstreams_authoring.py`: CLI script for validating workstream bundles, supporting human-readable and JSON output.
-   `tests/pipeline/test_workstream_authoring.py`: Unit tests covering template validity, validation success/failure, overlap detection, and JSON mode.
-   (Optional v2.0 Stubs):
    -   `src/pipeline/planner.py`: Draft automated planner with function skeletons and docstrings.
    -   `config/decomposition_rules.yaml`: Sample YAML file describing future decomposition rules.
    -   `scripts/generate_workstreams.py`: Stub CLI for generating workstreams, indicating current limitations.

## PH-06

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-06 execution rules, do not implement circuit breaker logic in an alternate path. Complete PH-00 through PH-05.5 in the target repo first so that the required components exist.

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-05.5 artifacts, proceed with PH-06 tasks.

## PH-07: GUI Layer & Plugin System

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-07 execution rules, do not implement GUI in an alternate path. Complete PH-00 through PH-06 in the target repo first so that the following required components exist:

- `src/pipeline/` with `orchestrator.py`, `db.py`, `bundles.py`, `worktree.py`, `tools.py`, and other core modules.
- Config files from prior phases (e.g., `config/tool_profiles.json`, `config/gui_config.yaml`).
- SQLite database with schema from PH-02.
- Workstream bundles under `workstreams/`.

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-06 artifacts, proceed with PH-07 tasks:

**Summary:**
Create a safe, plugin-based GUI that provides visual monitoring of runs, workstreams, tools, and logs. The GUI operates as an optional layer—the pipeline works fully headless without it.

**Planned Artifacts:**

- `docs/GUI_PERMISSIONS_MATRIX.md` - defines exactly what the GUI is allowed to do (read-heavy, write-light)
- `docs/PLUGINS_SCHEMA.json` - JSON Schema for plugin manifest files
- `docs/PLUGINS_INTERFACE.md` - defines Python Protocol for panel plugins and service locator
- `config/gui_config.yaml` - GUI-specific settings (window, engine, plugins, terminal, logging)
- `src/gui/shell.py` - main GUI window with plugin loading and lifecycle
- `src/gui/main.py` - GUI application entry point
- `src/gui/services/` - service clients for engine, state, tools, logs, config, terminal
  - `engine_client.py` - run lifecycle operations
  - `state_client.py` - read-only DB queries
  - `tools_client.py` - tool management
  - `logs_client.py` - event log queries
  - `config_client.py` - configuration access
  - `terminal_manager.py` - embedded terminal support
  - `service_locator.py` - dependency injection registry
- `src/gui/plugin_base.py` - PanelPluginBase abstract class with common helpers
- `src/gui/plugin_loader.py` - plugin discovery, loading, and validation
- `src/gui/panels/` - core panel plugins:
  - `dashboard_panel.py` - summary stats and recent runs
  - `runs_panel.py` - run management (start, cancel)
  - `workstreams_panel.py` - workstream monitoring and retry
  - `tools_panel.py` - tool health and testing
  - `logs_panel.py` - event log with filters
  - `terminal_panel.py` - embedded terminals with presets
- `config/plugins/*.plugin.json` - plugin manifests for all core panels
- `scripts/run_gui.py` - CLI entry point for GUI
- `tests/gui/` - unit tests for service locator, plugin loader, services, and panels

**Principles:**
- GUI MUST be optional—all pipeline operations work headlessly
- Strict permissions matrix—no direct DB/file writes, no secret viewing
- Plugin isolation—broken plugins should not crash GUI
- Lightweight—no heavy processing in GUI thread
## PH-06

Circuit breakers, retries, and FIX loop added to the single-workstream orchestrator.

- Config: config/circuit_breakers.yaml with defaults and per-step overrides.
- Module: src/pipeline/circuit_breakers.py provides config loading, signatures, and oscillation detection.
- Orchestrator: src/pipeline/orchestrator.py now wraps STATIC and RUNTIME with FIX attempts via Aider and records errors/events.
- CLI unchanged; --dry-run still supported.

Note: repository root is C:\Users\richg\ALL_AI\Complete AI Development Pipeline - Canonical Phase Plan. Docs that referenced a different root are superseded by this note.

## PH-08: AIM Tool Registry Integration

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-08 execution rules, do not implement AIM tool registry integration in an alternate path. Complete PH-00 through PH-03.5 in the target repo first so that the following required components exist:

- `src/pipeline/` with `tools.py`, `db.py`, and other core modules (from PH-00–PH-03)
- `config/tool_profiles.json` with existing tool profiles (from PH-03)
- Aider integration and prompt engine (from PH-03.5)
- Project skeleton with `docs/`, `scripts/`, `tests/` directories

**AIM Registry Location:**
- Expected at: `C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\.AIM_ai-tools-registry`

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-03.5 artifacts, proceed with PH-08 tasks:

**Summary:**
Integrate the AIM (AI Tools Registry) system to provide capability-based tool routing, fallback chains, audit logging, and automatic tool discovery. AIM extends the existing tool_profiles.json system with PowerShell-based adapters and coordination rules.

**Planned Artifacts:**

- `docs/AIM_INTEGRATION_CONTRACT.md` - integration contract documenting AIM registry structure, Python-to-PowerShell bridge, capability routing, and audit logging
- `docs/AIM_CAPABILITIES_CATALOG.md` - catalog of known capabilities (code_generation, refactoring, testing, etc.) with payload/result schemas
- `config/aim_config.yaml` - AIM-specific settings (registry path, enable flags, timeouts, audit retention)
- `src/pipeline/aim_bridge.py` - bridge module implementing:
  - `get_aim_registry_path()` - resolve AIM registry location
  - `load_aim_registry()` - load AIM_registry.json
  - `load_coordination_rules()` - load routing rules
  - `invoke_adapter(tool_id, capability, payload)` - invoke PowerShell adapters
  - `route_capability(capability, payload)` - capability-based routing with fallbacks
  - `detect_tool(tool_id)` - tool detection
  - `get_tool_version(tool_id)` - version detection
  - `record_audit_log()` - audit logging
- `config/tool_profiles.json` (extended) - add optional `aim_tool_id` and `aim_capabilities` fields
- `src/pipeline/tools.py` (enhanced) - add `run_tool_via_aim()` function
- `scripts/aim_status.py` - CLI utility for tool detection and status
- `scripts/aim_audit_query.py` - CLI utility for querying audit logs
- `tests/pipeline/test_aim_bridge.py` - unit tests for AIM bridge
- `tests/pipeline/test_tools_aim_integration.py` - integration tests for tools.py AIM support
- `tests/integration/test_aim_end_to_end.py` - end-to-end integration tests

**Environment Variable Support:**
- `AIM_REGISTRY_PATH` - override default AIM registry location

**Backward Compatibility:**
- Existing tool_profiles.json entries work unchanged
- AIM is an optional enhancement layer; pipeline functions without it

## PH-09

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is
missing on this machine. Per PH-09 execution rules, do not implement multi-document
versioning or spec management in an alternate path. Complete PH-00 through PH-06 in the
target repo first so that the required baseline exists.

- Required root: `C:\Users\richg\ALL_AI\AI_Dev_Pipeline`
- Source assets for PH-09: `C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\Multi-Document Versioning Automation final_spec_docs`

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00-PH-06 artifacts, proceed in that
repository with PH-09 deliverables (spec management contract, sidecar schema, and tools for
indexing, resolving, patching, rendering, and validation) and wire them into CI.

## PH-09 (Implemented in this repository)

Multi-document versioning and spec management delivered in this repository root
(`C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan`).

Artifacts:

- `docs/SPEC_MANAGEMENT_CONTRACT.md` — SPEC_MGMT_V1 contract (sidecars, linking, tools).
- `schema/sidecar_metadata.schema.yaml` — schema for `.sidecar.yaml` files.
- Tools under `tools/`:
  - `spec_indexer/indexer.py` — generates/validates sidecars, builds `docs/index.json` and `docs/.index/suite-index.yaml`.
  - `spec_resolver/resolver.py` — resolves `spec://` and `specid://` to files/ranges.
  - `spec_patcher/patcher.py` — patches a paragraph by id, updates sidecar and index.
  - `spec_renderer/renderer.py` — renders unified Markdown from suite index.
  - `spec_guard/guard.py` — validates consistency across suite, sidecars, and files.

Commands:

- `python tools/spec_indexer/indexer.py --source "docs/source" --output docs/index.json`
  (defaults to `Multi-Document Versioning Automation final_spec_docs/docs/source` if `docs/source` is missing)
- `python tools/spec_renderer/renderer.py --output build/spec.md`
- `python tools/spec_resolver/resolver.py spec://01-architecture/00-overview#p-2`
- `python tools/spec_patcher/patcher.py --id <ID> --text "New paragraph"`
- `python tools/spec_guard/guard.py`
