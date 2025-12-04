---
doc_id: DOC-GUIDE-AGENTS-453
---

# Repository Guidelines

## Project Structure & Module Organization
- `core/`: primary runtime modules (engine, planning, search, terminal UI) organized by capability; keep new modules narrow and colocated with their collaborators.
- `phase*/`: canonical phase plans and templates; mirror changes in code with the corresponding phase doc.
- `specs/`, `docs/`, `glossary/`, `patterns/`: authoritative references and vocab; preserve `doc_id` metadata when editing.
- `scripts/`: automation helpers (lint, glossary policy).
- `tests/`: mirrors runtime layout; add new tests alongside the code path they cover. Assets live in `assets/`; shared schemas in `schema/`.

## Build, Test, and Development Commands
- `python -m pytest -m "not slow"` — fast local signal; default for iterative work.
- `python -m pytest` — full suite; run before pushing or opening a PR.
- `pre-commit run --all-files` — formatting (black, isort), basic checks, glossary SSOT policy, optional mypy/pytest hooks if available.
- `python -m pytest tests/path/to/test_file.py -k case_name` — target a single area during debugging.

## Coding Style & Naming Conventions
- Python 3.12, 4-space indents, type hints where the interface is non-trivial.
- Format with `black`; sort imports with `isort --profile black`; keep imports local to the smallest scope practical.
- Modules and packages use snake_case; classes use PascalCase; tests use `test_*` files and functions.
- Maintain doc front-matter fields (`doc_id`, status banners) exactly; do not regenerate IDs.
- Prefer small, single-responsibility functions; raise explicit errors over silent `None`.

## Testing Guidelines
- Align new tests with existing markers: tag long/integration work as `@pytest.mark.slow` or `@pytest.mark.integration`.
- Keep fixtures in the nearest `conftest.py` to avoid cross-module bleed; use factories over ad-hoc literals for execution requests and jobs.
- When adding behaviors that touch routing, patching, or glossary policy, add regression cases under the matching subfolder in `tests/` and update `tests/TEST_INDEX.yaml` if you introduce new suites.

## Commit & Pull Request Guidelines
- Favor small, focused commits with imperative subject lines (`Add job queue retry guard`); include issue or doc links in the body.
- PRs should describe intent, key design decisions, and test results (`pytest -m "not slow"` or full suite); attach screenshots for UI/CLI output changes when useful.
- Keep changes scoped to the current git repo; avoid sweeping renames without paired test updates and doc touch points (phase docs, specs, glossary).
