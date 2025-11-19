# Complete AI Development Pipeline – Canonical Phase Plan

![Path Standards](https://github.com/USERNAME/REPOSITORY/actions/workflows/path_standards.yml/badge.svg)

This repository hosts a structured, phase-based plan and lightweight tooling for building and operating an AI development pipeline. Start with PH-00 to establish the baseline skeleton, then proceed through subsequent phases.

## Quick Start
- Ensure PowerShell (`pwsh`) is available on Windows.
- Bootstrap directories and basic checks:
  - `pwsh ./scripts/bootstrap.ps1`
  - `pwsh ./scripts/test.ps1`

### OpenSpec Integration Quick Start

**5-Minute Workflow:**

1. **Create proposal** (use Claude Code):
   ```
   /openspec:proposal "Your feature description"
   ```

2. **Convert to workstream**:
   ```bash
   # Interactive mode (recommended)
   python scripts/spec_to_workstream.py --interactive

   # Or direct conversion
   python scripts/spec_to_workstream.py --change-id <id>
   ```

3. **Validate and run**:
   ```bash
   python scripts/validate_workstreams.py
   python scripts/run_workstream.py --ws-id ws-<id>
   ```

4. **Archive completed work**:
   ```
   /openspec:archive <change-id>
   ```

**Full Documentation:**
- Quick Start: `docs/QUICKSTART_OPENSPEC.md`
- Bridge Guide: `docs/openspec_bridge.md`
- OpenSpec CLI: `npm install -g @fission-ai/openspec`

## Migration Guide (Phase E Refactor)

If you're updating code written before the Phase E refactor, use these new import paths:

**State Management**:
```python
# Old: from src.pipeline.db import init_db
from core.state.db import init_db

# Old: from src.pipeline.crud_operations import get_workstream
from core.state.crud import get_workstream

# Old: from src.pipeline.bundles import load_bundle
from core.state.bundles import load_bundle
```

**Orchestration & Execution**:
```python
# Old: from src.pipeline.orchestrator import Orchestrator
from core.engine.orchestrator import Orchestrator

# Old: from src.pipeline.scheduler import Scheduler
from core.engine.scheduler import Scheduler

# Old: from src.pipeline.tools import invoke_tool
from core.engine.tools import invoke_tool
```

**Error Detection**:
```python
# Old: from MOD_ERROR_PIPELINE.error_engine import ErrorEngine
from error.engine.error_engine import ErrorEngine

# Old: from MOD_ERROR_PIPELINE.plugins.syntax_checker import SyntaxChecker
from error.plugins.syntax_checker import SyntaxChecker
```

See [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md) for the complete mapping.

## Repository Layout

### Core Sections (Post-Phase E Refactor)

**Core Pipeline**:
- `core/state/` – Database, CRUD operations, bundles, worktree management
- `core/engine/` – Orchestrator, scheduler, executor, tools adapter, circuit breakers, recovery
- `core/planning/` – Workstream planner and archive utilities
- `core/` – OpenSpec parser/converter, spec indexing, agent coordinator

**Error Detection & Analysis**:
- `error/engine/` – Error engine, state machine, pipeline service, CLI
- `error/plugins/` – Detection plugins (Python, JS, linting, security, etc.)
- `error/shared/utils/` – Hashing, time utilities, JSONL manager

**Domain-Specific Sections**:
- `aim/` – AIM integration bridge and tool registry
- `pm/` – Project management and CCPM integrations
- `spec/` – Spec validation and tooling
- `aider/` – Aider integration and prompt templates

**Repository Infrastructure**:
- `docs/` – Architecture notes, ADRs, specifications, refactor mapping
- `plans/` – Phase checklists and templates
- `meta/` – Phase development docs and planning documents
- `scripts/` – Automation (bootstrap, tests, workstream runners)
- `schema/` – JSON/YAML/SQL schemas for workstreams and sidecars
- `workstreams/` – Authored workstream bundle JSONs
- `config/` – Runtime configuration (tool profiles, breakers, decomposition rules)
- `tools/` – Internal utilities (spec indexer, resolver, hardcoded path indexer)
- `tests/` – Unit/integration/pipeline tests
- `openspec/` – OpenSpec project and specifications
- `sandbox_repos/` – Toy repos for integration testing
- `assets/` – Diagrams and images
- `.worktrees/` – Per-workstream working folders (created at runtime)
- `state/` and `.state/` – Local state, reports, and DB files

**Legacy Compatibility**:
- `src/pipeline/` – Backward-compatibility shims (⚠️ deprecated, use `core.*` instead)
- `MOD_ERROR_PIPELINE/` – Legacy shims (⚠️ deprecated, use `error.*` instead)

See [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md) for complete old→new path mappings.

## Contributing
Read `AGENTS.md` for coding style, testing guidance, and PR conventions. Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).

### CI Path Standards
All pull requests are automatically checked for deprecated import patterns. The CI enforces the new section-based structure after the Phase E refactor:
- ✅ Use `from core.state.*`, `from core.engine.*`, `from error.*`
- ❌ Avoid `from src.pipeline.*`, `from MOD_ERROR_PIPELINE.*`

See [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) for details on fixing violations.

## Phases
- `PH-00_Baseline & Project Skeleton (Codex Autonomous Phase Executor).md` - create the base structure and verify local execution.

