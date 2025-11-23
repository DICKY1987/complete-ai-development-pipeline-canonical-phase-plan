# Section Refactor Mapping

This document provides the complete old → new path mapping for the entire repository refactor.

## Date: 2025-11-18
## Refactor Phases: A through E (WS-06 through WS-21)

---

## Core Section Mappings

### State Management (WS-15)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/pipeline/db.py` | `core/state/db.py` | Database initialization and connection |
| `src/pipeline/db_sqlite.py` | `core/state/db_sqlite.py` | SQLite implementation |
| `src/pipeline/crud_operations.py` | `core/state/crud.py` | CRUD operations (renamed) |
| `src/pipeline/bundles.py` | `core/state/bundles.py` | Workstream bundle management |
| `src/pipeline/worktree.py` | `core/state/worktree.py` | Git worktree management |

### Engine/Orchestration (WS-16)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/pipeline/orchestrator.py` | `core/engine/orchestrator.py` | Main orchestrator |
| `src/pipeline/scheduler.py` | `core/engine/scheduler.py` | Workstream scheduler |
| `src/pipeline/executor.py` | `core/engine/executor.py` | Step executor |
| `src/pipeline/tools.py` | `core/engine/tools.py` | Tool invocation |
| `src/pipeline/circuit_breakers.py` | `core/engine/circuit_breakers.py` | Circuit breaker logic |
| `src/pipeline/recovery.py` | `core/engine/recovery.py` | Recovery mechanisms |

### Planning (WS-17)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/pipeline/planner.py` | `core/planning/planner.py` | Workstream planner |
| `src/pipeline/archive.py` | `core/planning/archive.py` | Archive utilities |

### Other Core Components
| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/pipeline/openspec_parser.py` | `core/openspec_parser.py` | OpenSpec parser |
| `src/pipeline/openspec_convert.py` | `core/openspec_convert.py` | OpenSpec converter |
| `src/pipeline/prompts.py` | `src/pipeline/prompts.py` | Kept in place (Aider shim) |
| `src/pipeline/spec_index.py` | `core/spec_index.py` | Spec indexing |
| `src/pipeline/agent_coordinator.py` | `core/agent_coordinator.py` | Agent coordination |

---

## Error Subsystem Mappings

### Error Shared Utils (WS-12)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `MOD_ERROR_PIPELINE/file_hash_cache.py` | `error/file_hash_cache.py` | File hash caching |

### Error Plugins (WS-13)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `MOD_ERROR_PIPELINE/plugins/` | `error/plugins/` | All plugin implementations |
| `MOD_ERROR_PIPELINE/plugin_manager.py` | `error/plugin_manager.py` | Plugin manager |

### Error Engine (WS-14)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `MOD_ERROR_PIPELINE/error_engine.py` | `error/engine/error_engine.py` | Error engine core |
| `MOD_ERROR_PIPELINE/error_state_machine.py` | `error/engine/error_state_machine.py` | State machine |
| `MOD_ERROR_PIPELINE/error_pipeline_cli.py` | `error/engine/error_pipeline_cli.py` | CLI interface |
| `MOD_ERROR_PIPELINE/error_pipeline_service.py` | `error/engine/error_pipeline_service.py` | Service layer |
| `MOD_ERROR_PIPELINE/error_context.py` | `error/engine/error_context.py` | Error context |
| `MOD_ERROR_PIPELINE/pipeline_engine.py` | `error/engine/pipeline_engine.py` | Pipeline engine |

---

## Other Section Mappings

### AIM Section (WS-06)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `src/pipeline/aim_bridge.py` | `aim/bridge.py` | AIM integration bridge |
| `.AIM_ai-tools-registry/` | `aim/.AIM_ai-tools-registry/` | AIM registry |

### PM/CCPM Section (WS-07)
| Old Path | New Path | Notes |
|----------|----------|-------|
| Scattered CCPM scripts | `pm/` | Consolidated PM tools |

### Spec Tools (WS-09)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `tools/spec_*` | `spec/tools/` | Spec validation tools |

### Aider Section (WS-08)
| Old Path | New Path | Notes |
|----------|----------|-------|
| Aider scattered files | `aider/` | Aider integration |

### Meta Section (WS-03)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `PHASE_DEV_DOCS/` | `meta/PHASE_DEV_DOCS/` | Phase documentation |
| `plans/` | `meta/plans/` | Planning documents |
| `Coordination Mechanisms/` | `meta/Coordination Mechanisms/` | Coordination guides |

### GUI Section (WS-04)
| Old Path | New Path | Notes |
|----------|----------|-------|
| GUI scattered files | `gui/` | GUI components |

### Infrastructure (WS-05)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `.github/workflows/` | `infra/ci/.github/workflows/` | CI workflows |
| CI configs | `infra/ci/` | CI configuration |

---

## Import Path Changes

### Python Imports - State
```python
# Old
from src.pipeline.db import init_db
from src.pipeline.crud_operations import create_run
from src.pipeline.bundles import load_bundle

# New
from core.state.db import init_db
from core.state.crud import create_run
from core.state.bundles import load_bundle
```

### Python Imports - Engine
```python
# Old
from src.pipeline.orchestrator import run_workstream
from src.pipeline.tools import run_tool
from src.pipeline.circuit_breakers import CircuitBreaker

# New
from core.engine.orchestrator import run_workstream
from core.engine.tools import run_tool
from core.engine.circuit_breakers import CircuitBreaker
```

### Python Imports - Error
```python
# Old
from MOD_ERROR_PIPELINE.plugin_manager import PluginManager
from MOD_ERROR_PIPELINE.pipeline_engine import PipelineEngine

# New
from error.plugin_manager import PluginManager
from error.engine.pipeline_engine import PipelineEngine
```

### Python Imports - AIM
```python
# Old
from src.pipeline.aim_bridge import invoke_adapter

# New
from aim.bridge import invoke_adapter
```

---

## Backward Compatibility

All old import paths remain functional via **shim files** during the migration period:

- `src/pipeline/*.py` - Re-exports from `core.*`
- `MOD_ERROR_PIPELINE/*.py` - Re-exports from `error.*`
- `core/*.py` (top-level) - Re-exports from `core.*` subpackages

Example shim:
```python
"""db - Compatibility Shim

This module has been moved to core/state/db
This shim provides backward compatibility during the refactor.
"""

from core.state.db import *  # noqa: F401, F403
```

---

## Directory Structure After Refactor

```
.
├── core/
│   ├── state/          # WS-15: Database, CRUD, bundles, worktree
│   ├── engine/         # WS-16: Orchestrator, scheduler, executor, tools
│   ├── planning/       # WS-17: Planner, archive
│   └── *.py           # Other core modules (openspec, prompts, etc.)
├── error/
│   ├── engine/         # WS-14: Error engine core
│   ├── plugins/        # WS-13: Plugin implementations
│   └── *.py           # Shared utils (file_hash_cache, plugin_manager)
├── aim/               # WS-06: AIM integration
├── aider/             # WS-08: Aider integration
├── pm/                # WS-07: PM/CCPM tools
├── spec/              # WS-09: Spec tools
├── gui/               # WS-04: GUI components
├── infra/             # WS-05: Infrastructure/CI
├── meta/              # WS-03: Meta documentation
├── src/pipeline/      # Shims for backward compatibility
└── MOD_ERROR_PIPELINE/ # Shims for backward compatibility
```

---

## Verification Checklist

- [x] All core modules moved to `core/` subdirectories
- [x] All error modules moved to `error/` subdirectories
- [x] All imports updated in scripts/
- [x] All imports updated in tests/
- [x] Shim files created for backward compatibility
- [x] Git history preserved via `git mv`
- [x] Acceptance tests passing for each workstream
- [x] Documentation updated

---

## Migration Status: COMPLETE

All 21 workstreams (WS-01 through WS-21) have been executed successfully.
Phase D (Core Extraction) completed: 2025-11-18
