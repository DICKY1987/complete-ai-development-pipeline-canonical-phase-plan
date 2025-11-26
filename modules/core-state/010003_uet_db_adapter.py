"""UET Database Adapter - Migration Compatibility Layer

Adapts the functional database API in core.state.db to match
the class-based API expected by UET modules.
"""

from typing import Dict, Any, Optional, List
import sqlite3
from pathlib import Path

from modules.core_state import get_connection


class Database:
    """Database adapter providing UET-compatible API"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.conn = get_connection(db_path)
        self._ensure_uet_schema()
    
    def _ensure_uet_schema(self):
        """Ensure UET tables exist"""
        migration_sql = Path("schema/migrations/001_uet_unified_schema.sql")
        if migration_sql.exists():
            self.conn.executescript(migration_sql.read_text(encoding="utf-8"))
            self.conn.commit()
    
    # Run operations
    def create_run(self, run_data: Dict[str, Any]) -> str:
        """Create a new run record"""
        cursor = self.conn.execute(
            """INSERT INTO uet_executions 
               (execution_id, phase_name, status, metadata)
               VALUES (?, ?, ?, ?)""",
            (
                run_data['run_id'],
                run_data.get('phase_id', ''),
                run_data.get('status', 'pending'),
                str(run_data.get('metadata', {}))
            )
        )
        self.conn.commit()
        return run_data['run_id']
    
    def update_run(self, run_id: str, updates: Dict[str, Any]):
        """Update run record"""
        set_clauses = []
        values = []
        for key, val in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(str(val) if isinstance(val, dict) else val)
        
        values.append(run_id)
        sql = f"UPDATE uet_executions SET {', '.join(set_clauses)} WHERE execution_id = ?"
        self.conn.execute(sql, values)
        self.conn.commit()
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM uet_executions WHERE execution_id = ?",
            (run_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Task operations
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task"""
        cursor = self.conn.execute(
            """INSERT INTO uet_tasks 
               (task_id, execution_id, task_type, dependencies, status, result)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                task_data['task_id'],
                task_data['execution_id'],
                task_data.get('task_type', ''),
                str(task_data.get('dependencies', [])),
                task_data.get('status', 'pending'),
                str(task_data.get('result', {}))
            )
        )
        self.conn.commit()
        return task_data['task_id']
    
    def update_task(self, task_id: str, updates: Dict[str, Any]):
        """Update task record"""
        set_clauses = []
        values = []
        for key, val in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(str(val) if isinstance(val, (dict, list)) else val)
        
        values.append(task_id)
        sql = f"UPDATE uet_tasks SET {', '.join(set_clauses)} WHERE task_id = ?"
        self.conn.execute(sql, values)
        self.conn.commit()
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM uet_tasks WHERE task_id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_tasks(self, execution_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks for execution"""
        if status:
            cursor = self.conn.execute(
                "SELECT * FROM uet_tasks WHERE execution_id = ? AND status = ?",
                (execution_id, status)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM uet_tasks WHERE execution_id = ?",
                (execution_id,)
            )
        return [dict(row) for row in cursor.fetchall()]
    
    # Event operations (no-op for migration - events optional)
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create event (no-op for now - events are optional)"""
        # Events can be logged to telemetry instead
        return event_data.get('event_id', 'evt_noop')
    
    def list_events(self, run_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List events (no-op)"""
        return []
    
    # Patch ledger operations
    def create_patch(self, patch_data: Dict[str, Any]) -> str:
        """Create patch record"""
        cursor = self.conn.execute(
            """INSERT INTO patch_ledger 
               (patch_id, execution_id, state, patch_content, validation_result, metadata)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                patch_data['patch_id'],
                patch_data.get('execution_id', ''),
                patch_data.get('state', 'created'),
                patch_data.get('patch_content', ''),
                str(patch_data.get('validation_result', {})),
                str(patch_data.get('metadata', {}))
            )
        )
        self.conn.commit()
        return patch_data['patch_id']
    
    def update_patch(self, patch_id: str, updates: Dict[str, Any]):
        """Update patch record"""
        set_clauses = []
        values = []
        for key, val in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(str(val) if isinstance(val, dict) else val)
        
        values.append(patch_id)
        sql = f"UPDATE patch_ledger SET {', '.join(set_clauses)} WHERE patch_id = ?"
        self.conn.execute(sql, values)
        self.conn.commit()
    
    def get_patch(self, patch_id: str) -> Optional[Dict[str, Any]]:
        """Get patch by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM patch_ledger WHERE patch_id = ?",
            (patch_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_patches(self, execution_id: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List patches"""
        if execution_id and state:
            cursor = self.conn.execute(
                "SELECT * FROM patch_ledger WHERE execution_id = ? AND state = ?",
                (execution_id, state)
            )
        elif execution_id:
            cursor = self.conn.execute(
                "SELECT * FROM patch_ledger WHERE execution_id = ?",
                (execution_id,)
            )
        elif state:
            cursor = self.conn.execute(
                "SELECT * FROM patch_ledger WHERE state = ?",
                (state,)
            )
        else:
            cursor = self.conn.execute("SELECT * FROM patch_ledger ORDER BY created_at DESC LIMIT 100")
        return [dict(row) for row in cursor.fetchall()]
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute raw SQL"""
        return self.conn.execute(sql, params)
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def close(self):
        """Close connection"""
        self.conn.close()


def get_db(db_path: Optional[str] = None) -> Database:
    """Get Database instance (UET-compatible)"""
    return Database(db_path)
