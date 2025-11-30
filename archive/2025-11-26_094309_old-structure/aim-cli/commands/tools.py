"""
CLI commands for tool installation and management.

Provides commands to install, update, and manage development tools
via pipx, npm, and winget.
"""
DOC_ID: DOC-PAT-COMMANDS-TOOLS-420

import asyncio
import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from modules.aim_registry.m01001C_config_loader import ConfigLoader
from modules.aim_environment.m01001B_installer import ToolInstaller


console = Console()


@click.group()
def tools():
    """Manage development tools installation."""
    pass


@tools.command()
@click.argument("package")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "winget"]),
    required=True,
    help="Package manager to use"
)
@click.option(
    "--version",
    "-v",
    default=None,
    help="Specific version to install (uses pinned version if not specified)"
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force reinstall even if already installed"
)
def install(package: str, manager: str, version: str, force: bool):
    """Install a single tool."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        
        with console.status(f"[bold blue]Installing {package} via {manager}..."):
            if manager == "pipx":
                result = asyncio.run(installer.install_pipx(package, version, force))
            elif manager == "npm":
                result = asyncio.run(installer.install_npm(package, version, force))
            elif manager == "winget":
                result = asyncio.run(installer.install_winget(package, version, force))
        
        if result.success:
            console.print(f"[green]✓[/green] {package} installed successfully (v{result.version})")
        else:
            console.print(f"[red]✗[/red] {package} installation failed: {result.message}")
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@tools.command()
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "all"]),
    default="all",
    help="Package manager to use (default: all)"
)
@click.option(
    "--rollback/--no-rollback",
    default=True,
    help="Rollback all installations on any failure (default: enabled)"
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Install in parallel or one at a time (default: parallel)"
)
def install_all(manager: str, rollback: bool, parallel: bool):
    """Install all tools from configuration."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        
        managers = ["pipx", "npm"] if manager == "all" else [manager]
        all_results = []
        
        for mgr in managers:
            console.print(f"\n[bold blue]Installing {mgr} packages...[/bold blue]")
            
            with console.status(f"[bold blue]Installing via {mgr}..."):
                results = asyncio.run(
                    installer.install_from_config(mgr, rollback_on_failure=rollback)
                )
                all_results.extend(results)
            
            # Display results
            table = Table(title=f"{mgr.upper()} Installation Results")
            table.add_column("Package", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Version", style="yellow")
            table.add_column("Message", style="white")
            
            for result in results:
                status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
                table.add_row(
                    result.tool,
                    status,
                    result.version or "N/A",
                    result.message
                )
            
            console.print(table)
        
        # Summary
        total = len(all_results)
        successful = sum(1 for r in all_results if r.success)
        failed = total - successful
        
        console.print(f"\n[bold]Summary:[/bold] {successful}/{total} successful, {failed} failed")
        
        if failed > 0:
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@tools.command()
@click.argument("package")
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm"]),
    required=True,
    help="Package manager to use"
)
def uninstall(package: str, manager: str):
    """Uninstall a tool."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        
        with console.status(f"[bold blue]Uninstalling {package}..."):
            if manager == "pipx":
                success = asyncio.run(installer.uninstall_pipx(package))
            elif manager == "npm":
                success = asyncio.run(installer.uninstall_npm(package))
        
        if success:
            console.print(f"[green]✓[/green] {package} uninstalled successfully")
        else:
            console.print(f"[red]✗[/red] {package} uninstall failed")
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@tools.command()
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
def list(manager: str, json_output: bool):
    """List installed tools and versions."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        
        results = {}
        
        if manager in ["pipx", "all"]:
            pipx_apps = config.get("environment", {}).get("pipxApps", [])
            results["pipx"] = {}
            for package in pipx_apps:
                version = asyncio.run(installer._get_installed_version("pipx", package))
                results["pipx"][package] = version or "Not installed"
        
        if manager in ["npm", "all"]:
            npm_apps = config.get("environment", {}).get("npmGlobal", [])
            results["npm"] = {}
            for package in npm_apps:
                version = asyncio.run(installer._get_installed_version("npm", package))
                results["npm"][package] = version or "Not installed"
        
        if json_output:
            console.print_json(data=results)
        else:
            for mgr, packages in results.items():
                table = Table(title=f"{mgr.upper()} Tools")
                table.add_column("Package", style="cyan")
                table.add_column("Version", style="yellow")
                table.add_column("Status", style="white")
                
                for package, version in packages.items():
                    if version == "Not installed":
                        status = "[red]✗[/red]"
                        version_str = "—"
                    else:
                        status = "[green]✓[/green]"
                        version_str = version
                    
                    table.add_row(package, version_str, status)
                
                console.print(table)
                console.print()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@tools.command()
@click.option(
    "--manager",
    "-m",
    type=click.Choice(["pipx", "npm", "all"]),
    default="all",
    help="Package manager to check (default: all)"
)
def verify(manager: str):
    """Verify all configured tools are installed with correct versions."""
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        version_pins = config.get("environment", {}).get("versionPins", {})
        
        all_ok = True
        
        managers = ["pipx", "npm"] if manager == "all" else [manager]
        
        for mgr in managers:
            if mgr == "pipx":
                packages = config.get("environment", {}).get("pipxApps", [])
            else:
                packages = config.get("environment", {}).get("npmGlobal", [])
            
            table = Table(title=f"{mgr.upper()} Verification")
            table.add_column("Package", style="cyan")
            table.add_column("Expected", style="yellow")
            table.add_column("Actual", style="yellow")
            table.add_column("Status", style="white")
            
            for package in packages:
                installed_version = asyncio.run(installer._get_installed_version(mgr, package))
                pinned_version = version_pins.get(mgr, {}).get(package)
                
                if not installed_version:
                    status = "[red]Not installed[/red]"
                    all_ok = False
                elif pinned_version and installed_version != pinned_version:
                    status = f"[yellow]Version mismatch[/yellow]"
                    all_ok = False
                else:
                    status = "[green]✓[/green]"
                
                table.add_row(
                    package,
                    pinned_version or "Any",
                    installed_version or "—",
                    status
                )
            
            console.print(table)
            console.print()
        
        if all_ok:
            console.print("[green]All tools verified successfully[/green]")
        else:
            console.print("[yellow]Some tools need attention[/yellow]")
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()
