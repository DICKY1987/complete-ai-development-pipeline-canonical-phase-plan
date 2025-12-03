---
doc_id: DOC-CORE-UET-WORKSTREAM-SPEC-199
---

Here’s a clean formalization of **WORKSTREAM_SPEC** that fits with everything we already defined (PHASE_SPEC_MASTER, ExecutionRequest, PromptInstance, Patch, Run, etc.).

Staying in **schema/structure mode only**, no narrative doc.

---

## 1. Role & position of WORKSTREAM_SPEC

**WORKSTREAM_SPEC (core spec)**

* `doc_type`: `core_spec`
* `doc_layer`: `framework`
* Owns the schema: `schema/workstream_spec.v1.json`

**Workstream instance docs**

* `doc_type`: `workstream_spec`
* `doc_layer`: usually `project` or `module`
* Conform to `workstream_spec.v1.json`
* Typically named like: `WS-ERR-01A_error_pipeline_intake.yaml`

**Responsibility**

`WORKSTREAM_SPEC` defines how to describe a *bundle of tasks* that:

* Operate **within** a phase (`phase_id`).
* Produce 0+ **ExecutionRequests** (from TASK_ROUTING_SPEC).
* Use **PromptInstance** (from PROMPT_RENDERING_SPEC).
* Generate **PatchArtifact**s (PATCH_MANAGEMENT_SPEC).
* Are tracked inside a **Run** (COOPERATION_SPEC).

---

## 2. Top-level `WorkstreamSpec` object

Conceptual YAML shape for a workstream instance:

```yaml
workstream_id: "WS-ERR-01A"
project_id: "PRJ-HUEY_P"
phase_id: "PH-ERR-01"

name: "Error Patch Intake for Single Patch"
category: "error_pipeline"          # e.g. core_dev, refactor, migration, infra, analysis, etc.
description: "Validate, apply, and route a single failing patch into quarantine or escalation."

objective: "Take one failing patch and either safely apply+verify it or quarantine and escalate."

tags:
  - "error"
  - "patch"
  - "quarantine"

files_scope:            # optional; must be ⊆ phase.files_scope
  read:
    - "src/error_pipeline/**/*.py"
  write:
    - "src/error_pipeline/**/*.py"
  create:
    - "src/error_pipeline/migrations/**/*.py"
  forbidden:
    - ".git/**"
    - "secrets/**"

constraints:            # optional; can only tighten phase.constraints
  patch:
    max_lines_changed: 120
  tests:
    tests_must_run: true
  behavior:
    max_attempts_per_run: 2

concurrency:
  mode: "sequential"    # "sequential" | "parallel" | "parallel_groups"
  max_parallel: 1       # relevant when mode != sequential

error_handling:
  default_on_task_failure: "fail_workstream"  # or "skip_task", "route_error_phase"
  max_task_retries: 2
  error_phase_id: "PH-ERR-02"                # optional, for escalation

acceptance:             # optional, extra gates beyond phase.acceptance
  mode: "all"
  checks:
    - id: "no_unhandled_errors"
      type: "run_state"
      description: "Workstream must finish with no failed tasks."
      condition: "failed_tasks == 0"
      required: true
      severity: "error"
  post_actions: []
  
tasks:
  - ... TaskSpec ...
```

---

## 3. `WorkstreamSpec` JSON Schema (high-level)

File: `schema/workstream_spec.v1.json`

```json
{
  "$id": "schema/workstream_spec.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WorkstreamSpec v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "workstream_id",
    "project_id",
    "phase_id",
    "name",
    "objective",
    "tasks"
  ],
  "properties": {
    "workstream_id": {
      "type": "string",
      "minLength": 1
    },
    "project_id": {
      "type": "string",
      "minLength": 1
    },
    "phase_id": {
      "type": "string",
      "minLength": 1
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "category": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "objective": {
      "type": "string",
      "minLength": 1
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "minLength": 1 },
      "uniqueItems": true
    },
    "files_scope": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "read": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "write": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "create": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "forbidden": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        }
      }
    },
    "constraints": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "patch": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "max_lines_changed": { "type": "integer", "minimum": 1 },
            "max_files_changed": { "type": "integer", "minimum": 1 }
          }
        },
        "tests": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "tests_must_run": { "type": "boolean" },
            "tests_must_pass": { "type": "boolean" }
          }
        },
        "behavior": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "max_attempts_per_run": { "type": "integer", "minimum": 1 }
          }
        }
      }
    },
    "concurrency": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["sequential", "parallel", "parallel_groups"]
        },
        "max_parallel": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "error_handling": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "default_on_task_failure": {
          "type": "string",
          "enum": [
            "fail_workstream",
            "skip_task",
            "route_error_phase"
          ]
        },
        "max_task_retries": {
          "type": "integer",
          "minimum": 0
        },
        "error_phase_id": {
          "type": ["string", "null"]
        }
      }
    },
    "acceptance": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["all", "any", "custom"]
        },
        "checks": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["id", "type"],
            "properties": {
              "id": { "type": "string", "minLength": 1 },
              "type": {
                "type": "string",
                "enum": [
                  "test_command",
                  "patch_state",
                  "file_presence",
                  "run_state",
                  "custom_hook"
                ]
              },
              "description": { "type": "string" },
              "command": { "type": "string" },
              "condition": { "type": "string" },
              "path_glob": { "type": "string" },
              "required": { "type": "boolean" },
              "severity": {
                "type": "string",
                "enum": ["info", "warning", "error"]
              }
            }
          }
        },
        "post_actions": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      }
    },
    "tasks": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "task_spec.v1.json" }
    }
  }
}
```

> In your real schema you’d inline or `$ref` the `TaskSpec` definition (next section) rather than literally `"task_spec.v1.json"`; I’m keeping it conceptual here.

---

## 4. `TaskSpec` – unit of work inside a workstream

Each entry in `tasks:` is a **TaskSpec**.

### 4.1 Conceptual YAML shape for one task

```yaml
- task_id: "T1"
  name: "Analyze failing patch and derive minimal fix"
  description: "Ask tool to inspect the failing patch and propose a corrected version."

  sequence: 1                # ordering hint when mode=sequential
  kind: "analysis"           # aligns with ExecutionRequest.task_kind and Prompt kind
  phase_id: "PH-ERR-01"      # optional override; defaults to workstream.phase_id

  depends_on: []             # list of other task_ids this task waits on
  allow_parallel: false      # can this run parallel with other non-dependent tasks?

  classification:
    complexity: "medium"
    risk_tier: "R2"
    domain: "error_pipeline"
    priority: "normal"

  files_scope_delta:         # optional, must narrow workstream/phase scopes
    read:
      - "src/error_pipeline/**/*.py"
    write: []                # analysis only, so typically empty
    create: []
    forbidden: []

  constraints_delta:         # optional, must tighten phase/workstream constraints
    patch:
      max_lines_changed: 0   # analysis; no patch expected
    tests:
      tests_must_run: false  # analysis only
    behavior: {}

  execution:
    max_attempts: 1
    timeout_seconds: 600
    background: false
    retry_strategy:
      mode: "none"           # "none" | "simple" | "exponential"
      max_attempts: 1

  prompt_template_ref: "TEMPLATE_WORKSTREAM_V1_1"
  prompt_overrides:
    OBJECTIVE_suffix: "Focus only on understanding what went wrong with the patch, do not propose edits yet."

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
    on_failure: "route_error_phase"     # "fail_workstream" | "skip_task" | "route_error_phase"
    error_phase_id: "PH-ERR-02"
    note: "If tool cannot analyze patch, escalate to manual review phase."

  acceptance:
    mode: "any"
    checks:
      - id: "analysis_output_nonempty"
        type: "run_state"
        description: "Task must produce non-empty analysis output."
        condition: "task_output_size > 0"
        required: true
        severity: "error"
```

Not all fields will be required; schema will define which are optional.

---

## 5. `TaskSpec` JSON Schema (high-level)

File: `schema/task_spec.v1.json`

```json
{
  "$id": "schema/task_spec.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskSpec v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "task_id",
    "name",
    "kind"
  ],
  "properties": {
    "task_id": {
      "type": "string",
      "minLength": 1
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "sequence": {
      "type": "integer",
      "minimum": 1
    },
    "kind": {
      "type": "string",
      "enum": [
        "code_edit",
        "code_review",
        "analysis",
        "planning",
        "refactor",
        "documentation",
        "other"
      ]
    },
    "phase_id": {
      "type": ["string", "null"]
    },
    "depends_on": {
      "type": "array",
      "items": { "type": "string", "minLength": 1 },
      "uniqueItems": true
    },
    "allow_parallel": {
      "type": "boolean",
      "default": false
    },
    "classification": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "complexity": {
          "type": "string",
          "enum": ["low", "medium", "high"]
        },
        "risk_tier": {
          "type": "string",
          "enum": ["R1", "R2", "R3"]
        },
        "domain": { "type": "string" },
        "priority": {
          "type": "string",
          "enum": ["low", "normal", "high", "urgent"]
        }
      }
    },
    "files_scope_delta": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "read": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "write": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "create": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "forbidden": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        }
      }
    },
    "constraints_delta": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "patch": {
          "type": "object"
        },
        "tests": {
          "type": "object"
        },
        "behavior": {
          "type": "object"
        },
        "routing": {
          "type": "object"
        }
      }
    },
    "execution": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "max_attempts": {
          "type": "integer",
          "minimum": 1
        },
        "timeout_seconds": {
          "type": "integer",
          "minimum": 10
        },
        "background": {
          "type": "boolean",
          "default": false
        },
        "retry_strategy": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "mode": {
              "type": "string",
              "enum": ["none", "simple", "exponential"]
            },
            "max_attempts": {
              "type": "integer",
              "minimum": 1
            }
          }
        }
      }
    },
    "prompt_template_ref": {
      "type": ["string", "null"]
    },
    "prompt_overrides": {
      "type": "object"
    },
    "execution_request_template": {
      "type": "object"
    },
    "error_handling": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "on_failure": {
          "type": "string",
          "enum": [
            "fail_workstream",
            "skip_task",
            "route_error_phase"
          ]
        },
        "error_phase_id": {
          "type": ["string", "null"]
        },
        "note": {
          "type": "string"
        }
      }
    },
    "acceptance": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["all", "any", "custom"]
        },
        "checks": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      }
    }
  }
}
```

(Again, in practice you’d likely `$ref` shared “check” structures so phase & workstream & task acceptance all share the same shape.)

---

## 6. How WORKSTREAM_SPEC plugs into the rest of the stack

### 6.1 With PHASE_SPEC_MASTER

* `workstream.phase_id` must reference a valid phase instance.
* `workstream.files_scope` (if present) must be **subset** of `phase.files_scope`.
* Each task’s:

  * `phase_id` (if set) must reference a valid phase.
  * `files_scope_delta` must further **narrow** workstream/phase scopes; never expand.
* `workstream.constraints` and `task.constraints_delta` can only **tighten** phase-level constraints.

### 6.2 With TASK_ROUTING_SPEC / ExecutionRequest

For each `TaskSpec` that is “ready to run”, the orchestrator:

1. Resolves:

   * Phase (from task.phase_id or workstream.phase_id),
   * Effective `files_scope`:

     * Phase.files_scope
       ⟶ intersect with workstream.files_scope (if any)
       ⟶ then apply task.files_scope_delta (narrowing).
   * Effective `constraints`:

     * Phase.constraints
       ⟶ tighten with workstream.constraints
       ⟶ tighten with task.constraints_delta.

2. Builds an `ExecutionRequest` using:

   * `task.kind` → `ExecutionRequest.task_kind`.
   * `task.classification` → `ExecutionRequest.classification`.
   * Effective `files_scope` → `ExecutionRequest.files_scope`.
   * Effective `constraints` → `ExecutionRequest.constraints`.
   * `task.execution_request_template` → default `prompt_spec` & `routing` for this task.

3. Validates ExecutionRequest against `execution_request.schema.json` and PHASE constraints.

### 6.3 With PROMPT_RENDERING_SPEC

* `task.prompt_template_ref` and `execution_request_template.prompt_spec.template_id` must be valid template IDs defined in PROMPT_RENDERING_SPEC.
* `task.kind` must align with prompt `kind` (`code_edit`, `analysis`, etc.).
* Any `prompt_overrides` are applied when building the `PromptInstance` before rendering.

### 6.4 With PATCH_MANAGEMENT_SPEC

* For `code_edit` tasks:

  * Effective constraints (phase + workstream + task) become the **patch policy** for patches produced from that task.
  * PatchWorker uses:

    * Effective `files_scope`,
    * Effective patch limits (lines/files),
    * Task classification (risk tier, complexity),
      to validate patches.

### 6.5 With COOPERATION_SPEC

* A **Run** typically corresponds to one workstream instance execution.
* Each `TaskSpec` maps to one or more **StepAttempt**s:

  * Sequencing governed by `sequence` + `depends_on` + `concurrency.mode`.
* `workstream.acceptance` contributes to Run’s final decision:

  * Combined with `phase.acceptance` to decide `Run.state` (`succeeded`, `failed`, `quarantined`).
* `error_handling` at workstream and task levels drives:

  * Whether a failed task:

    * Fails the whole run,
    * Is skipped,
    * Or launches an error-phase workstream (PH-ERR).

---

This gives you a **formal shape** for WORKSTREAM_SPEC that:

* Is phase-aware (via `phase_id` and scope/constraint tightening).
* Produces well-formed ExecutionRequests.
* Plugs into Prompt, Patch, and Run orchestration.
* Stays patch-friendly and machine-readable for your agentic pipeline.

Whenever you’re ready, we can pick **one concrete workstream** (e.g., `WS-ERR-01A`) and, still in a structured way, map its tasks to this schema to sanity-check the design—without yet writing full, final docs.
