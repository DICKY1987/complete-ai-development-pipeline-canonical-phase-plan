"""File lifecycle management utilities.

This module provides helpers for tracking files through the pipeline lifecycle,
recording state transitions and tool touches.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.state.db import get_connection
from core.tool_instrumentation import emit_file_state_change


def compute_file_id(file_path: str) -> str:
    """Compute a stable file ID based on path.
    
    In a full implementation, this would hash the file content.
    For now, we use a hash of the path.
    
    Note: Using full SHA256 hash to minimize collision probability.
    File IDs are used as primary keys and must be unique.
    """
    return "file-" + hashlib.sha256(file_path.encode()).hexdigest()


def register_file(
    file_path: str,
    origin_path: Optional[str] = None,
    file_role: str = "other",
    workstream_id: Optional[str] = None,
    job_id: Optional[str] = None,
    run_id: Optional[str] = None,
    file_id: Optional[str] = None
) -> str:
    """Register a file in the lifecycle tracking system.
    
    Args:
        file_path: Current path to the file
        origin_path: Original path (e.g., in sandbox)
        file_role: code, spec, plan, test, config, docs, asset, other
        workstream_id: Associated workstream
        job_id: Associated job
        run_id: Associated run
        file_id: Optional explicit file ID (otherwise computed)
    
    Returns:
        The file ID
    """
    if not file_id:
        file_id = compute_file_id(file_path)
    
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if already registered
        cursor = conn.execute(
            "SELECT file_id FROM file_lifecycle WHERE file_id = ?",
            (file_id,)
        )
        exists = cursor.fetchone() is not None
        
        if not exists:
            # Insert new record
            conn.execute("""
                INSERT INTO file_lifecycle
                (file_id, current_path, origin_path, file_role, current_state,
                 workstream_id, job_id, run_id, first_seen, last_processed)
                VALUES (?, ?, ?, ?, 'discovered', ?, ?, ?, ?, ?)
            """, (
                file_id, file_path, origin_path or file_path, file_role,
                workstream_id, job_id, run_id, now, now
            ))
            
            # Record initial state
            conn.execute("""
                INSERT INTO file_state_history (file_id, state, timestamp)
                VALUES (?, 'discovered', ?)
            """, (file_id, now))
            
            conn.commit()
        
        return file_id
    finally:
        conn.close()


def update_file_state(
    file_id: str,
    new_state: str,
    tool_id: Optional[str] = None,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None
):
    """Update the lifecycle state of a file.
    
    Args:
        file_id: File identifier
        new_state: New state (discovered, classified, intake, routed, processing,
                   in_flight, awaiting_review, awaiting_commit, committed, quarantined)
        tool_id: Tool that triggered the state change
        run_id: Associated run
        workstream_id: Associated workstream
    """
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Get current state
        cursor = conn.execute(
            "SELECT current_state FROM file_lifecycle WHERE file_id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"File not registered: {file_id}")
        
        old_state = row[0]
        
        if old_state != new_state:
            # Update current state
            conn.execute("""
                UPDATE file_lifecycle
                SET current_state = ?, last_processed = ?
                WHERE file_id = ?
            """, (new_state, now, file_id))
            
            # Record state transition
            conn.execute("""
                INSERT INTO file_state_history (file_id, state, timestamp)
                VALUES (?, ?, ?)
            """, (file_id, new_state, now))
            
            conn.commit()
            
            # Emit event
            emit_file_state_change(
                file_id=file_id,
                old_state=old_state,
                new_state=new_state,
                run_id=run_id,
                workstream_id=workstream_id,
                tool_id=tool_id
            )
    finally:
        conn.close()


def record_tool_touch(
    file_id: str,
    tool_id: str,
    tool_name: str,
    action: str,
    status: str,
    error_message: Optional[str] = None
):
    """Record that a tool touched a file.
    
    Args:
        file_id: File identifier
        tool_id: Tool identifier
        tool_name: Human-readable tool name
        action: Action performed (e.g., "refactor", "test", "lint")
        status: Outcome status (e.g., "success", "failure")
        error_message: Optional error message if failed
    """
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO file_tool_touches
            (file_id, tool_id, tool_name, action, status, error_message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, tool_id, tool_name, action, status, error_message, now))
        
        # Update last_processed timestamp
        conn.execute("""
            UPDATE file_lifecycle
            SET last_processed = ?
            WHERE file_id = ?
        """, (now, file_id))
        
        conn.commit()
    finally:
        conn.close()


def mark_file_committed(
    file_id: str,
    commit_sha: str,
    repo_path: str,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None
):
    """Mark a file as committed to the repository.
    
    Args:
        file_id: File identifier
        commit_sha: Git commit SHA
        repo_path: Path in the repository
        run_id: Associated run
        workstream_id: Associated workstream
    """
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            UPDATE file_lifecycle
            SET current_state = 'committed',
                committed_sha = ?,
                committed_repo_path = ?,
                last_processed = ?
            WHERE file_id = ?
        """, (commit_sha, repo_path, now, file_id))
        
        # Record state transition
        conn.execute("""
            INSERT INTO file_state_history (file_id, state, timestamp)
            VALUES (?, 'committed', ?)
        """, (file_id, now))
        
        conn.commit()
        
        # Emit event
        emit_file_state_change(
            file_id=file_id,
            old_state="awaiting_commit",
            new_state="committed",
            run_id=run_id,
            workstream_id=workstream_id
        )
    finally:
        conn.close()


def mark_file_quarantined(
    file_id: str,
    reason: str,
    quarantine_folder: str,
    run_id: Optional[str] = None,
    workstream_id: Optional[str] = None,
    tool_id: Optional[str] = None
):
    """Mark a file as quarantined.
    
    Args:
        file_id: File identifier
        reason: Reason for quarantine
        quarantine_folder: Path to quarantine folder
        run_id: Associated run
        workstream_id: Associated workstream
        tool_id: Tool that triggered quarantine
    """
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Get current state
        cursor = conn.execute(
            "SELECT current_state FROM file_lifecycle WHERE file_id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        old_state = row[0] if row else "unknown"
        
        conn.execute("""
            UPDATE file_lifecycle
            SET current_state = 'quarantined',
                quarantine_reason = ?,
                quarantine_folder = ?,
                last_processed = ?
            WHERE file_id = ?
        """, (reason, quarantine_folder, now, file_id))
        
        # Record state transition
        conn.execute("""
            INSERT INTO file_state_history (file_id, state, timestamp)
            VALUES (?, 'quarantined', ?)
        """, (file_id, now))
        
        conn.commit()
        
        # Emit event
        emit_file_state_change(
            file_id=file_id,
            old_state=old_state,
            new_state="quarantined",
            run_id=run_id,
            workstream_id=workstream_id,
            tool_id=tool_id
        )
    finally:
        conn.close()


def update_file_metadata(
    file_id: str,
    **metadata
):
    """Update file metadata (stored as JSON).
    
    Args:
        file_id: File identifier
        **metadata: Arbitrary metadata fields to store
    """
    conn = get_connection()
    try:
        # Get existing metadata
        cursor = conn.execute(
            "SELECT metadata_json FROM file_lifecycle WHERE file_id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"File not registered: {file_id}")
        
        existing = json.loads(row[0]) if row[0] else {}
        existing.update(metadata)
        
        conn.execute("""
            UPDATE file_lifecycle
            SET metadata_json = ?
            WHERE file_id = ?
        """, (json.dumps(existing), file_id))
        
        conn.commit()
    finally:
        conn.close()


def get_files_by_state(
    state: str,
    workstream_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 100
):
    """Get list of file IDs in a specific state.
    
    Args:
        state: File lifecycle state
        workstream_id: Optional filter by workstream
        run_id: Optional filter by run
        limit: Maximum results
    
    Returns:
        List of file IDs
    """
    conn = get_connection()
    try:
        sql = "SELECT file_id FROM file_lifecycle WHERE current_state = ?"
        params = [state]
        
        if workstream_id:
            sql += " AND workstream_id = ?"
            params.append(workstream_id)
        
        if run_id:
            sql += " AND run_id = ?"
            params.append(run_id)
        
        sql += " ORDER BY last_processed DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(sql, params)
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()
