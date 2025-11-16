# Phase plan summary

This document summarizes the PH‑01 to PH‑03 plan and associated Codex/Claude
workstreams at a high level. See the detailed workstream execution plan in the
root for specifics.

## PH‑01

- Module scaffolding for `src/pipeline/*`.
- Spec index scanner to collect `[IDX-...]` tags.
- Initial documentation updates.

## PH‑02

- SQLite schema and DB core helpers.
- State machine validation and CRUD.
- Supporting scripts and tests.

## PH‑03

- Tool profiles and adapter core.
- DB integration and tests.
- Documentation refinements.

### Summary

Phase PH-03 introduces a profile-driven tool adapter that executes external
tools (utilities, tests, static analyzers, and AI tools) in a consistent,
configurable manner. Profiles are defined in `config/tool_profiles.json` and
consumed by `src/pipeline/tools.py`, which renders command templates, enforces
timeouts, and captures results. Subsequent workstreams integrate adapter events
with the DB layer and add tests.

### Artifacts

- `config/tool_profiles.json` - tool profiles configuration
- `src/pipeline/tools.py` - adapter logic (core + DB integration)
- `tests/pipeline/test_tools.py` - adapter tests (future)
 - Recommended profiles include Python quality tools (`ruff`, `black`, `mypy`),
   PowerShell analyzers/tests (`psscriptanalyzer`, `pester`), core test runner
   (`pytest`), optional linters/scanners (`yamllint`, `codespell`, `gitleaks`),
   and integration utilities (`aider`, `gh`).
