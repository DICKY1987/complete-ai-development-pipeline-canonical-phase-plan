"""CLI commands for health checks.

Commands:
- aim health check              - Run all health checks
- aim health check --json       - Output as JSON
- aim health report             - Generate detailed report

Contract Version: AIM_PLUS_V1
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from modules.aim_environment.m01001B_health import HealthMonitor, check_health


console = Console()


@click.group(name="health")
def health_cli():
    """System health checks and validation."""
    pass


@health_cli.command(name="check")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def check_health_cmd(json_output: bool, verbose: bool):
    """Run system health checks.
    
    Examples:
        aim health check
        aim health check --json
        aim health check --verbose
    """
    monitor = HealthMonitor()
    checks = monitor.check_all()
    
    if json_output:
        report = monitor.generate_report(checks)
        click.echo(json.dumps(report, indent=2))
        return
    
    # Display results in table
    table = Table(title="AIM+ Health Check Results", show_header=True)
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Message", style="white")
    
    for check in checks:
        # Color status based on result
        if check.status == "pass":
            status_str = "[green]✓ PASS[/green]"
        elif check.status == "warn":
            status_str = "[yellow]⚠ WARN[/yellow]"
        else:
            status_str = "[red]✗ FAIL[/red]"
        
        table.add_row(check.name, status_str, check.message)
    
    console.print(table)
    
    # Show overall status
    report = monitor.generate_report(checks)
    overall = report["overall_status"]
    
    if overall == "healthy":
        console.print("\n[bold green]✓ System is healthy[/bold green]")
    elif overall == "degraded":
        console.print("\n[bold yellow]⚠ System is degraded (some warnings)[/bold yellow]")
    else:
        console.print("\n[bold red]✗ System is unhealthy (failures detected)[/bold red]")
    
    # Show verbose details if requested
    if verbose:
        console.print("\n[bold]Details:[/bold]")
        for check in checks:
            if check.details:
                console.print(f"\n[cyan]{check.name}:[/cyan]")
                for key, value in check.details.items():
                    console.print(f"  {key}: {value}")


@health_cli.command(name="report")
@click.option("--output", "-o", type=click.Path(), help="Save report to file")
def generate_report_cmd(output: str):
    """Generate detailed health report.
    
    Examples:
        aim health report
        aim health report --output health_report.json
    """
    report = check_health()
    
    if output:
        # Save to file
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"✓ Report saved to {output}", style="green")
    else:
        # Display to console
        console.print(json.dumps(report, indent=2))


@health_cli.command(name="verify")
def verify_cmd():
    """Quick verification check (exit code 0 if healthy, 1 otherwise).
    
    Examples:
        aim health verify
        aim health verify && echo "System OK"
    """
    monitor = HealthMonitor()
    report = monitor.generate_report()
    
    if report["overall_status"] == "healthy":
        console.print("✓ System healthy", style="green")
        exit(0)
    elif report["overall_status"] == "degraded":
        console.print("⚠ System degraded", style="yellow")
        exit(1)
    else:
        console.print("✗ System unhealthy", style="red")
        exit(1)


if __name__ == "__main__":
    health_cli()
