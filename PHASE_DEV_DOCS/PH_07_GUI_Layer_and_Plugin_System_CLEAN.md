TITLE: PH-07 -- GUI Layer & Plugin System (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-07 (GUI Layer & Plugin System) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Implement a PyQt6-based GUI shell with plugin architecture.
- Define and enforce a strict permissions matrix (read-heavy, write-light).
- Implement service locator pattern for dependency injection.
- Create core panel plugins (Dashboard, Runs, Workstreams, Tools, Logs, Terminal).
- Add GUI configuration system with validation.
- Make the GUI completely optional -- pipeline must work headlessly.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- GUI Framework: PyQt6
- Orchestrator language: Python 3.12+
- Previous phases:
  - PH-00: project skeleton, docs, CI.
  - PH-01: spec index & canonical module layout.
  - PH-02: SQLite DB + state machine (db.py).
  - PH-03: Tool profiles & adapter layer (tool_profiles.json, tools.py).
  - PH-03.5: Aider integration & prompt engine.
  - PH-04: Workstream bundle parsing & validation (bundles.py).
  - PH-04.5: Git worktree lifecycle (worktree.py).
  - PH-05: Orchestrator core loop (orchestrator.py).
  - PH-05.5: Workstream authoring & validation.
  - PH-06: Circuit breakers, retries & fix loop.

PROJECT ROOT (IMPORTANT)
- Expected project root: C:\Users\richg\ALL_AI\AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-07 that PH-00 through PH-06 must be completed first.
- Do NOT attempt to implement GUI in some other path.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-07
====================================

Create a **safe, plugin-based GUI** that:

1) Provides visual monitoring of runs, workstreams, tools, and logs.
2) Allows controlled write operations (start/pause/cancel runs, retry workstreams) with confirmation dialogs.
3) Enforces strict permissions matrix -- no direct file/DB edits, no secret viewing.
4) Uses plugin architecture for extensibility and testability.
5) Operates as an optional layer -- pipeline works fully headless without GUI.
6) Supports embedded terminal panels with env presets.

You are NOT building a full IDE or code editor. This is a **monitoring and control interface** for the pipeline orchestrator.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-07, the repo MUST have at minimum:

1) GUI PERMISSIONS MATRIX DOCUMENT
- docs/GUI_PERMISSIONS_MATRIX.md
  - Defines exactly what the GUI is allowed to do.
  - Permission levels: none, read, write.
  - Categories:
    - Run & Workstream Permissions
    - Tool & Plugin Permissions
    - Logs & Events Permissions
    - Config & Environment Permissions
    - Engine Lifecycle Permissions
    - Terminal Panel Permissions
    - File System Permissions
  - Implementation constraints for each category.
  - This is a **hard contract** for any agent implementing or modifying the GUI.

2) PLUGIN SCHEMA
- docs/PLUGINS_SCHEMA.json
  - JSON Schema draft-07 for plugin manifest files.
  - Required fields: id, type, title, entry_point.
  - Optional fields: description, category, icon, enabled_by_default, order, requires_services, version, min_gui_version, config.
  - Validates manifests stored in config/plugins/*.plugin.json.

3) PLUGIN INTERFACE DOCUMENTATION
- docs/PLUGINS_INTERFACE.md
  - Defines Python Protocol for panel plugins.
  - ServiceLocator interface.
  - PanelPlugin protocol with:
    - plugin_id(), plugin_title() class methods
    - __init__(services, config)
    - create_widget(parent) -> QWidget
    - on_activate(), on_deactivate()
  - Service names: engine_client, state_client, tools_client, logs_client, config_client, terminal_manager.
  - Lifecycle rules and error handling.

4) GUI CONFIGURATION SCHEMA
- config/gui_config.yaml
  - GUI-specific settings:
    - window.title, width, height, theme
    - engine.api_base_url, timeout_ms
    - state_db.path
    - plugins.directory, auto_load
    - terminal.default_shell, default_working_dir
    - logging.level, log_file
  - All paths relative to repo root or absolute.
  - Validate against schema on load.

5) GUI SHELL IMPLEMENTATION
- src/gui/shell.py
  - Main GUI window class (QMainWindow).
  - Loads plugin manifests from config/plugins/.
  - Validates plugins against PLUGINS_SCHEMA.json.
  - Instantiates plugins with ServiceLocator.
  - Creates tab widget for panel plugins.
  - Handles lifecycle (on_activate/on_deactivate).
  - Error handling for broken plugins (skip and log).

- src/gui/main.py
  - Entry point for GUI application.
  - Parses CLI arguments (--config path/to/gui_config.yaml).
  - Initializes QApplication.
  - Loads gui_config.yaml.
  - Creates and shows shell window.
  - Runs event loop.

6) SERVICE CLIENTS
Implement abstraction layer between GUI and pipeline:

- src/gui/services/engine_client.py
  - health_check() -> bool
  - get_status() -> dict
  - list_runs() -> list[dict]
  - get_run(run_id) -> dict
  - start_run(change_id, opts) -> run_id
  - pause_run(run_id) -> bool
  - resume_run(run_id) -> bool
  - cancel_run(run_id) -> bool
  - Uses orchestrator.py APIs or future REST API.

- src/gui/services/state_client.py
  - query_runs(filters) -> list[dict]
  - query_workstreams(run_id) -> list[dict]
  - get_workstream(ws_id) -> dict
  - Uses db.py read-only queries.

- src/gui/services/tools_client.py
  - list_tools() -> list[dict]
  - get_status(tool_id) -> dict
  - start_tool(tool_id) -> bool
  - stop_tool(tool_id) -> bool
  - run_smoke_test(tool_id) -> dict
  - Uses tools.py APIs.

- src/gui/services/logs_client.py
  - query_events(filters) -> list[dict]
  - subscribe(callback) -> subscription_id
  - export(run_id, output_path) -> bool
  - Uses db.py events table.

- src/gui/services/config_client.py
  - get_gui_config() -> dict
  - get_engine_config() -> dict (non-sensitive only)
  - Loads from config/ files.

- src/gui/services/terminal_manager.py
  - open(preset, working_dir) -> tab_id
  - close(tab_id) -> bool
  - send_input(tab_id, text) -> bool
  - Uses QTermWidget or equivalent.

- src/gui/services/service_locator.py
  - get(name: str) -> Any
  - has(name: str) -> bool
  - register(name: str, instance: Any)
  - Simple dict-based registry.

7) CORE PANEL PLUGINS
Create default panels as plugins:

- src/gui/panels/dashboard_panel.py
  - Manifest: config/plugins/dashboard.plugin.json
  - Shows: summary stats, recent runs, active workstreams.
  - Requires: engine_client, state_client.

- src/gui/panels/runs_panel.py
  - Manifest: config/plugins/runs.plugin.json
  - Shows: table of all runs (filterable, sortable).
  - Actions: start new run (with confirmation dialog), cancel run.
  - Requires: engine_client, state_client.

- src/gui/panels/workstreams_panel.py
  - Manifest: config/plugins/workstreams.plugin.json
  - Shows: list of workstreams for selected run.
  - Actions: retry workstream (with confirmation).
  - Requires: engine_client, state_client.

- src/gui/panels/tools_panel.py
  - Manifest: config/plugins/tools.plugin.json
  - Shows: configured tools, health status.
  - Actions: run smoke test, start/stop managed tools.
  - Requires: tools_client.

- src/gui/panels/logs_panel.py
  - Manifest: config/plugins/logs.plugin.json
  - Shows: event log with filters (run, ws, severity, time).
  - Actions: export logs to file, clear filters.
  - Requires: logs_client.

- src/gui/panels/terminal_panel.py
  - Manifest: config/plugins/terminal.plugin.json
  - Shows: embedded terminal tabs with presets.
  - Actions: open new terminal, close terminal, send input.
  - Requires: terminal_manager.

Each panel plugin must:
- Implement PanelPlugin protocol.
- Have a corresponding .plugin.json manifest.
- Handle errors gracefully (display error message in panel if data unavailable).

8) BASE CLASSES FOR PLUGINS
- src/gui/plugin_base.py
  - PanelPluginBase abstract class implementing PanelPlugin protocol.
  - Provides common helpers:
    - _build_error_widget(message) -> QWidget
    - _confirm_action(title, message) -> bool (QMessageBox)
  - Handles ServiceLocator storage.

9) PLUGIN DISCOVERY & LOADING
- src/gui/plugin_loader.py
  - discover_plugins(plugins_dir) -> list[PluginManifest]
  - load_plugin(manifest, services) -> PanelPlugin instance
  - validate_manifest(manifest_data) -> bool (against PLUGINS_SCHEMA.json)
  - Error handling: skip broken plugins, log to GUI logs panel.

10) UNIT TESTS
- tests/gui/test_service_locator.py
  - Test registration, retrieval, has() checks.

- tests/gui/test_plugin_loader.py
  - Test discovery from config/plugins/.
  - Test manifest validation (valid/invalid cases).
  - Test plugin instantiation with mocked services.

- tests/gui/test_engine_client.py
  - Mock orchestrator.py APIs.
  - Test run lifecycle methods (start, pause, resume, cancel).

- tests/gui/test_state_client.py
  - Use temp DB.
  - Test run/workstream queries.

- tests/gui/test_logs_client.py
  - Use temp DB with sample events.
  - Test event queries with filters.

- tests/gui/test_dashboard_panel.py
  - Use mocked services.
  - Test widget creation.
  - Test on_activate/on_deactivate.

(Similar tests for other panel plugins.)

Use pytest and PyQt6 testing utilities. GUI tests may use QTest or simple assertions on widget properties.

11) CLI ENTRY POINT
- scripts/run_gui.py
  - Runnable as:
    - python scripts/run_gui.py
    - python scripts/run_gui.py --config path/to/gui_config.yaml
  - Calls src/gui/main.py.

12) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add "GUI Layer & Plugin System" section describing:
    - Role of GUI as optional monitoring/control interface.
    - Plugin architecture and service locator pattern.
    - Permissions matrix enforcement.
    - Integration with engine (orchestrator, db, tools).
    - Terminal panel support.

- docs/PHASE_PLAN.md:
  - Flesh out PH-07 section with:
    - Summary of GUI layer and plugin system.
    - List of artifacts:
      - docs/GUI_PERMISSIONS_MATRIX.md
      - docs/PLUGINS_SCHEMA.json
      - docs/PLUGINS_INTERFACE.md
      - config/gui_config.yaml
      - src/gui/shell.py, main.py
      - src/gui/services/*.py
      - src/gui/panels/*.py
      - config/plugins/*.plugin.json
      - tests/gui/*.py
    - Note that GUI is optional; pipeline works headlessly.

- README.md:
  - Add "Running the GUI" section:
    - Install PyQt6: pip install PyQt6
    - Run GUI: python scripts/run_gui.py
    - Note: GUI requires PH-00 through PH-06 to be complete for full functionality.

13) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-07: GUI layer and plugin system"
- Do NOT push (remote configuration is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00 through PH-06; only extend them.
- GUI MUST be optional:
  - All pipeline operations must work headlessly via CLI.
  - GUI is a view/controller layer, not core logic.
- Enforce permissions matrix strictly:
  - GUI never writes directly to DB or files.
  - All state changes go through engine/service APIs.
  - Secrets never displayed (show placeholders).
- Plugin isolation:
  - Plugins must not depend on each other.
  - Broken plugin should not crash GUI (skip and log error).
- Keep GUI lightweight:
  - No heavy processing in GUI thread.
  - Use background threads/workers for long operations (future enhancement).
- Testing:
  - Mock services for unit tests.
  - Test plugin loading, validation, lifecycle.

Implementation details:
- Use PyQt6 for GUI framework.
- Use jsonschema for manifest validation.
- Use PyYAML for gui_config.yaml.
- For terminal panel:
  - Use QProcess or QTermWidget (if available).
  - Fallback: simple command output display if full terminal emulation unavailable.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:\Users\richg\ALL_AI\AI_Dev_Pipeline exists.
   - cd C:\Users\richg\ALL_AI\AI_Dev_Pipeline
   - Confirm src/pipeline/, docs/, config/ exist; if not, create them and note in docs/PHASE_PLAN.md that earlier phases may be incomplete.

2) WRITE PERMISSIONS MATRIX DOC
   - Create docs/GUI_PERMISSIONS_MATRIX.md with:
     - Permission levels (none, read, write).
     - Detailed tables for each category.
     - Implementation constraints.

3) CREATE PLUGIN SCHEMA
   - Create docs/PLUGINS_SCHEMA.json with:
     - JSON Schema draft-07.
     - All required and optional fields.
     - Pattern constraints for id and entry_point.

4) WRITE PLUGIN INTERFACE DOC
   - Create docs/PLUGINS_INTERFACE.md with:
     - ServiceLocator protocol.
     - PanelPlugin protocol.
     - Lifecycle rules.
     - Error handling.
     - Code examples.

5) CREATE GUI CONFIG SCHEMA
   - Create config/gui_config.yaml with:
     - Default values for all settings.
     - Comments explaining each field.

6) IMPLEMENT SERVICE CLIENTS
   - Create src/gui/services/ directory.
   - Implement each service client (*_client.py).
   - Implement service_locator.py.

7) IMPLEMENT GUI SHELL
   - Create src/gui/shell.py with:
     - Main window class.
     - Plugin discovery and loading.
     - Tab widget for panels.
     - Lifecycle management.
   - Create src/gui/main.py with:
     - QApplication initialization.
     - Config loading.
     - Shell creation and show.

8) IMPLEMENT PLUGIN BASE CLASS
   - Create src/gui/plugin_base.py with:
     - PanelPluginBase abstract class.
     - Helper methods for common UI patterns.

9) IMPLEMENT PLUGIN LOADER
   - Create src/gui/plugin_loader.py with:
     - discover_plugins().
     - load_plugin().
     - validate_manifest().

10) CREATE CORE PANEL PLUGINS
    - Create src/gui/panels/ directory.
    - Implement each panel plugin (*_panel.py).
    - Create corresponding manifests in config/plugins/*.plugin.json.

11) ADD CLI ENTRY POINT
    - Create scripts/run_gui.py.

12) ADD TESTS
    - Create tests/gui/ directory.
    - Implement unit tests for:
      - service_locator
      - plugin_loader
      - service clients
      - panel plugins
    - Use pytest with PyQt6 testing support.

13) RUN TESTS
    - From project root:
      - Run: pytest tests/gui/
    - Fix any failing tests before marking PH-07 complete.

14) UPDATE DOCS
    - Update docs/ARCHITECTURE.md with GUI layer section.
    - Update docs/PHASE_PLAN.md with detailed PH-07 description.
    - Update README.md with GUI usage instructions.

15) GIT COMMIT
    - Stage and commit with message:
      - "PH-07: GUI layer and plugin system"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-07 done, ensure all of the following are true:

[ ] docs/GUI_PERMISSIONS_MATRIX.md exists and defines permission levels and constraints for all categories
[ ] docs/PLUGINS_SCHEMA.json exists and provides valid JSON Schema for plugin manifests
[ ] docs/PLUGINS_INTERFACE.md exists and documents PanelPlugin protocol and lifecycle
[ ] config/gui_config.yaml exists with default GUI configuration
[ ] src/gui/shell.py implements main GUI window with plugin loading and lifecycle
[ ] src/gui/main.py provides GUI entry point
[ ] src/gui/services/ contains all service clients:
    - engine_client.py
    - state_client.py
    - tools_client.py
    - logs_client.py
    - config_client.py
    - terminal_manager.py
    - service_locator.py
[ ] src/gui/plugin_base.py provides PanelPluginBase abstract class
[ ] src/gui/plugin_loader.py handles plugin discovery and loading
[ ] src/gui/panels/ contains core panel plugins:
    - dashboard_panel.py
    - runs_panel.py
    - workstreams_panel.py
    - tools_panel.py
    - logs_panel.py
    - terminal_panel.py
[ ] config/plugins/ contains plugin manifests for all core panels
[ ] scripts/run_gui.py provides CLI entry point for GUI
[ ] tests/gui/ contains unit tests for service locator, plugin loader, services, and panels
[ ] pytest passes successfully for all GUI tests
[ ] docs/ARCHITECTURE.md has a "GUI Layer & Plugin System" section
[ ] docs/PHASE_PLAN.md has an updated PH-07 section listing artifacts and behavior
[ ] README.md has "Running the GUI" section
[ ] A git commit with message like "PH-07: GUI layer and plugin system" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - docs/GUI_PERMISSIONS_MATRIX.md
  - docs/PLUGINS_INTERFACE.md
  - docs/PHASE_PLAN.md (PH-07 section)
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python, YAML, JSON, and Markdown file contents you would create or modify.

END OF PROMPT
