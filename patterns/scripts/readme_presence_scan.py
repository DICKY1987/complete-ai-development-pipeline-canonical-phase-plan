"""Scan directories for README coverage and group results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Sequence


DEFAULT_README_NAMES: tuple[str, ...] = (
    "README",
    "README.md",
    "README.txt",
    "readme",
    "readme.md",
    "readme.txt",
)
DEFAULT_SKIP_DIRS: tuple[str, ...] = (
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
)


def has_readme(dir_path: Path, names: Iterable[str]) -> bool:
    """Return True if the directory contains a README using any allowed name."""
# DOC_ID: DOC-SCRIPT-SCRIPTS-README-PRESENCE-SCAN-329
    names_lower = {name.lower() for name in names}
    try:
        for child in dir_path.iterdir():
            if child.is_file() and child.name.lower() in names_lower:
                return True
    except PermissionError:
        return False
    return False


def collect_directories(
    root: Path,
    *,
    max_depth: int | None,
    include_hidden: bool,
    skip_dirs: Sequence[str],
) -> List[Path]:
    """Return directories under root, honoring depth and skip rules."""
    collected: List[Path] = []
    stack: list[tuple[Path, int]] = [(root, 0)]
    skip_set = set(skip_dirs)

    while stack:
        current, depth = stack.pop()
        if depth and not include_hidden and current.name.startswith("."):
            continue
        if depth and current.name in skip_set:
            continue
        if depth:
            collected.append(current)
        if max_depth is not None and depth >= max_depth:
            continue

        try:
            children = sorted(current.iterdir(), key=lambda p: p.name.lower())
        except PermissionError:
            continue

        for child in children:
            if not child.is_dir() or child.is_symlink():
                continue
            stack.append((child, depth + 1))

    return collected


def build_report(
    root: Path,
    *,
    names: Sequence[str],
    skip_dirs: Sequence[str],
    max_depth: int | None,
    include_hidden: bool,
) -> dict[str, list[str]]:
    """Scan and return grouped README coverage results."""
    directories = collect_directories(
        root,
        max_depth=max_depth,
        include_hidden=include_hidden,
        skip_dirs=skip_dirs,
    )
    with_readme: list[Path] = []
    without_readme: list[Path] = []

    for dir_path in directories:
        target = with_readme if has_readme(dir_path, names) else without_readme
        target.append(dir_path)

    return {
        "root": str(root),
        "readme_names": list(names),
        "with_readme": [str(p.relative_to(root)) for p in sorted(with_readme)],
        "without_readme": [str(p.relative_to(root)) for p in sorted(without_readme)],
    }


def print_text_report(report: dict[str, list[str]]) -> None:
    """Pretty-print grouped coverage."""
    with_readme = report["with_readme"]
    without_readme = report["without_readme"]

    print(f"Directories with README ({len(with_readme)}):")
    for path in with_readme:
        print(f"- {path}")
    print()
    print(f"Directories without README ({len(without_readme)}):")
    for path in without_readme:
        print(f"- {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report directories that contain or lack a README file.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    parser.add_argument(
        "--names",
        nargs="+",
        default=list(DEFAULT_README_NAMES),
        help="Accepted README filenames (case-insensitive).",
    )
    parser.add_argument(
        "--skip-dirs",
        nargs="*",
        default=list(DEFAULT_SKIP_DIRS),
        help="Directory names to skip entirely.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum directory depth to scan (0 = root only).",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden directories (names starting with '.').",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit JSON instead of text.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    report = build_report(
        root,
        names=args.names,
        skip_dirs=args.skip_dirs,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
    )

    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)


if __name__ == "__main__":
    main()
