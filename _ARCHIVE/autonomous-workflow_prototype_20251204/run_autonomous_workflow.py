#!/usr/bin/env python3
"""
Autonomous Workflow Entry Point

Single command to execute the complete self-healing automation loop:
  Detect → Diagnose → Fix → Retest → Certify

Usage:
    python run_autonomous_workflow.py --repo-root /path/to/repo
    python run_autonomous_workflow.py --repo-root /path/to/repo --dry-run
    python run_autonomous_workflow.py --repo-root /path/to/repo --mode certify-only
"""
DOC_ID: DOC-CORE-AUTONOMOUS-WORKFLOW-PROTOTYPE-20251204-778

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent / "orchestrator"))

from automation_self_healing_loop import OrchestratorConfig, SelfHealingOrchestrator
from generate_index import generate_automation_index


def print_banner():
    """Print startup banner"""
    print(
        """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗ ██████╗ ║
║    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║██╔═══██╗║
║    ███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║██║   ██║║
║    ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║██║   ██║║
║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝║
║    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ║
║                                                                               ║
║              SELF-HEALING AUTOMATION WORKFLOW                                 ║
║              Detect → Diagnose → Fix → Retest → Certify                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    )


def run_workflow(args):
    """Execute the autonomous workflow"""

    print_banner()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()

    print(f"Repository: {repo_root}")
    print(f"Output:     {output_dir}")
    print(f"Mode:       {args.mode}")
    print(f"Dry Run:    {args.dry_run}")
    print()

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Phase 0: Generate or load index
    index_path = output_dir / "automation_index.json"

    if args.mode in ("full", "discover", "index-only"):
        print("═" * 60)
        print("PHASE 0: AUTOMATION DISCOVERY")
        print("═" * 60)

        report_path = (
            args.report
            if args.report
            else repo_root / "AUTOMATION_COMPONENTS_REPORT.md"
        )

        index = generate_automation_index(
            repo_root=repo_root,
            output_path=index_path,
            report_path=report_path if report_path.exists() else None,
        )

        if args.mode == "index-only":
            print(f"\n✓ Index generated: {index_path}")
            return 0

    if args.mode == "discover":
        print(f"\n✓ Discovery complete: {index_path}")
        return 0

    # Phases 1-5: Self-healing loop
    print()
    print("═" * 60)
    print("PHASES 1-5: SELF-HEALING LOOP")
    print("═" * 60)

    config = OrchestratorConfig(
        repo_root=repo_root,
        output_dir=output_dir,
        max_retry_cycles=args.max_retries,
        max_retries_per_unit=3,
        retry_delay_seconds=args.retry_delay,
        backoff_multiplier=2.0,
        certification_threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    orchestrator = SelfHealingOrchestrator(config)

    # Use existing status if provided
    status_path = None
    if args.status_file:
        status_path = args.status_file.resolve()

    # Run the self-healing loop
    certification = orchestrator.run(status_path)

    # Output summary
    print()
    print("═" * 60)
    print("WORKFLOW COMPLETE")
    print("═" * 60)
    print()
    print(f"  Certification ID:  {certification['certification_id']}")
    print(f"  Status:            {certification['status'].upper()}")
    print(f"  Success Rate:      {certification['summary']['success_rate']:.1f}%")
    print(f"  Units Checked:     {certification['summary']['automation_units']}")
    print(f"  Passing:           {certification['summary']['passing']}")
    print(f"  Failing:           {certification['summary']['failing']}")
    print(f"  Fixes Applied:     {certification['summary']['fixes_applied']}")
    print(f"  Retry Cycles:      {certification['summary']['retry_cycles']}")
    print()
    print("  Output Files:")
    for f in output_dir.glob("*.json"):
        print(f"    - {f.name}")
    print()

    # Return exit code based on certification status
    if certification["status"] == "certified":
        print("✓ CERTIFIED - All automation units healthy")
        return 0
    elif certification["status"] == "partial":
        print("⚠ PARTIAL - Some non-critical failures")
        return 1
    else:
        print("✗ FAILED - Certification threshold not met")
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Self-Healing Automation Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  full         Complete workflow: discover → validate → fix → certify (default)
  discover     Only discover automation components
  index-only   Only generate automation_index.json
  validate     Discover and validate (no fixes)
  certify-only Skip discovery, run from existing status file

Examples:
  # Full autonomous run
  python run_autonomous_workflow.py --repo-root /path/to/repo

  # Preview without executing fixes
  python run_autonomous_workflow.py --repo-root /path/to/repo --dry-run

  # Generate index only
  python run_autonomous_workflow.py --repo-root /path/to/repo --mode index-only

  # Run from existing health sweep
  python run_autonomous_workflow.py --repo-root /path/to/repo \\
      --status-file .automation-health/automation_runtime_status.json

Output Files:
  automation_index.json           - Canonical inventory of automation units
  automation_runtime_status.json  - Health check results
  automation_failure_report.json  - Classified failures
  automation_fix_plan.json        - Generated fix plans
  automation_certification.json   - Final certification
  orchestrator_*.jsonl            - Detailed audit log
        """,
    )

    parser.add_argument(
        "--repo-root", type=Path, required=True, help="Repository root path"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".automation-health"),
        help="Output directory for artifacts (default: .automation-health)",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "discover", "index-only", "validate", "certify-only"],
        default="full",
        help="Execution mode (default: full)",
    )
    parser.add_argument(
        "--status-file", type=Path, help="Use existing runtime status file"
    )
    parser.add_argument(
        "--report", type=Path, help="Path to AUTOMATION_COMPONENTS_REPORT.md"
    )
    parser.add_argument(
        "--max-retries", type=int, default=5, help="Maximum retry cycles (default: 5)"
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=5,
        help="Initial retry delay in seconds (default: 5)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Success rate threshold for certification (default: 100.0)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without executing fixes"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    try:
        exit_code = run_workflow(args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nWorkflow failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
