#!/usr/bin/env python3
"""
Restricted timestamp heuristics (policy guard).
Validates timestamp usage against file classes and emits a summary.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-MERGE-TIMESTAMP-RESOLVER-719

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Timestamp heuristics gate")
    parser.add_argument(
        "--input", required=True, help="Path to merge_file_classes_<branch>.json"
    )
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument(
        "--restrict-classes", action="store_true", help="Enforce safe/forbidden classes"
    )
    parser.add_argument("--output", default=None, help="Optional output summary path")
    args = parser.parse_args()

    classification_path = Path(args.input)
    if not classification_path.exists():
        print(f"FAIL: Classification file not found: {classification_path}")
        return 2

    data: Dict[str, Any] = json.loads(classification_path.read_text())
    safe_classes = set(data.get("timestamp_safe_classes", []))
    forbidden_classes = set(data.get("never_timestamp_classes", []))
    classifications: Dict[str, str] = data.get("classifications", {})

    summary = {
        "pattern_id": "MERGE-004-TIMESTAMP",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "branch": args.branch,
        "safe_classes": sorted(safe_classes),
        "forbidden_classes": sorted(forbidden_classes),
        "safe_candidates": [],
        "forbidden_hits": [],
    }

    for file_path, class_name in classifications.items():
        if class_name in safe_classes:
            summary["safe_candidates"].append(file_path)
        if class_name in forbidden_classes:
            summary["forbidden_hits"].append(file_path)

    out_path = (
        Path(args.output)
        if args.output
        else classification_path.with_name(f"timestamp_resolution_{args.branch}.json")
    )
    out_path.write_text(json.dumps(summary, indent=2))

    if args.restrict_classes and summary["forbidden_hits"]:
        print(
            f"FAIL: Timestamp resolver blocked: forbidden classes present "
            f"({len(summary['forbidden_hits'])} files)"
        )
        return 2

    print(f"OK: Timestamp heuristics check passed -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
