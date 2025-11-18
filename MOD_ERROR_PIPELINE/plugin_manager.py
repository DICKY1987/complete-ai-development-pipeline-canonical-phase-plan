"""Compatibility shim for legacy imports.

Re-exports the section-aligned implementation from the `error` package.
"""
from error.plugin_manager import PluginManager, BasePlugin  # type: ignore F401

