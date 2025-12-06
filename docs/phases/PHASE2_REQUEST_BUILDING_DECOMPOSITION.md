# Phase 2: Request Building - Folder Interaction Decomposition

## Phase Overview
**Phase 2: Request Building** - Prompt construction, context assembly, and request preparation

## Phase-Specific Folders (Primary Responsibility)

### 1. `phase2_request_building/`
- **Purpose**: Request building modules
- **Key Components**:
  - Prompt rendering engines
  - Context assembly logic
  - Request validation

### 2. `prompts/`
- **Purpose**: Prompt templates and fragments
- **Key Components**:
  - Template library (Jinja2)
  - Reusable prompt blocks
  - Tool-specific prompts

### 3. `core/memory/`
- **Purpose**: Context memory management
- **Key Components**:
  - Episodic memory
  - Working memory
  - Context window management

## Cross-Phase Folders (Shared with Other Phases)

### `core/state/`
- **Interaction**: Retrieves task and workstream state for context
- **Used By**: All phases (0-7)
- **Request Building Role**: Loads execution history and current state

### `templates/`
- **Interaction**: Uses templates for prompt generation
- **Used By**: Phases 0, 1, 2
- **Request Building Role**: Renders prompt templates

### `specs/`
- **Interaction**: Includes specification context in prompts
- **Used By**: Phases 1, 2
- **Request Building Role**: Embeds requirements in requests

### `core/knowledge/`
- **Interaction**: Retrieves relevant context from knowledge graph
- **Used By**: Phases 1, 5, 7
- **Request Building Role**: Enriches prompts with historical knowledge

### `core/search/`
- **Interaction**: Searches codebase for relevant context
- **Used By**: Phases 2, 5
- **Request Building Role**: Finds code examples and patterns

### `docs/`
- **Interaction**: Includes documentation context
- **Used By**: Phases 2, 7
- **Request Building Role**: Adds reference documentation to prompts

---

## Phase Execution Steps

### Step 1: Context Assembly
**Folders**: `core/memory/`, `core/state/`, `core/knowledge/`
- Load task context
- Retrieve execution history
- Query knowledge graph

### Step 2: Code Context Retrieval
**Folders**: `core/search/`, `core/indexing/`
- Search relevant code files
- Find related patterns
- Locate dependencies

### Step 3: Template Selection
**Folders**: `prompts/`, `templates/`
- Select appropriate prompt template
- Load template fragments
- Prepare rendering context

### Step 4: Prompt Rendering
**Folders**: `phase2_request_building/`, `prompts/`
- Render prompt with context
- Apply formatting rules
- Inject variables

### Step 5: Documentation Inclusion
**Folders**: `docs/`, `specs/`
- Add specification context
- Include API documentation
- Embed usage examples

### Step 6: Request Validation
**Folders**: `phase2_request_building/`, `schema/`
- Validate request structure
- Check context window limits
- Verify required fields

---

## Folder Interaction Summary

| Folder | Phase-Specific | Cross-Phase | Primary Role |
|--------|---------------|-------------|--------------|
| `phase2_request_building/` | ✓ | | Request assembly |
| `prompts/` | ✓ | | Prompt templates |
| `core/memory/` | ✓ | | Context management |
| `core/state/` | | ✓ (0-7) | State retrieval |
| `templates/` | | ✓ (0-2) | Template rendering |
| `specs/` | | ✓ (1-2) | Spec inclusion |
| `core/knowledge/` | | ✓ (1,5,7) | Knowledge retrieval |
| `core/search/` | | ✓ (2,5) | Code search |
| `docs/` | | ✓ (2,7) | Documentation |

---

## Dependencies
- **Requires**: Phase 1 (Planning)
- **Enables**: Phases 3, 4, 5
