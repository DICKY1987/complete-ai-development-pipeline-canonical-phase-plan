# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two integrated components:

1. **QFT Orchestrator** (PowerShell) - A headless orchestration tool for managing concurrent Aider workstreams using git worktrees
2. **Modular TUI Framework** (Python) - A contract-first terminal user interface framework for building pluggable TUI modules

**Component relationship:**
- The PowerShell orchestrator is the primary tool for automating Aider-based development workflows
- The Python TUI framework provides a pluggable interface layer (currently includes basic PowerShell TUI adapter in `src/Adapters/Tui.ps1`)
- The two components are designed to work together but can operate independently
- Future integration: Python TUI modules could display orchestrator status, worktree views, etc.

## Architecture

### PowerShell Orchestrator Architecture

Follows **Hexagonal/Ports & Adapters** pattern:

```
src/
├── Application/          # Orchestration logic
│   └── Orchestrator.ps1  # Main entry point - Start-Orchestration
├── Domain/               # Core business logic
│   ├── PlanValidator.ps1      # Validates against JSON schema, checks cycles
│   └── DependencyManager.ps1  # Topological sort for execution order
└── Adapters/             # External integrations
    ├── AiderAdapter.ps1       # Launches headless Aider processes
    ├── GitAdapter.ps1         # Worktree operations (create/remove/status)
    └── Tui.ps1               # PowerShell TUI display
```

**Key concepts:**
- Plan files (YAML/JSON) define workstreams with dependencies
- GitAdapter creates isolated worktrees for each workstream
- Max 5 concurrent Aider processes (hard limit)
- Topological sort ensures dependency order
- Optional commit/push/PR automation via GitHub CLI

### Python TUI Framework Architecture

Follows **Modular/Plugin** architecture with Redux-like state pattern:

```
tui_project/
├── src/host/             # Core framework
│   ├── app.py           # Entry point & runtime loop
│   ├── discovery.py     # Module discovery & manifest loading
│   ├── manifest.py      # Schema validation
│   ├── registry.py      # Metadata merging (routes/commands/keybindings)
│   └── store.py         # Redux-like state management
├── src/modules/         # Pluggable modules
│   ├── ledger_view/     # Example: ledger table display
│   │   ├── tui.module.yaml
│   │   └── ledger_view/
│   │       ├── __init__.py
│   │       └── module.py
│   └── worktrees_ui/    # Example: worktree list display
│       ├── tui.module.yaml
│       └── worktrees_ui/
│           ├── __init__.py
│           └── module.py
├── schema/
│   └── tui.module.schema.json
└── tests/
```

**Key patterns:**
- Contract-first: Modules declare capabilities via `tui.module.yaml` manifests
- Redux pattern: Actions, reducers, unidirectional data flow
- Semantic versioning conflict resolution (highest version wins)
- Namespaced state: Each module owns its state namespace
- Host API provided to modules for `dispatch()` and state access
- Three-phase loading: Discovery (scan manifests) → Registry (merge metadata) → Runtime (call build_module)

## Common Commands

### PowerShell Orchestrator

**Run orchestration:**
```powershell
Import-Module .\src\Application\Orchestrator.ps1 -Force
Start-Orchestration -PlanPath .\plan\phase_plan.yaml -Concurrency 5 -Verbose
```

**Run with auto-commit/PR:**
```powershell
# Requires: gh auth login
Start-Orchestration `
  -PlanPath .\plan\phase_plan.yaml `
  -DependenciesPath .\plan\dependencies.yaml `
  -Concurrency 2 `
  -CreatePullRequest `
  -BaseBranch main `
  -Verbose
```

**Generate absolute-path plan variant (for sharing prompts):**
```powershell
.\scripts\Create-AbsolutePlanVariant.ps1
```

**Run tests:**
```powershell
Invoke-Pester .\tests\Orchestrator.Tests.ps1 -Verbose
```

**Run specific test:**
```powershell
Invoke-Pester .\tests\Orchestrator.Tests.ps1 -TestName "Should validate plan file"
```

### Python TUI Framework

**Run TUI host:**
```bash
cd tui_project
python -m host.app src/modules
```

**Run specific test:**
```bash
cd tui_project
python -m pytest tests/test_manifest_validation.py -v
```

**Run all tests:**
```bash
cd tui_project
python -m pytest tests/
```

## Plan File Structure

Plan files define workstreams for the orchestrator. Use YAML (recommended) or JSON.

**Minimal YAML example:**
```yaml
repoPath: C:\Projects\YourRepo
workstreams:
  - id: ws-001
    name: "Refactor utilities"
    worktree: "ws-001-refactor-utilities"
    promptFile: "prompts/refactor_utilities.md"

  - id: ws-002
    name: "Add tests"
    worktree: "ws-002-add-tests"
    promptFile: "prompts/add_tests.md"
    dependsOn: ["ws-001"]  # Runs after ws-001
```

**Key rules:**
- `id`: Must be unique across all workstreams
- `worktree`: Branch name for git worktree (avoid special chars)
- `promptFile`: Path to markdown file with Aider instructions (relative to repo root)
- `dependsOn`: Array of workstream IDs (validates no cycles)
- Prompt files should be inside the repo so they're available in worktrees
- Worktree directories are created at `<repo>/../<worktree-name>` (sibling to main repo)

## Schema Validation

All schemas use JSON Schema for validation:

- `schemas/PlanFile.schema.json` - Validates workstream plans
- `schemas/DependencyFile.schema.json` - Validates dependency overrides
- `tui_project/schema/tui.module.schema.json` - Validates TUI module manifests

PlanValidator checks:
1. Schema conformance (against PlanFile.schema.json)
2. No duplicate workstream IDs
3. All `dependsOn` references exist
4. No dependency cycles (via DependencyManager)

## Module Boundaries

### PowerShell Orchestrator

- **Application layer**: Orchestrates workflow, manages concurrency
- **Domain layer**: Pure business logic (validation, dependency resolution) - no external dependencies
- **Adapters layer**: External integrations (Aider, Git, GitHub CLI)

**Import pattern:**
```powershell
# Modules import dependencies explicitly
Import-Module "$PSScriptRoot/../Adapters/AiderAdapter.ps1" -Force
Import-Module "$PSScriptRoot/../Adapters/GitAdapter.ps1" -Force
```

### Python TUI Framework

**Module structure:**
```
src/modules/<module_name>/
├── tui.module.yaml      # Manifest (routes, commands, keybindings)
└── <module_name>/       # Package directory (same name as parent)
    ├── __init__.py      # Must exist (can be empty)
    └── module.py        # Exports build_module(host_api)
```

**Module contract:**
```python
def build_module(host_api):
    """
    Called twice: once with MetaHostAPI during discovery, once with
    RuntimeHostAPI during normal operation.

    Returns {
        "reducers": {<namespace>: reducer_fn},
        "initial_state": {<namespace>: initial_state_dict},
        "commands": {<cmd_name>: callback_fn},
        "views": {<route_name>: view_fn}
    }
    """
```

**Important:** The nested package directory must have the same name as the parent directory. For example: `src/modules/ledger_view/ledger_view/module.py`

## Concurrency & Dependencies

**Orchestrator behavior:**
1. Validates plan file and dependency graph
2. Creates worktrees for all workstreams
3. Uses topological sort (Kahn's algorithm) to determine execution order
4. Launches up to 5 concurrent Aider processes (configurable via `-Concurrency` parameter)
5. Respects `dependsOn` constraints (dependent workstreams wait for predecessors)
6. Background PowerShell jobs for parallel execution
7. Cleans up worktrees after completion (unless errors occur)
8. Each Aider process runs in its own worktree with the specified prompt file

**Hard limit:** Maximum 5 concurrent Aider processes (default, prevents resource exhaustion)

**Execution model:**
- Workstreams without dependencies start immediately (up to concurrency limit)
- When a workstream completes, dependent workstreams become eligible
- Jobs are polled periodically to check completion status
- Failed workstreams prevent their dependents from running

## TUI Module Development

**Creating a new module:**

1. Create `src/modules/<name>/tui.module.yaml`:
```yaml
module:
  name: my_module
  version: 1.0.0
routes:
  - name: my_route
    title: "My Route"
    namespace: my_module
commands:
  - name: do_something
    description: "Does something"
keybindings:
  - key: "s"
    command: do_something
```

2. Create `src/modules/<name>/<name>/module.py`:
```python
def build_module(host_api):
    def my_reducer(state, action):
        # Handle actions
        return state

    def my_view(state):
        # Render view
        return "View content"

    def my_command(state):
        # Handle command
        host_api.dispatch({"type": "MY_ACTION"})

    return {
        "reducers": {"my_module": my_reducer},
        "initial_state": {"my_module": {}},
        "commands": {"do_something": my_command},
        "views": {"my_route": my_view}
    }
```

**Conflict resolution:**
- Routes/commands: Highest semantic version wins
- Keybindings: Conflicts cause hard failure (must be unique)

## Feature Flag

The orchestrator is controlled by feature flag `enable_qft_orchestrator` (default: off) per CHANGE_SPEC.yaml CHG-QFT-2025-001.

Rollback trigger: Error rate >5%

## GitHub CLI Integration

Optional automation for commit/push/PR requires:
- GitHub CLI installed: `gh --version`
- Authenticated: `gh auth login`
- Remote `origin` points to GitHub
- Base branch exists (main/master/etc)

Functions in `GitAdapter.ps1`:
- `Get-DefaultBranch`: Auto-detects base branch from origin/HEAD
- `Commit-And-Push`: Stages, commits, pushes worktree changes
- `Open-PullRequest`: Creates PR via `gh pr create`

## Development Notes

**PowerShell orchestrator:**
- Use `Write-Verbose` for detailed logging (requires `-Verbose` flag)
- Background jobs run in isolated sessions (must import modules)
- Worktrees create branches from current HEAD or origin/main
- Logs stored in `logs/<workstream-id>.log`
- Git operations use `Push-Location`/`Pop-Location` to ensure correct working directory

**Python TUI:**
- Discovery phase: Validates manifests, imports modules
- Registry phase: Merges metadata, resolves conflicts via semantic versioning
- Runtime phase: Calls `build_module()` with real host API
- State is immutable (reducers return new state)
- Press `q` to exit the TUI
- Module discovery scans for `tui.module.yaml` files in subdirectories
- Keybinding conflicts cause hard failure (must be globally unique)

**Testing:**
- PowerShell: Pester framework (`Invoke-Pester`)
- Python: pytest framework (`python -m pytest`)
- Tests use snapshot testing for view rendering
- Registry tests verify semantic versioning resolution

**Scripts:**
- `Create-AbsolutePlanVariant.ps1`: Converts relative prompt paths to absolute paths and publishes to GitHub Gist (requires `gh` CLI)
