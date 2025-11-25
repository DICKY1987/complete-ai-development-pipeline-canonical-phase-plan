# Dependency Analysis

**Purpose:** Document code dependencies and conceptual relationships to help AI agents understand module coupling and change impact.

**Last Updated:** 2025-11-22  
**Maintainer:** System Architecture Team

---

## Overview

This document provides:
- **Code Dependencies:** Which modules import which
- **Conceptual Dependencies:** Which concepts depend on others
- **Coupling Analysis:** How tightly modules are coupled
- **Change Impact:** What breaks when dependencies change

---

## Module Dependency Graph

### Core Dependencies

```
core/
├── state/
│   ├── db.py
│   │   └── Depends on: sqlite3 (stdlib)
│   ├── workstreams.py
│   │   └── Depends on: core.state.db
│   └── steps.py
│       └── Depends on: core.state.db, core.state.workstreams
│
├── engine/
│   ├── orchestrator.py
│   │   ├── Depends on: core.state.workstreams
│   │   ├── Depends on: core.state.steps
│   │   ├── Depends on: core.engine.tools
│   │   └── Depends on: core.engine.scheduler
│   ├── scheduler.py
│   │   └── Depends on: (no internal deps)
│   ├── tools.py
│   │   ├── Depends on: subprocess (stdlib)
│   │   └── Depends on: json (stdlib)
│   └── circuit_breaker.py
│       └── Depends on: time (stdlib)
│
└── planning/
    ├── planner.py
    │   └── Depends on: core.state.workstreams
    └── archiver.py
        └── Depends on: core.state.workstreams
```

### Error Detection Dependencies

```
error/
├── engine/
│   ├── error_engine.py
│   │   ├── Depends on: error.engine.plugin_manager
│   │   ├── Depends on: error.engine.file_cache
│   │   └── Depends on: core.state.db
│   ├── plugin_manager.py
│   │   └── Depends on: json (stdlib), pathlib (stdlib)
│   └── file_cache.py
│       └── Depends on: hashlib (stdlib), core.state.db
│
└── plugins/
    ├── python_ruff/
    │   └── plugin.py
    │       └── Depends on: subprocess, json
    ├── python_mypy/
    │   └── plugin.py
    │       └── Depends on: subprocess, re
    └── (other plugins similar pattern)
```

### Specifications Dependencies

```
specifications/
└── tools/
    ├── indexer/
    │   └── indexer.py
    │       └── Depends on: pathlib, markdown
    ├── resolver/
    │   └── resolver.py
    │       ├── Depends on: specifications.tools.indexer
    │       └── Depends on: re, pathlib
    └── guard/
        └── guard.py
            └── Depends on: specifications.tools.resolver
```

---

## Dependency Layers

### Layer Architecture

```
Layer 4: User Interface
────────────────────────
scripts/run_workstream.py
scripts/run_error_engine.py
    ↓ depends on

Layer 3: Orchestration
──────────────────────
core/engine/orchestrator.py
error/engine/error_engine.py
    ↓ depends on

Layer 2: Domain Logic
─────────────────────
core/state/workstreams.py
error/engine/plugin_manager.py
specifications/tools/resolver.py
    ↓ depends on

Layer 1: Infrastructure
───────────────────────
core/state/db.py
error/engine/file_cache.py
    ↓ depends on

Layer 0: Standard Library
─────────────────────────
sqlite3, subprocess, json, pathlib
```

**Rules:**
- ✅ Layer N can depend on Layer N-1 or below
- ❌ Layer N cannot depend on Layer N+1 (upward dependency)
- ❌ No circular dependencies between layers

---

## External Dependencies

### Python Packages (requirements.txt)

```
Direct Dependencies:
──────────────────────
pytest==7.4.0           # Testing framework
pydantic==2.0.0         # Data validation
jsonschema==4.17.0      # JSON schema validation
pyyaml==6.0.0           # YAML parsing
click==8.1.0            # CLI framework

Transitive Dependencies:
─────────────────────────
attrs (from pytest)
pluggy (from pytest)
iniconfig (from pytest)
packaging (from pytest)
typing_extensions (from pydantic)
annotated-types (from pydantic)
pydantic_core (from pydantic)
```

### Tool Dependencies

```
Linters & Formatters:
─────────────────────
ruff                    # Python linter (optional)
mypy                    # Type checker (optional)
black                   # Code formatter (optional)

AI Tools:
─────────
aider-chat              # AI code editor (optional)
```

**Installation:**
```bash
# Core dependencies
pip install -r requirements.txt

# Optional tools
pip install ruff mypy black aider-chat
```

---

## Conceptual Dependencies

### Core Concepts

```
Workstream
    ├── Contains: Steps (1:N)
    ├── Has: State (S_PENDING, S_RUNNING, etc.)
    └── Managed by: Orchestrator

Step
    ├── Belongs to: Workstream (N:1)
    ├── Depends on: Other Steps (N:M via depends_on)
    ├── Has: State (S_PENDING, S_RUNNING, etc.)
    └── Uses: Tool Profile

Tool Profile
    ├── Defines: Command Template
    ├── Specifies: Timeout, Retry Settings
    └── Used by: Steps

State Machine
    ├── Governs: Workstream State Transitions
    ├── Governs: Step State Transitions
    └── Enforces: Valid Transition Rules
```

### Error Detection Concepts

```
Plugin
    ├── Has: Manifest (metadata)
    ├── Implements: parse() function
    ├── Optionally implements: fix() function
    └── Discovered by: Plugin Manager

Error Record
    ├── Reported by: Plugin
    ├── Associated with: File, Line, Column
    ├── Has: Severity (ERROR, WARNING, INFO)
    └── Stored in: Database

File Hash
    ├── Computed for: Each source file
    ├── Stored in: file_hashes table
    └── Used for: Incremental scanning
```

### Specification Concepts

```
Spec
    ├── Located in: specifications/content/
    ├── Has: URI (spec://path#anchor)
    ├── Can reference: Other Specs
    └── Resolved by: Spec Resolver

Spec URI
    ├── Format: spec://path/to/spec#anchor
    ├── Resolves to: File path + line number
    ├── Cached: Yes (TTL 300s)
    └── Validated by: Spec Guard
```

---

## Dependency Coupling Analysis

### Tight Coupling (High Risk)

**Problem Areas:**
```
core/engine/orchestrator.py → core/state/workstreams.py
└─> Change to workstream schema breaks orchestrator

error/engine/error_engine.py → error/plugins/*
└─> Change to plugin interface breaks all plugins
```

**Mitigation:**
- Use versioned schemas
- Provide adapter layer for plugin interface changes
- Maintain backward compatibility for 2 versions

### Loose Coupling (Low Risk)

**Good Examples:**
```
scripts/run_workstream.py → core/engine/orchestrator.py
└─> Uses public API only, stable interface

error/plugins/python_ruff → subprocess
└─> External tool, no code dependency

specifications/tools/resolver → markdown files
└─> Data dependency, not code dependency
```

---

## Change Impact Analysis

### Impact: Change Database Schema

**Direct Impact:**
- `core/state/db.py` - Must update CRUD functions
- `schema/migrations/*.sql` - Must create migration
- All tests using database - Must update fixtures

**Indirect Impact:**
- `core/state/workstreams.py` - If workstreams table changes
- `core/state/steps.py` - If steps table changes
- `error/engine/file_cache.py` - If file_hashes table changes

**Ripple Effect:**
```
schema/migrations/003_add_priority.sql
    ↓
core/state/db.py (apply migration)
    ↓
core/state/workstreams.py (use new column)
    ↓
core/engine/orchestrator.py (sort by priority)
    ↓
tests/core/test_orchestrator.py (test priority sorting)
```

**Commands to Run:**
```bash
# 1. Create migration
vim schema/migrations/003_add_priority.sql

# 2. Apply migration
python -c "from core.state.db import init_db; init_db()"

# 3. Update code to use new column
# Edit core/state/workstreams.py

# 4. Update tests
pytest tests/core/test_workstreams.py

# 5. Validate schema
python scripts/validate_schemas.py
```

---

### Impact: Change Plugin Interface

**Direct Impact:**
- `error/engine/plugin_manager.py` - Interface definition
- All plugins in `error/plugins/*/plugin.py` - Must update to new interface

**Indirect Impact:**
- `error/engine/error_engine.py` - Plugin invocation code
- Tests for all plugins - Must update mocks

**Mitigation Strategy:**
```python
# Use version field in manifest to support multiple interfaces
{
  "plugin_id": "python_ruff",
  "interface_version": "2.0",  # Declares which interface it implements
  ...
}

# Plugin manager checks version and routes accordingly
if manifest["interface_version"] == "1.0":
    result = plugin.parse(file_path, content)
elif manifest["interface_version"] == "2.0":
    result = plugin.parse(file_path, content, context)
```

---

### Impact: Rename Module

**Direct Impact:**
- All import statements referencing module
- All documentation referencing module
- CI/CD scripts using module path

**Example: Rename `core/state/workstreams.py` → `core/state/workflows.py`**

**Files to Update:**
```
core/engine/orchestrator.py
    - from core.state.workstreams import ...
    + from core.state.workflows import ...

core/planning/planner.py
    - from core.state.workstreams import ...
    + from core.state.workflows import ...

docs/adr/0001-workstream-model-choice.md
    - References to `workstreams.py`
    + Update to `workflows.py`

tests/core/test_workstreams.py → tests/core/test_workflows.py
    - Rename file
    - Update imports

# And 15+ other files...
```

**Better Approach:**
Keep public API stable using `__init__.py`:
```python
# core/state/__init__.py
from core.state.workflows import (
    create_workstream,  # Deprecated name, still works
    create_workflow,    # New name
    get_workstream,     # Deprecated
    get_workflow,       # New
)
```

---

## Dependency Inversion Examples

### Before: Direct Dependency (Tight Coupling)

```python
# orchestrator.py
from core.engine.aider_adapter import AiderAdapter

class Orchestrator:
    def execute_step(self, step):
        adapter = AiderAdapter()  # Direct dependency
        result = adapter.execute(step)
        return result
```

**Problem:** Orchestrator is tightly coupled to AiderAdapter. Can't swap implementations.

### After: Dependency Inversion (Loose Coupling)

```python
# tool_adapter.py (abstract interface)
from abc import ABC, abstractmethod

class ToolAdapter(ABC):
    @abstractmethod
    def execute(self, context):
        pass

# aider_adapter.py
class AiderAdapter(ToolAdapter):
    def execute(self, context):
        # Implementation
        pass

# orchestrator.py
class Orchestrator:
    def __init__(self, adapter: ToolAdapter):
        self.adapter = adapter  # Injected dependency
    
    def execute_step(self, step):
        result = self.adapter.execute(step)
        return result

# Usage
orchestrator = Orchestrator(AiderAdapter())  # Or any other adapter
```

**Benefit:** Can swap implementations without changing Orchestrator.

---

## Circular Dependency Detection

### Known Circular Dependencies (NONE)

✅ **No circular dependencies detected** in current codebase.

### How to Detect

```bash
# Using Python import analyzer
pip install pydeps
pydeps core --show-cycles

# Manual check
python scripts/check_circular_deps.py
```

### If Circular Dependency Found

**Example:**
```
module_a.py → module_b.py → module_c.py → module_a.py
```

**Resolution:**
1. **Extract Interface:** Move shared interface to new module
2. **Dependency Inversion:** Use abstract base class
3. **Restructure:** Move code to break cycle

---

## Dependency Management Best Practices

### ✅ DO

- **Depend on abstractions, not concretions**
- **Keep dependencies unidirectional** (no cycles)
- **Use dependency injection** for flexibility
- **Version interfaces** when changing them
- **Document breaking changes** in CHANGELOG

### ❌ DON'T

- **Create circular dependencies**
- **Depend on implementation details**
- **Import from higher layers**
- **Tightly couple to external tools**
- **Change interfaces without migration path**

---

## Dependency Visualization

### Import Graph (Simplified)

```
scripts/
    ↓
core/engine/orchestrator.py
    ↓
core/state/workstreams.py
    ↓
core/state/db.py
    ↓
sqlite3
```

### Full Dependency Count

```
Module                          | Direct Deps | Transitive Deps | Total
────────────────────────────────|─────────────|─────────────────|──────
core/state/db.py                | 1           | 0               | 1
core/state/workstreams.py       | 1           | 1               | 2
core/engine/orchestrator.py     | 4           | 3               | 7
error/engine/error_engine.py    | 3           | 5               | 8
scripts/run_workstream.py       | 2           | 10              | 12
```

**Low dependency count = Good modularity**

---

## Related Documentation

- [Change Impact Matrix](CHANGE_IMPACT_MATRIX.md) - What to update when dependencies change
- [ADR-0004: Section-Based Organization](../adr/0004-section-based-organization.md) - Code organization
- [Anti-Patterns: Circular Dependencies](../guidelines/ANTI_PATTERNS.md)

---

**Modules Analyzed:** 25+  
**Circular Dependencies:** 0  
**Last Updated:** 2025-11-22  
**Next Review:** After major refactorings
