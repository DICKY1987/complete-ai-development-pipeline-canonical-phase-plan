# Repository Guidelines

## Project Structure & Module Organization
- docs/: canonical phase plans, architecture notes, decision records (ADR).
- plans/: phase checklists, milestones, and templates used across the pipeline.
- scripts/: small automation (validation, export, syncing). Prefer PowerShell (.ps1) or Python.
- tests/: tests for scripts and templates; add here when introducing logic.
- assets/: diagrams and images referenced by docs.

## Build, Test, and Development Commands
- Run scripts: `pwsh ./scripts/<name>.ps1` or `python ./scripts/<name>.py`.
- Validate Markdown (if configured): `npm run lint:md`.
- Run tests (if present): `pytest -q` or `pwsh ./scripts/test.ps1`.
- Generate docs (if present): `make docs` or `pwsh ./scripts/build-docs.ps1`.

## Coding Style & Naming Conventions
- Markdown: one H1 per file; sentence‑case headings; wrap at ~100 chars.
- YAML/JSON: 2‑space indent; kebab‑case keys (e.g., `phase-name`).
- Python (scripts): 4‑space indent; Black/PEP8; snake_case for files and functions.
- Files: descriptive, scope‑first names (e.g., `phase-02-design.md`).

## Testing Guidelines
- Prefer `pytest` for Python scripts; name tests `tests/test_*.py`.
- For docs/templates, use linters (Markdownlint, yamllint) and link checkers.
- Keep tests fast and isolated; avoid network/external state.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat: add evaluation checklist`, `docs: refine phase 3 goals`, `chore: update script runner`.
- Keep commits atomic; one logical change per commit.
- PRs include: clear description, linked issues, before/after context or screenshots, and checklist of affected phases.

## Security & Configuration Tips
- Never commit secrets. Use `.env.local`; provide `.env.example`.
- Redact sensitive data in docs/artifacts. Store large files outside the repo.

## Agent‑Specific Instructions
- Follow AGENTS.md scope rules; keep patches minimal and focused.
- Prefer small, readable diffs and repository‑relative paths.
- Do not refactor unrelated areas; update docs/tests when changing scripts.
