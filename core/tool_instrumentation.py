"""Tool adapter instrumentation utilities.

This module provides helpers for tool adapters to emit metrics and events,
enabling full observability of tool invocations for the UI.
"""

import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.engine.event_bus import Event, EventBus, EventSeverity, EventType


class ToolInvocationTracker:
    """Context manager for tracking tool invocations with automatic event emission."""
    
    def __init__(
        self,
        tool_id: str,
        tool_name: str,
        action: str,
        run_id: Optional[str] = None,
        workstream_id: Optional[str] = None,
        file_id: Optional[str] = None,
        job_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.action = action
        self.run_id = run_id
        self.workstream_id = workstream_id
        self.file_id = file_id
        self.job_id = job_id
        self.event_bus = event_bus or EventBus()
        
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.success: bool = False
        self.error: Optional[Exception] = None
        self.output_size: Optional[int] = None
    
    def __enter__(self):
        """Start tracking the tool invocation."""
        self.start_time = time.time()
        
        # Emit TOOL_INVOKED event
        self.event_bus.emit(Event(
            event_type=EventType.TOOL_INVOKED,
            timestamp=datetime.now(timezone.utc),
            severity=EventSeverity.INFO,
            message=f"{self.tool_name} invoked: {self.action}",
            run_id=self.run_id,
            workstream_id=self.workstream_id,
            job_id=self.job_id,
            file_id=self.file_id,
            tool_id=self.tool_id,
            payload={
                "action": self.action,
                "tool_name": self.tool_name,
            }
        ))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish tracking and emit completion event."""
        self.end_time = time.time()
        latency = self.end_time - self.start_time if self.start_time else 0.0
        
        if exc_type is None:
            # Success
            self.success = True
            self.event_bus.emit(Event(
                event_type=EventType.TOOL_SUCCEEDED,
                timestamp=datetime.now(timezone.utc),
                severity=EventSeverity.INFO,
                message=f"{self.tool_name} succeeded: {self.action}",
                run_id=self.run_id,
                workstream_id=self.workstream_id,
                job_id=self.job_id,
                file_id=self.file_id,
                tool_id=self.tool_id,
                payload={
                    "action": self.action,
                    "latency_sec": latency,
                    "output_size_bytes": self.output_size,
                }
            ))
        else:
            # Failure
            self.success = False
            self.error = exc_val
            self.event_bus.emit(Event(
                event_type=EventType.TOOL_FAILED,
                timestamp=datetime.now(timezone.utc),
                severity=EventSeverity.ERROR,
                message=f"{self.tool_name} failed: {str(exc_val)[:200]}",
                run_id=self.run_id,
                workstream_id=self.workstream_id,
                job_id=self.job_id,
                file_id=self.file_id,
                tool_id=self.tool_id,
                payload={
                    "action": self.action,
                    "latency_sec": latency,
                    "error_type": exc_type.__name__ if exc_type else None,
                    "error_message": str(exc_val),
                }
            ))
        
        # Update tool health metrics in database
        self._update_tool_metrics(latency, self.success)
        
        # Don't suppress exceptions
        return False
    
    def set_output_size(self, size_bytes: int):
        """Record the output size from the tool invocation."""
        self.output_size = size_bytes
    
    def _update_tool_metrics(self, latency: float, success: bool):
        """Update tool health metrics in the database."""
        from core.state.db import get_connection
        
        conn = get_connection()
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Check if tool metrics record exists
            cursor = conn.execute(
                "SELECT tool_id FROM tool_health_metrics WHERE tool_id = ?",
                (self.tool_id,)
            )
            exists = cursor.fetchone() is not None
            
            if not exists:
                # Create initial record
                conn.execute("""
                    INSERT INTO tool_health_metrics
                    (tool_id, display_name, category, status, updated_at)
                    VALUES (?, ?, 'other', 'unknown', ?)
                """, (self.tool_id, self.tool_name, now))
            
            # Update metrics
            if success:
                conn.execute("""
                    UPDATE tool_health_metrics
                    SET success_count = success_count + 1,
                        last_successful_invocation = ?,
                        updated_at = ?
                    WHERE tool_id = ?
                """, (now, now, self.tool_id))
            else:
                conn.execute("""
                    UPDATE tool_health_metrics
                    SET failure_count = failure_count + 1,
                        updated_at = ?
                    WHERE tool_id = ?
                """, (now, self.tool_id))
            
            # Recalculate success rate
            cursor = conn.execute("""
                SELECT success_count, failure_count
                FROM tool_health_metrics
                WHERE tool_id = ?
            """, (self.tool_id,))
            row = cursor.fetchone()
            if row:
                total = row[0] + row[1]
                success_rate = row[0] / total if total > 0 else 0.0
                conn.execute("""
                    UPDATE tool_health_metrics
                    SET success_rate = ?
                    WHERE tool_id = ?
                """, (success_rate, self.tool_id))
            
            # Update latency metrics (simple moving average for now)
            # TODO: Implement proper percentile calculation (P50, P95, P99) using
            # a proper percentile algorithm or time-series database
            # For now, using simplified p95 approximation
            conn.execute("""
                UPDATE tool_health_metrics
                SET mean_latency = (
                    COALESCE(mean_latency * (success_count + failure_count - 1), 0) + ?
                ) / (success_count + failure_count),
                p95_latency = ?,
                updated_at = ?
                WHERE tool_id = ?
            """, (latency, latency * 1.2, now, self.tool_id))  # Simplified p95 approximation
            
            conn.commit()
        finally:
            conn.close()


@contextmanager
def track_tool_invocation(
    tool_id: str,
    tool_name: str,
    action: str,
    **correlation_ids
):
    """Context manager for tracking tool invocations.
    
    Usage:
        with track_tool_invocation("aider", "Aider", "refactor", run_id=run_id, file_id=file_id):
            result = run_aider_command()
    """
    tracker = ToolInvocationTracker(
        tool_id=tool_id,
        tool_name=tool_name,
        action=action,
        **correlation_ids
    )
    with tracker:
        yield tracker


def emit_file_state_change(
    file_id: str,
    old_state: str,
    new_state: str,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    event_bus: Optional[EventBus] = None
):
    """Emit a file state change event."""
    bus = event_bus or EventBus()
    
    bus.emit(Event(
        event_type=EventType.FILE_STATE_CHANGED,
        timestamp=datetime.now(timezone.utc),
        severity=EventSeverity.INFO,
        message=f"File state: {old_state} → {new_state}",
        run_id=run_id,
        workstream_id=workstream_id,
        file_id=file_id,
        tool_id=tool_id,
        payload={
            "old_state": old_state,
            "new_state": new_state,
        }
    ))


def emit_error_raised(
    error_id: str,
    entity_type: str,
    severity: str,
    category: str,
    human_message: str,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None,
    file_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    technical_details: Optional[str] = None,
    event_bus: Optional[EventBus] = None
):
    """Emit an error raised event."""
    bus = event_bus or EventBus()
    
    bus.emit(Event(
        event_type=EventType.ERROR_RAISED,
        timestamp=datetime.now(timezone.utc),
        severity=EventSeverity(severity) if severity in ["debug", "info", "warning", "error", "critical"] else EventSeverity.ERROR,
        message=human_message,
        run_id=run_id,
        workstream_id=workstream_id,
        file_id=file_id,
        tool_id=tool_id,
        payload={
            "error_id": error_id,
            "entity_type": entity_type,
            "category": category,
            "technical_details": technical_details,
        }
    ))


def emit_job_event(
    job_id: str,
    event_type: EventType,
    message: str,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None,
    severity: EventSeverity = EventSeverity.INFO,
    payload: Optional[Dict[str, Any]] = None,
    event_bus: Optional[EventBus] = None
):
    """Emit a job lifecycle event."""
    bus = event_bus or EventBus()
    
    bus.emit(Event(
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        severity=severity,
        message=message,
        run_id=run_id,
        workstream_id=workstream_id,
        job_id=job_id,
        payload=payload,
    ))


def update_tool_health_status(
    tool_id: str,
    status: str,
    status_reason: Optional[str] = None,
    version: Optional[str] = None,
    category: Optional[str] = None,
):
    """Update tool health status in the database.
    
    Args:
        tool_id: Tool identifier
        status: One of: healthy, degraded, unreachable, circuit_open, unknown
        status_reason: Optional reason for the status
        version: Optional tool version
        category: Optional tool category
    """
    from core.state.db import get_connection
    
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if record exists
        cursor = conn.execute(
            "SELECT tool_id FROM tool_health_metrics WHERE tool_id = ?",
            (tool_id,)
        )
        exists = cursor.fetchone() is not None
        
        if not exists:
            # Create initial record
            conn.execute("""
                INSERT INTO tool_health_metrics
                (tool_id, display_name, category, version, status, status_reason, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tool_id, tool_id, category or "other", version, status, status_reason, now))
        else:
            # Update existing record
            updates = ["status = ?", "status_reason = ?", "updated_at = ?"]
            params = [status, status_reason, now]
            
            if version:
                updates.append("version = ?")
                params.append(version)
            
            if category:
                updates.append("category = ?")
                params.append(category)
            
            params.append(tool_id)
            
            conn.execute(f"""
                UPDATE tool_health_metrics
                SET {", ".join(updates)}
                WHERE tool_id = ?
            """, params)
        
        conn.commit()
    finally:
        conn.close()
