# UET Migration Guide
**Version**: 1.0.0 | **Date**: 2025-11-25

## Phases Completed
- PHASE_0: Template Library ✅
- PHASE_1: Foundation ✅
- PHASE_2: Parallel Execution ✅
- PHASE_3: Patch Management ✅
- PHASE_4: Integration Testing ✅
- PHASE_5: Cutover Documentation ✅

## Quick Start
```powershell
$env:PIPELINE_ENGINE = "uet"
python -m core.cli run-phase phase-01 --parallel=4
```

## Rollback
```powershell
$env:PIPELINE_ENGINE = "legacy"
sqlite3 .worktrees/pipeline_state.db < schema/migrations/uet_migration_001_rollback.sql
```
