"""
CRUD Operations for AI Development Pipeline Database.

Provides create, read, update operations for runs, workstreams, step_attempts,
errors, and events. All functions use ISO 8601 UTC timestamps and follow
transactional patterns for data integrity.
"""
# DOC_ID: DOC-CORE-STATE-CRUD-169

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List

from .db import get_connection


# ============================================================================
# RUN CRUD OPERATIONS
# ============================================================================

def create_run(
    run_id: str,
    status: str = "pending",
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new run record.

    Args:
        run_id: Unique run identifier
        status: Initial status (default: "pending")
        metadata: Optional metadata dictionary
        db_path: Optional database path

    Returns:
        Created run record as dictionary

    Raises:
        sqlite3.IntegrityError: If run_id already exists
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        now = datetime.now(UTC).isoformat() + "Z"
        metadata_json = json.dumps(metadata) if metadata else None

        cur.execute(
            """INSERT INTO runs (run_id, status, created_at, updated_at, metadata_json)
               VALUES (?, ?, ?, ?, ?)""",
            (run_id, status, now, now, metadata_json)
        )
        conn.commit()

        # Return created record
        return get_run(run_id, db_path)

    finally:
        cur.close()
        conn.close()


def get_run(run_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a run record by ID.

    Args:
        run_id: Run identifier
        db_path: Optional database path

    Returns:
        Run record as dictionary

    Raises:
        ValueError: If run not found
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        row = cur.fetchone()

        if row is None:
            raise ValueError(f"Run not found: {run_id}")

        result = dict(row)
        # Parse metadata JSON if present
        if result.get("metadata_json"):
            result["metadata"] = json.loads(result["metadata_json"])
            del result["metadata_json"]
        else:
            result["metadata"] = None

        return result

    finally:
        cur.close()
        conn.close()


def update_run_status(
    run_id: str,
    new_status: str,
    db_path: Optional[str] = None
) -> None:
    """
    Update run status.

    Note: This is a basic version. Use the state machine version from
    ws-ph02-state-machine for validated transitions.

    Args:
        run_id: Run identifier
        new_status: New status value
        db_path: Optional database path

    Raises:
        ValueError: If run not found
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        # Verify run exists
        cur.execute("SELECT run_id FROM runs WHERE run_id = ?", (run_id,))
        if cur.fetchone() is None:
            raise ValueError(f"Run not found: {run_id}")

        # Update status
        updated_at = datetime.now(UTC).isoformat() + "Z"
        cur.execute(
            "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
            (new_status, updated_at, run_id)
        )
        conn.commit()

    finally:
        cur.close()
        conn.close()


def list_runs(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List runs with optional filtering.

    Args:
        status: Optional status filter
        limit: Maximum number of results (default: 100)
        offset: Number of results to skip (default: 0)
        db_path: Optional database path

    Returns:
        List of run records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        if status:
            cur.execute(
                """SELECT * FROM runs
                   WHERE status = ?
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (status, limit, offset)
            )
        else:
            cur.execute(
                """SELECT * FROM runs
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            )

        rows = cur.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            if result.get("metadata_json"):
                result["metadata"] = json.loads(result["metadata_json"])
                del result["metadata_json"]
            else:
                result["metadata"] = None
            results.append(result)

        return results

    finally:
        cur.close()
        conn.close()


# ============================================================================
# WORKSTREAM CRUD OPERATIONS
# ============================================================================

def create_workstream(
    ws_id: str,
    run_id: Optional[str] = None,
    status: str = "pending",
    depends_on: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new workstream record.

    Args:
        ws_id: Unique workstream identifier
        run_id: Optional associated run ID
        status: Initial status (default: "pending")
        depends_on: Optional dependency workstream ID
        metadata: Optional metadata dictionary
        db_path: Optional database path

    Returns:
        Created workstream record

    Raises:
        sqlite3.IntegrityError: If ws_id already exists or run_id doesn't exist
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        now = datetime.now(UTC).isoformat() + "Z"
        metadata_json = json.dumps(metadata) if metadata else None

        cur.execute(
            """INSERT INTO workstreams (ws_id, run_id, status, depends_on, created_at, updated_at, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ws_id, run_id, status, depends_on, now, now, metadata_json)
        )
        conn.commit()

        return get_workstream(ws_id, db_path)

    finally:
        cur.close()
        conn.close()


def get_workstream(ws_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a workstream record by ID.

    Args:
        ws_id: Workstream identifier
        db_path: Optional database path

    Returns:
        Workstream record as dictionary

    Raises:
        ValueError: If workstream not found
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM workstreams WHERE ws_id = ?", (ws_id,))
        row = cur.fetchone()

        if row is None:
            raise ValueError(f"Workstream not found: {ws_id}")

        result = dict(row)
        if result.get("metadata_json"):
            result["metadata"] = json.loads(result["metadata_json"])
            del result["metadata_json"]
        else:
            result["metadata"] = None

        return result

    finally:
        cur.close()
        conn.close()


def get_workstreams_for_run(
    run_id: str,
    status: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all workstreams for a specific run.

    Args:
        run_id: Run identifier
        status: Optional status filter
        db_path: Optional database path

    Returns:
        List of workstream records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        if status:
            cur.execute(
                """SELECT * FROM workstreams
                   WHERE run_id = ? AND status = ?
                   ORDER BY created_at ASC""",
                (run_id, status)
            )
        else:
            cur.execute(
                """SELECT * FROM workstreams
                   WHERE run_id = ?
                   ORDER BY created_at ASC""",
                (run_id,)
            )

        rows = cur.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            if result.get("metadata_json"):
                result["metadata"] = json.loads(result["metadata_json"])
                del result["metadata_json"]
            else:
                result["metadata"] = None
            results.append(result)

        return results

    finally:
        cur.close()
        conn.close()


def update_workstream_status(
    ws_id: str,
    new_status: str,
    db_path: Optional[str] = None
) -> None:
    """
    Update workstream status.

    Note: This is a basic version. Use the state machine version from
    ws-ph02-state-machine for validated transitions.

    Args:
        ws_id: Workstream identifier
        new_status: New status value
        db_path: Optional database path

    Raises:
        ValueError: If workstream not found
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        # Verify workstream exists
        cur.execute("SELECT ws_id FROM workstreams WHERE ws_id = ?", (ws_id,))
        if cur.fetchone() is None:
            raise ValueError(f"Workstream not found: {ws_id}")

        # Update status
        updated_at = datetime.now(UTC).isoformat() + "Z"
        cur.execute(
            "UPDATE workstreams SET status = ?, updated_at = ? WHERE ws_id = ?",
            (new_status, updated_at, ws_id)
        )
        conn.commit()

    finally:
        cur.close()
        conn.close()


# ============================================================================
# STEP ATTEMPT OPERATIONS
# ============================================================================

def record_step_attempt(
    run_id: str,
    ws_id: str,
    step_name: str,
    status: str,
    started_at: Optional[str] = None,
    completed_at: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Record a step attempt.

    Args:
        run_id: Run identifier
        ws_id: Workstream identifier
        step_name: Name of the step
        status: Step status (e.g., "success", "failed")
        started_at: Optional ISO 8601 start timestamp
        completed_at: Optional ISO 8601 completion timestamp
        result: Optional result data dictionary
        db_path: Optional database path

    Returns:
        ID of created step attempt record

    Raises:
        sqlite3.IntegrityError: If foreign keys don't exist
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        result_json = json.dumps(result) if result else None

        cur.execute(
            """INSERT INTO step_attempts (run_id, ws_id, step_name, status, started_at, completed_at, result_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (run_id, ws_id, step_name, status, started_at, completed_at, result_json)
        )
        conn.commit()

        return cur.lastrowid

    finally:
        cur.close()
        conn.close()


def get_step_attempts(
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    step_name: Optional[str] = None,
    limit: int = 100,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get step attempts with optional filtering.

    Args:
        run_id: Optional run ID filter
        ws_id: Optional workstream ID filter
        step_name: Optional step name filter
        limit: Maximum results (default: 100)
        db_path: Optional database path

    Returns:
        List of step attempt records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        query = "SELECT * FROM step_attempts WHERE 1=1"
        params = []

        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if ws_id:
            query += " AND ws_id = ?"
            params.append(ws_id)
        if step_name:
            query += " AND step_name = ?"
            params.append(step_name)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            if result.get("result_json"):
                result["result"] = json.loads(result["result_json"])
                del result["result_json"]
            else:
                result["result"] = None
            results.append(result)

        return results

    finally:
        cur.close()
        conn.close()


# ============================================================================
# ERROR OPERATIONS (with deduplication)
# ============================================================================

def record_error(
    error_code: str,
    signature: str,
    message: str,
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    step_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Record an error with automatic deduplication.

    If an error with the same (run_id, ws_id, step_name, signature) exists,
    increments the count and updates last_seen_at. Otherwise, creates a new record.

    Args:
        error_code: Error code/category
        signature: Unique error signature for deduplication
        message: Error message
        run_id: Optional run ID
        ws_id: Optional workstream ID
        step_name: Optional step name
        context: Optional context data dictionary
        db_path: Optional database path

    Returns:
        ID of error record (created or updated)
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        now = datetime.now(UTC).isoformat() + "Z"
        context_json = json.dumps(context) if context else None

        # Check if error already exists
        cur.execute(
            """SELECT id, count FROM errors
               WHERE run_id IS ? AND ws_id IS ? AND step_name IS ? AND signature = ?""",
            (run_id, ws_id, step_name, signature)
        )
        existing = cur.fetchone()

        if existing:
            # Update existing error
            error_id = existing["id"]
            new_count = existing["count"] + 1

            cur.execute(
                """UPDATE errors
                   SET count = ?, last_seen_at = ?, message = ?, context_json = ?
                   WHERE id = ?""",
                (new_count, now, message, context_json, error_id)
            )
        else:
            # Insert new error
            cur.execute(
                """INSERT INTO errors (run_id, ws_id, step_name, error_code, signature, message, context_json, count, first_seen_at, last_seen_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
                (run_id, ws_id, step_name, error_code, signature, message, context_json, now, now)
            )
            error_id = cur.lastrowid

        conn.commit()
        return error_id

    finally:
        cur.close()
        conn.close()


def get_errors(
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    error_code: Optional[str] = None,
    limit: int = 100,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get errors with optional filtering.

    Args:
        run_id: Optional run ID filter
        ws_id: Optional workstream ID filter
        error_code: Optional error code filter
        limit: Maximum results (default: 100)
        db_path: Optional database path

    Returns:
        List of error records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        query = "SELECT * FROM errors WHERE 1=1"
        params = []

        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if ws_id:
            query += " AND ws_id = ?"
            params.append(ws_id)
        if error_code:
            query += " AND error_code = ?"
            params.append(error_code)

        query += " ORDER BY last_seen_at DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            if result.get("context_json"):
                result["context"] = json.loads(result["context_json"])
                del result["context_json"]
            else:
                result["context"] = None
            results.append(result)

        return results

    finally:
        cur.close()
        conn.close()


# ============================================================================
# EVENT OPERATIONS
# ============================================================================

def record_event(
    event_type: str,
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Record an event.

    Args:
        event_type: Type of event
        run_id: Optional run ID
        ws_id: Optional workstream ID
        payload: Optional event payload dictionary
        db_path: Optional database path

    Returns:
        ID of created event record
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        timestamp = datetime.now(UTC).isoformat() + "Z"
        payload_json = json.dumps(payload) if payload else None

        cur.execute(
            """INSERT INTO events (timestamp, run_id, ws_id, event_type, payload_json)
               VALUES (?, ?, ?, ?, ?)""",
            (timestamp, run_id, ws_id, event_type, payload_json)
        )
        conn.commit()

        return cur.lastrowid

    finally:
        cur.close()
        conn.close()


def get_events(
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get events with optional filtering.

    Args:
        run_id: Optional run ID filter
        ws_id: Optional workstream ID filter
        event_type: Optional event type filter
        limit: Maximum results (default: 100)
        offset: Number of results to skip (default: 0)
        db_path: Optional database path

    Returns:
        List of event records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if ws_id:
            query += " AND ws_id = ?"
            params.append(ws_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            if result.get("payload_json"):
                result["payload"] = json.loads(result["payload_json"])
                del result["payload_json"]
            else:
                result["payload"] = None
            results.append(result)

        return results

    finally:
        cur.close()
        conn.close()

# ============================================================================
# PATCH CRUD OPERATIONS
# ============================================================================

def record_patch(
    run_id: str,
    ws_id: str,
    step_name: str,
    attempt: int,
    patch_file: str,
    diff_hash: str,
    line_count: int,
    files_modified: List[str],
    validated: bool = False,
    applied: bool = False,
    db_path: Optional[str] = None
) -> int:
    """
    Record a patch in the database.
    
    Args:
        run_id: Run identifier
        ws_id: Workstream identifier
        step_name: Step name (edit, fix_static, fix_runtime)
        attempt: Attempt number
        patch_file: Path to patch file
        diff_hash: SHA256 hash of diff content
        line_count: Total line count (additions + deletions)
        files_modified: List of modified file paths
        validated: Whether patch passed validation
        applied: Whether patch was applied
        db_path: Optional database path
        
    Returns:
        Patch record ID
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    try:
        now = datetime.now(UTC).isoformat() + "Z"
        files_json = json.dumps(files_modified)
        
        cur.execute(
            """INSERT INTO patches 
               (run_id, ws_id, step_name, attempt, patch_file, diff_hash,
                line_count, files_modified, created_at, validated, applied)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, ws_id, step_name, attempt, patch_file, diff_hash,
             line_count, files_json, now, int(validated), int(applied))
        )
        conn.commit()
        
        return cur.lastrowid
        
    finally:
        cur.close()
        conn.close()


def get_patches_by_ws(
    ws_id: str,
    limit: int = 100,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all patches for a workstream.
    
    Args:
        ws_id: Workstream identifier
        limit: Maximum results
        db_path: Optional database path
        
    Returns:
        List of patch records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute(
            """SELECT * FROM patches 
               WHERE ws_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (ws_id, limit)
        )
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            # Parse files_modified JSON
            if result.get("files_modified"):
                result["files_modified"] = json.loads(result["files_modified"])
            # Convert int to bool
            result["validated"] = bool(result.get("validated", 0))
            result["applied"] = bool(result.get("applied", 0))
            results.append(result)
        
        return results
        
    finally:
        cur.close()
        conn.close()


def get_patches_by_hash(
    ws_id: str,
    diff_hash: str,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get patches by diff hash (for oscillation detection).
    
    Args:
        ws_id: Workstream identifier
        diff_hash: SHA256 hash of diff content
        db_path: Optional database path
        
    Returns:
        List of matching patch records
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute(
            """SELECT * FROM patches 
               WHERE ws_id = ? AND diff_hash = ? 
               ORDER BY created_at DESC""",
            (ws_id, diff_hash)
        )
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            if result.get("files_modified"):
                result["files_modified"] = json.loads(result["files_modified"])
            result["validated"] = bool(result.get("validated", 0))
            result["applied"] = bool(result.get("applied", 0))
            results.append(result)
        
        return results
        
    finally:
        cur.close()
        conn.close()


def update_patch_status(
    patch_id: int,
    validated: Optional[bool] = None,
    applied: Optional[bool] = None,
    db_path: Optional[str] = None
) -> None:
    """
    Update patch validation/application status.
    
    Args:
        patch_id: Patch record ID
        validated: New validation status
        applied: New application status
        db_path: Optional database path
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if validated is not None:
            updates.append("validated = ?")
            params.append(int(validated))
        
        if applied is not None:
            updates.append("applied = ?")
            params.append(int(applied))
        
        if not updates:
            return
        
        params.append(patch_id)
        query = f"UPDATE patches SET {', '.join(updates)} WHERE id = ?"
        
        cur.execute(query, tuple(params))
        conn.commit()
        
    finally:
        cur.close()
        conn.close()
