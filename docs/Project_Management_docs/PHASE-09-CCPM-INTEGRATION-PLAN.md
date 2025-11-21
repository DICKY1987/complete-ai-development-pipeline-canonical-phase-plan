# Phase 09: CCPM Integration - Recommended Plan

**Status:** Draft  
**Created:** 2025-11-21  
**Last Updated:** 2025-11-21  
**Version:** 1.0  

## Executive Summary

This phase integrates CCPM (Critical Chain Project Management) principles and workflows into the pipeline without vendoring the entire external CCPM repository. Instead, we extract core concepts (PRD → Epic → Task → Issue → Code) and implement them natively using existing pipeline architecture.

**Key Principle:** Bridge pattern - Keep CCPM workflow concepts separate from core pipeline execution, but provide seamless integration points.

---

## Objectives

1. **Enable spec-driven planning** - PRD creation, epic decomposition, task breakdown
2. **GitHub issue tracking** - Optional synchronization for visibility and collaboration
3. **Parallel task coordination** - Multi-agent execution with worktree isolation
4. **Traceability** - Full audit trail from requirement to implementation
5. **Windows-first** - PowerShell wrappers with Python core logic

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CCPM Workflow Layer                         │
│  PRD → Epic Planning → Task Decomposition → GitHub Issues       │
│              (pm/ section - domain-specific)                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Bridge & Conversion Layer                      │
│  OpenSpec ↔ CCPM ↔ Workstream Bundles                          │
│      (pm/bridge.py, core/planning/ccpm_integration.py)          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Core Pipeline Orchestration                     │
│  Workstream Execution → State Tracking → GitHub Updates         │
│          (core/engine/, core/state/, core/planning/)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Scope

### In Scope
- Native CCPM workflow implementation in `pm/` section
- Bridge modules for OpenSpec ↔ CCPM ↔ Workstream conversion
- Optional GitHub issue synchronization (feature-flagged)
- Parallel task orchestration with worktree support
- Windows-first tooling (PowerShell + Python)
- Comprehensive documentation and examples

### Out of Scope
- Vendoring entire CCPM repository (too heavy, maintenance burden)
- Replacing existing pipeline orchestration (extend, don't replace)
- Non-GitHub issue trackers (GitHub-only for now)
- GUI/web interface (CLI-focused)

---

## Key Design Decisions

### Decision 1: Native Implementation vs Vendoring
**Choice:** Implement CCPM principles natively, don't vendor external repo  
**Rationale:**
- External CCPM is designed for `.claude/` directories and slash commands
- Our pipeline uses different architecture (`core/`, `pm/`, Python-first)
- Vendoring creates maintenance burden and version conflicts
- Extract valuable concepts, implement in our style

### Decision 2: GitHub Integration Strategy
**Choice:** Optional, feature-flagged GitHub sync via `gh` CLI  
**Rationale:**
- Not all users want GitHub dependency
- `gh` CLI simpler than direct API calls
- Fallback to PyGithub for programmatic access
- Controlled via `ENABLE_CCPM_SYNC` config flag

### Decision 3: Section Placement
**Choice:** `pm/` for workflow logic, `core/` for execution  
**Rationale:**
- Aligns with AGENTS.md section-based architecture
- PM logic is domain-specific (project management)
- Core logic is execution-focused (orchestration, state)
- Clear separation of concerns

### Decision 4: Parallel Execution Model
**Choice:** Worktree-based isolation with Python subprocess orchestration  
**Rationale:**
- Git worktrees provide true filesystem isolation
- Python subprocess management is cross-platform
- Aligns with existing `core/engine/orchestrator.py` patterns
- Supports both local and CI environments

---

## Phase Breakdown

### Phase 09.1 - Clean Up and Foundation (Week 1)

**Goal:** Prepare `pm/` section and establish integration contracts

#### Tasks
1. **Clean up existing `pm/` folder**
   - Remove duplicate CCPM clone (`ccpm/` subdirectory)
   - Keep only integration-specific code
   - Add `.gitignore` entries for CCPM ephemeral data

2. **Create bridge module structure**
   ```
   pm/
   ├── __init__.py
   ├── bridge.py              # OpenSpec ↔ CCPM ↔ Workstream converter
   ├── github_client.py       # GitHub API wrapper (gh CLI + PyGithub)
   ├── event_handler.py       # Listen to pipeline events, update issues
   ├── models.py              # PRD, Epic, Task data classes
   └── templates/             # Jinja2 templates for PRDs, epics, tasks
   ```

3. **Define integration contracts**
   - `pm/CONTRACT.md` - Define interfaces between PM and pipeline
   - PRD format specification (YAML frontmatter + Markdown)
   - Epic/Task metadata schema
   - Event payload schema for GitHub updates

4. **Configuration setup**
   - `config/ccpm.yaml` - CCPM-specific settings
   - `.env.example` - Add `GITHUB_TOKEN`, `ENABLE_CCPM_SYNC`, `CCPM_REPO`
   - Feature flags in `config/features.yaml`

#### Deliverables
- [ ] Clean `pm/` structure with documented contracts
- [ ] Configuration files with sensible defaults
- [ ] `pm/CONTRACT.md` integration specification

#### Acceptance Criteria
- `pm/` imports cleanly in Python: `from pm.bridge import convert_prd_to_bundle`
- Configuration validates with existing config loader
- No external dependencies required when sync disabled

---

### Phase 09.2 - Core PM Workflow (Week 1-2)

**Goal:** Implement PRD → Epic → Task workflow without GitHub dependency

#### Tasks
1. **Implement PRD management** (`pm/prd.py`)
   ```python
   class PRDManager:
       def create_prd(name: str, interactive: bool = True) -> PRD
       def load_prd(name: str) -> PRD
       def list_prds() -> List[PRD]
       def validate_prd(prd: PRD) -> List[ValidationError]
   ```

2. **Implement Epic planning** (`pm/epic.py`)
   ```python
   class EpicManager:
       def create_epic_from_prd(prd: PRD) -> Epic
       def decompose_epic(epic: Epic) -> List[Task]
       def load_epic(name: str) -> Epic
       def validate_task_dependencies(tasks: List[Task]) -> bool
   ```

3. **Add CLI commands** (`scripts/prd.py`, `scripts/epic.py`)
   ```bash
   # PowerShell wrappers
   scripts/ccpm/New-PRD.ps1
   scripts/ccpm/New-Epic.ps1
   scripts/ccpm/Show-Epic.ps1
   ```

4. **File storage format**
   ```
   pm/workspace/
   ├── prds/
   │   └── feature-name.md      # PRD with YAML frontmatter
   ├── epics/
   │   └── feature-name/
   │       ├── epic.md          # Epic specification
   │       ├── tasks/
   │       │   ├── task-01.md   # Individual task files
   │       │   └── task-02.md
   │       └── .metadata.yaml   # Epic state, progress tracking
   ```

#### Deliverables
- [ ] `pm/prd.py`, `pm/epic.py`, `pm/models.py` implementation
- [ ] CLI commands: `New-PRD.ps1`, `New-Epic.ps1`, `Show-Epic.ps1`
- [ ] File format documentation in `pm/CONTRACT.md`
- [ ] Unit tests: `tests/pm/test_prd.py`, `tests/pm/test_epic.py`

#### Acceptance Criteria
- Can create PRD interactively or from template
- Epic generation from PRD produces valid task breakdown
- All operations work without network access
- `pytest tests/pm/ -q` passes with 100% coverage

---

### Phase 09.3 - Bridge Layer (Week 2)

**Goal:** Convert between OpenSpec, CCPM, and Workstream formats

#### Tasks
1. **Implement OpenSpec → CCPM converter** (`pm/bridge.py`)
   ```python
   def openspec_change_to_prd(change_dir: Path) -> PRD
   def openspec_change_to_epic(change_dir: Path) -> Epic
   ```

2. **Implement CCPM → Workstream converter** (`core/planning/ccpm_integration.py`)
   ```python
   def epic_to_bundle(epic: Epic, tool_profile: str = "aider") -> Dict
   def tasks_to_workstreams(tasks: List[Task]) -> List[Dict]
   def validate_parallel_tasks(tasks: List[Task]) -> List[ConflictError]
   ```

3. **Implement Workstream → CCPM sync** (`pm/bridge.py`)
   ```python
   def sync_workstream_progress(ws_id: str, epic: Epic) -> None
   def update_task_status(task_id: str, state: str) -> None
   ```

4. **Add integration tests**
   - Test OpenSpec → PRD conversion with real examples
   - Test Epic → Bundle generation
   - Test round-trip: OpenSpec → CCPM → Workstream → execution

#### Deliverables
- [ ] `pm/bridge.py` implementation
- [ ] `core/planning/ccpm_integration.py` implementation
- [ ] Integration tests: `tests/integration/test_ccpm_bridge.py`
- [ ] Example conversions in `examples/ccpm_workflows/`

#### Acceptance Criteria
- OpenSpec change converts to valid PRD with all metadata preserved
- Epic converts to schema-compliant workstream bundle
- Round-trip conversion maintains semantic equivalence
- Integration tests pass without network access

---

### Phase 09.4 - GitHub Integration (Week 2-3)

**Goal:** Optional GitHub issue synchronization (feature-flagged)

#### Tasks
1. **Implement GitHub client** (`pm/github_client.py`)
   ```python
   class GitHubClient:
       def __init__(self, token: str = None, use_cli: bool = True)
       
       # Epic operations
       def create_epic(title: str, body: str, labels: List[str]) -> int
       def update_epic(issue_num: int, state: str = None, labels: List[str] = None)
       
       # Task operations
       def create_task(epic_num: int, title: str, body: str) -> int
       def link_task_to_epic(task_num: int, epic_num: int) -> None
       
       # Comments and updates
       def add_comment(issue_num: int, body: str) -> None
       def update_task_checklist(epic_num: int, tasks: List[Task]) -> None
   ```

2. **Implement event handler** (`pm/event_handler.py`)
   ```python
   class PipelineEventHandler:
       def on_workstream_start(ws_id: str, epic: Epic) -> None
       def on_step_complete(ws_id: str, step: str, result: StepResult) -> None
       def on_workstream_complete(ws_id: str, success: bool) -> None
       def on_workstream_blocked(ws_id: str, reason: str) -> None
   ```

3. **Integrate with orchestrator** (`core/engine/orchestrator.py`)
   ```python
   # Add event emission at key lifecycle points
   def _emit_event(self, event_type: str, payload: Dict) -> None:
       if config.get("ENABLE_CCPM_SYNC"):
           event_handler.handle(event_type, payload)
   ```

4. **Add PowerShell commands**
   ```powershell
   scripts/ccpm/Sync-Epic.ps1        # Sync epic to GitHub
   scripts/ccpm/Update-TaskStatus.ps1 # Update task status
   scripts/ccpm/Show-EpicStatus.ps1   # Display epic progress
   ```

#### Deliverables
- [ ] `pm/github_client.py` with dual mode (`gh` CLI + PyGithub)
- [ ] `pm/event_handler.py` implementation
- [ ] Orchestrator integration points
- [ ] PowerShell commands for GitHub operations
- [ ] Tests: `tests/pm/test_github_client.py` (mocked)

#### Acceptance Criteria
- Works with `gh` CLI when available, falls back to PyGithub
- All GitHub calls skip gracefully when `ENABLE_CCPM_SYNC=false`
- Mocked tests verify correct API calls without network
- Can sync epic lifecycle to real GitHub repo (manual verification)

---

### Phase 09.5 - Parallel Orchestration (Week 3)

**Goal:** Multi-task execution with worktree isolation

#### Tasks
1. **Extend parallel orchestrator** (`core/engine/parallel.py`)
   ```python
   class ParallelOrchestrator:
       def plan_parallel_execution(epic: Epic) -> ExecutionPlan
       def execute_tasks_parallel(plan: ExecutionPlan, max_workers: int = 3) -> Results
       def monitor_progress() -> Dict[str, TaskStatus]
   ```

2. **Add worktree management** (`core/state/worktree.py`)
   ```python
   class WorktreeManager:
       def create_worktree(epic_name: str, branch: str = None) -> Path
       def sync_files_to_worktree(worktree: Path, files: List[Path]) -> None
       def merge_worktree(worktree: Path, strategy: str = "auto") -> MergeResult
       def cleanup_worktree(worktree: Path) -> None
   ```

3. **Add conflict detection**
   ```python
   def detect_file_conflicts(tasks: List[Task]) -> List[Conflict]
   def suggest_serialization(conflicts: List[Conflict]) -> ExecutionPlan
   ```

4. **PowerShell worktree commands**
   ```powershell
   scripts/ccpm/Start-EpicWorktree.ps1   # Create isolated worktree
   scripts/ccpm/Merge-EpicWorktree.ps1   # Merge results back
   scripts/ccpm/Test-ParallelTasks.ps1   # Validate parallel safety
   ```

#### Deliverables
- [ ] `core/engine/parallel.py` implementation
- [ ] `core/state/worktree.py` implementation
- [ ] Conflict detection algorithms
- [ ] PowerShell worktree commands
- [ ] Tests: `tests/core/test_parallel.py`, `tests/core/test_worktree.py`

#### Acceptance Criteria
- Can execute 2+ tasks in parallel with no file overlap
- Worktree creation/merge works on Windows and WSL
- Conflict detection prevents unsafe parallel execution
- Demo: 3-task epic completes in parallel, merges cleanly

---

### Phase 09.6 - End-to-End Integration (Week 3-4)

**Goal:** Complete workflow from OpenSpec change to merged code

#### Tasks
1. **Create end-to-end workflow script** (`scripts/ccpm_workflow.py`)
   ```python
   # Usage: python scripts/ccpm_workflow.py --change-id feature-validation
   
   def e2e_workflow(change_id: str, enable_github: bool = False):
       # 1. Convert OpenSpec change to PRD
       prd = openspec_change_to_prd(f"openspec/changes/{change_id}")
       
       # 2. Generate epic from PRD
       epic = create_epic_from_prd(prd)
       
       # 3. Convert epic to workstream bundles
       bundles = epic_to_bundles(epic)
       
       # 4. Sync to GitHub (if enabled)
       if enable_github:
           epic_num = github_client.create_epic(...)
       
       # 5. Execute workstreams in parallel
       results = parallel_orchestrator.execute(bundles)
       
       # 6. Update GitHub with results
       if enable_github:
           github_client.update_epic(epic_num, results)
       
       # 7. Merge worktrees
       worktree_manager.merge_all()
   ```

2. **Add comprehensive example**
   ```
   examples/ccpm_workflows/
   ├── input/
   │   └── openspec-change/          # Sample OpenSpec change
   ├── output/
   │   ├── prd.md                    # Generated PRD
   │   ├── epic/                     # Generated epic + tasks
   │   └── workstreams/              # Generated workstream bundles
   └── README.md                     # Step-by-step walkthrough
   ```

3. **Integration test suite**
   ```python
   # tests/integration/test_ccpm_e2e.py
   def test_full_workflow_local_only():
       """End-to-end without GitHub"""
   
   def test_full_workflow_with_github_mock():
       """End-to-end with mocked GitHub calls"""
   
   def test_parallel_execution():
       """Multi-task parallel workflow"""
   ```

#### Deliverables
- [ ] `scripts/ccpm_workflow.py` end-to-end script
- [ ] Complete example in `examples/ccpm_workflows/`
- [ ] Integration tests: `tests/integration/test_ccpm_e2e.py`
- [ ] Demo video/GIF showing full workflow (optional)

#### Acceptance Criteria
- `python scripts/ccpm_workflow.py --change-id example` completes successfully
- Example workflow documented in `examples/ccpm_workflows/README.md`
- Integration tests pass in CI without network access
- Manual GitHub sync verified on test repository

---

### Phase 09.7 - Documentation and Developer UX (Week 4)

**Goal:** Comprehensive docs and easy onboarding

#### Tasks
1. **Core documentation**
   - `docs/Project_Management_docs/CCPM_QUICKSTART.md` - 5-minute getting started
   - `docs/Project_Management_docs/CCPM_ARCHITECTURE.md` - Technical deep dive
   - `docs/Project_Management_docs/CCPM_WORKFLOWS.md` - Common use cases
   - `docs/Project_Management_docs/CCPM_GITHUB_SETUP.md` - GitHub integration guide

2. **API reference**
   - Docstrings for all public functions
   - Type hints for all signatures
   - `docs/api/pm.md` - Generated API docs (Sphinx or mkdocs)

3. **Troubleshooting guide**
   ```markdown
   # Common Issues
   
   ## GitHub authentication fails
   - Check `gh auth status`
   - Verify `GITHUB_TOKEN` in .env
   - Run `gh auth login`
   
   ## Worktree merge conflicts
   - Check file overlap: `python scripts/ccpm/Test-ParallelTasks.ps1`
   - Use `git worktree list` to inspect state
   - Manual merge: `cd worktree && git merge main`
   ```

4. **Update root README**
   - Add CCPM section with quick links
   - Add badges for build status
   - Add workflow diagram

5. **PowerShell help system**
   ```powershell
   # Add Get-Help support to all scripts
   <#
   .SYNOPSIS
   Creates a new Product Requirements Document
   
   .DESCRIPTION
   Interactively guides you through PRD creation...
   
   .EXAMPLE
   .\New-PRD.ps1 -Name "feature-validation"
   #>
   ```

#### Deliverables
- [ ] Complete documentation suite in `docs/Project_Management_docs/`
- [ ] API reference with examples
- [ ] Troubleshooting guide with common issues
- [ ] Updated root README with CCPM section
- [ ] PowerShell help for all scripts

#### Acceptance Criteria
- New contributor can bootstrap and run workflow in < 15 minutes
- All PowerShell scripts have `Get-Help` support
- Documentation covers 90% of common use cases
- Technical review completed by non-author

---

### Phase 09.8 - Hardening and CI (Week 4-5)

**Goal:** Production-ready, tested, and CI-integrated

#### Tasks
1. **Add feature flags**
   ```yaml
   # config/features.yaml
   ccpm:
     enabled: true
     github_sync: false        # Opt-in
     parallel_execution: true
     worktree_isolation: true
     max_parallel_tasks: 3
   ```

2. **CI integration**
   ```yaml
   # .github/workflows/ccpm-tests.yml
   name: CCPM Tests
   
   jobs:
     unit-tests:
       - pytest tests/pm/ -v
     
     integration-tests:
       - pytest tests/integration/test_ccpm_e2e.py -v
     
     github-sync-mock:
       - ENABLE_CCPM_SYNC=true pytest tests/pm/test_github_client.py
   ```

3. **Structured logging**
   ```python
   import structlog
   
   logger = structlog.get_logger("pm.epic")
   logger.info("epic_created", epic_name=name, task_count=len(tasks))
   logger.warning("github_sync_failed", issue_num=42, error=str(e))
   ```

4. **Telemetry and metrics** (optional)
   ```python
   # Track workflow metrics
   metrics.counter("ccpm.prd.created").inc()
   metrics.histogram("ccpm.epic.task_count").observe(len(tasks))
   metrics.timer("ccpm.workflow.duration").time()
   ```

5. **Error recovery**
   - Graceful degradation when GitHub unavailable
   - Retry logic with exponential backoff
   - Rollback support for failed worktree merges

6. **Performance testing**
   - Benchmark parallel execution (3 tasks vs 1 task)
   - Measure worktree overhead
   - Profile GitHub API call efficiency

#### Deliverables
- [ ] Feature flags in `config/features.yaml`
- [ ] CI workflows for unit + integration tests
- [ ] Structured logging throughout CCPM modules
- [ ] Error recovery mechanisms
- [ ] Performance benchmarks documented

#### Acceptance Criteria
- CI passes on Windows and Linux runners
- All feature flags work as documented
- GitHub unavailability doesn't break local workflows
- Performance benchmarks show 2-3x speedup with parallel execution

---

## Milestones and Timeline

### M1: Foundation (Week 1)
- Phase 09.1 complete: Clean structure, contracts defined
- Phase 09.2 complete: PRD/Epic workflow works locally

### M2: Bridge Layer (Week 2)
- Phase 09.3 complete: OpenSpec ↔ CCPM ↔ Workstream conversion
- Phase 09.4 complete: GitHub sync (feature-flagged)

### M3: Parallel Execution (Week 3)
- Phase 09.5 complete: Worktree-based parallel orchestration
- Phase 09.6 complete: End-to-end workflow tested

### M4: Production Ready (Week 4-5)
- Phase 09.7 complete: Documentation and UX polished
- Phase 09.8 complete: Hardened, CI-integrated, benchmarked

---

## Success Criteria

### Technical
- [ ] All unit tests pass (`pytest tests/pm/ -q`)
- [ ] All integration tests pass (`pytest tests/integration/ -q`)
- [ ] CI green on Windows and Linux
- [ ] No external dependencies when sync disabled
- [ ] 2-3x speedup with parallel execution vs sequential

### Functional
- [ ] Can create PRD from OpenSpec change in < 2 minutes
- [ ] Epic decomposition produces valid workstream bundles
- [ ] Parallel tasks execute without conflicts
- [ ] GitHub sync updates issues correctly (manual verification)
- [ ] Worktree merge succeeds with no manual intervention

### Documentation
- [ ] New contributor onboarded in < 15 minutes
- [ ] All PowerShell scripts have help text
- [ ] API reference covers 100% of public functions
- [ ] Troubleshooting guide covers common issues
- [ ] Architecture document reviewed by team

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GitHub rate limits | High | Medium | Cache responses, exponential backoff, dry-run mode |
| Worktree merge conflicts | High | Medium | File-scope validation, pre-merge checks, rollback support |
| Cross-platform issues | Medium | High | Windows-first design, WSL fallback, CI on both platforms |
| CCPM concept mismatch | Medium | Low | Regular reviews, architecture alignment sessions |
| Network dependency creep | Low | Medium | Feature flags, offline-first design, mocked tests |
| Performance overhead | Medium | Low | Benchmarking, profiling, lazy loading |

---

## Dependencies

### External Tools
- **Git** (>= 2.35) - Worktree support
- **Python** (>= 3.11) - Core implementation
- **PowerShell** (>= 7.0) - Windows scripting
- **GitHub CLI** (`gh`, optional) - GitHub integration
- **PyGithub** (optional) - API fallback

### Internal Components
- `core/engine/orchestrator.py` - Event emission
- `core/state/db.py` - State tracking
- `core/planning/planner.py` - Workstream generation
- `specifications/tools/` - OpenSpec integration

---

## Exit Criteria

Phase 09 is complete when:

1. ✅ All 8 sub-phases delivered with passing tests
2. ✅ End-to-end workflow demo recorded
3. ✅ Documentation reviewed and approved
4. ✅ CI green on Windows and Linux
5. ✅ Performance benchmarks meet targets (2x+ speedup)
6. ✅ New contributor can onboard in < 15 minutes
7. ✅ Technical review completed by at least 2 team members
8. ✅ Zero P0/P1 bugs in issue tracker

---

## Appendices

### Appendix A: File Structure

```
Complete AI Development Pipeline – Canonical Phase Plan/
├── pm/                                    # CCPM workflow implementation
│   ├── __init__.py
│   ├── CONTRACT.md                        # Integration contract
│   ├── bridge.py                          # Format conversions
│   ├── epic.py                            # Epic management
│   ├── event_handler.py                   # Pipeline event handling
│   ├── github_client.py                   # GitHub API wrapper
│   ├── models.py                          # Data classes
│   ├── prd.py                             # PRD management
│   ├── templates/                         # Jinja2 templates
│   └── workspace/                         # Working files (gitignored)
│       ├── prds/
│       └── epics/
├── core/
│   ├── engine/
│   │   └── parallel.py                    # Parallel orchestrator
│   ├── planning/
│   │   └── ccpm_integration.py            # CCPM → Workstream converter
│   └── state/
│       └── worktree.py                    # Worktree management
├── config/
│   ├── ccpm.yaml                          # CCPM configuration
│   └── features.yaml                      # Feature flags
├── scripts/
│   ├── ccpm_workflow.py                   # End-to-end workflow
│   └── ccpm/                              # PowerShell commands
│       ├── New-PRD.ps1
│       ├── New-Epic.ps1
│       ├── Sync-Epic.ps1
│       ├── Start-EpicWorktree.ps1
│       └── Merge-EpicWorktree.ps1
├── tests/
│   ├── pm/                                # Unit tests
│   │   ├── test_prd.py
│   │   ├── test_epic.py
│   │   ├── test_bridge.py
│   │   └── test_github_client.py
│   └── integration/
│       ├── test_ccpm_bridge.py
│       └── test_ccpm_e2e.py
├── docs/Project_Management_docs/
│   ├── CCPM_QUICKSTART.md
│   ├── CCPM_ARCHITECTURE.md
│   ├── CCPM_WORKFLOWS.md
│   └── CCPM_GITHUB_SETUP.md
└── examples/ccpm_workflows/
    └── feature-validation/
```

### Appendix B: Command Reference

```powershell
# PRD Management
.\scripts\ccpm\New-PRD.ps1 -Name "feature-validation"
.\scripts\ccpm\Show-PRD.ps1 -Name "feature-validation"
.\scripts\ccpm\List-PRDs.ps1

# Epic Management
.\scripts\ccpm\New-Epic.ps1 -PRDName "feature-validation"
.\scripts\ccpm\Show-Epic.ps1 -Name "feature-validation"
.\scripts\ccpm\Decompose-Epic.ps1 -Name "feature-validation"

# GitHub Sync (when enabled)
.\scripts\ccpm\Sync-Epic.ps1 -Name "feature-validation"
.\scripts\ccpm\Update-TaskStatus.ps1 -TaskID 1234 -Status completed
.\scripts\ccpm\Show-EpicStatus.ps1 -EpicNumber 42

# Parallel Execution
.\scripts\ccpm\Test-ParallelTasks.ps1 -EpicName "feature-validation"
.\scripts\ccpm\Start-EpicWorktree.ps1 -EpicName "feature-validation"
.\scripts\ccpm\Merge-EpicWorktree.ps1 -EpicName "feature-validation"

# End-to-End Workflow
python scripts/ccpm_workflow.py --change-id feature-validation
python scripts/ccpm_workflow.py --change-id feature-validation --enable-github
```

### Appendix C: Configuration Examples

```yaml
# config/ccpm.yaml
ccpm:
  workspace_dir: "pm/workspace"
  template_dir: "pm/templates"
  
  github:
    enabled: false                # Feature flag
    repo_owner: "your-org"
    repo_name: "your-repo"
    use_cli: true                 # Use gh CLI vs PyGithub
    rate_limit_buffer: 100
    retry_attempts: 3
    retry_backoff: 2.0
  
  parallel:
    enabled: true
    max_workers: 3
    use_worktrees: true
    worktree_base_dir: "../epic-worktrees"
  
  logging:
    level: INFO
    format: json
    file: "logs/ccpm.log"
```

```bash
# .env.example
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
ENABLE_CCPM_SYNC=false
CCPM_MAX_PARALLEL=3
CCPM_WORKTREE_DIR=../epic-worktrees
```

---

## References

- [CCPM Original Repository](https://github.com/automazeio/ccpm)
- [Phase 09 Original Plan](./phase-09-ccpm-optimization.md)
- [OpenSpec Workflow](./ccpm-openspec-workflow.md)
- [AGENTS.md](../../AGENTS.md)
- [Section Refactor Mapping](../SECTION_REFACTOR_MAPPING.md)

---

**Document Status:** Ready for Review  
**Next Action:** Team review and approval before implementation  
**Owner:** Pipeline Team  
**Reviewers:** Architecture Team, PM Team
