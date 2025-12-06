# Phase 4: Routing - Folder Interaction Decomposition

## Phase Overview
**Phase 4: Routing** - Tool selection, adapter configuration, and request routing

## Phase-Specific Folders (Primary Responsibility)

### 1. `phase4_routing/`
- **Purpose**: Routing logic and tool adapters
- **Key Components**:
  - `modules/tool_adapters/` - Tool adapter implementations
  - `modules/aim_tools/` - AIM environment management
  - `modules/aider_integration/` - Aider-specific routing

### 2. `core/adapters/`
- **Purpose**: Core adapter interfaces and base classes
- **Key Components**:
  - Adapter registry
  - Base adapter interfaces
  - Tool capability definitions

### 3. `aim/`
- **Purpose**: AI environment manager (AIM) for tool orchestration
- **Key Components**:
  - Process pool management
  - Tool environment isolation
  - Routing strategies

## Cross-Phase Folders (Shared with Other Phases)

### `core/engine/`
- **Interaction**: Provides orchestrator and executor for tool invocation
- **Used By**: Phases 4, 5, 6
- **Routing Role**: Executes routed tool calls

### `core/state/`
- **Interaction**: Stores routing decisions and tool availability
- **Used By**: All phases (0-7)
- **Routing Role**: Tracks tool usage and availability

### `config/`
- **Interaction**: Loads tool configurations and routing rules
- **Used By**: All phases (0-7)
- **Routing Role**: Defines routing policies

### `core/monitoring/`
- **Interaction**: Monitors tool performance and health
- **Used By**: Phases 3, 7
- **Routing Role**: Reports tool metrics

### `tools/`
- **Interaction**: Contains tool validation and helper scripts
- **Used By**: Phases 4, 5
- **Routing Role**: Validates tool availability

---

## Phase Execution Steps

### Step 1: Tool Selection
**Folders**: `phase4_routing/`, `core/adapters/`, `config/`
- Analyze task requirements
- Match capabilities to tools
- Apply routing policies

### Step 2: Adapter Lookup
**Folders**: `core/adapters/`, `phase4_routing/modules/tool_adapters/`
- Query adapter registry
- Load appropriate adapter
- Validate adapter compatibility

### Step 3: Environment Setup
**Folders**: `aim/`, `phase4_routing/modules/aim_tools/`
- Initialize tool environment
- Configure process isolation
- Set up resource limits

### Step 4: Request Transformation
**Folders**: `phase4_routing/modules/aider_integration/`, `core/adapters/`
- Transform request to tool format
- Apply tool-specific formatting
- Inject tool configuration

### Step 5: Health Check
**Folders**: `core/monitoring/`, `tools/`
- Verify tool availability
- Check tool health status
- Validate prerequisites

### Step 6: Routing Decision
**Folders**: `phase4_routing/`, `core/engine/`
- Finalize routing decision
- Submit to executor
- Update routing state

---

## Folder Interaction Summary

| Folder | Phase-Specific | Cross-Phase | Primary Role |
|--------|---------------|-------------|--------------|
| `phase4_routing/` | ✓ | | Routing orchestration |
| `core/adapters/` | ✓ | | Adapter registry |
| `aim/` | ✓ | | Environment management |
| `core/engine/` | | ✓ (4-6) | Execution coordination |
| `core/state/` | | ✓ (0-7) | State tracking |
| `config/` | | ✓ (0-7) | Configuration |
| `core/monitoring/` | | ✓ (3,7) | Tool monitoring |
| `tools/` | | ✓ (4-5) | Tool validation |

---

## Dependencies
- **Requires**: Phases 1 (Planning), 2 (Request Building), 3 (Scheduling)
- **Enables**: Phase 5 (Execution)
