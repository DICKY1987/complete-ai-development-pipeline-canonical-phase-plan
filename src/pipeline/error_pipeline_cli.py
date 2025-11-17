from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .error_context import ErrorPipelineContext
from .error_pipeline_service import tick
from . import error_db


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance the error pipeline by one state (tick)")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ws-id", required=True)
    parser.add_argument("--py", nargs="*", default=[], help="Python files to include")
    parser.add_argument("--ps", nargs="*", default=[], help="PowerShell files to include")
    args = parser.parse_args()

    ctx = error_db.get_error_context(args["run_id"] if isinstance(args, dict) else args.run_id,
                               args["ws_id"] if isinstance(args, dict) else args.ws_id)

    # Seed target files if empty
    if not ctx.python_files and args.py:
        ctx.python_files = [str(Path(p)) for p in args.py]
    if not ctx.powershell_files and args.ps:
        ctx.powershell_files = [str(Path(p)) for p in args.ps]

    ctx = tick(ctx)
    print(f"state={ctx.current_state} attempt={ctx.attempt_number} agent={ctx.current_agent} final={ctx.final_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

