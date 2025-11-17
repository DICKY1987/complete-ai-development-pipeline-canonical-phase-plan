# Complete AI Development Pipeline – Canonical Phase Plan

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
- `docs/` - architecture notes, ADRs, and specifications
- `plans/` - phase checklists and templates
- `scripts/` - automation (bootstrap, tests, exports)
- `tests/` - test files for scripts/templates
- `assets/` - diagrams and images

## Repository map
- `src/` – pipeline code: orchestrator, coordinator, tools adapter, prompts, DB helpers.
- `scripts/` – CLI entry points to validate, generate, run, and inspect.
- `schema/` – JSON/YAML/SQL schemas (e.g., `workstream.schema.json`).
- `workstreams/` – authored bundle JSONs consumed by the orchestrator.
- `config/` – runtime configuration (tool profiles, breakers, rules, AIM config).
- `tools/` - spec tooling: indexer, resolver, patcher, renderer, guard.
  - OpenSpec-first: see `docs/spec-tooling-consolidation.md`; renderer supports OpenSpec fallback.
- `docs/` – architecture, phase plans, contracts, spec docs.
- `plans/` – canonical phase plans and execution checklists (PH‑06 → PH‑13).
- `tests/` – unit/integration tests for bundles, pipeline, plugins.
- `templates/` – prompt templates (Aider EDIT/FIX, etc.).
- `openspec/` – OpenSpec project/specs used by the spec tools.
- `sandbox_repos/` – toy repos used by integration tests.
- `.worktrees/` – per‑workstream working folders created at runtime.
- `state/` and/or `.state/` – local state, reports, and/or DB files.
- `AIDER_PROMNT_HELP/`, `Coordination Mechanisms/`, `GUI_PIPELINE/`, `PHASE_DEV_DOCS/` – guidance and phase notes.

## Contributing
Read `AGENTS.md` for coding style, testing guidance, and PR conventions. Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).

## Phases
- `PH-00_Baseline & Project Skeleton (Codex Autonomous Phase Executor).md` - create the base structure and verify local execution.
