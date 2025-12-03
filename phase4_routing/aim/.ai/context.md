---
doc_id: DOC-GUIDE-CONTEXT-191
---

# Repository Context for AI

**Repository**: Complete AI Development Pipeline – Canonical Phase Plan  
**Type**: Automation Framework + Development Tools  
**Language**: Python (primary), PowerShell, YAML  
**Last Updated**: 2025-11-25

---

## Purpose

**AI-assisted workstream orchestration and error detection pipeline** for automated software development workflows with pattern-based execution and governance.

One-sentence: Orchestrates AI-driven development tasks with automated error detection, workstream management, and pattern-based execution templates.

---

## Architecture Overview

```
Repository Structure:
├── core/           - Core orchestration engine (scheduler, executor, state)
├── engine/         - Job execution engine (workers, queues)
├── error/          - Error detection pipeline (plugins, auto-fix)
├── pm/             - Project management tools (CCPM, workstreams)
├── specifications/ - Spec management and validation
├── docs/           - Documentation and governance
├── scripts/        - Automation and utility scripts
├── tests/          - Test suite (pytest)
└── .ai/            - AI context and guidance (this directory)
```

---

## Key Components

### 1. Core Orchestration (`core/`)
**Purpose**: Workstream planning, scheduling, and state management

**Key Files**:
- `core/engine/orchestrator.py` - Main orchestration engine
- `core/planning/workstream_manager.py` - Workstream lifecycle
- `core/state/db.py` - State persistence (SQLite)

**Entry Point**: `core/engine/orchestrator.py:Orchestrator.run()`

### 2. Error Detection (`error/`)
**Purpose**: Automated error detection and fixing across the codebase

**Key Files**:
- `error/engine/error_engine.py` - Main error detection engine
- `error/plugins/python_ruff/` - Python linting plugin
- `error/plugins/*/` - Extensible plugin architecture

**Entry Point**: `error/engine/error_engine.py:ErrorEngine.scan()`

### 3. Job Engine (`engine/`)
**Purpose**: Distributed job execution with retry logic

**Key Files**:
- `engine/executor.py` - Job executor with circuit breaker
- `engine/scheduler.py` - Job scheduling
- `engine/worker.py` - Worker pool management

### 4. Project Management (`pm/`)
**Purpose**: CCPM-based project management and workstream tracking

**Key Files**:
- `pm/ccpm/` - Critical Chain Project Management
- `pm/workstreams/` - Workstream definitions
- `pm/rules/` - Governance rules

### 5. Specifications (`specifications/`)
**Purpose**: OpenSpec-based specification management

**Key Files**:
- `specifications/tools/` - Spec validation and indexing
- `specifications/content/` - Actual specifications

---

## Common Entry Points

### For Development:
```bash
# Run orchestrator
python -m core.engine.orchestrator

# Run error scanner
python -m error.engine.error_engine --scan

# Run cleanup tools
python scripts/analyze_cleanup_candidates.py
```

### For Testing:
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/core/
pytest tests/engine/
pytest tests/error/

# Run with coverage
pytest --cov=core --cov=engine --cov=error
```

### For Maintenance:
```bash
# Cleanup duplicates
python scripts/analyze_cleanup_candidates.py

# Analyze folder versions
python scripts/analyze_folder_versions_v2.py

# Update codebase index
python scripts/update_codebase_index.py
```

---

## Dependencies

### Core Dependencies:
- Python 3.9+
- SQLite (state persistence)
- PyYAML (configuration)
- pytest (testing)

### Optional Tools:
- Ruff (Python linting - error detection)
- Aider (AI code assistant integration)
- PowerShell 7+ (Windows automation)

### Module Dependency Flow:
```
infra/ (lowest)
  ↓
core/ (orchestration)
  ↓
engine/ (execution) + error/ (detection)
  ↓
pm/ (management) + specifications/ (governance)
  ↓
gui/ (optional UI)
```

**Rule**: Lower layers cannot depend on higher layers.

---

## Common Tasks

### Debugging:
```bash
# Check orchestrator status
python -m core.engine.orchestrator --status

# View error logs
cat logs/error_engine.log

# Analyze state database
sqlite3 core/state/workstreams.db "SELECT * FROM workstreams;"
```

### Adding a New Error Plugin:
```bash
# 1. Create plugin directory
mkdir error/plugins/my_plugin

# 2. Implement plugin interface
# See: error/plugins/python_ruff/plugin.py as template

# 3. Add tests
# See: tests/error/plugins/test_python_ruff.py

# 4. Register in error engine
# See: error/engine/error_engine.py:_load_plugins()
```

### Adding a New Workstream:
```bash
# 1. Define workstream spec
# See: pm/workstreams/WS_*.yaml

# 2. Add to orchestrator
python -m core.planning.workstream_manager add --spec pm/workstreams/WS_NEW.yaml

# 3. Run orchestrator
python -m core.engine.orchestrator
```

---

## AI-Specific Guidance

### When Analyzing This Repo:

**Start Here**:
1. Read `CODEBASE_INDEX.yaml` - Canonical module map
2. Check `docs/FOLDER_VERSION_SCORING_SPEC.md` - Architecture decisions
3. Review this file (`.ai/context.md`) - You're here!

**Module Understanding**:
- Each top-level folder is a **module** (core, engine, error, pm)
- Modules have clear **purposes** (orchestration, execution, detection, management)
- Import paths follow structure: `from core.engine.orchestrator import Orchestrator`

**Code Patterns**:
- See `.ai/common-patterns.md` for coding standards
- Circuit breaker pattern in `engine/executor.py`
- Plugin architecture in `error/plugins/`
- State machines in `core/state/`

**Testing**:
- Tests mirror source structure: `tests/core/` ↔ `core/`
- Use pytest fixtures from `tests/conftest.py`
- Aim for 70% coverage on business logic

---

## File Naming Conventions

### Documentation:
- Strategic docs: `DOC_*.md` (have DOC_IDs)
- Module READMEs: `<module>/README.md`
- Session reports: `*_REPORT_*.md`

### Code:
- Python modules: `lowercase_with_underscores.py`
- Tests: `test_<module_name>.py`
- Scripts: `analyze_*.py`, `validate_*.py`, `generate_*.py`

### Configuration:
- YAML: `*.yaml` (preferred) or `*.yml`
- Environment: `.env.example` (template only)

---

## Quick Reference

### Repository Stats:
- **422 Python files** (active codebase)
- **61 test files** (~14% test ratio)
- **750 markdown files** (documentation)
- **Max depth**: 5 levels (AI-optimized)
- **Avg depth**: 2.7 levels (ideal for AI)

### Key Documentation:
- Architecture: `CODEBASE_INDEX.yaml`
- Scoring system: `docs/FOLDER_VERSION_SCORING_SPEC.md`
- Cleanup patterns: `docs/DOC_DOCUMENTATION_CLEANUP_PATTERN.md`
- Optimization roadmap: `docs/REPOSITORY_OPTIMIZATION_ROADMAP.md`

### Contact Points:
- Issue tracking: GitHub Issues
- Discussions: GitHub Discussions
- Documentation: `docs/` directory

---

## For AI Code Assistants

### Prompt Engineering Tips:
```
Good prompts:
- "Analyze the error detection pipeline in error/engine/"
- "Add a new workstream following the pattern in pm/workstreams/"
- "Fix the orchestrator retry logic in core/engine/orchestrator.py"

Bad prompts:
- "Fix everything" (too vague)
- "Rewrite the entire system" (too broad)
- "Make it faster" (needs metrics)
```

### Context Window Optimization:
- Start with `.ai/codebase-map.yaml` for structure
- Load specific modules as needed
- Use `CODEBASE_INDEX.yaml` for dependencies
- Reference `.ai/common-patterns.md` for patterns

### Safe Operations:
✅ Can safely modify:
- `core/`, `engine/`, `error/`, `pm/` (active code)
- `tests/` (add tests freely)
- `scripts/` (automation utilities)

⚠️ Require review:
- `docs/DOC_*.md` (governance docs)
- `CODEBASE_INDEX.yaml` (architecture map)
- `schema/` (data contracts)

❌ Never modify:
- `legacy/` (archived code)
- `.git/` (version control)
- Generated files (reports, logs)

---

**Last Updated**: 2025-11-25  
**Maintained By**: Repository automation  
**Next Review**: Monthly or after major refactor
