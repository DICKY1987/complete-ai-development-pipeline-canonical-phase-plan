#!/usr/bin/env python3
"""
Automated Import Migration Tool

Safely migrates all legacy src.* imports to new section-based imports.
Handles the complete refactor from src/pipeline/* to core/*, error/*, etc.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Define import mapping rules
IMPORT_MAPPINGS = {
    # State Management (src.pipeline -> core.state)
    r'from src\.pipeline\.db import': 'from core.state.db import',
    r'from src\.pipeline\.db_sqlite import': 'from core.state.db_sqlite import',
    r'from src\.pipeline\.crud_operations import': 'from core.state.crud import',
    r'from src\.pipeline\.bundles import': 'from core.state.bundles import',
    r'from src\.pipeline\.worktree import': 'from core.state.worktree import',
    
    # Engine/Orchestration (src.pipeline -> core.engine)
    r'from src\.pipeline\.orchestrator import': 'from core.engine.orchestrator import',
    r'from src\.pipeline\.scheduler import': 'from core.engine.scheduler import',
    r'from src\.pipeline\.executor import': 'from core.engine.executor import',
    r'from src\.pipeline\.tools import': 'from core.engine.tools import',
    r'from src\.pipeline\.circuit_breakers import': 'from core.engine.circuit_breakers import',
    r'from src\.pipeline\.recovery import': 'from core.engine.recovery import',
    
    # Planning (src.pipeline -> core.planning)
    r'from src\.pipeline\.planner import': 'from core.planning.planner import',
    r'from src\.pipeline\.archive import': 'from core.planning.archive import',
    
    # Error Engine (src.pipeline -> error.engine)
    r'from src\.pipeline\.error_engine import': 'from error.engine.error_engine import',
    r'from src\.pipeline\.error_state_machine import': 'from error.engine.error_state_machine import',
    r'from src\.pipeline\.error_pipeline_cli import': 'from error.engine.error_pipeline_cli import',
    r'from src\.pipeline\.error_pipeline_service import': 'from error.engine.error_pipeline_service import',
    r'from src\.pipeline\.error_context import': 'from error.engine.error_context import',
    
    # Core modules (src.pipeline -> core)
    r'from src\.pipeline\.openspec_parser import': 'from core.openspec_parser import',
    r'from src\.pipeline\.openspec_convert import': 'from core.openspec_convert import',
    r'from src\.pipeline\.spec_index import': 'from core.spec_index import',
    r'from src\.pipeline\.agent_coordinator import': 'from core.agent_coordinator import',
    r'from src\.pipeline\.prompts import': 'from core.prompts import',
    
    # AIM Integration (src.pipeline -> aim)
    r'from src\.pipeline\.aim_bridge import': 'from aim.bridge import',
    
    # Plugins (src.plugins.X.plugin -> error.plugins.X.plugin)
    r'from src\.plugins\.python_ruff\.plugin import': 'from error.plugins.python_ruff.plugin import',
    r'from src\.plugins\.python_mypy\.plugin import': 'from error.plugins.python_mypy.plugin import',
    r'from src\.plugins\.python_pyright\.plugin import': 'from error.plugins.python_pyright.plugin import',
    r'from src\.plugins\.python_pylint\.plugin import': 'from error.plugins.python_pylint.plugin import',
    r'from src\.plugins\.python_bandit\.plugin import': 'from error.plugins.python_bandit.plugin import',
    r'from src\.plugins\.python_safety\.plugin import': 'from error.plugins.python_safety.plugin import',
    r'from src\.plugins\.python_black_fix\.plugin import': 'from error.plugins.python_black_fix.plugin import',
    r'from src\.plugins\.python_isort_fix\.plugin import': 'from error.plugins.python_isort_fix.plugin import',
    r'from src\.plugins\.js_eslint\.plugin import': 'from error.plugins.js_eslint.plugin import',
    r'from src\.plugins\.js_prettier_fix\.plugin import': 'from error.plugins.js_prettier_fix.plugin import',
    r'from src\.plugins\.md_markdownlint\.plugin import': 'from error.plugins.md_markdownlint.plugin import',
    r'from src\.plugins\.md_mdformat_fix\.plugin import': 'from error.plugins.md_mdformat_fix.plugin import',
    r'from src\.plugins\.yaml_yamllint\.plugin import': 'from error.plugins.yaml_yamllint.plugin import',
    r'from src\.plugins\.json_jq\.plugin import': 'from error.plugins.json_jq.plugin import',
    r'from src\.plugins\.powershell_pssa\.plugin import': 'from error.plugins.powershell_pssa.plugin import',
    r'from src\.plugins\.gitleaks\.plugin import': 'from error.plugins.gitleaks.plugin import',
    r'from src\.plugins\.semgrep\.plugin import': 'from error.plugins.semgrep.plugin import',
    r'from src\.plugins\.codespell\.plugin import': 'from error.plugins.codespell.plugin import',
    r'from src\.plugins\.echo\.plugin import': 'from error.plugins.echo.plugin import',
    r'from src\.plugins\.test_runner\.plugin import': 'from error.plugins.test_runner.plugin import',
    r'from src\.plugins\.path_standardizer\.plugin import': 'from error.plugins.path_standardizer.plugin import',
    
    # Integrations (src.integrations -> keep as-is or map accordingly)
    r'from src\.integrations\.github_sync import': 'from src.integrations.github_sync import',
    
    # Utils (src.utils -> error.shared.utils)
    r'from src\.utils\.types import': 'from error.shared.utils.types import',
    r'from src\.utils\.time import': 'from error.shared.utils.time import',
    r'from src\.utils\.hashing import': 'from error.shared.utils.hashing import',
    r'from src\.utils\.jsonl_manager import': 'from error.shared.utils.jsonl_manager import',
    r'from src\.utils\.env import': 'from error.shared.utils.env import',
    r'from src\.utils import': 'from error.shared.utils import',
}


def migrate_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, int]:
    """
    Migrate imports in a single file.
    
    Args:
        file_path: Path to the file to migrate
        dry_run: If True, only show what would change
    
    Returns:
        Tuple of (changed, num_replacements)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        replacements = 0
        
        for old_pattern, new_import in IMPORT_MAPPINGS.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                replacements += 1
        
        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
            return True, replacements
        
        return False, 0
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}", file=sys.stderr)
        return False, 0


def find_python_files(base_dir: Path, exclude_dirs: List[str]) -> List[Path]:
    """Find all Python files excluding specified directories."""
    python_files = []
    
    for py_file in base_dir.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        python_files.append(py_file)
    
    return python_files


def main():
    parser = argparse.ArgumentParser(
        description='Migrate legacy src.* imports to new section-based imports'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for each file'
    )
    args = parser.parse_args()
    
    # Base directory (repository root)
    base_dir = Path(__file__).parent.parent
    
    # Directories to exclude from migration
    exclude_dirs = [
        '_DEPRECATED',
        '.venv',
        'venv',
        '__pycache__',
        '.pytest_cache',
        '.git',
        'node_modules',
        '.aider',
        '.migration_backup_20251120_144334'
    ]
    
    print("=" * 80)
    print("AUTOMATED IMPORT MIGRATION TOOL")
    print("=" * 80)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  LIVE MODE - Files will be modified!")
    
    print()
    print(f"📁 Scanning directory: {base_dir}")
    print(f"🚫 Excluding: {', '.join(exclude_dirs)}")
    print()
    
    # Find all Python files
    python_files = find_python_files(base_dir, exclude_dirs)
    print(f"📄 Found {len(python_files)} Python files")
    print()
    
    # Process files
    changed_files = []
    total_replacements = 0
    
    for file_path in python_files:
        changed, replacements = migrate_file(file_path, dry_run=args.dry_run)
        
        if changed:
            changed_files.append(file_path)
            total_replacements += replacements
            
            rel_path = file_path.relative_to(base_dir)
            status = "Would update" if args.dry_run else "Updated"
            print(f"✏️  {status}: {rel_path} ({replacements} import{'s' if replacements != 1 else ''})")
    
    # Summary
    print()
    print("=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Files scanned:     {len(python_files)}")
    print(f"Files changed:     {len(changed_files)}")
    print(f"Total imports:     {total_replacements}")
    print()
    
    if args.dry_run:
        print("💡 This was a DRY RUN. No files were modified.")
        print("   Run without --dry-run to apply changes:")
        print()
        print("   python scripts/auto_migrate_imports.py")
        print()
    else:
        print("✅ Migration complete!")
        print()
        print("NEXT STEPS:")
        print("1. Run tests: pytest -q")
        print("2. Verify imports: rg 'from src\\.(pipeline|plugins)' --type py")
        print("3. Move shims: pwsh scripts/consolidate_legacy_code.ps1")
        print()
    
    return 0 if not args.dry_run or len(changed_files) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
