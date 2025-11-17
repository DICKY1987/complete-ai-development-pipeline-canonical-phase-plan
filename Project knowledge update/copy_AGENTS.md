# Repository guidelines

## Project structure & module organization
- docs/: canonical phase plans, architecture notes, decision records (ADR), specs (see docs/spec/).
- plans/: phase checklists, milestones, and templates used across the pipeline.
- scripts/: automation (bootstrap, validate, generate, run). Prefer PowerShell (.ps1) or Python.
- tools/: internal Python utilities (e.g., spec_guard, spec_renderer, spec_resolver, spec_indexer).
- src/: light Python helpers and plugin stubs used by tools/tests.
- openspec/: OpenSpec project and specs (validation-pipeline, plugin-system, orchestration).
- workstreams/: example single/multi workstream JSON bundles.
- schema/: JSON/YAML/SQL schemas that define workstream and sidecar metadata contracts.
- config/: adapter/tool profiles, decomposition rules, and circuit-breaker config.
- tests/: unit/integration tests for scripts/tools/pipeline.
- assets/: diagrams and images referenced by docs.
- sandbox_repos/: self-contained toy repos for integration tests (excluded from pytest by default).
- PHASE_DEV_DOCS/, Coordination Mechanisms/, gui/: phase notes and coordination guides.

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
- Markdown: one H1 per file; sentence‑case headings; wrap at ~100 chars.
- YAML/JSON: 2‑space indent; kebab‑case keys (e.g., `phase-name`).
- Python: 4‑space indent; Black/PEP8; snake_case for files/modules; prefer type hints in new code.
- Files: descriptive, scope‑first names (e.g., `phase-02-design.md`).
- Scripts: prefer `.ps1` for Windows‑first flows; provide `.sh` parity where feasible (no WSL‑only assumptions in shared logic).

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
- Treat `openspec/` and `schema/` as source‑of‑truth contracts; validate changes via provided validators before merging.

## Agent‑specific instructions
- Follow AGENTS.md scope rules; keep patches minimal and focused.
- Prefer small, readable diffs and repository‑relative paths.
- Do not refactor unrelated areas; update docs/tests when changing scripts.
- When adding scripts under `scripts/`, prefer Python for logic and `.ps1`/`.sh` as thin wrappers if needed.
- Coordinate changes to `tools/` with tests under `tests/` (pipeline/plugins sections), keeping behavior reproducible/deterministic.

## Agent workflow (Codex CLI)
- Scope: this file applies to the entire repository unless a more deeply nested `AGENTS.md` overrides it.
- Preambles: before running groups of commands, send a short 1–2 sentence note describing what you’ll do next. Avoid trivial preambles for single file reads.
- Plans: use the `update_plan` tool for multi‑step or ambiguous tasks; keep steps short (5–7 words) with exactly one `in_progress` item at a time.
- Shell: prefer `rg`/`rg --files` for searches; read files in chunks ≤250 lines; avoid long outputs that will truncate.
- Patches: use `apply_patch` for edits; keep diffs focused; align with existing style; avoid unrelated refactors.
- Validation: when tests exist, run targeted tests for changed areas first; do not fix unrelated failures.
- Final messages: keep concise, include next steps if useful, and reference files with clickable repo‑relative paths like `src/app.py:42`.

## Repository‑specific notes
- Windows‑first: PowerShell is preferred; `.sh` scripts are provided for parity (WSL). Keep cross‑platform logic in Python where possible.
- Specs/workstreams: keep `workstreams/` examples in sync with `schema/` and `openspec/`. Run validators after edits.
- Indices/mapping: regenerate via `generate_spec_index.py` and `generate_spec_mapping.py` when specs or schema change.
- Determinism: tests under `tests/pipeline/` check deterministic execution. Avoid nondeterministic I/O, timestamps without control, or network calls in core code.
