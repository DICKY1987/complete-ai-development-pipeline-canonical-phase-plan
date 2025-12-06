#!/usr/bin/env python3
"""
Systematic incomplete implementation scanner.

Detects stubs, placeholders, missing implementations, and dead-end references
following the rules defined in INCOMPLETE_IMPLEMENTATION_RULES.md and
incomplete_implementation_scan_spec.json.

Usage (summary):
    python scripts/scan_incomplete_implementation.py
    python scripts/scan_incomplete_implementation.py --output .state/incomplete_scan_summary.json
    python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0 --max-major 10


DOC_ID: DOC-CORE-SYSTEM-ANALYZE-SYS-SCAN-INCOMPLETE-750
"""
# DOC_ID: DOC-SCRIPT-SCAN-INCOMPLETE-IMPLEMENTATION

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# --- Configuration defaults ---

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "env",
    ".eggs",
    "build",
    "dist",
    ".idea",
    ".vscode",
    ".DS_Store",
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

DEFAULT_ALLOWLIST_MARKERS = ("INCOMPLETE_OK", "STUB_ALLOWED")
DEFAULT_TINY_FILE_THRESHOLD = 3
DEFAULT_ALLOWLIST_FILE = Path("incomplete_allowlist.yaml")

PY_STUB_PATTERNS = (
    "pass",
    "...",
    "raise NotImplementedError",
    "raise NotImplemented",
)
JS_TS_STUB_PATTERNS = (
    'throw new Error("Not implemented")',
    "throw new Error('Not implemented')",
    "throw new Error(`Not implemented`)",
)
TODO_MARKERS = ("TODO", "FIXME", "TBD", "WIP", "HACK", "STUB", "XXX")


# --- Data Structures ---


@dataclass
class Finding:
    """Represents a single incomplete implementation finding."""

    kind: str  # stub_function, stub_class, empty_dir, missing_reference, etc.
    path: str
    symbol: Optional[str] = None
    line: Optional[int] = None
    reason: str = ""
    language: Optional[str] = None
    severity: str = "minor"
    context_score: float = 1.0
    body_preview: str = ""
    metadata: Optional[Dict] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Complete scan results."""

    scan_timestamp: str
    codebase_root: str
    stats: Dict[str, int]
    findings: List[Dict]
    summary_by_severity: Dict[str, int]
    summary_by_module: Dict[str, int]
    dependency_graph: Dict[str, List[str]]


@dataclass
class AllowlistConfig:
    """Paths/symbols explicitly allowed as incomplete."""

    path_patterns: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)
    markers: Tuple[str, ...] = DEFAULT_ALLOWLIST_MARKERS


# --- Allowlist handling ---


def load_allowlist_config(path: Path) -> AllowlistConfig:
    """Load allowlist YAML if available."""
    if not path.exists():
        return AllowlistConfig()

    if yaml is None:
        print(f"[warn] PyYAML not installed, skipping allowlist file at {path}")
        return AllowlistConfig()

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    path_patterns: List[str] = []
    symbols: List[str] = []

    for item in data.get("allowed_stubs", []):
        pattern = item.get("pattern")
        if pattern:
            path_patterns.append(pattern)
        path_value = item.get("path")
        if path_value:
            path_patterns.append(path_value)
    for item in data.get("exceptions", []):
        if "path" in item:
            path_patterns.append(item["path"])
        if "symbol" in item:
            symbols.append(item["symbol"])

    return AllowlistConfig(path_patterns=path_patterns, symbols=symbols)


# --- Inventory ---


def should_ignore(path_parts: Tuple[str, ...], ignored_dirs: Set[str]) -> bool:
    """Return True if any part is in ignored list."""
    return any(part in ignored_dirs for part in path_parts)


def inventory_codebase(
    root: Path, ignored_dirs: Set[str]
) -> Tuple[List[Dict], List[Dict]]:
    """Walk the tree and build inventory of all files and directories."""
    file_inventory: List[Dict] = []
    dir_inventory: List[Dict] = []

    for current_dir, dirs, files in os.walk(root):
        rel_dir = Path(current_dir).relative_to(root)
        if should_ignore(rel_dir.parts, ignored_dirs):
            dirs[:] = []
            continue

        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        dir_inventory.append(
            {
                "kind": "dir",
                "path": str(rel_dir) if str(rel_dir) != "." else ".",
                "num_files": len(files),
                "num_subdirs": len(dirs),
            }
        )

        for fname in files:
            fpath = Path(current_dir) / fname
            rel_path = fpath.relative_to(root)
            if should_ignore(rel_path.parts, ignored_dirs):
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                num_lines = len(content.splitlines())
                size_bytes = fpath.stat().st_size
            except Exception:
                content = ""
                num_lines = 0
                size_bytes = 0

            file_inventory.append(
                {
                    "kind": "file",
                    "path": rel_path.as_posix(),
                    "extension": fpath.suffix,
                    "size_bytes": size_bytes,
                    "num_lines": num_lines,
                }
            )

    return file_inventory, dir_inventory


# --- Stub and structure detection ---


def detect_python_stubs(file_path: Path, content: str) -> List[Finding]:
    """Use AST to detect Python function/class stubs."""
    findings: List[Finding] = []

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


def detect_js_ts_stubs(file_path: Path, content: str) -> List[Finding]:
    """Detect JS/TS stubs by simple pattern checks."""
    findings: List[Finding] = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if any(pattern in stripped for pattern in JS_TS_STUB_PATTERNS):
            findings.append(
                Finding(
                    kind="stub_function",
                    path=str(file_path),
                    line=i,
                    language="javascript_typescript",
                    reason="raises_not_implemented_error",
                    body_preview=stripped[:120],
                )
            )
    return findings


def check_function_stub(node: ast.FunctionDef, file_path: Path) -> Optional[Finding]:
    """Check if a function is a stub."""
    body = list(node.body)

    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
    ):
        if isinstance(body[0].value.value, str):
            body = body[1:]

    if not body:
        return Finding(
            kind="stub_function",
            path=str(file_path),
            symbol=node.name,
            line=node.lineno,
            reason="empty_body",
            language="python",
            body_preview="# Empty function body",
        )

    if len(body) == 1:
        stmt = body[0]

        if isinstance(stmt, ast.Pass):
            return Finding(
                kind="stub_function",
                path=str(file_path),
                symbol=node.name,
                line=node.lineno,
                reason="function_body_is_pass",
                language="python",
                body_preview="pass",
            )

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value is ...:
                return Finding(
                    kind="stub_function",
                    path=str(file_path),
                    symbol=node.name,
                    line=node.lineno,
                    reason="function_body_is_ellipsis",
                    language="python",
                    body_preview="...",
                )

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Ellipsis):
            return Finding(
                kind="stub_function",
                path=str(file_path),
                symbol=node.name,
                line=node.lineno,
                reason="function_body_is_ellipsis",
                language="python",
                body_preview="...",
            )

        if (
            isinstance(stmt, ast.Return)
            and isinstance(stmt.value, ast.Constant)
            and stmt.value.value is None
        ):
            return Finding(
                kind="stub_function",
                path=str(file_path),
                symbol=node.name,
                line=node.lineno,
                reason="returns_none_only",
                language="python",
                body_preview="return None",
            )

        if isinstance(stmt, ast.Raise):
            if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                if stmt.exc.func.id in ("NotImplementedError", "NotImplemented"):
                    return Finding(
                        kind="stub_function",
                        path=str(file_path),
                        symbol=node.name,
                        line=node.lineno,
                        reason="raises_not_implemented_error",
                        language="python",
                        body_preview="raise NotImplementedError",
                    )
            elif isinstance(stmt.exc, ast.Name) and stmt.exc.id in (
                "NotImplementedError",
                "NotImplemented",
            ):
                return Finding(
                    kind="stub_function",
                    path=str(file_path),
                    symbol=node.name,
                    line=node.lineno,
                    reason="raises_not_implemented_error",
                    language="python",
                    body_preview="raise NotImplementedError",
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
    if stub_methods == len(methods) and stub_methods > 0:
        return Finding(
            kind="stub_class",
            path=str(file_path),
            symbol=node.name,
            line=node.lineno,
            reason="all_methods_are_stubs",
            language="python",
            body_preview=f"{stub_methods}/{len(methods)} methods are stubs",
        )
    return None


def detect_pattern_stubs(content: str, file_path: Path) -> List[Finding]:
    """Pattern-based stub detection (markers)."""
    findings: List[Finding] = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        upper = line.upper()
        if any(marker in upper for marker in TODO_MARKERS):
            findings.append(
                Finding(
                    kind="todo_marker",
                    path=str(file_path),
                    line=i,
                    reason="contains_todo_marker",
                    severity="minor",
                    body_preview=line.strip()[:200],
                )
            )
    return findings


def detect_empty_structures(
    file_inventory: List[Dict],
    dir_inventory: List[Dict],
    tiny_file_threshold: int,
) -> List[Finding]:
    """Find empty or useless directories and files."""
    findings: List[Finding] = []

    for item in dir_inventory:
        if item["num_files"] == 0 and item["num_subdirs"] == 0 and item["path"] != ".":
            findings.append(
                Finding(
                    kind="empty_dir",
                    path=item["path"],
                    reason="directory_has_no_files",
                    severity="minor",
                )
            )

    for item in file_inventory:
        if item["num_lines"] <= tiny_file_threshold:
            path = Path(item["path"])
            if path.name == "__init__.py":
                continue
            findings.append(
                Finding(
                    kind="trivial_file",
                    path=item["path"],
                    reason="file_has_minimal_content",
                    severity="info",
                    body_preview=f"{item['num_lines']} lines",
                )
            )
    return findings


# --- Imports, references, dependency graph ---


def path_to_module(path: str) -> str:
    """Convert path/to/module.py to dotted path."""
    return Path(path).with_suffix("").as_posix().replace("/", ".")


def build_module_index(file_inventory: List[Dict]) -> Set[str]:
    """Create module index for python files."""
    modules = set()
    for item in file_inventory:
        if item["kind"] == "file" and item.get("extension") == ".py":
            modules.add(path_to_module(item["path"]))
    return modules


def extract_python_imports(content: str, current_module: str) -> Set[str]:
    """Return imported module names."""
    imports: Set[str] = set()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level and current_module:
                base_parts = current_module.split(".")[: -node.level]
                if module:
                    base_parts.extend(module.split("."))
                resolved = ".".join(part for part in base_parts if part)
                if resolved:
                    imports.add(resolved)
            elif module:
                imports.add(module)
    return imports


def detect_missing_references(
    file_inventory: List[Dict],
    root: Path,
    module_index: Set[str],
    content_cache: Dict[str, str],
) -> List[Finding]:
    """Identify imports to missing modules."""
    findings: List[Finding] = []
    for item in file_inventory:
        if item["extension"] != ".py":
            continue
        path = item["path"]
        current_module = path_to_module(path)
        content = content_cache.get(path)
        if content is None:
            try:
                content = (root / path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            content_cache[path] = content

        imports = extract_python_imports(content, current_module)
        for imp in imports:
            if not any(mod.startswith(imp) for mod in module_index):
                findings.append(
                    Finding(
                        kind="missing_reference",
                        path=path,
                        symbol=imp,
                        reason="import_module_not_found",
                        language="python",
                        severity="major",
                    )
                )
    return findings


def build_dependency_graph(
    file_inventory: List[Dict],
    root: Path,
    module_index: Set[str],
    content_cache: Dict[str, str],
) -> Dict[str, List[str]]:
    """Build file-level dependency graph using python imports (best effort)."""
    graph: Dict[str, List[str]] = defaultdict(list)
    for item in file_inventory:
        if item["extension"] != ".py":
            continue
        path = item["path"]
        current_module = path_to_module(path)
        content = content_cache.get(path)
        if content is None:
            try:
                content = (root / path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""
            content_cache[path] = content
        imports = extract_python_imports(content, current_module)
        for imp in imports:
            for module in module_index:
                if module.startswith(imp):
                    graph[path].append(module.replace(".", "/") + ".py")
                    break
    return graph


def detect_orphans(
    graph: Dict[str, List[str]],
    module_index: Set[str],
    content_cache: Dict[str, str],
    entrypoint_hints: Tuple[str, ...],
) -> List[Finding]:
    """Mark orphan modules with no inbound edges and not entrypoints."""
    inbound: Dict[str, int] = defaultdict(int)
    for src, targets in graph.items():
        for tgt in targets:
            inbound[tgt] += 1

    orphans: List[Finding] = []
    for module in module_index:
        path = module.replace(".", "/") + ".py"
        if inbound.get(path, 0) > 0:
            continue
        content = content_cache.get(path, "")
        if any(hint in path for hint in entrypoint_hints) or "__main__" in content:
            continue
        if path.startswith("tests/"):
            continue
        orphans.append(
            Finding(
                kind="orphan_module",
                path=path,
                reason="no_inbound_references",
                language="python",
                severity="minor",
            )
        )
    return orphans


# --- Severity and allowlist ---


def is_allowed_stub(
    path: str,
    finding: Finding,
    allowlist: AllowlistConfig,
    content_cache: Dict[str, str],
) -> bool:
    """Check allowlist markers and patterns."""
    normalized = path.replace("\\", "/")
    posix_obj = Path(normalized)

    def _matches(pattern: str) -> bool:
        simplified = pattern.replace("**/", "").replace("**", "*")
        return (
            posix_obj.match(pattern)
            or fnmatch(normalized, pattern)
            or fnmatch(normalized, simplified)
            or normalized.startswith(pattern.rstrip("*"))
        )

    for pattern in allowlist.path_patterns:
        if _matches(pattern):
            return True

    if finding.symbol and finding.symbol in allowlist.symbols:
        return True

    content = content_cache.get(normalized, "")
    if any(marker in content for marker in allowlist.markers):
        return True
    if any(marker in finding.body_preview for marker in allowlist.markers):
        return True
    return False


def calculate_severity(
    finding: Finding,
    root: Path,
    allowlist: Optional[AllowlistConfig] = None,
    content_cache: Optional[Dict[str, str]] = None,
) -> Tuple[str, float]:
    """Determine severity level and context score."""
    allowlist = allowlist or AllowlistConfig()
    content_cache = content_cache or {}
    path = finding.path

    if is_allowed_stub(path, finding, allowlist, content_cache):
        return "allowed_stub", 0.0

    base_severity = "minor"
    if finding.kind in ("stub_function", "stub_class"):
        for critical_path in ("core/", "engine/", "error/"):
            if path.startswith(critical_path):
                base_severity = "critical"
                break
        else:
            for major_path in ("aim/", "pm/", "specifications/"):
                if path.startswith(major_path):
                    base_severity = "major"
                    break
    elif finding.kind in ("missing_reference",):
        base_severity = "critical"
    elif finding.kind in ("orphan_module", "trivial_file"):
        base_severity = "minor"
    elif finding.kind in ("empty_dir",):
        base_severity = "info"

    context_score = 1.0
    for path_prefix, multiplier in SEVERITY_MULTIPLIERS.items():
        if path.startswith(path_prefix):
            context_score = multiplier
            break

    return base_severity, context_score


def apply_severity(
    findings: List[Finding],
    root: Path,
    allowlist: AllowlistConfig,
    content_cache: Dict[str, str],
) -> None:
    """Mutate findings with severity/context."""
    for finding in findings:
        severity, score = calculate_severity(finding, root, allowlist, content_cache)
        finding.severity = severity
        finding.context_score = score


# --- Reporting ---


def write_jsonl(records: Iterable[Dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def print_summary(result: ScanResult):
    """Print human-readable summary."""
    print("\n" + "=" * 60)
    print("INCOMPLETE IMPLEMENTATION SCAN RESULTS")
    print("=" * 60)
    print(f"Timestamp: {result.scan_timestamp}")
    print(f"Root: {result.codebase_root}")
    print()

    print("By Kind:")
    for kind, count in sorted(result.stats.items()):
        print(f"  {kind:25s}: {count:3d}")
    print()

    print("By Severity:")
    for severity in ["critical", "major", "minor", "info", "allowed_stub"]:
        count = result.summary_by_severity.get(severity, 0)
        print(f"  {severity:12s}: {count:3d}")
    print()

    print("Top 10 Modules:")
    for module, count in sorted(result.summary_by_module.items(), key=lambda x: -x[1])[
        :10
    ]:
        print(f"  {module:30s}: {count:3d}")
    print()

    critical = [f for f in result.findings if f["severity"] == "critical"]
    if critical:
        print("CRITICAL Findings (top 10):")
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
    print(f"[ok] Results saved to {output_path}")


def save_markdown_summary(result: ScanResult, output_path: Path) -> None:
    lines = [
        "# Incomplete Implementation Scan Summary",
        "",
        f"- Timestamp: `{result.scan_timestamp}`",
        f"- Root: `{result.codebase_root}`",
        "",
        "## Counts by Kind",
    ]
    for kind, count in sorted(result.stats.items()):
        lines.append(f"- {kind}: {count}")
    lines.append("")
    lines.append("## Counts by Severity")
    for severity in ["critical", "major", "minor", "info", "allowed_stub"]:
        lines.append(f"- {severity}: {result.summary_by_severity.get(severity, 0)}")
    if result.findings:
        lines.append("")
        lines.append("## Top Critical Findings")
        critical = [f for f in result.findings if f["severity"] == "critical"][:10]
        for finding in critical:
            lines.append(
                f"- {finding['path']}:{finding.get('line','?')} [{finding['kind']}] {finding.get('reason','')}"
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] Markdown summary saved to {output_path}")


def ci_check(result: ScanResult, max_critical: int = 0, max_major: int = 10) -> bool:
    """Check if scan passes CI thresholds."""
    critical_count = result.summary_by_severity.get("critical", 0)
    major_count = result.summary_by_severity.get("major", 0)

    if critical_count > max_critical:
        print(
            f"[fail] CI CHECK: {critical_count} critical findings (max: {max_critical})"
        )
        return False

    if major_count > max_major:
        print(f"[fail] CI CHECK: {major_count} major findings (max: {max_major})")
        return False

    print(f"[ok] CI CHECK: {critical_count} critical, {major_count} major findings")
    return True


# --- Main orchestration ---


def scan_incomplete_implementations(
    root: Path,
    tiny_file_threshold: int = DEFAULT_TINY_FILE_THRESHOLD,
    allowlist_file: Path = DEFAULT_ALLOWLIST_FILE,
    ignored_dirs: Set[str] = IGNORED_DIRS,
) -> Tuple[ScanResult, Dict[str, str], List[Finding]]:
    """Run the complete scan pipeline."""
    print(f"[run] Scanning {root} for incomplete implementations...")

    allowlist = load_allowlist_config(allowlist_file)
    content_cache: Dict[str, str] = {}

    print("  - Building codebase inventory...")
    file_inventory, dir_inventory = inventory_codebase(root, ignored_dirs)

    empty_findings = detect_empty_structures(
        file_inventory, dir_inventory, tiny_file_threshold
    )
    stub_findings: List[Finding] = []

    for item in file_inventory:
        if item["kind"] != "file":
            continue
        file_path = Path(item["path"])
        absolute = root / file_path
        try:
            content = absolute.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        content_cache[item["path"]] = content

        if item["extension"] == ".py":
            stub_findings.extend(detect_python_stubs(file_path, content))
            stub_findings.extend(detect_pattern_stubs(content, file_path))
        elif item["extension"] in {".js", ".ts", ".tsx", ".jsx"}:
            stub_findings.extend(detect_js_ts_stubs(file_path, content))
            stub_findings.extend(detect_pattern_stubs(content, file_path))

    module_index = build_module_index(file_inventory)
    missing_reference_findings = detect_missing_references(
        file_inventory, root, module_index, content_cache
    )
    dependency_graph = build_dependency_graph(
        file_inventory, root, module_index, content_cache
    )
    orphan_findings = detect_orphans(
        dependency_graph,
        module_index,
        content_cache,
        entrypoint_hints=("__main__.py", "_cli.py", "cli.py"),
    )

    all_findings: List[Finding] = []
    all_findings.extend(empty_findings)
    all_findings.extend(stub_findings)
    all_findings.extend(missing_reference_findings)
    all_findings.extend(orphan_findings)

    apply_severity(all_findings, root, allowlist, content_cache)

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

    result = ScanResult(
        scan_timestamp=datetime.utcnow().isoformat() + "Z",
        codebase_root=str(root),
        stats=dict(stats),
        findings=[asdict(f) for f in all_findings],
        summary_by_severity=dict(summary_by_severity),
        summary_by_module=dict(summary_by_module),
        dependency_graph=dependency_graph,
    )

    return result, content_cache, all_findings


def main():
    parser = argparse.ArgumentParser(description="Scan for incomplete implementations")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Codebase root")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".state/incomplete_scan_summary.json"),
        help="Output summary JSON path",
    )
    parser.add_argument(
        "--findings-output",
        type=Path,
        default=Path(".state/final_findings.jsonl"),
        help="Output JSONL path for detailed findings",
    )
    parser.add_argument(
        "--file-inventory-output",
        type=Path,
        default=Path(".state/file_inventory.jsonl"),
        help="Optional JSONL output for file inventory",
    )
    parser.add_argument(
        "--dir-inventory-output",
        type=Path,
        default=Path(".state/dir_inventory.jsonl"),
        help="Optional JSONL output for dir inventory",
    )
    parser.add_argument(
        "--stub-output",
        type=Path,
        default=Path(".state/stub_candidates.jsonl"),
        help="Optional JSONL output for stub candidates",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=Path(".state/incomplete_scan_summary.md"),
        help="Optional Markdown summary output path",
    )
    parser.add_argument(
        "--tiny-threshold",
        type=int,
        default=DEFAULT_TINY_FILE_THRESHOLD,
        help="Line threshold for tiny files",
    )
    parser.add_argument(
        "--allowlist-file",
        type=Path,
        default=DEFAULT_ALLOWLIST_FILE,
        help="Allowlist YAML file",
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

    result, _content_cache, findings = scan_incomplete_implementations(
        args.root,
        tiny_file_threshold=args.tiny_threshold,
        allowlist_file=args.allowlist_file,
    )

    print_summary(result)
    save_results(result, args.output)
    write_jsonl([asdict(f) for f in findings], args.findings_output)

    file_inventory, dir_inventory = inventory_codebase(args.root, IGNORED_DIRS)
    write_jsonl(file_inventory, args.file_inventory_output)
    write_jsonl(dir_inventory, args.dir_inventory_output)
    write_jsonl(
        [
            asdict(f)
            for f in findings
            if f.kind in ("stub_function", "stub_class", "todo_marker")
        ],
        args.stub_output,
    )

    if args.summary_md:
        save_markdown_summary(result, args.summary_md)

    if args.ci_check:
        success = ci_check(result, args.max_critical, args.max_major)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
