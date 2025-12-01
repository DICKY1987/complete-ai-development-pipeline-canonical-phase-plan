"""Error record management for the quarantine center.

This module provides utilities for creating and managing structured error records
that power the Error & Quarantine Center UI component.
"""
# DOC_ID: DOC-CORE-CORE-ERROR-RECORDS-041
# DOC_ID: DOC-CORE-CORE-ERROR-RECORDS-018

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from modules.core_state.m010003_db import get_connection
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.tool_instrumentation import emit_error_raised


def generate_error_id(
    entity_type: str,
    entity_id: str,
    category: str,
    message: str
) -> str:
    """Generate a stable error ID based on error attributes.
    
    This allows grouping of duplicate errors by using the same ID.
    Using full SHA256 hash to ensure uniqueness.
    """
    key = f"{entity_type}:{entity_id}:{category}:{message[:100]}"
    return "err-" + hashlib.sha256(key.encode()).hexdigest()


def create_error_record(
    entity_type: str,
    human_message: str,
    severity: str = "error",
    category: str = "unknown",
    file_id: Optional[str] = None,
    job_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    run_id: Optional[str] = None,
    plugin: Optional[str] = None,
    technical_details: Optional[str] = None,
    recommendation: Optional[str] = None,
    quarantine_path: Optional[str] = None,
    can_retry: bool = True,
    auto_fix_available: bool = False,
    error_id: Optional[str] = None
) -> str:
    """Create or update an error record.
    
    Args:
        entity_type: Type of entity (file, job, tool_instance, workstream)
        human_message: Human-readable error message
        severity: warning, error, critical
        category: Error category (syntax, config, network, etc.)
        file_id: Associated file
        job_id: Associated job
        ws_id: Associated workstream
        tool_id: Associated tool
        run_id: Associated run
        plugin: Error detection plugin
        technical_details: Technical error details/stack trace
        recommendation: Suggested remediation
        quarantine_path: Path where file was quarantined
        can_retry: Whether the operation can be retried
        auto_fix_available: Whether an auto-fix is available
        error_id: Optional explicit error ID (otherwise generated)
    
    Returns:
        The error ID
    """
    if not error_id:
        # Generate stable error ID for grouping duplicates
        entity_id = file_id or job_id or ws_id or tool_id or "unknown"
        error_id = generate_error_id(entity_type, entity_id, category, human_message)
    
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if error already exists
        cursor = conn.execute(
            "SELECT error_id, occurrence_count FROM error_records WHERE error_id = ?",
            (error_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update occurrence count and last_seen
            conn.execute("""
                UPDATE error_records
                SET last_seen = ?,
                    occurrence_count = occurrence_count + 1
                WHERE error_id = ?
            """, (now, error_id))
        else:
            # Insert new error record
            conn.execute("""
                INSERT INTO error_records
                (error_id, entity_type, file_id, job_id, ws_id, tool_id, run_id,
                 plugin, severity, category, human_message, technical_details,
                 recommendation, first_seen, last_seen, occurrence_count,
                 quarantine_path, can_retry, auto_fix_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (
                error_id, entity_type, file_id, job_id, ws_id, tool_id, run_id,
                plugin, severity, category, human_message, technical_details,
                recommendation, now, now, quarantine_path,
                1 if can_retry else 0, 1 if auto_fix_available else 0
            ))
        
        conn.commit()
        
        # Emit error event
        emit_error_raised(
            error_id=error_id,
            entity_type=entity_type,
            severity=severity,
            category=category,
            human_message=human_message,
            run_id=run_id,
            workstream_id=ws_id,
            file_id=file_id,
            tool_id=tool_id,
            technical_details=technical_details
        )
        
        return error_id
    finally:
        conn.close()


def update_error_record(
    error_id: str,
    **updates
):
    """Update fields of an error record.
    
    Args:
        error_id: Error identifier
        **updates: Fields to update (severity, category, recommendation, etc.)
    """
    conn = get_connection()
    try:
        # Build update query
        valid_fields = [
            "severity", "category", "human_message", "technical_details",
            "recommendation", "quarantine_path", "can_retry", "auto_fix_available"
        ]
        
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in valid_fields:
                set_clauses.append(f"{field} = ?")
                # Convert booleans to integers for SQLite
                if isinstance(value, bool):
                    value = 1 if value else 0
                params.append(value)
        
        if not set_clauses:
            return
        
        params.append(error_id)
        
        sql = f"""
            UPDATE error_records
            SET {", ".join(set_clauses)}
            WHERE error_id = ?
        """
        
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def mark_error_resolved(
    error_id: str,
    resolution_details: Optional[str] = None
):
    """Mark an error as resolved.
    
    This doesn't delete the error (for historical tracking) but marks it
    as resolved with optional details about how it was fixed.
    
    TODO: Add dedicated resolution_status column to error_records table
    instead of storing resolution in the recommendation field. This would
    allow better querying and filtering of resolved vs unresolved errors.
    
    Args:
        error_id: Error identifier
        resolution_details: Optional details about the resolution
    """
    conn = get_connection()
    try:
        # For now, we'll store resolution in the recommendation field
        # This is a temporary workaround until resolution_status column is added
        update_error_record(
            error_id,
            recommendation=f"RESOLVED: {resolution_details}" if resolution_details else "RESOLVED"
        )
        
        # Emit event
        from modules.core_engine.m010001_event_bus import Event, EventBus, EventSeverity, EventType
        bus = EventBus()
        
        bus.emit(Event(
            event_type=EventType.ERROR_RESOLVED,
            timestamp=datetime.now(timezone.utc),
            severity=EventSeverity.INFO,
            message=f"Error resolved: {error_id}",
            payload={"error_id": error_id, "resolution": resolution_details}
        ))
    finally:
        pass


def get_errors_by_category(
    category: str,
    run_id: Optional[str] = None,
    limit: int = 100
):
    """Get error IDs grouped by category.
    
    Args:
        category: Error category
        run_id: Optional filter by run
        limit: Maximum results
    
    Returns:
        List of error IDs
    """
    conn = get_connection()
    try:
        sql = "SELECT error_id FROM error_records WHERE category = ?"
        params = [category]
        
        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)
        
        sql += " ORDER BY last_seen DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(sql, params)
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_error_statistics(run_id: Optional[str] = None):
    """Get error statistics for dashboard.
    
    Args:
        run_id: Optional filter by run
    
    Returns:
        Dict with error counts by category and severity
    """
    conn = get_connection()
    try:
        # Count by category
        sql = "SELECT category, COUNT(*) FROM error_records WHERE 1=1"
        params = []
        
        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)
        
        sql += " GROUP BY category"
        
        cursor = conn.execute(sql, params)
        by_category = dict(cursor.fetchall())
        
        # Count by severity
        sql = "SELECT severity, COUNT(*) FROM error_records WHERE 1=1"
        params = []
        
        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)
        
        sql += " GROUP BY severity"
        
        cursor = conn.execute(sql, params)
        by_severity = dict(cursor.fetchall())
        
        return {
            "by_category": by_category,
            "by_severity": by_severity,
        }
    finally:
        conn.close()


def get_top_errors(
    run_id: Optional[str] = None,
    limit: int = 10
):
    """Get top errors by occurrence count.
    
    Args:
        run_id: Optional filter by run
        limit: Maximum results
    
    Returns:
        List of (error_id, occurrence_count, human_message) tuples
    """
    conn = get_connection()
    try:
        sql = """
            SELECT error_id, occurrence_count, human_message
            FROM error_records
            WHERE 1=1
        """
        params = []
        
        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)
        
        sql += " ORDER BY occurrence_count DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(sql, params)
        return [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    finally:
        conn.close()
