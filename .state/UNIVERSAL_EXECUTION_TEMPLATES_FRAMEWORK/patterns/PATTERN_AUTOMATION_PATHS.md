---
doc_id: DOC-PAT-PATTERN-AUTOMATION-PATHS-758
---

# Pattern automation paths

**Orchestrator/engine modules**
- `../core/orchestrator.py` (candidate import: `core.orchestrator`)
- `../engine/orchestrator/orchestrator.py` (import: `engine.orchestrator.orchestrator`)
- `../UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py` (import: `core.engine.orchestrator`)
- Legacy/archived variants under `../archive/**/core-engine/*.py` and `../modules/core-engine/*.py`

**Executor modules**
- `../core/executor.py` (import: `core.executor`)
- `../modules/core-engine/m010001_executor.py` (legacy variant)

**Database artifacts**
- SQLite files: `../.state/orchestrator.db`, `../.worktrees/pipeline_state.db`, `../infra/data/refactor_paths.db`
- Migration scripts: `../schema/migrations/uet_migration_001.sql`, `../schema/migrations/uet_migration_001_rollback.sql`
- DB helper modules: `../UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py`, `../archive/2025-11-26_094309_old-structure/core-state/db.py`

**Error engine**
- `../error/engine/error_engine.py` (import: `error.engine.error_engine`)
- Legacy: `../modules/error-engine/m010004_error_engine.py`
- Helper runner: `../scripts/run_error_engine.py`

**Import path notes**
- Root `patterns` parent is on disk at `C:\Users\richg\ALL_AI\Complete AI Development Pipeline - Canonical Phase Plan`.
- Directories do not have `__init__.py`, so imports assume namespace packages with the repo root on `PYTHONPATH`.

**Directory overview (top-level highlights)**
- Active roots: `core`, `engine`, `error`, `modules`, `schema`, `scripts`, `tests`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK`, `automation` (current workstream lives here).
