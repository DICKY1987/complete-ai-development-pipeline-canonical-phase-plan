# Core Module Structure

> **Module**: `core`  
> **Purpose**: Central pipeline implementation - state, orchestration, planning, and analysis  
> **Architecture Layer**: Domain Logic + Infrastructure  
> **Last Updated**: 2025-11-23

---

## Architecture Overview

The `core/` module is the heart of the AI Development Pipeline. It implements a **layered architecture** that separates concerns and enables independent evolution of components.

```
┌─────────────────────────────────────────────────────────┐
│                    AI Tools Layer                       │
│              (Aider, Claude, Codex, etc.)              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Tool Adapters                          │
│          core/engine/adapters/                          │
│     (Unified interface to external tools)               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│             Orchestration Engine                        │
│              core/engine/                               │
│  (Scheduler, Executor, Circuit Breakers, Recovery)      │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│  Planning   │ │   AST    │ │     State    │
│  core/      │ │  core/   │ │  core/state/ │
│  planning/  │ │  ast/    │ │              │
└─────────────┘ └──────────┘ └──────────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │  SQLite Database │
                           │  .worktrees/     │
                           │  pipeline_state  │
                           └──────────────────┘
```

---

## Directory Organization

### Hierarchy and Responsibilities

```
core/
│
├── state/                    # DATA LAYER
│   ├── db.py                # Database connection management
│   ├── db_sqlite.py         # SQLite-specific operations
│   ├── crud.py              # CRUD operations for all entities
│   ├── bundles.py           # Workstream bundle loading/validation
│   ├── worktree.py          # Git worktree lifecycle
│   ├── audit_logger.py      # Audit trail for state changes
│   ├── task_queue.py        # Task queue management
│   └── README.md            # State layer documentation
│
├── engine/                   # EXECUTION LAYER
│   ├── orchestrator.py      # Main orchestration logic
│   ├── scheduler.py         # Dependency-based scheduling
│   ├── executor.py          # Step execution with timeouts
│   ├── tools.py             # Tool profile management
│   ├── circuit_breakers.py  # Fault tolerance patterns
│   ├── recovery.py          # Recovery strategies
│   ├── recovery_manager.py  # Recovery coordination
│   ├── aim_integration.py   # AIM capability routing
│   ├── validators.py        # Validation utilities
│   ├── compensation.py      # Rollback and undo operations
│   ├── event_bus.py         # Event publication
│   ├── metrics.py           # Execution metrics
│   ├── cost_tracker.py      # API cost tracking
│   ├── context_estimator.py # Context window estimation
│   ├── patch_manager.py     # Git patch handling
│   ├── process_spawner.py   # Worker process management
│   ├── worker.py            # Worker pool implementation
│   ├── integration_worker.py# Integration coordination
│   ├── performance.py       # Performance optimization
│   ├── hardening.py         # Retry and rate limiting
│   ├── test_gates.py        # Test gate enforcement
│   ├── plan_validator.py    # Plan validation
│   ├── prompt_engine.py     # Prompt routing
│   ├── pipeline_plus_orchestrator.py  # Enhanced orchestrator
│   ├── adapters/            # Tool adapter implementations
│   │   ├── base.py          # Base adapter interface
│   │   ├── aider_adapter.py # Aider integration
│   │   ├── claude_adapter.py# Claude CLI integration
│   │   ├── codex_adapter.py # Codex integration
│   │   └── README.md        # Adapter documentation
│   └── README.md            # Engine layer documentation
│
├── planning/                 # PLANNING LAYER
│   ├── planner.py           # Automated workstream planning
│   ├── archive.py           # Archive operations
│   ├── ccpm_integration.py  # CCPM project management bridge
│   ├── parallelism_detector.py # Parallelism analysis
│   └── README.md            # Planning layer documentation
│
├── ast/                      # ANALYSIS LAYER
│   ├── extractors.py        # High-level AST extraction API
│   ├── languages/           # Language-specific parsers
│   │   ├── python.py        # Python AST parser
│   │   └── README.md        # Language parser documentation
│   └── README.md            # AST layer documentation
│
├── README.md                 # Core module overview
├── STRUCTURE.md             # This file - architecture documentation
└── __init__.py              # Public API exports
```

---

## Layer Responsibilities

### State Layer (`core/state/`)

**Purpose**: Persistent state management and data access

**Responsibilities**:
- Database schema initialization and migration
- CRUD operations for runs, workstreams, steps, errors, events
- Workstream bundle loading and validation
- Dependency graph construction and cycle detection
- Git worktree lifecycle management
- Audit logging for all state transitions

**Key Abstractions**:
- `WorkstreamBundle` - In-memory representation of workstream
- `Connection` - Database connection with foreign key support
- `DependencyGraph` - DAG for workstream dependencies

**External Dependencies**:
- SQLite (via Python standard library)
- Schema definitions (`schema/schema.sql`)

**Consumed By**:
- `core.engine` - Reads/writes execution state
- `core.planning` - Loads bundles, creates workstreams
- `engine/` - Job execution state tracking
- `error/` - Error recording

---

### Engine Layer (`core/engine/`)

**Purpose**: Workstream orchestration and execution

**Responsibilities**:
- Schedule workstreams in dependency order (waves)
- Execute EDIT → STATIC → RUNTIME step sequence
- Manage FIX retry loops with circuit breakers
- Coordinate parallel execution with worker pools
- Integrate with external tools via adapters
- Track execution metrics and costs
- Handle failures with recovery strategies
- Publish events for observability

**Key Abstractions**:
- `Orchestrator` - Main orchestration loop
- `Scheduler` - Dependency resolution and wave planning
- `Executor` - Individual step execution
- `BaseAdapter` - Tool adapter interface
- `CircuitBreaker` - Fault tolerance pattern
- `RecoveryStrategy` - Failure recovery policy

**External Dependencies**:
- `core.state` - State persistence
- `aim` - Capability-based tool routing (optional)
- Tool binaries (Aider, Claude CLI, etc.)
- `config/tool_profiles.json` - Tool configuration

**Consumed By**:
- `engine/` - Job-based execution wrapper
- CLI tools (`core/ui_cli.py`)
- Automation scripts

---

### Planning Layer (`core/planning/`)

**Purpose**: Workstream lifecycle management and analysis

**Responsibilities**:
- Generate workstream bundles from specs (future automation)
- Archive completed workstreams for analysis
- Bridge CCPM project management with workstreams
- Detect parallelism opportunities
- Validate workstream decomposition

**Key Abstractions**:
- `Planner` - Automated workstream generation (stub)
- `Archive` - Workstream packaging for storage
- `CCPMIntegration` - Task ↔ Workstream conversion
- `ParallelismProfile` - Parallelism analysis results

**External Dependencies**:
- `core.state` - Bundle loading and creation
- `core.ast` - Code analysis for decomposition
- `specifications.tools` - Spec parsing
- `pm/` - CCPM integration

**Consumed By**:
- Automated planning tools (future)
- Post-execution analysis
- Project management integrations

---

### AST Layer (`core/ast/`)

**Purpose**: Static code analysis and structure extraction

**Responsibilities**:
- Parse source code into AST (Tree-sitter)
- Extract functions, classes, imports, variables
- Infer file dependencies from imports
- Support multi-language analysis (Python, JS, TS planned)

**Key Abstractions**:
- `LanguageParser` - Language-specific AST parser
- `Extractor` - High-level extraction API
- `DependencyGraph` - File dependency relationships

**External Dependencies**:
- Tree-sitter library
- Language grammars (tree-sitter-python, etc.)

**Consumed By**:
- `core.planning` - Automated decomposition
- `core.state.bundles` - File scope validation
- `specifications.tools` - Change impact analysis

---

## Data Flow

### Workstream Execution Flow

```
1. LOAD BUNDLE
   ┌──────────────────────────────┐
   │ core.state.bundles           │
   │ load_and_validate_bundles()  │
   └──────────────┬───────────────┘
                  │
                  ▼
2. SCHEDULE
   ┌──────────────────────────────┐
   │ core.engine.scheduler        │
   │ build_execution_plan()       │
   │ - Resolve dependencies       │
   │ - Create waves               │
   └──────────────┬───────────────┘
                  │
                  ▼
3. ORCHESTRATE
   ┌──────────────────────────────┐
   │ core.engine.orchestrator     │
   │ execute_workstreams_parallel()│
   │ - Execute waves              │
   │ - Coordinate workers         │
   └──────────────┬───────────────┘
                  │
                  ▼
4. EXECUTE STEPS
   ┌──────────────────────────────┐
   │ core.engine.executor         │
   │ - EDIT step                  │
   │ - STATIC step (+ FIX loop)   │
   │ - RUNTIME step (+ FIX loop)  │
   └──────────────┬───────────────┘
                  │
                  ▼
5. INVOKE TOOLS
   ┌──────────────────────────────┐
   │ core.engine.adapters         │
   │ - AiderAdapter               │
   │ - ClaudeAdapter              │
   │ - CodexAdapter               │
   └──────────────┬───────────────┘
                  │
                  ▼
6. RECORD STATE
   ┌──────────────────────────────┐
   │ core.state.crud              │
   │ - record_step_attempt()      │
   │ - record_error()             │
   │ - update_workstream_status() │
   └──────────────────────────────┘
```

---

## Module Dependencies

### Dependency Graph

```
core.state ────────────────┐
    │                      │
    ▼                      │
core.planning              │
    │                      │
    ▼                      │
core.ast                   │
                           │
                           ▼
                      core.engine
                           │
                           ▼
                   core.engine.adapters
```

**Rules**:
1. `core.state` has **no internal dependencies** (pure data layer)
2. `core.engine` **depends on** `core.state`
3. `core.planning` **depends on** `core.state` and `core.ast`
4. `core.ast` has **no internal dependencies** (pure utility layer)
5. Adapters **depend only on** `core.engine.adapters.base`

---

## Public API

### Recommended Import Patterns

```python
# State management
from core.state.db import init_db, get_connection
from core.state.crud import create_workstream, get_workstream
from core.state.bundles import load_and_validate_bundles

# Orchestration
from core.engine.orchestrator import run_workstream, execute_workstreams_parallel
from core.engine.scheduler import build_execution_plan

# Planning
from core.planning.planner import plan_workstreams_from_spec
from core.planning.archive import auto_archive

# AST analysis
from core.ast.extractors import extract_functions, extract_dependencies
from core.ast.languages.python import extract_python_functions
```

### Private vs Public

**Public** (safe to import externally):
- `core.state.db` - Database operations
- `core.state.crud` - CRUD operations
- `core.state.bundles` - Bundle management
- `core.engine.orchestrator` - Orchestration
- `core.engine.scheduler` - Scheduling
- `core.planning.*` - Planning utilities
- `core.ast.extractors` - High-level AST API

**Private** (internal use only):
- `core.state.db_sqlite` - SQLite internals
- `core.engine.executor` - Step execution details
- `core.engine.workers` - Worker pool internals
- `core.ast.languages.*` - Language-specific details (use extractors instead)

---

## Configuration

### Environment Variables

- **`PIPELINE_DB_PATH`** - Database location (default: `.worktrees/pipeline_state.db`)
- **`PIPELINE_WORKSTREAM_DIR`** - Workstream bundles directory (default: `workstreams/`)
- **`PIPELINE_DRY_RUN`** - Skip tool invocations (default: `0`)
- **`PIPELINE_MAX_WORKERS`** - Parallel workers (default: `4`)
- **`PIPELINE_TIMEOUT_SEC`** - Global timeout (default: `3600`)
- **`AIM_REGISTRY_PATH`** - AIM registry location (optional)
- **`TREE_SITTER_LIB_PATH`** - Tree-sitter library (optional)

### Configuration Files

- **`schema/schema.sql`** - Database schema
- **`schema/workstream_bundle.schema.json`** - Bundle JSON schema
- **`config/tool_profiles.json`** - Tool adapter configurations
- **`config/circuit_breaker_config.yaml`** - Circuit breaker settings
- **`config/decomposition_rules.yaml`** - Planning rules (future)

---

## Testing Strategy

### Test Organization

```
tests/
├── pipeline/          # State layer tests
│   ├── test_crud.py
│   ├── test_bundles.py
│   └── test_worktree.py
│
├── orchestrator/      # Engine layer tests
│   ├── test_orchestrator.py
│   ├── test_scheduler.py
│   ├── test_executor.py
│   └── test_circuit_breakers.py
│
├── adapters/          # Adapter tests
│   ├── test_aider_adapter.py
│   ├── test_claude_adapter.py
│   └── test_base_adapter.py
│
├── ast/               # AST layer tests
│   ├── test_extractors.py
│   └── test_python_parser.py
│
└── integration/       # End-to-end tests
    ├── test_parallel_execution.py
    └── test_full_pipeline.py
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Layer-specific tests
pytest tests/pipeline/ -v          # State layer
pytest tests/orchestrator/ -v      # Engine layer
pytest tests/ast/ -v               # AST layer

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=core --cov-report=html
```

---

## Extension Points

### Adding New Capabilities

1. **New Tool Adapter**:
   - Implement `BaseAdapter` interface
   - Add to `core/engine/adapters/`
   - Register in `ADAPTERS` dict

2. **New Language Parser**:
   - Implement parser in `core/ast/languages/`
   - Follow interface specification
   - Register in language registry

3. **New Recovery Strategy**:
   - Implement in `core/engine/recovery.py`
   - Add to recovery manager

4. **New Planning Algorithm**:
   - Implement in `core/planning/planner.py`
   - Use `core.ast` for analysis

---

## Performance Characteristics

### State Layer
- **Database**: SQLite, single-threaded writes, parallel reads
- **Bundle Loading**: O(n) for n bundles, includes cycle detection
- **Worktree Creation**: File system operations, can be slow

### Engine Layer
- **Scheduling**: O(n log n) for topological sort
- **Parallel Execution**: Linear speedup up to max_workers
- **Circuit Breakers**: O(1) check per iteration

### AST Layer
- **Parsing**: ~100K lines/sec per file
- **Extraction**: O(n) for n AST nodes
- **Dependency Analysis**: O(n*m) for n files, m imports each

---

## Migration Notes

This module was established in **Phase E refactor**. Legacy paths are deprecated:

**❌ Deprecated**:
```python
from src.pipeline.db import init_db
from src.pipeline.orchestrator import run_workstream
```

**✅ Current**:
```python
from core.state.db import init_db
from core.engine.orchestrator import run_workstream
```

See `docs/CI_PATH_STANDARDS.md` for CI enforcement details.

---

## Related Documentation

- **Module READMEs**: Each subdirectory has detailed README
- **CODEBASE_INDEX.yaml**: Module metadata and dependencies
- **ai_policies.yaml**: Edit policies for AI tools
- **DIRECTORY_GUIDE.md**: Repository navigation
- **docs/ARCHITECTURE.md**: System architecture
- **docs/SECTION_REFACTOR_MAPPING.md**: Import path mapping

---

**For AI Tools**: This is the **highest priority** module for indexing. Understanding `core/` is essential for working with the pipeline system. Always refer to layer responsibilities and public APIs when making changes.
