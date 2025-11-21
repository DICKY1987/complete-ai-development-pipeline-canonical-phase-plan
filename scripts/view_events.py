#!/usr/bin/env python3
"""View execution events from database."""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.engine.event_bus import EventBus, EventType


def main():
    parser = argparse.ArgumentParser(description="View UET execution events")
    parser.add_argument('--run-id', help='Filter by run ID')
    parser.add_argument('--event-type', help='Filter by event type')
    parser.add_argument('--tail', type=int, default=50, help='Number of events to show')
    
    args = parser.parse_args()
    
    bus = EventBus()
    event_type = EventType[args.event_type] if args.event_type else None
    
    events = bus.query(
        event_type=event_type,
        run_id=args.run_id,
        limit=args.tail
    )
    
    print(f"Showing {len(events)} events:\n")
    
    for e in reversed(events):
        print(f"[{e.timestamp}] {e.event_type.value}")
        if e.worker_id:
            print(f"  Worker: {e.worker_id}")
        if e.workstream_id:
            print(f"  Workstream: {e.workstream_id}")
        if e.payload:
            print(f"  Payload: {e.payload}")
        print()


if __name__ == '__main__':
    main()
