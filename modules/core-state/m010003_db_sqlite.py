from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from modules.error_engine.m010004_error_context import ErrorPipelineContext


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            current_state TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS workstreams (
            run_id TEXT,
            ws_id TEXT,
            metadata_json TEXT,
            PRIMARY KEY (run_id, ws_id)
        );
        CREATE TABLE IF NOT EXISTS step_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            ws_id TEXT,
            step_name TEXT,
            result_json TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            ws_id TEXT,
            event_type TEXT,
            payload_json TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            ws_id TEXT,
            category TEXT,
            tool TEXT,
            message TEXT,
            path TEXT,
            created_at TEXT
        );
        """
    )
    conn.commit()


def get_error_context(conn: sqlite3.Connection, run_id: str, ws_id: str) -> ErrorPipelineContext:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT metadata_json FROM workstreams WHERE run_id=? AND ws_id=?", (run_id, ws_id))
    row = cur.fetchone()
    if row and row[0]:
        data = json.loads(row[0])
        return ErrorPipelineContext.from_json(data)

    # initialize
    ctx = ErrorPipelineContext(run_id=run_id, workstream_id=ws_id)
    save_error_context(conn, ctx)
    return ctx


def save_error_context(conn: sqlite3.Connection, ctx: ErrorPipelineContext) -> None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO runs(run_id, current_state, created_at) VALUES(?,?,?) "
        "ON CONFLICT(run_id) DO UPDATE SET current_state=excluded.current_state",
        (ctx.run_id, ctx.current_state, _utc_now()),
    )
    cur.execute(
        "INSERT INTO workstreams(run_id, ws_id, metadata_json) VALUES(?,?,?) "
        "ON CONFLICT(run_id, ws_id) DO UPDATE SET metadata_json=excluded.metadata_json",
        (ctx.run_id, ctx.workstream_id, json.dumps(ctx.to_json(), ensure_ascii=False)),
    )
    conn.commit()


def record_error_report(conn: sqlite3.Connection, ctx: ErrorPipelineContext, report: Dict[str, Any], step_name: str) -> None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO step_attempts(run_id, ws_id, step_name, result_json, created_at) VALUES(?,?,?,?,?)",
        (ctx.run_id, ctx.workstream_id, step_name, json.dumps(report, ensure_ascii=False), _utc_now()),
    )
    cur.execute(
        "INSERT INTO events(run_id, ws_id, event_type, payload_json, created_at) VALUES(?,?,?,?,?)",
        (
            ctx.run_id,
            ctx.workstream_id,
            "error_report_generated",
            json.dumps(
                {
                    "attempt_number": report.get("attempt_number"),
                    "ai_agent": report.get("ai_agent"),
                    "summary": report.get("summary", {}),
                },
                ensure_ascii=False,
            ),
            _utc_now(),
        ),
    )
    conn.commit()


def record_ai_attempt(conn: sqlite3.Connection, ctx: ErrorPipelineContext, attempt: Dict[str, Any]) -> None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events(run_id, ws_id, event_type, payload_json, created_at) VALUES(?,?,?,?,?)",
        (
            ctx.run_id,
            ctx.workstream_id,
            "ai_attempt",
            json.dumps(attempt, ensure_ascii=False),
            _utc_now(),
        ),
    )
    conn.commit()

