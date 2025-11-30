# MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1

> **Purpose:** Tell an AI exactly how to extend the existing DOC_ID registry with `module_id` for every doc and generate a module-centric view of the repo, **without breaking** current tools.

---

## 0. Intent & Constraints

You are an AI execution agent operating on this repository.

Your goals:

1. **Extend `DOC_ID_REGISTRY.yaml`** so that **every entry in `docs:` has a `module_id` field**.
2. **Infer `module_id`** from existing paths and categories in a deterministic, repeatable way.
3. **Create a module-centric mapping file** that groups docs by module.
4. **Do not break existing tooling** (e.g. `doc_id_registry_cli.py`, `doc_id_scanner.py`).

You MUST:

* Treat **existing files as ground truth** – do not invent IDs or categories.
* **Never** modify or delete `doc_id` values.
* Preserve **YAML structure and ordering** as much as possible.
* Work in **dry-run first**, then apply changes.
* Prefer **explicit mapping rules** over “AI guessing”.

---

## 1. Ground Truth Files & Locations

Assume the repo contains at least:

* `doc_id/DOC_ID_FRAMEWORK.md` – high-level spec for the doc_id system.
* `DOC_ID_REGISTRY.yaml` – canonical registry (this is what you will extend).
* `doc_id/doc_id_registry_cli.py` – CLI that reads/writes `DOC_ID_REGISTRY.yaml`.
* `scripts/doc_id_scanner.py` (or `doc_id_scanner.py`) – scanner that builds `docs_inventory.jsonl`.
* `docs_inventory.jsonl` – JSONL inventory of paths + doc_id presence.

**You MUST read these files** (paths may be slightly different, but names are authoritative) and adapt to their exact structure.

---

## 2. Target Data Model Changes

### 2.1 Add `module_id` to every doc entry

Current `DOC_ID_REGISTRY.yaml` has entries like:

```yaml
docs:
  - doc_id: DOC-GUIDE-DOC-ID-FRAMEWORK-001
    category: guide
    name: doc_id_framework
    title: DOC_ID Framework - Repository-Wide Documentation Identifier System
    status: active
    artifacts:
      - type: doc
        path: doc_id/DOC_ID_FRAMEWORK.md
    created: '2025-11-24'
    last_modified: '2025-11-24'
    tags:
      - framework
      - documentation
      - governance
```

You must extend **every element of the `docs:` list** to include:

```yaml
    module_id: <string>   # NEW FIELD
```

**Rules:**

* `module_id` MUST be a **non-empty string**.

* `module_id` MUST be **stable** over time; treat it as a logical ownership / module identity, not a directory name.

* `module_id` SHOULD use a **dotted namespace**:

  ```text
  <domain>[.<subsystem>[.<subarea>...]]

  # examples
  core.engine
  core.state
  aim.adapters
  pm.cli
  patterns.search
  patterns.patch
  infra.ci
  config.global
  docs.guides
  adr.architecture
  ```

* Place `module_id` in a consistent position, e.g. **after `title` or after `status`**, but **before `artifacts`** to keep related metadata together.

Example after modification:

```yaml
- doc_id: DOC-GUIDE-DOC-ID-FRAMEWORK-001
  category: guide
  name: doc_id_framework
  title: DOC_ID Framework - Repository-Wide Documentation Identifier System
  status: active
  module_id: docs.guides
  artifacts:
    - type: doc
      path: doc_id/DOC_ID_FRAMEWORK.md
  created: '2025-11-24'
  last_modified: '2025-11-24'
  tags:
    - framework
    - documentation
    - governance
```

### 2.2 Optional: Add a `module_taxonomy` section

Add a **new top-level section** to `DOC_ID_REGISTRY.yaml` that defines legal `module_id` values and their meaning:

```yaml
module_taxonomy:
  core.engine:
    description: Core execution engine components (orchestrator, scheduler, executor)
    root_paths:
      - core/engine
      - tests/engine
  core.state:
    description: State management, persistence, snapshots
    root_paths:
      - core/state
      - tests/state
  aim.adapters:
    description: AIM adapters, tool bridges, and integrations
    root_paths:
      - aim/adapters
  patterns.search:
    description: UET search-related patterns
    root_paths:
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/examples
  docs.guides:
    description: High-level user and system guides
    root_paths:
      - doc_id
      - docs
  adr.architecture:
    description: Architecture decision records
    root_paths:
      - adr
```

**Notes:**

* This section is **new**; existing code will ignore it unless extended.
* `root_paths` are used as **hints** to infer `module_id` for existing docs.
* Keep this list small and opinionated; you can expand in later passes.

---

## 3. Inferring `module_id` For All Existing Docs

Your job: assign `module_id` to every doc deterministically.

### 3.1 General algorithm

1. **Load** `DOC_ID_REGISTRY.yaml`.
2. **Load** `docs_inventory.jsonl` so you can cross-check paths if needed.
3. For each entry in `docs:`:

   1. Determine a **canonical artifact path**:

      * Prefer the first `artifacts` item of type `doc`, `spec`, or `source`.
      * If multiple relevant artifacts, choose the one in `src` or primary folder.
   2. Use **path + category** to pick a `module_id` via mapping rules (below).
   3. If no rule applies, assign a **fallback** module and mark for manual review.

### 3.2 Mapping rules by path / category

These rules should be encoded in code, not “guessed” per doc.

You may implement them in **priority order** like this:

1. **Core modules**

   * If any artifact path starts with `core/engine/` or `tests/engine/`:

     * `module_id = "core.engine"`
   * If path starts with `core/state/` or `tests/state/`:

     * `module_id = "core.state"`
   * If path starts with `core/error/` or `error/`:

     * `module_id = "core.error"`

2. **AIM**

   * Paths under `aim/`:

     * `aim/adapters/` → `aim.adapters`
     * `aim/core/` → `aim.core`
     * else → `aim.misc`

3. **Project Management / PM**

   * Paths under `pm/`:

     * `pm/cli/` → `pm.cli`
     * `pm/scripts/` → `pm.scripts`
     * else → `pm.misc`

4. **Patterns (UET)**

   * Paths under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/`:

     * `/specs/` → `patterns.specs`
     * `/executors/` → `patterns.executors`
     * `/examples/` → `patterns.examples`
     * else → `patterns.misc`

5. **Guides, docs, framework**

   * `doc_id/` or main `docs/` root:

     * System-level framework docs → `docs.guides`
     * Tool-specific guides → `docs.tooling` (if path under `docs/tooling`)
   * If `category: guide` and path under `docs/`: `docs.guides`.

6. **ADR / architecture**

   * Paths under `adr/`:

     * `module_id = "adr.architecture"`

7. **Configuration / Infra**

   * `config/` → `config.global` or `config.<subdomain>` if a subdirectory exists.
   * `infra/`, `.github/workflows/`, `ci/` → `infra.ci`.

8. **Tests**

   * If path is under `tests/` and **another doc** already shares the same base filename in a core module:

     * use that module’s `module_id` (e.g., `test_orchestrator.py` → `core.engine`).

### 3.3 Handling ambiguous or unmatched docs

If, after applying the rules above, you cannot infer a high-confidence module:

* Assign a **fallback**:

  ```yaml
  module_id: unassigned
  ```

* Also add a `flags:` list for that doc:

  ```yaml
  flags:
    - missing_module_id_inference
  ```

* Collect all such docs into a **separate report file**:

  * `doc_id/reports/MODULE_ID_UNASSIGNED.jsonl`

  Each line:

  ```json
  {
    "doc_id": "DOC-XXX-YYY-001",
    "category": "guide",
    "candidate_paths": ["unknown/path.md"],
    "reason": "no_matching_module_rule"
  }
  ```

The presence of `unassigned` module IDs is acceptable as an intermediate state but should be clearly visible.

---

## 4. Registry Update Procedure

You must update `DOC_ID_REGISTRY.yaml` **safely**.

### 4.1 Dry-run reporting

Before modifying any files:

1. Parse `DOC_ID_REGISTRY.yaml`.
2. Simulate the `module_id` assignment process.
3. Produce a **dry-run report**:

   * Location: `doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md`
   * Contents:

     * Count of docs per `module_id`.
     * List of `doc_id`s that would get `unassigned`.
     * Example entries for each module (2–3 docs each).

Do **not** modify the registry in this step.

### 4.2 Applying changes

When applying:

1. Create a backup:

   * `cp DOC_ID_REGISTRY.yaml DOC_ID_REGISTRY.backup.<YYYYMMDD_HHMM>.yaml`

2. Recompute `module_id` for every doc (do **not** partially update).

3. Inject `module_id` field into each doc entry.

4. If `module_taxonomy` is missing, add it at the top level.

5. Do not change:

   * `doc_id`
   * `category`
   * `name`
   * `title`
   * `status`
   * `created`
   * `last_modified`
   * `tags`
   * Any existing keys not mentioned here

6. Update `metadata.last_updated` to today’s date (the CLI already does this; if you use it, respect its behavior).

### 4.3 Post-update validation

After writing the file:

1. Run the existing registry validation (e.g. `doc_id_registry_cli.py validate`).

2. Implement or run an additional check that verifies:

   * Every entry in `docs:` has a non-empty `module_id`.
   * All `module_id` values are either:

     * Present in `module_taxonomy`, or
     * Equal to `unassigned`.

3. Emit a final report:

   * `doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json`

   With:

   ```json
   {
     "total_docs": 124,
     "modules": {
       "core.engine": 23,
       "core.state": 8,
       "aim.adapters": 26,
       "docs.guides": 6,
       "adr.architecture": 4,
       "unassigned": 3
     }
   }
   ```

---

## 5. Create a Module-Centric Map File

Once `module_id` exists on every doc, build a **module-centric view**.

### 5.1 New file: `modules/MODULE_DOC_MAP.yaml`

Create `modules/` if it doesn’t exist.

`MODULE_DOC_MAP.yaml` structure:

```yaml
metadata:
  generated_at: "2025-11-30T03:21:00Z"
  source_registry: "DOC_ID_REGISTRY.yaml"
  total_modules: 7
  total_docs: 124

modules:
  core.engine:
    description: Core execution engine components
    docs:
      - doc_id: DOC-CORE-ORCHESTRATOR-001
        category: core
        kind: source
        path: core/engine/orchestrator.py
      - doc_id: DOC-TEST-CORE-ORCHESTRATOR-010
        category: test
        kind: test
        path: tests/engine/test_orchestrator.py

  core.state:
    description: State management, persistence, snapshots
    docs:
      - doc_id: DOC-CORE-STATE-DB-001
        category: core
        kind: source
        path: core/state/db.py

  docs.guides:
    description: High-level framework and user guides
    docs:
      - doc_id: DOC-GUIDE-DOC-ID-FRAMEWORK-001
        category: guide
        kind: doc
        path: doc_id/DOC_ID_FRAMEWORK.md
```

**Rules:**

* `metadata` should be kept small and factual.
* For each `doc_id`:

  * Use `module_id` from registry as grouping key.
  * Derive `kind` from the `artifacts[*].type` field (e.g., `doc`, `spec`, `source`, `test`, `config`).
  * Choose the **most representative artifact** path for `path`:

    * Prefer `source` or `spec` over tests if multiple exist.
* If a `module_id` is `unassigned`, you may:

  * Either omit it from `modules` or
  * Include a dedicated `unassigned` entry with explanation.

---

## 6. Extend Existing CLI (Optional but Recommended)

To make this repeatable, extend `doc_id_registry_cli.py` with two new commands:

1. **`module-assign`**

   * Performs the **module_id inference + registry update**.
   * Supports `--dry-run` and `--apply` modes.
   * Writes the reports described above.

2. **`build-module-map`**

   * Reads `DOC_ID_REGISTRY.yaml` and writes `modules/MODULE_DOC_MAP.yaml`.
   * Optionally accepts `--module-id` filter to build a partial map.

You don’t have to implement these in this pass if not requested, but the spec should be **compatible** with such commands.

---

## 7. Expected Outputs & Files Touched

When you are done, the following should be true:

1. **Modified**

   * `DOC_ID_REGISTRY.yaml`

     * Every `docs:` entry has a `module_id` key.
     * Optional `module_taxonomy:` section exists.
     * `metadata.last_updated` reflects the change.

2. **Created**

   * `doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md`
   * `doc_id/reports/MODULE_ID_UNASSIGNED.jsonl`
   * `doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json`
   * `modules/MODULE_DOC_MAP.yaml`

3. **Preserved**

   * All existing `doc_id` values intact.
   * All categories / counts / indices still valid (or updated only by existing CLI logic).
   * No files outside of the registry + new report/map locations are modified.

---

## 8. How This Will Be Used Later

Do **not** perform any physical file moves in this spec.

The purpose here is:

* To make `module_id` a **first-class attribute** for every doc.
* To produce a **stable module → docs map** that later refactor patterns can consume.

Subsequent specs will:

* Use `module_id` to define **target module layouts**.
* Generate **move plans** (JSONL) that reorganize the repo into a module-centric structure.
* Use `doc_id` + `module_id` together as **stable identities** to track refactors over time.

For now, focus solely on:

> “Extend the registry with `module_id` for all docs and generate a trustworthy module map.”
