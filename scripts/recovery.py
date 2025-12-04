#!/usr/bin/env python
"""Recovery CLI for parallel execution.

Phase I WS-I5: Crash recovery utilities.
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-RECOVERY-222
# DOC_ID: DOC-SCRIPT-SCRIPTS-RECOVERY-159

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.core_engine.m010001_recovery_manager import RecoveryManager


def list_recoverable_runs() -> None:
    """List runs that can be recovered."""
    manager = RecoveryManager()
    runs = manager.get_recoverable_runs()

    if not runs:
        print("No recoverable runs found.")
        return

    print("=== Recoverable Runs ===")
    print()
    for run in runs:
        print(f"Run ID: {run['run_id']}")
        print(f"  Status: {run['status']}")
        print(f"  Created: {run['created_at']}")
        print(f"  Total workstreams: {run['total_workstreams']}")
        print(f"  Incomplete: {run['incomplete']}")
        print()


def recover_crash() -> None:
    """Recover from orchestrator crash."""
    manager = RecoveryManager()
    result = manager.recover_from_crash()

    print("=== Crash Recovery ===")
    print(json.dumps(result, indent=2))

    if result["orphaned_tasks"]:
        print(f"\n⚠️  Recovered {result['orphaned_tasks']} orphaned tasks")
        print("   These tasks have been marked as failed.")
    else:
        print("\n✓ No orphaned tasks found")


def resume_run(run_id: str, max_workers: int = 4) -> None:
    """Resume execution of incomplete run."""
    manager = RecoveryManager()

    print(f"=== Resuming Run: {run_id} ===")
    print(f"Max workers: {max_workers}")
    print()

    result = manager.resume_execution(run_id, max_workers)

    if result["resumed"]:
        print(f"✓ Resumed {result['incomplete_count']} incomplete workstreams")
        print()
        print(json.dumps(result["result"], indent=2))
    else:
        print(f"⚠️  {result['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recovery utilities for parallel execution"
    )

    subparsers = parser.add_subparsers(dest="command", help="Recovery command")

    # List recoverable runs
    subparsers.add_parser("list", help="List recoverable runs")

    # Recover from crash
    subparsers.add_parser("recover", help="Recover from orchestrator crash")

    # Resume run
    resume_parser = subparsers.add_parser("resume", help="Resume incomplete run")
    resume_parser.add_argument("--run-id", required=True, help="Run ID to resume")
    resume_parser.add_argument(
        "--max-workers", type=int, default=4, help="Max parallel workers"
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "list":
            list_recoverable_runs()
        elif args.command == "recover":
            recover_crash()
        elif args.command == "resume":
            resume_run(args.run_id, args.max_workers)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
