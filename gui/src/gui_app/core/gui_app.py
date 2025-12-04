"""Main GUI application window.

Central window that hosts panels and manages navigation.
"""

# DOC_ID: DOC-GUI-APP-CORE-GUI-APP-402

from typing import Optional

from gui_app.core.gui_panel_registry import get_registry
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from ui_core.layout_config import UIConfig
from ui_core.panel_context import PanelContext
from ui_core.pattern_client import PatternClient
from ui_core.state_client import StateClient


class GuiApp(QMainWindow):
    """Main GUI window for pipeline monitoring."""

    def __init__(
        self,
        state_client: StateClient,
        pattern_client: Optional[PatternClient] = None,
        config: Optional[UIConfig] = None,
        initial_panel: str = "dashboard",
    ):
        super().__init__()

        self.state_client = state_client
        self.pattern_client = pattern_client
        self.config = config
        self.registry = get_registry()

        self.setWindowTitle("AI Pipeline Monitor")

        if config and config.gui:
            self.resize(config.gui.width, config.gui.height)
        else:
            self.resize(1280, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self._load_panels()
        self._switch_to_panel(initial_panel)

    def _load_panels(self) -> None:
        """Load all registered panels into tabs."""
        panel_ids = [
            ("dashboard", "Dashboard"),
            ("file_lifecycle", "File Lifecycle"),
            ("tool_health", "Tool Health"),
            ("log_stream", "Log Stream"),
            ("pattern_activity", "Pattern Activity"),
        ]

        for panel_id, tab_title in panel_ids:
            panel = self.registry.create_panel(panel_id)
            if panel:
                context = PanelContext(
                    panel_id=panel_id,
                    state_client=self.state_client,
                    pattern_client=self.pattern_client,
                    config=self.config,
                )
                widget = panel.create_widget(context)
                self.tab_widget.addTab(widget, tab_title)

    def _switch_to_panel(self, panel_id: str) -> None:
        """Switch to a specific panel by ID."""
        panel_index_map = {
            "dashboard": 0,
            "file_lifecycle": 1,
            "tool_health": 2,
            "log_stream": 3,
            "pattern_activity": 4,
        }

        index = panel_index_map.get(panel_id, 0)
        self.tab_widget.setCurrentIndex(index)
