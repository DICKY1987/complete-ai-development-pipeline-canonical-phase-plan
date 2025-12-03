---
doc_id: DOC-GUIDE-UET-WS-ERR-01A-1647
---

Good target for a dry-run. Let’s treat this as a **design rehearsal** for `WS-ERR-01A`, not a final document.

I’ll do three things:

1. Propose an **illustrative WS-ERR-01A** mapped to the `WORKSTREAM_SPEC` schema (focus on `tasks`).
2. Show how each task maps into **ExecutionRequest / Prompt / Patch / Run**.
3. Call out any **design tweaks** we might want.

---

## 1. WS-ERR-01A – illustrative mapping to WORKSTREAM_SPEC

This is **pseudo-YAML**, meant only as a schema sanity check:

````yaml
workstream_id: "WS-ERR-01A"
project_id: "PRJ-HUEY_P"
phase_id: "PH-ERR-01"

name: "Error Patch Intake for Single Patch"
category: "error_pipeline"
description: "Validate, apply, and route a single failing patch into quarantine or escalation."
objective: "Take one failing patch produced elsewhere and either safely apply+verify it or quarantine and escalate."

tags:
  - "error"
  - "patch"
  - "quarantine"

# Optional: narrower than phase.files_scope, but not wider
files_scope:
  read:
    - "src/error_pipeline/**/*.py"
    - "docs/error_pipeline/**/*.md"
  write:
    - "src/error_pipeline/**/*.py"
  create: []
  forbidden:
    - ".git/**"
    - "secrets/**"

# Optional: tighter than PH-ERR-01 constraints
constraints:
  patch:
    max_lines_changed: 150     # phase might allow 200; this tightens
  tests:
    tests_must_run: true       # matches / tightens phase.tests
  behavior:
    max_attempts_per_run: 2    # phase may allow 3; this tightens

concurrency:
  mode: "sequential"
  max_parallel: 1

error_handling:
  default_on_task_failure: "route_error_phase"
  max_task_retries: 1
  error_phase_id: "PH-ERR-02"

acceptance:
  mode: "all"
  checks:
    - id: "no_failed_tasks"
      type: "run_state"
      description: "Workstream completes with no failed tasks."
      condition: "failed_tasks == 0"
      required: true
      severity: "error"
  post_actions: []

tasks:
  # T1: Normalize a raw failing patch into a PatchArtifact + ledger entry
  - task_id: "T1-normalize-patch"
    name: "Normalize failing patch into PatchArtifact"
    description: "Take an existing failing patch and normalize it into PatchArtifact + PatchLedgerEntry for this run."
    sequence: 1
    kind: "analysis"                  # no edits yet, just structure/metadata
    phase_id: "PH-ERR-01"
    depends_on: []
    allow_parallel: false

    classification:
      complexity: "low"
      risk_tier: "R1"
      domain: "error_pipeline"
      priority: "normal"

    files_scope_delta:
      read:
        - "patches/incoming/*.patch"  # logical location for raw patch
      write: []
      create: []
      forbidden: []

    constraints_delta:
      patch:
        max_lines_changed: 0          # this task should not create new patches
      tests:
        tests_must_run: false
      behavior: {}

    execution:
      max_attempts: 1
      timeout_seconds: 120
      background: false
      retry_strategy:
        mode: "none"
        max_attempts: 1

    # In practice this might be a non-AI internal worker; we still model it cleanly
    execution_request_template:
      task_kind: "analysis"
      prompt_spec:
        template_id: "TEMPLATE_WORKSTREAM_V1_1"
        kind: "analysis"
      routing:
        strategy: "fixed"
        preferred_tools: ["patch_intake_worker"]
        allowed_tools: ["patch_intake_worker"]

    error_handling:
      on_failure: "route_error_phase"
      error_phase_id: "PH-ERR-02"

    acceptance:
      mode: "all"
      checks:
        - id: "patch_artifact_created"
          type: "patch_state"
          description: "A valid PatchArtifact + PatchLedgerEntry exist for this run."
          condition: "count_patch_artifacts_for_run >= 1"
          required: true
          severity: "error"

  # T2: Ask AI to inspect the failing patch and propose corrections (no direct edits yet)
  - task_id: "T2-analyze-patch"
    name: "Analyze failing patch and propose corrected change"
    description: "Use an AI tool to analyze why the current patch fails and propose a corrected diff."
    sequence: 2
    kind: "analysis"
    phase_id: "PH-ERR-01"
    depends_on:
      - "T1-normalize-patch"
    allow_parallel: false

    classification:
      complexity: "medium"
      risk_tier: "R2"
      domain: "error_pipeline"
      priority: "normal"

    files_scope_delta:
      read:
        - "src/error_pipeline/**/*.py"
        - "patches/incoming/*.patch"
      write: []
      create: []
      forbidden: []

    constraints_delta:
      patch:
        max_lines_changed: 0          # still analysis only
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
      OBJECTIVE_suffix: "Explain why the patch fails and outline a minimal corrective diff. Do NOT propose direct file edits; output diff-only."

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
      on_failure: "route_error_phase"
      error_phase_id: "PH-ERR-02"

    acceptance:
      mode: "all"
      checks:
        - id: "analysis_nonempty"
          type: "run_state"
          description: "AI produced a non-empty explanation or suggested diff."
          condition: "task_output_size > 0"
          required: true
          severity: "error"

  # T3: Ask AI to emit a unified diff patch for the corrected change
  - task_id: "T3-generate-patch"
    name: "Generate corrected patch via AI"
    description: "Use AI to generate a unified diff patch implementing the corrected change for the error pipeline."
    sequence: 3
    kind: "code_edit"
    phase_id: "PH-ERR-01"
    depends_on:
      - "T2-analyze-patch"
    allow_parallel: false

    classification:
      complexity: "medium"
      risk_tier: "R2"
      domain: "error_pipeline"
      priority: "normal"

    files_scope_delta:
      read:
        - "src/error_pipeline/**/*.py"
      write:
        - "src/error_pipeline/**/*.py"    # allowed write targets for this task
      create: []
      forbidden: []

    constraints_delta:
      patch:
        max_lines_changed: 80             # tighter than workstream-level 150
        max_files_changed: 3
      tests:
        tests_must_run: true
        tests_must_pass: true
      behavior: {}

    execution:
      max_attempts: 2
      timeout_seconds: 900
      background: false
      retry_strategy:
        mode: "simple"
        max_attempts: 2

    prompt_template_ref: "TEMPLATE_WORKSTREAM_V1_1"
    prompt_overrides:
      OUTPUT_SPEC: "Return a single unified diff only, in ```diff``` fenced code block. Do not restate the patch in any other format."

    execution_request_template:
      task_kind: "code_edit"
      prompt_spec:
        template_id: "TEMPLATE_WORKSTREAM_V1_1"
        kind: "code_edit"
      routing:
        strategy: "auto"
        preferred_tools: ["aider"]
        allowed_tools: ["aider", "codex_cli"]

    error_handling:
      on_failure: "route_error_phase"
      error_phase_id: "PH-ERR-02"

    acceptance:
      mode: "all"
      checks:
        - id: "patch_created"
          type: "patch_state"
          description: "A syntactically valid unified diff PatchArtifact exists for this task."
          condition: "count_valid_patches_for_task >= 1"
          required: true
          severity: "error"

  # T4: Apply patch + run tests via Patch Worker; decide between success or quarantine/escalation
  - task_id: "T4-apply-and-verify"
    name: "Apply patch and verify via tests"
    description: "Apply the generated patch in the EDIT zone, run tests, and either accept or quarantine."
    sequence: 4
    kind: "other"                         # no AI; pure patch worker + tests
    phase_id: "PH-ERR-01"
    depends_on:
      - "T3-generate-patch"
    allow_parallel: false

    classification:
      complexity: "medium"
      risk_tier: "R2"
      domain: "error_pipeline"
      priority: "high"

    files_scope_delta:
      read:
        - "src/error_pipeline/**/*.py"
      write:
        - "src/error_pipeline/**/*.py"
      create: []
      forbidden: []

    constraints_delta:
      patch:
        max_lines_changed: 80
      tests:
        tests_must_run: true
        tests_must_pass: true
      behavior: {}

    execution:
      max_attempts: 1
      timeout_seconds: 900
      background: false
      retry_strategy:
        mode: "none"
        max_attempts: 1

    execution_request_template:
      task_kind: "other"
      prompt_spec: null                  # not needed; Patch Worker doesn’t use LLM prompt
      routing:
        strategy: "fixed"
        preferred_tools: ["patch_worker"]
        allowed_tools: ["patch_worker"]

    error_handling:
      on_failure: "route_error_phase"
      error_phase_id: "PH-ERR-02"
      note: "If tests fail or patch violates scope/constraints, quarantine patch and trigger PH-ERR-02."

    acceptance:
      mode: "all"
      checks:
        - id: "tests_green"
          type: "test_command"
          description: "All error pipeline tests must pass after patch."
          command: "pytest -q tests/error_pipeline"
          required: true
          severity: "error"
        - id: "no_quarantined_patches"
          type: "patch_state"
          description: "No patches left in quarantined state for this run."
          condition: "count_quarantined_patches == 0"
          required: true
          severity: "error"
````

---

## 2. How each task flows through the other specs

### T1 – Normalize failing patch

* **Phase / Files scope**

  * Reads only from `patches/incoming/*.patch`.
  * No writes; matches `kind: analysis`.
  * Scoped under `PH-ERR-01.files_scope` (assumed to allow reading from patch inbox).

* **ExecutionRequest**

  * `task_kind = analysis`.
  * `files_scope.read = ["patches/incoming/*.patch"]`.
  * Constraints set so **no patch creation** happens here (`max_lines_changed = 0`).

* **Prompt / Tool**

  * Modeled as calling a `patch_intake_worker` (non-LLM internal worker).
  * This worker could, in practice, be a simple script that parses diff and populates PatchArtifact/ledger.

* **Patch**

  * Output is a structured PatchArtifact with metadata; ledger entry moves to `created` / `validated`.

### T2 – Analyze patch (AI)

* **Phase / Scope / Constraints**

  * Read-only: code and patch; no writes.
  * `kind: analysis` + `max_lines_changed = 0` ensures no patch is produced.

* **ExecutionRequest**

  * `task_kind = analysis`, `kind = analysis` in PromptSpec.
  * Tools permitted: `claude_cli`, `codex_cli`.

* **Prompt / Tool**

  * Uses `TEMPLATE_WORKSTREAM_V1_1` plus OBJECTIVE suffix that bans file edits.
  * Output is explanatory text and maybe a “plan” for the fix, but not applied yet.

### T3 – Generate corrected patch (AI)

* **Phase / Scope / Constraints**

  * Read + write access limited to `src/error_pipeline/**/*.py`.
  * Tight patch limits (80 lines / 3 files) vs phase (200 lines / more files).

* **ExecutionRequest**

  * `task_kind = code_edit`; flows into TASK_ROUTING_SPEC.
  * Constraints align with PATCH_MANAGEMENT_SPEC (patch_only, max lines/files).

* **Prompt / Tool**

  * PROMPT_RENDERING_SPEC ensures OUTPUT_SPEC demands unified diff only.
  * Tools (`aider`, `codex_cli`) must obey patch-only route.

* **Patch**

  * Tool output normalized into `PatchArtifact`.
  * Ledger entry moves to `created` → `validated` if it passes patch rules.

### T4 – Apply + tests (Patch Worker)

* **Phase / Scope / Constraints**

  * Work happens in EDIT zone only (Git worktree per Run).
  * Tests required and must pass.

* **ExecutionRequest**

  * `task_kind = other`; no LLM involvement.
  * Routed to `patch_worker` as a “tool” in the same routing framework.

* **Patch / Run / Error pipeline**

  * PatchWorker:

    * Validates patch vs phase/workstream constraints.
    * Applies patch in worktree.
    * Runs tests.
    * Updates PatchLedgerEntry state.
  * If tests fail or constraints violated:

    * PatchLedgerEntry → `apply_failed` / `quarantined`.
    * RunEvent `error_pipeline_triggered`.
    * ErrorHandling `route_error_phase` launches PH-ERR-02.

* **Acceptance**

  * If T4 acceptance checks pass (tests, no quarantined patches):

    * This plus phase + workstream acceptance gives `Run.state = succeeded`.

---

## 3. Sanity-check observations & tweak points

**✅ Good alignment:**

* **Scope tightening:**
  Workstream `files_scope` is a subset of phase; each task’s `files_scope_delta` is narrower still (e.g., read-only for analysis, limited write for patch generation).

* **Constraint hierarchy:**
  Phase → Workstream → Task all follow “tighten only” rules:

  * T3/T4 patch limits ≤ workstream ≤ phase.
  * Tests are always required where code changes happen.

* **Clear separation of roles:**

  * AI tools only read + emit diffs (T2/T3).
  * Patch worker is the only thing that applies patches and runs tests (T4).
  * Non-LLM workers (e.g., `patch_intake_worker`) are still modeled via the same ExecutionRequest / routing system so cooperation stays uniform.

* **Error handling paths:**

  * All tasks point failures to PH-ERR-02 via `route_error_phase`.
  * T4 explicitly defines quarantine behavior through Patch/Run acceptance checks.

**🔍 Things to decide explicitly later (not blockers):**

* Whether you want **T1** to be a “true task” in the workstream or a pre-Run hook. Modeling it as a task is fine, but you might eventually move it into a “intake prelude” if it’s always required and never varies.

* How rich you want `execution_request_template` to be for **non-LLM workers** (`patch_intake_worker`, `patch_worker`). The schema supports them, but you may want a mini “NON_LLM_TOOL_SPEC” so they don’t need prompt-related fields at all.

---

From a schema perspective, `WS-ERR-01A` with these four tasks **fits cleanly** into:

* `PHASE_SPEC_MASTER` (phase ID, scopes, constraints),
* `WORKSTREAM_SPEC` (workstream + tasks),
* `TASK_ROUTING_SPEC` (ExecutionRequests + routing),
* `PROMPT_RENDERING_SPEC` (prompt kinds, sections, tool adapters),
* `PATCH_MANAGEMENT_SPEC` (PatchArtifact/ledger/policy),
* `COOPERATION_SPEC` (Run/StepAttempts/Events).

If you want to push the design further in planning, the next angle could be:

* Define a minimal **“Error Pipeline Bundle”**:

  * `PH-ERR-01` + `WS-ERR-01A` (intake),
  * `PH-ERR-02` + a second workstream for escalation / GitHub PR creation,
  * and sketch how those two phases chain via RunEvents and error handling.
