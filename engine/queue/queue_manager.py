"""
Queue Manager - High-level queue management API.

Provides simplified interface for:
- Job submission
- Queue monitoring
- Worker pool control
- Job cancellation
"""
DOC_ID: DOC-PAT-QUEUE-QUEUE-MANAGER-455

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from engine.queue.job_queue import JobQueue
from engine.queue.job_wrapper import JobWrapper, JobStatus, JobPriority
from engine.queue.worker_pool import WorkerPool
from engine.queue.retry_policy import RetryPolicy, DEFAULT_RETRY_POLICY
from engine.queue.escalation import EscalationManager


class QueueManager:
    """
    High-level queue manager.
    
    Simplifies queue operations:
    - Job submission with priorities
    - Worker pool management
    - Queue monitoring
    - Job lifecycle management
    """
    
    def __init__(
        self,
        db_path: str = "pipeline.db",
        worker_count: int = 3,
        retry_policy: Optional[RetryPolicy] = None,
        escalation_manager: Optional[EscalationManager] = None
    ):
        """
        Initialize queue manager.
        
        Args:
            db_path: Database path
            worker_count: Number of workers
            retry_policy: Retry policy
            escalation_manager: Escalation manager
        """
        self.queue = JobQueue(db_path=db_path)
        self.worker_pool = WorkerPool(
            queue=self.queue,
            worker_count=worker_count
        )
        self.retry_policy = retry_policy or DEFAULT_RETRY_POLICY
        self.escalation_manager = escalation_manager or EscalationManager()
        self.running = False
    
    async def start(self):
        """Start queue manager and workers."""
        if not self.running:
            await self.worker_pool.start()
            self.running = True
    
    async def stop(self, graceful: bool = True):
        """
        Stop queue manager and workers.
        
        Args:
            graceful: Wait for jobs to complete
        """
        if self.running:
            await self.worker_pool.stop(graceful=graceful)
            self.running = False
    
    async def submit_job(
        self,
        job_file: str,
        priority: str = "normal",
        depends_on: Optional[List[str]] = None
    ) -> str:
        """
        Submit job from file.
        
        Args:
            job_file: Path to job JSON file
            priority: Job priority (critical/high/normal/low)
            depends_on: List of job IDs this depends on
            
        Returns:
            Job ID
        """
        # Load job from file
        with open(job_file, 'r') as f:
            job_data = json.load(f)
        
        return await self.submit_job_dict(job_data, priority, depends_on)
    
    async def submit_job_dict(
        self,
        job_data: Dict[str, Any],
        priority: str = "normal",
        depends_on: Optional[List[str]] = None
    ) -> str:
        """
        Submit job from dictionary.
        
        Args:
            job_data: Job specification dict
            priority: Job priority
            depends_on: Job dependencies
            
        Returns:
            Job ID
        """
        job_id = job_data.get("job_id")
        if not job_id:
            raise ValueError("Job must have job_id")
        
        # Create job wrapper
        job_wrapper = JobWrapper(
            job_id=job_id,
            job_data=job_data,
            priority=JobPriority[priority.upper()],
            depends_on=depends_on or [],
            max_retries=self.retry_policy.max_retries
        )
        
        # Submit to queue
        await self.queue.submit(job_wrapper)
        
        return job_id
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a queued job.
        
        Args:
            job_id: Job to cancel
            
        Returns:
            True if cancelled
        """
        return await self.queue.cancel(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dict or None
        """
        # Check active jobs
        if job_id in self.queue.active_jobs:
            job = self.queue.active_jobs[job_id]
            return {
                'job_id': job.job_id,
                'status': job.status.value,
                'priority': job.priority.value,
                'retry_count': job.retry_count,
                'queued_at': job.queued_at.isoformat() if job.queued_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None
            }
        
        # Check waiting jobs
        if job_id in self.queue.waiting_jobs:
            job = self.queue.waiting_jobs[job_id]
            return {
                'job_id': job.job_id,
                'status': 'waiting',
                'depends_on': job.depends_on,
                'queued_at': job.queued_at.isoformat() if job.queued_at else None
            }
        
        # Check completed
        if job_id in self.queue.completed_jobs:
            return {
                'job_id': job_id,
                'status': 'completed'
            }
        
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'queue': self.queue.get_stats(),
            'workers': self.worker_pool.get_status(),
            'retry_policy': self.retry_policy.to_dict()
        }
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List jobs in queue.
        
        Args:
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of job dictionaries
        """
        import sqlite3
        
        conn = sqlite3.connect(self.queue.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT job_id, priority, status, queued_at, started_at, completed_at
                FROM job_queue
                WHERE status = ?
                ORDER BY priority, queued_at
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT job_id, priority, status, queued_at, started_at, completed_at
                FROM job_queue
                ORDER BY priority, queued_at
                LIMIT ?
            """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row[0],
                'priority': row[1],
                'status': row[2],
                'queued_at': row[3],
                'started_at': row[4],
                'completed_at': row[5]
            })
        
        conn.close()
        return jobs
    
    async def wait_all(self):
        """Wait for all jobs to complete."""
        await self.worker_pool.wait_all()
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.run(self.stop())
