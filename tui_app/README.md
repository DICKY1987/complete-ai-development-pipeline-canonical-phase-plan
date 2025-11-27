# TUI App - AI Development Pipeline Terminal UI

A Textual-based terminal user interface for monitoring and controlling the AI Development Pipeline.

## Quick Start

### Installation

```bash
pip install textual
```

### Running the TUI

```bash
# Launch with default dashboard panel
python -m tui_app.main

# Launch with specific panel
python -m tui_app.main --panel dashboard
python -m tui_app.main --panel pattern_activity
python -m tui_app.main --panel file_lifecycle

# Run smoke test (launch and exit)
python -m tui_app.main --smoke-test
```

## Available Panels

| Panel ID | Key Binding | Description |
|----------|-------------|-------------|
| `dashboard` | `d` | Pipeline summary and recent tasks |
| `file_lifecycle` | `f` | File tracking through pipeline stages (skeleton) |
| `tool_health` | `t` | Error detection tool status (skeleton) |
| `log_stream` | `l` | Real-time pipeline logs (skeleton) |
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

See [docs/gui/TUI_PANEL_FRAMEWORK_GUIDE.md](../docs/gui/TUI_PANEL_FRAMEWORK_GUIDE.md) for detailed documentation.

## Adding New Panels

1. Create a new panel class in `tui_app/panels/`
2. Decorate with `@register_panel("panel_id")`
3. Implement `PanelPlugin` protocol
4. Import in `tui_app/panels/__init__.py`
5. Add key binding in `tui_app/main.py` (optional)

Example:

```python
from tui_app.core.panel_registry import register_panel
from tui_app.core.panel_plugin import PanelPlugin, PanelContext
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
pytest tests/tui_panel_framework -q

# Run specific test file
pytest tests/tui_panel_framework/test_panels_smoke.py -v
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
- Real database backends for state/pattern data
- Live data refresh and auto-update
