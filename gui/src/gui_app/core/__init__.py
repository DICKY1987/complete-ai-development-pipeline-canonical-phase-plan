"""GUI Core Package.

Core infrastructure for GUI application.
"""

# DOC_ID: DOC-GUI-APP-CORE-INIT-405

__all__ = [
    "GuiApp",
    "GuiPanelPlugin",
    "GuiPanelRegistry",
    "get_registry",
    "register_panel",
]

from gui_app.core.gui_app import GuiApp
from gui_app.core.gui_panel_plugin import GuiPanelPlugin
from gui_app.core.gui_panel_registry import (
    GuiPanelRegistry,
    get_registry,
    register_panel,
)
