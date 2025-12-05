---
doc_id: DOC-GUIDE-DOC-UI-ARCHITECTURE-OVERVIEW-744
status: draft
doc_type: guide
module_refs:
  - gui_components
  - tui_app
---

# UI Architecture Overview

## 1. Purpose & Scope

This document defines the unified UI architecture for the AI Development Pipeline, across:

- The existing TUI (Textual-based Terminal UI), and
- A future GUI (desktop "windowed" UI).

The goal is:

> TUI and GUI are just different "shells" around a shared, deterministic UI core that understands pipeline state, pattern execution, and logs.

The TUI implementation is real and production-leaning.
The GUI is not implemented yet but must be architecturally isomorphic to the TUI:

- Same data contracts (state, patterns, logs)
- Same panel/plugin model
- Same configuration and theme sources
- Same "mission control" concepts (dashboard, file lifecycle, tool health, logs, pattern activity)

---

## 2. High-Level UI Stack

At a high level:

```text
+-----------------------------------------------------------+
|            AI Development Pipeline (Core Engine)          |
|  - UET executions, tasks, patterns, patch ledger, logs    |
+--------------------------+--------------------------------+
                           |
                           v
+-----------------------------------------------------------+
|                 UI Core (Shared Domain Layer)             |
|  - StateClient / StateBackend                             |
|  - PatternClient / PatternStateStore                      |
|  - LayoutConfig (theme, refresh, log sources)             |
|  - PanelPlugin / PanelContext / PanelRegistry             |
+--------------------------+--------------------------------+
       |                                   |
       v                                   v
+---------------------------+   +----------------------------+
|        TUI Shell          |   |        GUI Shell           |
|  - Textual App            |   |  - Desktop app framework   |
|  - Dashboard panel        |   |  - Dashboard screen        |
|  - File lifecycle panel   |   |  - File lifecycle view     |
|  - Tool health panel      |   |  - Tool health view        |
|  - Log stream panel       |   |  - Log stream view         |
|  - Pattern activity panel |   |  - Pattern activity view   |
+---------------------------+   +----------------------------+
```

The UI Core (Shared Domain Layer) is the key: if it stays clean and Textual-agnostic, the GUI can reuse it with minimal friction.

---

## 3. Shared Domain Layer

### 3.1 State Client & Backends

**Files:**

* `tui_app/core/state_client.py`
* `tui_app/core/sqlite_state_backend.py`

**Types (conceptual):**

* `StateBackend` (ABC)

  * `get_pipeline_summary() -> PipelineSummary`
  * `get_tasks(...) -> list[TaskInfo]`
  * `get_task(task_id) -> Optional[TaskInfo]`
  * `get_executions(...) -> list[ExecutionInfo]`
  * `get_patch_ledger(...) -> list[PatchLedgerEntry]`
* `InMemoryStateBackend(StateBackend)`
* `SQLiteStateBackend(StateBackend)`
* `StateClient`

  * Thin facade that panels use instead of raw backends.

**Design Rule:**

* All UI shells (TUI, GUI, future web) must use `StateClient`, never talk directly to SQLite or other storage.
* To add a new data source (e.g., REST API or HTTP-based state service), implement a new `StateBackend` and keep the `StateClient` API stable.

---

### 3.2 Pattern Client & Pattern State Store

**File:**

* `tui_app/core/pattern_client.py`

**Types (conceptual):**

* `PatternRun`, `PatternEvent`, `PatternStatus`, `PatternEventType`
* `PatternStateStore` (ABC)

  * `get_recent_runs(...)`
  * `get_run_events(run_id)`
  * `get_active_patterns(...)`
* `InMemoryPatternStateStore`
* `SQLitePatternStateStore`
* `PatternClient`

  * UI-facing facade over pattern state stores.

**Design Rule:**

* Panels/screens that visualize pattern execution must only depend on `PatternClient`.
* `PatternClient` must not depend on Textual or any GUI framework.

---

### 3.3 Layout & Theme Config

**File:**

* `tui_app/core/layout_config.py`
* `tui_app/config/tui_config.yaml`

**Concepts:**

* `TUIConfig`:

  * `theme_css_path`
  * `panel_refresh: { dashboard, file_lifecycle, tool_health, log_stream, pattern_activity }`
  * `log_config: { path, max_lines }`
  * Other visual settings.

**Design Rule:**

* Config is the single source of truth for refresh cadence, log locations, themes, and layout defaults.
* GUI must:

  * Either reuse `TUIConfig` directly, or
  * Provide a sibling config (`GUIConfig`) with the same semantic fields, referenced from a shared `LayoutConfig` module.

---

### 3.4 Panel Plugin, Context & Registry

**Files:**

* `tui_app/core/panel_plugin.py`
* `tui_app/core/panel_registry.py`

**Key Types:**

* `PanelContext`

  * `state_client: Optional[StateClient]`
  * `pattern_client: Optional[PatternClient]`
  * `config: TUIConfig` (generic config object)
  * `event_bus: Optional[Any]` (future pub/sub)
* `PanelPlugin` (protocol)

  * `panel_id: str`
  * `title: str`
  * `create_widget(context: PanelContext) -> WidgetType`
  * `on_mount(context: PanelContext) -> None`
  * `on_unmount(context: PanelContext) -> None`
* `PanelRegistry`

  * `register(panel_id, plugin_cls)`
  * `create_panel(panel_id, context)`
  * `list_panels()`

**Design Rule:**

* PanelPlugin is the core abstraction across TUI and GUI.

* For GUI, there are two options (pick one and keep it consistent):

  1. Shared `PanelPlugin` interface

     * Same logical contract, but `create_widget` returns a GUI widget instead of a Textual widget, in a separate registry module (e.g. `gui_app/core/panel_plugin.py`).
     * Panel IDs, titles, and semantics remain the same.

  2. Dual plugin types but same IDs and context

     * `TuiPanelPlugin` and `GuiPanelPlugin` both consume the same `PanelContext` and share the same `panel_id`.
     * A higher-level registry maps one logical panel to both shells.

* Panel IDs must be stable across shells:

  | Logical panel    | Panel ID           |
  | ---------------- | ------------------ |
  | Dashboard        | `dashboard`        |
  | File lifecycle   | `file_lifecycle`   |
  | Tool health      | `tool_health`      |
  | Log stream       | `log_stream`       |
  | Pattern activity | `pattern_activity` |

---

## 4. TUI Implementation (Current State)

### 4.1 TUI App & Layout

**File:**

* `tui_app/main.py` (`PipelineTUI`)

Responsibilities:

* Parse CLI flags:

  * `--panel`, `--layout [single|dual]`, `--secondary-panel`
  * `--use-mock-data`, `--smoke-test`
* Load `TUIConfig` and theme CSS.
* Instantiate `StateClient` + `PatternClient` with either:

  * `SQLiteStateBackend` / `SQLitePatternStateStore`, or
  * In-memory test backends.
* Use `PanelRegistry` and a `LayoutManager` to:

  * Mount the chosen primary panel.
  * Optionally mount a secondary panel for dual-pane layouts.
* Define key bindings:

  * `q` (quit), `r` (refresh), `d/f/t/l/p` (switch panels).

### 4.2 Layout Managers

**File:**

* `tui_app/core/layout_manager.py`

Types:

* `BasicLayoutManager`

  * Holds current `PanelPlugin` instance + `PanelContext`.
  * Handles `mount(panel_id)`, `unmount_current()`, and safe transitions.
* `MultiPanelLayoutManager` (placeholder)

  * Reserved for more complex layouts (grid, multi-pane, etc.).

**Design Rule:**

* LayoutManagers understand how panels are arranged, not what panels show.
* GUI should implement an analogous layout manager:

  * E.g., `BasicGuiLayoutManager`, `TabbedLayoutManager`, etc.
  * Reuse panel IDs and contexts.

---

## 4.3 Existing Panels (TUI)

Each TUI panel:

* Implements `PanelPlugin`
* Is registered via `@register_panel("panel_id")`
* Creates a Textual widget tree that consumes `StateClient` / `PatternClient`

| Panel            | Data source(s)                                    | Primary purpose                                |
| ---------------- | ------------------------------------------------- | ---------------------------------------------- |
| Dashboard        | `StateClient.get_pipeline_summary`, `get_tasks`   | High-level overview of pipeline + recent tasks |
| File Lifecycle   | `StateClient.get_patch_ledger`, `get_executions`  | Visualize patch ledger and file touch history  |
| Tool Health      | Log file via `LogConfig.path`                     | Aggregate tool errors/warnings by tool name    |
| Log Stream       | Log file via `LogConfig.path`                     | Tail pipeline log, show last N lines           |
| Pattern Activity | `PatternClient.get_recent_runs`, `get_run_events` | Timeline of pattern runs and events            |

---

## 5. Future GUI Shell: Design Approach

The GUI shell should:

1. Reuse the shared domain layer unchanged:

   * Import `StateClient`, `PatternClient`, and config loaders from a neutral module (e.g. `ui_core/` or `shared_ui/`).
2. Implement GUI-specific widget/component classes that mirror TUI panel behavior.
3. Preserve panel IDs and semantics:

   * A GUI "Dashboard" tab should be bound to `panel_id="dashboard"` and show the same information as the TUI Dashboard.

### 5.1 Suggested Package Structure

Example structure (to be adapted to your actual repo):

```text
ui_core/
  __init__.py
  state_client.py
  sqlite_state_backend.py
  pattern_client.py
  layout_config.py
  panel_core.py       # PanelContext, PanelRegistry, shared types

tui_app/
  main.py
  panels/
    dashboard_panel.py
    file_lifecycle_panel.py
    tool_health_panel.py
    log_stream_panel.py
    pattern_activity_panel.py
  core/
    layout_manager.py
    # re-export PanelRegistry from ui_core.panel_core

gui_app/
  main.py
  windows/
    dashboard_window.py
    file_lifecycle_window.py
    tool_health_window.py
    log_stream_window.py
    pattern_activity_window.py
  core/
    gui_layout_manager.py
    gui_panel_registry.py  # or reuse shared registry
```

Key points:

* `ui_core` contains only non-framework-specific code.
* `tui_app` and `gui_app` are thin shells around `ui_core`.

### 5.2 GUI Layout Parity

For minimum friction, the GUI should provide:

* A Dashboard view (default tab or screen).
* Tabs or left navigation for:

  * File Lifecycle
  * Tool Health
  * Log Stream
  * Pattern Activity
* Optional:

  * Split-pane layouts that mirror the TUI dual-panel mode:

    * Example: Dashboard on top, Log Stream on bottom.

---

## 6. Panel Design Contract Across TUI & GUI

For each logical panel (Dashboard, File Lifecycle, etc.):

1. Input Contract

   * Receives a `PanelContext` (or GUI equivalent) with:

     * `state_client`
     * `pattern_client`
     * `config`
   * Must not open files, DBs, or network connections directly.

2. Data Selection Rules

   * Dashboard:

     * Uses `get_pipeline_summary`, recent tasks ordered by time.
   * File Lifecycle:

     * Uses `get_patch_ledger` plus `get_executions` for correlation.
   * Tool Health:

     * Reads logs via `LogConfig.path`, groups by `toolName` or similar.
   * Log Stream:

     * Reads the same log file, showing the last N lines.
   * Pattern Activity:

     * Uses `PatternClient` to fetch runs/events; no direct DB access.

3. Output Contract

   * TUI:

     * Returns a Textual widget (e.g. `Container`, `DataTable`, etc.).
   * GUI:

     * Returns a GUI widget (e.g. top-level window, tab content, or frame).
   * Either way:

     * The information shown must be semantically equivalent.

4. Refresh & Auto-Update

   * Refresh interval taken from config (panel-specific).
   * Any internal timers or scheduled updates must respect `PanelRefreshConfig`.

---

## 7. Extensibility & Evolution

### 7.1 Adding a New Panel (Both Shells)

1. Define Data Needs:

   * What does the panel need from `StateClient` / `PatternClient` / logs?
   * If new queries are needed, add them to `StateBackend` / `PatternStateStore` first.

2. Extend Shared Domain Types (if required):

   * Add new dataclasses or methods in `ui_core/state_client.py` or `ui_core/pattern_client.py`.

3. Register Panel:

   * Add entry to `PanelRegistry` with a unique `panel_id`.
   * Extend `UI_DOCUMENTATION_INDEX` with a new row and status.

4. Implement TUI Panel:

   * In `tui_app/panels/<name>_panel.py`, implement `PanelPlugin`.
   * Use `PanelContext` to access the clients and config.

5. Implement GUI View:

   * In `gui_app/windows/<name>_window.py`, implement the GUI view bound to the same `panel_id`.
   * Consume the same shared domain APIs.

6. Add Tests:

   * Extend existing test suites to cover:

     * New `StateClient`/`PatternClient` methods.
     * New panel registration and basic rendering (smoke tests).

---

## 8. Testing & CI Expectations

* Core domain tests:

  * Validate `SQLiteStateBackend` schema assumptions.
  * Validate `PatternClient` mapping from executions/tasks to pattern runs/events.
* Panel-level tests (TUI):

  * Existing tests for `PanelRegistry` and `BasicLayoutManager` must remain green.
  * Add panel-specific tests for:

    * Data transformation (e.g. how logs are aggregated in Tool Health).
* GUI tests:

  * Once implemented, add smoke tests ensuring:

    * Each panel/screen can be created successfully with a fake `PanelContext`.
    * No framework-specific exceptions on startup.

---

## 9. Roadmap (Draft)

1. Extract `ui_core/` from TUI code:

   * Move `StateClient`, `PatternClient`, `LayoutConfig`, `PanelContext`, `PanelRegistry` to a framework-agnostic package.

2. Refine Panel Contracts:

   * Document each panel's input data and output semantics in a small spec file.

3. Prototype GUI Shell:

   * Implement a minimal GUI with:

     * One main window
     * Tabs for Dashboard + Log Stream, reusing `ui_core`.

4. Backfill Documentation:

   * Update:

     * `UI_DOCUMENTATION_INDEX.md`
     * `TUI_PANEL_FRAMEWORK_GUIDE.md`
     * New `GUI_DEVELOPMENT_GUIDE.md`
   * Ensure both shells reference this architecture overview as the single source of truth.

---

## 10. Summary

* The TUI is the reference implementation of the UI stack.
* The UI Core (state, pattern, config, panel contracts) must be reusable and framework-neutral.
* A future GUI should be a thin shell that:

  * Uses the same data contracts,
  * Implements the same panels by `panel_id`,
  * Provides equivalent views into the pipeline's state, patterns, and logs.

Treat this document as the single source of truth for how any new UI (TUI, GUI, web) must integrate with the AI Development Pipeline.
