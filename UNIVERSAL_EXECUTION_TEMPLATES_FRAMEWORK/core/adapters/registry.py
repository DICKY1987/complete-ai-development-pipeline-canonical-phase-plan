"""Adapter Registry - WS-03-02A

Manages tool adapters and loads them from router_config.
"""
DOC_ID: DOC-CORE-ADAPTERS-REGISTRY-134

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base import ToolAdapter, ToolConfig
from .subprocess_adapter import SubprocessAdapter


class AdapterRegistry:
    """Registry for tool adapters
    
    Loads adapters from router_config and provides lookup by tool_id.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.adapters: Dict[str, ToolAdapter] = {}
        self.config_path = config_path
        
        if config_path:
            self.load_from_config(config_path)
    
    def load_from_config(self, config_path: str):
        """Load adapters from router_config.json
        
        Args:
            config_path: Path to router_config.v1.json
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load apps as tool configs
        apps = config.get('apps', {})
        for tool_id, app_config in apps.items():
            tool_config = ToolConfig(
                tool_id=tool_id,
                kind=app_config.get('kind', 'tool'),
                command=app_config.get('command', ''),
                capabilities=app_config.get('capabilities', {}),
                limits=app_config.get('limits'),
                safety_tier=app_config.get('safety_tier', 'medium')
            )
            
            # Create appropriate adapter based on kind
            # For now, all use SubprocessAdapter
            adapter = SubprocessAdapter(tool_config)
            self.register(tool_id, adapter)
    
    def register(self, tool_id: str, adapter: ToolAdapter):
        """Register an adapter
        
        Args:
            tool_id: Unique tool identifier
            adapter: ToolAdapter instance
        """
        self.adapters[tool_id] = adapter
    
    def get(self, tool_id: str) -> Optional[ToolAdapter]:
        """Get adapter by tool_id
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            ToolAdapter or None if not found
        """
        return self.adapters.get(tool_id)
    
    def find_for_task(
        self, 
        task_kind: str, 
        domain: Optional[str] = None
    ) -> List[ToolAdapter]:
        """Find all adapters that support a task kind/domain
        
        Args:
            task_kind: Task kind (e.g., 'code_edit')
            domain: Optional domain filter
            
        Returns:
            List of capable adapters
        """
        capable = []
        for adapter in self.adapters.values():
            if adapter.supports_task(task_kind, domain):
                capable.append(adapter)
        return capable
    
    def list_tools(self) -> List[str]:
        """List all registered tool IDs"""
        return list(self.adapters.keys())
    
    def get_config(self, tool_id: str) -> Optional[ToolConfig]:
        """Get tool config by ID
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            ToolConfig or None
        """
        adapter = self.get(tool_id)
        return adapter.config if adapter else None
