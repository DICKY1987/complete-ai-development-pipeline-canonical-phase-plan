---
doc_id: DOC-PM-CONTRACT-021
---

# PM Section Integration Contract

**Version:** 1.0  
**Date:** 2025-11-21  
**Status:** Draft

## Overview

This document defines the integration contract between the PM (Project Management) section and the rest of the pipeline. The PM section implements CCPM-inspired workflows for spec-driven development, providing PRD creation, epic planning, task decomposition, and optional GitHub issue synchronization.

## Architecture Principles

### 1. Section Isolation
- PM section is self-contained in `pm/` directory
- No direct imports from `core/` or `error/` modules into PM models
- Communication via well-defined interfaces (bridge pattern)

### 2. Bridge Pattern
```
OpenSpec ←→ PM (PRD/Epic/Task) ←→ Workstream Bundles ←→ Core Pipeline
```

### 3. Offline-First
- All core PM operations work without network access
- GitHub sync is optional and feature-flagged
- No external dependencies for local workflows

---

## Data Models

### PRD (Product Requirements Document)

**File Format:** Markdown with YAML frontmatter

```yaml
---
title: Feature Name
author: Developer Name
date: 2025-11-21
status: draft  # draft | approved | implemented | archived
priority: high  # low | medium | high | critical
labels: [feature, enhancement]
---

# Problem Statement
Description of the problem this feature solves...

# Solution Overview
High-level approach...

# Requirements
- Functional requirement 1
- Functional requirement 2

# Success Criteria
- Measurable criterion 1
- Measurable criterion 2

# Constraints
Technical, timeline, or resource constraints...

# Edge Cases
Potential failure modes and considerations...
```

**Storage:** `pm/workspace/prds/{prd-name}.md`

**Python Model:**
```python
@dataclass
class PRD:
    name: str
    title: str
    author: str
    date: datetime
    status: str
    priority: str
    labels: List[str]
    problem: str
    solution: str
    requirements: List[str]
    success_criteria: List[str]
    constraints: List[str]
    edge_cases: List[str]
```

---

### Epic

**File Format:** Markdown with YAML frontmatter + metadata sidecar

```yaml
---
title: Epic Title
prd: feature-name
created: 2025-11-21
status: planned  # planned | in-progress | completed | blocked
priority: high
github_issue: null  # Issue number if synced
---

# Technical Approach
Architecture decisions and strategy...

# Dependencies
- External dependency 1
- Epic/task dependency 2

# Risk Assessment
Potential blockers and mitigation strategies...

# Implementation Plan
High-level steps to complete this epic...
```

**Metadata:** `pm/workspace/epics/{epic-name}/.metadata.yaml`
```yaml
epic_name: feature-name
status: planned
task_count: 5
completed_tasks: 0
progress_percent: 0
github_issue: null
created_at: 2025-11-21T00:00:00Z
updated_at: 2025-11-21T00:00:00Z
```

**Storage:** `pm/workspace/epics/{epic-name}/epic.md`

**Python Model:**
```python
@dataclass
class Epic:
    name: str
    title: str
    prd_name: str
    created: datetime
    status: str
    priority: str
    github_issue: Optional[int]
    technical_approach: str
    dependencies: List[str]
    risks: List[str]
    implementation_plan: str
    tasks: List['Task'] = field(default_factory=list)
```

---

### Task

**File Format:** Markdown with YAML frontmatter

```yaml
---
title: Task Title
epic: feature-name
task_id: task-01  # Auto-assigned
status: pending  # pending | in-progress | completed | blocked
priority: medium
assignee: null
effort: medium  # small | medium | large
parallel: true  # Can run in parallel with other tasks
dependencies: []  # List of task IDs
file_scope: [src/file1.py, src/file2.py]
github_issue: null
---

# Description
Detailed task description...

# Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

# Technical Notes
Implementation guidance, gotchas, references...

# Files to Modify
- src/file1.py: Add function X
- src/file2.py: Update class Y
```

**Storage:** `pm/workspace/epics/{epic-name}/tasks/{task-id}.md`

**Python Model:**
```python
@dataclass
class Task:
    task_id: str
    title: str
    epic_name: str
    status: str
    priority: str
    assignee: Optional[str]
    effort: str
    parallel: bool
    dependencies: List[str]
    file_scope: List[Path]
    github_issue: Optional[int]
    description: str
    acceptance_criteria: List[str]
    technical_notes: str
    files_to_modify: Dict[str, str]
```

---

## Interface Definitions

### 1. PM → Core Bridge (`pm/bridge.py`)

#### Convert PRD to Epic
```python
def prd_to_epic(prd: PRD) -> Epic:
    """Convert a PRD into an Epic with initial planning."""
    ...
```

#### Convert Epic to Workstream Bundle
```python
def epic_to_bundle(epic: Epic, tool_profile: str = "aider") -> Dict:
    """
    Convert Epic + Tasks into workstream bundle schema.
    
    Returns: Dict conforming to schema/workstream.schema.json
    """
    ...
```

#### Convert OpenSpec Change to PRD
```python
def openspec_to_prd(change_dir: Path) -> PRD:
    """
    Parse OpenSpec change (proposal.md + tasks.md) into PRD.
    """
    ...
```

#### Sync Workstream Progress to Epic
```python
def sync_workstream_to_task(ws_id: str, task_id: str, state: str) -> None:
    """Update task status based on workstream execution state."""
    ...
```

---

### 2. Core → PM Bridge (`core/planning/ccpm_integration.py`)

#### Generate Workstream from Task
```python
def task_to_workstream(task: Task, tool_profile: str = "aider") -> Dict:
    """
    Convert a single Task into a workstream JSON.
    
    Returns: Dict with workstream metadata and steps
    """
    ...
```

#### Validate Parallel Execution
```python
def validate_parallel_tasks(tasks: List[Task]) -> List[ConflictError]:
    """
    Check for file-scope conflicts between tasks marked parallel.
    
    Returns: List of conflicts (empty if safe to parallelize)
    """
    ...
```

---

### 3. GitHub Integration (`pm/github_client.py`)

**Feature Flag:** Controlled by `config/ccpm.yaml` → `github.enabled`

#### Create Epic Issue
```python
def create_epic(
    title: str,
    body: str,
    labels: List[str] = ["epic"]
) -> int:
    """
    Create GitHub issue representing an epic.
    
    Returns: Issue number
    """
    ...
```

#### Create Task Issue
```python
def create_task(
    epic_num: int,
    title: str,
    body: str,
    labels: List[str] = ["task"]
) -> int:
    """
    Create GitHub issue for task, linked to epic.
    
    Returns: Issue number
    """
    ...
```

#### Update Progress
```python
def add_comment(issue_num: int, body: str) -> None:
    """Post progress update as issue comment."""
    ...
```

---

### 4. Event System (`pm/event_handler.py`)

**Integration Point:** Core orchestrator emits events, PM handler listens

#### Event Types
```python
class EventType(Enum):
    WORKSTREAM_START = "workstream_start"
    STEP_COMPLETE = "step_complete"
    WORKSTREAM_COMPLETE = "workstream_complete"
    WORKSTREAM_BLOCKED = "workstream_blocked"
    WORKSTREAM_FAILED = "workstream_failed"
```

#### Event Payload Schema
```python
@dataclass
class WorkstreamEvent:
    event_type: EventType
    ws_id: str
    epic_name: Optional[str]
    task_id: Optional[str]
    timestamp: datetime
    payload: Dict  # Event-specific data
```

#### Handler Interface
```python
class PipelineEventHandler:
    def handle(self, event: WorkstreamEvent) -> None:
        """
        Process pipeline event and update PM state.
        Optionally sync to GitHub if enabled.
        """
        ...
```

---

## Configuration Schema

### `config/ccpm.yaml`

```yaml
ccpm:
  # Workspace settings
  workspace_dir: "pm/workspace"  # Relative to repo root
  template_dir: "pm/templates"
  
  # GitHub integration (optional)
  github:
    enabled: false               # Feature flag
    repo_owner: ""               # GitHub org/user
    repo_name: ""                # Repository name
    use_cli: true                # Prefer gh CLI over API
    rate_limit_buffer: 100       # Stop before hitting limit
    retry_attempts: 3
    retry_backoff: 2.0           # Exponential backoff multiplier
  
  # Parallel execution
  parallel:
    enabled: true
    max_workers: 3
    use_worktrees: true
    worktree_base_dir: "../epic-worktrees"
  
  # Logging
  logging:
    level: INFO                  # DEBUG | INFO | WARNING | ERROR
    format: json                 # json | text
    file: "logs/ccpm.log"
```

### Environment Variables

```bash
# .env (optional overrides)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx    # GitHub API token
ENABLE_CCPM_SYNC=false            # Override github.enabled
CCPM_MAX_PARALLEL=3               # Override parallel.max_workers
CCPM_WORKTREE_DIR=../epic-worktrees
```

---

## File System Layout

```
pm/
├── __init__.py
├── CONTRACT.md                   # This file
├── bridge.py                     # Format conversions
├── epic.py                       # Epic management
├── event_handler.py              # Pipeline event listener
├── github_client.py              # GitHub API wrapper
├── models.py                     # Data classes (PRD, Epic, Task)
├── prd.py                        # PRD management
├── templates/                    # Jinja2 templates
│   ├── prd.md.j2
│   ├── epic.md.j2
│   └── task.md.j2
└── workspace/                    # Working files (gitignored)
    ├── prds/
    │   └── {prd-name}.md
    └── epics/
        └── {epic-name}/
            ├── epic.md
            ├── .metadata.yaml
            └── tasks/
                └── {task-id}.md

core/planning/
└── ccpm_integration.py           # CCPM → Workstream converter

config/
├── ccpm.yaml                     # CCPM configuration
└── features.yaml                 # Feature flags (updated)
```

---

## Validation Rules

### PRD Validation
- ✅ Title is non-empty
- ✅ At least one requirement defined
- ✅ At least one success criterion defined
- ✅ Status is valid enum value
- ✅ Priority is valid enum value

### Epic Validation
- ✅ References existing PRD
- ✅ Technical approach is documented
- ✅ All task dependencies form valid DAG (no cycles)
- ✅ Status transitions are valid (planned → in-progress → completed)

### Task Validation
- ✅ References existing epic
- ✅ File scope is non-empty
- ✅ All dependencies reference existing tasks
- ✅ Parallel tasks have no file-scope overlap
- ✅ Acceptance criteria are defined

---

## Error Handling

### Network Failures (GitHub)
- Graceful degradation: Log error, continue local workflow
- Retry logic: 3 attempts with exponential backoff
- User notification: Warning displayed, epic continues offline

### Validation Failures
- Stop early: Don't convert invalid PRD to epic
- Clear errors: File, line number, specific issue
- Suggestions: Offer fixes when possible

### File Conflicts
- Pre-check: Validate file-scope overlap before parallel execution
- Early warning: Display conflicts during epic decomposition
- Manual resolution: Suggest serialization or file-scope adjustment

---

## Versioning and Compatibility

### Contract Version
- Current: `CCPM_CONTRACT_V1`
- Breaking changes require new version identifier
- Tooling checks compatibility at runtime

### Migration Path
When contract changes:
1. Add new version identifier
2. Support both old and new for 1 release cycle
3. Deprecation warnings for old version
4. Remove old version support after 2 releases

---

## Testing Requirements

### Unit Tests
- PRD/Epic/Task CRUD operations
- Validation logic (all rules)
- Bridge conversions (bidirectional where applicable)
- GitHub client (mocked API calls)

### Integration Tests
- OpenSpec → PRD → Epic → Workstream (full flow)
- Event handling (orchestrator → PM handler)
- Parallel execution (worktree creation/merge)

### Contract Tests
- Schema validation (all data models)
- Interface contracts (all public functions)
- Configuration loading (valid and invalid configs)

---

## Security Considerations

### Secrets Management
- GitHub token via environment variable only
- Never commit tokens to repository
- Support for token rotation (no hard-coded expiry)

### File Access
- Workspace directory restricted to `pm/workspace/`
- No arbitrary file system writes
- Validate all path inputs (prevent traversal)

### GitHub Operations
- Rate limit enforcement (respect API limits)
- Scope validation (only create/update issues)
- Audit logging (all GitHub operations logged)

---

## Performance Targets

### Local Operations (No GitHub)
- PRD creation: < 2 seconds
- Epic decomposition: < 5 seconds
- Task-to-workstream conversion: < 1 second per task

### GitHub Operations
- Epic creation: < 3 seconds (network dependent)
- Task creation: < 2 seconds per task (batched when possible)
- Progress update: < 1 second (async when possible)

### Parallel Execution
- 3 parallel tasks: 2-3x faster than sequential
- Worktree creation: < 5 seconds
- Worktree merge: < 10 seconds (no conflicts)

---

## Future Extensions (Out of Scope for Phase 09)

- Multiple issue tracker support (Jira, Linear, etc.)
- Web UI for PRD/Epic creation
- Automated task estimation (ML-based)
- Real-time collaboration (multi-user editing)
- Advanced dependency visualization (graph rendering)

---

## References

- [Phase 09 Plan](../../docs/Project_Management_docs/PHASE-09-CCPM-INTEGRATION-PLAN.md)
- [Workstream Schema](../../schema/workstream.schema.json)
- [CCPM Original Docs](../../ccpm/README.md)
- [AGENTS.md Section Rules](../../AGENTS.md)

---

**Status:** Draft - Ready for Review  
**Reviewers:** Architecture Team, Pipeline Team  
**Approval Required:** Yes (before Phase 09.2 implementation)
