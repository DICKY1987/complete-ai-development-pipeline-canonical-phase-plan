# PAT-SEARCH-002: README presence audit

## Pattern ID
**PAT-SEARCH-002**

## Pattern name
Recursive README presence audit

## Category
Utilities / Documentation hygiene

## Intent
Find every directory (including nested subdirectories) that either contains or lacks a README file, then
report grouped lists of directories by coverage status.

## Problem
- Teams need to quickly see which parts of a repository are missing basic documentation
- Manual inspection of nested directories is slow and error-prone
- README filenames vary (README.md, README, readme.txt), and case sensitivity differs by platform

## Solution
Implement a recursive scanner that:
1. Walks all directories from a root path (optionally excluding common junk directories)
2. Detects README presence using a configurable, case-insensitive filename set
3. Emits two groups: directories with a README and directories without one
4. Supports text and JSON output for humans and automation

## Implementation outline

### Core scan
```python
from pathlib import Path
from typing import Iterable

README_NAMES = {"README", "README.md", "README.txt", "readme.md", "readme"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}

def has_readme(dir_path: Path, names: Iterable[str]) -> bool:
    names_lower = {n.lower() for n in names}
    return any(child.is_file() and child.name.lower() in names_lower for child in dir_path.iterdir())

def scan_readme_coverage(root: Path, names: Iterable[str] = README_NAMES):
    with_readme, without_readme = [], []

    for dir_path in root.rglob("*"):
        if dir_path.is_dir():
            if dir_path.name in SKIP_DIRS:
                continue
            target = with_readme if has_readme(dir_path, names) else without_readme
            target.append(dir_path)

    return sorted(with_readme), sorted(without_readme)
```

### CLI behavior
```bash
# Text report (default)
python scripts/readme_presence_scan.py --root . --names README.md README

# JSON output (for pipelines)
python scripts/readme_presence_scan.py --root repo/path --json

# Limit depth to reduce noise
python scripts/readme_presence_scan.py --root . --max-depth 3

# Include hidden/system folders if needed
python scripts/readme_presence_scan.py --root . --include-hidden
```

### Output shape
```
Directories with README (7):
- docs
- docs/planning
- templates

Directories without README (3):
- scripts
- specs/examples
- verification/assets
```

### JSON output
```json
{
  "root": ".",
  "readme_names": ["README.md", "README"],
  "with_readme": ["docs", "docs/planning"],
  "without_readme": ["scripts"]
}
```

## Success criteria
- Reports every directory under the root (respecting skips)
- Correctly detects README files across common name variants and casing
- Provides both grouped text and machine-readable JSON output
- Handles missing/permission issues gracefully without crashing
- Options available for depth limits and custom ignore lists

## Anti-patterns
- Assuming a single README filename or case
- Following symlinks that create cycles
- Scanning the entire filesystem without excludes
- Failing when encountering unreadable directories

## Related patterns
- PAT-SEARCH-001: Deep directory search
- PAT-FILE-001: File organization standards

## Metadata
- **Created**: 2025-11-25
- **Version**: 1.0.0
- **Status**: Draft
