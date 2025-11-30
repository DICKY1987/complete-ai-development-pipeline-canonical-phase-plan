"""
Unit tests for Task Queue Management
"""
# DOC_ID: DOC-TEST-TESTS-TEST-TASK-QUEUE-106
# DOC_ID: DOC-TEST-TESTS-TEST-TASK-QUEUE-067
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from modules.core_state.m010003_task_queue import (
    Task, TaskQueue, TaskPayload, TaskConstraints,
    TaskTimeouts, RoutingState, TaskResult, TaskStatus
)


@pytest.fixture
def temp_queue_dir(tmp_path):
    """Create temporary queue directory"""
    queue_dir = tmp_path / ".tasks"
    yield str(queue_dir)
    # Cleanup handled by tmp_path


@pytest.fixture
def task_queue(temp_queue_dir):
    """Create TaskQueue instance"""
    return TaskQueue(base_path=temp_queue_dir)


@pytest.fixture
def sample_task():
    """Create sample task for testing"""
    return Task(
        task_id=Task.generate_id(),
        source_app="codex",
        mode="prompt",
        capabilities=["refactor", "python"],
        payload=TaskPayload(
            repo_path="/test/repo",
            files=["src/module.py"],
            description="Refactor for clarity"
        )
    )


def test_task_generation():
    """Test task ID generation"""
    task_id1 = Task.generate_id()
    task_id2 = Task.generate_id()
    
    assert task_id1 != task_id2
    assert len(task_id1) > 0


def test_task_serialization(sample_task):
    """Test task to/from dict"""
    task_dict = sample_task.to_dict()
    assert isinstance(task_dict, dict)
    assert task_dict['task_id'] == sample_task.task_id
    
    restored_task = Task.from_dict(task_dict)
    assert restored_task.task_id == sample_task.task_id
    assert restored_task.source_app == sample_task.source_app


def test_enqueue_dequeue(task_queue, sample_task):
    """Test basic enqueue/dequeue cycle"""
    # Enqueue
    task_id = task_queue.enqueue(sample_task)
    assert task_id == sample_task.task_id
    
    # Dequeue
    dequeued_task = task_queue.dequeue()
    assert dequeued_task is not None
    assert dequeued_task.task_id == sample_task.task_id
    assert dequeued_task.source_app == sample_task.source_app


def test_peek(task_queue):
    """Test peeking at queue without removing"""
    # Enqueue multiple tasks
    tasks = []
    for i in range(3):
        task = Task(
            task_id=Task.generate_id(),
            source_app="test",
            mode="prompt",
            capabilities=["test"],
            payload=TaskPayload(repo_path="/test", files=[f"file{i}.py"])
        )
        tasks.append(task)
        task_queue.enqueue(task)
    
    # Peek at queue
    peeked = task_queue.peek(limit=10)
    assert len(peeked) == 3
    
    # Verify tasks still in inbox
    peeked_again = task_queue.peek()
    assert len(peeked_again) == 3


def test_move_to_running(task_queue, sample_task):
    """Test moving task to running state"""
    task_queue.enqueue(sample_task)
    
    success = task_queue.move_to_running(sample_task.task_id)
    assert success is True
    
    # Verify task no longer in inbox
    peeked = task_queue.peek()
    assert len(peeked) == 0


def test_complete_task(task_queue, sample_task):
    """Test completing a task"""
    task_queue.enqueue(sample_task)
    task_queue.move_to_running(sample_task.task_id)
    
    result = TaskResult(
        task_id=sample_task.task_id,
        success=True,
        output="Task completed successfully"
    )
    
    success = task_queue.complete(sample_task.task_id, result)
    assert success is True
    
    # Verify task status
    status = task_queue.get_status(sample_task.task_id)
    assert status is not None
    assert status.state == "done"


def test_fail_task(task_queue, sample_task):
    """Test failing a task"""
    task_queue.enqueue(sample_task)
    task_queue.move_to_running(sample_task.task_id)
    
    error_msg = "Task execution failed"
    success = task_queue.fail(sample_task.task_id, error_msg)
    assert success is True
    
    # Verify task status
    status = task_queue.get_status(sample_task.task_id)
    assert status is not None
    assert status.state == "failed"
    assert status.error == error_msg


def test_get_status_not_found(task_queue):
    """Test getting status of non-existent task"""
    status = task_queue.get_status("non-existent-id")
    assert status is None


def test_persistence(temp_queue_dir, sample_task):
    """Test task persistence across queue instances"""
    # Create queue and enqueue task
    queue1 = TaskQueue(base_path=temp_queue_dir)
    queue1.enqueue(sample_task)
    
    # Create new queue instance
    queue2 = TaskQueue(base_path=temp_queue_dir)
    
    # Verify task persists
    dequeued = queue2.dequeue()
    assert dequeued is not None
    assert dequeued.task_id == sample_task.task_id


def test_concurrent_access(task_queue):
    """Test file locking for concurrent access safety"""
    # This is a basic test - full concurrency testing would require threading
    task1 = Task(
        task_id=Task.generate_id(),
        source_app="app1",
        mode="prompt",
        capabilities=["test"],
        payload=TaskPayload(repo_path="/test", files=["file1.py"])
    )
    
    task2 = Task(
        task_id=Task.generate_id(),
        source_app="app2",
        mode="prompt",
        capabilities=["test"],
        payload=TaskPayload(repo_path="/test", files=["file2.py"])
    )
    
    # Enqueue both - file locking should prevent corruption
    id1 = task_queue.enqueue(task1)
    id2 = task_queue.enqueue(task2)
    
    assert id1 == task1.task_id
    assert id2 == task2.task_id
    
    # Both should be retrievable
    peeked = task_queue.peek(limit=10)
    assert len(peeked) == 2


def test_empty_queue(task_queue):
    """Test behavior with empty queue"""
    dequeued = task_queue.dequeue()
    assert dequeued is None
    
    peeked = task_queue.peek()
    assert len(peeked) == 0


def test_fifo_order(task_queue):
    """Test FIFO ordering of queue"""
    import time
    tasks = []
    for i in range(5):
        task = Task(
            task_id=Task.generate_id(),
            source_app=f"app{i}",
            mode="prompt",
            capabilities=["test"],
            payload=TaskPayload(repo_path="/test", files=[f"file{i}.py"])
        )
        tasks.append(task)
        task_queue.enqueue(task)
        time.sleep(0.001)  # Ensure different timestamps
    
    # Dequeue and verify order
    for original_task in tasks:
        dequeued = task_queue.dequeue()
        assert dequeued.task_id == original_task.task_id
        task_queue.move_to_running(dequeued.task_id)
