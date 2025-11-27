from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .error_context import ErrorPipelineContext
from .m010004_error_pipeline_service import tick


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance the error pipeline by one state (tick)")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ws-id", required=True)
    parser.add_argument("--py", nargs="*", default=[], help="Python files to include")
    parser.add_argument("--ps", nargs="*", default=[], help="PowerShell files to include")
    args = parser.parse_args()

    ctx = ErrorPipelineContext(
        run_id=args["run_id"] if isinstance(args, dict) else args.run_id,
        workstream_id=args["ws_id"] if isinstance(args, dict) else args.ws_id,
        python_files=[str(Path(p)) for p in (args.py or [])],
        powershell_files=[str(Path(p)) for p in (args.ps or [])],
    )

    ctx = tick(ctx)
    print(f"state={ctx.current_state} attempt={ctx.attempt_number} agent={ctx.current_agent} final={ctx.final_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

