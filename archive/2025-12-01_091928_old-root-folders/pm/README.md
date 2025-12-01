---
doc_id: DOC-PM-README-024
---

# PM - Project Management & CCPM Integration

> **Module**: `pm`  
> **Purpose**: Project management, CCPM integration, and workstream lifecycle tracking  
> **Layer**: API/Integration  
> **Status**: Production

---

## Overview

The **PM (Project Management)** module provides integration with project management tools and Critical Chain Project Management (CCPM) methodologies. It bridges high-level project planning with workstream execution.

**Key Features**:
- ✅ **PRD Management** - Create and manage Product Requirement Documents
- ✅ **Epic Decomposition** - Break down epics into executable tasks
- ✅ **Workstream Lifecycle Tracking** - Bidirectional sync with workstream execution
- ✅ **GitHub Integration** - Sync with GitHub Issues (optional)
- ✅ **Event-driven Architecture** - React to workstream state changes
- ✅ **CCPM Optimization** - Critical chain scheduling and buffer management
- ✅ **CLI Commands** - Rich command-line interface for PM operations

---

## Directory Structure

```
pm/
├── models.py                # Data models (PRD, Epic, Task, Events)
├── prd.py                   # PRD manager
├── epic.py                  # Epic manager
├── bridge.py                # OpenSpec ↔ PRD ↔ Epic ↔ Workstream bridge
├── event_handler.py         # Event listener for workstream lifecycle
│
├── integrations/            # External integrations
│   ├── github_sync.py       # GitHub Issues sync
│   └── __init__.py
│
├── commands/                # CLI command implementations
│   ├── pm/                  # PM command markdown specs
│   │   ├── epic-list.md
│   │   ├── epic-show.md
│   │   ├── epic-start.md
│   │   ├── prd-new.md
│   │   └── ...
│   ├── context/             # Context command specs
│   └── testing/             # Testing command specs
│
├── agents/                  # Agent specifications
│   ├── code-analyzer.md
│   ├── file-analyzer.md
│   ├── parallel-worker.md
│   └── test-runner.md
│
├── context/                 # CCPM context management
│   └── README.md
│
├── hooks/                   # Integration hooks
│   └── README.md
│
├── epics/                   # Epic JSON files (workspace)
├── prds/                    # PRD JSON files (workspace)
├── rules/                   # Validation and conflict rules
├── scripts/                 # PM utility scripts
└── templates/               # PRD and Epic templates
```

---

## Core Concepts

### Hierarchy

```
OpenSpec Change Proposal
    ↓
Product Requirement Document (PRD)
    ↓
Epic (high-level feature)
    ↓
Tasks (executable units)
    ↓
Workstream Bundles (pipeline execution)
```

### Bidirectional Sync

```
PRD → Epic → Workstreams (planning → execution)
Workstreams → Epic → PRD (execution → status updates)
```

---

## Key Components

### Data Models (`models.py`)

Core data structures for project management.

#### PRD (Product Requirement Document)

```python
from pm.models import PRD, Status, Priority

prd = PRD(
    name="auth-system",
    title="User Authentication System",
    author="tech-lead",
    status=Status.DRAFT,
    priority=Priority.HIGH,
    description="Implement JWT-based authentication",
    acceptance_criteria=[
        "Users can register and login",
        "JWT tokens expire after 24h",
        "Password reset via email"
    ],
    stakeholders=["product", "engineering"],
    dependencies=["db-migration"],
    metadata={"project": "v2.0", "quarter": "Q4-2025"}
)
```

**Status Lifecycle**:
```
DRAFT → IN_REVIEW → APPROVED → IN_PROGRESS → DONE → ARCHIVED
```

#### Epic

```python
from pm.models import Epic, Task, Effort

epic = Epic(
    name="auth-backend",
    title="Authentication Backend",
    description="Backend services for auth system",
    prd_name="auth-system",
    status=Status.APPROVED,
    priority=Priority.HIGH,
    effort=Effort.MEDIUM,
    tasks=[
        Task(
            id="TASK-1",
            title="JWT token generation",
            description="Implement JWT encoding/decoding",
            effort=Effort.SMALL,
            dependencies=[]
        ),
        Task(
            id="TASK-2",
            title="Login endpoint",
            description="POST /api/login endpoint",
            effort=Effort.SMALL,
            dependencies=["TASK-1"]
        )
    ]
)
```

**Epic Status Lifecycle**:
```
DRAFT → APPROVED → IN_PROGRESS → BLOCKED → DONE → ARCHIVED
```

---

### PRD Manager (`prd.py`)

Create, load, and manage PRDs.

```python
from pm.prd import PRDManager, create_prd, load_prd, list_prds
from pm.models import Status, Priority

# Create PRD manager
manager = PRDManager(workspace_dir="pm/prds")

# Create new PRD
prd = create_prd(
    name="auth-system",
    title="User Authentication System",
    author="tech-lead",
    priority=Priority.HIGH,
    description="Implement JWT-based authentication"
)

# Save PRD
manager.save(prd)

# Load PRD
prd = load_prd("auth-system")

# List all PRDs
all_prds = list_prds()

# Filter by status
draft_prds = list_prds(status_filter=Status.DRAFT)

# Update PRD status
prd.status = Status.APPROVED
manager.save(prd)
```

**PRD File Location**: `pm/prds/<name>.json`

---

### Epic Manager (`epic.py`)

Create, decompose, and manage epics.

```python
from pm.epic import EpicManager, create_epic_from_prd, load_epic, list_epics
from pm.prd import load_prd

# Load PRD
prd = load_prd("auth-system")

# Create epic from PRD
epic = create_epic_from_prd(
    prd=prd,
    name="auth-backend",
    title="Authentication Backend",
    description="Backend services for auth"
)

# Add tasks
epic.tasks.append(
    Task(
        id="TASK-3",
        title="Password hashing",
        description="Use bcrypt for password storage",
        effort=Effort.SMALL
    )
)

# Save epic
manager = EpicManager(workspace_dir="pm/epics")
manager.save(epic)

# Load epic
epic = load_epic("auth-backend")

# List epics
all_epics = list_epics()
in_progress = list_epics(status_filter=Status.IN_PROGRESS)
```

**Epic File Location**: `pm/epics/<name>.json`

---

### Bridge API (`bridge.py`)

Converts between OpenSpec, PRD, Epic, and Workstream formats.

#### OpenSpec → PRD

```python
from pm.bridge import openspec_to_prd
from pathlib import Path

# Convert OpenSpec change proposal to PRD
prd = openspec_to_prd(Path("openspec/specs/OS-AUTH-001.yaml"))

# PRD is auto-populated from OpenSpec metadata
print(prd.name)         # "os-auth-001"
print(prd.title)        # From OpenSpec title
print(prd.description)  # From OpenSpec description
```

#### PRD → Epic

```python
from pm.bridge import prd_to_epic
from pm.prd import load_prd

# Load PRD
prd = load_prd("auth-system")

# Convert to Epic
epic = prd_to_epic(
    prd=prd,
    name="auth-backend",
    title="Authentication Backend"
)
```

#### Epic → Workstreams

```python
from pm.bridge import epic_to_workstreams
from pm.epic import load_epic

# Load epic
epic = load_epic("auth-backend")

# Convert to workstream bundles
workstreams = epic_to_workstreams(
    epic=epic,
    tool_profile="aider"
)

# Returns list of workstream bundle dictionaries
# [
#     {
#         "id": "ws-auth-backend-task-1",
#         "openspec_change": "OS-AUTH-001",
#         "ccpm_issue": "TASK-1",
#         "gate": 2,
#         "files_scope": ["src/auth/jwt.py"],
#         "tasks": ["Implement JWT encoding/decoding"],
#         "tool": "aider"
#     },
#     ...
# ]
```

#### Workstream Status Sync

```python
from pm.bridge import sync_workstream_status

# Update epic/task status based on workstream completion
sync_workstream_status(
    ws_id="ws-auth-backend-task-1",
    state="completed"
)

# Automatically updates:
# - Task status (IN_PROGRESS → DONE)
# - Epic progress (updates completion percentage)
# - PRD status (if all epics done)
```

---

### Event Handler (`event_handler.py`)

Listens to workstream lifecycle events and updates PM artifacts.

```python
from pm.event_handler import (
    get_event_handler,
    emit_workstream_start,
    emit_step_complete,
    emit_workstream_complete,
    emit_workstream_blocked,
    emit_workstream_failed
)

# Get event handler (singleton)
handler = get_event_handler(enable_github=True)

# Emit events (automatically handled by orchestrator)
emit_workstream_start(
    ws_id="ws-auth-backend-task-1",
    epic_name="auth-backend",
    task_id="TASK-1"
)

emit_step_complete(
    ws_id="ws-auth-backend-task-1",
    step_name="edit",
    success=True,
    files_modified=["src/auth/jwt.py"]
)

emit_workstream_complete(
    ws_id="ws-auth-backend-task-1",
    success=True,
    final_state="completed"
)
```

**Event Flow**:
```
Workstream Event
    ↓
Event Handler
    ↓
Update Epic/Task Status
    ↓
Sync to GitHub (optional)
    ↓
Log to Audit Trail
```

---

### GitHub Integration (`integrations/github_sync.py`)

Optional integration with GitHub Issues.

```python
from pm.integrations import github_sync

# Check if enabled
if github_sync._enabled():
    # Create GitHub issue for epic
    issue_number = github_sync.ensure_epic(
        title="Authentication Backend",
        body="Epic description...",
        labels=["epic", "high-priority"]
    )
    
    # Post lifecycle comment
    github_sync.comment(
        issue_number=issue_number,
        text="✓ Workstream ws-auth-backend-task-1 completed"
    )
    
    # Update issue status
    github_sync.set_status(
        issue_number=issue_number,
        state="closed",
        add_labels=["completed"]
    )
```

**Configuration** (`pm/config/github.yaml`):
```yaml
enabled: true
repo: "owner/repo"
sync_epics: true
sync_tasks: false
label_prefix: "pm:"
```

**Environment Variables**:
- `GITHUB_TOKEN` - GitHub API token (required)
- `GITHUB_REPO` - Repository in `owner/repo` format

---

## CLI Commands

The PM module provides a rich CLI interface via markdown command specifications.

### Epic Commands

```bash
# List epics
python -m pm.cli epic-list
python -m pm.cli epic-list --status in-progress

# Show epic details
python -m pm.cli epic-show auth-backend

# Start epic
python -m pm.cli epic-start auth-backend

# Update epic status
python -m pm.cli epic-status auth-backend --state done

# Decompose epic into workstreams
python -m pm.cli epic-decompose auth-backend --output workstreams/

# Close epic
python -m pm.cli epic-close auth-backend
```

### PRD Commands

```bash
# Create new PRD
python -m pm.cli prd-new auth-system --title "Authentication System"

# List PRDs
python -m pm.cli prd-list

# Edit PRD
python -m pm.cli prd-edit auth-system

# Show PRD status
python -m pm.cli prd-status auth-system
```

### Sync Commands

```bash
# Sync all workstream status
python -m pm.cli sync

# Sync specific workstream
python -m pm.cli issue-sync ws-auth-backend-task-1
```

### Status Commands

```bash
# Show overall status
python -m pm.cli status

# Show what's blocked
python -m pm.cli blocked

# Show what's in progress
python -m pm.cli in-progress

# Show next available work
python -m pm.cli next
```

---

## Integration with Pipeline

### From Orchestrator

```python
from core.engine.orchestrator import run_workstream
from pm.event_handler import (
    emit_workstream_start,
    emit_workstream_complete
)

# Emit start event
emit_workstream_start(ws_id="ws-auth-backend-task-1")

# Execute workstream
result = run_workstream(run_id, ws_id, bundle)

# Emit completion event
emit_workstream_complete(
    ws_id="ws-auth-backend-task-1",
    success=result["success"],
    final_state=result["final_status"]
)
```

### From Workstream Bundle

Workstream bundles reference CCPM issues:

```json
{
  "id": "ws-auth-backend-task-1",
  "openspec_change": "OS-AUTH-001",
  "ccpm_issue": "TASK-1",
  "gate": 2,
  "files_scope": ["src/auth/jwt.py"],
  "tasks": ["Implement JWT encoding/decoding"]
}
```

The `ccpm_issue` field links the workstream to the PM system.

---

## Configuration

### Environment Variables

- **`PM_WORKSPACE_DIR`** - Override workspace directory (default: `pm/`)
- **`PM_ENABLE_GITHUB`** - Enable GitHub sync (default: `false`)
- **`GITHUB_TOKEN`** - GitHub API token (required for sync)
- **`GITHUB_REPO`** - Repository in `owner/repo` format

### Configuration Files

- **`pm/config/github.yaml`** - GitHub sync configuration
- **`pm/config/ccpm.yaml`** - CCPM optimization settings

---

## Testing

Tests are located in `pm/tests/`:

```bash
# Unit tests
pytest pm/tests/test_models.py -v
pytest pm/tests/test_epic.py -v
pytest pm/tests/test_bridge.py -v

# Integration tests
pytest pm/tests/test_github_sync.py -v
```

---

## Best Practices

1. **Start with PRDs** - Define requirements before implementation
2. **Decompose epics into small tasks** - Easier to estimate and track
3. **Use bidirectional sync** - Keep PM artifacts up-to-date with execution
4. **Enable GitHub sync for transparency** - Stakeholders can track progress
5. **Review blocked workstreams daily** - Unblock dependencies quickly
6. **Archive completed epics** - Keep active list manageable
7. **Link OpenSpec changes to PRDs** - Maintain traceability

---

## Migration from Legacy

Legacy AI_MANGER had basic project tracking. PM module provides full CCPM integration:

```python
# ❌ LEGACY (AI_MANGER)
# No structured PM integration

# ✅ NEW (PM Module)
from pm.prd import create_prd
from pm.epic import create_epic_from_prd
from pm.bridge import epic_to_workstreams
```

---

## Related Documentation

- **CCPM Context**: `pm/context/README.md` - Context management details
- **Hooks**: `pm/hooks/README.md` - Integration hook specifications
- **Module Overview**: `pm/MODULE.md` - Module architecture
- **Contract**: `pm/CONTRACT.md` - API contract and versioning
- **CCPM Instructions**: `pm/CCPM_AI_INSTRUCTIONS.md` - AI agent guidelines
- **Planning Integration**: `core/planning/README.md` - Workstream planning
- **Orchestration**: `core/engine/README.md` - Execution engine

---

## Roadmap

### Phase 1 (Current - Production)
- ✅ PRD and Epic management
- ✅ OpenSpec → PRD → Epic → Workstream bridge
- ✅ Event-driven status sync
- ✅ GitHub Issues integration (optional)
- ✅ CLI commands

### Phase 2 (Planned)
- 🔜 CCPM buffer management
- 🔜 Critical chain visualization
- 🔜 Resource leveling
- 🔜 Burndown charts
- 🔜 Jira integration

### Phase 3 (Future)
- 🔜 Multi-project coordination
- 🔜 Portfolio management
- 🔜 AI-powered estimation
- 🔜 Risk analysis
- 🔜 Web dashboard
