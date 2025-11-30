---
doc_id: DOC-CORE-UET-COOPERATION-SPEC-193
---

Here’s a structured formalization of **COOPERATION_SPEC** as a *framework-level spec*, in the same style as the others (PROMPT / TASK_ROUTING / PATCH).

No prose doc, just: **objects, schemas, and behavior rules**.

---

## 1. Role & Position of COOPERATION_SPEC

**Doc meta**

* `doc_type`: `core_spec`
* `doc_layer`: `framework`
* `schema_ref`: `schema/cooperation_spec.v1.json`

**Responsibility**

COOPERATION_SPEC defines:

1. The **run/step/event model** for multi-tool cooperation.
2. The **worker & queue model** (who does what, and where).
3. The **zone model** (EDIT / STATIC / RUNTIME) and which actions are allowed in each.
4. The **coordination rules** between:

   * Orchestrator
   * Background workers
   * CLI tools (Aider, Codex CLI, Claude, etc.)
   * Error pipeline phases

It glues together:

* **ExecutionRequest** (from TASK_ROUTING_SPEC),
* **PromptInstance** (from PROMPT_RENDERING_SPEC),
* **PatchArtifact + PatchLedgerEntry** (from PATCH_MANAGEMENT_SPEC),
* **Phase / Workstream** (from PHASE_SPEC_MASTER / WORKSTREAM_SPEC),
  into one coherent **cooperation protocol**.

---

## 2. Core Object #1 – `RunRecord`

A **Run** is the top-level execution of a phase/workstream (or a single ExecutionRequest). It’s the thing you’d see on a dashboard.

### 2.1 Conceptual shape

```json
{
  "run_id": "01J2ZC987XY0ABCDEF12345678",
  "project_id": "PRJ-HUEY_P",
  "phase_id": "PH-ERR-01",
  "workstream_id": "WS-ERR-01A",
  "execution_request_id": "01J2Z9M2F0N6ABCD1234567890",
  "created_at": "2025-11-20T10:40:00Z",
  "started_at": "2025-11-20T10:40:05Z",
  "ended_at": null,
  "state": "running",
  "state_reason": "initial_tool_call",
  "origin": {
    "trigger_type": "error_pipeline",
    "trigger_ref": "ERR-PATCH-CHAIN-01",
    "requested_by": "SYSTEM:ERROR_PIPELINE"
  },
  "counters": {
    "step_attempts": 1,
    "patches_created": 1,
    "patches_applied": 0,
    "errors": 0
  }
}
```

### 2.2 `RunRecord` JSON Schema (high-level)

`schema/run_record.v1.json`:

```json
{
  "$id": "schema/run_record.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RunRecord v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "run_id",
    "project_id",
    "phase_id",
    "state",
    "created_at"
  ],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "project_id": { "type": "string", "minLength": 1 },
    "phase_id": { "type": "string", "minLength": 1 },
    "workstream_id": { "type": ["string", "null"] },
    "execution_request_id": {
      "type": ["string", "null"],
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "created_at": { "type": "string", "format": "date-time" },
    "started_at": { "type": ["string", "null"], "format": "date-time" },
    "ended_at": { "type": ["string", "null"], "format": "date-time" },
    "state": {
      "type": "string",
      "enum": [
        "pending",
        "running",
        "succeeded",
        "failed",
        "canceled",
        "quarantined"
      ]
    },
    "state_reason": {
      "type": ["string", "null"]
    },
    "origin": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "trigger_type": {
          "type": "string",
          "enum": [
            "manual",
            "ci",
            "error_pipeline",
            "scheduled",
            "other"
          ]
        },
        "trigger_ref": { "type": ["string", "null"] },
        "requested_by": { "type": ["string", "null"] }
      }
    },
    "counters": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "step_attempts": { "type": "integer", "minimum": 0 },
        "patches_created": { "type": "integer", "minimum": 0 },
        "patches_applied": { "type": "integer", "minimum": 0 },
        "errors": { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

**Invariants:**

* `state` moves through a defined lifecycle (see §5).
* A Run is the parent for:

  * StepAttempts
  * PatchLedgerEntries
  * Events

---

## 3. Core Object #2 – `StepAttempt`

A **StepAttempt** is a single call to a tool (Aider, Codex, Claude, etc.) for this run.

### 3.1 Conceptual shape

```json
{
  "step_attempt_id": "01J2ZCD4JX8P6M9QW3E7K2ABC",
  "run_id": "01J2ZC987XY0ABCDEF12345678",
  "sequence": 1,
  "tool_id": "aider",
  "tool_run_id": "AIDER-RUN-2025-11-20-001",
  "execution_request_id": "01J2Z9M2F0N6ABCD1234567890",
  "prompt_id": "01J2Z8X9ABCDEF1234567890AB",
  "started_at": "2025-11-20T10:40:05Z",
  "ended_at": "2025-11-20T10:40:45Z",
  "state": "completed",
  "state_reason": "patch_produced",
  "outputs": {
    "patch_ids": [
      "01J2ZB1B3Y5D0C8QK7F3HA2XYZ"
    ],
    "logs_path": "C:\\logs\\runs\\01J2ZC987XY0ABCDEF12345678\\aider-001.log",
    "raw_response_path": "C:\\logs\\runs\\01J2ZC987XY0ABCDEF12345678\\aider-001.txt"
  }
}
```

### 3.2 `StepAttempt` JSON Schema (high-level)

`schema/step_attempt.v1.json`:

```json
{
  "$id": "schema/step_attempt.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StepAttempt v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "step_attempt_id",
    "run_id",
    "sequence",
    "tool_id",
    "state",
    "started_at"
  ],
  "properties": {
    "step_attempt_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "run_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "sequence": {
      "type": "integer",
      "minimum": 1
    },
    "tool_id": { "type": "string", "minLength": 1 },
    "tool_run_id": { "type": ["string", "null"] },
    "execution_request_id": {
      "type": ["string", "null"],
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "prompt_id": {
      "type": ["string", "null"],
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "started_at": { "type": "string", "format": "date-time" },
    "ended_at": { "type": ["string", "null"], "format": "date-time" },
    "state": {
      "type": "string",
      "enum": [
        "pending",
        "running",
        "completed",
        "error",
        "canceled"
      ]
    },
    "state_reason": {
      "type": ["string", "null"]
    },
    "outputs": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "patch_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
          },
          "uniqueItems": true
        },
        "logs_path": { "type": ["string", "null"] },
        "raw_response_path": { "type": ["string", "null"] }
      }
    }
  }
}
```

**Invariants:**

* `sequence` is monotonically increasing per `run_id`.
* A StepAttempt is always associated with:

  * one Run,
  * one tool,
  * at most one ExecutionRequest (often the same for the full run).

---

## 4. Core Object #3 – `RunEvent`

A **RunEvent** is an append-only log entry. This is your **observability bus**.

### 4.1 Conceptual shape

```json
{
  "event_id": "01J2ZCFD4N0Q8ABCDEF1234567",
  "run_id": "01J2ZC987XY0ABCDEF12345678",
  "step_attempt_id": "01J2ZCD4JX8P6M9QW3E7K2ABC",
  "ts": "2025-11-20T10:40:06Z",
  "kind": "tool_call_started",
  "payload": {
    "tool_id": "aider",
    "execution_request_id": "01J2Z9M2F0N6ABCD1234567890"
  }
}
```

### 4.2 `RunEvent` JSON Schema (high-level)

`schema/run_event.v1.json`:

```json
{
  "$id": "schema/run_event.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RunEvent v1",
  "type": "object",
  "additionalProperties": false,
  "required": ["event_id", "run_id", "ts", "kind"],
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "run_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "step_attempt_id": {
      "type": ["string", "null"],
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "ts": { "type": "string", "format": "date-time" },
    "kind": {
      "type": "string",
      "enum": [
        "run_created",
        "run_started",
        "run_state_changed",
        "tool_call_started",
        "tool_call_completed",
        "tool_call_error",
        "patch_created",
        "patch_validated",
        "patch_apply_started",
        "patch_apply_succeeded",
        "patch_apply_failed",
        "patch_quarantined",
        "error_pipeline_triggered",
        "phase_transition",
        "note"
      ]
    },
    "payload": {
      "type": "object"
    }
  }
}
```

**Invariants:**

* Events are **append-only**; no in-place edits.
* Every state transition in Run / Step / Patch **must** correspond to at least one RunEvent.
* Error pipeline entry is always visible as `error_pipeline_triggered`.

---

## 5. Worker & Queue Model

COOPERATION_SPEC defines **who does what**, and the directories/queues they watch.

### 5.1 Worker types

At minimum:

* **Router Worker**

  * Consumes `ExecutionRequest` objects (from TASK_ROUTING_SPEC).
  * Performs:

    * phase compatibility checks,
    * route selection,
    * prompt construction.
  * Produces:

    * tool-specific **ToolWorkItem** objects into tool queues.

* **Tool Worker (per CLI tool)**

  * Watches a tool-specific queue (e.g., `.tasks/aider/inbox/`).
  * For each ToolWorkItem:

    * Renders prompt via PROMPT_RENDERING_SPEC.
    * Executes CLI tool.
    * Captures raw response.
    * Normalizes patch outputs into `PatchArtifact` (if code_edit).
    * Emits StepAttempt + RunEvents.

* **Patch Worker**

  * Consumes `PatchArtifact` + context.
  * Validates via PATCH_MANAGEMENT_SPEC.
  * Applies in the correct EDIT zone (worktree).
  * Runs tests.
  * Updates PatchLedgerEntry and emits events.
  * On failures, triggers error pipeline runs (PH-ERR-XX).

* **Error Pipeline Worker**

  * Executes PH-ERR-XX phases for quarantined patches or repeated failures.
  * Uses same ExecutionRequest → Prompt → Patch cycle, but under PH-ERR phases.

(There can be more specialized workers later; above is the minimal abstraction.)

### 5.2 ToolWorkItem shape

This is the payload a Tool Worker receives.

```json
{
  "tool_work_item_id": "01J2ZCZZ1234ABCDE56789FGH",
  "run_id": "01J2ZC987XY0ABCDEF12345678",
  "step_attempt_id": "01J2ZCD4JX8P6M9QW3E7K2ABC",
  "tool_id": "aider",
  "execution_request_id": "01J2Z9M2F0N6ABCD1234567890",
  "prompt_instance": {
    /* full PromptInstance object from PROMPT_RENDERING_SPEC */
  }
}
```

**Invariants:**

* A Tool Worker is **not allowed** to:

  * Directly write to repo files outside its ephemeral workspace.
  * Directly commit changes.
  * Apply patches – this is the Patch Worker’s job.

---

## 6. Zone Model – EDIT / STATIC / RUNTIME

COOPERATION_SPEC defines the zones and allowed actions:

### 6.1 Zones

* **STATIC zone**

  * Allowed:

    * Read-only access to:

      * project docs,
      * specs,
      * codebase (as of a baseline commit).
  * Forbidden:

    * Any write to tracked project files.
  * Typical actors:

    * Router Worker (reading Phase specs, etc.).
    * Tools doing pure analysis tasks.

* **EDIT zone**

  * A **Git worktree or equivalent** per Run/Workstream.
  * Allowed:

    * Applying patches validated by PATCH_MANAGEMENT_SPEC.
    * Creating new files within allowed FILES_SCOPE.
  * Forbidden:

    * Direct manual edits by tools (no `echo >> file` style writes).
    * Edits outside declared FILES_SCOPE.
  * Typical actors:

    * Patch Worker.
    * Tests.

* **RUNTIME zone**

  * Operational environment where:

    * built artifacts run,
    * services deploy,
    * scheduled tasks execute.
  * PATCH_MANAGEMENT_SPEC usually only touches this via:

    * deployments based on committed changes.

**Invariants:**

* Tools operate conceptually in STATIC (reading) + generating patches; not in EDIT.
* All file mutations happen via **patch application** in EDIT zone, under Patch Worker control.
* RUNTIME updates (deploy) only from committed + verified changes.

---

## 7. Run Lifecycle State Machine

COOPERATION_SPEC defines Run state transitions (tying together all workers):

**States:**

* `pending` – Run created, not yet started.
* `running` – At least one StepAttempt in progress or queued.
* `succeeded` – All required steps completed; phase acceptance met.
* `failed` – Unrecoverable error, or max retries exceeded.
* `quarantined` – Run associated with quarantined patches / critical errors.
* `canceled` – Manually or programmatically canceled.

**Core transitions (examples):**

* `pending → running`

  * When first StepAttempt is started.

* `running → succeeded`

  * When:

    * Required patches applied and committed, AND
    * Phase acceptance checks (tests, validations) pass.

* `running → failed`

  * When:

    * No further routing options remain, AND/OR
    * A fatal error occurs (e.g., policy violations, corrupt repo).

* `running → quarantined`

  * When:

    * One or more patches are quarantined due to repeated failures, OR
    * Error pipeline declares the run unsafe.

* `running → canceled`

  * Manual operator / higher-level policy.

COOPERATION_SPEC requires:

* Each transition is accompanied by a `run_state_changed` event.
* Error pipeline entry is explicit (via `error_pipeline_triggered`).

---

## 8. Cooperation Rules (Who Does What)

COOPERATION_SPEC should encode **hard boundaries** between roles:

### 8.1 Orchestrator

* Owns:

  * Runs / StepAttempts / Events DB.
  * Routing logic (via TASK_ROUTING_SPEC).
  * Enforcement of Phase & Patch policies.
* Must:

  * Validate all ExecutionRequests & PromptInstances before calling tools.
  * Refuse execution when required data is missing or invalid.
* Must not:

  * Apply patches directly (delegates to Patch Worker).
  * Let tools bypass patch pipeline.

### 8.2 CLI Tools (Aider, Codex CLI, etc.)

* Allowed:

  * Read files within declared FILES_SCOPE (or read-only copy).
  * Emit:

    * Unified diffs (for code_edit tasks),
    * Explanations/analysis (for analysis tasks).
* Must:

  * Respect OUTPUT_SPEC (no ad-hoc output formats).
* Must not:

  * Directly write project files.
  * Commit changes.
  * Access paths outside FILES_SCOPE.

### 8.3 Patch Worker

* Owns:

  * Patch validation, application, tests.
* Must:

  * Enforce PATCH_MANAGEMENT_SPEC invariants.
  * Update PatchLedgerEntry state.
  * Emit relevant RunEvents.

### 8.4 Error Pipeline Worker

* Owns:

  * PH-ERR-XX phases.
* Must:

  * Handle quarantined patches & failed runs.
  * Produce new patches or decisions (e.g., “open GitHub issue”).

---

## 9. Integration with Other Specs (Summary)

* **PROMPT_RENDERING_SPEC**

  * COOPERATION_SPEC uses `PromptInstance` inside `ToolWorkItem`.
  * Ensures that tool cooperation always goes through validated prompts.

* **TASK_ROUTING_SPEC**

  * Provides `ExecutionRequest`s that seed Runs and StepAttempts.
  * Router Worker behavior lives at the boundary between TASK_ROUTING_SPEC and COOPERATION_SPEC.

* **PATCH_MANAGEMENT_SPEC**

  * COOPERATION_SPEC defines how patches move through workers and states.
  * Patch Worker is the concrete agent of PATCH_MANAGEMENT_SPEC.

* **PHASE_SPEC_MASTER / WORKSTREAM_SPEC**

  * Drive:

    * Run creation,
    * Acceptance criteria,
    * Which tools & tasks are allowed in a Run.

* **ERROR_PIPELINE_SPEC**

  * Cooperates via:

    * RunEvents of type `error_pipeline_triggered`.
    * New Runs in PH-ERR phases, with their own ExecutionRequests, prompts, and patches.

---

If you’re happy with this, the next logical piece (still planning-only) would be to outline **PHASE_SPEC_MASTER** so its `files_scope`, `constraints`, and `acceptance` sections align exactly with:

* `ExecutionRequest.files_scope` / `.constraints`,
* `PatchPolicy` limits,
* Run `succeeded` criteria in COOPERATION_SPEC.
