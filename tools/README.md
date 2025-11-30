---
doc_id: DOC-GUIDE-README-1094
---

# Internal Python Utilities

**Purpose**: Internal tools for repository maintenance, path tracking, and specification management.

## Overview

The `tools/` directory contains Python utilities for indexing hardcoded paths, managing specifications, and generating repository metadata. These tools are used during development and CI to maintain codebase health.

## Structure

```
tools/
├── hardcoded_path_indexer.py  # Index and track hardcoded file paths
├── spec_guard/                # Specification validation and enforcement
├── spec_indexer/              # Generate specification indices
├── spec_patcher/              # Apply specification patches
├── spec_renderer/             # Render specifications to HTML/Markdown
└── spec_resolver/             # Resolve specification URIs
```

## Core Tools

### Hardcoded Path Indexer (`hardcoded_path_indexer.py`)

Scans the repository for hardcoded file paths in code, docs, and config files, tracks them in SQLite, and helps identify refactoring needs.

**Features**:
- Regex-based path detection in Python, PowerShell, Markdown, YAML, JSON
- SQLite database tracking (`refactor_paths.db`)
- Categorization by path type (code, config, docs)
- Skip directories: `.git`, `__pycache__`, `.venv`, `node_modules`, etc.

**Usage**:
```bash
# Scan repository and update database
python tools/hardcoded_path_indexer.py

# Export results to JSON
python tools/hardcoded_path_indexer.py --output paths.json

# Filter by extension
python tools/hardcoded_path_indexer.py --extensions .py .yaml
```

**Database Schema**:
```sql
CREATE TABLE paths (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    line_number INTEGER,
    matched_path TEXT,
    path_type TEXT,  -- 'code', 'config', 'docs'
    last_seen_utc TEXT
);
```

**Output Example** (`paths.json`):
```json
[
  {
    "file": "src/module.py",
    "line": 42,
    "path": "config/tool_profiles.json",
    "type": "code"
  }
]
```

**Use Cases**:
- Refactoring tracking (old → new paths)
- Dead code detection
- Configuration drift analysis
- Documentation accuracy validation

**Path Detection Patterns**:
```python
PATH_REGEX = re.compile(
    r"(?P<path>(?:[A-Za-z]:\\\\|\\\\\\\\|\.|~)?(?:[\\/][^\\/\n\r\t\f\v]+){1,})"
)
```

**Tracked Patterns**:
- `src/`, `core/`, `error/`, `config/`
- `scripts/`, `tests/`, `docs/`
- `.worktrees/`, `.state/`

## Specification Tools

Located in subdirectories, these tools are now migrated to `specifications/tools/`.

### Spec Guard (`spec_guard/`)

**Deprecated**: Use `specifications/tools/guard/` instead.

Validates that code changes don't violate specification contracts.

**See**: [specifications/tools/guard/README.md](../specifications/tools/guard/README.md)

### Spec Indexer (`spec_indexer/`)

**Deprecated**: Use `specifications/tools/indexer/` instead.

Generates indices for specification lookup and cross-referencing.

**See**: [specifications/tools/indexer/README.md](../specifications/tools/indexer/README.md)

### Spec Patcher (`spec_patcher/`)

**Deprecated**: Use `specifications/tools/patcher/` instead.

Applies specification patches to workstreams.

**See**: [specifications/tools/patcher/README.md](../specifications/tools/patcher/README.md)

### Spec Renderer (`spec_renderer/`)

**Deprecated**: Use `specifications/tools/renderer/` instead.

Renders specifications to HTML, Markdown, or PDF.

**See**: [specifications/tools/renderer/README.md](../specifications/tools/renderer/README.md)

### Spec Resolver (`spec_resolver/`)

**Deprecated**: Use `specifications/tools/resolver/` instead.

Resolves specification URIs to file paths.

**See**: [specifications/tools/resolver/README.md](../specifications/tools/resolver/README.md)

## Running Tools

### Development Usage

```bash
# Index hardcoded paths
python tools/hardcoded_path_indexer.py

# Query database
python -c "import sqlite3; conn = sqlite3.connect('refactor_paths.db'); print(conn.execute('SELECT COUNT(*) FROM paths').fetchone())"

# Export to JSON
python tools/hardcoded_path_indexer.py --output paths.json
```

### CI Integration

Tools are run automatically in CI pipelines:

```yaml
# .github/workflows/ci.yml
- name: Index hardcoded paths
  run: python tools/hardcoded_path_indexer.py
  
- name: Validate paths
  run: python scripts/validate_hardcoded_paths.py
```

## Configuration

### Path Indexer Settings

**Environment Variables**:
- `INDEXER_DB_PATH` - Database path (default: `refactor_paths.db`)
- `INDEXER_SKIP_DIRS` - Additional directories to skip (comma-separated)
- `INDEXER_EXTENSIONS` - File extensions to scan (comma-separated)

**Skip Directories** (hardcoded):
```python
SKIP_DIRS = {
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    ".venv", "venv",
    "node_modules",
    "build", "dist",
    "logs", "state"
}
```

**Tracked Extensions**:
```python
CODE_EXTS = {".py", ".ps1", ".psm1", ".sh", ".bat", ".cmd"}
CONFIG_EXTS = {".yml", ".yaml", ".json", ".ini", ".cfg", ".toml"}
DOC_EXTS = {".md", ".txt"}
```

## Testing

```bash
# Unit tests for path indexer
pytest tests/test_hardcoded_path_indexer.py -v

# Integration tests
pytest tests/integration/test_tool_usage.py -v
```

## Output Formats

### SQLite Database

Default storage format for efficient querying.

```python
import sqlite3
conn = sqlite3.connect("refactor_paths.db")
cursor = conn.execute("SELECT * FROM paths WHERE path_type = 'code'")
for row in cursor:
    print(row)
```

### JSON Export

Portable format for reporting and analysis.

```bash
python tools/hardcoded_path_indexer.py --output paths.json
```

### CSV Export

Spreadsheet-friendly format.

```bash
python tools/hardcoded_path_indexer.py --output paths.csv --format csv
```

## Use Cases

### Refactoring Tracking

When refactoring paths (e.g., `src/pipeline/` → `core/`):

1. Run indexer to capture current paths
2. Perform refactoring
3. Re-run indexer to detect stale references
4. Update references using `scripts/update_hardcoded_paths.py`

### Documentation Accuracy

Ensure documentation references valid file paths:

```bash
# Index paths in markdown files
python tools/hardcoded_path_indexer.py --extensions .md

# Validate against repository structure
python scripts/validate_doc_paths.py
```

### Configuration Drift

Detect when config files reference non-existent paths:

```bash
# Index config files
python tools/hardcoded_path_indexer.py --extensions .yaml .json

# Check for invalid paths
python scripts/check_config_paths.py
```

## Best Practices

1. **Run regularly**: Index paths after major refactorings
2. **Version database**: Commit `refactor_paths.db` for historical tracking
3. **Validate in CI**: Fail builds if invalid paths detected
4. **Filter noise**: Use `SKIP_DIRS` to exclude irrelevant directories
5. **Document exceptions**: Add comments for intentionally hardcoded paths

## Performance

- **Scan time**: ~2-5 seconds for typical repository (~5000 files)
- **Database size**: ~100-500 KB depending on repository size
- **Memory usage**: <50 MB during scanning

**Optimization Tips**:
- Use `--extensions` to limit scope
- Exclude large generated directories via `SKIP_DIRS`
- Run incrementally on changed files in CI

## Troubleshooting

**Issue**: Paths not detected
- Check regex pattern matches your path format
- Verify file extension in `CODE_EXTS`, `CONFIG_EXTS`, or `DOC_EXTS`
- Ensure file not in `SKIP_DIRS`

**Issue**: False positives
- Refine `PATH_REGEX` to exclude URL-like patterns
- Add exceptions for specific file patterns

**Issue**: Database locked
- Close other connections to `refactor_paths.db`
- Check for stale locks: `rm refactor_paths.db-journal`

## Related Sections

- **Scripts**: `scripts/` - Automation that uses these tools
- **Specifications**: `specifications/tools/` - Specification management tools (migrated)
- **CI**: `infra/ci/` - CI integration workflows

## See Also

- [Specification Tools README](../specifications/tools/README.md)
- [Refactoring Guide](../docs/refactoring_guide.md)
- [CI Path Standards](../docs/CI_PATH_STANDARDS.md)
