# Core State Management

> **Module**: `core.state`  
> **Purpose**: Database, CRUD operations, bundle management, and worktree lifecycle  
> **Layer**: Data/Persistence  
> **Status**: Production

---

## Overview

The `core/state/` module provides centralized state management and persistence for the AI development pipeline. It handles:

- **Database operations** - SQLite connection management and schema initialization
- **CRUD operations** - Create, read, update operations for runs, workstreams, steps, errors, and events
- **Bundle management** - Load, validate, and sync workstream bundles from JSON
- **Worktree lifecycle** - Create and manage per-workstream working directories

All state is persisted to a SQLite database with foreign key constraints and transactional integrity.

---

## Directory Structure

```
core/state/
├── db.py              # Database initialization and connection management
├── db_sqlite.py       # SQLite-specific operations
├── crud.py            # CRUD operations for all entities
├── bundles.py         # Workstream bundle loading and validation
├── worktree.py        # Git worktree helpers
├── audit_logger.py    # Audit logging for state changes
└── task_queue.py      # Task queue management
```

---

## Database Schema

**Database Location**: `.worktrees/pipeline_state.db` (configurable via `PIPELINE_DB_PATH`)

### Core Tables

- **runs** - Top-level execution runs
  - `run_id` (PK), `status`, `created_at`, `updated_at`, `metadata_json`
  
- **workstreams** - Individual workstream instances
  - `ws_id` (PK), `run_id` (FK), `status`, `gate`, `bundle_json`, timestamps
  
- **step_attempts** - Execution attempts for each step
  - `id` (PK), `run_id`, `ws_id`, `step_name`, `status`, `started_at`, `completed_at`, `result_json`
  
- **errors** - Error records for debugging
  - `id` (PK), `run_id`, `ws_id`, `step_name`, `error_code`, `message`, timestamps
  
- **events** - Audit trail of all state transitions
  - `id` (PK), `event_type`, `run_id`, `ws_id`, `timestamp`, `payload_json`

### Schema Management

Schema is defined in `schema/schema.sql` and applied idempotently via `init_db()`.

---

## Key Components

### Database Management (`db.py`)

Handles connection lifecycle and schema initialization.

**Core Functions**:

```python
from core.state.db import init_db, get_connection

# Initialize database (idempotent)
init_db()

# Get connection with foreign keys enabled
conn = get_connection()
```

**Environment Variables**:
- `PIPELINE_DB_PATH` - Override default database path (preferred)
- `ERROR_PIPELINE_DB` - Legacy compatibility path

**Resolution Priority**:
1. Explicit `db_path` parameter
2. `PIPELINE_DB_PATH` environment variable
3. `ERROR_PIPELINE_DB` environment variable (legacy)
4. Default: `.worktrees/pipeline_state.db`

---

### CRUD Operations (`crud.py`)

Provides transactional operations for all entities. All timestamps are UTC ISO 8601.

#### Run Operations

```python
from core.state.crud import create_run, get_run, update_run_status

# Create a new run
run = create_run(
    run_id="run-2025-11-22-001",
    status="pending",
    metadata={"user": "developer", "branch": "main"}
)

# Get run by ID
run = get_run("run-2025-11-22-001")

# Update run status
update_run_status("run-2025-11-22-001", "running")
```

#### Workstream Operations

```python
from core.state.crud import create_workstream, get_workstream, update_workstream_status

# Create workstream
ws = create_workstream(
    ws_id="ws-feature-auth",
    run_id="run-2025-11-22-001",
    gate=2,
    bundle={"tasks": ["Implement auth"], "files_scope": ["src/auth.py"]}
)

# Get workstream
ws = get_workstream("ws-feature-auth")

# Update status
update_workstream_status("ws-feature-auth", "editing")
```

#### Step Attempt Tracking

```python
from core.state.crud import record_step_attempt, get_step_attempts

# Record step execution
record_step_attempt(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    step_name="edit",
    status="success",
    started_at="2025-11-22T10:00:00Z",
    completed_at="2025-11-22T10:05:00Z",
    result={"files_modified": 3, "tool": "aider"}
)

# Get all attempts for a step
attempts = get_step_attempts("run-2025-11-22-001", "ws-feature-auth", "edit")
```

#### Error Recording

```python
from core.state.crud import record_error, get_errors_for_step

# Record error
record_error(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    step_name="static",
    error_code="LINT_E501",
    message="Line too long (85 > 79 characters)"
)

# Get errors
errors = get_errors_for_step("run-2025-11-22-001", "ws-feature-auth", "static")
```

#### Event Logging

```python
from core.state.crud import record_event, get_events

# Record event
record_event(
    event_type="step_start",
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    payload={"step": "edit", "tool": "aider"}
)

# Get all events for a run
events = get_events(run_id="run-2025-11-22-001")
```

---

### Bundle Management (`bundles.py`)

Loads and validates workstream bundles from JSON files.

#### Data Structures

```python
from core.state.bundles import WorkstreamBundle

bundle = WorkstreamBundle(
    id="ws-feature-auth",
    openspec_change="OS-AUTH-001",
    ccpm_issue=42,
    gate=2,
    files_scope=("src/auth.py", "tests/test_auth.py"),
    files_create=("src/auth_config.py",),
    tasks=("Implement JWT authentication", "Add unit tests"),
    acceptance_tests=("pytest tests/test_auth.py",),
    depends_on=("ws-db-setup",),
    tool="aider",
    parallel_ok=True,
    conflict_group="auth",
    priority="foreground"
)
```

#### Loading and Validation

```python
from core.state.bundles import load_and_validate_bundles, get_workstream_dir

# Get workstream directory (respects PIPELINE_WORKSTREAM_DIR)
ws_dir = get_workstream_dir()

# Load and validate bundles from directory
bundles = load_and_validate_bundles(ws_dir)

# Bundles are validated for:
# - Required fields (id, openspec_change, ccpm_issue, gate, files_scope)
# - ID format (ws-[a-z0-9-]+)
# - Gate range (1-10)
# - Dependency resolution
# - Cycle detection
# - File scope overlap detection
```

#### Dependency Analysis

```python
from core.state.bundles import build_dependency_graph, detect_cycles

# Build dependency graph
graph = build_dependency_graph(bundles)
# Returns: Dict[str, List[str]] - ws_id -> [dependent_ws_ids]

# Detect cycles
cycles = detect_cycles(graph)
if cycles:
    raise BundleCycleError(f"Dependency cycle detected: {cycles}")
```

#### Database Sync

```python
from core.state.bundles import sync_bundles_to_db

# Sync validated bundles to database
sync_bundles_to_db(bundles, run_id="run-2025-11-22-001")
```

#### Exceptions

```python
from core.state.bundles import (
    BundleValidationError,      # Invalid bundle structure
    BundleDependencyError,      # Missing dependency
    BundleCycleError,          # Circular dependency
    FileScopeOverlapError      # Overlapping file scopes
)
```

---

### Worktree Management (`worktree.py`)

Creates and validates per-workstream working directories.

```python
from core.state.worktree import (
    get_repo_root,
    get_worktrees_base,
    create_worktree_for_ws,
    validate_scope
)

# Get repository root (searches for .git)
repo_root = get_repo_root()

# Get worktrees base directory (.worktrees/)
base = get_worktrees_base()

# Create worktree for workstream
wt_path = create_worktree_for_ws(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth"
)
# Returns: "/path/to/repo/.worktrees/ws-feature-auth"

# Validate file scope (stub for Phase 5)
ok, violations = validate_scope(
    worktree_path=wt_path,
    allowed_paths=["src/auth.py", "tests/test_auth.py"]
)
```

**Note**: Current implementation creates directories only. Full `git worktree` integration is planned for a future phase.

---

## Usage Patterns

### Complete Workflow Example

```python
from core.state.db import init_db
from core.state.crud import create_run, create_workstream, record_step_attempt
from core.state.bundles import load_and_validate_bundles, sync_bundles_to_db
from core.state.worktree import create_worktree_for_ws

# 1. Initialize database
init_db()

# 2. Create run
run_id = "run-2025-11-22-001"
create_run(run_id, status="pending", metadata={"user": "developer"})

# 3. Load and validate bundles
bundles = load_and_validate_bundles("workstreams/examples")

# 4. Sync to database
sync_bundles_to_db(bundles, run_id)

# 5. Create worktree for each workstream
for bundle in bundles:
    ws_id = bundle.id
    wt_path = create_worktree_for_ws(run_id, ws_id)
    
    # 6. Record execution
    record_step_attempt(
        run_id=run_id,
        ws_id=ws_id,
        step_name="edit",
        status="success",
        started_at="2025-11-22T10:00:00Z",
        completed_at="2025-11-22T10:05:00Z",
        result={"worktree_path": wt_path}
    )
```

---

## Testing

Tests are located in `tests/pipeline/` and cover:

- Database initialization and connection pooling
- CRUD operations with transactional integrity
- Bundle validation and dependency resolution
- Worktree creation and path resolution

```bash
# Run state management tests
pytest tests/pipeline/test_crud.py -v
pytest tests/pipeline/test_bundles.py -v
```

---

## Configuration

### Environment Variables

- **`PIPELINE_DB_PATH`** - Override database location (default: `.worktrees/pipeline_state.db`)
- **`PIPELINE_WORKSTREAM_DIR`** - Override workstream bundle directory (default: `workstreams/`)
- **`ERROR_PIPELINE_DB`** - Legacy database path (backward compatibility)

### Schema Versioning

Schema is versioned via SQL migrations in `schema/migrations/`. Future schema changes will use migration scripts for backward compatibility.

---

## Best Practices

1. **Always call `init_db()` before database operations** - Ensures schema is current
2. **Use context managers for transactions** - Ensures rollback on errors
3. **Validate bundles before sync** - Catch issues early in the pipeline
4. **Use UTC timestamps** - All timestamps are ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`)
5. **Check for cycles** - Always validate dependency graphs before execution

---

## Migration from Legacy

Legacy import paths are deprecated and will be removed in a future release:

```python
# ❌ DEPRECATED - Do not use
from src.pipeline.db import init_db
from src.pipeline.crud import create_run

# ✅ USE INSTEAD
from core.state.db import init_db
from core.state.crud import create_run
```

See `docs/CI_PATH_STANDARDS.md` for CI enforcement details.

---

## Related Documentation

- **Schema**: `schema/schema.sql` - Database schema definition
- **Bundle Format**: `schema/workstream_bundle.schema.json` - JSON schema for bundles
- **Architecture**: `docs/architecture/state-management.md` - Design decisions
- **Parent Module**: `core/README.md` - Core pipeline overview
