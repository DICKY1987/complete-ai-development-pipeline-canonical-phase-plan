"""AIM+ CLI Module

Command-line interface for AIM+ operations.

This module provides:
- Secret management (set, get, list, delete)
- Health checks and diagnostics
- Tool installation and management
- Environment scanning
- Version control and compatibility checking
- Audit log querying and export

Public API:
    cli - Main CLI entry point (Click command group)

Usage:
    # As module
    python -m aim.cli <command>
    
    # Direct import
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.cli import cli
    
    # In code
    from click.testing import CliRunner
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.cli import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ['health', 'check'])
"""
DOC_ID: DOC-PAT-AIM-CLI-INIT-374
DOC_ID: DOC-PAT-AIM-CLI-INIT-330

__version__ = "1.0.0"

from .main import cli

__all__ = ["cli"]
