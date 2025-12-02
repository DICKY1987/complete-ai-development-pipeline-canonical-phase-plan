# PATTERN_DOC_SUITE_SPEC

**Pattern Documentation Suite & `doc_id` Usage**

* **Spec ID:** PATTERN_DOC_SUITE_SPEC-V1
* **Status:** DRAFT (but internally self-contained and normative)
* **Applies to:** All patterns under `patterns/`
* **Depends on:** PAT-CHECK-001-v2 (validation spec) 

This document is the **authoritative and complete** description of:

* What files make up a **pattern doc suite**
* How to **create** each file
* How to **assign, store, and use** `doc_id` as the **canonical join key** across all artifacts 

If an AI tool knows only this spec, it has enough information to **create, upgrade, and validate** pattern documentation with no additional context.

---

## 0. Scope & Normative Keywords

* This spec defines **how to author** and **organize** documentation and code for patterns in the `patterns/` tree.
* Normative keywords **MUST**, **SHOULD**, **MAY** are as defined in RFC 2119.
* This spec **re-states all required `doc_id` rules**; no external ID spec is required.

---

## 1. Conceptual Model

### 1.1 What is a “pattern doc suite”?

For a single logical pattern (e.g., “Save file with DOC_LINK and audit”), the **pattern doc suite** is the **set of all artifacts** that together define, validate, and implement that pattern.

For one pattern, the doc suite includes:

1. **Index entry** in `patterns/registry/PATTERN_INDEX.yaml`
2. **Spec file** in `patterns/specs/`
3. **Schema file** in `patterns/schemas/` (+ optional sidecar)
4. **Executor file** in `patterns/executors/`
5. **Test files** in `patterns/tests/`
6. **Example instances** in `patterns/examples/` (+ optional sidecars)
7. **Narrative docs** (Markdown/txt) with front matter (where applicable)

All of these artifacts are tied together by a **single `doc_id`**, which is the primary join key across them. 

### 1.2 Relationship between `doc_id`, `pattern_id`, and `version`

* **`doc_id`**

  * Identifies the **entire doc suite** for one logical pattern.
  * Stable across small edits and non-breaking changes.
  * Primary key for cross-artifact joins and automation. 

* **`pattern_id`**

  * Human-facing, domain-specific label (e.g., `PAT-SAVE-FILE-001`).
  * May remain stable even if implementations change.
  * **MUST NOT** be used as the primary cross-artifact join key.

* **`version`**

  * Describes the **version of the pattern spec** (e.g., `1.0.0`).
  * Bump when behavior changes but the pattern is still conceptually “the same pattern”.

**Rule:**
`doc_id` + `version` describe “which conceptual pattern” and “which version of its spec,” while `pattern_id` is the human label.

---

## 2. `doc_id` – Definition & Rules

### 2.1 Purpose

`doc_id` is a **repository-wide, stable identifier** for a **logical documentation unit**: everything that belongs to one pattern’s doc suite. It is:

* Used in **indexes**, **specs**, **schemas**, **executors**, **tests**, **examples**, and **docs**.
* The **only key** automation uses to say “these files belong to the same pattern.” 

### 2.2 Format

For pattern doc suites, `doc_id` **MUST**:

* Be **ASCII uppercase letters, digits, and dashes only**.
* Match this regex:

```text
^DOC-PAT-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$
```

Examples of **valid** `doc_id` values:

* `DOC-PAT-SAVE-FILE-001`
* `DOC-PAT-CREATE-FILE-LOGGING-001`
* `DOC-PAT-RUN-TESTS-CORE-002`

Structure:

1. `DOC` – literal prefix
2. `PAT` – literal for “pattern doc suite”
3. `<NAME_SEGMENTS>` – 1+ dash-separated uppercase alphanumeric segments describing the pattern
4. `<NNN>` – 3-digit numeric suffix for uniqueness

This is compatible with the more generic “uppercase with dashes” pattern enforced by PAT-CHECK-001. 

### 2.3 Minting new `doc_id` values

When creating a **new pattern**:

1. Take a concise name for the pattern, e.g. `save_file`.
2. Convert to uppercase segments with dashes, e.g. `SAVE-FILE`.
3. Look for existing `doc_id`s in `PATTERN_INDEX.yaml` with the same `DOC-PAT-SAVE-FILE-XXX` prefix.
4. Choose the **next free numeric suffix**, zero-padded to 3 digits:

   * If none exist → `DOC-PAT-SAVE-FILE-001`
   * If `DOC-PAT-SAVE-FILE-001` exists → next is `DOC-PAT-SAVE-FILE-002`
5. Use this `doc_id` consistently in **all artifacts** for the pattern.

### 2.4 When to **keep** vs **change** `doc_id`

* **Keep the same `doc_id`** when:

  * Fixing bugs in executor/tests.
  * Clarifying documentation.
  * Adding non-breaking parameters or optional features.

* **Mint a new `doc_id`** when:

  * The pattern’s behavior changes in a way that is **not backward compatible**, or
  * The pattern is fundamentally repurposed (e.g., old SAVE-FILE becomes a totally different workflow).

If `doc_id` changes:

* The old doc suite remains a historical unit.
* The new doc suite uses a **new** `doc_id` and typically a **new `pattern_id`** as well.

### 2.5 Cross-artifact consistency rule

For a given pattern entry in `PATTERN_INDEX.yaml`, the following artifacts **MUST** all share the **same** `doc_id`: 

* Index entry
* Spec file
* Schema (or its sidecar)
* Executor file
* All test files for that pattern
* All example JSONs (or their sidecars)
* All narrative docs in the suite

Automation **MUST** treat `doc_id` as the **canonical join key** across these. 

---

## 3. Required Files in a Pattern Doc Suite

This section describes, for each artifact:

* **Where** it lives
* **What** it must contain
* **How** to create it (step-by-step)
* **How** `doc_id` appears in it

We will use a running example pattern:

* `pattern_id`: `PAT-SAVE-FILE-001`
* `doc_id`: `DOC-PAT-SAVE-FILE-001`
* `pattern_name`: `save_file`

---

### 3.1 Pattern Index Entry (`PATTERN_INDEX.yaml`)

**Location & role**

* File: `patterns/registry/PATTERN_INDEX.yaml` 
* Contains a list under `patterns:` where each entry describes **one pattern doc suite**.

**MUST fields per entry** 

Each pattern entry **MUST** contain at least:

* `doc_id`
* `pattern_id`
* `name`
* `version`
* `status` (e.g., `draft`, `stable`, `deprecated`)
* `spec_path`
* `schema_path`
* `executor_path`
* `test_path`
* `example_dir`
* `operation_kinds` (list of operation kind names implemented) 

**Example entry**

```yaml
# patterns/registry/PATTERN_INDEX.yaml
patterns:
  - doc_id: DOC-PAT-SAVE-FILE-001
    pattern_id: PAT-SAVE-FILE-001
    name: save_file
    version: 1.0.0
    status: stable
    spec_path: patterns/specs/save_file.pattern.yaml
    schema_path: patterns/schemas/save_file.schema.json
    executor_path: patterns/executors/save_file_executor.ps1
    test_path: patterns/tests/test_save_file_main.ps1
    example_dir: patterns/examples/save_file/
    operation_kinds:
      - SAVE_FILE
```

**How to create a new index entry (AI procedure)**

1. Generate a `doc_id` as per §2.3.
2. Generate a `pattern_id` (e.g., `PAT-SAVE-FILE-001`).
3. Choose a `name` (lowercase snake or similar, e.g. `save_file`) – **SHOULD** match filenames.
4. Set `version` to `1.0.0` for new patterns.
5. Set `status` to `draft` or `stable` as appropriate.
6. Fill paths with **repository-relative** paths under the correct directories.
7. Add `operation_kinds` using names from `OPERATION_KIND_REGISTRY.yaml` (e.g., `SAVE_FILE`). 
8. Append the entry to the `patterns:` list.

---

### 3.2 Pattern Spec File (`patterns/specs/<pattern_name>.pattern.yaml`)

**Location & naming**

* Directory: `patterns/specs/`
* Filename **MUST** match: `<pattern_name>.pattern.yaml` 

  * Example: `patterns/specs/save_file.pattern.yaml`

**Required top-level fields** 

Each spec file **MUST** include:

* `doc_id`
* `pattern_id`
* `name`
* `version`
* `role: spec`
* `schema_ref` – typically same as `schema_path`
* `executor_ref` – same as `executor_path`
* `example_dir` – same as in index
* `operation_kinds` – list of operation kinds implemented
* Any additional pattern-specific fields (`description`, `parameters`, `steps`, etc.)

**Example spec**

```yaml
# patterns/specs/save_file.pattern.yaml
doc_id: DOC-PAT-SAVE-FILE-001
pattern_id: PAT-SAVE-FILE-001
name: save_file
version: 1.0.0
role: spec

operation_kinds:
  - SAVE_FILE

schema_ref: patterns/schemas/save_file.schema.json
executor_ref: patterns/executors/save_file_executor.ps1
example_dir: patterns/examples/save_file/

summary: "Write content to a file with required DOC_LINK and audit metadata."
parameters:
  required:
    - path
  optional:
    - content
    - encoding
    - mode
behavioral_contract:
  - "File writes MUST ensure a valid DOC_LINK header if applicable."
  - "On error, executor MUST return a machine-readable error object."
```

**How to create a new spec file (AI procedure)**

1. Use the `doc_id`, `pattern_id`, `name`, `version` from the index entry.
2. Set `role: spec`.
3. Set `schema_ref`, `executor_ref`, and `example_dir` to match the index paths.
4. Copy the `operation_kinds` list from `PATTERN_INDEX.yaml`.
5. Fill in `summary`, `parameters`, and `behavioral_contract` with clear, machine-parseable rules.

---

### 3.3 Schema File (`patterns/schemas/<pattern_name>.schema.json`)

**Location & naming**

* Directory: `patterns/schemas/`
* Filename **MUST** match: `<pattern_name>.schema.json` 

**doc_id embedding or sidecar** 

For each schema:

* **Preferred (SHOULD):** Embed `"doc_id"` at top level in the JSON.
* **Alternative (MUST if not embedded):** Provide a sidecar `.id.yaml` (see §4) that maps schema path → `doc_id`.

**Example schema (embedded `doc_id`)**

```json
{
  "doc_id": "DOC-PAT-SAVE-FILE-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "save_file pattern parameters",
  "type": "object",
  "properties": {
    "path": { "type": "string" },
    "content": { "type": "string" },
    "encoding": { "type": "string" },
    "mode": { "type": "string", "enum": ["overwrite", "append"] }
  },
  "required": ["path"]
}
```

**How to create a new schema file**

1. Start from a JSON Schema draft (e.g., 07).
2. Insert `"doc_id": "<DOC_ID>"` at the top level.
3. Define `properties` and `required` to match what the spec expects.
4. Save as `patterns/schemas/<pattern_name>.schema.json`.

If you cannot embed `doc_id` (legacy constraints), **also**:

1. Create sidecar: `patterns/schemas/<pattern_name>.schema.id.yaml` as in §4.

---

### 3.4 Schema Sidecar (optional but sometimes required)

**Location & naming** 

* Recommended: `patterns/schemas/<pattern_name>.schema.id.yaml`

**Required structure**

```yaml
schema_path: patterns/schemas/save_file.schema.json
doc_id: DOC-PAT-SAVE-FILE-001
role: schema_metadata
```

Sidecars **MUST**:

* Include `schema_path`.
* Include `doc_id`.
* Use the same `doc_id` as the index entry and spec.

---

### 3.5 Executor File (`patterns/executors/<pattern_name>_executor.*`)

**Location & naming** 

* Directory: `patterns/executors/`
* Filename **MUST** match: `<pattern_name>_executor.*`

  * Example: `patterns/executors/save_file_executor.ps1`

**DOC_LINK header with `doc_id`** 

Each executor file **MUST**:

* Include a `DOC_LINK` header as the first non-shebang, non-empty line.
* Contain the `doc_id` of the pattern.

Examples:

PowerShell:

```powershell
# DOC_LINK: DOC-PAT-SAVE-FILE-001
param(
    [string]$Path,
    [string]$Content,
    [string]$Encoding = "utf-8",
    [string]$Mode = "overwrite"
)

# ...implementation...
```

Python:

```python
# DOC_LINK: DOC-PAT-SAVE-FILE-001
import json
import sys
# ...implementation...
```

**How to create a new executor file**

1. Choose appropriate language and extension.
2. Name file `<pattern_name>_executor.<ext>`.
3. Add `DOC_LINK: <DOC_ID>` header at the top using language-appropriate comment syntax.
4. Implement behavior consistent with the spec and schema.

Executors **SHOULD NOT** hard-code absolute paths; automation should resolve paths via `doc_id` and index entries. 

---

### 3.6 Test Files (`patterns/tests/`)

**Location & naming** 

* Directory: `patterns/tests/`
* File(s) **MUST** be named starting with: `test_<pattern_name>_`

  * Example: `patterns/tests/test_save_file_main.ps1`
  * Multiple tests allowed; all belong to the same `doc_id` if they test that pattern.

**DOC_LINK header** 

Each test file **MUST**:

* Include a `DOC_LINK` header with the `doc_id`, just like executors.

Example (PowerShell):

```powershell
# DOC_LINK: DOC-PAT-SAVE-FILE-001
# Tests for save_file pattern

# ...Pester or other test code...
```

**How to create test files**

1. Name file `test_<pattern_name>_main.<ext>`.
2. Add `DOC_LINK: <DOC_ID>` header.
3. Implement tests that:

   * Validate executor behavior against the schema and spec.
   * Use repository-relative paths.

---

### 3.7 Examples (`patterns/examples/<pattern_name>/`)

**Location & structure** 

* Directory: `patterns/examples/<pattern_name>/`

  * Example: `patterns/examples/save_file/`
* Directory **MUST** contain at least one `.json` file.

  * Recommended name: `instance_minimal.json`

**doc_id placement** 

Each example **SHOULD**:

* Embed `doc_id` at top level **OR**
* Be listed in a sidecar index mapping example path → `doc_id`.

**Example JSON with embedded `doc_id`**

```json
{
  "doc_id": "DOC-PAT-SAVE-FILE-001",
  "path": "output/example.txt",
  "content": "Hello, world!",
  "mode": "overwrite"
}
```

**Example sidecar index (if not embedding)**

```yaml
# patterns/examples/save_file/examples.id.yaml
examples:
  - path: patterns/examples/save_file/instance_minimal.json
    doc_id: DOC-PAT-SAVE-FILE-001
  - path: patterns/examples/save_file/instance_append.json
    doc_id: DOC-PAT-SAVE-FILE-001
```

**How to create examples**

1. Create directory `patterns/examples/<pattern_name>/` if it does not exist.
2. Create at least one JSON file showing a valid parameter set for the schema.
3. Either:

   * Add `"doc_id": "<DOC_ID>"` at top level in each JSON, or
   * Create an `examples.id.yaml` sidecar referencing each example with `doc_id`.

---

### 3.8 Narrative Docs (Markdown/TXT with front matter)

These are human-readable docs (e.g., long-form explanations) that are still **machine-linked** via `doc_id`.

**Location**

* Recommended: `docs/patterns/<pattern_name>.md` or within a module folder that owns the pattern.

**Front matter with `doc_id`**

Each narrative doc **MUST** start with YAML front matter including `doc_id`:

```markdown
---
doc_id: DOC-PAT-SAVE-FILE-001
pattern_id: PAT-SAVE-FILE-001
role: pattern_narrative
title: Save File Pattern – Overview and Usage
---

# Save File Pattern

This document describes...
```

This allows tooling to locate narrative docs by `doc_id` even if paths move.

---

## 4. Sidecar & Index Metadata Formats

Sidecars are used when a file cannot easily store `doc_id` internally (or when a central index is preferred).

### 4.1 Schema sidecar (`*.schema.id.yaml`)

```yaml
schema_path: patterns/schemas/save_file.schema.json
doc_id: DOC-PAT-SAVE-FILE-001
role: schema_metadata
```

### 4.2 Example sidecar (`examples.id.yaml`)

```yaml
examples:
  - path: patterns/examples/save_file/instance_minimal.json
    doc_id: DOC-PAT-SAVE-FILE-001
  - path: patterns/examples/save_file/instance_append.json
    doc_id: DOC-PAT-SAVE-FILE-001
```

**Rules (all sidecars)**

* **MUST** contain `doc_id`.
* **MUST** reference the correct file path(s).
* **MUST** use the same `doc_id` as index, spec, executor, tests.

---

## 5. Creating a New Pattern Doc Suite (End-to-End AI Procedure)

This section gives a **complete, ordered recipe** for an AI to create a new pattern doc suite from scratch.

Assume:

* Pattern name: `save_file`
* Operation kind: `SAVE_FILE`

### Step 1 – Mint identifiers

1. Read `patterns/registry/PATTERN_INDEX.yaml` and collect existing `doc_id`s and `pattern_id`s.
2. Generate `doc_id`:

   * Prefix: `DOC-PAT-SAVE-FILE-`
   * Pick the next free numeric suffix, zero-padded (e.g., `001`).
   * Final: `DOC-PAT-SAVE-FILE-001`
3. Generate `pattern_id`:

   * Start with `PAT-SAVE-FILE-001`.
   * Ensure uniqueness in the index.

### Step 2 – Create or update PATTERN_INDEX.yaml

Add a new entry:

```yaml
- doc_id: DOC-PAT-SAVE-FILE-001
  pattern_id: PAT-SAVE-FILE-001
  name: save_file
  version: 1.0.0
  status: draft
  spec_path: patterns/specs/save_file.pattern.yaml
  schema_path: patterns/schemas/save_file.schema.json
  executor_path: patterns/executors/save_file_executor.ps1
  test_path: patterns/tests/test_save_file_main.ps1
  example_dir: patterns/examples/save_file/
  operation_kinds:
    - SAVE_FILE
```

### Step 3 – Create spec file

Create `patterns/specs/save_file.pattern.yaml` as in §3.2, using the same `doc_id`, `pattern_id`, and paths.

### Step 4 – Create schema

1. Create `patterns/schemas/save_file.schema.json` with:

   * `"doc_id": "DOC-PAT-SAVE-FILE-001"` at top level.
   * Properties for all allowed parameters.
2. Optionally generate sidecar `.schema.id.yaml` if you want both.

### Step 5 – Create executor

1. Create `patterns/executors/save_file_executor.ps1`.
2. Add `# DOC_LINK: DOC-PAT-SAVE-FILE-001` as the first non-empty line.
3. Implement logic to:

   * Parse input (path, content, etc.).
   * Write file according to spec.
   * Respect any audit/logging rules.

### Step 6 – Create tests

1. Create `patterns/tests/test_save_file_main.ps1`.
2. Add `# DOC_LINK: DOC-PAT-SAVE-FILE-001`.
3. Write tests that:

   * Call the executor with valid and invalid input.
   * Assert correct behavior (file created, errors handled, etc.).

### Step 7 – Create examples

1. Create directory `patterns/examples/save_file/`.
2. Create `instance_minimal.json` with `"doc_id": "DOC-PAT-SAVE-FILE-001"` and minimal valid parameters.
3. Optionally create more examples.
4. If you choose not to embed `doc_id` in each JSON, create an `examples.id.yaml` sidecar.

### Step 8 – Create narrative doc (optional but recommended)

Create `docs/patterns/save_file.md` (or a module-local doc) with front matter containing the same `doc_id`.

### Step 9 – Sanity check `doc_id` consistency

Before finishing:

1. Confirm the same `doc_id` is present in:

   * `PATTERN_INDEX.yaml` entry
   * Spec file
   * Schema (or its sidecar)
   * Executor DOC_LINK
   * Test DOC_LINK
   * Examples (or their sidecar)
   * Narrative docs (front matter)
2. Confirm that all the paths in the index entry exist.

---

## 6. Migrating Existing Patterns Without `doc_id`

For an existing repository where patterns exist but `doc_id` is missing, AI **MUST** follow this migration process per pattern:

### Step 1 – Extract current pattern metadata

For each pattern entry in `PATTERN_INDEX.yaml`:

* Read `pattern_id`, `name`, and all paths.

### Step 2 – Mint a `doc_id`

1. Normalize `name` (e.g., `save_file` → `SAVE-FILE`).
2. Generate `doc_id` using `DOC-PAT-<NAME>-NNN` scheme.
3. Ensure no collision with existing `doc_id`s.

### Step 3 – Update PATTERN_INDEX.yaml

* Add `doc_id` field to the pattern entry.
* Do **not** change existing paths unless they are invalid.

### Step 4 – Update spec file

1. Open `spec_path`.
2. If `doc_id` field is missing:

   * Insert `doc_id: <DOC_ID>` at the top of the YAML.
3. Ensure `pattern_id`, `name`, `schema_ref`, `executor_ref`, `example_dir`, and `operation_kinds` are consistent.

### Step 5 – Update executor(s)

1. Open `executor_path`.
2. If no `DOC_LINK` header is present:

   * Insert `DOC_LINK: <DOC_ID>` as the first non-shebang, non-empty line using comment syntax.
3. If a different `DOC_LINK` value exists:

   * Overwrite with `<DOC_ID>` and note in commit message.

### Step 6 – Update test files

1. Find all files in `patterns/tests/` that start with `test_<pattern_name>_`. 
2. Insert or update `DOC_LINK` header to use the new `doc_id`.

### Step 7 – Update schemas

1. Open `schema_path`.
2. If JSON contains `"doc_id"`, update value to `<DOC_ID>` (if needed).
3. If it does **not** contain `"doc_id"`:

   * Either add `"doc_id": "<DOC_ID>"` at top level, **or**
   * Create a `.schema.id.yaml` sidecar with the appropriate structure.

### Step 8 – Update examples

1. For each JSON under `example_dir`:

   * Add `"doc_id": "<DOC_ID>"` if allowed, **or**
   * Create/update `examples.id.yaml` to map each example to `<DOC_ID>`.

### Step 9 – Update narrative docs

1. For any known narrative docs for this pattern:

   * Add or update YAML front matter with `doc_id: <DOC_ID>`.

### Step 10 – Verify consistency

Run or emulate PAT-CHECK-001 checks for:

* `doc_id` presence in index/spec/executors/tests/schemas/examples. 
* `doc_id` consistency across all artifacts.
* Valid `doc_id` format.

---

## 7. Validation Expectations (for future tooling)

A future `PATTERN_DIR_CHECK` script (PowerShell or similar) **SHOULD** validate at least: 

1. **Directory layout**

   * All required `patterns/` subdirectories exist (`registry/`, `specs/`, `schemas/`, `executors/`, `examples/`, `tests/`).

2. **PATTERN_INDEX.yaml**

   * Exists and is valid YAML.
   * Each entry has all required fields including `doc_id`.
   * `doc_id` matches required regex.
   * Paths exist and point to correct directories.

3. **Spec files**

   * One spec per pattern entry.
   * Spec’s `doc_id` matches index `doc_id`.

4. **Executors & tests**

   * One executor per pattern entry.
   * Executor files and test files contain `DOC_LINK: <DOC_ID>` headers matching the index.

5. **Schemas & examples**

   * Each `schema_path` exists, with either embedded `doc_id` or a sidecar.
   * Each example JSON in `example_dir` embeds `doc_id` or is listed in an example sidecar.
   * All associated `doc_id`s match the index entry.

6. **Cross-artifact join**

   * For each entry in `PATTERN_INDEX.yaml`, all related artifacts resolve to **the same** `doc_id` and no artifact is linked to multiple `doc_id`s.

---

## 8. Summary

* A **pattern doc suite** is the **complete cluster** of artifacts for one pattern.
* `doc_id` is the **single, stable join key** that ties all those artifacts together.
* Every pattern’s artifacts (index, spec, schema, executor, tests, examples, docs) **MUST** use the same `doc_id`.
* This spec defines **exact formats**, **locations**, and **step-by-step creation/migration procedures** so that an AI can author and maintain pattern doc suites with **no additional references**.
