# GUI Quick Start Guide

## Installation

### Step 1: Install GUI Dependencies

```powershell
cd gui
pip install -r requirements-gui.txt
```

**Dependencies installed:**
- `PySide6>=6.6.0` - Qt for Python (windowed GUI framework)
- `PyYAML>=6.0` - Configuration file parsing

### Step 2: Verify Installation

```powershell
cd src
python -m gui_app.main --use-mock-data
```

**Expected result:** GUI window opens showing the Dashboard panel with mock data.

---

## Running the GUI

### Basic Usage

```powershell
# From gui/src/ directory

# Launch with mock data (for testing)
python -m gui_app.main --use-mock-data

# Launch with real SQLite database
python -m gui_app.main

# Start on specific panel
python -m gui_app.main --panel file_lifecycle

# Use custom config
python -m gui_app.main --config ../config/my_config.yaml
```

### Available Panels

Launch GUI on any of these panels:

```powershell
--panel dashboard           # Pipeline status summary
--panel file_lifecycle      # Patch ledger tracking
--panel tool_health         # Tool error monitoring
--panel log_stream          # Live log viewer
--panel pattern_activity    # Pattern execution runs
```

---

## GUI vs TUI

Both shells use the **same data sources**:

| Feature | TUI (Textual) | GUI (PySide6) |
|---------|---------------|---------------|
| Launch | `python -m tui_app.main` | `python -m gui_app.main` |
| Environment | Terminal | Windowed |
| Navigation | Keyboard shortcuts | Tabs / Mouse |
| Refresh | Auto-refresh | Auto-refresh |
| Data Source | SQLite / In-Memory | SQLite / In-Memory |
| Config | `ui_config.yaml` | `ui_config.yaml` |

**You can run both simultaneously** - they share the same database.

---

## Configuration

### Config File Location

**Default:** `gui/src/config/ui_config.yaml`

### Example Configuration

```yaml
# Shared settings (both TUI and GUI)
panels:
  dashboard_refresh_seconds: 2.0
  pattern_refresh_seconds: 5.0
  file_refresh_seconds: 3.0

logs:
  path: "logs/combined.log"
  max_lines: 60

# GUI-specific settings
gui:
  window:
    width: 1280
    height: 800
    remember_position: true
  theme: "Fusion"  # Qt theme: Fusion, Windows, WindowsVista
```

### Customizing Theme

Available Qt themes:
- `Fusion` (cross-platform, modern) ✅ Default
- `Windows` (native Windows look)
- `WindowsVista` (Windows Aero)
- `Macintosh` (macOS native)

Edit `gui.theme` in `ui_config.yaml`.

---

## Architecture Overview

```
gui/src/
├── ui_core/              # Framework-agnostic core
│   ├── state_client.py   # Database access layer
│   ├── pattern_client.py # Pattern execution tracking
│   ├── panel_context.py  # Shared panel context
│   └── layout_config.py  # Config loader
│
├── gui_app/              # PySide6 GUI shell
│   ├── main.py           # Entry point
│   ├── core/
│   │   ├── gui_app.py    # Main window
│   │   └── gui_panel_registry.py
│   └── panels/           # 5 GUI panels
│       ├── dashboard_panel.py
│       ├── file_lifecycle_panel.py
│       ├── tool_health_panel.py
│       ├── log_stream_panel.py
│       └── pattern_activity_panel.py
│
└── tui_app/              # Textual TUI shell (existing)
    └── ...
```

**Key Design:**
- `ui_core/` has **no framework imports** (Qt or Textual)
- Both TUI and GUI panels use the same `PanelContext`
- Both shells register panels with the same `panel_id`

---

## Troubleshooting

### Import Error: "No module named 'PySide6'"

**Solution:**
```powershell
pip install -r gui/requirements-gui.txt
```

### Import Error: "No module named 'ui_core'"

**Solution:** Make sure you're running from `gui/src/`:
```powershell
cd gui/src
python -m gui_app.main
```

Or add to `PYTHONPATH`:
```powershell
$env:PYTHONPATH = "gui/src"
python -m gui_app.main
```

### Database Error: "unable to open database file"

**Solution:** Run with `--use-mock-data` or ensure `.worktrees/pipeline_state.db` exists:
```powershell
mkdir .worktrees
python -m gui_app.main
```

### GUI Window is Blank

**Solution:** Ensure panels are registered. Check `gui_app/panels/__init__.py` imports all panels.

---

## Development

### Adding a New Panel

#### Step 1: Create GUI Panel File

**File:** `gui_app/panels/my_panel.py`

```python
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from gui_app.core.gui_panel_registry import register_panel
from ui_core.panel_context import PanelContext


@register_panel("my_panel")
class MyPanel:
    @property
    def panel_id(self) -> str:
        return "my_panel"

    @property
    def title(self) -> str:
        return "My Custom Panel"

    def create_widget(self, context: PanelContext) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("My Panel Content"))
        return widget

    def on_mount(self, context: PanelContext) -> None:
        pass

    def on_unmount(self, context: PanelContext) -> None:
        pass
```

#### Step 2: Register in `__init__.py`

**File:** `gui_app/panels/__init__.py`

```python
from gui_app.panels.my_panel import MyPanel  # Add this

__all__ = [
    "DashboardPanel",
    "MyPanel",  # Add this
    # ...
]
```

#### Step 3: Add to Main Window

**File:** `gui_app/core/gui_app.py`

```python
def _load_panels(self) -> None:
    panel_ids = [
        ("dashboard", "Dashboard"),
        ("my_panel", "My Panel"),  # Add this
        # ...
    ]
```

### Running Tests

```powershell
cd gui
pytest tests/test_gui_smoke.py -v
```

**Expected output:**
```
test_gui_smoke.py::test_gui_app_instantiates PASSED
test_gui_smoke.py::test_gui_app_with_all_clients PASSED
test_gui_smoke.py::test_gui_panel_switching PASSED
test_gui_smoke.py::test_gui_panels_registered PASSED
```

---

## Next Steps

1. **Launch GUI:** `python -m gui_app.main --use-mock-data`
2. **Explore panels:** Click through tabs to see Dashboard, Logs, Patterns
3. **Connect to real data:** Remove `--use-mock-data` flag
4. **Customize theme:** Edit `gui/src/config/ui_config.yaml`
5. **Add custom panels:** Follow "Adding a New Panel" guide above

---

## Additional Resources

- **Migration Guide:** `docs/GUI_MIGRATION_GUIDE.md` - How to update TUI imports
- **Architecture:** `docs/architecture.md` - Full system design
- **TUI Guide:** `tui_app/README.md` - Terminal UI documentation

---

## Support

**Issues with GUI?**
- Check `gui/tests/test_gui_smoke.py` passes
- Verify `ui_core/` imports work from both `tui_app` and `gui_app`
- Ensure PySide6 installed: `pip list | grep -i pyside`

**Need help?**
- See `docs/GUI_MIGRATION_GUIDE.md` for detailed setup
- Compare working TUI implementation in `tui_app/`
