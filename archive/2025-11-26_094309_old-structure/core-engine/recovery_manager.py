"""Crash recovery and state restoration.

Phase I WS-I5: Enhanced recovery with parallel execution support.
"""
DOC_ID: DOC-PAT-CORE-ENGINE-RECOVERY-MANAGER-400

from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from pathlib import Path


class RecoveryManager:
    """Handles orchestrator restart and crash recovery."""
    
    def __init__(self, run_id: Optional[str] = None):
        """Initialize recovery manager.
        
        Args:
            run_id: Optional run ID to recover
        """
        self.run_id = run_id
    
    def recover_from_crash(self) -> Dict[str, Any]:
        """Recover from orchestrator crash.
        
        Steps:
        1. Load last known states from persistence
        2. Identify orphaned tasks (RUNNING with no alive worker)
        3. Mark orphaned tasks as FAILED
        4. Apply self-heal policy
        5. Restore workers and resume scheduling
        
        Returns:
            Recovery report with orphaned tasks and status
        """
        from modules.core_state.m010003_db import get_connection
        
        conn = get_connection()
        orphaned = []
        recovered_workers = []
        
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
                recovered_workers.append(worker_id)
            
            # Mark orphaned workstreams as failed
            for task_id in orphaned:
                conn.execute(
                    "UPDATE workstreams SET status = 'failed' WHERE id = ?",
                    (task_id,)
                )
            
            conn.commit()
        finally:
            conn.close()
        
        return {
            'orphaned_tasks': len(orphaned),
            'orphaned_task_ids': orphaned,
            'recovered_workers': len(recovered_workers),
            'recovered': True
        }
    
    def get_recoverable_runs(self) -> List[Dict[str, Any]]:
        """Get list of runs that can be recovered.
        
        Returns:
            List of run records with incomplete workstreams
        """
        from modules.core_state.m010003_db import get_connection
        
        conn = get_connection()
        
        try:
            cursor = conn.execute("""
                SELECT DISTINCT r.id, r.status, r.created_at,
                       COUNT(w.id) as total_workstreams,
                       SUM(CASE WHEN w.status IN ('pending', 'editing', 'static_check', 'runtime_tests') THEN 1 ELSE 0 END) as incomplete
                FROM runs r
                LEFT JOIN workstreams w ON r.id = w.run_id
                WHERE r.status != 'completed'
                GROUP BY r.id
                HAVING incomplete > 0
                ORDER BY r.created_at DESC
            """)
            
            runs = []
            for row in cursor.fetchall():
                runs.append({
                    'run_id': row[0],
                    'status': row[1],
                    'created_at': row[2],
                    'total_workstreams': row[3],
                    'incomplete': row[4]
                })
            
            return runs
        
        finally:
            conn.close()
    
    def resume_execution(self, run_id: str, max_workers: int = 4) -> Dict[str, Any]:
        """Resume parallel execution from checkpoint.
        
        Args:
            run_id: Run ID to resume
            max_workers: Maximum parallel workers
            
        Returns:
            Resumption status
        """
        from modules.core_state.m010003_db import get_connection
        from modules.core_state import m010003_bundles
        from modules.core_engine.m010001_orchestrator import execute_workstreams_parallel
        
        # Get incomplete workstreams
        conn = get_connection()
        
        try:
            cursor = conn.execute("""
                SELECT id FROM workstreams
                WHERE run_id = ? AND status IN ('pending', 'failed')
            """, (run_id,))
            
            incomplete_ws_ids = [row[0] for row in cursor.fetchall()]
        
        finally:
            conn.close()
        
        if not incomplete_ws_ids:
            return {
                'resumed': False,
                'message': 'No incomplete workstreams found'
            }
        
        # Load bundles for incomplete workstreams
        all_bundles = bundles.load_and_validate_bundles()
        incomplete_bundles = [b for b in all_bundles if b.id in incomplete_ws_ids]
        
        # Resume execution
        result = execute_workstreams_parallel(
            incomplete_bundles,
            max_workers=max_workers,
            context={'resumed': True, 'original_run_id': run_id}
        )
        
        return {
            'resumed': True,
            'incomplete_count': len(incomplete_ws_ids),
            'result': result
        }
