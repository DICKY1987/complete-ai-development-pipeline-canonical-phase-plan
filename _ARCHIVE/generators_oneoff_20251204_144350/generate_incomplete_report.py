#!/usr/bin/env python3
"""
Generate human-readable markdown report from incomplete implementation scan results.

Usage:
    python scripts/generate_incomplete_report.py
    python scripts/generate_incomplete_report.py --input .state/incomplete_scan.json --output reports/incomplete_report.md


DOC_ID: DOC-CORE-GENERATORS-ONEOFF-20251204-144350-774
"""
# DOC_ID: DOC - SCRIPT - SCRIPTS - GENERATE - INCOMPLETE - REPORT - 756
# DOC_ID: DOC-SCRIPT-GENERATE-INCOMPLETE-REPORT

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_scan_results(input_path: Path) -> dict:
    """Load scan results JSON."""
    if not input_path.exists():
        print(f"❌ Scan results not found: {input_path}")
        print(f"   Run: python scripts/scan_incomplete_implementation.py first")
        sys.exit(1)

    return json.loads(input_path.read_text(encoding="utf-8"))


def generate_markdown_report(results: dict) -> str:
    """Generate markdown report from scan results."""
    lines = []

    # Header
    lines.append("# Incomplete Implementation Scan Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Scan Timestamp**: {results['scan_timestamp']}")
    lines.append(f"**Codebase Root**: `{results['codebase_root']}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")

    stats = results["stats"]
    total_findings = sum(stats.values())

    lines.append(f"**Total Findings**: {total_findings}")
    lines.append("")

    # Severity breakdown
    severity = results["summary_by_severity"]
    critical = severity.get("critical", 0)
    major = severity.get("major", 0)
    minor = severity.get("minor", 0)
    allowed = severity.get("allowed", 0)

    lines.append("### By Severity")
    lines.append("")
    lines.append(f"- 🔴 **Critical**: {critical} (blocks release)")
    lines.append(f"- 🟡 **Major**: {major} (should fix before release)")
    lines.append(f"- 🔵 **Minor**: {minor} (low priority)")
    lines.append(f"- ⚪ **Allowed**: {allowed} (whitelisted)")
    lines.append("")

    # Release readiness
    lines.append("### Release Readiness")
    lines.append("")
    if critical == 0 and major == 0:
        lines.append("✅ **READY**: No critical or major incomplete implementations")
    elif critical == 0:
        lines.append(f"⚠️ **CAUTION**: {major} major findings should be addressed")
    else:
        lines.append(f"❌ **BLOCKED**: {critical} critical findings must be fixed")
    lines.append("")
    lines.append("---")
    lines.append("")

    # By Kind
    lines.append("## Findings by Kind")
    lines.append("")
    lines.append("| Kind | Count |")
    lines.append("|------|------:|")
    for kind, count in sorted(stats.items(), key=lambda x: -x[1]):
        lines.append(f"| `{kind}` | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Top modules
    lines.append("## Top 20 Modules with Findings")
    lines.append("")
    module_summary = results["summary_by_module"]
    top_modules = sorted(module_summary.items(), key=lambda x: -x[1])[:20]

    lines.append("| Module | Findings |")
    lines.append("|--------|--------:|")
    for module, count in top_modules:
        lines.append(f"| `{module}` | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Critical findings detail
    findings = results["findings"]
    critical_findings = [f for f in findings if f["severity"] == "critical"]

    if critical_findings:
        lines.append("## 🔴 Critical Findings (MUST FIX)")
        lines.append("")
        lines.append(f"**Count**: {len(critical_findings)}")
        lines.append("")

        # Group by kind
        by_kind = defaultdict(list)
        for finding in critical_findings:
            by_kind[finding["kind"]].append(finding)

        for kind, items in sorted(by_kind.items()):
            lines.append(f"### {kind.replace('_', ' ').title()} ({len(items)})")
            lines.append("")

            for item in items[:20]:  # Limit to 20 per kind
                path = item["path"]
                symbol = item.get("symbol", "")
                line = item.get("line", "")
                reason = item["reason"]

                location = f"{path}:{line}" if line else path
                symbol_text = f" `{symbol}`" if symbol else ""

                lines.append(f"- **{location}**{symbol_text}")
                lines.append(f"  - Reason: `{reason}`")
                if item.get("body_preview"):
                    lines.append(f"  - Preview: `{item['body_preview'][:80]}`")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Major findings summary
    major_findings = [f for f in findings if f["severity"] == "major"]

    if major_findings:
        lines.append("## 🟡 Major Findings (Should Fix)")
        lines.append("")
        lines.append(f"**Count**: {len(major_findings)}")
        lines.append("")

        # Group by module
        by_module = defaultdict(list)
        for finding in major_findings:
            module = (
                finding["path"].split("/")[0]
                if "/" in finding["path"]
                else finding["path"]
            )
            by_module[module].append(finding)

        lines.append("### By Module")
        lines.append("")
        lines.append("| Module | Count | Top Issue |")
        lines.append("|--------|------:|-----------|")

        for module, items in sorted(by_module.items(), key=lambda x: -len(x[1]))[:15]:
            top_issue = items[0]
            symbol = top_issue.get("symbol", top_issue["kind"])
            lines.append(f"| `{module}` | {len(items)} | `{symbol}` |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Minor findings summary
    minor_findings = [f for f in findings if f["severity"] == "minor"]

    if minor_findings:
        lines.append("## 🔵 Minor Findings (Low Priority)")
        lines.append("")
        lines.append(f"**Count**: {len(minor_findings)}")
        lines.append("")

        # Stats by kind
        minor_by_kind = defaultdict(int)
        for finding in minor_findings:
            minor_by_kind[finding["kind"]] += 1

        lines.append("| Kind | Count |")
        lines.append("|------|------:|")
        for kind, count in sorted(minor_by_kind.items(), key=lambda x: -x[1]):
            lines.append(f"| `{kind}` | {count} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    if critical > 0:
        lines.append("### Immediate Actions Required")
        lines.append("")
        lines.append("1. **Fix all critical stubs** in core modules before release")
        lines.append("2. Review each critical finding and either:")
        lines.append("   - Implement the missing functionality")
        lines.append("   - Remove the stub if no longer needed")
        lines.append("   - Whitelist if intentional (with justification)")
        lines.append("")

    if major > 0:
        lines.append("### Before Release")
        lines.append("")
        lines.append("1. Address major stubs in domain modules")
        lines.append("2. Update documentation for any deferred implementations")
        lines.append("3. Add tracking issues for postponed work")
        lines.append("")

    if minor > 100:
        lines.append("### Code Cleanup")
        lines.append("")
        lines.append(f"1. {minor} minor findings suggest technical debt")
        lines.append("2. Consider cleanup sprint to:")
        lines.append("   - Remove empty directories")
        lines.append("   - Resolve or track TODO markers")
        lines.append("   - Archive unused experimental code")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("## How to Use This Report")
    lines.append("")
    lines.append("1. **Prioritize critical findings** - These block release")
    lines.append("2. **Plan fixes for major findings** - Schedule before release")
    lines.append("3. **Track minor findings** - Address during cleanup sprints")
    lines.append("4. **Review regularly** - Run scanner in CI to prevent regression")
    lines.append("")
    lines.append("**Run scanner**: `python scripts/scan_incomplete_implementation.py`")
    lines.append("")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate markdown report from scan results"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(".state/incomplete_scan.json"),
        help="Input scan results JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/incomplete_report.md"),
        help="Output markdown report path",
    )

    args = parser.parse_args()

    # Load results
    print(f"📖 Loading scan results from {args.input}...")
    results = load_scan_results(args.input)

    # Generate report
    print("📝 Generating markdown report...")
    report = generate_markdown_report(results)

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")

    print(f"✅ Report saved to {args.output}")
    print("")
    print("📊 Summary:")
    print(f"   Total findings: {sum(results['stats'].values())}")
    print(f"   Critical: {results['summary_by_severity'].get('critical', 0)}")
    print(f"   Major: {results['summary_by_severity'].get('major', 0)}")
    print(f"   Minor: {results['summary_by_severity'].get('minor', 0)}")


if __name__ == "__main__":
    main()
