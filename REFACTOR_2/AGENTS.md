# Repository Guidelines

## Project Structure & Module Organization
- Root contains EXEC-017 analysis utilities (`comprehensive_archival_analyzer.py`, `detect_parallel_implementations.py`, `entry_point_reachability.py`, `test_coverage_archival.py`, `validate_archival_safety.py`) plus summary docs (`EXEC017_*`, `DOCUMENTATION_INDEX.md`, `SESSION_INDEX_EXEC017.md`, `MODULE_INVENTORY_EXEC017.md`).
- Phase folders (`01_PLANNING`, `02_ARCHITECTURE`, `03_IMPLEMENTATION`, `04_OPERATIONS`, `05_REFERENCE`) mirror the canonical pipeline: each holds topic-focused READMEs and supporting guides (plans, architecture deep dives, protocols, completion summaries).
- Keep generated artifacts inside the repo (create an `artifacts/` subfolder when needed); do not write outside the workspace or mutate the parent repository.

## Build, Test, and Development Commands
- Python 3.11+ recommended; create a local venv (`python -m venv .venv; .\.venv\Scripts\Activate`).
- Static analyzers are CLI-driven; common runs:
  - `python .\test_coverage_archival.py --root . --output artifacts\\test_coverage_archival_report.json`
  - `python .\validate_archival_safety.py --root . --report artifacts\\archival_safety_report.json`
  - `python .\detect_parallel_implementations.py --root . --output artifacts\\parallel_candidates.json`
- Orchestration entrypoint lives in the main scripts folder: `pwsh ..\\scripts\\run_multi_agent_refactor.ps1 -DryRun` (use from repo root).
- Prefer `python -m pytest` for any new tests you add; keep fast, deterministic runs.

## Coding Style & Naming Conventions
- Python: PEP 8 with 4-space indents, snake_case modules/functions, type hints, and dataclasses where stateful data is grouped. Use `logging` (INFO by default) instead of print; keep pure functions and small helpers.
- PowerShell: PascalCase functions, comment-based help, `$ErrorActionPreference = "Stop"`, and `Write-Verbose`/`Write-Error` for messaging. Keep parameters explicit and validate inputs early.
- Markdown: concise headings, bullet-first structure, and cross-link to existing phase docs.

## Testing Guidelines
- Each analyzer is its own executable check; run with `--help` before making changes and rerun with representative sample paths after edits. Use `--verbose` to surface warnings.
- When adding tests, co-locate under `tests/` or alongside the script with `_test.py`; name cases after the scenario under evaluation and favor fixture-free, deterministic inputs.
- Capture outputs to `artifacts/` and review JSON for schema stability before committing.

## Commit & Pull Request Guidelines
- Follow conventional commits seen in history (`feat:`, `fix:`, `docs:`, `chore:`). Scope with a concise noun (e.g., `feat: add archival safety scoring`).
- PRs should include: purpose/impact summary, files touched (by phase or analyzer), commands run with results, and any doc updates linked. Attach before/after samples for JSON outputs when they change.

## Security & Configuration Tips
- No secrets or tokens in scripts or logs; scrub sample data before sharing.
- Keep runs scoped to this repository path; avoid modifying sibling repos or global git settings.
- Ensure artifacts that include file paths or module names are safe to publish before uploading anywhere external.
