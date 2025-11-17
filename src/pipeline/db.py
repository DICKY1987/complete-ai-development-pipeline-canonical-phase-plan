from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from .error_context import ErrorPipelineContext
from . import db_sqlite


# If a SQLite DB is present or ERROR_PIPELINE_DB is set, prefer SQLite; otherwise use file JSON.
BASE = Path(".state") / "error_pipeline"
DB_PATH = Path(os.getenv("ERROR_PIPELINE_DB", BASE.parent / "pipeline.db"))


def _use_sqlite() -> bool:
    # Prefer sqlite if the env var is set or the DB file exists
    return bool(os.getenv("ERROR_PIPELINE_DB")) or DB_PATH.exists()


# File-based fallback paths
def _ctx_path(run_id: str, ws_id: str) -> Path:
    return BASE / run_id / ws_id / "context.json"


def _reports_dir(run_id: str, ws_id: str) -> Path:
    return BASE / run_id / ws_id / "error_reports"


def get_error_context(run_id: str, ws_id: str) -> ErrorPipelineContext:
    if _use_sqlite():
        conn = db_sqlite.open_db(DB_PATH)
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
    if _use_sqlite():
        conn = db_sqlite.open_db(DB_PATH)
        try:
            db_sqlite.save_error_context(conn, ctx)
        finally:
            conn.close()
        return
    p = _ctx_path(ctx.run_id, ctx.workstream_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ctx.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")


def record_error_report(ctx: ErrorPipelineContext, report: Dict[str, Any], step_name: str) -> Path:
    if _use_sqlite():
        conn = db_sqlite.open_db(DB_PATH)
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
    if _use_sqlite():
        conn = db_sqlite.open_db(DB_PATH)
        try:
            db_sqlite.record_ai_attempt(conn, ctx, attempt)
        finally:
            conn.close()
