#!/usr/bin/env python3
"""
AI conflict resolver guard.
Currently validates conflict count and emits a report for manual review.


DOC_ID: DOC-SCRIPT-SCRIPTS-AI-CONFLICT-RESOLVER-780
"""
# DOC_ID: DOC - SCRIPT - SCRIPTS - AI - CONFLICT - RESOLVER - 705
# DOC_ID: DOC - SCRIPT - SCRIPTS - AI - CONFLICT - RESOLVER - 705

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def get_conflict_files() -> List[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=False,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return files


def load_classes(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return data.get("classifications", {})


def main() -> int:
    parser = argparse.ArgumentParser(description="AI conflict resolution guard")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument(
        "--file-classes", required=True, help="Path to merge_file_classes_<branch>.json"
    )
    parser.add_argument(
        "--max-files", type=int, default=20, help="Max conflicts before manual review"
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Optional report output path (defaults to .state/safe_merge/conflict_report_<branch>.json)",
    )
    args = parser.parse_args()

    conflict_files = get_conflict_files()
    classes = load_classes(Path(args.file_classes))

    report = {
        "pattern_id": "MERGE-AI-CONFLICT",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "branch": args.branch,
        "conflict_files": [
            {"path": f, "class": classes.get(f, "unknown")} for f in conflict_files
        ],
        "total_conflicts": len(conflict_files),
        "max_files": args.max_files,
        "action": "manual_review" if conflict_files else "clean",
    }

    report_path = (
        Path(args.report)
        if args.report
        else Path(".state/safe_merge") / f"conflict_report_{args.branch}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    if not conflict_files:
        print(f"OK: No conflicts detected -> {report_path}")
        return 0

    if len(conflict_files) > args.max_files:
        print(
            f"FAIL: Too many conflicts for AI flow ({len(conflict_files)} > {args.max_files})"
        )
        return 2

    print(
        f"WARN: Conflicts detected ({len(conflict_files)}). Manual review required. Report: {report_path}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
