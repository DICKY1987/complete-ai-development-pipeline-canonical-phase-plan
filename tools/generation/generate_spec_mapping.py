#!/usr/bin/env python3
"""
Generate intelligent spec-to-code mappings from IDX tags.

Scans specification documents for [IDX-...] tags and creates intelligent
mappings to code modules, functions, phases, and versions using semantic rules.

Outputs a formatted Markdown table to docs/spec/spec_index_map.md.

Usage:
    python scripts/generate_spec_mapping.py [--docs-dir docs] [--output docs/spec/spec_index_map.md]
"""
# DOC_ID: DOC-PAT-GENERATION-GENERATE-SPEC-MAPPING-623

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Dict

# Add repo root for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.spec_index import create_mapping, generate_mapping_table, SpecMapping


# Inline scanner functions to avoid import issues
IDX_PATTERN = re.compile(r"\[IDX-[A-Z0-9\-]+\]")


@dataclass
class IndexEntry:
    idx: str
    file: str
    line: int
    description: str


def detect_repo_root(start: Path) -> Path:
    """Ascend from start to find .git directory."""
    current = start.resolve()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve()


def iter_spec_files(docs_dir: Path) -> Iterable[Path]:
    """Iterate over .md and .txt files in docs_dir."""
    for ext in (".md", ".txt"):
        yield from docs_dir.rglob(f"*{ext}")


def scan_file(path: Path, repo_root: Path) -> List[IndexEntry]:
    """Scan a file for IDX tags."""
    entries: List[IndexEntry] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return entries

    last_heading = None
    for i, line in enumerate(text, start=1):
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
    """Scan docs directory for IDX tags."""
    results: List[IndexEntry] = []
    if not docs_dir.exists():
        return []
    for path in iter_spec_files(docs_dir):
        results.extend(scan_file(path, repo_root))
    return [asdict(e) for e in results]


def generate_mapping_document(mappings: list[SpecMapping]) -> str:
    """
    Generate complete Markdown document with spec mappings.

    Args:
        mappings: List of SpecMapping objects

    Returns:
        Full Markdown document content
    """
    doc = "# Spec Index Mapping\n\n"
    doc += "**AI Development Pipeline - Specification to Code Mapping**\n\n"
    doc += "This document maps specification IDX tags to their target implementation details.\n\n"

    doc += "## Semantic Mapping Rules\n\n"
    doc += "The mapping logic uses the following semantic rules:\n\n"

    doc += "### Module Assignment\n"
    doc += "- `IDX-DB-*` → `src/pipeline/db.py` (database operations)\n"
    doc += "- `IDX-PROMPT-*` → `src/pipeline/prompts.py` (AI prompts)\n"
    doc += "- `IDX-TOOL-*` → `src/pipeline/tools.py` (external tool adapters)\n"
    doc += "- `IDX-WORKTREE-*` → `src/pipeline/worktree.py` (git worktree management)\n"
    doc += "- `IDX-STATE-*` → `src/pipeline/db.py` (state machine)\n"
    doc += "- `IDX-SCHEMA-*` → `schema/schema.sql` (database schema)\n"
    doc += "- `IDX-CB-*` → `src/pipeline/circuit_breakers.py` (circuit breakers)\n"
    doc += "- `IDX-RECOVERY-*` → `src/pipeline/recovery.py` (crash recovery)\n\n"

    doc += "### Phase Assignment\n"
    doc += "- **PH-01**: Spec mapping, index scanning, module stubs\n"
    doc += "- **PH-02**: Database, state machine, CRUD operations\n"
    doc += "- **PH-03**: Tool adapters, profiles, integration\n"
    doc += "- **PH-04**: Orchestration, scheduling, execution\n"
    doc += "- **PH-05**: Circuit breakers, recovery, observability\n"
    doc += "- **PH-06**: Bundles, worktrees, full pipeline\n\n"

    doc += "### Version Assignment\n"
    doc += "- **v1.0**: Core functionality (IDX numbers 01-50)\n"
    doc += "- **v2.0**: Enhanced features (IDX numbers 51-99)\n"
    doc += "- **v3.0**: Advanced features (IDX numbers 100+)\n\n"

    doc += "---\n\n"
    doc += "## IDX Mappings\n\n"

    if not mappings:
        doc += "_No IDX tags found in specification documents._\n\n"
        doc += "**Note:** This mapping document is ready to be populated once specification \n"
        doc += "documents with `[IDX-...]` tags are added to the `docs/` directory.\n\n"
        doc += "**Example IDX Tag Format:**\n"
        doc += "```\n"
        doc += "[IDX-DB-SCHEMA-01] - Database schema definition\n"
        doc += "[IDX-TOOL-AIDER-CONFIG-05] - Aider tool configuration\n"
        doc += "[IDX-PROMPT-TEMPLATE-10] - Prompt template rendering\n"
        doc += "```\n"
    else:
        doc += f"**Total IDX Tags Found:** {len(mappings)}\n\n"
        doc += generate_mapping_table(mappings)

    doc += "\n---\n\n"
    doc += "_Generated by `scripts/generate_spec_mapping.py`_\n"

    return doc


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate intelligent spec-to-code mappings from IDX tags"
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--output",
        default="docs/spec/spec_index_map.md",
        help="Output file path (default: docs/spec/spec_index_map.md)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information",
    )
    args = parser.parse_args(argv)

    # Detect repo root
    repo_root = detect_repo_root(Path.cwd())
    docs_dir = (repo_root / args.docs_dir).resolve()
    output_path = (repo_root / args.output).resolve()

    if args.verbose:
        print(f"Repo root: {repo_root}")
        print(f"Docs dir: {docs_dir}")
        print(f"Output: {output_path}")
        print()

    # Scan for IDX tags
    if args.verbose:
        print("Scanning for IDX tags...")

    raw_entries = scan_docs(docs_dir, repo_root)

    if args.verbose:
        print(f"Found {len(raw_entries)} IDX tags")
        print()

    # Create intelligent mappings
    mappings: list[SpecMapping] = []
    for entry in raw_entries:
        mapping = create_mapping(
            idx=entry["idx"],
            description=entry["description"],
            source_file=entry["file"],
            line=entry["line"]
        )
        mappings.append(mapping)

        if args.verbose:
            print(f"  {mapping.idx} → {mapping.module}::{mapping.function_or_class} ({mapping.phase})")

    if args.verbose:
        print()

    # Generate document
    doc = generate_mapping_document(mappings)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    output_path.write_text(doc, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Total mappings: {len(mappings)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
