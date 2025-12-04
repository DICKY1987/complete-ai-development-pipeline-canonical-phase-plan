"""Tool health panel (GUI version)."""

# DOC_ID: DOC-GUI-APP-PANELS-TOOL-HEALTH-413

from gui_app.core.gui_panel_registry import register_panel
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from ui_core.panel_context import PanelContext


class ToolHealthWidget(QWidget):
    def __init__(self, context: PanelContext):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Tool Health Panel"))
        layout.addWidget(
            QLabel("(Implementation pending - parses logs for tool errors)")
        )


@register_panel("tool_health")
class ToolHealthPanel:
    @property
    def panel_id(self) -> str:
        return "tool_health"

    @property
    def title(self) -> str:
        return "Tool Health"

    def create_widget(self, context: PanelContext) -> ToolHealthWidget:
        return ToolHealthWidget(context)

    def on_mount(self, context: PanelContext) -> None:
        pass

    def on_unmount(self, context: PanelContext) -> None:
        pass
