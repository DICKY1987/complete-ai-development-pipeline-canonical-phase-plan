"""Task Router - WS-03-01B

Routes tasks to appropriate tools based on router_config.json.
Supports multiple routing strategies and capability matching.
"""
# DOC_ID: DOC-CORE-ENGINE-ROUTER-157

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class TaskRouter:
    """Routes tasks to tools based on configuration and capabilities"""
    
    def __init__(self, router_config_path: str):
        """
        Initialize router with configuration.
        
        Args:
            router_config_path: Path to router_config.json
        """
        self.config_path = Path(router_config_path)
        self.config = self._load_config()
        self.apps = self.config.get('apps', {})
        self.routing_rules = self.config.get('routing', {}).get('rules', [])
        self.defaults = self.config.get('defaults', {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse router configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Router config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate required fields
        if 'apps' not in config:
            raise ValueError("Router config missing 'apps' field")
        if 'routing' not in config:
            raise ValueError("Router config missing 'routing' field")
        
        return config
    
    def route_task(self, task_kind: str, 
                   risk_tier: Optional[str] = None,
                   complexity: Optional[str] = None,
                   domain: Optional[str] = None) -> Optional[str]:
        """
        Route a task to the best tool.
        
        Args:
            task_kind: Kind of task (e.g., 'code_edit', 'analysis')
            risk_tier: Risk level ('low', 'medium', 'high')
            complexity: Complexity level ('low', 'medium', 'high')
            domain: Domain hint (e.g., 'software-dev')
        
        Returns:
            tool_id: ID of selected tool, or None if no match
        """
        # Try to match routing rules first
        for rule in self.routing_rules:
            if self._matches_rule(rule, task_kind, risk_tier, complexity):
                candidates = rule.get('select_from', [])
                strategy = rule.get('strategy', 'fixed')
                
                if candidates:
                    return self._apply_strategy(candidates, strategy)
        
        # Fallback: find any tool that can handle this task_kind
        capable_tools = self._find_capable_tools(task_kind, domain)
        
        if capable_tools:
            # Default to first capable tool
            return capable_tools[0]
        
        return None
    
    def _matches_rule(self, rule: Dict[str, Any], 
                     task_kind: str,
                     risk_tier: Optional[str],
                     complexity: Optional[str]) -> bool:
        """Check if task matches routing rule"""
        match = rule.get('match', {})
        
        # Check task_kind
        if 'task_kind' in match:
            if task_kind not in match['task_kind']:
                return False
        
        # Check risk_tier
        if risk_tier and 'risk_tier' in match:
            if risk_tier not in match['risk_tier']:
                return False
        
        # Check complexity
        if complexity and 'complexity' in match:
            if complexity != match['complexity']:
                return False
        
        return True
    
    def _find_capable_tools(self, task_kind: str, 
                           domain: Optional[str] = None) -> List[str]:
        """Find all tools capable of handling task_kind"""
        capable = []
        
        for tool_id, app_config in self.apps.items():
            capabilities = app_config.get('capabilities', {})
            
            # Check if tool supports this task_kind
            supported_tasks = capabilities.get('task_kinds', [])
            if task_kind in supported_tasks:
                # If domain specified, check domain match
                if domain:
                    supported_domains = capabilities.get('domains', [])
                    if domain in supported_domains or not supported_domains:
                        capable.append(tool_id)
                else:
                    capable.append(tool_id)
        
        return capable
    
    def _apply_strategy(self, candidates: List[str], strategy: str) -> Optional[str]:
        """
        Apply routing strategy to select from candidates.
        
        Args:
            candidates: List of candidate tool IDs
            strategy: Routing strategy ('fixed', 'round_robin', 'auto')
        
        Returns:
            Selected tool ID
        """
        if not candidates:
            return None
        
        if strategy == 'fixed':
            # Always return first candidate
            return candidates[0]
        
        elif strategy == 'round_robin':
            # TODO: Implement round-robin state tracking
            # For now, return first
            return candidates[0]
        
        elif strategy == 'auto':
            # TODO: Implement auto-selection based on metrics
            # For now, return first
            return candidates[0]
        
        else:
            # Unknown strategy, default to first
            return candidates[0]
    
    def get_tool_config(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific tool"""
        return self.apps.get(tool_id)
    
    def get_tool_command(self, tool_id: str) -> Optional[str]:
        """Get command for a tool"""
        tool_config = self.get_tool_config(tool_id)
        if tool_config:
            return tool_config.get('command')
        return None
    
    def get_tool_limits(self, tool_id: str) -> Dict[str, Any]:
        """Get limits for a tool (timeout, max_parallel, etc.)"""
        tool_config = self.get_tool_config(tool_id)
        if tool_config:
            limits = tool_config.get('limits', {})
            # Merge with defaults
            return {
                'max_parallel': limits.get('max_parallel', 1),
                'timeout_seconds': limits.get('timeout_seconds', self.defaults.get('timeout_seconds', 600))
            }
        return {
            'max_parallel': 1,
            'timeout_seconds': self.defaults.get('timeout_seconds', 600)
        }
    
    def list_tools(self) -> List[str]:
        """List all available tool IDs"""
        return list(self.apps.keys())
    
    def get_capabilities(self, tool_id: str) -> Dict[str, Any]:
        """Get capabilities for a tool"""
        tool_config = self.get_tool_config(tool_id)
        if tool_config:
            return tool_config.get('capabilities', {})
        return {}


def create_router(router_config_path: str) -> TaskRouter:
    """Factory function to create a router"""
    return TaskRouter(router_config_path)
