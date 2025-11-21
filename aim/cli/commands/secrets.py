"""CLI commands for secrets management.

Commands:
- aim secrets set <KEY> <VALUE>       - Store a secret
- aim secrets get <KEY>               - Retrieve a secret
- aim secrets list                    - List all secrets
- aim secrets delete <KEY>            - Delete a secret
- aim secrets export [KEYS...]        - Export to environment

Contract Version: AIM_PLUS_V1
"""

import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional

from aim.environment.secrets import get_secrets_manager
from aim.environment.exceptions import SecretsError


console = Console()


@click.group(name="secrets")
def secrets_cli():
    """Manage secrets securely using system keyring."""
    pass


@secrets_cli.command(name="set")
@click.argument("key")
@click.argument("value", required=False)
@click.option("--description", "-d", default="", help="Secret description")
@click.option("--prompt", "-p", is_flag=True, help="Prompt for value securely")
def set_secret(key: str, value: Optional[str], description: str, prompt: bool):
    """Store a secret securely.
    
    Examples:
        aim secrets set OPENAI_API_KEY sk-...
        aim secrets set OPENAI_API_KEY --prompt --description "OpenAI API Key"
    """
    try:
        if prompt or value is None:
            value = click.prompt(f"Enter value for {key}", hide_input=True)
        
        manager = get_secrets_manager()
        manager.set_secret(key, value, description)
        
        console.print(f"✓ Secret '{key}' stored successfully", style="green")
        
    except SecretsError as e:
        console.print(f"✗ Failed to store secret: {e}", style="red")
        raise click.Abort()


@secrets_cli.command(name="get")
@click.argument("key")
@click.option("--clipboard", "-c", is_flag=True, help="Copy to clipboard")
@click.option("--show", "-s", is_flag=True, help="Show value (insecure)")
def get_secret(key: str, clipboard: bool, show: bool):
    """Retrieve a secret.
    
    Examples:
        aim secrets get OPENAI_API_KEY --show
        aim secrets get OPENAI_API_KEY --clipboard
    """
    try:
        manager = get_secrets_manager()
        value = manager.get_secret(key)
        
        if value is None:
            console.print(f"✗ Secret '{key}' not found", style="yellow")
            return
        
        if clipboard:
            try:
                import pyperclip
                pyperclip.copy(value)
                console.print(f"✓ Secret '{key}' copied to clipboard", style="green")
            except ImportError:
                console.print("⚠ pyperclip not installed. Install with: pip install pyperclip", style="yellow")
                if show:
                    console.print(f"{key}: {value}")
        elif show:
            console.print(f"{key}: {value}")
        else:
            console.print(f"✓ Secret '{key}' exists", style="green")
            console.print("Use --show to display or --clipboard to copy", style="dim")
        
    except SecretsError as e:
        console.print(f"✗ Failed to retrieve secret: {e}", style="red")
        raise click.Abort()


@secrets_cli.command(name="list")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def list_secrets(json_output: bool):
    """List all stored secrets.
    
    Examples:
        aim secrets list
        aim secrets list --json
    """
    try:
        manager = get_secrets_manager()
        secrets = manager.list_secrets()
        
        if json_output:
            import json
            click.echo(json.dumps(secrets, indent=2))
            return
        
        if not secrets:
            console.print("No secrets stored", style="yellow")
            return
        
        table = Table(title="Stored Secrets")
        table.add_column("Key", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Created", style="dim")
        table.add_column("Status", style="green")
        
        for secret in secrets:
            status = "✓" if secret["exists"] else "✗"
            table.add_row(
                secret["key"],
                secret["description"] or "-",
                secret["created_at"],
                status
            )
        
        console.print(table)
        
    except SecretsError as e:
        console.print(f"✗ Failed to list secrets: {e}", style="red")
        raise click.Abort()


@secrets_cli.command(name="delete")
@click.argument("key")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_secret(key: str, yes: bool):
    """Delete a secret.
    
    Examples:
        aim secrets delete OPENAI_API_KEY
        aim secrets delete OPENAI_API_KEY --yes
    """
    try:
        if not yes:
            if not click.confirm(f"Delete secret '{key}'?"):
                console.print("Cancelled", style="yellow")
                return
        
        manager = get_secrets_manager()
        deleted = manager.delete_secret(key)
        
        if deleted:
            console.print(f"✓ Secret '{key}' deleted", style="green")
        else:
            console.print(f"✗ Secret '{key}' not found", style="yellow")
        
    except SecretsError as e:
        console.print(f"✗ Failed to delete secret: {e}", style="red")
        raise click.Abort()


@secrets_cli.command(name="export")
@click.argument("keys", nargs=-1)
@click.option("--all", "export_all", is_flag=True, help="Export all secrets")
def export_secrets(keys: tuple[str], export_all: bool):
    """Export secrets to environment variables (current session only).
    
    Examples:
        aim secrets export OPENAI_API_KEY ANTHROPIC_API_KEY
        aim secrets export --all
    """
    try:
        manager = get_secrets_manager()
        
        if export_all:
            keys_to_export = None
        elif keys:
            keys_to_export = list(keys)
        else:
            console.print("Specify keys to export or use --all", style="yellow")
            return
        
        manager.export_to_env(keys_to_export)
        
        exported = manager.inject_into_env(keys_to_export)
        console.print(f"✓ Exported {len(exported)} secret(s) to environment", style="green")
        
        for key in exported:
            console.print(f"  - {key}", style="dim")
        
    except SecretsError as e:
        console.print(f"✗ Failed to export secrets: {e}", style="red")
        raise click.Abort()


if __name__ == "__main__":
    secrets_cli()
