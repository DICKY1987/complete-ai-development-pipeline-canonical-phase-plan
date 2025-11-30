"""ToolAdapter Protocol - Abstraction for tool adapters.

This module defines the ToolAdapter protocol for unified tool execution
across different tools (Aider, Codex, Tests, Git, etc.).

Example:
    >>> from core.adapters.registry import ToolRegistry
    >>> registry = ToolRegistry()
    >>> adapter = registry.get_adapter({'edit_code'})
    >>> result = adapter.run(job, executor=executor)
"""
DOC_ID: DOC-CORE-INTERFACES-TOOL-ADAPTER-103

from __future__ import annotations

from typing import Protocol, Any, runtime_checkable
from core.interfaces.process_executor import ProcessExecutor, ProcessResult


@runtime_checkable
class ToolAdapter(Protocol):
    """Protocol for tool adapters.
    
    This abstraction provides a unified interface for all tools,
    enabling easy tool addition and consistent execution patterns.
    
    Features:
    - Capability-based tool selection
    - Job preparation and normalization
    - ProcessExecutor integration
    - Result normalization
    """
    
    @property
    def name(self) -> str:
        """Adapter name (e.g., 'aider', 'codex', 'tests')."""
        ...
    
    @property
    def capabilities(self) -> set[str]:
        """Capabilities this adapter supports.
        
        Examples: {'edit_code', 'refactor', 'test', 'commit'}
        """
        ...
    
    def supports(self, required_capabilities: set[str]) -> bool:
        """Check if adapter supports all required capabilities.
        
        Args:
            required_capabilities: Set of required capability strings
            
        Returns:
            True if all capabilities are supported
            
        Example:
            >>> adapter.supports({'edit_code'})
            True
            >>> adapter.supports({'edit_code', 'deploy'})
            False
        """
        ...
    
    def prepare_job(self, job_spec: dict[str, Any]) -> dict[str, Any]:
        """Prepare job specification for execution.
        
        Args:
            job_spec: Raw job specification
            
        Returns:
            Prepared job dict with tool-specific parameters
            
        Raises:
            ValueError: If job spec is invalid
            
        Example:
            >>> job = adapter.prepare_job({
            ...     'action': 'edit_code',
            ...     'files': ['main.py'],
            ...     'instruction': 'Add logging'
            ... })
        """
        ...
    
    def run(
        self,
        job: dict[str, Any],
        *,
        executor: ProcessExecutor,
    ) -> ProcessResult:
        """Execute job using process executor.
        
        Args:
            job: Prepared job specification
            executor: ProcessExecutor for running commands
            
        Returns:
            ProcessResult from execution
            
        Example:
            >>> from core.execution.subprocess_executor import SubprocessExecutor
            >>> result = adapter.run(job, executor=SubprocessExecutor())
            >>> if result.success:
            ...     print("Job completed successfully")
        """
        ...
    
    def normalize_result(self, result: ProcessResult) -> dict[str, Any]:
        """Normalize process result to standard format.
        
        Args:
            result: ProcessResult from execution
            
        Returns:
            Normalized result dict with standard fields
            
        Example:
            >>> normalized = adapter.normalize_result(result)
            >>> print(normalized['status'])  # 'success' or 'failed'
            >>> print(normalized['files_changed'])
        """
        ...


class ToolAdapterError(Exception):
    """Base exception for tool adapter errors."""
    pass


class CapabilityNotSupportedError(ToolAdapterError):
    """Raised when required capability is not supported."""
    
    def __init__(self, adapter: str, capability: str):
        self.adapter = adapter
        self.capability = capability
        super().__init__(f"{adapter} does not support capability: {capability}")


class JobPreparationError(ToolAdapterError):
    """Raised when job preparation fails."""
    
    def __init__(self, adapter: str, reason: str):
        self.adapter = adapter
        self.reason = reason
        super().__init__(f"{adapter} job preparation failed: {reason}")
