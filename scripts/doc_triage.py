#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOC_TRIAGE - Repository Documentation Triage Tool

PURPOSE: Classify all Markdown docs and produce migration queue
PATTERN: PAT-DOCID-TRIAGE-001

USAGE:
    python scripts/doc_triage.py                    # Full repo scan
    python scripts/doc_triage.py --path modules/    # Scoped scan
    python scripts/doc_triage.py --report-only      # Summary only
"""

import sys
import io
from pathlib import Path
from typing import List, Dict, Set
import yaml
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

REPO_ROOT = Path(__file__).parent.parent

# Exclusion patterns
EXCLUDE_DIRS = {
    '.git', 'node_modules', '.venv', '__pycache__', 
    '.worktrees', '.pytest_cache', 'dist', 'build',
    'legacy'  # Per Phase 3 plan
}

# Valid locations for each doc class
DOC_LOCATIONS = {
    'DOC_': ['docs', 'modules'],
    'PLAN_': ['workstreams/plans', 'docs/plans'],
    '_DEV_': ['developer']
}


class DocTriageResult:
    """Classification result for a single document."""
    
    def __init__(self, path: Path, category: str, issue: str = None, suggestion: str = None):
        self.path = path
        self.category = category  # needs_move, needs_rename, needs_mint, needs_fix, ok
        self.issue = issue
        self.suggestion = suggestion


class DocTriage:
    """Triage all Markdown documentation in the repository."""
    
    def __init__(self, scan_path: Path = REPO_ROOT):
        self.scan_path = scan_path.resolve() if not scan_path.is_absolute() else scan_path
        self.results: List[DocTriageResult] = []
        
    def scan(self):
        """Scan all Markdown files."""
        for md_file in self._find_markdown_files():
            result = self._classify_file(md_file)
            if result:
                self.results.append(result)
    
    def _find_markdown_files(self) -> List[Path]:
        """Find all .md files, excluding specified directories."""
        md_files = []
        for md_file in self.scan_path.rglob('*.md'):
            # Check if any parent is in exclude list
            if any(excluded in md_file.parts for excluded in EXCLUDE_DIRS):
                continue
            md_files.append(md_file)
        return md_files
    
    def _classify_file(self, md_file: Path) -> DocTriageResult:
        """Classify a single Markdown file."""
        md_file = md_file.resolve()
        rel_path = md_file.relative_to(REPO_ROOT)
        filename = md_file.name
        
        # Check if it's a _DEV_ file
        if filename.startswith('_DEV_'):
            return self._check_dev_file(md_file, rel_path)
        
        # Check if it's a DOC_ file
        if filename.startswith('DOC_'):
            return self._check_doc_file(md_file, rel_path)
        
        # Check if it's a PLAN_ file
        if filename.startswith('PLAN_'):
            return self._check_plan_file(md_file, rel_path)
        
        # File in docs/** but not properly named
        if 'docs' in rel_path.parts or 'modules' in rel_path.parts:
            return DocTriageResult(
                md_file,
                'needs_rename',
                f"File in governed location but doesn't start with DOC_ or PLAN_",
                f"Rename to DOC_* or move to developer/ as _DEV_*"
            )
        
        # Everything else is likely scratch/temp
        return None
    
    def _check_dev_file(self, md_file: Path, rel_path: Path) -> DocTriageResult:
        """Check _DEV_ file placement."""
        if 'developer' not in rel_path.parts:
            return DocTriageResult(
                md_file,
                'needs_move',
                "_DEV_ file outside developer/ directory",
                f"Move to developer/"
            )
        return DocTriageResult(md_file, 'ok')
    
    def _check_doc_file(self, md_file: Path, rel_path: Path) -> DocTriageResult:
        """Check DOC_ file for proper location and front matter."""
        # Check location
        valid_location = any(loc in str(rel_path) for loc in ['docs', 'modules'])
        if not valid_location:
            return DocTriageResult(
                md_file,
                'needs_move',
                "DOC_ file not in docs/ or modules/",
                "Move to docs/ or appropriate module/"
            )
        
        # Check front matter
        front_matter = self._extract_front_matter(md_file)
        if not front_matter:
            return DocTriageResult(
                md_file,
                'needs_fix',
                "DOC_ file missing front matter",
                "Add YAML front matter with status: draft or status: canonical"
            )
        
        # Check if needs doc_id
        if 'doc_id' not in front_matter:
            status = front_matter.get('status', 'unknown')
            if status in ['canonical', 'draft']:
                return DocTriageResult(
                    md_file,
                    'needs_mint',
                    f"DOC_ file with status={status} but no doc_id",
                    "Add to batch spec for doc_id minting"
                )
        
        return DocTriageResult(md_file, 'ok')
    
    def _check_plan_file(self, md_file: Path, rel_path: Path) -> DocTriageResult:
        """Check PLAN_ file for proper location and front matter."""
        # Check location
        valid_location = 'plans' in str(rel_path) or 'workstreams' in str(rel_path)
        if not valid_location:
            return DocTriageResult(
                md_file,
                'needs_move',
                "PLAN_ file not in workstreams/plans/ or docs/plans/",
                "Move to workstreams/plans/"
            )
        
        # Check front matter
        front_matter = self._extract_front_matter(md_file)
        if not front_matter:
            return DocTriageResult(
                md_file,
                'needs_fix',
                "PLAN_ file missing front matter",
                "Add YAML front matter with status: draft"
            )
        
        # PLAN_ files only need doc_id when canonical
        status = front_matter.get('status', 'unknown')
        if status == 'canonical' and 'doc_id' not in front_matter:
            return DocTriageResult(
                md_file,
                'needs_mint',
                f"PLAN_ file with status=canonical but no doc_id",
                "Add to batch spec for doc_id minting"
            )
        
        return DocTriageResult(md_file, 'ok')
    
    def _extract_front_matter(self, md_file: Path) -> dict:
        """Extract YAML front matter from Markdown file."""
        try:
            content = md_file.read_text(encoding='utf-8')
            if not content.startswith('---'):
                return {}
            
            # Find second ---
            end_marker = content.find('---', 3)
            if end_marker == -1:
                return {}
            
            front_matter_text = content[3:end_marker].strip()
            return yaml.safe_load(front_matter_text) or {}
        except Exception as e:
            return {}
    
    def report(self, report_only: bool = False):
        """Generate triage report."""
        by_category = {}
        for result in self.results:
            category = result.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        print("=" * 80)
        print("DOC_TRIAGE REPORT - PAT-DOCID-TRIAGE-001")
        print("=" * 80)
        print()
        
        # Summary
        print(f"Total files scanned: {len(self.results)}")
        print(f"Files OK: {len(by_category.get('ok', []))}")
        print(f"Files needing action: {len(self.results) - len(by_category.get('ok', []))}")
        print()
        
        # Details by category
        for category in ['needs_move', 'needs_rename', 'needs_mint', 'needs_fix']:
            if category in by_category:
                files = by_category[category]
                print(f"\n## {category.upper().replace('_', ' ')} ({len(files)} files)")
                print("-" * 80)
                
                if not report_only:
                    for result in files:
                        rel_path = result.path.relative_to(REPO_ROOT)
                        print(f"\n  File: {rel_path}")
                        print(f"  Issue: {result.issue}")
                        print(f"  Suggestion: {result.suggestion}")
                else:
                    for result in files:
                        rel_path = result.path.relative_to(REPO_ROOT)
                        print(f"  - {rel_path}")
        
        print("\n" + "=" * 80)
        print("END TRIAGE REPORT")
        print("=" * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="DOC_TRIAGE - Classify repository documentation"
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=REPO_ROOT,
        help='Path to scan (default: repo root)'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Show summary only without detailed suggestions'
    )
    
    args = parser.parse_args()
    
    triage = DocTriage(scan_path=args.path)
    triage.scan()
    triage.report(report_only=args.report_only)


if __name__ == '__main__':
    main()
