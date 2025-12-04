#!/usr/bin/env python3
"""
Append merge events to a JSONL log.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-SAFE-MERGE-EMIT-EVENT-725

from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe merge event emitter")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument(
        "--status",
        required=True,
        choices=["success", "failed", "blocked"],
        help="Final status",
    )
    parser.add_argument("--phase-id", type=int, default=6, help="Phase id")
    parser.add_argument(
        "--phase-name", default="metrics_and_event_append", help="Phase name"
    )
    parser.add_argument(
        "--reason-code", default="", help="Reason code if failed/blocked"
    )
    parser.add_argument(
        "--events-file",
        default=".state/safe_merge/merge_events.jsonl",
        help="Events log path",
    )
    parser.add_argument("--details", default="{}", help="JSON string of extra details")
    parser.add_argument(
        "--invoker", default="human", choices=["human", "ai", "ci"], help="Invoker type"
    )
    args = parser.parse_args()

    try:
        details_obj: Dict[str, Any] = json.loads(args.details)
    except json.JSONDecodeError:
        details_obj = {"raw": args.details}

    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "branch": args.branch,
        "phase_id": args.phase_id,
        "phase_name": args.phase_name,
        "status": args.status,
        "reason_code": args.reason_code,
        "details": details_obj,
        "invoker": args.invoker,
        "host": socket.gethostname(),
    }

    events_path = Path(args.events_file)
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    print(f"OK: Event appended -> {events_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
