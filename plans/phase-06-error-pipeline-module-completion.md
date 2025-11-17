# Error pipeline module completion plan

This plan completes the current error pipeline module using the existing specs and stubs in
`MOD_ERROR_PIPELINE`. It focuses on the deterministic engine, incremental hashing, plugin
execution, and reporting. GUI and SQLite/state-machine wiring are out-of-scope for this phase.

## Objectives

- Implement a deterministic, plugin-based validation engine with temp-dir isolation.
- Add incremental hashing (skip unchanged files) with JSON cache persistence.
- Produce per-file JSON reports and an aggregated JSONL log with 75KB rotation.
- Provide a minimal CLI entry to run the engine on local files for validation.
- Add fast tests validating determinism and incremental behavior.

## In-scope

- Finish stubs in:
  - `MOD_ERROR_PIPELINE/pipeline_engine.py`
  - `MOD_ERROR_PIPELINE/plugin_manager.py`
  - `MOD_ERROR_PIPELINE/file_hash_cache.py`
- Add minimal utilities referenced by the architecture (types, hashing, JSONL manager).
- Implement simple sample plugin(s) to exercise the pipeline (e.g., echo/no-op validator).
- Emit normalized report fields consistent with the operating contract’s summary semantics.

## Out-of-scope (this phase)

- Desktop GUI (`main.py`, drag-and-drop) and packaging.
- SQLite state layer and state-machine orchestration (see workstream 2 spec).
- External tool installation and full adapter layer for every linter.

## References (authoritative)

- `MOD_ERROR_PIPELINE/ARCHITECTURE.md:1`
- `MOD_ERROR_PIPELINE/ERROR_PIPELINE_MOD_README.md:1`
- `MOD_ERROR_PIPELINE/WS-ERROR-ENGINE-CORE.md:1`
- `MOD_ERROR_PIPELINE/ERROR_Operating Contract.txt:1`
- `MOD_ERROR_PIPELINE/state-machine specification.txt:1`

## Milestones

- M1: Utilities scaffolded (`src/utils`: types, hashing, jsonl manager, env/time helpers).
- M2: `FileHashCache` loads/saves and detects changes by SHA-256.
- M3: `PluginManager` discovers plugins, filters by extension, orders by DAG.
- M4: `PipelineEngine` processes a single file in temp dir and returns a report.
- M5: Per-file JSON and aggregated JSONL (with 75KB rotation) written to disk.
- M6: Incremental skip verified; repeated run produces identical outputs (determinism).
- M7: Minimal CLI and tests green on Windows (no network required).

## Deliverables

- Implemented engine/core:
  - `pipeline_engine.py` (`process_file`, `_run_plugins`, `_generate_report`).
  - `plugin_manager.py` (discover, filter, run; base class kept minimal).
  - `file_hash_cache.py` (load/save/has_changed/mark_validated).
- Utilities:
  - `src/utils/types.py` (PluginResult, PipelineReport shapes).
  - `src/utils/hashing.py` (sha256 helper).
  - `src/utils/jsonl_manager.py` (append with atomic 75KB rotation).
  - `src/utils/env.py` (scrubbed env per architecture).
  - `src/utils/time.py` (UTC ISO timestamps; ULID wrapper if used).
- Sample plugin(s): `src/plugins/echo/manifest.json`, `src/plugins/echo/plugin.py`.
- Minimal CLI: `scripts/run_error_engine.py` or `scripts/run_error_engine.ps1`.
- Tests: `tests/test_incremental_cache.py`, `tests/test_engine_determinism.py`.

## Phase checklist

- Engine determinism
  - Stable plugin ordering (topological sort on `requires`).
  - No network access; scrub proxy env vars; set locale to `C`.
  - Use temp dirs; never modify originals.
  - Stable run IDs/timestamps formatting (UTC ISO 8601).
- Incremental hashing
  - Cache path configurable; default `.validation_cache.json` under module root.
  - `has_changed` returns False for identical content; True otherwise.
- Reporting
  - Per-file JSON includes toolchain versions (when available) and summary counts.
  - Aggregated JSONL appends one line per event; rotates at ~75KB keeping newest lines.
- Error handling
  - Timeouts and subprocess return-code mapping (`success_codes` from manifest).
  - Collect stdout/stderr; never use `shell=True`.
  - Mark cache with `had_errors` flag.
- Tests
  - Re-run with unchanged file skips work (uses cache).
  - Two identical runs produce identical outputs (excluding monotonic fields if any).

## Task breakdown

1) Utilities (M1)
- Add `src/utils/types.py` defining:
  - `PluginResult`: `{ plugin_id, success, issues, stdout, stderr, returncode, duration_ms }`.
  - `PipelineReport`: `{ run_id, file_in, file_out, timestamp_utc, toolchain, summary, issues }`.
- Add `src/utils/hashing.py` with `sha256_bytes(path: Path) -> str`.
- Add `src/utils/time.py` with `utc_now_iso()` and optional ULID helper.
- Add `src/utils/env.py` (`scrub_env()` removing proxies, locale to `C`).
- Add `src/utils/jsonl_manager.py` with `append(path, obj)` and `rotate_if_needed(path, max_bytes=75_000)`.

2) Incremental cache (M2)
- Implement `FileHashCache`:
  - `load()`/`save()` JSON with robust error handling.
  - `has_changed(file)` compares stored vs current SHA-256.
  - `mark_validated(file, had_errors)` updates `hash`, `last_validated`, and `had_errors`.

3) Plugin manager (M3)
- Discovery: iterate subdirs under `src/plugins`, require `manifest.json` + `plugin.py` with `register()`.
- Filtering: match by file extension and optional `patterns` in manifest.
- Ordering: build `{plugin_id: requires[]}`; compute `TopologicalSorter(...).static_order()`.
- Execution: call `plugin.execute(file)`; collect `PluginResult`.

4) Pipeline engine (M4–M5)
- `process_file(file_path)`:
  - Generate `run_id`; check `has_changed`; return `{"status": "skipped"}` when unchanged.
  - Create temp dir; copy in/out; select plugins; run; gather results.
  - Write per-file JSON (neighbor `.json` by output file); append JSONL event.
  - Update cache; return `PipelineReport`.
- `_run_plugins(file_path)`: iterate in DAG order; enforce timeouts and env scrubbing.
- `_generate_report(...)`: normalize issues and summary; capture toolchain versions where available.

5) Sample plugin and CLI (M6–M7)
- `echo` plugin: reports a single info-level issue or simply succeeds; used by tests.
- CLI: accepts list of files and output dir; prints summary and path to JSONL.

6) Tests (M6–M7)
- `test_incremental_cache.py`: verifies `has_changed`/`mark_validated` behavior and persistence.
- `test_engine_determinism.py`: two runs on same input yield identical report content and order.

## Acceptance criteria

- Running the CLI on a small text/Python file produces:
  - Output file in chosen directory (original unmodified).
  - Per-file JSON report at a predictable path.
  - A JSONL log file that rotates at ~75KB (verified by forced append loop in test).
- Re-running on the same inputs returns a skipped result and does not re-run plugins.
- Tests pass locally (`pytest -q`) without network or external tool installs.

## Risks & mitigations

- External tools unavailable
  - Mitigation: ship tests with no-op `echo` plugin; decouple from linters.
- Windows path edge cases (spaces, Unicode en-dash in repo path)
  - Mitigation: use `Path` APIs; avoid shell; quote paths when needed.
- Log rotation correctness
  - Mitigation: implement tail-preserving rotation; add unit test with synthetic growth.
- Determinism drift (timestamps, ordering)
  - Mitigation: minimize volatile fields; stable ordering; use UTC ISO and compare with keys excluded in tests when necessary.

## Timeline (relative)

- Week 1: Utilities + cache (M1–M2)
- Week 2: Plugin manager + engine loop (M3–M4)
- Week 3: Reporting, rotation, CLI (M5)
- Week 4: Tests, fixes, docs polish (M6–M7)

