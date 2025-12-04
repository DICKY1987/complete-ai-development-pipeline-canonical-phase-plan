"""File lifecycle panel for patch tracking (GUI version)."""

# DOC_ID: DOC-GUI-APP-PANELS-FILE-LIFECYCLE-412

from gui_app.core.gui_panel_registry import register_panel
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ui_core.panel_context import PanelContext


class FileLifecycleWidget(QWidget):
    """File lifecycle widget showing patch ledger."""

    def __init__(self, context: PanelContext):
        super().__init__()
        self.context = context
        panel_cfg = getattr(context.config, "panels", None)
        self.refresh_interval = int((panel_cfg.file if panel_cfg else 3.0) * 1000)

        layout = QVBoxLayout(self)
        self.label = QLabel("Patch Ledger")
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Patch ID", "Execution", "State", "Files"]
        )
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(self.refresh_interval)
        self._refresh_data()

    def _refresh_data(self) -> None:
        if not self.context.state_client:
            return

        patches = self.context.state_client.get_patch_ledger(limit=20)
        self.table.setRowCount(len(patches))

        for i, patch in enumerate(patches):
            self.table.setItem(i, 0, QTableWidgetItem(patch.patch_id))
            self.table.setItem(i, 1, QTableWidgetItem(patch.execution_id or "N/A"))
            self.table.setItem(i, 2, QTableWidgetItem(patch.state))
            self.table.setItem(i, 3, QTableWidgetItem(", ".join(patch.files[:3])))


@register_panel("file_lifecycle")
class FileLifecyclePanel:
    @property
    def panel_id(self) -> str:
        return "file_lifecycle"

    @property
    def title(self) -> str:
        return "File Lifecycle"

    def create_widget(self, context: PanelContext) -> FileLifecycleWidget:
        return FileLifecycleWidget(context)

    def on_mount(self, context: PanelContext) -> None:
        pass

    def on_unmount(self, context: PanelContext) -> None:
        pass
