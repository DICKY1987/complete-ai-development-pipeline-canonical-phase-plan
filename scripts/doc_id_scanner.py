#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-SCANNER-206
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-SCANNER-143
# -*- coding: utf-8 -*-
"""
Doc ID Scanner

PURPOSE:
    Scan repository for eligible files and detect which have doc_ids embedded.
    Generate docs_inventory.jsonl for tracking coverage.

PATTERN: PAT-DOC-ID-SCANNER-001

USAGE:
    python scripts/doc_id_scanner.py scan
    python scripts/doc_id_scanner.py stats
    python scripts/doc_id_scanner.py check <file_path>
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, List, Dict

# Repository root
REPO_ROOT = Path(__file__).parent.parent
INVENTORY_PATH = REPO_ROOT / "docs_inventory.jsonl"

# Doc ID pattern
DOC_ID_PATTERN = re.compile(r'DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-\d{3}')

# File types to scan
ELIGIBLE_EXTENSIONS = {
    '.py': 'py',
    '.md': 'md',
    '.yaml': 'yaml',
    '.yml': 'yml',
    '.json': 'json',
    '.ps1': 'ps1',
    '.sh': 'sh',
    '.txt': 'txt',
}

# Directories to exclude
EXCLUDED_DIRS = {
    '.git',
    '.github',
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    '.worktrees',
    'legacy',
    '.pytest_cache',
    '.mypy_cache',
    'dist',
    'build',
    'egg-info',
}


@dataclass
class FileEntry:
    """Represents a scanned file and its doc_id status."""
    path: str
    # DOC_ID: Optional[str]
    status: str  # 'present', 'missing'
    file_type: str
    last_modified: str
    scanned_at: str


class DocIDScanner:
    """Scan repository for files and detect doc_id presence."""
    
    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.inventory: List[FileEntry] = []
    
    def is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        parts = path.parts
        return any(excluded in parts for excluded in EXCLUDED_DIRS)
    
    def extract_doc_id(self, content: str, file_type: str) -> Optional[str]:
        """
        Extract doc_id from file content based on file type.
        
        Returns the first doc_id found, or None if not present.
        """
        # For all file types, search for DOC-* pattern
        matches = DOC_ID_PATTERN.findall(content)
        if matches:
            return matches[0]
        
        return None
    
    def scan_file(self, file_path: Path) -> Optional[FileEntry]:
        """
        Scan a single file for doc_id.
        
        Returns FileEntry or None if file should be skipped.
        """
        # Get relative path
        try:
            rel_path = file_path.relative_to(self.repo_root)
        except ValueError:
            return None
        
        # Check extension
        ext = file_path.suffix.lower()
        if ext not in ELIGIBLE_EXTENSIONS:
            return None
        
        file_type = ELIGIBLE_EXTENSIONS[ext]
        
        # Read file
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"[WARN] Could not read {rel_path}: {e}", file=sys.stderr)
            return None
        
        # Extract doc_id
        doc_id = self.extract_doc_id(content, file_type)
        
        # Get last modified time
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            last_modified = mtime.isoformat()
        except Exception:
            last_modified = ""
        
        status = "present" if doc_id else "missing"
        scanned_at = datetime.now().isoformat()
        
        return FileEntry(
            path=str(rel_path).replace('\\', '/'),
            doc_id=doc_id,
            status=status,
            file_type=file_type,
            last_modified=last_modified,
            scanned_at=scanned_at,
        )
    
    def scan_repository(self) -> List[FileEntry]:
        """
        Scan entire repository for eligible files.
        
        Returns list of FileEntry objects.
        """
        print(f"[INFO] Scanning repository: {self.repo_root}")
        
        entries: List[FileEntry] = []
        total_files = 0
        skipped_files = 0
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            total_files += 1
            
            # Skip excluded directories
            if self.is_excluded(file_path):
                skipped_files += 1
                continue
            
            entry = self.scan_file(file_path)
            if entry:
                entries.append(entry)
            
            if total_files % 100 == 0:
                print(f"[INFO] Scanned {total_files} files, found {len(entries)} eligible...", 
                      end='\r', file=sys.stderr)
        
        print(f"\n[INFO] Scan complete: {total_files} total files, {len(entries)} eligible, "
              f"{skipped_files} skipped")
        
        return entries
    
    def save_inventory(self, entries: List[FileEntry], output_path: Path = INVENTORY_PATH):
        """Save inventory to JSONL file."""
        with output_path.open('w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(asdict(entry)) + '\n')
        
        print(f"[OK] Inventory saved: {output_path}")
        print(f"[OK] Total entries: {len(entries)}")
    
    def load_inventory(self, input_path: Path = INVENTORY_PATH) -> List[FileEntry]:
        """Load inventory from JSONL file."""
        if not input_path.exists():
            print(f"[ERROR] Inventory file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        
        entries: List[FileEntry] = []
        with input_path.open('r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(FileEntry(**data))
                except Exception as e:
                    print(f"[WARN] Line {line_num}: {e}", file=sys.stderr)
        
        return entries
    
    def print_stats(self, entries: List[FileEntry]):
        """Print statistics about doc_id coverage."""
        total = len(entries)
        present = sum(1 for e in entries if e.status == "present")
        missing = sum(1 for e in entries if e.status == "missing")
        
        coverage_pct = (present / total * 100) if total > 0 else 0
        
        # Count by file type
        type_counts: Dict[str, Dict[str, int]] = {}
        for entry in entries:
            ft = entry.file_type
            if ft not in type_counts:
                type_counts[ft] = {'present': 0, 'missing': 0}
            type_counts[ft][entry.status] += 1
        
        print("\n" + "=" * 70)
        print("DOC_ID COVERAGE STATISTICS")
        print("=" * 70)
        print(f"Total eligible files:    {total:6}")
        print(f"Files with doc_id:       {present:6} ({coverage_pct:5.1f}%)")
        print(f"Files missing doc_id:    {missing:6} ({100-coverage_pct:5.1f}%)")
        print()
        print("By file type:")
        print("-" * 70)
        print(f"{'Type':<10} {'Total':>8} {'Present':>10} {'Missing':>10} {'Coverage':>10}")
        print("-" * 70)
        
        for file_type in sorted(type_counts.keys()):
            counts = type_counts[file_type]
            total_type = counts['present'] + counts['missing']
            pct = (counts['present'] / total_type * 100) if total_type > 0 else 0
            print(f"{file_type:<10} {total_type:8} {counts['present']:10} "
                  f"{counts['missing']:10} {pct:9.1f}%")
        
        print("=" * 70)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scan repository for doc_id coverage"
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # Scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan repository and update inventory"
    )
    scan_parser.add_argument(
        "--output",
        type=Path,
        default=INVENTORY_PATH,
        help="Output inventory file path"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show statistics from inventory"
    )
    stats_parser.add_argument(
        "--input",
        type=Path,
        default=INVENTORY_PATH,
        help="Input inventory file path"
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check a specific file for doc_id"
    )
    check_parser.add_argument(
        "file_path",
        type=Path,
        help="Path to file to check"
    )
    
    args = parser.parse_args()
    
    scanner = DocIDScanner()
    
    if args.command == "scan":
        entries = scanner.scan_repository()
        scanner.save_inventory(entries, args.output)
        scanner.print_stats(entries)
        return 0
    
    elif args.command == "stats":
        entries = scanner.load_inventory(args.input)
        scanner.print_stats(entries)
        return 0
    
    elif args.command == "check":
        file_path = args.file_path
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}", file=sys.stderr)
            return 1
        
        entry = scanner.scan_file(file_path)
        if not entry:
            print(f"[INFO] File type not eligible or could not be scanned")
            return 1
        
        print(f"Path:          {entry.path}")
        print(f"File type:     {entry.file_type}")
        print(f"Status:        {entry.status}")
        print(f"Doc ID:        {entry.doc_id or '(none)'}")
        print(f"Last modified: {entry.last_modified}")
        
        return 0 if entry.status == "present" else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
