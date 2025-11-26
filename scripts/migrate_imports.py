#!/usr/bin/env python3
"""
Automatically migrate deprecated imports to new paths.

This script updates Python files to use new import paths following the
Phase E section-based refactor.

Usage:
    # Check what would change
    python scripts/migrate_imports.py --check <path>
    
    # Preview changes without writing
    python scripts/migrate_imports.py --fix <path> --dry-run
    
    # Apply changes
    python scripts/migrate_imports.py --fix <path>
    
    # Fix entire project (excluding shims)
    python scripts/migrate_imports.py --fix . --exclude src/pipeline MOD_ERROR_PIPELINE

Safety features:
    - Creates .bak backups before modification
    - Dry-run mode for preview
    - Logs all changes to migration.log
"""

import argparse
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Import mapping: old pattern → new pattern
IMPORT_MIGRATIONS = {
    # State management
    (r'from\s+src\.pipeline\.db\s+import', 'from modules.core_state.m010003_db import'),
    (r'from\s+src\.pipeline\.db_sqlite\s+import', 'from modules.core_state.m010003_db_sqlite import'),
    (r'from\s+src\.pipeline\.crud_operations\s+import', 'from modules.core_state.m010003_crud import'),
    (r'from\s+src\.pipeline\.bundles\s+import', 'from modules.core_state.m010003_bundles import'),
    (r'from\s+src\.pipeline\.worktree\s+import', 'from modules.core_state.m010003_worktree import'),
    
    # Engine/orchestration
    (r'from\s+src\.pipeline\.orchestrator\s+import', 'from modules.core_engine.m010001_orchestrator import'),
    (r'from\s+src\.pipeline\.scheduler\s+import', 'from modules.core_engine.m010001_scheduler import'),
    (r'from\s+src\.pipeline\.executor\s+import', 'from modules.core_engine.m010001_executor import'),
    (r'from\s+src\.pipeline\.tools\s+import', 'from modules.core_engine.m010001_tools import'),
    (r'from\s+src\.pipeline\.circuit_breakers\s+import', 'from modules.core_engine.m010001_circuit_breakers import'),
    (r'from\s+src\.pipeline\.recovery\s+import', 'from modules.core_engine.m010001_recovery import'),
    
    # Planning
    (r'from\s+src\.pipeline\.planner\s+import', 'from modules.core_planning.m010002_planner import'),
    (r'from\s+src\.pipeline\.archive\s+import', 'from modules.core_planning.m010002_archive import'),
    
    # Other core components
    (r'from\s+src\.pipeline\.openspec_parser\s+import', 'from core.openspec_parser import'),
    (r'from\s+src\.pipeline\.openspec_convert\s+import', 'from core.openspec_convert import'),
    (r'from\s+src\.pipeline\.spec_index\s+import', 'from core.spec_index import'),
    (r'from\s+src\.pipeline\.agent_coordinator\s+import', 'from core.agent_coordinator import'),
    
    # AIM
    (r'from\s+src\.pipeline\.aim_bridge\s+import', 'from aim.bridge import'),
    
    # Error subsystem (from src.pipeline)
    (r'from\s+src\.pipeline\.error_engine\s+import', 'from modules.error_engine.m010004_error_engine import'),
    (r'from\s+src\.pipeline\.error_state_machine\s+import', 'from modules.error_engine.m010004_error_state_machine import'),
    (r'from\s+src\.pipeline\.error_pipeline_cli\s+import', 'from modules.error_engine.m010004_error_pipeline_cli import'),
    (r'from\s+src\.pipeline\.error_pipeline_service\s+import', 'from modules.error_engine.m010004_error_pipeline_service import'),
    (r'from\s+src\.pipeline\.error_context\s+import', 'from modules.error_engine.m010004_error_context import'),
    
    # Error subsystem (from MOD_ERROR_PIPELINE)
    (r'from\s+MOD_ERROR_PIPELINE\.file_hash_cache\s+import', 'from error.file_hash_cache import'),
    (r'from\s+MOD_ERROR_PIPELINE\.plugin_manager\s+import', 'from error.plugin_manager import'),
    (r'from\s+MOD_ERROR_PIPELINE\.pipeline_engine\s+import', 'from error.pipeline_engine import'),
    (r'from\s+MOD_ERROR_PIPELINE\.error_engine\s+import', 'from modules.error_engine.m010004_error_engine import'),
    (r'from\s+MOD_ERROR_PIPELINE\.error_state_machine\s+import', 'from modules.error_engine.m010004_error_state_machine import'),
    (r'from\s+MOD_ERROR_PIPELINE\.error_pipeline_cli\s+import', 'from modules.error_engine.m010004_error_pipeline_cli import'),
    (r'from\s+MOD_ERROR_PIPELINE\.error_pipeline_service\s+import', 'from modules.error_engine.m010004_error_pipeline_service import'),
    (r'from\s+MOD_ERROR_PIPELINE\.error_context\s+import', 'from modules.error_engine.m010004_error_context import'),
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def migrate_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Migrate imports in a single file.
    
    Args:
        filepath: Path to Python file
        dry_run: If True, don't write changes
        
    Returns:
        (changed, num_changes)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        logger.warning(f"Skipping {filepath}: {e}")
        return False, 0
    
    original_content = content
    changes_made = 0
    
    # Apply all migration patterns
    for old_pattern, new_pattern in IMPORT_MIGRATIONS:
        matches = list(re.finditer(old_pattern, content))
        if matches:
            logger.info(f"{filepath}: Migrating '{old_pattern}' → '{new_pattern}' ({len(matches)} occurrence(s))")
            content = re.sub(old_pattern, new_pattern, content)
            changes_made += len(matches)
    
    if changes_made > 0:
        if not dry_run:
            # Create backup
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
            shutil.copy2(filepath, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Updated {filepath} ({changes_made} change(s))")
        else:
            logger.info(f"[DRY RUN] Would update {filepath} ({changes_made} change(s))")
        
        return True, changes_made
    
    return False, 0


def migrate_directory(
    path: Path,
    dry_run: bool = False,
    exclude_patterns: List[str] = None
) -> Dict[str, int]:
    """
    Recursively migrate imports in a directory.
    
    Args:
        path: Directory to scan
        dry_run: If True, don't write changes
        exclude_patterns: Patterns to exclude
        
    Returns:
        Dict of filepath → num_changes
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '.pytest_cache',
            'build',
            'dist',
            '*.egg-info',
            # Don't migrate the shim files themselves
            'src/pipeline/',
            'MOD_ERROR_PIPELINE/',
            # Exclude top-level core shims
            'core/agent_coordinator.py',
            'core/aim_bridge.py',
            'core/archive.py',
            'core/circuit_breakers.py',
            'core/db.py',
            'core/db_sqlite.py',
            'core/error_context.py',
            'core/error_pipeline_service.py',
            'core/executor.py',
            'core/openspec_convert.py',
            'core/openspec_parser.py',
            'core/orchestrator.py',
            'core/planner.py',
            'core/prompts.py',
            'core/recovery.py',
            'core/scheduler.py',
            'core/spec_index.py',
            'core/tools.py',
            'core/worktree.py',
            'core/bundles.py',
            'core/crud_operations.py',
        ]
    
    results = {}
    
    for py_file in path.rglob('*.py'):
        # Check if file should be excluded
        skip = False
        # Normalize path separators for comparison
        file_str = str(py_file).replace('\\', '/')
        for pattern in exclude_patterns:
            # Normalize pattern separators
            pattern = pattern.replace('\\', '/')
            if pattern in file_str:
                skip = True
                break
        
        if skip:
            continue
        
        changed, num_changes = migrate_file(py_file, dry_run)
        if changed:
            results[str(py_file)] = num_changes
    
    return results


def check_directory(path: Path, exclude_patterns: List[str] = None) -> List[Path]:
    """
    Check which files would be modified.
    
    Args:
        path: Directory to scan
        exclude_patterns: Patterns to exclude
        
    Returns:
        List of file paths that would be modified
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.pytest_cache', 'build', 'dist', '*.egg-info',
            'src/pipeline/', 'MOD_ERROR_PIPELINE/',
            'core/agent_coordinator.py', 'core/aim_bridge.py', 'core/archive.py',
            'core/circuit_breakers.py', 'core/db.py', 'core/db_sqlite.py',
            'core/error_context.py', 'core/error_pipeline_service.py',
            'core/executor.py', 'core/openspec_convert.py', 'core/openspec_parser.py',
            'core/orchestrator.py', 'core/planner.py', 'core/prompts.py',
            'core/recovery.py', 'core/scheduler.py', 'core/spec_index.py',
            'core/tools.py', 'core/worktree.py', 'core/bundles.py', 'core/crud_operations.py'
        ]
    
    files_to_modify = []
    
    for py_file in path.rglob('*.py'):
        skip = False
        # Normalize path separators for comparison
        file_str = str(py_file).replace('\\', '/')
        for pattern in exclude_patterns:
            # Normalize pattern separators
            pattern = pattern.replace('\\', '/')
            if pattern in file_str:
                skip = True
                break
        
        if skip:
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if any migration patterns match
            for old_pattern, _ in IMPORT_MIGRATIONS:
                if re.search(old_pattern, content):
                    files_to_modify.append(py_file)
                    break
        except (UnicodeDecodeError, PermissionError):
            pass
    
    return files_to_modify


def main():
    parser = argparse.ArgumentParser(
        description="Migrate deprecated imports to new paths"
    )
    parser.add_argument(
        'path',
        type=Path,
        help='File or directory to migrate'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check which files would be modified (no changes)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Apply migrations (creates backups)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without writing files'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Additional patterns to exclude'
    )
    
    args = parser.parse_args()
    
    if not args.check and not args.fix:
        parser.error("Must specify either --check or --fix")
    
    if not args.path.exists():
        logger.error(f"Path does not exist: {args.path}")
        sys.exit(1)
    
    # Build exclude patterns
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.pytest_cache', 'build', 'dist', '*.egg-info',
            'src/pipeline/', 'MOD_ERROR_PIPELINE/',
            'core/agent_coordinator.py', 'core/aim_bridge.py', 'core/archive.py',
            'core/circuit_breakers.py', 'core/db.py', 'core/db_sqlite.py',
            'core/error_context.py', 'core/error_pipeline_service.py',
            'core/executor.py', 'core/openspec_convert.py', 'core/openspec_parser.py',
            'core/orchestrator.py', 'core/planner.py', 'core/prompts.py',
            'core/recovery.py', 'core/scheduler.py', 'core/spec_index.py',
            'core/tools.py', 'core/worktree.py', 'core/bundles.py', 'core/crud_operations.py'
        ] + args.exclude
    
    logger.info(f"Starting migration for: {args.path}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    if args.check:
        # Check mode
        if args.path.is_file():
            # Check single file
            try:
                with open(args.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                has_deprecated = any(re.search(pattern, content) for pattern, _ in IMPORT_MIGRATIONS)
                if has_deprecated:
                    print(f"✓ {args.path} - would be modified")
                else:
                    print(f"✗ {args.path} - no changes needed")
            except Exception as e:
                logger.error(f"Error reading {args.path}: {e}")
                sys.exit(1)
        else:
            # Check directory
            files_to_modify = check_directory(args.path, exclude_patterns)
            
            if files_to_modify:
                print(f"\nFound {len(files_to_modify)} file(s) that would be modified:\n")
                for filepath in sorted(files_to_modify):
                    print(f"  ✓ {filepath}")
                print(f"\nRun with --fix to apply changes")
            else:
                print("✅ No files need migration")
    
    elif args.fix:
        # Fix mode
        if args.path.is_file():
            # Migrate single file
            changed, num_changes = migrate_file(args.path, args.dry_run)
            if changed:
                status = "[DRY RUN]" if args.dry_run else "✅"
                print(f"{status} Updated {args.path} ({num_changes} change(s))")
            else:
                print(f"✗ {args.path} - no changes needed")
        else:
            # Migrate directory
            results = migrate_directory(args.path, args.dry_run, exclude_patterns)
            
            total_changes = sum(results.values())
            
            if results:
                status = "[DRY RUN]" if args.dry_run else "✅"
                print(f"\n{status} Migration complete!")
                print(f"  Files modified: {len(results)}")
                print(f"  Total changes: {total_changes}")
                
                if not args.dry_run:
                    print(f"\n💾 Backups created with .bak extension")
                    print(f"📝 Details logged to migration.log")
            else:
                print("✅ No files needed migration")
    
    logger.info("Migration complete")


if __name__ == '__main__':
    main()
