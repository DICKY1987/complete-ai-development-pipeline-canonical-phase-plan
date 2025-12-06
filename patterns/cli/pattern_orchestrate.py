"""Universal Pattern Execution CLI with Orchestrator Integration.

DOC_ID: DOC-PAT-CLI-PATTERN-ORCHESTRATE-001

This CLI provides a unified interface for executing patterns via the orchestrator,
with full telemetry, timeout enforcement, and event-driven automation support.

Usage:
    pattern execute --pattern-id PAT-ATOMIC-CREATE-001 --instance instance.yaml
    pattern list
    pattern info PAT-ATOMIC-CREATE-001
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

# Setup import paths
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import orchestration components
try:
    from patterns.automation.integration.orchestrator_hooks import PatternAutomationHooks
    from core.engine.orchestrator import Orchestrator
except ImportError as e:
    print(f"Error: Failed to import orchestration components: {e}", file=sys.stderr)
    print(f"Repository root: {repo_root}", file=sys.stderr)
    print("Ensure required modules are available.", file=sys.stderr)
    sys.exit(1)


def load_pattern_registry() -> list:
    """Load pattern registry from YAML."""
    registry_path = Path(__file__).parent.parent / "registry" / "PATTERN_INDEX.yaml"
    if not registry_path.exists():
        return []
    
    try:
        with open(registry_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('patterns', []) if data else []
    except Exception as e:
        print(f"Warning: Failed to load pattern registry: {e}", file=sys.stderr)
        return []


def load_pattern_from_registry(pattern_id: str) -> Optional[dict]:
    """Load specific pattern by ID from registry."""
    patterns = load_pattern_registry()
    for pattern in patterns:
        if pattern.get('id') == pattern_id or pattern.get('pattern_id') == pattern_id:
            return pattern
    return None


def find_executor_path(pattern: dict) -> Optional[Path]:
    """Find executor script path for a pattern."""
    executors_dir = Path(__file__).parent.parent / "executors"
    
    # Try executor field from pattern
    if 'executor' in pattern:
        executor_file = pattern['executor']
        if not executor_file.endswith('.ps1'):
            executor_file += '.ps1'
        path = executors_dir / executor_file
        if path.exists():
            return path
    
    # Try pattern ID-based naming
    pattern_id = pattern.get('id') or pattern.get('pattern_id', '')
    if pattern_id:
        # Try variations: PAT-ATOMIC-CREATE-001 -> atomic_create_executor.ps1
        name_parts = pattern_id.lower().replace('pat-', '').replace('-', '_')
        for suffix in ['_executor.ps1', '_001_executor.ps1', '.ps1']:
            test_path = executors_dir / f"{name_parts}{suffix}"
            if test_path.exists():
                return test_path
    
    return None


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Pattern execution CLI with full orchestration and telemetry."""
    pass


@cli.command()
@click.option('--pattern-id', required=True, help='Pattern ID (e.g., PAT-ATOMIC-CREATE-001)')
@click.option('--instance', type=click.Path(exists=True), help='Instance JSON/YAML file path')
@click.option('--timeout', default=300, type=int, help='Execution timeout in seconds (default: 300)')
@click.option('--no-telemetry', is_flag=True, help='Disable telemetry logging')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running')
def execute(pattern_id: str, instance: Optional[str], timeout: int, no_telemetry: bool, dry_run: bool):
    """Execute a pattern via orchestrator with full telemetry.
    
    Examples:
        pattern execute --pattern-id PAT-ATOMIC-CREATE-001 --instance input.yaml
        pattern execute --pattern-id PAT-BATCH-CREATE-001 --dry-run
    """
    # Load pattern from registry
    pattern = load_pattern_from_registry(pattern_id)
    if not pattern:
        click.echo(f"❌ Error: Pattern '{pattern_id}' not found in registry", err=True)
        click.echo("Run 'pattern list' to see available patterns", err=True)
        return 1
    
    # Find executor
    executor_path = find_executor_path(pattern)
    if not executor_path:
        click.echo(f"❌ Error: Executor not found for pattern '{pattern_id}'", err=True)
        click.echo(f"Expected in: patterns/executors/", err=True)
        return 1
    
    click.echo(f"📋 Pattern: {pattern.get('name', pattern_id)}")
    click.echo(f"🔧 Executor: {executor_path.name}")
    
    if dry_run:
        click.echo(f"🔍 Dry run - would execute:")
        click.echo(f"   powershell -File {executor_path}")
        if instance:
            click.echo(f"   -InputFile {instance}")
        click.echo(f"   -Timeout {timeout}")
        return 0
    
    # Initialize orchestrator and hooks
    try:
        hooks = PatternAutomationHooks(enabled=not no_telemetry)
        orch = Orchestrator()
    except Exception as e:
        click.echo(f"❌ Failed to initialize orchestrator: {e}", err=True)
        return 1
    
    # Create orchestrator run
    click.echo(f"🚀 Creating orchestrator run...")
    try:
        run_id = orch.create_run(
            project_id="patterns",
            phase_id="execution",
            metadata={
                "pattern_id": pattern_id,
                "instance": instance,
                "executor": str(executor_path)
            }
        )
        click.echo(f"   Run ID: {run_id}")
    except Exception as e:
        click.echo(f"❌ Failed to create run: {e}", err=True)
        return 1
    
    # Task start hook
    task_spec = {
        "pattern_id": pattern_id,
        "executor": str(executor_path),
        "inputs": {"instance": instance} if instance else {}
    }
    
    ctx = None
    if not no_telemetry:
        try:
            ctx = hooks.on_task_start(task_spec)
        except Exception as e:
            click.echo(f"⚠️  Warning: Telemetry start hook failed: {e}", err=True)
    
    # Execute PowerShell executor
    click.echo(f"⚙️  Executing pattern...")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(executor_path)]
    
    if instance:
        cmd.extend(["-InputFile", instance])
    
    try:
        result = subprocess.run(
            cmd,
            timeout=timeout,
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        success = result.returncode == 0
        
        # Display output
        if result.stdout:
            click.echo(result.stdout)
        
        if result.stderr and not success:
            click.echo(result.stderr, err=True)
        
        # Task complete hook
        if not no_telemetry:
            try:
                hooks.on_task_complete(
                    task_spec,
                    {
                        "success": success,
                        "exit_code": result.returncode,
                        "output": result.stdout[:500] if result.stdout else "",
                        "error": result.stderr[:500] if result.stderr else ""
                    },
                    ctx
                )
            except Exception as e:
                click.echo(f"⚠️  Warning: Telemetry complete hook failed: {e}", err=True)
        
        # Update orchestrator state
        try:
            state = "completed" if success else "failed"
            orch.update_run_state(run_id, state)
            click.echo(f"")
            if success:
                click.echo(f"✅ Run {run_id}: SUCCESS", err=False)
            else:
                click.echo(f"❌ Run {run_id}: FAILED (exit code {result.returncode})", err=True)
        except Exception as e:
            click.echo(f"⚠️  Warning: Failed to update orchestrator state: {e}", err=True)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        click.echo(f"❌ Execution timeout after {timeout} seconds", err=True)
        
        # Log timeout
        if not no_telemetry:
            try:
                hooks.on_task_complete(
                    task_spec,
                    {"success": False, "error": f"timeout after {timeout}s"},
                    ctx
                )
            except Exception:
                pass
        
        try:
            orch.update_run_state(run_id, "failed")
        except Exception:
            pass
        
        return 1
    
    except Exception as e:
        click.echo(f"❌ Execution error: {e}", err=True)
        
        if not no_telemetry:
            try:
                hooks.on_task_complete(
                    task_spec,
                    {"success": False, "error": str(e)},
                    ctx
                )
            except Exception:
                pass
        
        try:
            orch.update_run_state(run_id, "failed")
        except Exception:
            pass
        
        return 1


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def list(format: str):
    """List all available patterns from the registry.
    
    Examples:
        pattern list
        pattern list --format json
    """
    patterns = load_pattern_registry()
    
    if not patterns:
        click.echo("No patterns found in registry.")
        return 0
    
    if format == 'json':
        click.echo(json.dumps(patterns, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(patterns, default_flow_style=False))
    else:
        # Table format
        click.echo(f"{'ID':<30} {'Name':<40} {'Executor':<30}")
        click.echo("=" * 100)
        for p in patterns:
            pattern_id = p.get('id') or p.get('pattern_id', 'N/A')
            name = p.get('name', 'N/A')
            executor = p.get('executor', 'N/A')
            click.echo(f"{pattern_id:<30} {name:<40} {executor:<30}")
        
        click.echo(f"\nTotal patterns: {len(patterns)}")
    
    return 0


@cli.command()
@click.argument('pattern_id')
@click.option('--format', type=click.Choice(['text', 'json', 'yaml']), default='text', help='Output format')
def info(pattern_id: str, format: str):
    """Show detailed information about a specific pattern.
    
    Examples:
        pattern info PAT-ATOMIC-CREATE-001
        pattern info PAT-BATCH-CREATE-001 --format yaml
    """
    pattern = load_pattern_from_registry(pattern_id)
    
    if not pattern:
        click.echo(f"❌ Pattern '{pattern_id}' not found", err=True)
        return 1
    
    if format == 'json':
        click.echo(json.dumps(pattern, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(pattern, default_flow_style=False))
    else:
        # Text format
        click.echo(f"Pattern ID: {pattern.get('id') or pattern.get('pattern_id', 'N/A')}")
        click.echo(f"Name: {pattern.get('name', 'N/A')}")
        click.echo(f"Description: {pattern.get('description', 'N/A')}")
        click.echo(f"Executor: {pattern.get('executor', 'N/A')}")
        click.echo(f"Category: {pattern.get('category', 'N/A')}")
        
        if 'inputs' in pattern:
            click.echo(f"\nInputs:")
            for inp in pattern.get('inputs', []):
                click.echo(f"  - {inp}")
        
        if 'outputs' in pattern:
            click.echo(f"\nOutputs:")
            for out in pattern.get('outputs', []):
                click.echo(f"  - {out}")
        
        # Try to find executor
        executor_path = find_executor_path(pattern)
        if executor_path:
            click.echo(f"\nExecutor Path: {executor_path}")
            click.echo(f"Executor Exists: ✅")
        else:
            click.echo(f"\nExecutor Exists: ❌ Not found")
    
    return 0


@cli.command()
@click.option('--keyword', help='Search keyword in pattern name or description')
@click.option('--category', help='Filter by category')
def search(keyword: Optional[str], category: Optional[str]):
    """Search patterns by keyword or category.
    
    Examples:
        pattern search --keyword create
        pattern search --category automation
    """
    patterns = load_pattern_registry()
    
    if not patterns:
        click.echo("No patterns found in registry.")
        return 0
    
    # Filter patterns
    filtered = patterns
    
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [
            p for p in filtered
            if keyword_lower in p.get('name', '').lower()
            or keyword_lower in p.get('description', '').lower()
            or keyword_lower in str(p.get('id', '')).lower()
        ]
    
    if category:
        category_lower = category.lower()
        filtered = [
            p for p in filtered
            if category_lower == p.get('category', '').lower()
        ]
    
    if not filtered:
        click.echo(f"No patterns found matching criteria.")
        return 0
    
    # Display results
    click.echo(f"{'ID':<30} {'Name':<40} {'Category':<20}")
    click.echo("=" * 90)
    for p in filtered:
        pattern_id = p.get('id') or p.get('pattern_id', 'N/A')
        name = p.get('name', 'N/A')
        cat = p.get('category', 'N/A')
        click.echo(f"{pattern_id:<30} {name:<40} {cat:<20}")
    
    click.echo(f"\nFound {len(filtered)} pattern(s)")
    return 0


if __name__ == '__main__':
    cli()
