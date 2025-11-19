#!/usr/bin/env python3
"""Validate workstream bundle files and report issues.

Usage:
  python scripts/validate_workstreams.py [--run-id RUN] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure repository root is importable when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state import bundles as ws_bundles


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate workstream bundles")
    parser.add_argument("--run-id", dest="run_id", help="Run ID to sync bundles to DB")
    parser.add_argument("--json", dest="emit_json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args(argv)

    try:
        bundles = ws_bundles.load_and_validate_bundles()
        overlaps = ws_bundles.detect_filescope_overlaps(bundles)
        result: Dict[str, Any] = {
            "bundle_count": len(bundles),
            "overlaps": overlaps,
            "ok": len(overlaps) == 0,
        }

        if overlaps:
            # Treat any overlap as a hard error
            msg = "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(overlaps.items()))
            raise ws_bundles.FileScopeOverlapError(f"Overlapping file scopes: {msg}")

        if args.run_id:
            ws_bundles.sync_bundles_to_db(args.run_id, bundles)
            result["synced_run_id"] = args.run_id

        if args.emit_json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Bundles: {len(bundles)}; no cycles; no overlaps detected.")
            if args.run_id:
                print(f"Synced {len(bundles)} workstreams to run {args.run_id}.")
        return 0
    except Exception as e:
        if args and getattr(args, "emit_json", False):
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
