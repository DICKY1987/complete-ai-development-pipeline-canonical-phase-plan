WS-ERROR-ENGINE-CORE
Here’s a drop-in workstream spec you can hand straight to **Codex or Claude Code** to wire up the core error/validation pipeline using those old files.

I’ll write it in the same style as your PH-0x workstreams, but scoped just to this engine.

---

## WS-ERROR-ENGINE-CORE

**Implement the deterministic validation engine + hash cache using existing design docs**

### ROLE

You are an AI coding agent (Codex or Claude Code CLI) with **full read/write access** to the repo that contains:

* `ARCHITECTURE.md`
* `ERROR_PIPELINE_MOD_README.md`
* `pipeline_engine.py`
* `plugin_manager.py`
* `file_hash_cache.py`
* `errorfixpipleinechat.txt`
* `file_router.config.json`
* `requirements.txt`
* (and the rest of `src/` as laid out in the README)

Your job in this workstream is to **finish the core pipeline engine and hash cache implementation**, reusing the existing design and code fragments instead of inventing new architecture.

---

### PROJECT ROOT

* Assume the project root is **`C:\Users\richg\ALL_AI\ERROR_PIPELINE_MOD`** (update if different).
* All paths below are relative to that root.

---

### CONTEXT SOURCES (MUST READ FIRST)

Use these files as **authoritative context** before changing any code:

1. **High-level design & guarantees**

   * `ERROR_PIPELINE_MOD_README.md`
     – Overall goals: deterministic, plugin-based validation, temp-dir isolation, ULID run IDs, JSON + JSONL logs, incremental processing.
   * `ARCHITECTURE.md`
     – Detailed data flow, component responsibilities (plugin manager, engine, reporter, JSONL manager, etc.).

2. **Old design conversation / reference implementation**

   * `errorfixpipleinechat.txt`
     – Contains previously generated **reference code** and pseudocode for:

     * `PluginManager` behavior and plugin discovery.
     * Original `PipelineEngine.process_file` and JSON/JSONL workflow.
     * Incremental validation (`FileHashCache`, `enable_incremental`, `has_changed()`).
     * ULID, temp dir isolation, `_copy_to_output`, toolchain capture, JSONL rotation, etc.

3. **New stubs / placeholders to be implemented**

   * `pipeline_engine.py` (current stub in `src/core/`)
   * `file_hash_cache.py` (current stub in `src/core/`)

---

### TARGET FILES (YOU WILL MODIFY)

Focus changes on these modules:

* `src/core/pipeline_engine.py`

  * Implement:

    * `PipelineEngine.process_file(self, file_path: Path) -> PipelineReport`
    * `PipelineEngine._run_plugins(self, file_path: Path) -> List[PluginResult]`
    * `PipelineEngine._generate_report(self, file_path: Path, plugin_results: List[PluginResult], run_id: Optional[str]) -> PipelineReport`

* `src/core/file_hash_cache.py`

  * Implement:

    * `FileHashCache.load()`
    * `FileHashCache.save()`
    * `FileHashCache.has_changed(file_path: Path) -> bool`
    * `FileHashCache.mark_validated(file_path: Path) -> None`

* **Only if needed to make the above work cleanly** (minimal, non-breaking edits):

  * `src/core/plugin_manager.py`
  * `src/utils/jsonl_manager.py`
  * `src/utils/types.py` (where `PipelineReport` and `PluginResult` are defined)
  * Any obviously missing utility code that the architecture expects (e.g., hash helpers).

You should **not** touch GUI modules (`src/gui/*`) or plugin implementations except where absolutely necessary to satisfy the contracts.

---

### PRIMARY OBJECTIVE

Using the design in `ARCHITECTURE.md` + the reference snippets in `errorfixpipleinechat.txt`, implement a **deterministic, incremental, plugin-based validation engine** that:

1. **Skips unchanged files** based on content hash.
2. **Runs all applicable plugins** in a stable, dependency-aware order.
3. Processes each file in an **isolated temp directory** (original never modified).
4. Writes **per-file JSON reports** and **aggregated JSONL logs**.
5. Produces a `PipelineReport` object that the GUI can consume.

Do **not** design new behavior; **reconstruct the intended behavior** from the existing docs and snippets.

---

### BEHAVIORAL REQUIREMENTS (WHAT THE CODE MUST DO)

#### 1. Incremental validation via `FileHashCache`

Implement `FileHashCache` so that it:

* Stores a mapping of `{ file_path_str: { "hash": "...", "validated_at": "ISO-UTC" } }` in a JSON file under the engine’s output or state directory (follow the path used in older snippets, e.g. `.validation_cache.json`).

* Uses **SHA-256 content hashes** (as specified in README) for change detection.

* On `has_changed(file_path)`:

  * Compute current hash.
  * Compare to stored hash (if any).
  * Return `True` if no entry or hash changed.
  * Return `False` if identical.

* On `mark_validated(file_path)`:

  * Recompute hash.
  * Update in-memory cache.
  * Persist to disk via `save()`.

`load()` / `save()`:

* Should be **robust**:

  * If file doesn’t exist → start with empty cache (no exceptions).
  * If JSON is corrupt → log a warning, back up the bad file (e.g., `.bak`), start a fresh cache.

The **engine** should use this cache as follows:

* If incremental enabled and `has_changed(file_path)` is `False`:

  * Log a “skipped (unchanged)” message.
  * Return a `PipelineReport` whose status clearly indicates **skipped** and includes the reason.

#### 2. Plugin execution ordering & selection

In `PipelineEngine._run_plugins`:

* Ask the `PluginManager` for applicable plugins:

  * `plugins = self._plugin_manager.get_plugins_for_file(file_path)`
* The manager already:

  * Filters by file type using `plugin.can_process(file_path)`.
  * Applies execution ordering via `execution_order` and/or DAG dependencies (`requires`) as described in `errorfixpipleinechat.txt`.

`_run_plugins` must:

* Iterate plugins **in the order returned** by the manager.

* For each plugin:

  * Call `plugin.execute(temp_file_or_file_path)` to obtain a `PluginResult` (see existing types).
  * Collect:

    * `success`
    * `errors` (list of error objects)
    * `auto_fixed_count`
    * `execution_time`
    * `stdout`, `stderr` (if available)

* Aggregate all `PluginResult` objects into a list for later reporting.

**No network access** should be introduced here; the plugins themselves already scrub proxies and use local tools only (per existing design).

#### 3. Temp-dir isolation & output file naming

Recreate the behavior shown in the older `PipelineEngine` snippets:

* For each `process_file` call:

  * Generate a `run_id` (ULID, as per README).
  * Create a unique temp directory.
  * Copy the original file into that temp dir.
  * Run plugins against the **temp copy**.
  * After validation, copy the temp file to the output folder:

    * Name pattern:
      `{original_stem}_VALIDATED_{UTC_TIMESTAMP}_{RUNID6}{original_suffix}`

The original input file must **never be modified in place**.

#### 4. Report generation (`_generate_report`)

Use `PipelineReport` / `PluginResult` types from `src/utils/types.py` as the **ground truth schema**.

`_generate_report` should:

* Construct a report object with at least:

  * `run_id`
  * `file_in` (original path)
  * `file_out` (validated file path or `None` if skipped / failed)
  * `timestamp_utc` (ISO 8601, UTC)
  * `toolchain` (map of plugin/tool names → versions, if available from plugins)
  * `summary`:

    * `plugins_run`
    * `total_errors`
    * `total_warnings`
    * `auto_fixed`
  * `plugin_results`:

    * For each plugin:

      * `plugin_id`
      * `name`
      * `success`
      * `errors` (normalized dicts; use existing `_error_to_dict` helper if present in older snippets)
      * `auto_fixed_count`
      * `execution_time`
* If the file was **skipped** by the hash cache:

  * `summary` should indicate 0 plugins run, 0 errors, reason: `unchanged`.
* If plugin execution fails catastrophically, produce a report with:

  * `status` or equivalent field set to `failed`.
  * A top-level error message.

This report should be suitable as a **single source of truth** for both the GUI and any higher-level error pipeline system.

#### 5. JSON + JSONL persistence

Integrate with the existing JSONL manager design:

* For each processed file:

  * Write a **per-file JSON report** alongside the validated output (e.g., `<output_file>.json`).
  * Append a line to a **global JSONL file** (e.g., `pipeline_errors.jsonl`) managed by `JSONLManager`:

    * Respect the ~75KB rotation behavior described in `errorfixpipleinechat.txt` and `ARCHITECTURE.md`.
    * Ensure that rotation keeps most recent entries and never corrupts the file.

Implementation detail:

* `PipelineEngine.process_file` is responsible for:

  * Writing the JSON report.
  * Calling JSONL manager to append aggregated error records (per error or per file; follow the prior design in `errorfixpipleinechat.txt`).

#### 6. Determinism & robustness

Honor the design principles from README / ARCHITECTURE:

* Determinism:

  * Stable plugin ordering (delegated to `PluginManager`).
  * Content hashing for incremental logic.
  * ULID + UTC timestamps.
  * No random/uncontrolled env behavior.
* Isolation:

  * Temp directories for validation.
  * No in-place edits to original files.
* Atomicity:

  * Avoid partially written JSON/JSONL files.
  * If write fails, log error and avoid corrupting existing logs.

---

### IMPLEMENTATION PLAN (STEP-BY-STEP FOR THE AI)

1. **Confirm project root**

   * Locate the folder containing `ERROR_PIPELINE_MOD_README.md` and `ARCHITECTURE.md`.
   * Treat that as `<PROJECT_ROOT>`.

2. **Scan current code and types**

   * Open:

     * `src/core/pipeline_engine.py`
     * `src/core/file_hash_cache.py`
     * `src/core/plugin_manager.py`
     * `src/utils/jsonl_manager.py`
     * `src/utils/types.py`
   * Identify existing dataclasses/types:

     * `PipelineReport`
     * `PluginResult`
     * Any `Error`/`ValidationError` type and helper functions (`_error_to_dict`, etc.).

3. **Reconstruct intended behavior from docs**

   * Read **`ARCHITECTURE.md`** sections that describe:

     * Pipeline engine responsibilities.
     * Output artifacts (JSON, JSONL).
     * Incremental validation and hash cache.
   * Read relevant fragments in **`errorfixpipleinechat.txt`** that show:

     * Old `PipelineEngine` implementation.
     * Old `FileHashCache` behavior.
     * JSONL manager details.

4. **Implement `FileHashCache`**

   * Choose the cache file location as per prior design (e.g., `<output_folder>/.validation_cache.json` or `state/validation_hash_cache.json`).
   * Implement `load()`, `save()`, `has_changed()`, and `mark_validated()` exactly as described in the **Incremental validation** section above.
   * Add logging for:

     * Cache file load success/failure.
     * Hash changes.
     * Cache resets due to corruption.

5. **Wire incremental logic into `PipelineEngine.process_file`**

   * Add a boolean `enable_incremental` flag to `PipelineEngine` (if missing), default `True`, with an internal `FileHashCache` instance when enabled.
   * At the start of `process_file`:

     * If incremental enabled and `has_changed(file_path)` is `False`:

       * Log and return a “skipped/unchanged” `PipelineReport`.
   * Otherwise:

     * Generate `run_id`, create temp dir, copy file, and proceed with plugin execution.

6. **Implement `_run_plugins`**

   * Use `PluginManager.get_plugins_for_file(temp_file)` to get plugins.
   * For each plugin:

     * Call `plugin.execute(temp_file)`.
     * Collect a `PluginResult`.
   * Return a list of `PluginResult` instances.

7. **Implement `_generate_report`**

   * Take the list of `PluginResult` objects and construct a `PipelineReport`:

     * Use the fields described above.
     * Derive summary counts (`total_errors`, etc.) from the plugin results.
   * Keep field names and types aligned with `PipelineReport` in `src/utils/types.py`.

8. **Integrate JSON / JSONL output**

   * In `process_file`:

     * After generating the report, write it to a JSON file next to the output file.
     * Use `JSONLManager` to append a normalized record for this file (or each error) to the global JSONL log.
   * Ensure rotation logic is respected and that JSONL operations are atomic.

9. **Mark file as validated**

   * At the end of a successful validation (not skipped, not failed infrastucture), call `hash_cache.mark_validated(original_file_path)` and `hash_cache.save()`.

10. **Add or update tests**

* Under `tests/` (e.g., `tests/test_pipeline_engine.py`, `tests/test_file_hash_cache.py`):

  * Add minimal tests that cover:

    * `FileHashCache.has_changed()` behavior.
    * `PipelineEngine.process_file()`:

      * Executes plugins and produces reports.
      * Skips unchanged files when incremental is enabled.
    * JSON report file and JSONL entry creation.

11. **Run quality tools (if available)**

* If `ruff`, `black`, `pytest` are installed:

  * Run `ruff` on relevant modules.
  * Run `black` to format.
  * Run `pytest` to ensure tests pass.

---

### DONE CRITERIA

This workstream is **complete** when:

1. `PipelineEngine.process_file`, `_run_plugins`, and `_generate_report` are fully implemented and match the behavior described in README + ARCHITECTURE + historic snippets.
2. `FileHashCache` correctly detects unchanged files and the engine skips them with a clear “skipped/unchanged” report.
3. Processing a file through the GUI or a small CLI harness:

   * Produces:

     * A validated copy in the output folder with `_VALIDATED_<UTC>_<RID6>` naming.
     * A JSON report next to that file.
     * An appended entry in `pipeline_errors.jsonl` (or equivalent).
4. Basic tests for hash cache and engine pass.
5. No regression of the core design principles:

   * Determinism.
   * Isolation.
   * Atomicity.
   * Reproducibility.

---

If you want, next step we can do a **second workstream spec** that takes this engine and wires it into your **AI error pipeline state machine** (Aider → Codex → Claude) using `ERROR_Operating Contract.txt` and the SQLite state layer, but this one is just about getting the core engine rock solid.
