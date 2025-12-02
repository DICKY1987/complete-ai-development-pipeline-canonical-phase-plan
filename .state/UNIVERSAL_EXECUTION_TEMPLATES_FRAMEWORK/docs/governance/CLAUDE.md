---
doc_id: DOC-GUIDE-CLAUDE-1630
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **⚡ CRITICAL: Read [.meta/AI_GUIDANCE.md](.meta/AI_GUIDANCE.md) FIRST**  
> That 2-minute guide eliminates 25 min of onboarding per session.

## Section 0.1: Foundation - Global Principles

These core principles apply across **all** your work, regardless of repository:

1. **Minimal, surgical changes** - Make the smallest possible edits to achieve the goal. Prefer targeted patches over broad refactors.

2. **Test awareness** - Propose or update tests when changing behavior. Never comment out or delete tests to make them "pass."

3. **Clear communication** - Explain your plan before large refactors. Ask questions when uncertain about requirements or constraints.

4. **Safety first** - Never modify files outside the current repository. Respect edit zones and read-only boundaries.

5. **Git discipline** - All changes must be git-trackable and revertible. Commit secrets are forbidden; use placeholders like `YOUR_API_KEY_HERE`.

**When project-specific rules conflict with these global principles, project rules win.**

---

## Role & Context

You are working in the **Universal Execution Templates (UET) Framework**, a production-ready AI orchestration system for autonomous development workflows.

**Framework Type**: Schema-driven, spec-first development
**Status**: Phase 3 Complete (78% overall) - Orchestration Engine fully operational
**Tests**: 196/196 passing (100%)
**Language**: Python 3.8+

This is a **development framework repository**, not a target project. You'll be working on the orchestration engine itself, not using it to orchestrate other work.

## Core Architecture (Big Picture)

The UET Framework uses a 4-layer architecture that enables AI agents to autonomously manage complex development workflows:

```
┌─────────────────────────────────────────────────────────┐
│              Bootstrap Orchestrator                     │
│  (Auto-discover projects, select profile, generate     │
│   PROJECT_PROFILE.yaml + router_config.json)           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Execution Engine Layer                     │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │ Orchestrator │  Scheduler   │  Router          │    │
│  │ (Run mgmt)   │  (Dep graph) │  (Task→Tool)     │    │
│  └──────────────┴──────────────┴──────────────────┘    │
│  ┌──────────────┬──────────────────────────────────┐   │
│  │ StateMachine │  ProgressTracker / RunMonitor    │   │
│  └──────────────┴──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Tool Adapter Layer                         │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │ Registry     │ Subprocess   │ (Future: API,    │    │
│  │ (Cap match)  │ Adapter      │  Custom, etc.)   │    │
│  └──────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Resilience & State Layer                      │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │ Circuit      │ Retry Logic  │ SQLite State DB  │    │
│  │ Breaker      │ (Exp backoff)│ (runs, steps)    │    │
│  └──────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Schema Foundation (17 JSON Schemas)           │
│  phase_spec, execution_request, project_profile,        │
│  router_config, task_spec, workstream_spec, etc.        │
└─────────────────────────────────────────────────────────┘
```

### Key Concepts

- **Bootstrap**: Auto-discovers project structure, selects appropriate profile (Python/data/docs/ops/generic), generates configuration
- **Phase**: Major workflow stage with FILES_SCOPE, CONSTRAINTS, ACCEPTANCE criteria
- **Workstream**: Parallel execution stream within a phase
- **Task**: Atomic unit of work with task_kind (code_edit, analysis, refactor, etc.)
- **Adapter**: Tool integration abstraction (currently subprocess, extensible to API/custom)
- **Resilience**: Circuit breakers + exponential backoff retry + failure tracking
- **Schema-Driven**: All artifacts validate against JSON schemas before use

## Directory Structure

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── core/                          # Implementation (26 modules)
│   ├── bootstrap/                 # Auto-project configuration
│   │   ├── orchestrator.py        # Main bootstrap entry point
│   │   ├── discovery.py           # Project scanner
│   │   ├── selector.py            # Profile selector
│   │   ├── generator.py           # Artifact generator
│   │   └── validator.py           # Bootstrap validator
│   │
│   ├── engine/                    # Orchestration engine
│   │   ├── orchestrator.py        # Run management
│   │   ├── state_machine.py       # State transitions
│   │   ├── scheduler.py           # Dependency resolution
│   │   ├── router.py              # Task routing
│   │   ├── execution_request_builder.py
│   │   ├── resilience/            # Fault tolerance
│   │   │   ├── circuit_breaker.py
│   │   │   ├── retry.py
│   │   │   └── resilient_executor.py
│   │   └── monitoring/            # Progress tracking
│   │       ├── progress_tracker.py
│   │       └── run_monitor.py
│   │
│   ├── adapters/                  # Tool integration
│   │   ├── base.py                # Abstract adapter
│   │   ├── subprocess_adapter.py  # CLI tool wrapper
│   │   └── registry.py            # Adapter registry
│   │
│   └── state/                     # State management
│       └── db.py                  # SQLite database
│
├── schema/                        # JSON schemas (17 files)
│   ├── phase_spec.v1.json         # Phase definitions
│   ├── execution_request.v1.json  # Execution requests
│   ├── project_profile.v1.json    # Project profiles
│   ├── router_config.v1.json      # Router configuration
│   └── ...                        # 13 more schemas
│
├── profiles/                      # Project type templates
│   ├── software-dev-python/       # Python projects (most complete)
│   ├── data-pipeline/             # ETL/ML pipelines
│   ├── documentation/             # Docs projects
│   ├── operations/                # DevOps/SRE
│   └── generic/                   # Fallback
│
├── specs/                         # Documentation
│   ├── UET_BOOTSTRAP_SPEC.md
│   ├── UET_TASK_ROUTING_SPEC.md
│   ├── UET_PHASE_SPEC_MASTER.md
│   ├── UET_WORKSTREAM_SPEC.md
│   └── STATUS.md                  # Current progress
│
└── tests/                         # 196 tests
    ├── schema/                    # Schema validation (22)
    ├── bootstrap/                 # Bootstrap tests (8)
    ├── engine/                    # Engine tests (92)
    ├── adapters/                  # Adapter tests (27)
    ├── resilience/                # Resilience tests (32)
    └── monitoring/                # Monitoring tests (15)
```

## Common Development Commands

```bash
# Run all tests (REQUIRED before commits)
pytest tests/ -v

# Run specific test suites
pytest tests/bootstrap/ -v
pytest tests/engine/ -v
pytest tests/resilience/ -v
pytest tests/monitoring/ -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html

# Bootstrap a project (framework usage example)
python core/bootstrap/orchestrator.py /path/to/target/project

# Run specific test by name
pytest tests/engine/test_scheduler.py::test_detect_cycles -v
```

**No build/compile step** - Pure Python, no compilation needed.

## Import Path Standards

Use **section-based imports** from the `core/` package:

```python
# Bootstrap system
from core.bootstrap.orchestrator import BootstrapOrchestrator
from core.bootstrap.discovery import ProjectScanner
from core.bootstrap.selector import ProfileSelector

# Execution engine
from core.engine.orchestrator import Orchestrator
from core.engine.scheduler import ExecutionScheduler, Task
from core.engine.router import TaskRouter
from core.engine.state_machine import RunStateMachine, RunState
from core.engine.execution_request_builder import ExecutionRequestBuilder

# Resilience patterns
from core.engine.resilience import ResilientExecutor
from core.engine.resilience import CircuitBreaker, RetryStrategy

# Monitoring
from core.engine.monitoring import ProgressTracker, RunMonitor

# Adapters
from core.adapters import AdapterRegistry, ToolConfig
from core.adapters.base import BaseAdapter, ExecutionResult

# State management
from core.state.db import Database, get_db
```

**Common pitfall**: Don't import from `tests/` in production code. Tests should import from `core/`, not vice versa.

## Schema-Driven Development Workflow

All artifacts in this framework must validate against JSON schemas. This is **non-negotiable**.

**Development Process**:
1. Write specification in `specs/` (e.g., `UET_NEW_FEATURE_SPEC.md`)
2. Create/update JSON schema in `schema/` (e.g., `new_feature.v1.json`)
3. Implement Python code in `core/`
4. Add tests in `tests/`
5. Update `specs/STATUS.md` with progress

**Key Schemas**:
- `phase_spec.v1.json` - Phase definitions (FILES_SCOPE, CONSTRAINTS, ACCEPTANCE)
- `execution_request.v1.json` - Task execution requests
- `project_profile.v1.json` - Auto-generated project configuration
- `router_config.v1.json` - Tool routing and capability matching
- `task_spec.v1.json` - Task specifications
- `workstream_spec.v1.json` - Workstream definitions

**Validation**: Schema tests in `tests/schema/` ensure all schemas are valid and examples conform.

## Phase-Aware Execution Model

The framework uses **Phase constraints** to ensure safe, predictable execution:

### Phase Structure
```yaml
phase_id: "PH-001"
FILES_SCOPE:
  read: ["*.py", "tests/*"]
  write: ["core/engine/*.py"]
  create: []
  forbidden: ["schema/*", "specs/*"]
CONSTRAINTS:
  tests_must_pass: true
  patch_only: true
  max_lines_changed: 500
ACCEPTANCE:
  - "All engine tests pass"
  - "Circuit breaker handles failures"
```

### ExecutionRequest Constraints
When building an ExecutionRequest, constraints must be **subset/equal/stricter** than Phase constraints:

```python
# ✅ VALID: Tighter than Phase
execution_request = {
    "files_scope": {
        "read": ["core/engine/*.py"],  # Subset of Phase read
        "write": ["core/engine/resilience/*.py"]  # Subset of Phase write
    },
    "constraints": {
        "patch_only": True,
        "max_lines_changed": 200  # Stricter than Phase (500)
    }
}

# ❌ INVALID: Looser than Phase
execution_request = {
    "files_scope": {
        "write": ["schema/*"]  # Forbidden in Phase!
    },
    "constraints": {
        "max_lines_changed": 1000  # Looser than Phase (500)
    }
}
```

See `core/engine/execution_request_builder.py` for validation logic.

## Resilience Patterns

All external tool invocations should use `ResilientExecutor` for fault tolerance:

```python
from core.engine.resilience import ResilientExecutor

executor = ResilientExecutor()

# Register tool with resilience config
executor.register_tool(
    "aider",
    failure_threshold=5,     # Open circuit after 5 failures
    recovery_timeout=60,     # Try recovery after 60s
    max_retries=3,          # Retry up to 3 times
    base_delay=1.0          # Exponential backoff from 1s
)

# Execute with automatic retry + circuit breaker
result = executor.execute("aider", lambda: run_aider_command())
```

**Circuit Breaker States**:
- `CLOSED`: Normal operation
- `OPEN`: Too many failures, reject immediately
- `HALF_OPEN`: Testing recovery, allow one request

**Retry Strategy**: Exponential backoff with jitter
- Attempt 1: base_delay (1s)
- Attempt 2: base_delay * 2 (2s)
- Attempt 3: base_delay * 4 (4s)

## Key Workflows

### Bootstrap Workflow (5 Steps)

Entry point: `python core/bootstrap/orchestrator.py /path/to/project`

```
1. Discovery (discovery.py)
   ↓ Scans project structure, detects languages/frameworks/tools

2. Profile Selection (selector.py)
   ↓ Scores profiles, selects best match (python/data/docs/ops/generic)

3. Artifact Generation (generator.py)
   ↓ Generates PROJECT_PROFILE.yaml, router_config.json

4. Validation (validator.py)
   ↓ Validates against schemas, checks constraints

5. Report Generation (orchestrator.py)
   ↓ Outputs bootstrap_report.json, creates .framework_initialized
```

Files touched: Project root gets `PROJECT_PROFILE.yaml`, `router_config.json`, `.framework_initialized`

### Execution Workflow (6 Steps)

Entry point: `Orchestrator.create_run()` → `scheduler.get_execution_order()` → `router.route_task()`

```
1. Create Run (orchestrator.py)
   ↓ Initialize run_id (ULID), persist to SQLite

2. Schedule Tasks (scheduler.py)
   ↓ Build dependency graph, topological sort, detect cycles

3. Build ExecutionRequest (execution_request_builder.py)
   ↓ Validate against Phase constraints, ensure subset/equal/stricter

4. Route to Tool (router.py)
   ↓ Match task capabilities, select adapter

5. Execute with Resilience (resilient_executor.py)
   ↓ Circuit breaker check → Retry loop → Execute → Track progress

6. State Transition (state_machine.py)
   ↓ Update run state: PENDING → RUNNING → COMPLETED/FAILED
```

State persisted in: `.worktrees/pipeline_state.db` (SQLite)

### Task Routing Logic

Entry point: `TaskRouter.route_task(execution_request)`

```
1. Extract task classification
   ↓ task_kind, domain, complexity, risk_tier

2. Query adapter registry (registry.py)
   ↓ registry.find_for_task(task_kind, domain)

3. Capability matching
   ↓ Filter adapters by capabilities, supported_domains, task_kinds

4. Strategy selection (router_config.json)
   ↓ auto: Pick best match
   ↓ manual: Prompt user
   ↓ fixed: Use pre-configured mapping

5. Return ToolConfig
   ↓ tool_name, adapter_type, timeout, parallelism_limit
```

Routing rules defined in: `router_config.json` (generated by bootstrap)

## Testing Requirements

**Critical**: All 196 tests must pass before commits.

```bash
# Run full suite (REQUIRED)
pytest tests/ -v

# Expected output
tests/schema/          22 passed
tests/bootstrap/       8 passed
tests/engine/          92 passed
tests/adapters/        27 passed
tests/resilience/      32 passed
tests/monitoring/      15 passed
======================== 196 passed ========================
```

**Test Organization**:
- `tests/schema/` - Schema validation (all 17 schemas)
- `tests/bootstrap/` - Bootstrap system (discovery, selection, generation)
- `tests/engine/` - Orchestrator, scheduler, router, state machine
- `tests/adapters/` - Adapter registry, subprocess adapter
- `tests/resilience/` - Circuit breaker, retry, resilient executor
- `tests/monitoring/` - Progress tracker, run monitor

**Coverage Expectations**:
- Core modules: ~80% coverage
- New public APIs: Must have tests
- Bug fixes: Add regression tests

## Coding Conventions

**Python Style**:
- Black/PEP8 compliant (4-space indent)
- Type hints preferred in new code
- Docstrings for public APIs (Google style)
- `snake_case` for functions/modules
- `PascalCase` for classes

**Module Structure**:
- Each workstream maps to a module (e.g., WS-03-02A → `adapters/`)
- ABC pattern for extensibility (`BaseAdapter`, `BaseRetryStrategy`)
- Clear separation of concerns

**Example**:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAdapter(ABC):
    """Abstract base for tool adapters.

    Provides interface for executing tasks via external tools.
    Subclasses implement tool-specific execution logic.
    """

    @abstractmethod
    def execute(self, request: Dict[str, Any], timeout: Optional[int] = None) -> ExecutionResult:
        """Execute task using this adapter.

        Args:
            request: Execution request conforming to execution_request.v1.json
            timeout: Optional timeout in seconds

        Returns:
            ExecutionResult with status, output, error
        """
        pass
```

## Critical Invariants

1. **Schema Validation Required**: All generated artifacts MUST validate against JSON schemas. No exceptions.

2. **Phase Constraints**: ExecutionRequest constraints must be subset/equal/stricter than Phase constraints. Never looser.

3. **Tests Must Pass**: 196/196 tests must pass before commits. CI enforces this.

4. **ULID Identifiers**: All run/step/task IDs use 26-character uppercase hex (currently UUID-based, TODO: migrate to actual ULID).

5. **State Machine Driven**: All run state transitions must go through `RunStateMachine`. No direct DB updates.

6. **Patch-Only Mode**: Default for `software-dev-python` profile. Respect `patch_only: true` constraint.

7. **Schema Versioning**: All schemas use `.v1.json` suffix. Breaking changes require new version.

## Important File Locations

**Generated Artifacts** (per target project):
- `PROJECT_PROFILE.yaml` - Project-specific configuration
- `router_config.json` - Tool routing rules
- `.framework_initialized` - Bootstrap completion marker
- `.worktrees/` - Isolated execution environments
- `.tasks/` - Task queue directories
- `.ledger/` - Patch and run ledgers

**Framework Core** (this repository):
- `core/` - All implementation code
- `schema/` - All JSON schemas (17 files)
- `specs/` - All documentation and specifications
- `profiles/` - Project type templates
- `tests/` - All test suites
- `docs/integration/` - Integration documentation

## Key References

When working on this framework, consult these documents:

- **`specs/UET_BOOTSTRAP_SPEC.md`** - Bootstrap system design and workflow
- **`specs/UET_TASK_ROUTING_SPEC.md`** - Task routing logic and capability matching
- **`specs/UET_PHASE_SPEC_MASTER.md`** - Phase-based execution model
- **`specs/UET_WORKSTREAM_SPEC.md`** - Workstream definitions and parallelism
- **`specs/UET_COOPERATION_SPEC.md`** - Multi-agent coordination patterns
- **`specs/STATUS.md`** - Current progress, what's done, what's pending
- **`docs/integration/UET_INTEGRATION_DESIGN.md`** - Integration with other systems
- **`docs/integration/UET_QUICK_REFERENCE.md`** - Quick reference for common tasks
- **`schema/*.json`** - Canonical schemas for all data structures

## Non-Obvious Behaviors

**ULID Generation**: Currently uses UUID4 as placeholder
```python
from core.engine.orchestrator import generate_ulid
run_id = generate_ulid()  # Returns 26-char uppercase hex (TODO: real ULID)
```

**Database Location**: SQLite DB in `.worktrees/pipeline_state.db` by default
- Tables: `runs`, `steps`, `step_attempts`, `run_events`
- Use `get_db()` for singleton access
- Connection pooling handled automatically

**Profile Auto-Detection**: Based on file pattern scoring
- `*.py` files → software-dev-python
- `dbt_project.yml` or `airflow.cfg` → data-pipeline
- `mkdocs.yml` or `docs/` → documentation
- `ansible.cfg` or `terraform.tf` → operations
- Fallback → generic

**Circuit Breaker Recovery**: Uses half-open state for testing
- After `recovery_timeout`, allow ONE request
- If successful → CLOSED (normal operation)
- If failed → OPEN (wait another recovery_timeout)

**Parallel Execution**: Scheduler supports max_parallel batches
```python
batches = scheduler.get_parallel_batches(max_parallel=3)
# Returns: [[task1, task2, task3], [task4, task5], [task6]]
# Execute each batch concurrently, batches sequentially
```

## Development Tips

1. **Start with specs**: Read `specs/UET_*.md` before coding
2. **Validate early**: Run schema tests frequently
3. **Use type hints**: Helps with IDE autocomplete and catches bugs
4. **Test resilience**: Simulate failures in tests (see `tests/resilience/`)
5. **Check STATUS.md**: Understand what's done and what's in progress
6. **Follow patterns**: Look at existing modules for consistency
7. **Keep it simple**: Framework should be easy to understand and extend
