"""Tool Adapters Package

Tool-specific execution wrappers providing unified interface to AI coding tools.

This package implements the adapter pattern to integrate external tools
(Aider, Claude CLI, Codex, etc.) with a consistent interface.

Public API:
    Base Interface:
        - BaseAdapter - Abstract base class for all adapters
        - ToolAdapter - Alias for BaseAdapter (legacy)
        - ExecutionResult - Standard result format
    
    Adapters:
        - AiderAdapter - Aider AI coding assistant
        - ClaudeAdapter - Claude CLI integration
        - CodexAdapter - OpenAI Codex integration
    
    Registry:
        - get_adapter() - Get adapter instance by tool ID
        - list_adapters() - List available adapters
        - ADAPTERS - Registry dictionary

Usage:
    from core.engine.adapters import get_adapter, list_adapters
    
    # List available tools
    tools = list_adapters()
    # Returns: ["aider", "claude", "codex"]
    
    # Get adapter instance
    adapter = get_adapter("aider", timeout_sec=300)
    
    # Execute tool
    result = adapter.execute(
        prompt="Add error handling",
        files=["src/auth.py"],
        context={"worktree_path": "."}
    )

For details, see:
    - core/engine/adapters/README.md
    - core/engine/adapters/base.py

Adapter Interface:
    All adapters must implement:
    - execute(prompt, files, context) -> dict
    - validate_config() -> bool
    - get_capabilities() -> dict (optional)
"""
DOC_ID: DOC-PAT-ADAPTERS-INIT-437

from core.engine.adapters.base import BaseAdapter, ToolAdapter, ExecutionResult
from core.engine.adapters.aider_adapter import AiderAdapter
from core.engine.adapters.codex_adapter import CodexAdapter
from core.engine.adapters.claude_adapter import ClaudeAdapter

# Adapter registry
ADAPTERS = {
    "aider": AiderAdapter,
    "claude": ClaudeAdapter,
    "codex": CodexAdapter,
}

def get_adapter(tool_id: str, **kwargs) -> BaseAdapter:
    """
    Get adapter instance by tool ID.
    
    Args:
        tool_id: Tool identifier (e.g., "aider", "claude")
        **kwargs: Adapter-specific configuration
    
    Returns:
        Configured adapter instance
    
    Raises:
        ValueError: If tool_id not found
    
    Example:
        adapter = get_adapter("aider", timeout_sec=300)
        result = adapter.execute(...)
    """
    if tool_id not in ADAPTERS:
        available = ", ".join(ADAPTERS.keys())
        raise ValueError(
            f"Unknown tool: {tool_id}. Available: {available}"
        )
    
    adapter_class = ADAPTERS[tool_id]
    return adapter_class(**kwargs)

def list_adapters() -> list[str]:
    """
    List all registered adapters.
    
    Returns:
        List of tool IDs
    
    Example:
        tools = list_adapters()
        # Returns: ["aider", "claude", "codex"]
    """
    return list(ADAPTERS.keys())

__all__ = [
    # Base interface
    "BaseAdapter",
    "ToolAdapter",  # Legacy alias
    "ExecutionResult",
    
    # Adapters
    "AiderAdapter",
    "CodexAdapter",
    "ClaudeAdapter",
    
    # Registry
    "ADAPTERS",
    "get_adapter",
    "list_adapters",
]
