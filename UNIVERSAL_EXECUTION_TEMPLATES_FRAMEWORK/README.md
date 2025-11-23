# Universal Execution Templates (UET) Framework

> A comprehensive AI development pipeline system for orchestrating autonomous workflows across any project type.

[![Tests](https://img.shields.io/badge/tests-196%2F196%20passing-success)]()
[![Progress](https://img.shields.io/badge/progress-78%25-blue)]()
[![Phase](https://img.shields.io/badge/phase-3%20complete-brightgreen)]()

## Overview

The **Universal Execution Templates Framework** is a production-ready orchestration system that enables AI agents to autonomously manage complex development workflows. It provides schema-driven execution, resilience patterns, and project-agnostic templates for any codebase.

### Key Features

- **🤖 Autonomous Bootstrap** - Point at any project and automatically configure
- **📋 Project Profiles** - Pre-built templates for Python, data pipelines, documentation, and more
- **⚡ Parallel Execution** - Smart task scheduling with dependency resolution
- **🔄 Resilience Patterns** - Circuit breakers, retry logic, and automatic recovery
- **📊 Progress Tracking** - Real-time monitoring with detailed metrics
- **🔌 Tool Adapters** - Extensible system for integrating any CLI tool
- **📐 Schema-Driven** - 17 JSON schemas for type-safe operations

## Quick Start

### Bootstrap a New Project

```bash
# Navigate to the framework
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

# Run bootstrap on your project
python core/bootstrap/orchestrator.py /path/to/your/project

# This will:
# 1. Discover your project structure
# 2. Select the appropriate profile
# 3. Generate PROJECT_PROFILE.yaml and router_config.json
# 4. Validate all artifacts
```

### Programmatic Usage

```python
from core.bootstrap.orchestrator import BootstrapOrchestrator
from core.engine.scheduler import ExecutionScheduler, Task
from core.engine.resilience import ResilientExecutor

# Bootstrap your project
bootstrap = BootstrapOrchestrator("/path/to/project")
result = bootstrap.run()

# Define workflow
tasks = [
    Task('analyze', 'analysis'),
    Task('implement', 'code_edit', depends_on=['analyze']),
    Task('test', 'testing', depends_on=['implement'])
]

# Schedule execution
scheduler = ExecutionScheduler()
scheduler.add_tasks(tasks)
order = scheduler.get_execution_order()

# Execute with resilience
executor = ResilientExecutor()
executor.register_tool("aider", max_retries=3, failure_threshold=5)
```

## Directory Structure

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── README.md                    # This file
├── specs/                       # 📚 All documentation & specifications
│   ├── UET_BOOTSTRAP_SPEC.md   # Bootstrap system design
│   ├── UET_COOPERATION_SPEC.md # Multi-agent coordination
│   ├── UET_PHASE_SPEC_MASTER.md # Phase-based execution
│   ├── UET_TASK_ROUTING_SPEC.md # Task routing logic
│   ├── UET_WORKSTREAM_SPEC.md  # Workstream definitions
│   └── STATUS.md               # Current progress & metrics
├── templates/                   # 🎨 Reusable Templates (NEW)
│   ├── orchestration/          # Phase, workstream, DAG, task templates
│   ├── adapters/               # Tool adapter templates
│   ├── configuration/          # Profile, router, constraint templates
│   ├── ui/                     # Dashboard, report, monitoring templates
│   └── examples/               # Complete working examples
├── core/                        # 🔧 Implementation (26 modules)
│   ├── bootstrap/              # Project discovery & setup
│   ├── engine/                 # Orchestration & execution
│   │   ├── monitoring/         # Progress tracking
│   │   └── resilience/         # Circuit breakers & retry
│   ├── adapters/               # Tool integration layer
│   └── state/                  # State management
├── schema/                      # 📐 JSON schemas (17 files)
│   ├── phase_spec.v1.json
│   ├── task_spec.v1.json
│   ├── execution_request.v1.json
│   └── ...
├── profiles/                    # 📋 Project type templates
│   ├── software-dev-python/
│   ├── data-pipeline/
│   ├── documentation/
│   ├── operations/
│   └── generic/
└── tests/                       # ✅ Test suites (196 tests)
    ├── bootstrap/
    ├── engine/
    ├── adapters/
    ├── resilience/
    └── monitoring/
```

## Templates (NEW)

The **`templates/`** directory provides reusable components following AI-codebase structure principles. Templates are organized by architectural layer and include comprehensive documentation.

### Quick Access

- **[Templates Overview](templates/README.md)** - Master index and quick start
- **[Templates Structure](templates/STRUCTURE.md)** - Detailed organization guide
- **[Templates Context](templates/CONTEXT.md)** - Execution model and usage patterns

### Template Categories

| Category | Purpose | Location |
|----------|---------|----------|
| **Orchestration** | Phases, workstreams, DAGs, tasks | [templates/orchestration/](templates/orchestration/) |
| **Adapters** | Tool integration templates | [templates/adapters/](templates/adapters/) |
| **Configuration** | Profiles, routers, constraints | [templates/configuration/](templates/configuration/) |
| **UI** | Dashboards, reports, monitoring | [templates/ui/](templates/ui/) |
| **Examples** | Complete working implementations | [templates/examples/](templates/examples/) |

### Using Templates

```bash
# Browse available templates
ls templates/orchestration/phases/

# Copy a template
cp templates/orchestration/phases/phase-core-template.yaml my-phase.yaml

# Customize (replace {{PLACEHOLDERS}})
# Validate
python core/bootstrap/validator.py my-phase.yaml

# Use in your workflow
```

See [templates/README.md](templates/README.md) for complete documentation.

## Documentation

### Core Specifications

All specifications are in the [`specs/`](specs/) directory:

| Document | Purpose |
|----------|---------|
| [UET_BOOTSTRAP_SPEC.md](specs/UET_BOOTSTRAP_SPEC.md) | How to bootstrap any project |
| [UET_TASK_ROUTING_SPEC.md](specs/UET_TASK_ROUTING_SPEC.md) | Task routing & execution requests |
| [UET_PHASE_SPEC_MASTER.md](specs/UET_PHASE_SPEC_MASTER.md) | Phase-based workflow structure |
| [UET_WORKSTREAM_SPEC.md](specs/UET_WORKSTREAM_SPEC.md) | Workstream definitions |
| [UET_COOPERATION_SPEC.md](specs/UET_COOPERATION_SPEC.md) | Multi-agent coordination |
| [UET_PATCH_MANAGEMENT_SPEC.md](specs/UET_PATCH_MANAGEMENT_SPEC.md) | Patch/diff management |
| [UET_PROMPT_RENDERING_SPEC.md](specs/UET_PROMPT_RENDERING_SPEC.md) | Prompt generation system |
| [STATUS.md](specs/STATUS.md) | Current progress & statistics |

### Key Concepts

- **Bootstrap**: Autonomous project discovery and configuration
- **Profiles**: Project type templates (Python, data, docs, ops, generic)
- **Phases**: Major workflow stages with defined inputs/outputs
- **Workstreams**: Parallel execution streams within phases
- **Tasks**: Atomic units of work routed to tools
- **Adapters**: Tool integration layer (subprocess, API, etc.)
- **Resilience**: Circuit breakers, retries, exponential backoff

## Current Status

**Version**: 1.0.0-beta
**Overall Progress**: 78% Complete
**Tests Passing**: 196/196 (100%)

### Completed Phases ✅

- **Phase 0**: Schema Foundation (100%)
  - 17 JSON schemas
  - Complete type system

- **Phase 1**: Profile System (60%)
  - 5 domain profiles
  - Software-dev-python has full templates

- **Phase 2**: Bootstrap Implementation (100%)
  - Project scanner
  - Profile selector
  - Artifact generator
  - Validation engine

- **Phase 3**: Orchestration Engine (100%)
  - Run management & state tracking
  - Task routing & scheduling
  - Tool adapter framework
  - Circuit breakers & retry logic
  - Progress tracking & monitoring

### In Progress 🚧

- **Phase 4**: Documentation & Examples (20%)
  - API documentation
  - User guides
  - Example projects
  - Integration tests

## Features in Detail

### 🤖 Autonomous Bootstrap

The framework can analyze any project and configure itself:

```bash
python core/bootstrap/orchestrator.py /path/to/project
```

**What it does:**
1. Scans project structure (languages, frameworks, tools)
2. Selects best-matching profile
3. Generates PROJECT_PROFILE.yaml
4. Creates router_config.json for tool routing
5. Validates all artifacts

### ⚡ Smart Task Scheduling

Execute tasks in optimal order with automatic dependency resolution:

```python
scheduler = ExecutionScheduler()
scheduler.add_tasks(tasks)

# Get topological order
order = scheduler.get_execution_order()

# Get parallel batches (max 3 concurrent)
batches = scheduler.get_parallel_batches(max_parallel=3)

# Detect circular dependencies
cycle = scheduler.detect_cycles()
```

### 🔄 Resilience Patterns

Built-in fault tolerance for external tools:

```python
executor = ResilientExecutor()

# Configure per-tool settings
executor.register_tool(
    "aider",
    failure_threshold=5,     # Open circuit after 5 failures
    recovery_timeout=60,     # Try recovery after 60s
    max_retries=3,          # Retry up to 3 times
    base_delay=1.0          # Exponential backoff from 1s
)

# Execute with automatic retry
result = executor.execute("aider", lambda: risky_operation())
```

### 📊 Progress Tracking

Monitor execution in real-time:

```python
tracker = ProgressTracker("run-123", total_tasks=10)
tracker.start()

tracker.start_task("task-1")
tracker.update_task_progress(50.0)
tracker.complete_task("task-1", duration=5.2)

# Get live snapshot
snapshot = tracker.get_snapshot()
print(f"Progress: {snapshot.completion_percent}%")
print(f"ETA: {snapshot.estimated_completion}")
```

### 🔌 Tool Adapters

Integrate any CLI tool or API:

```python
from core.adapters import AdapterRegistry

registry = AdapterRegistry("router_config.json")

# Find tools for a task
capable = registry.find_for_task('code_edit', domain='python')

# Execute
adapter = registry.get('aider')
result = adapter.execute(request, timeout=300)
```

## Project Profiles

The framework includes 5 built-in profiles:

| Profile | Use Case | Languages | Tools |
|---------|----------|-----------|-------|
| **software-dev-python** | Python projects | Python | pytest, ruff, aider |
| **data-pipeline** | ETL/ML pipelines | Python, SQL | pandas, dbt, airflow |
| **documentation** | Docs projects | Markdown | mkdocs, sphinx |
| **operations** | DevOps/SRE | YAML, Shell | ansible, terraform |
| **generic** | Any project | Multi-language | Universal tools |

Each profile includes:
- Tool routing configuration
- Phase templates
- Domain-specific constraints
- Recommended workflows

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/bootstrap/ -v
pytest tests/engine/ -v
pytest tests/resilience/ -v

# With coverage
pytest tests/ --cov=core --cov-report=html
```

**Current Test Coverage:**
- Schema tests: 22/22 ✅
- Bootstrap tests: 8/8 ✅
- Engine tests: 92/92 ✅
- Adapter tests: 27/27 ✅
- Resilience tests: 32/32 ✅
- Monitoring tests: 15/15 ✅

## Contributing

This framework follows a **spec-driven development** approach:

1. **Write spec** - Create/update UET_*.md in specs/
2. **Create schema** - Define JSON schema in schema/
3. **Implement** - Write Python code in core/
4. **Test** - Add tests in tests/
5. **Document** - Update STATUS.md

## Architecture

The framework uses a layered architecture:

```
┌─────────────────────────────────────┐
│         CLI / API Layer            │
├─────────────────────────────────────┤
│      Bootstrap Orchestrator        │
├─────────────────────────────────────┤
│     Execution Engine               │
│  ┌─────────┬─────────┬──────────┐  │
│  │ Router  │Scheduler│ Monitor  │  │
│  └─────────┴─────────┴──────────┘  │
├─────────────────────────────────────┤
│      Tool Adapter Layer            │
│  ┌─────────┬─────────┬──────────┐  │
│  │Subprocess│  API   │ Custom   │  │
│  └─────────┴─────────┴──────────┘  │
├─────────────────────────────────────┤
│    Resilience & State Layer        │
│  ┌─────────┬─────────┬──────────┐  │
│  │Circuit  │ Retry   │ State DB │  │
│  │Breaker  │ Logic   │          │  │
│  └─────────┴─────────┴──────────┘  │
├─────────────────────────────────────┤
│        Schema Foundation           │
│     (17 JSON Schemas v1)           │
└─────────────────────────────────────┘
```

## License

[Specify your license here]

## Support

- **Documentation**: See [`specs/`](specs/) directory
- **Issues**: [Report bugs or request features]
- **Status**: Check [`specs/STATUS.md`](specs/STATUS.md) for current progress

---

**Built with**: Python 3.8+, JSON Schema, SQLite
**Status**: Production-ready orchestration engine (Phase 3 complete)
**Next**: Documentation & examples (Phase 4)
