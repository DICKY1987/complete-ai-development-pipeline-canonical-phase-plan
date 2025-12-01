---
doc_id: DOC-CORE-README-058
---

# Core Pipeline Implementation

> **Purpose**: Core pipeline functionality - state management, orchestration, and planning  
> **Last Updated**: 2025-11-22  
> **Status**: Production

---

## Overview

The `core/` directory contains the heart of the AI development pipeline system. It provides:
- State management and persistence
- Workstream orchestration and execution
- Planning and archive utilities
- OpenSpec integration

## Directory Structure

```
core/
├── state/              # State management
│   ├── db.py          # Database initialization and connection
│   ├── crud.py        # CRUD operations
│   ├── bundles.py     # Bundle loading and validation
│   └── worktree.py    # Worktree lifecycle management
│
├── engine/            # Orchestration and execution
│   ├── orchestrator.py    # Main orchestrator
│   ├── scheduler.py       # Task scheduling
│   ├── executor.py        # Step execution
│   ├── tools.py          # Tool adapter
│   ├── circuit_breaker.py # Circuit breaker patterns
│   └── recovery.py        # Recovery strategies
│
├── planning/          # Workstream planning
│   ├── planner.py     # Workstream generation
│   └── archive.py     # Archive operations
│
└── openspec_parser.py # OpenSpec integration
```

## Key Components

### State Management (`state/`)

Handles all database operations and state persistence.

**Database Location**: `.worktrees/pipeline_state.db` (configurable via `PIPELINE_DB_PATH`)

**Key Functions**:
- `init_db()` - Initialize database connection
- `create_workstream()` - Create new workstream
- `get_workstream()` - Retrieve workstream by ID
- `update_workstream()` - Update workstream state
- `load_bundle()` - Load workstream bundle from JSON

**Import Pattern**:
```python
from core.state.db import init_db
from core.state.crud import get_workstream, create_workstream
from core.state.bundles import load_bundle
```

### Orchestration (`engine/`)

Coordinates workstream execution with retry logic, circuit breakers, and recovery.

**Key Classes**:
- `Orchestrator` - Main orchestration logic
- `Scheduler` - Task scheduling and dependency resolution
- `Executor` - Step execution with timeout handling
- `CircuitBreaker` - Fault tolerance patterns

**Import Pattern**:
```python
from core.engine.orchestrator import Orchestrator
from core.engine.scheduler import Scheduler
```

### Planning (`planning/`)

Generates and manages workstream plans.

**Key Functions**:
- `generate_workstream()` - Create workstream from spec
- `archive_workstream()` - Archive completed work

**Import Pattern**:
```python
from core.planning.planner import generate_workstream
```

## Usage Examples

### Initialize and Run a Workstream

```python
from core.state.db import init_db
from core.state.crud import get_workstream
from core.engine.orchestrator import Orchestrator

# Initialize database
init_db()

# Load workstream
ws = get_workstream("ws-001")

# Create and run orchestrator
orchestrator = Orchestrator()
result = orchestrator.run(ws)
```

### Load a Workstream Bundle

```python
from core.state.bundles import load_bundle

# Load from JSON file
bundle = load_bundle("workstreams/example-workstream.json")
```

## Testing

Tests for core functionality are in:
- `tests/pipeline/` - Pipeline tests
- `tests/integration/` - Integration tests
- `tests/unit/` - Unit tests (if present)

Run tests:
```bash
pytest tests/pipeline/ -v
```

## Related Documentation

- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository navigation
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md) - Import path mapping

## Migration Notes

This directory structure was established in Phase E refactor. Old import paths:

❌ **Deprecated**:
```python
from src.pipeline.db import init_db
from src.pipeline.orchestrator import Orchestrator
```

✅ **Current**:
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
```

See [docs/CI_PATH_STANDARDS.md](../docs/CI_PATH_STANDARDS.md) for CI enforcement details.

---

**For AI Tools**: This is a HIGH priority directory - core business logic that should always be indexed.
