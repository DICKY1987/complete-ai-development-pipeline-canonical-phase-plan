"""Database layer for UET Framework - WS-03-01A

Provides SQLite backend for persisting run state, step attempts, and events.
Follows COOPERATION_SPEC state machine model.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import json


class Database:
    """SQLite database for framework state"""
    
    def __init__(self, db_path: str = ".ledger/framework.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Open database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self._initialize_schema()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _initialize_schema(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Runs table (RunRecord)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                workstream_id TEXT,
                execution_request_id TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                ended_at TEXT,
                state TEXT NOT NULL CHECK(state IN (
                    'pending', 'running', 'succeeded', 'failed', 
                    'quarantined', 'canceled'
                )),
                exit_code INTEGER,
                error_message TEXT,
                metadata TEXT
            )
        """)
        
        # Step attempts table (StepAttempt)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS step_attempts (
                step_attempt_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                tool_id TEXT NOT NULL,
                tool_run_id TEXT,
                execution_request_id TEXT,
                prompt_id TEXT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                state TEXT NOT NULL CHECK(state IN (
                    'running', 'succeeded', 'failed', 'canceled'
                )),
                exit_code INTEGER,
                input_prompt TEXT,
                output_patch_id TEXT,
                error_log TEXT,
                metadata TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(run_id)
            )
        """)
        
        # Run events table (RunEvent)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(run_id)
            )
        """)
        
        # Indices for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_project ON runs(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_state ON runs(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_steps_run ON step_attempts(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_run ON run_events(run_id)")
        
        self.conn.commit()
    
    # Run CRUD operations
    
    def create_run(self, run_data: Dict[str, Any]) -> str:
        """Create a new run record"""
        cursor = self.conn.cursor()
        
        # Serialize metadata if present
        metadata_json = json.dumps(run_data.get('metadata', {}))
        
        cursor.execute("""
            INSERT INTO runs (
                run_id, project_id, phase_id, workstream_id,
                execution_request_id, created_at, state, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data['run_id'],
            run_data['project_id'],
            run_data['phase_id'],
            run_data.get('workstream_id'),
            run_data.get('execution_request_id'),
            run_data['created_at'],
            run_data.get('state', 'pending'),
            metadata_json
        ))
        
        self.conn.commit()
        return run_data['run_id']
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a run record by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        # Convert Row to dict and deserialize metadata
        run_dict = dict(row)
        if run_dict.get('metadata'):
            run_dict['metadata'] = json.loads(run_dict['metadata'])
        
        return run_dict
    
    def update_run(self, run_id: str, updates: Dict[str, Any]):
        """Update run record fields"""
        cursor = self.conn.cursor()
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'run_id':
                continue  # Don't update primary key
            
            if key == 'metadata':
                value = json.dumps(value)
            
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if not set_clauses:
            return
        
        values.append(run_id)
        query = f"UPDATE runs SET {', '.join(set_clauses)} WHERE run_id = ?"
        
        cursor.execute(query, values)
        self.conn.commit()
    
    def delete_run(self, run_id: str):
        """Delete a run record (and cascading step attempts/events)"""
        cursor = self.conn.cursor()
        
        # Delete in correct order due to foreign keys
        cursor.execute("DELETE FROM run_events WHERE run_id = ?", (run_id,))
        cursor.execute("DELETE FROM step_attempts WHERE run_id = ?", (run_id,))
        cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
        
        self.conn.commit()
    
    def list_runs(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List runs with optional filters"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM runs"
        where_clauses = []
        values = []
        
        if filters:
            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                values.append(value)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        values.append(limit)
        
        cursor.execute(query, values)
        rows = cursor.fetchall()
        
        runs = []
        for row in rows:
            run_dict = dict(row)
            if run_dict.get('metadata'):
                run_dict['metadata'] = json.loads(run_dict['metadata'])
            runs.append(run_dict)
        
        return runs
    
    # Step attempt CRUD operations
    
    def create_step_attempt(self, step_data: Dict[str, Any]) -> str:
        """Create a new step attempt record"""
        cursor = self.conn.cursor()
        
        metadata_json = json.dumps(step_data.get('metadata', {}))
        
        cursor.execute("""
            INSERT INTO step_attempts (
                step_attempt_id, run_id, sequence, tool_id, tool_run_id,
                execution_request_id, prompt_id, started_at, state, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            step_data['step_attempt_id'],
            step_data['run_id'],
            step_data['sequence'],
            step_data['tool_id'],
            step_data.get('tool_run_id'),
            step_data.get('execution_request_id'),
            step_data.get('prompt_id'),
            step_data['started_at'],
            step_data.get('state', 'running'),
            metadata_json
        ))
        
        self.conn.commit()
        return step_data['step_attempt_id']
    
    def get_step_attempt(self, step_attempt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a step attempt by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM step_attempts WHERE step_attempt_id = ?", (step_attempt_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        step_dict = dict(row)
        if step_dict.get('metadata'):
            step_dict['metadata'] = json.loads(step_dict['metadata'])
        
        return step_dict
    
    def update_step_attempt(self, step_attempt_id: str, updates: Dict[str, Any]):
        """Update step attempt fields"""
        cursor = self.conn.cursor()
        
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'step_attempt_id':
                continue
            
            if key == 'metadata':
                value = json.dumps(value)
            
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if not set_clauses:
            return
        
        values.append(step_attempt_id)
        query = f"UPDATE step_attempts SET {', '.join(set_clauses)} WHERE step_attempt_id = ?"
        
        cursor.execute(query, values)
        self.conn.commit()
    
    def list_step_attempts(self, run_id: str) -> List[Dict[str, Any]]:
        """List all step attempts for a run"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM step_attempts 
            WHERE run_id = ? 
            ORDER BY sequence ASC
        """, (run_id,))
        
        rows = cursor.fetchall()
        
        steps = []
        for row in rows:
            step_dict = dict(row)
            if step_dict.get('metadata'):
                step_dict['metadata'] = json.loads(step_dict['metadata'])
            steps.append(step_dict)
        
        return steps
    
    # Event operations
    
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new run event"""
        cursor = self.conn.cursor()
        
        data_json = json.dumps(event_data.get('data', {}))
        
        cursor.execute("""
            INSERT INTO run_events (event_id, run_id, timestamp, event_type, data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event_data['event_id'],
            event_data['run_id'],
            event_data['timestamp'],
            event_data['event_type'],
            data_json
        ))
        
        self.conn.commit()
        return event_data['event_id']
    
    def list_events(self, run_id: str) -> List[Dict[str, Any]]:
        """List all events for a run"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM run_events 
            WHERE run_id = ? 
            ORDER BY timestamp ASC
        """, (run_id,))
        
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event_dict = dict(row)
            if event_dict.get('data'):
                event_dict['data'] = json.loads(event_dict['data'])
            events.append(event_dict)
        
        return events


# Singleton database instance
_db_instance: Optional[Database] = None


def get_db(db_path: str = ".ledger/framework.db") -> Database:
    """Get or create singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
        _db_instance.connect()
    return _db_instance


def init_db(db_path: str = ".ledger/framework.db") -> Database:
    """Initialize database and return instance"""
    db = Database(db_path)
    db.connect()
    return db
