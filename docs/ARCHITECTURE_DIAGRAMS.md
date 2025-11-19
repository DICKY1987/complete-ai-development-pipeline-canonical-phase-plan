# Architecture Diagrams

**Last Updated**: 2025-11-19  
**Phase**: F - Post-Refactor Finalization  
**Status**: Complete

This document explains the architecture diagrams for the AI Development Pipeline. All diagrams are created using Mermaid and can be rendered in GitHub, most markdown viewers, or using the [Mermaid Live Editor](https://mermaid.live/).

---

## Overview

The architecture diagrams visualize different aspects of the refactored codebase:

1. **Directory Structure** - Physical organization of code
2. **Module Dependencies** - How components depend on each other
3. **Data Flows** - How data moves through the system for different use cases
4. **Integration Overview** - High-level system integration

---

## 1. Directory Structure Diagram

**File**: `assets/diagrams/directory-structure.mmd`

**Purpose**: Shows the physical organization of the repository after the Phase E refactor.

**Key Features**:
- **Color-coded sections**:
  - 🔵 Blue: Core pipeline (state, engine, planning)
  - 🔴 Red: Error detection subsystem
  - 🟢 Green: External integrations (AIM, PM, Spec, Aider)
  - 🟠 Orange: Configuration and infrastructure
  - ⚫ Gray (dashed): Deprecated/legacy shims
- **Hierarchical layout**: Root → Sections → Subsections → Key files
- **Key files highlighted**: Shows important modules in each section

**Use Cases**:
- Onboarding new developers
- Understanding where to find specific functionality
- Planning new features (where should code go?)

**Legend**:
- Solid borders: Active, maintained code
- Dashed borders: Deprecated shims (will be removed)
- Dotted lines: "Contains" relationships showing key files

---

## 2. Module Dependencies Diagram

**File**: `assets/diagrams/module-dependencies.mmd`

**Purpose**: Shows how Python modules import and depend on each other.

**Key Dependencies**:
- **User → Scripts → Core Engine**: Entry point flow
- **Core Engine → Core State**: Engine uses state for persistence
- **Core Engine → Error Detection**: Integration for validation
- **Shims → Core/Error**: Backward compatibility layer

**Important Insights**:
- **Database is central**: `core.state.db` and `core.state.crud` are used by most components
- **No circular dependencies**: Clean one-way dependency flow
- **Shims are isolated**: Legacy imports route through shims but don't affect core logic
- **External integrations are optional**: AIM and Aider connections are dotted (optional)

**Use Cases**:
- Understanding import relationships
- Identifying potential circular dependencies
- Planning refactors or new features
- Debugging import errors

---

## 3. Data Flow Diagrams

### 3a. Workstream Execution Flow

**File**: `assets/diagrams/data-flow-workstream.mmd`

**Purpose**: Shows the complete lifecycle of executing a workstream bundle.

**Phases**:
1. **Validation & Loading** (Blue):
   - Load workstream JSON
   - Validate schema
   - Build dependency DAG
   - Store in database

2. **Scheduling** (Blue):
   - Resolve dependencies
   - Schedule execution order

3. **Execution** (Blue):
   - Create Git worktree
   - Execute EDIT → STATIC → RUNTIME phases
   - Invoke external tools (Aider, pytest, etc.)

4. **Error Handling** (Red):
   - Check circuit breakers
   - Retry on failure
   - Handle max retries

5. **Completion** (Green):
   - Update state
   - Cleanup worktrees
   - Archive results

**Use Cases**:
- Understanding workstream lifecycle
- Debugging execution issues
- Onboarding to the pipeline
- Planning new execution features

---

### 3b. Error Detection Flow

**File**: `assets/diagrams/data-flow-error-detection.mmd`

**Purpose**: Shows how error detection works across different file types.

**Flow**:
1. **Trigger**: Manual or automated detection request
2. **Plugin Selection**: Choose relevant linters based on file types
3. **Parallel Execution**: Run multiple plugins simultaneously
   - Python: ruff, mypy, black, pylint
   - JavaScript: eslint, prettier
   - YAML: yamllint
   - Markdown: markdownlint
   - Security: bandit, semgrep, gitleaks
4. **Result Collection**: Aggregate findings from all plugins
5. **Classification**: Categorize errors by severity and type
6. **State Machine**: Track error lifecycle (NEW → DETECTED → FIXED/IGNORED)
7. **Auto-Fix**: Attempt automatic fixes for some errors
8. **Storage**: Persist to database and JSONL file
9. **Reporting**: Generate output for CLI or API

**Use Cases**:
- Understanding error detection pipeline
- Adding new linter plugins
- Debugging detection issues
- Planning auto-fix strategies

---

### 3c. Database Operations Flow

**File**: `assets/diagrams/data-flow-database.mmd`

**Purpose**: Shows how components interact with the SQLite database.

**Architecture**:
- **Component Layer**: Orchestrator, Scheduler, Executor, Error Engine, Planner
- **CRUD Layer**: Single abstraction (`core.state.crud`)
- **Operation Layer**: Specific operations (create, read, update, list)
- **Backend Layer**: SQLite implementation (`core.state.db_sqlite`)
- **Storage Layer**: Physical database file (`refactor_paths.db`)
- **Schema Layer**: Tables (runs, workstreams, steps, errors, events)

**Key Tables**:
- `runs`: Execution runs (one per pipeline invocation)
- `workstreams`: Workstream definitions and status
- `steps`: Individual step execution records
- `errors`: Detected errors and their states
- `events`: Audit log of all state changes

**Use Cases**:
- Understanding data persistence
- Adding new database operations
- Debugging state issues
- Planning schema migrations

---

### 3d. AIM Integration Flow

**File**: `assets/diagrams/data-flow-aim-integration.mmd`

**Purpose**: Shows how the pipeline integrates with AI models via AIM.

**Flow**:
1. **Request**: Executor needs AI assistance
2. **Bridge**: Request goes through `aim.bridge`
3. **Registry**: Check AIM registry for available tools
4. **Selection**: Choose appropriate tool based on task
5. **Configuration**: Load model settings (temperature, max tokens, etc.)
6. **Invocation**: Call external AI tool:
   - Aider (local AI code editor)
   - Claude (Anthropic API)
   - GPT-4 (OpenAI API)
   - Local LLMs (Ollama, etc.)
7. **Response**: Collect generated code/analysis
8. **Validation**: Check output format and quality
9. **Logging**: Record token usage and costs to database
10. **Return**: Send results back to executor

**Use Cases**:
- Understanding AI integration
- Adding new AI model support
- Debugging AI invocations
- Tracking AI usage and costs

---

## 4. Integration Overview Diagram

**File**: `assets/diagrams/integration-overview.mmd`

**Purpose**: High-level view of how all sections integrate together.

**Layers** (top to bottom):
1. **Entry Layer** (Purple): User and CLI scripts
2. **Core Pipeline** (Blue): State, Engine, Planning
3. **Error Detection** (Red): Error engine and plugins
4. **External Integrations** (Green): AIM, Aider, PM, Spec
5. **Configuration & Data** (Orange): Config files, schemas, workstreams
6. **Backward Compatibility** (Gray, dashed): Legacy shims

**Key Integration Points**:
- CLI → Core Engine: Main execution path
- Core Engine → Error Detection: Validation integration
- Core Engine → External Tools: AI and tool invocations
- Everything → Database: Centralized state management
- Shims → Core/Error: Deprecated backward compatibility

**Use Cases**:
- High-level system understanding
- Planning large-scale changes
- Explaining architecture to stakeholders
- Identifying integration points

---

## Rendering the Diagrams

### In GitHub
All `.mmd` files will render automatically in GitHub's web interface.

### In VS Code
Install the "Markdown Preview Mermaid Support" extension.

### Mermaid Live Editor
1. Copy the contents of any `.mmd` file
2. Paste into https://mermaid.live/
3. View, edit, and export as PNG/SVG

### Command Line (Node.js)
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i assets/diagrams/directory-structure.mmd -o assets/diagrams/directory-structure.png
```

### Python (optional)
```bash
pip install mermaid-py
python -m mermaid assets/diagrams/directory-structure.mmd -o assets/diagrams/directory-structure.png
```

---

## Diagram Maintenance

### When to Update

**Directory Structure**:
- New top-level directories added
- Major reorganization of sections
- New subsections created

**Module Dependencies**:
- New major components added
- Dependencies between sections change
- Circular dependencies introduced (and need visualization)

**Data Flows**:
- Execution flow changes significantly
- New phases added to workstream lifecycle
- Error detection logic changes
- New external integrations

**Integration Overview**:
- New sections added
- Major architectural changes
- New external systems integrated

### How to Update

1. Edit the `.mmd` source file
2. Test rendering in Mermaid Live Editor or GitHub preview
3. Update this documentation if diagram purpose changes
4. Re-generate PNG/SVG if needed (optional)
5. Commit both source and rendered versions

---

## Color Coding Reference

All diagrams use consistent color schemes:

| Color | Hex Code | Usage |
|-------|----------|-------|
| 🔵 Blue | `#4A90E2` | Core pipeline components |
| 🔴 Red | `#E24A4A` | Error detection system |
| 🟢 Green | `#50C878` | External integrations, success states |
| 🟠 Orange | `#F5A623` | Configuration, planning, warnings |
| 🟣 Purple | `#9B59B6` | User/entry points |
| ⚫ Gray | `#95A5A6` | Legacy/deprecated components |

**Border Styles**:
- Solid: Active, maintained code
- Dashed: Deprecated or temporary
- Dotted lines: Optional dependencies or "contains" relationships

---

## Related Documentation

- **Architecture Overview**: [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
- **Refactor Mapping**: [docs/SECTION_REFACTOR_MAPPING.md](./SECTION_REFACTOR_MAPPING.md)
- **Phase F Plan**: [docs/PHASE_F_PLAN.md](./PHASE_F_PLAN.md)
- **Repository Structure**: [README.md](../README.md)

---

## Feedback & Improvements

If you notice:
- Diagrams are outdated
- Missing important components
- Confusing layouts
- Errors in relationships

Please update the `.mmd` files and this documentation, or create an issue describing what should be changed.
