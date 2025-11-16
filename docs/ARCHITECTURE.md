# Architecture overview

This repository implements a multi‑phase AI development pipeline with clear
workstreams. The code is organized under `src/pipeline/` with supporting
scripts in `scripts/`, schema in `schema/`, and documentation in `docs/`.

## Components

- Pipeline core: `src/pipeline/` modules (orchestrator, scheduler, executor).
- Persistence: SQLite state store defined in `schema/schema.sql`.
- Tooling: profile-driven adapter in `src/pipeline/tools.py` (PH-03).
- Utilities: prompts, worktree helpers, circuit breakers, recovery, bundles.

## Workstream Bundles & Validation

- Purpose: Define inputs for orchestration — each workstream declares its id, files scope, tasks, and dependencies.
- Schema: `schema/workstream.schema.json` specifies required fields and constraints (strict, no unknown fields).
- Loader: `src/pipeline/bundles.py` resolves the workstream directory, loads JSON (per-file object or list), validates against the schema (using `jsonschema` if available; strict manual checks otherwise), builds a dependency DAG, detects cycles, and finds file-scope overlaps.
- CLI: `python scripts/validate_workstreams.py` validates all bundles, reports cycles/overlaps, and optionally syncs them into the DB (`workstreams` table) with `--run-id`.
- Directory: default `workstreams/` at repo root; override with env `PIPELINE_WORKSTREAM_DIR`.

## Flow

1. Plan workstreams (docs, plans).
2. Execute workstreams via orchestrator/scheduler/executor.
3. Record events/errors/steps in SQLite.
4. Generate artifacts and reports.

See also:
- State machine details in `docs/state_machine.md` (run/workstream transitions).
- Phase plan in `docs/PHASE_PLAN.md` (PH-01 to PH-03 scope and artifacts).
  PH-04 adds schema, loader/validator, examples, CLI, and tests.

## Conventions

- Git worktrees for isolated branches per workstream.
- Python 3.12+, PowerShell 7; tests with `pytest`.
- JSON uses two‑space indent and kebab‑case keys.

## State & persistence

- Database path: `state/pipeline_state.db` (override with `PIPELINE_DB_PATH`).
- Initialization: `python scripts/init_db.py` (idempotent; applies `schema/schema.sql`).
- Core tables:
  - `runs` - lifecycle of an orchestrated run.
  - `workstreams` - individual work units within a run, with dependencies.
  - `step_attempts` - execution attempts with timestamps and results.
  - `errors` - deduplicated errors with signatures and counts.
  - `events` - append-only event log for traceability.

## Tool profiles & adapter layer

- Location: `config/tool_profiles.json` contains declarative profiles for tools.
- Purpose: enable consistent, configurable execution of utilities, tests, and
  static analyzers via a common adapter.
- Types: `ai`, `static-check`, `test`, `utility` (see profiles JSON).
- Adapter: `src/pipeline/tools.py` loads profiles, renders commands with
  template vars like `{cwd}` and `{repo_root}`, executes with timeouts, and
  captures stdout/stderr and exit codes. DB integration records events/errors
  in PH-03 follow-up workstreams.
  - Profiles live in `config/tool_profiles.json` and include core tools:
    `pytest`, `psscriptanalyzer`, and recommended linters/formatters
    (`ruff`, `black`, `mypy`), plus optional scanners (`yamllint`, `codespell`,
    `gitleaks`) and integration utilities (`aider`, `gh`).
