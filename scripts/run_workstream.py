#!/usr/bin/env python
"""
CLI to run a single workstream end-to-end via the PH-05 orchestrator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from pathlib import Path


def _repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a single workstream via orchestrator")
    parser.add_argument("--ws-id", required=True, help="Workstream id to run (e.g., ws-hello-world)")
    parser.add_argument("--run-id", required=False, help="Optional run id (default: generated)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate steps without invoking external tools")
    args = parser.parse_args(argv)

    # Lazy import to avoid heavy module import at CLI startup
    from core import orchestrator

    context: Dict[str, Any] = {}
    if args.dry_run:
        context["dry_run"] = True
        os.environ["PIPELINE_DRY_RUN"] = "1"

    try:
        result = orchestrator.run_single_workstream_from_bundle(args.ws_id, run_id=args.run_id, context=context)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("final_status") == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
