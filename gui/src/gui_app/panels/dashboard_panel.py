"""Dashboard panel for pipeline summary visualization (GUI version)."""

# DOC_ID: DOC-GUI-APP-PANELS-DASHBOARD-411

from datetime import datetime

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


class DashboardWidget(QWidget):
    """Dashboard widget with auto-refresh capability."""

    def __init__(self, context: PanelContext):
        super().__init__()

        self.context = context
        panel_cfg = getattr(context.config, "panels", None)
        self.refresh_interval = int((panel_cfg.dashboard if panel_cfg else 2.0) * 1000)

        layout = QVBoxLayout(self)

        self.status_label = QLabel("Status: Loading...")
        layout.addWidget(self.status_label)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Task", "Status", "Worker"])
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(self.refresh_interval)

        self._refresh_data()

    def _refresh_data(self) -> None:
        """Fetch and display updated dashboard data."""
        if not self.context.state_client:
            self.status_label.setText("Status: No state client configured")
            return

        last_updated = datetime.now().strftime("%H:%M:%S")

        summary = self.context.state_client.get_pipeline_summary()
        tasks = self.context.state_client.get_tasks(limit=10)

        self.status_label.setText(
            f"Status: {summary.status.upper()} (Updated: {last_updated})"
        )

        summary_text = f"""
Total Tasks: {summary.total_tasks}
Running: {summary.running_tasks}
Completed: {summary.completed_tasks}
Failed: {summary.failed_tasks}
Active Workers: {summary.active_workers}
        """.strip()

        self.summary_label.setText(summary_text)

        self.table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.table.setItem(i, 0, QTableWidgetItem(task.name))
            self.table.setItem(i, 1, QTableWidgetItem(task.status))
            self.table.setItem(i, 2, QTableWidgetItem(task.worker_id or "N/A"))


@register_panel("dashboard")
class DashboardPanel:
    """Main dashboard panel showing pipeline summary (GUI version)."""

    @property
    def panel_id(self) -> str:
        return "dashboard"

    @property
    def title(self) -> str:
        return "Pipeline Dashboard"

    def create_widget(self, context: PanelContext) -> DashboardWidget:
        """Create dashboard widget with auto-refresh."""
        return DashboardWidget(context)

    def on_mount(self, context: PanelContext) -> None:
        """Called when panel is mounted."""
        pass

    def on_unmount(self, context: PanelContext) -> None:
        """Called when panel is unmounted."""
        pass
