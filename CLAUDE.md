---
doc_id: DOC-GUIDE-CLAUDE-1095
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role & Persona

You are my primary AI coding assistant. You help me design, implement, debug, and refactor code across all my projects.

## Core Principles

1. **Minimal, surgical changes** - Make the smallest possible edits to achieve the goal
2. **Test awareness** - Propose or update tests when changing behavior
3. **Clear communication** - Explain your plan before large refactors
4. **Safety first** - Never modify files outside the current repository
5. **Git discipline** - All changes must be git-trackable and revertible

## Default Behavior

- Prefer unified diffs for edits
- Add concise comments only where needed (avoid obvious comments)
- Keep code idiomatic to the project's primary language
- Preserve existing formatting and style
- Never commit real secrets; use placeholders like `YOUR_API_KEY_HERE`

## Tool Usage

- Use file edit capabilities directly when appropriate
- Explain destructive commands before execution
- Stay within repository boundaries unless explicitly instructed otherwise

## Repository Overview

**Universal Execution Templates (UET) Framework** - A production-ready AI orchestration system for managing complex development workflows with autonomous task execution, parallel processing, and resilience patterns.

**Status**: 78% complete (Phase 3 done, Phase 4 planned)
**Language**: Python 3.8+
**Tests**: 196 tests, 100% passing
**Architecture**: 4-layer spec-driven pipeline (Schema → State → Domain → Orchestration)
**Environment**: Windows (PowerShell), cross-platform Python code

## Essential Commands

### Testing
```bash
# Run all tests (must pass before commits)
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/engine/test_orchestrator.py -q

# Run tests by marker (defined in pytest.ini)
python -m pytest -m unit -q
python -m pytest -m integration -q
python -m pytest -m "not slow" -q
python -m pytest -m bootstrap -q
python -m pytest -m engine -q
python -m pytest -m adapter -q
python -m pytest -m resilience -q

# Run with coverage (optional)
pytest --cov=core --cov=error --cov=aim --cov=pm tests/
```

**Note**: Test configuration exists in both `pytest.ini` (primary) and `pyproject.toml`. If there are conflicts, pytest.ini takes precedence.

### Validation
```bash
# Validate workstreams (check for DAG cycles)
python scripts/validate_workstreams.py

# Check for deprecated import paths (CI gate)
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Validate all schemas
python scripts/validate_all_schemas.py

# Run all quality gates
python scripts/run_quality_gates.py
```

### Bootstrap
```bash
# Initialize framework for a project
python core/bootstrap/orchestrator.py <project_path>
```

## Architecture

### 4-Layer System

**Layer 1 - Foundation (schema/)**
- JSON schema contracts for all framework artifacts
- 17 production schemas defining all data structures
- Zero dependencies

**Layer 2 - State (core/state/)**
- SQLite persistence at `.worktrees/pipeline_state.db`
- Tables: runs, steps, step_attempts, run_events
- Database singleton with connection pooling
- Path resolution: ENV var > function arg > default

**Layer 3 - Domain (core/, error/, aim/, pm/, tools/)**
- `core/bootstrap/` - Auto-discovery and project configuration
- `core/engine/` - Task orchestration, routing, and scheduling
- `core/engine/resilience/` - Circuit breakers, retry logic, exponential backoff
- `core/engine/monitoring/` - Progress tracking and run monitoring
- `core/adapters/` - Tool integration abstraction layer
- `error/` - Plugin-based error detection and fixing
- `aim/` - AI tool capability matching bridge
- `pm/` - Project metadata management
- `tools/` - Specification tools (guard, indexer, patcher, renderer, resolver)

**Layer 4 - Orchestration (profiles/, specs/, templates/)**
- 5 project profiles: software-dev-python, data-pipeline, documentation, operations, generic
- Core specifications defining framework behavior
- Reusable phase and task templates

### Key Workflows

**Bootstrap Workflow:**
```
discovery → selection → generation → validation → report
```

**Execution Workflow:**
```
create_run → schedule → route → execute → track → transition
```

**State Machine:**
```
PENDING → RUNNING → COMPLETED/FAILED
```

**Circuit Breaker:**
```
CLOSED → OPEN → HALF_OPEN
```

## Module Navigation

| Module | Purpose | Entry Point |
|--------|---------|-------------|
| `core/engine/` | Orchestrator, scheduler, router | `orchestrator.Orchestrator` |
| `core/state/` | SQLite state management | `db.init_db()` |
| `core/bootstrap/` | Auto-discovery and config | `orchestrator.BootstrapOrchestrator` |
| `core/adapters/` | Tool integration | `registry.AdapterRegistry` |
| `core/engine/resilience/` | Fault tolerance | `resilient_executor.ResilientExecutor` |
| `core/engine/monitoring/` | Progress tracking | `progress_tracker.ProgressTracker` |
| `schema/` | JSON schemas | N/A (data files) |
| `profiles/` | Project templates | N/A (config files) |
| `tools/` | Spec tooling modules | Various (guard, indexer, patcher, etc.) |

## Import Standards

### ✅ Correct (Always Use These)
```python
from core.state.db import get_db, init_db
from core.bootstrap.orchestrator import BootstrapOrchestrator
from core.engine.orchestrator import Orchestrator
from core.engine.resilience import ResilientExecutor
from core.engine.monitoring import ProgressTracker
from core.adapters import AdapterRegistry
from error.engine.error_engine import ErrorEngine
from aim.bridge import get_tool_info
from tools.guard import guard_function
from tools.indexer import create_index
from tools.patcher import apply_patch
from tools.renderer import render_template
from tools.resolver import resolve_dependency
```

### ❌ Forbidden (CI Will Block)
```python
from src.pipeline.*           # Deprecated - use core.*
from MOD_ERROR_PIPELINE.*     # Deprecated - use error.*
from legacy.*                 # Never import
```

## Critical Requirements

### Before Every Commit
1. ✅ All tests must pass: `python -m pytest tests/ -q`
2. ✅ No deprecated import paths
3. ✅ Only touch files within declared scope
4. ✅ Validation scripts pass with exit code 0

### Import Path Rules
- **Always** use absolute imports with section-based paths (`core.*`, `error.*`, `aim.*`, `pm.*`)
- **Never** import from `src.*`, `legacy.*`, or deprecated paths
- **Never** use relative imports across architectural layers

### Database Schema Changes
1. Create migration in `schema/migrations/00X_description.sql`
2. Update `schema/README.md`
3. Test migration: `python core/state/db.py --migrate`
4. Validate: `python -m pytest tests/state/test_db.py -q`

### Workstream Validation
- Dependencies must form a directed acyclic graph (DAG)
- Always validate before committing: `python scripts/validate_workstreams.py`
- No circular dependencies allowed

## Quick Reference Files

**First-Time Setup:**
- `.meta/AI_GUIDANCE.md` - 2-minute AI onboarding guide
- `CODEBASE_INDEX.yaml` - Complete module map with dependencies
- `README.md` - Master documentation index

**When Working:**
- `ai_policies.yaml` - Edit zones, forbidden patterns, invariants (if exists)
- `QUALITY_GATE.yaml` - All validation checkpoints and commands (if exists)
- `specifications/specs/STATUS.md` - Current framework status
- `DOC_ID_SYSTEM_STATUS.md` - Status of the doc_id cross-referencing system

**Specifications:**
- `specifications/specs/UET_BOOTSTRAP_SPEC.md` - Autonomous framework installation
- `specifications/specs/UET_COOPERATION_SPEC.md` - Multi-tool cooperation
- `specifications/specs/UET_PHASE_SPEC_MASTER.md` - Phase template definitions
- `specifications/specs/UET_TASK_ROUTING_SPEC.md` - Task routing logic

**Note**: Specifications were recently reorganized. Always use paths under `specifications/specs/` (not the old `specs/` directory structure).

## Edit Zones

### Safe to Edit (No Review)
- `core/**/*.py` - Core engine, state, planning
- `error/**/*.py` - Error detection plugins
- `aim/**/*.py` - AI tool bridge
- `pm/**/*.py` - Project management
- `tools/**/*.py` - Spec tooling modules (guard, indexer, patcher, etc.)
- `tests/**/*.py` - All test files
- `scripts/**/*.{py,ps1}` - Automation scripts

### Review Required
- `schema/**/*.json` - Schema contracts (validate downstream impact)
- `config/**/*.yaml` - Configuration (affects all tools)
- `core/state/db*.py` - Database operations (coordinate with migrations)

### Read-Only (Never Edit)
- `legacy/**` - Archived deprecated code
- `_ARCHIVE/**` - Archived historical content
- `src/pipeline/**` - Deprecated (use `core.*`) [may not exist]
- `MOD_ERROR_PIPELINE/**` - Deprecated (use `error.*`) [may not exist]
- `docs/adr/**` - Architecture Decision Records (append only) [if exists]
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/**` - Primary spec documentation (read-only reference)

## Common Patterns

### Add Error Detection Plugin
```bash
# 1. Copy template
cp -r error/plugins/python_ruff error/plugins/my_plugin

# 2. Update manifest.json with plugin info
edit error/plugins/my_plugin/manifest.json

# 3. Implement parse() method in plugin.py
edit error/plugins/my_plugin/plugin.py

# 4. Add tests
create tests/error/plugins/test_my_plugin.py

# 5. Validate
python -m pytest tests/error/plugins/test_my_plugin.py -q
```

### Add Validation Script
```bash
# 1. Create script in scripts/
create scripts/my_validator.py

# 2. Add to QUALITY_GATE.yaml if it's a validation gate
edit QUALITY_GATE.yaml

# 3. Test
python scripts/my_validator.py --help
```

## Testing Strategy

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.bootstrap` - Bootstrap-related tests
- `@pytest.mark.engine` - Engine-related tests
- `@pytest.mark.adapter` - Adapter-related tests
- `@pytest.mark.resilience` - Resilience-related tests

### Coverage Requirements
- Core modules: High coverage expected
- All new features must include tests
- 196 tests currently, all must pass

## Speed Optimization Principles

### Decision Elimination
- Use existing templates and patterns (don't reinvent)
- Copy working patterns for similar tasks
- Pre-made structural decisions in specs

### Ground Truth Verification
- Base decisions ONLY on CLI output
- Run tests before claiming completion
- No "looks right" without verification

### Atomic Execution
- Small, focused changes (1-3 files per commit)
- Batch similar operations together
- Use parallel tool calls when possible

### Template-Driven Development
- Second time doing similar task? Extract template
- Prefer editing existing files over creating new ones
- Follow established patterns in codebase

## Proven Performance Results

- **37x speedup** on pattern extraction (55 min vs 31 hours)
- **2.7x speedup** on module manifests (55 min vs 2.5 hours)
- **5-10x speedup** on documentation cleanup (2-3 hours vs 10+ hours)

## Success Criteria

A task is complete when ALL of these are true:
1. ✅ Tests pass: `python -m pytest tests/ -q` → "X passed"
2. ✅ Files exist: All expected files present
3. ✅ No scope violations: Only declared files touched
4. ✅ Validation scripts pass: Exit code 0
5. ✅ Git status clean or expected: No surprise modifications

## Document ID System

This codebase uses a `doc_id` system for cross-referencing documents. Each major document has a unique ID in YAML frontmatter:

```yaml
---
doc_id: DOC-GUIDE-CLAUDE-1095
---
```

- Check `DOC_ID_SYSTEM_STATUS.md` for the current status
- Use `write_doc_ids_to_files.py` to add doc_ids to new documents
- Always preserve existing doc_ids when editing files

## Additional Resources

- `QUICK_EXECUTION_PLAYBOOK.md` - Speed patterns and techniques
- `UET_DOC_CLEANUP_PHASE_PLAN.md` - Example 5-wave execution
- `specifications/specs/PHASE_4_AI_ENHANCEMENT_PLAN.md` - Future roadmap
- `profiles/README.md` - Profile system documentation
- `E2E_PROCESS_VISUAL_DIAGRAM.md` - End-to-end process visualization
- `SYSTEM_VISUAL_DIAGRAMS.md` - System architecture diagrams
