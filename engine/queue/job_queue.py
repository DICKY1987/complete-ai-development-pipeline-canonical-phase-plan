"""
Job Queue - Priority queue with async support.

Provides priority-based job queuing with:
- Priority ordering
- Dependency tracking  
- State persistence
- Thread-safe operations
"""
# DOC_ID: DOC-PAT-QUEUE-JOB-QUEUE-453

import asyncio
import sqlite3
from typing import Optional, List, Dict, Any, Set
from pathlib import Path
import json
from datetime import datetime

from engine.queue.job_wrapper import JobWrapper, JobStatus, JobPriority


class JobQueue:
    """
    Async priority queue for jobs with dependencies.
    
    Features:
    - Priority-based ordering
    - Dependency resolution
    - SQLite persistence
    - Async get/put operations
    """
    
    def __init__(self, db_path: str = "pipeline.db"):
        """
        Initialize job queue.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_jobs: Dict[str, JobWrapper] = {}
        self.completed_jobs: Set[str] = set()
        self.waiting_jobs: Dict[str, JobWrapper] = {}
        self._init_db()
        self._load_from_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                job_data TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                depends_on TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                queued_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_queue_status_priority
            ON job_queue(status, priority)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_from_db(self):
        """Load queued jobs from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT job_id, job_data, priority, status, depends_on,
                   retry_count, max_retries, queued_at, started_at, 
                   completed_at, metadata
            FROM job_queue
            WHERE status IN ('queued', 'waiting', 'retry')
            ORDER BY priority, queued_at
        """)
        
        for row in cursor.fetchall():
            job_wrapper = JobWrapper(
                job_id=row[0],
                job_data=json.loads(row[1]),
                priority=JobPriority(row[2]),
                status=JobStatus(row[3]),
                depends_on=json.loads(row[4]) if row[4] else [],
                retry_count=row[5],
                max_retries=row[6],
                queued_at=datetime.fromisoformat(row[7]),
                started_at=datetime.fromisoformat(row[8]) if row[8] else None,
                completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
                metadata=json.loads(row[10]) if row[10] else {}
            )
            
            if job_wrapper.is_ready(self.completed_jobs):
                # Non-blocking put
                try:
                    self.queue.put_nowait(job_wrapper)
                except asyncio.QueueFull:
                    pass
            else:
                self.waiting_jobs[job_wrapper.job_id] = job_wrapper
        
        conn.close()
    
    async def submit(self, job_wrapper: JobWrapper):
        """
        Submit job to queue.
        
        Args:
            job_wrapper: Job to queue
        """
        # Save to database
        self._save_to_db(job_wrapper)
        
        # Add to queue or waiting list
        if job_wrapper.is_ready(self.completed_jobs):
            await self.queue.put(job_wrapper)
        else:
            job_wrapper.status = JobStatus.WAITING
            self.waiting_jobs[job_wrapper.job_id] = job_wrapper
            self._update_status_in_db(job_wrapper.job_id, JobStatus.WAITING)
    
    async def get_next(self) -> Optional[JobWrapper]:
        """
        Get next job from queue.
        
        Returns:
            Next job to execute or None if queue empty
        """
        try:
            job = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            self.active_jobs[job.job_id] = job
            job.mark_running()
            self._update_status_in_db(job.job_id, JobStatus.RUNNING)
            return job
        except asyncio.TimeoutError:
            return None
    
    def mark_complete(self, job_id: str):
        """
        Mark job as completed.
        
        Args:
            job_id: ID of completed job
        """
        if job_id in self.active_jobs:
            job = self.active_jobs.pop(job_id)
            job.mark_completed()
            self.completed_jobs.add(job_id)
            self._update_status_in_db(job_id, JobStatus.COMPLETED)
            
            # Check waiting jobs
            self._process_waiting_jobs()
    
    def mark_failed(self, job_id: str):
        """
        Mark job as failed.
        
        Args:
            job_id: ID of failed job
        """
        if job_id in self.active_jobs:
            job = self.active_jobs.pop(job_id)
            job.mark_failed()
            self._update_status_in_db(job_id, JobStatus.FAILED)
    
    async def requeue_for_retry(self, job_id: str):
        """
        Requeue job for retry.
        
        Args:
            job_id: ID of job to retry
        """
        if job_id in self.active_jobs:
            job = self.active_jobs.pop(job_id)
            if job.can_retry():
                job.mark_retry()
                self._update_status_in_db(job_id, JobStatus.RETRY)
                await self.queue.put(job)
            else:
                job.mark_failed()
                self._update_status_in_db(job_id, JobStatus.FAILED)
    
    def _process_waiting_jobs(self):
        """Check if any waiting jobs can now run."""
        ready_jobs = []
        
        for job_id, job in list(self.waiting_jobs.items()):
            if job.is_ready(self.completed_jobs):
                ready_jobs.append(job)
                del self.waiting_jobs[job_id]
        
        for job in ready_jobs:
            job.status = JobStatus.QUEUED
            self._update_status_in_db(job.job_id, JobStatus.QUEUED)
            # Add to queue synchronously (we're not in async context)
            try:
                self.queue.put_nowait(job)
            except asyncio.QueueFull:
                # Queue full, put back in waiting
                self.waiting_jobs[job.job_id] = job
    
    def _save_to_db(self, job: JobWrapper):
        """Save job to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO job_queue
            (job_id, job_data, priority, status, depends_on, retry_count,
             max_retries, queued_at, started_at, completed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.job_id,
            json.dumps(job.job_data),
            job.priority.value,
            job.status.value,
            json.dumps(job.depends_on) if job.depends_on else None,
            job.retry_count,
            job.max_retries,
            job.queued_at.isoformat() if job.queued_at else None,
            job.started_at.isoformat() if job.started_at else None,
            job.completed_at.isoformat() if job.completed_at else None,
            json.dumps(job.metadata) if job.metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def _update_status_in_db(self, job_id: str, status: JobStatus):
        """Update job status in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE job_queue
            SET status = ?, completed_at = ?
            WHERE job_id = ?
        """, (
            status.value,
            datetime.now().isoformat() if status in [JobStatus.COMPLETED, JobStatus.FAILED] else None,
            job_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM job_queue
            GROUP BY status
        """)
        
        stats = dict(cursor.fetchall())
        conn.close()
        
        return {
            'queued': stats.get('queued', 0),
            'waiting': stats.get('waiting', 0),
            'running': len(self.active_jobs),
            'completed': stats.get('completed', 0),
            'failed': stats.get('failed', 0),
            'total': sum(stats.values())
        }
    
    async def cancel(self, job_id: str) -> bool:
        """
        Cancel a queued job.
        
        Args:
            job_id: ID of job to cancel
            
        Returns:
            True if cancelled, False if not found or already running
        """
        # Can only cancel queued or waiting jobs
        if job_id in self.waiting_jobs:
            job = self.waiting_jobs.pop(job_id)
            job.status = JobStatus.CANCELLED
            self._update_status_in_db(job_id, JobStatus.CANCELLED)
            return True
        
        return False
