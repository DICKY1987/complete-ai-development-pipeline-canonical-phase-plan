#!/usr/bin/env python3
"""
Generate pipeline workstream JSON from OpenSpec changes or bundles.

Examples:
  python scripts/generate_workstreams_from_openspec.py --change-id test-001 \
    --files-scope src/pipeline/openspec_parser.py docs/ --tool aider --gate 1

  python scripts/generate_workstreams_from_openspec.py --bundle bundles/openspec-test-001.yaml \
    --files-scope src/pipeline/** --ccpm-issue 123
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add src to import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.openspec_convert import (
    bundle_to_workstream,
    load_bundles_from_input,
)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Convert OpenSpec changes/bundles to workstreams JSON")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--change-id", help="OpenSpec change id under openspec/changes/")
    src.add_argument("--bundle", help="Path to a bundle YAML or directory of bundles")
    ap.add_argument("--out-dir", default="workstreams", help="Output directory for JSON workstreams")
    ap.add_argument("--files-scope", nargs="*", help="Explicit files_scope paths (overrides inference)")
    ap.add_argument("--tool", default="aider", help="Primary tool name for workstream")
    ap.add_argument("--gate", type=int, default=1, help="Gate level (>=1)")
    ap.add_argument("--ccpm-issue", default="TBD", help="Issue reference id or string")
    ap.add_argument("--echo", action="store_true", help="Print generated JSON to stdout")
    args = ap.parse_args(argv)

    input_path = Path(args.bundle).resolve() if args.bundle else None
    bundles = load_bundles_from_input(change_id=args.change_id, input_path=input_path)
    if not bundles:
        print("No bundles found", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    last_out: Optional[Path] = None
    for b in bundles:
        ws = bundle_to_workstream(
            b,
            change_id=args.change_id,
            files_scope=args.files_scope,
            tool=args.tool,
            gate=args.gate,
            ccpm_issue=args.ccpm_issue,
        )
        out_path = out_dir / f"{ws['id']}.json"
        out_path.write_text(json.dumps(ws, indent=2), encoding="utf-8")
        last_out = out_path
        if args.echo:
            print(json.dumps(ws, indent=2))

    if last_out:
        print(str(last_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

