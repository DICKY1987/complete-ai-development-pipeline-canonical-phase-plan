#!/usr/bin/env python
"""
CLI to run a single workstream end-to-end via the PH-05 orchestrator.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-RUN-WORKSTREAM-230
DOC_ID: DOC-SCRIPT-SCRIPTS-RUN-WORKSTREAM-167

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a single workstream via orchestrator")
    parser.add_argument("--ws-id", required=False, help="Workstream id to run (e.g., ws-hello-world)")
    parser.add_argument("--run-id", required=False, help="Optional run id (default: generated)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate steps without invoking external tools")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel execution (Phase I)")
    parser.add_argument("--max-workers", type=int, default=4, help="Max parallel workers (default: 4)")
    parser.add_argument("--workstreams-dir", default="workstreams", help="Directory containing workstream bundles")
    args = parser.parse_args(argv)

    # Lazy import to avoid heavy module import at CLI startup
    from modules.core_engine import m010001_orchestrator
    from modules.core_state import m010003_bundles

    context: Dict[str, Any] = {}
    if args.dry_run:
        context["dry_run"] = True
        os.environ["PIPELINE_DRY_RUN"] = "1"

    # Parallel execution mode
    if args.parallel:
        try:
            # Load all bundles
            bundle_objs = bundles.load_and_validate_bundles()
            
            result = orchestrator.execute_workstreams_parallel(
                bundle_objs,
                max_workers=args.max_workers,
                dry_run=args.dry_run,
                context=context
            )
            
            print(json.dumps(result, indent=2))
            
            # Return 0 if all completed successfully
            failed = result.get('failed', [])
            return 0 if len(failed) == 0 else 1
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 2
    
    # Single workstream mode (original behavior)
    if not args.ws_id:
        print("Error: --ws-id required for single workstream mode", file=sys.stderr)
        return 2

    try:
        result = orchestrator.run_single_workstream_from_bundle(args.ws_id, run_id=args.run_id, context=context)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("final_status") == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
