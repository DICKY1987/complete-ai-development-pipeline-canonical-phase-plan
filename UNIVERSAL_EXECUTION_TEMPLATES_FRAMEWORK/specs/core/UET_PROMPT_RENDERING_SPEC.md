Nice, this is the fun one.

I’ll treat **PROMPT_RENDERING_SPEC** as a *core spec* that does two things:

1. Defines a **universal prompt object** (JSON) that every prompt must conform to before it’s rendered.
2. Defines how that object is **rendered to text** for tools like Aider / Codex / Claude.

No narrative doc, just structure + semantics.

---

## 1. Positioning PROMPT_RENDERING_SPEC in your stack

* `doc_type`: `core_spec`
* `doc_layer`: `framework`
* Body of the doc: a machine-readable definition that includes:

  * A **Prompt Instance schema** (what a valid prompt looks like).
  * A set of **Prompt Kinds** (`code_edit`, `analysis`, `plan`, etc.) with required sections.
  * A set of **Prompt Sections** (OBJECTIVE, CONTEXT, CONSTRAINTS, FILE_SCOPE, OUTPUT_SPEC, etc.).
  * **Rendering rules** (how to turn that JSON into the final text).
  * **Tool adapters** (small variations per CLI tool, still from same core).

Think of it as: “The Bible for how to talk to any agent.”

---

## 2. Canonical Prompt Instance – core JSON shape

This is the object your orchestrator builds and validates **before** rendering text.

### 2.1 Top-level fields (Prompt Instance)

```json
{
  "prompt_id": "01J2Z8X9ABCDEF1234567890AB",
  "template_id": "TEMPLATE_WORKSTREAM_V1_1",
  "kind": "code_edit",
  "target_tool": "aider",
  "workstream_id": "WS-ERR-01",
  "phase_id": "PH-ERR-01",
  "project_id": "PRJ-HUEY_P",
  "origin": {
    "source_app": "orchestrator",
    "requested_by": "SYSTEM:ERROR_PIPELINE",
    "created_at": "2025-11-20T09:45:00Z"
  },
  "classification": {
    "complexity": "medium",
    "risk_tier": "R2",
    "domain": "file_management",
    "priority": "normal"
  },
  "sections": {
    "HEADER": "...",
    "ROLE": "...",
    "OBJECTIVE": "...",
    "CONTEXT": "...",
    "FILES_SCOPE": "...",
    "CONSTRAINTS": "...",
    "OUTPUT_SPEC": "...",
    "VALIDATION_RULES": "...",
    "ERROR_HANDLING": "...",
    "REASONING_STYLE": "...",
    "TOOL_NOTES": "..."
  },
  "rendering_profile": {
    "profile_id": "PROFILE_CANONICAL_V1",
    "line_endings": "LF",
    "encoding": "utf-8",
    "ascii_only": true
  }
}
```

### 2.2 JSON Schema for `PromptInstance`

Call this `schema/prompt_instance.v1.json`.

High level (not every property fully spelled, just enough to formalize):

```json
{
  "$id": "schema/prompt_instance.v1.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Prompt Instance v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "prompt_id",
    "template_id",
    "kind",
    "target_tool",
    "origin",
    "classification",
    "sections",
    "rendering_profile"
  ],
  "properties": {
    "prompt_id": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "template_id": {
      "type": "string",
      "minLength": 1
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
        "question_answering",
        "other"
      ]
    },
    "target_tool": {
      "type": "string",
      "minLength": 1
    },
    "workstream_id": {
      "type": ["string", "null"]
    },
    "phase_id": {
      "type": ["string", "null"]
    },
    "project_id": {
      "type": ["string", "null"]
    },
    "origin": {
      "type": "object",
      "additionalProperties": false,
      "required": ["source_app", "requested_by", "created_at"],
      "properties": {
        "source_app": { "type": "string", "minLength": 1 },
        "requested_by": { "type": "string", "minLength": 1 },
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
        "domain": {
          "type": "string",
          "minLength": 1
        },
        "priority": {
          "type": "string",
          "enum": ["low", "normal", "high", "urgent"]
        }
      }
    },
    "sections": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "HEADER": { "type": "string" },
        "ROLE": { "type": "string" },
        "OBJECTIVE": { "type": "string" },
        "CONTEXT": { "type": "string" },
        "FILES_SCOPE": { "type": "string" },
        "CONSTRAINTS": { "type": "string" },
        "OUTPUT_SPEC": { "type": "string" },
        "VALIDATION_RULES": { "type": "string" },
        "ERROR_HANDLING": { "type": "string" },
        "REASONING_STYLE": { "type": "string" },
        "TOOL_NOTES": { "type": "string" }
      }
    },
    "rendering_profile": {
      "type": "object",
      "additionalProperties": false,
      "required": ["profile_id"],
      "properties": {
        "profile_id": { "type": "string", "minLength": 1 },
        "line_endings": {
          "type": "string",
          "enum": ["LF", "CRLF"]
        },
        "encoding": {
          "type": "string",
          "enum": ["utf-8"]
        },
        "ascii_only": {
          "type": "boolean"
        }
      }
    }
  }
}
```

> Behavior: your orchestrator **must** validate this JSON against the schema *and* against the rules in PROMPT_RENDERING_SPEC before rendering/sending anything.

---

## 3. Canonical Sections (IDs + meaning)

PROMPT_RENDERING_SPEC should define each section as a stable object with:

* `section_id` – stable ID used in `sections` map.
* `title` – human-facing title in the rendered prompt.
* `required_for_kinds` – which `kind`s require this section to be non-empty.
* `max_chars` / `max_lines` – optional soft limits.
* `content_guidance` – short description for agents (not human prose).

### 3.1 Section definitions (conceptual)

Suggested list:

1. **HEADER**

   * Purpose: carry workstream/phase info and single-line “what this is”.
   * Example content: `WORKSTREAM WS-ERR-01 → Repair error pipeline patch application for file X`.

2. **ROLE**

   * Purpose: persona + expertise (Anthropic-style).
   * Example: `You are a senior software developer specialized in agentic pipelines and patch-based workflows.`

3. **OBJECTIVE**

   * Purpose: precise task definition; close to “Goal” / “Task”.
   * Example: `Your task is to refactor the error pipeline module to ensure all error flows end in quarantine or GitHub save.`

4. **CONTEXT**

   * Purpose: relevant background (project, architecture, constraints summary).
   * Includes: references to other docs, short explanation of state.

5. **FILES_SCOPE**

   * Purpose: precise file-level constraints.
   * Example: explicit list of allowed paths, allowed operations (read/write/append).

6. **CONSTRAINTS**

   * Purpose: DO/DON’T rules: tests-first, patch-only, no hallucinated success, ASCII only, etc.

7. **OUTPUT_SPEC**

   * Purpose: exact output format (patch vs code block vs JSON), example skeleton, naming rules.

8. **VALIDATION_RULES**

   * Purpose: how the tool should self-check its answer (e.g., run tests, re-open diff, verify invariants).

9. **ERROR_HANDLING**

   * Purpose: what to do on uncertainty or tool errors (e.g., emit structured error, ask for missing info, do not guess).

10. **REASONING_STYLE**

    * Purpose: 3C / thinking-style knobs (short chain-of-thought, step labels, etc.).

11. **TOOL_NOTES**

    * Purpose: small tool-specific quirks (Aider vs Codex vs Claude), but still from the same canonical skeleton.

In PROMPT_RENDERING_SPEC, these are declared as structured entries, for example (conceptually):

```yaml
sections:
  - section_id: "HEADER"
    title: "HEADER"
    required_for_kinds: ["code_edit", "refactor", "analysis", "planning", "documentation"]
    max_lines: 5
    content_guidance: "Single-line summary with workstream and phase IDs."

  - section_id: "ROLE"
    title: "ROLE"
    required_for_kinds: ["code_edit", "analysis", "planning", "refactor"]
    max_lines: 3
    content_guidance: "Persona + expertise; must mention responsibilities, not fluff."

  # etc...
```

(We’re not drafting the actual file; this is the *shape*.)

---

## 4. Prompt Kinds – mapping kinds → required sections

PROMPT_RENDERING_SPEC should have a table like:

```yaml
prompt_kinds:
  - kind: "code_edit"
    description: "Make concrete code changes via patches."
    required_sections:
      - "HEADER"
      - "ROLE"
      - "OBJECTIVE"
      - "CONTEXT"
      - "FILES_SCOPE"
      - "CONSTRAINTS"
      - "OUTPUT_SPEC"
    optional_sections:
      - "VALIDATION_RULES"
      - "ERROR_HANDLING"
      - "REASONING_STYLE"
      - "TOOL_NOTES"

  - kind: "analysis"
    description: "Explain, assess, or reason about code or docs without editing."
    required_sections:
      - "HEADER"
      - "ROLE"
      - "OBJECTIVE"
      - "CONTEXT"
      - "CONSTRAINTS"
      - "OUTPUT_SPEC"
    optional_sections:
      - "REASONING_STYLE"
      - "ERROR_HANDLING"
      - "TOOL_NOTES"

  # etc...
```

**Execution rule** (important):

> The orchestrator **must** refuse to execute a prompt instance if `kind` is K and any `required_sections` for K are empty or missing.

This is the “auto-reject missing elements” behavior you wanted.

---

## 5. Rendering Rules – from JSON to text

PROMPT_RENDERING_SPEC also defines **how** to render a `PromptInstance` into the plain-text prompt string.

Minimal fields needed here:

```yaml
rendering:
  profile_id: "PROFILE_CANONICAL_V1"
  header_prefix: "==== "
  header_suffix: " ===="
  section_header_format: "## {section_id}"
  section_order:
    - "HEADER"
    - "ROLE"
    - "OBJECTIVE"
    - "CONTEXT"
    - "FILES_SCOPE"
    - "CONSTRAINTS"
    - "OUTPUT_SPEC"
    - "VALIDATION_RULES"
    - "ERROR_HANDLING"
    - "REASONING_STYLE"
    - "TOOL_NOTES"
  section_separator: "\n\n"
  line_endings: "LF"
  encoding: "utf-8"
  ascii_only: true
```

Your renderer then:

1. Orders sections according to `section_order`.
2. For each section S that is present and non-empty:

   * Writes `## {section_id}` (or `title` if you prefer) on its own line.
   * Writes the `sections[S]` content below it.
3. Joins sections with `section_separator`.

This means:

* The **text prompt** is a deterministic function of the JSON object.
* Every section heading is **line-stable**, great for patches.
* You can change rendering by switching `profile_id` while keeping the same `PromptInstance` structure.

---

## 6. Tool Adapters (Aider / Codex / Claude / …)

Under `tool_adapters`, PROMPT_RENDERING_SPEC can define small per-tool tweaks, still from the same canonical sections.

Conceptual shape:

````yaml
tool_adapters:
  aider:
    inherit_profile: "PROFILE_CANONICAL_V1"
    prepend_instructions: "Aider-specific note about diffs and file paths."
    section_overrides:
      OUTPUT_SPEC:
        extra_lines:
          - "Return only unified diffs in ```diff``` blocks."
  codex:
    inherit_profile: "PROFILE_CANONICAL_V1"
    section_overrides:
      OUTPUT_SPEC:
        extra_lines:
          - "Return a single JSON object with a 'patch' field containing unified diff text."
  claude:
    inherit_profile: "PROFILE_CANONICAL_V1"
    section_overrides: {}
````

Rules:

* **No tool ever changes the list of required sections**; they only tweak phrasing/format in OUTPUT_SPEC or TOOL_NOTES.
* The orchestrator chooses `target_tool` and uses the adapter to render.

---

## 7. Validation Behavior (how PROMPT_RENDERING_SPEC is enforced)

For each prompt generation step, your orchestrator should:

1. Build the `PromptInstance` JSON.
2. Validate against `prompt_instance.v1.json`.
3. Look up PROMPT_RENDERING_SPEC for:

   * the `kind` (`prompt_kinds` entry),
   * the `sections` definitions,
   * the `tool_adapters` entry for `target_tool`.
4. Check:

   * All `required_sections` are present and non-empty.
   * ASCII-only if required.
   * `FILES_SCOPE` obeys your global rules (no wildcards, no unknown dirs).
5. If **any** check fails:

   * Do **not** render or send.
   * Emit a structured error (e.g., `prompt_invalid_missing_section`, `prompt_invalid_scope_violation`).
6. Only after passing validation:

   * Render text according to `rendering` + `tool_adapters`.
   * Send to the CLI tool.

That’s the formal behavior that makes prompts deterministic, machine-checkable, and rejectable when incomplete.

---

If you like this structure, the next planning move could be:

* Define a similar **PHASE_SPEC_MASTER** schema that plugs into `FILES_SCOPE`, `CONSTRAINTS`, `OUTPUT_SPEC` etc., so phase docs and prompts are tightly coupled.
