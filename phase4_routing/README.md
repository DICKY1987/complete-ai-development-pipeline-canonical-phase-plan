---
doc_id: DOC-GUIDE-README-504
---

# Phase 4 – Tool Routing & Adapter Selection

**Purpose**: Match tasks to tool profiles and select adapters (Aider/Codex/Custom).

## Phase Contents

Located in: `phase4_routing/`

- `tools/` - Tool implementations (guard, indexer, patcher, renderer, resolver)
- `aider/` - Aider adapter configuration
- `aim/` - AIM environment manager and tool capability matching
- `README.md` - This file

## Current Components

### Tools (`tools/`)
- `guard/` - Schema validation tools
- `indexer/` - Index generation
- `patcher/` - Patch application
- `renderer/` - Template rendering
- `resolver/` - Dependency resolution

### Aider (`aider/`)
- Aider CLI adapter configuration
- Multi-instance support

### AIM - AI Tool Matching (`aim/`)
- `bridge/` - Capability matching algorithms
- `capabilities/` - Tool capability definitions
- Tool selection and routing logic

### Implementation (`core/engine/`, `core/adapters/`)
Located in cross-cutting `core/` directory:
- `core/engine/router.py` - Task routing logic ⚠️ (partial)
- `core/engine/tools.py` - Tool registry and selection ⚠️ (partial)
- `core/adapters/base.py` - ToolAdapter base class ✅
- `core/adapters/registry.py` - AdapterRegistry ✅
- `core/adapters/subprocess_adapter.py` - Basic subprocess adapter ✅

## Main Operations
- Match tasks by language, task type, environment
- Select best tool adapter with fallbacks
- Validate adapter configuration (commands, paths, env, timeouts)
- Manage multi-instance pools for Aider/Codex

## Missing Components
- ToolProcessPool - Multi-instance pool management
- ClusterManager - Cluster control for parallel execution
- Full Aider adapter implementation
- Codex adapter implementation

## Test Coverage
~27 tests for adapters

## Status
⚠️ Partial (60%) - Router and pooling need implementation
