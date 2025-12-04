---
doc_id: DOC-GUIDE-API-INDEX-834
---

# API Index – Public Interfaces & Entry Points

**Purpose**: Quick reference for all public APIs, CLIs, and programmatic entry points.

## CLI Commands

### Main Orchestrator
```bash
python -m core.orchestrator run --plan <file>
python -m core.orchestrator validate --plan <file>
python -m core.orchestrator status --run-id <id>
```

### Error Pipeline
```bash
python -m error.engine.error_engine detect --target <path>
python -m error.engine.error_engine fix --target <path>
```

### Specification Tools
```bash
python -m specifications.tools.indexer generate
python -m specifications.tools.validator validate --spec <file>
```

### Project Management
```bash
python -m pm.cli workstream create --name <name>
python -m pm.cli workstream list
python -m pm.cli workstream status --id <id>
```

### Scripts (Direct Invocation)
```bash
python scripts/validate_workstreams.py
python scripts/validate_acs_conformance.py
python scripts/generate_doc_index.py
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

## Python APIs

### Core Orchestrator
```python
from core.orchestrator import Orchestrator
from core.planner import Planner
from core.scheduler import Scheduler
from core.executor import Executor

orch = Orchestrator()
result = orch.run_plan(plan_path="path/to/plan.json")
```

### State Management
```python
from core.state.db import init_db, get_db
from core.state.models import WorkstreamState, TaskState

db = init_db()
state = WorkstreamState.load(db, workstream_id="WS-001")
```

### Error Detection
```python
from error.engine.error_engine import ErrorEngine
from error.plugins import get_plugin

engine = ErrorEngine()
errors = engine.detect(target_path="src/")
```

### Capability Catalog
```python
from aim.bridge import get_tool_info, list_capabilities

info = get_tool_info(tool_name="ruff")
caps = list_capabilities(category="linting")
```

## Configuration Interfaces

### Workstream Definition (JSON)
```json
{
  "id": "WS-001",
  "name": "Feature Implementation",
  "phases": [...],
  "dependencies": [...]
}
```

### Capability Manifest (YAML)
```yaml
capability:
  id: "python-linting"
  tools: ["ruff", "mypy"]
  mcp_services: ["python-analysis"]
```

## MCP Service Endpoints

See `aim/README.md` for full MCP service documentation.

**Reference**: See `MASTER_NAVIGATION_INDEX.md` for full module documentation.
