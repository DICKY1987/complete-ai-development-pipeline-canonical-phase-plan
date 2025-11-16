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

## PH-03

- Tool profiles and adapter core.
- DB integration and tests.
- Documentation refinements.

### Summary

Phase PH-03 introduces a profile-driven tool adapter that executes external
tools (utilities, tests, static analyzers, and AI tools) in a consistent,
configurable manner. Profiles are defined in `config/tool_profiles.json` and
consumed by `src/pipeline/tools.py`, which renders command templates, enforces
timeouts, and captures results. Subsequent workstreams integrate adapter events
with the DB layer and add tests.

### Artifacts

- `config/tool_profiles.json` - tool profiles configuration
- `src/pipeline/tools.py` - adapter logic (core + DB integration)
- `tests/pipeline/test_tools.py` - adapter tests (future)
 - Recommended profiles include Python quality tools (`ruff`, `black`, `mypy`),
   PowerShell analyzers/tests (`psscriptanalyzer`, `pester`), core test runner
   (`pytest`), optional linters/scanners (`yamllint`, `codespell`, `gitleaks`),
   and integration utilities (`aider`, `gh`).

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

Note: repository root is C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan. Docs that referenced a different root are superseded by this note.

