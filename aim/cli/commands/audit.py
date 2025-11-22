"""
CLI commands for audit log management.

Commands:
    aim audit show              - Show recent audit events
    aim audit query             - Query audit log with filters
    aim audit stats             - Show audit log statistics
    aim audit export            - Export audit log
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box
import json
from datetime import datetime, timedelta, timezone

from aim.environment.audit import get_audit_logger, EventType, EventSeverity


console = Console()


@click.group()
def audit():
    """Audit log management commands."""
    pass


@audit.command("show")
@click.option("--count", "-n", default=20, help="Number of recent events to show")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show_recent(count: int, output_json: bool):
    """Show recent audit events."""
    logger = get_audit_logger()
    events = logger.get_recent_events(count)
    
    if not events:
        console.print("[yellow]No audit events found[/yellow]")
        return
    
    if output_json:
        output = [event.to_dict() for event in events]
        console.print_json(json.dumps(output, indent=2))
        return
    
    table = Table(title=f"Recent Audit Events (last {count})", box=box.ROUNDED)
    table.add_column("Time", style="cyan", width=20)
    table.add_column("Type", style="magenta", width=15)
    table.add_column("Severity", style="yellow", width=10)
    table.add_column("Message", style="white")
    
    for event in reversed(events):  # Show newest first
        # Format timestamp
        try:
            dt = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            time_str = event.timestamp[:19]
        
        # Color code severity
        severity_style = {
            "debug": "dim",
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red"
        }.get(event.severity, "white")
        
        table.add_row(
            time_str,
            event.event_type,
            f"[{severity_style}]{event.severity}[/{severity_style}]",
            event.message
        )
    
    console.print(table)


@audit.command("query")
@click.option("--type", "event_type", help="Filter by event type")
@click.option("--severity", help="Filter by severity level")
@click.option("--since", help="Show events since (ISO timestamp or '1h', '1d', '1w')")
@click.option("--limit", default=100, help="Maximum events to return")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def query_events(event_type: str, severity: str, since: str, limit: int, output_json: bool):
    """Query audit log with filters.
    
    Examples:
        aim audit query --type tool_install
        aim audit query --severity error
        aim audit query --since 1h
        aim audit query --type secret_set --since "2025-01-01T00:00:00"
    """
    logger = get_audit_logger()
    
    # Parse event type
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            console.print(f"[red]Invalid event type: {event_type}[/red]")
            console.print(f"Valid types: {', '.join(e.value for e in EventType)}")
            return
    
    # Parse severity
    severity_enum = None
    if severity:
        try:
            severity_enum = EventSeverity(severity)
        except ValueError:
            console.print(f"[red]Invalid severity: {severity}[/red]")
            console.print(f"Valid severities: {', '.join(s.value for s in EventSeverity)}")
            return
    
    # Parse since timestamp
    since_timestamp = None
    if since:
        # Check for relative time (1h, 1d, 1w)
        if since.endswith('h'):
            hours = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
            since_timestamp = since_dt.isoformat()
        elif since.endswith('d'):
            days = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(days=days)
            since_timestamp = since_dt.isoformat()
        elif since.endswith('w'):
            weeks = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(weeks=weeks)
            since_timestamp = since_dt.isoformat()
        else:
            since_timestamp = since
    
    events = logger.query_events(
        event_type=event_type_enum,
        severity=severity_enum,
        since=since_timestamp,
        limit=limit
    )
    
    if not events:
        console.print("[yellow]No matching events found[/yellow]")
        return
    
    if output_json:
        output = [event.to_dict() for event in events]
        console.print_json(json.dumps(output, indent=2))
        return
    
    console.print(f"\n[bold]Found {len(events)} matching events[/bold]\n")
    
    table = Table(box=box.ROUNDED)
    table.add_column("Time", style="cyan", width=20)
    table.add_column("Type", style="magenta", width=15)
    table.add_column("Severity", style="yellow", width=10)
    table.add_column("Message", style="white")
    table.add_column("Details", style="dim")
    
    for event in reversed(events):
        # Format timestamp
        try:
            dt = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            time_str = event.timestamp[:19]
        
        # Format details
        details_str = ""
        if event.details:
            key_details = {k: v for k, v in event.details.items() if k in ["tool", "version", "key", "status"]}
            if key_details:
                details_str = ", ".join(f"{k}={v}" for k, v in key_details.items())
        
        severity_style = {
            "debug": "dim",
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red"
        }.get(event.severity, "white")
        
        table.add_row(
            time_str,
            event.event_type,
            f"[{severity_style}]{event.severity}[/{severity_style}]",
            event.message,
            details_str[:40]
        )
    
    console.print(table)


@audit.command("stats")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show_stats(output_json: bool):
    """Show audit log statistics."""
    logger = get_audit_logger()
    stats = logger.get_stats()
    
    if output_json:
        console.print_json(json.dumps(stats, indent=2))
        return
    
    console.print("\n[bold cyan]Audit Log Statistics[/bold cyan]\n")
    
    # General stats
    console.print(f"[bold]Total Events:[/bold] {stats['total_events']}")
    console.print(f"[bold]Log Size:[/bold] {stats['log_size_bytes'] / 1024:.1f} KB")
    
    if stats['oldest_event']:
        console.print(f"[bold]Oldest Event:[/bold] {stats['oldest_event'][:19]}")
    if stats['newest_event']:
        console.print(f"[bold]Newest Event:[/bold] {stats['newest_event'][:19]}")
    
    # Events by type
    if stats['by_type']:
        console.print("\n[bold]Events by Type:[/bold]")
        type_table = Table(show_header=False, box=None)
        type_table.add_column("Type", style="magenta")
        type_table.add_column("Count", style="cyan", justify="right")
        
        for event_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            type_table.add_row(event_type, str(count))
        
        console.print(type_table)
    
    # Events by severity
    if stats['by_severity']:
        console.print("\n[bold]Events by Severity:[/bold]")
        severity_table = Table(show_header=False, box=None)
        severity_table.add_column("Severity", style="yellow")
        severity_table.add_column("Count", style="cyan", justify="right")
        
        severity_order = ["debug", "info", "warning", "error", "critical"]
        for severity in severity_order:
            if severity in stats['by_severity']:
                count = stats['by_severity'][severity]
                severity_table.add_row(severity, str(count))
        
        console.print(severity_table)
    
    console.print()


@audit.command("export")
@click.argument("output_file", type=click.Path())
@click.option("--format", type=click.Choice(["json", "jsonl", "csv"]), default="json")
@click.option("--since", help="Export events since (ISO timestamp or '1h', '1d', '1w')")
def export_log(output_file: str, format: str, since: str):
    """Export audit log to file.
    
    Examples:
        aim audit export audit_backup.json
        aim audit export recent.json --since 1d
        aim audit export audit.csv --format csv
    """
    logger = get_audit_logger()
    
    # Parse since timestamp
    since_timestamp = None
    if since:
        if since.endswith('h'):
            hours = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
            since_timestamp = since_dt.isoformat()
        elif since.endswith('d'):
            days = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(days=days)
            since_timestamp = since_dt.isoformat()
        elif since.endswith('w'):
            weeks = int(since[:-1])
            since_dt = datetime.now(timezone.utc) - timedelta(weeks=weeks)
            since_timestamp = since_dt.isoformat()
        else:
            since_timestamp = since
    
    events = logger.query_events(since=since_timestamp, limit=100000)
    
    if not events:
        console.print("[yellow]No events to export[/yellow]")
        return
    
    try:
        if format == "json":
            # Export as JSON array
            output = [event.to_dict() for event in events]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)
        
        elif format == "jsonl":
            # Export as JSON Lines
            with open(output_file, 'w', encoding='utf-8') as f:
                for event in events:
                    f.write(event.to_jsonl() + '\n')
        
        elif format == "csv":
            # Export as CSV
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if events:
                    # Get all possible fields
                    fieldnames = ["timestamp", "event_type", "severity", "message", "user", "session_id"]
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for event in events:
                        row = {
                            "timestamp": event.timestamp,
                            "event_type": event.event_type,
                            "severity": event.severity,
                            "message": event.message,
                            "user": event.user or "",
                            "session_id": event.session_id or ""
                        }
                        writer.writerow(row)
        
        console.print(f"[green]✓ Exported {len(events)} events to {output_file}[/green]")
    
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")
        raise click.Abort()


def register_commands(cli_group):
    """Register audit commands with the main CLI."""
    cli_group.add_command(audit)
