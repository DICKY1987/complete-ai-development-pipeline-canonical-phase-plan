"""Orchestrator CLI for workstream execution.

DOC_ID: DOC-CORE-CLI-ORCHESTRATOR-001
"""

import click
import json
import yaml
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from core.engine.orchestrator import Orchestrator


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Orchestrator CLI for running workstreams."""
    pass


@cli.command()
@click.option("--plan", required=True, type=click.Path(exists=True))
@click.option("--phase", required=True)
@click.option("--workstream", default=None)
@click.option("--project", default="user")
@click.option("--timeout", default=3600, type=int)
def run(plan, phase, workstream, project, timeout):
    """Execute a plan via orchestrator."""
    orch = Orchestrator()
    run_id = orch.create_run(project, phase, workstream)
    click.echo(f"Created run: {run_id}")
    click.echo(f"Plan: {plan}, Phase: {phase}")
    return 0


@cli.command()
@click.argument("run_id")
@click.option("--format", type=click.Choice(["json", "yaml", "text"]), default="text")
def status(run_id, format):
    """Get run status."""
    orch = Orchestrator()
    status_data = orch.get_run_status(run_id)
    
    if not status_data:
        click.echo(f"Run {run_id} not found", err=True)
        return 1
    
    if format == "json":
        click.echo(json.dumps(status_data, indent=2))
    elif format == "yaml":
        click.echo(yaml.dump(status_data))
    else:
        click.echo(f"Run ID: {status_data['run_id']}")
        click.echo(f"State: {status_data['state']}")
    return 0


@cli.command()
@click.option("--phase", help="Filter by phase")
@click.option("--limit", default=10, type=int)
def list(phase, limit):
    """List recent runs."""
    orch = Orchestrator()
    click.echo(f"Listing runs (phase={phase}, limit={limit})")
    return 0


if __name__ == "__main__":
    cli()
