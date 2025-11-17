"""Plugins Module - Extensible plugin ecosystem for tool integrations.

This module provides a plugin architecture for integrating external tools
(linters, formatters, type checkers, security scanners) into the pipeline.

Each plugin follows a standard contract:
    - check_tool_available() -> bool
    - build_command(file_path: Path) -> List[str]
    - execute(file_path: Path) -> PluginResult

Plugins are organized by category:
    - Python: black, isort, ruff, pylint, mypy, pyright, bandit, safety
    - JavaScript/TypeScript: prettier, eslint
    - PowerShell: PSScriptAnalyzer
    - Markup/Data: yamllint, mdformat, markdownlint, jq
    - Cross-Cutting: codespell, semgrep, gitleaks

Plugin Registration:
    Each plugin module exports a register() function that returns the plugin instance.
    The error pipeline discovers and loads plugins dynamically.

Public API:
    Plugins are registered via individual plugin.py::register() functions.
    See src/utils/types.py for PluginResult and PluginIssue data structures.
"""

from __future__ import annotations

# Plugins register themselves via plugin.py::register()
# No central exports needed - discovery is dynamic

__all__ = []

