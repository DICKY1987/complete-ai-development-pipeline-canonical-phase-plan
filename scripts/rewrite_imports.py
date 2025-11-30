"""
Import Rewriter - Week 2 Day 2

Rewrites import statements from old paths to new ULID-prefixed module paths.

Usage:
    python scripts/rewrite_imports.py --dry-run
    python scripts/rewrite_imports.py --execute
    python scripts/rewrite_imports.py --module core-engine --execute
    
Features:
- AST-based rewriting (preserves code structure)
- Conversion rules from MODULES_INVENTORY.yaml
- Dry-run mode for safety
- Syntax validation after rewriting
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-IMPORTS-226
# DOC_ID: DOC-SCRIPT-SCRIPTS-REWRITE-IMPORTS-163

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import argparse
import shutil


class ImportRewriter(ast.NodeTransformer):
    """AST transformer to rewrite import statements."""
    
    def __init__(self, conversion_map: Dict[str, str]):
        self.conversion_map = conversion_map
        self.changes_made = []
    
    def visit_Import(self, node):
        """Rewrite 'import X' statements."""
        new_names = []
        changed = False
        
        for alias in node.names:
            old_module = alias.name
            if old_module in self.conversion_map:
                new_module = self.conversion_map[old_module]
                new_names.append(ast.alias(name=new_module, asname=alias.asname))
                self.changes_made.append((old_module, new_module))
                changed = True
            else:
                new_names.append(alias)
        
        if changed:
            node.names = new_names
        
        return node
    
    def visit_ImportFrom(self, node):
        """Rewrite 'from X import Y' statements."""
        if node.module and node.module in self.conversion_map:
            old_module = node.module
            new_module = self.conversion_map[old_module]
            node.module = new_module
            self.changes_made.append((old_module, new_module))
        
        return node


def load_inventory() -> dict:
    """Load MODULES_INVENTORY.yaml."""
    inventory_path = Path("MODULES_INVENTORY.yaml")
    if not inventory_path.exists():
        raise FileNotFoundError("MODULES_INVENTORY.yaml not found")
    
    return yaml.safe_load(inventory_path.read_text(encoding='utf-8'))


def build_conversion_map(inventory: dict) -> Dict[str, str]:
    """
    Build conversion map from old import paths to new ULID-prefixed paths.
    
    Example:
        'core.state.db' -> 'modules.core_state.010003_db'
        'error.engine.error_engine' -> 'modules.error_engine.010004_error_engine'
    """
    conversion_map = {}
    
    for module in inventory['modules']:
        module_id = module['id']
        ulid_prefix = module['ulid_prefix']
        source_dir = module['source_dir']
        files = module.get('files', [])
        
        # Convert module_id to Python import format (replace - with _)
        module_import_name = module_id.replace('-', '_')
        
        # Map each file in the module
        for file_path in files:
            file_obj = Path(file_path)
            file_name_no_ext = file_obj.stem  # e.g., 'db' from 'db.py'
            
            # Old import path (e.g., core.state.db)
            # Derive from source_dir
            source_parts = Path(source_dir).parts
            old_path_parts = list(source_parts) + [file_name_no_ext]
            old_import_path = '.'.join(old_path_parts)
            
            # New import path (e.g., modules.core_state.010003_db)
            new_file_name = f"{ulid_prefix}_{file_name_no_ext}"
            new_import_path = f"modules.{module_import_name}.{new_file_name}"
            
            conversion_map[old_import_path] = new_import_path
        
        # Also map directory-level imports
        # e.g., 'core.state' -> 'modules.core_state'
        source_parts = Path(source_dir).parts
        if len(source_parts) > 0:
            old_dir_import = '.'.join(source_parts)
            new_dir_import = f"modules.{module_import_name}"
            conversion_map[old_dir_import] = new_dir_import
    
    return conversion_map


def rewrite_file(filepath: Path, conversion_map: Dict[str, str], dry_run: bool = True) -> Tuple[bool, List[Tuple[str, str]]]:
    """
    Rewrite imports in a single file.
    
    Returns:
        (success, changes_made)
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))
        
        # Apply transformations
        rewriter = ImportRewriter(conversion_map)
        new_tree = rewriter.visit(tree)
        
        if not rewriter.changes_made:
            return True, []  # No changes needed
        
        if dry_run:
            return True, rewriter.changes_made
        
        # Generate new code
        new_code = ast.unparse(new_tree)
        
        # Backup original
        backup_path = filepath.with_suffix('.py.bak')
        shutil.copy2(filepath, backup_path)
        
        # Write new code
        filepath.write_text(new_code, encoding='utf-8')
        
        # Validate syntax
        try:
            compile(new_code, str(filepath), 'exec')
        except SyntaxError as e:
            # Restore from backup
            shutil.copy2(backup_path, filepath)
            print(f"  [!] Syntax error after rewrite: {e}")
            return False, []
        
        # Remove backup if successful
        backup_path.unlink()
        
        return True, rewriter.changes_made
    
    except Exception as e:
        print(f"  [!] Error processing {filepath}: {e}")
        return False, []


def rewrite_modules(module_pattern: str, conversion_map: Dict[str, str], dry_run: bool = True):
    """Rewrite imports in modules matching pattern."""
    modules_dir = Path("modules")
    
    if module_pattern == "all":
        module_dirs = list(modules_dir.iterdir())
    else:
        import fnmatch
        module_dirs = [d for d in modules_dir.iterdir() if fnmatch.fnmatch(d.name, module_pattern)]
    
    total_files = 0
    total_changes = 0
    failed_files = []
    
    for module_dir in module_dirs:
        if not module_dir.is_dir():
            continue
        
        print(f"\nModule: {module_dir.name}")
        
        py_files = list(module_dir.glob("*.py"))
        
        for py_file in py_files:
            success, changes = rewrite_file(py_file, conversion_map, dry_run)
            
            if changes:
                total_files += 1
                total_changes += len(changes)
                mode = "[DRY-RUN]" if dry_run else "[UPDATED]"
                print(f"  {mode} {py_file.name}: {len(changes)} imports")
                for old, new in changes[:3]:  # Show first 3
                    print(f"    {old} -> {new}")
                if len(changes) > 3:
                    print(f"    ... and {len(changes) - 3} more")
            
            if not success:
                failed_files.append(str(py_file))
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files with changes: {total_files}")
    print(f"  Total imports rewritten: {total_changes}")
    
    if failed_files:
        print(f"  Failed files: {len(failed_files)}")
        for f in failed_files:
            print(f"    - {f}")
    
    return total_files, total_changes, failed_files


def main():
    parser = argparse.ArgumentParser(description="Rewrite import statements")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Show what would be changed without modifying files")
    parser.add_argument("--execute", action="store_true",
                       help="Actually modify files (overrides --dry-run)")
    parser.add_argument("--module", default="all",
                       help="Module pattern to rewrite (default: all)")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print(f"Import Rewriter")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"Pattern: {args.module}\n")
    
    # Load inventory and build conversion map
    print("Loading MODULES_INVENTORY.yaml...")
    inventory = load_inventory()
    
    print("Building conversion map...")
    conversion_map = build_conversion_map(inventory)
    print(f"  {len(conversion_map)} conversion rules loaded\n")
    
    # Rewrite imports
    files_changed, imports_changed, failures = rewrite_modules(
        args.module, 
        conversion_map, 
        dry_run
    )
    
    if dry_run:
        print(f"\nTo apply these changes, run with --execute")
    else:
        print(f"\nChanges applied successfully!")
        print(f"\nValidation:")
        print(f"  Run: python -m compileall modules/ -q")
        print(f"  Run: python scripts/analyze_imports.py modules/")
    
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
