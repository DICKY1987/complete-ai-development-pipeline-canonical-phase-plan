# Modular Architecture Guide

## Overview

This document defines the modular architecture of the AI Development Pipeline, establishing clear boundaries, responsibilities, and interfaces between components.

## Module Structure

### Core Modules

```
src/
├── pipeline/       # Core orchestration and workflow execution
├── plugins/        # Plugin ecosystem for tool integrations
└── utils/          # Shared utility functions
```

## Module Definitions

### 1. Pipeline Module (`src/pipeline/`)

**Purpose:** Core orchestration, workflow management, and execution control.

**Public Interface:**
- Orchestrator - Main workflow execution
- Scheduler - Dependency resolution and scheduling (stub)
- Executor - Parallel task execution (stub)
- Bundles - Workstream bundle loading and validation
- Tools - External tool execution adapter

**Internal Components:**
- DB operations (database abstraction)
- Circuit breakers (failure detection)
- Prompts (AI integration)
- Worktree management
- Error tracking

**Dependencies:**
- External: jsonschema, Jinja2
- Internal: src.utils

**Key Responsibilities:**
- Workstream orchestration (EDIT → STATIC → RUNTIME)
- Tool execution and result tracking
- Database state management
- AI tool integration (Aider)
- Error detection and recovery

### 2. Plugins Module (`src/plugins/`)

**Purpose:** Extensible plugin ecosystem for language-specific and cross-cutting tools.

**Public Interface:**
- Plugin registration via `register()` function
- Standard plugin contract (check_tool_available, build_command, execute)
- Normalized result format (PluginResult, PluginIssue)

**Plugin Categories:**
- **Python:** formatters (black, isort), linters (ruff, pylint), type checkers (mypy, pyright), security (bandit, safety)
- **JavaScript/TypeScript:** formatters (prettier), linters (eslint)
- **PowerShell:** PSScriptAnalyzer
- **Markup/Data:** YAML (yamllint), Markdown (mdformat, markdownlint), JSON (jq)
- **Cross-Cutting:** codespell, semgrep, gitleaks

**Dependencies:**
- External: Tool-specific binaries (ruff, black, etc.)
- Internal: src.utils (env, types)

**Key Responsibilities:**
- Tool availability detection
- Command construction
- Subprocess execution with timeouts
- Output parsing to normalized format
- Graceful degradation (missing tools)

### 3. Utils Module (`src/utils/`)

**Purpose:** Shared utility functions with no business logic dependencies.

**Public Interface:**
- `env.py` - Environment variable scrubbing
- `types.py` - Shared type definitions (PluginIssue, PluginResult)
- `hashing.py` - Hash computation utilities
- `time.py` - Time/timestamp utilities
- `jsonl_manager.py` - JSONL file operations

**Dependencies:**
- External: None (stdlib only)
- Internal: None (leaf module)

**Key Responsibilities:**
- Environment sanitization for subprocess execution
- Shared data structures
- Common utility functions
- No business logic

## Dependency Rules

### Module Dependency Graph

```
utils (no internal dependencies)
  ↓
plugins (depends on: utils)
  ↓
pipeline (depends on: utils, optionally plugins via tool profiles)
```

### Principles

1. **Acyclic Dependencies:** No circular dependencies between modules
2. **Layered Architecture:** Higher layers can depend on lower layers, not vice versa
3. **Interface Segregation:** Modules expose minimal public APIs via `__init__.py`
4. **Dependency Inversion:** Core logic depends on abstractions, not concrete implementations

## Module Boundaries

### Pipeline ↔ Plugins

**Coupling:** Loose (via tool profiles and subprocess)

The pipeline module does NOT directly import plugin modules. Instead:
- Tool profiles (`config/tool_profiles.json`) define tool commands
- `pipeline/tools.py` executes tools via subprocess
- Plugins are discovered and registered independently
- Error pipeline can invoke plugins via `agent_coordinator.py`

### Pipeline ↔ Utils

**Coupling:** Tight (direct imports allowed)

Pipeline modules can directly import from utils:
```python
from src.utils.env import scrub_env
from src.utils.types import PluginIssue, PluginResult
```

### Plugins ↔ Utils

**Coupling:** Tight (direct imports allowed)

Plugins can directly import from utils:
```python
from src.utils.env import scrub_env
from src.utils.types import PluginResult, PluginIssue
```

## Public API Contracts

### Pipeline Module API

Export only essential orchestration functions:
```python
# src/pipeline/__init__.py
from .orchestrator import run_workstream, run_single_workstream_from_bundle
from .bundles import load_and_validate_bundles, WorkstreamBundle
from .tools import run_tool, ToolResult
```

### Plugins Module API

Export registration protocol:
```python
# src/plugins/__init__.py
# Plugins self-register via plugin.py::register()
# No need to expose internal plugin classes
```

### Utils Module API

Export all utilities (already public):
```python
# src/utils/__init__.py
from .env import scrub_env
from .types import PluginIssue, PluginResult
from .hashing import compute_hash
from .time import utc_now
from .jsonl_manager import JSONLManager
```

## Testing Strategy

### Module Isolation

- **Unit Tests:** Test modules in isolation with mocked dependencies
- **Integration Tests:** Test cross-module interactions
- **Contract Tests:** Validate public API stability

### Test Organization

```
tests/
├── pipeline/          # Pipeline module tests
├── plugins/           # Plugin ecosystem tests
├── integration/       # Cross-module integration tests
└── test_*.py          # Top-level integration tests
```

## Migration Guidelines

### For New Code

1. Identify which module the code belongs to
2. Use public APIs from other modules
3. Add new public APIs to `__init__.py` if needed
4. Follow dependency rules (no cycles)

### For Existing Code

1. No changes required unless refactoring
2. Existing imports continue to work
3. Gradually migrate to public APIs
4. Add explicit exports to `__init__.py` over time

## Benefits

### Modularity

- **Clear Boundaries:** Each module has well-defined responsibilities
- **Loose Coupling:** Modules interact via stable interfaces
- **High Cohesion:** Related code lives together

### Maintainability

- **Easier Testing:** Modules can be tested in isolation
- **Reduced Complexity:** Clear structure reduces cognitive load
- **Safe Refactoring:** Changes within module boundaries are low-risk

### Extensibility

- **Plugin Architecture:** New tools added without core changes
- **Swappable Components:** Database, tools, etc. can be replaced
- **Parallel Development:** Teams can work on different modules

## Future Enhancements

### Phase 1 (Current)
- [x] Document module boundaries
- [x] Define public APIs in `__init__.py`
- [ ] Add architectural validation tests

### Phase 2 (Future)
- [ ] Extract database interface layer
- [ ] Create service layer for orchestration
- [ ] Implement dependency injection
- [ ] Add module-level configuration

### Phase 3 (Future)
- [ ] Plugin registry with dynamic loading
- [ ] Event-driven architecture for pipeline steps
- [ ] API versioning for module contracts
