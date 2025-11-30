#!/usr/bin/env python3
"""
Scan codebase for deprecated import patterns.

Legacy path patterns have been removed from the repository; this script remains
as a guardrail scaffold and can be repopulated if new deprecated namespaces
emerge. It currently reports success by default.
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-CHECK-DEPRECATED-USAGE-196
# DOC_ID: DOC-SCRIPT-SCRIPTS-CHECK-DEPRECATED-USAGE-133

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Populated when new deprecated patterns are introduced; intentionally empty now.
DEPRECATED_PATTERNS: Dict[str, str] = {}


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Scan a single file for deprecated imports."""
    results: List[Tuple[int, str, str]] = []
    if not DEPRECATED_PATTERNS:
        return results
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                for old_pattern, new_pattern in DEPRECATED_PATTERNS.items():
                    if old_pattern in line:
                        results.append((line_num, line.strip(), new_pattern))
    except (UnicodeDecodeError, PermissionError):
        pass
    return results


def scan_directory(path: Path, exclude_patterns: List[str] | None = None) -> Dict[str, List[Tuple[int, str, str]]]:
    """Recursively scan a directory for deprecated imports."""
    results: Dict[str, List[Tuple[int, str, str]]] = {}
    for py_file in path.rglob("*.py"):
        file_results = scan_file(py_file)
        if file_results:
            results[str(py_file)] = file_results
    return results


def generate_report(results: Dict[str, List[Tuple[int, str, str]]], output_format: str = "text") -> str:
    """Generate a report of deprecated usage."""
    if output_format == "json":
        json_results = {
            filepath: [
                {"line": line_num, "deprecated": old_import, "suggested": new_import}
                for line_num, old_import, new_import in issues
            ]
            for filepath, issues in results.items()
        }
        return json.dumps(json_results, indent=2)

    if not results:
        return "✓ No deprecated imports found."

    total_issues = sum(len(issues) for issues in results.values())
    lines = [f"Found {total_issues} deprecated import(s) in {len(results)} file(s)"]
    for filepath, issues in sorted(results.items()):
        lines.append(f"\n{filepath} ({len(issues)} issue(s))")
        for line_num, old_import, new_import in issues:
            lines.append(f"  L{line_num}: {old_import} -> {new_import}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for deprecated imports")
    parser.add_argument("--path", type=Path, default=Path("."), help="Path to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = scan_directory(args.path)
    report = generate_report(results, "json" if args.json else "text")
    print(report)
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
