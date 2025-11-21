"""Tool Adapters - WS-03-02A

Adapters for executing tasks via external tools.
"""

from .base import ToolAdapter, ExecutionResult, ToolConfig
from .subprocess_adapter import SubprocessAdapter
from .registry import AdapterRegistry

__all__ = [
    'ToolAdapter',
    'ExecutionResult', 
    'ToolConfig',
    'SubprocessAdapter',
    'AdapterRegistry',
]
