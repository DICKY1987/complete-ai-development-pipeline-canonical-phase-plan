Nice, this is where everything starts to snap together.

I’ll keep this as an **outline + structure** for `PHASE_SPEC_MASTER`, and focus on the three key sections you named:

* `files_scope`
* `constraints`
* `acceptance`

I’ll also show how each one aligns with:

* `ExecutionRequest.files_scope` / `.constraints`
* `PatchPolicy`
* Run `succeeded` in COOPERATION_SPEC.

No full prose spec, just structure and behavior.

---

## 1. Position & role of PHASE_SPEC_MASTER

**PHASE_SPEC_MASTER** defines the template/schema for all *phase instance* docs like `PH-ERR-01`, `PH-CORE-05`, etc.

* `doc_type`: `phase_spec_master`
* `doc_layer`: `framework`
* It owns `phase_spec.schema.json`, which all `phase_spec_instance` docs must conform to.

Each **phase instance** doc will have:

* Doc meta (from `doc-meta.v1`)
* Phase body with (at minimum):

  ```yaml
  phase_id: "PH-ERR-01"
  name: "Error Patch Intake and Quarantine"
  category: "error_pipeline"   # or core_dev, refactor, migration, etc.
  description: "..."
  files_scope: { ... }
  constraints: { ... }
  acceptance: { ... }
  routing_defaults: { ... }    # optional but common
  patch_policy_ref: "PATCH_POLICY_ERR_V1"  # optional link
  ```

Below is how those three big sections should look.

---

## 2. `files_scope` – phase-level file permissions contract

This is the **authoritative contract** for which files this phase may touch and how. ExecutionRequests and PatchArtifacts must *not exceed* this.

### 2.1 Conceptual structure

At phase level:

```yaml
files_scope:
  read:
    - "src/error_pipeline/**/*.py"
    - "docs/error_pipeline/**/*.md"
  write:
    - "src/error_pipeline/**/*.py"
  create:
    - "src/error_pipeline/migrations/**/*.py"
  forbidden:
    - "src/core/security/**"
    - ".git/**"
    - "secrets/**"

  # Optional: per-path overrides
  strict:
    - path: "src/error_pipeline/handler.py"
      max_lines_changed: 80
    - path: "src/error_pipeline/paths.py"
      max_lines_changed: 40
```

### 2.2 Key semantics

* `read`
  Glob patterns for files the phase may **read** (tools can inspect these).

* `write`
  Glob patterns for files the phase may **modify** (via patches, never direct edits).

* `create`
  Where **new** files may be created (e.g., migration scripts, new modules).

* `forbidden`
  Paths that this phase **must never** touch—even if they match other patterns.

* `strict` (optional, but powerful)
  Path-specific fine-grained limits (e.g., “this hot file may only be changed by ≤ X lines per patch”).

### 2.3 Invariants vs other specs

* For any `ExecutionRequest ER` under this phase:

  * `ER.files_scope.read` ⊆ `Phase.files_scope.read`
  * `ER.files_scope.write` ⊆ `Phase.files_scope.write`
  * `ER.files_scope.create` ⊆ `Phase.files_scope.create`
  * `ER.files_scope.forbidden` ⊇ `Phase.files_scope.forbidden`

* For any `PatchArtifact P` applied under this phase:

  * `P.scope.files_touched` must:

    * match `Phase.files_scope.write/create` and **not** match `forbidden`.
    * respect any `strict` override limits (see `constraints` below).

If these conditions fail, PATCH_MANAGEMENT_SPEC / TASK_ROUTING_SPEC must reject and send to error pipeline.

---

## 3. `constraints` – safety & behavior rules for this phase

This is where PHASE_SPEC_MASTER encodes **what is allowed** and **how strict** this phase is. Think of this as the per-phase version of:

* `ExecutionRequest.constraints`
* `PatchPolicy.constraints`
* Development rules (tests, patch-only, etc.)

### 3.1 Conceptual structure

```yaml
constraints:
  patch:
    patch_required: true
    allowed_formats: ["unified_diff"]
    max_lines_changed: 200           # per patch
    max_files_changed: 6             # per patch
    forbid_binary_patches: true
    require_issue_ref: true
    min_reviewers: 1

  tests:
    tests_must_run: true
    tests_must_pass: true
    test_command: "pytest -q"
    extra_test_commands:
      - "pytest -q tests/error_pipeline"
    skip_allowed: false
    allowed_skip_reasons: []         # or ["no_tests_available"] in some phases

  behavior:
    ascii_only: true
    forbid_direct_file_writes: true
    require_doc_update: false        # e.g. for some phases, set true
    max_attempts_per_run: 3
    max_step_attempts_per_tool: 2

  routing:
    allowed_tools:
      - "aider"
      - "codex_cli"
    disallowed_tools:
      - "dangerous_experimental_tool"
    default_task_kinds:
      - "code_edit"
      - "analysis"
```

You can think of four subgroups:

1. `patch` – patch-specific rules.
2. `tests` – testing/verification rules.
3. `behavior` – agent behavior rules.
4. `routing` – what tools and task types are legal in this phase.

### 3.2 Tightening-only rule

For any `ExecutionRequest` under this phase:

* `ER.constraints` can only **tighten** these phase constraints, never relax them. Examples:

  * If `phase.constraints.tests_must_pass = true`, ER cannot set `tests_must_pass = false`.
  * If `phase.constraints.max_lines_changed = 200`, ER can set `100` but not `300`.

Similarly, `PatchPolicy` at phase/doc level can only **tighten** global policy.

---

## 4. `acceptance` – when a phase is “done” / Run can go to `succeeded`

This is the **gating logic** that COOPERATION_SPEC will use to move `Run.state` from `running` → `succeeded`.

### 4.1 Conceptual structure

Break `acceptance` into:

* **checks** – what must be true.
* **mode** – all vs any vs custom.
* **post_actions** – optional follow-ups (like “open GitHub PR”).

```yaml
acceptance:
  mode: "all"    # "all", "any", or "custom"

  checks:
    - id: "tests_green"
      type: "test_command"
      description: "All tests must pass in this module."
      command: "pytest -q tests/error_pipeline"
      required: true
      severity: "error"

    - id: "no_quarantined_patches"
      type: "patch_state"
      description: "No patches for this phase may be in 'quarantined' state."
      condition: "count_quarantined_patches == 0"
      required: true
      severity: "error"

    - id: "doc_update_optional"
      type: "file_presence"
      description: "Docs updated when public behavior changes."
      path_glob: "docs/error_pipeline/*.md"
      required: false
      severity: "warning"

  post_actions:
    - id: "open_github_pr"
      type: "github_action"
      when: "phase_succeeded"
      enabled: true
      config:
        repo: "user/error-pipeline-repo"
        target_branch: "main"
        title_template: "[PH-ERR-01] Error pipeline patch chain"
```

### 4.2 Check types (examples)

PHASE_SPEC_MASTER should define a small set of **check types** that the orchestrator knows how to evaluate:

* `test_command`

  * Run a shell command in the EDIT zone workspace.
  * Success = exit code 0 (unless otherwise configured).
* `patch_state`

  * Query patch ledger for this `phase_id` / `run_id`.
  * Examples:

    * `no_quarantined_patches`
    * `all_required_patches_committed`
* `file_presence`

  * Ensure certain files exist or were changed.
  * Example: docs updated when behavior changes.
* `custom_hook`

  * Reserved for pluggable checks (e.g., call an external service).

### 4.3 Acceptance vs Run state

COOPERATION_SPEC uses `acceptance` as:

* Transition rule for `Run.state`:

  * `running → succeeded` if all required `acceptance.checks` pass (for `mode: "all"`).
  * If any `required` check fails with `severity: "error"`:

    * `running → failed` or `running → quarantined` depending on the check.

* Error pipeline triggering:

  * Certain check failures (e.g., tests failing after `max_attempts_per_run`) will:

    * Trigger an `error_pipeline_triggered` event.
    * Start a PH-ERR phase run.

---

## 5. How these 3 sections align with other specs (wiring summary)

### 5.1 With TASK_ROUTING_SPEC

* `files_scope`

  * ExecutionRequest’s `files_scope` must be a **subset** of the phase’s `files_scope`.
* `constraints`

  * ExecutionRequest’s `.constraints` must **tighten** the phase’s constraints.
  * `routing.allowed_tools` must be compatible with phase’s `constraints.routing.allowed_tools / disallowed_tools`.

### 5.2 With PATCH_MANAGEMENT_SPEC

* `files_scope` + `constraints.patch`

  * Phase defines:

    * which files can be touched,
    * limits on lines/files,
    * whether patch-only is required.
  * Patch policy for the phase is derived from or references these values.
  * Patch Worker must enforce these before applying any `PatchArtifact`.

### 5.3 With COOPERATION_SPEC

* `acceptance`

  * Defines the **gating conditions** for Run `succeeded`.
  * COOPERATION_SPEC’s Run engine knows how to:

    * Evaluate tests and ledger-based checks,
    * Use acceptance to decide `succeeded` vs `failed` vs `quarantined`.

### 5.4 With PROMPT_RENDERING_SPEC

* `constraints` and `files_scope` inform prompt sections:

  * `FILES_SCOPE` section in the prompt is generated from `phase.files_scope` intersected with `ExecutionRequest.files_scope`.
  * `CONSTRAINTS` section in the prompt uses `phase.constraints` as a baseline, possibly tightened by ExecutionRequest.

---

## 6. Minimal phase instance outline (bringing it together)

Putting it all in one **outline** for a concrete phase (not writing the actual document, just structure):

```yaml
---
# Doc Meta goes here (doc-meta.v1)
---

phase_id: "PH-ERR-01"
name: "Error Patch Intake and Quarantine"
category: "error_pipeline"
description: "Handle failing patches and route them to quarantine or escalation."

files_scope:
  read:
    - "src/error_pipeline/**/*.py"
    - "docs/error_pipeline/**/*.md"
  write:
    - "src/error_pipeline/**/*.py"
  create:
    - "src/error_pipeline/migrations/**/*.py"
  forbidden:
    - ".git/**"
    - "secrets/**"
  strict:
    - path: "src/error_pipeline/handler.py"
      max_lines_changed: 80

constraints:
  patch:
    patch_required: true
    allowed_formats: ["unified_diff"]
    max_lines_changed: 200
    max_files_changed: 6
    forbid_binary_patches: true
    require_issue_ref: true
    min_reviewers: 1

  tests:
    tests_must_run: true
    tests_must_pass: true
    test_command: "pytest -q tests/error_pipeline"
    skip_allowed: false

  behavior:
    ascii_only: true
    forbid_direct_file_writes: true
    require_doc_update: false
    max_attempts_per_run: 3

  routing:
    allowed_tools:
      - "aider"
      - "codex_cli"
    disallowed_tools: []

acceptance:
  mode: "all"
  checks:
    - id: "tests_green"
      type: "test_command"
      description: "All error pipeline tests must pass."
      command: "pytest -q tests/error_pipeline"
      required: true
      severity: "error"

    - id: "no_quarantined_patches"
      type: "patch_state"
      description: "No patches left in quarantined state for this run."
      condition: "count_quarantined_patches == 0"
      required: true
      severity: "error"

  post_actions: []
```

That’s the **outline** – with `files_scope`, `constraints`, and `acceptance` shaped to plug directly into your other specs and be validated + enforced in a fully deterministic, agentic pipeline.

If you want to keep going in planning mode, the next thing we could outline is **WORKSTREAM_SPEC** so a workstream/phase plan instance can reference `phase_id` and fill in specific tasks that respect these `files_scope` / `constraints` / `acceptance` rules.
