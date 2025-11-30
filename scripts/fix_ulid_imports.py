"""
Fix ULID imports - Remove ULID prefixes from import statements

This script finds and fixes imports like:
    from modules.core_state.010003_db import X
And converts them to:
    from modules.core_state import X

Usage:
    python scripts/fix_ulid_imports.py --dry-run
    python scripts/fix_ulid_imports.py --execute
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-FIX-ULID-IMPORTS-209
# DOC_ID: DOC-SCRIPT-SCRIPTS-FIX-ULID-IMPORTS-146

import re
import sys
from pathlib import Path
import argparse
import shutil


def fix_ulid_imports_in_file(filepath: Path, dry_run: bool = True) -> int:
    """
    Fix ULID-prefixed imports in a file.
    
    Pattern: from modules.X.0XXXXX_file import Y
    Replace: from modules.X import Y
    
    Returns: Number of fixes made
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern: from modules.module_name.ULID_filename import
        # Match: from modules.(\w+)\.0[0-9A-F]{5}_\w+ import
        pattern = re.compile(
            r'\bfrom\s+modules\.(\w+)\.0[0-9A-Fa-f]{5,6}_\w+\s+import\b'
        )
        
        def replacement(match):
            module_name = match.group(1)
            return f"from modules.{module_name} import"
        
        new_content, count = pattern.subn(replacement, content)
        
        if count == 0:
            return 0
        
        if dry_run:
            return count
        
        # Backup
        backup_path = filepath.with_suffix('.py.bak2')
        shutil.copy2(filepath, backup_path)
        
        # Write fixed content
        filepath.write_text(new_content, encoding='utf-8')
        
        # Remove backup
        backup_path.unlink()
        
        return count
    
    except Exception as e:
        print(f"  [!] Error: {filepath.name}: {e}")
        return 0


def fix_all_modules(dry_run: bool = True):
    """Fix ULID imports in all module files."""
    modules_dir = Path("modules")
    
    total_files = 0
    total_fixes = 0
    
    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        
        # Process all Python files except __init__.py
        py_files = [f for f in module_dir.glob("*.py") if f.name != '__init__.py']
        
        module_had_fixes = False
        
        for py_file in py_files:
            fixes = fix_ulid_imports_in_file(py_file, dry_run)
            
            if fixes > 0:
                if not module_had_fixes:
                    print(f"\n{module_dir.name}:")
                    module_had_fixes = True
                
                total_files += 1
                total_fixes += fixes
                mode = "[DRY-RUN]" if dry_run else "[FIXED]"
                print(f"  {mode} {py_file.name}: {fixes} imports")
    
    return total_files, total_fixes


def main():
    parser = argparse.ArgumentParser(description="Fix ULID-prefixed imports")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print(f"Fix ULID Imports")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")
    
    files_fixed, imports_fixed = fix_all_modules(dry_run)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Imports fixed: {imports_fixed}")
    
    if dry_run:
        print(f"\nTo apply: --execute")
    else:
        print(f"\nValidate:")
        print(f"  python -m compileall modules/ -q")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
