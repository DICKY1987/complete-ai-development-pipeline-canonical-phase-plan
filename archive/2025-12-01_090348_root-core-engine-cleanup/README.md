# Archived Files - 2025-12-01_090348

**Purpose**: UET Migration Cleanup - Remove duplicate files

## Summary

- **Date**: 2025-12-01 09:03:48
- **Reason**: Duplicate files (canonical versions in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK)
- **Files Archived**: 22 files from core/engine/
- **Status**: All files safely preserved

## Files Archived

### core/engine/ (22 files)
- recovery.py
- worker_lifecycle.py
- patch_converter.py
- execution_request_builder.py
- cost_tracker.py
- dag_builder.py
- process_spawner.py
- resilience/circuit_breaker.py
- resilience/__init__.py
- monitoring/__init__.py
- monitoring/progress_tracker.py
- patch_ledger.py
- prompt_engine.py
- state_machine.py
- resilience/retry.py
- context_estimator.py
- resilience/resilient_executor.py
- circuit_breakers.py
- __init__.py
- tools.py
- integration_worker.py
- router.py

## Canonical Versions

All canonical (production) versions exist in:
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/
```

## Restoration

If restoration is needed:
```bash
git checkout pre-uet-migration-20251201
```

Or restore individual files:
```bash
cp archive/2025-12-01_090348_root-core-engine-cleanup/core/engine/[file] core/engine/
```

## Migration Context

- Part of: UET Migration Week 2 (Option B - Quick Archive)
- Branch: feature/uet-migration-completion  
- Previous work: 74 files migrated on Nov 29, 2025
- This cleanup: Final 22 duplicate files archived
- Result: Zero duplicates achieved ✅

---

**Created**: 2025-12-01 15:03 UTC  
**Migration Phase**: Week 2 - Cleanup Complete
