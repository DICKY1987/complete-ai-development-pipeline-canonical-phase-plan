"""Database facade module for AI Development Pipeline.

This module provides a unified interface to the database layer, re-exporting
functions from crud_operations and providing initialization logic.

The database layer consists of:
- crud_operations.py: CRUD operations for runs, workstreams, steps, errors, events
- db_sqlite.py: Low-level SQLite connection and schema management
- error_db.py: Error pipeline context storage (separate concern)

Public API:
    All CRUD operations from crud_operations are re-exported for convenience.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional

# Re-export all CRUD operations including get_connection
from .crud_operations import (
    get_connection,
    create_run,
    get_run,
    update_run_status,
    list_runs,
    create_workstream,
    get_workstream,
    get_workstreams_for_run,
    update_workstream_status,
    record_step_attempt,
    get_step_attempts,
    record_error,
    get_errors,
    record_event,
    get_events,
)

__all__ = [
    # Initialization
    "init_db",
    "get_connection",
    # Run operations
    "create_run",
    "get_run",
    "update_run_status",
    "list_runs",
    # Workstream operations
    "create_workstream",
    "get_workstream",
    "get_workstreams_for_run",
    "update_workstream_status",
    # Step operations
    "record_step_attempt",
    "get_step_attempts",
    # Error operations
    "record_error",
    "get_errors",
    # Event operations
    "record_event",
    "get_events",
]


def _get_db_path() -> Path:
    """Get database path from environment or default location."""
    default_path = Path("state") / "pipeline_state.db"
    db_path_str = os.getenv("PIPELINE_DB_PATH", str(default_path))
    return Path(db_path_str)


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize the database schema.
    
    Creates the database file if it doesn't exist and applies the schema
    from schema/schema.sql. This operation is idempotent - it's safe to
    call multiple times.
    
    Args:
        db_path: Optional database path. If None, uses PIPELINE_DB_PATH env var
                or default location.
    """
    path = Path(db_path) if db_path else _get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection(str(path))
    try:
        # Check if schema is already applied by looking for runs table
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
        )
        exists = cursor.fetchone() is not None
        
        if not exists:
            # Apply schema from schema/schema.sql
            schema_path = Path("schema") / "schema.sql"
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
    finally:
        conn.close()
