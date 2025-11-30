"""
CLI commands for environment scanning.

Commands:
- aim scan all           - Run complete scan
- aim scan duplicates    - Find duplicate files
- aim scan caches        - Find misplaced caches
- aim scan clean         - Clean up caches
"""
DOC_ID: DOC-PAT-COMMANDS-SCAN-418

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from modules.aim_environment.m01001B_scanner import EnvironmentScanner
from modules.aim_registry.m01001C_config_loader import ConfigLoader


console = Console()


@click.group(name="scan")
def scan_cli():
    """Environment scanning and cleanup."""
    pass


@scan_cli.command(name="all")
@click.option(
    "--min-size",
    type=int,
    default=100,
    help="Minimum file size in KB for duplicate detection (default: 100)"
)
@click.option(
    "--json-output",
    "-j",
    is_flag=True,
    help="Output results as JSON"
)
def scan_all(min_size: int, json_output: bool):
    """Run complete environment scan."""
    try:
        config = ConfigLoader().load()
        scanner_config = config.get("environment", {}).get("scanner", {})
        
        # Get scan roots
        roots = scanner_config.get("roots", [])
        if not roots:
            console.print("[yellow]No scan roots configured[/yellow]")
            return
        
        roots = [Path(r) for r in roots]
        
        # Get central cache
        central_cache = config.get("environment", {}).get("centralCache")
        central_cache = Path(central_cache) if central_cache else None
        
        # Run scan
        with console.status("[bold blue]Scanning environment..."):
            scanner = EnvironmentScanner()
            report = scanner.scan(roots, min_size, central_cache)
        
        if json_output:
            output = {
                "duplicates": [
                    {
                        "hash": d.file_hash,
                        "files": d.files,
                        "size_mb": d.size_mb,
                        "wasted_mb": d.wasted_mb
                    }
                    for d in report.duplicates
                ],
                "misplaced_caches": [
                    {
                        "path": c.path,
                        "pattern": c.pattern,
                        "size_mb": c.size_mb,
                        "file_count": c.file_count
                    }
                    for c in report.misplaced_caches
                ],
                "summary": {
                    "total_scanned_files": report.total_scanned_files,
                    "total_scanned_mb": report.total_scanned_bytes / (1024 * 1024),
                    "total_wasted_mb": report.total_wasted_mb,
                    "total_cache_mb": report.total_cache_mb
                }
            }
            console.print_json(data=output)
        else:
            # Display duplicates
            if report.duplicates:
                table = Table(title="Duplicate Files")
                table.add_column("Hash", style="cyan")
                table.add_column("Files", style="yellow")
                table.add_column("Size (MB)", style="green")
                table.add_column("Wasted (MB)", style="red")
                
                for dup in report.duplicates[:10]:  # Top 10
                    table.add_row(
                        dup.file_hash[:16] + "...",
                        str(len(dup.files)),
                        f"{dup.size_mb:.2f}",
                        f"{dup.wasted_mb:.2f}"
                    )
                
                console.print(table)
                
                if len(report.duplicates) > 10:
                    console.print(f"\n[dim]... and {len(report.duplicates) - 10} more duplicate groups[/dim]")
            
            # Display caches
            if report.misplaced_caches:
                table = Table(title="Misplaced Caches")
                table.add_column("Path", style="cyan")
                table.add_column("Pattern", style="yellow")
                table.add_column("Size (MB)", style="green")
                table.add_column("Files", style="white")
                
                for cache in report.misplaced_caches[:10]:  # Top 10
                    table.add_row(
                        cache.path[:50] + "..." if len(cache.path) > 50 else cache.path,
                        cache.pattern,
                        f"{cache.size_mb:.2f}",
                        str(cache.file_count)
                    )
                
                console.print(table)
                
                if len(report.misplaced_caches) > 10:
                    console.print(f"\n[dim]... and {len(report.misplaced_caches) - 10} more caches[/dim]")
            
            # Summary
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  Scanned: {report.total_scanned_files:,} files ({report.total_scanned_bytes / (1024**3):.2f} GB)")
            console.print(f"  Duplicates: {len(report.duplicates)} groups wasting {report.total_wasted_mb:.2f} MB")
            console.print(f"  Caches: {len(report.misplaced_caches)} locations using {report.total_cache_mb:.2f} MB")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@scan_cli.command(name="duplicates")
@click.option(
    "--min-size",
    type=int,
    default=100,
    help="Minimum file size in KB (default: 100)"
)
@click.option(
    "--extension",
    "-e",
    multiple=True,
    help="File extensions to scan (e.g., .py, .js)"
)
@click.option(
    "--json-output",
    "-j",
    is_flag=True,
    help="Output results as JSON"
)
def scan_duplicates(min_size: int, extension: tuple, json_output: bool):
    """Find duplicate files by hash."""
    try:
        config = ConfigLoader().load()
        scanner_config = config.get("environment", {}).get("scanner", {})
        
        roots = scanner_config.get("roots", [])
        if not roots:
            console.print("[yellow]No scan roots configured[/yellow]")
            return
        
        roots = [Path(r) for r in roots]
        extensions = list(extension) if extension else None
        
        with console.status("[bold blue]Scanning for duplicates..."):
            scanner = EnvironmentScanner()
            duplicates = scanner.find_duplicates(roots, min_size, extensions)
        
        if json_output:
            output = [
                {
                    "hash": d.file_hash,
                    "files": d.files,
                    "size_mb": d.size_mb,
                    "wasted_mb": d.wasted_mb
                }
                for d in duplicates
            ]
            console.print_json(data=output)
        else:
            if not duplicates:
                console.print("[green]No duplicates found[/green]")
                return
            
            table = Table(title=f"Duplicate Files (min {min_size} KB)")
            table.add_column("Hash", style="cyan")
            table.add_column("Count", style="yellow")
            table.add_column("Size (MB)", style="green")
            table.add_column("Wasted (MB)", style="red")
            table.add_column("Files", style="white")
            
            for dup in duplicates[:20]:  # Top 20
                files_preview = "\n".join(dup.files[:3])
                if len(dup.files) > 3:
                    files_preview += f"\n... and {len(dup.files) - 3} more"
                
                table.add_row(
                    dup.file_hash[:16] + "...",
                    str(len(dup.files)),
                    f"{dup.size_mb:.2f}",
                    f"{dup.wasted_mb:.2f}",
                    files_preview
                )
            
            console.print(table)
            
            total_wasted = sum(d.wasted_mb for d in duplicates)
            console.print(f"\n[bold]Total:[/bold] {len(duplicates)} duplicate groups wasting {total_wasted:.2f} MB")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@scan_cli.command(name="caches")
@click.option(
    "--json-output",
    "-j",
    is_flag=True,
    help="Output results as JSON"
)
def scan_caches(json_output: bool):
    """Find misplaced cache directories."""
    try:
        config = ConfigLoader().load()
        scanner_config = config.get("environment", {}).get("scanner", {})
        
        roots = scanner_config.get("roots", [])
        if not roots:
            console.print("[yellow]No scan roots configured[/yellow]")
            return
        
        roots = [Path(r) for r in roots]
        
        central_cache = config.get("environment", {}).get("centralCache")
        central_cache = Path(central_cache) if central_cache else None
        
        cache_patterns = scanner_config.get("cachePatterns")
        
        with console.status("[bold blue]Scanning for caches..."):
            scanner = EnvironmentScanner(cache_patterns)
            caches = scanner.find_misplaced_caches(roots, central_cache)
        
        if json_output:
            output = [
                {
                    "path": c.path,
                    "pattern": c.pattern,
                    "size_mb": c.size_mb,
                    "file_count": c.file_count
                }
                for c in caches
            ]
            console.print_json(data=output)
        else:
            if not caches:
                console.print("[green]No misplaced caches found[/green]")
                return
            
            table = Table(title="Misplaced Cache Directories")
            table.add_column("Path", style="cyan", no_wrap=False)
            table.add_column("Pattern", style="yellow")
            table.add_column("Size (MB)", style="green")
            table.add_column("Files", style="white")
            
            for cache in caches[:20]:  # Top 20
                table.add_row(
                    cache.path,
                    cache.pattern,
                    f"{cache.size_mb:.2f}",
                    str(cache.file_count)
                )
            
            console.print(table)
            
            total_mb = sum(c.size_mb for c in caches)
            total_files = sum(c.file_count for c in caches)
            console.print(f"\n[bold]Total:[/bold] {len(caches)} caches using {total_mb:.2f} MB ({total_files:,} files)")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@scan_cli.command(name="clean")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting"
)
@click.option(
    "--pattern",
    "-p",
    help="Only clean caches matching this pattern"
)
def scan_clean(dry_run: bool, pattern: str):
    """Clean up misplaced cache directories."""
    try:
        config = ConfigLoader().load()
        scanner_config = config.get("environment", {}).get("scanner", {})
        
        roots = scanner_config.get("roots", [])
        if not roots:
            console.print("[yellow]No scan roots configured[/yellow]")
            return
        
        roots = [Path(r) for r in roots]
        
        central_cache = config.get("environment", {}).get("centralCache")
        central_cache = Path(central_cache) if central_cache else None
        
        cache_patterns = scanner_config.get("cachePatterns")
        
        with console.status("[bold blue]Finding caches to clean..."):
            scanner = EnvironmentScanner(cache_patterns)
            caches = scanner.find_misplaced_caches(roots, central_cache)
        
        # Filter by pattern if specified
        if pattern:
            caches = [c for c in caches if c.pattern == pattern]
        
        if not caches:
            console.print("[green]No caches to clean[/green]")
            return
        
        # Show what will be cleaned
        table = Table(title="Caches to Clean" + (" (DRY RUN)" if dry_run else ""))
        table.add_column("Path", style="cyan")
        table.add_column("Pattern", style="yellow")
        table.add_column("Size (MB)", style="green")
        
        total_mb = 0
        for cache in caches:
            table.add_row(cache.path, cache.pattern, f"{cache.size_mb:.2f}")
            total_mb += cache.size_mb
        
        console.print(table)
        console.print(f"\n[bold]Total to clean:[/bold] {total_mb:.2f} MB")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - no files were deleted[/yellow]")
            return
        
        # Confirm deletion
        if not click.confirm("\nProceed with cleanup?", default=False):
            console.print("[yellow]Cleanup cancelled[/yellow]")
            return
        
        # Clean caches
        cleaned = 0
        failed = 0
        
        with console.status("[bold blue]Cleaning caches..."):
            for cache in caches:
                try:
                    if scanner.cleanup_cache(Path(cache.path)):
                        cleaned += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        
        console.print(f"\n[green]Cleaned {cleaned} caches[/green]")
        if failed > 0:
            console.print(f"[yellow]Failed to clean {failed} caches[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()
