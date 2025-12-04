#!/usr/bin/env python3
"""
MERGE-003 detector wrapper.
Uses patterns/safe_merge implementation and writes to .state/safe_merge.
"""
DOC_ID: DOC - SCRIPT - SCRIPTS - NESTED - REPO - DETECTOR - 721
DOC_ID: DOC - SCRIPT - SCRIPTS - NESTED - REPO - DETECTOR - 721

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def load_detector():
    scripts_dir = (
        Path(__file__).resolve().parent.parent / "patterns" / "safe_merge" / "scripts"
    )
    sys.path.append(str(scripts_dir))
    try:
        from nested_repo_detector import detect_nested_repos  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ImportError(f"Failed to import nested_repo_detector: {exc}") from exc
    return detect_nested_repos


def main() -> int:
    parser = argparse.ArgumentParser(description="Nested repo detector (policy gate)")
    parser.add_argument("--work-dir", default=".", help="Repository root")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--max-stray", type=int, default=0, help="Maximum allowed stray nested repos"
    )
    args = parser.parse_args()

    detect_nested_repos = load_detector()
    work_path = Path(args.work_dir).resolve()
    report: Dict[str, Any] = detect_nested_repos(str(work_path))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))

    stray_count = report.get("summary", {}).get("stray_count") or report.get(
        "stray_count", 0
    )
    if stray_count > args.max_stray:
        print(
            f"FAIL: Found {stray_count} stray nested repos (allowed {args.max_stray})"
        )
        return 2

    print(f"OK: Nested repo gate passed (stray={stray_count}) -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
