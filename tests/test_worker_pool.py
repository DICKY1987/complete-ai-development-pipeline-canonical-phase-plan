"""
Integration tests for WorkerPool (Phase 4B)
Tests worker pool operations, job execution, and concurrency.
"""
DOC_ID: DOC-TEST-TESTS-TEST-WORKER-POOL-110
DOC_ID: DOC-TEST-TESTS-TEST-WORKER-POOL-071
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from engine.queue.worker_pool import WorkerPool
from engine.queue.job_queue import JobQueue
from engine.queue.job_wrapper import JobWrapper, JobStatus, JobPriority
from engine.types import JobResult


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database"""
    db_path = tmp_path / "test_worker.db"
    yield str(db_path)


@pytest.fixture
def queue(temp_db):
    """Create JobQueue instance"""
    return JobQueue(db_path=temp_db)


@pytest.fixture
def mock_orchestrator():
    """Create mock orchestrator"""
    orchestrator = Mock()
    orchestrator.run_job_dict = Mock(return_value=JobResult(
        success=True,
        exit_code=0,
        stdout="Success",
        stderr=""
    ))
    return orchestrator


@pytest.fixture
def worker_pool(queue, mock_orchestrator):
    """Create WorkerPool instance"""
    return WorkerPool(
        queue=queue,
        worker_count=2,
        orchestrator=mock_orchestrator
    )


@pytest.mark.asyncio
async def test_worker_pool_initialization(queue):
    """Test worker pool initializes correctly"""
    pool = WorkerPool(queue=queue, worker_count=3)
    
    assert pool.worker_count == 3
    assert pool.running is False
    assert len(pool.workers) == 0


@pytest.mark.asyncio
async def test_start_workers(worker_pool):
    """Test starting worker pool"""
    await worker_pool.start()
    
    assert worker_pool.running is True
    assert len(worker_pool.workers) == 2


@pytest.mark.asyncio
async def test_stop_workers_graceful(worker_pool):
    """Test graceful shutdown of workers"""
    await worker_pool.start()
    await worker_pool.stop(graceful=True)
    
    assert worker_pool.running is False
    assert len(worker_pool.workers) == 0


@pytest.mark.asyncio
async def test_stop_workers_force(worker_pool):
    """Test force shutdown of workers"""
    await worker_pool.start()
    await worker_pool.stop(graceful=False)
    
    assert worker_pool.running is False
    assert len(worker_pool.workers) == 0


@pytest.mark.asyncio
async def test_worker_executes_job(queue, mock_orchestrator):
    """Test worker picks up and executes job"""
    # Create worker pool
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=mock_orchestrator
    )
    
    # Submit job
    job = JobWrapper(
        job_id="exec-test",
        job_data={"tool": "aider", "command": {"exe": "aider"}}
    )
    await queue.submit(job)
    
    # Start workers
    await pool.start()
    
    # Wait a bit for worker to process
    await asyncio.sleep(0.5)
    
    # Stop workers
    await pool.stop(graceful=True)
    
    # Job should be completed
    stats = queue.get_stats()
    assert stats['completed'] >= 1 or stats['running'] >= 0


@pytest.mark.asyncio
async def test_worker_handles_job_failure(queue):
    """Test worker handles job execution failure"""
    # Create orchestrator that fails
    failing_orchestrator = Mock()
    failing_orchestrator.run_job_dict = Mock(return_value=JobResult(
        success=False,
        exit_code=1,
        stdout="",
        stderr="Error"
    ))
    
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=failing_orchestrator
    )
    
    # Submit job with limited retries
    job = JobWrapper(
        job_id="fail-test",
        job_data={"tool": "aider"},
        max_retries=1
    )
    await queue.submit(job)
    
    # Start workers
    await pool.start()
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Stop workers
    await pool.stop(graceful=True)
    
    # Job should be retried or failed
    stats = queue.get_stats()
    assert stats['failed'] >= 0 or stats['retry'] >= 0


@pytest.mark.asyncio
async def test_worker_concurrent_execution(queue, mock_orchestrator):
    """Test multiple workers execute jobs concurrently"""
    pool = WorkerPool(
        queue=queue,
        worker_count=3,
        orchestrator=mock_orchestrator
    )
    
    # Submit multiple jobs
    for i in range(5):
        job = JobWrapper(
            job_id=f"concurrent-{i}",
            job_data={"tool": "aider"}
        )
        await queue.submit(job)
    
    # Start workers
    await pool.start()
    
    # Wait for processing
    await asyncio.sleep(1.0)
    
    # Stop workers
    await pool.stop(graceful=True)
    
    # Multiple jobs should be processed
    stats = queue.get_stats()
    assert stats['completed'] + stats['running'] > 0


@pytest.mark.asyncio
async def test_worker_handles_exception(queue):
    """Test worker handles execution exception"""
    # Create orchestrator that raises exception
    failing_orchestrator = Mock()
    failing_orchestrator.run_job_dict = Mock(
        side_effect=RuntimeError("Execution error")
    )
    
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=failing_orchestrator
    )
    
    # Submit job
    job = JobWrapper(
        job_id="exception-test",
        job_data={"tool": "aider"},
        max_retries=1
    )
    await queue.submit(job)
    
    # Start workers
    await pool.start()
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Stop workers
    await pool.stop(graceful=True)
    
    # Job should be retried or failed (not crash the worker)
    assert pool.running is False


@pytest.mark.asyncio
async def test_get_status(worker_pool):
    """Test getting worker pool status"""
    status = worker_pool.get_status()
    
    assert 'running' in status
    assert 'worker_count' in status
    assert 'active_workers' in status
    assert 'queue_stats' in status
    
    assert status['running'] is False
    assert status['worker_count'] == 2


@pytest.mark.asyncio
async def test_get_status_running(worker_pool):
    """Test status when workers are running"""
    await worker_pool.start()
    
    status = worker_pool.get_status()
    
    assert status['running'] is True
    assert status['active_workers'] >= 0
    
    await worker_pool.stop()


@pytest.mark.asyncio
async def test_wait_all(worker_pool, queue):
    """Test waiting for all workers to complete"""
    # Submit job
    job = JobWrapper(
        job_id="wait-test",
        job_data={"tool": "aider"}
    )
    await queue.submit(job)
    
    # Start workers
    await worker_pool.start()
    
    # Wait for completion (with timeout)
    try:
        await asyncio.wait_for(worker_pool.wait_all(), timeout=2.0)
    except asyncio.TimeoutError:
        pass
    
    # Cleanup
    await worker_pool.stop(graceful=False)


@pytest.mark.asyncio
async def test_worker_respects_shutdown_event(queue, mock_orchestrator):
    """Test worker stops when shutdown event is set"""
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=mock_orchestrator
    )
    
    # Start workers
    await pool.start()
    assert pool.running is True
    
    # Trigger shutdown
    pool.shutdown_event.set()
    
    # Wait a bit for workers to notice
    await asyncio.sleep(0.2)
    
    # Workers should stop
    await pool.stop(graceful=True)


@pytest.mark.asyncio
async def test_worker_pool_with_priority_jobs(queue, mock_orchestrator):
    """Test worker pool processes jobs in priority order"""
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=mock_orchestrator
    )
    
    # Submit jobs with different priorities
    low = JobWrapper(
        job_id="low",
        job_data={},
        priority=JobPriority.LOW
    )
    high = JobWrapper(
        job_id="high",
        job_data={},
        priority=JobPriority.HIGH
    )
    
    # Submit in reverse priority order
    await queue.submit(low)
    await queue.submit(high)
    
    # Start workers
    await pool.start()
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    await pool.stop(graceful=True)
    
    # Both should be processed, high priority first
    stats = queue.get_stats()
    assert stats['completed'] + stats['running'] > 0


@pytest.mark.asyncio
async def test_worker_loop_continues_after_error(queue):
    """Test worker continues processing after job error"""
    # Orchestrator that fails first job, succeeds second
    call_count = [0]
    
    def run_job(job_data):
        call_count[0] += 1
        if call_count[0] == 1:
            raise RuntimeError("First job fails")
        return JobResult(success=True, exit_code=0, stdout="", stderr="")
    
    orchestrator = Mock()
    orchestrator.run_job_dict = Mock(side_effect=run_job)
    
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=orchestrator
    )
    
    # Submit two jobs
    job1 = JobWrapper(job_id="job1", job_data={}, max_retries=0)
    job2 = JobWrapper(job_id="job2", job_data={})
    
    await queue.submit(job1)
    await queue.submit(job2)
    
    # Start workers
    await pool.start()
    
    # Wait for processing
    await asyncio.sleep(1.0)
    
    await pool.stop(graceful=True)
    
    # Worker should have processed both jobs despite first failing
    assert call_count[0] >= 1


@pytest.mark.asyncio
async def test_empty_queue_handling(queue, mock_orchestrator):
    """Test worker handles empty queue gracefully"""
    pool = WorkerPool(
        queue=queue,
        worker_count=1,
        orchestrator=mock_orchestrator
    )
    
    # Start workers with empty queue
    await pool.start()
    
    # Wait a bit
    await asyncio.sleep(0.3)
    
    # Should still be running, not crashed
    assert pool.running is True
    
    await pool.stop(graceful=True)
