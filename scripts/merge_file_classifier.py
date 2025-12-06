#!/usr/bin/env python3
"""
MERGE-008 file classifier wrapper.
Uses patterns/safe_merge implementation and enforces required class sets.


DOC_ID: DOC-SCRIPT-SCRIPTS-MERGE-FILE-CLASSIFIER-781
"""
# DOC_ID: DOC - SCRIPT - SCRIPTS - MERGE - FILE - CLASSIFIER - 718
# DOC_ID: DOC - SCRIPT - SCRIPTS - MERGE - FILE - CLASSIFIER - 718

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def load_classifier():
    scripts_dir = (
        Path(__file__).resolve().parent.parent / "patterns" / "safe_merge" / "scripts"
    )
    sys.path.append(str(scripts_dir))
    try:
        from merge_file_classifier import classify_files  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ImportError(f"Failed to import merge_file_classifier: {exc}") from exc
    return classify_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge file classifier (policy gate)")
    parser.add_argument("--work-dir", default=".", help="Repository root")
    parser.add_argument(
        "--policy", default="config/merge_policy.yaml", help="Merge policy path"
    )
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    policy_path = Path(args.policy)
    if not policy_path.exists():
        print(f"FAIL: Merge policy missing: {policy_path}")
        return 2

    classify_files = load_classifier()
    output: Dict[str, Any] = classify_files(args.work_dir, str(policy_path))

    # Enforce required class sets
    required_classes = {
        "generated",
        "binary",
        "human_text",
        "config_sensitive",
        "do_not_merge",
    }
    missing = required_classes.difference(output.get("rules", {}).keys())
    if missing:
        print(f"FAIL: Missing required classes in rules: {', '.join(sorted(missing))}")
        return 2

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))

    safe = set(output.get("timestamp_safe_classes", []))
    forbidden = set(output.get("never_timestamp_classes", []))
    if not {"generated", "binary"}.issubset(safe) or not {
        "human_text",
        "config_sensitive",
    }.issubset(forbidden):
        print("WARN: Timestamp class sets look unusual; review merge policy.")

    print(f"OK: File classification complete -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
