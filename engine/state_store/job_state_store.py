"""
Job-centric state store implementation.

Wraps existing core/state/ DB operations with StateInterface protocol.
Provides a job-oriented API layer for the orchestrator and GUI while
maintaining compatibility with the existing workstream-based schema.

ADAPTER_ROLE: state_store
VERSION: 0.1.0
"""
DOC_ID: DOC-PAT-STATE-STORE-JOB-STATE-STORE-460

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from modules.core_state import m010003_db, crud
from engine.types import JobResult


class JobStateStore:
    """
    Implements StateInterface using existing pipeline database.
    
    Maps between job-centric API and workstream-based schema:
    - Jobs are stored as step_attempts with metadata
    - Job status tracked via step_attempts.status
    - Job results stored in step_attempts.result_json
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize state store.
        
        Args:
            db_path: Optional path to SQLite database
                    (defaults to state/pipeline_state.db)
        """
        self.db_path = db_path
        db.init_db(self.db_path)
    
    def create_run(self, ws_id: str, **kwargs) -> str:
        """
        Create a new run and return run_id.
        
        Args:
            ws_id: Workstream ID for this run
            **kwargs: Additional metadata
            
        Returns:
            Created run_id
        """
        # Generate run_id from timestamp if not provided
        run_id = kwargs.pop("run_id", None)
        if not run_id:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            run_id = f"run-{timestamp}"
        
        metadata = kwargs.pop("metadata", {})
        metadata["ws_id"] = ws_id
        metadata.update(kwargs)
        
        crud.create_run(run_id, status="pending", metadata=metadata, db_path=self.db_path)
        return run_id
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get run details by ID.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Run record as dictionary
        """
        return crud.get_run(run_id, db_path=self.db_path)
    
    def update_run_status(self, run_id: str, status: str) -> None:
        """
        Update run status.
        
        Args:
            run_id: Run identifier
            status: New status value
        """
        crud.update_run_status(run_id, status, db_path=self.db_path)
    
    def mark_job_running(self, job_id: str) -> None:
        """
        Mark a job as running (status transition).
        
        Jobs are stored as step_attempts with job_id in metadata.
        
        Args:
            job_id: Job identifier
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            # Find step_attempt by job_id in result_json
            cur.execute(
                """
                UPDATE step_attempts 
                SET status = 'running',
                    started_at = ?
                WHERE json_extract(result_json, '$.job_id') = ?
                """,
                (datetime.utcnow().isoformat() + "Z", job_id)
            )
            
            if cur.rowcount == 0:
                # Job not found, this is OK - it may not be in DB yet
                pass
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def update_job_result(self, job: Dict[str, Any], result: JobResult) -> None:
        """
        Update job with execution result.
        
        Creates or updates step_attempt record with job data and result.
        
        Args:
            job: Job dictionary (from job JSON)
            result: JobResult from adapter execution
        """
        job_id = job["job_id"]
        ws_id = job["workstream_id"]
        run_id = job.get("run_id", "default")
        tool = job["tool"]
        
        # Determine final status
        if result.success:
            status = "completed"
        elif result.exit_code == -1:  # timeout
            status = "timeout"
        else:
            status = "failed"
        
        # Prepare result data
        result_data = {
            "job_id": job_id,
            "exit_code": result.exit_code,
            "duration_s": result.duration_s,
            "success": result.success,
            "error_report_path": result.error_report_path,
            "stdout_preview": result.stdout[:500] if result.stdout else "",
            "stderr_preview": result.stderr[:500] if result.stderr else "",
            "metadata": result.metadata
        }
        
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            # Check if step_attempt already exists
            cur.execute(
                """
                SELECT id FROM step_attempts 
                WHERE json_extract(result_json, '$.job_id') = ?
                """,
                (job_id,)
            )
            existing = cur.fetchone()
            
            now = datetime.utcnow().isoformat() + "Z"
            
            if existing:
                # Update existing
                cur.execute(
                    """
                    UPDATE step_attempts
                    SET status = ?,
                        completed_at = ?,
                        result_json = ?
                    WHERE id = ?
                    """,
                    (status, now, json.dumps(result_data), existing[0])
                )
            else:
                # Create new step_attempt
                cur.execute(
                    """
                    INSERT INTO step_attempts 
                    (run_id, ws_id, step_name, status, started_at, completed_at, result_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (run_id, ws_id, tool, status, now, now, json.dumps(result_data))
                )
            
            conn.commit()
            
            # Record event
            self.record_event("job.completed", {
                "job_id": job_id,
                "ws_id": ws_id,
                "tool": tool,
                "status": status,
                "exit_code": result.exit_code,
                "duration_s": result.duration_s
            })
            
        finally:
            cur.close()
            conn.close()
    
    def list_jobs(self, run_id: str) -> List[Dict[str, Any]]:
        """
        List all jobs for a given run.
        
        Returns step_attempts as job records.
        
        Args:
            run_id: Run identifier
            
        Returns:
            List of job dictionaries
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute(
                """
                SELECT * FROM step_attempts 
                WHERE run_id = ?
                ORDER BY started_at DESC
                """,
                (run_id,)
            )
            
            jobs = []
            for row in cur.fetchall():
                job = dict(row)
                # Parse result_json if present
                if job.get("result_json"):
                    try:
                        job["result"] = json.loads(job["result_json"])
                        job["job_id"] = job["result"].get("job_id", f"job-{job['id']}")
                    except json.JSONDecodeError:
                        job["result"] = None
                        job["job_id"] = f"job-{job['id']}"
                else:
                    job["result"] = None
                    job["job_id"] = f"job-{job['id']}"
                
                jobs.append(job)
            
            return jobs
            
        finally:
            cur.close()
            conn.close()
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get job details by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job record dictionary
            
        Raises:
            ValueError: If job not found
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute(
                """
                SELECT * FROM step_attempts 
                WHERE json_extract(result_json, '$.job_id') = ?
                """,
                (job_id,)
            )
            
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Job not found: {job_id}")
            
            job = dict(row)
            if job.get("result_json"):
                try:
                    job["result"] = json.loads(job["result_json"])
                except json.JSONDecodeError:
                    job["result"] = None
            
            return job
            
        finally:
            cur.close()
            conn.close()
    
    def record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Record an event to the event log.
        
        Args:
            event_type: Event type identifier
            payload: Event data
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            run_id = payload.get("run_id")
            ws_id = payload.get("ws_id")
            
            cur.execute(
                """
                INSERT INTO events (timestamp, run_id, ws_id, event_type, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, run_id, ws_id, event_type, json.dumps(payload))
            )
            conn.commit()
            
        finally:
            cur.close()
            conn.close()
    
    def list_workstreams(self, run_id: str) -> List[Dict[str, Any]]:
        """
        List all workstreams for a given run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            List of workstream dictionaries
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute(
                """
                SELECT * FROM workstreams 
                WHERE run_id = ?
                ORDER BY created_at DESC
                """,
                (run_id,)
            )
            
            workstreams = []
            for row in cur.fetchall():
                ws = dict(row)
                if ws.get("metadata_json"):
                    try:
                        ws["metadata"] = json.loads(ws["metadata_json"])
                        del ws["metadata_json"]
                    except json.JSONDecodeError:
                        ws["metadata"] = None
                
                workstreams.append(ws)
            
            return workstreams
            
        finally:
            cur.close()
            conn.close()
    
    def get_workstream(self, ws_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workstream details by ID.
        
        Args:
            ws_id: Workstream identifier
            
        Returns:
            Workstream dictionary or None if not found
        """
        conn = db.get_connection(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT * FROM workstreams WHERE ws_id = ?", (ws_id,))
            row = cur.fetchone()
            
            if row is None:
                return None
            
            ws = dict(row)
            if ws.get("metadata_json"):
                try:
                    ws["metadata"] = json.loads(ws["metadata_json"])
                    del ws["metadata_json"]
                except json.JSONDecodeError:
                    ws["metadata"] = None
            
            return ws
            
        finally:
            cur.close()
            conn.close()
    
    def list_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent runs (for GUI dashboard).
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of run dictionaries
        """
        return crud.list_runs(limit=limit, db_path=self.db_path)
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Status string (queued, running, completed, failed, timeout)
        """
        try:
            job = self.get_job(job_id)
            return job.get("status", "unknown")
        except ValueError:
            return "not_found"
