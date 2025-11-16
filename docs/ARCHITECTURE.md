# Architecture overview

This repository implements a multi‑phase AI development pipeline with clear
workstreams. The code is organized under `src/pipeline/` with supporting
scripts in `scripts/`, schema in `schema/`, and documentation in `docs/`.

## Components

- Pipeline core: `src/pipeline/` modules (orchestrator, scheduler, executor).
- Persistence: SQLite state store defined in `schema/schema.sql`.
- Tooling: profile‑driven adapter in `src/pipeline/tools.py` (PH‑03).
- Utilities: prompts, worktree helpers, circuit breakers, recovery, bundles.

## Flow

1. Plan workstreams (docs, plans).
2. Execute workstreams via orchestrator/scheduler/executor.
3. Record events/errors/steps in SQLite.
4. Generate artifacts and reports.

## Conventions

- Git worktrees for isolated branches per workstream.
- Python 3.12+, PowerShell 7; tests with `pytest`.
- JSON uses two‑space indent and kebab‑case keys.

## State & persistence

- Database path: `state/pipeline_state.db` (override with `PIPELINE_DB_PATH`).
- Initialization: `python scripts/init_db.py` (idempotent; applies `schema/schema.sql`).
- Core tables:
  - `runs` — lifecycle of an orchestrated run.
  - `workstreams` — individual work units within a run, with dependencies.
  - `step_attempts` — execution attempts with timestamps and results.
  - `errors` — deduplicated errors with signatures and counts.
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
