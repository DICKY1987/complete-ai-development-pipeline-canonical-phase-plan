#!/usr/bin/env python3
"""
Sync log policy gate wrapper (MERGE-002).
Parses .sync-log.txt and enforces thresholds before merge.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-SYNC-LOG-SUMMARY-727

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


def parse_time_window(minutes: int | None) -> timedelta | None:
    if minutes is None:
        return None
    return timedelta(minutes=minutes)


def parse_sync_log(log_path: Path, window: timedelta | None) -> Dict[str, Any]:
    pattern = "%Y-%m-%d %H:%M:%S"
    events: List[Dict[str, Any]] = []
    error_clusters: defaultdict[str, List[str]] = defaultdict(list)

    if not log_path.exists():
        raise FileNotFoundError(f"Sync log not found: {log_path}")

    with log_path.open() as f:
        for line_num, line in enumerate(f, 1):
            parts = line.strip().split(" ", 2)
            if len(parts) < 3:
                continue
            timestamp_str = f"{parts[0]} {parts[1]}"
            try:
                timestamp = datetime.strptime(timestamp_str, pattern)
            except ValueError:
                continue

            if window and datetime.now() - timestamp > window:
                continue

            level_and_rest = parts[2]
            if "]" in level_and_rest:
                level = level_and_rest.split("]", 1)[0].replace("[", "")
                message = level_and_rest.split("]", 1)[1].strip()
            else:
                level = "INFO"
                message = level_and_rest

            action = "unknown"
            lowered = message.lower()
            if "push" in lowered:
                action = "push"
            elif "pull" in lowered:
                action = "pull"
            if "error" in lowered or "fail" in lowered:
                action = "error"
                error_clusters[str(timestamp.date())].append(message)

            events.append(
                {
                    "line": line_num,
                    "timestamp": timestamp_str,
                    "level": level,
                    "action": action,
                    "detail": message,
                }
            )

    push_events = [e for e in events if e["action"] == "push"]
    pull_events = [e for e in events if e["action"] == "pull"]
    error_events = [e for e in events if e["action"] == "error"]

    last_push = push_events[-1]["timestamp"] if push_events else None
    last_pull = pull_events[-1]["timestamp"] if pull_events else None

    activity_windows: List[Dict[str, Any]] = []
    if len(push_events) >= 5:
        for i in range(len(push_events) - 4):
            window_slice = push_events[i : i + 5]
            start = datetime.strptime(window_slice[0]["timestamp"], pattern)
            end = datetime.strptime(window_slice[-1]["timestamp"], pattern)
            duration = (end - start).total_seconds()
            if duration < 60:
                activity_windows.append(
                    {
                        "start": window_slice[0]["timestamp"],
                        "end": window_slice[-1]["timestamp"],
                        "push_count": 5,
                        "duration_seconds": duration,
                    }
                )

    summary: Dict[str, Any] = {
        "pattern_id": "MERGE-002",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "log_path": str(log_path),
        "lookback_minutes": (
            None if window is None else int(window.total_seconds() / 60)
        ),
        "total_events": len(events),
        "statistics": {
            "push_count": len(push_events),
            "pull_count": len(pull_events),
            "error_count": len(error_events),
            "last_push": last_push,
            "last_pull": last_pull,
            "high_activity_windows": activity_windows,
            "error_clusters": {k: len(v) for k, v in error_clusters.items()},
        },
        "recent_events": events[-50:] if len(events) > 50 else events,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync log policy gate")
    parser.add_argument("--log-path", default=".sync-log.txt", help="Path to sync log")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--lookback-minutes", type=int, default=30, help="Time window in minutes"
    )
    parser.add_argument("--max-errors", type=int, default=5, help="Max allowed errors")
    parser.add_argument(
        "--max-high-activity", type=int, default=0, help="Max allowed storm windows"
    )
    args = parser.parse_args()

    log_path = Path(args.log_path)
    try:
        window = parse_time_window(args.lookback_minutes)
        summary = parse_sync_log(log_path, window)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: Failed to parse sync log: {exc}")
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))

    errors = summary["statistics"]["error_count"]
    storms = len(summary["statistics"]["high_activity_windows"])
    violated = errors > args.max_errors or storms > args.max_high_activity

    if violated:
        print(
            f"FAIL: Sync health violated (errors={errors} limit={args.max_errors}, "
            f"storms={storms} limit={args.max_high_activity})"
        )
        return 2

    print(f"OK: Sync health ok (errors={errors}, storms={storms}) -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
