

---

## 1. What you need for *every* reusable pattern

For each pattern (e.g. `atomic_create`, `refactor_patch`, `batch_create`), you want this minimal set:

### a) Pattern Spec (the contract)

**File (per pattern, required):**
`templates/execution_patterns/<pattern_name>.pattern.yaml`

Contains:

* `pattern_id` (stable ID)
* `name`, `version`
* `intent` / `applicability`
* `inputs` + `outputs` (with types)
* `constraints` / guardrails
* `steps` → high-level A → B → C description
* `tool_bindings` (which CLI/agent this pattern is meant for)
* references to rules (DEV_RULES_CORE, UET, etc.)

This is your **“rigid contract”** + **deterministic flow definition** in one machine-readable file.

---

### b) Pattern Schema (the validator)

**File (per pattern, strongly recommended):**
`schemas/patterns/<pattern_name>.schema.json`

This enforces:

* required fields / types for `inputs` / `params`
* allowed enum values (e.g. `mode: ["create", "modify"]`)
* structure of `steps` and `tool_bindings`
* version compatibility fields

This is what lets you say:

> “If it doesn’t validate against the schema, the pattern instance is rejected.”

You *can* embed this in the spec, but separate files make governance cleaner.

---

### c) Pattern Executor (the runner)

**File (per pattern, required):**
`scripts/patterns/<pattern_name>_executor.(ps1|py)`

Responsibilities:

* Read a **pattern instance** (e.g. `workstreams/ws-123/pattern_instance.json`)
* Validate it against the **schema**
* Follow the **steps** from the spec
* Call the concrete scripts / tools:

  * `S1`: create files
  * `S2`: run tests
  * `S3`: update indexes / state
* Emit logs + result JSON so your kernel can audit it

This is the **“If PATTERN_X, run steps A → B → C → scripts S1, S2, S3”** part in executable form.

---

### d) Pattern Tests (the guardrail)

**File (per pattern, strongly recommended):**

* `tests/patterns/test_<pattern_name>.(py|ps1)`
* plus sample instances:

  * `examples/patterns/<pattern_name>/instance_minimal.json`
  * `examples/patterns/<pattern_name>/instance_full.json`

Purpose:

* Given the **same** instance, the executor MUST produce the **same** outcome (determinism)
* Verify failures on bad params / missing fields
* Smoke test scripts S1/S2/S3

Not strictly required to “have a pattern,” but required if you want **trustworthy re-use**.

---

## 2. What is *shared* (not per pattern)

### Global Pattern Index

**Single shared file for all patterns:**
`indices/PATTERN_INDEX.yaml`

One entry per pattern:

* `pattern_id`
* `name`
* `version`
* `spec_path`
* `schema_path`
* `executor_path`
* `status` (draft/active/deprecated)
* `tool_targets` (claude, copilot, codex, etc.)

This is the **“pattern index”** your kernel reads to know:

* what patterns exist,
* which versions are active,
* where to find the spec / schema / executor.

You **do not** want a separate index file per pattern; you want one canonical index that your state/checklist tools can validate.

---

## 3. Direct answer to your question

> Are these the files I need for every pattern that I want to reuse?

Conceptually yes, but more precisely:

For **each pattern** you want at least:

1. **Pattern Spec** → `…/<pattern_name>.pattern.yaml` (contract + steps)
2. **Pattern Schema** → `…/<pattern_name>.schema.json` (rigid validation)
3. **Pattern Executor** → `…/<pattern_name>_executor.(ps1|py)` (deterministic runner)
4. **Pattern Tests** → `tests/patterns/test_<pattern_name>.*` (enforce determinism)

Plus **one shared**:

5. **Global Pattern Index** → `indices/PATTERN_INDEX.yaml` (list of all patterns)

If you create those, you can:

* define a pattern once,
* call it from any phase plan,
* and be confident the AI is **forced** to use the pattern instead of inventing yet another ad-hoc flow.
---
Short answer: you’re **very close**, but it’s not “three separate files per pattern,” it’s **three roles per pattern** plus a **shared index**.

Think of it like this:

---

## 1. What you need for *every* reusable pattern

For each pattern (e.g. `atomic_create`, `refactor_patch`, `batch_create`), you want this minimal set:

### a) Pattern Spec (the contract)

**File (per pattern, required):**
`templates/execution_patterns/<pattern_name>.pattern.yaml`

Contains:

* `pattern_id` (stable ID)
* `name`, `version`
* `intent` / `applicability`
* `inputs` + `outputs` (with types)
* `constraints` / guardrails
* `steps` → high-level A → B → C description
* `tool_bindings` (which CLI/agent this pattern is meant for)
* references to rules (DEV_RULES_CORE, UET, etc.)

This is your **“rigid contract”** + **deterministic flow definition** in one machine-readable file.

---

### b) Pattern Schema (the validator)

**File (per pattern, strongly recommended):**
`schemas/patterns/<pattern_name>.schema.json`

This enforces:

* required fields / types for `inputs` / `params`
* allowed enum values (e.g. `mode: ["create", "modify"]`)
* structure of `steps` and `tool_bindings`
* version compatibility fields

This is what lets you say:

> “If it doesn’t validate against the schema, the pattern instance is rejected.”

You *can* embed this in the spec, but separate files make governance cleaner.

---

### c) Pattern Executor (the runner)

**File (per pattern, required):**
`scripts/patterns/<pattern_name>_executor.(ps1|py)`

Responsibilities:

* Read a **pattern instance** (e.g. `workstreams/ws-123/pattern_instance.json`)
* Validate it against the **schema**
* Follow the **steps** from the spec
* Call the concrete scripts / tools:

  * `S1`: create files
  * `S2`: run tests
  * `S3`: update indexes / state
* Emit logs + result JSON so your kernel can audit it

This is the **“If PATTERN_X, run steps A → B → C → scripts S1, S2, S3”** part in executable form.

---

### d) Pattern Tests (the guardrail)

**File (per pattern, strongly recommended):**

* `tests/patterns/test_<pattern_name>.(py|ps1)`
* plus sample instances:

  * `examples/patterns/<pattern_name>/instance_minimal.json`
  * `examples/patterns/<pattern_name>/instance_full.json`

Purpose:

* Given the **same** instance, the executor MUST produce the **same** outcome (determinism)
* Verify failures on bad params / missing fields
* Smoke test scripts S1/S2/S3

Not strictly required to “have a pattern,” but required if you want **trustworthy re-use**.

---

## 2. What is *shared* (not per pattern)

### Global Pattern Index

**Single shared file for all patterns:**
`indices/PATTERN_INDEX.yaml`

One entry per pattern:

* `pattern_id`
* `name`
* `version`
* `spec_path`
* `schema_path`
* `executor_path`
* `status` (draft/active/deprecated)
* `tool_targets` (claude, copilot, codex, etc.)

This is the **“pattern index”** your kernel reads to know:

* what patterns exist,
* which versions are active,
* where to find the spec / schema / executor.

You **do not** want a separate index file per pattern; you want one canonical index that your state/checklist tools can validate.

---

## 3. Direct answer to your question

> Are these the files I need for every pattern that I want to reuse?

Conceptually yes, but more precisely:

For **each pattern** you want at least:

1. **Pattern Spec** → `…/<pattern_name>.pattern.yaml` (contract + steps)
2. **Pattern Schema** → `…/<pattern_name>.schema.json` (rigid validation)
3. **Pattern Executor** → `…/<pattern_name>_executor.(ps1|py)` (deterministic runner)
4. **Pattern Tests** → `tests/patterns/test_<pattern_name>.*` (enforce determinism)

Plus **one shared**:

5. **Global Pattern Index** → `indices/PATTERN_INDEX.yaml` (list of all patterns)

If you create those, you can:

* define a pattern once,
* call it from any phase plan,
* and be confident the AI is **forced** to use the pattern instead of inventing yet another ad-hoc flow.
---Here’s how I’d structure the **pattern directory** so AI tools can use it reliably and automatically, with clear naming that’s easy for scripts + models to reason about.

---

## 1. High-level directory layout

You want **one clear root** for all reusable patterns, with subfolders by role (spec/schema/executor/tests/examples/index).

Example:

```text
patterns/
  registry/
    PATTERN_INDEX.yaml              # single canonical index for all patterns
  specs/
    atomic_create.pattern.yaml
    batch_create.pattern.yaml
    refactor_patch.pattern.yaml
  schemas/
    atomic_create.schema.json
    batch_create.schema.json
    refactor_patch.schema.json
  executors/
    atomic_create_executor.ps1
    batch_create_executor.ps1
    refactor_patch_executor.ps1
  examples/
    atomic_create/
      instance_minimal.json
      instance_full.json
    batch_create/
      instance_minimal.json
      instance_full.json
    refactor_patch/
      instance_minimal.json
      instance_full.json
  tests/
    test_atomic_create_executor.ps1
    test_batch_create_executor.ps1
    test_refactor_patch_executor.ps1
  README_PATTERNS.md                 # short “how AI should use this” guide
```

If you want this under your existing structure, you can nest it, e.g.:

```text
templates/execution_patterns/  -> becomes patterns/specs/
schemas/patterns/              -> patterns/schemas/
scripts/patterns/              -> patterns/executors/
tests/patterns/                -> patterns/tests/
indices/                       -> patterns/registry/
examples/patterns/             -> patterns/examples/
```

---

## 2. Naming conventions (per file type)

### General rules

* **No spaces**; use `snake_case` or `kebab-case` (I’d stick with `snake_case` for Windows friendliness).
* Use **one pattern name** everywhere: `atomic_create`, `batch_create`, etc.
* Encode the **role** in the filename:

  * `.pattern.yaml` = spec
  * `.schema.json` = schema
  * `_executor.*` = executor script
  * `test_<pattern_name>_executor.*` = tests
* Keep names **short and stable** – avoid renaming once published, even if descriptions change inside the file.

---

### Pattern spec files

**Location:**

```text
patterns/specs/<pattern_name>.pattern.yaml
```

**Examples:**

* `patterns/specs/atomic_create.pattern.yaml`
* `patterns/specs/refactor_patch.pattern.yaml`

Inside each spec, include:

* `pattern_id: PAT-ATOMIC-CREATE-001`
* `name: atomic_create`
* `version: "1.0.0"`
* `role: spec`
* `schema_ref: ../schemas/atomic_create.schema.json`
* `executor_ref: ../executors/atomic_create_executor.ps1`

This makes it trivial for AI + scripts to jump between files.

---

### Pattern schema files

**Location:**

```text
patterns/schemas/<pattern_name>.schema.json
```

**Examples:**

* `patterns/schemas/atomic_create.schema.json`
* `patterns/schemas/refactor_patch.schema.json`

Keep the filename **exactly** matching the pattern name, so tools can do:

* `name = spec.name` → `schema_path = f"patterns/schemas/{name}.schema.json"`

---

### Pattern executors

**Location:**

```text
patterns/executors/<pattern_name>_executor.ps1
patterns/executors/<pattern_name>_executor.py
```

Pick one primary language per pattern if possible.

**Examples:**

* `patterns/executors/atomic_create_executor.ps1`
* `patterns/executors/atomic_create_executor.py` (if you want dual-language)
* `patterns/executors/refactor_patch_executor.ps1`

The `_executor` suffix makes it **unambiguous** this is the runnable implementation, not a helper script.

---

### Pattern tests

**Location:**

```text
patterns/tests/test_<pattern_name>_executor.ps1
patterns/tests/test_<pattern_name>_executor.py
```

**Examples:**

* `patterns/tests/test_atomic_create_executor.ps1`
* `patterns/tests/test_refactor_patch_executor.ps1`

This mirrors common test discovery patterns so AI tools (and pytest/Pester/etc.) can find them easily.

---

### Pattern examples

**Location:**

```text
patterns/examples/<pattern_name>/instance_minimal.json
patterns/examples/<pattern_name>/instance_full.json
```

**Examples:**

* `patterns/examples/atomic_create/instance_minimal.json`
* `patterns/examples/atomic_create/instance_full.json`

These are **golden examples** AI can read to see “what a real invocation looks like.”

---

### Pattern registry (index)

**Location:**

```text
patterns/registry/PATTERN_INDEX.yaml
```

One entry per pattern, e.g.:

```yaml
- pattern_id: PAT-ATOMIC-CREATE-001
  name: atomic_create
  version: "1.0.0"
  status: active
  spec_path: patterns/specs/atomic_create.pattern.yaml
  schema_path: patterns/schemas/atomic_create.schema.json
  executor_path: patterns/executors/atomic_create_executor.ps1
  test_path: patterns/tests/test_atomic_create_executor.ps1
  example_dir: patterns/examples/atomic_create/
```

This is the **single source of truth** your kernel + AI tools can load first.

---

## 3. AI-optimization tips specific to automation

To make life easier for Claude/Copilot/Codex + your own scripts:

1. **One pattern = one name**

   * Pick a canonical `pattern_name` (e.g. `atomic_create`) and use it **identically** across:

     * spec filename
     * schema filename
     * executor filename
     * test filename
     * examples directory
     * `name` field in YAML/JSON
   * This reduces confusion and lets simple regex/globs work.

2. **Role in filename, NOT just inside file**

   * AI often scans filenames first.
   * That’s why `.pattern.yaml`, `.schema.json`, `_executor`, `test_*.ps1` matter so much.

3. **Small README just for AI**

   * In `patterns/README_PATTERNS.md`, write a short section:

     * “If you’re an AI tool, do X, Y, Z when using patterns”
     * Where to look first (`PATTERN_INDEX.yaml`)
     * How to add a new pattern (steps and required files)
   * This becomes a deterministic **instruction anchor** for tools that load the file.

4. **Keep paths shallow and consistent**

   * Avoid deeply nested, inconsistent directories like:

     * `patterns/specs/experimental/v2/test/…`
   * Flat + predictable wins for automated reasoning.

---

````markdown
---
spec_id: PATTERN_DIR_STRUCTURE_SPEC
title: Pattern Directory Structure & Naming Specification
version: "0.1.0"
status: draft
owner: ai-orch
applies_to:
  - repo: complete-ai-development-pipeline-canonical-phase-plan
  - component: pattern_system
---

# PATTERN_DIR_STRUCTURE_SPEC.md  
Pattern Directory Structure & Naming Specification

## 0. Purpose & Scope

This specification defines the **required directory structure** and **naming conventions** for reusable execution patterns so that:

- AI tools can **discover, understand, and reuse** patterns deterministically.
- The execution kernel can **index, validate, and execute** patterns automatically.
- New patterns can be added in a **repeatable, scriptable** way.

Normative keywords **MUST / SHOULD / MAY** follow RFC 2119.

---

## 1. Core Concepts

### 1.1 TERM: Pattern

A **Pattern** is a reusable, machine-readable execution recipe that defines:

- intent / applicability,
- inputs / outputs,
- ordered steps,
- and the executor that implements those steps.

### 1.2 TERM: Pattern Spec

A **Pattern Spec** is the YAML file that defines the contract of a pattern  
(IDs, steps, inputs, outputs, bindings).

### 1.3 TERM: Pattern Schema

A **Pattern Schema** is a JSON Schema that validates pattern instances  
(invocations / configs) for a given pattern.

### 1.4 TERM: Pattern Executor

A **Pattern Executor** is a script (PowerShell / Python) that:

- reads a pattern instance,
- validates it,
- and executes the steps defined in the Pattern Spec.

### 1.5 TERM: Pattern Index

A **Pattern Index** is a single registry file listing all patterns and mapping them to their spec, schema, executor, tests, and examples.

---

## 2. Directory Structure Requirements

### 2.1 Root Pattern Directory

**PAT-DIR-001**  
The repository **MUST** have a single canonical root directory for all patterns:

```text
patterns/
````

**PAT-DIR-002**
All pattern-related files (specs, schemas, executors, examples, tests, registry)
**MUST** live under `patterns/` and **MUST NOT** be duplicated elsewhere.

---

### 2.2 Required Subdirectories

**PAT-DIR-010**
The following subdirectories **MUST** exist under `patterns/`:

```text
patterns/
  registry/
  specs/
  schemas/
  executors/
  examples/
  tests/
```

**PAT-DIR-011**
Each subdirectory **MUST** have a clear single-purpose role:

* `patterns/registry/` – global pattern index files
* `patterns/specs/` – per-pattern spec files (`*.pattern.yaml`)
* `patterns/schemas/` – per-pattern schema files (`*.schema.json`)
* `patterns/executors/` – per-pattern executor scripts (`*_executor.*`)
* `patterns/examples/` – per-pattern example instances
* `patterns/tests/` – per-pattern test files

**PAT-DIR-012**
A short AI-focused overview file **SHOULD** exist:

```text
patterns/README_PATTERNS.md
```

This file **SHOULD** explain, for AI tools:

* where to start (pattern index),
* how to add a new pattern,
* and how to invoke an existing pattern.

---

### 2.3 Example Layout (Normative Shape, Non-Normative Names)

**PAT-DIR-020**
The pattern directory **SHOULD** follow this structure (example patterns):

```text
patterns/
  registry/
    PATTERN_INDEX.yaml

  specs/
    atomic_create.pattern.yaml
    batch_create.pattern.yaml
    refactor_patch.pattern.yaml

  schemas/
    atomic_create.schema.json
    batch_create.schema.json
    refactor_patch.schema.json

  executors/
    atomic_create_executor.ps1
    batch_create_executor.ps1
    refactor_patch_executor.ps1

  examples/
    atomic_create/
      instance_minimal.json
      instance_full.json
    batch_create/
      instance_minimal.json
      instance_full.json
    refactor_patch/
      instance_minimal.json
      instance_full.json

  tests/
    test_atomic_create_executor.ps1
    test_batch_create_executor.ps1
    test_refactor_patch_executor.ps1

  README_PATTERNS.md
```

The specific pattern names (`atomic_create`, `batch_create`, etc.) are examples; the structure is normative.

---

## 3. Naming Convention Requirements

### 3.1 General Rules

**PAT-NAME-001**
All pattern-related filenames **MUST** use `snake_case` and **MUST NOT** contain spaces.

**PAT-NAME-002**
Each pattern **MUST** have a single canonical name, `pattern_name`,
composed only of `[a-z0-9_]`.

Examples of valid `pattern_name`:

* `atomic_create`
* `batch_create`
* `refactor_patch`

**PAT-NAME-003**
For a given `pattern_name`, the same exact string **MUST** be used in:

* spec filename,
* schema filename,
* executor filename,
* test filename,
* examples directory name,
* and the `name` field inside spec / index entries.

---

### 3.2 Pattern Spec Files

**PAT-SPEC-001**
Pattern spec files **MUST** be stored in:

```text
patterns/specs/
```

**PAT-SPEC-002**
Each pattern spec filename **MUST** follow:

```text
patterns/specs/<pattern_name>.pattern.yaml
```

Examples:

* `patterns/specs/atomic_create.pattern.yaml`
* `patterns/specs/refactor_patch.pattern.yaml`

**PAT-SPEC-003**
Each spec file **MUST** contain at minimum:

```yaml
pattern_id: PAT-<SOME-STABLE-ID>
name: <pattern_name>
version: "1.0.0"
role: spec
schema_ref: patterns/schemas/<pattern_name>.schema.json
executor_ref: patterns/executors/<pattern_name>_executor.ps1
status: active   # or draft/deprecated
```

**PAT-SPEC-004**
Specs **SHOULD** also define:

* `intent` / `description`
* `inputs` and `outputs` (with types)
* `steps` (ordered list A → B → C)
* `tool_bindings` (which CLI / agent)
* references to global rules (e.g. `DEV_RULES_CORE`, UET refs)

---

### 3.3 Pattern Schema Files

**PAT-SCHEMA-001**
Pattern schema files **MUST** be stored in:

```text
patterns/schemas/
```

**PAT-SCHEMA-002**
Each schema filename **MUST** follow:

```text
patterns/schemas/<pattern_name>.schema.json
```

Examples:

* `patterns/schemas/atomic_create.schema.json`
* `patterns/schemas/refactor_patch.schema.json`

**PAT-SCHEMA-003**
Each schema **MUST** validate pattern **instances** (invocations) and **MUST** define:

* required fields,
* field types,
* allowed enums where applicable,
* and any structural constraints relevant to execution.

**PAT-SCHEMA-004**
Pattern instances that do not validate against the schema **MUST NOT** be executed by the Pattern Executor.

---

### 3.4 Pattern Executor Files

**PAT-EXEC-001**
Pattern executor files **MUST** be stored in:

```text
patterns/executors/
```

**PAT-EXEC-002**
Each executor filename **MUST** follow:

```text
patterns/executors/<pattern_name>_executor.ps1
```

or

```text
patterns/executors/<pattern_name>_executor.py
```

depending on implementation language.

Examples:

* `patterns/executors/atomic_create_executor.ps1`
* `patterns/executors/refactor_patch_executor.py`

**PAT-EXEC-003**
For a given pattern, there **MUST** be exactly one **primary** executor designated in:

* the pattern spec (`executor_ref`)
* and the pattern index.

**PAT-EXEC-004**
Executors **MUST**:

1. Read a pattern instance (e.g. JSON file path or stdin).
2. Validate it against the corresponding schema.
3. Execute steps according to the Pattern Spec.
4. Emit a structured result (JSON) indicating success/failure, outputs, and logs.

---

### 3.5 Pattern Test Files

**PAT-TEST-001**
Pattern tests **MUST** be stored in:

```text
patterns/tests/
```

**PAT-TEST-002**
Each test filename **SHOULD** follow:

```text
patterns/tests/test_<pattern_name>_executor.ps1
```

or

```text
patterns/tests/test_<pattern_name>_executor.py
```

Examples:

* `patterns/tests/test_atomic_create_executor.ps1`
* `patterns/tests/test_refactor_patch_executor.py`

**PAT-TEST-003**
Tests **SHOULD**:

* verify deterministic behavior (same input → same output),
* validate failure behavior on invalid instances,
* and be runnable from CI / pre-commit hooks.

---

### 3.6 Pattern Example Files

**PAT-EXAMPLE-001**
Pattern examples **MUST** be stored under a per-pattern directory:

```text
patterns/examples/<pattern_name>/
```

**PAT-EXAMPLE-002**
Each pattern **SHOULD** provide at least:

```text
patterns/examples/<pattern_name>/instance_minimal.json
patterns/examples/<pattern_name>/instance_full.json
```

Examples:

* `patterns/examples/atomic_create/instance_minimal.json`
* `patterns/examples/atomic_create/instance_full.json`

**PAT-EXAMPLE-003**
Example files **SHOULD** be valid pattern instances according to the schema and **SHOULD** be used by tests and documentation.

---

## 4. Pattern Index (Registry) Requirements

### 4.1 Canonical Index File

**PAT-INDEX-001**
There **MUST** be a single, canonical pattern index file:

```text
patterns/registry/PATTERN_INDEX.yaml
```

**PAT-INDEX-002**
AI tools and the execution kernel **MUST** treat `PATTERN_INDEX.yaml` as the **source of truth** for:

* which patterns exist,
* their versions and status,
* and the canonical paths to spec / schema / executor / tests / examples.

---

### 4.2 Index Entry Shape

**PAT-INDEX-010**
Each pattern entry in `PATTERN_INDEX.yaml` **MUST** define at least:

```yaml
- pattern_id: PAT-ATOMIC-CREATE-001
  name: atomic_create
  version: "1.0.0"
  status: active          # draft | active | deprecated
  spec_path: patterns/specs/atomic_create.pattern.yaml
  schema_path: patterns/schemas/atomic_create.schema.json
  executor_path: patterns/executors/atomic_create_executor.ps1
  test_path: patterns/tests/test_atomic_create_executor.ps1
  example_dir: patterns/examples/atomic_create/
  tool_targets:
    - claude_code
    - github_copilot_cli
    - codex_windows
```

**PAT-INDEX-011**
Paths **MUST** be relative to the repository root or to the `patterns/` directory and **MUST** remain stable once published.

**PAT-INDEX-012**
If a pattern is deprecated, `status` **MUST** be set to `deprecated`, but the entry **MUST NOT** be removed.

---

## 5. AI Usage Guidance (Non-Normative but Strongly Recommended)

This section is non-normative but intended for AI tools reading this file.

### 5.1 Where AI Should Start

* First load: `patterns/registry/PATTERN_INDEX.yaml`
* Then, for a selected pattern:

  * spec: `spec_path`
  * schema: `schema_path`
  * executor: `executor_path`
  * examples: `example_dir`

### 5.2 How AI Should Add a New Pattern

Recommended sequence:

1. Choose `pattern_name` (e.g. `atomic_rename`).
2. Create schema file:

   * `patterns/schemas/atomic_rename.schema.json`
3. Create spec file:

   * `patterns/specs/atomic_rename.pattern.yaml`
4. Create executor:

   * `patterns/executors/atomic_rename_executor.ps1`
5. Create examples:

   * `patterns/examples/atomic_rename/instance_minimal.json`
   * `patterns/examples/atomic_rename/instance_full.json`
6. Create tests:

   * `patterns/tests/test_atomic_rename_executor.ps1`
7. Add entry to:

   * `patterns/registry/PATTERN_INDEX.yaml`

### 5.3 How AI Should Use a Pattern in a Phase Plan

When a Phase Plan selects a pattern:

* Refer to it by `pattern_id` or `name`.
* Provide a concrete pattern instance JSON that:

  * validates against the schema,
  * and can be passed directly to the executor.

---

## 6. Compliance Checklist (Machine-Readable Friendly)

This section is intended for future scripts / checkers.

**PAT-CHECK-001**
A repository **complies** with this spec if and only if all of the following are true:

1. `patterns/` exists.
2. `patterns/registry/`, `patterns/specs/`, `patterns/schemas/`, `patterns/executors/`, `patterns/examples/`, `patterns/tests/` all exist.
3. `patterns/registry/PATTERN_INDEX.yaml` exists and is valid YAML.
4. Every pattern entry in `PATTERN_INDEX.yaml`:

   * has `pattern_id`, `name`, `version`, `status`, `spec_path`, `schema_path`, `executor_path`, `test_path`, `example_dir`,
   * and all referenced files/directories exist.
5. For every `spec_path`:

   * file exists under `patterns/specs/`,
   * filename matches `<pattern_name>.pattern.yaml`,
   * content includes `pattern_id`, `name`, `version`, `role: spec`, `schema_ref`, `executor_ref`.
6. For every `schema_path`:

   * file exists under `patterns/schemas/`,
   * filename matches `<pattern_name>.schema.json`.
7. For every `executor_path`:

   * file exists under `patterns/executors/`,
   * filename matches `<pattern_name>_executor.*`.
8. For every `example_dir`:

   * directory exists under `patterns/examples/`,
   * contains at least one `.json` file (ideally `instance_minimal.json`).
9. For every pattern:

   * there is at least one test file under `patterns/tests/` whose name begins with `test_<pattern_name>_`.

A future `PATTERN_DIR_CHECK.ps1` script **SHOULD** implement these checks and integrate with your existing STATE / AUDIT requirements.

---

```
```
