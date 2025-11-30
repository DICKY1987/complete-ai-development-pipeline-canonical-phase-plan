"""Client interfaces for UI components to query pipeline state.

This module provides read-only query interfaces for the TUI/GUI to access
pipeline state, metrics, and observability data without direct database access.
"""
DOC_ID: DOC-CORE-CORE-UI-CLIENTS-055
DOC_ID: DOC-CORE-CORE-UI-CLIENTS-032

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.core_state.m010003_db import get_connection
from core.ui_models import (
    ErrorCategory,
    ErrorRecord,
    ErrorSeverity,
    FileLifecycleRecord,
    FileRole,
    FileState,
    FileToolTouch,
    PipelineSummary,
    ToolCategory,
    ToolHealthMetrics,
    ToolHealthStatus,
    ToolStatus,
    ToolSummary,
    WorkstreamProgress,
    WorkstreamRecord,
    WorkstreamStatus,
)


class StateClient:
    """Read-only state queries for UI components."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
    
    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)
    
    # ========================================================================
    # File Lifecycle Queries
    # ========================================================================
    
    def get_file_lifecycle(self, file_id: str) -> Optional[FileLifecycleRecord]:
        """Get complete lifecycle record for a file."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT 
                    file_id, current_path, origin_path, file_role, current_state,
                    workstream_id, job_id, run_id, first_seen, last_processed,
                    committed_sha, committed_repo_path, quarantine_reason, 
                    quarantine_folder, metadata_json
                FROM file_lifecycle
                WHERE file_id = ?
            """, (file_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get state history
            cursor = conn.execute("""
                SELECT state, timestamp
                FROM file_state_history
                WHERE file_id = ?
                ORDER BY timestamp
            """, (file_id,))
            state_timestamps = {
                row[0]: datetime.fromisoformat(row[1])
                for row in cursor.fetchall()
            }
            
            # Get tool touches
            cursor = conn.execute("""
                SELECT tool_id, tool_name, action, status, error_message, timestamp
                FROM file_tool_touches
                WHERE file_id = ?
                ORDER BY timestamp
            """, (file_id,))
            tools_touched = [
                FileToolTouch(
                    timestamp=datetime.fromisoformat(touch[5]),
                    tool_id=touch[0],
                    tool_name=touch[1],
                    action=touch[2],
                    status=touch[3],
                    error_message=touch[4]
                )
                for touch in cursor.fetchall()
            ]
            
            metadata = json.loads(row[14]) if row[14] else {}
            
            return FileLifecycleRecord(
                file_id=row[0],
                current_path=row[1],
                origin_path=row[2],
                file_role=FileRole(row[3]) if row[3] else FileRole.OTHER,
                current_state=FileState(row[4]),
                workstream_id=row[5],
                job_id=row[6],
                run_id=row[7],
                first_seen=datetime.fromisoformat(row[8]) if row[8] else None,
                last_processed=datetime.fromisoformat(row[9]) if row[9] else None,
                committed_sha=row[10],
                committed_repo_path=row[11],
                quarantine_reason=row[12],
                quarantine_folder=row[13],
                state_timestamps=state_timestamps,
                tools_touched=tools_touched,
                last_error_code=metadata.get("last_error_code"),
                last_error_message=metadata.get("last_error_message"),
                last_error_plugin=metadata.get("last_error_plugin"),
            )
        finally:
            conn.close()
    
    def list_files(
        self,
        state: Optional[FileState] = None,
        workstream_id: Optional[str] = None,
        run_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        limit: int = 100
    ) -> List[FileLifecycleRecord]:
        """List files with optional filters."""
        conn = self._get_conn()
        try:
            sql = "SELECT file_id FROM file_lifecycle WHERE 1=1"
            params = []
            
            if state:
                sql += " AND current_state = ?"
                params.append(state.value)
            
            if workstream_id:
                sql += " AND workstream_id = ?"
                params.append(workstream_id)
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
            
            if tool_id:
                sql += """ AND file_id IN (
                    SELECT DISTINCT file_id FROM file_tool_touches
                    WHERE tool_id = ?
                )"""
                params.append(tool_id)
            
            sql += " ORDER BY last_processed DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(sql, params)
            file_ids = [row[0] for row in cursor.fetchall()]
            
            return [
                self.get_file_lifecycle(fid)
                for fid in file_ids
                if self.get_file_lifecycle(fid) is not None
            ]
        finally:
            conn.close()
    
    def get_file_counts_by_state(self, run_id: Optional[str] = None) -> Dict[str, int]:
        """Get count of files in each lifecycle state."""
        conn = self._get_conn()
        try:
            sql = """
                SELECT current_state, COUNT(*)
                FROM file_lifecycle
                WHERE 1=1
            """
            params = []
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
            
            sql += " GROUP BY current_state"
            
            cursor = conn.execute(sql, params)
            return dict(cursor.fetchall())
        finally:
            conn.close()
    
    # ========================================================================
    # Workstream Queries
    # ========================================================================
    
    def get_workstream(self, ws_id: str) -> Optional[WorkstreamRecord]:
        """Get complete workstream record."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT ws_id, run_id, status, created_at, updated_at, metadata_json
                FROM workstreams
                WHERE ws_id = ?
            """, (ws_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            metadata = json.loads(row[5]) if row[5] else {}
            
            # Count files
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN current_state = 'committed' THEN 1 ELSE 0 END) as succeeded,
                    SUM(CASE WHEN current_state = 'quarantined' THEN 1 ELSE 0 END) as quarantined
                FROM file_lifecycle
                WHERE workstream_id = ?
            """, (ws_id,))
            file_counts = cursor.fetchone()
            
            # Count tool invocations
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT id)
                FROM file_tool_touches
                WHERE file_id IN (
                    SELECT file_id FROM file_lifecycle WHERE workstream_id = ?
                )
            """, (ws_id,))
            tool_invocations = cursor.fetchone()[0] or 0
            
            start_time = datetime.fromisoformat(row[3]) if row[3] else None
            last_update = datetime.fromisoformat(row[4]) if row[4] else None
            duration = None
            if start_time and last_update:
                duration = (last_update - start_time).total_seconds()
            
            return WorkstreamRecord(
                ws_id=row[0],
                run_id=row[1],
                status=WorkstreamStatus(row[2]) if row[2] in [s.value for s in WorkstreamStatus] else WorkstreamStatus.PENDING,
                label=metadata.get("label"),
                description=metadata.get("description"),
                start_time=start_time,
                last_update=last_update,
                total_duration_sec=duration,
                files_processed=file_counts[0] or 0,
                files_succeeded=file_counts[1] or 0,
                files_quarantined=file_counts[2] or 0,
                total_tool_invocations=tool_invocations,
                worktree_path=metadata.get("worktree_path"),
                spec_path=metadata.get("spec_path"),
                workstream_json_path=metadata.get("workstream_json_path"),
            )
        finally:
            conn.close()
    
    def list_workstreams(
        self,
        run_id: Optional[str] = None,
        status: Optional[WorkstreamStatus] = None,
        limit: int = 100
    ) -> List[WorkstreamRecord]:
        """List workstreams with optional filters."""
        conn = self._get_conn()
        try:
            sql = "SELECT ws_id FROM workstreams WHERE 1=1"
            params = []
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
            
            if status:
                sql += " AND status = ?"
                params.append(status.value)
            
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(sql, params)
            ws_ids = [row[0] for row in cursor.fetchall()]
            
            return [
                self.get_workstream(ws_id)
                for ws_id in ws_ids
                if self.get_workstream(ws_id) is not None
            ]
        finally:
            conn.close()
    
    def get_workstream_counts_by_status(self, run_id: Optional[str] = None) -> Dict[str, int]:
        """Get count of workstreams by status."""
        conn = self._get_conn()
        try:
            sql = "SELECT status, COUNT(*) FROM workstreams WHERE 1=1"
            params = []
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
            
            sql += " GROUP BY status"
            
            cursor = conn.execute(sql, params)
            return dict(cursor.fetchall())
        finally:
            conn.close()
    
    # ========================================================================
    # Error Queries
    # ========================================================================
    
    def get_error_record(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error record by ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT 
                    error_id, entity_type, file_id, job_id, ws_id, tool_id, run_id,
                    plugin, severity, category, human_message, technical_details,
                    recommendation, first_seen, last_seen, occurrence_count,
                    quarantine_path, can_retry, auto_fix_available
                FROM error_records
                WHERE error_id = ?
            """, (error_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ErrorRecord(
                error_id=row[0],
                entity_type=row[1],
                file_id=row[2],
                job_id=row[3],
                ws_id=row[4],
                tool_id=row[5],
                run_id=row[6],
                plugin=row[7],
                severity=ErrorSeverity(row[8]) if row[8] else ErrorSeverity.ERROR,
                category=ErrorCategory(row[9]) if row[9] else ErrorCategory.UNKNOWN,
                human_message=row[10] or "",
                technical_details=row[11] or "",
                recommendation=row[12],
                first_seen=datetime.fromisoformat(row[13]) if row[13] else datetime.now(),
                last_seen=datetime.fromisoformat(row[14]) if row[14] else datetime.now(),
                occurrence_count=row[15] or 1,
                quarantine_path=row[16],
                can_retry=bool(row[17]),
                auto_fix_available=bool(row[18]),
            )
        finally:
            conn.close()
    
    def list_errors(
        self,
        run_id: Optional[str] = None,
        ws_id: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        tool_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ErrorRecord]:
        """List error records with optional filters."""
        conn = self._get_conn()
        try:
            sql = "SELECT error_id FROM error_records WHERE 1=1"
            params = []
            
            if run_id:
                sql += " AND run_id = ?"
                params.append(run_id)
            
            if ws_id:
                sql += " AND ws_id = ?"
                params.append(ws_id)
            
            if severity:
                sql += " AND severity = ?"
                params.append(severity.value)
            
            if category:
                sql += " AND category = ?"
                params.append(category.value)
            
            if tool_id:
                sql += " AND tool_id = ?"
                params.append(tool_id)
            
            sql += " ORDER BY last_seen DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(sql, params)
            error_ids = [row[0] for row in cursor.fetchall()]
            
            return [
                self.get_error_record(eid)
                for eid in error_ids
                if self.get_error_record(eid) is not None
            ]
        finally:
            conn.close()
    
    # ========================================================================
    # Dashboard Summary
    # ========================================================================
    
    def get_pipeline_summary(self, run_id: Optional[str] = None) -> PipelineSummary:
        """Get high-level pipeline summary for dashboard."""
        # Get workstream counts
        ws_counts = self.get_workstream_counts_by_status(run_id)
        
        # Get file counts
        file_counts = self.get_file_counts_by_state(run_id)
        
        # Calculate throughput (files/hour, jobs/hour)
        # This is simplified - real implementation would use time windows
        conn = self._get_conn()
        try:
            # Get files processed in last hour
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM file_lifecycle
                WHERE last_processed >= ?
            """ + (" AND run_id = ?" if run_id else ""),
                (one_hour_ago, run_id) if run_id else (one_hour_ago,))
            files_last_hour = cursor.fetchone()[0] or 0
            
            # Get errors in last hour
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM error_records
                WHERE last_seen >= ?
            """ + (" AND run_id = ?" if run_id else ""),
                (one_hour_ago, run_id) if run_id else (one_hour_ago,))
            errors_last_hour = cursor.fetchone()[0] or 0
            
            # Get top error types
            cursor = conn.execute("""
                SELECT category, COUNT(*)
                FROM error_records
                WHERE 1=1
            """ + (" AND run_id = ?" if run_id else "") + """
                GROUP BY category
                ORDER BY COUNT(*) DESC
                LIMIT 3
            """, (run_id,) if run_id else ())
            top_errors = [(row[0], row[1]) for row in cursor.fetchall()]
            
        finally:
            conn.close()
        
        return PipelineSummary(
            workstreams_running=ws_counts.get("running", 0),
            workstreams_queued=ws_counts.get("queued", 0) + ws_counts.get("pending", 0),
            workstreams_completed=ws_counts.get("completed", 0),
            workstreams_failed=ws_counts.get("failed", 0),
            files_intake=file_counts.get("intake", 0),
            files_classified=file_counts.get("classified", 0),
            # Combine in_flight and processing states as they both represent active work
            files_in_flight=file_counts.get("in_flight", 0) + file_counts.get("processing", 0),
            files_awaiting_review=file_counts.get("awaiting_review", 0),
            files_committed=file_counts.get("committed", 0),
            files_quarantined=file_counts.get("quarantined", 0),
            files_per_hour=float(files_last_hour),
            errors_per_hour=float(errors_last_hour),
            top_error_types=top_errors,
        )


class ToolsClient:
    """Tool health and status queries for UI components."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
    
    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)
    
    def get_tool_health(self, tool_id: str) -> Optional[ToolHealthStatus]:
        """Get health status for a tool."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT 
                    tool_id, display_name, category, version, status, status_reason,
                    last_successful_invocation, requests_5min, requests_15min, requests_60min,
                    success_count, failure_count, success_rate, mean_latency, p95_latency,
                    p99_latency, max_concurrency, current_in_flight, queue_length,
                    retry_count, time_since_last_failure, avg_output_size_bytes
                FROM tool_health_metrics
                WHERE tool_id = ?
            """, (tool_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            metrics = ToolHealthMetrics(
                requests_5min=row[7] or 0,
                requests_15min=row[8] or 0,
                requests_60min=row[9] or 0,
                success_count=row[10] or 0,
                failure_count=row[11] or 0,
                success_rate=row[12] or 0.0,
                mean_latency=row[13] or 0.0,
                p95_latency=row[14] or 0.0,
                p99_latency=row[15] or 0.0,
                max_concurrency=row[16] or 1,
                current_in_flight=row[17] or 0,
                queue_length=row[18] or 0,
                retry_count=row[19] or 0,
                time_since_last_failure=row[20],
                avg_output_size_bytes=row[21],
            )
            
            return ToolHealthStatus(
                tool_id=row[0],
                display_name=row[1],
                category=ToolCategory(row[2]) if row[2] else ToolCategory.OTHER,
                version=row[3],
                status=ToolStatus(row[4]) if row[4] else ToolStatus.UNKNOWN,
                status_reason=row[5],
                last_successful_invocation=datetime.fromisoformat(row[6]) if row[6] else None,
                metrics=metrics,
            )
        finally:
            conn.close()
    
    def list_tools(self) -> List[ToolHealthStatus]:
        """List all tools with health status."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT tool_id FROM tool_health_metrics")
            tool_ids = [row[0] for row in cursor.fetchall()]
            
            return [
                self.get_tool_health(tid)
                for tid in tool_ids
                if self.get_tool_health(tid) is not None
            ]
        finally:
            conn.close()
    
    def get_tools_summary(self) -> List[ToolSummary]:
        """Get one-line summary for all tools (for dashboard)."""
        tools = self.list_tools()
        return [
            ToolSummary(
                tool_id=tool.tool_id,
                tool_name=tool.display_name,
                status=tool.status,
                success_rate=tool.metrics.success_rate,
                p95_latency=tool.metrics.p95_latency,
            )
            for tool in tools
        ]


class LogsClient:
    """Event and log queries for UI components."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
    
    def query_events(
        self,
        run_id: Optional[str] = None,
        ws_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        file_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query events with flexible filters."""
        from modules.core_engine.m010001_event_bus import EventBus
        
        bus = EventBus()
        # This would use the enhanced query method
        # For now, return empty list as placeholder
        return []
    
    def export_logs(self, run_id: str, output_path: str) -> int:
        """Export logs for a run to JSON/JSONL file."""
        from modules.core_engine.m010001_event_bus import EventBus
        
        bus = EventBus()
        return bus.export_to_jsonl(output_path, run_id=run_id, limit=10000)
