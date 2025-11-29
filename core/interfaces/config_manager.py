"""ConfigManager Protocol - Abstraction for configuration management.

This module defines the ConfigManager protocol for unified configuration
access across the pipeline.

Example:
    >>> from core.config.yaml_config_manager import YamlConfigManager
    >>> config = YamlConfigManager('config.yaml')
    >>> timeout = config.get('execution.timeout', 300)
    >>> profile = config.get_tool_profile('aider')
"""

from __future__ import annotations

from typing import Protocol, Any, Optional, runtime_checkable


@runtime_checkable
class ConfigManager(Protocol):
    """Protocol for configuration management.
    
    This abstraction provides:
    - Hierarchical configuration access
    - Tool-specific profiles
    - Schema validation
    - Hot-reload support
    """
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dotted key path.
        
        Args:
            key: Dotted key path (e.g., 'execution.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            >>> config.get('tools.aider.enabled', True)
            True
        """
        ...
    
    def get_tool_profile(self, tool: str) -> dict[str, Any]:
        """Get tool-specific configuration profile.
        
        Args:
            tool: Tool name (e.g., 'aider', 'codex')
            
        Returns:
            Tool configuration dict
            
        Raises:
            KeyError: If tool profile not found
            
        Example:
            >>> profile = config.get_tool_profile('aider')
            >>> print(profile['model'])
            gpt-4
        """
        ...
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value (runtime only, not persisted).
        
        Args:
            key: Dotted key path
            value: Value to set
            
        Example:
            >>> config.set('execution.dry_run', True)
        """
        ...
    
    def validate_all(self) -> list[str]:
        """Validate all configurations against schemas.
        
        Returns:
            List of validation error messages (empty if valid)
            
        Example:
            >>> errors = config.validate_all()
            >>> if errors:
            ...     print("Config errors:", errors)
        """
        ...
    
    def reload(self) -> None:
        """Hot-reload configuration from disk.
        
        Example:
            >>> config.reload()  # Pick up changes without restart
        """
        ...
    
    def get_all(self) -> dict[str, Any]:
        """Get all configuration as dict.
        
        Returns:
            Complete configuration dictionary
        """
        ...


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Configuration validation failed: {len(errors)} errors")


class ToolProfileNotFoundError(ConfigError):
    """Raised when tool profile is not found."""
    
    def __init__(self, tool: str):
        self.tool = tool
        super().__init__(f"Tool profile not found: {tool}")
