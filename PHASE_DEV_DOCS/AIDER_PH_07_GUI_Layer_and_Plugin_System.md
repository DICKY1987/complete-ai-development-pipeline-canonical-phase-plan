---
workstream_id: ph-07-gui-layer
phase: PH-07
difficulty: hard
version_target: v1.0
depends_on: [PH-02, PH-03, PH-05, PH-06]
writable_globs:
  - "src/gui/**/*.py"
  - "config/gui_config.yaml"
  - "config/plugins/*.plugin.json"
  - "docs/GUI_PERMISSIONS_MATRIX.md"
  - "docs/PLUGINS_SCHEMA.json"
  - "docs/PLUGINS_INTERFACE.md"
  - "templates/docs/*.template"
  - "tests/gui/**/*.py"
  - "scripts/run_gui.py"
readonly_globs:
  - "src/pipeline/db.py"
  - "src/pipeline/orchestrator.py"
  - "src/pipeline/tools.py"
  - "config/tool_profiles.json"
---

# PH-07 – GUI Layer & Plugin System (Aider Workstream)

## 1. HEADER SUMMARY

**Workstream ID:** ph-07-gui-layer
**Phase Reference:** PH-07
**Difficulty:** hard
**Version Target:** v1.0
**Dependencies:** PH-02 (DB), PH-03 (tools), PH-05 (orchestrator), PH-06 (circuit breakers)

## 2. ROLE & OBJECTIVE

Implement a PyQt6-based GUI shell with plugin architecture for the AI Development Pipeline. The GUI provides visual monitoring of runs, workstreams, tools, and logs with controlled write operations (start/pause/cancel runs, retry workstreams). This file governs only the artifacts listed in Scope.

**Mission:** Create a safe, plugin-based GUI that enforces strict permissions (read-heavy, write-light), uses service locator pattern for dependency injection, and operates as an optional layer—pipeline must work fully headless without GUI.

## 3. SCOPE & FILE BOUNDARIES

### Writable Paths
```
src/gui/shell.py
src/gui/main.py
src/gui/services/service_locator.py
src/gui/services/engine_client.py
src/gui/services/state_client.py
src/gui/services/tools_client.py
src/gui/services/logs_client.py
src/gui/services/config_client.py
src/gui/services/terminal_manager.py
src/gui/plugin_base.py
src/gui/plugin_loader.py
src/gui/panels/dashboard_panel.py
src/gui/panels/runs_panel.py
src/gui/panels/workstreams_panel.py
src/gui/panels/tools_panel.py
src/gui/panels/logs_panel.py
src/gui/panels/terminal_panel.py
config/gui_config.yaml
config/plugins/*.plugin.json
docs/GUI_PERMISSIONS_MATRIX.md
docs/PLUGINS_SCHEMA.json
docs/PLUGINS_INTERFACE.md
tests/gui/test_service_locator.py
tests/gui/test_plugin_loader.py
tests/gui/test_engine_client.py
tests/gui/test_state_client.py
tests/gui/test_logs_client.py
tests/gui/test_dashboard_panel.py
scripts/run_gui.py
```

### Read-only Reference Paths
```
src/pipeline/db.py
src/pipeline/orchestrator.py
src/pipeline/tools.py
config/tool_profiles.json
schema/schema.sql
```

### Explicitly Out of Scope
- **Do NOT** modify any file in `src/pipeline/` (except imports)
- **Do NOT** modify database schema or DB module
- **Do NOT** modify orchestrator logic or tool adapter
- **Do NOT** create CLI commands outside `scripts/run_gui.py`
- **Do NOT** add dependencies to existing modules beyond GUI layer

**Note:** All non-listed files must remain unchanged.

## 4. ENVIRONMENT & PRECONDITIONS

**Project Root:** C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan
**Operating System:** Windows 10/11
**Python Version:** 3.12+
**GUI Framework:** PyQt6
**Shell:** PowerShell 7+ (pwsh)
**Version Control:** git

**Required Prior Phases:**
- PH-00: Project skeleton, docs, CI
- PH-01: Spec index & module layout
- PH-02: SQLite DB + state machine (db.py)
- PH-03: Tool profiles & adapter (tools.py)
- PH-05: Orchestrator core loop (orchestrator.py)
- PH-06: Circuit breakers & fix loop

**Required Tools:**
- python (3.12+)
- pytest
- PyQt6 (install via: `pip install PyQt6`)
- jsonschema (for manifest validation)
- PyYAML (for config)

**Dependency Check:**
If any required module missing:
- Write note to `docs/PHASE_PLAN.md` under PH-07 section
- Add entry: "BLOCKED: Missing [module_name] from [phase]. Complete [phase] first."
- **Do NOT** implement substitute logic or stubs

## 5. TARGET ARTIFACTS & ACCEPTANCE CRITERIA

### [ARTIFACT] docs/GUI_PERMISSIONS_MATRIX.md
**Type:** doc
**Purpose:** Defines exactly what GUI is allowed to do
**Must Provide:**
- Permission levels table (none, read, write)
- Run & Workstream permissions with API mechanisms
- Tool & Plugin permissions
- Logs & Events permissions
- Config & Environment permissions (no secret viewing)
- Engine lifecycle permissions
- Terminal panel permissions
- File system permissions (no direct code/config edits)

**Must Not:**
- Allow GUI to write directly to DB or files
- Display secrets or sensitive data
- Permit destructive operations without confirmation

**Acceptance Tests:**
- Doc exists and includes all 8 permission categories
- Each category has implementation constraints table
- Permission levels clearly defined (none/read/write)

**Determinism:**
- Table format stable (columns: Capability, Level, API/Mechanism, Notes)
- Sorted alphabetically by capability within each category

---

### [ARTIFACT] docs/PLUGINS_SCHEMA.json
**Type:** config schema
**Purpose:** JSON Schema for plugin manifest validation
**Must Provide:**
- JSON Schema draft-07 format
- Required fields: id, type, title, entry_point
- Optional fields: description, category, icon, enabled_by_default, order, requires_services, version, min_gui_version, config
- Pattern constraints for id (^[a-z0-9_\\.\\-]+$) and entry_point (module:ClassName format)
- Enum for requires_services: [engine_client, state_client, tools_client, logs_client, config_client, terminal_manager]

**Must Not:**
- Allow arbitrary Python code in manifests
- Permit external imports or network calls

**Acceptance Tests:**
- Schema validates valid manifest (tests/gui/fixtures/valid.plugin.json)
- Schema rejects invalid manifests (missing id, wrong type, invalid entry_point)

**Determinism:**
- Schema fields ordered: $schema, title, description, type, required, properties
- Enum values alphabetically sorted

---

### [ARTIFACT] docs/PLUGINS_INTERFACE.md
**Type:** doc
**Purpose:** Python Protocol for panel plugins
**Must Provide:**
- ServiceLocator protocol definition
- PanelPlugin protocol with methods:
  - plugin_id() -> str (classmethod)
  - plugin_title() -> str (classmethod)
  - __init__(services, config)
  - create_widget(parent) -> QWidget
  - on_activate() -> None
  - on_deactivate() -> None
- Service names documentation
- Lifecycle rules
- Error handling strategy

**Must Not:**
- Specify implementation details (only interface contract)
- Mandate specific UI libraries beyond PyQt6

**Acceptance Tests:**
- Doc includes complete protocol definitions
- Code examples provided for PanelPluginBase usage

---

### [ARTIFACT] config/gui_config.yaml
**Type:** config
**Purpose:** GUI configuration settings
**Must Provide:**
- window: title, width, height, theme
- engine: api_base_url, timeout_ms
- state_db: path (relative to repo root)
- plugins: directory, auto_load
- terminal: default_shell, default_working_dir
- logging: level, log_file

**Must Not:**
- Contain secrets or credentials
- Use absolute paths (prefer repo-relative)

**Acceptance Tests:**
- YAML parses successfully
- All required keys present
- Paths are valid (repo-relative or absolute)

**Determinism:**
- Keys alphabetically sorted within each section
- Comments explain each setting

---

### [ARTIFACT] src/gui/shell.py
**Type:** code
**Purpose:** Main GUI window with plugin loading
**Must Provide:**
- GuiShell class (QMainWindow subclass)
- Methods:
  - __init__(config)
  - load_plugins(plugins_dir)
  - create_tab_widget()
  - handle_plugin_error(plugin_id, error)
  - show()
- Plugin discovery using plugin_loader
- ServiceLocator instantiation
- Tab widget for panels
- Lifecycle management (on_activate/on_deactivate)

**Must Not:**
- Perform heavy processing in main thread
- Directly access DB or files (use service clients)
- Crash on broken plugin (skip and log)

**Acceptance Tests:**
- test_shell_initialization (tests/gui/test_shell.py)
- test_plugin_loading_success
- test_plugin_loading_with_broken_plugin (skips gracefully)

**Determinism:**
- Plugins loaded in alphabetical order by manifest filename

---

### [ARTIFACT] src/gui/services/service_locator.py
**Type:** code
**Purpose:** Service registry for dependency injection
**Must Provide:**
- ServiceLocator class
- Methods:
  - register(name: str, instance: Any)
  - get(name: str) -> Any
  - has(name: str) -> bool
- Simple dict-based storage

**Must Not:**
- Allow service name conflicts (raise on duplicate register)
- Return None silently (raise if service not found)

**Acceptance Tests:**
- test_service_registration
- test_service_retrieval
- test_service_not_found_raises

---

### [ARTIFACT] src/gui/services/engine_client.py, state_client.py, tools_client.py, logs_client.py, config_client.py, terminal_manager.py
**Type:** code
**Purpose:** Service clients for GUI-to-pipeline communication
**Must Provide:** (per client)
- **engine_client:** health_check(), get_status(), list_runs(), get_run(), start_run(), pause_run(), resume_run(), cancel_run()
- **state_client:** query_runs(), query_workstreams(), get_workstream()
- **tools_client:** list_tools(), get_status(), start_tool(), stop_tool(), run_smoke_test()
- **logs_client:** query_events(), subscribe(), export()
- **config_client:** get_gui_config(), get_engine_config()
- **terminal_manager:** open(), close(), send_input()

**Must Not:**
- Modify DB or files directly (read-only queries via db.py)
- Block main GUI thread (future: use background workers)

**Acceptance Tests:**
- One test per service client with mocked backend

---

### [ARTIFACT] src/gui/panels/*.py (6 panel plugins)
**Type:** code
**Purpose:** Core panel plugins for Dashboard, Runs, Workstreams, Tools, Logs, Terminal
**Must Provide:** (each panel)
- PanelPlugin protocol implementation
- create_widget() returns QWidget with panel UI
- on_activate() starts timers/subscriptions
- on_deactivate() stops timers/subscriptions
- Error handling (display message if data unavailable)

**Must Not:**
- Depend on other panels
- Modify backend state without confirmation dialog
- Display secrets

**Acceptance Tests:**
- test_<panel>_widget_creation
- test_<panel>_activate_deactivate

---

### [ARTIFACT] config/plugins/*.plugin.json (6 manifests)
**Type:** config
**Purpose:** Plugin manifests for core panels
**Must Provide:**
- Valid JSON matching PLUGINS_SCHEMA.json
- id, type, title, entry_point for each panel
- requires_services list

**Acceptance Tests:**
- All manifests validate against schema

---

### [ARTIFACT] tests/gui/*.py
**Type:** test
**Purpose:** Unit tests for GUI components
**Must Provide:**
- Tests for service_locator, plugin_loader, each service client, each panel
- Use pytest with mocked services
- Coverage ≥ 80% for GUI modules

**Acceptance Tests:**
- `pytest tests/gui/` passes

---

### [ARTIFACT] scripts/run_gui.py
**Type:** script
**Purpose:** CLI entry point for GUI
**Must Provide:**
- Argument parsing (--config path)
- QApplication initialization
- Config loading and validation
- Shell creation and show
- Event loop execution

**Acceptance Tests:**
- `python scripts/run_gui.py --help` shows usage
- Script runs without errors (when config valid)

## 6. OPERATIONS SEQUENCE (Atomic Steps)

### Step 1: Design GUI Architecture
**Intent:** Plan service layer and plugin system
**Files:** /read-only docs/ARCHITECTURE.md
**Command:** `/architect`
**Prompt:**
```
Design a PyQt6 GUI architecture with:
1. Service locator pattern for dependency injection
2. Plugin discovery and loading system
3. Service clients (engine, state, tools, logs, config, terminal)
4. Panel plugin protocol (create_widget, lifecycle)
5. Error isolation (broken plugin doesn't crash GUI)

Constraints:
- No direct DB/file access (use service clients)
- Optional layer (pipeline works headlessly)
- Permissions matrix enforcement

Output: Architecture diagram (text) + key classes/interfaces
```
**Expected Outcome:** Architecture design documented in response
**Commit:** N/A (design step, no code yet)

---

### Step 2: Implement Permissions Matrix Document
**Intent:** Define GUI permission boundaries
**Files:** /add docs/GUI_PERMISSIONS_MATRIX.md
**Command:** `/code`
**Prompt:**
```
Create docs/GUI_PERMISSIONS_MATRIX.md with:

Sections:
1. Permission Levels (none, read, write)
2. Run & Workstream Permissions table
3. Tool & Plugin Permissions table
4. Logs & Events Permissions table
5. Config & Environment Permissions table
6. Engine Lifecycle Permissions table
7. Terminal Panel Permissions table
8. File System Permissions table
9. Summary

Format: Markdown tables with columns: Capability | Level | API/Mechanism | Notes

Constraints:
- GUI never displays secrets (show placeholders)
- All state changes via engine/service APIs
- Write operations require confirmation dialogs

Determinism:
- Capabilities sorted alphabetically within each category
- Consistent table formatting
```
**Expected Outcome:** Complete permissions matrix document
**Commit:** `docs(ph-07): add GUI permissions matrix`

---

### Step 3: Implement Plugin Schema
**Intent:** Create JSON Schema for plugin manifests
**Files:** /add docs/PLUGINS_SCHEMA.json
**Command:** `/code`
**Prompt:**
```
Create docs/PLUGINS_SCHEMA.json as JSON Schema draft-07 with:

Required fields:
- id: string, pattern ^[a-z0-9_\\.\\-]+$
- type: enum ["panel"]
- title: string
- entry_point: string, pattern module.path:ClassName

Optional fields:
- description, category, icon, enabled_by_default, order
- requires_services: array of enum [engine_client, state_client, tools_client, logs_client, config_client, terminal_manager]
- version, min_gui_version, config

Constraints:
- additionalProperties: false
- All patterns must be valid regex

Determinism:
- Fields ordered: $schema, title, description, type, required, properties
- Enum values sorted alphabetically
```
**Expected Outcome:** Valid JSON Schema file
**Commit:** `docs(ph-07): add plugin manifest schema`

---

### Step 4: Implement Plugin Interface Documentation
**Intent:** Document PanelPlugin protocol
**Files:** /add docs/PLUGINS_INTERFACE.md
**Command:** `/code`
**Prompt:**
```
Create docs/PLUGINS_INTERFACE.md with:

Sections:
1. Panel Plugin Basics
2. Required Class Interface (ServiceLocator Protocol, PanelPlugin Protocol)
3. Service Names (engine_client, state_client, etc.)
4. Lifecycle Rules (init, create_widget, activate, deactivate)
5. Error Handling (skip broken plugins, log errors)
6. Code Examples (PanelPluginBase usage)

Include Python code blocks with Protocol definitions

Constraints:
- Interface only (not implementation)
- Clear lifecycle order
- Error handling strategy for broken plugins
```
**Expected Outcome:** Complete interface documentation
**Commit:** `docs(ph-07): add plugin interface documentation`

---

### Step 5: Implement ServiceLocator
**Intent:** Create dependency injection registry
**Files:** /add src/gui/services/service_locator.py
**Command:** `/code`
**Prompt:**
```
Implement src/gui/services/service_locator.py:

Class: ServiceLocator
- _services: dict[str, Any] = {}

Methods:
- register(name: str, instance: Any) -> None
  - Raise ValueError if name already registered
- get(name: str) -> Any
  - Raise KeyError if name not found
- has(name: str) -> bool

Constraints:
- No external dependencies
- Thread-safe not required (single-threaded GUI)
- Clear error messages

Determinism:
- Predictable error messages with service name
```
**Expected Outcome:** ServiceLocator class with 3 methods
**Commit:** `feat(ph-07): implement service locator`

---

### Step 6: Test ServiceLocator
**Intent:** Validate service registry
**Files:** /add tests/gui/test_service_locator.py
**Command:** `/test`
**Prompt:**
```
Create tests/gui/test_service_locator.py with pytest:

Tests:
- test_register_and_get: register service, retrieve successfully
- test_get_nonexistent_raises: KeyError when service not found
- test_has_returns_true_when_present
- test_has_returns_false_when_absent
- test_duplicate_register_raises: ValueError on duplicate name

Run: pytest tests/gui/test_service_locator.py -v

Constraints:
- No mocking needed (unit test)
- Clear test names
```
**Expected Outcome:** All tests pass
**Commit:** `test(ph-07): add service locator tests`

---

### Step 7-12: Implement Service Clients
**Intent:** Create abstraction layer for GUI-to-pipeline communication
**Files:** /add src/gui/services/engine_client.py, state_client.py, tools_client.py, logs_client.py, config_client.py, terminal_manager.py
**Command:** `/code` (for each client)
**Prompt Template:**
```
Implement src/gui/services/<client_name>.py:

Class: <ClientName>
Methods: [list methods from acceptance criteria]

Implementation:
- Import required modules (orchestrator.py, db.py, tools.py as needed)
- Implement methods with proper error handling
- Return dicts for structured data
- Raise clear exceptions on failure

Constraints:
- Read-only for state_client (no DB writes)
- Use existing pipeline APIs (don't duplicate logic)
- Handle missing data gracefully (return empty list, not crash)

Example: engine_client.list_runs() calls orchestrator or db.query_runs()
```
**Expected Outcome:** 6 service client modules
**Commit:** `feat(ph-07): implement service clients (engine, state, tools, logs, config, terminal)`

---

### Step 13: Implement Plugin Base Class
**Intent:** Provide common functionality for panels
**Files:** /add src/gui/plugin_base.py
**Command:** `/code`
**Prompt:**
```
Implement src/gui/plugin_base.py:

Abstract Class: PanelPluginBase (implements PanelPlugin protocol)

Methods:
- __init__(services: ServiceLocator, config: dict | None)
- plugin_id() -> str (abstract classmethod)
- plugin_title() -> str (abstract classmethod)
- create_widget(parent) -> QWidget (abstract)
- on_activate() -> None (default empty)
- on_deactivate() -> None (default empty)

Helpers:
- _build_error_widget(message: str) -> QWidget (returns QLabel with error)
- _confirm_action(title: str, message: str) -> bool (QMessageBox confirmation)

Constraints:
- Abstract methods raise NotImplementedError
- Helpers use PyQt6 widgets
```
**Expected Outcome:** PanelPluginBase abstract class
**Commit:** `feat(ph-07): implement plugin base class`

---

### Step 14: Implement Plugin Loader
**Intent:** Discover and validate plugin manifests
**Files:** /add src/gui/plugin_loader.py
**Command:** `/code`
**Prompt:**
```
Implement src/gui/plugin_loader.py:

Functions:
- discover_plugins(plugins_dir: Path) -> list[dict]
  - Scan for *.plugin.json files
  - Load and parse JSON
  - Return list of manifest dicts

- validate_manifest(manifest: dict) -> bool
  - Validate against PLUGINS_SCHEMA.json using jsonschema
  - Return True if valid, False otherwise
  - Log validation errors

- load_plugin(manifest: dict, services: ServiceLocator) -> PanelPlugin | None
  - Import entry_point module and class
  - Instantiate with (services, manifest.get("config"))
  - Return instance or None on error
  - Log import/instantiation errors

Constraints:
- Skip broken plugins gracefully (don't crash)
- Log errors to GUI logger
- Validate before loading
```
**Expected Outcome:** Plugin discovery and loading functions
**Commit:** `feat(ph-07): implement plugin loader`

---

### Step 15-20: Implement Panel Plugins
**Intent:** Create 6 core panel plugins
**Files:** /add src/gui/panels/dashboard_panel.py, runs_panel.py, workstreams_panel.py, tools_panel.py, logs_panel.py, terminal_panel.py
**Command:** `/code` (for each panel)
**Prompt Template:**
```
Implement src/gui/panels/<panel_name>.py:

Class: <PanelName> (extends PanelPluginBase)

Methods:
- plugin_id() -> str: return "<panel_id>"
- plugin_title() -> str: return "<Panel Title>"
- create_widget(parent) -> QWidget:
  - Build UI using PyQt6 widgets
  - Connect to service clients (self._services.get("engine_client"))
  - Handle errors with _build_error_widget()
- on_activate(): start timers, subscribe to events
- on_deactivate(): stop timers, unsubscribe

UI Elements:
- [Describe specific widgets for this panel]

Constraints:
- No direct backend access (use service clients)
- Display error message if data unavailable
- Confirmation dialog for write operations

Example: runs_panel has QTableWidget for runs list, QPushButton for "Start Run"
```
**Expected Outcome:** 6 panel plugin modules
**Commit:** `feat(ph-07): implement core panel plugins (dashboard, runs, workstreams, tools, logs, terminal)`

---

### Step 21-26: Create Plugin Manifests
**Intent:** Define metadata for each panel
**Files:** /add config/plugins/dashboard.plugin.json, runs.plugin.json, workstreams.plugin.json, tools.plugin.json, logs.plugin.json, terminal.plugin.json
**Command:** `/code`
**Prompt:**
```
Create config/plugins/<panel_id>.plugin.json for each panel:

Template:
{
  "id": "<panel_id>",
  "type": "panel",
  "title": "<Panel Title>",
  "entry_point": "gui.panels.<panel_name>:<ClassName>",
  "description": "<Brief description>",
  "category": "Monitoring" | "Tools" | "Control",
  "requires_services": ["engine_client", "state_client", ...],
  "enabled_by_default": true,
  "order": <number>
}

Constraints:
- Must validate against PLUGINS_SCHEMA.json
- entry_point must match actual Python module path
```
**Expected Outcome:** 6 plugin manifest files
**Commit:** `config(ph-07): add plugin manifests for core panels`

---

### Step 27: Implement GUI Shell
**Intent:** Main window with plugin orchestration
**Files:** /add src/gui/shell.py
**Command:** `/code`
**Prompt:**
```
Implement src/gui/shell.py:

Class: GuiShell (QMainWindow)

Methods:
- __init__(config: dict)
  - Set window title, size from config
  - Create ServiceLocator and register services

- load_plugins(plugins_dir: Path)
  - Use plugin_loader.discover_plugins()
  - Validate each manifest
  - Load each plugin
  - Add to tab widget

- create_tab_widget() -> QTabWidget
  - Create main tab container
  - Return widget

- handle_plugin_error(plugin_id: str, error: Exception)
  - Log error
  - Show error tab placeholder

- show()
  - Call QMainWindow.show()

Constraints:
- Skip broken plugins (log and continue)
- Activate first tab by default
- Call on_activate() when tab selected

Determinism:
- Plugins loaded alphabetically by manifest filename
- Tabs ordered by manifest "order" field
```
**Expected Outcome:** GuiShell class
**Commit:** `feat(ph-07): implement GUI shell`

---

### Step 28: Implement GUI Main Entry Point
**Intent:** CLI entry point for GUI
**Files:** /add src/gui/main.py, scripts/run_gui.py
**Command:** `/code`
**Prompt:**
```
Implement src/gui/main.py:

Function: main(config_path: str | None = None)
- Load config from path or default config/gui_config.yaml
- Validate config
- Create QApplication
- Create GuiShell(config)
- Load plugins
- shell.show()
- sys.exit(app.exec())

Implement scripts/run_gui.py:

- Parse args (--config PATH)
- Call main(config_path)

Constraints:
- Handle config load errors gracefully
- Print error and exit if config invalid
```
**Expected Outcome:** GUI entry point
**Commit:** `feat(ph-07): implement GUI main entry point`

---

### Step 29: Create GUI Configuration
**Intent:** Default GUI settings
**Files:** /add config/gui_config.yaml
**Command:** `/code`
**Prompt:**
```
Create config/gui_config.yaml:

window:
  title: "AI Development Pipeline - GUI"
  width: 1280
  height: 800
  theme: "default"

engine:
  api_base_url: "http://localhost:8000"  # Future REST API
  timeout_ms: 5000

state_db:
  path: "pipeline.db"  # Relative to repo root

plugins:
  directory: "config/plugins"
  auto_load: true

terminal:
  default_shell: "pwsh"
  default_working_dir: "."

logging:
  level: "INFO"
  log_file: "logs/gui.log"

Constraints:
- All paths repo-relative
- Comments explain each setting
- Keys alphabetically sorted within sections
```
**Expected Outcome:** GUI config file
**Commit:** `config(ph-07): add GUI configuration`

---

### Step 30: Add GUI Tests
**Intent:** Test GUI components
**Files:** /add tests/gui/test_plugin_loader.py, test_engine_client.py, test_state_client.py, test_logs_client.py, test_dashboard_panel.py
**Command:** `/test`
**Prompt:**
```
Create tests for GUI components:

test_plugin_loader.py:
- test_discover_plugins: finds manifests in temp dir
- test_validate_manifest_valid: passes for valid manifest
- test_validate_manifest_invalid: fails for invalid manifest
- test_load_plugin_success: loads valid plugin
- test_load_plugin_broken: returns None for broken plugin

test_engine_client.py:
- Mock orchestrator.py APIs
- test_list_runs, test_start_run, test_cancel_run

test_state_client.py:
- Use temp DB
- test_query_runs, test_query_workstreams

test_logs_client.py:
- Use temp DB with sample events
- test_query_events_with_filters

test_dashboard_panel.py:
- Mock services
- test_create_widget, test_activate_deactivate

Run: pytest tests/gui/ -v

Constraints:
- Mock external dependencies
- Use pytest fixtures for setup
```
**Expected Outcome:** All GUI tests pass
**Commit:** `test(ph-07): add GUI component tests`

---

### Step 31: Update Documentation
**Intent:** Document GUI layer
**Files:** /add docs/ARCHITECTURE.md (append section), docs/PHASE_PLAN.md (append section)
**Command:** `/code`
**Prompt:**
```
Update docs/ARCHITECTURE.md:

Add section "GUI Layer & Plugin System":
- Role of GUI as optional monitoring/control interface
- Plugin architecture and service locator pattern
- Permissions matrix enforcement
- Integration with engine (orchestrator, db, tools)
- Terminal panel support

Update docs/PHASE_PLAN.md:

Add PH-07 section with:
- Summary of GUI layer
- List of artifacts (all files created)
- Note: GUI is optional; pipeline works headlessly
```
**Expected Outcome:** Documentation updated
**Commit:** `docs(ph-07): document GUI layer architecture`

---

### Step 32: Final Validation
**Intent:** Ensure all acceptance criteria met
**Command:** `/test`
**Run:**
```bash
pytest tests/gui/ -v
python scripts/run_gui.py --help
```
**Expected Outcome:** All tests pass, GUI launches

---

## 7. SLASH COMMAND PLAYBOOK

| Action | Command | Usage |
|--------|---------|-------|
| Design module architecture | `/architect` | With acceptance criteria block |
| Implement code changes | `/code` | Add only in-scope files first |
| Inspect changes | `/diff` | After each code step |
| Lint Python code | `/lint` | After implementation steps |
| Run tests | `/test` | With pytest command |
| Undo last change | `/undo` | If wrong scope touched |
| Add reference only | `/read-only` | For pipeline modules |

## 8. PROMPT TEMPLATES FOR THIS WORKSTREAM

### Design Phase Prompt
```
Design [component_name] with these requirements:
[List acceptance criteria from artifact section]

Constraints:
- [List must-not constraints]
- [File scope limits]
- [Dependency restrictions]

Output: Architecture diagram (text) + key classes/methods
```

### Implementation Prompt
```
Implement [artifact_path] with:

Must Provide:
- [List from acceptance criteria]

Must Not:
- [List from acceptance criteria]

Constraints:
- Only edit [artifact_path]
- Use imports: [allowed imports]
- No external dependencies beyond PyQt6

Determinism:
- [Ordering rules]
- [Naming conventions]
```

### Test & Validation Prompt
```
Test [component_name]:

Test Cases:
- [List from test matrix]

Commands:
- pytest tests/gui/test_[component].py -v
- [Additional validation commands]

Expected: All tests pass
```

## 9. SAFETY & GUARDRAILS

**Path Allowlist Enforcement:**
- Only touch files listed in writable_globs
- Verify with `git status` before each commit

**No Edits to Dependencies:**
- Do NOT modify src/pipeline/* (except imports)
- Do NOT modify DB schema
- Do NOT modify orchestrator or tool adapter

**Fail-Fast Rules:**
- If PH-02, PH-03, PH-05, or PH-06 incomplete: write note to docs/PHASE_PLAN.md and stop
- If PyQt6 not installed: document in README and stop

**Scope Violation Response:**
- If diff includes out-of-scope file: `/undo` and restate constraints

**Rollback Triggers:**
- Test failure: fix minimal, re-test
- Lint introduces new errors: revert change
- Plugin loading crashes shell: add try-except, log error

## 10. DETERMINISM & REPRODUCIBILITY RULES

**Stable Ordering:**
- Plugin loading: alphabetical by manifest filename
- Tab order: by manifest "order" field
- Permission matrix tables: alphabetical by capability

**Timestamp Policy:**
- Avoid timestamps in code or config
- If needed, isolate in comments or logs

**Error Messages:**
- Use stable format: "[ComponentName] Error: {specific_message}"
- No dynamic tokens in error signatures

**Idempotency:**
- Re-running same operations produces identical output
- Config loading deterministic (same file → same result)

## 11. TEST & VALIDATION MATRIX

| Criterion | Verification Command | Artifacts | Failure Handling |
|-----------|---------------------|-----------|------------------|
| ServiceLocator works | `pytest tests/gui/test_service_locator.py -v` | service_locator.py | Fix registration/retrieval logic |
| Plugin loading works | `pytest tests/gui/test_plugin_loader.py -v` | plugin_loader.py | Fix discovery or validation |
| Service clients work | `pytest tests/gui/test_*_client.py -v` | services/*.py | Mock backend properly |
| Panels create widgets | `pytest tests/gui/test_*_panel.py -v` | panels/*.py | Fix widget creation |
| Manifests validate | `jsonschema -i config/plugins/*.plugin.json docs/PLUGINS_SCHEMA.json` | *.plugin.json | Fix manifest schema |
| GUI launches | `python scripts/run_gui.py` | main.py, shell.py | Check config, imports |
| All tests pass | `pytest tests/gui/ -v` | All test files | Fix failing tests |

## 12. COMPLETION CHECKLIST

- [ ] docs/GUI_PERMISSIONS_MATRIX.md exists with 8 permission categories
- [ ] docs/PLUGINS_SCHEMA.json exists and validates manifests
- [ ] docs/PLUGINS_INTERFACE.md documents PanelPlugin protocol
- [ ] config/gui_config.yaml exists with all settings
- [ ] src/gui/services/service_locator.py implements ServiceLocator
- [ ] src/gui/services/*.py implements 6 service clients
- [ ] src/gui/plugin_base.py provides PanelPluginBase
- [ ] src/gui/plugin_loader.py handles discovery and loading
- [ ] src/gui/panels/*.py implements 6 core panels
- [ ] config/plugins/*.plugin.json contains 6 manifests
- [ ] src/gui/shell.py implements GuiShell
- [ ] src/gui/main.py + scripts/run_gui.py provide entry point
- [ ] tests/gui/*.py contains unit tests
- [ ] pytest tests/gui/ passes
- [ ] docs/ARCHITECTURE.md has GUI section
- [ ] docs/PHASE_PLAN.md has PH-07 section
- [ ] Git commit: `feat(ph-07): GUI layer and plugin system`

**Final Commit Message:**
```
feat(ph-07): GUI layer and plugin system

- Implement PyQt6 GUI shell with plugin architecture
- Add service locator for dependency injection
- Create 6 core panel plugins (dashboard, runs, workstreams, tools, logs, terminal)
- Define permissions matrix (read-heavy, write-light)
- Add plugin discovery and validation system
- GUI is optional layer; pipeline works headlessly

🤖 Generated with Aider

Co-Authored-By: Aider <noreply@aider.com>
```

## 13. APPENDIX

### Crosswalk: Codex → Aider Terms

| Codex Element | Aider Section |
|---------------|---------------|
| ROLE | Role & Objective (Section 2) |
| OPERATING CONTEXT | Environment & Preconditions (Section 4) |
| REQUIRED OUTPUTS | Target Artifacts & Acceptance Criteria (Section 5) |
| EXECUTION PLAN | Operations Sequence (Section 6) |
| CONSTRAINTS & PRINCIPLES | Safety & Guardrails + Determinism (Sections 9-10) |
| COMPLETION CHECKLIST | Completion Checklist (Section 12) |

### IDX Tag References
- None (GUI is standalone layer)

### Phase Dependencies
- PH-02 provides: db.py (for state queries)
- PH-03 provides: tools.py (for tool status)
- PH-05 provides: orchestrator.py (for run control)
- PH-06 provides: circuit breaker awareness (for logs panel)

END OF WORKSTREAM
