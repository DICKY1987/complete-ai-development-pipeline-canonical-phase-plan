# Dependency Index – Module Relationships

**Purpose**: Map dependencies between modules and layers.

## Dependency Layers (Low → High)

```
Layer 1: Infrastructure
  └─ infra/ (no dependencies)

Layer 2: Domain Core
  ├─ core/ (depends on: infra)
  ├─ error/ (depends on: infra)
  ├─ aim/ (depends on: infra)
  └─ pm/ (depends on: infra)

Layer 3: Tools & API
  ├─ specifications/ (depends on: infra, core)
  ├─ engine/ (depends on: infra, core)
  └─ scripts/ (depends on: infra, core, error, aim, pm)

Layer 4: UI & External
  └─ gui/ (depends on: all layers)
```

## Module Dependency Graph

### core/ Dependencies
```
core/
├─ Uses: infra/
├─ Provides: Orchestrator, Planner, Scheduler, Executor
└─ Used by: engine/, pm/, specifications/, scripts/
```

### error/ Dependencies
```
error/
├─ Uses: infra/
├─ Provides: ErrorEngine, error detection plugins
└─ Used by: core/, scripts/
```

### aim/ Dependencies
```
aim/
├─ Uses: infra/
├─ Provides: MCP service bridge, capability catalog
└─ Used by: core/, engine/
```

### pm/ Dependencies
```
pm/
├─ Uses: infra/, core/state
├─ Provides: Workstream management, checkpoint system
└─ Used by: scripts/, gui/
```

### specifications/ Dependencies
```
specifications/
├─ Uses: infra/, core/
├─ Provides: Spec validation, indexer tools
└─ Used by: core/planner, scripts/
```

### engine/ Dependencies
```
engine/
├─ Uses: infra/, core/, aim/
├─ Provides: Job execution engine
└─ Used by: core/orchestrator
```

## Critical Import Paths (CI Enforced)

### ✅ Allowed Patterns
```python
from core.state.db import init_db
from core.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse
from aim.bridge import get_tool_info
from pm.workstream_manager import create_workstream
from specifications.tools.indexer import generate_index
```

### ❌ Forbidden Patterns (CI Blocks)
```python
from src.pipeline.*           # Deprecated
from MOD_ERROR_PIPELINE.*     # Deprecated
from legacy.*                 # Never import
```

## External Dependencies

**Runtime Requirements** (from `requirements.txt`):
- pydantic (data validation)
- ulid-py (unique identifiers)
- jsonschema (spec validation)
- click (CLI framework)

**Development Requirements**:
- pytest (testing)
- mypy (type checking)
- ruff (linting)

## Circular Dependency Prevention

**Forbidden**:
- `core/` importing from `pm/`
- `error/` importing from `core/`
- `infra/` importing from any domain layer

**Allowed Communication**:
- Via events (publish/subscribe)
- Via shared state (database)
- Via interfaces (abstract base classes)

## Dependency Validation

**Check dependencies**:
```bash
python scripts/validate_acs_conformance.py
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

**Update dependency graph**:
```bash
python scripts/generate_dependency_graph.py
```

**Reference**: See `CODEBASE_INDEX.yaml` for complete module structure.
