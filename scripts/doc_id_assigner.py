#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-ASSIGNER-204
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-ASSIGNER-141
# -*- coding: utf-8 -*-
"""
Doc ID Auto-Assigner

PURPOSE:
    Use docs_inventory.jsonl + DOC_ID_REGISTRY.yaml to assign doc_ids to all
    eligible files that are currently missing them, and inject the IDs into
    the files in-place.

PATTERN: PAT-DOC-ID-AUTOASSIGN-002

USAGE:
    python scripts/doc_id_assigner.py auto-assign --dry-run
    python scripts/doc_id_assigner.py auto-assign --limit 50 --dry-run
    python scripts/doc_id_assigner.py auto-assign
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Assuming this file lives in scripts/ at repo root
REPO_ROOT = Path(__file__).parent.parent
INVENTORY_PATH = REPO_ROOT / "docs_inventory.jsonl"


# --- Registry module loader -------------------------------------------------


def _load_registry_module():
    """
    Load doc_id_registry_cli.py as a module so we can reuse DocIDRegistry
    without spawning a subprocess for every file.

    This expects:
        repo_root/doc_id/tools/doc_id_registry_cli.py
    """
    registry_path = REPO_ROOT / "doc_id" / "tools" / "doc_id_registry_cli.py"
    if not registry_path.exists():
        print(f"[ERROR] Could not find registry CLI at {registry_path}", file=sys.stderr)
        sys.exit(1)

    import importlib.util

    spec = importlib.util.spec_from_file_location("doc_id_registry_cli", registry_path)
    if spec is None or spec.loader is None:
        print("[ERROR] Failed to load doc_id_registry_cli module", file=sys.stderr)
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_registry_module = _load_registry_module()
DocIDRegistry = _registry_module.DocIDRegistry  # type: ignore[attr-defined]


# --- Inventory model --------------------------------------------------------


@dataclass
class InventoryEntry:
    path: str
    # DOC_ID: Optional[str]
    status: str
    file_type: str
    last_modified: str = ""
    scanned_at: str = ""

    @classmethod
    def from_dict(cls, d: Dict) -> "InventoryEntry":
        return cls(
            path=d["path"],
            doc_id=d.get("doc_id"),
            status=d.get("status", "missing"),
            file_type=d.get("file_type", "unknown"),
            last_modified=d.get("last_modified", ""),
            scanned_at=d.get("scanned_at", ""),
        )


def load_inventory(path: Path = INVENTORY_PATH) -> List[InventoryEntry]:
    """Load docs_inventory.jsonl into memory."""
    if not path.exists():
        print(f"[ERROR] Inventory file not found: {path}", file=sys.stderr)
        print("        Run: python scripts/doc_id_scanner.py scan", file=sys.stderr)
        sys.exit(1)

    entries: List[InventoryEntry] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(InventoryEntry.from_dict(data))

    return entries


# --- Inference helpers ------------------------------------------------------


def infer_category(path: str, available_categories: List[str]) -> str:
    """
    Infer registry category from file path.

    Enhanced with comprehensive directory-to-category mappings for 100% coverage.
    Priority order:
    1. Exact directory path matches (most specific)
    2. Partial path matches
    3. File extension fallbacks
    4. Default fallback (legacy/patterns)
    """
    normalized = path.replace("\\", "/")
    if not normalized.startswith("/"):
        normalized = "/" + normalized

    # Priority 1: Exact directory mappings (most specific first)
    exact_mappings: List[Tuple[str, str]] = [
        # Core system components
        ("core", "/core/"),
        ("error", "/error/"),
        ("aim", "/aim/"),
        ("pm", "/pm/"),
        ("engine", "/engine/"),
        ("infra", "/infra/"),

        # Patterns and UET
        ("patterns", "/UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/"),
        ("patterns", "/patterns/"),
        ("guide", "/UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/guides/"),
        ("spec", "/UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/"),

        # Documentation
        ("guide", "/docs/"),
        ("guide", "/documentation/"),
        ("guide", "/developer/"),
        ("arch", "/adr/"),

        # Modules and components
        ("core", "/modules/"),
        ("spec", "/specifications/"),
        ("spec", "/schema/"),
        ("spec", "/openspec/"),

        # Testing
        ("test", "/tests/"),

        # Scripts and tools
        ("script", "/scripts/"),
        ("script", "/tools/"),

        # Configuration
        ("config", "/config/"),
        ("config", "/.github/"),

        # Special directories
        ("legacy", "/archive/"),
        ("legacy", "/legacy/"),
        ("task", "/ToDo_Task/"),
        ("task", "/workstreams/"),
        ("task", "/workstreams_uet/"),

        # Doc_id system
        ("guide", "/doc_id/"),

        # Build and package artifacts
        ("infra", "/build/"),
        ("infra", "/__pycache__/"),
        ("infra", "/.venv/"),
        ("infra", "/node_modules/"),
    ]

    # Priority 2: Partial path matches (for nested structures)
    partial_mappings: List[Tuple[str, str]] = [
        ("test", "/test"),
        ("spec", "/spec"),
        ("guide", "/guide"),
        ("patterns", "/pattern"),
        ("config", "/config"),
    ]

    # Priority 3: File extension mappings
    extension_mappings: List[Tuple[str, str]] = [
        ("script", ".ps1"),
        ("script", ".sh"),
        ("script", ".bat"),
        ("config", ".yaml"),
        ("config", ".yml"),
        ("config", ".toml"),
        ("config", ".ini"),
        ("config", ".json"),
        ("guide", ".md"),
        ("guide", ".txt"),
        ("core", ".py"),
    ]

    # Try exact directory matches first
    for candidate, marker in exact_mappings:
        if marker in normalized and candidate in available_categories:
            return candidate

    # Try partial path matches
    for candidate, marker in partial_mappings:
        if marker in normalized and candidate in available_categories:
            return candidate

    # Try extension-based mapping
    for candidate, ext in extension_mappings:
        if normalized.endswith(ext) and candidate in available_categories:
            return candidate

    # Fallback priority: patterns > guide > legacy > first available
    for fallback in ("patterns", "guide", "legacy"):
        if fallback in available_categories:
            return fallback

    # Absolute fallback: first category defined in registry
    if available_categories:
        return available_categories[0]

    print("[ERROR] No categories available in DOC_ID_REGISTRY.yaml", file=sys.stderr)
    sys.exit(1)


def infer_name_and_title(path: str, file_type: str) -> Tuple[str, str]:
    """
    Infer logical 'name' and human-readable 'title' for the registry.

    name: short machine-friendly identifier (used in doc_id)
    title: human-readable description shown in registry
    """
    rel = Path(path)
    stem = rel.stem
    parent = rel.parent.name

    # Special case: __*__ files (dunder files)
    if stem.startswith("__") and stem.endswith("__"):
        stem_clean = stem[2:-2].upper()  # Remove __ from both ends
        if not stem_clean:
            stem_clean = "DUNDER"
    else:
        # Sanitize stem: remove special chars, limit length
        stem_clean = re.sub(r'[^a-zA-Z0-9_-]', '-', stem)
        stem_clean = re.sub(r'-+', '-', stem_clean).strip('-')

    # Limit to reasonable length (max 50 chars for stem)
    if len(stem_clean) > 50:
        stem_clean = stem_clean[:50].rsplit('-', 1)[0]  # Cut at word boundary

    if file_type == "py":
        if stem.startswith("test_"):
            name = f"{parent}-{stem_clean}".replace("_", "-")
            title = f"Tests for {parent}.{stem.replace('test_', '')}"
        else:
            name = f"{parent}-{stem_clean}".replace("_", "-")
            title = f"{parent} module: {stem}"
    elif file_type in ("ps1", "sh"):
        name = stem_clean.replace("_", "-")
        title = f"Script: {stem}"
    elif file_type in ("yaml", "yml"):
        name = stem_clean.replace("_", "-")
        title = f"Config: {stem}"
    elif file_type == "json":
        name = stem_clean.replace("_", "-")
        title = f"JSON spec: {stem}"
    elif file_type == "md":
        name = stem_clean.replace("_", "-")
        # Clean up title too
        title = stem.replace("-", " ").replace("_", " ").title()
        if len(title) > 80:
            title = title[:77] + "..."
    else:
        name = stem_clean.replace("_", "-")
        title = stem

    # Final name cleanup: ensure uppercase, no underscores
    name = name.replace("_", "-").upper()
    # Remove leading/trailing dashes and collapse multiple dashes
    name = re.sub(r'-+', '-', name).strip('-')
    # If name is empty or invalid, use fallback
    if not name or not re.match(r'^[A-Z0-9]', name):
        name = f"FILE-{parent.upper()}-{stem_clean[:20].upper()}"
        name = re.sub(r'-+', '-', name).strip('-')
    # Limit total name length to avoid overly long IDs
    if len(name) > 40:
        name = name[:40].rsplit('-', 1)[0] if '-' in name[:40] else name[:40]
    # Remove any trailing dashes again
    name = name.rstrip('-')
    # Final validation: must not be empty and not end with dash
    if not name or name.endswith('-'):
        name = "UNNAMED"

    return name, title


# --- Injection helpers ------------------------------------------------------


def inject_doc_id_into_content(content: str, file_type: str, doc_id: str) -> str:
    """
    Inject doc_id into file content based on type.

    Simple and idempotent: if the doc_id is already present, content is
    returned unchanged.
    """
    if doc_id in content:
        return content

    # Python: module docstring or header comment
    if file_type == "py":
        lines = content.splitlines()
        new_lines: List[str] = []

        idx = 0
        # Preserve shebang
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            idx = 1

        inserted = False

        # Look for a top-level docstring
        if idx < len(lines) and (
            lines[idx].lstrip().startswith('"""') or lines[idx].lstrip().startswith("'''")
        ):
            quote = lines[idx].lstrip()[:3]
            new_lines.append(lines[idx])
            i = idx + 1
            while i < len(lines):
                new_lines.append(lines[i])
                if lines[i].rstrip().endswith(quote):
                    new_lines.append(f"DOC_ID: {doc_id}")
                    inserted = True
                    i += 1
                    break
                i += 1
            new_lines.extend(lines[i:])
        else:
            # No obvious docstring – insert comment near top
            new_lines.append(f"# DOC_LINK: {doc_id}")
            new_lines.extend(lines[idx:])
            inserted = True
            if idx > 0:
                # We already added shebang above if it existed
                pass

        if not inserted:
            new_lines.append(f"# DOC_LINK: {doc_id}")

        result = "\n".join(new_lines)
        if content.endswith("\n"):
            result += "\n"
        return result

    # Markdown: YAML frontmatter
    if file_type == "md":
        if content.startswith("---\n"):
            lines = content.splitlines()
            end_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    end_idx = i
                    break
            if end_idx is not None:
                fm = lines[1:end_idx]
                if any(l.strip().startswith("doc_id:") for l in fm):
                    return content
                new_fm = ["doc_id: " + doc_id] + fm
                new_lines = ["---", *new_fm, "---", *lines[end_idx + 1 :]]
                result = "\n".join(new_lines)
                if content.endswith("\n"):
                    result += "\n"
                return result
        # No frontmatter
        fm = f"---\ndoc_id: {doc_id}\n---\n\n"
        return fm + content

    # YAML
    if file_type in ("yaml", "yml"):
        lines = content.splitlines()
        if any(l.strip().startswith("doc_id:") for l in lines[:20]):
            return content
        result = "doc_id: " + doc_id + "\n" + content
        return result

    # JSON
    if file_type == "json":
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                if "doc_id" in data:
                    return content
                data["doc_id"] = doc_id
                return json.dumps(data, indent=2) + "\n"
        except json.JSONDecodeError:
            # Fall back to a header comment
            pass
        return f"/* DOC_ID: {doc_id} */\n" + content

    # PowerShell / Shell
    if file_type in ("ps1", "sh"):
        lines = content.splitlines()
        new_lines: List[str] = []
        idx = 0
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            idx = 1
        new_lines.append(f"# DOC_LINK: {doc_id}")
        new_lines.extend(lines[idx:])
        result = "\n".join(new_lines)
        if content.endswith("\n"):
            result += "\n"
        return result

    # TXT: treat like light markdown
    if file_type == "txt":
        if content.startswith("---\n"):
            lines = content.splitlines()
            end_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    end_idx = i
                    break
            if end_idx is not None:
                fm = lines[1:end_idx]
                if any(l.strip().startswith("doc_id:") for l in fm):
                    return content
                new_fm = ["doc_id: " + doc_id] + fm
                new_lines = ["---", *new_fm, "---", *lines[end_idx + 1 :]]
                result = "\n".join(new_lines)
                if content.endswith("\n"):
                    result += "\n"
                return result
        fm = f"---\ndoc_id: {doc_id}\n---\n\n"
        return fm + content

    # Unknown / other: leave unchanged
    return content


# --- Assignment core --------------------------------------------------------


@dataclass
class AssignmentResult:
    path: str
    # DOC_ID: str
    category: str
    name: str
    skipped: bool
    reason: Optional[str] = None


def auto_assign(
    dry_run: bool = True,
    limit: Optional[int] = None,
    include_types: Optional[List[str]] = None,
) -> Dict:
    """
    Assign doc_ids to all inventory entries marked as 'missing'.

    Returns a dict with summary + per-file assignment details.
    """
    inventory = load_inventory()
    registry = DocIDRegistry()
    available_categories = list(registry.data["categories"].keys())

    missing = [e for e in inventory if e.status == "missing"]
    total_missing = len(missing)

    if include_types:
        include_set = set(include_types)
        missing = [e for e in missing if e.file_type in include_set]

    if limit is not None:
        missing = missing[:limit]

    assignments: List[AssignmentResult] = []
    skipped: List[AssignmentResult] = []

    for idx, entry in enumerate(missing, start=1):
        rel_path = entry.path
        full_path = REPO_ROOT / rel_path

        if not full_path.exists():
            skipped.append(
                AssignmentResult(
                    path=rel_path,
                    doc_id="",
                    category="",
                    name="",
                    skipped=True,
                    reason="File does not exist",
                )
            )
            continue

        category = infer_category(rel_path, available_categories)
        name, title = infer_name_and_title(rel_path, entry.file_type)

        if dry_run:
            # We just preview what *would* happen
            preview_id = f"DOC-{category.upper()}-{name.upper().replace('_', '-')}-XXX"
            assignments.append(
                AssignmentResult(
                    path=rel_path,
                    doc_id=preview_id,
                    category=category,
                    name=name,
                    skipped=False,
                )
            )
        else:
            artifacts = [{"type": "source", "path": rel_path}]
            new_doc_id = registry.mint_doc_id(
                category=category,
                name=name,
                title=title,
                artifacts=artifacts,
                tags=[entry.file_type],
            )

            content = full_path.read_text(encoding="utf-8", errors="ignore")
            new_content = inject_doc_id_into_content(content, entry.file_type, new_doc_id)
            full_path.write_text(new_content, encoding="utf-8")

            assignments.append(
                AssignmentResult(
                    path=rel_path,
                    doc_id=new_doc_id,
                    category=category,
                    name=name,
                    skipped=False,
                )
            )

        if idx % 50 == 0:
            print(f"[INFO] Processed {idx}/{len(missing)} files...")

    summary = {
        "total_missing_in_inventory": total_missing,
        "processed": len(missing),
        "assigned": len([a for a in assignments if not a.skipped]),
        "skipped": len(skipped),
        "dry_run": dry_run,
        "timestamp": datetime.now().isoformat(),
    }

    return {
        "summary": summary,
        "assignments": [asdict(a) for a in assignments],
        "skipped": [asdict(s) for s in skipped],
    }


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auto-assign doc_ids to files based on docs_inventory.jsonl"
    )
    subparsers = parser.add_subparsers(dest="command")

    assign_parser = subparsers.add_parser(
        "auto-assign",
        help="Assign doc_ids to files that are missing them",
    )
    assign_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview assignments without modifying files or registry",
    )
    assign_parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of files processed (for testing)",
    )
    assign_parser.add_argument(
        "--types",
        nargs="+",
        help="Limit to specific file types (e.g. py md yaml json ps1 sh txt)",
    )
    assign_parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON file to write a detailed report",
    )

    args = parser.parse_args()

    if args.command == "auto-assign":
        result = auto_assign(
            dry_run=args.dry_run,
            limit=args.limit,
            include_types=args.types,
        )
        summary = result["summary"]

        print("\n=== DOC_ID AUTO-ASSIGN REPORT ===")
        print(f"Total missing in inventory: {summary['total_missing_in_inventory']}")
        print(f"Processed in this run:      {summary['processed']}")
        print(f"Assigned:                   {summary['assigned']}")
        print(f"Skipped:                    {summary['skipped']}")
        print(f"Dry run:                    {summary['dry_run']}")
        print(f"Timestamp:                  {summary['timestamp']}")

        if args.report:
            args.report.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"\n[OK] Detailed report written to {args.report}")

        # Non-zero exit if anything was skipped so you see it in CI if you choose
        return 0 if summary["skipped"] == 0 else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
