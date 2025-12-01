---
doc_id: DOC-ERROR-AGENTS-035
---

# Repository Guidelines

## Project Structure & Module Organization
- Core: `core/state/` (DB, CRUD, worktree), `core/engine/` (orchestration, executors, circuit breakers), `core/planning/` (planner, archive), `core/` (OpenSpec, indexing, coordinator).
- Error: `error/engine/` (error state machine, pipeline), `error/plugins/` (linters, security; each has `parse()` and optional `fix()`), `error/shared/utils/` (hash/time/jsonl).
- Domain: `aim/`, `pm/`, `spec/`, `aider/` (adapters/bridges).
- Infra: `docs/`, `plans/`, `meta/`, `scripts/`, `tools/`, `workstreams/`, `schema/`, `config/`, `tests/`, `openspec/`, `assets/`, `sandbox_repos/`.
- Deprecated: `src/pipeline/`, `MOD_ERROR_PIPELINE/` (do not use in new code).

## Build, Test, and Development Commands
- Setup: `python -m venv .venv && . ./.venv/Scripts/Activate.ps1 && pip install -r requirements.txt`.
- Bootstrap/checks: `pwsh ./scripts/bootstrap.ps1`, `pwsh ./scripts/test.ps1`.
- Validate: `python ./scripts/validate_workstreams.py`, `python ./scripts/validate_workstreams_authoring.py`.
- Spec indices: `python ./scripts/generate_spec_index.py`, `python ./scripts/generate_spec_mapping.py`.
- Run: `python ./scripts/run_workstream.py`, error engine `python ./scripts/run_error_engine.py`.
- Tests: `pytest -q` (CI-friendly via PowerShell script above).

## Coding Style & Naming Conventions
- Python: 4-space indent, Black/PEP8, snake_case modules; add type hints in new code.
- Markdown: one H1; sentence‑case headings; wrap ~100 chars.
- YAML/JSON: 2-space indent; kebab-case keys.
- Imports: use section paths only, e.g. `from core.engine.orchestrator import Orchestrator`; avoid legacy `src.pipeline.*` and `MOD_ERROR_PIPELINE.*`.

## Testing Guidelines
- Framework: `pytest`; place tests under `tests/` (unit/integration). Keep network/CLI-dependent tests skipped by default.
- Determinism required (no uncontrolled timestamps/network). `sandbox_repos/` excluded by default (see `pytest.ini`).

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat:`, `fix:`, `docs:`). Keep commits atomic.
- PRs: clear description, linked issues, before/after context or screenshots, and impacted phases checklist.
- When editing `schema/`, `config/`, or `openspec/`, note compat/versioning and regenerate indices/mapping.

## Security & Configuration Tips
- Do not commit secrets. Use `.env.local`; add `.env.example` when introducing new vars.
- Treat `openspec/` and `schema/` as contracts; run validators before merging.

## Agent‑Specific Instructions
- Prefer small, focused diffs; align with existing style.
- Windows-first: use `pwsh` wrappers; keep shared logic in Python.
- Tools/tests: coordinate changes under `tools/` with corresponding tests in `tests/`.
