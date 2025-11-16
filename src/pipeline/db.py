"""Database core

Provides connection helpers and initialization routines for the local SQLite
state store used by the pipeline. Implemented in PH-02 ws-ph02-db-core.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional

__all__ = [
    "get_connection",
    "init_db",
    # Run CRUD
    "create_run",
    "get_run",
    "update_run_status",
    "list_runs",
    # Workstream CRUD
    "create_workstream",
    "get_workstream",
    "get_workstreams_for_run",
    "update_workstream_status",
    # Step attempts
    "record_step_attempt",
    "get_step_attempts",
    # Errors
    "record_error",
    "get_errors",
    # Events
    "record_event",
    "get_events",
]


def _detect_repo_root(start: Optional[Path] = None) -> Path:
    """Ascend directories to locate the repository root (contains .git).

    Falls back to the provided start or current working directory if not found.
    """
    base = (start or Path.cwd()).resolve()
    cur = base
    for _ in range(10):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return base


def _resolve_db_path(db_path: Optional[os.PathLike | str] = None) -> Path:
    """Resolve the database path.

    Priority:
    1) Explicit `db_path` argument
    2) `PIPELINE_DB_PATH` environment variable
    3) Default: `<repo_root>/state/pipeline_state.db`
    """
    if db_path:
        path = Path(db_path)
    else:
        env_path = os.getenv("PIPELINE_DB_PATH")
        if env_path:
            path = Path(env_path)
        else:
            repo_root = _detect_repo_root()
            path = repo_root / "state" / "pipeline_state.db"

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """Create and return a SQLite connection with row factory configured.

    - Path resolution follows `_resolve_db_path`.
    - Ensures parent directory exists.
    - Sets `row_factory` to `sqlite3.Row` for dict-like row access.
    """
    path = _resolve_db_path(db_path)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[os.PathLike | str] = None, schema_path: Optional[os.PathLike | str] = None) -> None:
    """Initialize the database schema if not already applied.

    - Uses `get_connection()` to open/create the database.
    - Detects whether the schema is applied by checking for `schema_meta` and
      a `schema_version` entry.
    - If not applied, executes `schema/schema.sql` relative to repo root unless
      an explicit `schema_path` is provided, then writes `schema_version=1`.
    - Idempotent: running repeatedly makes no harmful changes.
    """
    conn = get_connection(db_path)
    cur = conn.cursor()

    def schema_applied() -> bool:
        try:
            cur.execute(
                "SELECT value FROM schema_meta WHERE key = 'schema_version'"
            )
            row = cur.fetchone()
            return row is not None
        except sqlite3.Error:
            return False

    if not schema_applied():
        # Determine schema file
        if schema_path is not None:
            schema_file = Path(schema_path)
        else:
            repo_root = _detect_repo_root()
            schema_file = repo_root / "schema" / "schema.sql"

        sql = schema_file.read_text(encoding="utf-8")
        cur.executescript(sql)
        # Set initial version (ignore if already present)
        cur.execute(
            "INSERT OR IGNORE INTO schema_meta(key, value) VALUES('schema_version', '1')"
        )
        conn.commit()

    cur.close()
    conn.close()


# ============================================================================
# Import CRUD operations from crud_operations module
# ============================================================================

from .crud_operations import (
    # Run CRUD
    create_run,
    get_run,
    update_run_status,
    list_runs,
    # Workstream CRUD
    create_workstream,
    get_workstream,
    get_workstreams_for_run,
    update_workstream_status,
    # Step attempts
    record_step_attempt,
    get_step_attempts,
    # Errors
    record_error,
    get_errors,
    # Events
    record_event,
    get_events,
)

