---
doc_id: DOC-PAT-PAT-SEARCH-001-DEEP-DIRECTORY-SEARCH-866
---

# PAT-SEARCH-001: Deep Directory Search

## Pattern ID
**PAT-SEARCH-001**

## Pattern Name
Recursive Deep Directory Search

## Category
Utilities / File Management

## Intent
Recursively search through all subdirectories (including nested sub-subdirectories) to find files matching specific criteria, regardless of depth.

## Problem
- Files may be buried in deeply nested subdirectory structures
- Standard search only looks at immediate subdirectories
- Need to find all files of a certain type across entire directory tree
- Manual navigation through nested folders is time-consuming and error-prone

## Solution
Implement recursive directory traversal that:
1. **Searches all levels** - No depth limit
2. **Filters by criteria** - File extensions, patterns, content
3. **Returns full paths** - Absolute or relative paths
4. **Handles errors** - Skip inaccessible directories gracefully

## Structure

### Search Types
```
1. By Extension:     *.patch, *.py, *.md
2. By Pattern:       *test*, *config*, patch-*
3. By Content:       Files containing specific text
4. By Attributes:    Size, date, permissions
```

## Implementation

### Core Search Function
```python
from pathlib import Path
from typing import List, Callable, Optional
import fnmatch

def deep_search(
    root_dir: str,
    pattern: str = "*",
    max_depth: Optional[int] = None,
    filter_func: Optional[Callable] = None,
    follow_symlinks: bool = False
) -> List[Path]:
    """
    Recursively search directory tree for matching files.

    Args:
        root_dir: Starting directory for search
        pattern: Glob pattern (e.g., "*.patch", "*test*")
        max_depth: Maximum recursion depth (None = unlimited)
        filter_func: Optional custom filter function
        follow_symlinks: Whether to follow symbolic links

    Returns:
        List of Path objects matching criteria
    """
    results = []
    root = Path(root_dir)

    def search_recursive(current_path: Path, depth: int = 0):
        if max_depth is not None and depth > max_depth:
            return

        try:
            for item in current_path.iterdir():
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
            # Skip directories we can't access
            pass
        except Exception as e:
            # Log other errors but continue
            print(f"Warning: Error accessing {current_path}: {e}")

    search_recursive(root)
    return sorted(results)
```

### Search by Extension
```python
def find_by_extension(root_dir: str, extension: str) -> List[Path]:
    """Find all files with specific extension."""
    pattern = f"*.{extension.lstrip('.')}"
    return deep_search(root_dir, pattern)
```

### Search by Multiple Extensions
```python
def find_by_extensions(root_dir: str, extensions: List[str]) -> List[Path]:
    """Find files matching any of the given extensions."""
    results = []
    for ext in extensions:
        results.extend(find_by_extension(root_dir, ext))
    return sorted(set(results))  # Remove duplicates
```

### Search by Content
```python
def find_by_content(
    root_dir: str,
    search_text: str,
    file_pattern: str = "*",
    case_sensitive: bool = False
) -> List[tuple[Path, int]]:
    """
    Find files containing specific text.

    Returns:
        List of (file_path, line_number) tuples
    """
    matches = []
    files = deep_search(root_dir, file_pattern)

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_to_check = line if case_sensitive else line.lower()
                    text_to_find = search_text if case_sensitive else search_text.lower()

                    if text_to_find in line_to_check:
                        matches.append((file_path, line_num))
        except Exception:
            # Skip files we can't read
            pass

    return matches
```

### Search with Size Filter
```python
def find_by_size(
    root_dir: str,
    min_size: int = 0,
    max_size: int = float('inf'),
    pattern: str = "*"
) -> List[tuple[Path, int]]:
    """
    Find files within size range.

    Args:
        min_size: Minimum size in bytes
        max_size: Maximum size in bytes

    Returns:
        List of (file_path, size_bytes) tuples
    """
    def size_filter(path: Path) -> bool:
        size = path.stat().st_size
        return min_size <= size <= max_size

    files = deep_search(root_dir, pattern, filter_func=size_filter)
    return [(f, f.stat().st_size) for f in files]
```

### Search with Date Filter
```python
from datetime import datetime, timedelta

def find_modified_since(
    root_dir: str,
    days_ago: int,
    pattern: str = "*"
) -> List[tuple[Path, datetime]]:
    """Find files modified within last N days."""
    cutoff_time = datetime.now() - timedelta(days=days_ago)

    def date_filter(path: Path) -> bool:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        return mtime >= cutoff_time

    files = deep_search(root_dir, pattern, filter_func=date_filter)
    return [(f, datetime.fromtimestamp(f.stat().st_mtime)) for f in files]
```

## Usage

### CLI Tool
```bash
# Find all .patch files recursively
python scripts/deep_search.py --ext .patch

# Find multiple extensions
python scripts/deep_search.py --ext .patch .diff .txt

# Find by pattern
python scripts/deep_search.py --pattern "*config*"

# Find by content
python scripts/deep_search.py --content "TODO" --ext .py

# Limit search depth
python scripts/deep_search.py --ext .md --max-depth 3

# Find large files
python scripts/deep_search.py --min-size 1048576  # > 1MB

# Find recently modified
python scripts/deep_search.py --modified-days 7 --ext .py
```

### Python API
```python
from scripts.deep_search import DeepSearch

# Initialize searcher
searcher = DeepSearch(".")

# Find patch files
patches = searcher.find_by_extension(".patch")
for patch in patches:
    print(f"Found: {patch}")

# Find files by multiple criteria
results = searcher.find_by_extensions([".patch", ".diff"])

# Search with custom filter
def is_large_file(path):
    return path.stat().st_size > 1024 * 1024

large_files = searcher.search("*", filter_func=is_large_file)

# Search by content
matches = searcher.find_by_content("FIXME", "*.py")
for file_path, line_num in matches:
    print(f"{file_path}:{line_num}")
```

## Output Formats

### Simple List
```
patches/001-config.patch
patches/archive/2025-11-24/002-fix.patch
subdir/nested/003-update.patch
```

### Detailed View
```
Found 3 files:

📄 patches/001-config.patch
   Size: 2.4 KB
   Modified: 2025-11-24 10:30:15

📄 patches/archive/2025-11-24/002-fix.patch
   Size: 1.8 KB
   Modified: 2025-11-23 14:22:08

📄 subdir/nested/003-update.patch
   Size: 512 B
   Modified: 2025-11-24 09:15:42
```

### JSON Output
```json
{
  "search_criteria": {
    "root_dir": ".",
    "pattern": "*.patch",
    "max_depth": null
  },
  "results": [
    {
      "path": "patches/001-config.patch",
      "size": 2456,
      "modified": "2025-11-24T10:30:15",
      "relative_path": "patches/001-config.patch"
    }
  ],
  "total_found": 1
}
```

## Common Use Cases

### 1. Find All Patches Anywhere
```python
patches = deep_search(".", "*.patch")
print(f"Found {len(patches)} patch files")
```

### 2. Find Configuration Files
```python
configs = deep_search(".", "*config*")
```

### 3. Find Large Files
```python
large_files = find_by_size(".", min_size=10*1024*1024)  # > 10MB
```

### 4. Find Recent Changes
```python
recent = find_modified_since(".", days_ago=7)
```

### 5. Find TODOs in Code
```python
todos = find_by_content(".", "TODO", "*.py")
```

## Integration with Patch Manager

### Enhanced Patch Discovery
```python
class PatchManager:
    def discover_all_patches(self) -> List[Path]:
        """Find patches anywhere in directory tree."""
        return deep_search(self.repo_path, "*.patch")

    def process_discovered_patches(self):
        """Process all patches found recursively."""
        all_patches = self.discover_all_patches()

        for patch in all_patches:
            print(f"\nFound patch: {patch.relative_to(self.repo_path)}")

            if self.is_patch_applied(patch):
                print("  Already applied - archiving")
                self.archive_patch(patch)
            else:
                print("  Not applied - attempting to apply")
                result = self.apply_patch(patch)
                if result["success"]:
                    self.archive_patch(patch)
```

## Performance Optimization

### Skip Common Directories
```python
SKIP_DIRS = {
    '.git', '.venv', '__pycache__', 'node_modules',
    '.pytest_cache', '.mypy_cache', 'build', 'dist'
}

def optimized_search(root_dir: str, pattern: str) -> List[Path]:
    """Search with common exclusions."""
    def should_skip(path: Path) -> bool:
        return path.name in SKIP_DIRS

    results = []
    for path in Path(root_dir).rglob(pattern):
        # Check if any parent is in skip list
        if not any(p.name in SKIP_DIRS for p in path.parents):
            results.append(path)

    return results
```

### Parallel Search (for large directories)
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_search(root_dir: str, pattern: str, workers: int = 4) -> List[Path]:
    """Search using multiple threads."""
    root = Path(root_dir)
    subdirs = [d for d in root.iterdir() if d.is_dir()]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(deep_search, str(subdir), pattern)
            for subdir in subdirs
        ]
        results = []
        for future in futures:
            results.extend(future.result())

    return sorted(results)
```

## Success Criteria
- ✅ Finds files at any depth level
- ✅ Handles permission errors gracefully
- ✅ Supports multiple filter criteria
- ✅ Fast performance on large directory trees
- ✅ Provides flexible output formats

## Anti-Patterns
❌ Searching entire filesystem without constraints
❌ Not handling permission errors
❌ Following circular symlinks
❌ Loading all file contents into memory
❌ Not skipping irrelevant directories (.git, etc.)

## Related Patterns
- **PAT-PATCH-001**: Patch Lifecycle Management
- **PAT-FILE-001**: File Organization Standards
- **PAT-PERF-001**: Performance Optimization

## References
- Python pathlib documentation
- Unix find command
- Glob pattern matching

## Metadata
- **Created**: 2025-11-24
- **Version**: 1.0.0
- **Status**: Active
- **Compliance**: UET, ACS
