# UET Framework Dependency Graph

## Dependency Layers

The UET framework follows a strict layered architecture where dependencies flow downward only. Higher layers may depend on lower layers, but never the reverse.

### Layer 0: Foundation (No Dependencies)

**`schema/`** - JSON Schema definitions
- Purpose: Type contracts for all operations
- Dependencies: None
- Used by: All modules for validation

**`core/state/`** - State management
- Purpose: Run state persistence, checkpoint management
- Dependencies: None (SQLite standard library)
- Used by: engine, bootstrap, adapters

### Layer 1: Domain Logic

**`core/adapters/`** - Tool integration layer
- Purpose: Execute external tools (CLI, API)
- Dependencies: 
  - `schema/` (execution_request.v1.json)
  - `core/state/` (for logging)
- Used by: `core/engine/`

**`core/engine/resilience/`** - Fault tolerance
- Purpose: Circuit breakers, retry logic, exponential backoff
- Dependencies:
  - `core/state/` (state tracking)
- Used by: `core/engine/`

**`core/engine/monitoring/`** - Progress tracking
- Purpose: Real-time metrics, ETA calculation
- Dependencies:
  - `core/state/` (run state)
- Used by: `core/engine/`

**`core/bootstrap/`** - Project discovery
- Purpose: Analyze projects, select profiles, generate config
- Dependencies:
  - `schema/` (profile.v1.json, router_config.v1.json)
  - `core/state/` (bootstrap state)
  - `profiles/` (templates)
- Used by: CLI entry points

### Layer 2: Orchestration Engine

**`core/engine/`** - Task orchestration
- Purpose: Routing, scheduling, execution coordination
- Dependencies:
  - `core/adapters/` (tool execution)
  - `core/engine/resilience/` (fault tolerance)
  - `core/engine/monitoring/` (progress tracking)
  - `core/state/` (run management)
  - `schema/` (task_spec.v1.json, phase_spec.v1.json)
- Used by: Bootstrap orchestrator, external callers

### Layer 3: Configuration & Templates

**`profiles/`** - Project type templates
- Purpose: Pre-built configurations for common project types
- Dependencies:
  - `schema/` (profile.v1.json structure)
- Used by: `core/bootstrap/`

### Layer 4: Testing (Horizontal, No Production Dependencies)

**`tests/`** - Test suites
- Purpose: Validate all modules
- Dependencies: All modules (test-only)
- Used by: CI/CD, developers

## Module Dependency Matrix

```
                    schema  state  adapters  resilience  monitoring  bootstrap  engine  profiles
schema              -       -      -         -           -           -          -       -
state               ✓       -      -         -           -           -          -       -
adapters            ✓       ✓      -         -           -           -          -       -
resilience          ✓       ✓      -         -           -           -          -       -
monitoring          ✓       ✓      -         -           -           -          -       -
bootstrap           ✓       ✓      -         -           -           -          -       ✓
engine              ✓       ✓      ✓         ✓           ✓           -          -       -
profiles            ✓       -      -         -           -           -          -       -
```

Legend:
- ✓ = Direct dependency
- - = No dependency

## Detailed Module Dependencies

### core/state/
```python
# External dependencies
import sqlite3  # Standard library
import json     # Standard library
import uuid     # Standard library

# Internal dependencies
None
```

### core/adapters/
```python
# External dependencies
import subprocess  # Standard library
import requests    # Third-party (for API adapters)

# Internal dependencies
from core.state import StateManager
from schema import validate_execution_request
```

### core/engine/resilience/
```python
# External dependencies
import time     # Standard library
import logging  # Standard library

# Internal dependencies
from core.state import StateManager
```

### core/engine/monitoring/
```python
# External dependencies
import time       # Standard library
from datetime import datetime, timedelta

# Internal dependencies
from core.state import RunState, TaskState
```

### core/bootstrap/
```python
# External dependencies
import os
import pathlib
from typing import Dict, List

# Internal dependencies
from core.state import StateManager
from schema import validate_profile, validate_router_config
# Reads from profiles/ directory
```

### core/engine/
```python
# External dependencies
from collections import defaultdict, deque
from typing import List, Dict, Set, Optional

# Internal dependencies
from core.adapters import AdapterRegistry, SubprocessAdapter
from core.engine.resilience import ResilientExecutor, CircuitBreaker
from core.engine.monitoring import ProgressTracker, MetricsCollector
from core.state import RunManager, TaskState
from schema import validate_task_spec, validate_phase_spec
```

## Import Path Rules

All imports MUST use the section-based format:

✅ **Correct:**
```python
from core.state.db import init_db
from core.engine.scheduler import ExecutionScheduler
from core.adapters.subprocess_adapter import SubprocessAdapter
```

❌ **Forbidden:**
```python
from src.pipeline.db import init_db              # Deprecated path
from MOD_ERROR_PIPELINE.engine import Engine     # Wrong section
from legacy.anything import anything             # Never import legacy
```

## Circular Dependency Prevention

### Rules
1. **Never import upward** - Lower layers cannot import from higher layers
2. **Use dependency injection** - Pass dependencies as constructor arguments
3. **Use protocols for abstractions** - Define interfaces to break cycles
4. **Event-based communication** - Use callbacks/events for cross-module communication

### Example: Breaking a Circular Dependency
```python
# ❌ Bad: engine imports bootstrap, bootstrap imports engine
# core/engine/orchestrator.py
from core.bootstrap.scanner import ProjectScanner  # Upward import!

# ✅ Good: Use dependency injection
# core/engine/orchestrator.py
class Orchestrator:
    def __init__(self, scanner: ProjectScanner):  # Inject dependency
        self.scanner = scanner

# core/bootstrap/main.py
from core.engine.orchestrator import Orchestrator
from core.bootstrap.scanner import ProjectScanner

scanner = ProjectScanner()
orchestrator = Orchestrator(scanner)  # Inject downward
```

## External Dependencies (Third-Party)

### Production Dependencies
```
# Core execution
pydantic>=2.0.0         # Schema validation (alternative to jsonschema)
jsonschema>=4.0.0       # JSON schema validation

# State management
sqlalchemy>=2.0.0       # Database ORM (optional, currently using raw sqlite3)

# Tool adapters
requests>=2.28.0        # HTTP client for API adapters
python-ulid>=1.1.0      # ULID generation for checkpoints
```

### Development Dependencies
```
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code quality
ruff>=0.1.0            # Linting and formatting
mypy>=1.5.0            # Type checking

# Documentation
mkdocs>=1.5.0          # Documentation generation
```

## Dependency Installation

```bash
# Production dependencies only
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Specific adapters (optional)
pip install requests          # For API adapters
pip install python-ulid       # For checkpoint system
```

## Dependency Update Policy

1. **Schema changes**: Require major version bump
2. **State format changes**: Require migration scripts
3. **API changes**: Follow semantic versioning
4. **Internal refactoring**: No version change if public API unchanged

## Validation

### Check for Circular Dependencies
```bash
# Using pydeps (install: pip install pydeps)
pydeps core --show-cycles

# Expected output: No cycles found
```

### Validate Import Paths
```bash
# Run the path validation gate (CI check)
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Expected: All imports use section-based paths
```

## References

- **Module structure**: See `CODEBASE_INDEX.yaml`
- **Import standards**: See `docs/CI_PATH_STANDARDS.md`
- **Architecture overview**: See `ARCHITECTURE.md`
