#!/usr/bin/env python3
"""
MERGE-003 normalizer wrapper.
Consumes detector output and optionally normalizes stray nested repos.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_normalizer():
    scripts_dir = (
        Path(__file__).resolve().parent.parent / "patterns" / "safe_merge" / "scripts"
    )
    sys.path.append(str(scripts_dir))
    try:
        from nested_repo_normalizer import normalize_nested_repos  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ImportError(f"Failed to import nested_repo_normalizer: {exc}") from exc
    return normalize_nested_repos


def _remove_stray_git(stray_paths: List[Path], dry_run: bool) -> List[str]:
    actions = []
    for git_dir in stray_paths:
        if not git_dir.exists():
            continue
        if dry_run:
            actions.append(f"would-remove:{git_dir}")
            continue
        backup = git_dir.with_suffix(".stray-backup")
        shutil.move(str(git_dir), backup)
        actions.append(f"moved:{git_dir}->{backup}")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Nested repo normalizer (policy gate)")
    parser.add_argument("--input", required=True, help="Detector output JSON")
    parser.add_argument(
        "--policy", default="auto", help="Policy name for normalization"
    )
    parser.add_argument(
        "--default",
        dest="default_policy",
        default="absorb_as_folder",
        help="Default action",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply normalization (moves stray .git)"
    )
    parser.add_argument(
        "--output",
        default=".state/safe_merge/nested_repo_normalization.json",
        help="Output plan path",
    )
    args = parser.parse_args()

    normalize_nested_repos = load_normalizer()
    report = json.loads(Path(args.input).read_text())
    work_dir = report.get("work_dir") or "."
    result: Dict[str, Any] = normalize_nested_repos(work_dir, args.default_policy, dry_run=not args.apply)  # type: ignore

    stray_git_paths = [
        Path(item["path"])
        for item in report.get("nested_repos", [])
        if item.get("type") == "stray_nested_repo"
    ]
    applied_actions = _remove_stray_git(stray_git_paths, dry_run=not args.apply)
    result["actions"] = applied_actions
    result["policy"] = args.policy
    result["default_policy"] = args.default_policy

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))

    stray_count = report.get("summary", {}).get("stray_count", 0)
    if stray_count > 0 and not args.apply:
        print(
            f"WARN: Stray repos detected ({stray_count}); rerun with --apply to normalize."
        )
        return 1

    if stray_count > 0 and args.apply:
        print(f"OK: Normalization actions: {applied_actions}")
    else:
        print("OK: No stray nested repos to normalize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
