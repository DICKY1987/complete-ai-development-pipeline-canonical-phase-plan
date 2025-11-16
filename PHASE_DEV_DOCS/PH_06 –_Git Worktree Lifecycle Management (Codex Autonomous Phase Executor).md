TITLE: PH-06 – Circuit Breakers, Retries & Fix Loop (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-06 (Circuit Breakers, Retries & Fix Loop) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Implement a generic circuit_breakers module and YAML config.
- Add FIX loops around STATIC and RUNTIME steps using Aider.
- Use error signatures and attempt counts to decide whether to keep retrying or stop.
- Detect oscillation via diff hashes and trip breakers cleanly.
- Wire this into the existing orchestrator without implementing crash-resume or multi-workstream scheduling (those are later phases).

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git (worktree enabled)
- Orchestrator language: Python 3.12+

Previous phases (assumed available and not to be broken):
- PH-00: Baseline & project skeleton
  - Repo: C:\Users\richg\ALL_AI\AI_Dev_Pipeline
  - src/pipeline/, tests/pipeline/, scripts/, docs/, config/
- PH-01: Spec alignment & module stubs
- PH-02: SQLite state layer & state machine
  - src/pipeline/db.py
  - Tables: runs, workstreams, step_attempts, errors, events
- PH-03: Tool profiles & adapter
  - config/tool_profiles.json
  - src/pipeline/tools.py with run_tool()
- PH-03.5: Aider integration & prompt engine
  - docs/aider_contract.md
  - src/pipeline/prompts.py
  - helpers such as run_aider_edit(...) and run_aider_fix(...)
- PH-04: Workstream bundle parsing & validation
  - schema/workstream.schema.json, src/pipeline/bundles.py
- PH-04.5: Git worktree lifecycle
  - src/pipeline/worktree.py (.worktrees/<ws-id>, scope validation)
- PH-05: Orchestrator core loop (single workstream)
  - src/pipeline/orchestrator.py
  - EDIT → STATIC → RUNTIME sequence, no FIX loop yet
- PH-05.5: Workstream authoring & validation
  - docs/workstream_authoring_guide.md
  - templates/workstream_template.json
  - scripts/validate_workstreams_authoring.py

PROJECT ROOT (IMPORTANT)
- Expected project root: C:\Users\richg\ALL_AI\AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-06 that PH-00–PH-05.5 must be completed first.
- Do NOT implement circuit breakers anywhere else.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-06
====================================

Make the EDIT/STATIC/FIX pipeline robust by adding:

1) **Error signatures & counters**
   - Stable signatures derived from error_code + normalized error text.
   - Counters stored in the `errors` table so patterns can be detected.

2) **FIX loop around STATIC and RUNTIME**
   - When STATIC or RUNTIME fails:
     - Build a FIX prompt from error list.
     - Call Aider to attempt a repair.
     - Re-run STATIC or RUNTIME.
   - Repeat until:
     - Success, OR
     - Circuit breaker trips.

3) **Circuit breaker configuration**
   - Configurable thresholds in config/circuit_breakers.yaml:
     - Max attempts per step.
     - Max attempts per error signature.
     - Oscillation threshold (same diff repeating).

4) **Oscillation detection**
   - Hash diffs between attempts.
   - Detect repeated patterns and trip breakers when we’re “stuck”.

NO crash-resume (PH-06.5) and NO multi-workstream scheduling/parallelism (PH-07). This phase only strengthens a **single-workstream** loop with FIX and circuit breakers.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-06, the repo MUST have at minimum:

1) CIRCUIT BREAKER CONFIG
- File: config/circuit_breakers.yaml

Define a simple, explicit schema, e.g.:

```yaml
defaults:
  max_attempts_per_step: 3          # total STATIC or RUNTIME attempts (including the first one)
  max_fix_attempts_per_step: 2      # number of FIX retries allowed after the initial failure
  max_attempts_per_error_signature: 3
  oscillation_window: 4             # how many recent attempts to inspect
  oscillation_threshold: 2          # how many repeated diff hashes in that window triggers oscillation
  enable_fix_for_steps:
    - static
    - runtime

per_step:
  static:
    max_attempts_per_step: 3
    max_fix_attempts_per_step: 2
  runtime:
    max_attempts_per_step: 2
    max_fix_attempts_per_step: 1
Here’s a ready-to-paste Codex prompt for **PH-06 – Circuit Breakers, Retries & Fix Loop**.

````text
TITLE: PH-06 – Circuit Breakers, Retries & Fix Loop (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-06 (Circuit Breakers, Retries & Fix Loop) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Implement a generic circuit_breakers module and YAML config.
- Add FIX loops around STATIC and RUNTIME steps using Aider.
- Use error signatures and attempt counts to decide whether to keep retrying or stop.
- Detect oscillation via diff hashes and trip breakers cleanly.
- Wire this into the existing orchestrator without implementing crash-resume or multi-workstream scheduling (those are later phases).

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git (worktree enabled)
- Orchestrator language: Python 3.12+

Previous phases (assumed available and not to be broken):
- PH-00: Baseline & project skeleton
  - Repo: C:\Users\richg\ALL_AI\AI_Dev_Pipeline
  - src/pipeline/, tests/pipeline/, scripts/, docs/, config/
- PH-01: Spec alignment & module stubs
- PH-02: SQLite state layer & state machine
  - src/pipeline/db.py
  - Tables: runs, workstreams, step_attempts, errors, events
- PH-03: Tool profiles & adapter
  - config/tool_profiles.json
  - src/pipeline/tools.py with run_tool()
- PH-03.5: Aider integration & prompt engine
  - docs/aider_contract.md
  - src/pipeline/prompts.py
  - helpers such as run_aider_edit(...) and run_aider_fix(...)
- PH-04: Workstream bundle parsing & validation
  - schema/workstream.schema.json, src/pipeline/bundles.py
- PH-04.5: Git worktree lifecycle
  - src/pipeline/worktree.py (.worktrees/<ws-id>, scope validation)
- PH-05: Orchestrator core loop (single workstream)
  - src/pipeline/orchestrator.py
  - EDIT → STATIC → RUNTIME sequence, no FIX loop yet
- PH-05.5: Workstream authoring & validation
  - docs/workstream_authoring_guide.md
  - templates/workstream_template.json
  - scripts/validate_workstreams_authoring.py

PROJECT ROOT (IMPORTANT)
- Expected project root: C:\Users\richg\ALL_AI\AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-06 that PH-00–PH-05.5 must be completed first.
- Do NOT implement circuit breakers anywhere else.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-06
====================================

Make the EDIT/STATIC/FIX pipeline robust by adding:

1) **Error signatures & counters**
   - Stable signatures derived from error_code + normalized error text.
   - Counters stored in the `errors` table so patterns can be detected.

2) **FIX loop around STATIC and RUNTIME**
   - When STATIC or RUNTIME fails:
     - Build a FIX prompt from error list.
     - Call Aider to attempt a repair.
     - Re-run STATIC or RUNTIME.
   - Repeat until:
     - Success, OR
     - Circuit breaker trips.

3) **Circuit breaker configuration**
   - Configurable thresholds in config/circuit_breakers.yaml:
     - Max attempts per step.
     - Max attempts per error signature.
     - Oscillation threshold (same diff repeating).

4) **Oscillation detection**
   - Hash diffs between attempts.
   - Detect repeated patterns and trip breakers when we’re “stuck”.

NO crash-resume (PH-06.5) and NO multi-workstream scheduling/parallelism (PH-07). This phase only strengthens a **single-workstream** loop with FIX and circuit breakers.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-06, the repo MUST have at minimum:

1) CIRCUIT BREAKER CONFIG
- File: config/circuit_breakers.yaml

Define a simple, explicit schema, e.g.:

```yaml
defaults:
  max_attempts_per_step: 3          # total STATIC or RUNTIME attempts (including the first one)
  max_fix_attempts_per_step: 2      # number of FIX retries allowed after the initial failure
  max_attempts_per_error_signature: 3
  oscillation_window: 4             # how many recent attempts to inspect
  oscillation_threshold: 2          # how many repeated diff hashes in that window triggers oscillation
  enable_fix_for_steps:
    - static
    - runtime

per_step:
  static:
    max_attempts_per_step: 3
    max_fix_attempts_per_step: 2
  runtime:
    max_attempts_per_step: 2
    max_fix_attempts_per_step: 1
````

Notes/requirements:

* Put all values under `defaults` and allow overrides under `per_step.<step_name>`.
* Steps of interest for now: `static`, `runtime`.
* Document this format in docs/ARCHITECTURE.md and/or a short comment block in the YAML (or a separate small Markdown note).

2. CIRCUIT BREAKERS MODULE

* File: src/pipeline/circuit_breakers.py

Responsibilities:

* Load and validate circuit-breaker config.
* Generate error signatures.
* Compute step and error counts (from DB).
* Decide whether to retry, stop, or trip a breaker.
* Support basic oscillation detection based on diff hashes.

Recommended structure:

* Data structures:

  * CircuitBreakerConfig (dataclass or TypedDict):

    * max_attempts_per_step: int
    * max_fix_attempts_per_step: int
    * max_attempts_per_error_signature: int
    * oscillation_window: int
    * oscillation_threshold: int
  * BreakerDecision (dataclass or TypedDict):

    * should_retry: bool
    * breaker_tripped: bool
    * reason: str
    * data: dict (extra info for logging)

* Public functions:

  1. load_config() -> dict[str, CircuitBreakerConfig]

     * Reads config/circuit_breakers.yaml.
     * Returns a dict keyed by step_name:

       * e.g. {"static": CircuitBreakerConfig(...), "runtime": CircuitBreakerConfig(...)}.
     * Merge:

       * defaults with per_step overrides.
     * Fail fast with clear error if the file is missing or invalid.
     * Cache in module-level variable to avoid re-reading.

  2. make_error_signature(error_code: str, message: str) -> str

     * Normalize message:

       * Lowercase.
       * Strip whitespace.
       * Collapse multiple spaces.
       * Optionally truncate to a safe max length.
     * Return something like: f"{error_code}:{normalized_message_hash_or_prefix}".

  3. get_attempt_counts(db, run_id: str, ws_id: str, step_name: str) -> dict

     * Using db.py:

       * Count total attempts for this (run_id, ws_id, step_name) in `step_attempts`.
       * Count errors per error signature (from `errors` table).
     * Return a dict e.g.:
       {
       "total_attempts": 3,
       "per_signature": {
       "STATIC:Pylint:missing-import": 2,
       ...
       }
       }

  4. should_retry(
     db,
     run_id: str,
     ws_id: str,
     step_name: str,
     error_signatures: list[str],
     recent_diff_hashes: list[str]
     ) -> BreakerDecision

     * Load relevant CircuitBreakerConfig for this step.

     * Read attempt counts via get_attempt_counts().

     * Apply rules:

       * If total_attempts >= max_attempts_per_step:

         * breaker_tripped=True, should_retry=False.

       * For each signature:

         * If per_signature[signature] >= max_attempts_per_error_signature:

           * breaker_tripped=True, should_retry=False.

       * Oscillation detection:

         * Inspect recent_diff_hashes (most recent N = oscillation_window).
         * If any diff hash appears >= oscillation_threshold:

           * breaker_tripped=True, should_retry=False.

       * Otherwise:

         * breaker_tripped=False, should_retry=True.

     * The `reason` field MUST clearly explain why we stopped (which limit, which signature, or oscillation).

  5. record_error_with_signature(
     db,
     run_id: str,
     ws_id: str,
     step_name: str,
     error_code: str,
     message: str,
     context: dict | None = None
     ) -> str

     * Compute signature with make_error_signature().
     * Call db.record_error(...) with:

       * error_code, signature, message, context_json.
     * Return the signature so the caller can include it in StepResult details.

Implementation notes:

* Use only standard library + PyYAML **if** available, or add PyYAML to requirements.txt.
* All functions must be deterministic and side-effect-light (besides DB writes).

3. ORCHESTRATOR FIX LOOP & CIRCUIT BREAKER INTEGRATION

* File to modify: src/pipeline/orchestrator.py

Goal:

* Extend the single-workstream orchestrator to support FIX loops for STATIC and RUNTIME using the PH-03.5 Aider helpers and the new circuit_breakers module.

Key requirements:

1. Introduce a FIX step concept

   * Add a step constant:

     * STEP_FIX = "fix"
   * Add a helper:

     * run_fix_step(run_id, ws_id, bundle, step_name, last_step_errors, context) -> StepResult

       * Uses run_aider_fix(...) from the Aider integration layer.
       * Builds a FIX prompt using:

         * bundle info.
         * `last_step_errors` (list of error dicts).
       * Records:

         * step_attempt for FIX.
         * events for FIX start/end.
       * Returns StepResult with:

         * success: bool
         * details containing e.g. list of applied files, maybe diff_hash.

2. Ensure STATIC and RUNTIME StepResult carry error metadata

   * Modify run_static_step(...) and run_runtime_step(...) so that on failure they populate:

     * details["errors"] = list of { error_code, message, tool_id, optional extra }
     * details["diff_hash"] = hash representing current diff in the worktree (see oscillation section below).
   * On success:

     * details["errors"] may be empty/null.
     * details["diff_hash"] can still be set (optional but useful for debugging).

3. Implement FIX loop per step

   * Wrap the existing STATIC and RUNTIME steps in a retry loop.

   For each step_name in {"static", "runtime"}:

   * Pseudocode sketch (you must implement in real Python):

     def run_step_with_fix(run_id, ws_id, bundle, context, *, step_name: str) -> StepResult:
     # step_name is "static" or "runtime"
     # 1) run the base step once
     base_result = run_static_step(...) or run_runtime_step(...)
     collect current diff_hash into a list for oscillation detection

     ```
     if base_result.success:
         return base_result

     # 2) Otherwise, enter FIX loop
     diff_history = [base_result.details.get("diff_hash")]
     error_signatures = []

     while True:
         # Build error_signatures from base_result.details["errors"] using circuit_breakers.record_error_with_signature(...)
         # Update diff_history as we go

         decision = circuit_breakers.should_retry(
             db,
             run_id,
             ws_id,
             step_name,
             error_signatures,
             recent_diff_hashes=[h for h in diff_history if h]
         )

         if not decision.should_retry:
             # Mark breaker trip via db.record_event(...)
             # Return a failure StepResult with a clear reason
             return StepResult(... success=False, ...)

         # Attempt FIX
         fix_result = run_fix_step(run_id, ws_id, bundle, step_name, last_step_errors, context)

         # If FIX itself fatally fails (e.g., Aider error):
         #   - Optionally call should_retry again (treat as just another failure)
         #   - Or stop immediately (document decision in ARCHITECTURE)
         # For v1.0, you may treat a failed FIX as just another failed attempt that counts towards the limits.

         # Re-run base step
         base_result = run_static_step(...) or run_runtime_step(...)
         diff_hash = base_result.details.get("diff_hash")
         if diff_hash:
             diff_history.append(diff_hash)

         if base_result.success:
             return base_result
     ```

   * The orchestrator’s run_workstream(...) should call:

     * run_step_with_fix(..., step_name="static")
     * run_step_with_fix(..., step_name="runtime")
       instead of the previous one-shot run_static_step/run_runtime_step.

4. Oscillation detection via diff hashing

   * Implement a small helper in orchestrator or worktree.py:

     * compute_diff_hash(ws_id, base_branch, files_scope=None) -> str

       * From the worktree for ws_id:

         * Use git to compute a textual diff (e.g., `git diff <base_branch>..HEAD`).
       * Optionally restrict to files_scope (nice-to-have).
       * Hash with SHA-256.
       * Return hex digest.

   * run_static_step and run_runtime_step should:

     * Call compute_diff_hash(...) and store the result in StepResult.details["diff_hash"].

   * The FIX loop passes the list of recent diff hashes to circuit_breakers.should_retry(...).

   * If the same diff hash appears oscillation_threshold times in the last oscillation_window attempts:

     * should_retry returns breaker_tripped=True, with reason "oscillation_detected".

   * Log this via db.record_event(run_id, ws_id, "circuit_breaker_oscillation", payload_json).

5. DB integration & logging

   * Continue using db.py for:

     * record_step_attempt(...)
     * record_error(...)
     * record_event(...)
     * update_workstream_status(...)

   * Add new event types:

     * "fix_step_started", "fix_step_completed"
     * "circuit_breaker_tripped"
     * "oscillation_detected"

   * On breaker trip:

     * Update workstream status to "failed".
     * Include decision.reason in context_json of db.record_error or db.record_event.

IMPORTANT: Do NOT add crash-resume logic or new run-level states here. Only step-level FIX loops and circuit breaker decisions.

4. UNIT TESTS FOR CIRCUIT BREAKERS & FIX LOOP

* New tests:

  * tests/pipeline/test_circuit_breakers.py
  * tests/pipeline/test_orchestrator_fix_loop.py

You can also extend existing orchestrator tests if they already cover parts of this.

Focus on 2 layers:

A) circuit_breakers.py (pure logic tests)

* For test_circuit_breakers.py:

  * Use an in-memory or temporary DB and/or stubbed db object.
  * Tests should cover:

    1. make_error_signature:

       * Same (error_code, message) → same signature.
       * Insignificant whitespace or case changes do not change signature.
       * Different error_code or substantially different message → different signature.

    2. get_attempt_counts:

       * Insert multiple step_attempts and errors into the temp DB.
       * Ensure counts match expectations.

    3. should_retry:

       * Scenario: Under attempt and signature limits:

         * should_retry=True, breaker_tripped=False.
       * Scenario: total attempts >= max_attempts_per_step:

         * should_retry=False, breaker_tripped=True, reason mentions "max_attempts_per_step".
       * Scenario: per signature >= max_attempts_per_error_signature:

         * should_retry=False, breaker_tripped=True, reason mentions that signature.
       * Scenario: oscillation:

         * Provide repeated diff hashes in recent_diff_hashes meeting the threshold.
         * should_retry=False, breaker_tripped=True, reason mentions oscillation.

B) Orchestrator FIX loop integration

* For test_orchestrator_fix_loop.py:

  * Use pytest with monkeypatch/mocks for:

    * run_static_step / run_runtime_step
    * run_fix_step
    * circuit_breakers.should_retry
    * circuit_breakers.record_error_with_signature
    * compute_diff_hash (if separate)

  * Recommended cases:

    1. STATIC fails once, FIX succeeds, STATIC re-run passes:

       * Expect:

         * FIX called once.
         * should_retry called once.
         * final workstream status == "done".
         * No breaker_tripped events.

    2. STATIC continually fails and breaker trips:

       * Mock should_retry to eventually return breaker_tripped=True.
       * Expect:

         * workstream status == "failed".
         * circuit_breaker_tripped event recorded.

    3. RUNTIME fails, repeated diff hash triggers oscillation:

       * Provide repeating diff_hash values to the FIX loop.
       * Mock should_retry to look at those hashes and trip on oscillation.
       * Expect appropriate event and failure.

    4. FIX step itself fails:

       * run_fix_step returns success=False.
       * Ensure orchestrator still obeys limits via circuit_breakers.should_retry.
       * Eventually stops and marks workstream failed once limits are hit.

====================================
DOCUMENTATION UPDATES
=====================

Update at least:

1. docs/ARCHITECTURE.md

   * Add or extend a section: “Circuit Breakers & FIX Loop”.
   * Explain:

     * What circuit_breakers.py does.
     * The meaning of config/circuit_breakers.yaml fields.
     * How FIX loops work around STATIC and RUNTIME steps.
     * The role of error signatures and diff hashes.
     * The fact that crash-resume logic and parallelism are handled in later phases (PH-06.5, PH-07).

2. docs/PHASE_PLAN.md

   * Flesh out the PH-06 section with:

     * Summary of error signatures, FIX loop, and circuit breakers.
     * List of artifacts:

       * src/pipeline/circuit_breakers.py
       * config/circuit_breakers.yaml
       * tests/pipeline/test_circuit_breakers.py
       * tests/pipeline/test_orchestrator_fix_loop.py
       * orchestration changes (run_step_with_fix, run_fix_step, etc.)

====================================
GIT COMMIT
==========

* Stage all new/modified files.
* Commit with message:

  * "PH-06: circuit breakers, retries & fix loop"
* Do NOT push (remote configuration is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
========================

* Do NOT break or remove outputs from PH-00–PH-05.5; extend them only.
* Do NOT implement:

  * Run-level crash recovery (PH-06.5).
  * Multi-workstream scheduling or parallelism (PH-07).
* Keep all decisions **auditable**:

  * Every retry and breaker trip should have corresponding entries in events/errors.
* Keep logic **config-driven**:

  * Thresholds must live in config/circuit_breakers.yaml, not hardcoded in Python.
* Favor testability:

  * Core decision logic belongs in circuit_breakers.py and can be tested without invoking Aider or git.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
===================================

You should:

1. PRECHECKS & NAVIGATION

   * Confirm C:\Users\richg\ALL_AI\AI_Dev_Pipeline exists.
   * cd C:\Users\richg\ALL_AI\AI_Dev_Pipeline
   * Confirm src/pipeline/, config/, docs/, tests/ exist; create missing folders if needed and note in docs/PHASE_PLAN.md if earlier phases are incomplete.

2. CREATE circuit_breakers.yaml

   * Add config/circuit_breakers.yaml with defaults and per_step overrides as described.
   * Document the meaning of each key.

3. IMPLEMENT circuit_breakers.py

   * Implement:

     * load_config()
     * CircuitBreakerConfig, BreakerDecision types
     * make_error_signature()
     * get_attempt_counts()
     * should_retry()
     * record_error_with_signature()
   * Integrate with db.py for counts and error recording.

4. UPDATE orchestrator.py

   * Add STEP_FIX constant.
   * Implement run_fix_step().
   * Ensure run_static_step/run_runtime_step populate details["errors"] and details["diff_hash"].
   * Implement a helper like run_step_with_fix() to wrap STATIC and RUNTIME with a FIX loop calling circuit_breakers.should_retry().
   * Update run_workstream() to use these wrapped steps, keeping overall flow EDIT → STATIC(+FIX) → RUNTIME(+FIX).

5. IMPLEMENT diff hashing helper

   * Either inside orchestrator.py or worktree.py:

     * compute_diff_hash(ws_id, ...).
   * Hook into STATIC/RUNTIME step results.

6. ADD TESTS

   * Implement tests/pipeline/test_circuit_breakers.py.
   * Implement tests/pipeline/test_orchestrator_fix_loop.py.
   * Use pytest fixtures, temp DBs, and monkeypatching to avoid external Aider/git dependencies.

7. RUN TESTS

   * From project root:

     * Run: pytest
   * Fix any failing tests before marking PH-06 complete.

8. UPDATE DOCS

   * Update docs/ARCHITECTURE.md and docs/PHASE_PLAN.md as described.

9. GIT COMMIT

   * Stage and commit with:

     * "PH-06: circuit breakers, retries & fix loop"

====================================
PHASE COMPLETION CHECKLIST
==========================

Before you consider PH-06 done, ensure all of the following are true:

[ ] config/circuit_breakers.yaml exists with defaults and per_step overrides for static/runtime
[ ] src/pipeline/circuit_breakers.py implements:
- load_config(), make_error_signature(), get_attempt_counts(),
should_retry(), record_error_with_signature()
[ ] src/pipeline/orchestrator.py:
- Defines STEP_FIX
- Implements run_fix_step()
- Wraps STATIC and RUNTIME in a FIX loop using circuit_breakers.should_retry()
- Computes and passes diff hashes for oscillation detection
[ ] Errors from STATIC/RUNTIME are:
- Recorded in DB via record_error()
- Included in StepResult.details["errors"]
[ ] Circuit breaker trip:
- Marks workstream as failed
- Records a clear event with reason (max attempts / per-signature / oscillation)
[ ] tests/pipeline/test_circuit_breakers.py exists and passes
[ ] tests/pipeline/test_orchestrator_fix_loop.py exists and passes
[ ] docs/ARCHITECTURE.md has a “Circuit Breakers & FIX Loop” section
[ ] docs/PHASE_PLAN.md has an updated PH-06 section listing artifacts and behavior
[ ] A git commit with message like "PH-06: circuit breakers, retries & fix loop" has been created

====================================
INTERACTION STYLE
=================

* Do NOT ask the user questions unless you are completely blocked.
* Make reasonable assumptions and document them in:

  * circuit_breakers.py docstrings,
  * docs/ARCHITECTURE.md (Circuit Breakers & FIX Loop),
  * docs/PHASE_PLAN.md (PH-06 section).
* When you output your response, clearly separate:

  * PowerShell commands you would run.
  * Python, YAML, and Markdown file contents you would create or modify.

END OF PROMPT

```
```
