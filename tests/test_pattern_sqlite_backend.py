"""Tests for SQLite-backed pattern store."""

from datetime import datetime
import sqlite3

from gui.tui_app.core.pattern_client import SQLitePatternStateStore, PatternStatus


def test_sqlite_pattern_store_reads_runs_and_events(tmp_path):
    """Ensure runs/events map from executions and patch ledger."""
    # DOC_ID: DOC-TEST-TESTS-TEST-PATTERN-SQLITE-BACKEND-099
    # DOC_ID: DOC-TEST-TESTS-TEST-PATTERN-SQLITE-BACKEND-060
    db_path = tmp_path / "pipeline_state.db"
    store = SQLitePatternStateStore(db_path=str(db_path))
    conn: sqlite3.Connection = store._conn  # test hook
    now = datetime.now().isoformat(sep=" ", timespec="seconds")

    conn.execute(
        """
        INSERT INTO uet_executions (execution_id, phase_name, started_at, completed_at, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("exec-psql-1", "PHASE_TEST", now, now, "completed", "{}"),
    )
    conn.execute(
        """
        INSERT INTO uet_tasks (task_id, execution_id, task_type, dependencies, status, created_at, started_at, completed_at, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "task-psql-1",
            "exec-psql-1",
            "PHASE_A",
            "[]",
            "completed",
            now,
            now,
            now,
            "{}",
        ),
    )
    conn.execute(
        """
        INSERT INTO patch_ledger (patch_id, execution_id, created_at, state, patch_content, validation_result, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "patch-psql-1",
            "exec-psql-1",
            now,
            "validated",
            "diff --git a/x b/x\n+1",
            "{}",
            "{}",
        ),
    )
    conn.commit()

    runs = store.get_recent_runs(limit=5)
    assert runs
    run = next(r for r in runs if r.run_id == "exec-psql-1")
    assert run.status in (
        PatternStatus.RUNNING,
        PatternStatus.COMPLETED,
        PatternStatus.PENDING,
    )

    events = store.get_run_events("exec-psql-1")
    assert len(events) >= 3  # start + task + patch
    assert events[0].run_id == "exec-psql-1"
