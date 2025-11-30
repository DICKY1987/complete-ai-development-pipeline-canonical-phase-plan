"""
Worker Pool - Async worker pool for job execution.

Provides concurrent job execution with:
- Configurable worker count
- Graceful shutdown
- Job cancellation
- Resource limits
"""
DOC_ID: DOC-PAT-QUEUE-WORKER-POOL-457

import asyncio
from typing import Optional, Callable, Awaitable
import logging

from engine.queue.job_queue import JobQueue
from engine.queue.job_wrapper import JobWrapper, JobStatus
from engine.orchestrator.orchestrator import Orchestrator
from engine.types import JobResult

logger = logging.getLogger(__name__)


class WorkerPool:
    """
    Async worker pool for executing jobs from queue.
    
    Features:
    - Concurrent job execution
    - Graceful shutdown
    - Error handling and retry
    """
    
    def __init__(
        self,
        queue: JobQueue,
        worker_count: int = 3,
        orchestrator: Optional[Orchestrator] = None
    ):
        """
        Initialize worker pool.
        
        Args:
            queue: Job queue to pull from
            worker_count: Number of concurrent workers
            orchestrator: Orchestrator for job execution
        """
        self.queue = queue
        self.worker_count = worker_count
        self.orchestrator = orchestrator or Orchestrator()
        self.workers = []
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start worker pool."""
        self.running = True
        self.shutdown_event.clear()
        
        logger.info(f"Starting {self.worker_count} workers")
        
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker_loop(i))
            self.workers.append(worker)
        
        logger.info(f"Worker pool started with {self.worker_count} workers")
    
    async def stop(self, graceful: bool = True):
        """
        Stop worker pool.
        
        Args:
            graceful: If True, wait for current jobs to complete
        """
        logger.info("Stopping worker pool...")
        self.running = False
        self.shutdown_event.set()
        
        if graceful:
            # Wait for workers to finish current jobs
            await asyncio.gather(*self.workers, return_exceptions=True)
        else:
            # Cancel all workers immediately
            for worker in self.workers:
                worker.cancel()
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        logger.info("Worker pool stopped")
    
    async def _worker_loop(self, worker_id: int):
        """
        Worker loop - continuously pulls and executes jobs.
        
        Args:
            worker_id: Worker identifier
        """
        logger.info(f"Worker {worker_id} started")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get next job from queue
                job = await self.queue.get_next()
                
                if job is None:
                    # No job available, continue
                    continue
                
                logger.info(f"Worker {worker_id} executing job {job.job_id}")
                
                # Execute job
                try:
                    result = await self._execute_job(job)
                    
                    if result.success:
                        self.queue.mark_complete(job.job_id)
                        logger.info(f"Worker {worker_id} completed job {job.job_id}")
                    else:
                        logger.warning(f"Worker {worker_id} job {job.job_id} failed (exit={result.exit_code})")
                        await self.queue.requeue_for_retry(job.job_id)
                
                except Exception as e:
                    logger.error(f"Worker {worker_id} error executing job {job.job_id}: {e}")
                    await self.queue.requeue_for_retry(job.job_id)
            
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} unexpected error: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on errors
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _execute_job(self, job: JobWrapper) -> JobResult:
        """
        Execute a job using orchestrator.
        
        Args:
            job: Job to execute
            
        Returns:
            Job execution result
        """
        # Run job in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.orchestrator.run_job_dict,
            job.job_data
        )
        return result
    
    async def wait_all(self):
        """Wait for all workers to complete."""
        await asyncio.gather(*self.workers, return_exceptions=True)
    
    def get_status(self) -> dict:
        """Get worker pool status."""
        return {
            'running': self.running,
            'worker_count': self.worker_count,
            'active_workers': len([w for w in self.workers if not w.done()]),
            'queue_stats': self.queue.get_stats()
        }
