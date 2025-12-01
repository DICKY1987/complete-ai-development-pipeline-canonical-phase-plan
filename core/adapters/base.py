"""Base Tool Adapter - Common functionality for all adapters."""

from __future__ import annotations

from typing import Any
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.tool_adapter import ToolAdapter, JobPreparationError
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.process_executor import ProcessExecutor, ProcessResult


class BaseToolAdapter:
    """Base implementation for ToolAdapter protocol."""
# DOC_ID: DOC-CORE-ADAPTERS-BASE-070
    
    def __init__(self, name: str, capabilities: set[str]):
        self._name = name
        self._capabilities = capabilities
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def capabilities(self) -> set[str]:
        return self._capabilities
    
    def supports(self, required_capabilities: set[str]) -> bool:
        return required_capabilities.issubset(self._capabilities)
    
    def prepare_job(self, job_spec: dict[str, Any]) -> dict[str, Any]:
        required_fields = {'action'}
        missing = required_fields - set(job_spec.keys())
        
        if missing:
            raise JobPreparationError(
                self.name,
                f"Missing required fields: {missing}"
            )
        
        return job_spec.copy()
    
    def run(
        self,
        job: dict[str, Any],
        *,
        executor: ProcessExecutor,
    ) -> ProcessResult:
        """Default run implementation - should be overridden."""
        raise NotImplementedError(f"{self.name} must implement run()")
    
    def normalize_result(self, result: ProcessResult) -> dict[str, Any]:
        return {
            'status': 'success' if result.success else 'failed',
            'exit_code': result.exit_code,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration_s': result.duration_s,
            'timed_out': result.timed_out,
            'tool': self.name,
        }
