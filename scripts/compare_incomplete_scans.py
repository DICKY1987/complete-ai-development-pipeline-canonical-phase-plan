#!/usr/bin/env python3
"""
Compare two incomplete implementation scan results to track trends.

Usage:
    python scripts/compare_incomplete_scans.py scan1.json scan2.json
    python scripts/compare_incomplete_scans.py .state/incomplete_scan_20251203.json .state/incomplete_scan_20251204.json
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-COMPARE-INCOMPLETE-SCANS-759
DOC_ID: DOC - SCRIPT - SCRIPTS - COMPARE - INCOMPLETE - SCANS - 754
# DOC_ID: DOC-SCRIPT-COMPARE-INCOMPLETE-SCANS

import json
import sys
from pathlib import Path
from typing import Dict, Set, Tuple


def load_scan(path: Path) -> dict:
    """Load a scan results JSON file."""
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def compare_stats(old: dict, new: dict) -> Dict[str, Dict]:
    """Compare statistics between two scans."""
    old_stats = old["stats"]
    new_stats = new["stats"]

    all_kinds = set(old_stats.keys()) | set(new_stats.keys())

    comparison = {}
    for kind in all_kinds:
        old_count = old_stats.get(kind, 0)
        new_count = new_stats.get(kind, 0)
        diff = new_count - old_count

        comparison[kind] = {
            "old": old_count,
            "new": new_count,
            "diff": diff,
            "pct_change": (diff / old_count * 100) if old_count > 0 else 0,
        }

    return comparison


def compare_severity(old: dict, new: dict) -> Dict[str, Dict]:
    """Compare severity breakdown."""
    old_sev = old["summary_by_severity"]
    new_sev = new["summary_by_severity"]

    severities = ["critical", "major", "minor", "allowed"]

    comparison = {}
    for sev in severities:
        old_count = old_sev.get(sev, 0)
        new_count = new_sev.get(sev, 0)
        diff = new_count - old_count

        comparison[sev] = {"old": old_count, "new": new_count, "diff": diff}

    return comparison


def find_new_stubs(old: dict, new: dict) -> list:
    """Find stubs that exist in new but not in old."""
    old_stubs = {
        (f["path"], f.get("symbol", ""), f.get("line", 0)) for f in old["findings"]
    }
    new_stubs = [
        (f["path"], f.get("symbol", ""), f.get("line", 0), f) for f in new["findings"]
    ]

    return [
        finding
        for (path, symbol, line, finding) in new_stubs
        if (path, symbol, line) not in old_stubs
    ]


def find_fixed_stubs(old: dict, new: dict) -> list:
    """Find stubs that existed in old but not in new (fixed)."""
    old_stubs = [
        (f["path"], f.get("symbol", ""), f.get("line", 0), f) for f in old["findings"]
    ]
    new_stubs = {
        (f["path"], f.get("symbol", ""), f.get("line", 0)) for f in new["findings"]
    }

    return [
        finding
        for (path, symbol, line, finding) in old_stubs
        if (path, symbol, line) not in new_stubs
    ]


def print_comparison(old_path: Path, new_path: Path, old: dict, new: dict):
    """Print human-readable comparison."""
    print("=" * 70)
    print("INCOMPLETE IMPLEMENTATION SCAN COMPARISON")
    print("=" * 70)
    print(f"Old scan: {old_path.name} ({old['scan_timestamp']})")
    print(f"New scan: {new_path.name} ({new['scan_timestamp']})")
    print()

    # Stats comparison
    print("📊 STATISTICS COMPARISON")
    print("-" * 70)
    print(f"{'Kind':<25} {'Old':>8} {'New':>8} {'Diff':>8} {'% Change':>10}")
    print("-" * 70)

    stats_comp = compare_stats(old, new)
    for kind, data in sorted(stats_comp.items(), key=lambda x: -abs(x[1]["diff"])):
        old_count = data["old"]
        new_count = data["new"]
        diff = data["diff"]
        pct = data["pct_change"]

        diff_str = f"{diff:+d}" if diff != 0 else "0"
        pct_str = f"{pct:+.1f}%" if pct != 0 else "0%"
        icon = "📈" if diff > 0 else ("📉" if diff < 0 else "➡️")

        print(
            f"{kind:<25} {old_count:8d} {new_count:8d} {diff_str:>8} {pct_str:>10} {icon}"
        )

    print()

    # Severity comparison
    print("🎯 SEVERITY COMPARISON")
    print("-" * 70)
    sev_comp = compare_severity(old, new)

    for sev, data in sev_comp.items():
        old_count = data["old"]
        new_count = data["new"]
        diff = data["diff"]

        icon = {"critical": "🔴", "major": "🟡", "minor": "🔵", "allowed": "⚪"}.get(
            sev, "•"
        )
        status = "✅" if diff <= 0 else "⚠️"

        print(
            f"{icon} {sev.title():<15}: {old_count:3d} → {new_count:3d} ({diff:+d}) {status}"
        )

    print()

    # New stubs (regressions)
    new_stubs = find_new_stubs(old, new)
    if new_stubs:
        print(f"🆕 NEW STUBS (REGRESSIONS): {len(new_stubs)}")
        print("-" * 70)

        # Show top 10 by severity
        critical = [f for f in new_stubs if f["severity"] == "critical"]
        major = [f for f in new_stubs if f["severity"] == "major"]
        minor = [f for f in new_stubs if f["severity"] == "minor"]

        if critical:
            print(f"\n🔴 Critical ({len(critical)}):")
            for f in critical[:5]:
                print(
                    f"  - {f['path']}:{f.get('line', '?')} [{f['kind']}] {f.get('symbol', '')}"
                )

        if major:
            print(f"\n🟡 Major ({len(major)}):")
            for f in major[:5]:
                print(
                    f"  - {f['path']}:{f.get('line', '?')} [{f['kind']}] {f.get('symbol', '')}"
                )

        if minor and len(minor) <= 10:
            print(f"\n🔵 Minor ({len(minor)}):")
            for f in minor[:5]:
                print(
                    f"  - {f['path']}:{f.get('line', '?')} [{f['kind']}] {f.get('symbol', '')}"
                )

        print()

    # Fixed stubs (improvements)
    fixed_stubs = find_fixed_stubs(old, new)
    if fixed_stubs:
        print(f"✅ FIXED STUBS (IMPROVEMENTS): {len(fixed_stubs)}")
        print("-" * 70)

        # Group by kind
        by_kind = {}
        for f in fixed_stubs:
            kind = f["kind"]
            by_kind.setdefault(kind, []).append(f)

        for kind, items in sorted(by_kind.items(), key=lambda x: -len(x[1]))[:5]:
            print(f"  {kind}: {len(items)} fixed")
            for f in items[:3]:
                print(f"    - {f['path']}:{f.get('line', '?')} {f.get('symbol', '')}")

        print()

    # Overall assessment
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    total_old = sum(old["stats"].values())
    total_new = sum(new["stats"].values())
    total_diff = total_new - total_old

    critical_diff = sev_comp["critical"]["diff"]
    major_diff = sev_comp["major"]["diff"]

    if critical_diff > 0:
        print("❌ REGRESSION: New critical stubs introduced!")
    elif critical_diff < 0:
        print("✅ IMPROVEMENT: Critical stubs fixed!")

    if major_diff > 0:
        print("⚠️ CAUTION: New major stubs introduced")
    elif major_diff < 0:
        print("✅ IMPROVEMENT: Major stubs fixed!")

    if total_diff > 0:
        print(f"📈 Overall: {total_diff} more findings ({total_old} → {total_new})")
    elif total_diff < 0:
        print(
            f"📉 Overall: {abs(total_diff)} fewer findings ({total_old} → {total_new})"
        )
    else:
        print(f"➡️ Overall: No change ({total_old} findings)")

    print()

    # Recommendation
    if critical_diff > 0 or len(new_stubs) > 10:
        print("⚠️ RECOMMENDATION: Review new stubs before merging")
    elif critical_diff == 0 and major_diff <= 0:
        print("✅ RECOMMENDATION: Changes look good, no new blockers")
    else:
        print("ℹ️ RECOMMENDATION: Minor increase in stubs, track but not blocking")

    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare two incomplete implementation scans"
    )
    parser.add_argument("old_scan", type=Path, help="Path to older scan results")
    parser.add_argument("new_scan", type=Path, help="Path to newer scan results")
    parser.add_argument("--json", action="store_true", help="Output comparison as JSON")

    args = parser.parse_args()

    # Load scans
    old = load_scan(args.old_scan)
    new = load_scan(args.new_scan)

    if args.json:
        # JSON output for automation
        comparison = {
            "old_scan": str(args.old_scan),
            "new_scan": str(args.new_scan),
            "old_timestamp": old["scan_timestamp"],
            "new_timestamp": new["scan_timestamp"],
            "stats_comparison": compare_stats(old, new),
            "severity_comparison": compare_severity(old, new),
            "new_stubs": [
                {
                    "path": f["path"],
                    "symbol": f.get("symbol", ""),
                    "line": f.get("line", 0),
                    "severity": f["severity"],
                }
                for f in find_new_stubs(old, new)
            ],
            "fixed_stubs": [
                {
                    "path": f["path"],
                    "symbol": f.get("symbol", ""),
                    "line": f.get("line", 0),
                    "severity": f["severity"],
                }
                for f in find_fixed_stubs(old, new)
            ],
        }
        print(json.dumps(comparison, indent=2))
    else:
        # Human-readable output
        print_comparison(args.old_scan, args.new_scan, old, new)


if __name__ == "__main__":
    main()
