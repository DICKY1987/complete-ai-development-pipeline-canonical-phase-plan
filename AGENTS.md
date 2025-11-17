# Repository guidelines

## Project structure & module organization
- docs/: canonical phase plans, architecture notes, decision records (ADR).
- plans/: phase checklists, milestones, and templates used across the pipeline.
- scripts/: small automation (validation, export, syncing). Prefer PowerShell (.ps1) or Python.
- tests/: tests for scripts and templates; add here when introducing logic.
- assets/: diagrams and images referenced by docs.

## Build, test, and development commands
- Run scripts: `pwsh ./scripts/<name>.ps1` or `python ./scripts/<name>.py`.
- Validate Markdown (if configured): `npm run lint:md`.
- Run tests (if present): `pytest -q` or `pwsh ./scripts/test.ps1`.
- Generate docs (if present): `make docs` or `pwsh ./scripts/build-docs.ps1`.

## Coding style & naming conventions
- Markdown: one H1 per file; sentence‑case headings; wrap at ~100 chars.
- YAML/JSON: 2‑space indent; kebab‑case keys (e.g., `phase-name`).
- Python (scripts): 4‑space indent; Black/PEP8; snake_case for files and functions.
- Files: descriptive, scope‑first names (e.g., `phase-02-design.md`).

## Testing guidelines
- Prefer `pytest` for Python scripts; name tests `tests/test_*.py`.
- For docs/templates, use linters (Markdownlint, yamllint) and link checkers.
- Keep tests fast and isolated; avoid network/external state.

## Commit & pull request guidelines
- Conventional Commits: `feat: add evaluation checklist`, `docs: refine phase 3 goals`, `chore: update script runner`.
- Keep commits atomic; one logical change per commit.
- PRs include: clear description, linked issues, before/after context or screenshots, and checklist of affected phases.

## Security & configuration tips
- Never commit secrets. Use `.env.local`; provide `.env.example`.
- Redact sensitive data in docs/artifacts. Store large files outside the repo.

## Agent-specific instructions
- Follow AGENTS.md scope rules; keep patches minimal and focused.
- Prefer small, readable diffs and repository-relative paths.
- Do not refactor unrelated areas; update docs/tests when changing scripts.

## Agent workflow (Codex CLI)
- Scope: this file applies to the entire repository unless a more deeply nested
  `AGENTS.md` overrides it.
- Preambles: before running groups of commands, send a short 1–2 sentence note
  describing what you’ll do next. Avoid trivial preambles for single file reads.
- Plans: use the `update_plan` tool for multi-step or ambiguous tasks; keep steps
  short (5–7 words) with exactly one `in_progress` item at a time.
- Shell: prefer `rg`/`rg --files` for searches; read files in chunks ≤250 lines;
  avoid long outputs that will truncate.
- Patches: use `apply_patch` for edits; keep diffs focused; align with existing
  style; avoid unrelated refactors.
- Validation: when tests exist, run targeted tests for changed areas first; do not
  fix unrelated failures.
- Final messages: keep concise, include next steps if useful, and reference files
  with clickable repo-relative paths like `src/app.py:42`.
