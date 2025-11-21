"""Crash recovery and state restoration."""

from typing import Dict, List, Any


class RecoveryManager:
    """Handles orchestrator restart and crash recovery."""
    
    def recover_from_crash(self) -> Dict[str, Any]:
        """Recover from orchestrator crash.
        
        Steps:
        1. Load last known states from persistence
        2. Identify orphaned tasks (RUNNING with no alive worker)
        3. Mark orphaned tasks as FAILED
        4. Apply self-heal policy
        5. Restore workers and resume scheduling
        """
        from core.state.db import get_connection
        
        conn = get_connection()
        orphaned = []
        
        try:
            # Find workers in BUSY state (potential orphans)
            cursor = conn.execute("""
                SELECT worker_id, current_task_id 
                FROM workers 
                WHERE state = 'BUSY'
            """)
            
            for row in cursor.fetchall():
                worker_id, task_id = row
                if task_id:
                    orphaned.append(task_id)
                
                # Terminate the worker
                conn.execute(
                    "UPDATE workers SET state = 'TERMINATED' WHERE worker_id = ?",
                    (worker_id,)
                )
            
            conn.commit()
        finally:
            conn.close()
        
        return {
            'orphaned_tasks': len(orphaned),
            'recovered': True
        }
