#!/usr/bin/env python3
"""
Test Suite for Task Queue Manager - PH-4B
"""

import json
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from task_queue import TaskQueue, TaskState, TaskPriority


class TestTaskQueue:
    """Test task queue functionality."""
    
    @pytest.fixture
    def queue(self, tmp_path):
        """Create TaskQueue with temp directory."""
        return TaskQueue(queue_dir=str(tmp_path / "tasks"))
    
    def test_initialization(self, queue):
        """Test queue initialization creates directories."""
        assert queue.queue_dir.exists()
        assert (queue.queue_dir / "queued").exists()
        assert (queue.queue_dir / "running").exists()
        assert (queue.queue_dir / "complete").exists()
        assert (queue.queue_dir / "failed").exists()
    
    def test_enqueue_task(self, queue):
        """Test enqueueing a task."""
        task_id = queue.enqueue("PH-1A", priority="high")
        
        assert task_id is not None
        assert "PH-1A" in task_id
        
        # Check task file exists
        task_file = queue.queue_dir / "queued" / "PH-1A.json"
        assert task_file.exists()
    
    def test_enqueue_with_metadata(self, queue):
        """Test enqueueing task with metadata."""
        metadata = {"workstream": "WS-SPEC", "author": "test"}
        task_id = queue.enqueue("PH-1A", metadata=metadata)
        
        task = queue.get_task("PH-1A")
        assert task["metadata"] == metadata
    
    def test_dequeue_empty(self, queue):
        """Test dequeueing from empty queue."""
        task = queue.dequeue()
        assert task is None
    
    def test_dequeue_single_task(self, queue):
        """Test dequeueing single task."""
        queue.enqueue("PH-1A", priority="medium")
        
        task = queue.dequeue()
        
        assert task is not None
        assert task["phase_id"] == "PH-1A"
        assert task["priority_name"] == "medium"
    
    def test_priority_ordering(self, queue):
        """Test tasks are dequeued by priority."""
        queue.enqueue("PH-1A", priority="low")
        queue.enqueue("PH-1B", priority="high")
        queue.enqueue("PH-1C", priority="critical")
        queue.enqueue("PH-1D", priority="medium")
        
        # Should dequeue in priority order
        task1 = queue.dequeue()
        assert task1["phase_id"] == "PH-1C"  # critical
        
        task2 = queue.dequeue()
        assert task2["phase_id"] == "PH-1B"  # high
        
        task3 = queue.dequeue()
        assert task3["phase_id"] == "PH-1D"  # medium
        
        task4 = queue.dequeue()
        assert task4["phase_id"] == "PH-1A"  # low
    
    def test_mark_running(self, queue):
        """Test marking task as running."""
        queue.enqueue("PH-1A")
        
        success = queue.mark_running("PH-1A")
        
        assert success is True
        
        # Check task moved to running
        running_file = queue.queue_dir / "running" / "PH-1A.json"
        assert running_file.exists()
        
        # Check not in queued
        queued_file = queue.queue_dir / "queued" / "PH-1A.json"
        assert not queued_file.exists()
    
    def test_mark_complete(self, queue):
        """Test marking task as complete."""
        queue.enqueue("PH-1A")
        queue.mark_running("PH-1A")
        
        result = {"status": "success", "tests_passed": 10}
        success = queue.mark_complete("PH-1A", result=result)
        
        assert success is True
        
        # Check task moved to complete
        complete_file = queue.queue_dir / "complete" / "PH-1A.json"
        assert complete_file.exists()
        
        # Check result saved
        task = queue.get_task("PH-1A")
        assert task["result"] == result
    
    def test_mark_failed(self, queue):
        """Test marking task as failed."""
        queue.enqueue("PH-1A")
        queue.mark_running("PH-1A")
        
        success = queue.mark_failed("PH-1A", "Test error")
        
        assert success is True
        
        # Check task moved to failed
        failed_file = queue.queue_dir / "failed" / "PH-1A.json"
        assert failed_file.exists()
        
        # Check error saved
        task = queue.get_task("PH-1A")
        assert task["error"] == "Test error"
    
    def test_list_queued(self, queue):
        """Test listing queued tasks."""
        queue.enqueue("PH-1A", priority="low")
        queue.enqueue("PH-1B", priority="high")
        
        tasks = queue.list_queued()
        
        assert len(tasks) == 2
        # Should be sorted by priority
        assert tasks[0]["phase_id"] == "PH-1B"  # high
        assert tasks[1]["phase_id"] == "PH-1A"  # low
    
    def test_list_running(self, queue):
        """Test listing running tasks."""
        queue.enqueue("PH-1A")
        queue.enqueue("PH-1B")
        queue.mark_running("PH-1A")
        
        tasks = queue.list_running()
        
        assert len(tasks) == 1
        assert tasks[0]["phase_id"] == "PH-1A"
    
    def test_list_complete(self, queue):
        """Test listing completed tasks."""
        queue.enqueue("PH-1A")
        queue.mark_running("PH-1A")
        queue.mark_complete("PH-1A")
        
        tasks = queue.list_complete()
        
        assert len(tasks) == 1
        assert tasks[0]["phase_id"] == "PH-1A"
    
    def test_list_failed(self, queue):
        """Test listing failed tasks."""
        queue.enqueue("PH-1A")
        queue.mark_running("PH-1A")
        queue.mark_failed("PH-1A", "Error")
        
        tasks = queue.list_failed()
        
        assert len(tasks) == 1
        assert tasks[0]["phase_id"] == "PH-1A"
    
    def test_get_task(self, queue):
        """Test getting task by phase ID."""
        queue.enqueue("PH-1A", priority="high")
        
        task = queue.get_task("PH-1A")
        
        assert task is not None
        assert task["phase_id"] == "PH-1A"
        assert task["priority_name"] == "high"
    
    def test_get_task_not_found(self, queue):
        """Test getting non-existent task."""
        task = queue.get_task("PH-NONEXISTENT")
        assert task is None
    
    def test_clear_state(self, queue):
        """Test clearing tasks in a state."""
        queue.enqueue("PH-1A")
        queue.enqueue("PH-1B")
        queue.enqueue("PH-1C")
        
        count = queue.clear_state(TaskState.QUEUED)
        
        assert count == 3
        assert len(queue.list_queued()) == 0
    
    def test_get_stats(self, queue):
        """Test queue statistics."""
        queue.enqueue("PH-1A")
        queue.enqueue("PH-1B")
        queue.mark_running("PH-1A")
        
        stats = queue.get_stats()
        
        assert stats["queued"] == 1
        assert stats["running"] == 1
        assert stats["complete"] == 0
        assert stats["failed"] == 0
        assert stats["total"] == 2
    
    def test_task_state_transitions(self, queue):
        """Test complete task lifecycle."""
        # Enqueue
        queue.enqueue("PH-1A")
        task = queue.get_task("PH-1A")
        assert task["state"] == "queued"
        
        # Mark running
        queue.mark_running("PH-1A")
        task = queue.get_task("PH-1A")
        assert task["state"] == "running"
        
        # Mark complete
        queue.mark_complete("PH-1A")
        task = queue.get_task("PH-1A")
        assert task["state"] == "complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
