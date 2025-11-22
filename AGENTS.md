# Repository Guidelines – Codex / Agentic CLI Instructions

> **Note**: This file serves dual purposes:
> 1. **For Codex CLI**: Primary instruction file (hierarchical merge: global → repo → subdir)
> 2. **For All Tools**: Repository guidelines and coding standards

---

## 0. Role and Context (Codex-Specific)

You are an **agentic CLI tool** (Codex CLI) operating in a UET-governed development pipeline.

You are aware of:
- **Phases, Workstreams, and Tasks** as the planning layer
- **ExecutionRequests** as the unit of work you receive
- **Patch Management** as the only allowed way to change code
- **Execution Kernel** and **Tool Execution** specs governing scheduling, parallelism, and tool usage

You should coordinate planning and implementation steps, and emit outputs that other tools (Claude Code, Copilot, CI, etc.) can consume.

**See also**: 
- `CLAUDE.md` – Instructions for Claude Code
- `.github/copilot-instructions.md` – Instructions for GitHub Copilot

---

## AI Codebase Structure (ACS) Artifacts

**For AI Tools**: This repository implements the AI Codebase Structure Specification for improved AI tool effectiveness.

### Key ACS Artifacts
- **CODEBASE_INDEX.yaml**: Complete module index with dependencies, layers, and import patterns
- **QUALITY_GATE.yaml**: Quality gates and validation commands
- **ai_policies.yaml**: Machine-readable edit policies (safe/review/read-only zones) and invariants
- **.aiignore**: Unified AI tool ignore rules (consolidates .gitignore + .aiderignore)
- **.meta/AI_GUIDANCE.md**: Human-readable AI agent onboarding guide
- **.meta/ai_context/**: Pre-computed AI context summaries
  - `repo_summary.json` - Machine-readable repository metadata
  - `code_graph.json` - Module dependency graph (validated acyclic)

### Usage for AI Agents
1. **Start here**: Read `.meta/AI_GUIDANCE.md` for quick onboarding
2. **Module discovery**: Consult `CODEBASE_INDEX.yaml` for module IDs and dependencies
3. **Edit policies**: Check `ai_policies.yaml` before modifying files
4. **Validation**: Run `python scripts/validate_acs_conformance.py` to verify changes
5. **Regenerate context**: Run `python scripts/generate_repo_summary.py` and `python scripts/generate_code_graph.py` after structure changes

### Edit Zone Quick Reference
- ✅ **Safe to modify**: `core/**`, `engine/**`, `error/**`, `tests/**`, `scripts/**`
- ⚠️ **Review required**: `schema/**`, `config/**`, canonical docs (CODEBASE_INDEX, etc.)
- ❌ **Read-only**: `legacy/**`, ADRs, runtime directories (`.worktrees/`, etc.)

See `ai_policies.yaml` for complete zone definitions and invariants.

---

## Project structure & module organization (Post-Phase E Refactor)

### Core Sections
- **core/state/**: Database, CRUD operations, bundles, worktree management
  - Database location: `.worktrees/pipeline_state.db` (configurable via `PIPELINE_DB_PATH`)
- **core/engine/**: Workstream orchestrator, scheduler, executor, tools adapter, circuit breakers, recovery
- **core/planning/**: Workstream planner and archive utilities
- **core/**: OpenSpec parser/converter, spec indexing, agent coordinator

### Execution Engines
- **engine/**: Job-based standalone execution engine (hybrid GUI/Terminal/TUI architecture)
  - Separate from core/engine/ - uses job JSON pattern instead of workstream steps
  - See `engine/README.md` for architecture details
  - Adapters: aider, codex, git, tests
  - Queue management and worker pools

### Error Detection
- **error/engine/**: Error engine, state machine, pipeline service, CLI, plugin manager
- **error/plugins/**: Detection plugins (Python, JS, linting, security, utilities)
- **error/shared/utils/**: Hashing, time utilities, JSONL manager

### Domain-Specific Sections
- **aim/**: AIM+ unified AI environment manager (registry, secrets, health, scanner, installer)
  - Replaces legacy AI_MANGER (archived 2025-11-22)
  - CLI: `python -m aim`
- **pm/**: Project management and CCPM integrations
- **specifications/**: Unified spec management (content, tools, changes, bridge)
- **aider/**: Aider integration and prompt templates
- **openspec/**: Source OpenSpec proposals and bridge docs before conversion into workstreams or specs

### UI and prompt systems
- **gui/**: Hybrid GUI/terminal/TUI design docs for the job runner, panels, and layout prototypes
- **Prompt/**: Prompt-engineering references and reusable prompt templates for agent operations

### Repository Infrastructure
- **docs/**: Canonical phase plans, architecture notes, ADRs, permanent reference documentation
- **devdocs/**: Developer session logs, phase tracking, execution reports, process analysis (ephemeral)
- **plans/**: Phase checklists, milestones, and templates
- **meta/**: Phase development docs and planning documents
- **scripts/**: Automation (bootstrap, validate, generate, run). Prefer PowerShell (.ps1) or Python.
- **tools/**: Internal Python utilities (hardcoded_path_indexer, etc.)
- **workstreams/**: Example single/multi workstream JSON bundles
- **schema/**: JSON/YAML/SQL schemas that define workstream and sidecar metadata contracts
- **config/**: Adapter/tool profiles, decomposition rules, and circuit-breaker config
- **tests/**: Unit/integration tests for scripts/tools/pipeline
- **assets/**: Diagrams and images referenced by docs
- **sandbox_repos/**: Self-contained toy repos for integration tests (excluded from pytest by default)
- **infra/**: CI/CD configuration (see `infra/ci`) shared across engines and tooling

### Legacy (Deprecated - Do Not Use in New Code)
- **src/pipeline/**: Backward-compatibility shims -> Use `core.*` instead
- **MOD_ERROR_PIPELINE/**: Legacy error shims -> Use `error.*` instead
- **legacy/AI_MANGER_archived_2025-11-22/**: Archived PowerShell environment manager (migrated to `aim/`)
- **legacy/AUX_mcp-data_archived_2025-11-22/**: Archived MCP setup files (superseded by `.worktrees/pipeline_state.db`)

See [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md) for complete old->new path mappings.

## Build, test, and development commands
- Environment setup (recommended):
  - `python -m venv .venv && . ./.venv/Scripts/Activate.ps1` (Windows PowerShell)
  - `pip install -r requirements.txt`
- Script runner conventions:
  - `pwsh ./scripts/<name>.ps1` (Windows-first); companion `.sh` exists for WSL where present.
  - `python ./scripts/<name>.py` for Python scripts.
- Common tasks:
  - Bootstrap/checks: `pwsh ./scripts/bootstrap.ps1`, `pwsh ./scripts/test.ps1`
  - Validate workstreams: `python ./scripts/validate_workstreams.py`
  - Validate authoring: `python ./scripts/validate_workstreams_authoring.py`
  - Generate indices/mapping: `python ./scripts/generate_spec_index.py`, `python ./scripts/generate_spec_mapping.py`
  - Run a workstream: `python ./scripts/run_workstream.py`
  - Error pipeline: `python ./scripts/run_error_engine.py`
- Tests:
  - `pytest -q` (root config in `pytest.ini`); integration tests under `tests/`.
  - CI-friendly run: `pwsh ./scripts/test.ps1`
- Optional: Markdown lint (if configured): `npm run lint:md`

## Coding style & naming conventions
- Markdown: one H1 per file; sentence-case headings; wrap at ~100 chars.
- YAML/JSON: 2-space indent; kebab-case keys (e.g., `phase-name`).
- Python: 4-space indent; Black/PEP8; snake_case for files/modules; prefer type hints in new code.
- Files: descriptive, scope-first names (e.g., `phase-02-design.md`).
- Scripts: prefer `.ps1` for Windows-first flows; provide `.sh` parity where feasible (no WSL-only assumptions in shared logic).

## Section-specific conventions

### Core State (`core/state/`)
- Database initialization and connection management
- CRUD operations follow pattern: `create_*`, `get_*`, `update_*`, `delete_*`
- Bundle loading and validation
- Worktree lifecycle management
- **Example**: `from core.state.db import init_db`

### Core Engine (`core/engine/`)
- Orchestration and execution logic
- Step retry and circuit breaker patterns
- Tool profile adapters with timeout handling
- Recovery strategies for failed steps
- **Example**: `from core.engine.orchestrator import Orchestrator`

### Core Planning (`core/planning/`)
- Workstream generation and planning utilities
- Archive operations for completed work
- **Example**: `from core.planning.planner import generate_workstream`

### Error Detection (`error/engine/`, `error/plugins/`)
- Error state machine transitions
- Plugin discovery via manifest.json
- Each plugin implements `parse()` and optionally `fix()`
- Incremental detection using file hash caching
- **Example**: `from error.engine.error_engine import ErrorEngine`
- **Plugin example**: `from error.plugins.python_ruff.plugin import parse`

### Domain Sections (`aim/`, `pm/`, `specifications/`)
- Keep section-specific logic isolated
- Use clear bridge/adapter patterns for external integrations
- **AIM example**: `from aim.bridge import get_tool_info`
- **Spec example**: `from specifications.tools.indexer.indexer import generate_index`

### Specifications (`specifications/`)
- Unified specification management system
- **content/**: Specification documents organized by domain
- **tools/**: Processing utilities (indexer, resolver, guard, patcher, renderer)
- **changes/**: Active OpenSpec change proposals
- **bridge/**: OpenSpec -> Workstream integration
- **Example**: `from specifications.tools.resolver.resolver import resolve_spec_uri`

## Testing guidelines
- Use `pytest`; place tests under `tests/` (unit, pipeline, integration subfolders as needed).
- Mark tests that rely on external CLIs or network, and keep them skipped/off by default; avoid network/external state.
- Sandbox repos under `sandbox_repos/` are excluded by default (`pytest.ini`), and are only for targeted integration tests.
- For docs/templates, prefer linters (Markdownlint, yamllint) and link checkers.

## Commit & pull request guidelines
- Conventional Commits: `feat: add evaluation checklist`, `docs: refine phase 3 goals`, `chore: update script runner`.
- Keep commits atomic; one logical change per commit.
- PRs include: clear description, linked issues, before/after context or screenshots, and checklist of affected phases.
- When updating schemas/config under `schema/` or `config/`, note versioning/compat changes and regenerate indices if applicable.

## Security & configuration tips
- Never commit secrets. Use `.env.local`; provide `.env.example` when adding new env vars.
- Redact sensitive data in docs/artifacts. Store large files outside the repo.
- Treat `specifications/` and `schema/` as source-of-truth contracts; validate changes via provided validators before merging.

## Agent-specific instructions
- Follow AGENTS.md scope rules; keep patches minimal and focused.
- Prefer small, readable diffs and repository-relative paths.
- Do not refactor unrelated areas; update docs/tests when changing scripts.
- When adding scripts under `scripts/`, prefer Python for logic and `.ps1`/`.sh` as thin wrappers if needed.
- Coordinate changes to `tools/` with tests under `tests/` (pipeline/plugins sections), keeping behavior reproducible/deterministic.

### When to use which section
- **Adding state/database logic** -> `core/state/`
- **Adding orchestration/execution logic** -> `core/engine/`
- **Adding planning/archive features** -> `core/planning/`
- **Adding error detection logic** -> `error/engine/`
- **Adding a new detection plugin** -> `error/plugins/<plugin-name>/`
- **Adding AIM integration** -> `aim/`
- **Adding PM/CCPM features** -> `pm/`
- **Adding spec content** -> `specifications/content/`
- **Adding spec tools** -> `specifications/tools/`
- **Adding Aider integration** -> `aider/`

### Import path rules (CRITICAL - CI enforced)
✅ **Use section-based imports**:
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse
from specifications.tools.indexer.indexer import generate_index
from specifications.tools.resolver.resolver import resolve_spec_uri
from aim.bridge import get_tool_info
```

❌ **Do NOT use deprecated imports** (will fail CI):
```python
from src.pipeline.db import init_db                    # ❌ FAILS CI
from src.pipeline.orchestrator import Orchestrator     # ❌ FAILS CI
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine  # ❌ FAILS CI
from legacy.* import anything                          # ❌ NEVER import legacy
from spec.tools.spec_indexer import generate_index     # ❌ DEPRECATED - use specifications.tools.indexer
from openspec.specs import load_spec                   # ❌ DEPRECATED - use specifications.content
```

**Validation**: `python scripts/paths_index_cli.py gate --db refactor_paths.db --regex "src/pipeline|MOD_ERROR_PIPELINE"`

See [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) for CI enforcement details.

## Agent workflow (Codex CLI)
- Scope: this file applies to the entire repository unless a more deeply nested `AGENTS.md` overrides it.
- Preambles: before running groups of commands, send a short 1-2 sentence note describing what you'll do next. Avoid trivial preambles for single file reads.
- Plans: use the `update_plan` tool for multi-step or ambiguous tasks; keep steps short (5-7 words) with exactly one `in_progress` item at a time.
- Shell: prefer `rg`/`rg --files` for searches; read files in chunks <=250 lines; avoid long outputs that will truncate.
- Patches: use `apply_patch` for edits; keep diffs focused; align with existing style; avoid unrelated refactors.
- Validation: when tests exist, run targeted tests for changed areas first; do not fix unrelated failures.
- Final messages: keep concise, include next steps if useful, and reference files with clickable repo-relative paths like `src/app.py:42`.

## Repository-specific notes
- Windows-first: PowerShell is preferred; `.sh` scripts are provided for parity (WSL). Keep cross-platform logic in Python where possible.
- Specs/workstreams: keep `workstreams/` examples in sync with `schema/` and `openspec/`. Run validators after edits.
- Indices/mapping: regenerate via `generate_spec_index.py` and `generate_spec_mapping.py` when specs or schema change.
- Determinism: tests under `tests/pipeline/` check deterministic execution. Avoid nondeterministic I/O, timestamps without control, or network calls in core code.

