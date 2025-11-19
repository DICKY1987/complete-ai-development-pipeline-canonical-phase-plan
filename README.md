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

## Repository Layout
- `docs/` – architecture notes, ADRs, and specifications
- `plans/` – phase checklists and templates  
- `scripts/` – automation (bootstrap, tests, exports)
- `src/` – pipeline code: orchestrator, coordinator, tools adapter, prompts, DB helpers
- `schema/` – JSON/YAML/SQL schemas (e.g., `workstream.schema.json`)
- `workstreams/` – authored bundle JSONs consumed by the orchestrator
- `config/` – runtime configuration (tool profiles, breakers, rules, AIM config)
- `tools/` – spec tooling: indexer, resolver, patcher, renderer, guard
  - OpenSpec-first: see `docs/spec-tooling-consolidation.md`; renderer supports OpenSpec fallback
- `tests/` – unit/integration tests for bundles, pipeline, plugins
- `aider/templates/` – prompt templates (Aider EDIT/FIX, etc.)
- `openspec/` – OpenSpec project/specs used by the spec tools
- `sandbox_repos/` – toy repos used by integration tests
- `assets/` – diagrams and images
- `.worktrees/` – per‑workstream working folders created at runtime
- `state/` and/or `.state/` – local state, reports, and/or DB files
- `AIDER_PROMNT_HELP/`, `Coordination Mechanisms/`, `gui/`, `PHASE_DEV_DOCS/` – guidance and phase notes

## Contributing
Read `AGENTS.md` for coding style, testing guidance, and PR conventions. Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).

### CI Path Standards
All pull requests are automatically checked for deprecated import patterns. The CI enforces the new section-based structure after the Phase E refactor:
- ✅ Use `from core.state.*`, `from core.engine.*`, `from error.*`
- ❌ Avoid `from src.pipeline.*`, `from MOD_ERROR_PIPELINE.*`

See [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) for details on fixing violations.

## Phases
- `PH-00_Baseline & Project Skeleton (Codex Autonomous Phase Executor).md` - create the base structure and verify local execution.

