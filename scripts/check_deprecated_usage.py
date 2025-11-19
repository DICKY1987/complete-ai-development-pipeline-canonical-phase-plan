#!/usr/bin/env python3
"""
Scan codebase for deprecated import patterns.

This script identifies files still using old import paths that have been
deprecated during the Phase E section-based refactor.

Usage:
    python scripts/check_deprecated_usage.py
    python scripts/check_deprecated_usage.py --path <directory>
    python scripts/check_deprecated_usage.py --json
    python scripts/check_deprecated_usage.py --strict  # Exit 1 if deprecated usage found
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Old → New import mappings
DEPRECATED_PATTERNS = {
    # src.pipeline.* → core.* or aim.*
    r'from\s+src\.pipeline\.db\s+import': 'from core.state.db import',
    r'from\s+src\.pipeline\.db_sqlite\s+import': 'from core.state.db_sqlite import',
    r'from\s+src\.pipeline\.crud_operations\s+import': 'from core.state.crud import',
    r'from\s+src\.pipeline\.bundles\s+import': 'from core.state.bundles import',
    r'from\s+src\.pipeline\.worktree\s+import': 'from core.state.worktree import',
    r'from\s+src\.pipeline\.orchestrator\s+import': 'from core.engine.orchestrator import',
    r'from\s+src\.pipeline\.scheduler\s+import': 'from core.engine.scheduler import',
    r'from\s+src\.pipeline\.executor\s+import': 'from core.engine.executor import',
    r'from\s+src\.pipeline\.tools\s+import': 'from core.engine.tools import',
    r'from\s+src\.pipeline\.circuit_breakers\s+import': 'from core.engine.circuit_breakers import',
    r'from\s+src\.pipeline\.recovery\s+import': 'from core.engine.recovery import',
    r'from\s+src\.pipeline\.planner\s+import': 'from core.planning.planner import',
    r'from\s+src\.pipeline\.archive\s+import': 'from core.planning.archive import',
    r'from\s+src\.pipeline\.aim_bridge\s+import': 'from aim.bridge import',
    r'from\s+src\.pipeline\.openspec_parser\s+import': 'from core.openspec_parser import',
    r'from\s+src\.pipeline\.openspec_convert\s+import': 'from core.openspec_convert import',
    r'from\s+src\.pipeline\.spec_index\s+import': 'from core.spec_index import',
    r'from\s+src\.pipeline\.agent_coordinator\s+import': 'from core.agent_coordinator import',
    r'from\s+src\.pipeline\.error_engine\s+import': 'from error.engine.error_engine import',
    r'from\s+src\.pipeline\.error_state_machine\s+import': 'from error.engine.error_state_machine import',
    r'from\s+src\.pipeline\.error_pipeline_cli\s+import': 'from error.engine.error_pipeline_cli import',
    r'from\s+src\.pipeline\.error_pipeline_service\s+import': 'from error.engine.error_pipeline_service import',
    r'from\s+src\.pipeline\.error_context\s+import': 'from error.engine.error_context import',
    
    # MOD_ERROR_PIPELINE.* → error.*
    r'from\s+MOD_ERROR_PIPELINE\.file_hash_cache\s+import': 'from error.file_hash_cache import',
    r'from\s+MOD_ERROR_PIPELINE\.plugin_manager\s+import': 'from error.plugin_manager import',
    r'from\s+MOD_ERROR_PIPELINE\.pipeline_engine\s+import': 'from error.pipeline_engine import',
    r'from\s+MOD_ERROR_PIPELINE\.error_engine\s+import': 'from error.engine.error_engine import',
    r'from\s+MOD_ERROR_PIPELINE\.error_state_machine\s+import': 'from error.engine.error_state_machine import',
    r'from\s+MOD_ERROR_PIPELINE\.error_pipeline_cli\s+import': 'from error.engine.error_pipeline_cli import',
    r'from\s+MOD_ERROR_PIPELINE\.error_pipeline_service\s+import': 'from error.engine.error_pipeline_service import',
    r'from\s+MOD_ERROR_PIPELINE\.error_context\s+import': 'from error.engine.error_context import',
    
    # Catch-all patterns for any remaining src.pipeline or MOD_ERROR_PIPELINE imports
    r'from\s+src\.pipeline\.': 'from core.* or error.* or aim.*',
    r'from\s+MOD_ERROR_PIPELINE\.': 'from error.*',
    r'import\s+src\.pipeline\.': 'import core.* or error.* or aim.*',
    r'import\s+MOD_ERROR_PIPELINE\.': 'import error.*',
}


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Scan a single file for deprecated imports.
    
    Returns:
        List of (line_number, deprecated_import, suggested_replacement)
    """
    results = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                for old_pattern, new_pattern in DEPRECATED_PATTERNS.items():
                    if re.search(old_pattern, line):
                        results.append((line_num, line.strip(), new_pattern))
    except (UnicodeDecodeError, PermissionError):
        # Skip binary files or files we can't read
        pass
    
    return results


def scan_directory(path: Path, exclude_patterns: List[str] = None) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Recursively scan a directory for deprecated imports.
    
    Args:
        path: Directory to scan
        exclude_patterns: List of path patterns to exclude
        
    Returns:
        Dict mapping file paths to lists of deprecated imports
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
            # Don't scan the shim files themselves
            'src/pipeline/',
            'MOD_ERROR_PIPELINE/',
            # Exclude top-level core shims (they're < 200 bytes)
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
        
        file_results = scan_file(py_file)
        if file_results:
            results[str(py_file)] = file_results
    
    return results


def generate_report(results: Dict[str, List[Tuple[int, str, str]]], output_format: str = 'text') -> str:
    """
    Generate a report of deprecated usage.
    
    Args:
        results: Scan results
        output_format: 'text' or 'json'
        
    Returns:
        Formatted report string
    """
    if output_format == 'json':
        json_results = {}
        for filepath, issues in results.items():
            json_results[filepath] = [
                {
                    'line': line_num,
                    'deprecated': old_import,
                    'suggested': new_import
                }
                for line_num, old_import, new_import in issues
            ]
        return json.dumps(json_results, indent=2)
    
    # Text format
    if not results:
        return "✅ No deprecated imports found!"
    
    total_issues = sum(len(issues) for issues in results.values())
    
    report_lines = [
        "=" * 80,
        "DEPRECATED IMPORT USAGE REPORT",
        "=" * 80,
        f"\nFound {total_issues} deprecated import(s) in {len(results)} file(s)\n",
    ]
    
    for filepath, issues in sorted(results.items()):
        report_lines.append(f"\n📄 {filepath} ({len(issues)} issue(s))")
        report_lines.append("-" * 80)
        
        for line_num, old_import, new_import in issues:
            report_lines.append(f"  Line {line_num}:")
            report_lines.append(f"    ❌ {old_import}")
            report_lines.append(f"    ✅ {new_import}")
            report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("\nRECOMMENDATIONS:")
    report_lines.append("-" * 80)
    report_lines.append("1. Run migration tool:")
    report_lines.append("   python scripts/migrate_imports.py --fix <path>")
    report_lines.append("")
    report_lines.append("2. Or manually update imports following the suggestions above")
    report_lines.append("")
    report_lines.append("3. See docs/DEPRECATION_PLAN.md for migration timeline")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan codebase for deprecated import patterns"
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=Path.cwd(),
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with code 1 if deprecated usage is found (useful for CI)'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Additional patterns to exclude from scanning'
    )
    
    args = parser.parse_args()
    
    # Scan directory
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.pytest_cache', 'build', 'dist', '*.egg-info',
            'src/pipeline/', 'MOD_ERROR_PIPELINE/'
        ] + args.exclude
    
    results = scan_directory(args.path, exclude_patterns)
    
    # Generate and print report
    output_format = 'json' if args.json else 'text'
    report = generate_report(results, output_format)
    print(report)
    
    # Exit with appropriate code
    if args.strict and results:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
