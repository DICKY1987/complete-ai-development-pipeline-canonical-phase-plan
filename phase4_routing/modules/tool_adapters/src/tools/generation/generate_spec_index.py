#!/usr/bin/env python3
"""Generate a simple index of [IDX-...] tags from docs.

Scans a documentation directory recursively for Markdown and text files,
extracts spec index tags of the form [IDX-...], and prints a structured
summary in text or JSON format.

Usage:
  python scripts/generate_spec_index.py --docs-dir docs --format json
"""
# DOC_ID: DOC-PAT-GENERATION-GENERATE-SPEC-INDEX-622

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Dict


IDX_PATTERN = re.compile(r"\[IDX-[A-Z0-9\-]+\]")


@dataclass
class IndexEntry:
    idx: str
    file: str
    line: int
    description: str


def detect_repo_root(start: Path) -> Path:
    """Ascend from start to the directory containing a .git folder, if present.

    Falls back to start if not found to avoid failures.
    """
    current = start.resolve()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve()


def iter_spec_files(docs_dir: Path) -> Iterable[Path]:
    for ext in (".md", ".txt"):
        yield from docs_dir.rglob(f"*{ext}")


def scan_file(path: Path, repo_root: Path) -> List[IndexEntry]:
    entries: List[IndexEntry] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return entries

    last_heading = None
    for i, line in enumerate(text, start=1):
        # Track nearest preceding heading for context
        if line.lstrip().startswith("#"):
            last_heading = line.strip()

        for m in IDX_PATTERN.finditer(line):
            tag = m.group(0)
            description = line.strip() or (last_heading or "")
            rel = path.resolve().relative_to(repo_root)
            entries.append(
                IndexEntry(
                    idx=tag.strip("[]"),
                    file=str(rel).replace("\\", "/"),
                    line=i,
                    description=description,
                )
            )
    return entries


def scan_docs(docs_dir: Path, repo_root: Path) -> List[Dict[str, object]]:
    results: List[IndexEntry] = []
    if not docs_dir.exists():
        return []
    for path in iter_spec_files(docs_dir):
        results.extend(scan_file(path, repo_root))
    return [asdict(e) for e in results]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan docs for [IDX-...] tags")
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args(argv)

    start = Path.cwd()
    repo_root = detect_repo_root(start)
    docs_dir = (repo_root / args.docs_dir).resolve()

    entries = scan_docs(docs_dir, repo_root)

    if args.format == "json":
        print(json.dumps(entries, indent=2))
    else:
        for e in entries:
            print(
                f"{e['idx']}: {e['file']}:{e['line']} - "
                f"{e['description'][:200]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

