"""
Automated Import Rewriter
Pattern: EXEC-001 + Batch Processing
Generates and applies import path rewrites across all Python files
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-ALL-IMPORTS-225
DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-ALL-IMPORTS-162

import sys
from pathlib import Path
import yaml
from typing import Dict, Set, List
import re

def load_inventory() -> Dict:
    """Load MODULES_INVENTORY.yaml."""
    inventory_path = Path("MODULES_INVENTORY.yaml")
    if not inventory_path.exists():
        print("❌ MODULES_INVENTORY.yaml not found")
        sys.exit(1)
    
    with inventory_path.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_rewrite_map() -> Dict[str, str]:
    """Generate import rewrite rules from inventory."""
    print("Generating import rewrite map...")
    inventory = load_inventory()
    
    rewrites = {}
    
    for module in inventory['modules']:
        module_id = module['id']
        ulid = module['ulid_prefix']
        
        # Process each file in the module
        for file_path in module.get('files', []):
            file_obj = Path(file_path)
            
            # Skip non-Python files
            if file_obj.suffix != '.py':
                continue
            
            # Original import path (without .py)
            # Example: core/state/db.py -> core.state.db
            original_path = file_path.replace('\\', '/').replace('.py', '').replace('/', '.')
            
            # New import path in modules
            # Example: modules.core_state.m010003_db (m prefix + underscores for valid Python)
            # Python doesn't allow identifiers starting with digits or containing hyphens
            new_filename = f"m{ulid}_{file_obj.stem}"
            # Replace hyphens with underscores for valid Python identifiers
            safe_module_id = module_id.replace('-', '_')
            new_path = f"modules.{safe_module_id}.{new_filename}"
            
            # Add rewrite rules for different import patterns
            # Pattern 1: from X import Y
            rewrites[f"from {original_path} import"] = f"from {new_path} import"
            
            # Pattern 2: import X
            rewrites[f"import {original_path}"] = f"import {new_path}"
            
            # Pattern 3: from X.Y import (for parent packages)
            parts = original_path.split('.')
            if len(parts) > 1:
                parent = '.'.join(parts[:-1])
                module_part = parts[-1]
                # from modules.core_state import m010003_db -> from modules.core_state import m010003_db
                old_parent_import = f"from {parent} import {module_part}"
                new_parent_import = f"from modules.{safe_module_id} import {new_filename}"
                rewrites[old_parent_import] = new_parent_import
    
    print(f"  Generated {len(rewrites)} rewrite rules")
    return rewrites

def rewrite_file(file_path: Path, rewrites: Dict[str, str]) -> tuple:
    """Rewrite imports in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        changes = 0
        
        # Apply each rewrite rule
        for old_import, new_import in rewrites.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes += 1
        
        # Write back if changed
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return (True, changes)
        
        return (False, 0)
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path}: {e}")
        return (False, 0)

def rewrite_all_imports(dry_run: bool = False) -> int:
    """Rewrite imports in all Python files."""
    print("=" * 70)
    print("Batch Import Rewriting - EXEC-001 Pattern")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 70)
    
    # Generate rewrite map
    rewrites = generate_rewrite_map()
    
    if not rewrites:
        print("❌ No rewrite rules generated")
        return 1
    
    # Find all Python files (excluding some directories)
    exclude_dirs = {'.venv', '__pycache__', '.git', 'legacy', 'archive'}
    python_files = []
    
    for py_file in Path(".").rglob("*.py"):
        # Skip excluded directories
        if any(excl in py_file.parts for excl in exclude_dirs):
            continue
        python_files.append(py_file)
    
    print(f"\nFound {len(python_files)} Python files to process")
    
    if dry_run:
        print("\n[DRY RUN] Showing sample rewrites:")
        sample_count = 0
        for old, new in list(rewrites.items())[:10]:
            print(f"  {old}")
            print(f"  → {new}")
            sample_count += 1
        if len(rewrites) > 10:
            print(f"  ... and {len(rewrites) - 10} more rules")
        return 0
    
    # Process all files
    files_changed = 0
    total_changes = 0
    
    for i, py_file in enumerate(python_files):
        changed, change_count = rewrite_file(py_file, rewrites)
        if changed:
            files_changed += 1
            total_changes += change_count
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(python_files)} files...")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Rewrite complete!")
    print(f"  Files changed:     {files_changed}/{len(python_files)}")
    print(f"  Total rewrites:    {total_changes}")
    print("=" * 70)
    
    return 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Rewrite import paths for module migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    
    args = parser.parse_args()
    
    return rewrite_all_imports(args.dry_run)

if __name__ == "__main__":
    sys.exit(main())
