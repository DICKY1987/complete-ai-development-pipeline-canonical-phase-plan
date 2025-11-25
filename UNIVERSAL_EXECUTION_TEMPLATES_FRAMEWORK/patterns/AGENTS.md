
# Repository Guidelines

## Project Structure & Module Organization
The repo is rooted in `patterns\`: `executors\` hosts the Codex/Aider/Git runners, `schemas\` and `specs\` store pattern contracts, and `scripts\` supplies cross-platform automation (PowerShell first). Use `docs\DEV_RULES_CORE.md` as the contract of record for planning, rules, and architecture. Reference implementations sit in `examples\`, audit output in `reports\`, regression assets in `verification\`, and harnesses/tests in `tests\`. `registry\` holds generated catalogs; avoid `legacy_atoms\` unless migrating by request.

## Build, Test, and Development Commands
Create an isolated environment via `python -m venv .venv ; .\.venv\Scripts\Activate.ps1`, then `pip install -r requirements.txt`. Run `pwsh .\scripts\bootstrap.ps1` to lint structure and confirm prerequisites. `pwsh .\scripts\test.ps1` drives the deterministic suite, while `pytest -q` is the fast unit/integration loop. Validate workstreams with `python .\scripts\validate_workstreams.py` and ensure authoring compliance via `python .\scripts\validate_workstreams_authoring.py` before updating the registry.

## Coding Style & Naming Conventions
Follow Windows-friendly paths and keep edits inside the current git root. Markdown uses a single `#` heading per file, sentence-case headers, and ~100 character wrap. YAML/JSON prefer two-space indents and kebab-case keys; Python uses four spaces, snake_case files, and type hints for new helpers. Preserve sanctioned import paths (e.g., `from core.state.db import init_db`) and avoid deprecated `src\pipeline\*` modules. Keep edits minimal, comments concise, and never introduce secrets.

## Testing Guidelines
Tests live under `tests\` (mirroring module names) and must stay deterministic—avoid network calls unless mocked. Name Python tests `test_<feature>.py` and mirror fixtures from `tests\pipeline\` when expanding harnesses. Run `pytest -q` plus `pwsh .\scripts\test.ps1` before pushing; update or add regression cases whenever behavior changes. Sandbox repositories in `sandbox_repos\` are for targeted integration and remain excluded from default pytest runs.

## Commit & Pull Request Guidelines
Use Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`). Keep commits atomic, summarize motivation plus validation steps, and document follow-up tasks when needed. Pull requests should reference related ExecutionRequests or issues, describe scope, list validation commands, and attach screenshots or logs for UX-facing work. Highlight schema or contract updates so reviewers can re-run the relevant validators.

## Security & Configuration Tips
Never commit credentials; store local secrets in `.env.local` and provide sanitized examples when new variables are required. Respect `ai_policies.yaml` safe zones—`core\`, `engine\`, `error\`, and `scripts\` are safe, whereas `schema\` or `config\` changes demand review diligence. After altering repository topology, rerun `python .\scripts\generate_repo_summary.py` and `python .\scripts\generate_code_graph.py` to refresh AI guidance artifacts.
