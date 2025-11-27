from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from modules.error_engine import ErrorPipelineContext
from . import db_sqlite


# ---------------------------
# Connection and schema (CRUD)
# ---------------------------

def _resolve_db_path(db_path: Optional[str]) -> Path:
    """Resolve the SQLite DB path.

    Priority:
    1) explicit db_path
    2) env PIPELINE_DB_PATH (preferred)
    3) env ERROR_PIPELINE_DB (legacy)
    4) default: .worktrees/pipeline_state.db
    """
    if db_path:
        return Path(db_path).expanduser().resolve()
    env = os.getenv("PIPELINE_DB_PATH") or os.getenv("ERROR_PIPELINE_DB")
    if env:
        return Path(env).expanduser().resolve()
    return (Path(".worktrees") / "pipeline_state.db").resolve()


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys and row factory enabled."""
    p = _resolve_db_path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> None:
    """Initialize the database by applying `schema/schema.sql` (idempotent)."""
    conn = get_connection(db_path)
    try:
        schema_file = Path(schema_path) if schema_path else Path("schema") / "schema.sql"
        if schema_file.exists():
            sql = schema_file.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.commit()
    finally:
        conn.close()


# -----------------------------
# Error pipeline context helpers
# -----------------------------

# Keep compatibility with the error context subsystem (separate storage path)
_EP_BASE = Path(".state") / "error_pipeline"
_EP_DB = Path(os.getenv("ERROR_PIPELINE_DB", _EP_BASE.parent / "pipeline.db"))


def _ep_use_sqlite() -> bool:
    return bool(os.getenv("ERROR_PIPELINE_DB")) or _EP_DB.exists()


def _ctx_path(run_id: str, ws_id: str) -> Path:
    return _EP_BASE / run_id / ws_id / "context.json"


def _reports_dir(run_id: str, ws_id: str) -> Path:
    return _EP_BASE / run_id / ws_id / "error_reports"


def get_error_context(run_id: str, ws_id: str) -> ErrorPipelineContext:
    if _ep_use_sqlite():
        conn = db_sqlite.open_db(_EP_DB)
        try:
            return db_sqlite.get_error_context(conn, run_id, ws_id)
        finally:
            conn.close()
    p = _ctx_path(run_id, ws_id)
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        return ErrorPipelineContext.from_json(data)
    ctx = ErrorPipelineContext(run_id=run_id, workstream_id=ws_id)
    save_error_context(ctx)
    return ctx


def save_error_context(ctx: ErrorPipelineContext) -> None:
    if _ep_use_sqlite():
        conn = db_sqlite.open_db(_EP_DB)
        try:
            db_sqlite.save_error_context(conn, ctx)
        finally:
            conn.close()
        return
    p = _ctx_path(ctx.run_id, ctx.workstream_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ctx.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")


def record_error_report(ctx: ErrorPipelineContext, report: Dict[str, Any], step_name: str) -> Path:
    if _ep_use_sqlite():
        conn = db_sqlite.open_db(_EP_DB)
        try:
            db_sqlite.record_error_report(conn, ctx, report, step_name)
        finally:
            conn.close()
    d = _reports_dir(ctx.run_id, ctx.workstream_id)
    d.mkdir(parents=True, exist_ok=True)
    name = f"error_report_attempt_{ctx.attempt_number}.json"
    p = d / name
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def record_ai_attempt(ctx: ErrorPipelineContext, attempt: Dict[str, Any]) -> None:
    ctx.record_ai_attempt(attempt)
    save_error_context(ctx)
    if _ep_use_sqlite():
        conn = db_sqlite.open_db(_EP_DB)
        try:
            db_sqlite.record_ai_attempt(conn, ctx, attempt)
        finally:
            conn.close()


# ----------------------
# CRUD re-export facade
# ----------------------

# Re-export CRUD operations so callers can import `db` consistently
# ----------------------
# Phase I: Event helpers for monitoring
# ----------------------

def get_recent_events(limit: int = 20, db_path: Optional[str] = None) -> list[dict]:
    """Get recent events for monitoring."""
    from .m010003_crud import get_events

    return get_events(limit=limit, db_path=db_path)


def get_all_events(db_path: Optional[str] = None) -> list[dict]:
    """Get all events."""
    from .m010003_crud import get_events

    return get_events(limit=10000, db_path=db_path)


def get_events_since(last_event_id: int, db_path: Optional[str] = None) -> list[dict]:
    """Get events since a specific ID."""
    from .m010003_crud import get_events

    conn = get_connection(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT * FROM events WHERE id > ? ORDER BY id ASC",
            (last_event_id,)
        )
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            if result.get("payload_json"):
                import json
                result["payload"] = json.loads(result["payload_json"])
                del result["payload_json"]
            else:
                result["payload"] = None
            results.append(result)
        
        return results
    
    finally:
        cur.close()
        conn.close()
