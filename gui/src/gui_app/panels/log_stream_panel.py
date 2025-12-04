"""Log stream panel (GUI version)."""

# DOC_ID: DOC-GUI-APP-PANELS-LOG-STREAM-414

from gui_app.core.gui_panel_registry import register_panel
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from ui_core.panel_context import PanelContext


class LogStreamWidget(QWidget):
    def __init__(self, context: PanelContext):
        super().__init__()
        self.context = context
        panel_cfg = getattr(context.config, "panels", None)
        self.refresh_interval = int((panel_cfg.log if panel_cfg else 3.0) * 1000)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_logs)
        self.timer.start(self.refresh_interval)
        self._refresh_logs()

    def _refresh_logs(self) -> None:
        log_config = getattr(self.context.config, "logs", None)
        if not log_config:
            return

        try:
            with open(log_config.path, "r") as f:
                lines = f.readlines()
                self.text_edit.setPlainText("".join(lines[-log_config.max_lines :]))
        except FileNotFoundError:
            self.text_edit.setPlainText("Log file not found")


@register_panel("log_stream")
class LogStreamPanel:
    @property
    def panel_id(self) -> str:
        return "log_stream"

    @property
    def title(self) -> str:
        return "Log Stream"

    def create_widget(self, context: PanelContext) -> LogStreamWidget:
        return LogStreamWidget(context)

    def on_mount(self, context: PanelContext) -> None:
        pass

    def on_unmount(self, context: PanelContext) -> None:
        pass
