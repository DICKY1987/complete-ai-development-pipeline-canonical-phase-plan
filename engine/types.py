"""
Shared type definitions for the engine package.

These types are used across orchestrator, adapters, and state store
to ensure consistent contracts.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class JobResult:
    """Result from executing a job via an adapter."""
    
    exit_code: int
    error_report_path: str
    duration_s: float
    stdout: str = ""
    stderr: str = ""
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Automatically set success based on exit code if not explicitly set."""
        if self.exit_code == 0 and not self.success:
            self.success = True


@dataclass
class Job:
    """Job definition for tool execution."""
    
    job_id: str
    workstream_id: str
    tool: str
    command: Dict[str, Any]
    env: Dict[str, str]
    paths: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "workstream_id": self.workstream_id,
            "tool": self.tool,
            "command": self.command,
            "env": self.env,
            "paths": self.paths,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create Job from dictionary."""
        return cls(
            job_id=data["job_id"],
            workstream_id=data["workstream_id"],
            tool=data["tool"],
            command=data["command"],
            env=data["env"],
            paths=data["paths"],
            metadata=data.get("metadata", {})
        )


@dataclass
class JobStatus:
    """Status information for a job."""
    
    job_id: str
    status: str  # queued, running, completed, failed, quarantined
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
