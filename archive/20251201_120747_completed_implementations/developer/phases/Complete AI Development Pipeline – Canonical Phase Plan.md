---
doc_id: DOC-GUIDE-COMPLETE-AI-DEVELOPMENT-PIPELINE-1228
---

# Complete AI Development Pipeline – Canonical Phase Plan



Legend:

* **v1.0 core**: Required to have a safe, single-node, multi-workstream orchestrator.
* **v1.1+**: Nice-to-have hardening.
* **v2.0+**: Parallelism / automation / advanced features.

Phases in order:

> PH-00 → PH-01 → PH-02 → PH-03 → **PH-03.5** → PH-04 → **PH-04.5** → PH-05 → **PH-05.5** → PH-06 → **PH-06.5** → **PH-07a** → *(v1.0 complete)* → **PH-07b** → PH-08 → PH-09 → PH-10 → PH-11

---

## [PH-00] Baseline & Project Skeleton (v1.0 core)

**Objective**
Create a clean, versioned home for the pipeline and lock in core tech choices (Python orchestrator, PowerShell tools, etc.).

**Key Artifacts**

* Repo: `ALL_AI/AI_Dev_Pipeline` (or similar).
* `pyproject.toml`, `requirements.txt`, optional `tasks.py` (Invoke) or `scripts/` (PowerShell).
* `src/`, `tests/`, `scripts/`, `docs/` layout.
* Top-level docs: `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`.

**Main Tasks**

1. **Repo & layout**

   * Create repo and canonical folder layout:
     `src/pipeline/`, `tests/pipeline/`, `scripts/`, `.github/workflows/`, `docs/`.
   * Decide on **single language of record** for orchestrator: Python, with PowerShell tools as external commands.

2. **Tooling & CI skeleton**

   * Add lint/format tooling (e.g., Ruff, Black, mypy, PSScriptAnalyzer) and minimal `pytest` setup.
   * Add CI workflow that runs lint + unit tests on PRs.

3. **Config baseline**

   * Add `config/` folder with stub `config.yaml` and `.env.example`.
   * Define pattern for environment/secret usage (paths, DB, tokens).

4. **Docs**

   * `ARCHITECTURE.md`: high-level overview + link to spec + phase plan file.
   * `PHASE_PLAN.md`: this document committed into repo.

**Exit / Gate**

* Repo builds/tests successfully in CI.
* Clear folder structure exists with no “mystery” paths.
* Architecture + phase docs are in `docs/` and linked from `README.md`.

---

## [PH-01] Spec Alignment & Index Mapping (v1.0 core)

**Objective**
Map the indexed spec (`[IDX-...]`) to concrete modules, functions, and phases.

**Key Artifacts**

* `docs/spec_index_map.md` – mapping `[IDX-...] → module → function/class → phase`.
* Updated `ARCHITECTURE.md` referencing the index map.

**Main Tasks**

1. **Index extraction**

   * List all `[IDX-...]` tags from the spec / indexed spec file.
   * Classify them by responsibility: DB, orchestration, steps, circuit breakers, prompts, observability, recovery.

2. **Module mapping**

   * Decide module layout: e.g.

     * `db.py`, `orchestrator.py`, `tools.py`, `prompts.py`, `worktree.py`,
       `bundles.py`, `recovery.py`, `scheduler.py`, `executor.py`, `integrations/`.

3. **Phase assignment**

   * For each `[IDX-...]`:

     * Assign a **destination module + function/class**.
     * Assign a **phase** (PH-02, PH-03, …).
     * Mark as:

       * `v1.0`, `v1.1`, or `v2.0+`.

4. **Document it**

   * Create `docs/spec_index_map.md` as a table:

     * `IDX`, `Description`, `Module`, `Function/Class`, `Phase`, `Version`.

**Exit / Gate**

* Every `[IDX-...]` tag is:

  * mapped to code, **or**
  * explicitly marked as “Future (v2.0+)”.
* No ambiguity about where each behavior will live.

---

## [PH-02] Data Model, SQLite State Layer & State Machine (v1.0 core)

**Objective**
Implement the state database and a **formal state machine** for runs/workstreams/steps.

**Key Artifacts**

* `src/pipeline/db.py` – DB access layer.
* `schema.sql` or migrations.
* `docs/state_machine.md` – formal lifecycle doc.
* Unit tests for DB + state transitions.

**Main Tasks**

1. **DB schema**

   * Tables:

     * `runs` (run_id, status, started_at, completed_at, metadata).
     * `workstreams` (ws_id, run_id, status, deps, metadata).
     * `step_attempts` (id, run_id, ws_id, step, started_at, completed_at, result_json).
     * `errors` (id, run_id, ws_id, step, error_code, signature, count).
     * `events` (id, timestamp, run_id, ws_id, event_type, payload_json).
   * Indexes for common queries (by run_id, ws_id, status).

2. **DB API**

   * Functions like:

     * `create_run(...)`, `update_run_status(...)`, `get_run(...)`.
     * `create_workstream(...)`, `update_workstream_status(...)`, `get_workstreams_for_run(...)`.
     * `record_step_attempt(...)`, `record_error(...)`, `record_event(...)`.

3. **State machine documentation**

   * Define allowed **workstream states**, e.g.:

     * `pending → ready → editing → static_check → fixing (loop) → runtime_check → done`
     * plus `failed`, `blocked`, `abandoned`.
   * Write `docs/state_machine.md` with:

     * Text + diagram of states.
     * Valid transitions and what triggers each.

4. **State transition guard**

   * Implement `validate_state_transition(from_state, to_state)` and call it from `db.py`.
   * Reject illegal transitions and log them as events.

5. **Tests**

   * Unit tests ensuring:

     * All valid transitions pass.
     * Illegal transitions are blocked and logged.
   * Smoke test to create a run with multiple workstreams and move them through states.

**Exit / Gate**

* DB schema is stable and versioned.
* `docs/state_machine.md` exists and matches what code enforces.
* Attempting an illegal state transition fails predictably and logs an event.

---

## [PH-03] Tool Profiles & Adapter Layer (v1.0 core)

**Objective**
Formalize tool definitions (Aider, PSScriptAnalyzer, Pester, etc.) and a single `run_tool()` entry point.

**Key Artifacts**

* `config/tool_profiles.json` (or YAML).
* `src/pipeline/tools.py`.
* Unit tests + a dummy “echo” tool for adapter testing.

**Main Tasks**

1. **Tool profile schema**

   * Define shape for tool entries:

     * `id`, `type` (ai, static_check, test), `command`, `args`, `env`, `timeout`, `success_criteria`.

2. **Tool adapter**

   * Implement `run_tool(tool_id, context)`:

     * Resolve profile.
     * Render command/args/env from context.
     * Execute process, capture `stdout`, `stderr`, `exit_code`, `elapsed`.
     * Return structured result.

3. **Error handling**

   * Map failures to structured codes:

     * Missing binary.
     * Timeout.
     * Non-zero exit.
   * Record `events` and `errors` rows.

4. **Mocks & tests**

   * Create mock tool that simply returns JSON for echo testing.
   * Unit tests verifying parsing, error handling, and event recording.

**Exit / Gate**

* `run_tool()` can execute both a real tool (e.g. `echo`) and the mock tool successfully.
* Errors are recorded in `errors` and `events` tables with structured signatures.

---

## [PH-03.5] Aider Integration Contract & Prompt Template System (v1.0 core)

**Objective**
Define a **deterministic Aider contract** and a reusable prompt engine that turns workstream bundles + context into Aider prompts.

**Key Artifacts**

* `docs/aider_contract.md` – full integration spec.
* `src/pipeline/prompts.py` – prompt builder API.
* `templates/prompts/edit.txt.j2`, `templates/prompts/fix.txt.j2`.
* `config/aider_profiles.json` – model-specific Aider configs.
* `tests/integration/test_aider_sandbox.py`.
* `sandbox_repos/` – small test repos for validation.

**Main Tasks**

1. **Aider contract**

   * Document in `docs/aider_contract.md`:

     * Exact CLI invocation (`aider ...`) and the flags you will always use.
     * Required env vars (e.g. API keys, model selection).
     * Working directory expectations (clean worktree, etc.).
     * Success / failure criteria & typical error shapes.

2. **Prompt engine**

   * Implement in `prompts.py`:

     * `build_edit_prompt(run, ws, bundle, context)`.
     * `build_fix_prompt(run, ws, bundle, error_list, context)`.
   * Use Jinja templates for text; all dynamic bits come from:

     * `workstreams/*.json`.
     * OpenSpec change details.
     * Error summaries from `errors` table.

3. **Safety wrapper for Aider**

   * Pre-flight:

     * Verify Aider binary + version.
     * Check API credentials / model availability.
     * Confirm clean worktree and correct branch.
   * Execution:

     * Enforce timeouts.
     * Capture logs to structured events.
   * Post:

     * Verify only `files_scope` (and allowed `files_create`) were modified.
     * Detect unexpected commits or branch changes.

4. **Sandbox integration tests**

   * Build 2–3 tiny repos in `sandbox_repos/` (e.g. Python+PowerShell mix).
   * For each:

     * Run EDIT+FIX using real Aider.
     * Assert 90%+ success on known scenarios.
     * Confirm scope validation and logging work.

**Exit / Gate**

* `docs/aider_contract.md` is complete and checked in.
* Prompts can be generated **without** changing code (template-driven).
* Aider wrapper enforces safety checks and rejects out-of-scope edits.
* Integration tests pass on sandbox repos with high reliability.

---

## [PH-04] Workstream Bundle Parsing & Validation (v1.0 core)

**Objective**
Turn `workstreams/*.json` into validated in-memory structures ready for orchestration.

**Key Artifacts**

* `schema/workstream.schema.json`.
* `src/pipeline/bundles.py`.
* Validation tests & sample bundles in `examples/workstreams/`.

**Main Tasks**

1. **Bundle schema**

   * Fields like:

     * `id`, `openspec_change`, `gate`, `files_scope`, `files_create`, `tasks`, `acceptance_tests`, `depends_on`, `tool`, `circuit_breaker`.

2. **Loader & validator**

   * Load all `workstreams/*.json`.
   * Validate against schema.
   * Enforce:

     * No duplicate IDs.
     * Valid gates.
     * `files_scope` and `files_create` shapes.

3. **DAG construction**

   * Build dependency graph from `depends_on`.
   * Enforce:

     * No cycles.
     * All referenced workstreams exist.

4. **Scope overlap detection**

   * Detect overlapping `files_scope` between workstreams.
   * For v1: require manual resolution (or explicit allow-list).

**Exit / Gate**

* Invalid bundles fail fast with clear error messages.
* A valid bundle set gives a clean DAG and a complete list of workstreams.

---

## [PH-04.5] Git Worktree Lifecycle Management (v1.0 core)

**Objective**
Provide safe, isolated git worktrees per workstream and enforce **file-scope isolation**.

**Key Artifacts**

* `src/pipeline/worktree.py`, `src/pipeline/git_safety.py`.
* CLI helpers: `pipeline worktree-init/list/status/cleanup`.
* `docs/worktree_guidelines.md`.

**Main Tasks**

1. **Worktree creation**

   * Standard layout: `.worktrees/<ws-id>/`.
   * Naming rules for branches (e.g. `ws/<change-id>/<ws-id>`).
   * Base branch detection (e.g., `main` or `develop`).

2. **Pre- and post-checks**

   * Pre:

     * No uncommitted changes in base working copy.
     * Base branch exists and is clean.
   * Post:

     * Only `files_scope + files_create` modified.
     * No detached HEAD, no weird reflog state.

3. **Scope enforcement**

   * After EDIT/FIX:

     * `git diff --name-only` vs `files_scope`.
     * Treat extra files as scope violations → fail workstream.

4. **Cleanup & inspection**

   * Commands to:

     * List all worktrees and their status.
     * Detect orphaned worktrees from crashed runs.
     * Clean up worktrees when:

       * Success → remove.
       * Failure → optionally keep for debugging with clear label.

**Exit / Gate**

* For a toy repo, each workstream gets its own worktree, and only scoped files change.
* Orphaned worktrees can be detected and cleaned without affecting active runs.

---

## [PH-05] Orchestrator Core Loop (Single Workstream) (v1.0 core)

**Objective**
Implement the EDIT → STATIC → RUNTIME pipeline for **one workstream**, fully wired to DB and tools.

**Key Artifacts**

* `src/pipeline/orchestrator.py` – `run_workstream()` + `run_pipeline()` (MVP).
* CLI entry (e.g. `python -m pipeline run --workstream-id ...`).

**Main Tasks**

1. **run_workstream(ws)**

   * Steps:

     * EDIT: call Aider via `run_tool()` + `build_edit_prompt()`.
     * STATIC: call static analyzers/tests (PSScriptAnalyzer, Pester, etc.).
     * RUNTIME: run workstream-specific acceptance tests (if any).

2. **DB integration**

   * Record:

     * `step_attempts` for each step.
     * state transitions (`workstreams.status`).
     * events for each major action.

3. **Simple run_pipeline()**

   * For now:

     * Create a run with 1 workstream.
     * Call `run_workstream()` and update run status.

4. **CLI & output**

   * Provide simple progress logs:

     * Step names, success/failure, error summaries.

**Exit / Gate**

* On a toy repo + bundle, you can run a full EDIT → STATIC → RUNTIME cycle end-to-end.
* DB is populated with runs/workstreams/steps/errors/events correctly.

---

## [PH-05.5] Workstream Bundle Generator (v1.0 core, v2.0+ automation)

**Objective**
Provide tools to generate or validate `workstreams/*.json` from OpenSpec changes.

**Key Artifacts**

* **v1.0 (semi-manual)**:

  * `docs/workstream_authoring_guide.md`.
  * `scripts/validate-workstream.py`.
  * `templates/workstream_template.json`.
* **v2.0 (automated)**:

  * `src/pipeline/planner.py`.
  * `config/decomposition_rules.yaml`.
  * `scripts/generate-workstreams.py`.

**Main Tasks**

1. **v1.0 – Semi-manual authoring**

   * Document how to:

     * Read an OpenSpec change.
     * Decompose into 3–5 workstreams.
     * Assign `files_scope`, `files_create`, `tasks`, `depends_on`.
   * Build `validate-workstream.py`:

     * Runs schema validation + DAG cycle detection + overlap checks.
     * Reports missing tasks / gates.

2. **v2.0 – Automated planner (optional)**

   * `planner.py`:

     * Read OpenSpec/CCPM artifacts.
     * Use decomposition rules + import graphs to propose bundles.
   * Human reviews and tweaks generated bundles.

**Exit / Gate**

* For v1.0, someone new can:

  * Author bundles following the guide.
  * Run the validator and get clean output.
* For v2.0, planner can generate draft bundles covering all tasks with limited manual editing.

---

## [PH-06] Circuit Breakers, Retries & Fix Loop (v1.0 core)

**Objective**
Make EDIT/STATIC/FIX robust with bounded retries and oscillation detection.

**Key Artifacts**

* `src/pipeline/circuit_breakers.py`.
* Config: `config/circuit_breakers.yaml`.
* Tests simulating failure/error patterns.

**Main Tasks**

1. **Error signatures & counters**

   * Generate stable signatures from error messages (`error_code + normalized text`).
   * Increment per-signature counters in `errors` table.

2. **Retry loop**

   * After STATIC or RUNTIME failures:

     * Build FIX prompt with error list.
     * Call Aider to fix.
     * Re-run STATIC or RUNTIME.
   * Stop when:

     * Success, **or**
     * Circuit breaker trips.

3. **Circuit breakers**

   * Parameters (per workstream / step type):

     * Max total attempts per step.
     * Max per error signature.
     * Oscillation threshold (same diff repeating).

   * When breaker trips:

     * Mark workstream as `failed`.
     * Record detailed event with reason.

4. **Oscillation detection**

   * Hash diffs; detect repeated patterns between attempts.
   * Use to trigger oscillation breaker.

**Exit / Gate**

* On a controlled failing scenario, FIX loop:

  * Either resolves the error within limits, **or**
  * Trips a breaker with a clear explanation.
* No infinite loops; logs show each retry and breaker.

---

## [PH-06.5] Crash Recovery & Resume Logic (v1.0 core)

**Objective**
Allow safe **resume** after crashes, and provide manual recovery tools.

**Key Artifacts**

* `src/pipeline/recovery.py`, `src/pipeline/shutdown.py`.
* `docs/recovery_runbook.md`.
* CLI commands: `pipeline run --resume`, `pipeline recover-run`, `pipeline abandon-run`, etc.

**Main Tasks**

1. **Run-level resume**

   * On startup:

     * Detect `runs` with `status='running'` but no active process.
     * Decide to:

       * Auto-resume, **or**
       * Prompt user/flag to resume or abandon.

2. **Workstream-level resume**

   * For each ws:

     * Resume from last completed step.
     * Reuse artifacts where safe; re-run where required.
   * Ensure idempotency of steps (e.g. STATIC test reruns are safe).

3. **Crash-safe shutdown**

   * Register shutdown hooks:

     * Mark in-progress steps as interrupted.
     * Flush logs/events.
   * On restart:

     * Detect interrupted steps.
     * Either rollback worktree or re-run from clean state.

4. **Corruption checks**

   * Before resuming:

     * Confirm DB schema version matches code.
     * Bundles still present.
     * Worktrees valid and not in weird git state.

5. **Manual recovery commands**

   * `recover-run <run-id>`:

     * Attempt auto-fix of common issues (orphaned worktrees, missing artifacts).
   * `abandon-run <run-id>`:

     * Mark run as `abandoned`, clean worktrees, retain logs.
   * `reset-workstream`, `rollback-workstream` for targeted cleanup.

**Exit / Gate**

* Killing the process mid-run and then using `--resume`:

  * Does not corrupt DB or repo.
  * Either resumes or fails with clear recovery instructions.
* Recovery runbook fully describes operator workflows.

---

## [PH-07a] Multi-Workstream Sequential DAG Execution (v1.0 core)

**Objective**
Execute a DAG of workstreams **sequentially**, honoring dependencies and failures.

**Key Artifacts**

* `src/pipeline/scheduler.py`.
* Updated `run_pipeline()` to handle many workstreams.
* DB fields for `depends_on` and `status` transitions.

**Main Tasks**

1. **Scheduler**

   * Use bundle DAG + state machine to:

     * Mark workstreams `ready` when all `depends_on` are `done`.
     * Keep others `pending` or `blocked`.

2. **Execution loop (sequential)**

   * Pseudocode:

     ```python
     while not all_complete(run_id):
         ready = get_ready_workstreams(run_id)
         if not ready and has_pending(run_id):
             mark_run_failed_or_partial(run_id)
             break
         for ws in ready:
             execute_workstream_sequential(ws)
     ```

3. **Dependency failure handling**

   * If A fails:

     * All dependents (B, C…) become `blocked`.
   * Final run status:

     * `completed`, `partial`, or `failed`.

4. **Reporting**

   * Simple CLI views:

     * `pipeline show-run --id RUN123` showing workstream states.
     * `pipeline show-dag --id RUN123` (text-based summary is enough).

**Exit / Gate**

* With a multi-workstream bundle set:

  * Execution respects dependencies.
  * Failures in upstream workstreams block downstream ones.
* Run status accurately reflects `completed`, `partial`, or `failed`.

---

## [PH-07b] Parallel Workstream Execution (v2.0+)

**Objective**
Optionally run independent workstreams in parallel with safe resource and concurrency management.

**Key Artifacts**

* `src/pipeline/executor.py`.
* `config/executor.yaml`.
* Concurrency / race-condition tests.

**Main Tasks**

1. **Concurrency model**

   * Choose: threads / processes / AsyncIO.
   * Implement worker pool with configurable size (`executor.yaml`).

2. **Task queue**

   * Queue of `ready` workstreams.
   * Workers pull and execute `run_workstream()`.
   * DB updates and logs are done with appropriate locking/transactions.

3. **Resource management**

   * Limit:

     * Concurrent Aider processes (API limits).
     * Disk I/O (worktree operations).
     * CPU / memory (for heavy tests).

4. **Robustness**

   * Detect worker crashes and:

     * Mark affected workstreams appropriately.
     * Avoid double execution.

**Exit / Gate**

* With parallelism enabled:

  * Runs finish faster on independent workstreams.
  * DB/logs remain consistent.
  * Disabling parallelism falls back to PH-07a behavior.

---

## [PH-08] Integrations (OpenSpec, CCPM, GitHub, etc.) (v1.1+)

**Objective**
Wire pipeline results into OpenSpec/CCPM tracking and GitHub (branches, PRs, issues).

**Key Artifacts**

* `src/pipeline/integrations/openspec.py`.
* `src/pipeline/integrations/github.py`.
* Config for tokens/URLs in your centralized secrets system.

**Main Tasks**

1. **OpenSpec / CCPM**

   * Map workstreams to OpenSpec changes and gates.
   * Optionally post:

     * Status updates.
     * Links to PRs or logs.

2. **GitHub integration**

   * For successful workstreams:

     * Push branches.
     * Open PRs with:

       * Description, associated OpenSpec/CCPM IDs.
       * Summary of changes / tests.

3. **Secrets management**

   * Ensure all tokens are loaded via your standardized secrets layout (SecretManagement, .env, etc.).
   * Avoid storing secrets in configs or logs.

**Exit / Gate**

* After a successful run:

  * PRs and/or CCPM artifacts are created or updated.
  * No secrets leak into logs or git history.

---

## [PH-09] Observability, Logging & Diagnostics (v1.1+)

**Objective**
Make the system debug-friendly for humans and AI agents.

**Key Artifacts**

* Logging config: `config/logging.yaml`.
* JSONL logs per run.
* CLI diagnostics: `pipeline show-run`, `pipeline show-errors`, etc.

**Main Tasks**

1. **Logging standardization**

   * JSON lines with fields:

     * run_id, ws_id, step, level, message, timestamps, context.

2. **Diagnostic commands**

   * `pipeline show-run --id RUN123`.
   * `pipeline show-errors --run RUN123`.
   * `pipeline show-events --run RUN123 --ws WS-01`.

3. **Summaries**

   * Optional: generate per-run summary reports (JSON/Markdown) for archival or AI input.

**Exit / Gate**

* On any failure, you can reconstruct what happened from DB + logs using CLI commands.
* Logs are structured and parsable by other tools or AI agents.

---

## [PH-10] Production Hardening, CI/CD & Packaging (v1.1+)

**Objective**
Make the pipeline production-ready: tested, packaged, and deployable.

**Key Artifacts**

* Full test suite with coverage reports.
* CI/CD workflows.
* Packaging config (e.g. `pyproject.toml` with `console_scripts` entry points).

**Main Tasks**

1. **Testing**

   * High coverage on:

     * DB layer.
     * Orchestrator & scheduler.
     * Circuit breakers & recovery.
     * Worktree management & scope enforcement.

2. **CI/CD**

   * CI:

     * Lint, tests, coverage thresholds.
   * CD:

     * Build and publish package.
     * Optionally deploy to internal runner/VM.

3. **Performance & reliability checks**

   * Run on larger repositories / workstream sets.
   * Identify slow paths, tune DB queries and logging.

**Exit / Gate**

* CI is green.
* Package can be installed and used on another machine with minimal setup.
* Pipeline is stable under moderate load.

---

## [PH-11] Runbooks, Operating Contracts & Onboarding (v1.1+)

**Objective**
Document how humans and AI agents should operate and evolve the pipeline.

**Key Artifacts**

* `docs/runbook.md`.
* `docs/ai_integration_guide.md`.
* Updated Operating Contract referencing this pipeline.

**Main Tasks**

1. **Runbook**

   * How to start/run/stop/resume runs.
   * How to read logs and DB.
   * Common failure modes and how to respond.

2. **AI integration guide**

   * How other AI agents (Codex, Claude Code, Aider, etc.) should:

     * Propose workstreams.
     * Call CLI.
     * Interpret results and logs.

3. **Operating Contract**

   * Add a section to your existing Operating Contract:

     * Ownership of the pipeline.
     * Change control / versioning.
     * Required checks before enabling new tools or prompts.

**Exit / Gate**

* A new engineer (or AI agent) can read the docs and operate the pipeline without tribal knowledge.
* The pipeline is formally governed by your Operating Contract.

---

If you’d like, next step I can:

* Extract **just one phase** (e.g. PH-03.5 or PH-04.5) into a separate, AI-friendly prompt template for Codex/Claude/Aider to implement that phase autonomously.
