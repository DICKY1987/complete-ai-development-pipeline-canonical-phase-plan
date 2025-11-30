"""Pattern event inspection CLI.

Usage:
    python -m core.engine.pattern_inspect events --job-id JOB-...
    python -m core.engine.pattern_inspect run --pattern-run-id PRUN-...
    python -m core.engine.pattern_inspect events --follow
"""
# DOC_ID: DOC-PAT-PATTERN-EVENT-SYSTEM-PATTERN-INSPECT-810

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from core.engine.pattern_events import PatternEventEmitter, PatternRunAggregator


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp for display."""
    from datetime import datetime
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return dt.strftime('%H:%M:%S')


def print_event_timeline(events, colorize=True):
    """Print events as a timeline."""
    
    # Color codes
    if colorize and sys.stdout.isatty():
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BLUE = '\033[94m'
        RESET = '\033[0m'
    else:
        GREEN = YELLOW = RED = BLUE = RESET = ''
    
    for event in events:
        timestamp = format_timestamp(event.timestamp)
        event_name = event.event_type.split('.')[-1]
        
        # Color by status
        if event.status == 'success':
            color = GREEN
        elif event.status == 'failed':
            color = RED
        elif event.status == 'warning':
            color = YELLOW
        else:
            color = BLUE
        
        # Format details summary
        details_summary = ""
        if event.event_type == "pattern.selection.resolved":
            method = event.details.get("selection_method", "")
            details_summary = f" → {method}"
        elif event.event_type == "pattern.template.expanded":
            artifacts = len(event.details.get("generated_artifacts", []))
            details_summary = f" → {artifacts} artifacts"
        elif event.event_type == "pattern.execution.completed":
            duration = event.details.get("duration_seconds", 0)
            findings = event.details.get("result_summary", {}).get("finding_count", 0)
            details_summary = f" → {findings} findings, {duration:.1f}s"
        elif event.event_type == "pattern.execution.failed":
            error = event.details.get("error_message", "")[:50]
            details_summary = f" → {error}"
        
        print(f"[{timestamp}] {color}{event.pattern_id:20}{RESET} {event_name:20}{details_summary}")


def cmd_events(args):
    """Show pattern events."""
    emitter = PatternEventEmitter(Path(args.events_dir) if args.events_dir else None)
    
    if args.follow:
        # Follow mode: tail events
        print("Following pattern events (Ctrl+C to stop)...")
        seen_events = set()
        
        try:
            while True:
                events = emitter.get_events(job_id=args.job_id)
                new_events = [e for e in events if e.event_id not in seen_events]
                
                if new_events:
                    print_event_timeline(new_events, colorize=not args.no_color)
                    seen_events.update(e.event_id for e in new_events)
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped following.")
            return
    
    else:
        # One-shot mode
        events = emitter.get_events(
            job_id=args.job_id,
            pattern_run_id=args.pattern_run_id,
        )
        
        if not events:
            print("No events found.")
            return
        
        # Print header
        if args.job_id:
            print(f"Pattern Events for Job {args.job_id}")
        else:
            print("Recent Pattern Events")
        print("─" * 80)
        
        print_event_timeline(events, colorize=not args.no_color)
        print()
        print(f"Total events: {len(events)}")


def cmd_run(args):
    """Show pattern run details."""
    emitter = PatternEventEmitter(Path(args.events_dir) if args.events_dir else None)
    aggregator = PatternRunAggregator(emitter)
    
    # Get events for this run
    events = emitter.get_events(pattern_run_id=args.pattern_run_id)
    
    if not events:
        print(f"No events found for pattern run {args.pattern_run_id}")
        return
    
    # Rebuild run from events
    for event in events:
        aggregator.handle_event(event)
    
    run = aggregator.get_run(args.pattern_run_id)
    
    if not run:
        print(f"Could not reconstruct run {args.pattern_run_id}")
        return
    
    # Print run details
    print(f"Pattern Run: {run.pattern_run_id}")
    print("─" * 80)
    print(f"Pattern ID:      {run.pattern_id}")
    print(f"Operation:       {run.operation_kind}")
    print(f"Job ID:          {run.job_id}")
    if run.step_id:
        print(f"Step ID:         {run.step_id}")
    print(f"Status:          {run.status}")
    print(f"Started:         {run.started_at}")
    if run.finished_at:
        print(f"Finished:        {run.finished_at}")
        print(f"Duration:        {run.duration_seconds:.2f}s")
    print()
    
    # Inputs
    if run.inputs:
        print("Inputs:")
        for key, value in run.inputs.items():
            print(f"  {key}: {value}")
        print()
    
    # Outputs
    if run.outputs:
        print("Outputs:")
        for key, value in run.outputs.items():
            print(f"  {key}: {value}")
        print()
    
    # Artifacts
    if run.artifacts:
        print("Artifacts:")
        for artifact in run.artifacts:
            print(f"  - {artifact}")
        print()
    
    # Tool metadata
    if run.tool_metadata:
        print("Tool:")
        for key, value in run.tool_metadata.items():
            print(f"  {key}: {value}")
        print()
    
    # Error (if failed)
    if run.error:
        print("Error:")
        for key, value in run.error.items():
            if value:
                print(f"  {key}: {value}")
        print()
    
    # Event timeline
    print("Event Timeline:")
    print_event_timeline(events, colorize=not args.no_color)


def main():
    parser = argparse.ArgumentParser(description="Inspect pattern execution events")
    parser.add_argument(
        "--events-dir",
        help="Path to events directory (default: state/events/)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Events command
    events_parser = subparsers.add_parser("events", help="Show pattern events")
    events_parser.add_argument(
        "--job-id",
        help="Filter by job ID"
    )
    events_parser.add_argument(
        "--pattern-run-id",
        help="Filter by pattern run ID"
    )
    events_parser.add_argument(
        "--follow",
        action="store_true",
        help="Follow events in real-time"
    )
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Show pattern run details")
    run_parser.add_argument(
        "pattern_run_id",
        help="Pattern run ID to inspect"
    )
    
    args = parser.parse_args()
    
    if args.command == "events":
        cmd_events(args)
    elif args.command == "run":
        cmd_run(args)


if __name__ == "__main__":
    main()
