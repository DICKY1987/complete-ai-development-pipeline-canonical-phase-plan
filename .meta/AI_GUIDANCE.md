# AI Guidance for Complete AI Development Pipeline

> **Purpose**: AI agent onboarding and safe editing guidance  
> **Format Version**: 1.0.0  
> **Last Updated**: 2025-11-22  
> **Target Audience**: AI coding assistants, automated agents, and LLM-based tools

---

## 🎯 Quick Start for AI Agents

Welcome! This repository implements a sophisticated AI development pipeline with strict architectural boundaries. This guide helps you contribute safely and effectively.

### Essential Reading Order

1. **Start here** - This file (AI context and safe zones)
2. **Module structure** - [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) (comprehensive module map)
3. **Quality gates** - [QUALITY_GATE.yaml](../QUALITY_GATE.yaml) (must-pass checks)
4. **Human guidelines** - [AGENTS.md](../AGENTS.md) (detailed coding standards)
5. **Architecture** - [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) (system design)

---

## 🛡️ Safe Edit Zones (AI-Friendly Areas)

These modules are **safe to modify** without special review:

### ✅ Core Logic (HIGH PRIORITY for AI context)
- `core/state/` - Database and state management
- `core/engine/` - Orchestration and execution
- `core/planning/` - Workstream planning
- `engine/` - Standalone job execution engine
- `error/engine/` - Error detection orchestration
- `error/plugins/` - Error detection plugins
- `aim/` - AI environment management
- `tests/` - Test suite (always safe to add tests)

**Edit Policy**: `safe` - Make changes following existing patterns, run tests afterward.

### ✅ Integration & Utilities (MEDIUM PRIORITY)
- `aider/` - Aider integration
- `pm/` - Project management tools
- `scripts/` - Automation scripts
- `tools/` - Internal utilities
- `workstreams/` - Example workstreams
- `docs/` - Documentation (always encouraged!)

**Edit Policy**: `safe` - Update as needed, maintain consistency.

---

## ⚠️ Review-Required Zones (Proceed with Caution)

These areas require **human review** before changes:

### ⚠️ Contracts & Schemas
- `schema/` - JSON/YAML/SQL schemas (breaking changes affect multiple consumers)
- `config/` - Runtime configuration (circuit breaker settings, profiles)
- `specifications/content/` - Canonical specifications (source of truth)
- `specifications/changes/` - Active change proposals

**Edit Policy**: `review-required` - Propose changes, don't commit directly.

**Why?** Schema changes can break tooling. Always validate with:
```bash
python scripts/validate_workstreams.py
python scripts/generate_spec_index.py
```

---

## ❌ Read-Only Zones (Do Not Modify)

These areas are **off-limits** for automated edits:

### ❌ Legacy & Archive
- `legacy/` - Archived code (migration history only)
- `docs/archive/` - Historical documentation
- `.worktrees/` - Runtime workspace (gitignored)
- `.ledger/`, `.tasks/`, `.runs/` - Execution state (gitignored)
- `pm/workspace/` - Local planning artifacts (gitignored)

**Edit Policy**: `read-only` or `exclude`

**Why?** Legacy code is for reference only. See [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md) for modern equivalents.

### ❌ Forbidden Import Patterns (CI ENFORCED)

These import patterns will **fail CI checks**:

```python
# ❌ FORBIDDEN (Post-Phase E refactor)
from src.pipeline.db import init_db                    # Use: from core.state.db import init_db
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine  # Use: from error.engine.error_engine import ErrorEngine
from legacy.* import anything                          # Use: See SECTION_REFACTOR_MAPPING.md

# ❌ DEPRECATED (Migration in progress)
from openspec.specs import load_spec                   # Use: from specifications.content import load_spec
from spec.tools import generate_index                  # Use: from specifications.tools.indexer.indexer import generate_index
```

**Enforcement**: Automated gate in `scripts/paths_index_cli.py` (see [docs/CI_PATH_STANDARDS.md](../docs/CI_PATH_STANDARDS.md))

---

## 📋 Required Quality Gates

Before submitting changes, ensure these pass:

### Must-Pass (BLOCKING)
```bash
# 1. Python unit tests
python -m pytest -q tests

# 2. Workstream validation
python scripts/validate_workstreams.py

# 3. Import path standards (CI enforced)
python scripts/paths_index_cli.py gate --db refactor_paths.db --regex "src/pipeline|MOD_ERROR_PIPELINE"

# 4. Error module imports
python scripts/validate_error_imports.py
```

### Should-Pass (WARNINGS)
```bash
# 5. Workstream authoring quality
python scripts/validate_workstreams_authoring.py

# 6. Markdown linting (if installed)
markdownlint **/*.md

# 7. Python linting (if installed)
ruff check .
```

**One Command**: `pwsh scripts/test.ps1` (runs all gates)

See [QUALITY_GATE.yaml](../QUALITY_GATE.yaml) for complete list.

---

## 🏗️ Architecture Quick Reference

### Layered Design (Bottom-Up)

```
┌─────────────────────────────────────────┐
│ UI Layer (scripts, GUI, CLI)            │ ← Safe to modify
├─────────────────────────────────────────┤
│ API Layer (aim, pm, aider, specs)      │ ← Safe with tests
├─────────────────────────────────────────┤
│ Domain Layer (core.engine, error)      │ ← Safe with tests
├─────────────────────────────────────────┤
│ Infrastructure (core.state, schema)    │ ← Schema changes need review
└─────────────────────────────────────────┘
```

### Dependency Rules (CRITICAL)

1. **No circular dependencies** - Modules can only depend on same/lower layer
2. **No legacy imports** - Legacy code is read-only reference
3. **Section isolation** - `core.*`, `error.*`, `aim.*` are self-contained
4. **Tests can import anything** - Except other tests

**Validation**: See `dependency_graph` section in [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml)

---

## 🎨 Code Style Guidelines

### Python
- **Indent**: 4 spaces (PEP8)
- **Naming**: `snake_case` for files/modules, `PascalCase` for classes
- **Type hints**: Preferred in new code
- **Imports**: Absolute imports from section roots (`from core.state.db import init_db`)
- **Formatter**: Black (if installed)

### Markdown
- **Headings**: One H1 per file, sentence-case
- **Line length**: ~100 characters
- **Lists**: Consistent bullet style (-, *, or numbered)

### YAML/JSON
- **Indent**: 2 spaces
- **Keys**: `kebab-case` (e.g., `phase-name`, `workstream-id`)

### PowerShell
- **Prefer Python** for cross-platform logic
- **Use .ps1** only for Windows-specific wrappers
- **Provide .sh parity** where feasible

---

## 📦 Module Import Patterns (Copy-Paste Ready)

```python
# Core modules
from core.state.db import init_db
from core.state.crud import get_workstream, create_workstream
from core.engine.orchestrator import Orchestrator
from core.planning.planner import generate_workstream

# Error detection
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse

# Domain integrations
from aim.registry.registry import get_tool_info
from specifications.tools.indexer.indexer import generate_index
from specifications.tools.resolver.resolver import resolve_spec_uri

# Standalone engine
from engine.orchestrator import JobOrchestrator
```

---

## 🔍 Finding What You Need

### "Where do I add X?"

| Task | Location | Module ID |
|------|----------|-----------|
| Database operations | `core/state/` | `core.state` |
| Orchestration logic | `core/engine/` | `core.engine` |
| Error detection plugin | `error/plugins/<name>/` | `error.plugins` |
| Job execution adapter | `engine/adapters/<tool>_adapter.py` | `engine` |
| AI tool integration | `aim/` | `aim` |
| Spec processing | `specifications/tools/` | `specifications.tools` |
| Automation script | `scripts/` | `scripts` |
| Tests | `tests/<category>/` | `tests` |
| Documentation | `docs/` | `docs` |

### "How do I validate X?"

| What | Command |
|------|---------|
| Workstreams | `python scripts/validate_workstreams.py` |
| Imports | `python scripts/validate_error_imports.py` |
| Engine | `python scripts/validate_engine.py` |
| Database | `python scripts/db_inspect.py` |
| Tests | `pytest -q tests` |

---

## 🚦 Decision Tree for Edits

```
┌─────────────────────────────────────┐
│ Is this a schema/config change?     │
├─────────────────────────────────────┤
│ YES → Review required               │
│  - Validate with scripts            │
│  - Regenerate indices               │
│  - Update CODEBASE_INDEX if needed  │
│                                      │
│ NO → Continue ↓                     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Is this in legacy/ or archive/?     │
├─────────────────────────────────────┤
│ YES → STOP - Read-only!             │
│  - See SECTION_REFACTOR_MAPPING.md  │
│                                      │
│ NO → Continue ↓                     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Does it match existing patterns?    │
├─────────────────────────────────────┤
│ YES → Safe to proceed               │
│  - Run quality gates                │
│  - Update tests                     │
│  - Update docs if needed            │
│                                      │
│ NO → Review AGENTS.md first         │
└─────────────────────────────────────┘
```

---

## 📚 Key Documents Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **CODEBASE_INDEX.yaml** | Module structure, dependencies, layers | Before modifying any module |
| **QUALITY_GATE.yaml** | Quality checks and commands | Before committing changes |
| **AGENTS.md** | Detailed coding guidelines | When uncertain about patterns |
| **DIRECTORY_GUIDE.md** | Human-friendly navigation | When exploring codebase |
| **docs/ARCHITECTURE.md** | System design and components | Understanding data flows |
| **docs/SECTION_REFACTOR_MAPPING.md** | Old→new path mappings | Migrating from legacy code |
| **docs/CI_PATH_STANDARDS.md** | Import enforcement details | Debugging CI failures |
| **pytest.ini** | Test configuration | Running specific test suites |
| **requirements.txt** | Python dependencies | Setting up environment |

---

## 🤖 AI Agent Best Practices

### DO ✅
- Read CODEBASE_INDEX.yaml first to understand module boundaries
- Run quality gates before submitting (see QUALITY_GATE.yaml)
- Follow existing import patterns (see "Module Import Patterns" above)
- Add tests for new functionality
- Update documentation when changing public APIs
- Use absolute imports from section roots
- Respect layer boundaries (infra → domain → api → ui)

### DON'T ❌
- Import from `legacy/` directory (see SECTION_REFACTOR_MAPPING.md instead)
- Use deprecated paths (`src.pipeline.*`, `MOD_ERROR_PIPELINE.*`)
- Modify schemas without validation
- Create circular dependencies between modules
- Refactor code outside your change scope
- Commit without running pytest
- Ignore CI path standards checks

### WHEN UNCERTAIN 🤔
1. Check CODEBASE_INDEX.yaml for module dependencies
2. Consult QUALITY_GATE.yaml for validation steps
3. Review similar existing code in the same module
4. Run `pytest -q tests` to ensure nothing breaks
5. Ask for human review on schema/config changes

---

## 🔧 Common Tasks for AI Agents

### Task: Add a new error detection plugin
1. Create `error/plugins/<name>/` directory
2. Add `manifest.json` with plugin metadata
3. Implement `plugin.py` with `parse()` function
4. Add tests in `tests/plugins/test_<name>.py`
5. Run: `pytest -q tests/plugins/`
6. Document in `error/plugins/README.md`

### Task: Modify core orchestration logic
1. Edit files in `core/engine/`
2. Update related tests in `tests/pipeline/`
3. Run: `pytest -q tests/pipeline/`
4. Run: `python scripts/validate_workstreams.py`
5. Update docs if public API changed

### Task: Add a new automation script
1. Create `scripts/<name>.py` (Python preferred)
2. Add header docstring with usage
3. Make executable: `chmod +x scripts/<name>.py`
4. Document in `scripts/README.md`
5. Optionally add `.ps1` wrapper for Windows

### Task: Update documentation
1. Edit files in `docs/`
2. Maintain one H1 per file
3. Use sentence-case headings
4. Run: `markdownlint docs/` (if installed)
5. Update `docs/DOCUMENTATION_INDEX.md` if adding new doc

---

## 📞 Support & Escalation

### AI Agent Cannot Proceed?
- **Schema conflicts** → Flag for human review
- **Test failures** → Show diagnostic output, halt
- **Import path violations** → See SECTION_REFACTOR_MAPPING.md
- **Circular dependencies** → Review CODEBASE_INDEX.yaml layers
- **Architectural uncertainty** → Consult docs/ARCHITECTURE.md

### Validation Failed?
```bash
# Get diagnostic info
python scripts/db_inspect.py              # Database state
python -m aim status                      # AIM tool status
pytest -v tests/<specific_test>.py        # Detailed test output
python scripts/paths_index_cli.py scan    # Import analysis
```

---

## 🎓 Learning Resources

- **Phase K Documentation**: Complete implementation records in `docs/PHASE_K_*_COMPLETE.md`
- **UET Framework**: Universal Execution Templates in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
- **Example Workstreams**: `workstreams/` directory
- **Plugin Examples**: `error/plugins/python_ruff/` (simple), `error/plugins/semgrep/` (complex)
- **Adapter Examples**: `engine/adapters/aider_adapter.py`

---

## ✨ Summary

**TL;DR for AI Agents**:
1. Read [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) to understand structure
2. Check [QUALITY_GATE.yaml](../QUALITY_GATE.yaml) for required validations
3. Use correct import patterns (no `src.pipeline.*` or `MOD_ERROR_PIPELINE.*`)
4. Avoid modifying `legacy/`, `schema/`, and `config/` without review
5. Run `pytest -q tests` before committing
6. Follow layer boundaries: infra → domain → api → ui
7. When uncertain, consult [AGENTS.md](../AGENTS.md) or flag for human review

**Happy contributing! 🚀**

---

**Document Version**: 1.0.0  
**Maintained By**: Phase K+ Team  
**Last Reviewed**: 2025-11-22
