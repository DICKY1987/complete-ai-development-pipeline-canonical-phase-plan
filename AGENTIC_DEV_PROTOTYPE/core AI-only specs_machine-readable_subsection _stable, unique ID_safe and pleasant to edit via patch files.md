core AI-only specs_machine-readable_subsection a **stable, unique ID_safe and pleasant to edit via patch files

* Make them **strictly machine-readable**
* Give every section/subsection a **stable, unique ID**
* Make them **safe and pleasant to edit via patch files**

I’ll lay out a concrete plan, not just vibes.

---

## 1. Clarify the target state

For all three docs:

1. **AI-first, machine-readable**

   * No “pretty prose” formatting that makes parsing harder.
   * Consistent markers and delimiters so an AI or script can:

     * Extract sections
     * Find rules
     * Check required fields.

2. **Stable, unique identifiers**

   * Every section, subsection, and rule has a durable ID.
   * IDs are reusable across tools (phase planner, orchestrator, validators, etc.).

3. **Patch-friendly**

   * Minimal reflow (don’t wrap at 80 columns and change all lines).
   * Stable ordering and indentation.
   * Clear boundaries so a patch can target one section or rule without collateral damage.

---

## 2. Decide on a common “Spec-Doc v1” format

Use **one canonical structure** for all three files so the orchestrator and AI agents don’t need custom logic per doc.

### 2.1 File-level structure

Each doc:

1. **YAML front-matter (single block at top)**
2. **Plain-text body in “block+marker” format**

Example front-matter:

```yaml
doc_key: UNIVERSAL_PHASE_SPEC
doc_semver: 1.3.0
doc_role: phase_lifecycle_definition
doc_audience: agentic_ai_only
id_prefix: UPS
status: active
```

For PRO_Phase:

```yaml
doc_key: PRO_PHASE_SPEC
id_prefix: PPS
```

For RULES:

```yaml
doc_key: DEV_RULES
id_prefix: DR
```

Front-matter is:

* Easy to parse (YAML)
* Patch-friendly (small, rarely-changed block at top).

### 2.2 Section + subsection marker format

Define a **simple ASCII marker** for sections that never changes:

```text
== SEC UPS-001
TITLE: Phase Definition Overview
LEVEL: 1
PARENT: ROOT
TAGS: definition,overview
== BODY
... text ...
== ENDSEC
```

Subsection example:

```text
== SEC UPS-001-A
TITLE: Phase Identity Fields
LEVEL: 2
PARENT: UPS-001
TAGS: fields,identity
== BODY
... text ...
== ENDSEC
```

Key properties:

* `== SEC` and `== ENDSEC` are easy anchors.
* `UPS-001`, `PPS-010-B`, `DR-DO-007` are **stable IDs** you can reference from other docs, prompts, tests, tools.
* You can patch **one section** by patching from `== SEC ...` to `== ENDSEC` with minimal spillover.

---

## 3. ID scheme for the three docs

### 3.1 UNIVERSAL PHASE SPEC (UPS-* IDs)

* Prefix: `UPS`
* Top-level sections: `UPS-001`, `UPS-002`, ...
* Subsections: `UPS-001-A`, `UPS-001-B` etc.
* Optional deeper nesting: `UPS-001-A-1` (only if needed).

Examples:

* `UPS-001` – “What is a Phase?”
* `UPS-002` – “Phase Lifecycle Overview”
* `UPS-003` – “Phase Required Fields”
* `UPS-004` – “Pre-Flight Checks”
* `UPS-005` – “Execution Loop”
* `UPS-006` – “Completion & Acceptance”

These map directly to how you already think about phases.

### 3.2 PRO_Phase mandatory structure (PPS-* IDs)

* Prefix: `PPS`
* Each **structural requirement** gets its own section ID.
* Each **field** can get a sub-ID if you want fine-grained automation.

Examples:

* `PPS-001` – “Phase Spec Metadata Block (YAML frontmatter)”
* `PPS-002` – “Required Top-Level Fields”
* `PPS-002-A` – “Field: phase_id”
* `PPS-002-B` – “Field: workstream_id”
* `PPS-003` – “file_scope Structure”
* `PPS-004` – “Acceptance Tests Section”
* `PPS-005` – “Anti-Patterns / FORBIDDEN Patterns”

Your validator and AI prompts can say things like:

> “Reject this phase: missing PPS-003 (file_scope section).”

### 3.3 DEVELOPMENT RULES DO & DONT (DR-* IDs)

This one really benefits from **rule-level IDs**.

* Prefix: `DR`
* Group by category and polarity.

Example:

```text
== RULE DR-DO-001
TYPE: DO
CATEGORY: EXECUTION_DISCIPLINE
SEVERITY: HIGH
TEXT:
Always treat CLI output as primary ground truth for success/failure.
== ENDRULE

== RULE DR-DONT-007
TYPE: DONT
CATEGORY: HALLUCINATION
SEVERITY: CRITICAL
TEXT:
Do not claim success for a change that has not been validated via tests or analysis tools.
== ENDRULE
```

You can still wrap these in `== SEC` blocks if you want, but **RULE** blocks let tools:

* Search “all CRITICAL rules”
* Attach rule IDs to telemetry & violations
* Reference them in prompts:

  > “Follow DR-DONT-007 and DR-DONT-009 when proposing a fix.”

---

## 4. Patch-friendly formatting rules

To keep these spec-docs easy to edit via patch files:

1. **One logical thing per block**

   * Each `SEC` or `RULE` is an atomic unit.
   * Avoid mixing multiple concepts in one block.

2. **Avoid reflowing text**

   * Use natural line breaks by sentence or bullet, not auto-wrap to a width.
   * That way, editing one sentence only changes that line in the diff.

3. **Stable ordering**

   * Don’t re-order sections unless absolutely necessary.
   * If you must insert something, use ID spaces:

     * e.g. leave gaps: UPS-010, UPS-020, UPS-030 so you can insert UPS-015 later.

4. **No hidden formatting**

   * No tabs vs spaces chaos.
   * No trailing whitespace.
   * One blank line between blocks.

5. **Patch policy**

   * For AI tools: require **patches only inside block boundaries**:

     * Not allowed: patch that starts in one section and ends in another.
     * Allowed: patch entirely inside `== BODY` / `== TEXT:` segment.

---

## 5. A concrete migration plan (phase/workstream style)

Here’s a simple **multi-phase plan** to transform the three docs into this format.

### Phase 1 – Inventory & Section Map (manual + AI)

**Goal:** Know what’s there, before rewriting.

* Extract the current headings and major subsections from:

  * UNIVERSAL PHASE SPEC
  * PRO_Phase Spec
  * DEVELOPMENT RULES
* Build a simple **Section Map** file (YAML or JSON) with:

  * `id_candidate`
  * `proposed_title`
  * `doc_key`
  * `parent`
  * `tags`

This can be an AI-assisted job:
“Read this doc and propose a section map for UPS IDs.”

### Phase 2 – Finalize ID schemes

**Goal:** Lock in identifiers before massive editing.

* Assign:

  * `UPS-*` IDs to all phase spec sections.
  * `PPS-*` IDs to all PRO_Phase sections.
  * `DR-*` IDs to each rule (DO/DONT).
* Store ID scheme in a small registry:

  * `spec_index.yaml` with all doc/section/rule IDs as a source of truth.

### Phase 3 – Rewrite into Spec-Doc v1 format

**Goal:** Convert content into the `== SEC/RULE` format.

For each doc:

1. Add YAML front-matter.
2. Wrap each section into:

```text
== SEC <ID>
TITLE: ...
LEVEL: ...
PARENT: ...
TAGS: ...
== BODY
...existing content, cleaned up...
== ENDSEC
```

3. For the DEV RULES doc, additionally wrap each DO/DONT into `RULE` blocks.

This is a perfect use case for AI with patch files:

* You can give the AI a `SEC` skeleton and ask it to move content into the new structure in small increments.

### Phase 4 – Build a tiny validator script

**Goal:** Let machines (and AI) check their own work.

Write a simple Python/PowerShell validator that:

* Parses front-matter.
* Reads each `== SEC` and `== RULE` block.
* Checks:

  * IDs are present and match `id_prefix`.
  * Titles are non-empty.
  * No duplicate IDs.
  * Every `RULE` has TYPE, CATEGORY, SEVERITY, TEXT.
* Outputs a JSON or table report:

  * Missing fields
  * Unknown sections
  * Orphaned rules.

Once this exists, you can tell all AI tools in your prompts:

> “After editing, run `validate_specs.ps1` and fix any errors in the report.”

### Phase 5 – Wire it into the patch workflow

**Goal:** Make changes safe and atomic.

* Update your **Patch Files sub-spec** to say:

  * For these three docs, **only allow** patches that:

    * Modify existing `SEC`/`RULE` blocks, or
    * Add new blocks at well-defined insertion points.
* Update AI prompts for code/spec editing:

  * Explicitly tell them:

    * “Identify the target `SEC`/`RULE` ID.”
    * “Generate a unified diff that only touches that block.”
    * “Do not re-order blocks or reflow existing text.”

### Phase 6 – Add cross-references

Once everything is stable, add **machine-readable references** between them:

* In UPS sections:

  * `REFS: PPS-003, DR-DONT-007`
* In PPS:

  * `REFS: UPS-003, DR-DO-002`
* In DR rules:

  * `APPLIES_TO: UPS-*, PPS-*`

This lets AI agents and scripts answer questions like:

* “Show all rules that apply to `file_scope` behavior.”
* “Which rules apply to phase acceptance tests?”

---

## 6. How AI will use this in practice

After this plan:

* AI can:

  * Parse the doc quickly by scanning `== SEC` / `== RULE`.
  * Search by ID: “Explain UPS-003 only.”
  * Validate: “Before executing a phase, ensure the spec includes all mandatory PPS-* sections.”
  * Patch: “Update the text of DR-DONT-007, but nothing else.”

Your orchestrator can:

* Enforce “no missing PPS-* sections.”
* Log rule violations with IDs (e.g. `violated_rules: ["DR-DONT-007"]`).
* Use IDs in prompts to keep instructions short and precise.

---
