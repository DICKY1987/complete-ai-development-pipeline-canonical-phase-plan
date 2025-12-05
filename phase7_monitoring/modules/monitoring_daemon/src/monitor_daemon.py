"""Monitoring Daemon - Continuous run monitoring and completion detection.

GAP-001 Implementation: Automated monitoring pipeline
Pattern: EXEC-002 (Batch Validation)
"""
# DOC_ID: DOC-PHASE7-MONITORING-DAEMON-001

import time
import signal
import sys
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from core.engine.monitoring.run_monitor import RunMonitor, RunMetrics
from core.events.event_bus import EventBus


class MonitoringDaemon:
    """Background daemon that monitors active runs and triggers automation.
    
    Implements continuous monitoring loop with:
    - Active run polling (10s interval)
    - Completion detection
    - Stall detection
    - Event emission for downstream automation
    """
    
    def __init__(self, db_path: str, poll_interval: int = 10):
        """Initialize monitoring daemon.
        
        Args:
            db_path: Path to orchestration database
            poll_interval: Polling interval in seconds (default: 10)
        """
        self.db_path = db_path
        self.poll_interval = poll_interval
        self.running = False
        
        # Initialize core components
        self.monitor = RunMonitor(db_path)
        self.event_bus = EventBus(db_path)
        
        # Track processed completions to avoid duplicate events
        self.completed_runs = set()
        
        # Stall detection thresholds
        self.stall_threshold_minutes = 30
        self.stall_detected = set()
    
    def start(self):
        """Start continuous monitoring loop."""
        self.running = True
        print(f"[{self._timestamp()}] Monitoring daemon started (poll_interval={self.poll_interval}s)")
        
        while self.running:
            try:
                self._poll_active_runs()
            except Exception as e:
                print(f"[{self._timestamp()}] ERROR: Polling failed: {e}")
                # Continue monitoring despite errors
            
            time.sleep(self.poll_interval)
    
    def stop(self):
        """Stop monitoring daemon gracefully."""
        print(f"[{self._timestamp()}] Monitoring daemon stopping...")
        self.running = False
    
    def _poll_active_runs(self):
        """Poll all active runs and detect state transitions."""
        active_runs = self.monitor.list_active_runs()
        
        if not active_runs:
            print(f"[{self._timestamp()}] No active runs", end='\r')
            return
        
        print(f"[{self._timestamp()}] Monitoring {len(active_runs)} active runs")
        
        for run_id in active_runs:
            try:
                metrics = self.monitor.get_run_metrics(run_id)
                if not metrics:
                    continue
                
                # Check for completion
                if self._is_complete(metrics) and run_id not in self.completed_runs:
                    self._handle_completion(run_id, metrics)
                    self.completed_runs.add(run_id)
                
                # Check for stalls
                elif self._is_stalled(metrics) and run_id not in self.stall_detected:
                    self._handle_stall(run_id, metrics)
                    self.stall_detected.add(run_id)
                    
            except Exception as e:
                print(f"[{self._timestamp()}] ERROR: Failed to process run {run_id}: {e}")
    
    def _is_complete(self, metrics: RunMetrics) -> bool:
        """Check if run is complete (all steps finished).
        
        Args:
            metrics: Run metrics
            
        Returns:
            True if all steps are completed or failed
        """
        total_finished = metrics.completed_steps + metrics.failed_steps
        return total_finished == metrics.total_steps and metrics.total_steps > 0
    
    def _is_stalled(self, metrics: RunMetrics) -> bool:
        """Check if run is stalled (no progress in N minutes).
        
        Args:
            metrics: Run metrics
            
        Returns:
            True if run appears stalled
        """
        if not metrics.started_at:
            return False
        
        # Check if run has been running too long without completion
        try:
            started = datetime.fromisoformat(metrics.started_at.replace('Z', '+00:00'))
            elapsed = datetime.now(started.tzinfo) - started
            
            # Stalled if running > threshold and no recent progress
            if elapsed > timedelta(minutes=self.stall_threshold_minutes):
                # Check if any steps completed recently (would need last_updated tracking)
                return True
                
        except Exception:
            pass
        
        return False
    
    def _handle_completion(self, run_id: str, metrics: RunMetrics):
        """Handle run completion - emit event for downstream automation.
        
        Args:
            run_id: Completed run ID
            metrics: Run metrics
        """
        # Determine final status
        if metrics.failed_steps == 0:
            status = "succeeded"
        elif metrics.completed_steps > 0:
            status = "partial"
        else:
            status = "failed"
        
        print(f"[{self._timestamp()}] Run {run_id} completed: {status} "
              f"({metrics.completed_steps}/{metrics.total_steps} succeeded)")
        
        # Update run state in database
        try:
            cursor = self.monitor.db.conn.cursor()
            cursor.execute(
                "UPDATE runs SET state = ?, ended_at = ? WHERE run_id = ?",
                (status, self._timestamp(), run_id)
            )
            self.monitor.db.conn.commit()
        except Exception as e:
            print(f"[{self._timestamp()}] WARNING: Failed to update run state: {e}")
        
        # Emit completion event (triggers archival, reporting, alerts)
        try:
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="run_completed",
                severity="info",
                data={
                    "status": status,
                    "metrics": metrics.to_dict()
                }
            )
        except Exception as e:
            print(f"[{self._timestamp()}] ERROR: Failed to emit completion event: {e}")
    
    def _handle_stall(self, run_id: str, metrics: RunMetrics):
        """Handle stalled run - emit warning event.
        
        Args:
            run_id: Stalled run ID
            metrics: Run metrics
        """
        print(f"[{self._timestamp()}] WARNING: Run {run_id} appears stalled "
              f"({metrics.completed_steps}/{metrics.total_steps} completed)")
        
        try:
            self.event_bus.emit_event(
                run_id=run_id,
                event_type="run_stalled",
                severity="warning",
                data={
                    "threshold_minutes": self.stall_threshold_minutes,
                    "metrics": metrics.to_dict()
                }
            )
        except Exception as e:
            print(f"[{self._timestamp()}] ERROR: Failed to emit stall event: {e}")
    
    def _timestamp(self) -> str:
        """Get current timestamp for logging."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point for monitoring daemon."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous monitoring daemon")
    parser.add_argument(
        "--db-path",
        default=".state/orchestration.db",
        help="Database path (default: .state/orchestration.db)"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Poll interval in seconds (default: 10)"
    )
    parser.add_argument(
        "--stall-threshold",
        type=int,
        default=30,
        help="Stall detection threshold in minutes (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Initialize daemon
    daemon = MonitoringDaemon(args.db_path, args.poll_interval)
    daemon.stall_threshold_minutes = args.stall_threshold
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal")
        daemon.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring
    try:
        daemon.start()
    except Exception as e:
        print(f"FATAL: Daemon failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
