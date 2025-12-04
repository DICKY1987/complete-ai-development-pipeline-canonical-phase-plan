#!/usr/bin/env python
"""Real-time monitoring for parallel execution.

Phase I WS-I3: Event-driven monitoring implementation.
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-MONITOR-PARALLEL-219
# DOC_ID: DOC-SCRIPT-SCRIPTS-MONITOR-PARALLEL-156

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.core_state import m010003_db
from modules.core_engine.m010001_event_bus import EventType


def format_event(event: dict) -> str:
    """Format event for display."""
    ts = event.get('timestamp', '')
    if ts:
        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        ts = ts.strftime('%H:%M:%S')

    event_type = event.get('event_type', '')
    worker_id = event.get('worker_id', '')
    ws_id = event.get('workstream_id', '')

    parts = [f"[{ts}]", event_type]
    if worker_id:
        parts.append(f"worker={worker_id[:8]}")
    if ws_id:
        parts.append(f"ws={ws_id}")

    return " ".join(parts)


def monitor_live(run_id: str = None, tail: int = 20) -> None:
    """Monitor parallel execution in real-time.

    Args:
        run_id: Optional run ID to filter events
        tail: Number of recent events to show initially
    """
    db.init_db()

    print("=== UET Parallel Execution Monitor ===")
    print(f"Watching for events (Ctrl+C to exit)")
    if run_id:
        print(f"Filtered to run_id: {run_id}")
    print()

    # Show recent events
    events = db.get_recent_events(limit=tail)
    if run_id:
        events = [e for e in events if e.get('run_id') == run_id]

    for event in events:
        print(format_event(event))

    # Watch for new events
    last_event_id = events[-1]['id'] if events else 0

    try:
        while True:
            time.sleep(1)

            # Get new events
            new_events = db.get_events_since(last_event_id)
            if run_id:
                new_events = [e for e in new_events if e.get('run_id') == run_id]

            for event in new_events:
                print(format_event(event))
                last_event_id = max(last_event_id, event['id'])

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def show_summary(run_id: str = None) -> None:
    """Show execution summary.

    Args:
        run_id: Optional run ID to filter
    """
    db.init_db()

    # Get all events
    events = db.get_all_events()
    if run_id:
        events = [e for e in events if e.get('run_id') == run_id]

    if not events:
        print("No events found.")
        return

    # Count event types
    event_counts = {}
    for event in events:
        etype = event.get('event_type', 'unknown')
        event_counts[etype] = event_counts.get(etype, 0) + 1

    print("=== Execution Summary ===")
    print()
    for etype, count in sorted(event_counts.items()):
        print(f"{etype:30s}: {count:4d}")

    print()
    print(f"Total events: {len(events)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Monitor parallel execution")
    parser.add_argument("--run-id", help="Filter by run ID")
    parser.add_argument("--tail", type=int, default=20, help="Number of initial events to show")
    parser.add_argument("--summary", action="store_true", help="Show summary instead of live monitoring")

    args = parser.parse_args(argv)

    try:
        if args.summary:
            show_summary(run_id=args.run_id)
        else:
            monitor_live(run_id=args.run_id, tail=args.tail)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
