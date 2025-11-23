#!/usr/bin/env python3
"""
Documentation Orphan Checker
Finds documentation files outside governed directories
"""
import argparse
import sys
from pathlib import Path


GOVERNED_DIRS = {
    "docs/spec",
    "docs/planning",
    "docs/scratch",
    "docs/runtime",
    "docs/archive",
    "docs/ai"
}


def load_ignore_patterns(repo_root: Path) -> list[str]:
    """Load patterns from .docs_ignore file."""
    ignore_file = repo_root / ".docs_ignore"
    if not ignore_file.exists():
        return []
    
    patterns = []
    for line in ignore_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def should_ignore(path: Path, repo_root: Path, patterns: list[str]) -> bool:
    """Check if path matches any ignore pattern."""
    rel_path = path.relative_to(repo_root).as_posix()
    
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            if rel_path.startswith(prefix + "/") or rel_path == prefix:
                return True
        elif "*" in pattern:
            import fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        elif rel_path.startswith(pattern):
            return True
    
    return False


def is_in_governed_dir(path: Path, repo_root: Path) -> bool:
    """Check if path is within a governed directory."""
    rel_path = path.relative_to(repo_root).as_posix()
    
    for gov_dir in GOVERNED_DIRS:
        if rel_path.startswith(gov_dir + "/"):
            return True
    
    return False


def find_orphans(repo_root: Path, ignore_patterns: list[str]) -> list[Path]:
    """Find orphaned documentation files."""
    orphans = []
    
    for ext in ["*.md", "*.txt"]:
        for path in repo_root.rglob(ext):
            if should_ignore(path, repo_root, ignore_patterns):
                continue
            if not is_in_governed_dir(path, repo_root):
                orphans.append(path)
    
    return orphans


def main():
    parser = argparse.ArgumentParser(
        description="Check for orphaned documentation files"
    )
    parser.add_argument("--report-only", action="store_true",
                       help="Report orphans as warning (exit 0)")
    parser.add_argument("--strict", action="store_true",
                       help="Report orphans as error (exit 1)")
    
    args = parser.parse_args()
    
    repo_root = Path.cwd()
    ignore_patterns = load_ignore_patterns(repo_root)
    
    orphans = find_orphans(repo_root, ignore_patterns)
    
    if orphans:
        print(f"{'⚠️  WARNING' if args.report_only else '❌ ERROR'}: Found {len(orphans)} orphaned documentation files:")
        for orphan in orphans[:20]:  # Limit output
            print(f"  - {orphan.relative_to(repo_root)}")
        
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more")
        
        print(f"\nGoverned directories: {', '.join(GOVERNED_DIRS)}")
        
        return 0 if args.report_only else 1
    else:
        print("✅ No orphaned documentation files found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
