---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-ANTI-PATTERNS-802
---

# Anti-Patterns Catalog

**Purpose:** Document common mistakes and discouraged practices to help AI agents and developers avoid repeating historical errors.

**Last Updated:** 2025-11-22
**Maintainer:** System Architecture Team

---

## How to Use This Catalog

Each anti-pattern entry includes:
- **Problem:** What the anti-pattern is
- **Example:** BAD code demonstrating the issue
- **Why It's Wrong:** Explanation of negative consequences
- **Correct Approach:** GOOD code showing the right way
- **Historical Incidents:** Links to commits/issues where this caused problems (when applicable)

---

## Core State Anti-Patterns

### AP-CS-01: Direct File Database Access

**Category:** Core State
**Severity:** High

**Problem:**
Directly opening SQLite database file without using `core/state/db.py` functions

**Example (BAD):**
```python
import sqlite3

# DON'T DO THIS
conn = sqlite3.connect('.worktrees/pipeline_state.db')
cursor = conn.execute("SELECT * FROM workstreams")
results = cursor.fetchall()
conn.close()
```

**Why It's Wrong:**
- Bypasses database initialization logic
- Missing connection pooling and error handling
- Doesn't respect `PIPELINE_DB_PATH` environment variable
- No transaction management
- Schema version not checked

**Correct Approach (GOOD):**
```python
from core.state.db import get_connection
from core.state.workstreams import get_workstreams

# Use provided functions
conn = get_connection()
workstreams = get_workstreams(conn)
```

**Historical Incidents:**
- Early prototypes had hardcoded paths that broke on different machines
- Missing transactions caused database corruption during crashes

---

### AP-CS-02: Missing Database Migrations

**Category:** Core State
**Severity:** Critical

**Problem:**
Modifying database schema directly without creating migration file

**Example (BAD):**
```python
# DON'T DO THIS - modifying schema in code
conn = get_connection()
conn.execute("ALTER TABLE workstreams ADD COLUMN priority TEXT")
conn.commit()
```

**Why It's Wrong:**
- Schema changes not tracked or versioned
- Other developers' databases become incompatible
- No rollback capability
- Breaks schema version tracking

**Correct Approach (GOOD):**
```sql
-- Create schema/migrations/003_add_priority.sql
-- Migration: Add priority field to workstreams
-- Date: 2025-11-22

ALTER TABLE workstreams ADD COLUMN priority TEXT DEFAULT 'normal';

UPDATE schema_version SET version = 3;
```

```python
# Migration applied automatically on next init_db()
from core.state.db import init_db
conn = init_db()  # Runs all pending migrations
```

**Historical Incidents:**
- Phase E refactor required manual database recreation due to missing migrations

---

### AP-CS-03: State Machine State Pollution

**Category:** Core State
**Severity:** Medium

**Problem:**
Manually setting workstream state without going through state machine transitions

**Example (BAD):**
```python
# DON'T DO THIS - bypassing state machine
conn.execute("UPDATE workstreams SET state = 'S_SUCCESS' WHERE ws_id = ?", (ws_id,))
```

**Why It's Wrong:**
- Violates state machine invariants
- Skips validation logic
- No state transition logging
- Can create invalid states (e.g., skip S_RUNNING)

**Correct Approach (GOOD):**
```python
from core.state.workstreams import transition_workstream

# Use state machine function
transition_workstream(conn, ws_id, 'S_SUCCESS', metadata={'reason': 'all steps completed'})
```

---

## Error Engine Anti-Patterns

### AP-EE-01: Skipping Plugin Manifest

**Category:** Error Engine
**Severity:** High

**Problem:**
Creating error detection plugin without `manifest.json` file

**Example (BAD):**
```
error/plugins/my_linter/
├── plugin.py  # Only this file, no manifest
└── tests/
```

**Why It's Wrong:**
- Plugin not discoverable by plugin manager
- No metadata about capabilities, dependencies
- Can't disable/enable plugin selectively
- Missing version information

**Correct Approach (GOOD):**
```
error/plugins/my_linter/
├── manifest.json  # REQUIRED
├── plugin.py
└── tests/
```

```json
{
  "plugin_id": "my_linter",
  "name": "My Custom Linter",
  "version": "1.0.0",
  "supported_languages": ["python"],
  "file_patterns": ["*.py"],
  "capabilities": ["parse"],
  "entry_point": "plugin.py"
}
```

---

### AP-EE-02: Non-Incremental Scanning

**Category:** Error Engine
**Severity:** Medium

**Problem:**
Rescanning all files even when most haven't changed

**Example (BAD):**
```python
def scan_project():
    # DON'T DO THIS - scans everything every time
    all_files = glob.glob("**/*.py", recursive=True)
    for file in all_files:
        errors = run_linter(file)
        store_errors(errors)
```

**Why It's Wrong:**
- Wastes time scanning unchanged files
- Slow for large projects (minutes vs seconds)
- Ignores file hash caching system

**Correct Approach (GOOD):**
```python
from error.engine.file_cache import get_changed_files

def scan_project():
    # Only scan files that changed
    changed_files = get_changed_files()
    for file in changed_files:
        errors = run_linter(file)
        store_errors(errors)
        update_file_hash(file)  # Mark as scanned
```

---

### AP-EE-03: Swallowing Plugin Errors

**Category:** Error Engine
**Severity:** Medium

**Problem:**
Catching plugin exceptions without logging or reporting

**Example (BAD):**
```python
try:
    results = plugin.parse(file_path, content)
except Exception:
    # DON'T DO THIS - silent failure
    return []
```

**Why It's Wrong:**
- Users don't know plugin failed
- Debugging is impossible
- Appears that file has no errors (false negative)

**Correct Approach (GOOD):**
```python
import logging

logger = logging.getLogger(__name__)

try:
    results = plugin.parse(file_path, content)
except Exception as e:
    logger.error(f"Plugin {plugin_id} failed on {file_path}: {e}")
    # Record failure in database
    record_plugin_failure(plugin_id, file_path, str(e))
    return []  # But now user knows why
```

---

## Specifications Anti-Patterns

### AP-SP-01: Circular Spec Dependencies

**Category:** Specifications
**Severity:** High

**Problem:**
Specification A references specification B which references specification A

**Example (BAD):**
```markdown
<!-- specs/core/orchestrator.md -->
See [State Management](spec://core/state) for details.

<!-- specs/core/state.md -->
See [Orchestrator](spec://core/orchestrator) for usage.
```

**Why It's Wrong:**
- Spec resolver can infinite loop
- Unclear which spec is authoritative
- Makes specifications harder to understand

**Correct Approach (GOOD):**
```markdown
<!-- specs/core/orchestrator.md -->
Uses state management (see spec://core/state) to persist execution state.

<!-- specs/core/state.md -->
State management provides persistence. For usage examples, see:
- spec://examples/orchestrator-usage
- spec://core/orchestrator (implementation details)
```

Create hierarchy: core concepts → implementation → examples

---

### AP-SP-02: Missing URI Resolution

**Category:** Specifications
**Severity:** Medium

**Problem:**
Using plain markdown links instead of spec URIs for cross-specification references

**Example (BAD):**
```markdown
See [Database Module](../../core/state/db.md) for implementation.
```

**Why It's Wrong:**
- Breaks when files move
- Not tracked by spec resolver
- Can't validate cross-references automatically

**Correct Approach (GOOD):**
```markdown
See [Database Module](spec://core/state/db) for implementation.
```

Spec resolver handles location changes automatically.

---

## Scripts Anti-Patterns

### AP-SC-01: Hardcoded Absolute Paths

**Category:** Scripts
**Severity:** Critical

**Problem:**
Using absolute paths that only work on one machine

**Example (BAD):**
```python
# DON'T DO THIS
DB_PATH = "C:\\Users\\alice\\project\\pipeline_state.db"
CONFIG_FILE = "/home/bob/configs/tool_profiles.json"
```

**Why It's Wrong:**
- Breaks on other developers' machines
- Breaks in CI/CD
- Not portable across OS (Windows vs Linux)

**Correct Approach (GOOD):**
```python
import os
from pathlib import Path

# Use repository-relative paths
REPO_ROOT = Path(__file__).parent.parent  # scripts/ -> repo root
DB_PATH = os.getenv("PIPELINE_DB_PATH", REPO_ROOT / ".worktrees" / "pipeline_state.db")
CONFIG_FILE = REPO_ROOT / "config" / "tool_profiles.json"
```

---

### AP-SC-02: Missing Error Handling

**Category:** Scripts
**Severity:** High

**Problem:**
Not handling expected errors (file not found, permissions, subprocess failures)

**Example (BAD):**
```python
# DON'T DO THIS - crashes on missing file
content = open("data.json").read()
data = json.loads(content)
subprocess.run(["external-tool", "arg"], check=True)
```

**Why It's Wrong:**
- Cryptic error messages for users
- No recovery or helpful guidance
- Stack traces instead of user-friendly errors

**Correct Approach (GOOD):**
```python
import sys

try:
    with open("data.json") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: data.json not found. Run 'init.py' first.", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in data.json: {e}", file=sys.stderr)
    sys.exit(1)

result = subprocess.run(["external-tool", "arg"], capture_output=True)
if result.returncode != 0:
    print(f"Error: external-tool failed: {result.stderr.decode()}", file=sys.stderr)
    sys.exit(1)
```

---

### AP-SC-03: Printing Sensitive Information

**Category:** Scripts
**Severity:** High

**Problem:**
Logging or printing API keys, tokens, passwords

**Example (BAD):**
```python
# DON'T DO THIS
api_key = os.getenv("OPENAI_API_KEY")
print(f"Using API key: {api_key}")
logger.info(f"Authenticating with token {auth_token}")
```

**Why It's Wrong:**
- Secrets appear in logs
- CI logs expose credentials publicly
- Security vulnerability

**Correct Approach (GOOD):**
```python
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    masked = api_key[:8] + "..." + api_key[-4:]
    print(f"Using API key: {masked}")
else:
    print("Error: OPENAI_API_KEY not set", file=sys.stderr)
```

---

## Testing Anti-Patterns

### AP-TS-01: Network Calls in Unit Tests

**Category:** Testing
**Severity:** High

**Problem:**
Making real HTTP requests or external API calls in unit tests

**Example (BAD):**
```python
def test_fetch_data():
    # DON'T DO THIS - makes real HTTP request
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
```

**Why It's Wrong:**
- Tests fail when network is unavailable
- Tests are slow
- Can hit rate limits
- Non-deterministic (external service may change)

**Correct Approach (GOOD):**
```python
from unittest.mock import patch, Mock

def test_fetch_data():
    # Mock the HTTP call
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = fetch_data()
        assert result == {"key": "value"}
```

---

### AP-TS-02: Non-Deterministic Assertions

**Category:** Testing
**Severity:** Medium

**Problem:**
Tests that depend on current time, random values, or execution order

**Example (BAD):**
```python
import datetime
import random

def test_recent_activity():
    # DON'T DO THIS - depends on current time
    activities = get_recent_activities()
    assert activities[0].timestamp > datetime.datetime.now() - datetime.timedelta(hours=1)

def test_random_selection():
    # DON'T DO THIS - uses random without seed
    result = select_random_item()
    assert result in ['A', 'B', 'C']  # Flaky - sometimes passes, sometimes fails
```

**Why It's Wrong:**
- Tests fail randomly ("flaky tests")
- Debugging is difficult
- CI failures can't be reproduced locally

**Correct Approach (GOOD):**
```python
from unittest.mock import patch
import datetime

def test_recent_activity():
    # Mock time to be deterministic
    fixed_time = datetime.datetime(2025, 11, 22, 12, 0, 0)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        activities = get_recent_activities()
        assert activities[0].timestamp > fixed_time - datetime.timedelta(hours=1)

def test_random_selection():
    # Seed random for determinism
    random.seed(42)
    result = select_random_item()
    assert result == 'B'  # Always returns same value with seed 42
```

---

### AP-TS-03: Testing Implementation Instead of Behavior

**Category:** Testing
**Severity:** Low

**Problem:**
Testing internal implementation details instead of public API behavior

**Example (BAD):**
```python
def test_workstream_processing():
    # DON'T DO THIS - testing private methods
    orchestrator = Orchestrator()
    assert orchestrator._validate_step({'step_id': 'test'}) == True
    assert orchestrator._internal_counter == 0
```

**Why It's Wrong:**
- Tests break when refactoring internals
- Doesn't test actual user-facing behavior
- Couples tests to implementation

**Correct Approach (GOOD):**
```python
def test_workstream_processing():
    # Test public API behavior
    orchestrator = Orchestrator()
    result = orchestrator.execute_workstream(valid_workstream)

    assert result.status == 'success'
    assert result.steps_completed == 3
    # Tests what users care about, not how it's implemented
```

---

## Configuration Anti-Patterns

### AP-CF-01: Environment-Specific Config in Code

**Category:** Configuration
**Severity:** High

**Problem:**
Hardcoding environment-specific settings in source code

**Example (BAD):**
```python
# DON'T DO THIS
if socket.gethostname() == "alice-laptop":
    DB_PATH = "/home/alice/db.sqlite"
elif socket.gethostname() == "production-server":
    DB_PATH = "/var/lib/pipeline/db.sqlite"
```

**Why It's Wrong:**
- Doesn't work on new machines
- Production config exposed in source code
- Hard to test different configurations

**Correct Approach (GOOD):**
```python
# Use environment variables or config files
DB_PATH = os.getenv("PIPELINE_DB_PATH", ".worktrees/pipeline_state.db")

# Or load from config file
from pathlib import Path
import json

config_file = Path("config/local.json")  # Gitignored
if config_file.exists():
    config = json.loads(config_file.read_text())
    DB_PATH = config.get("db_path", ".worktrees/pipeline_state.db")
```

---

## General Anti-Patterns

### AP-GN-01: Copy-Paste Code Duplication

**Category:** General
**Severity:** Medium

**Problem:**
Duplicating logic instead of extracting to shared function

**Example (BAD):**
```python
# File 1
results = []
for item in items:
    if item.status == 'active' and item.priority > 5:
        results.append(item)

# File 2 (same logic!)
filtered = []
for thing in things:
    if thing.status == 'active' and thing.priority > 5:
        filtered.append(thing)
```

**Why It's Wrong:**
- Bug fixes must be applied in multiple places
- Inconsistency when one copy is updated
- Violates DRY (Don't Repeat Yourself)

**Correct Approach (GOOD):**
```python
# shared/filters.py
def filter_active_high_priority(items):
    return [item for item in items
            if item.status == 'active' and item.priority > 5]

# File 1
results = filter_active_high_priority(items)

# File 2
filtered = filter_active_high_priority(things)
```

---

### AP-GN-02: God Objects

**Category:** General
**Severity:** Medium

**Problem:**
Single class/module that does everything

**Example (BAD):**
```python
class Pipeline:
    # DON'T DO THIS - 3000 lines, does everything
    def __init__(self): ...
    def load_config(self): ...
    def init_database(self): ...
    def scan_files(self): ...
    def run_linters(self): ...
    def fix_errors(self): ...
    def generate_report(self): ...
    def send_notifications(self): ...
    # ... 50 more methods
```

**Why It's Wrong:**
- Hard to understand and maintain
- Tight coupling between unrelated concerns
- Difficult to test in isolation
- Merge conflicts frequent

**Correct Approach (GOOD):**
```python
# Separate concerns into focused modules
from core.state.db import init_database
from error.engine.scanner import scan_files
from error.engine.linter import run_linters
from error.engine.fixer import fix_errors
from reporting.generator import generate_report

class Pipeline:
    """Coordinates workflow - delegates to specialists."""
    def __init__(self, config):
        self.config = config
        self.db = init_database(config.db_path)

    def run(self):
        files = scan_files(self.config.scan_paths)
        errors = run_linters(files)
        if self.config.auto_fix:
            fix_errors(errors)
        return generate_report(errors)
```

---

## Summary

### Most Critical Anti-Patterns to Avoid

1. **AP-CS-02:** Missing Database Migrations (breaks collaboration)
2. **AP-SC-01:** Hardcoded Paths (breaks portability)
3. **AP-TS-01:** Network Calls in Tests (breaks CI/CD)
4. **AP-EE-01:** Missing Plugin Manifest (breaks discoverability)
5. **AP-SC-03:** Printing Secrets (security vulnerability)

### Quick Reference Table

| Code | Category | Severity | Quick Description |
|------|----------|----------|-------------------|
| AP-CS-01 | Core State | High | Direct file DB access |
| AP-CS-02 | Core State | Critical | Missing migrations |
| AP-CS-03 | Core State | Medium | State machine bypass |
| AP-EE-01 | Error Engine | High | No plugin manifest |
| AP-EE-02 | Error Engine | Medium | Non-incremental scan |
| AP-EE-03 | Error Engine | Medium | Swallowing plugin errors |
| AP-SP-01 | Specifications | High | Circular dependencies |
| AP-SP-02 | Specifications | Medium | Missing URI resolution |
| AP-SC-01 | Scripts | Critical | Hardcoded paths |
| AP-SC-02 | Scripts | High | Missing error handling |
| AP-SC-03 | Scripts | High | Printing secrets |
| AP-TS-01 | Testing | High | Network calls in tests |
| AP-TS-02 | Testing | Medium | Non-deterministic tests |
| AP-TS-03 | Testing | Low | Testing implementation |
| AP-CF-01 | Configuration | High | Environment-specific code |
| AP-GN-01 | General | Medium | Copy-paste duplication |
| AP-GN-02 | General | Medium | God objects |

---

## Related Documentation

- [Change Impact Matrix](../reference/CHANGE_IMPACT_MATRIX.md) - What to update when changing components
- [Testing Strategy](TESTING_STRATEGY.md) - How to test properly
- [ADRs](../adr/) - Architecture decisions and rationale

---

## Contributing

Found a new anti-pattern? Add it following this template:

```markdown
### AP-XX-NN: Pattern Name

**Category:** [Core State | Error Engine | etc.]
**Severity:** [Critical | High | Medium | Low]

**Problem:** [What the anti-pattern is]

**Example (BAD):**
```[language]
[bad code example]
```

**Why It's Wrong:** [Explanation]

**Correct Approach (GOOD):**
```[language]
[good code example]
```

**Historical Incidents:** [Optional links]
```

---

**Maintainer:** System Architecture Team
**Last Reviewed:** 2025-11-22
**Next Review:** 2025-12-22 or after major incidents
