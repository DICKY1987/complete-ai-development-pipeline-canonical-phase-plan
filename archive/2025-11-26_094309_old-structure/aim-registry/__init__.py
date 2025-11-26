"""AIM+ Registry Module

Tool capability registry, configuration loading, and routing logic.

This module provides:
- Configuration loading and validation
- JSON schema validation
- Environment variable expansion
- Tool capability definitions

Public API:
    ConfigLoader - Load and validate AIM configuration

Usage:
    from aim.registry import ConfigLoader
    
    loader = ConfigLoader()
    config = loader.load(validate=True)
"""

from .config_loader import ConfigLoader

__all__ = ["ConfigLoader"]
