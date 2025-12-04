#!/usr/bin/env python3
"""
Documentation Inventory Generator
Implements DOC-ORG-020 through DOC-ORG-024
"""
# DOC_ID: DOC-PAT-TOOLS-DOC-INVENTORY-659
import argparse
import json
import sys
from pathlib import Path
from typing import Iterator


def load_ignore_patterns(repo_root: Path) -> list[str]:
    """Load patterns from .docs_ignore file."""
    ignore_file = repo_root / ".docs_ignore"
    if not ignore_file.exists():
        return []

    patterns = []
    for line in ignore_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def should_ignore(path: Path, repo_root: Path, patterns: list[str]) -> bool:
    """Check if path matches any ignore pattern."""
    rel_path = path.relative_to(repo_root).as_posix()

    for pattern in patterns:
        # Simple glob matching (supports **/ and *)
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            if rel_path.startswith(prefix + "/") or rel_path == prefix:
                return True
        elif "*" in pattern:
            # Basic wildcard matching
            import fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        elif rel_path.startswith(pattern):
            return True

    return False


def find_docs(repo_root: Path, ignore_patterns: list[str]) -> Iterator[Path]:
    """Recursively find all .md and .txt files."""
    for ext in ["*.md", "*.txt"]:
        for path in repo_root.rglob(ext):
            if not should_ignore(path, repo_root, ignore_patterns):
                yield path


def generate_inventory(repo_root: Path, output_path: Path, preview_chars: int = 600) -> int:
    """Generate doc inventory JSONL file."""
    ignore_patterns = load_ignore_patterns(repo_root)
    count = 0

    with output_path.open("w", encoding="utf-8") as f:
        for doc_path in find_docs(repo_root, ignore_patterns):
            try:
                content = doc_path.read_text(encoding="utf-8", errors="ignore")
                preview = content[:preview_chars]

                record = {
                    "path": doc_path.relative_to(repo_root).as_posix(),
                    "name": doc_path.name,
                    "preview": preview
                }
                f.write(json.dumps(record) + "\n")
                count += 1
            except Exception as e:
                print(f"Warning: Could not read {doc_path}: {e}", file=sys.stderr)

    return count


def main():
    parser = argparse.ArgumentParser(description="Generate documentation inventory")
    parser.add_argument("--output", default=".state/docs/doc_inventory.jsonl",
                       help="Output JSONL file path")
    parser.add_argument("--preview-chars", type=int, default=600,
                       help="Number of preview characters (default: 600)")
    parser.add_argument("--config", help="Optional config file (not yet implemented)")

    args = parser.parse_args()

    repo_root = Path.cwd()
    output_path = repo_root / args.output

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Scanning repository: {repo_root}")
    print(f"Output file: {output_path}")

    count = generate_inventory(repo_root, output_path, args.preview_chars)

    print(f"✅ Generated inventory: {count} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
