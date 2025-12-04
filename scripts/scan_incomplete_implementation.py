#!/usr/bin/env python3
"""
Systematic incomplete implementation scanner.

Detects stubs, placeholders, missing implementations, and dead-end references
following the rules defined in INCOMPLETE_IMPLEMENTATION_RULES.md.

Usage:
    python scripts/scan_incomplete_implementation.py
    python scripts/scan_incomplete_implementation.py --output .state/incomplete_scan.json
    python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0
"""
# DOC_ID: DOC-SCRIPT-SCAN-INCOMPLETE-IMPLEMENTATION

import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# --- Configuration ---

IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "venv",
    "env",
    ".eggs",
    "build",
    "dist",
}

SEVERITY_MULTIPLIERS = {
    "core/": 3.0,
    "engine/": 3.0,
    "error/": 3.0,
    "aim/": 2.0,
    "pm/": 2.0,
    "specifications/": 2.0,
    "experiments/": 0.1,
    "scratch/": 0.1,
    "_ARCHIVE/": 0.01,
    "legacy/": 0.01,
    "docs/examples/": 0.5,
}

ALLOWED_PATTERNS = [
    r"tests/fixtures/",
    r"docs/examples/",
    r"_ARCHIVE/",
    r"legacy/",
]

# --- Data Structures ---


@dataclass
class Finding:
    """Represents a single incomplete implementation finding."""

    kind: str  # stub_function, stub_class, empty_dir, missing_reference, etc.
    path: str
    symbol: Optional[str] = None
    line: Optional[int] = None
    reason: str = ""
    severity: str = "minor"
    context_score: float = 1.0
    body_preview: str = ""


@dataclass
class ScanResult:
    """Complete scan results."""

    scan_timestamp: str
    codebase_root: str
    stats: Dict[str, int]
    findings: List[Dict]
    summary_by_severity: Dict[str, int]
    summary_by_module: Dict[str, int]


# --- Step 1: Inventory ---


def inventory_codebase(root: Path) -> List[Dict]:
    """Walk the tree and build inventory of all files and directories."""
    inventory = []

    for path in root.rglob("*"):
        # Skip ignored directories
        if any(ignored in path.parts for ignored in IGNORED_DIRS):
            continue

        if path.is_file():
            try:
                size = path.stat().st_size
                lines = len(
                    path.read_text(encoding="utf-8", errors="ignore").splitlines()
                )
            except Exception:
                size = 0
                lines = 0

            inventory.append(
                {
                    "kind": "file",
                    "path": str(path.relative_to(root)),
                    "extension": path.suffix,
                    "size_bytes": size,
                    "num_lines": lines,
                }
            )
        elif path.is_dir():
            # Count files in directory (non-recursive)
            try:
                num_files = len([f for f in path.iterdir() if f.is_file()])
            except Exception:
                num_files = 0

            inventory.append(
                {
                    "kind": "dir",
                    "path": str(path.relative_to(root)),
                    "num_files": num_files,
                }
            )

    return inventory


# --- Step 2: Language-Aware Stub Detection ---


def detect_python_stubs(file_path: Path, content: str) -> List[Finding]:
    """Use AST to detect Python function/class stubs."""
    findings = []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            finding = check_function_stub(node, file_path)
            if finding:
                findings.append(finding)
        elif isinstance(node, ast.ClassDef):
            finding = check_class_stub(node, file_path)
            if finding:
                findings.append(finding)

    return findings


def check_function_stub(node: ast.FunctionDef, file_path: Path) -> Optional[Finding]:
    """Check if a function is a stub."""
    body = node.body

    # Filter out docstrings
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
    ):
        if isinstance(body[0].value.value, str):  # It's a docstring
            body = body[1:]

    if not body:
        return Finding(
            kind="stub_function",
            path=str(file_path),
            symbol=node.name,
            line=node.lineno,
            reason="empty_body",
            body_preview="# Empty function body",
        )

    # Check for single-statement stubs
    if len(body) == 1:
        stmt = body[0]

        # pass
        if isinstance(stmt, ast.Pass):
            return Finding(
                kind="stub_function",
                path=str(file_path),
                symbol=node.name,
                line=node.lineno,
                reason="function_body_is_pass",
                body_preview="    pass",
            )

        # ... (Ellipsis)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value is ...:
                return Finding(
                    kind="stub_function",
                    path=str(file_path),
                    symbol=node.name,
                    line=node.lineno,
                    reason="function_body_is_ellipsis",
                    body_preview="    ...",
                )

        # Ellipsis as expression (Python 3.8+)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Ellipsis):
            return Finding(
                kind="stub_function",
                path=str(file_path),
                symbol=node.name,
                line=node.lineno,
                reason="function_body_is_ellipsis",
                body_preview="    ...",
            )

        # raise NotImplementedError
        if isinstance(stmt, ast.Raise):
            # Check if raising NotImplementedError (as call or name)
            if isinstance(stmt.exc, ast.Call):
                if isinstance(stmt.exc.func, ast.Name):
                    if stmt.exc.func.id in ("NotImplementedError", "NotImplemented"):
                        return Finding(
                            kind="stub_function",
                            path=str(file_path),
                            symbol=node.name,
                            line=node.lineno,
                            reason="raises_not_implemented_error",
                            body_preview="    raise NotImplementedError",
                        )
            elif isinstance(stmt.exc, ast.Name):
                if stmt.exc.id in ("NotImplementedError", "NotImplemented"):
                    return Finding(
                        kind="stub_function",
                        path=str(file_path),
                        symbol=node.name,
                        line=node.lineno,
                        reason="raises_not_implemented_error",
                        body_preview="    raise NotImplementedError",
                    )

    return None


def check_class_stub(node: ast.ClassDef, file_path: Path) -> Optional[Finding]:
    """Check if a class is entirely stub methods."""
    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

    if not methods:
        return None

    stub_methods = sum(
        1 for m in methods if check_function_stub(m, file_path) is not None
    )

    # If all methods are stubs, class is a stub
    if stub_methods == len(methods) and stub_methods > 0:
        return Finding(
            kind="stub_class",
            path=str(file_path),
            symbol=node.name,
            line=node.lineno,
            reason="all_methods_are_stubs",
            body_preview=f"{stub_methods}/{len(methods)} methods are stubs",
        )

    return None


def detect_pattern_stubs(content: str, file_path: Path) -> List[Finding]:
    """Pattern-based stub detection (faster, less precise)."""
    findings = []
    lines = content.splitlines()

    # Look for TODO/FIXME with no real logic
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if any(
            marker in stripped.upper()
            for marker in ["TODO", "FIXME", "TBD", "WIP", "HACK", "STUB", "XXX"]
        ):
            # Check if this is the only content in the function
            # (This is a simple heuristic; AST check is more accurate)
            if re.match(r"^\s*#.*(?:TODO|FIXME|TBD|WIP)", line):
                findings.append(
                    Finding(
                        kind="todo_marker",
                        path=str(file_path),
                        line=i,
                        reason="contains_todo_marker",
                        severity="minor",
                        body_preview=line.strip(),
                    )
                )

    return findings


# --- Step 3: Empty Structure Detection ---


def detect_empty_structures(inventory: List[Dict]) -> List[Finding]:
    """Find empty or useless directories and files."""
    findings = []

    for item in inventory:
        if item["kind"] == "dir":
            # Empty directory
            if item["num_files"] == 0:
                findings.append(
                    Finding(
                        kind="empty_dir",
                        path=item["path"],
                        reason="directory_has_no_files",
                        severity="minor",
                    )
                )

        elif item["kind"] == "file":
            # Trivial files (≤ 3 lines, excluding common patterns)
            if item["num_lines"] <= 3 and item["extension"] == ".py":
                path = Path(item["path"])
                if path.name != "__init__.py":  # __init__.py with imports is OK
                    findings.append(
                        Finding(
                            kind="trivial_file",
                            path=item["path"],
                            reason="file_has_minimal_content",
                            severity="minor",
                            body_preview=f"{item['num_lines']} lines",
                        )
                    )

    return findings


# --- Step 4: Context and Severity Scoring ---


def calculate_severity(finding: Finding, root: Path) -> Tuple[str, float]:
    """Determine severity level and context score."""
    path = finding.path

    # Check if allowed
    if is_allowed_stub(path, finding):
        return "allowed", 0.0

    # Base severity
    base_severity = "minor"
    if finding.kind in ("stub_function", "stub_class"):
        # Check if in critical paths
        for critical_path in ["core/", "engine/", "error/"]:
            if path.startswith(critical_path):
                base_severity = "critical"
                break
        else:
            for major_path in ["aim/", "pm/", "specifications/"]:
                if path.startswith(major_path):
                    base_severity = "major"
                    break

    # Context multiplier
    context_score = 1.0
    for path_prefix, multiplier in SEVERITY_MULTIPLIERS.items():
        if path.startswith(path_prefix):
            context_score = multiplier
            break

    return base_severity, context_score


def is_allowed_stub(path: str, finding: Finding) -> bool:
    """Check if this is an allowed/intentional stub."""
    # Check against allowed patterns
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, path):
            return True

    # Check for inline markers (would need to parse content)
    # For now, simplified check
    if (
        "INCOMPLETE_OK" in finding.body_preview
        or "STUB_ALLOWED" in finding.body_preview
    ):
        return True

    return False


# --- Main Scanner ---


def scan_incomplete_implementations(root: Path) -> ScanResult:
    """Run the complete scan pipeline."""
    print(f"🔍 Scanning {root} for incomplete implementations...")

    # Step 1: Inventory
    print("  → Building codebase inventory...")
    inventory = inventory_codebase(root)

    # Step 2 & 3: Detect stubs and empty structures
    print("  → Detecting stubs and empty structures...")
    all_findings = []

    # Empty structures
    all_findings.extend(detect_empty_structures(inventory))

    # Language-specific stub detection
    for item in inventory:
        if item["kind"] != "file":
            continue

        file_path = root / item["path"]

        if item["extension"] == ".py":
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                all_findings.extend(
                    detect_python_stubs(file_path.relative_to(root), content)
                )
                all_findings.extend(
                    detect_pattern_stubs(content, file_path.relative_to(root))
                )
            except Exception as e:
                print(f"    ⚠️  Error scanning {file_path}: {e}")

    # Step 4: Calculate severity and context
    print("  → Calculating severity and context scores...")
    for finding in all_findings:
        severity, score = calculate_severity(finding, root)
        finding.severity = severity
        finding.context_score = score

    # Generate statistics
    stats = defaultdict(int)
    for finding in all_findings:
        stats[finding.kind] += 1

    summary_by_severity = defaultdict(int)
    for finding in all_findings:
        summary_by_severity[finding.severity] += 1

    summary_by_module = defaultdict(int)
    for finding in all_findings:
        module = finding.path.split("/")[0] if "/" in finding.path else finding.path
        summary_by_module[module] += 1

    # Build result
    result = ScanResult(
        scan_timestamp=datetime.utcnow().isoformat() + "Z",
        codebase_root=str(root),
        stats=dict(stats),
        findings=[asdict(f) for f in all_findings],
        summary_by_severity=dict(summary_by_severity),
        summary_by_module=dict(summary_by_module),
    )

    return result


# --- Output and Reporting ---


def print_summary(result: ScanResult):
    """Print human-readable summary."""
    print("\n" + "=" * 60)
    print("📊 INCOMPLETE IMPLEMENTATION SCAN RESULTS")
    print("=" * 60)
    print(f"Timestamp: {result.scan_timestamp}")
    print(f"Root: {result.codebase_root}")
    print()

    print("By Kind:")
    for kind, count in sorted(result.stats.items()):
        print(f"  {kind:25s}: {count:3d}")
    print()

    print("By Severity:")
    for severity in ["critical", "major", "minor", "allowed"]:
        count = result.summary_by_severity.get(severity, 0)
        icon = {"critical": "🔴", "major": "🟡", "minor": "🔵", "allowed": "⚪"}.get(
            severity, "•"
        )
        print(f"  {icon} {severity:10s}: {count:3d}")
    print()

    print("Top 10 Modules:")
    for module, count in sorted(result.summary_by_module.items(), key=lambda x: -x[1])[
        :10
    ]:
        print(f"  {module:30s}: {count:3d}")
    print()

    # Show top critical findings
    critical = [f for f in result.findings if f["severity"] == "critical"]
    if critical:
        print("🔴 CRITICAL Findings (top 10):")
        for finding in critical[:10]:
            print(
                f"  - {finding['path']}:{finding.get('line', '?')} [{finding['kind']}] {finding.get('symbol', '')}"
            )
            print(f"    Reason: {finding['reason']}")
        print()


def save_results(result: ScanResult, output_path: Path):
    """Save results to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    print(f"✅ Results saved to {output_path}")


def ci_check(result: ScanResult, max_critical: int = 0, max_major: int = 10) -> bool:
    """Check if scan passes CI thresholds."""
    critical_count = result.summary_by_severity.get("critical", 0)
    major_count = result.summary_by_severity.get("major", 0)

    if critical_count > max_critical:
        print(
            f"❌ CI CHECK FAILED: {critical_count} critical findings (max: {max_critical})"
        )
        return False

    if major_count > max_major:
        print(f"❌ CI CHECK FAILED: {major_count} major findings (max: {max_major})")
        return False

    print(
        f"✅ CI CHECK PASSED: {critical_count} critical, {major_count} major findings"
    )
    return True


# --- CLI ---


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scan for incomplete implementations")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Codebase root")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".state/incomplete_scan.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "--ci-check", action="store_true", help="Run CI threshold check"
    )
    parser.add_argument(
        "--max-critical", type=int, default=0, help="Max critical findings for CI"
    )
    parser.add_argument(
        "--max-major", type=int, default=10, help="Max major findings for CI"
    )

    args = parser.parse_args()

    # Run scan
    result = scan_incomplete_implementations(args.root)

    # Print summary
    print_summary(result)

    # Save results
    save_results(result, args.output)

    # CI check
    if args.ci_check:
        success = ci_check(result, args.max_critical, args.max_major)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
