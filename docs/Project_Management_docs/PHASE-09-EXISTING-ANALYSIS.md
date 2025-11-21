# Phase 09.1: Existing PM Folder Analysis

**Date:** 2025-11-21  
**Purpose:** Inventory existing CCPM assets and identify gaps for native implementation

---

## Current PM Folder Structure

```
pm/
├── agents/                    # ✅ CCPM agents (keep as reference)
│   ├── code-analyzer.md
│   ├── file-analyzer.md
│   ├── parallel-worker.md
│   └── test-runner.md
├── commands/                  # ✅ CCPM slash commands (keep as reference)
│   ├── pm/                   # 50+ command files
│   ├── context/
│   └── testing/
├── context/                   # ✅ Context management (keep)
│   └── README.md
├── epics/                     # ✅ Epic workspace (.gitkeep only)
├── hooks/                     # ✅ Git hooks (keep)
│   ├── bash-worktree-fix.sh
│   └── README.md
├── integrations/              # ✅ EXISTING GITHUB SYNC!
│   ├── __init__.py
│   └── github_sync.py        # ← Already implemented!
├── prds/                      # ✅ PRD workspace (.gitkeep only)
├── rules/                     # ✅ CCPM rules (keep as reference)
│   ├── agent-coordination.md
│   ├── branch-operations.md
│   ├── datetime.md
│   ├── frontmatter-operations.md
│   ├── github-operations.md
│   ├── path-standards.md
│   ├── standard-patterns.md
│   ├── strip-frontmatter.md
│   ├── test-execution.md
│   ├── use-ast-grep.md
│   └── worktree-operations.md
├── scripts/                   # ✅ Bash scripts (reference for PowerShell conversion)
│   ├── pm/                   # 15+ utility scripts
│   │   ├── init.sh           # ← Initialization logic
│   │   ├── status.sh
│   │   ├── help.sh
│   │   └── ...
│   ├── test-and-log.sh       # ← Test runner
│   ├── check-path-standards.sh
│   └── fix-path-standards.sh
├── __init__.py                # ✅ Updated with new structure
├── models.py                  # ✅ NEW - Created in Phase 09.1
└── CONTRACT.md                # ✅ NEW - Created in Phase 09.1
```

---

## Key Findings

### ✅ Already Implemented

1. **GitHub Sync (`pm/integrations/github_sync.py`)**
   - ✅ `gh` CLI integration with fallback
   - ✅ `comment()` - Post issue comments
   - ✅ `ensure_epic()` - Find/create epic issues
   - ✅ `set_status()` - Update labels and state
   - ✅ `post_lifecycle_comment()` - Event formatting
   - ✅ Config loading from `config/github.yaml`
   - ✅ Environment variable overrides
   - ✅ Safe no-op when disabled

2. **Initialization Script (`pm/scripts/pm/init.sh`)**
   - ✅ Dependency checks (gh CLI)
   - ✅ GitHub authentication
   - ✅ gh-sub-issue extension install
   - ✅ Directory structure creation
   - ✅ Label creation on GitHub
   - ✅ CLAUDE.md template

3. **Existing Rules and Patterns**
   - ✅ Agent coordination patterns
   - ✅ Worktree operations
   - ✅ GitHub operations
   - ✅ Frontmatter handling
   - ✅ Path standards

4. **Command Definitions (50+ markdown files)**
   - ✅ PRD commands (new, list, edit, parse, status)
   - ✅ Epic commands (decompose, sync, show, close, etc.)
   - ✅ Issue commands (start, sync, close, analyze)
   - ✅ Workflow commands (next, status, blocked, etc.)

---

## Gaps to Fill (Phase 09.1-09.2)

### ❌ Missing Python Implementations

1. **PRD Management (`pm/prd.py`)** - NOT YET IMPLEMENTED
   - Need: `PRDManager` class
   - Functions: `create_prd()`, `load_prd()`, `list_prds()`, `validate_prd()`
   - File I/O with YAML frontmatter parsing

2. **Epic Management (`pm/epic.py`)** - NOT YET IMPLEMENTED
   - Need: `EpicManager` class
   - Functions: `create_epic_from_prd()`, `decompose_epic()`, `load_epic()`
   - Metadata management (`.metadata.yaml`)

3. **Bridge Layer (`pm/bridge.py`)** - NOT YET IMPLEMENTED
   - OpenSpec → PRD conversion
   - PRD → Epic conversion
   - Epic → Workstream bundle conversion
   - Task status sync

4. **Event Handler (`pm/event_handler.py`)** - NOT YET IMPLEMENTED
   - Listen to pipeline events
   - Call `github_sync.py` functions
   - Update local task status

### ⚠️ Needs Adaptation

5. **PowerShell Commands** - BASH ONLY
   - Current: 15+ bash scripts in `pm/scripts/pm/`
   - Need: PowerShell equivalents in `scripts/ccpm/`
   - Strategy: Python core + thin PowerShell wrappers

6. **Templates (`pm/templates/`)** - MISSING
   - Need: Jinja2 templates for PRD, Epic, Task
   - Reference: Command markdown files have inline templates

---

## Integration Points

### ✅ Ready to Use

**GitHub Sync (`pm/integrations/github_sync.py`)**
```python
from pm.integrations.github_sync import comment, ensure_epic, set_status

# Usage (already works!)
issue_num = ensure_epic("Feature: User Authentication", body="...", labels=["epic"])
comment(issue_num, "Starting implementation...")
set_status(issue_num, state="open", add_labels=["in-progress"])
```

### 🔧 Needs Wiring

**Core Pipeline → PM Events**
```python
# In core/engine/orchestrator.py (to be added)
from pm.event_handler import PipelineEventHandler

handler = PipelineEventHandler()
handler.on_workstream_start(ws_id="ws-001", epic_name="feature-auth")
```

---

## Recommended Phase 09.1 Actions

### 1. Clean Up (Minimal Changes)
- ✅ Keep existing `pm/integrations/github_sync.py` (already perfect!)
- ✅ Keep `pm/agents/`, `pm/commands/`, `pm/rules/` as reference docs
- ✅ Keep `pm/scripts/` as bash reference
- ❌ Don't delete anything yet - may need for reference

### 2. Add Missing Core (New Files)
- ✅ `pm/models.py` - DONE ✓
- ✅ `pm/CONTRACT.md` - DONE ✓
- ⏭️ `pm/prd.py` - NEXT
- ⏭️ `pm/epic.py` - NEXT
- ⏭️ `pm/bridge.py` - Phase 09.3
- ⏭️ `pm/event_handler.py` - Phase 09.4
- ⏭️ `pm/templates/` - Phase 09.2

### 3. PowerShell Wrappers (New Scripts)
- ⏭️ `scripts/ccpm/New-PRD.ps1` - Thin wrapper → `python -m pm.prd create`
- ⏭️ `scripts/ccpm/New-Epic.ps1` - Thin wrapper → `python -m pm.epic create`
- ⏭️ `scripts/ccpm/Sync-Epic.ps1` - Thin wrapper → `python -m pm.bridge sync`

### 4. Configuration (Already Done!)
- ✅ `config/github.yaml` - Updated ✓
- ✅ `config/ccpm.yaml` - Created ✓
- ✅ `.env.example` - Updated ✓
- ✅ `.gitignore` - Updated ✓

---

## Phase 09.1 Completion Checklist

### Foundation
- [x] Analyze existing `pm/` folder
- [x] Create `pm/CONTRACT.md`
- [x] Create `pm/models.py` with data classes
- [x] Update `pm/__init__.py`
- [x] Update `config/github.yaml`
- [x] Create `config/ccpm.yaml`
- [x] Update `.env.example`
- [x] Update `.gitignore`

### Next: PRD/Epic Implementation (Phase 09.2)
- [ ] Create `pm/templates/` directory
- [ ] Add `pm/templates/prd.md.j2`
- [ ] Add `pm/templates/epic.md.j2`
- [ ] Add `pm/templates/task.md.j2`
- [ ] Implement `pm/prd.py`
- [ ] Implement `pm/epic.py`
- [ ] Create PowerShell wrapper: `scripts/ccpm/New-PRD.ps1`
- [ ] Create PowerShell wrapper: `scripts/ccpm/New-Epic.ps1`
- [ ] Unit tests: `tests/pm/test_prd.py`
- [ ] Unit tests: `tests/pm/test_epic.py`

---

## Key Insights

1. **GitHub sync already works!** 
   - `pm/integrations/github_sync.py` is production-ready
   - Just need to wire it into the pipeline

2. **CCPM commands are templates, not code**
   - Command `.md` files define behavior
   - Bash scripts provide implementation
   - We need Python equivalents

3. **Agents are documentation**
   - Markdown files describe agent roles
   - Not executable code
   - Reference for building features

4. **Rules are valuable patterns**
   - Keep as documentation
   - Use when implementing features
   - E.g., `worktree-operations.md` guides worktree implementation

---

## Decision: Hybrid Approach

**Keep:**
- ✅ `pm/integrations/github_sync.py` (production code)
- ✅ `pm/agents/`, `pm/commands/`, `pm/rules/` (documentation)
- ✅ `pm/scripts/` (bash reference)

**Add:**
- ✅ `pm/models.py` (Python data classes)
- ⏭️ `pm/prd.py`, `pm/epic.py` (Python management)
- ⏭️ `pm/bridge.py` (format converters)
- ⏭️ `pm/event_handler.py` (pipeline integration)
- ⏭️ `scripts/ccpm/*.ps1` (PowerShell wrappers)

**Don't Delete:**
- Keep everything for now
- May need bash scripts as reference
- Commands define expected behavior

---

## Status

✅ **Phase 09.1 Foundation: COMPLETE**

Ready to proceed with Phase 09.2: Core PM Workflow Implementation

---

**Next Steps:**
1. Create Jinja2 templates
2. Implement `pm/prd.py`
3. Implement `pm/epic.py`
4. Add PowerShell wrappers
5. Write unit tests

