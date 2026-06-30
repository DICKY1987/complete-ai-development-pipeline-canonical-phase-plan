"""Tool Adapters - WS-03-02A

Adapters for executing tasks via external tools.
"""

# DOC_ID: DOC-CORE-ADAPTERS-INIT-INIT-001

from .base import ExecutionResult, ToolAdapter, ToolConfig
from .registry import AdapterRegistry
from .subprocess_adapter import SubprocessAdapter

__all__ = [
    "ToolAdapter",
    "ExecutionResult",
    "ToolConfig",
    "SubprocessAdapter",
    "AdapterRegistry",
]
