"""TUI Application Main Entry Point.

Textual-based terminal UI for AI Development Pipeline monitoring and control.
"""

import argparse
import sys
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static

from tui_app.core.panel_registry import get_registry
from tui_app.core.layout_manager import BasicLayoutManager
from tui_app.core.state_client import StateClient, InMemoryStateBackend
from tui_app.core.pattern_client import PatternClient, InMemoryPatternStateStore
from tui_app.core.panel_plugin import PanelContext
from tui_app.config.layout_config import LayoutConfig

# Import panels to trigger registration
import tui_app.panels


class PipelineTUI(App):
    """Main TUI application for pipeline monitoring."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #panel-container {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    
    Header {
        background: $primary;
    }
    
    Footer {
        background: $primary;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "switch_dashboard", "Dashboard"),
        ("f", "switch_file_lifecycle", "Files"),
        ("t", "switch_tool_health", "Tools"),
        ("l", "switch_log_stream", "Logs"),
        ("p", "switch_pattern_activity", "Patterns"),
    ]
    
    def __init__(self, panel_id: str = "dashboard", smoke_test: bool = False):
        super().__init__()
        self.panel_id = panel_id
        self.smoke_test = smoke_test
        
        # Initialize clients
        self.state_client = StateClient(InMemoryStateBackend())
        self.pattern_client = PatternClient(InMemoryPatternStateStore())
        
        # Initialize layout manager
        self.layout_manager = BasicLayoutManager()
        
        # Get panel registry
        self.registry = get_registry()
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header(show_clock=True)
        yield Container(id="panel-container")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = "AI Pipeline TUI"
        self.sub_title = "Monitoring & Control"
        
        # Mount initial panel
        self._mount_panel(self.panel_id)
        
        # If smoke test, exit immediately
        if self.smoke_test:
            self.exit(0)
    
    def _mount_panel(self, panel_id: str) -> None:
        """Mount a panel by ID."""
        panel = self.registry.create_panel(panel_id)
        if not panel:
            # Fallback to dashboard
            panel = self.registry.create_panel("dashboard")
            if not panel:
                self.exit(1, f"Failed to create panel: {panel_id}")
                return
        
        # Create context
        context = PanelContext(
            panel_id=panel_id,
            state_client=self.state_client,
            pattern_client=self.pattern_client
        )
        
        # Mount panel
        widget = self.layout_manager.mount_panel(panel, context)
        
        # Update container
        container = self.query_one("#panel-container", Container)
        container.remove_children()
        container.mount(widget)
        
        # Update subtitle
        self.sub_title = panel.title
    
    def action_switch_dashboard(self) -> None:
        """Switch to dashboard panel."""
        self._mount_panel("dashboard")
    
    def action_switch_file_lifecycle(self) -> None:
        """Switch to file lifecycle panel."""
        self._mount_panel("file_lifecycle")
    
    def action_switch_tool_health(self) -> None:
        """Switch to tool health panel."""
        self._mount_panel("tool_health")
    
    def action_switch_log_stream(self) -> None:
        """Switch to log stream panel."""
        self._mount_panel("log_stream")
    
    def action_switch_pattern_activity(self) -> None:
        """Switch to pattern activity panel."""
        self._mount_panel("pattern_activity")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Pipeline TUI")
    parser.add_argument(
        "--panel",
        default="dashboard",
        choices=["dashboard", "file_lifecycle", "tool_health", "log_stream", "pattern_activity"],
        help="Initial panel to display"
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run smoke test (launch and exit immediately)"
    )
    
    args = parser.parse_args()
    
    app = PipelineTUI(panel_id=args.panel, smoke_test=args.smoke_test)
    
    try:
        app.run()
    except Exception as e:
        print(f"Error running TUI: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
