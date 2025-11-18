# Repository Guidelines

## Project structure & module organization
- `docs/` canonical plans, ADRs, specs; `assets/` images.
- `plans/` phase checklists and milestones.
- `scripts/` bootstrap, validate, run; PowerShell-first with `.sh` parity.
- `tools/` internal Python utilities; `src/` light helpers and stubs.
- `openspec/` OpenSpec source of truth; `schema/` contracts.
- `workstreams/` example bundles; keep in sync with `schema/` + validators.
- `config/` adapter profiles and rules; `tests/` unit/integration.
- `sandbox_repos/` toy repos for targeted integration (excluded by default).
- `PHASE_DEV_DOCS/`, `Coordination Mechanisms/`, `gui/` phase notes and guides.

## Build, test, and development commands
- Environment (Windows PowerShell): `python -m venv .venv && . ./.venv/Scripts/Activate.ps1`
  then `pip install -r requirements.txt`.
- Bootstrap/checks: `pwsh ./scripts/bootstrap.ps1`, `pwsh ./scripts/test.ps1`.
- Validate workstreams/authoring: `python ./scripts/validate_workstreams.py`,
  `python ./scripts/validate_workstreams_authoring.py`.
- Generate indices/mapping: `python ./scripts/generate_spec_index.py`,
  `python ./scripts/generate_spec_mapping.py`.
- Run pipeline: `python ./scripts/run_workstream.py`; error pipeline: `python ./scripts/run_error_engine.py`.
- Tests: `pytest -q` (CI-friendly: `pwsh ./scripts/test.ps1`). Optional: `npm run lint:md`.

## Coding style & naming conventions
- Markdown: one H1 per file; sentence‑case headings; wrap ~100 chars.
- YAML/JSON: 2‑space indent; kebab‑case keys.
- Python: 4‑space indent; Black/PEP8; snake_case files; add type hints in new code.
- Files: descriptive, scope‑first names (e.g., `phase-02-design.md`).
- Scripts: Windows‑first `.ps1`; provide `.sh` parity when feasible.

## Testing guidelines
- Use `pytest`; place tests under `tests/`. Keep execution deterministic; avoid network/external CLIs.
- Mark/skips for integration or external dependencies. `sandbox_repos/` excluded via `pytest.ini`.
- Validate `openspec/` and `schema/` changes with provided validators before merging.

## Commit & pull request guidelines
- Conventional Commits (e.g., `feat: add evaluation checklist`, `docs: refine phase 3 goals`).
- Keep commits atomic. PRs include description, linked issues, before/after context or screenshots.
- When updating `schema/` or `config/`, note compat/versioning and regenerate indices/mapping.

## Security & configuration tips
- Never commit secrets. Use `.env.local`; add `.env.example` when introducing env vars.
- Redact sensitive data in docs/artifacts. Treat `openspec/` and `schema/` as source of truth.

## Agent‑specific notes
- Prefer small, focused diffs; align with this guide’s scope rules.
- Use Python for cross‑platform logic; keep behavior reproducible and deterministic.
