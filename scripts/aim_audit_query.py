#!/usr/bin/env python3
"""AIM Audit Log Query CLI Utility

Query and filter AIM audit logs with various output formats.

Usage:
    python scripts/aim_audit_query.py [OPTIONS]

Examples:
    python scripts/aim_audit_query.py --tool aider
    python scripts/aim_audit_query.py --capability code_generation --since 2025-11-15
    python scripts/aim_audit_query.py --format json
    python scripts/aim_audit_query.py --tool aider --format csv > results.csv
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-AIM-AUDIT-QUERY-183
# DOC_ID: DOC-SCRIPT-SCRIPTS-AIM-AUDIT-QUERY-120

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aim.bridge import get_aim_registry_path


def load_audit_logs(
    audit_dir: Path,
    tool_filter: str = None,
    capability_filter: str = None,
    since_date: str = None
):
    """Load and filter audit logs from AIM_audit directory.

    Args:
        audit_dir: Path to AIM_audit directory
        tool_filter: Filter by tool ID (optional)
        capability_filter: Filter by capability (optional)
        since_date: Filter by date (YYYY-MM-DD) (optional)

    Returns:
        List[dict]: Filtered audit log entries
    """
    if not audit_dir.exists():
        return []

    entries = []

    # Parse since_date if provided
    since_dt = None
    if since_date:
        try:
            since_dt = datetime.strptime(since_date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{since_date}'. Use YYYY-MM-DD.")
            return []

    # Iterate through date directories
    for date_dir in sorted(audit_dir.iterdir()):
        if not date_dir.is_dir():
            continue

        # Check if date is after since_date
        if since_dt:
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < since_dt:
                    continue
            except ValueError:
                continue

        # Load all JSON files in date directory
        for audit_file in sorted(date_dir.glob("*.json")):
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)

                # Apply filters
                if tool_filter and entry.get("tool_id") != tool_filter:
                    continue

                if capability_filter and entry.get("capability") != capability_filter:
                    continue

                entries.append(entry)

            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not read {audit_file}: {e}", file=sys.stderr)
                continue

    return entries


def print_text_format(entries):
    """Print audit log entries in human-readable text format."""
    if not entries:
        print("No audit log entries found.")
        return

    print(f"Found {len(entries)} audit log entries:\n")
    print("=" * 80)

    for i, entry in enumerate(entries, 1):
        timestamp = entry.get("timestamp", "N/A")
        tool_id = entry.get("tool_id", "N/A")
        capability = entry.get("capability", "N/A")
        success = entry.get("result", {}).get("success", False)
        success_str = "SUCCESS" if success else "FAILED"
        message = entry.get("result", {}).get("message", "N/A")

        print(f"[{i}] {timestamp}")
        print(f"    Tool:       {tool_id}")
        print(f"    Capability: {capability}")
        print(f"    Status:     {success_str}")
        print(f"    Message:    {message}")
        print()

    print("=" * 80)


def print_json_format(entries):
    """Print audit log entries in JSON format."""
    output = {
        "count": len(entries),
        "entries": entries
    }
    print(json.dumps(output, indent=2))


def print_csv_format(entries):
    """Print audit log entries in CSV format."""
    if not entries:
        return

    # Define CSV columns
    fieldnames = ["timestamp", "tool_id", "capability", "success", "message"]

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for entry in entries:
        row = {
            "timestamp": entry.get("timestamp", ""),
            "tool_id": entry.get("tool_id", ""),
            "capability": entry.get("capability", ""),
            "success": entry.get("result", {}).get("success", False),
            "message": entry.get("result", {}).get("message", "")
        }
        writer.writerow(row)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query AIM audit logs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--tool",
        help="Filter by tool ID (e.g., 'aider')"
    )

    parser.add_argument(
        "--capability",
        help="Filter by capability (e.g., 'code_generation')"
    )

    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Filter by date (inclusive)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Get AIM registry path
    try:
        aim_path = get_aim_registry_path()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    audit_dir = aim_path / "AIM_audit"

    # Load and filter audit logs
    entries = load_audit_logs(
        audit_dir,
        tool_filter=args.tool,
        capability_filter=args.capability,
        since_date=args.since
    )

    # Print in requested format
    if args.format == "json":
        print_json_format(entries)
    elif args.format == "csv":
        print_csv_format(entries)
    else:
        print_text_format(entries)

    return 0


if __name__ == "__main__":
    sys.exit(main())
