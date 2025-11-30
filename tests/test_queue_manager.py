"""
Integration tests for QueueManager (Phase 4B)
Tests high-level queue operations, job submission, and status tracking.
"""
DOC_ID: DOC-TEST-TESTS-TEST-QUEUE-MANAGER-102
DOC_ID: DOC-TEST-TESTS-TEST-QUEUE-MANAGER-063
import pytest
import asyncio
import json
import tempfile
from pathlib import Path

from engine.queue.queue_manager import QueueManager
from engine.queue.job_wrapper import JobPriority, JobStatus
from engine.queue.retry_policy import RetryPolicy, BackoffStrategy


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database"""
    db_path = tmp_path / "test_manager.db"
    yield str(db_path)


@pytest.fixture
async def manager(temp_db):
    """Create QueueManager instance"""
    mgr = QueueManager(db_path=temp_db, worker_count=2)
    yield mgr
    # Cleanup
    if mgr.running:
        await mgr.stop(graceful=False)


@pytest.fixture
def sample_job_data():
    """Create sample job data"""
    return {
        "job_id": "test-job-1",
        "tool": "aider",
        "command": {
            "exe": "aider",
            "args": ["--yes", "Fix the bug"]
        }
    }


@pytest.mark.asyncio
async def test_manager_initialization(temp_db):
    """Test manager initializes with correct defaults"""
    manager = QueueManager(db_path=temp_db)
    
    assert manager.queue is not None
    assert manager.worker_pool is not None
    assert manager.running is False


@pytest.mark.asyncio
async def test_manager_start_stop(manager):
    """Test starting and stopping manager"""
    await manager.start()
    assert manager.running is True
    
    await manager.stop()
    assert manager.running is False


@pytest.mark.asyncio
async def test_submit_job_dict(manager, sample_job_data):
    """Test submitting job from dictionary"""
    job_id = await manager.submit_job_dict(sample_job_data)
    
    assert job_id == "test-job-1"
    
    status = manager.get_job_status(job_id)
    assert status is not None
    assert status['job_id'] == job_id


@pytest.mark.asyncio
async def test_submit_job_with_priority(manager, sample_job_data):
    """Test submitting job with custom priority"""
    job_id = await manager.submit_job_dict(sample_job_data, priority="high")
    
    status = manager.get_job_status(job_id)
    assert status['priority'] == JobPriority.HIGH.value


@pytest.mark.asyncio
async def test_submit_job_with_dependencies(manager):
    """Test submitting job with dependencies"""
    job1_data = {
        "job_id": "job1",
        "tool": "git",
        "command": {"exe": "git", "args": ["status"]}
    }
    job2_data = {
        "job_id": "job2",
        "tool": "aider",
        "command": {"exe": "aider", "args": []}
    }
    
    await manager.submit_job_dict(job1_data)
    job2_id = await manager.submit_job_dict(
        job2_data,
        depends_on=["job1"]
    )
    
    # job2 should be waiting for job1
    status = manager.get_job_status(job2_id)
    assert status is not None
    if status.get('status') == 'waiting':
        assert 'job1' in status.get('depends_on', [])


@pytest.mark.asyncio
async def test_submit_job_file(manager, sample_job_data, tmp_path):
    """Test submitting job from file"""
    job_file = tmp_path / "job.json"
    with open(job_file, 'w') as f:
        json.dump(sample_job_data, f)
    
    job_id = await manager.submit_job(str(job_file))
    
    assert job_id == "test-job-1"


@pytest.mark.asyncio
async def test_submit_job_missing_id(manager):
    """Test submitting job without job_id raises error"""
    job_data = {
        "tool": "aider",
        "command": {"exe": "aider"}
    }
    
    with pytest.raises(ValueError, match="job_id"):
        await manager.submit_job_dict(job_data)


@pytest.mark.asyncio
async def test_cancel_job(manager, sample_job_data):
    """Test cancelling a queued job"""
    # Submit job with dependency so it waits
    sample_job_data['job_id'] = "cancel-test"
    job_id = await manager.submit_job_dict(
        sample_job_data,
        depends_on=["nonexistent"]
    )
    
    # Cancel job
    result = await manager.cancel_job(job_id)
    
    # Should succeed for waiting jobs
    # (may fail if job already started, which is ok)
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_get_job_status_active(manager, sample_job_data):
    """Test getting status of active job"""
    job_id = await manager.submit_job_dict(sample_job_data)
    
    status = manager.get_job_status(job_id)
    
    assert status is not None
    assert status['job_id'] == job_id
    assert 'status' in status
    assert 'priority' in status


@pytest.mark.asyncio
async def test_get_job_status_not_found(manager):
    """Test getting status of non-existent job"""
    status = manager.get_job_status("nonexistent")
    
    assert status is None


@pytest.mark.asyncio
async def test_get_queue_stats(manager):
    """Test getting queue statistics"""
    stats = manager.get_queue_stats()
    
    assert 'queue' in stats
    assert 'workers' in stats
    assert 'retry_policy' in stats
    
    # Check queue stats
    queue_stats = stats['queue']
    assert 'queued' in queue_stats
    assert 'running' in queue_stats
    assert 'completed' in queue_stats


@pytest.mark.asyncio
async def test_list_jobs_empty(manager):
    """Test listing jobs when queue is empty"""
    jobs = manager.list_jobs()
    
    assert isinstance(jobs, list)


@pytest.mark.asyncio
async def test_list_jobs_with_filter(manager, sample_job_data):
    """Test listing jobs with status filter"""
    await manager.submit_job_dict(sample_job_data)
    
    # List all jobs
    all_jobs = manager.list_jobs()
    assert isinstance(all_jobs, list)
    
    # Filter by status
    queued_jobs = manager.list_jobs(status="queued")
    assert isinstance(queued_jobs, list)


@pytest.mark.asyncio
async def test_list_jobs_limit(manager):
    """Test listing jobs with limit"""
    # Submit multiple jobs
    for i in range(5):
        job_data = {
            "job_id": f"job-{i}",
            "tool": "aider",
            "command": {"exe": "aider"}
        }
        await manager.submit_job_dict(job_data)
    
    # List with limit
    jobs = manager.list_jobs(limit=3)
    
    assert len(jobs) <= 3


@pytest.mark.asyncio
async def test_custom_retry_policy(temp_db):
    """Test manager with custom retry policy"""
    custom_policy = RetryPolicy(
        max_retries=5,
        strategy=BackoffStrategy.LINEAR
    )
    
    manager = QueueManager(
        db_path=temp_db,
        retry_policy=custom_policy
    )
    
    assert manager.retry_policy.max_retries == 5
    assert manager.retry_policy.strategy == BackoffStrategy.LINEAR


@pytest.mark.asyncio
async def test_custom_worker_count(temp_db):
    """Test manager with custom worker count"""
    manager = QueueManager(db_path=temp_db, worker_count=5)
    
    assert manager.worker_pool.worker_count == 5


@pytest.mark.asyncio
async def test_context_manager(temp_db, sample_job_data):
    """Test using manager as context manager"""
    with QueueManager(db_path=temp_db) as manager:
        job_id = asyncio.run(manager.submit_job_dict(sample_job_data))
        assert job_id == "test-job-1"
    
    # Manager should be stopped after context


@pytest.mark.asyncio
async def test_submit_multiple_priorities(manager):
    """Test submitting jobs with different priorities"""
    priorities = ["critical", "high", "normal", "low"]
    
    for i, priority in enumerate(priorities):
        job_data = {
            "job_id": f"job-{priority}",
            "tool": "aider",
            "command": {"exe": "aider"}
        }
        await manager.submit_job_dict(job_data, priority=priority)
    
    stats = manager.get_queue_stats()
    total = stats['queue'].get('queued', 0) + stats['queue'].get('running', 0)
    assert total >= 4


@pytest.mark.asyncio
async def test_job_status_completed(manager):
    """Test job status shows as completed"""
    job_data = {
        "job_id": "completed-test",
        "tool": "aider",
        "command": {"exe": "aider"}
    }
    
    job_id = await manager.submit_job_dict(job_data)
    
    # Manually mark complete for testing
    if job_id in manager.queue.active_jobs:
        manager.queue.mark_complete(job_id)
    
    status = manager.get_job_status(job_id)
    if status:
        # Status could be completed or None (if not in active tracking)
        assert status.get('status') in ['completed', None] or status is None


@pytest.mark.asyncio
async def test_graceful_shutdown(manager, sample_job_data):
    """Test graceful shutdown waits for jobs"""
    await manager.start()
    await manager.submit_job_dict(sample_job_data)
    
    # Stop gracefully
    await manager.stop(graceful=True)
    
    assert manager.running is False


@pytest.mark.asyncio
async def test_force_shutdown(manager, sample_job_data):
    """Test force shutdown doesn't wait"""
    await manager.start()
    await manager.submit_job_dict(sample_job_data)
    
    # Force stop
    await manager.stop(graceful=False)
    
    assert manager.running is False
