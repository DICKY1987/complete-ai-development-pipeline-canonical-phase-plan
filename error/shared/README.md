---
doc_id: DOC-ERROR-README-091
---

# Error System Shared Utilities

**Purpose**: Common utilities, types, and helpers for the error detection system.

## Overview

Shared utilities used across error engine, plugins, and service layer for type definitions, file hashing, environment management, and JSONL logging.

## Structure

```
error/shared/
└── utils/
    ├── types.py          # Type definitions and dataclasses
    ├── hashing.py        # File hash computation for incremental validation
    ├── jsonl_manager.py  # JSONL append-only logging
    ├── env.py            # Environment variable scrubbing
    ├── time.py           # UTC timestamp utilities
    ├── security.py       # Secrets redaction
    └── __init__.py
```

## Core Modules

### Types (`types.py`)

Canonical type definitions for the error system.

#### PluginIssue

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PluginIssue:
    tool: str                    # Plugin ID (e.g., "python_ruff")
    path: str                    # File path
    line: Optional[int] = None   # Line number (1-indexed)
    column: Optional[int] = None # Column number (1-indexed)
    code: Optional[str] = None   # Error code (e.g., "E501")
    category: Optional[str] = None  # "syntax", "type", "style", "security", etc.
    severity: Optional[str] = None  # "error", "warning", "info"
    message: Optional[str] = None   # Human-readable message
```

**Usage**:
```python
from error.shared.utils.types import PluginIssue

issue = PluginIssue(
    tool="python_ruff",
    path="src/module.py",
    line=42,
    column=10,
    code="E501",
    category="style",
    severity="error",
    message="Line too long (120 > 88 characters)"
)
```

#### PluginResult

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class PluginResult:
    plugin_id: str
    success: bool
    issues: List[PluginIssue] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Usage**:
```python
from error.shared.utils.types import PluginResult

result = PluginResult(
    plugin_id="python_mypy",
    success=True,
    issues=[issue1, issue2],
    stdout="Success: no issues found",
    returncode=0,
    duration_ms=1250
)
```

#### PipelineSummary

```python
@dataclass
class PipelineSummary:
    plugins_run: int
    total_errors: int
    total_warnings: int
    auto_fixed: int = 0
    issues_by_tool: Dict[str, int] = field(default_factory=dict)
    issues_by_category: Dict[str, int] = field(default_factory=dict)
    has_hard_fail: Optional[bool] = None
    style_only: Optional[bool] = None
```

#### PipelineReport

```python
@dataclass
class PipelineReport:
    run_id: str
    file_in: str
    file_out: Optional[str]
    timestamp_utc: str
    toolchain: Dict[str, str] = field(default_factory=dict)
    summary: PipelineSummary = field(default=None)
    issues: List[PluginIssue] = field(default_factory=list)
```

### Hashing (`hashing.py`)

Efficient file content hashing for incremental validation.

```python
from pathlib import Path
from error.shared.utils.hashing import compute_file_hash

# Compute SHA-256 hash of file content
file_hash = compute_file_hash(Path("src/module.py"))
# Returns: "a1b2c3d4e5f6..."
```

**Features**:
- SHA-256 hash algorithm
- Memory-efficient chunked reading for large files
- Handles encoding errors gracefully
- Skips binary files

**Implementation**:
```python
import hashlib
from pathlib import Path

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""
```

### JSONL Manager (`jsonl_manager.py`)

Append-only JSONL logging for audit trails and pipeline history.

```python
from error.shared.utils.jsonl_manager import JSONLManager

manager = JSONLManager(Path(".state/pipeline_history.jsonl"))

# Append record
manager.append({"run_id": "run-001", "status": "success"})

# Read all records
for record in manager.read():
    print(record["run_id"])
```

**Features**:
- Atomic append operations
- File locking for concurrent writes
- Auto-creation of parent directories
- Streaming read support

**Use Cases**:
- Pipeline execution history
- Agent invocation logs
- Error detection audit trail
- Performance metrics

### Environment Utilities (`env.py`)

Safe environment variable handling with credential scrubbing.

```python
from error.shared.utils.env import scrub_env

# Get scrubbed environment (removes API keys, tokens, etc.)
safe_env = scrub_env()

# Use for subprocess execution
result = run_command("tool", env=safe_env)
```

**Scrubbed Variables**:
- `*_API_KEY`
- `*_SECRET`
- `*_TOKEN`
- `PASSWORD`
- `AWS_*` credentials
- `GITHUB_TOKEN`
- Custom patterns via config

**Custom Scrubbing**:
```python
from error.shared.utils.env import scrub_env

# Additional patterns
safe_env = scrub_env(extra_patterns=["CUSTOM_CRED_*"])
```

### Time Utilities (`time.py`)

UTC timestamp generation and formatting.

```python
from error.shared.utils.time import utc_now, utc_timestamp

# Get current UTC datetime
now = utc_now()
# Returns: datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

# Get ISO 8601 timestamp string
timestamp = utc_timestamp()
# Returns: "2025-01-15T10:30:00Z"
```

**Features**:
- Timezone-aware UTC timestamps
- ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- Reproducible for deterministic testing

### Security Utilities (`security.py`)

Redact sensitive data from logs and reports.

```python
from error.shared.utils.security import redact_secrets

text = "API key: sk-abc123def456 is secret"
safe_text = redact_secrets(text)
# Returns: "API key: [REDACTED] is secret"
```

**Detected Patterns**:
- API keys (OpenAI, Anthropic, etc.)
- JWT tokens
- SSH keys
- AWS credentials
- Generic secrets (base64 patterns)

**Custom Patterns**:
```python
from error.shared.utils.security import redact_secrets

safe_text = redact_secrets(
    text,
    extra_patterns=[r"password=\S+"]
)
```

## Integration with Error Engine

### File Hash Cache

**Location**: `.state/validation_cache.json`

```python
from error.engine.file_hash_cache import FileHashCache
from error.shared.utils.hashing import compute_file_hash

cache = FileHashCache(Path(".state/validation_cache.json"))
cache.load()

file_path = Path("src/module.py")
current_hash = compute_file_hash(file_path)

if cache.get(str(file_path)) == current_hash:
    # Skip validation
    pass
else:
    # Run validation
    cache.set(str(file_path), current_hash, "pass")
    cache.save()
```

### Plugin Result Normalization

```python
from error.shared.utils.types import PluginIssue, PluginResult

def parse_tool_output(stdout: str) -> List[PluginIssue]:
    issues = []
    for line in stdout.splitlines():
        # Parse line
        issues.append(PluginIssue(
            tool="my_tool",
            path="file.py",
            line=42,
            severity="error",
            message=line
        ))
    return issues

result = PluginResult(
    plugin_id="my_tool",
    success=len(issues) == 0,
    issues=issues
)
```

### Audit Logging

```python
from error.shared.utils.jsonl_manager import JSONLManager
from error.shared.utils.time import utc_timestamp

audit_log = JSONLManager(Path(".state/audit.jsonl"))

audit_log.append({
    "timestamp": utc_timestamp(),
    "action": "error_pipeline_run",
    "file": "src/module.py",
    "status": "success",
    "issues_found": 0
})
```

## Testing

```bash
# Unit tests for utilities
pytest tests/error/test_hashing.py -v
pytest tests/error/test_jsonl_manager.py -v
pytest tests/error/test_env.py -v
pytest tests/error/test_security.py -v

# Integration tests
pytest tests/pipeline/ -v
```

## Best Practices

1. **Use typed dataclasses**: Prefer `PluginIssue`, `PluginResult` over raw dicts
2. **Hash-based caching**: Always compute hashes for incremental validation
3. **Scrub environments**: Never pass raw `os.environ` to subprocesses
4. **UTC timestamps**: Use `utc_timestamp()` for all time-related data
5. **Redact secrets**: Use `redact_secrets()` before logging tool output

## Performance Considerations

### Hashing
- **Large files**: Chunked reading (8KB chunks) minimizes memory usage
- **Skip binary files**: Hash computation skips binary files by default

### JSONL Manager
- **Append-only**: O(1) append operations
- **Streaming reads**: Memory-efficient iteration
- **File locking**: Prevents concurrent write corruption

### Environment Scrubbing
- **Lazy evaluation**: Scrubbing only happens when `scrub_env()` is called
- **Pattern caching**: Regex patterns compiled once

## Configuration

### Hash Algorithm

Default: SHA-256 (can be configured via environment variable)

```bash
export PIPELINE_HASH_ALGORITHM=sha256  # or sha1, md5 (not recommended)
```

### JSONL Format

**Standard format**:
```json
{"timestamp": "2025-01-15T10:30:00Z", "event": "pipeline_run", "status": "success"}
{"timestamp": "2025-01-15T10:31:00Z", "event": "plugin_execute", "plugin_id": "python_ruff"}
```

**Features**:
- One JSON object per line
- No top-level array (streaming-friendly)
- Self-describing schema via keys

## Environment Variables

- `PIPELINE_HASH_ALGORITHM` - Hash algorithm (default: `sha256`)
- `PIPELINE_STATE_DIR` - State directory (default: `.state/`)
- `PIPELINE_REDACT_SECRETS` - Enable secret redaction (default: `true`)

## Related Sections

- **Error Engine**: `error/engine/` - Uses these utilities for pipeline execution
- **Error Plugins**: `error/plugins/` - Plugins return `PluginResult` and `PluginIssue`
- **Core State**: `core/state/` - Database-backed state (complementary to JSONL audit logs)

## See Also

- [Error Engine README](../engine/README.md)
- [Error Plugins README](../plugins/README.md)
- [Operating Contract](../../docs/operating_contract.md)
