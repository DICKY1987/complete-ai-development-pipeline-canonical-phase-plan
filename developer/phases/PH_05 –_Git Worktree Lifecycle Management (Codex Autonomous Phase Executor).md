---
doc_id: DOC-GUIDE-PH-05-GIT-WORKTREE-LIFECYCLE-MANAGEMENT-1235
---

TITLE: PH-05 – Orchestrator Core Loop (Single Workstream) (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-05 (Orchestrator Core Loop – Single Workstream) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Implement a first version of the orchestrator core loop for a SINGLE workstream.
- Wire together the existing pieces: db.py, bundles.py, worktree.py, tools.py, prompts/Aider integration.
- Implement clear step sequencing: EDIT → STATIC → RUNTIME (NO FIX loop yet).
- Record all state transitions and step attempts in the DB.
- Provide a simple CLI for running a single workstream and tests to verify behavior.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- Previous phases (assumed available):
  - PH-00: baseline project skeleton.
  - PH-01: spec index & module stubs (src/pipeline/orchestrator.py exists as stub).
  - PH-02: SQLite state layer & state machine (db.py + schema + state_machine.md).
  - PH-03: tool adapter (tool_profiles.json, tools.py with run_tool()).
  - PH-03.5: Aider integration & prompt engine (prompts.py, run_aider_edit/run_aider_fix or equivalents).
  - PH-04: workstream bundle parsing & validation (bundles.py, workstreams/, schema).
  - PH-04.5: git worktree lifecycle (worktree.py, .worktrees/<ws-id>).

PROJECT ROOT (IMPORTANT)
- Expected project root: C:/Users/richg/ALL_AI/AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-05 that PH-00–PH-04.5 must be completed first.
- Do NOT implement orchestrator logic in a different path.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-05
====================================

Implement the **first working orchestrator loop** for a SINGLE workstream that:

1) Creates or reuses a dedicated git worktree for the workstream.
2) Executes the steps:
   - EDIT: Aider-based editing using prompt engine.
   - STATIC: Static analyzers/tests (e.g., PSScriptAnalyzer, pytest, etc.).
   - RUNTIME: Acceptance / runtime tests specified in the workstream bundle.
3) Records DB state transitions and step attempts in a consistent way.
4) Enforces basic scope checks at the end (using worktree.validate_scope()).
5) Provides a simple CLI to run one workstream end-to-end:
   - Example entry: `python scripts/run_workstream.py --ws-id ws-example-single`

IMPORTANT: This phase does NOT implement FIX loops or circuit breakers. If STATIC or RUNTIME fails, the workstream should simply be marked failed. FIX + retries are PH-06.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-05, the repo MUST have at minimum:

1) orchestrator.py – SINGLE WORKSTREAM PIPELINE
Implement src/pipeline/orchestrator.py with:

Core concepts:

- A notion of pipeline steps:
  - EDIT
  - STATIC
  - RUNTIME

  Represented as:
  - Constants, an Enum, or simple string constants:
    - STEP_EDIT = "edit"
    - STEP_STATIC = "static"
    - STEP_RUNTIME = "runtime"

- A StepResult type:
  - Dataclass or typed dict with:
    - step_name: str
    - success: bool
    - details: dict | None
    - error_message: str | None

Core functions:

1) run_edit_step(run_id: str, ws_id: str, bundle, context) -> StepResult
   - Responsibilities:
     - Ensure worktree exists for this workstream:
       - Call worktree.create_worktree_for_ws(run_id, ws_id) if not already created.
     - Use Aider integration to implement required changes:
       - Call run_aider_edit(...) (from your PH-03.5 helper or equivalent).
     - Record:
       - A step_attempt row via db.record_step_attempt(...).
       - Events via db.record_event(...).
     - Update workstream state:
       - db.update_workstream_status(ws_id, "editing") before start.
       - On success: set status to transition target (e.g., "static_check" or "ready_for_static").
       - On failure: set status to "failed".
     - Return StepResult(success=..., details={...}, error_message=...).

2) run_static_step(run_id: str, ws_id: str, bundle, context) -> StepResult
   - Responsibilities:
     - Run static analyzers and test tools defined for this workstream:
       - Examples: PSScriptAnalyzer, pytest, yamllint, etc., referenced through tools.py.
     - For PH-05, define a simple, explicit behavior:
       - Run a pre-defined list of tools (e.g., "pytest" and possibly a PS static check if relevant) OR
       - Read from the bundle (acceptance_tests or metadata) which static tools to apply.
       - You may start with a hardcoded minimal set and document assumptions.
     - Treat **any** failing tool as a STATIC failure.
     - Record:
       - Step attempt (db.record_step_attempt).
       - Events for each tool run.
     - Update workstream status:
       - To "static_check" at start.
       - To "runtime_check" or similar on success.
       - To "failed" on failure.

3) run_runtime_step(run_id: str, ws_id: str, bundle, context) -> StepResult
   - Responsibilities:
     - Execute runtime/acceptance tests described by the bundle:
       - e.g., commands in bundle["acceptance_tests"] run via tools.run_tool().
     - All acceptance tests must pass for success.
     - Record:
       - Step attempt.
       - Events and errors (if any).
     - Update workstream status:
       - To "runtime_check" at start.
       - To "done" on success.
       - To "failed" on failure.

4) run_workstream(run_id: str, bundle, context) -> dict
   - This is the **main entry point** for a single workstream.
   - Inputs:
     - run_id: pre-existing or newly created run.
     - bundle: a validated workstream bundle dict (from bundles.load_and_validate_bundles()).
     - context: dict with values such as:
       - "repo_root"
       - "worktree_path" (may be computed inside)
       - additional config.
   - Behavior:
     - Derive ws_id from bundle["id"].
     - Ensure workstream row exists in DB (create if missing, or reuse existing).
     - Sequence:
       1) EDIT
       2) STATIC
       3) RUNTIME
     - Short-circuit on first failure:
       - If EDIT fails → mark workstream failed → stop.
       - If STATIC fails → mark workstream failed → stop.
       - If RUNTIME fails → mark workstream failed → stop.
     - At the end, run:
       - worktree.validate_scope(ws_id, files_scope, files_create)
       - If out_of_scope_files present, override status to "failed" and log a clear event.
     - Return a summary dict containing:
       - run_id
       - ws_id
       - final_status
       - step_results: mapping of step_name → StepResult

5) run_single_workstream_from_bundle(bundle_id: str) -> dict
   - Utility function that:
     - Uses bundles.load_and_validate_bundles() to load all bundles.
     - Selects the bundle with id == bundle_id.
     - Creates a new run via db.create_run().
     - Sets up a simple context (repo_root, etc.).
     - Calls run_workstream(run_id, bundle, context).
     - Updates run status in DB to:
       - "completed" if workstream is done.
       - "failed" otherwise.
     - Returns summary dict.

2) BASIC RUN SCRIPT / CLI ENTRY
- scripts/run_workstream.py
  - Runnable as:
    - python scripts/run_workstream.py --ws-id WS_ID
  - Behavior:
    - Initializes DB (db.init_db()) if needed.
    - Loads bundles and finds the requested ws-id.
    - Creates a new run (db.create_run()).
    - Calls run_workstream(...) or run_single_workstream_from_bundle(...).
    - Prints out:
      - Run ID
      - Workstream ID
      - Final status
      - Step statuses

- Optional flags:
  - --run-id to reuse an existing run instead of creating a new one.
  - --dry-run to simulate without actually invoking tools (could be added later; document if you only stub it).

3) DB & STATE INTEGRATION (MINIMUM REQUIRED)
- orchestrator.py MUST use db.py consistently:

  - For runs:
    - If a new run is created:
      - db.create_run(status="running", metadata=...) → run_id
      - On completion:
        - db.update_run_status(run_id, "completed" | "failed" | "partial" as appropriate).

  - For workstreams:
    - On first encounter:
      - db.create_workstream(run_id, ws_id, status="pending", depends_on=None, metadata=bundle subset).
        - NOTE: PH-04/PH-05.5 may later handle bulk creation; here you can create lazily if needed.
    - Before each step:
      - db.update_workstream_status(ws_id, <step-state>).
    - On success:
      - db.update_workstream_status(ws_id, "done").
    - On failure:
      - db.update_workstream_status(ws_id, "failed").

  - For step attempts:
    - Before/after each step:
      - db.record_step_attempt(run_id, ws_id, step_name, status="success"/"failure"/"skipped", result_json=...).

  - For events:
    - At key points (start/end of steps, worktree operations, scope validation outcomes), use:
      - db.record_event(run_id, ws_id, event_type="step_started"/"step_completed"/"scope_violation", payload_json=...).

4) INTEGRATION WITH EXISTING MODULES

orchestrator.py will call:

- from src/pipeline.bundles import load_and_validate_bundles
- from src/pipeline.worktree import create_worktree_for_ws, validate_scope
- from src/pipeline.tools import run_tool
- from src/pipeline.prompts (or aider_integration) import run_aider_edit

You MUST:

- Keep the coupling fairly loose:
  - orchestrator should not know about the internal details of tools.py or worktree.py; just call their public APIs.
- NOT implement FIX loops here:
  - If any step fails → mark workstream failed and stop.
- Document in module-level docstring that:
  - PH-06 will wrap these steps in FIX + circuit breaker logic.

5) UNIT TESTS
- tests/pipeline/test_orchestrator_single.py
  - Use pytest.
  - Use a temporary DB and a temporary git repo/worktree if needed; keep real repo untouched.

  Recommended strategies:

  - For ORCHESTRATOR LOGIC:
    - Mock or monkeypatch:
      - worktree.create_worktree_for_ws (no real git operations).
      - worktree.validate_scope (simulated OK vs scope violation).
      - run_aider_edit (simulate success/failure).
      - run_tool (for static/runtime steps) to simulate success/failure.

  - Test cases:

    1) Happy path:
       - run_workstream() where:
         - EDIT succeeds.
         - STATIC succeeds.
         - RUNTIME succeeds.
         - validate_scope() returns ok=True.
       - Assert:
         - final_status == "done".
         - DB shows workstream status "done".
         - Steps recorded as success.

    2) EDIT failure:
       - Simulate run_aider_edit → failure.
       - Assert:
         - STATIC and RUNTIME are NOT called.
         - workstream status == "failed".

    3) STATIC failure:
       - EDIT success, STATIC failure.
       - Assert:
         - RUNTIME not called.
         - workstream == "failed".

    4) RUNTIME failure:
       - EDIT success, STATIC success, RUNTIME failure.
       - Assert:
         - workstream == "failed".

    5) Scope violation:
       - All steps succeed, but validate_scope() returns:
         - ok=False, out_of_scope_files non-empty.
       - Assert:
         - final_status treated as failure (or "failed_due_to_scope", but status column should be "failed").
         - Event logged for scope violation.

    6) CLI script:
       - Use subprocess to invoke `python scripts/run_workstream.py --ws-id ...` against a small fake bundle set (you may point PIPELINE_WORKSTREAM_DIR to a temp location).
       - Assert that it exits with 0 on success and with non-zero on failure.

6) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add or extend the “Orchestrator Core Loop” section describing:
    - Single-workstream pipeline: EDIT → STATIC → RUNTIME.
    - Relationship with:
      - db.py (state layer),
      - bundles.py (inputs),
      - worktree.py (per-workstream git isolation),
      - tools.py + Aider integration (steps).
    - Clarify that FIX loops and multi-workstream scheduling come in PH-06 and PH-07a/b.

- docs/PHASE_PLAN.md:
  - Flesh out PH-05 section with:
    - Summary of the single-workstream orchestrator.
    - Steps implemented (EDIT, STATIC, RUNTIME).
    - List of artifacts:
      - src/pipeline/orchestrator.py
      - scripts/run_workstream.py
      - tests/pipeline/test_orchestrator_single.py

7) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-05: orchestrator core loop (single workstream)"
- Do NOT push (remote configuration is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00–PH-04.5; extend and integrate them.
- Do NOT implement circuit breakers, FIX loops, or multi-workstream DAG in this phase.
  - Those belong in PH-06 and PH-07a/b.
- Make the orchestrator **deterministic and testable**:
  - Step sequencing must be explicit and predictable.
  - Behavior on failure must be clear and easy to assert in tests.
- Avoid hidden global state:
  - Pass run_id, ws_id, and bundle explicitly to functions.
  - Use context dict instead of global config where possible.

Implementation details (recommended):

- Use Python standard library only (datetime, typing, dataclasses, json, etc.).
- For time stamps in DB records:
  - Use UTC ISO 8601 with "Z" suffix.
- For summary results:
  - Consider returning plain dicts from top-level functions for easy JSON serialization later.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:/Users/richg/ALL_AI/AI_Dev_Pipeline exists.
   - cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline
   - Confirm src/pipeline/, docs/, scripts/, tests/ exist; if not, create them and note in docs/PHASE_PLAN.md that earlier phases may be incomplete.

2) IMPLEMENT orchestrator.py
   - Open src/pipeline/orchestrator.py (stub).
   - Add:
     - Step constants/enum.
     - StepResult data structure.
     - run_edit_step(), run_static_step(), run_runtime_step().
     - run_workstream() and run_single_workstream_from_bundle().
   - Integrate with db.py, bundles.py, worktree.py, tools.py, prompts/Aider helpers.

3) IMPLEMENT CLI SCRIPT
   - Create scripts/run_workstream.py.
   - Use argparse.
   - Support at least:
     - --ws-id WS_ID
     - (optionally) --run-id RUN_ID
   - Wire it to call orchestrator.run_single_workstream_from_bundle() or equivalent.

4) ADD TESTS
   - Implement tests/pipeline/test_orchestrator_single.py.
   - Use pytest fixtures to:
     - Set up temp DB (override PIPELINE_DB_PATH).
     - Create minimal workstream bundle(s) in a temp workstreams dir and point PIPELINE_WORKSTREAM_DIR there.
   - Mock or monkeypatch:
     - run_aider_edit / run_tool / worktree functions as needed to avoid real external calls.

5) RUN TESTS
   - From project root:
     - Run: pytest
   - Fix any failing tests before considering PH-05 complete.

6) UPDATE DOCS
   - Update docs/ARCHITECTURE.md with “Orchestrator Core Loop”.
   - Update docs/PHASE_PLAN.md with detailed PH-05 description.

7) GIT COMMIT
   - Stage and commit with message:
     - "PH-05: orchestrator core loop (single workstream)"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-05 done, ensure all of the following are true:

[ ] src/pipeline/orchestrator.py implements:
    - Step constants (EDIT, STATIC, RUNTIME)
    - run_edit_step(), run_static_step(), run_runtime_step()
    - run_workstream()
    - run_single_workstream_from_bundle()
[ ] Steps call:
    - worktree.create_worktree_for_ws()
    - run_aider_edit(...) for EDIT
    - run_tool(...) for STATIC/RUNTIME tools
    - worktree.validate_scope() at the end
[ ] DB layer is used to:
    - create/update runs and workstreams
    - record step_attempts and events
[ ] scripts/run_workstream.py exists and can run a single workstream by ws-id
[ ] tests/pipeline/test_orchestrator_single.py exists and passes all cases:
    - success path
    - EDIT/STATIC/RUNTIME failure paths
    - scope violation behavior
[ ] docs/ARCHITECTURE.md has an “Orchestrator Core Loop” section
[ ] docs/PHASE_PLAN.md has an updated PH-05 section listing artifacts and behavior
[ ] A git commit with message like "PH-05: orchestrator core loop (single workstream)" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - src/pipeline/orchestrator.py docstrings,
  - docs/ARCHITECTURE.md (Orchestrator Core Loop),
  - docs/PHASE_PLAN.md (PH-05 section).
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python and Markdown file contents you would create or modify.

END OF PROMPT
