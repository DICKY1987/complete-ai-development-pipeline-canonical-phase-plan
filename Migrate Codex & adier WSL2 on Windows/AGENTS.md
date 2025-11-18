# Repository Guidelines

This AGENTS.md applies to the entire repository. The project is Windows‑first (PowerShell), with `.sh` parity where feasible. Keep cross‑platform logic in Python.

## Project Structure & Module Organization
- `docs/`: phase plans, architecture notes, ADRs, specs (`docs/spec/`).
- `plans/`: checklists, milestones, templates.
- `scripts/`: automation (bootstrap, validate, generate, run).
- `tools/`: internal Python utilities (e.g., spec_guard, spec_renderer, spec_indexer).
- `src/`: light Python helpers and plugin stubs used by tools/tests.
- `openspec/`: OpenSpec project and specs.
- `workstreams/`: example single/multi workstream bundles.
- `schema/`: JSON/YAML/SQL contracts for workstreams and sidecars.
- `config/`: adapter/tool profiles, decomposition rules, circuit‑breaker config.
- `tests/`: unit/integration tests; root `pytest.ini`.
- `assets/`: diagrams and images.
- `sandbox_repos/`: toy repos for integration tests (excluded by default).

## Build, Test, and Development Commands
- Setup (Windows): `python -m venv .venv && . ./.venv/Scripts/Activate.ps1 && pip install -r requirements.txt`
- Run scripts: `pwsh ./scripts/<name>.ps1` or `python ./scripts/<name>.py`
- Bootstrap/checks: `pwsh ./scripts/bootstrap.ps1`, `pwsh ./scripts/test.ps1`
- Validate: `python ./scripts/validate_workstreams.py`, `python ./scripts/validate_workstreams_authoring.py`
- Generate indices/mapping: `python ./scripts/generate_spec_index.py`, `python ./scripts/generate_spec_mapping.py`
- Run pipeline: `python ./scripts/run_workstream.py`, error engine: `python ./scripts/run_error_engine.py`
- Tests: `pytest -q`

## Coding Style & Naming Conventions
- Markdown: one H1; sentence‑case headings; wrap at ~100 chars.
- YAML/JSON: 2‑space indent; kebab‑case keys (e.g., `phase-name`).
- Python: 4‑space indent; Black/PEP8; snake_case modules; prefer type hints.
- Scripts: prefer `.ps1`; provide `.sh` parity; keep core logic in Python.

## Testing Guidelines
- Framework: `pytest`; place tests under `tests/` (unit/integration subfolders as needed).
- Conventions: name files `test_*.py`; keep runs deterministic; avoid network/external state.
- Mark external/slow/CLI‑dependent tests; `sandbox_repos/` excluded by default via `pytest.ini`.
- Run targeted tests for changed tools/scripts first; then broader suites.

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat: add evaluation checklist`, `docs: refine phase 3 goals`, `chore: update script runner`).
- Keep commits atomic; one logical change per commit.
- PRs: clear description, linked issues, before/after context or screenshots, affected phases checklist.
- Schema/config changes: note versioning/compat; regenerate indices/mapping when applicable.

## Security & Configuration Tips
- Never commit secrets. Use `.env.local`; add `.env.example` when introducing new vars.
- Redact sensitive data; keep large files out of the repo.
- Treat `openspec/` and `schema/` as source‑of‑truth; run validators before merging.

## Agent‑Specific Instructions
- Scope: this file governs the entire repo unless a deeper AGENTS.md overrides it.
- Prefer small, focused diffs; avoid unrelated refactors; update docs/tests with script changes.
- Use `rg` for searches; `apply_patch` for edits; read files in ≤250‑line chunks.
- Use plans for multi‑step tasks with exactly one `in_progress` step; run validators and targeted tests after changes.

