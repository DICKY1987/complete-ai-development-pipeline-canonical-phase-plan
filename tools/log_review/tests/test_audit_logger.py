"""Unit tests for AuditLogger and PatchLedger."""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '..')

from audit_logger import AuditLogger, EventFilters, PatchLedger, PatchArtifact


class TestAuditLogger:
    """Test AuditLogger functionality."""

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        """Create temporary log file for testing."""
        log_file = tmp_path / "test-audit.jsonl"
        return str(log_file)

    def test_log_event(self, temp_log_file):
        """Events are logged correctly."""
        audit = AuditLogger(log_path=temp_log_file)
        audit.log_event("task_received", task_id="task-001", data={"priority": "high"})
        
        # Read log file
        with open(temp_log_file) as f:
            log_line = f.read().strip()
            log_data = json.loads(log_line)
        
        assert log_data["event_type"] == "task_received"
        assert log_data["task_id"] == "task-001"
        assert log_data["data"]["priority"] == "high"
        assert "timestamp" in log_data

    def test_multiple_events(self, temp_log_file):
        """Multiple events are appended correctly."""
        audit = AuditLogger(log_path=temp_log_file)
        
        audit.log_event("task_received", task_id="task-001")
        audit.log_event("process_started", task_id="task-001")
        audit.log_event("completed", task_id="task-001")
        
        with open(temp_log_file) as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        
        events = [json.loads(line) for line in lines]
        assert events[0]["event_type"] == "task_received"
        assert events[1]["event_type"] == "process_started"
        assert events[2]["event_type"] == "completed"

    def test_query_all_events(self, temp_log_file):
        """Query without filters returns all events."""
        audit = AuditLogger(log_path=temp_log_file)
        
        audit.log_event("task_received", task_id="task-001")
        audit.log_event("task_received", task_id="task-002")
        audit.log_event("completed", task_id="task-001")
        
        events = audit.query_events()
        assert len(events) == 3

    def test_query_by_task_id(self, temp_log_file):
        """Query filters by task_id correctly."""
        audit = AuditLogger(log_path=temp_log_file)
        
        audit.log_event("task_received", task_id="task-001")
        audit.log_event("task_received", task_id="task-002")
        audit.log_event("completed", task_id="task-001")
        
        filters = EventFilters(task_id="task-001")
        events = audit.query_events(filters)
        
        assert len(events) == 2
        assert all(e.task_id == "task-001" for e in events)

    def test_query_by_event_type(self, temp_log_file):
        """Query filters by event_type correctly."""
        audit = AuditLogger(log_path=temp_log_file)
        
        audit.log_event("task_received", task_id="task-001")
        audit.log_event("process_started", task_id="task-001")
        audit.log_event("completed", task_id="task-001")
        
        filters = EventFilters(event_type="completed")
        events = audit.query_events(filters)
        
        assert len(events) == 1
        assert events[0].event_type == "completed"

    def test_query_with_limit(self, temp_log_file):
        """Query respects limit parameter."""
        audit = AuditLogger(log_path=temp_log_file)
        
        for i in range(10):
            audit.log_event("task_received", task_id=f"task-{i:03d}")
        
        filters = EventFilters(limit=5)
        events = audit.query_events(filters)
        
        assert len(events) == 5

    def test_unknown_event_type_warning(self, temp_log_file):
        """Unknown event types are logged with warning."""
        audit = AuditLogger(log_path=temp_log_file)
        audit.log_event("custom_event", task_id="task-001", data={"test": "value"})
        
        with open(temp_log_file) as f:
            log_data = json.loads(f.read().strip())
        
        assert log_data["event_type"] == "custom_event"
        assert "_warning" in log_data["data"]
        assert "Unknown event type" in log_data["data"]["_warning"]

    def test_empty_log_file(self, temp_log_file):
        """Querying non-existent log file returns empty list."""
        audit = AuditLogger(log_path=temp_log_file)
        events = audit.query_events()
        assert events == []


class TestPatchLedger:
    """Test PatchLedger functionality."""

    @pytest.fixture
    def temp_ledger_dir(self, tmp_path):
        """Create temporary ledger directory."""
        return tmp_path / "test-ledger"

    def test_store_patch(self, temp_ledger_dir):
        """Patches can be stored in ledger."""
        ledger = PatchLedger(ledger_path=str(temp_ledger_dir))
        
        patch = PatchArtifact(
            patch_id="patch-001",
            patch_file=Path("test.patch"),
            diff_hash="abc123",
            files_modified=["main.py", "utils.py"],
            line_count=42,
            created_at="2025-12-08T22:00:00Z",
            ws_id="ws-001",
            run_id="run-001"
        )
        
        ledger.store_patch(patch)
        
        # Verify metadata file was created
        metadata_file = temp_ledger_dir / "metadata.jsonl"
        assert metadata_file.exists()
        
        with open(metadata_file) as f:
            stored_data = json.loads(f.read().strip())
        
        assert stored_data["patch_id"] == "patch-001"
        assert stored_data["diff_hash"] == "abc123"

    def test_get_patch(self, temp_ledger_dir):
        """Patches can be retrieved by ID."""
        ledger = PatchLedger(ledger_path=str(temp_ledger_dir))
        
        patch = PatchArtifact(
            patch_id="patch-001",
            patch_file=Path("test.patch"),
            diff_hash="abc123",
            files_modified=["main.py"],
            line_count=10,
            created_at="2025-12-08T22:00:00Z"
        )
        
        ledger.store_patch(patch)
        retrieved = ledger.get_patch("patch-001")
        
        assert retrieved is not None
        assert retrieved.patch_id == "patch-001"
        assert retrieved.diff_hash == "abc123"
        assert retrieved.files_modified == ["main.py"]

    def test_get_nonexistent_patch(self, temp_ledger_dir):
        """Getting non-existent patch returns None."""
        ledger = PatchLedger(ledger_path=str(temp_ledger_dir))
        retrieved = ledger.get_patch("nonexistent")
        assert retrieved is None

    def test_get_history(self, temp_ledger_dir):
        """Workstream history can be retrieved."""
        ledger = PatchLedger(ledger_path=str(temp_ledger_dir))
        
        # Store patches for different workstreams
        for i in range(3):
            patch = PatchArtifact(
                patch_id=f"patch-ws1-{i}",
                patch_file=Path(f"test{i}.patch"),
                diff_hash=f"hash{i}",
                files_modified=["file.py"],
                line_count=10,
                created_at=f"2025-12-08T22:0{i}:00Z",
                ws_id="ws-001"
            )
            ledger.store_patch(patch)
        
        # Store patch for different workstream
        patch = PatchArtifact(
            patch_id="patch-ws2-0",
            patch_file=Path("test.patch"),
            diff_hash="hash_other",
            files_modified=["file.py"],
            line_count=10,
            created_at="2025-12-08T22:00:00Z",
            ws_id="ws-002"
        )
        ledger.store_patch(patch)
        
        # Get history for ws-001
        history = ledger.get_history("ws-001")
        
        assert len(history) == 3
        assert all(p.ws_id == "ws-001" for p in history)
        # Should be sorted by created_at
        assert history[0].created_at <= history[1].created_at <= history[2].created_at


class TestEventFilters:
    """Test EventFilters dataclass."""

    def test_default_filters(self):
        """Default filters are all None."""
        filters = EventFilters()
        assert filters.task_id is None
        assert filters.event_type is None
        assert filters.since is None
        assert filters.until is None
        assert filters.limit is None

    def test_custom_filters(self):
        """Custom filters can be set."""
        filters = EventFilters(
            task_id="task-001",
            event_type="completed",
            limit=10
        )
        assert filters.task_id == "task-001"
        assert filters.event_type == "completed"
        assert filters.limit == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
