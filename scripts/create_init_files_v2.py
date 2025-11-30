"""
Create __init__.py files (v2) - Module-level imports from ULID files

Strategy:
- For each module, find all {ULID}_*.py files
- Generate: from .{ULID}_filename import *
- This makes ULID files importable via module level

Usage:
    python scripts/create_init_files_v2.py --all --dry-run
    python scripts/create_init_files_v2.py --all --execute
    python scripts/create_init_files_v2.py --module core-state --execute
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-INIT-FILES-V2-200
DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-INIT-FILES-V2-137

from pathlib import Path
import yaml
import argparse


def create_init_file_v2(module_dir: Path, module_id: str, ulid_prefix: str, layer: str) -> str:
    """
    Create __init__.py that imports from ULID-prefixed files.
    
    Returns: Generated content
    """
    # Find all Python files with ULID prefix
    py_files = sorted(module_dir.glob(f"{ulid_prefix}_*.py"))
    
    # Filter out non-code files
    code_files = [
        f for f in py_files 
        if not f.name.endswith(('_README.md', '.manifest.yaml', '.manifest.json'))
    ]
    
    if not code_files:
        return None
    
    # Generate content
    content = f'''"""Module: {module_id}

ULID Prefix: {ulid_prefix}
Layer: {layer}
Files: {len(code_files)}

This module re-exports all symbols from ULID-prefixed files.
Import from this module, not from ULID files directly:
    
    from modules.{module_id.replace('-', '_')} import function_name  # ✅
    from modules.{module_id.replace('-', '_')}.{ulid_prefix}_file import function_name  # ❌
"""

# Re-export all symbols from ULID-prefixed files
'''
    
    for py_file in code_files:
        module_name = py_file.stem  # e.g., "010003_db"
        content += f"from .{module_name} import *\n"
    
    content += f'''
# Module metadata
__module_id__ = "{module_id}"
__ulid_prefix__ = "{ulid_prefix}"
__layer__ = "{layer}"
__all__ = []  # Populated by wildcard imports above
'''
    
    return content


def main():
    parser = argparse.ArgumentParser(description="Create __init__.py files (v2)")
    parser.add_argument("--all", action="store_true", help="Process all modules")
    parser.add_argument("--module", help="Process specific module")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print(f"Create __init__.py Files (v2)")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")
    
    # Load inventory
    inventory = yaml.safe_load(Path("MODULES_INVENTORY.yaml").read_text())
    
    # Select modules
    if args.all:
        modules = inventory['modules']
    elif args.module:
        modules = [m for m in inventory['modules'] if m['id'] == args.module]
        if not modules:
            print(f"Module '{args.module}' not found in inventory")
            return 1
    else:
        print("Specify --all or --module")
        return 1
    
    created = 0
    skipped = 0
    
    for module in modules:
        module_id = module['id']
        ulid_prefix = module['ulid_prefix']
        layer = module.get('layer', 'unknown')
        
        module_dir = Path("modules") / module_id
        
        if not module_dir.exists():
            print(f"[SKIP] {module_id} - directory not found")
            skipped += 1
            continue
        
        # Generate content
        content = create_init_file_v2(module_dir, module_id, ulid_prefix, layer)
        
        if not content:
            print(f"[SKIP] {module_id} - no Python files found")
            skipped += 1
            continue
        
        init_file = module_dir / "__init__.py"
        
        if dry_run:
            print(f"[DRY-RUN] {module_id} - would create __init__.py ({len(content)} bytes)")
        else:
            init_file.write_text(content, encoding='utf-8')
            print(f"[CREATED] {module_id} - __init__.py ({len(content)} bytes)")
            created += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    
    if dry_run:
        print(f"\nTo apply: --execute")
    else:
        print(f"\nValidate:")
        print(f"  python -m compileall modules/*/__ init__.py -q")


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
