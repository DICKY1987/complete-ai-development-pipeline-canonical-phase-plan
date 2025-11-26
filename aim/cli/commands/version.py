"""
CLI commands for version control.

Commands:
- aim version check   - Check for version drift
- aim version sync    - Sync to pinned versions
- aim version pin     - Pin current versions
"""

import asyncio
import json

import click
from rich.console import Console
from rich.table import Table

from modules.aim_environment.m01001B_version_control import VersionControl
from modules.aim_environment.m01001B_installer import ToolInstaller
from modules.aim_registry.m01001C_config_loader import ConfigLoader


console = Console()


@click.group(name="version")
def version_cli():
    """Version control and drift detection."""
    pass


@version_cli.command(name="check")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "all"]),
    default="all",
    help="Package manager to check (default: all)"
)
@click.option(
    "--json-output",
    "-j",
    is_flag=True,
    help="Output results as JSON"
)
def version_check(manager: str, json_output: bool):
    """Check all tools for version drift."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        vc = VersionControl(config, installer)
        
        mgr = None if manager == "all" else manager
        
        with console.status("[bold blue]Checking versions..."):
            report = asyncio.run(vc.check_all(mgr))
        
        if json_output:
            output = {
                "statuses": [
                    {
                        "tool": s.tool,
                        "manager": s.manager,
                        "expected": s.expected_version,
                        "actual": s.actual_version,
                        "status": s.status
                    }
                    for s in report.statuses
                ],
                "summary": {
                    "total": report.total_count,
                    "ok": report.ok_count,
                    "drift": report.drift_count,
                    "missing": report.missing_count,
                    "has_drift": report.has_drift
                }
            }
            console.print_json(data=output)
        else:
            # Display table
            table = Table(title="Version Status")
            table.add_column("Tool", style="cyan")
            table.add_column("Manager", style="yellow")
            table.add_column("Expected", style="white")
            table.add_column("Actual", style="white")
            table.add_column("Status", style="white")
            
            for status in report.statuses:
                # Color code status
                if status.status == "ok":
                    status_display = "[green]✓ OK[/green]"
                elif status.status == "missing":
                    status_display = "[red]✗ Missing[/red]"
                elif status.status == "drift":
                    status_display = "[yellow]⚠ Drift[/yellow]"
                else:
                    status_display = "[dim]? Unknown[/dim]"
                
                table.add_row(
                    status.tool,
                    status.manager,
                    status.expected_version or "Any",
                    status.actual_version or "—",
                    status_display
                )
            
            console.print(table)
            
            # Summary
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  Total: {report.total_count}")
            console.print(f"  [green]OK:[/green] {report.ok_count}")
            console.print(f"  [yellow]Drift:[/yellow] {report.drift_count}")
            console.print(f"  [red]Missing:[/red] {report.missing_count}")
            
            if report.has_drift:
                console.print(f"\n[yellow]Version drift detected - run 'aim version sync' to fix[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@version_cli.command(name="sync")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be synced without actually syncing"
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force reinstall even if version matches"
)
def version_sync(dry_run: bool, force: bool):
    """Sync all tools to pinned versions."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        vc = VersionControl(config, installer)
        
        action = "Checking what would be synced" if dry_run else "Syncing versions"
        
        with console.status(f"[bold blue]{action}..."):
            results = asyncio.run(vc.sync(dry_run=dry_run, force=force))
        
        # Display results
        table = Table(title="Sync Results" + (" (DRY RUN)" if dry_run else ""))
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Message", style="white")
        
        success_count = 0
        failure_count = 0
        
        for tool, success, message in results:
            if success:
                status_display = "[green]✓[/green]"
                success_count += 1
            else:
                status_display = "[red]✗[/red]"
                failure_count += 1
            
            table.add_row(tool, status_display, message)
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold] {success_count} succeeded, {failure_count} failed")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - no changes were made[/yellow]")
            console.print("Run without --dry-run to apply changes")
        
        if failure_count > 0 and not dry_run:
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@version_cli.command(name="pin")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "all"]),
    default="all",
    help="Package manager to pin (default: all)"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for version pins (default: stdout)"
)
def version_pin(manager: str, output: str):
    """Pin current versions to configuration."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        vc = VersionControl(config, installer)
        
        mgr = None if manager == "all" else manager
        
        with console.status("[bold blue]Reading current versions..."):
            pins = asyncio.run(vc.pin_current_versions(mgr))
        
        # Filter out empty managers
        pins = {k: v for k, v in pins.items() if v}
        
        if not pins:
            console.print("[yellow]No installed tools found to pin[/yellow]")
            return
        
        # Output pins
        if output:
            import json
            from pathlib import Path
            
            out_path = Path(output)
            with open(out_path, "w") as f:
                json.dump({"environment": {"versionPins": pins}}, f, indent=2)
            
            console.print(f"[green]Version pins written to {output}[/green]")
        else:
            # Display as JSON
            console.print_json(data={"environment": {"versionPins": pins}})
        
        # Show summary
        total_pins = sum(len(v) for v in pins.values())
        console.print(f"\n[bold]Pinned {total_pins} tool versions[/bold]")
        
        for mgr, tools in pins.items():
            if tools:
                console.print(f"  {mgr}: {len(tools)} tools")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@version_cli.command(name="report")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "all"]),
    default="all",
    help="Package manager to report (default: all)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "markdown"]),
    default="table",
    help="Output format (default: table)"
)
def version_report(manager: str, format: str):
    """Generate detailed version report."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        vc = VersionControl(config, installer)
        
        mgr = None if manager == "all" else manager
        
        with console.status("[bold blue]Generating report..."):
            report = asyncio.run(vc.check_all(mgr))
        
        if format == "json":
            output = {
                "tools": [
                    {
                        "tool": s.tool,
                        "manager": s.manager,
                        "expected_version": s.expected_version,
                        "actual_version": s.actual_version,
                        "status": s.status,
                        "has_drift": s.has_drift,
                        "is_installed": s.is_installed
                    }
                    for s in report.statuses
                ],
                "summary": {
                    "total_count": report.total_count,
                    "ok_count": report.ok_count,
                    "drift_count": report.drift_count,
                    "missing_count": report.missing_count,
                    "has_drift": report.has_drift
                }
            }
            console.print_json(data=output)
        
        elif format == "markdown":
            # Generate markdown report
            md = "# Version Control Report\n\n"
            md += f"**Total Tools**: {report.total_count}\n"
            md += f"**Status**: {'❌ Drift Detected' if report.has_drift else '✅ All OK'}\n\n"
            
            md += "## Summary\n\n"
            md += f"- ✅ OK: {report.ok_count}\n"
            md += f"- ⚠️ Drift: {report.drift_count}\n"
            md += f"- ❌ Missing: {report.missing_count}\n\n"
            
            md += "## Tools\n\n"
            md += "| Tool | Manager | Expected | Actual | Status |\n"
            md += "|------|---------|----------|--------|--------|\n"
            
            for s in report.statuses:
                status_icon = {
                    "ok": "✅",
                    "drift": "⚠️",
                    "missing": "❌",
                    "unexpected": "❓"
                }.get(s.status, "?")
                
                md += f"| {s.tool} | {s.manager} | {s.expected_version or 'Any'} | {s.actual_version or '—'} | {status_icon} {s.status} |\n"
            
            console.print(md)
        
        else:  # table format
            table = Table(title="Version Control Report")
            table.add_column("Tool", style="cyan")
            table.add_column("Manager", style="yellow")
            table.add_column("Expected", style="white")
            table.add_column("Actual", style="white")
            table.add_column("Drift", style="white")
            table.add_column("Installed", style="white")
            
            for s in report.statuses:
                drift_display = "Yes" if s.has_drift else "No"
                drift_style = "red" if s.has_drift else "green"
                
                installed_display = "Yes" if s.is_installed else "No"
                installed_style = "green" if s.is_installed else "red"
                
                table.add_row(
                    s.tool,
                    s.manager,
                    s.expected_version or "Any",
                    s.actual_version or "—",
                    f"[{drift_style}]{drift_display}[/{drift_style}]",
                    f"[{installed_style}]{installed_display}[/{installed_style}]"
                )
            
            console.print(table)
            
            # Summary panel
            from rich.panel import Panel
            
            summary = f"""[bold]Total:[/bold] {report.total_count} tools
[green]OK:[/green] {report.ok_count}
[yellow]Drift:[/yellow] {report.drift_count}
[red]Missing:[/red] {report.missing_count}

[bold]Overall Status:[/bold] {'[yellow]Drift Detected[/yellow]' if report.has_drift else '[green]All OK[/green]'}"""
            
            console.print(Panel(summary, title="Summary", border_style="blue"))
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()
