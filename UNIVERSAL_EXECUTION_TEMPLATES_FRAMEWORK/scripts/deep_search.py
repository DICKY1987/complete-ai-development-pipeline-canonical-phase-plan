#!/usr/bin/env python3
"""
Deep Directory Search Tool
Implements PAT-SEARCH-001: Recursive directory search

Usage:
    python scripts/deep_search.py --ext .patch                    # Find by extension
    python scripts/deep_search.py --ext .patch .diff .txt         # Multiple extensions
    python scripts/deep_search.py --pattern "*config*"            # Pattern matching
    python scripts/deep_search.py --content "TODO" --ext .py      # Search file contents
    python scripts/deep_search.py --max-depth 3                   # Limit depth
    python scripts/deep_search.py --min-size 1048576              # Files > 1MB
    python scripts/deep_search.py --modified-days 7               # Modified in last 7 days
    python scripts/deep_search.py --json                          # JSON output
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Callable
import fnmatch


class DeepSearch:
    """Recursive directory search with multiple filter options."""
    
    SKIP_DIRS = {
        '.git', '.venv', '__pycache__', 'node_modules',
        '.pytest_cache', '.mypy_cache', 'build', 'dist',
        '.worktrees', '.state', '.tox'
    }
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
    
    def search(
        self,
        pattern: str = "*",
        max_depth: Optional[int] = None,
        filter_func: Optional[Callable] = None,
        follow_symlinks: bool = False,
        skip_hidden: bool = True
    ) -> List[Path]:
        """
        Recursively search directory tree for matching files.
        
        Args:
            pattern: Glob pattern (e.g., "*.patch", "*test*")
            max_depth: Maximum recursion depth (None = unlimited)
            filter_func: Optional custom filter function
            follow_symlinks: Whether to follow symbolic links
            skip_hidden: Skip hidden files/directories
        
        Returns:
            List of Path objects matching criteria
        """
        results = []
        
        def search_recursive(current_path: Path, depth: int = 0):
            if max_depth is not None and depth > max_depth:
                return
            
            try:
                for item in current_path.iterdir():
                    # Skip hidden files if requested
                    if skip_hidden and item.name.startswith('.'):
                        continue
                    
                    # Skip common directories
                    if item.name in self.SKIP_DIRS:
                        continue
                    
                    # Skip symlinks unless explicitly requested
                    if item.is_symlink() and not follow_symlinks:
                        continue
                    
                    # If it's a directory, recurse
                    if item.is_dir():
                        search_recursive(item, depth + 1)
                    
                    # If it's a file, check if it matches
                    elif item.is_file():
                        if fnmatch.fnmatch(item.name, pattern):
                            if filter_func is None or filter_func(item):
                                results.append(item)
            
            except PermissionError:
                pass  # Skip directories we can't access
            except Exception as e:
                print(f"Warning: Error accessing {current_path}: {e}", file=sys.stderr)
        
        search_recursive(self.root_dir)
        return sorted(results)
    
    def find_by_extension(self, extension: str, **kwargs) -> List[Path]:
        """Find all files with specific extension."""
        pattern = f"*.{extension.lstrip('.')}"
        return self.search(pattern, **kwargs)
    
    def find_by_extensions(self, extensions: List[str], **kwargs) -> List[Path]:
        """Find files matching any of the given extensions."""
        results = []
        for ext in extensions:
            results.extend(self.find_by_extension(ext, **kwargs))
        return sorted(set(results))  # Remove duplicates
    
    def find_by_content(
        self,
        search_text: str,
        file_pattern: str = "*",
        case_sensitive: bool = False,
        **kwargs
    ) -> List[tuple]:
        """
        Find files containing specific text.
        
        Returns:
            List of (file_path, line_number, line_text) tuples
        """
        matches = []
        files = self.search(file_pattern, **kwargs)
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line_to_check = line if case_sensitive else line.lower()
                        text_to_find = search_text if case_sensitive else search_text.lower()
                        
                        if text_to_find in line_to_check:
                            matches.append((file_path, line_num, line.rstrip()))
            except Exception:
                pass  # Skip files we can't read
        
        return matches
    
    def find_by_size(
        self,
        pattern: str = "*",
        min_size: int = 0,
        max_size: int = float('inf'),
        **kwargs
    ) -> List[tuple]:
        """
        Find files within size range.
        
        Returns:
            List of (file_path, size_bytes) tuples
        """
        def size_filter(path: Path) -> bool:
            try:
                size = path.stat().st_size
                return min_size <= size <= max_size
            except Exception:
                return False
        
        files = self.search(pattern, filter_func=size_filter, **kwargs)
        return [(f, f.stat().st_size) for f in files]
    
    def find_modified_since(
        self,
        days_ago: int,
        pattern: str = "*",
        **kwargs
    ) -> List[tuple]:
        """Find files modified within last N days."""
        cutoff_time = datetime.now() - timedelta(days=days_ago)
        
        def date_filter(path: Path) -> bool:
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                return mtime >= cutoff_time
            except Exception:
                return False
        
        files = self.search(pattern, filter_func=date_filter, **kwargs)
        return [(f, datetime.fromtimestamp(f.stat().st_mtime)) for f in files]


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Deep Directory Search (PAT-SEARCH-001)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Search criteria
    parser.add_argument(
        "--ext",
        nargs="+",
        metavar="EXT",
        help="File extension(s) to search for (e.g., .patch .diff)"
    )
    parser.add_argument(
        "--pattern",
        metavar="PATTERN",
        help="Glob pattern to match (e.g., '*config*')"
    )
    parser.add_argument(
        "--content",
        metavar="TEXT",
        help="Search for files containing specific text"
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Case-sensitive content search"
    )
    
    # Filters
    parser.add_argument(
        "--min-size",
        type=int,
        metavar="BYTES",
        help="Minimum file size in bytes"
    )
    parser.add_argument(
        "--max-size",
        type=int,
        metavar="BYTES",
        help="Maximum file size in bytes"
    )
    parser.add_argument(
        "--modified-days",
        type=int,
        metavar="DAYS",
        help="Files modified within last N days"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        metavar="N",
        help="Maximum directory depth to search"
    )
    
    # Options
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to search (default: current directory)"
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed file information"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.ext, args.pattern, args.content, args.min_size, args.modified_days]):
        parser.error("Must specify at least one search criterion")
    
    searcher = DeepSearch(args.root)
    
    # Determine search pattern
    if args.ext:
        results = searcher.find_by_extensions(
            args.ext,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            skip_hidden=not args.include_hidden
        )
        
        # Apply additional filters
        if args.min_size or args.max_size:
            min_s = args.min_size or 0
            max_s = args.max_size or float('inf')
            results = [r for r in results if min_s <= r.stat().st_size <= max_s]
        
        if args.modified_days:
            cutoff = datetime.now() - timedelta(days=args.modified_days)
            results = [
                r for r in results
                if datetime.fromtimestamp(r.stat().st_mtime) >= cutoff
            ]
    
    elif args.pattern:
        results = searcher.search(
            args.pattern,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            skip_hidden=not args.include_hidden
        )
    
    elif args.content:
        pattern = f"*.{args.ext[0].lstrip('.')}" if args.ext else "*"
        content_results = searcher.find_by_content(
            args.content,
            pattern,
            case_sensitive=args.case_sensitive,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            skip_hidden=not args.include_hidden
        )
        
        # Output content search results
        if args.json:
            output = {
                "search_text": args.content,
                "case_sensitive": args.case_sensitive,
                "results": [
                    {
                        "file": str(path.relative_to(searcher.root_dir)),
                        "line_number": line_num,
                        "line_text": text
                    }
                    for path, line_num, text in content_results
                ],
                "total_matches": len(content_results)
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nFound {len(content_results)} matches for '{args.content}':\n")
            for path, line_num, text in content_results:
                rel_path = path.relative_to(searcher.root_dir)
                print(f"{rel_path}:{line_num}  {text}")
        
        return
    
    elif args.min_size or args.max_size:
        results = searcher.find_by_size(
            min_size=args.min_size or 0,
            max_size=args.max_size or float('inf'),
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            skip_hidden=not args.include_hidden
        )
        results = [r[0] for r in results]  # Extract just paths
    
    elif args.modified_days:
        results = searcher.find_modified_since(
            args.modified_days,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            skip_hidden=not args.include_hidden
        )
        results = [r[0] for r in results]  # Extract just paths
    
    # Output results
    if args.json:
        output = {
            "search_criteria": {
                "root_dir": str(searcher.root_dir),
                "extensions": args.ext,
                "pattern": args.pattern,
                "max_depth": args.max_depth
            },
            "results": [
                {
                    "path": str(path.relative_to(searcher.root_dir)),
                    "absolute_path": str(path),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                for path in results
            ],
            "total_found": len(results)
        }
        print(json.dumps(output, indent=2))
    
    elif args.detailed:
        print(f"\nFound {len(results)} files:\n")
        for path in results:
            rel_path = path.relative_to(searcher.root_dir)
            stat = path.stat()
            size = format_size(stat.st_size)
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"📄 {rel_path}")
            print(f"   Size: {size}")
            print(f"   Modified: {mtime}\n")
    
    else:
        # Simple list output
        if not results:
            print("No files found matching criteria")
        else:
            print(f"\nFound {len(results)} files:\n")
            for path in results:
                rel_path = path.relative_to(searcher.root_dir)
                print(rel_path)


if __name__ == "__main__":
    main()
