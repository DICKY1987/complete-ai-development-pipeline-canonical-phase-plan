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

