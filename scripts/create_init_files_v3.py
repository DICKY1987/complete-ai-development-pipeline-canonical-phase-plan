"""
Create __init__.py files (v3) - Using importlib for ULID files

Since Python identifiers can't start with digits, we use importlib
to dynamically import ULID-prefixed files and re-export their symbols.

Usage:
    python scripts/create_init_files_v3.py --all --execute
"""

from pathlib import Path
import yaml
import argparse


def create_init_file_v3(module_dir: Path, module_id: str, ulid_prefix: str, layer: str) -> str:
    """
    Create __init__.py using importlib for ULID files.
    
    Strategy:
    - Use importlib.import_module() to load ULID files
    - Extract all public symbols (__all__ or non-private)
    - Re-export at module level
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
    
    module_import_name = module_id.replace('-', '_')
    
    # Generate content
    content = f'''"""Module: {module_id}

ULID Prefix: {ulid_prefix}
Layer: {layer}
Files: {len(code_files)}

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.{module_import_name} import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "{module_id}"
__ulid_prefix__ = "{ulid_prefix}"
__layer__ = "{layer}"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
'''
    
    for py_file in code_files:
        module_name = py_file.stem
        content += f'    "{module_name}",\n'
    
    content += f''']

for _file_stem in _ulid_files:
    _module_path = f"modules.{module_import_name}.{{_file_stem}}"
    try:
        _mod = importlib.import_module(_module_path)
        
        # Re-export all public symbols
        if hasattr(_mod, '__all__'):
            for _name in _mod.__all__:
                globals()[_name] = getattr(_mod, _name)
        else:
            # Export everything that doesn't start with underscore
            for _name in dir(_mod):
                if not _name.startswith('_'):
                    globals()[_name] = getattr(_mod, _name)
    except Exception as e:
        print(f"Warning: Could not import {{_module_path}}: {{e}}", file=sys.stderr)
'''
    
    return content


def main():
    parser = argparse.ArgumentParser(description="Create __init__.py files (v3 - importlib)")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--module", help="Process specific module")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print(f"Create __init__.py Files (v3 - importlib)")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")
    
    # Load inventory
    inventory = yaml.safe_load(Path("MODULES_INVENTORY.yaml").read_text())
    
    # Select modules
    if args.all:
        modules = inventory['modules']
    elif args.module:
        modules = [m for m in inventory['modules'] if m['id'] == args.module]
        if not modules:
            print(f"Module '{args.module}' not found")
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
        content = create_init_file_v3(module_dir, module_id, ulid_prefix, layer)
        
        if not content:
            print(f"[SKIP] {module_id} - no Python files")
            skipped += 1
            continue
        
        init_file = module_dir / "__init__.py"
        
        if dry_run:
            print(f"[DRY-RUN] {module_id} ({len(content)} bytes)")
        else:
            init_file.write_text(content, encoding='utf-8')
            print(f"[CREATED] {module_id} ({len(content)} bytes)")
            created += 1
    
    print(f"\n{'='*60}")
    print(f"Created: {created}, Skipped: {skipped}")
    
    if dry_run:
        print(f"\nTo apply: --execute")
    else:
        print(f"\nValidate: python -m compileall modules/ -q")


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
