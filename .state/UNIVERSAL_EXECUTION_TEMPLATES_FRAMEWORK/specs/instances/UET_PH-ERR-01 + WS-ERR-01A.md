---
doc_id: DOC-GUIDE-UET-PH-ERR-01-WS-ERR-01A-1646
---

Here’s a tight “Error Pipeline Bundle” design that stays in planning mode and snaps into everything we’ve already defined.

We’ll define:

* **PH-ERR-01 + WS-ERR-01A** → intake & repair attempts (what we already sketched).
* **PH-ERR-02 + WS-ERR-02A** → escalation & GitHub PR/issue creation.
* The **chaining** between them via `RunEvent`s and error handling.

---

## 1. Bundle overview (conceptual)

Think of the Error Pipeline Bundle as two phases:

1. **PH-ERR-01 – Patch Intake & Automated Repair**

   * Workstream: **WS-ERR-01A**
     “Try to normalize, analyze, and automatically fix a failing patch, then apply+verify it.”

2. **PH-ERR-02 – Escalation & Human Handoff**

   * Workstream: **WS-ERR-02A**
     “If PH-ERR-01 can’t fix the patch, bundle the evidence and create a GitHub PR/Issue for a human.”

The orchestrator chains these via **RunEvents** and **error_handling** rules, not ad-hoc logic.

---

## 2. PH-ERR-01 + WS-ERR-01A (summary)

We already outlined WS-ERR-01A in schema form:

* **Phase ID**: `PH-ERR-01`
* Objective: “Handle failing patches: normalize → analyze → generate corrected patch → apply & test.”
* **Workstream**: `WS-ERR-01A`

  * T1: Normalize raw failing patch → `PatchArtifact` + ledger.
  * T2: Analyze why patch fails (AI analysis).
  * T3: Generate corrected patch (AI unified diff).
  * T4: Apply patch + run tests (Patch Worker).
* **Key acceptance**: tests pass AND no patches in `quarantined` state.

**Important error-handling rule** for WS-ERR-01A (already in the outline):

```yaml
error_handling:
  default_on_task_failure: "route_error_phase"
  max_task_retries: 1
  error_phase_id: "PH-ERR-02"
```

So: any unrecoverable failure in WS-ERR-01A (test failures after retries, policy violations, oscillation, etc.) → **must** route into PH-ERR-02.

---

## 3. PH-ERR-02 – Escalation & Handoff (outline)

A minimal `PH-ERR-02` phase instance, using the PHASE_SPEC_MASTER structure, focusing on the three big sections:

```yaml
phase_id: "PH-ERR-02"
name: "Error Patch Escalation and Handoff"
category: "error_pipeline"
description: "Escalate persistent patch failures by packaging evidence and opening a GitHub PR/Issue for human review."

files_scope:
  read:
    - "src/error_pipeline/**/*.py"
    - "docs/error_pipeline/**/*.md"
    - "C:\\QUARANTINE\\patches\\PH-ERR-01\\**/*.patch"
    - "logs/runs/**/*.log"
  write:
    - "docs/error_pipeline/**/*.md"        # optional: add escalation notes
  create:
    - "docs/error_pipeline/escalations/**/*.md"
  forbidden:
    - ".git/**"                            # repo mutation still forbidden at this phase
    - "secrets/**"

constraints:
  patch:
    patch_required: false                  # this phase shouldn't generate code patches
    allowed_formats: ["unified_diff"]
    max_lines_changed: 0                   # no edits; purely escalation
    max_files_changed: 0
    forbid_binary_patches: true
    require_issue_ref: false               # escalation phase will create the issue/PR itself
    min_reviewers: 0

  tests:
    tests_must_run: false                  # escalation is meta-level, no code changes
    tests_must_pass: false

  behavior:
    ascii_only: true
    forbid_direct_file_writes: false       # allowed to write docs under allowed paths
    require_doc_update: false
    max_attempts_per_run: 1

  routing:
    allowed_tools:
      - "claude_cli"                       # for summarization/report generation
      - "github_worker"                    # non-LLM worker that calls GitHub API
    disallowed_tools: []

acceptance:
  mode: "all"
  checks:
    - id: "github_artifact_created"
      type: "run_state"
      description: "Escalation artifacts created (PR or Issue opened)."
      condition: "github_artifact_created == true"
      required: true
      severity: "error"
    - id: "quarantined_patches_linked"
      type: "patch_state"
      description: "All quarantined patches referenced in escalation payload."
      condition: "all_quarantined_patches_linked == true"
      required: true
      severity: "error"
  post_actions: []
```

Key points:

* **No patch creation** here (`max_lines_changed = 0`).
* Read access to:

  * Quarantined patch files,
  * Run logs,
  * Source/docs (for context).
* Optional write access only to docs (e.g., escalation logs).

---

## 4. WS-ERR-02A – Escalation & GitHub PR/Issue workstream

A minimal workstream that fits `WORKSTREAM_SPEC` and the PH-ERR-02 constraints.

### 4.1 Top-level WorkstreamSpec (schema-style)

```yaml
workstream_id: "WS-ERR-02A"
project_id: "PRJ-HUEY_P"
phase_id: "PH-ERR-02"

name: "Escalate Quarantined Patch to GitHub"
category: "error_pipeline"
description: "Summarize the failure context and create a GitHub PR or Issue for human review."
objective: "For any quarantined patch coming from PH-ERR-01, bundle the evidence and open a corresponding GitHub artifact."

tags:
  - "error"
  - "escalation"
  - "github"

# Narrow scope relative to PH-ERR-02
files_scope:
  read:
    - "C:\\QUARANTINE\\patches\\PH-ERR-01\\**/*.patch"
    - "logs/runs/**/*.log"
    - "src/error_pipeline/**/*.py"
  write:
    - "docs/error_pipeline/escalations/**/*.md"
  create:
    - "docs/error_pipeline/escalations/**/*.md"
  forbidden:
    - ".git/**"
    - "secrets/**"

constraints:
  patch:
    max_lines_changed: 0          # again, no code edits in this workstream
  tests:
    tests_must_run: false
  behavior:
    max_attempts_per_run: 1

concurrency:
  mode: "sequential"
  max_parallel: 1

error_handling:
  default_on_task_failure: "fail_workstream"
  max_task_retries: 0
  error_phase_id: null           # PH-ERR-02 is already the escalation end of the line

acceptance:
  mode: "all"
  checks:
    - id: "github_artifact_created"
      type: "run_state"
      description: "GitHub PR or Issue created successfully."
      condition: "github_artifact_created == true"
      required: true
      severity: "error"
    - id: "quarantined_patches_linked"
      type: "patch_state"
      description: "All quarantined patches linked from GitHub artifact."
      condition: "all_quarantined_patches_linked == true"
      required: true
      severity: "error"
  post_actions: []
```

### 4.2 Tasks for WS-ERR-02A

Minimal sequence:

1. **T1-collect-context** – summarize what went wrong.
2. **T2-github-artifact** – create PR/Issue via worker.
3. **T3-doc-log (optional)** – write a local escalation note (optional).

#### T1 – Collect context / summarize (AI)

```yaml
- task_id: "T1-collect-context"
  name: "Summarize failure context for escalation"
  description: "Use AI to summarize quarantined patch details, failing tests, and relevant logs for human consumption."
  sequence: 1
  kind: "analysis"
  phase_id: "PH-ERR-02"
  depends_on: []
  allow_parallel: false

  classification:
    complexity: "medium"
    risk_tier: "R2"
    domain: "error_pipeline"
    priority: "normal"

  files_scope_delta:
    read:
      - "C:\\QUARANTINE\\patches\\PH-ERR-01\\**/*.patch"
      - "logs/runs/**/*.log"
      - "src/error_pipeline/**/*.py"
    write: []
    create: []
    forbidden: []

  constraints_delta:
    patch:
      max_lines_changed: 0
    tests:
      tests_must_run: false
    behavior: {}

  execution:
    max_attempts: 1
    timeout_seconds: 600
    background: false
    retry_strategy:
      mode: "none"
      max_attempts: 1

  prompt_template_ref: "TEMPLATE_WORKSTREAM_V1_1"
  prompt_overrides:
    OBJECTIVE_suffix: "Produce a concise but complete summary suitable for a GitHub PR or Issue body."

  execution_request_template:
    task_kind: "analysis"
    prompt_spec:
      template_id: "TEMPLATE_WORKSTREAM_V1_1"
      kind: "analysis"
    routing:
      strategy: "auto"
      preferred_tools: ["claude_cli"]
      allowed_tools: ["claude_cli", "codex_cli"]

  error_handling:
    on_failure: "fail_workstream"
    error_phase_id: null

  acceptance:
    mode: "all"
    checks:
      - id: "summary_nonempty"
        type: "run_state"
        description: "Summary for escalation is non-empty."
        condition: "task_output_size > 0"
        required: true
        severity: "error"
```

#### T2 – Create GitHub PR or Issue (non-LLM worker)

```yaml
- task_id: "T2-github-artifact"
  name: "Create GitHub PR/Issue with context"
  description: "Use a GitHub worker to open a PR or Issue containing the AI-generated summary and patch references."
  sequence: 2
  kind: "other"
  phase_id: "PH-ERR-02"
  depends_on:
    - "T1-collect-context"
  allow_parallel: false

  classification:
    complexity: "medium"
    risk_tier: "R2"
    domain: "error_pipeline"
    priority: "high"

  files_scope_delta:
    read:
      - "docs/error_pipeline/escalations/**/*.md"
    write:
      - "docs/error_pipeline/escalations/**/*.md"
    create:
      - "docs/error_pipeline/escalations/**/*.md"
    forbidden: []

  constraints_delta:
    patch:
      max_lines_changed: 0               # still no code edits
    tests:
      tests_must_run: false
    behavior: {}

  execution:
    max_attempts: 1
    timeout_seconds: 600
    background: false
    retry_strategy:
      mode: "none"
      max_attempts: 1

  execution_request_template:
    task_kind: "other"
    prompt_spec: null                    # non-LLM GitHub worker
    routing:
      strategy: "fixed"
      preferred_tools: ["github_worker"]
      allowed_tools: ["github_worker"]

  error_handling:
    on_failure: "fail_workstream"
    error_phase_id: null

  acceptance:
    mode: "all"
    checks:
      - id: "github_artifact_created"
        type: "run_state"
        description: "GitHub PR or Issue created successfully."
        condition: "github_artifact_created == true"
        required: true
        severity: "error"
```

(You can add T3 to write an escalation note locally, but the above two are enough for a minimal bundle.)

---

## 5. How PH-ERR-01 and PH-ERR-02 chain via RunEvents & error handling

Here’s the end-to-end story.

### 5.1 Run in PH-ERR-01 (WS-ERR-01A) fails → Error pipeline trigger

1. A Run `RUN-ERR-01A` is executing **PH-ERR-01** / **WS-ERR-01A**.
2. T3 (generate patch) succeeds; T4 (apply+verify) runs via Patch Worker.
3. In **T4**, patch application or tests **fail**:

   * PatchLedgerEntry transitions:

     * `validated → applied → apply_failed` (or)
     * `validated → quarantined` directly (e.g., policy violation).
   * Patch Worker emits RunEvents:

     * `patch_apply_failed`
     * Possibly `patch_quarantined`
4. WS-ERR-01A’s `error_handling` and T4’s `error_handling` both say:

   * `on_failure: "route_error_phase"`
   * `error_phase_id: "PH-ERR-02"`
5. Orchestrator records:

   * `RunEvent` with `kind: "error_pipeline_triggered"` and payload containing:

     * `source_phase_id: "PH-ERR-01"`
     * `target_phase_id: "PH-ERR-02"`
     * `quarantined_patch_ids: [...]`
   * Run `RUN-ERR-01A.state` moves to `quarantined` or `failed` (depending on your policy).

### 5.2 Orchestrator starts PH-ERR-02 run based on that event

6. Orchestrator consumes the `error_pipeline_triggered` event and constructs a **new ExecutionRequest** for PH-ERR-02:

   * `project_id` = same project as RUN-ERR-01A.
   * `phase_id` = `"PH-ERR-02"`.
   * `workstream_id` = `"WS-ERR-02A"`.
   * `task_kind` = `"analysis"` or `"other"`, depending on T1.
   * `classification` = derived from PH-ERR-01 run (complexity, risk tier).
   * `files_scope` = subset from PH-ERR-02.files_scope:

     * read from quarantine patch dir, logs, code.
   * `constraints` = from PH-ERR-02 + WS-ERR-02A.

7. New **RunRecord** `RUN-ERR-02A` is created:

   * `run_id` = new ULID.
   * `phase_id = "PH-ERR-02"`.
   * `origin.trigger_type = "error_pipeline"`.
   * `origin.trigger_ref = RUN-ERR-01A.run_id` or the id of the `error_pipeline_triggered` event.

8. Run events:

   * `run_created` (for RUN-ERR-02A).
   * `run_started` when T1 is enqueued.

### 5.3 WS-ERR-02A executes and completes handoff

9. **Task T1 (collect context)**:

   * Tool (`claude_cli` or `codex_cli`) is called with a strict `analysis` prompt.
   * Produces a human-readable summary plus references to patch ids, failing tests, logs.
   * `StepAttempt` logged with `tool_call_started` / `tool_call_completed`.
   * Acceptance check `summary_nonempty` passes.

10. **Task T2 (GitHub artifact)**:

    * `github_worker` reads T1’s summary and patch info.
    * Calls GitHub API to create a PR or Issue.
    * On success, writes:

      * A link or ID for the GitHub artifact into Run state (e.g., `github_artifact_id`).
      * Optionally writes a `.md` note into `docs/error_pipeline/escalations/`.
    * Emits RunEvents:

      * `tool_call_started`
      * `tool_call_completed`
      * `note` with `github_artifact_url`
    * Acceptance check `github_artifact_created` passes.

11. **Run-level acceptance in PH-ERR-02**:

    * `acceptance.checks` from PH-ERR-02 and WS-ERR-02A all evaluate to true:

      * `github_artifact_created == true`
      * `all_quarantined_patches_linked == true`
    * `RunRecord RUN-ERR-02A.state` transitions:

      * `running → succeeded`
      * `RunEvent: run_state_changed` with reason `"escalation_complete"`.

12. **Back-link to original run / patch**:

    * Ledger entries for quarantined patches can record:

      * `relations.chain_id` linking PH-ERR-01 and PH-ERR-02 runs.
      * `relations.replaces_patch_id` or `rollback_of_patch_id` if a future patch supersedes the quarantined one.
    * A human seeing the GitHub PR/Issue can jump back to:

      * Quarantine folder patch file.
      * Logs for RUN-ERR-01A and RUN-ERR-02A.

---

## 6. Why this bundle is minimal but complete

* **PH-ERR-01 + WS-ERR-01A**:

  * Responsible for all **automated repair attempts**.
  * Owns patch creation and application.

* **PH-ERR-02 + WS-ERR-02A**:

  * Responsible for **human handoff**, with no further code edits.
  * Owns summarization and external GitHub-facing workflow.

* Chaining is:

  * Explicit and **machine-readable** via:

    * `error_handling.error_phase_id`,
    * `RunEvent.kind = error_pipeline_triggered`,
    * new `ExecutionRequest` seeded from that event.
  * **No magic strings** or hidden coupling: everything is declared in phase + workstream specs.

If you want to keep iterating in planning, the next refinement step could be:

* Define a **tiny schema for “github_worker”** (its config and expected inputs/outputs), so it becomes a first-class tool in `TASK_ROUTING_SPEC` and can be swapped or extended without touching the PH-ERR specs.
