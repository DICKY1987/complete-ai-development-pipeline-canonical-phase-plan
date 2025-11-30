"""SQLite State Store - Concrete implementation of StateStore protocol."""

from __future__ import annotations

import sqlite3
import json
from typing import Optional, Any
from datetime import datetime
from pathlib import Path
import uuid

from core.interfaces.state_store import (
    StateStore,
    WorkstreamNotFoundError,
    ExecutionNotFoundError,
)


class SQLiteStateStore:
    """Concrete StateStore implementation using SQLite."""
# DOC_ID: DOC-CORE-STATE-SQLITE-STORE-111
    
    def __init__(self, db_path: str | Path = ".state/pipeline.db"):
        """Initialize SQLiteStateStore."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _init_schema(self) -> None:
        """Initialize database schema if not exists."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workstreams (
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    run_id TEXT,
                    data TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    ws_id TEXT,
                    status TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    exit_code INTEGER,
                    data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    payload TEXT,
                    created_at TEXT
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def get_workstream(self, ws_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a workstream by ID."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        try:
            row = conn.execute(
                "SELECT * FROM workstreams WHERE id = ?",
                (ws_id,)
            ).fetchone()
            
            if not row:
                return None
            
            data = json.loads(row['data']) if row['data'] else {}
            return {
                'id': row['id'],
                'status': row['status'],
                'run_id': row['run_id'],
                **data,
            }
        finally:
            conn.close()
    
    def save_workstream(self, workstream: dict[str, Any]) -> None:
        """Save or update a workstream."""
        if 'id' not in workstream:
            raise ValueError("Workstream must have 'id' field")
        
        ws_id = workstream['id']
        status = workstream.get('status', 'pending')
        run_id = workstream.get('run_id')
        
        data = {k: v for k, v in workstream.items() 
                if k not in ['id', 'status', 'run_id']}
        
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            now = datetime.now().isoformat()
            
            cursor = conn.execute(
                """UPDATE workstreams 
                   SET status = ?, run_id = ?, data = ?, updated_at = ?
                   WHERE id = ?""",
                (status, run_id, json.dumps(data), now, ws_id)
            )
            
            if cursor.rowcount == 0:
                conn.execute(
                    """INSERT INTO workstreams (id, status, run_id, data, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (ws_id, status, run_id, json.dumps(data), now, now)
                )
            
            conn.commit()
        finally:
            conn.close()
    
    def list_workstreams(
        self,
        *,
        status: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List workstreams with optional filtering."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        try:
            query = "SELECT * FROM workstreams WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if run_id:
                query += " AND run_id = ?"
                params.append(run_id)
            
            rows = conn.execute(query, params).fetchall()
            
            result = []
            for row in rows:
                data = json.loads(row['data']) if row['data'] else {}
                result.append({
                    'id': row['id'],
                    'status': row['status'],
                    'run_id': row['run_id'],
                    **data,
                })
            
            return result
        finally:
            conn.close()
    
    def record_execution(self, execution: dict[str, Any]) -> str:
        """Record a job execution."""
        exec_id = execution.get('id', str(uuid.uuid4()))
        run_id = execution.get('run_id')
        ws_id = execution.get('ws_id')
        status = execution.get('status', 'pending')
        started_at = execution.get('started_at', datetime.now()).isoformat()
        
        data = {k: v for k, v in execution.items() 
                if k not in ['id', 'run_id', 'ws_id', 'status', 'started_at']}
        
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            conn.execute(
                """INSERT INTO executions (id, run_id, ws_id, status, started_at, data)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (exec_id, run_id, ws_id, status, started_at, json.dumps(data))
            )
            conn.commit()
            return exec_id
        finally:
            conn.close()
    
    def list_executions(
        self,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """List executions with optional filtering."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        try:
            query = "SELECT * FROM executions WHERE 1=1"
            params = []
            
            if filters:
                if 'status' in filters:
                    query += " AND status = ?"
                    params.append(filters['status'])
                
                if 'run_id' in filters:
                    query += " AND run_id = ?"
                    params.append(filters['run_id'])
                
                if 'ws_id' in filters:
                    query += " AND ws_id = ?"
                    params.append(filters['ws_id'])
            
            rows = conn.execute(query, params).fetchall()
            
            result = []
            for row in rows:
                data = json.loads(row['data']) if row['data'] else {}
                result.append({
                    'id': row['id'],
                    'run_id': row['run_id'],
                    'ws_id': row['ws_id'],
                    'status': row['status'],
                    'started_at': row['started_at'],
                    'completed_at': row['completed_at'],
                    'exit_code': row['exit_code'],
                    **data,
                })
            
            return result
        finally:
            conn.close()
    
    def update_execution_status(
        self,
        exec_id: str,
        status: str,
        *,
        completed_at: Optional[datetime] = None,
        exit_code: Optional[int] = None,
    ) -> None:
        """Update execution status."""
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            completed_at_str = completed_at.isoformat() if completed_at else None
            
            cursor = conn.execute(
                """UPDATE executions 
                   SET status = ?, completed_at = ?, exit_code = ?
                   WHERE id = ?""",
                (status, completed_at_str, exit_code, exec_id)
            )
            
            if cursor.rowcount == 0:
                raise ExecutionNotFoundError(exec_id)
            
            conn.commit()
        finally:
            conn.close()
    
    def record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Record a pipeline event."""
        event_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            conn.execute(
                """INSERT INTO events (id, event_type, payload, created_at)
                   VALUES (?, ?, ?, ?)""",
                (event_id, event_type, json.dumps(payload), created_at)
            )
            conn.commit()
        finally:
            conn.close()
