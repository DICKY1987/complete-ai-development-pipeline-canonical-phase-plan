"""Tests for worker lifecycle management."""

import pytest
from datetime import datetime, timedelta, timezone
from modules.core_engine.m010001_worker import Worker, WorkerState, WorkerPool


def test_worker_creation():
    """Test worker instance creation."""
    worker = Worker(
        worker_id="test-worker-1",
        adapter_type="aider",
        state=WorkerState.IDLE
    )
    
    assert worker.worker_id == "test-worker-1"
    assert worker.adapter_type == "aider"
    assert worker.state == WorkerState.IDLE
    assert worker.spawned_at is not None


def test_worker_pool_spawn(worker_pool):
    """Test worker pool spawning."""
    pool = worker_pool
    
    worker1 = pool.spawn_worker("aider")
    assert worker1.state == WorkerState.IDLE
    assert worker1.worker_id in pool.workers
    
    worker2 = pool.spawn_worker("codex")
    assert len(pool.workers) == 2
    
    # Pool full (max=4 in fixture)
    worker3 = pool.spawn_worker("aider")
    worker4 = pool.spawn_worker("aider")
    
    with pytest.raises(RuntimeError, match="Worker pool full"):
        pool.spawn_worker("aider")


def test_worker_assignment(worker_pool):
    """Test task assignment to worker."""
    pool = worker_pool
    worker = pool.spawn_worker("aider")
    
    pool.assign_task(worker.worker_id, "task-1")
    
    assert pool.workers[worker.worker_id].state == WorkerState.BUSY
    assert pool.workers[worker.worker_id].current_task_id == "task-1"
    assert worker.worker_id not in pool.idle_queue


def test_worker_release(worker_pool):
    """Test releasing worker back to idle."""
    pool = worker_pool
    worker = pool.spawn_worker("aider")
    
    pool.assign_task(worker.worker_id, "task-1")
    pool.release_worker(worker.worker_id)
    
    assert pool.workers[worker.worker_id].state == WorkerState.IDLE
    assert pool.workers[worker.worker_id].current_task_id is None
    assert worker.worker_id in pool.idle_queue


def test_get_idle_worker(worker_pool):
    """Test getting idle worker from pool."""
    pool = worker_pool
    
    w1 = pool.spawn_worker("aider")
    w2 = pool.spawn_worker("codex")
    w3 = pool.spawn_worker("aider")
    
    # All idle
    idle = pool.get_idle_worker()
    assert idle is not None
    
    # Filter by adapter type
    aider_worker = pool.get_idle_worker(adapter_type="aider")
    assert aider_worker.adapter_type == "aider"
    
    # Assign all workers
    pool.assign_task(w1.worker_id, "task-1")
    pool.assign_task(w2.worker_id, "task-2")
    pool.assign_task(w3.worker_id, "task-3")
    
    # No idle workers
    idle = pool.get_idle_worker()
    assert idle is None


def test_worker_termination(worker_pool):
    """Test worker termination."""
    pool = worker_pool
    worker = pool.spawn_worker("aider")
    
    pool.terminate_worker(worker.worker_id)
    
    assert pool.workers[worker.worker_id].state == WorkerState.TERMINATED
    assert pool.workers[worker.worker_id].terminated_at is not None
    assert worker.worker_id not in pool.idle_queue


def test_invalid_state_transition(worker_pool):
    """Test that invalid state transitions raise errors."""
    pool = worker_pool
    worker = pool.spawn_worker("aider")
    
    # Can't assign task to busy worker
    pool.assign_task(worker.worker_id, "task-1")
    with pytest.raises(ValueError, match="not idle"):
        pool.assign_task(worker.worker_id, "task-2")


def test_heartbeat_check(worker_pool):
    """Test heartbeat monitoring."""
    pool = worker_pool
    worker = pool.spawn_worker("aider")
    
    # Fresh worker - no stale heartbeat
    stale = pool.check_heartbeats(timeout_sec=300)
    assert len(stale) == 0
    
    # Manually set old heartbeat
    pool.workers[worker.worker_id].heartbeat_at = datetime.now(timezone.utc) - timedelta(seconds=400)
    
    # Now should be stale
    stale = pool.check_heartbeats(timeout_sec=300)
    assert worker.worker_id in stale
