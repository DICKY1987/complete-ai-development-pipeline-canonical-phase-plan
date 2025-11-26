# ADR-009: Module-Centric Architecture Decision

## Context
The repo previously mixed artifact-type organization (docs/, tests/, schemas/) with domain folders,
causing scattered context for AI tools, drifted dependencies, and awkward SafePatch/worktree usage.

## Decision
- Organize by module boundary under `modules/`, each owning its code, tests, schemas, docs, and
  `.state/`.
- Use ULID-prefixed artifacts per module for machine-verifiable grouping.
- Treat module directories as the atomic context unit for AI tools and SafePatch worktrees.

## Rationale
- Locality: one directory contains everything needed to reason about a module.
- Determinism: ULID identity plus manifests enable reproducible DAGs and imports.
- Parallelism: module boundaries reduce contention and simplify worktree isolation.
- Import hygiene: wrapper `__init__.py` enables clean imports despite numeric filenames.

## Consequences
- Migration requires manifest authoring, import rewrites, and DAG regeneration.
- Global artifact-type directories become legacy/archived; modules are the source of truth.
- Tooling (validators, DAG refresh) must run after manifest changes.
