"""AIM+ Unified CLI

Main entry point for the AIM+ command-line interface.

Commands:
- aim secrets    - Secret management
- aim health     - Health checks
- aim setup      - Bootstrap environment (Phase 2B)
- aim tools      - Tool management (Phase 2B)
- aim scan       - Environment scanner (Phase 3A)
- aim version    - Version control (Phase 3B)

Contract Version: AIM_PLUS_V1
"""

import click
from rich.console import Console

from aim.cli.commands.secrets import secrets_cli
from aim.cli.commands.health import health_cli
from aim.cli.commands.tools import tools
from aim.cli.commands.scan import scan_cli


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="AIM+")
def cli():
    """AIM+ - Unified AI Development Environment Manager
    
    Manage AI tools, secrets, environment configuration, and system health.
    
    Examples:
        aim secrets list
        aim health check
        aim tools install-all
        aim scan all
        aim --help
    """
    pass


# Register command groups
cli.add_command(secrets_cli)
cli.add_command(health_cli)
cli.add_command(tools)
cli.add_command(scan_cli)


@cli.command(name="status")
def status():
    """Quick status overview.
    
    Shows system health and configuration summary.
    """
    from aim.environment.health import HealthMonitor
    from aim.registry.config_loader import load_config
    
    console.print("\n[bold cyan]AIM+ System Status[/bold cyan]\n")
    
    # Load config
    try:
        config = load_config(validate=False)
        console.print(f"[green]✓[/green] Config: v{config.get('version', 'unknown')}")
        
        # Show tool count
        tools = config.get("registry", {}).get("tools", {})
        console.print(f"[green]✓[/green] AI Tools: {len(tools)} configured")
    except Exception as e:
        console.print(f"[red]✗[/red] Config: {e}")
    
    # Run quick health check
    try:
        monitor = HealthMonitor()
        report = monitor.generate_report()
        
        status_color = {
            "healthy": "green",
            "degraded": "yellow",
            "unhealthy": "red"
        }.get(report["overall_status"], "white")
        
        console.print(f"[{status_color}]●[/{status_color}] Health: {report['overall_status']}")
        
        summary = report["summary"]
        console.print(f"  Pass: {summary['pass']}, Warn: {summary['warn']}, Fail: {summary['fail']}")
    except Exception as e:
        console.print(f"[red]✗[/red] Health check failed: {e}")
    
    console.print()


if __name__ == "__main__":
    cli()
