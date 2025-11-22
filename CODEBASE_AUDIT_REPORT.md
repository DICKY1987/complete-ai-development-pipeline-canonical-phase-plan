# Codebase Audit Report

**Generated:** 2025-11-22T14:28:48.764816

## Summary

- **Deprecated files:** 0
- **Legacy directories:** 0
- **Temporary/backup files:** 2
- **Potential duplicates:** 37
- **Outdated documentation:** 27
- **Potentially obsolete:** 41

## Temporary/Backup Files

- `create_backup_20251120_125719.ps1` - Delete or move to archive
- `__tmp_o.py` - Delete or move to archive

## Potential Duplicates

### `bridge.py`
Found in:
- pm/bridge.py
- aim/bridge.py

**Recommendation:** Review for consolidation or clarify purpose

### `recovery.py`
Found in:
- scripts/recovery.py
- core/recovery.py
- core/engine/recovery.py

**Recommendation:** Review for consolidation or clarify purpose

### `test_adapters.py`
Found in:
- scripts/test_adapters.py
- tests/test_adapters.py

**Recommendation:** Review for consolidation or clarify purpose

### `__main__.py`
Found in:
- aim/__main__.py
- engine/queue/__main__.py
- engine/orchestrator/__main__.py

**Recommendation:** Review for consolidation or clarify purpose

### `types.py`
Found in:
- engine/types.py
- error/shared/utils/types.py

**Recommendation:** Review for consolidation or clarify purpose

### `config_loader.py`
Found in:
- core/config_loader.py
- aim/registry/config_loader.py

**Recommendation:** Review for consolidation or clarify purpose

### `orchestrator.py`
Found in:
- core/orchestrator.py
- engine/orchestrator/orchestrator.py
- core/engine/orchestrator.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/orchestrator.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py

**Recommendation:** Review for consolidation or clarify purpose

### `error_pipeline_service.py`
Found in:
- core/error_pipeline_service.py
- error/engine/error_pipeline_service.py

**Recommendation:** Review for consolidation or clarify purpose

### `scheduler.py`
Found in:
- core/scheduler.py
- core/engine/scheduler.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py

**Recommendation:** Review for consolidation or clarify purpose

### `error_context.py`
Found in:
- core/error_context.py
- error/engine/error_context.py

**Recommendation:** Review for consolidation or clarify purpose

### `tools.py`
Found in:
- core/tools.py
- aim/cli/commands/tools.py
- core/engine/tools.py

**Recommendation:** Review for consolidation or clarify purpose

### `test_patch_manager.py`
Found in:
- tests/test_patch_manager.py
- AGENTIC_DEV_PROTOTYPE/tests/test_patch_manager.py

**Recommendation:** Review for consolidation or clarify purpose

### `test_task_queue.py`
Found in:
- tests/test_task_queue.py
- AGENTIC_DEV_PROTOTYPE/tests/test_task_queue.py

**Recommendation:** Review for consolidation or clarify purpose

### `conftest.py`
Found in:
- tests/conftest.py
- aim/tests/conftest.py
- tests/plugins/conftest.py
- tests/error/conftest.py

**Recommendation:** Review for consolidation or clarify purpose

### `codex_adapter.py`
Found in:
- engine/adapters/codex_adapter.py
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/adapters/codex_adapter.py
- core/engine/adapters/codex_adapter.py
- AGENTIC_DEV_PROTOTYPE/src/adapters/codex_adapter.py

**Recommendation:** Review for consolidation or clarify purpose

### `aider_adapter.py`
Found in:
- engine/adapters/aider_adapter.py
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/adapters/aider_adapter.py
- core/engine/adapters/aider_adapter.py
- AGENTIC_DEV_PROTOTYPE/src/adapters/aider_adapter.py

**Recommendation:** Review for consolidation or clarify purpose

### `spec_renderer.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/spec_renderer.py
- AGENTIC_DEV_PROTOTYPE/src/spec_renderer.py

**Recommendation:** Review for consolidation or clarify purpose

### `schema_generator.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/schema_generator.py
- AGENTIC_DEV_PROTOTYPE/src/schema_generator.py

**Recommendation:** Review for consolidation or clarify purpose

### `spec_resolver.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/spec_resolver.py
- AGENTIC_DEV_PROTOTYPE/src/spec_resolver.py

**Recommendation:** Review for consolidation or clarify purpose

### `prompt_renderer.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/prompt_renderer.py
- AGENTIC_DEV_PROTOTYPE/src/prompt_renderer.py

**Recommendation:** Review for consolidation or clarify purpose

### `task_queue.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/task_queue.py
- core/state/task_queue.py
- AGENTIC_DEV_PROTOTYPE/src/task_queue.py

**Recommendation:** Review for consolidation or clarify purpose

### `patch_manager.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/patch_manager.py
- core/engine/patch_manager.py
- AGENTIC_DEV_PROTOTYPE/src/patch_manager.py

**Recommendation:** Review for consolidation or clarify purpose

### `validation_gateway.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/validation_gateway.py
- AGENTIC_DEV_PROTOTYPE/src/validation_gateway.py

**Recommendation:** Review for consolidation or clarify purpose

### `schema_validator.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/validators/schema_validator.py
- AGENTIC_DEV_PROTOTYPE/src/validators/schema_validator.py

**Recommendation:** Review for consolidation or clarify purpose

### `guard_rules_engine.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/validators/guard_rules_engine.py
- AGENTIC_DEV_PROTOTYPE/src/validators/guard_rules_engine.py

**Recommendation:** Review for consolidation or clarify purpose

### `state_machine.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/orchestrator/state_machine.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/state_machine.py
- AGENTIC_DEV_PROTOTYPE/src/orchestrator/state_machine.py

**Recommendation:** Review for consolidation or clarify purpose

### `parallel_executor.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/orchestrator/parallel_executor.py
- AGENTIC_DEV_PROTOTYPE/src/orchestrator/parallel_executor.py

**Recommendation:** Review for consolidation or clarify purpose

### `core.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/orchestrator/core.py
- AGENTIC_DEV_PROTOTYPE/src/orchestrator/core.py

**Recommendation:** Review for consolidation or clarify purpose

### `dependency_resolver.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/orchestrator/dependency_resolver.py
- AGENTIC_DEV_PROTOTYPE/src/orchestrator/dependency_resolver.py

**Recommendation:** Review for consolidation or clarify purpose

### `claude_adapter.py`
Found in:
- PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/sessions/session_3_m5_m6_completion/src_snapshot/adapters/claude_adapter.py
- core/engine/adapters/claude_adapter.py
- AGENTIC_DEV_PROTOTYPE/src/adapters/claude_adapter.py

**Recommendation:** Review for consolidation or clarify purpose

### `guard.py`
Found in:
- specifications/tools/guard/guard.py
- Multi-Document Versioning Automation final_spec_docs/tools/spec_guard/guard.py

**Recommendation:** Review for consolidation or clarify purpose

### `resolver.py`
Found in:
- specifications/tools/resolver/resolver.py
- Multi-Document Versioning Automation final_spec_docs/tools/spec_resolver/resolver.py

**Recommendation:** Review for consolidation or clarify purpose

### `patcher.py`
Found in:
- specifications/tools/patcher/patcher.py
- Multi-Document Versioning Automation final_spec_docs/tools/spec_patcher/patcher.py

**Recommendation:** Review for consolidation or clarify purpose

### `indexer.py`
Found in:
- specifications/tools/indexer/indexer.py
- Multi-Document Versioning Automation final_spec_docs/tools/spec_indexer/indexer.py

**Recommendation:** Review for consolidation or clarify purpose

### `renderer.py`
Found in:
- specifications/tools/renderer/renderer.py
- Multi-Document Versioning Automation final_spec_docs/tools/spec_renderer/renderer.py

**Recommendation:** Review for consolidation or clarify purpose

### `db.py`
Found in:
- core/state/db.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py

**Recommendation:** Review for consolidation or clarify purpose

### `base.py`
Found in:
- core/engine/adapters/base.py
- UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/base.py

**Recommendation:** Review for consolidation or clarify purpose

## Outdated Documentation

- `AGENTS.md` - Update to use new import paths
- `README.md` - Update to use new import paths
- `DIRECTORY_GUIDE.md` - Update to use new import paths
- `aim/PRODUCTION_READINESS_ANALYSIS.md` - Update to use new import paths
- `docs/ARCHITECTURE.md` - Update to use new import paths
- `docs/DEPRECATION_PLAN.md` - Update to use new import paths
- `docs/PHASE_F_PLAN.md` - Update to use new import paths
- `docs/SECTION_REFACTOR_MAPPING.md` - Update to use new import paths
- `docs/WS-21_COMPLETE.md` - Update to use new import paths
- `docs/CI_PATH_STANDARDS.md` - Update to use new import paths
- `docs/WS-22_COMPLETE.md` - Update to use new import paths
- `docs/PHASE_F_CHECKLIST.md` - Update to use new import paths
- `docs/WS-08-COMPLETION-PLAN.md` - Update to use new import paths
- `docs/SECTION_REFACTOR_VERIFICATION.md` - Update to use new import paths
- `core/README.md` - Update to use new import paths
- `AGENTIC_DEV_PROTOTYPE/# Comprehensive Integration Specification Enhanced Prompt Engineering.md` - Update to use new import paths
- `meta/plans/phase-09-openspec-parser.md` - Update to use new import paths
- `meta/plans/phase-10-agent-coordinator.md` - Update to use new import paths
- `meta/plans/phase-11-pipeline-integration.md` - Update to use new import paths
- `meta/plans/phase-13-advanced-features.md` - Update to use new import paths
- `meta/plans/phase-12-end-to-end-validation.md` - Update to use new import paths
- `PROCESS_DEEP_DIVE_OPTOMIZE/raw_data/git_logs/git_stats_session_3_m5_m6_completion.txt` - Update to use new import paths
- `docs/AIM_docs/AIM_INTEGRATION_CONTRACT.md` - Update to use new import paths
- `docs/AIM_docs/AIM_CAPABILITIES_CATALOG.md` - Update to use new import paths
- `docs/sessions/SESSION_SUMMARY_2025-11-19.md` - Update to use new import paths
- `docs/archive/phase-h-legacy/pipeline_plus/_archive/exploration/orchestration-scripts.md` - Update to use new import paths
- `docs/reference/tools/CLAUDE.md` - Update to use new import paths

## Potentially Obsolete Files

Files with no apparent references (may be executable scripts or legitimately unused):

- `test.py` - No import references found
- `tasks.py` - No import references found
- `__tmp_o.py` - No import references found
- `pm/event_handler.py` - No import references found
- `aider/engine.py` - No import references found
- `core/planner.py` - No import references found
- `core/orchestrator.py` - No import references found
- `core/circuit_breakers.py` - No import references found
- `core/scheduler.py` - No import references found
- `core/recovery.py` - No import references found
- `core/executor.py` - No import references found
- `core/error_context.py` - No import references found
- `core/archive.py` - No import references found
- `aim/cli/commands/install.py` - No import references found
- `core/engine/integration_worker.py` - No import references found
- `core/engine/compensation.py` - No import references found
- `core/engine/hardening.py` - No import references found
- `core/engine/performance.py` - No import references found
- `core/engine/context_estimator.py` - No import references found
- `core/planning/ccpm_integration.py` - No import references found
- `core/state/worktree.py` - No import references found
- `core/state/db_sqlite.py` - No import references found
- `core/engine/adapters/codex_adapter.py` - No import references found
- `core/engine/adapters/claude_adapter.py` - No import references found
- `core/engine/adapters/aider_adapter.py` - No import references found
- `core/engine/adapters/base.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/execution_request_builder.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/router.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/registry.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/subprocess_adapter.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/base.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/run_monitor.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/progress_tracker.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/retry.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/resilient_executor.py` - No import references found
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/circuit_breaker.py` - No import references found
- `error/plugins/echo/plugin.py` - No import references found
- `infra/ci/sandbox_repos/sandbox_python/src/app.py` - No import references found

## Audit Criteria

### Deprecated
- Files in `src/pipeline/` (legacy shims)
- Files in `MOD_ERROR_PIPELINE/` (legacy error shims)

### Legacy/Archive Candidates
- `build/` - Legacy build output
- `bundles/` - Misplaced test files
- `pipeline_plus/` - Previous implementation
- `state/` - Database file location

### Temporary/Backup
- Files matching: *.bak, *.old, *.tmp, *~
- Files matching: __tmp_*, *_backup_*

### Duplicative
- Multiple files with same name in different directories

### Outdated Documentation
- Documentation referencing `src.pipeline.*`
- Documentation referencing `MOD_ERROR_PIPELINE.*`

### Obsolete
- Python files with no import references
- Excludes: test files, __init__.py, executable scripts

## Recommendations

### Safe Removal Strategy

1. **Deprecated files**: Remove after Phase 1 grace period (2026-02-19)
2. **Legacy directories**: Archive to `docs/archive/phase-h-legacy/`
3. **Temporary files**: Delete after backing up
4. **Duplicates**: Review and consolidate or document purpose
5. **Outdated docs**: Update import references
6. **Obsolete files**: Verify unused, then archive or delete

### Archival Process

```bash
# Create archive directory
mkdir -p docs/archive/audit-{date}/

# Move files (don't delete immediately)
mv <file> docs/archive/audit-{date}/

# Document in archive/README.md
# Commit with clear message
# Wait one sprint before permanent deletion
```
