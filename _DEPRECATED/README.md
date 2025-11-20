# Deprecated Code Archive

This directory contains all legacy shim files and deprecated code consolidated from the repository.

## Migration Date
2025-11-20

## ⚠️ CRITICAL WARNING

**DO NOT move files to this directory yet!** There are 40+ files still using legacy `src.` imports that will break if the shims are removed.

## Current Status: BLOCKED

### Prerequisites Before Migration
1. ✅ Identify all legacy import references (DONE - 40+ files found)
2. ❌ Update all imports to use new paths (REQUIRED)
3. ❌ Run full test suite to verify (REQUIRED)
4. ❌ Move shims to `_DEPRECATED/` (BLOCKED)
5. ❌ Delete `_DEPRECATED/` after confirmation (BLOCKED)

## Files Blocking Migration (40+ files)

### Active Code Using `src.pipeline.*`
- `core/agent_coordinator.py`
- `core/engine/orchestrator.py`
- `core/prompts.py`
- `core/openspec_parser.py`
- `core/openspec_convert.py`
- `core/error_pipeline_service.py`
- `core/error_context.py`
- `core/spec_index.py`
- `aider/engine.py`
- `src/orchestrator/parallel.py`

### Plugins Using Legacy Imports (15+ files)
- `src/plugins/*/plugin.py` (all plugin implementations)

### Tests Using Legacy Imports (10+ files)
- `tests/plugins/*.py`
- `tests/test_spec_validator.py`
- `tests/test_path_standardizer.py`

### Scripts Using Legacy Imports
- `scripts/migrate_imports.py`
- `scripts/gh_issue_update.py`
- `scripts/gh_epic_sync.py`

## Recommended Migration Strategy

### Option 1: Automated Import Update (RECOMMENDED)
```powershell
# 1. Create import migration script
python scripts/create_import_migrator.py

# 2. Run automated migration
python scripts/auto_migrate_imports.py --dry-run  # Preview changes
python scripts/auto_migrate_imports.py            # Apply changes

# 3. Verify
pytest -q

# 4. Move shims to _DEPRECATED
pwsh scripts/consolidate_legacy_code.ps1
```

### Option 2: Manual Migration
Use the import mapping guide below to manually update each file.

## Import Migration Reference

### State Management
```python
# OLD (deprecated)
from src.pipeline.db import init_db
from src.pipeline.crud_operations import create_run
from src.pipeline.bundles import load_bundle
from src.pipeline.worktree import setup_worktree

# NEW (current)
from core.state.db import init_db
from core.state.crud import create_run
from core.state.bundles import load_bundle
from core.state.worktree import setup_worktree
```

### Engine/Orchestration
```python
# OLD (deprecated)
from src.pipeline.orchestrator import run_workstream
from src.pipeline.scheduler import schedule_workstream
from src.pipeline.executor import execute_step
from src.pipeline.tools import run_tool
from src.pipeline.circuit_breakers import CircuitBreaker
from src.pipeline.recovery import recover_step

# NEW (current)
from core.engine.orchestrator import run_workstream
from core.engine.scheduler import schedule_workstream
from core.engine.executor import execute_step
from core.engine.tools import run_tool
from core.engine.circuit_breakers import CircuitBreaker
from core.engine.recovery import recover_step
```

### Planning
```python
# OLD (deprecated)
from src.pipeline.planner import generate_workstream
from src.pipeline.archive import archive_workstream

# NEW (current)
from core.planning.planner import generate_workstream
from core.planning.archive import archive_workstream
```

### Error Detection
```python
# OLD (deprecated)
from src.pipeline.error_engine import ErrorEngine
from src.pipeline.error_state_machine import ErrorStateMachine
from src.pipeline.error_pipeline_cli import run_error_cli

# NEW (current)
from error.engine.error_engine import ErrorEngine
from error.engine.error_state_machine import ErrorStateMachine
from error.engine.error_pipeline_cli import run_error_cli
```

### Plugins
```python
# OLD (deprecated)
from src.plugins.python_ruff import RuffPlugin

# NEW (current)
from error.plugins.python_ruff import RuffPlugin
```

### AIM Integration
```python
# OLD (deprecated)
from src.pipeline.aim_bridge import invoke_adapter

# NEW (current)
from aim.bridge import invoke_adapter
```

## Planned Directory Structure (After Migration)

```
_DEPRECATED/
├── README.md (this file)
├── src/
│   ├── pipeline/          # 24 shim files
│   ├── plugins/           # Plugin shims
│   ├── integrations/      # Integration shims
│   ├── utils/             # Utility shims
│   └── orchestrator/      # Orchestrator utilities
├── core_shims/
│   ├── aim_bridge.py
│   ├── bundles.py
│   ├── crud_operations.py
│   ├── db.py
│   ├── db_sqlite.py
│   └── worktree.py
└── error_shims/
    ├── file_hash_cache.py
    ├── pipeline_engine.py
    └── plugin_manager.py
```

## Verification Commands

```powershell
# Find all remaining legacy imports
rg "from src\.(pipeline|plugins|integrations|utils)" --type py

# Run tests
pytest -q

# Check import health
python -m scripts.validate_imports
```

## DO NOT PROCEED until all imports are updated!
