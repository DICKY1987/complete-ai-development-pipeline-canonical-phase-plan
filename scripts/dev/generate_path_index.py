"""Generate a canonical path registry covering every file in the repo."""
DOC_ID: DOC-SCRIPT-DEV-GENERATE-PATH-INDEX-753

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Dict, Set, Tuple

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "config" / "path_index.yaml"
EXCLUDE_DIRS: Set[str] = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".state",
    ".execution",
    ".claude",
    ".ledger",
    ".aider",
    ".aider.tags.cache.v4",
}
EXCLUDE_EXTS: Set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".db-journal",
    ".db-wal",
    ".db-shm",
    ".tmp",
    ".log",
    ".swp",
    ".swo",
}
EXCLUDE_FILES: Set[str] = {
    ".coverage",
    "coverage.json",
    "test_results_full.txt",
}

# Curated high-value entries to ensure they remain in the registry even if excluded or moved.
# Keys are dot-delimited namespace.key strings.
MANUAL_ENTRIES: Dict[str, Dict[str, str]] = {
    "docs.phase_dev_root": {
        "path": "meta/PHASE_DEV_DOCS",
        "section": "docs",
        "description": "Canonical root for phase development documents.",
    },
    "docs.plans_root": {
        "path": "plans",
        "section": "docs",
        "description": "Canonical root for plan documents.",
    },
    "docs.coord_mech_root": {
        "path": "meta/Coordination Mechanisms",
        "section": "docs",
        "description": "Coordination mechanisms docs root.",
    },
    "docs.aider_instructions_ph07": {
        "path": "meta/PHASE_DEV_DOCS/AIDER_INSTRUCTIONS_PH07.txt",
        "section": "docs",
        "description": "Aider instructions for PH07 (historical reference).",
    },
    "governance.agents_rules": {
        "path": "AGENTS.md",
        "section": "governance",
        "description": "Global repository rules for AI agents.",
    },
    "docs.readme": {
        "path": "README.md",
        "section": "docs",
        "description": "Repository overview README.",
    },
    "docs.uet_abstraction_guidelines": {
        "path": "docs/UET_ABSTRACTION_GUIDELINES.md",
        "section": "docs",
        "description": "Abstraction guidance for UET stack.",
    },
    "docs.path_abstraction_layer": {
        "path": "docs/PATH ABSTRACTION & INDIRECTION LAYER.md",
        "section": "docs",
        "description": "Path indirection layer specification.",
    },
    "docs.ssot_policy": {
        "path": "SSOT_POLICY_MISSION_COMPLETE.md",
        "section": "docs",
        "description": "Glossary SSOT policy completion summary.",
    },
    "docs.phase_directory_map": {
        "path": "PHASE_DIRECTORY_MAP.md",
        "section": "docs",
        "description": "Mapping of phases to directories.",
    },
    "docs.folder_structure_phase_mapping": {
        "path": "Folder Structure to Phase Mapping.md",
        "section": "docs",
        "description": "Folder structure mapped to phases reference.",
    },
    "docs.master_plan": {
        "path": "master_plan.md",
        "section": "docs",
        "description": "Master plan overview document.",
    },
    "docs.safe_merge_phase_plan": {
        "path": "SAFE_MERGE_PHASE_PLAN.md",
        "section": "docs",
        "description": "Safe merge phase plan guidance.",
    },
    "docs.architecture_main": {
        "path": "docs/ARCHITECTURE.md",
        "section": "docs",
        "description": "Primary architecture overview document.",
    },
    "docs.directory_guide": {
        "path": "DIRECTORY_GUIDE.md",
        "section": "docs",
        "description": "Guide to repository directory structure.",
    },
    "docs.documentation_index": {
        "path": "docs/DOCUMENTATION_INDEX.md",
        "section": "docs",
        "description": "Documentation index entry point.",
    },
    "docs.phase_plan": {
        "path": "docs/PHASE_PLAN.md",
        "section": "docs",
        "description": "Phase plan overview document.",
    },
    "docs.check_workstream_status_ps1": {
        "path": "scripts/check_workstream_status.ps1",
        "section": "scripts",
        "description": "Workstream status checker (PowerShell).",
    },
    "docs.check_workstream_status_sh": {
        "path": "scripts/check_workstream_status.sh",
        "section": "scripts",
        "description": "Workstream status checker (shell).",
    },
    "core.db": {
        "path": "core/state/db.py",
        "section": "core",
        "description": "Core state database module.",
    },
}


def sanitize(token: str) -> str:
    """Convert a path token into a safe identifier fragment."""
DOC_ID: DOC-SCRIPT-DEV-GENERATE-PATH-INDEX-738
DOC_ID: DOC-SCRIPT-DEV-GENERATE-PATH-INDEX-734
DOC_ID: DOC-SCRIPT-DEV-GENERATE-PATH-INDEX-733
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", token).strip("_")
    if not cleaned:
        cleaned = "item"
    if cleaned[0].isdigit():
        cleaned = f"p_{cleaned}"
    return cleaned


def iter_files(include_hidden: bool) -> Tuple[Path, ...]:
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # filter directories
        dirnames[:] = [
            d
            for d in dirnames
            if d not in EXCLUDE_DIRS and (include_hidden or not d.startswith("."))
        ]
        for fname in filenames:
            if fname in EXCLUDE_FILES:
                continue
            if not include_hidden and fname.startswith("."):
                continue
            ext = Path(fname).suffix.lower()
            if ext in EXCLUDE_EXTS:
                continue
            files.append(Path(dirpath) / fname)
    return tuple(sorted(files))


def path_to_entry(path: Path) -> Tuple[str, str, Dict[str, str]]:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if len(parts) == 1:
        namespace = "root"
        remainder = (parts[0],)
    else:
        namespace = parts[0]
        remainder = parts[1:]

    ns_key = sanitize(namespace)
    name_fragments = [sanitize(p) for p in remainder]
    name = "__".join(name_fragments) if name_fragments else "item"

    meta = {
        "path": rel.as_posix(),
        "section": ns_key,
    }
    return ns_key, name, meta


def build_registry(include_hidden: bool) -> Dict[str, Dict[str, Dict[str, str]]]:
    registry: Dict[str, Dict[str, Dict[str, str]]] = {}
    collisions: Dict[Tuple[str, str], int] = {}

    for path in iter_files(include_hidden):
        ns, name, meta = path_to_entry(path)
        bucket = registry.setdefault(ns, {})

        key_base = name
        key = key_base
        while key in bucket:
            collisions[(ns, key_base)] = collisions.get((ns, key_base), 1) + 1
            key = f"{key_base}_{collisions[(ns, key_base)]}"

        bucket[key] = meta

    return registry


def merge_manual_entries(registry: Dict[str, Dict[str, Dict[str, str]]]) -> None:
    for full_key, meta in MANUAL_ENTRIES.items():
        if "." not in full_key:
            continue
        ns, name = full_key.split(".", 1)
        bucket = registry.setdefault(ns, {})
        bucket[name] = dict(meta)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate config/path_index.yaml for the repo"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output path (default: config/path_index.yaml)",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include files in hidden directories and dotfiles (except .git which is always skipped)",
    )
    args = parser.parse_args()

    registry = build_registry(include_hidden=args.include_hidden)
    merge_manual_entries(registry)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    data = {"paths": registry}
    args.out.write_text(
        yaml.safe_dump(
            data, sort_keys=True, allow_unicode=False, default_flow_style=False
        ),
        encoding="utf-8",
    )
    print(
        f"Wrote registry with {sum(len(v) for v in registry.values())} entries to {args.out}"
    )


if __name__ == "__main__":
    main()
