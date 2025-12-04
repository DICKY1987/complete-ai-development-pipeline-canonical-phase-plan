---
doc_id: DOC-REG-LAYER-001
title: Registry Layer Specification
version: 1.0.0
status: draft
role: spec
---

# REGISTRY_LAYER_SPEC v1.0.0
**Scope:** Define how the registry layer ties together:
- Operation kinds
- Patterns
- Routing
- `doc_id`-based pattern doc suites

This spec **cross-walks**:

- `OPERATION_KIND_REGISTRY` model (operation-kind vocabulary + planner constraints)
- `PAT-CHECK-001 v2` model (pattern directory + `doc_id` join rules)

---

## 0. Terms

- **operation_kind** – A normalized action type (e.g. `CREATE_FILE`, `RUN_TESTS`) chosen from `OPERATION_KIND_REGISTRY`.
- **pattern** – A reusable execution contract with a doc suite (spec, schema, executor, tests, examples).
- **doc_id** – Global identifier for a documentation object; **primary join key** across all pattern artifacts.
- **pattern_id** – Stable domain label (e.g. `PAT-ATOMIC-CREATE-001`); secondary key.
- **registry layer** – The set of YAML/JSON registries that define vocabulary, patterns, and routing.

---

## 1. Registry Files

### REG-001: Registry file locations

The following files **MUST** exist:

1. `patterns/registry/OPERATION_KIND_REGISTRY.yaml`
2. `patterns/registry/PATTERN_INDEX.yaml`
3. `patterns/registry/PATTERN_ROUTING.yaml`

The following files **SHOULD** exist:

4. `patterns/registry/PATTERN_INDEX.schema.json`
5. `doc_id_mapping.json` at repo root (or under `.state/`)

---

## 2. Primary Keys & Joins

### REG-010: `doc_id` as canonical join key

- `doc_id` **MUST** be the **primary** join key between:
  - `PATTERN_INDEX.yaml` entries
  - `patterns/specs/*.pattern.yaml`
  - `patterns/schemas/*.schema.json` (and/or sidecars)
  - `patterns/executors/*_executor.*`
  - `patterns/tests/test_*`
  - `patterns/examples/<pattern_name>/*`

- All artifacts for a given pattern **MUST** share the same `doc_id`.

### REG-011: `pattern_id` as secondary key

- `pattern_id` **MUST** be stable and unique within the registry layer.
- `pattern_id` **MUST NOT** be used as the primary join key where `doc_id` is available.
- Tools **MAY** use `pattern_id` as a human-friendly label or routing alias.

---

## 3. OPERATION_KIND_REGISTRY

File: `patterns/registry/OPERATION_KIND_REGISTRY.yaml`

### REG-020: Operation-kind entries

- File **MUST** contain:
  - `version` (string, SemVer)
  - `status` (`draft|active|deprecated`)
  - `operation_kinds` (list)

Each element in `operation_kinds` **MUST** include at least:

```yaml
- id: OPK-0001          # stable ID
  name: CREATE_FILE     # SCREAMING_SNAKE_CASE, unique
  category: file_io     # short, lowercase token
  summary: >-
    One-line description of the operation.
  required_params:      # name + short type hints
    - path
  optional_params:
    - template_id
```

### REG-021: Global constraints

- `name` values **MUST** be unique across registry.
- `name` values **MUST** be stable once in use by patterns or phase plans.
- Planners **MUST** choose `operation_kind` only from this registry.

---

## 4. PATTERN_INDEX

File: `patterns/registry/PATTERN_INDEX.yaml`

### REG-030: Pattern entries

Each pattern entry **MUST** include:

```yaml
- doc_id: DOC-PAT-XXXX-001
  pattern_id: PAT-XXXX-001
  name: atomic_create
  version: 1.0.0
  status: active            # e.g. draft|active|deprecated
  spec_path: patterns/specs/atomic_create.pattern.yaml
  schema_path: patterns/schemas/atomic_create.schema.json
  executor_path: patterns/executors/atomic_create_executor.py
  test_path: patterns/tests/test_atomic_create_executor.py
  example_dir: patterns/examples/atomic_create/
  operation_kinds:
    - CREATE_FILE
    - SAVE_FILE
```

### REG-031: Path & existence rules

- All paths **MUST** point inside the appropriate subdirectories:

  - `spec_path` → `patterns/specs/`
  - `schema_path` → `patterns/schemas/`
  - `executor_path` → `patterns/executors/`
  - `test_path` → `patterns/tests/`
  - `example_dir` → `patterns/examples/`

- Every referenced file/directory **MUST** exist for patterns with `status: active`.

### REG-032: Operation-kind links

- `operation_kinds` list **MUST** contain only names present in `OPERATION_KIND_REGISTRY.yaml`.
- For each pattern entry, the `operation_kinds` list **SHOULD** be minimal but complete: every major action the pattern performs should be represented.

---

## 5. PATTERN_ROUTING

File: `patterns/registry/PATTERN_ROUTING.yaml`

### REG-040: Routing entries

File **MUST** define routing from `operation_kind` → pattern(s). Minimum structure:

```yaml
version: 1.0.0
routes:
  - operation_kind: CREATE_FILE
    default_pattern_id: PAT-ATOMIC-CREATE-001
    alternatives:
      - pattern_id: PAT-BATCH-CREATE-001
        when: large_batch
  - operation_kind: RUN_TESTS
    default_pattern_id: PAT-RUN-TESTS-001
```

### REG-041: Consistency constraints

- Every `operation_kind` used here **MUST** exist in `OPERATION_KIND_REGISTRY.yaml`.
- Every `default_pattern_id` and `alternatives[*].pattern_id` **MUST** exist in `PATTERN_INDEX.yaml`.
- For each `pattern_id` used here, the `operation_kinds` list in `PATTERN_INDEX.yaml` **MUST** include the corresponding `operation_kind`.

---

## 6. Cross-Registry Invariants

### REG-050: One source of truth per concern

- OPERATION_KIND_REGISTRY is the **only** place to define:
  - Which `operation_kind` names are allowed.
- PATTERN_INDEX is the **only** place to define:
  - Which patterns exist and their `doc_id` + artifact paths.
- PATTERN_ROUTING is the **only** place to define:
  - Which pattern is chosen for a given `operation_kind` in default and variant cases.

### REG-051: Doc-suite completeness (PAT-CHECK cross-link)

For any pattern with `status: active` in `PATTERN_INDEX.yaml`:

- `spec_path` **MUST** point to a `.pattern.yaml` containing:
  - `doc_id`, `pattern_id`, `name`, `version`, `role: spec`, `schema_ref`, `executor_ref`.
- `schema_path` target:
  - **MUST** either embed `doc_id` or be mapped via a sidecar/index to the same `doc_id`.
- `executor_path` target:
  - **MUST** contain a `DOC_LINK: <DOC_ID>` style header matching the index `doc_id`.
- `test_path` target:
  - **SHOULD** contain a `DOC_LINK` header with the same `doc_id`.
- Files in `example_dir`:
  - **SHOULD** embed `doc_id` or be mapped via a sidecar; that `doc_id` **MUST** match the index.

These requirements **extend** and specialize `PAT-CHECK-001 v2` at the registry layer.

---

## 7. Phase Plan & Tool Integration

### REG-060: Planner behavior

- Phase plans **MUST** annotate each step with:
  - `operation_kind` (string, from OPERATION_KIND_REGISTRY)
  - Tool-specific arguments/params

- Planners **MUST NOT** directly choose `pattern_id`; they choose only `operation_kind`.
- A router component uses `PATTERN_ROUTING.yaml` to resolve `operation_kind` → `pattern_id` at execution time.

### REG-061: Executor behavior

- Executors **MUST** locate patterns using:
  - `pattern_id` and/or `doc_id` from `PATTERN_INDEX.yaml`,
  - Not hard-coded paths.

- When applying pattern logic, executors **MUST** follow:
  - Schema specified by `schema_path`.
  - The spec in `spec_path`.

---

## 8. Validation & Automation

### REG-070: Required checks

At minimum, the registry layer **SHOULD** be validated by:

1. `PATTERN_DIR_CHECK` (implements PAT-CHECK-001 v2 + REGISTRY_LAYER_SPEC checks)
2. `validate_doc_id_consistency` (ensures 1:1 `doc_id` joins)
3. A small registry validator that verifies:

   - OPERATION_KIND_REGISTRY name uniqueness.
   - PATTERN_INDEX ↔ OPERATION_KIND_REGISTRY ↔ PATTERN_ROUTING references are all valid, with no orphans.

Validation tools **MAY** emit per-requirement PASS/FAIL keyed by:

- `PAT-CHECK-001-*` (directory + doc suite)
- `REG-*` (registry layer rules defined in this spec)

---
