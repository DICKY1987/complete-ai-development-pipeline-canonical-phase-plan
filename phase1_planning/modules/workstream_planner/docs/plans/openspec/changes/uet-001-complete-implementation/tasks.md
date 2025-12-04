---
doc_id: DOC-GUIDE-TASKS-078
---

# UET Implementation Tasks - Master Checklist

**Change ID**: uet-001-complete-implementation
**Last Updated**: 2025-11-23
**Status**: Planning

---

## Phase A: Quick Wins (Week 1-2) - 18 hours

### Schema Foundation
- [ ] Copy all 17 UET schemas from `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/` to `schema/uet/`
- [ ] Validate schemas with JSON Schema validator
- [ ] Create `schema/uet/README.md` documenting each schema
- [ ] Update `.gitignore` if needed for schema artifacts

### Worker Health System
- [ ] Create `core/engine/worker_health.py` module
- [ ] Implement heartbeat monitoring (every 30 seconds)
- [ ] Add health check to WorkerPool
- [ ] Implement worker quarantine on health failure
- [ ] Add `WORKER_HEALTH_CHECK_FAILED` event type
- [ ] Write unit tests for health checks

### Event Persistence
- [ ] Add `run_events` table to database schema
- [ ] Create migration script `schema/migrations/001_add_run_events.sql`
- [ ] Modify EventBus to persist events to database
- [ ] Add event replay functionality for debugging
- [ ] Implement event subscribers for orchestrator
- [ ] Write tests for event persistence

### Feedback Loop
- [ ] Create `core/engine/feedback_loop.py` module
- [ ] Implement auto-creation of fix tasks on test failures
- [ ] Add prioritization based on failure impact
- [ ] Block dependent tasks until failures fixed
- [ ] Add `FEEDBACK_TASK_CREATED` event type
- [ ] Write integration tests for feedback loop

### Context Manager Enhancements
- [ ] Enhance `context_estimator.py` with token counting
- [ ] Implement context pruning strategy (remove less relevant sections)
- [ ] Add summarization for large context (first/last N lines)
- [ ] Implement chunking for tasks exceeding token limits
- [ ] Write tests for context operations

---

## Phase B: Patch System (Week 3-5) - 42 hours

### Database Migration
- [ ] Create `schema/migrations/002_uet_alignment.sql`
- [ ] Add `patches` table with ULID primary key
- [ ] Add `patch_ledger_entries` table
- [ ] Add ULID columns to existing tables (runs, workstreams, attempts)
- [ ] Install `python-ulid` package: `pip install python-ulid`
- [ ] Create migration script `scripts/migrate_db_to_uet.py`
- [ ] Create rollback script `scripts/rollback_db_migration.py`
- [ ] Test migration on copy of production database
- [ ] Document migration procedure in `docs/DATABASE_MIGRATION.md`

### Patch Ledger Implementation
- [ ] Create `core/patches/` directory
- [ ] Create `core/patches/__init__.py`
- [ ] Create `core/patches/patch_artifact.py` (wrap existing PatchArtifact)
- [ ] Create `core/patches/patch_ledger.py` with state machine
- [ ] Implement state transitions: created → validated → queued → applied → verified → committed
- [ ] Add state history tracking (JSON array)
- [ ] Integrate with event bus for state changes
- [ ] Write unit tests for state machine

### Patch Validator
- [ ] Create `core/patches/patch_validator.py`
- [ ] Implement format validation (unified diff only)
- [ ] Implement scope validation (file paths, line counts)
- [ ] Implement constraint validation (max lines, file patterns)
- [ ] Add validation result dataclass
- [ ] Write tests for all validation types

### Patch Policy Engine
- [ ] Create `core/patches/patch_policy.py`
- [ ] Create `config/patch_policies/` directory
- [ ] Create `config/patch_policies/global.json` (default policy)
- [ ] Create `config/patch_policies/python_strict.json`
- [ ] Create `config/patch_policies/docs_permissive.json`
- [ ] Implement policy loading and enforcement
- [ ] Write tests for policy engine

### Patch Applier
- [ ] Create `core/patches/patch_applier.py`
- [ ] Implement safe patch application with rollback
- [ ] Add dry-run mode (test without applying)
- [ ] Track applied files for rollback
- [ ] Integrate with git for atomic operations
- [ ] Write tests for apply/rollback

---

## Phase C: Orchestration (Week 5-7) - 30 hours

### DAG Scheduler
- [ ] Create `core/engine/scheduler_dag.py`
- [ ] Implement dependency parsing from workstream specs
- [ ] Implement topological sort for execution order
- [ ] Add cycle detection (prevent circular dependencies)
- [ ] Implement parallel execution of independent tasks
- [ ] Add `parallel_strategy` config option (sequential/dag)
- [ ] Create migration guide for existing workstreams
- [ ] Write tests for DAG construction and execution

### Merge Orchestration
- [ ] Create `core/engine/merge_strategy.py`
- [ ] Implement deterministic merge order (priority, dependency, age)
- [ ] Add conflict detection (E_MERGE_CONFLICT event)
- [ ] Implement rollback on merge failure
- [ ] Add merge preview mode
- [ ] Write tests for merge strategies

### Context Manager (Token Management)
- [ ] Create `core/engine/context_manager.py`
- [ ] Implement token estimation per model (GPT-4, Claude, etc.)
- [ ] Add intelligent pruning (remove boilerplate, keep critical)
- [ ] Implement summarization (compress large files)
- [ ] Add chunking for tasks exceeding context window
- [ ] Track context usage in cost tracker
- [ ] Write tests for context operations

### Integration Worker Enhancements
- [ ] Enhance `core/engine/integration_worker.py`
- [ ] Integrate with merge orchestration
- [ ] Add merge conflict resolution strategies
- [ ] Implement partial merge support (merge non-conflicting first)
- [ ] Write tests for integration scenarios

---

## Phase D: Adapters - Patch-First (Week 7-10) - 42 hours

### Feature Flag Infrastructure
- [ ] Add `patch_mode` to `PROJECT_PROFILE.yaml`
- [ ] Add `patch_mode` to adapter base class
- [ ] Implement dual-mode detection in orchestrator
- [ ] Document feature flags in `docs/FEATURE_FLAGS.md`

### Base Adapter Refactoring
- [ ] Modify `core/engine/adapters/base.py`
- [ ] Add `patch_mode` parameter to ToolAdapter
- [ ] Add task mode support (prompt, patch_review, patch_apply_validate)
- [ ] Add `_extract_patch()` helper method
- [ ] Update adapter interface documentation

### Aider Adapter (Patch-First)
- [ ] Modify `core/engine/adapters/aider_adapter.py`
- [ ] Change default: `--no-auto-commits --output-diff`
- [ ] Implement `_extract_patch()` for Aider output
- [ ] Add `patch_review` mode support
- [ ] Add `patch_apply_validate` mode support
- [ ] Test with dual-mode (both old and new behavior)

### Codex Adapter (Patch-First)
- [ ] Modify `core/engine/adapters/codex_adapter.py`
- [ ] Implement patch extraction from Codex output
- [ ] Add diff formatting to unified diff spec
- [ ] Test with dual-mode

### Claude Adapter (Patch-First)
- [ ] Modify `core/engine/adapters/claude_adapter.py`
- [ ] Implement patch extraction from Claude output
- [ ] Add diff formatting to unified diff spec
- [ ] Test with dual-mode

### Migration Testing
- [ ] Create `tests/migration/` directory
- [ ] Create test suite with 20+ existing workstreams
- [ ] Test dual-mode with `patch_mode: false` (legacy)
- [ ] Test dual-mode with `patch_mode: true` (UET)
- [ ] Validate identical outcomes between modes
- [ ] Create migration checklist document

### Orchestrator Integration
- [ ] Modify `core/engine/orchestrator.py`
- [ ] Integrate patch capture after EDIT step
- [ ] Add patch validation before STATIC step
- [ ] Store patch metadata in database
- [ ] Add patch quarantine on validation failure
- [ ] Update error handling for patch failures

---

## Phase E: Resilience (Week 10-11) - 40 hours

### Compensation Engine
- [ ] Enhance `core/engine/compensation.py`
- [ ] Implement Saga pattern (forward + compensation actions)
- [ ] Define compensation actions per phase
- [ ] Add rollback scopes: patch, task, phase, multi-phase
- [ ] Implement compensation cascade (undo multiple phases)
- [ ] Write tests for all rollback scenarios

### Human Review Workflow
- [ ] Create `core/engine/human_review.py`
- [ ] Add `HUMAN_REVIEW` task type
- [ ] Implement escalation triggers (gate failure, merge conflict, etc.)
- [ ] Create structured feedback format (approve/reject/adjust)
- [ ] Add CLI interface for review actions
- [ ] Write tests for review workflow

### Checkpoint System
- [ ] Create `core/engine/checkpoint.py`
- [ ] Implement git tag creation at phase boundaries
- [ ] Add worktree snapshot functionality
- [ ] Implement database backup at checkpoints
- [ ] Add fast restore from checkpoint
- [ ] Write tests for checkpoint/restore

---

## Cross-Phase Tasks

### Documentation
- [ ] Create `docs/UET_MIGRATION_GUIDE.md`
- [ ] Update `docs/ARCHITECTURE.md` with UET patterns
- [ ] Create `docs/PATCH_WORKFLOW.md`
- [ ] Create `docs/DATABASE_MIGRATION.md`
- [ ] Update `CLAUDE.md` with UET import paths
- [ ] Update `AGENTS.md` with UET conventions

### Testing
- [ ] Create `tests/uet/` directory
- [ ] Write unit tests for all new modules (target: 85% coverage)
- [ ] Write integration tests for end-to-end workflows
- [ ] Write regression tests (backward compatibility)
- [ ] Add UET validation to CI pipeline
- [ ] Create test data fixtures for UET schemas

### Validation
- [ ] Create `scripts/validate_uet_alignment.py`
- [ ] Check schema presence (17/17 copied)
- [ ] Check component implementation
- [ ] Check test coverage (≥85% for UET code)
- [ ] Check backward compatibility
- [ ] Generate alignment report

---

**Total Effort**: 172 hours
**Timeline**: 9-12 weeks
**MVP**: 130 hours, 7-8 weeks (skip security)
