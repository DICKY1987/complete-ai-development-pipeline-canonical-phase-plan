"""
State Interface Protocol

Defines the contract for state storage implementations.
All sections interact with persistent state through this interface.
"""

from typing import Protocol, Dict, Any, List, Optional
from engine.types import JobResult


class StateInterface(Protocol):
    """Protocol for job and workstream state persistence."""
    
    def create_run(self, ws_id: str, **kwargs) -> str:
        """Create a new run and return run_id."""
        ...
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run details by ID."""
        ...
    
    def update_run_status(self, run_id: str, status: str) -> None:
        """Update run status."""
        ...
    
    def mark_job_running(self, job_id: str) -> None:
        """Mark a job as running (status transition)."""
        ...
    
    def update_job_result(self, job: Dict[str, Any], result: JobResult) -> None:
        """Update job with execution result."""
        ...
    
    def list_jobs(self, run_id: str) -> List[Dict[str, Any]]:
        """List all jobs for a given run."""
        ...
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get job details by ID."""
        ...
    
    def record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an event to the event log."""
        ...
    
    def list_workstreams(self, run_id: str) -> List[Dict[str, Any]]:
        """List all workstreams for a given run."""
        ...
    
    def get_workstream(self, ws_id: str) -> Optional[Dict[str, Any]]:
        """Get workstream details by ID."""
        ...
