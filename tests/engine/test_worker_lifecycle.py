"""
Tests for WorkerLifecycle state machine and tracking.

Tests worker creation, state transitions, task assignment/completion,
heartbeat monitoring, and statistics tracking.

Author: AI Development Pipeline
Created: 2025-11-23
WS: WS-NEXT-002-001 (Testing)
"""
# DOC_ID: DOC-TEST-ENGINE-TEST-WORKER-LIFECYCLE-179

import pytest
import sys
import sqlite3
from datetime import datetime, UTC, timedelta
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.worker_lifecycle import WorkerLifecycle, WorkerStatistics


class MockDB:
    """Mock database for testing"""
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize test schema"""
        schema_path = Path(__file__).parent.parent.parent / 'schema' / 'migrations' / '002_add_workers_table.sql'
        with open(schema_path, 'r') as f:
            self.conn.executescript(f.read())
        self.conn.commit()


@pytest.fixture
def db():
    """Create test database"""
    return MockDB()


@pytest.fixture
def lifecycle(db):
    """Create WorkerLifecycle instance"""
    return WorkerLifecycle(db)


@pytest.fixture
def worker_id():
    """Generate test worker ID"""
    return "01HQTEST00000000000000001"


@pytest.fixture
def task_id():
    """Generate test task ID"""
    return "01HQTASK00000000000000001"


class TestWorkerStatistics:
    """Test WorkerStatistics dataclass"""

    def test_initial_statistics(self):
        """Test initial statistics are zero"""
        stats = WorkerStatistics()
        assert stats.tasks_completed == 0
        assert stats.tasks_failed == 0
        assert stats.total_execution_time == 0.0
        assert stats.avg_task_duration == 0.0

    def test_avg_task_duration_with_tasks(self):
        """Test average duration calculation"""
        stats = WorkerStatistics(
            tasks_completed=3,
            tasks_failed=1,
            total_execution_time=40.0
        )
        assert stats.avg_task_duration == 10.0  # 40s / 4 tasks

    def test_avg_task_duration_zero_tasks(self):
        """Test average duration with no tasks"""
        stats = WorkerStatistics(total_execution_time=10.0)
        assert stats.avg_task_duration == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary"""
        stats = WorkerStatistics(
            tasks_completed=5,
            tasks_failed=2,
            total_execution_time=100.0
        )
        data = stats.to_dict()

        assert data['tasks_completed'] == 5
        assert data['tasks_failed'] == 2
        assert data['total_execution_time'] == 100.0
        assert data['avg_task_duration'] == pytest.approx(14.285, rel=0.01)


class TestWorkerCreation:
    """Test worker creation"""

    def test_create_worker(self, lifecycle, worker_id):
        """Test creating a new worker"""
        result = lifecycle.create_worker(
            worker_id=worker_id,
            worker_type='executor'
        )

        assert result == worker_id

        # Verify worker was created
        worker = lifecycle.get_worker(worker_id)
        assert worker is not None
        assert worker['worker_id'] == worker_id
        assert worker['worker_type'] == 'executor'
        assert worker['state'] == 'idle'
        assert worker['current_task_id'] is None

    def test_create_worker_with_config(self, lifecycle, worker_id):
        """Test creating worker with config"""
        config = {
            'max_parallel_tasks': 5,
            'heartbeat_interval': 30,
            'timeout_seconds': 300
        }

        lifecycle.create_worker(
            worker_id=worker_id,
            worker_type='executor',
            config=config
        )

        worker = lifecycle.get_worker(worker_id)
        assert worker['config'] == config

    def test_create_worker_with_metadata(self, lifecycle, worker_id):
        """Test creating worker with metadata"""
        metadata = {
            'hostname': 'worker-001',
            'version': '1.0.0'
        }

        lifecycle.create_worker(
            worker_id=worker_id,
            worker_type='monitor',
            metadata=metadata
        )

        worker = lifecycle.get_worker(worker_id)
        assert worker['metadata'] == metadata

    def test_create_worker_invalid_type(self, lifecycle, worker_id):
        """Test creating worker with invalid type"""
        with pytest.raises(ValueError, match="Invalid worker_type"):
            lifecycle.create_worker(
                worker_id=worker_id,
                worker_type='invalid_type'
            )

    def test_create_worker_all_types(self, lifecycle):
        """Test creating workers of all valid types"""
        types = ['executor', 'monitor', 'validator', 'scheduler', 'custom']

        for i, worker_type in enumerate(types):
            worker_id = f"01HQTEST000000000000000{i:02d}"
            lifecycle.create_worker(worker_id, worker_type)

            worker = lifecycle.get_worker(worker_id)
            assert worker['worker_type'] == worker_type


class TestWorkerRetrieval:
    """Test worker retrieval"""

    def test_get_worker(self, lifecycle, worker_id):
        """Test getting a worker by ID"""
        lifecycle.create_worker(worker_id, 'executor')
        worker = lifecycle.get_worker(worker_id)

        assert worker is not None
        assert worker['worker_id'] == worker_id

    def test_get_nonexistent_worker(self, lifecycle):
        """Test getting a worker that doesn't exist"""
        worker = lifecycle.get_worker('nonexistent')
        assert worker is None

    def test_get_worker_statistics_deserialized(self, lifecycle, worker_id):
        """Test that statistics are properly deserialized"""
        lifecycle.create_worker(worker_id, 'executor')
        worker = lifecycle.get_worker(worker_id)

        assert isinstance(worker['statistics'], dict)
        assert 'tasks_completed' in worker['statistics']
        assert 'tasks_failed' in worker['statistics']


class TestTaskAssignment:
    """Test task assignment"""

    def test_assign_task_idle_to_busy(self, lifecycle, worker_id, task_id):
        """Test assigning task to idle worker"""
        lifecycle.create_worker(worker_id, 'executor')

        result = lifecycle.assign_task(worker_id, task_id)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'busy'
        assert worker['current_task_id'] == task_id

    def test_assign_task_nonexistent_worker(self, lifecycle, task_id):
        """Test assigning task to nonexistent worker"""
        with pytest.raises(ValueError, match="Worker not found"):
            lifecycle.assign_task('nonexistent', task_id)

    def test_assign_task_already_busy(self, lifecycle, worker_id, task_id):
        """Test assigning task to already busy worker"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        # Try to assign another task
        with pytest.raises(ValueError, match="Cannot assign task"):
            lifecycle.assign_task(worker_id, '01HQTASK00000000000000002')

    def test_assign_task_paused_worker(self, lifecycle, worker_id, task_id):
        """Test cannot assign task to paused worker"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.pause_worker(worker_id)

        with pytest.raises(ValueError, match="Cannot assign task"):
            lifecycle.assign_task(worker_id, task_id)


class TestTaskCompletion:
    """Test task completion"""

    def test_complete_task_success(self, lifecycle, worker_id, task_id):
        """Test completing task successfully"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        result = lifecycle.complete_task(worker_id, success=True, execution_time=10.0)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'idle'
        assert worker['current_task_id'] is None
        assert worker['statistics']['tasks_completed'] == 1
        assert worker['statistics']['total_execution_time'] == 10.0

    def test_complete_task_failure(self, lifecycle, worker_id, task_id):
        """Test completing task with failure"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        lifecycle.complete_task(worker_id, success=False, execution_time=5.0)

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'idle'
        assert worker['statistics']['tasks_failed'] == 1
        assert worker['statistics']['tasks_completed'] == 0

    def test_complete_task_not_busy(self, lifecycle, worker_id):
        """Test completing task when worker not busy"""
        lifecycle.create_worker(worker_id, 'executor')

        with pytest.raises(ValueError, match="Cannot complete task"):
            lifecycle.complete_task(worker_id)

    def test_complete_multiple_tasks(self, lifecycle, worker_id):
        """Test completing multiple tasks accumulates statistics"""
        lifecycle.create_worker(worker_id, 'executor')

        # Complete 3 successful tasks
        for i in range(3):
            task_id = f"01HQTASK0000000000000000{i}"
            lifecycle.assign_task(worker_id, task_id)
            lifecycle.complete_task(worker_id, success=True, execution_time=10.0)

        worker = lifecycle.get_worker(worker_id)
        assert worker['statistics']['tasks_completed'] == 3
        assert worker['statistics']['total_execution_time'] == 30.0


class TestHeartbeat:
    """Test heartbeat tracking"""

    def test_heartbeat_updates(self, lifecycle, worker_id):
        """Test heartbeat updates timestamp"""
        lifecycle.create_worker(worker_id, 'executor')

        worker_before = lifecycle.get_worker(worker_id)
        heartbeat_before = worker_before['last_heartbeat']

        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)

        result = lifecycle.heartbeat(worker_id)
        assert result is True

        worker_after = lifecycle.get_worker(worker_id)
        heartbeat_after = worker_after['last_heartbeat']

        assert heartbeat_after != heartbeat_before


class TestWorkerPause:
    """Test worker pause/resume"""

    def test_pause_idle_worker(self, lifecycle, worker_id):
        """Test pausing idle worker"""
        lifecycle.create_worker(worker_id, 'executor')

        result = lifecycle.pause_worker(worker_id)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'paused'

    def test_pause_busy_worker(self, lifecycle, worker_id, task_id):
        """Test pausing busy worker"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        result = lifecycle.pause_worker(worker_id)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'paused'

    def test_resume_worker(self, lifecycle, worker_id):
        """Test resuming paused worker"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.pause_worker(worker_id)

        result = lifecycle.resume_worker(worker_id)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'idle'

    def test_resume_not_paused(self, lifecycle, worker_id):
        """Test cannot resume worker that's not paused"""
        lifecycle.create_worker(worker_id, 'executor')

        with pytest.raises(ValueError, match="Cannot resume"):
            lifecycle.resume_worker(worker_id)


class TestWorkerCrash:
    """Test worker crash handling"""

    def test_crash_worker(self, lifecycle, worker_id):
        """Test marking worker as crashed"""
        lifecycle.create_worker(worker_id, 'executor')

        result = lifecycle.crash_worker(
            worker_id,
            error_message="Worker encountered fatal error",
            stack_trace="Traceback..."
        )
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'crashed'
        assert worker['crash_info'] is not None
        assert worker['crash_info']['error_message'] == "Worker encountered fatal error"
        assert worker['crash_info']['stack_trace'] == "Traceback..."

    def test_crash_clears_current_task(self, lifecycle, worker_id, task_id):
        """Test crash clears current task"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        lifecycle.crash_worker(worker_id, "Error")

        worker = lifecycle.get_worker(worker_id)
        assert worker['current_task_id'] is None


class TestWorkerShutdown:
    """Test worker shutdown"""

    def test_shutdown_worker(self, lifecycle, worker_id):
        """Test shutting down worker"""
        lifecycle.create_worker(worker_id, 'executor')

        result = lifecycle.shutdown_worker(worker_id)
        assert result is True

        worker = lifecycle.get_worker(worker_id)
        assert worker['state'] == 'stopped'
        assert worker['stopped_at'] is not None

    def test_shutdown_clears_current_task(self, lifecycle, worker_id, task_id):
        """Test shutdown clears current task"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.assign_task(worker_id, task_id)

        lifecycle.shutdown_worker(worker_id)

        worker = lifecycle.get_worker(worker_id)
        assert worker['current_task_id'] is None


class TestWorkerListing:
    """Test worker listing and filtering"""

    def test_list_workers_empty(self, lifecycle):
        """Test listing workers when none exist"""
        workers = lifecycle.list_workers()
        assert len(workers) == 0

    def test_list_all_workers(self, lifecycle):
        """Test listing all workers"""
        for i in range(3):
            worker_id = f"01HQTEST000000000000000{i:02d}"
            lifecycle.create_worker(worker_id, 'executor')

        workers = lifecycle.list_workers()
        assert len(workers) == 3

    def test_list_workers_by_state(self, lifecycle):
        """Test filtering workers by state"""
        lifecycle.create_worker('01HQTEST00000000000000001', 'executor')
        lifecycle.create_worker('01HQTEST00000000000000002', 'executor')
        lifecycle.create_worker('01HQTEST00000000000000003', 'executor')

        lifecycle.pause_worker('01HQTEST00000000000000002')

        idle_workers = lifecycle.list_workers(state='idle')
        paused_workers = lifecycle.list_workers(state='paused')

        assert len(idle_workers) == 2
        assert len(paused_workers) == 1

    def test_list_workers_by_type(self, lifecycle):
        """Test filtering workers by type"""
        lifecycle.create_worker('01HQTEST00000000000000001', 'executor')
        lifecycle.create_worker('01HQTEST00000000000000002', 'monitor')
        lifecycle.create_worker('01HQTEST00000000000000003', 'executor')

        executors = lifecycle.list_workers(worker_type='executor')
        monitors = lifecycle.list_workers(worker_type='monitor')

        assert len(executors) == 2
        assert len(monitors) == 1


class TestStateTransitions:
    """Test state machine transitions"""

    def test_terminal_states_immutable(self, lifecycle, worker_id):
        """Test that terminal states cannot transition"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.shutdown_worker(worker_id)

        # Cannot transition from stopped
        assert not lifecycle._can_transition('stopped', 'idle')
        assert not lifecycle._can_transition('stopped', 'busy')

    def test_valid_transitions(self, lifecycle):
        """Test all valid state transitions"""
        # idle -> busy
        assert lifecycle._can_transition('idle', 'busy') is True

        # idle -> paused
        assert lifecycle._can_transition('idle', 'paused') is True

        # busy -> idle
        assert lifecycle._can_transition('busy', 'idle') is True

        # paused -> idle
        assert lifecycle._can_transition('paused', 'idle') is True

        # any -> crashed/stopped
        assert lifecycle._can_transition('idle', 'crashed') is True
        assert lifecycle._can_transition('busy', 'stopped') is True

    def test_invalid_transitions(self, lifecycle):
        """Test invalid state transitions"""
        # Cannot go from idle to idle
        assert lifecycle._can_transition('idle', 'idle') is False

        # Cannot go from paused to busy
        assert lifecycle._can_transition('paused', 'busy') is False

    def test_is_terminal(self):
        """Test terminal state detection"""
        assert WorkerLifecycle.is_terminal('stopped') is True
        assert WorkerLifecycle.is_terminal('crashed') is True
        assert WorkerLifecycle.is_terminal('idle') is False
        assert WorkerLifecycle.is_terminal('busy') is False


class TestStaleWorkers:
    """Test stale worker detection"""

    def test_get_stale_workers_none(self, lifecycle, worker_id):
        """Test no stale workers when all recent"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.heartbeat(worker_id)

        stale = lifecycle.get_stale_workers(timeout_seconds=60)
        assert len(stale) == 0

    def test_terminal_workers_not_stale(self, lifecycle, worker_id):
        """Test terminal workers not reported as stale"""
        lifecycle.create_worker(worker_id, 'executor')
        lifecycle.shutdown_worker(worker_id)

        stale = lifecycle.get_stale_workers(timeout_seconds=0)
        assert len(stale) == 0
