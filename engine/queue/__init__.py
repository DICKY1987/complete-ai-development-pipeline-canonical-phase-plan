"""
Queue package for job management.

Provides:
- Job queueing and persistence
- Worker pool management
- Retry policies
- Escalation handling
"""
DOC_ID: DOC-PAT-QUEUE-INIT-458

from engine.queue.job_queue import JobQueue
from engine.queue.job_wrapper import JobWrapper, JobStatus, JobPriority
from engine.queue.queue_manager import QueueManager
from engine.queue.retry_policy import (
    RetryPolicy,
    BackoffStrategy,
    DEFAULT_RETRY_POLICY,
    FAST_RETRY_POLICY,
    SLOW_RETRY_POLICY,
    NO_RETRY_POLICY,
)
from engine.queue.worker_pool import WorkerPool
from engine.queue.escalation import EscalationManager

__all__ = [
    "JobQueue",
    "JobWrapper",
    "JobStatus",
    "JobPriority",
    "QueueManager",
    "RetryPolicy",
    "BackoffStrategy",
    "DEFAULT_RETRY_POLICY",
    "FAST_RETRY_POLICY",
    "SLOW_RETRY_POLICY",
    "NO_RETRY_POLICY",
    "WorkerPool",
    "EscalationManager",
]
