---
doc_id: DOC-GUIDE-SECOND-WORKSTREAM-SPEC-1130
---


Here’s the **second workstream spec** you asked for – written so you can drop it straight into Codex or Claude Code as a single `.md` workstream file.

I’m assuming **Workstream 1** already turned the old plugin-based engine (`pipeline_engine.py`, `plugin_manager.py`, `file_router.config.json`, etc.) into a **canonical error engine** that can run all your Python/PowerShell validators and emit normalized error JSON.

This **Workstream 2** takes that engine and **wires it into**:

* The **Code Quality Escalation state machine** (S_INIT → … → S_SUCCESS / S4_QUARANTINE / S_ERROR_INFRA).
* The **shared context object** (context, error_reports, ai_attempts).
* The **SQLite state layer & data model** (runs, workstreams, step_attempts, errors, events).

---

````markdown
---
doc_type: workstream_spec
doc_key: WS-ERROR-PIPELINE-WIREUP
version: 0.1.0
status: draft
owner: pipeline.architecture
phase: PH-06_Error_Escalation
target_agents:
  - codex
  - claude-code
upstream:
  - WS-ERROR-ENGINE-CORE        # workstream 1: canonical error engine
  - OC-CODEQ-ESCALATION         # ERROR_Operating Contract.txt
  - PH-02_Data_Model_SQLite_State_Layer
  - PH-03_Tool_Profiles_Adapter_Layer
related_docs:
  - state-machine specification.txt
  - full trip through the pipeline.txt
---

# WS-ERROR-PIPELINE-WIREUP
## Wire the canonical error engine into the AI error pipeline state machine (Aider → Codex → Claude)

### 0. Role & Mode

You are implementing **plumbing and orchestration**, not inventing new behavior.

- **Codex / Claude role** under this spec:
  - Realize the **Code Quality Escalation state machine** in code.
  - Persist & load the **shared context** using the **SQLite state layer**.
  - Wrap the existing **canonical error engine** so it:
    - Reads `run_id` / `workstream_id` context.
    - Runs all configured tools via the PH-03 Tool Adapter.
    - Emits normalized JSON error reports and logs into SQLite and disk.
- You MUST follow the **Operating Contract** for data shapes, states, and behavior; this spec just tells you how to wire it into this repo.

---

## 1. Scope

### 1.1 In-scope

1. **Context → SQLite mapping**
   - Store and retrieve the **Code Quality Escalation context** from the existing DB schema (no breaking schema changes).  
2. **Error engine integration**
   - Wrap the **canonical error engine** from WS-ERROR-ENGINE-CORE behind a single entrypoint:
     - Conceptually: `run_error_pipeline(python_files, powershell_files, ctx) -> dict`.  
3. **State machine service**
   - Implement a **service module** that:
     - Loads context from SQLite.
     - Applies the **CodeQualityEscalationStateMachine** transitions.  
     - Decides when to:
       - Run baseline error pipeline.
       - Run mechanical autofix.
       - Hand off to Aider, Codex, or Claude.
       - Quarantine or finalize.
4. **Single-step “tick” controller**
   - A CLI / function that advances **one step** of the state machine for a given `(run_id, workstream_id)`.
5. **Event & error logging**
   - Use existing `events` and `errors` tables to log:
     - State transitions.
     - Error pipeline runs.
     - AI attempts and finalization.  

### 1.2 Out-of-scope (for this workstream)

- Designing detailed **Aider / Codex / Claude prompt templates** (those live in PH-03.5 / prompt system).
- Implementing the Aider CLI integration itself (shell commands, flags).
- Outer orchestrator, scheduler, or multi-workstream DAG (PH-04+).

This workstream focuses on the **internal quality pipeline**: context ↔ SQLite ↔ state machine ↔ error engine.

---

## 2. Required Context (LOAD THESE FILES FIRST)

When you start this workstream, **load these documents into context**:

1. **Error pipeline architecture & engine**
   - `ARCHITECTURE.md`
   - `ERROR_PIPELINE_MOD_README.md`
   - `pipeline_engine.py`
   - `plugin_manager.py`
   - `file_router.config.json`
   - `file_hash_cache.py`  

2. **State machine & contract**
   - `ERROR_Operating Contract.txt` (OC-CODEQ-ESCALATION).  
   - `state-machine specification.txt` (CodeQualityEscalationStateMachine).
   - `full trip through the pipeline.txt` (end-to-end artifact flow).  

3. **SQLite / DB layer**
   - `PH-02_Data Model, SQLite State Layer & State Machine (Codex Autonomous Phase Executor).md`
   - `Data Flow Analysis.md` (tables: `runs`, `workstreams`, `step_attempts`, `errors`, `events`).  

4. **Tool adapter**
   - `PH-03_Tool Profiles & Adapter Layer (Codex Autonomous Phase Executor).md` (for `run_tool(...)` conventions).  

---

## 3. Target File Layout (what you will create / edit)

> Adjust exact module names to match the existing Python package layout, but keep responsibilities as described.

**New / modified modules (Python)**

- `src/pipeline/error_context.py`
  - Context dataclass / helpers for the **Code Quality Escalation context** (mirrors contract’s context YAML).  
- `src/pipeline/error_state_machine.py`
  - Pure state machine logic (no I/O).
- `src/pipeline/error_pipeline_service.py`
  - Glue between:
    - `error_context`
    - `error_state_machine`
    - Canonical error engine (`run_error_pipeline(...)`).
    - SQLite DB layer (`db.py` or equivalent).
- `src/pipeline/error_pipeline_cli.py`
  - CLI / entrypoint exposing a **single-step “tick”** command.
- `src/pipeline/db.py` (or equivalent existing DB module)
  - Add helpers to persist context and error reports.
- Tests:
  - `tests/test_error_context.py`
  - `tests/test_error_state_machine.py`
  - `tests/test_error_pipeline_service.py`

---

## 4. Step-by-Step Tasks

### 4.1 Define the in-memory Error Context model

**Goal:** Represent the **Code Quality Escalation context** as a Python object that matches the Operating Contract.  

1. In `src/pipeline/error_context.py`:
   - Create a dataclass or equivalent named `ErrorPipelineContext` with at least:

     - Identity:
       - `run_id: str`
       - `workstream_id: str`

     - Target files:
       - `python_files: list[str]`
       - `powershell_files: list[str]`

     - Config:
       - `enable_mechanical_autofix: bool`
       - `enable_aider: bool`
       - `enable_codex: bool`
       - `enable_claude: bool`
       - `strict_mode: bool`
       - `max_attempts_per_agent: int`

     - Attempt metadata:
       - `attempt_number: int` (0=baseline,1=aider,2=codex,3=claude)
       - `current_agent: str` (`"none"|"aider"|"codex"|"claude"`)
       - `mechanical_fix_applied: bool`

     - Error reports:
       - `last_error_report: dict | None`
       - `previous_error_report: dict | None`

     - AI attempts:
       - `ai_attempts: list[dict]`

     - Finalization:
       - `final_status: str | None` (`"success"|"quarantined"|"infra_failure"`)
       - `quarantine_path: str | None`

2. Add helper methods:

   - `to_json()` / `from_json()`:
     - Serialize/deserialize to a plain dict JSON compatible with SQLite `metadata_json`.

   - `record_ai_attempt(attempt_dict: dict)`:
     - Append AI attempt entries (matching the AI Attempt Log schema: `attempt_number`, `agent`, `input_error_report_id`, `changed_files`, `notes`).  

   - `update_error_reports(new_report: dict)`:
     - Shift `last_error_report` → `previous_error_report`.
     - Set new `last_error_report`.

---

### 4.2 Map Error Context into SQLite

**Goal:** Persist `ErrorPipelineContext` using existing tables (`workstreams.metadata_json`, `step_attempts`, `events`, `errors`).  

1. In `src/pipeline/db.py`:

   - Implement:

     ```python
     def get_error_context(run_id: str, ws_id: str) -> ErrorPipelineContext: ...
     def save_error_context(ctx: ErrorPipelineContext) -> None: ...
     ```

   - Storage convention:

     - Use `workstreams.metadata_json` (or equivalent JSON field) for an `error_pipeline` sub-object, e.g.:

       ```jsonc
       {
         "error_pipeline": {
           "...": "serialized ErrorPipelineContext"
         },
         "other_metadata": "..."
       }
       ```

   - Behavior:

     - If no context exists for `(run_id, ws_id)`:
       - Initialize a new `ErrorPipelineContext` from defaults in the contract (enabled tools, tiers, strict mode).  
       - Set `current_state = "S0_BASELINE_CHECK"` in SQLite (appropriate column or metadata).  

2. Error report persistence:

   - Add helper:

     ```python
     def record_error_report(
         ctx: ErrorPipelineContext,
         report: dict,
         step_name: str,
     ) -> None:
         ...
     ```

   - This function MUST:

     - Write `report` to disk under a stable path:

       - `state/error_reports/<run_id>/<workstream_id>/error_report_attempt_<attempt_number>.json`.  

     - Insert a row into `step_attempts` with:

       - `run_id`, `ws_id`
       - `step_name` (e.g. `"error_pipeline_baseline"` / `"error_pipeline_recheck"`)
       - `result_json` containing summarized report data.

     - Insert a row into `events` with:

       - `event_type = "error_report_generated"`
       - `payload_json` including `attempt_number`, `ai_agent`, summary totals.  

3. AI attempt persistence:

   - Add helper:

     ```python
     def record_ai_attempt(ctx: ErrorPipelineContext, attempt: dict) -> None:
         ...
     ```

   - Behavior:

     - Append to `ctx.ai_attempts`.
     - Insert `events` row with `event_type = "ai_attempt"` and payload = attempt.
     - Optionally increment a deduplicated counter in `errors` if repeated failures.  

---

### 4.3 Wrap the canonical error engine as `run_error_pipeline(...)`

**Goal:** Make the existing plugin-based engine conform to the **canonical error pipeline contract**.  

1. Locate or create `src/pipeline/error_engine.py` (or equivalent) that exposes:

   ```python
   def run_error_pipeline(
       python_files: list[str],
       powershell_files: list[str],
       ctx: ErrorPipelineContext,
   ) -> dict:
       """
       Runs all configured tools (Ruff, Black check, Mypy, pytest, PSScriptAnalyzer, Pester, etc.)
       via the PH-03 Tool Adapter and returns a JSON-serializable error report
       matching the normalized schema.
       """
````

2. Internals:

   * Use the **plugin-based engine** (`PipelineEngine`, `PluginManager`, `file_router.config.json`) to actually run tools and bridge to the tool adapter.
   * Normalize the result into the **Error Report schema**:

     * Top-level fields:

       * `attempt_number`
       * `ai_agent`
       * `run_id`
       * `workstream_id`
       * `issues` (list with `tool`, `path`, `line`, `column`, `code`, `category`, `severity`, `message`).
       * `summary` block: `total_issues`, `issues_by_tool`, `issues_by_category`, `has_hard_fail`, `style_only`.

3. This function MUST:

   * Write the report to disk with the standard filename.
   * Update `ctx.error_reports.last_error_report`.
   * Return the full report dict to the caller.
   * Not change `current_state` itself (that’s handled by the state machine).

---

### 4.4 Implement the Code Quality Escalation state machine

**Goal:** Implement the **finite state machine** in a pure service module.

1. In `src/pipeline/error_state_machine.py`:

   * Define constants for all states:

     * `S_INIT`
     * `S0_BASELINE_CHECK`
     * `S0_MECHANICAL_AUTOFIX`
     * `S0_MECHANICAL_RECHECK`
     * `S1_AIDER_FIX`
     * `S1_AIDER_RECHECK`
     * `S2_CODEX_FIX`
     * `S2_CODEX_RECHECK`
     * `S3_CLAUDE_FIX`
     * `S3_CLAUDE_RECHECK`
     * `S4_QUARANTINE`
     * `S_SUCCESS`
     * `S_ERROR_INFRA`

   * Implement a pure function (no DB / file I/O):

     ```python
     class NextAction(NamedTuple):
         new_state: str
         action: str  # e.g. "RUN_PIPELINE", "MECHANICAL_AUTOFIX", "CALL_AIDER", "CALL_CODEX", "CALL_CLAUDE", "QUARANTINE", "FINALIZE_SUCCESS", "FINALIZE_INFRA_ERROR"

     def decide_next_action(ctx: ErrorPipelineContext) -> NextAction:
         ...
     ```

2. Implement the transition logic consistent with the Operating Contract:

   * `S_INIT` → initialize context and move to `S0_BASELINE_CHECK`.

   * `S0_BASELINE_CHECK`:

     * Action: `RUN_PIPELINE`.
     * After pipeline:

       * If no blocking issues and policy allows style-only → `S_SUCCESS`.
       * If style-only issues and mechanical autofix enabled → `S0_MECHANICAL_AUTOFIX`.
       * If hard fails and AIs enabled → `S1_AIDER_FIX` OR `S2_CODEX_FIX` / `S3_CLAUDE_FIX` depending on which tiers are enabled.
       * If no AI tiers enabled → `S4_QUARANTINE`.

   * `S0_MECHANICAL_AUTOFIX`:

     * Action: `MECHANICAL_AUTOFIX`.
     * Next: `S0_MECHANICAL_RECHECK`.

   * `S0_MECHANICAL_RECHECK`:

     * Action: `RUN_PIPELINE`.
     * Similar branching to baseline.

   * `S1_AIDER_FIX` / `S2_CODEX_FIX` / `S3_CLAUDE_FIX`:

     * Action: `CALL_AIDER` / `CALL_CODEX` / `CALL_CLAUDE`.
     * Next: respective `*_RECHECK` state.

   * `S1_AIDER_RECHECK` / `S2_CODEX_RECHECK` / `S3_CLAUDE_RECHECK`:

     * Action: `RUN_PIPELINE`.
     * On clean → `S_SUCCESS`.
     * On remaining issues:

       * Escalate to next tier if enabled.
       * Else → `S4_QUARANTINE`.

   * `S4_QUARANTINE` / `S_SUCCESS` / `S_ERROR_INFRA`:

     * Final states; `decide_next_action` returns actions like `QUARANTINE`, `FINALIZE_SUCCESS`, or `FINALIZE_INFRA_ERROR`.

3. Enforce behavioral rules:

   * **No skipping states** (e.g., must go through `*_RECHECK` after any fix).
   * Deterministic: same context → same decision.
   * All decisions based on **canonical error pipeline runs**, not AI’s internal lint-only loops.

---

### 4.5 Implement the Error Pipeline Service (wire DB + state machine + engine)

**Goal:** Provide a single function that advances one step for `(run_id, workstream_id)`.

1. In `src/pipeline/error_pipeline_service.py`:

   * Implement:

     ```python
     def run_error_pipeline_step(run_id: str, ws_id: str) -> None:
         """
         Load context from SQLite, decide what to do next using the state machine,
         execute that action (error pipeline or mechanical/AI placeholders),
         update context, persist to SQLite, and log events.
         """
     ```

2. Inside this function:

   1. **Load context & state**

      * Fetch `ErrorPipelineContext` via `get_error_context(...)`.
      * Read current state (`ctx.current_state` from SQLite or metadata).

   2. **Decide next action**

      * Call `decide_next_action(ctx)` to get `NextAction`.

   3. **Execute action**

      * If `RUN_PIPELINE`:

        * Call `run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)`.
        * Call `ctx.update_error_reports(report)` and `record_error_report(ctx, report, step_name)`.

      * If `MECHANICAL_AUTOFIX`:

        * Call a **mechanical autofix helper** (Black/ruff `--fix` etc.) using PH-03’s tool adapter or plugin engine.
        * Set `ctx.attempt.mechanical_fix_applied = True`.

      * If `CALL_AIDER` / `CALL_CODEX` / `CALL_CLAUDE`:

        * For this workstream, it is sufficient to:

          * Record an `events` row (`event_type = "ai_action_required"`, payload includes state and tier).
          * (Optionally) leave TODO hooks where prompt builders / CLI adapters will be plugged in by PH-03.5.
        * **Do not** attempt to call these tools directly here yet.

      * If `QUARANTINE`:

        * Create quarantine folder and write artifacts as described in the Operating Contract:

          * `final_scripts/`
          * All `error_report_attempt_*.json`
          * `ai_attempts.json`
          * `metadata.json` capturing `final_status`, enabled tools, tiers, timestamps.

      * If `FINALIZE_SUCCESS`:

        * Mark `final_status = "success"`.
        * Optionally persist final clean error report path.

      * If `FINALIZE_INFRA_ERROR`:

        * Log infra error, set `final_status = "infra_failure"`, and stop.

   4. **Apply transition & persist**

      * Update `ctx` and `current_state` to `NextAction.new_state`.
      * Call `save_error_context(ctx)`.
      * Insert `events` row with `event_type = "state_transition"` and payload containing:

        * `from_state`, `to_state`, `attempt_number`, `current_agent`.

---

### 4.6 CLI entrypoint

**Goal:** Provide a simple CLI hook to run **one step** of the error pipeline.

1. In `src/pipeline/error_pipeline_cli.py`:

   * Implement a click/argparse-based CLI with command:

     ```bash
     pipeline error-step --run-id RUN123 --ws-id ws-error-001
     ```

   * It should:

     * Parse args.
     * Call `run_error_pipeline_step(run_id, ws_id)`.
     * Print a concise summary of:

       * Previous state → new state.
       * Whether an error report was generated.
       * Whether AI action is required.

2. Wire this into packaging (later PH-10) as a console_script; for now, just keep module-level `if __name__ == "__main__":` bootstrapping.

---

## 5. Testing & Validation

### 5.1 Unit tests

Create tests that simulate the most important flows using **in-memory or temporary SQLite DBs**:

1. **Baseline success path**

   * Context with no issues (mocked error engine returns `total_issues = 0`, `has_hard_fail = false`).
   * Verify:

     * `S0_BASELINE_CHECK` → `S_SUCCESS`.
     * `final_status = "success"`.
     * Final error report persisted and linked.

2. **Escalation path (Aider → Codex → Claude)**

   * Mock error engine to:

     * Attempt 0: hard errors present.
     * Attempt 1 (after Aider): fewer errors but still hard errors.
     * Attempt 2 (after Codex): still errors.
     * Attempt 3 (after Claude): either success or remaining errors.
   * Verify correct state transitions and that AI attempts are logged with correct `attempt_number` and `agent`.

3. **Quarantine path**

   * Disable some or all AI tiers or force persistent failures.
   * Ensure:

     * State ends at `S4_QUARANTINE`.
     * Quarantine folder is created with required files.

4. **Infra error path**

   * Simulate tool adapter failure / DB failure.
   * Ensure:

     * State ends at `S_ERROR_INFRA`.
     * Corresponding `events` and `errors` rows exist.

### 5.2 Behavioral checks (contract compliance)

* Verify that:

  * No transition skips `*_RECHECK` states after any fix.
  * Every AI attempt is followed by a full error pipeline run before state advancement.
  * All decisions about success/quarantine are based on canonical error reports.

---

## 6. Done criteria (for this workstream)

This workstream is **complete** when:

1. You can run:

   ```bash
   pipeline error-step --run-id DEMO-RUN --ws-id ws-error-demo
   ```

   and see the state advance according to the Operating Contract for at least:

   * Baseline success path.
   * Aider → Codex → Claude escalation path (with mocked AI behaviors).
   * Quarantine path.

2. SQLite contains:

   * `workstreams.metadata_json.error_pipeline` with serialized context.
   * `step_attempts` rows for each error pipeline run.
   * `events` rows for `state_transition`, `error_report_generated`, and `ai_attempt` events.

3. Disk contains:

   * `state/error_reports/<run_id>/<ws_id>/error_report_attempt_<n>.json` files.
   * For quarantine cases, a full quarantine bundle as specified in the Operating Contract.

4. Tests:

   * Unit tests for context, state machine, and service are passing.
   * At least one test validates that the implementation remains consistent with `ERROR_Operating Contract.txt` and `full trip through the pipeline.txt` (e.g., via fixture snapshots of context + reports).

---

*End of WS-ERROR-PIPELINE-WIREUP spec.*

```
```
