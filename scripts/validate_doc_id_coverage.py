#!/usr/bin/env python3
"""
DOC_ID Coverage Validator - CI/CD friendly

Validates doc_id coverage and detects regressions.
Exit code 0: Pass, Exit code 1: Fail

Usage:
    python scripts/validate_doc_id_coverage.py
    python scripts/validate_doc_id_coverage.py --baseline 0.92
    python scripts/validate_doc_id_coverage.py --report coverage_report.json
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timezone

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Doc ID pattern
DOC_ID_PATTERN = re.compile(r'DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-\d{3}')

# File types to scan
ELIGIBLE_EXTENSIONS = {
    '.py', '.md', '.yaml', '.yml', '.json', '.ps1', '.sh', '.txt'
}

# Directories to exclude
EXCLUDED_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv',
    '.pytest_cache', '.tox', 'dist', 'build', '.egg-info'
}


def should_scan_file(file_path: Path) -> bool:
    """Check if file should be scanned for doc_id"""
    # Check extension
    if file_path.suffix not in ELIGIBLE_EXTENSIONS:
        return False
    
    # Check if in excluded directory
    for part in file_path.parts:
        if part in EXCLUDED_DIRS:
            return False
    
    return True


def has_doc_id(file_path: Path) -> bool:
    """Check if file contains a doc_id"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return bool(DOC_ID_PATTERN.search(content))
    except Exception:
        return False


def scan_repository() -> Dict:
    """Scan repository and return coverage statistics"""
    eligible_files = []
    files_with_doc_id = []
    
    for file_path in REPO_ROOT.rglob('*'):
        if not file_path.is_file():
            continue
        
        if should_scan_file(file_path):
            rel_path = file_path.relative_to(REPO_ROOT)
            eligible_files.append(str(rel_path))
            
            if has_doc_id(file_path):
                files_with_doc_id.append(str(rel_path))
    
    total = len(eligible_files)
    with_id = len(files_with_doc_id)
    coverage = (with_id / total * 100) if total > 0 else 0
    
    return {
        'total_eligible': total,
        'with_doc_id': with_id,
        'without_doc_id': total - with_id,
        'coverage_percent': round(coverage, 2),
        'scanned_at': datetime.now(timezone.utc).isoformat(),
        'files_without_doc_id': sorted([f for f in eligible_files if f not in files_with_doc_id])
    }


def validate_coverage(baseline: float = 0.90) -> bool:
    """
    Validate coverage meets baseline.
    
    Args:
        baseline: Minimum acceptable coverage (0.0-1.0)
    
    Returns:
        True if coverage meets baseline, False otherwise
    """
    print("==> Scanning repository for doc_id coverage...")
    
    results = scan_repository()
    
    coverage = results['coverage_percent'] / 100
    total = results['total_eligible']
    with_id = results['with_doc_id']
    without_id = results['without_doc_id']
    
    print(f"\n==> Coverage Results:")
    print(f"   Total eligible files: {total}")
    print(f"   Files with doc_id:    {with_id} ({results['coverage_percent']}%)")
    print(f"   Files without doc_id: {without_id}")
    print(f"   Baseline required:    {baseline * 100}%")
    
    passed = coverage >= baseline
    
    if passed:
        print(f"\n✓ PASS: Coverage {results['coverage_percent']}% meets baseline {baseline * 100}%")
    else:
        print(f"\n✗ FAIL: Coverage {results['coverage_percent']}% below baseline {baseline * 100}%")
        
        if results['files_without_doc_id']:
            print(f"\n==> Files missing doc_id (first 10):")
            for file_path in results['files_without_doc_id'][:10]:
                print(f"   - {file_path}")
            
            if without_id > 10:
                print(f"   ... and {without_id - 10} more")
    
    return passed, results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate doc_id coverage')
    parser.add_argument('--baseline', type=float, default=0.90,
                        help='Minimum coverage required (default: 0.90)')
    parser.add_argument('--report', type=str,
                        help='Output JSON report to file')
    
    args = parser.parse_args()
    
    passed, results = validate_coverage(baseline=args.baseline)
    
    # Write report if requested
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n==> Report written to: {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
