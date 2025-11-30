"""
Job Wrapper - Wraps job data with metadata and state.

Provides structured representation of queued jobs with:
- Priority levels
- Status tracking
- Dependency management
- Retry counting
- Metadata storage
"""
DOC_ID: DOC-PAT-QUEUE-JOB-WRAPPER-454

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import json


class JobPriority(Enum):
    """Job priority levels (lower number = higher priority)."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class JobStatus(Enum):
    """Job execution status."""
    QUEUED = "queued"
    WAITING = "waiting"  # Waiting for dependencies
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


@dataclass
class JobWrapper:
    """
    Wrapper for job data with queue metadata.
    
    Attributes:
        job_id: Unique job identifier
        job_data: Job specification dict
        priority: Job priority level
        status: Current job status
        depends_on: List of job_ids this job depends on
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts allowed
        queued_at: When job was queued
        started_at: When job execution started
        completed_at: When job completed
        metadata: Additional metadata
    """
    
    job_id: str
    job_data: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.QUEUED
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set queued_at if not provided."""
        if self.queued_at is None:
            self.queued_at = datetime.now()
    
    def __lt__(self, other: 'JobWrapper') -> bool:
        """
        Compare jobs for priority queue ordering.
        
        Lower priority value = higher priority
        If same priority, earlier queued_at = higher priority
        """
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.queued_at < other.queued_at
    
    def mark_running(self):
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_failed(self):
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
    
    def mark_retry(self):
        """Mark job for retry."""
        self.status = JobStatus.RETRY
        self.retry_count += 1
    
    def mark_escalated(self, to_tool: str):
        """Mark job as escalated."""
        self.status = JobStatus.ESCALATED
        self.metadata['escalated_to'] = to_tool
        self.metadata['escalated_at'] = datetime.now().isoformat()
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.retry_count < self.max_retries
    
    def is_ready(self, completed_jobs: set) -> bool:
        """
        Check if job is ready to run.
        
        Job is ready if all dependencies are completed.
        """
        if not self.depends_on:
            return True
        return all(dep in completed_jobs for dep in self.depends_on)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'job_id': self.job_id,
            'job_data': self.job_data,
            'priority': self.priority.value,
            'status': self.status.value,
            'depends_on': self.depends_on,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'queued_at': self.queued_at.isoformat() if self.queued_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobWrapper':
        """Create JobWrapper from dictionary."""
        return cls(
            job_id=data['job_id'],
            job_data=data['job_data'],
            priority=JobPriority(data['priority']),
            status=JobStatus(data['status']),
            depends_on=data.get('depends_on', []),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            queued_at=datetime.fromisoformat(data['queued_at']) if data.get('queued_at') else None,
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            metadata=data.get('metadata', {})
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'JobWrapper':
        """Create JobWrapper from JSON string."""
        return cls.from_dict(json.loads(json_str))
