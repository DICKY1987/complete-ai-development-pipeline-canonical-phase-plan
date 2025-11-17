# OpenSpec integration phase plan

## Overview
This plan delivers an end-to-end, spec-driven flow that aligns OpenSpec change
folders with the pipeline’s workstream execution. It resolves schema drift,
introduces a deterministic converter from OpenSpec changes to workstream JSON,
integrates the official OpenSpec CLI where useful, reconciles documentation,
and adds CI + E2E validation.

Phases are small, independently shippable, and keep behavior deterministic.

## Phase 01 — Schema alignment and bundle normalization
Goals
- Eliminate drift between example bundles and the parser’s expected shape.
- Decide on the canonical bundle schema used by the pipeline.

Deliverables
- Updated example bundle(s) under `bundles/` matching the canonical schema.
- Compatibility note and migration guidance in `README.md` and `docs/`.

Tasks
- Choose canonical form: either parser’s `bundle-id/items/when-then` or the
  existing `bundle_id/workstreams` example. Prefer unifying on the parser’s
  `bundle-id` with hyphenated keys for consistency.
- Update `bundles/openspec-test-001.yaml` to the chosen schema.
- (Optional) Make the parser tolerant to both `bundle-id` and `bundle_id` to
  smooth migration.

Acceptance
- `tests/test_openspec_parser.py` passes with the updated bundle shape.
- Example bundle loads and round-trips via the parser.

## Phase 02 — Parser CLI parity with documentation
Goals
- Bring `src/pipeline/openspec_parser.py` to parity with documented flags.

Deliverables
- New flags implemented and tested:
  - `--change-id <id>`: resolve `openspec/changes/<id>/` as source input.
  - `--generate-bundle`: emit normalized bundle YAML to `bundles/`.
  - `--create-epic` (stub/no-op or feature-flagged): print payload shape or
    integrate with existing CCPM glue when available.

Tasks
- Extend parser to read `openspec/changes/<id>/proposal.md` and `tasks.md`,
  generate an `OpenSpecBundle` (map proposal title/requirements to items and
  when-then where feasible).
- Keep the existing `input` path flow intact; new flags are additive.
- Add focused unit tests that exercise `--change-id` and `--generate-bundle`.

Acceptance
- `python -m src.pipeline.openspec_parser --change-id test-001 --generate-bundle`
  generates a bundle under `bundles/` and prints the path.
- New tests pass locally and in CI.

## Phase 03 — Change → Workstream JSON converter
Goals
- Deterministically convert OpenSpec bundles into pipeline workstreams that
  satisfy `schema/workstream.schema.json`.

Deliverables
- New script `scripts/generate_workstreams_from_openspec.py`.
- Workstreams emitted as `workstreams/ws-<id>.json` with correct fields:
  `id`, `openspec_change`, `ccpm_issue` (placeholder allowed), `gate`,
  `files_scope`, `tasks`, `acceptance_tests`, and dependencies when present.

Tasks
- Map bundle content to workstream fields:
  - Change id → `id`/`openspec_change`.
  - Tasks/requirements → `tasks`.
  - When-then/acceptance criteria → `acceptance_tests`.
  - Spec deltas or touched files → `files_scope` (conservative set; allow manual
    augmentation via metadata if needed).
- Validate output via `src/pipeline/bundles.py` before writing.
- Add a round-trip test: change → bundle → workstream → validate.

Acceptance
- `python scripts/generate_workstreams_from_openspec.py --change-id test-001`
  creates a valid `workstreams/ws-test-001.json`.
- `python scripts/validate_workstreams.py` reports OK for the generated file.

## Phase 04 — OpenSpec CLI integration (optional but recommended)
Goals
- Use the official OpenSpec CLI for validate/list/archive where it improves
  ergonomics, while keeping core logic in Python for determinism.

Deliverables
- Dev docs update to include `npm i -g @fission-ai/openspec` and quickstart.
- Thin wrappers (optional) in PowerShell for common tasks.

Tasks
- Add `openspec validate` and `openspec list` steps to contributor docs.
- Provide `scripts/openspec.ps1` as a convenience wrapper (optional).
- Keep critical flows (conversion and validation) in Python to avoid runtime
  dependency on Node in CI, unless explicitly enabled.

Acceptance
- Local workflow: `openspec validate` runs clean; docs reflect CLI usage.
- CI remains deterministic without requiring Node unless opted in.

## Phase 05 — Documentation reconciliation
Goals
- Align documentation with actual capabilities and flags.

Deliverables
- Updated `docs/ccpm-openspec-workflow.md` with correct flags and examples.
- README additions for the end-to-end flow.

Tasks
- Replace references to undocumented flags with the Phase 02 interface.
- Add examples for change → bundle → workstream → pipeline runs.

Acceptance
- All examples execute as written on a clean clone following setup steps.

## Phase 06 — Acceptance criteria mapping and gating
Goals
- Ensure acceptance criteria travel from OpenSpec to runtime gating signals.

Deliverables
- Mapping rules documented and enforced in the converter (Phase 03).
- Optional: a small helper to render acceptance checks for agents/tests.

Tasks
- Formalize translation of when-then blocks to `acceptance_tests` strings.
- Expose acceptance tests in orchestrator or error pipeline context where
  meaningful.

Acceptance
- Generated workstreams include non-empty `acceptance_tests` when present in
  OpenSpec changes, and they are visible to downstream phases.

## Phase 07 — Spec tooling consolidation
Goals
- Avoid tool drift by deciding what remains vs what adopts OpenSpec’s model.

Deliverables
- Decision record (ADR) under `docs/` covering `tools/spec_*` alignment.
- Minimal changes to keep a single source of truth in `openspec/specs/`.

Tasks
- Evaluate `tools/spec_guard`, `spec_renderer`, `spec_resolver`, `spec_indexer`,
  `spec_patcher` against OpenSpec workflows.
- Either adapt them to consume `openspec/specs/` directly or deprecate with
  clear guidance.

Acceptance
- ADR merged; README/docs reference the consolidated approach only.

## Phase 08 — CI integration and E2E test
Goals
- Add automated checks for the full flow and keep it deterministic.

Deliverables
- CI steps (PowerShell-first) invoking:
  - Parser/bundle round-trip tests.
  - Change → workstream conversion and validation.
  - Optional: end-to-end dry run of the error pipeline over a sandbox change.

Tasks
- Update `scripts/test.ps1` to include the new tests and validators.
- Add an integration test under `tests/integration/` covering the pipeline
  path with a tiny change in `openspec/changes/`.

Acceptance
- CI passes on the new integration tests.
- Contributors can reproduce locally via `pwsh ./scripts/test.ps1`.

## Milestones and sequencing
- M1: Phases 01–02 (schema + CLI parity) — unblock bundle generation.
- M2: Phase 03 (converter) — unlock pipeline-driven workstreams from OpenSpec.
- M3: Phases 05–06 (docs + acceptance mapping) — developer workflow solidity.
- M4: Phase 07 (tooling ADR) — reduce drift and duplication.
- M5: Phase 08 (CI/E2E) — guardrails for ongoing changes.

## Risks and mitigations
- Schema churn: support a brief compatibility window (both `bundle-id` and
  `bundle_id`) and document the cutoff.
- Overly broad `files_scope`: start conservative and allow override via
  metadata or a curated list in `proposal.md` until better inference lands.
- Optional Node dependency: keep core flows in Python; treat the OpenSpec CLI
  as a developer convenience unless CI opts in.

