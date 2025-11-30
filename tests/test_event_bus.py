"""Tests for event bus."""

import pytest
from datetime import datetime, timezone
from modules.core_engine.m010001_event_bus import Event, EventType, EventBus


def test_event_creation():
    """Test event instance creation."""
DOC_ID: DOC-TEST-TESTS-TEST-EVENT-BUS-081
DOC_ID: DOC-TEST-TESTS-TEST-EVENT-BUS-042
    now = datetime.now(timezone.utc)
    
    event = Event(
        event_type=EventType.WORKER_SPAWNED,
        timestamp=now,
        worker_id="worker-1",
        payload={"adapter_type": "aider"}
    )
    
    assert event.event_type == EventType.WORKER_SPAWNED
    assert event.worker_id == "worker-1"
    assert event.payload["adapter_type"] == "aider"


def test_event_bus_emit(temp_db):
    """Test emitting events to database."""
    bus = EventBus()
    
    event = Event(
        event_type=EventType.TASK_STARTED,
        timestamp=datetime.now(timezone.utc),
        worker_id="worker-1",
        task_id="task-1",
        run_id="run-1",
        workstream_id="ws-test",
        payload={"status": "starting"}
    )
    
    # Should not raise
    bus.emit(event)


def test_event_bus_query(temp_db):
    """Test querying events from database."""
    bus = EventBus()
    
    # Emit some test events
    for i in range(3):
        event = Event(
            event_type=EventType.HEARTBEAT,
            timestamp=datetime.now(timezone.utc),
            worker_id=f"worker-{i}",
            run_id="run-test"
        )
        bus.emit(event)
    
    # Query all events for run
    events = bus.query(run_id="run-test", limit=10)
    assert len(events) >= 3
    
    # Query by event type
    heartbeats = bus.query(event_type=EventType.HEARTBEAT, limit=10)
    assert len(heartbeats) >= 3
    assert all(e.event_type == EventType.HEARTBEAT for e in heartbeats)
