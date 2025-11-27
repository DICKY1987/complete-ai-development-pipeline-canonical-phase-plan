"""Pattern activity panel for visualizing pattern execution."""

from textual.widgets import Static, DataTable
from textual.containers import Container, Horizontal, Vertical

from tui_app.core.panel_plugin import PanelPlugin, PanelContext
from tui_app.core.panel_registry import register_panel


@register_panel("pattern_activity")
class PatternActivityPanel:
    """Panel showing pattern execution timeline and event details.
    
    Displays:
    - Timeline view (left): List of pattern runs
    - Detail view (right): Events for selected run
    """
    
    @property
    def panel_id(self) -> str:
        return "pattern_activity"
    
    @property
    def title(self) -> str:
        return "Pattern Activity"
    
    def create_widget(self, context: PanelContext) -> Static:
        """Create pattern activity widget."""
        
        if context.pattern_client:
            runs = context.pattern_client.get_recent_runs(limit=10)
            
            # Build timeline view
            timeline_lines = ["[bold cyan]Pattern Runs:[/]", ""]
            for run in runs:
                status_symbol = {
                    "completed": "[green]✓[/]",
                    "running": "[yellow]⟳[/]",
                    "failed": "[red]✗[/]",
                    "pending": "[dim]○[/]",
                    "cancelled": "[dim]✗[/]"
                }.get(run.status.value, "○")
                
                timeline_lines.append(f"{status_symbol} {run.pattern_name}")
                timeline_lines.append(f"   [dim]{run.run_id}[/] - Progress: {int(run.progress * 100)}%")
                if run.current_phase:
                    timeline_lines.append(f"   [dim cyan]Phase: {run.current_phase}[/]")
                if run.error_message:
                    timeline_lines.append(f"   [dim red]Error: {run.error_message}[/]")
                timeline_lines.append("")
            
            # Build detail view for first run
            detail_lines = ["[bold cyan]Event Details:[/]", ""]
            if runs:
                first_run = runs[0]
                events = context.pattern_client.get_run_events(first_run.run_id)
                
                detail_lines.append(f"[bold]{first_run.pattern_name}[/]")
                detail_lines.append(f"Run ID: {first_run.run_id}")
                detail_lines.append("")
                detail_lines.append("[bold cyan]Events:[/]")
                detail_lines.append("")
                
                for event in events:
                    event_symbol = {
                        "started": "▶",
                        "phase_started": "▷",
                        "phase_completed": "✓",
                        "validation_passed": "✓",
                        "validation_failed": "✗",
                        "executed": "●",
                        "completed": "✓",
                        "failed": "✗"
                    }.get(event.event_type.value, "●")
                    
                    detail_lines.append(f"{event_symbol} {event.message}")
                    if event.phase:
                        detail_lines.append(f"  [dim]Phase: {event.phase}[/]")
            
            # Combine views side-by-side (simplified text layout)
            content = "\n".join(timeline_lines)
            content += "\n\n" + "─" * 60 + "\n\n"
            content += "\n".join(detail_lines)
        else:
            content = "[bold red]No pattern client configured[/]"
        
        return Static(content, id="pattern-activity-content")
    
    def on_mount(self, context: PanelContext) -> None:
        """Called when panel is mounted."""
        pass
    
    def on_unmount(self, context: PanelContext) -> None:
        """Called when panel is unmounted."""
        pass
