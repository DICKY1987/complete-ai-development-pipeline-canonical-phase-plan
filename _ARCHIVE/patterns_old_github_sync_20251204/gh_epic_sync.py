#!/usr/bin/env python3
"""Ensure an epic exists (by title) and print its issue number.

Usage:
  python scripts/gh_epic_sync.py --title "Epic: feature-name" --label epic:feature-name
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-GH-EPIC-SYNC-GH-EPIC-SYNC-001
# DOC_ID: DOC-SCRIPT-SCRIPTS-GH-EPIC-SYNC-149

from __future__ import annotations

import argparse
import sys
from typing import List
from pathlib import Path


def _repo_import():
    base = Path(__file__).resolve().parents[1]
    github_v2_path = base / ".github" / "github_integration_v2"
    sys.path.insert(0, str(github_v2_path))
    from executors import phase_sync  # type: ignore

    return phase_sync


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True, help="Epic title")
    p.add_argument("--body", default="", help="Epic body")
    p.add_argument("--label", dest="labels", action="append", help="Add label(s)")
    args = p.parse_args(argv)

    gh = _repo_import()
    num = gh.ensure_epic(args.title, body=args.body, labels=args.labels)
    if num is None:
        return 1
    print(num)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

