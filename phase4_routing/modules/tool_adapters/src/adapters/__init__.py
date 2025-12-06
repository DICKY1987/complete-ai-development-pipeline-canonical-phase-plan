"""
DEPRECATED: This module has been consolidated into core.adapters

All adapter classes have been moved to core/adapters/:
- base.py -> core.adapters.base
- registry.py -> core.adapters.registry
- subprocess_adapter.py -> core.adapters.subprocess_adapter

This file redirects imports for backward compatibility.
Original files archived: _ARCHIVE/phase4_tool_adapters_duplicate_20251204_143544/
"""
DOC_ID: DOC-CORE-ADAPTERS-INIT-846

# Redirect imports to canonical location
from core.adapters.base import ExecutionResult, ToolAdapter, ToolConfig
from core.adapters.registry import AdapterRegistry
from core.adapters.subprocess_adapter import SubprocessAdapter

__all__ = [
    "ToolAdapter",
    "ToolConfig",
    "ExecutionResult",
    "AdapterRegistry",
    "SubprocessAdapter",
]
