# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Rules (From .claude/rules/)

### DateTime Standard
**HIGHEST PRIORITY**: Always use real system datetime, never placeholders or estimates.

```bash
# Get current datetime in ISO 8601 format
date -u +"%Y-%m-%dT%H:%M:%SZ"

# Windows PowerShell
Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
```

- **Required format**: `YYYY-MM-DDTHH:MM:SSZ` (UTC with Z suffix)
- **Never use**: Placeholders like `[Current ISO date/time]` or estimates
- **Always preserve**: Original `created` dates, only update `updated` fields
- **See**: `.claude/rules/datetime.md` for full specification

### Path Standards
**Protect privacy and ensure portability**:

```markdown
# ✅ CORRECT - Relative paths
- `internal/auth/server.go`
- `../project-name/src/components/Button.tsx`
- `.claude/commands/pm/sync.md`

# ❌ WRONG - Absolute paths expose usernames
- `/Users/username/project/internal/auth/server.go`
- `C:\Users\username\project\cmd\server\main.go`
```

- **Always use**: Relative paths from project root
- **Never expose**: User directories or absolute local paths
- **Cross-project refs**: Use `../project-name/` format
- **See**: `.claude/rules/path-standards.md` for full specification

### GitHub Operations
**Repository protection required**:

```bash
# MUST CHECK before ANY GitHub write operation
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$remote_url" == *"automazeio/ccpm"* ]]; then
  echo "❌ ERROR: Cannot modify template repository!"
  echo "Fork or create your own repo first"
  exit 1
fi
```

- **Required for**: Issue creation/editing, PR creation, comments
- **Trust gh CLI**: Don't pre-check auth, handle failures gracefully
- **Error format**: `❌ {What failed}: {Exact solution}`
- **See**: `.claude/rules/github-operations.md` for full specification

### Standard Patterns
**Core principles for all operations**:

1. **Fail Fast** - Check critical prerequisites, then proceed
2. **Trust the System** - Don't over-validate things that rarely fail
3. **Clear Errors** - Show exactly what failed and how to fix it
4. **Minimal Output** - Show what matters, skip decoration

```markdown
# ✅ GOOD - Concise and actionable
✅ Done: 3 files created
Failed: auth.test.js (syntax error - line 42)

# ❌ BAD - Too verbose
🎯 Starting operation...
📋 Validating prerequisites...
✅ Step 1 complete
✅ Step 2 complete
```

- **See**: `.claude/rules/standard-patterns.md` for full specification

### Test Execution
**Always use test-runner agent**:

- **No mocking** - Use real services for accurate results
- **Verbose output** - Capture everything for debugging
- **Check test structure first** - Before assuming code bugs
- **Cleanup after**: Kill test processes properly
- **See**: `.claude/rules/test-execution.md` for full specification

### Worktree Operations
**For parallel development and epic workflows**:

```bash
# Create worktree from clean main
git checkout main && git pull origin main
git worktree add ../epic-{name} -b epic/{name}

# Work in worktree
cd ../epic-{name}
git add {files}
git commit -m "Issue #{number}: {description}"
```

- **One worktree per epic** - Not per issue
- **Clean before create** - Always start from updated main
- **Commit frequently** - Small commits merge easier
- **See**: `.claude/rules/worktree-operations.md` for full specification

### Agent Coordination
**For parallel agent workflows in same worktree**:

1. **File-level parallelism** - Different files = no conflicts
2. **Explicit coordination** - Same file = coordinate explicitly
3. **Fail fast** - Surface conflicts immediately
4. **Human resolution** - Never auto-merge conflicts

```bash
# Before modifying shared file
git status {file}
if [[ $(git status --porcelain {file}) ]]; then
  echo "Waiting for {file} to be available..."
fi
```

- **See**: `.claude/rules/agent-coordination.md` for full specification

## Overview

This is a **multi-phase AI development pipeline** that orchestrates workstreams through deterministic execution steps (EDIT → STATIC → RUNTIME). The architecture separates:
- **Orchestration**: Multi-agent coordinator with dependency resolution, SQLite persistence
- **Workstreams**: JSON bundles defining file scope, tasks, and dependencies
- **Plugin System**: 17+ Python plugins for linting, fixing, type-checking, security scanning
- **Error Pipeline**: State machine for error detection, deduplication, and AI-assisted fixes
- **AIM Integration**: Tool registry with capability-based routing and PowerShell adapters
- **Spec Tooling**: OpenSpec validation, indexing, rendering, patching

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
. ./.venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests (uses pytest.ini config)
python -m pytest -q

# Run specific test categories
python -m pytest tests/pipeline/        # Core pipeline tests
python -m pytest tests/plugins/         # Plugin tests
python -m pytest tests/integration/     # Integration tests

# Run with markers
python -m pytest -m aider              # Tests requiring aider CLI

# Run CI-friendly test suite
pwsh ./scripts/test.ps1                # Runs pytest + optional markdownlint
```

### Database Operations
```bash
# Initialize database (idempotent)
python scripts/init_db.py

# Inspect database state
python scripts/db_inspect.py

# Database location: state/pipeline_state.db
# Override with: PIPELINE_DB_PATH=<path>
```

### Workstream Operations
```bash
# Validate all workstream bundles
python scripts/validate_workstreams.py

# Validate with authoring-friendly errors
python scripts/validate_workstreams_authoring.py --json

# Run a single workstream
python scripts/run_workstream.py --ws-id <id> [--run-id <run>] [--dry-run]

# Generate workstreams (stub)
python scripts/generate_workstreams.py
```

### OpenSpec Bridge
```bash
# List available OpenSpec changes
python scripts/spec_to_workstream.py --list
pwsh ./scripts/spec_to_workstream.ps1 -List

# Interactive conversion (recommended)
python scripts/spec_to_workstream.py --interactive
pwsh ./scripts/spec_to_workstream.ps1 -Interactive

# Convert specific change to workstream
python scripts/spec_to_workstream.py --change-id <id>
pwsh ./scripts/spec_to_workstream.ps1 -ChangeId <id>

# Dry run (preview without saving)
python scripts/spec_to_workstream.py --change-id <id> --dry-run

# See docs/QUICKSTART_OPENSPEC.md for workflow
```

### Spec Tooling
```bash
# Generate spec index
python scripts/generate_spec_index.py

# Generate spec mapping
python scripts/generate_spec_mapping.py

# Run these after modifying openspec/ or schema/
```

### AIM Integration
```bash
# Check AIM tool status and capability routing
python scripts/aim_status.py

# Query audit logs
python scripts/aim_audit_query.py [--tool <name>] [--capability <cap>]
```

### Error Pipeline
```bash
# Run error detection engine
python scripts/run_error_engine.py
```

### Bootstrap & Setup
```bash
# Bootstrap directories and basic checks
pwsh ./scripts/bootstrap.ps1
```

## Architecture

### Core Components

#### Pipeline (`src/pipeline/`)
- **orchestrator.py**: Single-workstream execution loop (EDIT → STATIC → RUNTIME)
- **scheduler.py**: Multi-workstream dependency resolution and scheduling
- **executor.py**: Step execution with retry logic and circuit breakers
- **bundles.py**: Workstream JSON loader, validator, dependency DAG builder
- **db.py**: SQLite connection management and CRUD facade
- **crud_operations.py**: Database operations for runs, workstreams, steps, errors, events
- **tools.py**: Tool profile adapter with templating and timeout handling
- **prompts.py**: Jinja2-based prompt rendering for Aider EDIT/FIX commands
- **worktree.py**: Git worktree creation and file scope validation
- **circuit_breakers.py**: Failure threshold logic to prevent runaway retries
- **recovery.py**: Error recovery strategies
- **planner.py**: Stub for automated workstream generation

#### Error Pipeline (`src/pipeline/`)
- **error_state_machine.py**: State transitions for error lifecycle (NEW → ANALYZED → FIXED → VERIFIED)
- **error_context.py**: Error context tracking with history and metadata
- **error_pipeline_cli.py**: CLI for error pipeline operations
- **db_sqlite.py**: SQLite backend for error contexts

#### AIM Bridge (`src/pipeline/`)
- **aim_bridge.py**: Python-to-PowerShell bridge with 8 core functions
  - Registry loading, tool detection, version checking
  - Capability-based routing with fallback chains
  - Audit logging to `.AIM_ai-tools-registry/AIM_audit/`

#### Plugin System (`src/plugins/`)
17+ plugins organized by category:
- **Python**: ruff, black, isort, pylint, mypy, pyright, bandit, safety
- **PowerShell**: PSScriptAnalyzer
- **JavaScript**: prettier, eslint
- **Markup/Data**: yamllint, mdformat, markdownlint, jq
- **Cross-cutting**: codespell, semgrep, gitleaks
- **Echo**: Test/stub plugin

Each plugin has:
- `manifest.json`: Metadata (ID, name, version, type, tool, capabilities)
- `plugin.py`: `parse()` and optional `fix()` implementations
- `__init__.py`: Package marker

#### Spec Tooling (`tools/`)
- **spec_indexer/**: Generates cross-reference indices
- **spec_resolver/**: Resolves references across specs
- **spec_renderer/**: Renders specs to HTML/Markdown
- **spec_patcher/**: Applies patches to specs
- **spec_guard/**: Validates spec integrity

### Data Flow

1. **Authoring**: Create workstream bundles in `workstreams/` following `schema/workstream.schema.json`
2. **Validation**: `scripts/validate_workstreams.py` checks schema, dependencies, cycles, file overlaps
3. **Orchestration**: `scripts/run_workstream.py` executes steps via orchestrator
4. **Worktrees**: Created in `.worktrees/<ws-id>` for isolation
5. **State**: Recorded in SQLite (`state/pipeline_state.db`)
6. **Reports**: Error reports in `.state/error_pipeline/<run>/<ws>/error_reports/`

### State Machine

#### Run States
- `pending` → `running` → `completed` / `failed`

#### Workstream States
- `pending` → `editing` → `static_check` → `runtime_tests` → `done` / `failed`

#### Error States
- `NEW` → `ANALYZING` → `ANALYZED` → `FIXING` → `FIXED` → `VERIFYING` → `VERIFIED` / `VERIFICATION_FAILED`

### Database Schema

Core tables in `schema/schema.sql`:
- **runs**: Orchestrated run lifecycle
- **workstreams**: Work units with dependencies
- **step_attempts**: Execution attempts with results
- **errors**: Deduplicated errors with signatures
- **events**: Append-only event log

## Configuration

### Tool Profiles (`config/tool_profiles.json`)
Declarative tool definitions with:
- `type`: `ai`, `static-check`, `test`, `utility`
- `command`: Template with vars like `{cwd}`, `{repo_root}`
- `args`: Array of argument templates
- `timeout_seconds`: Execution timeout
- Optional `aim_tool_id`, `aim_capabilities` for AIM routing

### AIM Config (`config/aim_config.yaml`)
- Feature flags (enable/disable AIM)
- Timeouts for adapter invocations
- Audit log retention settings

### Decomposition Rules (`config/decomposition_rules.yaml`)
Rules for automated workstream generation (v2.0 stub)

### Breaker Settings
Circuit breaker thresholds in `src/pipeline/circuit_breakers.py`

## Key Conventions

### Code Style
- **Python**: 4-space indent, Black/PEP8, snake_case, type hints preferred
- **JSON/YAML**: 2-space indent, kebab-case keys
- **Markdown**: One H1 per file, sentence-case headings, ~100 char wrap
- **PowerShell**: Strict mode, kebab-case for functions

### Git Workflow
- **Branches**: Feature branches off `main`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Worktrees**: Pipeline creates per-workstream worktrees in `.worktrees/`

### Testing Guidelines
- Place tests in `tests/` mirroring `src/` structure
- Use pytest markers for tests requiring external tools (`@pytest.mark.aider`)
- Sandbox repos in `sandbox_repos/` excluded by default (see `pytest.ini`)
- Keep tests deterministic (no network, no timestamps without control)

### File Organization
- **src/**: Pipeline logic, plugins, utilities
- **scripts/**: CLI entry points (Python + PowerShell wrappers)
- **schema/**: Single source of truth for validation
- **workstreams/**: Authored bundle inputs
- **config/**: Runtime configuration
- **tools/**: Spec tooling (separate from pipeline)
- **docs/**: Architecture, contracts, phase plans
- **templates/**: Jinja2 prompt templates
- **openspec/**: OpenSpec project/specs
- **.worktrees/**: Runtime per-workstream directories (gitignored)
- **state/**: SQLite DB and reports (gitignored)

## Important Patterns

### Workstream Authoring
1. Start with `templates/workstream_template.json`
2. Follow `docs/workstream_authoring_guide.md`
3. Validate with `scripts/validate_workstreams_authoring.py`
4. Required fields: `id`, `files`, `tasks`, `dependencies`

### Adding a New Plugin
1. Create directory: `src/plugins/<name>/`
2. Add `manifest.json` with metadata
3. Implement `plugin.py` with `parse(output: str) -> PluginResult`
4. Optional: `fix(files: list[str]) -> FixResult`
5. Add tests in `tests/plugins/test_<category>.py`

### Tool Profile Integration
1. Add entry to `config/tool_profiles.json`
2. Use `src/pipeline/tools.py::run_tool(profile_name, ...)`
3. Optional: Add AIM adapter in `.AIM_ai-tools-registry/AIM_adapters/`

### Prompt Engineering
1. Create Jinja2 template in `templates/prompts/*.txt.j2`
2. Use `src/pipeline/prompts.py::run_aider_edit()` or `run_aider_fix()`
3. Prompts rendered to `<worktree>/.aider/prompts/`

## Environment Variables

- `PIPELINE_DB_PATH`: Override default SQLite path (`state/pipeline_state.db`)
- `PIPELINE_WORKSTREAM_DIR`: Override workstream directory (`workstreams/`)
- `AIM_REGISTRY_PATH`: Override AIM registry location (`.AIM_ai-tools-registry/`)
- `ERROR_PIPELINE_DB`: Legacy error pipeline DB path

## Platform-Specific Notes

### Windows-First Design
- PowerShell (`pwsh`) is the primary shell
- `.ps1` scripts are authoritative
- `.sh` scripts provided for WSL parity where feasible
- Cross-platform logic should live in Python

### Path Handling
- Use `Path` from `pathlib` for cross-platform compatibility
- Repository root is assumed as CWD for scripts
- Worktrees use absolute paths

## Common Workflows

### Running a Complete Workflow
```bash
# 1. Initialize database
python scripts/init_db.py

# 2. Validate workstreams
python scripts/validate_workstreams.py

# 3. Run workstream
python scripts/run_workstream.py --ws-id my-workstream

# 4. Inspect results
python scripts/db_inspect.py
```

### Debugging a Plugin
```bash
# 1. Run plugin tests
python -m pytest tests/plugins/test_<category>.py -v

# 2. Test plugin directly
python -c "from src.plugins.<name>.plugin import parse; print(parse('<output>'))"

# 3. Check plugin discovery
python -c "from MOD_ERROR_PIPELINE.plugin_manager import discover_plugins; print(discover_plugins())"
```

### Regenerating Indices After Schema Changes
```bash
# 1. Update schema/workstream.schema.json or openspec/
# 2. Regenerate indices
python scripts/generate_spec_index.py
python scripts/generate_spec_mapping.py
# 3. Commit both schema and indices
```

## References

### Key Documentation
- `README.md`: Quick start and repository map
- `docs/ARCHITECTURE.md`: Detailed component architecture
- `AGENTS.md`: Coding style, testing, PR conventions
- `docs/workstream_authoring_guide.md`: Workstream bundle authoring
- `docs/aider_contract.md`: Aider integration contract (AIDER_CONTRACT_V1)
- `docs/AIM_INTEGRATION_CONTRACT.md`: AIM integration contract (AIM_INTEGRATION_V1)
- `docs/plugin-ecosystem-summary.md`: Plugin architecture and catalog
- `src/plugins/README.md`: Plugin reference and installation guide

### Contracts
All contracts are versioned and documented in `docs/`:
- Aider contract: `AIDER_CONTRACT_V1`
- AIM integration: `AIM_INTEGRATION_V1`
- Workstream schema: `schema/workstream.schema.json`

## Tips for Claude Code

### When Modifying Workstreams
1. Read `schema/workstream.schema.json` first
2. Validate after changes with `scripts/validate_workstreams_authoring.py`
3. Check for cycles and file overlaps in validation output
4. Test with `--dry-run` before running

### When Adding Tests
1. Check `pytest.ini` for test discovery patterns
2. Use fixtures from `tests/plugins/conftest.py` for plugin tests
3. Mark external dependencies with `@pytest.mark.aider` or custom markers
4. Keep tests under `tests/` mirroring `src/` structure

### When Updating Schema
1. Modify `schema/schema.sql` or `schema/workstream.schema.json`
2. Run `python scripts/init_db.py` to apply SQL changes (idempotent)
3. Regenerate indices with spec tooling scripts
4. Update affected workstream bundles and tests

### When Working with Plugins
1. Follow manifest schema strictly (see existing plugins)
2. Return `PluginResult` from `parse()` with `issues` list
3. Optional `fix()` should return `FixResult` with `success` and `modified_files`
4. Add installation instructions to `src/plugins/README.md`

### When Debugging Pipeline Issues
1. Check SQLite DB with `scripts/db_inspect.py`
2. Review event log in `events` table for traceability
3. Examine error reports in `.state/error_pipeline/<run>/<ws>/`
4. Enable `--dry-run` to simulate without external tool calls
