"""Event bus for worker and task events."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class EventType(Enum):
    WORKER_SPAWNED = "worker_spawned"
    WORKER_TERMINATED = "worker_terminated"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    HEARTBEAT = "heartbeat"
    MERGE_CONFLICT = "merge_conflict"
    RESOURCE_LIMIT = "resource_limit"


@dataclass
class Event:
    event_type: EventType
    timestamp: datetime
    worker_id: Optional[str] = None
    task_id: Optional[str] = None
    run_id: Optional[str] = None
    workstream_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class EventBus:
    """Centralized event logging and routing."""
    
    def emit(self, event: Event) -> None:
        """Persist event to database and notify listeners."""
        from core.state.db import get_connection
        
        conn = get_connection()
        try:
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
                json.dumps(event.payload) if event.payload else None
            ))
            conn.commit()
        finally:
            conn.close()
    
    def query(
        self,
        event_type: Optional[EventType] = None,
        run_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Query events from database."""
        from core.state.db import get_connection
        
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
            
            if since:
                sql += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                payload = json.loads(row[7]) if row[7] else None
                events.append(Event(
                    event_type=EventType(row[1]),
                    worker_id=row[2],
                    task_id=row[3],
                    run_id=row[4],
                    workstream_id=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    payload=payload
                ))
            
            return events
        finally:
            conn.close()
