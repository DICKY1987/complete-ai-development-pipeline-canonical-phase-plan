"""Tests for progress tracker - WS-03-03B"""

import pytest
import sys
from pathlib import Path

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.monitoring import ProgressTracker


class TestProgressTracker:
    """Test ProgressTracker functionality"""

    # DOC_ID: DOC-TEST-MONITORING-TEST-PROGRESS-TRACKER-181

    def test_create_tracker(self):
        """Test creating a progress tracker"""
        tracker = ProgressTracker("run-123", total_tasks=10)

        assert tracker.run_id == "run-123"
        assert tracker.total_tasks == 10
        assert tracker.completed_tasks == 0

    def test_start_tracking(self):
        """Test starting progress tracking"""
        tracker = ProgressTracker("run-123", total_tasks=5)
        tracker.start()

        assert tracker.started_at is not None
        assert tracker.get_elapsed_time() is not None

    def test_complete_task(self):
        """Test completing a task"""
        tracker = ProgressTracker("run-123", total_tasks=5)
        tracker.complete_task("task-1", duration=1.5)

        assert tracker.completed_tasks == 1
        assert len(tracker.task_durations) == 1

    def test_fail_task(self):
        """Test failing a task"""
        tracker = ProgressTracker("run-123", total_tasks=5)
        tracker.fail_task("task-1")

        assert tracker.failed_tasks == 1

    def test_completion_percent_zero_tasks(self):
        """Test completion percent with zero tasks"""
        tracker = ProgressTracker("run-123", total_tasks=0)

        assert tracker.get_completion_percent() == 100.0

    def test_completion_percent_basic(self):
        """Test basic completion percent calculation"""
        tracker = ProgressTracker("run-123", total_tasks=10)

        # 0% complete
        assert tracker.get_completion_percent() == 0.0

        # 50% complete
        for i in range(5):
            tracker.complete_task(f"task-{i}")
        assert tracker.get_completion_percent() == 50.0

        # 100% complete
        for i in range(5):
            tracker.complete_task(f"task-{i+5}")
        assert tracker.get_completion_percent() == 100.0

    def test_completion_percent_with_current_task(self):
        """Test completion percent includes current task progress"""
        tracker = ProgressTracker("run-123", total_tasks=10)

        # Complete 5 tasks (50%)
        for i in range(5):
            tracker.complete_task(f"task-{i}")

        # Start a task and mark it 50% done
        tracker.start_task("task-6")
        tracker.update_task_progress(50.0)

        # Should be 50% + (50% of 1/10) = 55%
        percent = tracker.get_completion_percent()
        assert 54.0 < percent < 56.0

    def test_time_estimates(self):
        """Test time estimation"""
        tracker = ProgressTracker("run-123", total_tasks=5)
        tracker.start()

        # Complete 3 tasks with known durations
        tracker.complete_task("task-1", duration=2.0)
        tracker.complete_task("task-2", duration=2.0)
        tracker.complete_task("task-3", duration=2.0)

        # Estimated remaining: 2 tasks * 2s avg = 4s
        remaining = tracker.get_estimated_remaining_time()
        assert remaining is not None
        assert 3.5 < remaining < 4.5

    def test_snapshot(self):
        """Test getting progress snapshot"""
        tracker = ProgressTracker("run-123", total_tasks=10)
        tracker.start()

        tracker.complete_task("task-1", duration=1.0)
        tracker.complete_task("task-2", duration=1.0)
        tracker.fail_task("task-3")

        snapshot = tracker.get_snapshot()

        assert snapshot.run_id == "run-123"
        assert snapshot.total_tasks == 10
        assert snapshot.completed_tasks == 2
        assert snapshot.failed_tasks == 1
        assert snapshot.pending_tasks == 7
        assert snapshot.started_at is not None

    def test_snapshot_to_dict(self):
        """Test converting snapshot to dict"""
        tracker = ProgressTracker("run-123", total_tasks=5)
        tracker.start()
        tracker.complete_task("task-1")

        snapshot = tracker.get_snapshot()
        d = snapshot.to_dict()

        assert d["run_id"] == "run-123"
        assert d["total_tasks"] == 5
        assert d["completed_tasks"] == 1
        assert "timestamp" in d
