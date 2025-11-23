# UET Integration Guide – Understanding the Two Execution Systems

**Created**: 2025-11-23  
**Purpose**: Clarify the relationship between UET Framework and the production pipeline  
**Audience**: AI agents and developers working on UET alignment

---

## Executive Summary

This repository contains **two execution systems** that serve different purposes:

1. **`UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`** – Reference implementation (the blueprint)
2. **`core/`, `engine/`, `error/`** – Production pipeline (the house being renovated)

**Current Status**: ~40% UET-aligned, migration in progress  
**Goal**: Full UET alignment over 9-10 weeks (see `UET_INTEGRATION_PLAN_ANALYSIS.md`)

---

## The Two Systems Explained

### System 1: UET Framework (Reference Implementation)

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`

**Purpose**: 
- Canonical schema definitions (17 JSON schemas)
- Reference implementation showing "how it should work"
- Proof of concept for UET patterns
- Source of truth for schema-driven development

**Key Components**:
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── schema/                     # 17 canonical JSON schemas
│   ├── patch_artifact.v1.json
│   ├── patch_ledger_entry.v1.json
│   ├── patch_policy.v1.json
│   ├── phase_spec.v1.json
│   ├── workstream_spec.v1.json
│   └── ... (12 more)
├── core/
│   ├── bootstrap/              # Project discovery & config generation
│   ├── engine/                 # Clean execution orchestrator
│   └── adapters/               # Tool integration abstraction
├── specs/                      # 22 specification documents
└── tests/                      # 196 passing tests
```

**Characteristics**:
- ✅ Fully schema-driven (validates against JSON schemas)
- ✅ Patch-first workflow (unified diffs only)
- ✅ Bootstrap system (auto-configures for any project)
- ✅ Clean architecture (no legacy code)
- ✅ 100% test coverage (196/196 tests pass)

**When to Use**:
- Reference UET schemas when designing new features
- Study architecture patterns for best practices
- Copy schema files when implementing UET alignment
- **DO NOT** use for actual production work

---

### System 2: Production Pipeline (Active Development)

**Location**: Root directory (`core/`, `engine/`, `error/`, etc.)

**Purpose**:
- Real production orchestration for AI development
- Multi-phase development pipeline
- Error detection and recovery
- Active workstream execution

**Key Components**:
```
./
├── core/
│   ├── state/                  # Database, CRUD, worktree management
│   ├── engine/                 # Orchestrator, scheduler, executor
│   ├── planning/               # Workstream planner
│   └── patches/                # [TO CREATE] Patch management system
├── engine/                     # Job-based execution engine
├── error/
│   ├── engine/                 # Error detection state machine
│   └── plugins/                # Language-specific error detectors
├── aim/                        # AI environment manager
├── pm/                         # Project management
├── specifications/             # Unified spec management
└── schema/                     # Current schemas (to be aligned with UET)
```

**Current State** (~40% UET-aligned):
- ✅ Worker lifecycle (80% - has states, needs health checks)
- ✅ Event bus (85% - has events, needs persistence)
- ✅ Cost tracker (75% - budget tracking, needs per-phase)
- ✅ Patch manager (50% - basic parsing, needs full ledger)
- ✅ Test gates (65% - enforcer exists, needs predefined gates)
- ⚠️ Adapters (direct file edits - needs patch-first refactor)
- ⚠️ Scheduler (basic - needs DAG-based)
- ❌ ULIDs (using auto-increment IDs)
- ❌ Schema validation (not enforced)

**When to Use**:
- All actual development work
- Running workstreams and jobs
- Error detection and recovery
- Production orchestration

---

## The Integration Plan (What's Happening)

### Phase-by-Phase Alignment

The goal is to **migrate the production pipeline to UET patterns** while maintaining backward compatibility.

```
┌─────────────────────────────────────────────────────────┐
│ UET Framework (Reference)                               │
│  • Canonical schemas                                    │
│  • Clean patterns                                       │
│  • 100% aligned                                         │
└────────────┬────────────────────────────────────────────┘
             │
             │ Copy schemas, patterns, architecture
             ↓
┌─────────────────────────────────────────────────────────┐
│ Production Pipeline (Current: ~40% aligned)             │
│  • Active development                                   │
│  • Legacy patterns                                      │
│  • Gradual migration                                    │
└─────────────────────────────────────────────────────────┘
```

### Migration Strategy

**Week 1-2: Quick Wins** (Phase A)
```bash
# Copy UET schemas to production
Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json schema\uet\

# Add missing components
# - Worker health checks
# - Event persistence
# - Feedback loop
# - Context manager enhancements
```

**Week 3-4: Patch System** (Phase B)
```bash
# Database migration (BACKUP FIRST!)
cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup
python scripts/migrate_db_to_uet.py

# New components:
# - core/patches/patch_ledger.py
# - core/patches/patch_validator.py
# - core/patches/patch_policy.py
```

**Week 5-6: Orchestration** (Phase C)
```bash
# New DAG scheduler (feature branch)
# - core/engine/scheduler_dag.py
# - core/engine/merge_strategy.py
# - core/engine/context_manager.py
```

**Week 7-9: Adapters - BREAKING CHANGE** (Phase D)
```bash
# Refactor to patch-first (dual-mode support)
# - core/engine/adapters/base.py (add patch_mode flag)
# - core/engine/adapters/aider_adapter.py (output unified diff)
# - Migration testing
```

**Week 10: Resilience** (Phase E)
```bash
# Human review and compensation
# - core/engine/human_review.py
# - core/engine/compensation.py (full Saga pattern)
```

---

## Feature Flags for Gradual Migration

To avoid breaking existing workstreams, use feature flags in `PROJECT_PROFILE.yaml`:

```yaml
execution:
  # Patch-first workflow (default: false for backward compat)
  patch_mode: false              # true = UET mode (unified diffs only)
  
  # Scheduler strategy
  parallel_strategy: sequential  # or "dag" for UET DAG scheduler
  
  # ID system
  ulid_enabled: false           # true = use ULIDs, false = current IDs
  
  # Schema validation
  uet_schema_validation: false  # true = enforce UET schema validation
```

**Migration Path**:
1. Implement new UET-aligned components alongside existing ones
2. Set feature flags to `false` (old behavior)
3. Test new components with flags set to `true`
4. Gradually migrate workstreams one-by-one
5. Deprecate old components after 3 months

---

## Which System Should You Use?

### When Working with Schemas

**USE**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/`

```bash
# Reference the canonical schemas
cat UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/patch_artifact.v1.json

# Copy to production when implementing
Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\patch_artifact.v1.json schema\uet\
```

**Rationale**: UET schemas are the source of truth.

---

### When Writing Code

**USE**: Production pipeline (`core/`, `engine/`, `error/`)

```python
# Correct (production system)
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine

# Incorrect (don't use reference implementation)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator  # ❌
```

**Rationale**: Production code lives in root, not in UET Framework.

---

### When Studying Architecture

**USE**: Both (compare reference vs current)

```bash
# Study clean implementation
cat UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py

# Then check current implementation
cat core/engine/orchestrator.py

# Note differences and plan alignment
```

**Rationale**: Learn from reference, apply to production.

---

### When Running Workstreams

**USE**: Production pipeline

```bash
# Run production orchestrator
python scripts/run_workstream.py workstreams/example.json

# NOT the reference implementation
# (UET Framework orchestrator is for demonstration only)
```

**Rationale**: Only production system is configured for your project.

---

## Import Path Rules During Migration

### Current State (Production Pipeline)

**Correct** (use these):
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
```

**Forbidden** (CI will block):
```python
from src.pipeline.db import init_db                           # ❌ Deprecated
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine       # ❌ Deprecated
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.* import *       # ❌ Reference only
```

### After UET Alignment (Future State)

**New imports will use UET patterns**:
```python
from core.patches.patch_ledger import PatchLedger            # ✅ New UET component
from core.engine.scheduler_dag import DAGScheduler           # ✅ New UET component
from core.engine.adapters.base import ToolAdapter            # ✅ Refactored for patch-first
```

---

## File Organization During Migration

### UET Framework (Reference) – READ ONLY

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── CLAUDE.md                   # Instructions for working with UET Framework
├── schema/                     # Source of truth for schemas
├── core/                       # Clean reference implementation
└── specs/                      # UET specification documents
```

**Operations**:
- ✅ Read schemas
- ✅ Study architecture
- ✅ Copy schemas to production
- ❌ DO NOT modify (reference only)

---

### Production Pipeline (Active Development)

```
./
├── CLAUDE.md                   # Production agent instructions
├── UET_INTEGRATION_GUIDE.md    # This file
├── UET_INTEGRATION_PLAN_ANALYSIS.md  # Detailed migration plan
├── schema/
│   ├── uet/                    # [COPY FROM] UET Framework schemas
│   ├── schema.sql              # Current database schema
│   └── migrations/             # [CREATE] Migration scripts
├── core/
│   ├── patches/                # [CREATE] New UET patch system
│   ├── engine/                 # [ENHANCE] Add UET patterns
│   └── state/                  # [ENHANCE] Add ULID support
└── [all other directories]     # Active development
```

**Operations**:
- ✅ All development work
- ✅ Create new UET-aligned components
- ✅ Refactor existing components
- ✅ Add feature flags for gradual migration

---

## Testing Strategy During Migration

### Test Both Systems Independently

**UET Framework Tests** (reference):
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
pytest tests/ -v
# Expected: 196/196 tests pass
```

**Production Pipeline Tests**:
```bash
cd ..  # Back to root
pytest tests/ -q
# Expected: All tests pass (count varies as we add UET components)
```

---

### Dual-Mode Testing (During Migration)

```python
# tests/engine/test_orchestrator.py

def test_orchestrator_legacy_mode():
    """Test orchestrator with current (non-UET) behavior."""
    config = {'patch_mode': False}  # Feature flag OFF
    orchestrator = Orchestrator(config)
    # ... test legacy behavior

def test_orchestrator_uet_mode():
    """Test orchestrator with UET patch-first behavior."""
    config = {'patch_mode': True}   # Feature flag ON
    orchestrator = Orchestrator(config)
    # ... test UET behavior
```

---

## Common Pitfalls and How to Avoid Them

### ❌ Pitfall #1: Importing from UET Framework in Production Code

**Wrong**:
```python
# core/engine/orchestrator.py
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import BaseOrchestrator
```

**Right**:
```python
# Study the reference implementation, then write production code
# No imports from UET Framework - it's reference only
```

---

### ❌ Pitfall #2: Modifying UET Framework Instead of Production

**Wrong**:
```bash
# Editing reference implementation
vim UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py
```

**Right**:
```bash
# Use reference for guidance, edit production code
cat UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py  # Study
vim core/engine/orchestrator.py  # Edit production
```

---

### ❌ Pitfall #3: Breaking Changes Without Feature Flags

**Wrong**:
```python
# core/engine/adapters/aider_adapter.py
def execute(self, task):
    # Immediately switch to patch-first (breaks existing workstreams)
    return self._generate_patch(task)  # ❌
```

**Right**:
```python
# core/engine/adapters/aider_adapter.py
def execute(self, task):
    if self.config.get('patch_mode', False):
        return self._generate_patch(task)  # UET mode
    else:
        return self._direct_edit(task)     # Legacy mode
```

---

### ❌ Pitfall #4: Forgetting Database Backups

**Wrong**:
```bash
# Directly run migration
python scripts/migrate_db_to_uet.py  # ❌ No backup!
```

**Right**:
```bash
# ALWAYS backup before migration
cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup
python scripts/migrate_db_to_uet.py
# Validate migration
python scripts/validate_db_migration.py
```

---

## Progress Tracking

### Current UET Alignment Status (~40%)

| Component | Status | Location | UET Aligned? |
|-----------|--------|----------|--------------|
| Worker Lifecycle | 80% | `core/engine/worker.py` | 🟡 Needs health checks |
| Event Bus | 85% | `core/engine/event_bus.py` | 🟡 Needs persistence |
| Patch Manager | 50% | `core/engine/patch_manager.py` | 🟡 Needs ledger |
| Cost Tracker | 75% | `core/engine/cost_tracker.py` | 🟡 Needs per-phase |
| Test Gates | 65% | `core/engine/test_gates.py` | 🟡 Needs predefined gates |
| Integration Worker | 60% | `core/engine/integration_worker.py` | 🟡 Needs orchestration |
| Compensation | 40% | `core/engine/compensation.py` | ❌ Stub only |
| Adapters | 0% | `core/engine/adapters/` | ❌ Direct edits (not patch-first) |
| Scheduler | 0% | `core/engine/scheduler.py` | ❌ Not DAG-based |
| ULIDs | 0% | `core/state/db.py` | ❌ Using auto-increment |
| Schema Validation | 0% | - | ❌ Not enforced |

**Legend**:
- ✅ Fully UET-aligned
- 🟡 Partially aligned (needs enhancements)
- ❌ Not aligned (greenfield or refactor needed)

---

### Milestone Tracking

- [ ] **Week 1-2**: Quick Wins (schemas copied, worker health, event persistence)
- [ ] **Week 3-4**: Patch System (database migrated, ledger implemented)
- [ ] **Week 5-6**: Orchestration (DAG scheduler, merge orchestration)
- [ ] **Week 7-9**: Adapters (dual-mode support, patch-first refactoring)
- [ ] **Week 10**: Resilience (compensation engine, human review)

**Check Progress**:
```bash
# Run validation script (to be created)
python scripts/validate_uet_alignment.py

# Expected output:
# ✅ UET Schemas: 17/17 copied
# 🟡 Patch System: 2/4 components complete
# ❌ Adapters: 0/3 refactored to patch-first
# Overall: 45% UET-aligned
```

---

## Quick Reference Card

### For AI Agents

**Question**: Where do I find the schema for X?  
**Answer**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/X.v1.json`

**Question**: Where do I implement feature Y?  
**Answer**: Production pipeline (`core/`, `engine/`, etc.)

**Question**: Can I modify UET Framework code?  
**Answer**: No - it's reference only. Study it, then write production code.

**Question**: How do I know if I should use patch-first mode?  
**Answer**: Check `PROJECT_PROFILE.yaml` → `execution.patch_mode`

**Question**: What if my change breaks existing workstreams?  
**Answer**: Add feature flag for dual-mode support, migrate gradually.

---

### For Developers

**Command**: Copy UET schemas to production  
```bash
Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json schema\uet\
```

**Command**: Check UET alignment status  
```bash
python scripts/validate_uet_alignment.py  # (to be created)
```

**Command**: Run tests for both systems  
```bash
# UET Framework (reference)
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK && pytest tests/ -v

# Production pipeline
cd .. && pytest tests/ -q
```

**Command**: Enable UET mode for testing  
```yaml
# Edit PROJECT_PROFILE.yaml
execution:
  patch_mode: true
  parallel_strategy: dag
  uet_schema_validation: true
```

---

## Related Documentation

- **`UET_INTEGRATION_PLAN_ANALYSIS.md`** – Comprehensive 40K+ character migration plan
- **`CLAUDE.md`** – Production agent instructions (patch-first, import rules)
- **`UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/CLAUDE.md`** – UET Framework reference agent instructions
- **`docs/CI_PATH_STANDARDS.md`** – Import path enforcement
- **`docs/SECTION_REFACTOR_MAPPING.md`** – Old→new path mappings

---

## Summary

### The Two Systems

1. **UET Framework** (`UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`)
   - Reference implementation
   - Canonical schemas
   - Study, don't modify
   - 100% UET-aligned

2. **Production Pipeline** (root directory)
   - Active development
   - ~40% UET-aligned
   - Gradual migration in progress
   - Where all work happens

### Key Principles

1. **UET Framework = Blueprint** – Use for schemas, patterns, architecture study
2. **Production = House** – Where actual development happens
3. **Feature Flags = Safety** – Enable gradual migration without breaking changes
4. **Dual-Mode = Compatibility** – Support old and new behavior during transition
5. **Schema-First = Quality** – Validate against UET schemas as you align

### Next Steps

1. **Immediate** (This Week):
   ```bash
   Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json schema\uet\
   ```

2. **Phase A** (Week 1-2): Quick wins (worker health, event persistence)
3. **Phase B** (Week 3-4): Patch system (database migration, ledger)
4. **Phase C** (Week 5-6): Orchestration (DAG scheduler, merge orchestration)
5. **Phase D** (Week 7-9): Adapters (patch-first refactoring - BREAKING CHANGE)
6. **Phase E** (Week 10): Resilience (compensation, human review)

**Estimated Timeline**: 9-10 weeks to full UET alignment  
**MVP Timeline**: 6-7 weeks (skip security, human review optional)

---

**This guide clarifies the relationship between the two execution systems and provides a roadmap for UET integration.**
