---
doc_id: DOC-CORE-UET-PATCH-MANAGEMENT-SPEC-MD-001
---

Good target. Let’s lock down **what PATCH_MANAGEMENT_SPEC actually is** in your stack and define the core data structures + rules, without writing an actual spec file yet.

I’ll treat it just like we did PROMPT_RENDERING_SPEC and TASK_ROUTING_SPEC: **schemas + behaviors + invariants.**

---

## 1. Role & position of PATCH_MANAGEMENT_SPEC

* `doc_type`: `core_spec`
* `doc_layer`: `framework`
* It owns the rules and schemas for:

  1. **PatchArtifact** – the actual unified diff + metadata.
  2. **PatchLedgerEntry** – how every patch is logged, validated, and tracked.
  3. **PatchPolicy** – constraints and rules about what patches are allowed.

And it defines how patches interact with:

* **PHASE_SPEC_MASTER** (per-phase constraints: scope, tests, limits).
* **TASK_ROUTING_SPEC** (ExecutionRequest.constraints.patch_only, max_lines, etc.).
* **PROMPT_RENDERING_SPEC** (OUTPUT_SPEC telling tools to output unified diffs only).
* **ERROR_PIPELINE_SPEC** (what happens on patch failure → quarantine / escalation).

---

## 2. Core object #1 – `PatchArtifact`

This is the *canonical representation* of a patch: one patch, one diff, with enough metadata that any agent/tool can understand it.

### 2.1 Conceptual shape

```json
{
  "patch_id": "01J2ZB1B3Y5D0C8QK7F3HA2XYZ",
  "format": "unified_diff",
  "target_repo": "C:\\Users\\richg\\HIGH_LEVEL_MOD_PLUGIN_DEV",
  "base_ref": "main",
  "base_commit": "a1b2c3d4e5f6g7h8i9j0",
  "origin": {
    "execution_request_id": "01J2Z9M2F0N6ABCD1234567890",
    "prompt_id": "01J2Z8X9ABCDEF1234567890AB",
    "phase_id": "PH-ERR-01",
    "workstream_id": "WS-ERR-01A",
    "tool_id": "aider",
    "tool_run_id": "AIDER-RUN-2025-11-20-001",
    "created_at": "2025-11-20T10:25:00Z"
  },
  "summary": "Tighten error pipeline file routing and add quarantine directory creation.",
  "scope": {
    "files_touched": [
      "src/error_pipeline/handler.py",
      "src/error_pipeline/paths.py"
    ],
    "line_insertions": 34,
    "line_deletions": 12,
    "hunks": 4
  },
  "diff_text": "diff --git a/src/error_pipeline/handler.py b/src/error_pipeline/handler.py\n@@ -1,5 +1,8 @@\n ... (full unified diff text here) ...\n"
}
```

### 2.2 `PatchArtifact` JSON Schema (high-level)

`schema/patch_artifact.v1.json`:

```json
{
  "$id": "schema/patch_artifact.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PatchArtifact v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "patch_id",
    "format",
    "target_repo",
    "origin",
    "diff_text"
  ],
  "properties": {
    "patch_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "format": {
      "type": "string",
      "enum": ["unified_diff"]
    },
    "target_repo": {
      "type": "string",
      "minLength": 1
    },
    "base_ref": {
      "type": ["string", "null"]
    },
    "base_commit": {
      "type": ["string", "null"]
    },
    "origin": {
      "type": "object",
      "additionalProperties": false,
      "required": ["execution_request_id", "tool_id", "created_at"],
      "properties": {
        "execution_request_id": {
          "type": "string",
          "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
        },
        "prompt_id": {
          "type": ["string", "null"]
        },
        "phase_id": {
          "type": ["string", "null"]
        },
        "workstream_id": {
          "type": ["string", "null"]
        },
        "tool_id": {
          "type": "string",
          "minLength": 1
        },
        "tool_run_id": {
          "type": ["string", "null"]
        },
        "created_at": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "summary": {
      "type": "string",
      "maxLength": 512
    },
    "scope": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "files_touched": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "line_insertions": {
          "type": "integer",
          "minimum": 0
        },
        "line_deletions": {
          "type": "integer",
          "minimum": 0
        },
        "hunks": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "diff_text": {
      "type": "string",
      "minLength": 1
    }
  }
}
```

**Key invariants from PATCH_MANAGEMENT_SPEC:**

* `format` **must** be `"unified_diff"`; no raw file dumps, no proprietary formats.
* `diff_text` **must** parse as a valid unified diff.
* `scope.files_touched` **must** match the filenames extracted from `diff_text` (or be omitted and derived by the patch engine if not provided).
* No patch is applied unless it first passes **this** schema and the additional checks below.

---

## 3. Core object #2 – `PatchLedgerEntry`

Every patch that exists in the system gets a ledger entry. This is the **audit trail** and lifecycle record.

Think of this as what you store under `.ledger/patches/` alongside the .patch file.

### 3.1 Conceptual shape

```json
{
  "ledger_id": "01J2ZBA14T8C7M0ZPB4G3J8XYZ",
  "patch_id": "01J2ZB1B3Y5D0C8QK7F3HA2XYZ",
  "project_id": "PRJ-HUEY_P",
  "phase_id": "PH-ERR-01",
  "workstream_id": "WS-ERR-01A",
  "execution_request_id": "01J2Z9M2F0N6ABCD1234567890",
  "state": "validated",
  "state_history": [
    {
      "state": "created",
      "at": "2025-11-20T10:25:02Z",
      "reason": "captured_from_tool"
    },
    {
      "state": "validated",
      "at": "2025-11-20T10:25:05Z",
      "reason": "scope_ok_constraints_ok"
    }
  ],
  "validation": {
    "format_ok": true,
    "scope_ok": true,
    "constraints_ok": true,
    "tests_ran": true,
    "tests_passed": false,
    "validation_errors": [
      "tests_failed: 2 failing unit tests"
    ]
  },
  "apply": {
    "attempts": 1,
    "last_attempt_at": "2025-11-20T10:26:00Z",
    "last_error_code": "tests_failed",
    "last_error_message": "pytest reported 2 failing tests",
    "workspace_path": "C:\\repos\\error_pipeline_ws-err-01a",
    "applied_files": [
      "src/error_pipeline/handler.py"
    ]
  },
  "quarantine": {
    "is_quarantined": true,
    "quarantine_reason": "tests_failed_after_max_attempts",
    "quarantine_path": "C:\\QUARANTINE\\patches\\PH-ERR-01\\01J2ZB1B3Y5D0C8QK7F3HA2XYZ.patch",
    "quarantined_at": "2025-11-20T10:27:30Z"
  },
  "relations": {
    "replaces_patch_id": null,
    "rollback_of_patch_id": null,
    "chain_id": "CHAIN-PH-ERR-01-001"
  }
}
```

### 3.2 `PatchLedgerEntry` JSON Schema (high-level)

`schema/patch_ledger_entry.v1.json`:

```json
{
  "$id": "schema/patch_ledger_entry.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PatchLedgerEntry v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "ledger_id",
    "patch_id",
    "project_id",
    "state",
    "validation"
  ],
  "properties": {
    "ledger_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "patch_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "project_id": { "type": "string", "minLength": 1 },
    "phase_id": { "type": ["string", "null"] },
    "workstream_id": { "type": ["string", "null"] },
    "execution_request_id": {
      "type": ["string", "null"],
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "state": {
      "type": "string",
      "enum": [
        "created",
        "validated",
        "queued",
        "applied",
        "apply_failed",
        "verified",
        "committed",
        "rolled_back",
        "quarantined",
        "dropped"
      ]
    },
    "state_history": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["state", "at"],
        "properties": {
          "state": { "type": "string" },
          "at": { "type": "string", "format": "date-time" },
          "reason": { "type": "string" }
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["format_ok", "scope_ok", "constraints_ok"],
      "properties": {
        "format_ok": { "type": "boolean" },
        "scope_ok": { "type": "boolean" },
        "constraints_ok": { "type": "boolean" },
        "tests_ran": { "type": "boolean" },
        "tests_passed": { "type": "boolean" },
        "validation_errors": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "apply": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "attempts": { "type": "integer", "minimum": 0 },
        "last_attempt_at": { "type": "string", "format": "date-time" },
        "last_error_code": { "type": "string" },
        "last_error_message": { "type": "string" },
        "workspace_path": { "type": "string" },
        "applied_files": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        }
      }
    },
    "quarantine": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "is_quarantined": { "type": "boolean" },
        "quarantine_reason": { "type": "string" },
        "quarantine_path": { "type": "string" },
        "quarantined_at": { "type": "string", "format": "date-time" }
      }
    },
    "relations": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "replaces_patch_id": {
          "type": ["string", "null"],
          "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
        },
        "rollback_of_patch_id": {
          "type": ["string", "null"],
          "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
        },
        "chain_id": { "type": ["string", "null"] }
      }
    }
  }
}
```

**Key invariants from PATCH_MANAGEMENT_SPEC:**

* Every `PatchArtifact` that enters the system **must** have a `PatchLedgerEntry`.
* Patch state transitions must follow the state machine (see next section).
* Quarantined patches **must not** be auto-applied again without explicit human/agent override.

---

## 4. Core object #3 – `PatchPolicy`

This encodes the **rules** about what kind of patches are allowed. It ties into:

* `doc_meta.patch_policy` (per-doc).
* `PHASE_SPEC_MASTER` (per-phase).
* Global defaults.

### 4.1 Conceptual shape

```json
{
  "patch_policy_id": "GLOBAL_POLICY_V1",
  "scope": {
    "level": "global",                  // global | project | phase | doc
    "project_id": null,
    "phase_id": null,
    "doc_ulid": null
  },
  "constraints": {
    "allowed_formats": ["unified_diff"],
    "patch_required": true,
    "max_lines_changed": 300,
    "max_files_changed": 10,
    "forbid_binary_patches": true,
    "forbid_touching_paths": [
      "secrets/*",
      ".git/*"
    ],
    "require_tests_for_paths": [
      "src/**/*.py",
      "src/**/*.mq4"
    ],
    "require_issue_ref": true,
    "min_reviewers": 1,
    "oscillation_window": 5,
    "oscillation_threshold": 3
  }
}
```

### 4.2 `PatchPolicy` JSON Schema (high-level)

`schema/patch_policy.v1.json`:

```json
{
  "$id": "schema/patch_policy.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PatchPolicy v1",
  "type": "object",
  "additionalProperties": false,
  "required": ["patch_policy_id", "scope", "constraints"],
  "properties": {
    "patch_policy_id": {
      "type": "string",
      "minLength": 1
    },
    "scope": {
      "type": "object",
      "additionalProperties": false,
      "required": ["level"],
      "properties": {
        "level": {
          "type": "string",
          "enum": ["global", "project", "phase", "doc"]
        },
        "project_id": { "type": ["string", "null"] },
        "phase_id": { "type": ["string", "null"] },
        "doc_ulid": { "type": ["string", "null"] }
      }
    },
    "constraints": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "allowed_formats": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "patch_required": {
          "type": "boolean",
          "default": true
        },
        "max_lines_changed": {
          "type": "integer",
          "minimum": 1
        },
        "max_files_changed": {
          "type": "integer",
          "minimum": 1
        },
        "forbid_binary_patches": {
          "type": "boolean",
          "default": true
        },
        "forbid_touching_paths": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "require_tests_for_paths": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "require_issue_ref": {
          "type": "boolean",
          "default": true
        },
        "min_reviewers": {
          "type": "integer",
          "minimum": 0,
          "default": 1
        },
        "oscillation_window": {
          "type": "integer",
          "minimum": 1
        },
        "oscillation_threshold": {
          "type": "integer",
          "minimum": 1
        }
      }
    }
  }
}
```

**Layering rule:**

* More specific policies (phase, doc) can only **tighten** constraints vs global, never loosen them. E.g.:

  * Global `max_lines_changed = 300` → phase can set `100`, not `500`.

---

## 5. Patch lifecycle state machine

PATCH_MANAGEMENT_SPEC should define a **state diagram** for patches; here’s the logical set:

**States:**

* `created` – captured from tool output, not yet validated.
* `validated` – format + scope + constraints checked.
* `queued` – accepted for possible application.
* `applied` – successfully applied to a worktree.
* `apply_failed` – failed to apply or tests failed.
* `verified` – applied + tests passed + manual checks (optional).
* `committed` – changes committed to repo.
* `rolled_back` – applied, then reverted.
* `quarantined` – isolated and blocked.
* `dropped` – rejected and discarded (but ledger entry remains).

**Allowed transitions (examples):**

* `created → validated` (if schema + basic checks OK).
* `validated → queued` (if policy allows).
* `queued → applied` (patch applied cleanly).
* `applied → verified` (tests & additional checks pass).
* `applied → apply_failed` (conflict, or tests fail).
* `verified → committed` (changes merged/committed).
* `apply_failed → quarantined` (after max retries).
* `validated → quarantined` (if policy violation discovered later).
* Any state → `dropped` (manual/admin override).

PATCH_MANAGEMENT_SPEC says:

* Patch engine **must not** commit any patch that hasn’t been at least `applied` + `verified`.
* Quarantined patches **must** be written to a quarantine folder (per your error pipeline path rules) and clearly tagged in the ledger.

---

## 6. Validation and safety checks

For **every patch** before applying:

1. **Schema validation**

   * Validate `PatchArtifact` against `patch_artifact.v1.json`.
   * If invalid → `format_ok = false`; state `created → dropped`.

2. **Scope vs ExecutionRequest**

   * Compare `PatchArtifact.scope.files_touched` with `ExecutionRequest.files_scope`.
   * Every touched file must be allowed for write/create.
   * If any forbidden path touched → `scope_ok = false`; state `created → quarantined`.

3. **Scope vs PhaseSpec**

   * Ensure files are allowed within the phase’s `files_scope` (PHASE_SPEC_INSTANCE).
   * Phase constraints may prohibit editing certain shared or critical files.

4. **Constraints vs PatchPolicy**

   * Check `max_lines_changed`, `max_files_changed`.
   * Verify no binary patches if `forbid_binary_patches`.
   * Ensure tests are required and run when touching specified paths.

5. **Oscillation detection**

   * Use `oscillation_window` and `oscillation_threshold`:

     * e.g., N patches in the last M attempts that toggle the same lines/files.
     * If threshold exceeded → automatically route to error pipeline + quarantine.

Only when **format_ok, scope_ok, constraints_ok** are all true → patch can advance to `validated` and then `queued`.

---

## 7. Integration with other specs

### 7.1 With PROMPT_RENDERING_SPEC

* For `code_edit` prompts, `OUTPUT_SPEC` in PROMPT_RENDERING_SPEC **must** instruct tools to return:

  * Either pure unified diff text, or
  * A JSON object that contains a `PatchArtifact`-compatible structure.

* PATCH_MANAGEMENT_SPEC requires that:

  * Any patch-like answer from tools is normalized into a `PatchArtifact`.
  * Prompts that ask for direct file rewrites violate `patch_only` and should be rejected by the orchestrator.

### 7.2 With TASK_ROUTING_SPEC

* `ExecutionRequest.constraints.patch_only = true` informs routing & output specs.
* Task router:

  * Must ensure any tool selected for `code_edit` tasks *supports* unified diffs.
  * Must store the resulting patch in the ledger and associate it with the `ExecutionRequest`.

### 7.3 With PHASE_SPEC_MASTER

* Phase specs define baseline patch constraints (max lines/files, allowed paths, etc.).
* PATCH_MANAGEMENT_SPEC enforces that:

  * PatchPolicy for the phase cannot relax these.
  * Any patch violating phase rules is blocked and sent into PH-ERR error phases.

### 7.4 With COOPERATION_SPEC / ERROR_PIPELINE_SPEC

* Patch states (`apply_failed`, `quarantined`, `oscillation`) emit events:

  * These events trigger:

    * Error pipeline workstreams (PH-ERR-01/02).
    * Automated creation of GitHub issues, etc.
* Quarantine folder structure and GitHub-save behavior for repeated failures live in ERROR_PIPELINE_SPEC, but PATCH_MANAGEMENT_SPEC defines **when** a patch becomes eligible for those flows.

---

## 8. Big picture: what PATCH_MANAGEMENT_SPEC guarantees

Once this is implemented:

* **All edits** (code and machine-readable docs) flow through a **patch-first** pipeline.
* Every patch:

  * Has a unique ULID and structured metadata.
  * Is validated against schemas + phase rules + patch policy.
  * Leaves an auditable trail in the ledger.
* No tool can silently:

  * Edit forbidden files,
  * Bypass tests (when required),
  * Or circumvent the patch ledger.

And any future module (error pipeline, file manager, trading module, etc.) can plug into this same patch framework without reinventing the rules.

If you want, the *next* planning move could be to outline **PHASE_SPEC_MASTER** so its `files_scope` and `constraints` line up cleanly with `ExecutionRequest` and `PatchPolicy`.
