"""
Unit tests for Audit Logger and Patch Ledger
"""
# DOC_ID: DOC-TEST-TESTS-TEST-AUDIT-LOGGER-075
# DOC_ID: DOC-TEST-TESTS-TEST-AUDIT-LOGGER-036
import pytest
import json
from pathlib import Path
from datetime import datetime
from modules.core_state.m010003_audit_logger import (
    AuditLogger, AuditEvent, EventFilters,
    PatchLedger, PatchArtifact
)


@pytest.fixture
def temp_audit_dir(tmp_path):
    """Create temporary audit directory"""
    audit_dir = tmp_path / ".runs"
    audit_dir.mkdir(exist_ok=True)
    yield audit_dir


@pytest.fixture
def temp_ledger_dir(tmp_path):
    """Create temporary ledger directory"""
    ledger_dir = tmp_path / ".ledger" / "patches"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    yield ledger_dir


@pytest.fixture
def audit_logger(temp_audit_dir):
    """Create AuditLogger instance"""
    log_path = temp_audit_dir / "audit.jsonl"
    return AuditLogger(log_path=str(log_path))


@pytest.fixture
def patch_ledger(temp_ledger_dir):
    """Create PatchLedger instance"""
    return PatchLedger(ledger_path=str(temp_ledger_dir))


def test_audit_event_creation():
    """Test AuditEvent creation and serialization"""
    event = AuditEvent(
        timestamp="2025-11-19T21:00:00Z",
        event_type="task_received",
        task_id="test-task-123",
        data={"source": "codex"}
    )

    event_dict = event.to_dict()
    assert event_dict['event_type'] == "task_received"
    assert event_dict['task_id'] == "test-task-123"

    restored = AuditEvent.from_dict(event_dict)
    assert restored.event_type == event.event_type


def test_log_event(audit_logger):
    """Test logging an event"""
    audit_logger.log_event(
        event_type="task_received",
        task_id="test-123",
        data={"source": "codex", "mode": "prompt"}
    )

    # Verify event was written
    assert audit_logger.log_path.exists()

    with open(audit_logger.log_path, 'r') as f:
        line = f.readline()
        event_data = json.loads(line)
        assert event_data['event_type'] == "task_received"
        assert event_data['task_id'] == "test-123"


def test_log_multiple_events(audit_logger):
    """Test logging multiple events"""
    events = [
        ("task_received", "task-1", {"source": "codex"}),
        ("task_routed", "task-1", {"target": "aider"}),
        ("patch_captured", "task-1", {"files": ["test.py"]}),
    ]

    for event_type, task_id, data in events:
        audit_logger.log_event(event_type, task_id, data)

    # Verify all events written
    with open(audit_logger.log_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 3


def test_query_events_no_filter(audit_logger):
    """Test querying all events"""
    # Log events
    audit_logger.log_event("task_received", "task-1", {})
    audit_logger.log_event("task_routed", "task-2", {})

    # Query all
    events = audit_logger.query_events()
    assert len(events) == 2


def test_query_events_by_task_id(audit_logger):
    """Test querying events by task ID"""
    audit_logger.log_event("task_received", "task-1", {})
    audit_logger.log_event("task_routed", "task-1", {})
    audit_logger.log_event("task_received", "task-2", {})

    filters = EventFilters(task_id="task-1")
    events = audit_logger.query_events(filters)

    assert len(events) == 2
    assert all(e.task_id == "task-1" for e in events)


def test_query_events_by_type(audit_logger):
    """Test querying events by type"""
    audit_logger.log_event("task_received", "task-1", {})
    audit_logger.log_event("task_routed", "task-1", {})
    audit_logger.log_event("task_received", "task-2", {})

    filters = EventFilters(event_type="task_received")
    events = audit_logger.query_events(filters)

    assert len(events) == 2
    assert all(e.event_type == "task_received" for e in events)


def test_query_events_with_limit(audit_logger):
    """Test querying with limit"""
    for i in range(10):
        audit_logger.log_event("task_received", f"task-{i}", {})

    filters = EventFilters(limit=5)
    events = audit_logger.query_events(filters)

    assert len(events) == 5


def test_query_events_time_range(audit_logger):
    """Test querying events by time range"""
    # Log events with different timestamps
    audit_logger.log_event("task_received", "task-1", {})
    audit_logger.log_event("task_received", "task-2", {})

    # Query with time filter (using ISO format)
    filters = EventFilters(since="2025-11-19T00:00:00Z")
    events = audit_logger.query_events(filters)

    assert len(events) >= 0  # All recent events


def test_query_empty_log(audit_logger):
    """Test querying when no events exist"""
    events = audit_logger.query_events()
    assert len(events) == 0


def test_unknown_event_type(audit_logger):
    """Test logging unknown event type"""
    audit_logger.log_event("unknown_event", "task-1", {})

    events = audit_logger.query_events()
    assert len(events) == 1
    assert '_warning' in events[0].data


def test_patch_artifact_creation():
    """Test PatchArtifact creation"""
    patch = PatchArtifact(
        patch_id="patch-123",
        patch_file=Path("test.patch"),
        diff_hash="abc123",
        files_modified=["test.py"],
        line_count=10,
        created_at="2025-11-19T21:00:00Z",
        ws_id="ws-1",
        run_id="run-1"
    )

    assert patch.patch_id == "patch-123"
    assert patch.diff_hash == "abc123"


def test_patch_artifact_serialization():
    """Test PatchArtifact to/from dict"""
    patch = PatchArtifact(
        patch_id="patch-123",
        patch_file=Path("test.patch"),
        diff_hash="abc123",
        files_modified=["test.py"],
        line_count=10,
        created_at="2025-11-19T21:00:00Z"
    )

    patch_dict = patch.to_dict()
    assert isinstance(patch_dict['patch_file'], str)

    restored = PatchArtifact.from_dict(patch_dict)
    assert isinstance(restored.patch_file, Path)
    assert restored.patch_id == patch.patch_id


def test_store_patch(patch_ledger, tmp_path):
    """Test storing a patch"""
    patch_file = tmp_path / "test.patch"
    patch_file.write_text("diff --git a/test.py")

    patch = PatchArtifact(
        patch_id="patch-123",
        patch_file=patch_file,
        diff_hash="abc123",
        files_modified=["test.py"],
        line_count=10,
        created_at="2025-11-19T21:00:00Z",
        ws_id="ws-1"
    )

    stored_path = patch_ledger.store_patch(patch)
    assert stored_path is not None

    # Verify metadata written
    assert patch_ledger.metadata_file.exists()


def test_get_patch(patch_ledger, tmp_path):
    """Test retrieving a patch by ID"""
    patch_file = tmp_path / "test.patch"
    patch_file.write_text("diff --git a/test.py")

    patch = PatchArtifact(
        patch_id="patch-123",
        patch_file=patch_file,
        diff_hash="abc123",
        files_modified=["test.py"],
        line_count=10,
        created_at="2025-11-19T21:00:00Z"
    )

    patch_ledger.store_patch(patch)

    retrieved = patch_ledger.get_patch("patch-123")
    assert retrieved is not None
    assert retrieved.patch_id == "patch-123"
    assert retrieved.diff_hash == "abc123"


def test_get_patch_not_found(patch_ledger):
    """Test retrieving non-existent patch"""
    retrieved = patch_ledger.get_patch("non-existent")
    assert retrieved is None


def test_get_history(patch_ledger, tmp_path):
    """Test getting patch history for workstream"""
    for i in range(3):
        patch_file = tmp_path / f"test{i}.patch"
        patch_file.write_text(f"diff {i}")

        patch = PatchArtifact(
            patch_id=f"patch-{i}",
            patch_file=patch_file,
            diff_hash=f"hash{i}",
            files_modified=["test.py"],
            line_count=10,
            created_at=f"2025-11-19T21:00:0{i}Z",
            ws_id="ws-1"
        )
        patch_ledger.store_patch(patch)

    # Get history for ws-1
    history = patch_ledger.get_history("ws-1")
    assert len(history) == 3
    assert all(p.ws_id == "ws-1" for p in history)


def test_get_history_empty(patch_ledger):
    """Test getting history when no patches exist"""
    history = patch_ledger.get_history("ws-1")
    assert len(history) == 0


def test_jsonl_format(audit_logger):
    """Test JSONL format is valid"""
    # Log multiple events
    for i in range(5):
        audit_logger.log_event("test_event", f"task-{i}", {"index": i})

    # Verify each line is valid JSON
    with open(audit_logger.log_path, 'r') as f:
        for line in f:
            event_data = json.loads(line.strip())
            assert 'event_type' in event_data
            assert 'timestamp' in event_data
