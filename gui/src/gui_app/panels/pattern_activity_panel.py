"""Pattern activity panel (GUI version)."""

# DOC_ID: DOC-GUI-APP-PANELS-PATTERN-ACTIVITY-415

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


class PatternActivityWidget(QWidget):
    def __init__(self, context: PanelContext):
        super().__init__()
        self.context = context
        panel_cfg = getattr(context.config, "panels", None)
        self.refresh_interval = int((panel_cfg.pattern if panel_cfg else 5.0) * 1000)

        layout = QVBoxLayout(self)
        self.label = QLabel("Pattern Execution Runs")
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Run ID", "Pattern", "Status", "Progress", "Phase"]
        )
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(self.refresh_interval)
        self._refresh_data()

    def _refresh_data(self) -> None:
        if not self.context.pattern_client:
            return

        runs = self.context.pattern_client.get_recent_runs(limit=20)
        self.table.setRowCount(len(runs))

        for i, run in enumerate(runs):
            self.table.setItem(i, 0, QTableWidgetItem(run.run_id))
            self.table.setItem(i, 1, QTableWidgetItem(run.pattern_name))
            self.table.setItem(i, 2, QTableWidgetItem(run.status.value))
            self.table.setItem(i, 3, QTableWidgetItem(f"{run.progress * 100:.0f}%"))
            self.table.setItem(i, 4, QTableWidgetItem(run.current_phase or "N/A"))


@register_panel("pattern_activity")
class PatternActivityPanel:
    @property
    def panel_id(self) -> str:
        return "pattern_activity"

    @property
    def title(self) -> str:
        return "Pattern Activity"

    def create_widget(self, context: PanelContext) -> PatternActivityWidget:
        return PatternActivityWidget(context)

    def on_mount(self, context: PanelContext) -> None:
        pass

    def on_unmount(self, context: PanelContext) -> None:
        pass
