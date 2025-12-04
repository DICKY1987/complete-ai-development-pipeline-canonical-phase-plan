"""
Import Rewriter v2 - Module-level imports only

Rewrites file-level imports to module-level imports.
Example:
    from modules.core_state.m010003_db import get_connection
    → from modules.core_state import get_connection

Usage:
    python scripts/rewrite_imports_v2.py --modules "core-*" --dry-run
    python scripts/rewrite_imports_v2.py --modules "core-*" --execute
    python scripts/rewrite_imports_v2.py --all --execute
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-IMPORTS-V2-228
# DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-IMPORTS-V2-165

import re
import sys
from pathlib import Path
from typing import Dict, List
import yaml
import argparse
import fnmatch
import shutil


def load_inventory() -> dict:
    """Load MODULES_INVENTORY.yaml."""
    return yaml.safe_load(Path("MODULES_INVENTORY.yaml").read_text())


def build_conversion_map(inventory: dict) -> Dict[str, str]:
    """
    Build map from old import paths to new module-level paths.

    Example:
        'core.state' -> 'modules.core_state'
        'error.engine' -> 'modules.error_engine'
    """
    conversion_map = {}

    for module in inventory['modules']:
        module_id = module['id']
        source_dir = module['source_dir']

        # Convert to Python import format
        module_import_name = module_id.replace('-', '_')
        new_module_path = f"modules.{module_import_name}"

        # Base import paths to rewrite to module-level
        base_paths = set()
        # From source directory (e.g., modules/core-state -> modules.core-state/core_state)
        source_parts = Path(source_dir).parts
        if source_parts:
            base_paths.add('.'.join(source_parts))
        base_paths.add(f"modules.{module_id}")  # modules.core-engine
        base_paths.add(f"modules.{module_import_name}")  # modules.core_engine
        # Legacy section-based imports (core.state, error.engine, etc.)
        section_parts = module_id.split('-', 1)
        if len(section_parts) == 2:
            base_paths.add('.'.join(section_parts))

        # Map base paths and their file-level imports to module-level
        for base_path in base_paths:
            conversion_map[base_path] = new_module_path
            for file_path in module.get('files', []):
                file_stem = Path(file_path).stem
                conversion_map[f"{base_path}.{file_stem}"] = new_module_path

    return conversion_map


def rewrite_file(filepath: Path, conversion_map: Dict[str, str], dry_run: bool = True) -> int:
    """
    Rewrite imports in file to use module-level paths.

    Returns: Number of changes made
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        changes_count = 0

        # Sort by length (longest first) to avoid partial matches
        sorted_patterns = sorted(conversion_map.items(), key=lambda x: len(x[0]), reverse=True)

        for old_path, new_path in sorted_patterns:
            # Pattern 1: from X import Y
            pattern1 = re.compile(rf'\bfrom\s+{re.escape(old_path)}\s+import\b')
            replacement1 = f"from {new_path} import"

            new_content, count1 = pattern1.subn(replacement1, content)
            if count1 > 0:
                content = new_content
                changes_count += count1

            # Pattern 2: import X (less common but handle it)
            pattern2 = re.compile(rf'\bimport\s+{re.escape(old_path)}\b')
            replacement2 = f"import {new_path}"

            new_content, count2 = pattern2.subn(replacement2, content)
            if count2 > 0:
                content = new_content
                changes_count += count2

        if changes_count == 0:
            return 0

        if dry_run:
            return changes_count

        # Backup original
        backup_path = filepath.with_suffix('.py.bak')
        shutil.copy2(filepath, backup_path)

        # Write new content
        filepath.write_text(content, encoding='utf-8')

        # Remove backup (we trust the regex replacements)
        backup_path.unlink()

        return changes_count

    except Exception as e:
        print(f"  [!] Error: {filepath.name}: {e}")
        return 0


def rewrite_modules(module_pattern: str, conversion_map: Dict[str, str], dry_run: bool = True):
    """Rewrite imports in modules matching pattern."""
    modules_dir = Path("modules")

    if module_pattern == "all":
        module_dirs = [d for d in modules_dir.iterdir() if d.is_dir()]
    else:
        # Support multiple patterns separated by comma
        patterns = [p.strip() for p in module_pattern.split(',')]
        module_dirs = []
        for d in modules_dir.iterdir():
            if d.is_dir() and any(fnmatch.fnmatch(d.name, p) for p in patterns):
                module_dirs.append(d)

    total_files = 0
    total_changes = 0

    for module_dir in sorted(module_dirs):
        py_files = [f for f in module_dir.glob("*.py") if not f.name.startswith('__init__')]

        if not py_files:
            continue

        module_had_changes = False

        for py_file in py_files:
            changes = rewrite_file(py_file, conversion_map, dry_run)

            if changes > 0:
                if not module_had_changes:
                    print(f"\n{module_dir.name}:")
                    module_had_changes = True

                total_files += 1
                total_changes += changes
                mode = "[DRY-RUN]" if dry_run else "[UPDATED]"
                print(f"  {mode} {py_file.name}: {changes} imports")

    return total_files, total_changes


def main():
    parser = argparse.ArgumentParser(description="Rewrite imports to module-level (v2)")
    parser.add_argument("--all", action="store_true", help="Process all modules")
    parser.add_argument("--modules", help="Module pattern (e.g., 'core-*' or 'core-*,error-*')")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")

    args = parser.parse_args()
    dry_run = not args.execute

    # Determine pattern
    if args.all:
        pattern = "all"
    elif args.modules:
        pattern = args.modules
    else:
        print("Specify --all or --modules")
        return 1

    print(f"Import Rewriter v2")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"Pattern: {pattern}\n")

    # Load inventory and build map
    print("Loading conversion rules...")
    inventory = load_inventory()
    conversion_map = build_conversion_map(inventory)
    print(f"  {len(conversion_map)} rules loaded\n")

    # Rewrite
    files_changed, imports_changed = rewrite_modules(pattern, conversion_map, dry_run)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files changed: {files_changed}")
    print(f"  Imports rewritten: {imports_changed}")

    if dry_run:
        print(f"\nTo apply: --execute")
    else:
        print(f"\nValidate:")
        print(f"  python -m compileall modules/ -q")

    return 0


if __name__ == "__main__":
    sys.exit(main())
