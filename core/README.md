# core

**Module Path**: `core`
**Layer**: Domain
**Status**: Active

## Purpose

Core framework components including state management, execution engine, and bootstrap orchestration

## Contents

- `__init__.py` - File
- `adapters/` - Directory
- `ast/` - Directory
- `bootstrap/` - Directory
- `engine/` - Directory
- `planning/` - Directory
- `state/` - Directory
- `ui_cli.py` - File
- `ui_models.py` - File
- `ui_settings.py` - File
- `ui_settings_cli.py` - File

## Key Components

- `state/` - SQLite persistence and state management
- `engine/` - Task orchestration and execution engine
- `bootstrap/` - Auto-discovery and project configuration


## Dependencies

schema/ (foundation layer)

## Usage

```python
from core.engine.orchestrator import Orchestrator
from core.state.db import init_db
```


## Integration Points

Foundation for all domain and orchestration layers

## Related Documentation

CODEBASE_INDEX.yaml, ENGINE_ORCHESTRATOR_GUIDE.md

---

**Generated**: 2025-12-02 22:40:27 UTC
**Framework**: Universal Execution Templates (UET)
