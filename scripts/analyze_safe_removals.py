#!/usr/bin/env python3
"""
Safe Removal Analyzer

Analyzes which folders can be safely removed by checking import dependencies.

Usage:
    python scripts/analyze_safe_removals.py
"""
DOC_ID: DOC - SCRIPT - SCRIPTS - ANALYZE - SAFE - REMOVALS - 706
DOC_ID: DOC - SCRIPT - SCRIPTS - ANALYZE - SAFE - REMOVALS - 706

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in repository."""
    return list(root.rglob("*.py"))


def extract_imports(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # from X import Y
                match = re.match(r"^from\s+([\w.]+)", line)
                if match:
                    imports.add(match.group(1))
                # import X
                match = re.match(r"^import\s+([\w.]+)", line)
                if match:
                    imports.add(match.group(1))
    except Exception:
        pass
    return imports


def analyze_folder_usage(root: Path, target_folder: str) -> Dict[str, any]:
    """
    Analyze if a folder is safe to remove.

    Returns dict with:
    - imported_by: list of files importing from target
    - file_count: number of files in target
    - is_safe: whether it's safe to remove
    """
    result = {
        "imported_by": [],
        "file_count": 0,
        "is_safe": False,
        "recommendation": "",
    }

    target_path = root / target_folder
    if not target_path.exists():
        result["recommendation"] = f"Folder '{target_folder}' does not exist"
        result["is_safe"] = True
        return result

    # Count files in target
    result["file_count"] = len(list(target_path.rglob("*.py")))

    # Find all Python files outside target
    all_files = find_python_files(root)

    # Check which files import from target
    for file_path in all_files:
        # Skip files in target folder itself
        if str(file_path).startswith(str(target_path)):
            continue

        imports = extract_imports(file_path)
        for imp in imports:
            # Check if import references target folder
            if imp.startswith(target_folder.replace("/", ".").replace("\\", ".")):
                rel_path = str(file_path.relative_to(root))
                result["imported_by"].append(rel_path)
                break

    # Determine if safe to remove
    result["is_safe"] = len(result["imported_by"]) == 0

    if result["is_safe"]:
        result["recommendation"] = f"✅ SAFE TO REMOVE - No imports found"
    elif len(result["imported_by"]) < 10:
        result["recommendation"] = (
            f"⚠️ NEEDS MIGRATION - {len(result['imported_by'])} files to update"
        )
    else:
        result["recommendation"] = (
            f"❌ HEAVILY USED - {len(result['imported_by'])} imports, keep or major refactor"
        )

    return result


def main():
    root = Path(".")

    # Folders to analyze
    candidates = [
        "engine",
        "src",
        "legacy",
        "src/pipeline",
        "MOD_ERROR_PIPELINE",
    ]

    print("=" * 80)
    print("SAFE REMOVAL ANALYSIS")
    print("=" * 80)
    print()

    for folder in candidates:
        print(f"📁 Analyzing: {folder}/")
        print("-" * 80)

        result = analyze_folder_usage(root, folder)

        print(f"  Files in folder: {result['file_count']}")
        print(f"  Imported by: {len(result['imported_by'])} files")
        print(f"  {result['recommendation']}")

        if result["imported_by"] and len(result["imported_by"]) <= 20:
            print(f"\n  Importers:")
            for imp in sorted(result["imported_by"])[:20]:
                print(f"    - {imp}")
            if len(result["imported_by"]) > 20:
                print(f"    ... and {len(result['imported_by']) - 20} more")

        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    for folder in candidates:
        result = analyze_folder_usage(root, folder)
        status_icon = (
            "✅"
            if result["is_safe"]
            else ("⚠️" if len(result["imported_by"]) < 10 else "❌")
        )
        print(
            f"{status_icon} {folder}/ - {result['file_count']} files, "
            f"{len(result['imported_by'])} imports"
        )

    print()
    print("Legend:")
    print("  ✅ = Safe to remove immediately")
    print("  ⚠️ = Can remove after updating <10 imports")
    print("  ❌ = Heavily used, keep or plan major migration")


if __name__ == "__main__":
    main()
