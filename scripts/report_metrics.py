#!/usr/bin/env python
"""Metrics reporting CLI for parallel execution.

Phase I WS-I9: Metrics and reporting utilities.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine.metrics import MetricsAggregator


def show_metrics(run_id: str) -> None:
    """Show metrics for a run."""
    aggregator = MetricsAggregator()
    report = aggregator.generate_report(run_id)
    print(report)


def export_json(run_id: str, output_file: str) -> None:
    """Export metrics to JSON."""
    aggregator = MetricsAggregator()
    aggregator.export_metrics_json(run_id, output_file)
    print(f"✓ Metrics exported to {output_file}")


def compare_runs(run_ids: list[str]) -> None:
    """Compare metrics across multiple runs."""
    aggregator = MetricsAggregator()
    
    print("=" * 80)
    print("RUN COMPARISON")
    print("=" * 80)
    print()
    
    print(f"{'Run ID':<30} {'Duration(s)':<12} {'Cost($)':<12} {'Completed':<12} {'Failed':<12}")
    print("-" * 80)
    
    for run_id in run_ids:
        try:
            metrics = aggregator.compute_metrics(run_id)
            print(f"{run_id:<30} {metrics.total_duration_sec:<12.1f} "
                  f"${metrics.total_cost_usd:<11.4f} {metrics.workstreams_completed:<12} "
                  f"{metrics.workstreams_failed:<12}")
        except Exception as e:
            print(f"{run_id:<30} ERROR: {e}")
    
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Metrics and reporting for parallel execution")
    
    subparsers = parser.add_subparsers(dest='command', help='Metrics command')
    
    # Show metrics
    show_parser = subparsers.add_parser('show', help='Show execution metrics')
    show_parser.add_argument('--run-id', required=True, help='Run ID')
    
    # Export JSON
    export_parser = subparsers.add_parser('export', help='Export metrics to JSON')
    export_parser.add_argument('--run-id', required=True, help='Run ID')
    export_parser.add_argument('--output', required=True, help='Output JSON file')
    
    # Compare runs
    compare_parser = subparsers.add_parser('compare', help='Compare multiple runs')
    compare_parser.add_argument('--run-ids', nargs='+', required=True, help='Run IDs to compare')
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'show':
            show_metrics(args.run_id)
        elif args.command == 'export':
            export_json(args.run_id, args.output)
        elif args.command == 'compare':
            compare_runs(args.run_ids)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
