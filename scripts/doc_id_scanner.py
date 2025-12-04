#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DOC_LINK: DOC-SCRIPT-DOC-ID-SCANNER-046
"""
Doc ID Scanner

PURPOSE: Scan repository for doc_id presence and generate inventory
PATTERN: PAT-DOC-ID-SCAN-001

USAGE:
    python scripts/doc_id_scanner.py scan
    python scripts/doc_id_scanner.py stats
    python scripts/doc_id_scanner.py report --format markdown
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Repository root
REPO_ROOT = Path(__file__).parent.parent
INVENTORY_PATH = REPO_ROOT / "docs_inventory.jsonl"

# Doc ID regex
DOC_ID_REGEX = re.compile(r"^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$")

# Eligible file patterns (glob)
ELIGIBLE_PATTERNS = [
    "**/*.py",
    "**/*.md",
    "**/*.yaml",
    "**/*.yml",
    "**/*.json",
    "**/*.ps1",
    "**/*.sh",
    "**/*.txt",
]

# Exclude patterns
EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".worktrees",
    "legacy",
    ".state",
    "refactor_paths.db",
    "*.db-shm",
    "*.db-wal",
]


class DocIDScanner:
    """Scan repository for doc_id presence."""

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.inventory: List[Dict] = []

    def is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded."""
        path_str = str(path.relative_to(self.repo_root))

        for pattern in EXCLUDE_PATTERNS:
            if pattern in path_str:
                return True

        return False

    def extract_doc_id_python(self, content: str) -> Optional[str]:
        """Extract doc_id from Python file."""
        # Look for DOC_ID: or DOC_LINK: in first 50 lines
        lines = content.split('\n')[:50]

        for line in lines:
            # Module docstring: DOC_ID: DOC-...
            match = re.search(r'DOC_ID:\s*(DOC-[A-Z0-9-]+)', line)
            if match:
                return match.group(1)

            # Test header: # DOC_LINK: DOC-...
            match = re.search(r'DOC_LINK:\s*(DOC-[A-Z0-9-]+)', line)
            if match:
                return match.group(1)

        return None

    def extract_doc_id_markdown(self, content: str) -> Optional[str]:
        """Extract doc_id from Markdown YAML frontmatter."""
        # Look for YAML frontmatter
        if not content.startswith('---'):
            return None

        # Find closing ---
        lines = content.split('\n')
        if len(lines) < 3:
            return None

        frontmatter_end = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if not frontmatter_end:
            return None

        # Parse frontmatter
        frontmatter = '\n'.join(lines[1:frontmatter_end])
        match = re.search(r'doc_id:\s*["\']?(DOC-[A-Z0-9-]+)["\']?', frontmatter)
        if match:
            return match.group(1)

        return None

    def extract_doc_id_yaml(self, content: str) -> Optional[str]:
        """Extract doc_id from YAML file."""
        # Look for top-level doc_id field
        lines = content.split('\n')[:20]

        for line in lines:
            match = re.search(r'^doc_id:\s*["\']?(DOC-[A-Z0-9-]+)["\']?', line)
            if match:
                return match.group(1)

        return None

    def extract_doc_id_json(self, content: str) -> Optional[str]:
        """Extract doc_id from JSON file."""
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'doc_id' in data:
                return data['doc_id']
        except json.JSONDecodeError:
            pass

        return None

    def extract_doc_id_script(self, content: str) -> Optional[str]:
        """Extract doc_id from script file (PowerShell, Bash)."""
        # Look for # DOC_LINK: in first 20 lines
        lines = content.split('\n')[:20]

        for line in lines:
            match = re.search(r'DOC_LINK:\s*(DOC-[A-Z0-9-]+)', line)
            if match:
                return match.group(1)

        return None

    def extract_doc_id(self, file_path: Path) -> Optional[str]:
        """Extract doc_id from file based on type."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"[WARN] Could not read {file_path}: {e}")
            return None

        suffix = file_path.suffix.lower()

        if suffix == '.py':
            return self.extract_doc_id_python(content)
        elif suffix == '.md':
            return self.extract_doc_id_markdown(content)
        elif suffix in ['.yaml', '.yml']:
            return self.extract_doc_id_yaml(content)
        elif suffix == '.json':
            return self.extract_doc_id_json(content)
        elif suffix in ['.ps1', '.sh']:
            return self.extract_doc_id_script(content)
        elif suffix == '.txt':
            # Try markdown frontmatter first, then YAML
            doc_id = self.extract_doc_id_markdown(content)
            if doc_id:
                return doc_id
            return self.extract_doc_id_yaml(content)

        return None

    def validate_doc_id(self, doc_id: str) -> bool:
        """Validate doc_id format."""
        if not doc_id:
            return False
        return bool(DOC_ID_REGEX.match(doc_id))

    def scan_file(self, file_path: Path) -> Dict:
        """Scan a single file for doc_id."""
        rel_path = file_path.relative_to(self.repo_root)

        doc_id = self.extract_doc_id(file_path)

        if doc_id:
            valid = self.validate_doc_id(doc_id)
            status = "registered" if valid else "invalid"
        else:
            valid = False
            status = "missing"

        return {
            "path": str(rel_path).replace('\\', '/'),
            "doc_id": doc_id,
            "status": status,
            "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "scanned_at": datetime.now().isoformat(),
        }

    def scan_repository(self) -> List[Dict]:
        """Scan entire repository for eligible files."""
        print(f"[INFO] Scanning repository: {self.repo_root}")

        eligible_files = []

        # Collect all eligible files
        for pattern in ELIGIBLE_PATTERNS:
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file() and not self.is_excluded(file_path):
                    eligible_files.append(file_path)

        print(f"[INFO] Found {len(eligible_files)} eligible files")

        # Scan each file
        self.inventory = []
        for i, file_path in enumerate(eligible_files, start=1):
            if i % 50 == 0:
                print(f"[INFO] Scanned {i}/{len(eligible_files)} files...")

            entry = self.scan_file(file_path)
            self.inventory.append(entry)

        print(f"[INFO] Scan complete: {len(self.inventory)} files")

        return self.inventory

    def save_inventory(self, output_path: Path = INVENTORY_PATH):
        """Save inventory to JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in self.inventory:
                f.write(json.dumps(entry) + '\n')

        print(f"[OK] Inventory saved: {output_path}")

    def load_inventory(self, input_path: Path = INVENTORY_PATH) -> List[Dict]:
        """Load inventory from JSONL file."""
        if not input_path.exists():
            print(f"[ERROR] Inventory not found: {input_path}")
            sys.exit(1)

        self.inventory = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.inventory.append(json.loads(line))

        print(f"[INFO] Loaded {len(self.inventory)} entries from {input_path}")
        return self.inventory

    def get_stats(self) -> Dict:
        """Calculate statistics from inventory."""
        total = len(self.inventory)

        if total == 0:
            return {
                "total": 0,
                "with_id": 0,
                "without_id": 0,
                "invalid": 0,
                "coverage": 0.0,
            }

        with_id = len([e for e in self.inventory if e['status'] == 'registered'])
        invalid = len([e for e in self.inventory if e['status'] == 'invalid'])
        without_id = len([e for e in self.inventory if e['status'] == 'missing'])

        # Stats by file type
        by_type = {}
        for entry in self.inventory:
            ft = entry['file_type']
            if ft not in by_type:
                by_type[ft] = {"total": 0, "with_id": 0, "without_id": 0}

            by_type[ft]['total'] += 1
            if entry['status'] == 'registered':
                by_type[ft]['with_id'] += 1
            elif entry['status'] == 'missing':
                by_type[ft]['without_id'] += 1

        return {
            "total": total,
            "with_id": with_id,
            "without_id": without_id,
            "invalid": invalid,
            "coverage": with_id / total if total > 0 else 0.0,
            "by_type": by_type,
        }

    def print_stats(self):
        """Print statistics to console."""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("DOC_ID COVERAGE STATISTICS")
        print("="*60)
        print(f"Total eligible files:    {stats['total']}")
        print(f"Files with doc_id:       {stats['with_id']} ({stats['coverage']:.1%})")
        print(f"Files without doc_id:    {stats['without_id']}")
        print(f"Files with invalid ID:   {stats['invalid']}")
        print(f"\nCoverage: {stats['coverage']:.1%}")

        print("\nBy file type:")
        print("-" * 60)
        for ft, counts in sorted(stats['by_type'].items()):
            cov = counts['with_id'] / counts['total'] if counts['total'] > 0 else 0.0
            print(f"  {ft:10s}  {counts['with_id']:3d} / {counts['total']:3d}  ({cov:6.1%})")
        print("="*60 + "\n")

    def generate_markdown_report(self) -> str:
        """Generate Markdown coverage report."""
        stats = self.get_stats()

        report = f"""# Doc ID Coverage Report
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Inventory**: {INVENTORY_PATH.relative_to(REPO_ROOT)}

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Files** | {stats['total']} |
| **With doc_id** | {stats['with_id']} ({stats['coverage']:.1%}) |
| **Without doc_id** | {stats['without_id']} |
| **Invalid doc_id** | {stats['invalid']} |
| **Coverage** | **{stats['coverage']:.1%}** |

---

## Coverage by File Type

| File Type | With ID | Total | Coverage |
|-----------|---------|-------|----------|
"""

        for ft, counts in sorted(stats['by_type'].items(), key=lambda x: x[1]['total'], reverse=True):
            cov = counts['with_id'] / counts['total'] if counts['total'] > 0 else 0.0
            report += f"| {ft} | {counts['with_id']} | {counts['total']} | {cov:.1%} |\n"

        # Files without doc_id
        missing = [e for e in self.inventory if e['status'] == 'missing']

        if missing:
            report += f"\n---\n\n## Files Without doc_id ({len(missing)})\n\n"

            # Group by file type
            missing_by_type = {}
            for entry in missing:
                ft = entry['file_type']
                if ft not in missing_by_type:
                    missing_by_type[ft] = []
                missing_by_type[ft].append(entry['path'])

            for ft, paths in sorted(missing_by_type.items()):
                report += f"\n### {ft.upper()} Files ({len(paths)})\n\n"
                for path in sorted(paths)[:20]:  # Show first 20
                    report += f"- `{path}`\n"

                if len(paths) > 20:
                    report += f"\n_... and {len(paths) - 20} more_\n"

        # Invalid doc_ids
        invalid = [e for e in self.inventory if e['status'] == 'invalid']

        if invalid:
            report += f"\n---\n\n## Files with Invalid doc_id ({len(invalid)})\n\n"
            for entry in invalid:
                report += f"- `{entry['path']}`: `{entry['doc_id']}`\n"

        report += "\n---\n\n**Next Steps:**\n"
        if stats['without_id'] > 0:
            report += f"1. Run auto-assigner: `python scripts/doc_id_assigner.py auto-assign --dry-run`\n"
            report += f"2. Review proposed changes\n"
            report += f"3. Execute: `python scripts/doc_id_assigner.py auto-assign`\n"
        else:
            report += "✅ **100% coverage achieved!**\n"

        return report


def main():
    parser = argparse.ArgumentParser(description="Scan repository for doc_id presence")
    parser.add_argument(
        "command",
        choices=["scan", "stats", "report"],
        help="Command to execute"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INVENTORY_PATH,
        help="Output path for inventory (default: docs_inventory.jsonl)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format (default: markdown)"
    )

    args = parser.parse_args()

    scanner = DocIDScanner()

    if args.command == "scan":
        # Scan repository
        scanner.scan_repository()
        scanner.save_inventory(args.output)
        scanner.print_stats()

    elif args.command == "stats":
        # Load inventory and show stats
        scanner.load_inventory(args.output)
        scanner.print_stats()

    elif args.command == "report":
        # Generate report
        scanner.load_inventory(args.output)

        if args.format == "markdown":
            report = scanner.generate_markdown_report()
            report_path = REPO_ROOT / "DOC_ID_COVERAGE_REPORT.md"
            report_path.write_text(report, encoding='utf-8')
            print(f"[OK] Report saved: {report_path}")

        elif args.format == "json":
            stats = scanner.get_stats()
            print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
