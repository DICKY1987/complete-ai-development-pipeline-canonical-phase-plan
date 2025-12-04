"""Integration tests for the SQLite state backend."""

import sqlite3
from datetime import datetime

from gui.tui_app.core.sqlite_state_backend import SQLiteStateBackend


def test_sqlite_backend_reads_data(tmp_path):
    """Ensure SQLite backend returns executions, tasks, and patches."""
    # DOC_ID: DOC-TEST-TESTS-TEST-SQLITE-BACKEND-105
    # DOC_ID: DOC-TEST-TESTS-TEST-SQLITE-BACKEND-066
    db_path = tmp_path / "pipeline_state.db"
    backend = SQLiteStateBackend(db_path=str(db_path))

    conn: sqlite3.Connection = backend._conn  # Access test hook
    now = datetime.now().isoformat(sep=" ", timespec="seconds")

    conn.execute(
        """
        INSERT INTO uet_executions (execution_id, phase_name, started_at, completed_at, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("exec-1", "PHASE_TEST", now, None, "running", '{"owner": "test"}'),
    )
    conn.execute(
        """
        INSERT INTO uet_tasks (task_id, execution_id, task_type, dependencies, status, created_at, started_at, completed_at, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("task-1", "exec-1", "unit-test", "[]", "running", now, now, None, "{}"),
    )
    conn.execute(
        """
        INSERT INTO patch_ledger (patch_id, execution_id, created_at, state, patch_content, validation_result, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "patch-1",
            "exec-1",
            now,
            "validated",
            "diff --git a/sample.py b/sample.py\n+print('ok')",
            "{}",
            '{"files": ["sample.py"]}',
        ),
    )
    conn.commit()

    summary = backend.get_pipeline_summary()
    assert summary.total_tasks == 1
    assert summary.running_tasks == 1

    tasks = backend.get_tasks(limit=5)
    assert tasks and tasks[0].task_id == "task-1"

    executions = backend.get_executions()
    assert executions and executions[0].execution_id == "exec-1"

    patches = backend.get_patch_ledger()
    assert patches and patches[0].files[0] == "sample.py"
