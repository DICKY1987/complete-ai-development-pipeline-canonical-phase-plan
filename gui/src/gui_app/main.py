"""GUI Application Main Entry Point.

PySide6-based windowed GUI for AI Development Pipeline monitoring and control.
"""

# DOC_ID: DOC-GUI-APP-MAIN-401

import argparse
import sys
from pathlib import Path
from typing import Optional

from gui_app.core.gui_app import GuiApp
from PySide6.QtWidgets import QApplication
from ui_core.layout_config import UIConfig, load_ui_config
from ui_core.pattern_client import (
    InMemoryPatternStateStore,
    PatternClient,
    SQLitePatternStateStore,
)
from ui_core.sqlite_state_backend import SQLiteStateBackend
from ui_core.state_client import InMemoryStateBackend, StateClient


def main():
    """Main entry point for GUI application."""
    parser = argparse.ArgumentParser(description="AI Pipeline GUI")
    parser.add_argument(
        "--panel",
        default="dashboard",
        choices=[
            "dashboard",
            "file_lifecycle",
            "tool_health",
            "log_stream",
            "pattern_activity",
        ],
        help="Initial panel to display",
    )
    parser.add_argument(
        "--use-mock-data",
        action="store_true",
        help="Use mock in-memory data instead of SQLite database",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to UI config file (defaults to gui/src/config/ui_config.yaml)",
    )

    args = parser.parse_args()

    config = load_ui_config(args.config)

    app = QApplication(sys.argv)

    if config.gui and config.gui.theme:
        app.setStyle(config.gui.theme)

    if args.use_mock_data:
        state_client = StateClient(InMemoryStateBackend())
        pattern_client = PatternClient(InMemoryPatternStateStore())
    else:
        state_backend = SQLiteStateBackend()
        state_client = StateClient(state_backend)
        pattern_client = PatternClient(
            SQLitePatternStateStore(db_path=state_backend.db_path)
        )

    window = GuiApp(
        state_client=state_client,
        pattern_client=pattern_client,
        config=config,
        initial_panel=args.panel,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
