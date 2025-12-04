# GUI Architecture Migration Guide

## Overview

This guide explains the new **framework-neutral** architecture that enables both TUI (Textual) and GUI (PySide6) shells to coexist.

## Architecture Summary

```
gui/src/
├── ui_core/              # ✨ NEW - Framework-agnostic core
│   ├── panel_context.py  # No Widget imports
│   ├── state_client.py   # Moved from tui_app/core
│   ├── pattern_client.py # Moved from tui_app/core
│   ├── sqlite_state_backend.py
│   └── layout_config.py  # Unified UIConfig
│
├── tui_app/              # ✅ Existing TUI (Textual)
│   ├── core/
│   │   ├── layout_manager.py
│   │   └── panel_registry.py
│   └── panels/
│       ├── dashboard_panel.py
│       ├── file_lifecycle_panel.py
│       ├── tool_health_panel.py
│       ├── log_stream_panel.py
│       └── pattern_activity_panel.py
│
└── gui_app/              # ✨ NEW - GUI (PySide6)
    ├── core/
    │   ├── gui_app.py
    │   ├── gui_panel_plugin.py
    │   ├── gui_panel_registry.py
    │   └── __init__.py
    ├── panels/
    │   ├── dashboard_panel.py  # GUI versions
    │   ├── file_lifecycle_panel.py
    │   ├── tool_health_panel.py
    │   ├── log_stream_panel.py
    │   └── pattern_activity_panel.py
    └── main.py
```

---

## Phase 1: Update TUI Imports (CRITICAL)

### Step 1.1: Update TUI Panel Imports

**All TUI panels** must change imports from `tui_app.core` → `ui_core`:

```python
# OLD (tui_app/panels/dashboard_panel.py)
from tui_app.core.panel_plugin import PanelContext, PanelPlugin
from tui_app.core.panel_registry import register_panel

# NEW
from ui_core.panel_context import PanelContext
from tui_app.core.panel_plugin import TuiPanelPlugin  # Framework-specific
from tui_app.core.panel_registry import register_panel
```

**Files to update:**
- `tui_app/panels/dashboard_panel.py`
- `tui_app/panels/file_lifecycle_panel.py`
- `tui_app/panels/tool_health_panel.py`
- `tui_app/panels/log_stream_panel.py`
- `tui_app/panels/pattern_activity_panel.py`

### Step 1.2: Update TUI main.py

```python
# OLD (tui_app/main.py)
from tui_app.config.layout_config import TUIConfig, load_tui_config
from tui_app.core.state_client import InMemoryStateBackend, StateClient
from tui_app.core.pattern_client import InMemoryPatternStateStore, PatternClient

# NEW
from ui_core.layout_config import UIConfig, load_ui_config
from ui_core.state_client import InMemoryStateBackend, StateClient
from ui_core.pattern_client import InMemoryPatternStateStore, PatternClient
```

### Step 1.3: Update TUI panel_plugin.py (Create TUI-specific protocol)

**Create new file:** `tui_app/core/tui_panel_plugin.py`

```python
"""TUI-specific panel plugin protocol."""

from typing import Protocol
from textual.widget import Widget
from ui_core.panel_context import PanelContext


class TuiPanelPlugin(Protocol):
    """Protocol for TUI panels (Textual-specific)."""

    @property
    def panel_id(self) -> str: ...

    @property
    def title(self) -> str: ...

    def create_widget(self, context: PanelContext) -> Widget:
        """Create Textual Widget."""
        ...

    def on_mount(self, context: PanelContext) -> None: ...

    def on_unmount(self, context: PanelContext) -> None: ...
```

**Deprecate:** `tui_app/core/panel_plugin.py` (keep for backward compatibility)

---

## Phase 2: Running the GUI

### Step 2.1: Install Dependencies

```powershell
pip install -r gui/requirements-gui.txt
```

### Step 2.2: Launch GUI

```powershell
# From gui/src/ directory
python -m gui_app.main
```

**CLI Options:**
```powershell
# Use mock data (no SQLite)
python -m gui_app.main --use-mock-data

# Start on specific panel
python -m gui_app.main --panel pattern_activity

# Custom config
python -m gui_app.main --config path/to/ui_config.yaml
```

### Step 2.3: Compare TUI vs GUI

**TUI (still works):**
```powershell
python -m tui_app.main --panel dashboard
```

**GUI (new):**
```powershell
python -m gui_app.main --panel dashboard
```

Both use the **same data sources** (`StateClient`, `PatternClient`).

---

## Phase 3: Configuration Unification

### Old Config (TUI-only)

**File:** `tui_app/config/tui_config.yaml`

```yaml
theme:
  surface: "#0b1221"
  primary: "#1f6feb"
panels:
  dashboard_refresh_seconds: 2.0
logs:
  path: "logs/combined.log"
```

### New Config (Unified TUI + GUI)

**File:** `config/ui_config.yaml`

```yaml
# Shared settings
panels:
  dashboard_refresh_seconds: 2.0
  pattern_refresh_seconds: 5.0
logs:
  path: "logs/combined.log"

# TUI-specific
tui:
  theme:
    surface: "#0b1221"
    primary: "#1f6feb"

# GUI-specific
gui:
  window:
    width: 1280
    height: 800
  theme: "Fusion"
```

**Backward Compatibility:**
- `load_tui_config()` → alias for `load_ui_config()`
- `TUIConfig` → alias for `UIConfig`
- Old `tui_config.yaml` still supported as fallback

---

## Phase 4: Adding New Panels

### TUI Panel (Textual)

```python
# tui_app/panels/my_panel.py
from textual.widget import Widget
from ui_core.panel_context import PanelContext
from tui_app.core.panel_registry import register_panel


@register_panel("my_panel")
class MyPanel:
    @property
    def panel_id(self) -> str:
        return "my_panel"

    @property
    def title(self) -> str:
        return "My Panel"

    def create_widget(self, context: PanelContext) -> Widget:
        # Return Textual Widget
        pass
```

### GUI Panel (PySide6)

```python
# gui_app/panels/my_panel.py
from PySide6.QtWidgets import QWidget
from ui_core.panel_context import PanelContext
from gui_app.core.gui_panel_registry import register_panel


@register_panel("my_panel")
class MyPanel:
    @property
    def panel_id(self) -> str:
        return "my_panel"

    @property
    def title(self) -> str:
        return "My Panel"

    def create_widget(self, context: PanelContext) -> QWidget:
        # Return Qt QWidget
        pass
```

**Key Points:**
- **Same panel_id** for both TUI and GUI
- **Same data sources** (`context.state_client`, `context.pattern_client`)
- **Different widgets** (Textual vs Qt)

---

## Phase 5: Testing

### Smoke Test (TUI)

```powershell
python -m tui_app.main --smoke-test --use-mock-data
# Should launch and exit immediately (exit code 0)
```

### Smoke Test (GUI)

```powershell
python -m pytest gui/tests/test_gui_smoke.py
```

**Test file:** `gui/tests/test_gui_smoke.py`

```python
from PySide6.QtWidgets import QApplication
from gui_app.core.gui_app import GuiApp
from ui_core.state_client import StateClient, InMemoryStateBackend


def test_gui_app_instantiates():
    """GUI app can be created without crashing."""
    app = QApplication([])
    state = StateClient(InMemoryStateBackend())
    window = GuiApp(state_client=state)
    assert window.windowTitle() == "AI Pipeline Monitor"
```

---

## FAQ

### Q: Do I need to migrate TUI code immediately?

**A:** No. Old TUI code still works. Migration is **recommended** for:
- Future GUI support
- Cleaner separation of concerns
- Unified configuration

### Q: Can I run both TUI and GUI simultaneously?

**A:** Yes. They're independent applications sharing the same database.

### Q: What if I don't want GUI?

**A:** Don't install `requirements-gui.txt`. The TUI remains fully functional.

### Q: How do I know if imports are correct?

**A:** Run:
```powershell
python -m tui_app.main --use-mock-data
python -m gui_app.main --use-mock-data
```

Both should launch without import errors.

---

## Breaking Changes

### None (Backward Compatible)

All changes are **additive**:
- Old TUI imports still work (via compatibility aliases)
- Old `tui_config.yaml` still supported
- No API changes to `StateClient` or `PatternClient`

---

## Next Steps

1. **Update TUI imports** (Phase 1)
2. **Install GUI dependencies** (`pip install -r gui/requirements-gui.txt`)
3. **Run GUI smoke test** (`python -m gui_app.main --use-mock-data`)
4. **Iterate on panels** (start with Dashboard)
5. **Write integration tests**

---

## Support

- **TUI Issues:** `tui_app/README.md`
- **GUI Issues:** `gui_app/README.md` (TODO: create)
- **Architecture:** `docs/architecture.md`
