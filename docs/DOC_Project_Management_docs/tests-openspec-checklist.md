---
doc_id: DOC-GUIDE-TESTS-OPENSPEC-CHECKLIST-833
---

# OpenSpec test checklist

This checklist enumerates existing tests and proposed tests to ensure the OpenSpec → Bundle → Workstream → Pipeline flow remains correct and deterministic.

## Existing tests
- Parser roundtrip: `tests/test_openspec_parser.py`
  - Loads a small YAML bundle with `bundle-id`, `items`, and `when-then`.
  - Asserts roundtrip `write_bundle` produces expected keys.
- Change → Workstream conversion: `tests/test_openspec_convert.py`
  - Creates a temporary OpenSpec change (`proposal.md`, `tasks.md`).
  - Generates an `OpenSpecBundle` via `--change-id` and converts to a schema-valid workstream.
  - Validates via `src/pipeline/bundles.validate_bundle_data`.

## Proposed unit tests
- Parser CLI flags
  - `--change-id` produces bundle with `bundle_id` prefix `openspec-<id>`.
  - `--generate-bundle` writes to `bundles/` and prints path.
  - `--echo` prints normalized YAML.
  - `--create-epic` prints a well-formed JSON stub payload.
- Bundle schema tolerance
  - Accept both `bundle-id` and `bundle_id` at read-time (compatibility window).
- Converter mapping
  - When-then mapping: items with `when-then` produce `acceptance_tests` lines prefixed with `WHEN/THEN`.
  - Task extraction: task lines with paths infer `files_scope`.
  - Explicit `files_scope` overrides inference.
  - Validation error when neither inference nor explicit `files_scope` provided.
- Renderer fallback
  - When `docs/.index/suite-index.yaml` missing, `tools/spec_renderer/renderer.py` concatenates `openspec/specs/**/spec.md` deterministically.

## Proposed integration tests
- Smoke: end-to-end OpenSpec flow
  - Given `openspec/changes/<id>`, run:
    1) `python -m src.pipeline.openspec_parser --change-id <id> --generate-bundle`
    2) `python scripts/generate_workstreams_from_openspec.py --change-id <id> --files-scope <some path>`
    3) `python scripts/validate_workstreams.py`
  - Assert exit codes are 0 and artifacts exist `bundles/openspec-<id>.yaml`, `workstreams/ws-<id>.json`.
- Workstream overlap detection
  - Create two workstreams with overlapping `files_scope`.
  - `validate_workstreams.py --json` returns `ok: false` and includes overlap details.
- Orchestrator dry-run
  - Use a generated workstream id `ws-<id>`.
  - Run `scripts/run_workstream.py --ws-id ws-<id>` with `PIPELINE_DRY_RUN=1`.
  - Assert step transitions and recorded events are present in state/DB.

## Notes
- Tests requiring external tools or network should be marked/skipped by default.
- Prefer deterministic fixtures; avoid timestamps unless controlled.

