"""YAML Config Manager - Implementation of ConfigManager protocol."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any
from copy import deepcopy

from core.interfaces.config_manager import (
    ConfigManager,
    ToolProfileNotFoundError,
)


class YamlConfigManager:
    """ConfigManager implementation using YAML files."""
# DOC_ID: DOC-CORE-CONFIG-YAML-CONFIG-MANAGER-077
    
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._overrides: dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}
    
    def _get_nested(self, data: dict, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _set_nested(self, data: dict, key: str, value: Any) -> None:
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        value = self._get_nested(self._overrides, key)
        if value is not None:
            return value
        
        return self._get_nested(self._config, key, default)
    
    def get_tool_profile(self, tool: str) -> dict[str, Any]:
        profile = self.get(f'tools.{tool}')
        
        if profile is None:
            raise ToolProfileNotFoundError(tool)
        
        return deepcopy(profile)
    
    def set(self, key: str, value: Any) -> None:
        self._set_nested(self._overrides, key, value)
    
    def validate_all(self) -> list[str]:
        errors = []
        
        tools = self.get('tools', {})
        if not isinstance(tools, dict):
            errors.append("'tools' must be a dictionary")
        
        timeout = self.get('execution.timeout')
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            errors.append("'execution.timeout' must be positive number")
        
        return errors
    
    def reload(self) -> None:
        self._load_config()
    
    def get_all(self) -> dict[str, Any]:
        result = deepcopy(self._config)
        
        for key, value in self._flatten_dict(self._overrides).items():
            self._set_nested(result, key, value)
        
        return result
    
    def _flatten_dict(self, d: dict, parent_key: str = '') -> dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)
