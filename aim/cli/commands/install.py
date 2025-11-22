"""
CLI commands for tool installation and management.

Commands:
    aim install <tool>          - Install a specific tool
    aim install --all           - Install all configured tools
    aim install --pipx-only     - Install only Python tools
    aim install --npm-only      - Install only Node tools
    aim verify <tool>           - Verify tool installation
    aim bootstrap               - Bootstrap entire development environment
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json

from aim.environment.installer import get_installer, InstallResult


console = Console()


@click.group()
def install():
    """Tool installation and management commands."""
    pass


@install.command("tool")
@click.argument("tool_name")
@click.option("--version", help="Specific version to install")
@click.option("--manager", type=click.Choice(["pipx", "npm", "auto"]), default="auto",
              help="Package manager to use")
def install_tool(tool_name: str, version: str, manager: str):
    """Install a specific tool."""
    installer = get_installer()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Installing {tool_name}...", total=None)
        
        if manager == "pipx" or (manager == "auto" and not tool_name.startswith("@")):
            result = installer.install_pipx_tool(tool_name, version)
        else:
            result = installer.install_npm_tool(tool_name, version)
        
        progress.update(task, completed=True)
    
    if result.success:
        console.print(f"✓ {result.message}", style="green")
        if result.version:
            console.print(f"  Version: {result.version}", style="dim")
    else:
        console.print(f"✗ {result.message}", style="red")
        for error in result.errors:
            console.print(f"  {error}", style="dim red")


@install.command("all")
@click.option("--pipx-only", is_flag=True, help="Install only Python tools")
@click.option("--npm-only", is_flag=True, help="Install only Node tools")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
def install_all(pipx_only: bool, npm_only: bool, output_json: bool):
    """Install all configured tools."""
    installer = get_installer()
    
    if output_json:
        results = installer.install_all()
        summary = installer.get_install_summary(results)
        console.print_json(json.dumps(summary, indent=2))
        return
    
    console.print("\n[bold cyan]AIM+ Tool Installation[/bold cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing tools...", total=None)
        
        results = installer.install_all()
        summary = installer.get_install_summary(results)
        
        progress.update(task, completed=True)
    
    # Display results table
    table = Table(title="Installation Results")
    table.add_column("Tool", style="cyan")
    table.add_column("Manager", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Message")
    
    for manager, manager_results in results.items():
        for result in manager_results:
            status = "✓" if result.success else "✗"
            status_style = "green" if result.success else "red"
            
            table.add_row(
                result.tool_name,
                result.package_manager,
                f"[{status_style}]{status}[/{status_style}]",
                result.version or "-",
                result.message
            )
    
    console.print(table)
    
    # Display summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total: {summary['total']}")
    console.print(f"  [green]Successful: {summary['successful']}[/green]")
    if summary['failed'] > 0:
        console.print(f"  [red]Failed: {summary['failed']}[/red]")
    console.print(f"  Success Rate: {summary['success_rate']}\n")


@install.command("verify")
@click.argument("tool_name")
def verify_tool(tool_name: str):
    """Verify a tool is installed and accessible."""
    installer = get_installer()
    
    is_installed = installer.verify_installation(tool_name)
    
    if is_installed:
        console.print(f"✓ {tool_name} is installed and accessible", style="green")
    else:
        console.print(f"✗ {tool_name} is not found in PATH", style="red")
        raise click.exceptions.Exit(1)


@install.command("bootstrap")
@click.option("--skip-health", is_flag=True, help="Skip pre-installation health checks")
@click.option("--dry-run", is_flag=True, help="Show what would be installed without installing")
def bootstrap(skip_health: bool, dry_run: bool):
    """Bootstrap the complete AIM+ development environment.
    
    This command:
    1. Runs health checks (unless --skip-health)
    2. Installs package managers (pipx, npm)
    3. Installs all configured tools
    4. Verifies installations
    5. Generates setup report
    """
    console.print("\n[bold cyan]AIM+ Environment Bootstrap[/bold cyan]\n")
    
    # Health checks
    if not skip_health:
        from aim.environment.health import check_health
        
        console.print("[bold]Step 1: Health Checks[/bold]")
        health = check_health()
        
        if health["overall_status"] == "unhealthy":
            console.print("[red]✗ System health check failed. Fix issues before bootstrapping.[/red]")
            console.print("Run 'aim health check' for details")
            raise click.exceptions.Exit(1)
        
        console.print("[green]✓ Health checks passed[/green]\n")
    
    # Check package managers
    console.print("[bold]Step 2: Package Manager Verification[/bold]")
    installer = get_installer()
    
    pipx_ok, pipx_msg = installer.check_package_manager("pipx")
    npm_ok, npm_msg = installer.check_package_manager("npm")
    
    if pipx_ok:
        console.print(f"[green]✓ pipx: {pipx_msg}[/green]")
    else:
        console.print(f"[yellow]⚠ pipx: {pipx_msg} - will attempt to install[/yellow]")
    
    if npm_ok:
        console.print(f"[green]✓ npm: {npm_msg}[/green]")
    else:
        console.print(f"[yellow]⚠ npm: {npm_msg} - ensure Node.js is installed[/yellow]")
    
    console.print()
    
    if dry_run:
        console.print("[yellow]Dry run mode - showing what would be installed:[/yellow]\n")
        config = installer.config
        
        console.print("[bold]Python tools (pipx):[/bold]")
        for tool in config.get("pipx_tools", []):
            console.print(f"  • {tool}")
        
        console.print("\n[bold]Node tools (npm):[/bold]")
        for tool in config.get("npm_global", []):
            console.print(f"  • {tool}")
        
        return
    
    # Install all tools
    console.print("[bold]Step 3: Installing Tools[/bold]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing all configured tools...", total=None)
        results = installer.install_all()
        progress.update(task, completed=True)
    
    summary = installer.get_install_summary(results)
    
    # Display results
    console.print(f"\n[bold green]✓ Bootstrap Complete![/bold green]")
    console.print(f"  Installed: {summary['successful']}/{summary['total']} tools")
    console.print(f"  Success Rate: {summary['success_rate']}\n")
    
    if summary['failed'] > 0:
        console.print("[yellow]Some tools failed to install. Run 'aim install all --json' for details[/yellow]")


def register_commands(cli_group):
    """Register install commands with the main CLI."""
    cli_group.add_command(install)
