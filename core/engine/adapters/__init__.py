"""
Tool Adapters Package
App-specific execution wrappers for Pipeline Plus
"""
from .base import ToolAdapter, ExecutionResult
from .aider_adapter import AiderAdapter
from .codex_adapter import CodexAdapter
from .claude_adapter import ClaudeAdapter

__all__ = [
    'ToolAdapter',
    'ExecutionResult',
    'AiderAdapter',
    'CodexAdapter',
    'ClaudeAdapter',
]
