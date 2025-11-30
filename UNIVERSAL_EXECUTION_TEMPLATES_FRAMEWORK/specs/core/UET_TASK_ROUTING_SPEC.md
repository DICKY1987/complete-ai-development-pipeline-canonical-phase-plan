---
doc_id: DOC-CORE-UET-TASK-ROUTING-SPEC-198
---

Short answer: **yes** – in your world, `TASK_ROUTING_SPEC` should always be phase-aware and treat `PHASE_SPEC_MASTER` as the “contract of record” for what a task is allowed to do (FILES_SCOPE, CONSTRAINTS, OUTPUT_SPEC, etc.).

Below I’ll **formalize `TASK_ROUTING_SPEC` as a schema + behavior**, and show exactly how it plugs into:

* `PHASE_SPEC_MASTER` / `phase_spec.schema.json`
* `PROMPT_RENDERING_SPEC` / `prompt_instance.v1.json`

No prose spec file, just the **shape and rules**.

---

## 1. Role of `TASK_ROUTING_SPEC` in the stack

**Doc meta (from Doc Meta Schema)**

* `doc_type`: `core_spec`
* `doc_layer`: `framework`
* `schema_ref`: `schema/task_routing_spec.v1.json`

**Responsibility**

`TASK_ROUTING_SPEC` defines three things:

1. **ExecutionRequest schema**
   The *canonical task object* that moves through the system.

2. **RouterConfig schema** (`router.config.yaml`)
   How tasks are matched to tools/apps and routing strategies.

3. **Guard / Validation rules**
   How to:

   * Cross-check each `ExecutionRequest` against:

     * `PHASE_SPEC_MASTER` (`phase_spec.schema.json`)
     * `PROMPT_RENDERING_SPEC` (`prompt_instance.v1.json`)
   * Reject anything that violates FILES_SCOPE, CONSTRAINTS, OUTPUT_SPEC contracts.

So: **Phase defines what’s allowed**, **Prompt defines how we talk to tools**, **Task routing ensures the tool and route respect both.**

---

## 2. Core object #1 – `ExecutionRequest`

This is the *unit of work* your orchestrator routes. Think of it as the JSON your `.tasks/inbox` queue represents.

### 2.1 ExecutionRequest – conceptual shape

```json
{
  "request_id": "01J2Z9M2F0N6ABCD1234567890",
  "project_id": "PRJ-HUEY_P",
  "phase_id": "PH-ERR-01",
  "workstream_id": "WS-ERR-01A",
  "task_kind": "code_edit",
  "origin": {
    "source_app": "orchestrator",
    "created_by": "SYSTEM:ERROR_PIPELINE",
    "created_at": "2025-11-20T10:10:00Z"
  },

  "classification": {
    "complexity": "medium",
    "risk_tier": "R2",
    "domain": "error_pipeline",
    "priority": "normal"
  },

  "files_scope": {
    "read": [
      "src/error_pipeline/*.py"
    ],
    "write": [
      "src/error_pipeline/handler.py"
    ],
    "create": [],
    "forbidden": [
      "src/core/security/*"
    ]
  },

  "constraints": {
    "tests_must_pass": true,
    "patch_only": true,
    "ascii_only": true,
    "max_lines_changed": 200
  },

  "prompt_spec": {
    "template_id": "TEMPLATE_WORKSTREAM_V1_1",
    "kind": "code_edit",
    "prompt_instance_id": null
  },

  "routing": {
    "strategy": "auto",
    "preferred_tools": ["aider"],
    "allowed_tools": ["aider", "codex_cli"],
    "max_attempts": 3,
    "timeout_seconds": 900
  },

  "telemetry": {
    "correlation_id": "CORR-2025-11-20-ERR-01",
    "trace_flags": ["log_prompt", "log_patches"]
  }
}
```

### 2.2 `ExecutionRequest` JSON Schema (high-level)

Call this `schema/execution_request.schema.json`. (You already reference a file with this name in the Game Board doc.)

```json
{
  "$id": "schema/execution_request.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutionRequest v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "request_id",
    "project_id",
    "phase_id",
    "task_kind",
    "origin",
    "classification",
    "files_scope",
    "constraints",
    "prompt_spec",
    "routing",
    "telemetry"
  ],
  "properties": {
    "request_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "project_id": { "type": "string", "minLength": 1 },
    "phase_id": { "type": "string", "minLength": 1 },
    "workstream_id": {
      "type": ["string", "null"]
    },
    "task_kind": {
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
    "origin": {
      "type": "object",
      "additionalProperties": false,
      "required": ["source_app", "created_by", "created_at"],
      "properties": {
        "source_app": { "type": "string", "minLength": 1 },
        "created_by": { "type": "string", "minLength": 1 },
        "created_at": { "type": "string", "format": "date-time" }
      }
    },
    "classification": {
      "type": "object",
      "additionalProperties": false,
      "required": ["complexity", "risk_tier", "domain", "priority"],
      "properties": {
        "complexity": {
          "type": "string",
          "enum": ["low", "medium", "high"]
        },
        "risk_tier": {
          "type": "string",
          "enum": ["R1", "R2", "R3"]
        },
        "domain": { "type": "string", "minLength": 1 },
        "priority": {
          "type": "string",
          "enum": ["low", "normal", "high", "urgent"]
        }
      }
    },
    "files_scope": {
      "type": "object",
      "additionalProperties": false,
      "required": ["read", "write", "create", "forbidden"],
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
        "tests_must_pass": { "type": "boolean", "default": true },
        "patch_only": { "type": "boolean", "default": true },
        "ascii_only": { "type": "boolean", "default": true },
        "max_lines_changed": { "type": "integer", "minimum": 1 },
        "max_files_changed": { "type": "integer", "minimum": 1 }
      }
    },
    "prompt_spec": {
      "type": "object",
      "additionalProperties": false,
      "required": ["template_id", "kind"],
      "properties": {
        "template_id": { "type": "string", "minLength": 1 },
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
        "prompt_instance_id": {
          "type": ["string", "null"]
        }
      }
    },
    "routing": {
      "type": "object",
      "additionalProperties": false,
      "required": ["strategy", "allowed_tools", "max_attempts", "timeout_seconds"],
      "properties": {
        "strategy": {
          "type": "string",
          "enum": ["auto", "manual", "fixed"]
        },
        "preferred_tools": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        },
        "allowed_tools": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true,
          "minItems": 1
        },
        "max_attempts": {
          "type": "integer",
          "minimum": 1
        },
        "timeout_seconds": {
          "type": "integer",
          "minimum": 10
        }
      }
    },
    "telemetry": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "correlation_id": { "type": "string", "minLength": 1 },
        "trace_flags": {
          "type": "array",
          "items": { "type": "string", "minLength": 1 },
          "uniqueItems": true
        }
      }
    }
  }
}
```

---

## 3. How `ExecutionRequest` plugs into `PHASE_SPEC_MASTER`

This is the piece you explicitly asked about.

Assume you have:

* `phase_spec.schema.json` (defined by `PHASE_SPEC_MASTER`)
* Concrete phase docs like `PH-ERR-01.yaml` that conform to it, with fields:

  * `phase_id`
  * `files_scope` (allowed read/write/create patterns)
  * `constraints` (tests, patch policy, max lines/files changed)
  * `allowed_tools` / `disallowed_tools`
  * `output_spec_contract` (what outputs are allowed)

**TASK_ROUTING_SPEC must define invariants:**

For any `ExecutionRequest ER`:

1. **Phase existence**

   * The router **must** load the phase spec for `ER.phase_id`.
   * If not found or invalid → reject request (`phase_not_found` / `phase_spec_invalid`).

2. **Scope containment**

   * `ER.files_scope.read` ⊆ `Phase.files_scope.read`
   * `ER.files_scope.write` ⊆ `Phase.files_scope.write`
   * `ER.files_scope.create` ⊆ `Phase.files_scope.create`
   * `ER.files_scope.forbidden` ⊇ `Phase.files_scope.forbidden` (never *less* strict)

   If any field violates containment → reject request (`files_scope_violation`).

3. **Constraint tightening only**

   * Where both phase and ER define the same constraint, ER may be **equal or stricter**, never looser. Examples:

     * `ER.constraints.tests_must_pass` must be true if phase requires tests.
     * `ER.constraints.max_lines_changed` ≤ `Phase.constraints.max_lines_changed` (if phase sets a maximum).
   * If ER tries to *relax* a phase constraint → reject (`constraint_weakened`).

4. **Tool set compatibility**

   * `ER.routing.allowed_tools` ⊆ `Phase.allowed_tools`
   * `ER.routing.allowed_tools` ∩ `Phase.disallowed_tools` = ∅

   If a disallowed tool appears → reject (`tool_not_permitted_for_phase`).

5. **Prompt linkage**

   * `ER.prompt_spec.kind` must be compatible with:

     * `ER.task_kind`
     * `Phase.allowed_prompt_kinds` (if present)

These rules are what “plug” routing into `FILES_SCOPE`, `CONSTRAINTS`, and `OUTPUT_SPEC` from the phase spec.

---

## 4. Core object #2 – `RouterConfig` (`config/router.config.yaml`)

This is the static configuration the router uses to decide **where** an `ExecutionRequest` goes.

### 4.1 Conceptual YAML shape

```yaml
version: "1.0.0"

apps:
  aider:
    kind: "tool"
    command: "aider"
    args: []
    capabilities:
      task_kinds: ["code_edit", "refactor", "code_review"]
      domains: ["general", "python", "mql4"]
    limits:
      max_parallel: 2
      timeout_seconds: 1200
    safety_tier: "high"

  codex_cli:
    kind: "tool"
    command: "codex"
    args: []
    capabilities:
      task_kinds: ["code_edit", "analysis", "planning"]
      domains: ["general", "python"]
    limits:
      max_parallel: 1
      timeout_seconds: 900
    safety_tier: "high"

routing:
  rules:
    - id: "route_code_edit_default"
      description: "Route normal risk code edits to Aider."
      match:
        task_kind: ["code_edit"]
        complexity: ["low", "medium"]
        risk_tier: ["R1", "R2"]
      select_from: ["aider"]
      strategy: "round_robin"
      fallback_to: ["codex_cli"]

    - id: "route_high_risk"
      description: "High risk tasks go to Claude/Codex only."
      match:
        risk_tier: ["R3"]
      select_from: ["codex_cli"]
      strategy: "fixed"
      fallback_to: []

defaults:
  max_attempts: 3
  timeout_seconds: 900
  strategy: "auto"

guard_rules:
  reject_if:
    - id: "no_allowed_tools"
      condition: "len(ExecutionRequest.routing.allowed_tools) == 0"
      error_code: "no_allowed_tools"
    - id: "phase_missing"
      condition: "PhaseSpec is null"
      error_code: "phase_not_found"
```

### 4.2 `RouterConfig` JSON Schema (top-level)

You don’t have to implement every detail now, but at minimum:

* `apps` – map of app IDs → capabilities/limits.
* `routing.rules` – list of match/strategy/fallback definitions.
* `defaults` – fallback routing behavior.
* `guard_rules` – list of conditions (you’ll implement as Python, not pure JSON logic).

---

## 5. Validation & flow behavior (what TASK_ROUTING_SPEC *requires* the orchestrator to do)

For each incoming `ExecutionRequest`:

1. **Schema validation**

   * Validate against `execution_request.schema.json`.
   * If invalid → `request_invalid_schema`, log & drop.

2. **Phase resolution & validation**

   * Load phase spec `PHASE_SPEC_INSTANCE` for `ER.phase_id`.
   * Validate against `phase_spec.schema.json` (owned by `PHASE_SPEC_MASTER`).
   * If invalid or missing → `phase_spec_invalid` / `phase_not_found`.

3. **Phase–Request compatibility checks**

   * Enforce scope containment and constraint-tightening rules from §3.
   * Enforce allowed/disallowed tools.
   * If any violation → reject with precise error code.

4. **Routing decision**

   * Evaluate `RouterConfig.routing.rules` in order.
   * First rule whose `match` predicates all hold for this ER + classification wins.
   * From that rule:

     * Pick `select_from` candidates according to `strategy` (round_robin, random, fixed, etc.).
     * Filter by `ER.routing.allowed_tools` ∩ `Phase.allowed_tools`.
   * If no viable tool remains → `no_routable_tool_for_phase`.

5. **Prompt binding**

   * Using `ER.prompt_spec`:

     * Ensure `template_id` & `kind` are valid against `PROMPT_RENDERING_SPEC`.
     * Build a `PromptInstance` object.
     * Validate it with `prompt_instance.v1.json`.
   * If invalid → `prompt_spec_invalid`.

6. **Execution handoff**

   * Create a work item for the chosen app:

     * `tool_id`
     * `ExecutionRequest`
     * `PromptInstance`
   * Enqueue into `.tasks/inbox` (or equivalent) for that tool worker.

7. **Error routing / retries**

   * If the tool fails:

     * Depending on `ER.routing.strategy` and `RouterConfig`, either:

       * Retry same tool (up to `max_attempts`).
       * Fallback to next tool in `fallback_to`.
       * Emit `final_failure` and pass into the error pipeline phases (PH-ERR-XX) you described earlier.

All of these steps belong in `TASK_ROUTING_SPEC` as behavioral rules, not just data.

---

## 6. Integration summary: `TASK_ROUTING_SPEC` + `PHASE_SPEC_MASTER` + `PROMPT_RENDERING_SPEC`

To make the relationships explicit:

* **`PHASE_SPEC_MASTER`**

  * Owns `phase_spec.schema.json`.
  * Defines:

    * Allowed FILES_SCOPE per phase.
    * Baseline CONSTRAINTS (tests, patch policy, etc.).
    * Allowed tools and prompt kinds.
  * `TASK_ROUTING_SPEC` *must* consult this before routing.

* **`TASK_ROUTING_SPEC`**

  * Owns:

    * `execution_request.schema.json`
    * `router.config.yaml` schema
  * Enforces:

    * **Phase-compatible** scopes and constraints.
    * **Tool-compatible** routing.
    * Deterministic, rule-driven routing behavior.

* **`PROMPT_RENDERING_SPEC`**

  * Owns:

    * `prompt_instance.v1.json`
    * Section definitions (OBJECTIVE, FILES_SCOPE, etc.).
  * `TASK_ROUTING_SPEC` uses `prompt_spec` fields from `ExecutionRequest` to:

    * Construct a `PromptInstance`.
    * Ensure it’s valid before handing to the tool.

So yes: `TASK_ROUTING_SPEC` absolutely **plugs into a PHASE_SPEC_MASTER schema**, and what we’ve done here is formalize the data shapes and invariants that make that plug-in *deterministic and reject-on-violation*.
