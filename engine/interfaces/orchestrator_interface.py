"""
Orchestrator Interface Protocol

Defines the contract for the job orchestrator.
This is the main entry point for job execution.
"""

from typing import Protocol, Dict, Any
from engine.types import JobResult


class OrchestratorInterface(Protocol):
    """Protocol for the job orchestrator.
    
    The orchestrator is responsible for:
    - Job lifecycle management (queued → running → completed/failed)
    - Dispatching jobs to appropriate adapters
    - Updating state store with results
    - Coordinating retries and escalations
    """
    
    def run_job(self, job_file: str) -> JobResult:
        """
        Execute a job from a job file.
        
        Args:
            job_file: Path to JSON file conforming to job.schema.json
            
        Returns:
            JobResult with execution outcome
        """
        ...
    
    def queue_job(self, job: Dict[str, Any]) -> str:
        """
        Queue a job for execution.
        
        Args:
            job: Job dictionary
            
        Returns:
            job_id for the queued job
        """
        ...
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Status string (queued, running, completed, failed, quarantined)
        """
        ...
