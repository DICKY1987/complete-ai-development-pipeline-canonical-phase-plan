"""
Adapter Interface Protocol

Defines the contract for tool adapters.
Each tool (Aider, Codex, tests, git) implements this interface.
"""
# DOC_ID: DOC-PAT-INTERFACES-ADAPTER-INTERFACE-445

from typing import Protocol, Dict, Any
from engine.types import JobResult


class AdapterInterface(Protocol):
    """Protocol for tool adapters.
    
    Each adapter wraps a specific CLI tool and knows how to:
    - Build the correct command line from a job
    - Execute the tool in a pseudo-terminal
    - Capture logs and results
    - Return standardized JobResult
    """
    
    def run_job(self, job: Dict[str, Any]) -> JobResult:
        """
        Execute a job using this adapter's tool.
        
        Args:
            job: Job dictionary conforming to job.schema.json
            
        Returns:
            JobResult with exit code, logs, and error report path
        """
        ...
    
    def validate_job(self, job: Dict[str, Any]) -> bool:
        """
        Validate that a job has required fields for this adapter.
        
        Args:
            job: Job dictionary to validate
            
        Returns:
            True if job is valid for this adapter
        """
        ...
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get adapter metadata (tool name, version, capabilities).
        
        Returns:
            Dictionary with tool information
        """
        ...
