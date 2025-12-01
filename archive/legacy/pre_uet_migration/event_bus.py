"""Event bus for worker and task events."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class EventType(Enum):
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


class EventSeverity(Enum):
    """Severity levels for events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Event:
    """Unified event model for all pipeline events.
    
    Correlation IDs:
        - run_id: Links event to a specific run
        - workstream_id: Links event to a workstream
        - job_id: Links event to a job (optional, for job-based execution)
        - file_id: Links event to a specific file
        - tool_id: Links event to a specific tool/adapter
    """
    event_type: EventType
    timestamp: datetime
    severity: EventSeverity = EventSeverity.INFO
    message: str = ""
    
    # Correlation IDs
    run_id: Optional[str] = None
    workstream_id: Optional[str] = None
    job_id: Optional[str] = None
    file_id: Optional[str] = None
    tool_id: Optional[str] = None
    
    # Legacy compatibility
    worker_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Structured payload
    payload: Optional[Dict[str, Any]] = None


class EventBus:
    """Centralized event logging and routing."""
    
    def emit(self, event: Event) -> None:
        """Persist event to database and notify listeners."""
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.db import get_connection
        
        conn = get_connection()
        try:
            # Store in uet_events table (extended schema)
            conn.execute("""
                INSERT INTO uet_events 
                (event_type, worker_id, task_id, run_id, workstream_id, timestamp, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_type.value,
                event.worker_id,
                event.task_id,
                event.run_id,
                event.workstream_id,
                event.timestamp.isoformat(),
                json.dumps({
                    "severity": event.severity.value,
                    "message": event.message,
                    "job_id": event.job_id,
                    "file_id": event.file_id,
                    "tool_id": event.tool_id,
                    **(event.payload or {})
                }) if event.payload or event.severity or event.message else None
            ))
            conn.commit()
        finally:
            conn.close()
    
    def query(
        self,
        event_type: Optional[EventType] = None,
        run_id: Optional[str] = None,
        workstream_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        file_id: Optional[str] = None,
        severity: Optional[EventSeverity] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Query events from database with flexible filters."""
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.db import get_connection
        
        conn = get_connection()
        try:
            sql = "SELECT * FROM uet_events WHERE 1=1"
            params = []
            
            if event_type:
                sql += " AND event_type = ?"
                params.append(event_type.value)
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
                
            if workstream_id:
                sql += " AND workstream_id = ?"
                params.append(workstream_id)
            
            if tool_id:
                sql += " AND json_extract(payload_json, '$.tool_id') = ?"
                params.append(tool_id)
                
            if file_id:
                sql += " AND json_extract(payload_json, '$.file_id') = ?"
                params.append(file_id)
                
            if severity:
                sql += " AND json_extract(payload_json, '$.severity') = ?"
                params.append(severity.value)
            
            if since:
                sql += " AND timestamp >= ?"
                params.append(since.isoformat())
                
            if until:
                sql += " AND timestamp <= ?"
                params.append(until.isoformat())
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                payload_data = json.loads(row[7]) if row[7] else {}
                
                events.append(Event(
                    event_type=EventType(row[1]),
                    worker_id=row[2],
                    task_id=row[3],
                    run_id=row[4],
                    workstream_id=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    severity=EventSeverity(payload_data.get("severity", "info")) if payload_data.get("severity") else EventSeverity.INFO,
                    message=payload_data.get("message", ""),
                    job_id=payload_data.get("job_id"),
                    file_id=payload_data.get("file_id"),
                    tool_id=payload_data.get("tool_id"),
                    payload=payload_data
                ))
            
            return events
        finally:
            conn.close()
    
    def export_to_jsonl(self, output_path: str, **query_kwargs) -> int:
        """Export events to JSONL file.
        
        Args:
            output_path: Path to output JSONL file
            **query_kwargs: Arguments to pass to query()
            
        Returns:
            Number of events exported
        """
        events = self.query(**query_kwargs)
        
        with open(output_path, 'w') as f:
            for event in events:
                event_dict = {
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "severity": event.severity.value,
                    "message": event.message,
                    "run_id": event.run_id,
                    "workstream_id": event.workstream_id,
                    "job_id": event.job_id,
                    "file_id": event.file_id,
                    "tool_id": event.tool_id,
                    "worker_id": event.worker_id,
                    "task_id": event.task_id,
                    "payload": event.payload
                }
                f.write(json.dumps(event_dict) + "\n")
        
        return len(events)
