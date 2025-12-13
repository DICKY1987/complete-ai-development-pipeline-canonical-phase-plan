---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-ERROR-CATALOG-846
---

# Error Catalog

**Purpose:** Document common errors with recovery procedures to help AI agents and developers diagnose and fix issues quickly.

**Last Updated:** 2025-11-22
**Maintainer:** System Architecture Team

---

## Overview

This catalog provides:
- **Error Patterns:** Common failure scenarios
- **Root Causes:** Why errors occur
- **Recovery Procedures:** Step-by-step fixes
- **Prevention:** How to avoid in the future

---

## Error Categories

1. [Database Errors](#database-errors) (6 errors)
2. [Workstream Execution Errors](#workstream-execution-errors) (5 errors)
3. [Plugin Errors](#plugin-errors) (4 errors)
4. [Specification Resolution Errors](#specification-resolution-errors) (3 errors)
5. [Tool Adapter Errors](#tool-adapter-errors) (4 errors)
6. [Configuration Errors](#configuration-errors) (3 errors)

**Total:** 25 documented errors

---

## Database Errors

### ERR-DB-01: Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Root Cause:**
- Another process has exclusive write lock
- Long-running transaction not committed
- File system issues (network drive, permissions)

**Recovery:**
```bash
# 1. Check for other processes
ps aux | grep python | grep pipeline

# 2. Kill stale processes if safe
kill <pid>

# 3. If file is corrupted, restore backup
cp .worktrees/pipeline_state.db.backup .worktrees/pipeline_state.db

# 4. Set busy timeout in code
conn.execute("PRAGMA busy_timeout = 5000")  # Wait 5 seconds
```

**Prevention:**
- Keep transactions short (<100ms)
- Always commit or rollback
- Use WAL mode: `PRAGMA journal_mode=WAL`
- Don't run on NFS/SMB filesystems

**Related:** [ADR-0003: SQLite State Storage](../adr/0003-sqlite-state-storage.md)

---

### ERR-DB-02: Schema Version Mismatch

**Symptoms:**
```
SchemaVersionError: Expected v3, found v1
```

**Root Cause:**
- Database created with older code version
- Migrations not applied
- Manual schema modification

**Recovery:**
```bash
# 1. Check current version
sqlite3 .worktrees/pipeline_state.db "SELECT version FROM schema_version;"

# 2. Apply missing migrations manually
sqlite3 .worktrees/pipeline_state.db < schema/migrations/002_add_metadata.sql
sqlite3 .worktrees/pipeline_state.db < schema/migrations/003_add_priority.sql

# 3. Verify version
sqlite3 .worktrees/pipeline_state.db "SELECT version FROM schema_version;"

# OR recreate database (loses data!)
rm .worktrees/pipeline_state.db
python -c "from core.state.db import init_db; init_db()"
```

**Prevention:**
- Always create migration files for schema changes
- Run init_db() which applies migrations automatically
- Document schema version in migrations

**Related:** [Anti-Pattern AP-CS-02: Missing Database Migrations](../guidelines/ANTI_PATTERNS.md#ap-cs-02-missing-database-migrations)

---

### ERR-DB-03: Invalid State Transition

**Symptoms:**
```
InvalidTransition: Cannot transition from S_SUCCESS to S_RUNNING
```

**Root Cause:**
- Attempted invalid state machine transition
- Concurrent state updates
- Manual state modification bypassing state machine

**Recovery:**
```python
# 1. Check current state
from core.state.workstreams import get_workstream
ws = get_workstream(conn, "WS-001")
print(f"Current state: {ws['state']}")

# 2. If state is wrong, fix manually (last resort)
conn.execute("UPDATE workstreams SET state = ? WHERE ws_id = ?",
             ("S_PENDING", "WS-001"))
conn.commit()

# 3. Better: Create new workstream with correct state
```

**Prevention:**
- Always use `transition_workstream()` function
- Never UPDATE state column directly
- Check allowed transitions before attempting

**Valid Transitions:**
```
S_PENDING → S_RUNNING
S_RUNNING → S_SUCCESS
S_RUNNING → S_FAILED
S_FAILED → S_RETRYING
S_RETRYING → S_RUNNING
S_FAILED → S_ABANDONED
```

**Related:** [Anti-Pattern AP-CS-03: State Machine State Pollution](../guidelines/ANTI_PATTERNS.md#ap-cs-03-state-machine-state-pollution)

---

### ERR-DB-04: Database Not Found

**Symptoms:**
```
FileNotFoundError: .worktrees/pipeline_state.db
```

**Root Cause:**
- Database never initialized
- Wrong working directory
- PIPELINE_DB_PATH pointing to wrong location

**Recovery:**
```bash
# 1. Check current directory
pwd  # Should be repository root

# 2. Check environment variable
echo $PIPELINE_DB_PATH

# 3. Initialize database
python -c "from core.state.db import init_db; init_db()"

# 4. Verify creation
ls -la .worktrees/pipeline_state.db
```

**Prevention:**
- Run `init_db()` on first use
- Document initialization in README
- Bootstrap script should create database

**Related:** [ADR-0008: Database Location Worktree](../adr/0008-database-location-worktree.md)

---

### ERR-DB-05: Constraint Violation

**Symptoms:**
```
sqlite3.IntegrityError: UNIQUE constraint failed: workstreams.ws_id
```

**Root Cause:**
- Attempting to create duplicate workstream ID
- Foreign key constraint violation
- NOT NULL constraint on required field

**Recovery:**
```python
# 1. Check if workstream exists
ws = get_workstream(conn, "WS-001")
if ws:
    print("Workstream already exists, use different ID")

# 2. Or update existing instead of creating
update_workstream(conn, "WS-001", {"name": "Updated Name"})

# 3. For foreign key violations, check referenced record exists
step = get_step(conn, "s1")  # Ensure step exists before referencing
```

**Prevention:**
- Generate unique IDs (timestamp + random)
- Check existence before creating
- Use INSERT OR IGNORE for idempotency

---

### ERR-DB-06: Deadlock Detected

**Symptoms:**
```
Database deadlock: multiple transactions waiting on each other
```

**Root Cause:**
- Two transactions trying to update same rows in different order
- Long-lived transactions
- Missing indexes causing full table locks

**Recovery:**
```python
# 1. Retry transaction with exponential backoff
import time

for attempt in range(3):
    try:
        conn.execute("BEGIN")
        # ... transaction operations
        conn.commit()
        break
    except sqlite3.OperationalError:
        conn.rollback()
        time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

**Prevention:**
- Keep transactions short
- Always access tables in same order
- Use BEGIN IMMEDIATE for write transactions
- Add indexes on frequently queried columns

---

## Workstream Execution Errors

### ERR-WS-01: Step Dependency Not Met

**Symptoms:**
```
DependencyError: Step s2 depends on s1, but s1 is in state S_FAILED
```

**Root Cause:**
- Dependency step failed
- Dependency step not yet executed
- Circular dependency in workstream

**Recovery:**
```bash
# 1. Check dependency status
python -c "from core.state.steps import get_step;
           print(get_step(conn, 's1')['state'])"

# 2. Re-run failed dependency
python scripts/run_workstream.py --step s1 --retry

# 3. Or skip dependency if safe
python scripts/run_workstream.py --step s2 --force-dependencies
```

**Prevention:**
- Validate workstream before execution
- Use topological sort for execution order
- Detect circular dependencies at load time

**Related:** [Execution Trace: Workstream Execution](../EXECUTION_TRACES_SUMMARY.md)

---

### ERR-WS-02: Invalid Workstream Schema

**Symptoms:**
```
ValidationError: 'steps' is a required property
```

**Root Cause:**
- Workstream JSON doesn't match schema
- Missing required fields
- Invalid field types

**Recovery:**
```bash
# 1. Validate against schema
python scripts/validate_workstreams.py workstreams/my-bundle.json

# 2. Check required fields
# Required: ws_id, name, steps (array)

# 3. Fix JSON and re-validate
```

**Prevention:**
- Always validate workstreams before execution
- Use JSON schema editor with autocompletion
- Copy from working examples in `workstreams/`

**Related:** [Change Impact Matrix: Workstreams](../reference/CHANGE_IMPACT_MATRIX.md#workstreams)

---

### ERR-WS-03: Tool Profile Not Found

**Symptoms:**
```
ToolProfileNotFound: No profile found for 'unknown-tool'
```

**Root Cause:**
- Tool profile ID doesn't exist in config
- Typo in tool_profile_id
- Config file not loaded

**Recovery:**
```bash
# 1. List available profiles
python -c "from core.engine.tools import list_profiles;
           print(list_profiles())"

# 2. Check config file exists
ls -la config/tool_profiles.json

# 3. Fix workstream to use valid profile
```

**Prevention:**
- Validate tool_profile_id against available profiles
- Use constants for profile IDs
- Document available profiles in README

---

### ERR-WS-04: Step Timeout Exceeded

**Symptoms:**
```
TimeoutError: Step s1 exceeded timeout of 300 seconds
```

**Root Cause:**
- Step took longer than configured timeout
- Tool hung or stuck
- Insufficient timeout for task

**Recovery:**
```bash
# 1. Kill hung process
pkill -f "aider"  # If aider is stuck

# 2. Increase timeout in tool profile
# Edit config/tool_profiles.json:
{
  "tool_id": "aider",
  "timeout_seconds": 600  # Increase from 300
}

# 3. Retry step
python scripts/run_workstream.py --step s1 --retry
```

**Prevention:**
- Set realistic timeouts for each tool
- Monitor typical execution times
- Add progress logging to detect hangs early

---

### ERR-WS-05: Parallel Execution Conflict

**Symptoms:**
```
ConflictError: Steps s1 and s2 both modifying core/state/db.py
```

**Root Cause:**
- Parallel steps modifying same file
- Missing conflict_group annotation
- File lock not acquired

**Recovery:**
```bash
# 1. Run steps sequentially instead
python scripts/run_workstream.py --no-parallel

# 2. Or add conflict groups to workstream
{
  "steps": [
    {"step_id": "s1", "conflict_group": "db_changes"},
    {"step_id": "s2", "conflict_group": "db_changes"}
  ]
}
```

**Prevention:**
- Declare conflict_group for steps modifying same files
- Use file locking for concurrent access
- Design steps to be independent

---

## Plugin Errors

### ERR-PL-01: Plugin Manifest Invalid

**Symptoms:**
```
ManifestValidationError: manifest.json missing required field 'plugin_id'
```

**Root Cause:**
- manifest.json doesn't match schema
- Missing required fields
- Invalid JSON syntax

**Recovery:**
```bash
# 1. Validate manifest against schema
python -c "import json;
           manifest = json.load(open('error/plugins/my_plugin/manifest.json'));
           print(manifest)"

# 2. Check required fields
# Required: plugin_id, name, version, entry_point

# 3. Fix and retry
python error/engine/error_engine.py --discover-plugins
```

**Prevention:**
- Copy manifest from working plugin
- Validate JSON syntax
- Use schema validation in editor

**Related:** [Anti-Pattern AP-EE-01: Skipping Plugin Manifest](../guidelines/ANTI_PATTERNS.md#ap-ee-01-skipping-plugin-manifest)

---

### ERR-PL-02: Plugin Execution Failed

**Symptoms:**
```
PluginExecutionError: python_ruff plugin failed: ruff: command not found
```

**Root Cause:**
- Plugin dependency not installed
- Tool not in PATH
- Plugin code has bug

**Recovery:**
```bash
# 1. Install missing dependency
pip install ruff  # For python_ruff plugin

# 2. Verify tool works
ruff check --version

# 3. Check plugin code for errors
python -c "from error.plugins.python_ruff.plugin import parse;
           parse('test.py', '')"
```

**Prevention:**
- Document plugin dependencies in manifest
- Check tool availability before executing
- Add plugin self-test command

---

### ERR-PL-03: File Hash Mismatch

**Symptoms:**
```
HashMismatchError: Stored hash doesn't match computed hash for file.py
```

**Root Cause:**
- File modified during scan
- Hash algorithm changed
- Database corruption

**Recovery:**
```bash
# 1. Clear hash cache
sqlite3 .worktrees/pipeline_state.db "DELETE FROM file_hashes;"

# 2. Re-scan files
python error/engine/error_engine.py --force-rescan

# 3. Verify file integrity
sha256sum file.py
```

**Prevention:**
- Don't modify files during error scan
- Use consistent hash algorithm
- Validate hash on every read

---

### ERR-PL-04: Plugin Not Discovered

**Symptoms:**
```
PluginNotFound: Plugin 'my_custom_plugin' not found
```

**Root Cause:**
- Plugin directory not in error/plugins/
- Missing manifest.json
- Plugin disabled in config

**Recovery:**
```bash
# 1. Check plugin directory exists
ls error/plugins/my_custom_plugin/

# 2. Check manifest exists
cat error/plugins/my_custom_plugin/manifest.json

# 3. Force plugin discovery
python error/engine/error_engine.py --discover-plugins --verbose
```

**Prevention:**
- Place plugin in error/plugins/<name>/
- Include manifest.json
- Test discovery after adding plugin

---

## Specification Resolution Errors

### ERR-SP-01: Spec URI Not Found

**Symptoms:**
```
SpecNotFoundError: spec://unknown/module not found
```

**Root Cause:**
- Spec file doesn't exist
- Wrong URI path
- Spec not in specifications/content/

**Recovery:**
```bash
# 1. Search for spec
find specifications/ -name "*.md" | grep module

# 2. Check expected locations
ls specifications/content/unknown/module.md

# 3. Fix URI or create spec
```

**Prevention:**
- Validate spec URIs before referencing
- Use spec:// resolver to check existence
- Maintain spec index

**Related:** [Anti-Pattern AP-SP-02: Missing URI Resolution](../guidelines/ANTI_PATTERNS.md#ap-sp-02-missing-uri-resolution)

---

### ERR-SP-02: Circular Spec Reference

**Symptoms:**
```
CircularReferenceError: spec://core/state references spec://core/orchestrator which references spec://core/state
```

**Root Cause:**
- Spec A references Spec B which references Spec A
- Infinite loop in resolution
- Poor spec organization

**Recovery:**
```bash
# 1. Detect circular references
python specifications/tools/guard/guard.py --check-circular

# 2. Refactor specs to break cycle
# Move common content to third spec:
# core/state → core/common ← core/orchestrator
```

**Prevention:**
- Create hierarchy: core → implementation → examples
- Use guard tool to detect cycles
- Design specs with clear dependencies

**Related:** [Anti-Pattern AP-SP-01: Circular Spec Dependencies](../guidelines/ANTI_PATTERNS.md#ap-sp-01-circular-spec-dependencies)

---

### ERR-SP-03: Anchor Not Found

**Symptoms:**
```
AnchorNotFoundError: Anchor #initialization not found in spec://core/state/db
```

**Root Cause:**
- Anchor doesn't exist in spec
- Typo in anchor name
- Spec changed, anchor removed

**Recovery:**
```bash
# 1. List available anchors
python -c "from specifications.tools.resolver import list_anchors;
           print(list_anchors('spec://core/state/db'))"

# 2. Fix URI to use correct anchor
# spec://core/state/db#init → spec://core/state/db#initialization

# 3. Or add anchor to spec if missing
```

**Prevention:**
- Validate anchors exist before referencing
- Use conventional anchor names (lowercase, hyphens)
- Update references when renaming anchors

---

## Tool Adapter Errors

### ERR-TA-01: Circuit Breaker Open

**Symptoms:**
```
CircuitBreakerOpen: aider circuit is open, retry in 58 seconds
```

**Root Cause:**
- 5+ consecutive tool failures
- Circuit breaker protecting against cascading failures
- Tool is unhealthy

**Recovery:**
```bash
# 1. Wait for circuit to close (60 seconds default)
sleep 60

# 2. Or manually reset circuit breaker
python -c "from core.engine.circuit_breaker import reset_circuit;
           reset_circuit('aider')"

# 3. Check tool health
aider --version  # Verify tool works

# 4. Retry operation
```

**Prevention:**
- Fix underlying tool issues
- Increase failure threshold if false positives
- Monitor circuit breaker state

**Related:** [Execution Trace: Tool Adapter](../EXECUTION_TRACES_SUMMARY.md)

---

### ERR-TA-02: Tool Not Found

**Symptoms:**
```
ToolNotFoundError: Command 'aider' not found in PATH
```

**Root Cause:**
- Tool not installed
- Tool not in PATH environment variable
- Wrong tool name in command

**Recovery:**
```bash
# 1. Install tool
pip install aider-chat  # For aider

# 2. Verify installation
which aider
aider --version

# 3. Add to PATH if needed
export PATH="$PATH:$HOME/.local/bin"
```

**Prevention:**
- Document tool dependencies in README
- Check tool availability at startup
- Provide installation instructions

---

### ERR-TA-03: Command Template Render Failed

**Symptoms:**
```
TemplateRenderError: Unknown variable 'instruction' in template
```

**Root Cause:**
- Missing variable in context
- Typo in template variable name
- Template syntax error

**Recovery:**
```bash
# 1. Check tool profile template
cat config/tool_profiles.json | jq '.[] | select(.tool_id=="aider")'

# 2. Verify context has required variables
# Template: "aider {files} --message '{instruction}'"
# Context must include: files, instruction

# 3. Fix template or add missing context
```

**Prevention:**
- Validate template variables at load time
- Provide default values for optional variables
- Test template rendering before execution

---

### ERR-TA-04: Tool Exit Code Unexpected

**Symptoms:**
```
UnexpectedExitCodeError: Expected 0, got 1 from pytest
```

**Root Cause:**
- Tool failed but returned non-zero exit code
- Tests failed
- Exit code not in expected_exit_codes

**Recovery:**
```bash
# 1. Check tool stdout/stderr
cat .worktrees/step_s1_output.log

# 2. If exit code is valid, add to profile
{
  "tool_id": "pytest",
  "expected_exit_codes": [0, 1]  # 1 = tests failed but ran
}

# 3. Or fix underlying issue causing failure
```

**Prevention:**
- Define all valid exit codes in profile
- Log tool output for debugging
- Handle expected failures gracefully

---

## Configuration Errors

### ERR-CF-01: Config File Not Found

**Symptoms:**
```
FileNotFoundError: config/tool_profiles.json
```

**Root Cause:**
- Config file missing
- Wrong working directory
- File not committed to repo

**Recovery:**
```bash
# 1. Check if file exists
ls config/tool_profiles.json

# 2. Copy from example if available
cp config/tool_profiles.example.json config/tool_profiles.json

# 3. Or create minimal config
echo '{"profiles": []}' > config/tool_profiles.json
```

**Prevention:**
- Commit config files to repo
- Provide example configs
- Document config file locations

---

### ERR-CF-02: Invalid JSON/YAML

**Symptoms:**
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Root Cause:**
- Syntax error in JSON/YAML
- Trailing comma
- Missing quotes

**Recovery:**
```bash
# 1. Validate JSON
python -m json.tool config/tool_profiles.json

# 2. Find syntax error
# Common issues: trailing commas, single quotes, missing braces

# 3. Fix and re-validate
```

**Prevention:**
- Use JSON/YAML linter in editor
- Validate on save
- Use schema validation

---

### ERR-CF-03: Environment Variable Not Set

**Symptoms:**
```
EnvironmentError: OPENAI_API_KEY not set
```

**Root Cause:**
- Required environment variable missing
- Wrong variable name
- .env file not loaded

**Recovery:**
```bash
# 1. Set environment variable
export OPENAI_API_KEY="sk-..."

# 2. Or create .env file (gitignored)
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Load .env in code
from dotenv import load_dotenv
load_dotenv()
```

**Prevention:**
- Document required environment variables
- Provide .env.example template
- Check for required vars at startup

**Related:** [Anti-Pattern AP-SC-03: Printing Sensitive Information](../guidelines/ANTI_PATTERNS.md#ap-sc-03-printing-sensitive-information)

---

## Error Recovery Workflow

```
Error Occurs
    ↓
Check Error Code (ERR-XX-YY)
    ↓
Read Root Cause
    ↓
Follow Recovery Steps
    ↓
Verify Fix
    ↓
Apply Prevention
    ↓
Document if New Error
```

---

## Related Documentation

- [Anti-Patterns Catalog](../guidelines/ANTI_PATTERNS.md) - Prevention patterns
- [Change Impact Matrix](../reference/CHANGE_IMPACT_MATRIX.md) - Dependencies
- [Testing Strategy](../guidelines/TESTING_STRATEGY.md) - Test error handling
- [ADRs](../adr/) - Architecture decisions

---

**Total Errors Documented:** 25
**Categories:** 6
**Last Updated:** 2025-11-22
**Next Review:** After major incidents or pattern changes
