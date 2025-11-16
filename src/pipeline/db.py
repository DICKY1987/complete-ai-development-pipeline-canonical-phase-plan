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
    "validate_state_transition",
    "update_run_status",
    "update_workstream_status",
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
# State Machine - Formal State Transition Validation
# ============================================================================
#
# This section implements a formal state machine for runs and workstreams.
# All state transitions are validated before being applied to ensure
# consistency and prevent invalid state changes.
#
# State Diagrams:
#
# RUN STATES:
#   pending → running → completed
#                    → failed
#                    → partial
#                    → abandoned
#
# WORKSTREAM STATES:
#   pending → ready → editing → static_check → runtime_check → done
#                                          ↓         ↓
#                                        fixing ────┘
#   Any state → failed (on critical error)
#   Any state → abandoned (manual intervention)
#   pending/ready → blocked (dependency failure)
#
# ============================================================================

from typing import Set, Dict, Literal

# Type aliases for state values
RunState = Literal["pending", "running", "completed", "failed", "partial", "abandoned"]
WorkstreamState = Literal[
    "pending", "ready", "editing", "static_check", "fixing",
    "runtime_check", "done", "failed", "blocked", "abandoned"
]

# Valid states for each entity type
VALID_RUN_STATES: Set[str] = {
    "pending",
    "running",
    "completed",
    "failed",
    "partial",
    "abandoned",
}

VALID_WORKSTREAM_STATES: Set[str] = {
    "pending",
    "ready",
    "editing",
    "static_check",
    "fixing",
    "runtime_check",
    "done",
    "failed",
    "blocked",
    "abandoned",
}

# Valid state transitions
# Format: {from_state: {valid_to_states}}
RUN_TRANSITIONS: Dict[str, Set[str]] = {
    "pending": {"running", "failed", "abandoned"},
    "running": {"completed", "failed", "partial", "abandoned"},
    "completed": {"abandoned"},  # Can only abandon a completed run
    "failed": {"abandoned"},
    "partial": {"running", "abandoned"},  # Can retry from partial
    "abandoned": set(),  # Terminal state
}

WORKSTREAM_TRANSITIONS: Dict[str, Set[str]] = {
    "pending": {"ready", "blocked", "failed", "abandoned"},
    "ready": {"editing", "blocked", "failed", "abandoned"},
    "editing": {"static_check", "failed", "abandoned"},
    "static_check": {"fixing", "runtime_check", "failed", "abandoned"},
    "fixing": {"static_check", "failed", "abandoned"},  # Retry loop
    "runtime_check": {"done", "failed", "abandoned"},
    "done": {"abandoned"},  # Can only abandon after completion
    "failed": {"abandoned"},  # Can abandon a failed workstream
    "blocked": {"ready", "abandoned"},  # Unblock when dependency resolves
    "abandoned": set(),  # Terminal state
}


def validate_state_transition(
    entity_type: Literal["run", "workstream"],
    from_state: str,
    to_state: str
) -> None:
    """
    Validate that a state transition is allowed.

    Enforces the formal state machine rules for runs and workstreams.
    Raises ValueError if the transition is invalid.

    Args:
        entity_type: Type of entity ("run" or "workstream")
        from_state: Current state
        to_state: Desired next state

    Raises:
        ValueError: If the transition is not allowed

    Examples:
        >>> validate_state_transition("run", "pending", "running")
        None  # Valid transition

        >>> validate_state_transition("run", "completed", "running")
        ValueError: Invalid run state transition: completed → running

        >>> validate_state_transition("workstream", "editing", "static_check")
        None  # Valid transition

        >>> validate_state_transition("workstream", "done", "editing")
        ValueError: Invalid workstream state transition: done → editing
    """
    # Select appropriate state sets and transitions
    if entity_type == "run":
        valid_states = VALID_RUN_STATES
        transitions = RUN_TRANSITIONS
    elif entity_type == "workstream":
        valid_states = VALID_WORKSTREAM_STATES
        transitions = WORKSTREAM_TRANSITIONS
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'run' or 'workstream'")

    # Validate states exist
    if from_state not in valid_states:
        raise ValueError(f"Invalid {entity_type} state: {from_state}")
    if to_state not in valid_states:
        raise ValueError(f"Invalid {entity_type} state: {to_state}")

    # Allow staying in same state (idempotent)
    if from_state == to_state:
        return

    # Check if transition is allowed
    allowed_transitions = transitions.get(from_state, set())
    if to_state not in allowed_transitions:
        raise ValueError(
            f"Invalid {entity_type} state transition: {from_state} -> {to_state}. "
            f"Allowed transitions from {from_state}: {sorted(allowed_transitions) if allowed_transitions else 'none (terminal state)'}"
        )


def update_run_status(
    run_id: str,
    new_status: str,
    db_path: Optional[os.PathLike | str] = None
) -> None:
    """
    Update run status with state transition validation.

    Enforces state machine rules before applying the update.
    Records the transition as an event if successful.

    Args:
        run_id: Run identifier
        new_status: New status to set
        db_path: Optional database path

    Raises:
        ValueError: If state transition is invalid
        sqlite3.Error: If database operation fails

    Example:
        >>> update_run_status("run-001", "running")
        # Updates status from pending to running
    """
    from datetime import datetime

    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        # Get current status
        cur.execute("SELECT status FROM runs WHERE run_id = ?", (run_id,))
        row = cur.fetchone()

        if row is None:
            raise ValueError(f"Run not found: {run_id}")

        current_status = row["status"]

        # Validate transition
        validate_state_transition("run", current_status, new_status)

        # Apply update
        updated_at = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
            (new_status, updated_at, run_id)
        )

        # Record event
        cur.execute(
            """INSERT INTO events (timestamp, run_id, event_type, payload_json)
               VALUES (?, ?, ?, ?)""",
            (
                updated_at,
                run_id,
                "run_status_changed",
                f'{{"from": "{current_status}", "to": "{new_status}"}}'
            )
        )

        conn.commit()

    finally:
        cur.close()
        conn.close()


def update_workstream_status(
    ws_id: str,
    new_status: str,
    db_path: Optional[os.PathLike | str] = None
) -> None:
    """
    Update workstream status with state transition validation.

    Enforces state machine rules before applying the update.
    Records the transition as an event if successful.

    Args:
        ws_id: Workstream identifier
        new_status: New status to set
        db_path: Optional database path

    Raises:
        ValueError: If state transition is invalid
        sqlite3.Error: If database operation fails

    Example:
        >>> update_workstream_status("ws-ph01-spec-mapping", "editing")
        # Updates status from ready to editing
    """
    from datetime import datetime

    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        # Get current status
        cur.execute("SELECT status, run_id FROM workstreams WHERE ws_id = ?", (ws_id,))
        row = cur.fetchone()

        if row is None:
            raise ValueError(f"Workstream not found: {ws_id}")

        current_status = row["status"]
        run_id = row["run_id"]

        # Validate transition
        validate_state_transition("workstream", current_status, new_status)

        # Apply update
        updated_at = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            "UPDATE workstreams SET status = ?, updated_at = ? WHERE ws_id = ?",
            (new_status, updated_at, ws_id)
        )

        # Record event
        cur.execute(
            """INSERT INTO events (timestamp, run_id, ws_id, event_type, payload_json)
               VALUES (?, ?, ?, ?, ?)""",
            (
                updated_at,
                run_id,
                ws_id,
                "workstream_status_changed",
                f'{{"from": "{current_status}", "to": "{new_status}"}}'
            )
        )

        conn.commit()

    finally:
        cur.close()
        conn.close()

