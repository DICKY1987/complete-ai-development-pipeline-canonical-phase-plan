# Phase 1: Planning - Folder Interaction Decomposition

## Phase Overview
**Phase 1: Planning** - Workstream creation, task decomposition, and execution planning

## Phase-Specific Folders (Primary Responsibility)

### 1. `phase1_planning/`
- **Purpose**: Planning modules and workstream management
- **Key Components**:
  - `modules/workstream_planner/` - Workstream creation and management
  - `modules/spec_parser/` - Specification parsing
  - `modules/spec_tools/` - Spec manipulation tools
  - Planning templates and patterns

### 2. `core/planning/`
- **Purpose**: Core planning logic and utilities
- **Key Components**:
  - Task decomposition algorithms
  - Dependency resolution
  - Planning state management

### 3. `plans/`
- **Purpose**: Stored execution plans
- **Key Components**:
  - Workstream definitions (JSON/YAML)
  - Phase templates
  - Planning artifacts

## Cross-Phase Folders (Shared with Other Phases)

### `core/state/`
- **Interaction**: Stores workstream and task state
- **Used By**: All phases (0-7)
- **Planning Role**: Persists plans, tasks, and dependencies

### `schema/`
- **Interaction**: Validates workstream and task schemas
- **Used By**: All phases (0-7)
- **Planning Role**: Ensures plan structure compliance

### `templates/`
- **Interaction**: Uses templates for workstream generation
- **Used By**: Phases 0, 1, 2
- **Planning Role**: Instantiates workstream templates

### `specs/`
- **Interaction**: Reads specification documents
- **Used By**: Phases 1, 2
- **Planning Role**: Parses requirements into tasks

### `core/knowledge/`
- **Interaction**: Queries knowledge graph for planning context
- **Used By**: Phases 1, 5, 7
- **Planning Role**: Context-aware plan generation

### `patterns/`
- **Interaction**: Applies execution patterns to plans
- **Used By**: Phases 1, 5
- **Planning Role**: Pattern-based task generation

---

## Phase Execution Steps

### Step 1: Specification Parsing
**Folders**: `phase1_planning/modules/spec_parser/`, `specs/`
- Parse specification documents
- Extract requirements
- Identify constraints

### Step 2: Workstream Creation
**Folders**: `phase1_planning/modules/workstream_planner/`, `templates/`
- Generate workstream structure
- Apply templates
- Define phases

### Step 3: Task Decomposition
**Folders**: `core/planning/`, `patterns/`
- Break down workstream into tasks
- Apply execution patterns
- Define task dependencies

### Step 4: Dependency Resolution
**Folders**: `core/planning/`, `core/state/`
- Analyze task dependencies
- Build dependency graph
- Detect circular dependencies

### Step 5: Plan Validation
**Folders**: `schema/`, `phase1_planning/modules/spec_tools/`
- Validate plan structure
- Check resource requirements
- Verify feasibility

### Step 6: Plan Storage
**Folders**: `plans/`, `core/state/`
- Persist workstream definition
- Store task metadata
- Save execution plan

---

## Folder Interaction Summary

| Folder | Phase-Specific | Cross-Phase | Primary Role |
|--------|---------------|-------------|--------------|
| `phase1_planning/` | ✓ | | Workstream management |
| `core/planning/` | ✓ | | Planning algorithms |
| `plans/` | ✓ | | Plan storage |
| `core/state/` | | ✓ (0-7) | State persistence |
| `schema/` | | ✓ (0-7) | Schema validation |
| `templates/` | | ✓ (0-2) | Template usage |
| `specs/` | | ✓ (1-2) | Spec reading |
| `core/knowledge/` | | ✓ (1,5,7) | Context retrieval |
| `patterns/` | | ✓ (1,5) | Pattern application |

---

## Dependencies
- **Requires**: Phase 0 (Bootstrap)
- **Enables**: Phases 2, 3, 4, 5
