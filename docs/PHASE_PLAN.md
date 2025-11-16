# Phase plan summary

This document summarizes the PH-01 to PH-03 plan and associated Codex/Claude
workstreams at a high level. See the detailed workstream execution plan in the
root for specifics.

## PH-01

- Module scaffolding for `src/pipeline/*`.
- Spec index scanner to collect `[IDX-...]` tags.
- Initial documentation updates.

## PH-02

- SQLite schema and DB core helpers.
- State machine validation and CRUD.
- Supporting scripts and tests.

## PH-03

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

## PH-04

Workstream Bundle Parsing & Validation is implemented in this repository.

Artifacts added:

- `schema/workstream.schema.json` - JSON Schema for workstream bundles
- `src/pipeline/bundles.py` - loading, validation, DAG/cycle detection, filescope checks, optional DB sync
- `workstreams/example_single.json`, `workstreams/example_multi.json` - sample bundles (example_multi includes an overlap to exercise detection)
- `scripts/validate_workstreams.py` - CLI to validate bundles; `--run-id` to sync to DB; `--json` for machine-readable output
- `tests/pipeline/test_bundles.py` - unit tests for validation and graphs

Commands:

- `python scripts/validate_workstreams.py` - validate bundles and report issues
- `python scripts/validate_workstreams.py --json` - emit JSON summary
- `python scripts/validate_workstreams.py --run-id <RUN>` - validate and sync to DB
- `pytest -q` - run tests for this phase

## PH-03.5

Aider Integration Contract & Prompt Template System is implemented.

Artifacts added:

- `docs/aider_contract.md` - integration contract (CONTRACT_VERSION AIDER_CONTRACT_V1)
- `config/tool_profiles.json` - `aider` profile with flags, env, working dir, timeout
- `src/pipeline/prompts.py` - prompt engine, helpers to run Aider, DB event recording
- `templates/prompts/edit_prompt.txt.j2`, `templates/prompts/fix_prompt.txt.j2` - prompt templates
- `sandbox_repos/sandbox_python/` - small test repo
- `tests/integration/test_aider_sandbox.py` - integration test (skips if Aider missing)

Commands:

- `python -c "import shutil; print(shutil.which('aider'))"` — verify Aider is available
- `pytest -q -m aider` - run only Aider integration tests

## PH-05

Orchestrator core loop (single workstream).

Precheck failed: expected project root `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` is missing on this machine. Per PH-05 execution rules, do not implement orchestrator logic in an alternate path. Complete PH-00 through PH-04.5 in the target repo first so that the following required components exist:

- `src/pipeline/` with stubs for `orchestrator.py`, `db.py`, `bundles.py`, `worktree.py`, `tools.py`, and Aider prompt helpers (`prompts.py`).
- Config and schema from prior phases (e.g., `config/tool_profiles.json`, `schema/workstream.schema.json`).
- Workstream bundles under `workstreams/` and a SQLite DB location.

Once `C:\Users\richg\ALL_AI\AI_Dev_Pipeline` exists with PH-00–PH-04.5 artifacts, proceed with PH-05 tasks:

- Implement `src/pipeline/orchestrator.py` with steps EDIT → STATIC → RUNTIME and DB state/event recording.
- Add CLI `scripts/run_workstream.py` to run one workstream by `--ws-id`.
- Add tests `tests/pipeline/test_orchestrator_single.py` covering success, EDIT/STATIC/RUNTIME failures, and scope violations.
- Update `docs/ARCHITECTURE.md` with an “Orchestrator Core Loop” section and record artifacts here.

Note: FIX/retry loops and multi-workstream scheduling are out of scope for PH-05.
