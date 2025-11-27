"""Dashboard panel for pipeline summary visualization."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, DataTable

from tui_app.core.panel_plugin import PanelPlugin, PanelContext
from tui_app.core.panel_registry import register_panel


@register_panel("dashboard")
class DashboardPanel:
    """Main dashboard panel showing pipeline summary."""
    
    @property
    def panel_id(self) -> str:
        return "dashboard"
    
    @property
    def title(self) -> str:
        return "Pipeline Dashboard"
    
    def create_widget(self, context: PanelContext) -> Static:
        """Create dashboard widget with pipeline summary."""
        
        # Get pipeline summary from state client
        if context.state_client:
            summary = context.state_client.get_pipeline_summary()
            tasks = context.state_client.get_tasks(limit=5)
            
            # Build display text
            lines = [
                f"[bold cyan]Pipeline Status:[/] {summary.status.upper()}",
                "",
                f"Total Tasks:     {summary.total_tasks}",
                f"Running:         {summary.running_tasks}",
                f"Completed:       {summary.completed_tasks}",
                f"Failed:          {summary.failed_tasks}",
                f"Active Workers:  {summary.active_workers}",
                "",
                "[bold cyan]Recent Tasks:[/]",
                "",
            ]
            
            for task in tasks:
                status_color = {
                    "completed": "green",
                    "running": "yellow",
                    "failed": "red"
                }.get(task.status, "white")
                
                lines.append(f"[{status_color}]●[/] {task.name} ({task.status})")
                if task.error_message:
                    lines.append(f"  [dim red]Error: {task.error_message}[/]")
            
            content = "\n".join(lines)
        else:
            content = "[bold red]No state client configured[/]"
        
        return Static(content, id="dashboard-content")
    
    def on_mount(self, context: PanelContext) -> None:
        """Called when panel is mounted."""
        pass
    
    def on_unmount(self, context: PanelContext) -> None:
        """Called when panel is unmounted."""
        pass
