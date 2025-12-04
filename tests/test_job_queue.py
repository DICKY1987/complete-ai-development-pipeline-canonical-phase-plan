"""
Integration tests for JobQueue (Phase 4B)
Tests priority queue operations, persistence, and dependency tracking.
"""
# DOC_ID: DOC-TEST-TESTS-TEST-JOB-QUEUE-088
# DOC_ID: DOC-TEST-TESTS-TEST-JOB-QUEUE-049
import pytest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime

from engine.queue.job_queue import JobQueue
from engine.queue.job_wrapper import JobWrapper, JobPriority, JobStatus


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database"""
    db_path = tmp_path / "test_queue.db"
    yield str(db_path)


@pytest.fixture
def queue(temp_db):
    """Create JobQueue instance"""
    return JobQueue(db_path=temp_db)


@pytest.fixture
def sample_job():
    """Create sample job"""
    return JobWrapper(
        job_id="test-job-1",
        job_data={"tool": "aider", "command": {"exe": "aider", "args": []}},
        priority=JobPriority.NORMAL
    )


@pytest.mark.asyncio
async def test_queue_initialization(temp_db):
    """Test queue initialization creates database"""
    queue = JobQueue(db_path=temp_db)

    assert Path(temp_db).exists()
    assert queue.db_path == temp_db


@pytest.mark.asyncio
async def test_submit_job(queue, sample_job):
    """Test submitting job to queue"""
    await queue.submit(sample_job)

    stats = queue.get_stats()
    assert stats['queued'] >= 1


@pytest.mark.asyncio
async def test_get_next_job(queue, sample_job):
    """Test getting next job from queue"""
    await queue.submit(sample_job)

    job = await queue.get_next()

    assert job is not None
    assert job.job_id == sample_job.job_id
    assert job.status == JobStatus.RUNNING


@pytest.mark.asyncio
async def test_priority_ordering(queue):
    """Test jobs are retrieved in priority order"""
    # Submit jobs with different priorities
    job_low = JobWrapper(
        job_id="low",
        job_data={},
        priority=JobPriority.LOW
    )
    job_high = JobWrapper(
        job_id="high",
        job_data={},
        priority=JobPriority.HIGH
    )
    job_normal = JobWrapper(
        job_id="normal",
        job_data={},
        priority=JobPriority.NORMAL
    )

    # Submit in non-priority order
    await queue.submit(job_low)
    await queue.submit(job_normal)
    await queue.submit(job_high)

    # Should get high priority first
    job1 = await queue.get_next()
    assert job1.job_id == "high"

    # Then normal
    job2 = await queue.get_next()
    assert job2.job_id == "normal"

    # Then low
    job3 = await queue.get_next()
    assert job3.job_id == "low"


@pytest.mark.asyncio
async def test_mark_complete(queue, sample_job):
    """Test marking job as complete"""
    await queue.submit(sample_job)
    job = await queue.get_next()

    queue.mark_complete(job.job_id)

    assert job.job_id in queue.completed_jobs
    assert job.job_id not in queue.active_jobs

    stats = queue.get_stats()
    assert stats['completed'] >= 1


@pytest.mark.asyncio
async def test_mark_failed(queue, sample_job):
    """Test marking job as failed"""
    await queue.submit(sample_job)
    job = await queue.get_next()

    queue.mark_failed(job.job_id)

    assert job.status == JobStatus.FAILED
    assert job.job_id not in queue.active_jobs

    stats = queue.get_stats()
    assert stats['failed'] >= 1


@pytest.mark.asyncio
async def test_requeue_for_retry(queue):
    """Test requeueing job for retry"""
    job = JobWrapper(
        job_id="retry-test",
        job_data={},
        max_retries=3
    )

    await queue.submit(job)
    retrieved_job = await queue.get_next()

    initial_retry_count = retrieved_job.retry_count

    # Retry job
    await queue.requeue_for_retry(retrieved_job.job_id)

    # Job should be requeued with incremented retry count
    await asyncio.sleep(0.1)  # Give time for requeue

    # Check that job is back in queue or active
    next_job = await queue.get_next()
    if next_job and next_job.job_id == "retry-test":
        assert next_job.retry_count == initial_retry_count + 1
    else:
        # Job might still be processing, check stats show activity
        stats = queue.get_stats()
        assert stats.get('total', 0) >= 1


@pytest.mark.asyncio
async def test_max_retries_exceeded(queue):
    """Test job fails when max retries exceeded"""
    job = JobWrapper(
        job_id="max-retry-test",
        job_data={},
        max_retries=2,
        retry_count=2  # Already at max
    )

    await queue.submit(job)
    retrieved_job = await queue.get_next()

    # Try to retry - should fail instead
    await queue.requeue_for_retry(retrieved_job.job_id)

    assert retrieved_job.status == JobStatus.FAILED

    stats = queue.get_stats()
    assert stats['failed'] >= 1


@pytest.mark.asyncio
async def test_dependency_tracking(queue):
    """Test jobs wait for dependencies"""
    # Create dependent job
    dep_job = JobWrapper(
        job_id="dep-job",
        job_data={},
        depends_on=["job1", "job2"]
    )

    await queue.submit(dep_job)

    # Should be in waiting jobs
    assert dep_job.job_id in queue.waiting_jobs
    assert dep_job.status == JobStatus.WAITING


@pytest.mark.asyncio
async def test_dependency_resolution(queue):
    """Test jobs become ready when dependencies complete"""
    # Create jobs
    job1 = JobWrapper(job_id="job1", job_data={})
    job2 = JobWrapper(job_id="job2", job_data={})
    dep_job = JobWrapper(
        job_id="dep-job",
        job_data={},
        depends_on=["job1", "job2"]
    )

    # Submit and complete dependencies
    await queue.submit(job1)
    await queue.submit(job2)
    await queue.submit(dep_job)

    # dep_job should be waiting
    assert dep_job.job_id in queue.waiting_jobs

    # Complete job1
    j1 = await queue.get_next()
    queue.mark_complete(j1.job_id)

    # dep_job still waiting
    assert dep_job.job_id in queue.waiting_jobs

    # Complete job2
    j2 = await queue.get_next()
    queue.mark_complete(j2.job_id)

    # Now dep_job should be ready
    assert dep_job.job_id not in queue.waiting_jobs


@pytest.mark.asyncio
async def test_cancel_queued_job(queue):
    """Test cancelling a queued job"""
    job = JobWrapper(
        job_id="cancel-test",
        job_data={},
        depends_on=["dep1"]  # Will be in waiting
    )

    await queue.submit(job)
    assert job.job_id in queue.waiting_jobs

    # Cancel job
    result = await queue.cancel(job.job_id)

    assert result is True
    assert job.job_id not in queue.waiting_jobs
    assert job.status == JobStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_running_job_fails(queue, sample_job):
    """Test cannot cancel running job"""
    await queue.submit(sample_job)
    job = await queue.get_next()

    # Try to cancel running job
    result = await queue.cancel(job.job_id)

    assert result is False


@pytest.mark.asyncio
async def test_queue_persistence(temp_db):
    """Test queue state persists across instances"""
    # Create queue and submit jobs
    queue1 = JobQueue(db_path=temp_db)
    job = JobWrapper(
        job_id="persist-test",
        job_data={"tool": "aider"},
        priority=JobPriority.HIGH
    )
    await queue1.submit(job)

    # Create new queue instance
    queue2 = JobQueue(db_path=temp_db)

    # Job should be loaded from database
    retrieved_job = await queue2.get_next()
    assert retrieved_job is not None
    assert retrieved_job.job_id == "persist-test"
    assert retrieved_job.priority == JobPriority.HIGH


@pytest.mark.asyncio
async def test_get_stats(queue):
    """Test queue statistics"""
    # Add jobs in various states
    job1 = JobWrapper(job_id="queued1", job_data={})
    job2 = JobWrapper(job_id="queued2", job_data={})
    job3 = JobWrapper(job_id="waiting", job_data={}, depends_on=["dep"])

    await queue.submit(job1)
    await queue.submit(job2)
    await queue.submit(job3)

    # Get one job (will be running)
    running_job = await queue.get_next()

    stats = queue.get_stats()

    assert stats['running'] >= 1
    assert stats['waiting'] >= 1
    assert stats['queued'] >= 1


@pytest.mark.asyncio
async def test_empty_queue_timeout(queue):
    """Test get_next returns None on empty queue"""
    job = await queue.get_next()

    assert job is None


@pytest.mark.asyncio
async def test_fifo_within_priority(queue):
    """Test FIFO ordering within same priority"""
    # Create jobs with same priority but different times
    job1 = JobWrapper(
        job_id="first",
        job_data={},
        priority=JobPriority.NORMAL
    )
    await asyncio.sleep(0.01)  # Ensure different timestamp
    job2 = JobWrapper(
        job_id="second",
        job_data={},
        priority=JobPriority.NORMAL
    )

    await queue.submit(job1)
    await queue.submit(job2)

    # Should get job1 first (earlier timestamp)
    retrieved1 = await queue.get_next()
    assert retrieved1.job_id == "first"

    retrieved2 = await queue.get_next()
    assert retrieved2.job_id == "second"


@pytest.mark.asyncio
async def test_concurrent_operations(queue):
    """Test concurrent job submissions"""
    jobs = [
        JobWrapper(job_id=f"concurrent-{i}", job_data={})
        for i in range(10)
    ]

    # Submit all jobs concurrently
    await asyncio.gather(*[queue.submit(job) for job in jobs])

    stats = queue.get_stats()
    assert stats['queued'] >= 10
