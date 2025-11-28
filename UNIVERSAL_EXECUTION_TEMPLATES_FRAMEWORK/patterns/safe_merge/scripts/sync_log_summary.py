#!/usr/bin/env python3
"""
MERGE-002: Sync Log Summary

Parses .sync-log.txt into structured data for automation rules.
"""

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import argparse


def parse_time_window(window_str):
    """Convert '24h', '7d' to timedelta."""
    if not window_str:
        return None
    
    unit = window_str[-1]
    value = int(window_str[:-1])
    
    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    else:
        raise ValueError(f"Unknown time window unit: {unit}")


def parse_sync_log(log_path, time_window=None):
    """Parse .sync-log.txt into structured events."""
    
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)'
    events = []
    error_clusters = defaultdict(list)
    
    log_file = Path(log_path)
    if not log_file.exists():
        print(f"❌ Log file not found: {log_path}")
        return None
    
    window_delta = parse_time_window(time_window) if time_window else None
    
    with open(log_file) as f:
        for line_num, line in enumerate(f, 1):
            match = re.match(pattern, line.strip())
            if not match:
                continue
            
            timestamp_str, level, message = match.groups()
            
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
            
            # Filter by time window
            if window_delta:
                if datetime.now() - timestamp > window_delta:
                    continue
            
            # Extract action
            action = 'unknown'
            if 'Pushing' in message or 'Push' in message:
                action = 'push'
            elif 'Pulling' in message or 'Pull' in message:
                action = 'pull'
            elif 'SUCCESS' in level or 'SUCCESS' in message:
                action = 'success'
            elif 'ERROR' in level or 'FAIL' in level:
                action = 'error'
                error_clusters[timestamp.date()].append(message)
            
            events.append({
                'line': line_num,
                'timestamp': timestamp_str,
                'level': level,
                'action': action,
                'detail': message
            })
    
    # Calculate statistics
    push_events = [e for e in events if e['action'] == 'push']
    pull_events = [e for e in events if e['action'] == 'pull']
    error_events = [e for e in events if e['action'] == 'error']
    
    last_push = push_events[-1]['timestamp'] if push_events else None
    last_pull = pull_events[-1]['timestamp'] if pull_events else None
    
    # Identify high-activity windows (>5 pushes per minute)
    activity_windows = []
    if len(push_events) >= 5:
        for i in range(len(push_events) - 4):
            window = push_events[i:i+5]
            start_time = datetime.strptime(window[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(window[-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
            duration = (end_time - start_time).total_seconds()
            
            if duration < 60:  # 5 pushes in less than 1 minute
                activity_windows.append({
                    'start': window[0]['timestamp'],
                    'end': window[-1]['timestamp'],
                    'push_count': 5,
                    'duration_seconds': duration
                })
    
    # Generate summary
    summary = {
        'pattern_id': 'MERGE-002',
        'timestamp': datetime.now().isoformat(),
        'log_path': str(log_path),
        'time_window': time_window,
        'total_events': len(events),
        'statistics': {
            'push_count': len(push_events),
            'pull_count': len(pull_events),
            'error_count': len(error_events),
            'last_push': last_push,
            'last_pull': last_pull,
            'high_activity_windows': activity_windows,
            'error_clusters': {
                str(date): len(errors)
                for date, errors in error_clusters.items()
            }
        },
        'recent_events': events[-50:] if len(events) > 50 else events
    }
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='MERGE-002: Sync Log Summary')
    parser.add_argument('log_path', help='Path to .sync-log.txt')
    parser.add_argument('--time-window', help='Time window (e.g., "24h", "7d")')
    parser.add_argument('--output', default='sync_log_summary.json', help='Output file')
    
    args = parser.parse_args()
    
    print("🔍 Parsing sync log...")
    summary = parse_sync_log(args.log_path, args.time_window)
    
    if not summary:
        return 1
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary saved: {args.output}")
    print(f"\n📊 Statistics:")
    print(f"   Total events: {summary['total_events']}")
    print(f"   Pushes: {summary['statistics']['push_count']}")
    print(f"   Pulls: {summary['statistics']['pull_count']}")
    print(f"   Errors: {summary['statistics']['error_count']}")
    print(f"   Last push: {summary['statistics']['last_push']}")
    print(f"   High-activity windows: {len(summary['statistics']['high_activity_windows'])}")
    
    return 0


if __name__ == '__main__':
    exit(main())
