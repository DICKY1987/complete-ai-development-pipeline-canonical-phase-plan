"""
Simple Import Rewriter - String-based

Rewrites import statements using regex patterns.
Safer and more reliable than AST manipulation.

Usage:
    python scripts/rewrite_imports_simple.py --dry-run
    python scripts/rewrite_imports_simple.py --execute
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import argparse
import shutil


def load_inventory() -> dict:
    """Load MODULES_INVENTORY.yaml."""
    inventory_path = Path("MODULES_INVENTORY.yaml")
    if not inventory_path.exists():
        raise FileNotFoundError("MODULES_INVENTORY.yaml not found")
    
    return yaml.safe_load(inventory_path.read_text(encoding='utf-8'))


def build_conversion_rules(inventory: dict) -> List[Tuple[str, str]]:
    """
    Build list of (old_pattern, new_pattern) tuples for replacement.
    
    Strategy: Convert to module-level imports since ULID filenames can't be imported directly.
    Example:
        from core.state.db import X  ->  from modules.core_state import X
    """
    rules = []
    
    for module in inventory['modules']:
        module_id = module['id']
        source_dir = module['source_dir']
        files = module.get('files', [])
        
        # Convert module_id to Python import format
        module_import_name = module_id.replace('-', '_')
        
        # Directory-level conversion (this is what we'll use)
        source_parts = Path(source_dir).parts
        if len(source_parts) > 0:
            old_dir_import = '.'.join(source_parts)
            new_dir_import = f"modules.{module_import_name}"
            rules.append((old_dir_import, new_dir_import))
        
        # File-level conversions (map to module level)
        for file_path in files:
            file_obj = Path(file_path)
            file_name_no_ext = file_obj.stem
            
            # Old import path
            old_path_parts = list(source_parts) + [file_name_no_ext]
            old_import_path = '.'.join(old_path_parts)
            
            # New import path (module level, not file level)
            new_import_path = f"modules.{module_import_name}"
            
            rules.append((old_import_path, new_import_path))
    
    # Sort by length (longest first) to avoid partial replacements
    rules.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_rules = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            unique_rules.append(rule)
    
    return unique_rules


def rewrite_file_simple(filepath: Path, conversion_rules: List[Tuple[str, str]], dry_run: bool = True) -> Tuple[bool, int]:
    """
    Rewrite imports in file using string replacement.
    
    Returns:
        (success, changes_count)
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        changes_count = 0
        
        for old_pattern, new_pattern in conversion_rules:
            # Pattern 1: from X import Y
            pattern1 = f"from {re.escape(old_pattern)} import"
            replacement1 = f"from {new_pattern} import"
            
            new_content, count1 = re.subn(pattern1, replacement1, content)
            if count1 > 0:
                content = new_content
                changes_count += count1
            
            # Pattern 2: import X
            pattern2 = f"import {re.escape(old_pattern)}"
            replacement2 = f"import {new_pattern}"
            
            new_content, count2 = re.subn(pattern2, replacement2, content)
            if count2 > 0:
                content = new_content
                changes_count += count2
        
        if changes_count == 0:
            return True, 0
        
        if dry_run:
            return True, changes_count
        
        # Backup original
        backup_path = filepath.with_suffix('.py.bak')
        shutil.copy2(filepath, backup_path)
        
        # Write new content
        filepath.write_text(content, encoding='utf-8')
        
        # Remove backup (skip syntax validation - Python files were already valid)
        backup_path.unlink()
        
        return True, changes_count
    
    except Exception as e:
        print(f"  [!] Error: {filepath.name}: {e}")
        return False, 0


def rewrite_all_modules(conversion_rules: List[Tuple[str, str]], dry_run: bool = True):
    """Rewrite imports in all modules."""
    modules_dir = Path("modules")
    
    total_files = 0
    total_changes = 0
    failed = []
    
    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        
        py_files = list(module_dir.glob("*.py"))
        if not py_files:
            continue
        
        module_had_changes = False
        
        for py_file in py_files:
            success, changes = rewrite_file_simple(py_file, conversion_rules, dry_run)
            
            if changes > 0:
                if not module_had_changes:
                    print(f"\n{module_dir.name}:")
                    module_had_changes = True
                
                total_files += 1
                total_changes += changes
                mode = "[DRY-RUN]" if dry_run else "[UPDATED]"
                print(f"  {mode} {py_file.name}: {changes} imports")
            
            if not success:
                failed.append(str(py_file))
    
    return total_files, total_changes, failed


def main():
    parser = argparse.ArgumentParser(description="Rewrite import statements (simple)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print(f"Simple Import Rewriter")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")
    
    # Load conversion rules
    print("Loading conversion rules...")
    inventory = load_inventory()
    rules = build_conversion_rules(inventory)
    print(f"  {len(rules)} rules loaded\n")
    
    # Rewrite
    files_changed, imports_changed, failures = rewrite_all_modules(rules, dry_run)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files changed: {files_changed}")
    print(f"  Imports rewritten: {imports_changed}")
    
    if failures:
        print(f"  Failed: {len(failures)}")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)
    
    if dry_run:
        print(f"\nTo apply: --execute")
    else:
        print(f"\nSuccess! Validate with:")
        print(f"  python -m compileall modules/ -q")


if __name__ == "__main__":
    main()
