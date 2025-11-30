# GUI Components and Design Documentation

**Purpose**: Hybrid GUI/Terminal/TUI architecture design documents, specifications, and interface definitions for the standalone execution engine.

## Overview

The `gui/` directory contains design documentation for the hybrid GUI layer that provides visual monitoring and control of the AI Development Pipeline execution engine. This is **design documentation only** - implementation lives in `engine/`.

## Structure

```
gui/
├── GUI_PIPELINE.txt                # GUI pipeline architecture overview
├── GUI_PIPELINE_SPEC.txt           # Detailed GUI specifications
├── GUI_PERMISSIONS_MATRIX.md       # What GUI can/cannot do
├── Hybrid UI_GUI shell_terminal_TUI engine.md  # Hybrid architecture design
├── Pipeline Radar" plugin.md       # Real-time pipeline monitoring plugin
├── Plan Map coreStructure to engine Hybrid Architecture.md  # Migration plan
├── Top-level layout split GUI vs Engine vs Specs.md  # Architecture boundaries
└── AIM_ai-steward.md              # AI steward assistant integration
```

## Core Design Documents

### GUI Pipeline Architecture

**File**: `GUI_PIPELINE.txt`

**Purpose**: High-level overview of GUI layer architecture and design principles.

**Key Topics**:
- Separation of concerns (GUI vs Engine)
- Event-driven architecture
- Real-time monitoring
- User interaction patterns
- Security boundaries

**Design Principles**:
- **Read-mostly**: GUI primarily observes, rarely mutates state
- **Headless-first**: Everything GUI does must work via CLI/API
- **Safe-by-default**: Explicit user confirmation for destructive actions
- **Real-time**: Live updates via websockets or polling
- **Modular**: Panel-based design for extensibility

### GUI Pipeline Specification

**File**: `GUI_PIPELINE_SPEC.txt`

**Purpose**: Detailed technical specification for GUI implementation.

**Contents**:
- Panel definitions (Runs, Workstreams, Logs, Settings)
- API contracts for GUI ↔ Engine communication
- Data models and state synchronization
- Error handling and edge cases
- Performance requirements

**Panel Specifications**:

#### Runs Panel
- **Purpose**: Display all pipeline runs with status, timing, and progress
- **Data Source**: `engine.list_runs()`
- **Update Frequency**: 1-2 seconds (configurable)
- **Actions**: Start new run, pause, resume, cancel

#### Workstreams Panel
- **Purpose**: Show workstreams within selected run
- **Data Source**: `engine.list_workstreams(run_id)`
- **Update Frequency**: Real-time
- **Actions**: View workstream details, retry failed workstream

#### Logs Panel
- **Purpose**: Streaming log output from engine and tools
- **Data Source**: `engine.get_logs(run_id)` or log files
- **Update Frequency**: Real-time streaming
- **Actions**: Filter by level, search, export

#### Settings Panel
- **Purpose**: Configure engine behavior and tool execution modes
- **Data Source**: `config/ui_settings.yaml`
- **Actions**: Toggle headless modes, adjust thresholds, save settings

### GUI Permissions Matrix

**File**: `GUI_PERMISSIONS_MATRIX.md`

**Purpose**: Defines exactly what the GUI is allowed to do with respect to the engine, tools, and local environment.

**Permission Levels**:
- **none**: GUI cannot perform action
- **read**: GUI can view but not modify
- **write**: GUI can perform action (with confirmation)

**Matrix**:

| Capability | Level | API | Notes |
|------------|-------|-----|-------|
| List runs | read | `engine.list_runs()` | Dashboard, Runs panel |
| Start run | write | `engine.start_run(change_id)` | Requires confirmation |
| Pause run | write | `engine.pause_run(run_id)` | Graceful pause |
| Cancel run | write | `engine.cancel_run(run_id)` | Requires confirmation |
| View logs | read | `engine.get_logs(run_id)` | Logs panel |
| Modify code | none | N/A | GUI never edits code |
| Install tools | none | N/A | Use AIM CLI instead |

**Security Constraints**:
- GUI **never** executes arbitrary commands
- All actions go through engine API
- No direct file system access (read logs via API only)
- Tool execution controlled by engine, not GUI

### Hybrid UI Architecture

**File**: `Hybrid UI_GUI shell_terminal_TUI engine.md`

**Purpose**: Design for supporting GUI, terminal, and TUI interfaces from single engine.

**Modes**:
1. **GUI Mode**: Rich visual interface (tkinter, PyQt, or web-based)
2. **TUI Mode**: Terminal UI (rich, textual)
3. **CLI Mode**: Pure command-line with structured output (JSON/YAML)

**Architecture**:
```
┌─────────────────────────────────────┐
│         Interface Layer             │
│  ┌─────┐  ┌─────┐  ┌─────┐         │
│  │ GUI │  │ TUI │  │ CLI │         │
│  └──┬──┘  └──┬──┘  └──┬──┘         │
│     └────────┼────────┘             │
│              │                      │
│    ┌─────────▼─────────┐           │
│    │   Engine API      │           │
│    │  (JSON-RPC/REST)  │           │
│    └─────────┬─────────┘           │
│              │                      │
│    ┌─────────▼─────────┐           │
│    │  Execution Engine │           │
│    │  (engine/)        │           │
│    └───────────────────┘           │
└─────────────────────────────────────┘
```

**Interface Selection**:
```bash
# GUI mode
python -m engine.run --ui=gui

# TUI mode
python -m engine.run --ui=tui

# CLI mode (default)
python -m engine.run --ui=cli --output=json
```

### Pipeline Radar Plugin

**File**: `Pipeline Radar" plugin.md`

**Purpose**: Real-time pipeline monitoring plugin design.

**Features**:
- **Live status visualization**: Runs, workstreams, steps
- **Progress tracking**: Per-step and overall completion
- **Error highlighting**: Failed steps, quality gate violations
- **Performance metrics**: Duration, throughput, bottlenecks

**Visualization Concepts**:
```
Pipeline Radar
══════════════════════════════════════
Run: ci-validation-001  [████████░░] 80%

Workstreams:
  ✓ validate-python   [Complete] 2.3s
  ⏳ validate-docs     [Running]  1.1s
  ○ validate-config   [Pending]  -

Recent Errors:
  ⚠ ruff: E501 line too long (file.py:42)
  ⚠ mypy: Incompatible types (module.py:15)

Performance:
  Throughput: 12 files/sec
  Avg step duration: 1.8s
```

### Architecture Migration Plan

**File**: `Plan Map coreStructure to engine Hybrid Architecture.md`

**Purpose**: Plan for migrating from monolithic core to hybrid GUI/Engine architecture.

**Migration Phases**:
1. **Phase 1**: Extract engine API from `core/engine/`
2. **Phase 2**: Build headless CLI interface
3. **Phase 3**: Add TUI layer using `rich`/`textual`
4. **Phase 4**: Implement GUI layer (web-based or desktop)
5. **Phase 5**: Deprecate direct `core/` access in favor of API

**Compatibility Strategy**:
- Maintain backward compatibility with existing `core/` imports
- Gradual migration, not big-bang rewrite
- Parallel operation: old and new APIs coexist

### Top-Level Architecture Split

**File**: `Top-level layout split GUI vs Engine vs Specs.md`

**Purpose**: Defines clear boundaries between GUI, Engine, and Specifications.

**Boundaries**:

```
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│     GUI     │   │    Engine    │   │    Specs     │
│  (gui/)     │──▶│  (engine/)   │──▶│ (spec/)      │
│             │   │              │   │              │
│ - Panels    │   │ - Job Queue  │   │ - OpenSpec   │
│ - Widgets   │   │ - Workers    │   │ - Workstreams│
│ - Events    │   │ - Adapters   │   │ - Schemas    │
└─────────────┘   └──────────────┘   └──────────────┘
```

**Rules**:
- **GUI → Engine**: Via API only (JSON-RPC, REST, or Python API)
- **Engine → Specs**: Load/validate workstreams, no modification
- **GUI → Specs**: Read-only access for display
- **No circular dependencies**: GUI never imported by Engine

### AI Steward Integration

**File**: `AIM_ai-steward.md`

**Purpose**: Design for AI assistant integration within GUI.

**Features**:
- Natural language queries about pipeline state
- Intelligent error explanation and suggestions
- Workstream generation from natural language
- Tool recommendation based on task

**Example Interactions**:
```
User: "Why did the last run fail?"
AI Steward: "Run ci-validation-001 failed at step 3 due to Ruff linting 
            errors. 5 files have line-length violations. Run 
            'ruff check --fix' to auto-fix."

User: "Create a workstream to validate all Python files"
AI Steward: [Generates workstream JSON]
            "I've created workstream 'validate-all-python' with 3 steps:
            1. Run Ruff linter
            2. Run Mypy type checker
            3. Run pytest test suite
            Would you like to execute it?"
```

## GUI Implementation Guidelines

### Technology Stack (Recommendations)

**Web-based GUI** (Recommended):
- **Backend**: FastAPI or Flask (Python)
- **Frontend**: React or Vue.js
- **Real-time**: WebSockets (via Socket.IO)
- **Styling**: Tailwind CSS or Material-UI

**Desktop GUI**:
- **Framework**: PyQt6, tkinter, or Electron
- **Advantage**: No web server required
- **Disadvantage**: Platform-specific builds

**TUI** (Terminal UI):
- **Framework**: `textual` or `rich`
- **Advantage**: Works over SSH, no GUI required
- **Use case**: Server environments, headless systems

### API Design

**REST API** (for web-based GUI):
```python
# GET /api/runs
# Returns: List of all runs with status

# POST /api/runs
# Body: {"change_id": "test-001", "options": {...}}
# Returns: {"run_id": "run-123"}

# GET /api/runs/{run_id}/workstreams
# Returns: List of workstreams for run

# POST /api/runs/{run_id}/cancel
# Returns: {"status": "cancelled"}
```

**Python API** (for desktop/TUI):
```python
from engine.api import EngineAPI

api = EngineAPI()

# List runs
runs = api.list_runs()

# Start run
run_id = api.start_run("test-001")

# Get workstreams
workstreams = api.list_workstreams(run_id)

# Cancel run
api.cancel_run(run_id)
```

### Event System

**Event Types**:
- `run.started`
- `run.completed`
- `run.failed`
- `workstream.started`
- `workstream.completed`
- `step.started`
- `step.completed`
- `step.failed`

**Subscription** (WebSocket):
```javascript
// Frontend subscribes to events
socket.on('run.started', (data) => {
  console.log(`Run ${data.run_id} started`);
  updateUI(data);
});

socket.on('step.failed', (data) => {
  showError(`Step ${data.step_id} failed: ${data.error}`);
});
```

## Development Workflow

### 1. Design Phase (Current - `gui/` docs)
- Write specifications
- Define API contracts
- Create wireframes
- Review permissions matrix

### 2. Implementation Phase (`engine/` + GUI framework)
- Implement engine API
- Build GUI frontend
- Connect via API
- Test integration

### 3. Testing Phase
- Unit tests for API endpoints
- Integration tests for GUI ↔ Engine
- UI/UX testing
- Performance testing

### 4. Deployment Phase
- Package GUI (web app or desktop app)
- Deploy engine as service
- Configure reverse proxy (if web-based)
- Set up monitoring

## Security Considerations

**Authentication** (for web-based GUI):
- Basic auth, OAuth, or API keys
- Session management
- CSRF protection

**Authorization**:
- Role-based access control (RBAC)
- Read-only users vs admins
- Action audit logging

**Input Validation**:
- Sanitize all user inputs
- Validate workstream IDs, change IDs
- Prevent command injection

## Performance Requirements

**Response Times**:
- API calls: <100ms
- UI updates: <200ms
- Log streaming: <50ms latency

**Scalability**:
- Support 10+ concurrent runs
- Handle 1000+ workstreams
- Stream logs for multiple runs simultaneously

## Related Sections

- **Engine**: `engine/` - Standalone execution engine (implementation)
- **Examples**: `examples/` - GUI integration examples
- **Config**: `config/ui_settings.yaml` - UI configuration
- **Docs**: `docs/` - Additional GUI documentation

## See Also

- [Engine README](../engine/README.md)
- [UI Settings Guide](../docs/ui_settings_guide.md)
- [API Reference](../docs/api_reference.md)
- [Security Guidelines](../docs/security.md)


## TUI Implementation

# TUI App - AI Development Pipeline Terminal UI

A Textual-based terminal user interface for monitoring and controlling the AI Development Pipeline.

## Quick Start

### Installation

```bash
pip install -r gui/tui_app/config/requirements.txt
```

### Running the TUI

```bash
# Launch with default dashboard panel
python -m gui.tui_app.main

# Launch with specific panel
python -m gui.tui_app.main --panel dashboard
python -m gui.tui_app.main --panel pattern_activity
python -m gui.tui_app.main --panel file_lifecycle

# Run smoke test (launch and exit)
python -m gui.tui_app.main --smoke-test
```

## Available Panels

| Panel ID | Key Binding | Description |
|----------|-------------|-------------|
| `dashboard` | `d` | Pipeline summary and recent tasks |
| `file_lifecycle` | `f` | Patch ledger with file/exec state and counters |
| `tool_health` | `t` | Log-derived tool status grid with last-seen info |
| `log_stream` | `l` | Live tail of the configured pipeline log file |
| `pattern_activity` | `p` | Pattern execution timeline and events |

## Key Bindings

- `q` - Quit application
- `d` - Switch to Dashboard
- `f` - Switch to File Lifecycle
- `t` - Switch to Tool Health
- `l` - Switch to Log Stream
- `p` - Switch to Pattern Activity

## Architecture

The TUI is built on a plugin-based panel framework:

- **PanelPlugin**: Protocol that all panels implement
- **PanelRegistry**: Manages panel registration and lookup
- **BasicLayoutManager**: Handles panel mounting (single panel currently)
- **StateClient**: Provides access to pipeline state
- **PatternClient**: Provides access to pattern execution data

See [TUI Panel Framework Guide](docs/TUI_PANEL_FRAMEWORK_GUIDE.md) for detailed documentation.

## Adding New Panels

1. Create a new panel class in `gui/tui_app/panels/`
2. Decorate with `@register_panel("panel_id")`
3. Implement `PanelPlugin` protocol
4. Import in `gui/tui_app/panels/__init__.py`
5. Add key binding in `gui/tui_app/main.py` (optional)

Example:

```python
from gui.tui_app.core.panel_registry import register_panel
from gui.tui_app.core.panel_plugin import PanelPlugin, PanelContext
from textual.widgets import Static

@register_panel("my_panel")
class MyPanel:
    @property
    def panel_id(self) -> str:
        return "my_panel"
    
    @property
    def title(self) -> str:
        return "My Panel"
    
    def create_widget(self, context: PanelContext) -> Static:
        return Static("Panel content")
    
    def on_mount(self, context: PanelContext) -> None:
        pass
    
    def on_unmount(self, context: PanelContext) -> None:
        pass
```

## Testing

```bash
# Run all TUI tests
pytest tests/gui/tui_panel_framework -q

# Run backend and TUI smoke integration
pytest tests/test_sqlite_backend.py -q
pytest tests/test_tui_integration.py -q

# Run specific test file
pytest tests/gui/tui_panel_framework/test_panels_smoke.py -v
```

## Design Principles

1. **TUI-First**: Core in Textual, GUI wrapper optional
2. **Panel Isolation**: Self-contained, reusable components
3. **Pluggable Backends**: StateClient/PatternClient use abstract backends
4. **Future-Proof**: Designed for multi-panel layouts without refactors

## Future Enhancements

- Multi-panel split layouts (horizontal/vertical)
- Link groups for shared selection context
- Thin GUI wrapper for visual enhancements
- Background/tray mode for always-on monitoring

