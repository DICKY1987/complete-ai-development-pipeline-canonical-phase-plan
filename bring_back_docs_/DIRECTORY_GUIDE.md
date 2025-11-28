# Directory Guide - AI Development Pipeline

> **Purpose**: Quick navigation and understanding of the repository structure for both humans and AI tools.  
> **Last Updated**: 2025-11-22  
> **For AI Tools**: This document provides context on repository organization and section purposes.
> 
> **📋 File Organization System**: See [docs/FILE_ORGANIZATION_SYSTEM.md](docs/FILE_ORGANIZATION_SYSTEM.md) for the complete specification on separating development artifacts from system files. Quick reference: [docs/FILE_ORGANIZATION_QUICK_REF.md](docs/FILE_ORGANIZATION_QUICK_REF.md)

---

## 📋 Quick Navigation

| Looking for... | Go to... | Purpose |
|---------------|----------|---------|
| **Getting Started** | [README.md](README.md) | Main entry point, quick start guide |
| **Core Pipeline Code** | [core/](#core-pipeline-implementation) | State, orchestration, planning |
| **Job Execution Engine** | [engine/](#execution-engine) | Standalone job-based execution |
| **Error Detection** | [error/](#error-detection-system) | Error pipeline and plugins |
| **Documentation** | [docs/](#documentation) | Architecture, guides, implementation records |
| **Specifications** | [specifications/](#specifications) | Spec management and tools |
| **Workstream Examples** | [workstreams/](#workstreams) | Sample workstream bundles |
| **Tests** | [tests/](#tests) | Unit, integration, and pipeline tests |
| **Scripts** | [scripts/](#scripts) | Automation and utilities |
| **Contributing** | [AGENTS.md](AGENTS.md) | Coding guidelines and conventions |

---

## 📂 Directory Tree (Visual Overview)

```
complete-ai-development-pipeline-canonical-phase-plan/
│
├── 📚 CORE IMPLEMENTATION
│   ├── core/               # Core pipeline (state, engine, planning)
│   ├── engine/             # Job-based execution engine
│   ├── error/              # Error detection system
│   ├── aim/                # AIM integration bridge
│   ├── pm/                 # Project management integrations
│   └── specifications/     # Unified spec management
│
├── 📖 DOCUMENTATION & PLANNING
│   ├── docs/               # Architecture, guides, summaries
│   ├── meta/               # Phase development docs
│   └── assets/             # Diagrams and images
│
├── 🔧 INFRASTRUCTURE
│   ├── scripts/            # Automation scripts
│   ├── tests/              # Test suite
│   ├── schema/             # JSON/YAML schemas
│   ├── config/             # Runtime configuration
│   └── tools/              # Internal utilities
│
├── 📦 INTEGRATION & TOOLING
│   ├── aider/              # Aider integration
│   ├── openspec/           # OpenSpec integration (legacy)
│   ├── workstreams/        # Example workstream bundles
│   └── gui/                # GUI components
│
├── 🗃️ WORKSPACE & STATE
│   ├── .worktrees/         # Runtime worktree folders (gitignored)
│   │   └── pipeline_state.db  # Active SQLite database
│   ├── .ledger/            # Execution ledger
│   ├── .tasks/             # Task queue storage
│   └── .runs/              # Execution run records
│
├── 🗄️ LEGACY (ARCHIVED)
│   └── legacy/             # Archived/deprecated components
│       ├── AI_MANGER_archived_2025-11-22/  # PowerShell env manager (→ aim/)
│       └── AUX_mcp-data_archived_2025-11-22/  # Old MCP files (→ .worktrees/)
│
└── 📄 ROOT DOCUMENTATION
    ├── README.md           # Main entry point
    ├── AGENTS.md           # Coding guidelines
    ├── DIRECTORY_GUIDE.md  # This file
    └── requirements.txt    # Python dependencies
```

---

## 🎯 Section Details

### Core Pipeline Implementation

#### `core/`
**Purpose**: Core pipeline functionality - the heart of the system.

**Structure**:
- `state/` - Database, CRUD operations, bundles, worktree management
- `engine/` - Orchestrator, scheduler, executor, tools adapter
- `planning/` - Workstream planner and archive utilities
- `openspec_parser.py` - OpenSpec integration

**Key Concepts**:
- State management and persistence
- Workstream orchestration
- Circuit breakers and recovery
- Tool profile adapters

**Import Pattern**: `from core.state.db import init_db`

**AI Context Priority**: HIGH - Core business logic

---

#### `engine/`
**Purpose**: Standalone job-based execution engine (separate from core/engine/).

**Structure**:
- `orchestrator.py` - Job orchestration
- `state_store.py` - Job state persistence
- `adapters/` - Tool adapters (aider, codex, git, tests)
- `queue_manager.py` - Job queue management

**Key Differences from core/engine/**:
- Uses job JSON pattern (not workstream steps)
- Hybrid GUI/Terminal/TUI architecture
- Independent state management

**Documentation**: See [engine/README.md](engine/README.md)

**AI Context Priority**: HIGH - Alternative execution model

---

#### `error/`
**Purpose**: Error detection and analysis system.

**Structure**:
- `engine/` - Error engine, state machine, plugin manager
- `plugins/` - Detection plugins (Python, JS, linting, security)
- `shared/utils/` - Hashing, time utilities, JSONL manager

**Plugin Architecture**:
- Each plugin has `manifest.json`
- Implements `parse()` and optionally `fix()`
- Incremental detection via file hash caching

**Import Pattern**: `from error.engine.error_engine import ErrorEngine`

**AI Context Priority**: HIGH - Quality assurance system

---

### Domain-Specific Integrations

#### `aim/`
**Purpose**: AIM+ unified AI environment manager.

**Structure**:
- `registry/` - AI tool capability registry and routing
- `environment/` - Environment management (secrets, health, scanner, installer, version control, audit)
- `services/` - Unified services layer
- `cli/` - Command-line interface
- `config/` - Unified configuration (aim_config.json)

**Key Features**:
- Tool capability routing with fallback chains
- DPAPI vault for secret management (Windows) / keyring (cross-platform)
- Environment health checks and validation
- Automated tool installation and version pinning
- Duplicate/cache detection via scanner
- Unified audit logging

**Import Pattern**: `from aim.bridge import get_tool_info`  
**CLI**: `python -m aim status|health|secrets|scan`  

**Migration**: Replaces legacy AI_MANGER (archived 2025-11-22)

**AI Context Priority**: HIGH - Core infrastructure for AI tool management

---

#### `pm/`
**Purpose**: Project management and CCPM (Critical Chain Project Management) integrations.

**Structure**:
- `commands/` - PM CLI commands
- `workspace/` - Local planning artifacts (gitignored)

**AI Context Priority**: MEDIUM - Project coordination

---

#### `specifications/`
**Purpose**: Unified specification management system.

**Structure**:
- `content/` - Specification documents by domain
- `tools/` - Processing utilities (indexer, resolver, guard, patcher)
- `changes/` - Active OpenSpec change proposals
- `bridge/` - OpenSpec → Workstream integration

**Import Pattern**: `from specifications.tools.indexer.indexer import generate_index`

**AI Context Priority**: HIGH - Source of truth for specs

---

### Documentation

#### `docs/`
**Purpose**: Canonical documentation, architecture notes, ADRs, implementation records.

**Structure**:
- Architecture documents (ARCHITECTURE.md, etc.)
- Implementation summaries (PHASE_*_COMPLETE.md)
- Configuration guides
- Refactor mapping

**Best Practices**:
- One H1 per file
- Sentence-case headings
- ~100 char line wrapping
- Include metadata headers

**AI Context Priority**: MEDIUM - Reference documentation

---

#### `meta/`
**Purpose**: Phase development docs and planning documents.

**AI Context Priority**: LOW - Planning artifacts

---

### Infrastructure

#### `scripts/`
**Purpose**: Automation scripts for common tasks.

**Key Scripts**:
- `bootstrap.ps1` - Initial setup
- `test.ps1` - Run tests
- `validate_workstreams.py` - Workstream validation
- `run_workstream.py` - Execute workstreams
- `generate_spec_index.py` - Generate spec indices

**Conventions**:
- Prefer PowerShell (.ps1) for Windows-first flows
- Provide .sh parity where feasible
- Python for cross-platform logic

**AI Context Priority**: MEDIUM - Operational tools

---

#### `tests/`
**Purpose**: Comprehensive test suite.

**Structure**:
- `unit/` - Unit tests
- `integration/` - Integration tests
- `pipeline/` - Pipeline-specific tests
- `plugins/` - Error plugin tests
- `error/` - Error engine tests

**Test Runner**: `pytest -q` (config in pytest.ini)

**AI Context Priority**: HIGH - Quality validation

---

#### `schema/`
**Purpose**: JSON/YAML/SQL schemas defining contracts.

**Key Schemas**:
- Workstream metadata contracts
- Sidecar definitions
- Job specifications

**AI Context Priority**: HIGH - Type definitions and contracts

---

#### `config/`
**Purpose**: Runtime configuration files.

**Contents**:
- Adapter/tool profiles
- Decomposition rules
- Circuit-breaker configuration

**AI Context Priority**: MEDIUM - System configuration

---

#### `tools/`
**Purpose**: Internal Python utilities.

**Examples**:
- `hardcoded_path_indexer/` - Path indexing utilities

**AI Context Priority**: LOW - Internal utilities

---

### Integration & Tooling

#### `aider/`
**Purpose**: Aider integration and prompt templates.

**AI Context Priority**: MEDIUM - Tool integration

---

#### `workstreams/`
**Purpose**: Example workstream JSON bundles.

**Structure**:
- Single workstream examples
- Multi-workstream examples

**Validation**: Use `scripts/validate_workstreams.py`

**AI Context Priority**: MEDIUM - Reference examples

---

### Workspace & State (Runtime)

These directories are created at runtime and typically gitignored:

#### `.worktrees/`
Per-workstream working folders. Contains `pipeline_state.db` (configurable via `PIPELINE_DB_PATH`).

#### `.ledger/`
Execution ledger for tracking workstream runs.

#### `.tasks/`
Task queue storage.

#### `.runs/`
Execution run records.

**AI Context Priority**: EXCLUDE - Runtime artifacts

---

## 🔍 Finding What You Need

### For New Contributors

1. **Start with**: [README.md](README.md)
2. **Understand conventions**: [AGENTS.md](AGENTS.md)
3. **Check architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Find import paths**: [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md)

### For AI Tools

**High Priority Sections** (always index):
- `core/` - Core business logic
- `engine/` - Alternative execution engine
- `error/` - Error detection
- `specifications/` - Specs and contracts
- `schema/` - Type definitions
- `tests/` - Test suite

**Medium Priority** (index on request):
- `docs/` - Documentation
- `scripts/` - Automation
- `aider/`, `aim/`, `pm/` - Integrations
- `workstreams/` - Examples

**Low Priority** (explicit request only):
- `meta/` - Planning docs
- `tools/` - Internal utilities

**Exclude**:
- `.worktrees/`, `.ledger/`, `.tasks/`, `.runs/` - Runtime artifacts
- `__pycache__/`, `.pytest_cache/` - Build artifacts
- `legacy/` - Archived components (AI_MANGER, AUX_mcp-data)

### For Specific Tasks

**Adding State/Database Logic** → `core/state/`  
**Adding Orchestration Logic** → `core/engine/`  
**Adding Error Detection** → `error/engine/`  
**Adding Detection Plugin** → `error/plugins/<plugin-name>/`  
**Adding Spec Content** → `specifications/content/`  
**Adding Tests** → `tests/`  
**Adding Scripts** → `scripts/`  
**Adding Documentation** → `docs/`

---

## 🏗️ Architecture Patterns

### Import Path Rules (CI Enforced)

✅ **Use section-based imports**:
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from specifications.tools.indexer.indexer import generate_index
```

❌ **Do NOT use deprecated imports** (will fail CI):
```python
from src.pipeline.db import init_db                    # ❌ FAILS CI
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine  # ❌ FAILS CI
```

See [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) for details.

### Module Organization

- **core/state/**: CRUD operations follow `create_*`, `get_*`, `update_*`, `delete_*` pattern
- **core/engine/**: Orchestration with retry, circuit breakers, recovery
- **error/plugins/**: Each plugin has `manifest.json` and implements `parse()`, `fix()`

### Testing Strategy

- Unit tests under `tests/unit/`
- Integration tests under `tests/integration/`
- Pipeline tests under `tests/pipeline/`
- Plugin tests under `tests/plugins/`
- Sandbox repos under `sandbox_repos/` (excluded by default)

---

## 🚀 Common Workflows

### Running Tests
```bash
# All tests
pytest -q

# Specific test file
pytest tests/pipeline/test_orchestrator_single.py -v

# Run scripts/test.ps1 for CI-friendly output
pwsh ./scripts/test.ps1
```

### Validating Workstreams
```bash
python ./scripts/validate_workstreams.py
python ./scripts/validate_workstreams_authoring.py
```

### Running a Workstream
```bash
python ./scripts/run_workstream.py --ws-id ws-<id>
```

### Generating Indices
```bash
python ./scripts/generate_spec_index.py
python ./scripts/generate_spec_mapping.py
```

---

## 📚 Related Documentation

- [README.md](README.md) - Main repository overview
- [AGENTS.md](AGENTS.md) - Coding guidelines and conventions
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [docs/FILE_ORGANIZATION_SYSTEM.md](docs/FILE_ORGANIZATION_SYSTEM.md) - **File organization system** (dev vs system files)
- [docs/FILE_ORGANIZATION_QUICK_REF.md](docs/FILE_ORGANIZATION_QUICK_REF.md) - Quick reference for file placement
- [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md) - Import path mapping
- [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) - CI enforcement rules
- [engine/README.md](engine/README.md) - Engine architecture
- [error/README.md](error/README.md) - Error pipeline documentation

---

## 🤖 AI Tool Integration Notes

This repository is designed for AI-assisted development. Key features for AI tools:

1. **Clear Section Boundaries**: Each major directory has a single, clear purpose
2. **Consistent Import Patterns**: Section-based imports are enforced by CI
3. **Type Definitions**: Schemas in `schema/` directory define all contracts
4. **Test Coverage**: Comprehensive tests validate behavior
5. **Documentation**: Each section should have a README explaining its purpose

**Context Management**:
- Use this guide to understand repository structure
- Focus on high-priority sections for most tasks
- Exclude runtime artifacts and build outputs
- Follow import path rules to avoid CI failures

---

**END OF DIRECTORY GUIDE**
