"""Completion Handlers - Automated actions on run completion.

GAP-003 & GAP-005 Implementation: Auto-archival and auto-reporting
Pattern: EXEC-002 (Batch Validation) + Event-driven architecture
"""
# DOC_ID: DOC-PHASE7-COMPLETION-HANDLERS-002

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from core.events.event_bus import EventBus, Event
from core.planning.archive import auto_archive


class CompletionHandlers:
    """Event handlers triggered on run completion.
    
    Implements automated workflows:
    - Archival with validation (GAP-003, GAP-004)
    - Report generation (GAP-005)
    - Cleanup operations
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize completion handlers.
        
        Args:
            event_bus: Event bus for subscribing to events
        """
        self.event_bus = event_bus
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers with event bus."""
        # Subscribe to completion events
        self.event_bus.subscribe("run_completed", self.handle_archival)
        self.event_bus.subscribe("run_completed", self.handle_reporting)
        
        print("[CompletionHandlers] Registered handlers for run_completed events")
    
    def handle_archival(self, event: Event):
        """Automatically archive completed run with validation.
        
        Implements GAP-003 (auto-archival) and GAP-004 (validation).
        
        Args:
            event: Completion event with run_id and metrics
        """
        run_id = event.run_id
        print(f"[Archival] Processing run {run_id}")
        
        # Find run artifacts
        artifacts_path = Path(f".worktrees/{run_id}")
        
        if not artifacts_path.exists():
            print(f"[Archival] No artifacts found for run {run_id}")
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="archival_skipped",
                severity="info",
                data={"reason": "artifacts_not_found"}
            )
            return
        
        try:
            # Pre-flight validation: Check disk space
            archive_dest = Path(".archive")
            archive_dest.mkdir(exist_ok=True)
            
            required_space = self._calculate_dir_size(artifacts_path)
            available_space = shutil.disk_usage(archive_dest).free
            
            if available_space < required_space * 1.5:  # 50% buffer
                raise Exception(
                    f"Insufficient disk space: {available_space / 1e9:.1f}GB free, "
                    f"{required_space * 1.5 / 1e9:.1f}GB required"
                )
            
            print(f"[Archival] Archiving {required_space / 1e6:.1f}MB to .archive/")
            
            # Perform archival
            archive_path = auto_archive(artifacts_path, archive_dest)
            
            # Post-flight validation: Verify archive integrity
            if not archive_path.exists():
                raise Exception("Archive file was not created")
            
            if archive_path.stat().st_size == 0:
                raise Exception("Archive file is empty")
            
            # Test archive can be opened
            import zipfile
            with zipfile.ZipFile(archive_path, 'r') as zf:
                test_result = zf.testzip()
                if test_result is not None:
                    raise Exception(f"Archive corruption detected: {test_result}")
            
            print(f"[Archival] ✅ Archived to {archive_path} ({archive_path.stat().st_size / 1e6:.1f}MB)")
            
            # Update archival log in database
            self._log_archival(run_id, archive_path)
            
            # Emit success event
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="run_archived",
                severity="info",
                data={
                    "archive_path": str(archive_path),
                    "size_mb": archive_path.stat().st_size / 1e6
                }
            )
            
        except Exception as e:
            print(f"[Archival] ❌ Failed: {e}")
            
            # Emit failure event (triggers alert via GAP-002)
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="archival_failed",
                severity="error",
                data={"error": str(e)}
            )
    
    def handle_reporting(self, event: Event):
        """Automatically generate completion report.
        
        Implements GAP-005 (auto-reporting).
        
        Args:
            event: Completion event with run_id and metrics
        """
        run_id = event.run_id
        metrics = event.data.get("metrics", {})
        
        print(f"[Reporting] Generating report for run {run_id}")
        
        try:
            # Generate report
            report = {
                "run_id": run_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "status": metrics.get("status", "unknown"),
                "duration_seconds": metrics.get("duration_seconds"),
                "steps": {
                    "total": metrics.get("total_steps", 0),
                    "completed": metrics.get("completed_steps", 0),
                    "failed": metrics.get("failed_steps", 0)
                },
                "events": {
                    "total": metrics.get("total_events", 0),
                    "errors": metrics.get("error_events", 0)
                },
                "timestamps": {
                    "created": metrics.get("created_at"),
                    "started": metrics.get("started_at"),
                    "ended": metrics.get("ended_at")
                }
            }
            
            # Write JSON report
            report_dir = Path("reports")
            report_dir.mkdir(exist_ok=True)
            
            report_path = report_dir / f"{run_id}_summary.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"[Reporting] ✅ Report saved to {report_path}")
            
            # Emit success event
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="report_generated",
                severity="info",
                data={"report_path": str(report_path)}
            )
            
        except Exception as e:
            print(f"[Reporting] ❌ Failed: {e}")
            
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="reporting_failed",
                severity="warning",
                data={"error": str(e)}
            )
    
    def _calculate_dir_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes.
        
        Args:
            path: Directory path
            
        Returns:
            Total size in bytes
        """
        return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    
    def _log_archival(self, run_id: str, archive_path: Path):
        """Log archival operation to database.
        
        Args:
            run_id: Run ID
            archive_path: Path to archive file
        """
        try:
            # Get database connection from event bus
            db = self.event_bus.db
            cursor = db.conn.cursor()
            
            # Create archival_log table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS archival_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    archived_at TEXT NOT NULL,
                    size_bytes INTEGER,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Insert archival record
            cursor.execute("""
                INSERT INTO archival_log (run_id, archive_path, archived_at, size_bytes)
                VALUES (?, ?, ?, ?)
            """, (
                run_id,
                str(archive_path),
                datetime.utcnow().isoformat() + "Z",
                archive_path.stat().st_size
            ))
            
            db.conn.commit()
            
        except Exception as e:
            print(f"[Archival] WARNING: Failed to log to database: {e}")
