#!/usr/bin/env python3
"""Monitoring Daemon Launcher - Start continuous monitoring with all handlers.

Usage:
    python scripts/start_monitoring_daemon.py
    python scripts/start_monitoring_daemon.py --db-path custom.db --poll-interval 5
    
Environment Variables:
    SLACK_WEBHOOK_URL - Slack webhook for alerts
    SMTP_HOST - SMTP server for email alerts
    ALERT_EMAIL_FROM - From address for email alerts
    ALERT_EMAIL_TO - Recipient address for email alerts
"""
# DOC_ID: DOC-SCRIPTS-MONITORING-DAEMON-LAUNCHER-004

import argparse
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase7_monitoring.modules.monitoring_daemon.src.monitor_daemon import MonitoringDaemon
from phase7_monitoring.modules.monitoring_daemon.src.completion_handlers import CompletionHandlers
from phase7_monitoring.modules.alerting.src.alert_engine import AlertEngine
from core.events.event_bus import EventBus


# Global daemon reference for signal handlers
daemon = None


def signal_handler(sig, frame):
    """Graceful shutdown on SIGINT/SIGTERM."""
    print("\n[Main] Received shutdown signal")
    if daemon:
        daemon.stop()
    sys.exit(0)


def main():
    """Main entry point for monitoring daemon launcher."""
    parser = argparse.ArgumentParser(
        description="Launch continuous monitoring daemon with auto-archival and alerts"
    )
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
    parser.add_argument(
        "--alerts-config",
        default="phase7_monitoring/modules/alerting/config/alerts.yaml",
        help="Path to alerts configuration (default: phase7_monitoring/modules/alerting/config/alerts.yaml)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Pipeline Monitoring Daemon")
    print("=" * 60)
    print(f"Database: {args.db_path}")
    print(f"Poll interval: {args.poll_interval}s")
    print(f"Stall threshold: {args.stall_threshold}m")
    print(f"Alerts config: {args.alerts_config}")
    print("=" * 60)
    print()
    
    # Validate database exists
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"WARNING: Database not found: {args.db_path}")
        print("Creating database directory...")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize event bus
    event_bus = EventBus(args.db_path)
    
    # Initialize alert engine
    print("[Main] Initializing alert engine...")
    alert_engine = AlertEngine(args.alerts_config)
    
    # Initialize monitoring daemon
    print("[Main] Initializing monitoring daemon...")
    global daemon
    daemon = MonitoringDaemon(args.db_path, args.poll_interval)
    daemon.stall_threshold_minutes = args.stall_threshold
    
    # Register alert handler for error events
    def alert_handler(event):
        """Forward events to alert engine."""
        alert_engine.process_event(
            event_type=event.event_type,
            run_id=event.run_id,
            data=event.data
        )
    
    event_bus.subscribe("run_failed", alert_handler)
    event_bus.subscribe("run_quarantined", alert_handler)
    event_bus.subscribe("step_failed", alert_handler)
    event_bus.subscribe("run_stalled", alert_handler)
    event_bus.subscribe("archival_failed", alert_handler)
    event_bus.subscribe("archival_preflight_failed", alert_handler)
    event_bus.subscribe("archival_validation_failed", alert_handler)
    
    # Initialize completion handlers (auto-archival, auto-reporting)
    print("[Main] Initializing completion handlers...")
    completion_handlers = CompletionHandlers(event_bus)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print()
    print("✅ All handlers registered")
    print("✅ Monitoring daemon ready")
    print()
    print("Active features:")
    print("  - Continuous run monitoring")
    print("  - Automatic completion detection")
    print("  - Automatic archival on completion")
    print("  - Automatic report generation")
    print("  - Multi-channel alerts (console, Slack, email)")
    print("  - Stall detection")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Start monitoring loop
    try:
        daemon.start()
    except Exception as e:
        print(f"FATAL: Daemon failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
