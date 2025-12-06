"""Database-backed event bus with simple pub/sub hooks.

DOC_ID: DOC-CORE-EVENTS-EVENT-BUS-847
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from core.state.db import get_connection


class EventType(Enum):
    """Common event types shared across phases."""

    # Worker events
    WORKER_SPAWNED = "worker_spawned"
    WORKER_TERMINATED = "worker_terminated"

    # Task events
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Job/Workstream events
    JOB_CREATED = "job_created"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    JOB_PAUSED = "job_paused"
    JOB_RESUMED = "job_resumed"
    JOB_CANCELLED = "job_cancelled"

    # Tool invocation events
    TOOL_INVOKED = "tool_invoked"
    TOOL_SUCCEEDED = "tool_succeeded"
    TOOL_FAILED = "tool_failed"
    TOOL_TIMEOUT = "tool_timeout"

    # File lifecycle events
    FILE_DISCOVERED = "file_discovered"
    FILE_CLASSIFIED = "file_classified"
    FILE_STATE_CHANGED = "file_state_changed"
    FILE_PROCESSING = "file_processing"
    FILE_COMMITTED = "file_committed"
    FILE_QUARANTINED = "file_quarantined"

    # Error events
    ERROR_RAISED = "error_raised"
    ERROR_RESOLVED = "error_resolved"

    # Circuit breaker events
    CIRCUIT_OPENED = "circuit_opened"
    CIRCUIT_CLOSED = "circuit_closed"
    CIRCUIT_HALF_OPEN = "circuit_half_open"

    # Queue events
    QUEUE_DEPTH_CHANGED = "queue_depth_changed"

    # System events
    HEARTBEAT = "heartbeat"
    MERGE_CONFLICT = "merge_conflict"
    RESOURCE_LIMIT = "resource_limit"
    ROUTING_COMPLETE = "routing_complete"
    FIX_APPLIED = "fix_applied"


class EventSeverity(Enum):
    """Severity levels for events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Event:
    """Unified event model for pipeline telemetry."""

    event_type: Union[EventType, str]
    timestamp: datetime
    severity: EventSeverity = EventSeverity.INFO
    message: str = ""

    # Correlation IDs
    run_id: Optional[str] = None
    workstream_id: Optional[str] = None
    job_id: Optional[str] = None
    file_id: Optional[str] = None
    tool_id: Optional[str] = None
    worker_id: Optional[str] = None
    task_id: Optional[str] = None

    # Structured payload
    payload: Optional[Dict[str, Any]] = None


Subscriber = Callable[[Event], None]


class EventBus:
    """Central event router backed by SQLite run_events."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._subscribers: Dict[str, List[tuple[str, Subscriber]]] = {}
        self._subscription_counter = 0

    def emit(
        self,
        event: Union[Event, EventType, str],
        payload: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> str:
        """Emit an event, persist to DB, and notify subscribers."""
        evt = self._coerce_event(event, payload=payload, **metadata)
        self._persist(evt)
        self._dispatch(evt)
        return evt.run_id or ""

    def subscribe(self, event_type: Union[EventType, str], handler: Subscriber) -> str:
        """Subscribe a handler to an event type."""
        self._subscription_counter += 1
        sub_id = f"sub-{self._subscription_counter}"
        key = self._event_type_value(event_type)
        self._subscribers.setdefault(key, []).append((sub_id, handler))
        return sub_id

    def unsubscribe(self, subscription_id: str) -> None:
        """Remove a previously registered subscription."""
        for handlers in self._subscribers.values():
            for idx, (sid, _) in enumerate(handlers):
                if sid == subscription_id:
                    handlers.pop(idx)
                    return

    def query(
        self,
        event_type: Optional[Union[EventType, str]] = None,
        run_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """Query events from the run_events table."""
        etype_value = self._event_type_value(event_type) if event_type else None
        conn = get_connection(str(self.db_path)) if self.db_path else get_connection()
        params: List[Any] = []
        sql = "SELECT event_id, run_id, timestamp, event_type, data FROM run_events WHERE 1=1"

        if etype_value:
            sql += " AND event_type = ?"
            params.append(etype_value)

        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        events: List[Event] = []
        for row in rows:
            data = json.loads(row[4]) if row[4] else {}
            events.append(self._row_to_event(row[3], row[2], row[1], data))
        conn.close()
        return events

    def _coerce_event(
        self,
        event: Union[Event, EventType, str],
        payload: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> Event:
        if isinstance(event, Event):
            return event

        event_type_value: Union[EventType, str] = event
        timestamp = metadata.pop("timestamp", None) or datetime.now(timezone.utc)
        run_id = metadata.pop("run_id", None)
        payload_data = payload or metadata.pop("payload", None) or {}
        severity = metadata.pop("severity", EventSeverity.INFO)
        message = metadata.pop("message", "")

        return Event(
            event_type=event_type_value,
            timestamp=timestamp,
            run_id=run_id,
            severity=(
                severity if isinstance(severity, EventSeverity) else EventSeverity.INFO
            ),
            message=message,
            payload=payload_data if payload_data else None,
            **metadata,
        )

    def _persist(self, event: Event) -> None:
        event_type_value = self._event_type_value(event.event_type)
        ts = event.timestamp or datetime.now(timezone.utc)
        payload = event.payload or {}

        # Preserve structured fields in payload for easy querying.
        structured = {
            "severity": (
                event.severity.value if event.severity else EventSeverity.INFO.value
            ),
            "message": event.message,
            "workstream_id": event.workstream_id,
            "job_id": event.job_id,
            "file_id": event.file_id,
            "tool_id": event.tool_id,
            "worker_id": event.worker_id,
            "task_id": event.task_id,
        }
        payload = {**structured, **payload}
        data_json = json.dumps(payload) if payload else None

        conn = get_connection(str(self.db_path)) if self.db_path else get_connection()
        run_id = event.run_id or "UNKNOWN"
        with conn:
            self._ensure_run_record(conn, run_id)
            conn.execute(
                """
                INSERT INTO run_events (event_id, run_id, timestamp, event_type, data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    uuid.uuid4().hex,
                    run_id,
                    ts.isoformat(),
                    event_type_value,
                    data_json,
                ),
            )
        conn.close()

    def _ensure_run_record(self, conn, run_id: str) -> None:
        """Guarantee a run row exists so foreign keys succeed."""
        cursor = conn.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,))
        if cursor.fetchone():
            return

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO runs (
                run_id, project_id, phase_id, workstream_id,
                execution_request_id, created_at, started_at, ended_at,
                state, exit_code, error_message, metadata
            )
            VALUES (?, ?, ?, NULL, NULL, ?, NULL, NULL, 'pending', NULL, NULL, ?)
            """,
            (
                run_id,
                "unknown",
                "unknown",
                now,
                json.dumps({"auto_created": "event_bus"}),
            ),
        )

    def _dispatch(self, event: Event) -> None:
        key = self._event_type_value(event.event_type)
        for etype in (key, "*"):
            for _, handler in self._subscribers.get(etype, []):
                try:
                    handler(event)
                except Exception:
                    # Subscriber failures are isolated from the bus.
                    continue

    def _row_to_event(
        self,
        event_type_value: str,
        timestamp: str,
        run_id: str,
        payload: Dict[str, Any],
    ) -> Event:
        try:
            event_type: Union[EventType, str] = EventType(event_type_value)
        except ValueError:
            event_type = event_type_value

        severity_value = payload.get("severity", EventSeverity.INFO.value)
        severity = (
            EventSeverity(severity_value)
            if severity_value in EventSeverity._value2member_map_
            else EventSeverity.INFO
        )

        return Event(
            event_type=event_type,
            timestamp=datetime.fromisoformat(timestamp),
            run_id=run_id,
            workstream_id=payload.get("workstream_id"),
            job_id=payload.get("job_id"),
            file_id=payload.get("file_id"),
            tool_id=payload.get("tool_id"),
            worker_id=payload.get("worker_id"),
            task_id=payload.get("task_id"),
            severity=severity,
            message=payload.get("message", ""),
            payload=payload or None,
        )

    @staticmethod
    def _event_type_value(event_type: Union[EventType, str, None]) -> str:
        if event_type is None:
            return ""
        return event_type.value if isinstance(event_type, Enum) else str(event_type)
