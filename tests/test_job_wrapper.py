"""
Unit tests for JobWrapper (Phase 4B)
Tests job metadata, priorities, dependencies, and state transitions.
"""

from datetime import datetime, timedelta

# DOC_ID: DOC-TEST-TESTS-TEST-JOB-WRAPPER-089
# DOC_ID: DOC-TEST-TESTS-TEST-JOB-WRAPPER-050
import pytest
from engine.queue.job_wrapper import JobPriority, JobStatus, JobWrapper


def test_job_priority_ordering():
    """Test that job priorities are correctly ordered"""
    assert JobPriority.CRITICAL.value < JobPriority.HIGH.value
    assert JobPriority.HIGH.value < JobPriority.NORMAL.value
    assert JobPriority.NORMAL.value < JobPriority.LOW.value


def test_job_wrapper_defaults():
    """Test JobWrapper default values"""
    job = JobWrapper(
        job_id="test-123",
        job_data={"tool": "aider", "command": {"exe": "aider", "args": []}},
    )

    assert job.priority == JobPriority.NORMAL
    assert job.status == JobStatus.QUEUED
    assert job.depends_on == []
    assert job.retry_count == 0
    assert job.max_retries == 3
    assert job.queued_at is not None
    assert job.started_at is None
    assert job.completed_at is None
    assert job.metadata == {}


def test_job_wrapper_priority_comparison():
    """Test priority-based job comparison for queue ordering"""
    now = datetime.now()

    job_critical = JobWrapper(
        job_id="critical", job_data={}, priority=JobPriority.CRITICAL, queued_at=now
    )

    job_high = JobWrapper(
        job_id="high", job_data={}, priority=JobPriority.HIGH, queued_at=now
    )

    job_normal = JobWrapper(
        job_id="normal", job_data={}, priority=JobPriority.NORMAL, queued_at=now
    )

    # Critical < High < Normal (lower value = higher priority)
    assert job_critical < job_high
    assert job_high < job_normal
    assert job_critical < job_normal


def test_job_wrapper_time_ordering():
    """Test that jobs with same priority are ordered by queued_at"""
    earlier = datetime.now()
    later = earlier + timedelta(seconds=10)

    job_earlier = JobWrapper(
        job_id="earlier", job_data={}, priority=JobPriority.NORMAL, queued_at=earlier
    )

    job_later = JobWrapper(
        job_id="later", job_data={}, priority=JobPriority.NORMAL, queued_at=later
    )

    # Earlier queued job has higher priority
    assert job_earlier < job_later


def test_mark_running():
    """Test marking job as running"""
    job = JobWrapper(job_id="test", job_data={})
    assert job.started_at is None

    job.mark_running()

    assert job.status == JobStatus.RUNNING
    assert job.started_at is not None


def test_mark_completed():
    """Test marking job as completed"""
    job = JobWrapper(job_id="test", job_data={})
    job.mark_running()

    job.mark_completed()

    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None


def test_mark_failed():
    """Test marking job as failed"""
    job = JobWrapper(job_id="test", job_data={})
    job.mark_running()

    job.mark_failed()

    assert job.status == JobStatus.FAILED
    assert job.completed_at is not None


def test_mark_retry():
    """Test marking job for retry"""
    job = JobWrapper(job_id="test", job_data={})
    initial_count = job.retry_count

    job.mark_retry()

    assert job.status == JobStatus.RETRY
    assert job.retry_count == initial_count + 1


def test_mark_escalated():
    """Test marking job as escalated"""
    job = JobWrapper(job_id="test", job_data={})

    job.mark_escalated("codex")

    assert job.status == JobStatus.ESCALATED
    assert job.metadata["escalated_to"] == "codex"
    assert "escalated_at" in job.metadata


def test_can_retry():
    """Test retry limit checking"""
    job = JobWrapper(job_id="test", job_data={}, max_retries=3)

    assert job.can_retry() is True

    job.retry_count = 2
    assert job.can_retry() is True

    job.retry_count = 3
    assert job.can_retry() is False

    job.retry_count = 4
    assert job.can_retry() is False


def test_is_ready_no_dependencies():
    """Test job is ready when no dependencies"""
    job = JobWrapper(job_id="test", job_data={}, depends_on=[])
    completed_jobs = set()

    assert job.is_ready(completed_jobs) is True


def test_is_ready_with_dependencies():
    """Test job dependency resolution"""
    job = JobWrapper(job_id="test", job_data={}, depends_on=["job1", "job2"])

    # Not ready if dependencies incomplete
    completed_jobs = {"job1"}
    assert job.is_ready(completed_jobs) is False

    # Ready when all dependencies complete
    completed_jobs = {"job1", "job2"}
    assert job.is_ready(completed_jobs) is True

    # Extra completed jobs don't affect readiness
    completed_jobs = {"job1", "job2", "job3"}
    assert job.is_ready(completed_jobs) is True


def test_to_dict():
    """Test job serialization to dict"""
    job = JobWrapper(
        job_id="test-123",
        job_data={"tool": "aider"},
        priority=JobPriority.HIGH,
        status=JobStatus.QUEUED,
        depends_on=["dep1"],
        retry_count=1,
        max_retries=5,
        metadata={"custom": "value"},
    )

    job_dict = job.to_dict()

    assert job_dict["job_id"] == "test-123"
    assert job_dict["job_data"] == {"tool": "aider"}
    assert job_dict["priority"] == JobPriority.HIGH.value
    assert job_dict["status"] == JobStatus.QUEUED.value
    assert job_dict["depends_on"] == ["dep1"]
    assert job_dict["retry_count"] == 1
    assert job_dict["max_retries"] == 5
    assert job_dict["metadata"] == {"custom": "value"}
    assert "queued_at" in job_dict


def test_from_dict():
    """Test job deserialization from dict"""
    now = datetime.now()
    job_dict = {
        "job_id": "test-123",
        "job_data": {"tool": "aider"},
        "priority": JobPriority.HIGH.value,
        "status": JobStatus.RUNNING.value,
        "depends_on": ["dep1"],
        "retry_count": 2,
        "max_retries": 5,
        "queued_at": now.isoformat(),
        "started_at": now.isoformat(),
        "completed_at": None,
        "metadata": {"custom": "value"},
    }

    job = JobWrapper.from_dict(job_dict)

    assert job.job_id == "test-123"
    assert job.job_data == {"tool": "aider"}
    assert job.priority == JobPriority.HIGH
    assert job.status == JobStatus.RUNNING
    assert job.depends_on == ["dep1"]
    assert job.retry_count == 2
    assert job.max_retries == 5
    assert job.metadata == {"custom": "value"}


def test_json_round_trip():
    """Test JSON serialization round trip"""
    job = JobWrapper(
        job_id="test-123",
        job_data={"tool": "aider", "command": {"exe": "aider"}},
        priority=JobPriority.CRITICAL,
        depends_on=["dep1", "dep2"],
        metadata={"key": "value"},
    )

    json_str = job.to_json()
    restored_job = JobWrapper.from_json(json_str)

    assert restored_job.job_id == job.job_id
    assert restored_job.job_data == job.job_data
    assert restored_job.priority == job.priority
    assert restored_job.depends_on == job.depends_on
    assert restored_job.metadata == job.metadata
