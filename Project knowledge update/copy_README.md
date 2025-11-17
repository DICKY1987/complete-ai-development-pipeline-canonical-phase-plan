# Complete AI Development Pipeline – Canonical Phase Plan

This repository hosts a structured, phase-based plan and lightweight tooling for building and operating an AI development pipeline. Start with PH-00 to establish the baseline skeleton, then proceed through subsequent phases.

## Quick Start
- Ensure PowerShell (`pwsh`) is available on Windows.
- Bootstrap directories and basic checks:
  - `pwsh ./scripts/bootstrap.ps1`
  - `pwsh ./scripts/test.ps1`

### OpenSpec quickstart
- Author a change: create `openspec/changes/<id>/{proposal.md,tasks.md}`
- Generate a normalized bundle YAML:
  - `python -m src.pipeline.openspec_parser --change-id <id> --generate-bundle`
- Convert to a pipeline workstream JSON:
  - `python scripts/generate_workstreams_from_openspec.py --change-id <id> --files-scope <path...>`
- Validate and run:
  - `python ./scripts/validate_workstreams.py`
  - `python ./scripts/run_workstream.py --ws-id ws-<id>`

See `docs/ccpm-openspec-workflow.md` for the end-to-end flow.

Optional: install the OpenSpec CLI for `openspec list/validate/archive` commands:
- `npm install -g @fission-ai/openspec`
- `openspec --version`

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
- `AIDER_PROMNT_HELP/`, `Coordination Mechanisms/`, `gui/`, `PHASE_DEV_DOCS/` – guidance and phase notes.

## Contributing
Read `AGENTS.md` for coding style, testing guidance, and PR conventions. Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).

## Phases
- `PH-00_Baseline & Project Skeleton (Codex Autonomous Phase Executor).md` - create the base structure and verify local execution.
