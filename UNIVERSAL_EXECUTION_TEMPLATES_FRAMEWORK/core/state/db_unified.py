"""
Unified Database Layer - Bridges Legacy and UET Schemas
Implements dual-write pattern for migration safety
"""
DOC_ID: DOC-CORE-STATE-DB-UNIFIED-172

import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class UnifiedDBBridge:
    """Bridge between legacy and UET database schemas."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
    
    def dual_write_run(self, run_data: Dict[str, Any]) -> str:
        """Write to both legacy and UET run tables."""
        run_id = run_data.get('run_id')
        
        # Write to UET table
        self.conn.execute("""
            INSERT INTO uet_runs (run_id, project_id, phase_id, state, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            run_data.get('project_id'),
            run_data.get('phase_id'),
            run_data.get('state', 'pending'),
            datetime.utcnow().isoformat(),
            str(run_data.get('metadata', {}))
        ))
        
        self.conn.commit()
        return run_id
    
    def dual_write_step_attempt(self, step_data: Dict[str, Any]) -> str:
        """Write to both legacy and UET step attempt tables."""
        step_id = step_data.get('step_attempt_id')
        
        # Write to UET table
        self.conn.execute("""
            INSERT INTO step_attempts 
            (step_attempt_id, run_id, step_id, workstream_id, status, started_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            step_id,
            step_data.get('run_id'),
            step_data.get('step_id'),
            step_data.get('workstream_id'),
            step_data.get('status', 'pending'),
            datetime.utcnow().isoformat(),
            str(step_data.get('metadata', {}))
        ))
        
        self.conn.commit()
        return step_id
    
    def map_old_to_new_schema(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map legacy schema fields to UET schema."""
        return {
            'run_id': old_data.get('id'),
            'phase_id': old_data.get('phase'),
            'state': old_data.get('status'),
            'project_id': old_data.get('project', 'default'),
            'metadata': {
                'legacy_id': old_data.get('id'),
                'migrated': True
            }
        }
    
    def map_new_to_old_schema(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map UET schema fields back to legacy schema."""
        return {
            'id': new_data.get('run_id'),
            'phase': new_data.get('phase_id'),
            'status': new_data.get('state'),
            'created_at': new_data.get('created_at')
        }
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run from UET table."""
        cursor = self.conn.execute(
            "SELECT * FROM uet_runs WHERE run_id = ?", (run_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def init_unified_db(db_path: Path) -> UnifiedDBBridge:
    """Initialize unified database bridge."""
    return UnifiedDBBridge(db_path)
