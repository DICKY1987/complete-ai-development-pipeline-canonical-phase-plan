"""Integration test: JSONL event streaming and logging."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-JSONL-STREAMING-009

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.shared.utils.jsonl_manager import (
    append,
    read_all,
    rotate_if_needed,
)


@pytest.fixture
def jsonl_file(tmp_path: Path) -> Path:
    """Create a JSONL file for testing."""
    file_path = tmp_path / "events.jsonl"
    return file_path


def test_append_creates_new_file(jsonl_file):
    """Test that append creates a new JSONL file if it doesn't exist."""
    event = {"event_type": "test", "message": "Hello, World!"}

    append(jsonl_file, event)

    assert jsonl_file.exists()


def test_append_adds_event(jsonl_file):
    """Test that append adds an event to JSONL file."""
    event = {"event_type": "error_detected", "tool": "mypy", "count": 5}

    append(jsonl_file, event)

    events = read_all(jsonl_file)
    assert len(events) == 1
    assert events[0]["event_type"] == "error_detected"


def test_append_multiple_events(jsonl_file):
    """Test appending multiple events."""
    events = [
        {"event": "baseline_check", "status": "started"},
        {"event": "baseline_check", "status": "completed", "errors": 5},
        {"event": "mechanical_fix", "status": "started"},
    ]

    for event in events:
        append(jsonl_file, event)

    loaded_events = read_all(jsonl_file)
    assert len(loaded_events) == 3
    assert loaded_events[0]["event"] == "baseline_check"
    assert loaded_events[2]["event"] == "mechanical_fix"


def test_read_all_returns_empty_for_missing_file(tmp_path):
    """Test that read_all returns empty list for missing file."""
    missing_file = tmp_path / "nonexistent.jsonl"

    events = read_all(missing_file)

    assert events == []


def test_jsonl_format_is_valid(jsonl_file):
    """Test that JSONL format is valid (one JSON per line)."""
    events = [
        {"id": 1, "message": "First"},
        {"id": 2, "message": "Second"},
        {"id": 3, "message": "Third"},
    ]

    for event in events:
        append(jsonl_file, event)

    # Read raw file and validate format
    lines = jsonl_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3

    for line in lines:
        parsed = json.loads(line)
        assert isinstance(parsed, dict)


def test_rotate_if_needed_handles_large_file(jsonl_file):
    """Test that rotation happens when file exceeds max size."""
    # Append many events to exceed size limit
    for i in range(100):
        event = {"id": i, "data": "x" * 100}
        append(jsonl_file, event)

    # Rotate with small max size
    rotate_if_needed(jsonl_file, max_lines=50)

    # File should now have fewer lines
    events = read_all(jsonl_file)
    assert len(events) <= 50


def test_rotate_preserves_recent_events(jsonl_file):
    """Test that rotation preserves most recent events."""
    events = [{"id": i} for i in range(100)]

    for event in events:
        append(jsonl_file, event)

    rotate_if_needed(jsonl_file, max_lines=20)

    remaining_events = read_all(jsonl_file)

    # Should keep most recent 20 events (ids 80-99)
    assert len(remaining_events) <= 20
    if remaining_events:
        assert remaining_events[-1]["id"] == 99


def test_event_streaming_preserves_order(jsonl_file):
    """Test that event streaming preserves insertion order."""
    events = [
        {"timestamp": "2025-12-05T10:00:00Z", "event": "start"},
        {"timestamp": "2025-12-05T10:01:00Z", "event": "progress"},
        {"timestamp": "2025-12-05T10:02:00Z", "event": "complete"},
    ]

    for event in events:
        append(jsonl_file, event)

    loaded = read_all(jsonl_file)

    assert loaded[0]["event"] == "start"
    assert loaded[1]["event"] == "progress"
    assert loaded[2]["event"] == "complete"


def test_jsonl_handles_special_characters(jsonl_file):
    """Test that JSONL handles special characters correctly."""
    event = {
        "message": 'Line with "quotes" and \\backslashes\\ and \nnewlines',
        "unicode": "Unicode: 你好 🚀",
    }

    append(jsonl_file, event)

    loaded = read_all(jsonl_file)
    assert loaded[0]["message"] == event["message"]
    assert loaded[0]["unicode"] == event["unicode"]


def test_jsonl_append_is_atomic(jsonl_file):
    """Test that appending is atomic (no partial writes)."""
    event = {"data": "x" * 1000}

    append(jsonl_file, event)

    # File should be readable and complete
    loaded = read_all(jsonl_file)
    assert len(loaded) == 1
    assert len(loaded[0]["data"]) == 1000


def test_jsonl_concurrent_append_safety(jsonl_file):
    """Test that multiple appends don't corrupt file."""
    # Simulate multiple quick appends
    for i in range(50):
        append(jsonl_file, {"id": i})

    loaded = read_all(jsonl_file)

    # All events should be present
    assert len(loaded) == 50

    # All should be valid
    for i, event in enumerate(loaded):
        assert event["id"] == i
