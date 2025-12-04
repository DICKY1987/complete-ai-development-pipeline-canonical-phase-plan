"""GUI Panels Package.

All GUI panel implementations (PySide6-based).
"""

# DOC_ID: DOC-GUI-APP-PANELS-INIT-410

# Import all panels to trigger registration
from gui_app.panels.dashboard_panel import DashboardPanel
from gui_app.panels.file_lifecycle_panel import FileLifecyclePanel
from gui_app.panels.log_stream_panel import LogStreamPanel
from gui_app.panels.pattern_activity_panel import PatternActivityPanel
from gui_app.panels.tool_health_panel import ToolHealthPanel

__all__ = [
    "DashboardPanel",
    "FileLifecyclePanel",
    "ToolHealthPanel",
    "LogStreamPanel",
    "PatternActivityPanel",
]
