# TUI Panel Framework Guide

## Overview

The TUI Panel Framework provides a Textual-based terminal user interface for monitoring and controlling the AI Development Pipeline. It implements a plugin-based architecture where panels are self-contained, reusable components.

## Architecture

### Core Components

1. **PanelPlugin Protocol** (`tui_app/core/panel_plugin.py`)
   - Defines the contract all panels must implement
   - Properties: `panel_id`, `title`
   - Methods: `create_widget()`, `on_mount()`, `on_unmount()`

2. **PanelContext** (`tui_app/core/panel_plugin.py`)
   - Provides panels access to shared resources
   - Contains: `state_client`, `pattern_client`, `config`, `event_bus`

3. **PanelRegistry** (`tui_app/core/panel_registry.py`)
   - Manages registration and lookup of panel plugins
   - Use `@register_panel("panel_id")` decorator to auto-register

4. **BasicLayoutManager** (`tui_app/core/layout_manager.py`)
   - Handles panel mounting/unmounting
   - Currently supports single-panel layouts
   - Designed for extension to multi-panel splits

5. **StateClient** (`tui_app/core/state_client.py`)
   - Provides access to pipeline state (tasks, summary)
   - Pluggable backend (InMemory, SQLite, etc.)

6. **PatternClient** (`tui_app/core/pattern_client.py`)
   - Provides access to pattern execution data
   - Used by PatternActivityPanel to visualize pattern runs

## How to Add a New Panel

### Step 1: Create Panel Class

Create a new file in `tui_app/panels/`:

```python
from textual.widgets import Static
from tui_app.core.panel_plugin import PanelPlugin, PanelContext
from tui_app.core.panel_registry import register_panel

@register_panel("my_panel")
class MyPanel:
    """Description of your panel."""
    
    @property
    def panel_id(self) -> str:
        return "my_panel"
    
    @property
    def title(self) -> str:
        return "My Panel Title"
    
    def create_widget(self, context: PanelContext) -> Static:
        """Create the Textual widget for this panel."""
        # Access state/pattern data via context
        if context.state_client:
            summary = context.state_client.get_pipeline_summary()
        
        # Build widget content
        content = "My panel content"
        return Static(content)
    
    def on_mount(self, context: PanelContext) -> None:
        """Called when panel is mounted."""
        pass
    
    def on_unmount(self, context: PanelContext) -> None:
        """Called when panel is unmounted."""
        pass
```

### Step 2: Import in `tui_app/panels/__init__.py`

```python
from .my_panel import MyPanel

__all__ = [..., "MyPanel"]
```

### Step 3: Add to Main App (optional)

In `tui_app/main.py`, add key binding and action:

```python
BINDINGS = [
    ...,
    ("m", "switch_my_panel", "My Panel"),
]

def action_switch_my_panel(self) -> None:
    self._mount_panel("my_panel")
```

### Step 4: Test Your Panel

```bash
python -m gui.tui_app.main --panel my_panel --smoke-test
```

## Using StateClient

StateClient provides access to pipeline state:

```python
def create_widget(self, context: PanelContext) -> Static:
    if context.state_client:
        # Get pipeline summary
        summary = context.state_client.get_pipeline_summary()
        # summary.total_tasks, .running_tasks, .status, etc.
        
        # Get recent tasks
        tasks = context.state_client.get_tasks(limit=10)
        
        # Get specific task
        task = context.state_client.get_task("task-001")
```

## Using PatternClient

PatternClient provides access to pattern execution data:

```python
def create_widget(self, context: PanelContext) -> Static:
    if context.pattern_client:
        # Get recent pattern runs
        runs = context.pattern_client.get_recent_runs(limit=10)
        
        # Get events for a specific run
        events = context.pattern_client.get_run_events("run-001")
        
        # Get currently active patterns
        active = context.pattern_client.get_active_patterns()
```

## Available Panels

| Panel ID | Title | Status | Description |
|----------|-------|--------|-------------|
| `dashboard` | Pipeline Dashboard | ✓ Complete | Shows pipeline summary and recent tasks |
| `file_lifecycle` | File Lifecycle | Skeleton | Will track files through pipeline stages |
| `tool_health` | Tool Health | Skeleton | Will show error detection tool status |
| `log_stream` | Log Stream | Skeleton | Will stream pipeline logs |
| `pattern_activity` | Pattern Activity | ✓ Complete | Shows pattern execution timeline and events |

## Running the TUI

```bash
# Run with default (dashboard) panel
python -m gui.tui_app.main

# Run with specific panel
python -m gui.tui_app.main --panel pattern_activity

# Smoke test (launch and exit)
python -m gui.tui_app.main --smoke-test
```

### Key Bindings

- `q` - Quit
- `d` - Switch to Dashboard
- `f` - Switch to File Lifecycle
- `t` - Switch to Tool Health
- `l` - Switch to Log Stream
- `p` - Switch to Pattern Activity

## Future Extensions

### Multi-Panel Layouts

The `MultiPanelLayoutManager` is a placeholder for future support of:
- Split layouts (horizontal/vertical)
- Weighted panel sizes
- Link groups for shared selection context

### GUI Wrapper

The TUI is designed to support an optional thin GUI wrapper that:
- Reads the same layout configuration
- Uses the same state/pattern clients
- Renders panels in native GUI widgets
- Provides visual enhancements (charts, graphs)

### Real State Backend

Replace `InMemoryStateBackend` with a real backend:

```python
from tui_app.core.state_client import StateBackend

class SQLiteStateBackend(StateBackend):
    def get_pipeline_summary(self):
        # Query database
        pass
```

Then use it in the app:

```python
state_client = StateClient(SQLiteStateBackend("pipeline.db"))
```

## Testing

```bash
# Run all TUI tests
pytest tests/tui_panel_framework -q

# Run specific test
pytest tests/tui_panel_framework/test_panels_smoke.py -v
```

## Design Principles

1. **TUI-First**: Core functionality in Textual TUI, GUI wrapper is optional
2. **Panel Isolation**: Panels are self-contained and don't depend on each other
3. **Pluggable Backends**: State/pattern clients use abstract backends
4. **Future-Proof**: Architecture supports multi-panel layouts without refactors
5. **Testability**: Panels can be tested without launching the full app
