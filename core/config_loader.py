"""
Configuration utilities for Invoke integration.

Provides helpers to load and access project configuration
from invoke.yaml with proper structure.
"""
DOC_ID: DOC-CORE-CORE-CONFIG-LOADER-038
DOC_ID: DOC-CORE-CORE-CONFIG-LOADER-015

from typing import Any, Dict, Optional
from pathlib import Path
import yaml


def load_project_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load project configuration from invoke.yaml.
    
    Args:
        config_path: Path to invoke.yaml (default: ./invoke.yaml)
    
    Returns:
        Dictionary containing project configuration
    """
    if config_path is None:
        config_path = "invoke.yaml"
    
    config_file = Path(config_path)
    if not config_file.exists():
        return {}
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_tool_config(tool_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific tool.
    
    Args:
        tool_id: Tool identifier (e.g., 'aider', 'pytest')
        config: Pre-loaded config dict (loads from file if None)
    
    Returns:
        Tool configuration dictionary
    """
    if config is None:
        config = load_project_config()
    
    return config.get('tools', {}).get(tool_id, {})


def get_orchestrator_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get orchestrator configuration.
    
    Args:
        config: Pre-loaded config dict (loads from file if None)
    
    Returns:
        Orchestrator configuration dictionary
    """
    if config is None:
        config = load_project_config()
    
    return config.get('orchestrator', {})


def get_paths_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get paths configuration.
    
    Args:
        config: Pre-loaded config dict (loads from file if None)
    
    Returns:
        Paths configuration dictionary
    """
    if config is None:
        config = load_project_config()
    
    return config.get('paths', {})


def get_error_engine_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get error engine configuration.
    
    Args:
        config: Pre-loaded config dict (loads from file if None)
    
    Returns:
        Error engine configuration dictionary
    """
    if config is None:
        config = load_project_config()
    
    return config.get('error_engine', {})


def get_circuit_breaker_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get circuit breaker configuration.
    
    Args:
        config: Pre-loaded config dict (loads from file if None)
    
    Returns:
        Circuit breaker configuration dictionary
    """
    if config is None:
        config = load_project_config()
    
    return config.get('circuit_breakers', {})
