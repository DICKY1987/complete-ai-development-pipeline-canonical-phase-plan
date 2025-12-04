"""GUI panel plugin protocol.

Defines the contract for GUI panels (PySide6-based).
"""

# DOC_ID: DOC-GUI-APP-CORE-GUI-PANEL-PLUGIN-403

from typing import Protocol

from PySide6.QtWidgets import QWidget
from ui_core.panel_context import PanelContext


class GuiPanelPlugin(Protocol):
    """Protocol that all GUI panels must implement."""

    @property
    def panel_id(self) -> str:
        """Unique identifier for this panel type."""
        ...

    @property
    def title(self) -> str:
        """Human-readable title for this panel."""
        ...

    def create_widget(self, context: PanelContext) -> QWidget:
        """Create the Qt widget for this panel."""
        ...

    def on_mount(self, context: PanelContext) -> None:
        """Called when panel is mounted in the layout."""
        ...

    def on_unmount(self, context: PanelContext) -> None:
        """Called when panel is unmounted from the layout."""
        ...
