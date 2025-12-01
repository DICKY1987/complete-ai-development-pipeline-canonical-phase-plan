"""Tool Registry - Discovery and selection of tool adapters."""

from __future__ import annotations

from typing import Optional, Any
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.tool_adapter import ToolAdapter, CapabilityNotSupportedError
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.adapters.base import BaseToolAdapter
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.process_executor import ProcessExecutor, ProcessResult


class ToolRegistry:
    """Registry for discovering and selecting tool adapters."""
# DOC_ID: DOC-CORE-ADAPTERS-REGISTRY-071
    
    def __init__(self):
        self._adapters: dict[str, ToolAdapter] = {}
        self._register_builtin_adapters()
    
    def _register_builtin_adapters(self) -> None:
        self.register(MockAdapter('echo', {'test', 'debug'}))
    
    def register(self, adapter: ToolAdapter) -> None:
        if adapter.name in self._adapters:
            raise ValueError(f"Adapter already registered: {adapter.name}")
        
        self._adapters[adapter.name] = adapter
    
    def get_adapter(
        self,
        required_capabilities: set[str],
        *,
        preferred: Optional[str] = None,
    ) -> ToolAdapter:
        if preferred and preferred in self._adapters:
            adapter = self._adapters[preferred]
            if adapter.supports(required_capabilities):
                return adapter
        
        for adapter in self._adapters.values():
            if adapter.supports(required_capabilities):
                return adapter
        
        raise CapabilityNotSupportedError(
            'registry',
            f"No adapter supports: {required_capabilities}"
        )
    
    def list_adapters(self) -> list[str]:
        return list(self._adapters.keys())
    
    def get_by_name(self, name: str) -> Optional[ToolAdapter]:
        return self._adapters.get(name)


class MockAdapter(BaseToolAdapter):
    """Mock adapter for testing."""
    
    def run(
        self,
        job: dict[str, Any],
        *,
        executor: ProcessExecutor,
    ) -> ProcessResult:
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.process_executor import ProcessResult
        
        action = job.get('action', 'unknown')
        
        return ProcessResult(
            exit_code=0,
            stdout=f"Mock {self.name}: executed {action}",
            stderr="",
            duration_s=0.1,
            command=[self.name, action],
        )
