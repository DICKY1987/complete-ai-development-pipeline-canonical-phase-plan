---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-AI_CONTEXT-106
---

# AI Context - Complete AI Development Pipeline

## What This Repository Does

Production-grade AI development orchestration system using:
- **Universal Execution Templates (UET)** for phase-based execution
- **Section-based architecture** (core, engine, error, aim, pm, specifications)
- **Workstream model** for decomposed, testable tasks
- **State persistence** via SQLite with DAG dependency tracking

**In one sentence**: A spec-driven, patch-first pipeline that orchestrates AI development workflows through workstreams with automatic error detection, dependency management, and multi-tool integration.

---

## Quick Orientation (30 seconds)

### I want to...
- **Understand architecture** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Run a workstream** → [core/orchestrator.py](core/orchestrator.py) + [QUICK_START.md](QUICK_START.md)
- **Add error detection** → [error/README.md](error/README.md)
- **Find any code** → [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md)
- **See module structure** → [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml)
- **Navigate efficiently** → [NAVIGATION.md](NAVIGATION.md)

### Entry Points
1. **Orchestration**: `python -m core.orchestrator run --plan <file>`
2. **Error Detection**: `python -m error.engine --scan <dir>`
3. **Spec Tools**: `python scripts/spec_generate.py`

---

## Architecture (10-word summary)

Section-based modules → State layer → Orchestrator → Tool adapters → Execution

**Visual**:
```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: UI (scripts, gui, engine/standalone)          │
├─────────────────────────────────────────────────────────┤
│  Layer 3: API (aim, pm, specifications.bridge)          │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Domain (core.engine, error.engine, planning)  │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure (core.state, schema, config)   │
└─────────────────────────────────────────────────────────┘
```

---

## Common AI Confusion Points

### Q: Why two import paths (src.pipeline vs core)?
**A**: Deprecated refactor. Always use `core.*`, `error.*`, `aim.*` paths.

**Migration**:
```python
# ❌ OLD (Deprecated)
from src.pipeline.db import init_db
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine

# ✅ NEW (Current)
from core.state.db import init_db
from error.engine.error_engine import ErrorEngine
```

**Reference**: [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md)

---

### Q: What's the difference between engine/ and core/engine/?
**A**: 
- `engine/` = **Standalone job-based execution** (can run independently)
- `core/engine/` = **Orchestration layer** (scheduler, executor, orchestrator)

Use `core.orchestrator` for workstream execution, `engine/` for job-based tasks.

---

### Q: Where's the main entry point?
**A**: `core/orchestrator.py:Orchestrator.run_plan()`

**Code path**:
```
python -m core.orchestrator run --plan workstreams/example.json
  ↓
core/orchestrator.py:main()
  ↓
Orchestrator.run_plan()
  ↓
  ├─ core.state.bundle_loader:load_workstream_bundle()
  ├─ core.engine.scheduler:Scheduler.schedule()
  └─ core.engine.executor:Executor.execute_step()
```

---

### Q: Are legacy/, AGENTIC_DEV_PROTOTYPE/, PROCESS_DEEP_DIVE_OPTOMIZE/ active?
**A**: **NO**. These are archived/experimental directories.

**Active code locations**:
- Core logic: `core/`, `error/`, `specifications/`
- Integrations: `aim/`, `pm/`
- Tools: `scripts/`, `engine/` (standalone)

**See**: `_archive_deprecated/DEPRECATED.md` (or `legacy/DEPRECATED.md` if not yet renamed)

---

### Q: Where's task/workstream state stored?
**A**: SQLite database at `.worktrees/<run_id>/pipeline.db`

**Schema**: runs, workstreams, steps, dependencies, errors, events

**Access**:
```python
from core.state import crud, db

db.init_db(db_path)
workstream = crud.get_workstream(ws_id)
steps = crud.get_steps_by_workstream(ws_id)
```

---

## Module Hierarchy (Dependency Order)

**Layer 1 (Infrastructure)**: Foundation, no dependencies
- `core.state` - Database, CRUD, DAG utilities
- `schema` - JSON/YAML schemas
- `config` - Runtime configuration

**Layer 2 (Domain)**: Core business logic
- `core.engine` - Orchestrator, scheduler, executor
- `core.planning` - Workstream planning, routing
- `error.engine` - Error detection engine
- `specifications.tools` - Spec management tools

**Layer 3 (API/Integrations)**: External tool bridges
- `aim` - AI environment manager (tool discovery, installation)
- `pm` - Project management (CCPM, OpenSpec)
- `specifications.bridge` - OpenSpec proposal → workstream bridge

**Layer 4 (UI)**: User-facing interfaces
- `scripts` - CLI automation tools
- `gui` - GUI (future/in development)
- `engine` - Standalone job execution
- `error.plugins` - Error detection plugins

**Dependency Rule**: Lower layers never import from higher layers.

**Reference**: [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml), [DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md)

---

## Key Files for AI Tools

### Machine-Readable Indexes
- **[CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml)** - Complete module map with dependencies
- **[PROJECT_PROFILE.yaml](PROJECT_PROFILE.yaml)** - Project metadata, constraints
- **[ai_policies.yaml](ai_policies.yaml)** - Edit zones, forbidden patterns, invariants

### Navigation & Discovery
- **[NAVIGATION.md](NAVIGATION.md)** - Unified navigation hub
- **[DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md)** - Directory structure tour
- **[docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md)** - Term → file:line lookup

### API & Execution
- **[API_INDEX.md](API_INDEX.md)** - All CLIs, Python APIs, configuration
- **[EXECUTION_INDEX.md](EXECUTION_INDEX.md)** - Execution flows, state machines
- **[DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md)** - Module dependencies, import rules

### Policies & Guidelines
- **[AGENTS.md](AGENTS.md)** - Coding conventions, contribution guidelines
- **[QUALITY_GATE.yaml](QUALITY_GATE.yaml)** - Validation commands
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI-specific guidance

---

## Documentation Strategy

### docs/ = System Documentation
Architecture, guides, references, ADRs (Architecture Decision Records)
- **Purpose**: Canonical knowledge about how the system works
- **Audience**: Developers, AI tools, maintainers
- **Examples**: ARCHITECTURE.md, CI_PATH_STANDARDS.md, workstream_authoring_guide.md

### devdocs/ = Development Artifacts
Phase plans, execution reports, session summaries
- **Purpose**: Historical record of development process
- **Audience**: Project tracking, post-mortems
- **Examples**: Phase completion reports, session summaries, implementation notes

### Module READMEs = Module-Specific Usage
Each module has README.md + .ai-module-manifest (new)
- **Purpose**: Quick module understanding, usage examples
- **Audience**: Developers working in that module
- **Examples**: core/README.md, error/README.md

---

## Recent Major Changes (Last 7 Days)

**2025-11-23**:
- ✅ Moved 53 development docs to devdocs/ (phase plans, summaries)
- ✅ Created AI Navigation Enhancement Phase Plan (PH-AI-NAV-002)

**2025-11-22**:
- ✅ AI Navigation improvements (15 directories with manifests)
- ✅ File organization cleanup

**2025-11-20**:
- ✅ UET Framework integration planning complete
- ✅ Section-based refactor (src.pipeline → core.*)

**2025-11-19**:
- ✅ Import path standardization enforced in CI

**Migration Status**:
- Section-based refactor: ✅ COMPLETE
- Dev docs reorganization: ✅ COMPLETE
- UET integration: 📋 PLANNED (Option A: Selective Integration)

---

## Import Path Standards (CI ENFORCED)

### ✅ Correct Imports (Use These)
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse
from specifications.tools.indexer.indexer import generate_index
from aim.bridge import get_tool_info
```

### ❌ Forbidden Imports (CI FAILS)
```python
from src.pipeline.db import init_db                    # ❌ Deprecated
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine  # ❌ Deprecated
from legacy.* import anything                          # ❌ Never
```

**CI Gate**: `python scripts/paths_index_cli.py gate --db refactor_paths.db`

**Reference**: [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md)

---

## Next Steps for AI Tools

### First Time Orienting?
1. ✅ **Read this file** (you are here - 2 min)
2. **Skim** [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) for module structure (1 min)
3. **Check** [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md) for specific terms (30 sec)
4. **Review** target module's README before editing (1 min)

**Total orientation time**: ~5 minutes

### Before Making Changes?
1. **Check** [ai_policies.yaml](ai_policies.yaml) for edit zones
2. **Verify** imports use section-based paths (core.*, error.*)
3. **Read** module's `.ai-module-manifest` if it exists
4. **Follow** patterns in [AGENTS.md](AGENTS.md)

### Common Tasks?
- **Find code**: [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md)
- **Understand flow**: [EXECUTION_INDEX.md](EXECUTION_INDEX.md)
- **Check dependencies**: [DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md)
- **Navigate**: [NAVIGATION.md](NAVIGATION.md)

---

## Status & Maturity

**Project Phase**: Active Development  
**Primary Branch**: main  
**Python Version**: 3.9+  
**Test Coverage**: ~70% (target: 85%)

**Production-Ready Components**:
- ✅ Core state management (core.state)
- ✅ Database layer with DAG support
- ✅ Workstream orchestration (core.engine)
- ⚠️ Error detection (70% complete)
- ⚠️ AIM integration (85% complete)
- 📋 GUI (planned)

**Development Focus**:
- UET Framework selective integration
- Error pipeline production readiness
- GUI development
- Test coverage improvements

---

## Quick Command Reference

```bash
# Run a workstream
python -m core.orchestrator run --plan workstreams/example.json

# Validate a workstream (dry run)
python -m core.orchestrator validate --plan workstreams/example.json

# Scan for errors
python -m error.engine --scan path/to/code

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=core --cov=error --cov-report=html

# Validate import paths (CI gate)
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Bootstrap UET configuration
python scripts/bootstrap_uet.py .
```

---

## For Contributors

**Start here**: [AGENTS.md](AGENTS.md)

**Key guidelines**:
- Use section-based imports (core.*, error.*)
- Keep changes small and targeted
- Add tests for new functionality
- Follow existing code patterns
- Respect module boundaries (no layer violations)

**Quality gates**:
- Import path validation (CI)
- Test coverage ≥70% (target: 85%)
- Workstream validation passes
- No deprecated path usage

---

## Getting Help

**Documentation**:
- [docs/README.md](docs/README.md) - Documentation hub
- [QUICK_START.md](QUICK_START.md) - Fast entry points
- [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - Complete doc map

**For Specific Topics**:
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Workstreams: [docs/workstream_authoring_guide.md](docs/workstream_authoring_guide.md)
- Error Pipeline: [error/README.md](error/README.md)
- Specifications: [specifications/README.md](specifications/README.md)

**Still confused?** Check [NAVIGATION.md](NAVIGATION.md) for topic-based navigation.

---

**Last Updated**: 2025-11-23  
**Version**: 2.0 (AI Navigation Enhancement v2)
