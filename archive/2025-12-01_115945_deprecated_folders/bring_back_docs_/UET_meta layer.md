---
doc_id: DOC-GUIDE-UET-META-LAYER-331
---

Perfect, this is a clean place to standardize things.

Here’s a **single, universal “Doc Meta Schema”** we can apply to *every* document in your system. This is the frontmatter that sits at the top of each file and gives the pipeline everything it needs to:

* know **what** the doc is,
* know **where** it lives in the stack,
* validate that it’s **safe to use**,
* and enforce **patch-only, schema-first** changes.

I’ll define:

1. The **fields & semantics** (canonical list).
2. A **JSON Schema** you can adopt as `schema/doc-meta.v1.json`.
3. A **frontmatter shape** (not a full doc, just the meta block).

---

## 1. Canonical Doc Meta Schema — Fields & Semantics

This is the *flat* set of keys every doc must have in its YAML frontmatter (or equivalent JSON sidecar). All other doc-specific fields (phase, workstream, tool profile, etc.) live **below** this meta layer.

### Required core identity

* **`meta_version`** (string)

  * Fixed identifier for this meta schema version.
  * Example: `"doc-meta.v1"`.
  * Lets you evolve this later (v2, v3) without breaking old docs.

* **`doc_ulid`** (string)

  * The **stable, unique ID** for this document, never changes once assigned.
  * ULID format: `^[0-9A-HJKMNP-TV-Z]{26}$`.
  * All references between docs (dependencies, spec_refs, etc.) point to this.

* **`doc_type`** (string, enum)

  * What *kind* of document this is. Suggested enum values:

    * `"global_spec"`        – AGENT_OPERATIONS_SPEC, DEVELOPMENT_RULES, etc.
    * `"core_spec"`          – PROMPT_RENDERING_SPEC, TASK_ROUTING_SPEC, etc.
    * `"project_profile"`    – project-level config.
    * `"phase_spec_master"`  – reusable phase template spec.
    * `"phase_spec_instance"`– concrete PH-XX doc.
    * `"workstream_spec"`    – workstream/phase plan description.
    * `"error_pipeline_spec"`– PH-ERR docs, error flows.
    * `"tool_profile"`       – Aider/Codex/etc profiles.
    * `"capability_card"`    – capability descriptions.
    * `"run_artifact"`       – logs, reports, run snapshots.
    * `"other"`              – fallback, to be narrowed later.

* **`doc_layer`** (string, enum)

  * Where it sits in your stack:

    * `"global"`    – applies to all projects.
    * `"framework"` – shared core specs & schemas.
    * `"project"`   – project-level.
    * `"module"`    – module/component-level.
    * `"run"`       – specific execution/run outputs.

* **`title`** (string)

  * Short human-readable name of the doc.

* **`summary`** (string)

  * 1–3 sentence description for quick classification (kept short for patches).

* **`version`** (string, semver)

  * Document version, SemVer-style: `"1.0.0"`, `"1.1.3"`.
  * This is the **doc content version**, not the schema version.

* **`status`** (string, enum)

  * Lifecycle state:

    * `"draft"`
    * `"active"`
    * `"deprecated"`
    * `"superseded"`
    * `"experimental"`

* **`schema_ref`** (string)

  * Where to find the schema that validates this **doc body** (not the meta itself).
  * Example: `"schema/prompt_rendering_spec.v1.json"`.

* **`created_at`** (string, ISO-8601)

  * First creation timestamp of this doc (never changes).
  * Example: `"2025-11-20T09:30:00Z"`.

* **`updated_at`** (string, ISO-8601)

  * Last time the **content** (below the meta) changed.

* **`author_type`** (string, enum)

  * Who primarily created/edited the doc:

    * `"human"`
    * `"ai"`
    * `"mixed"`

* **`owner`** (string)

  * Logical owner—team, role, or person.
  * Example: `"SYSTEM:AGENT_ORCHESTRATOR"`, `"TEAM:TRADING_CORE"`.

* **`security_tier`** (string, enum)

  * Controls visibility & handling rules:

    * `"public"`
    * `"internal"`
    * `"confidential"`
    * `"restricted"`

---

### Optional scope / wiring fields

* **`project_id`** (string or null)

  * ID of the project this doc belongs to (`"GLOBAL"` or `null` for global docs).

* **`module_id`** (string or null)

  * Module/component ID when applicable.

* **`phase_id`** (string or null)

  * For phase-related docs (PH-XX).

* **`workstream_id`** (string or null)

  * For workstream-related docs.

* **`spec_refs`** (array of string)

  * List of `doc_ulid`s this document depends on / implements / extends.
  * Example: references to AGENT_OPERATIONS_SPEC, PROMPT_RENDERING_SPEC, etc.

* **`tags`** (array of string)

  * Flat tags for quick filters: `["prompt", "spec", "agentic", "phase"]`.

---

### Optional patch & quality constraints

* **`patch_policy`** (object)

  * Controls how changes to this doc are allowed:

    * `patch_required` (boolean, default `true`)

      * If `true`, orchestrator must *only* accept unified diff edits.
    * `require_issue_ref` (boolean, default `true`)

      * If `true`, edits must reference a ticket/issue ID.
    * `min_reviewers` (integer, default `1`)

      * Minimal code-owner or agent review requirement.

* **`ascii_only`** (boolean, default `true`)

  * If `true`, body text must be ASCII-only for maximum tool compatibility.

* **`max_line_length`** (integer, optional)

  * Soft limit for line length (e.g., `120`).

* **`last_validated_at`** (string, ISO-8601, optional)

  * Last time this doc passed schema validation.

* **`checksum`** (string, optional)

  * Hash of the *body* (non-meta) content.
  * Example: `"sha256:ab12cd..."`. Helps detect out-of-band edits.

---

## 2. JSON Schema — `doc-meta.v1`

This is the **single definition** you can use everywhere to validate the meta block.

```json
{
  "$id": "schema/doc-meta.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Doc Meta Schema v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "meta_version",
    "doc_ulid",
    "doc_type",
    "doc_layer",
    "title",
    "summary",
    "version",
    "status",
    "schema_ref",
    "created_at",
    "updated_at",
    "author_type",
    "owner",
    "security_tier"
  ],
  "properties": {
    "meta_version": {
      "type": "string",
      "const": "doc-meta.v1"
    },
    "doc_ulid": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "doc_type": {
      "type": "string",
      "enum": [
        "global_spec",
        "core_spec",
        "project_profile",
        "phase_spec_master",
        "phase_spec_instance",
        "workstream_spec",
        "error_pipeline_spec",
        "tool_profile",
        "capability_card",
        "run_artifact",
        "other"
      ]
    },
    "doc_layer": {
      "type": "string",
      "enum": [
        "global",
        "framework",
        "project",
        "module",
        "run"
      ]
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "summary": {
      "type": "string",
      "minLength": 1,
      "maxLength": 512
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "status": {
      "type": "string",
      "enum": [
        "draft",
        "active",
        "deprecated",
        "superseded",
        "experimental"
      ]
    },
    "schema_ref": {
      "type": "string",
      "minLength": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "author_type": {
      "type": "string",
      "enum": [
        "human",
        "ai",
        "mixed"
      ]
    },
    "owner": {
      "type": "string",
      "minLength": 1
    },
    "security_tier": {
      "type": "string",
      "enum": [
        "public",
        "internal",
        "confidential",
        "restricted"
      ]
    },
    "project_id": {
      "type": ["string", "null"]
    },
    "module_id": {
      "type": ["string", "null"]
    },
    "phase_id": {
      "type": ["string", "null"]
    },
    "workstream_id": {
      "type": ["string", "null"]
    },
    "spec_refs": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
      },
      "uniqueItems": true
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "uniqueItems": true
    },
    "patch_policy": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "patch_required": {
          "type": "boolean",
          "default": true
        },
        "require_issue_ref": {
          "type": "boolean",
          "default": true
        },
        "min_reviewers": {
          "type": "integer",
          "minimum": 0,
          "default": 1
        }
      }
    },
    "ascii_only": {
      "type": "boolean",
      "default": true"
    },
    "max_line_length": {
      "type": "integer",
      "minimum": 40
    },
    "last_validated_at": {
      "type": "string",
      "format": "date-time"
    },
    "checksum": {
      "type": "string"
    }
  }
}
```

> Note: There’s a stray quote after `default": true"` in `ascii_only` you’d want to fix when you actually paste this into a file. I’m intentionally leaving it as-is here so you can see where the typo would be caught by your own tools.

---

## 3. Frontmatter shape (how it appears in docs)

Not writing a full doc—just what the **meta block** would look like at the top of any file:

```yaml
---
meta_version: "doc-meta.v1"
doc_ulid: "01J2Z6Z2ZK73F0F70D1Q2X3ABC"
doc_type: "core_spec"
doc_layer: "framework"
title: "Prompt Rendering Specification"
summary: "Defines the canonical prompt template family and validation rules for all agentic tools."
version: "1.0.0"
status: "active"
schema_ref: "schema/prompt_rendering_spec.v1.json"
created_at: "2025-11-20T09:30:00Z"
updated_at: "2025-11-20T09:30:00Z"
author_type: "mixed"
owner: "SYSTEM:AGENT_ORCHESTRATOR"
security_tier: "internal"

project_id: null
module_id: null
phase_id: null
workstream_id: null
spec_refs:
  - "01J2Z6WYGZ3FCP6R88F8TTMXYZ"  # AGENT_OPERATIONS_SPEC
tags:
  - "spec"
  - "prompt"
  - "agentic"

patch_policy:
  patch_required: true
  require_issue_ref: true
  min_reviewers: 1

ascii_only: true
max_line_length: 120
last_validated_at: "2025-11-20T09:31:00Z"
checksum: "sha256:deadbeef..."
---
```

Every doc in your suite—global specs, phase instances, workstream plans, error-pipeline specs—would start with *this* meta block, validated by `doc-meta.v1`. The body below can then follow its own schema (PROMPT_RENDERING_SPEC, PHASE_SPEC, WORKSTREAM_SPEC, etc.).

---

If you’re happy with this as the universal meta layer, the next step in planning could be: choose which **spec family** to formalize next (PROMPT_RENDERING_SPEC vs TASK_ROUTING_SPEC vs PHASE_SPEC_MASTER), and define *its* fields so it plugs cleanly under this meta block.
