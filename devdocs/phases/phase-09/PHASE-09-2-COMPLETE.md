# Phase 09.2: Core PM Workflow - COMPLETE

**Date:** 2025-11-21
**Status:** ✅ Complete

## Deliverables

### ✅ Jinja2 Templates
- `pm/templates/prd.md.j2` - PRD template with YAML frontmatter
- `pm/templates/epic.md.j2` - Epic template with progress tracking
- `pm/templates/task.md.j2` - Task template with acceptance criteria

### ✅ Python Core Implementation
- `pm/prd.py` - PRDManager class with CRUD operations
  - `create_prd()` - Create new PRD with validation
  - `load_prd()` - Parse PRD from markdown + YAML
  - `list_prds()` - List all PRDs with optional filtering
  - `update_prd()` - Update PRD fields
  - `delete_prd()` - Remove PRD file
  
- `pm/epic.py` - EpicManager class with full lifecycle
  - `create_epic_from_prd()` - Generate epic from PRD
  - `load_epic()` - Load epic with tasks
  - `list_epics()` - List all epics
  - `decompose_epic()` - Break into tasks
  - `update_task_status()` - Update task progress

## Features Implemented

### PRD Management
- Kebab-case name validation
- YAML frontmatter parsing
- Markdown section extraction
- Jinja2 template rendering
- Full CRUD operations
- Validation with detailed errors

### Epic Management
- PRD → Epic conversion
- Epic decomposition into tasks
- Metadata sidecar (`.metadata.yaml`)
- Progress tracking
- Task dependency management
- Parallel task detection

### File Format Support
- YAML frontmatter for metadata
- Markdown for content
- Jinja2 for template rendering
- Cross-platform path handling

## Dependencies

Required Python packages:
- `pyyaml` - YAML parsing
- `jinja2` - Template rendering

Install with:
```bash
pip install pyyaml jinja2
```

## Usage Examples

### Create PRD
```python
from pm.prd import create_prd, Priority

prd = create_prd(
    name="user-authentication",
    title="User Authentication System",
    author="Dev Team",
    problem="Users need secure login",
    solution="Implement JWT-based auth",
    requirements=[
        "Email/password login",
        "JWT token generation",
        "Password hashing"
    ],
    success_criteria=[
        "Users can login successfully",
        "Tokens expire after 24h"
    ],
    priority=Priority.HIGH
)
```

### Create Epic from PRD
```python
from pm.prd import load_prd
from pm.epic import create_epic_from_prd

prd = load_prd("user-authentication")
epic = create_epic_from_prd(
    prd,
    technical_approach="Use bcrypt for hashing, JWT for tokens",
    risks=["Token security", "Password strength"],
    implementation_plan="Phase 1: Models, Phase 2: Auth logic, Phase 3: Tests"
)
```

### Decompose Epic into Tasks
```python
from pm.epic import load_epic
from pathlib import Path

epic = load_epic("user-authentication")

tasks_data = [
    {
        "title": "Create User model",
        "description": "Define User model with password hashing",
        "file_scope": ["src/models/user.py"],
        "acceptance_criteria": [
            "User model with email/password fields",
            "Password hashing on save",
            "Unit tests pass"
        ],
        "effort": "small",
        "parallel": True
    },
    {
        "title": "Implement JWT authentication",
        "description": "Add JWT token generation and validation",
        "file_scope": ["src/auth/jwt.py"],
        "acceptance_criteria": [
            "Generate JWT on login",
            "Validate JWT middleware",
            "Token expiry handling"
        ],
        "effort": "medium",
        "parallel": True
    }
]

from pm.epic import EpicManager
manager = EpicManager()
epic = manager.decompose_epic(epic, tasks_data)
```

## File Structure After Phase 09.2

```
pm/
├── __init__.py                    ✅
├── models.py                      ✅
├── CONTRACT.md                    ✅
├── prd.py                         ✅ NEW
├── epic.py                        ✅ NEW
├── templates/                     ✅ NEW
│   ├── prd.md.j2
│   ├── epic.md.j2
│   └── task.md.j2
├── integrations/
│   └── github_sync.py             ✅ (existing)
└── workspace/                     (gitignored)
    ├── prds/
    │   └── user-authentication.md
    └── epics/
        └── user-authentication/
            ├── epic.md
            ├── .metadata.yaml
            └── tasks/
                ├── task-01.md
                └── task-02.md
```

## Validation

All implementations include:
- ✅ Input validation
- ✅ Error handling
- ✅ Type hints
- ✅ Docstrings
- ✅ File existence checks
- ✅ Kebab-case name validation
- ✅ Status/Priority enum validation

## Next Steps (Phase 09.3)

- [ ] Implement `pm/bridge.py` - Format conversions
  - OpenSpec → PRD
  - Epic → Workstream bundle
  - Task status sync
- [ ] Create integration tests
- [ ] Add PowerShell wrappers
- [ ] Wire into core pipeline

## Status: ✅ READY FOR PHASE 09.3
