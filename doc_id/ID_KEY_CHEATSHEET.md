---
title: ID Key & Categorical Structure Cheatsheet
status: draft
audience: humans_and_ai
# NOTE: Run doc_id_registry_cli.py mint and replace this once registered
doc_id: DOC-TBD-ID-KEY-CHEATSHEET-001
---

# ID Key & Categorical Structure Cheatsheet

This cheatsheet explains **how IDs work in this repo**:

- The **primary key**: `doc_id`
- The **categorical structure**: category + prefix + name + sequence
- The relationship between **`doc_id`** and **domain IDs** like `pattern_id`
- Where and how IDs MUST be embedded in files

Use this whenever you mint new IDs, wire tools, or reason about registry / inventory state.

---

## 1. Quick Glossary

- **`doc_id`**  
  The **single primary identifier** that links all artifacts (docs, code, configs, tests, patterns).  
  Example: `DOC-CORE-STATE-DB-001`

- **Category (registry category key)**  
  Lowercase bucket in `DOC_ID_REGISTRY.yaml` that determines **where** something lives conceptually.  
  Example: `core`, `patterns`, `script`, `test`, `guide`.

- **Category prefix**  
  Uppercase token used inside the `doc_id`, defined per category.  
  Example: `core → CORE`, `patterns → PAT`.

- **Domain IDs (e.g., `pattern_id`)**  
  Domain-specific identifiers (like `PAT-ATOMIC-CREATE-001`) used inside UET or other subsystems.  
  They are **secondary IDs** and MUST NOT replace `doc_id` as the cross-artifact join key.

- **Registry** (`DOC_ID_REGISTRY.yaml`)  
  The **source of truth** that stores:
  - All categories and their prefixes
  - All registered `doc_id` entries
  - Artifact paths + tags for each ID

- **Inventory** (`docs_inventory.jsonl`)  
  A **scan of real files** in the repo and whether they have a `doc_id` embedded.  
  Used to measure coverage and drive auto-assignment.

---

## 2. `doc_id` – Primary Key (Single Linking ID)

### 2.1 Role

- `doc_id` is the **only cross-artifact join key** for this system.
- Every logical "documentation unit" (spec, pattern, module, script, guide, etc.) **MUST** have exactly one `doc_id`.
- All artifacts that belong to that unit **MUST** embed the same `doc_id`.

> **Rule (MUST):** If two files describe the same logical thing (e.g., `orchestrator.py`, its spec, and tests), they **MUST** share one `doc_id`.

### 2.2 Format

There are two active layers of spec:

1. **Base ID format** (from `ID_SYSTEM_SPEC`):

   ```text
   [A-Z0-9]+(-[A-Z0-9]+)*
   ```

2. **Concrete repo format** (from `DOC_ID_FRAMEWORK` + registry):

   ```text
   DOC-<CATEGORY_PREFIX>-<NAME_SEGMENTS>-<NNN>
   ```

Where:

* `DOC` – fixed namespace for doc registry
* `<CATEGORY_PREFIX>` – one of the prefixes from the **categories table** (below)
* `<NAME_SEGMENTS>` – uppercase, dash-separated name (e.g., `STATE-DB`, `SAVE-FILE`)
* `<NNN>` – 3-digit sequence **per category** (`001–999`), managed by the registry

---

## 3. Categories & Prefixes (Categorical Structure)

Categories live in `DOC_ID_REGISTRY.yaml` under `categories:`.

Each category defines:

* A **key** (lowercase) – used by tools / CLI
* A **prefix** (uppercase) – used in the `doc_id`
* A **description**
* An `index_file` for category-specific lists

### 3.1 Current categories (summary)

> **Source of truth:** `DOC_ID_REGISTRY.yaml → categories`

| Category key | Prefix   | Typical scope / directory                                              | Example `doc_id`                     |
| ------------ | -------- | ---------------------------------------------------------------------- | ------------------------------------ |
| `patterns`   | `PAT`    | UET patterns under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/` | `DOC-PAT-SAVE-FILE-001`              |
| `core`       | `CORE`   | Core modules in `core/`                                                | `DOC-CORE-STATE-DB-001`              |
| `error`      | `ERROR`  | Error system modules and plugins in `error/`                           | `DOC-ERROR-HANDLER-001`              |
| `spec`       | `SPEC`   | Specs & schemas in `specifications/`                                   | `DOC-SPEC-WORKFLOW-SCHEMA-001`       |
| `arch`       | `ARCH`   | ADRs & design docs in `adr/`                                           | `DOC-ARCH-ADR-010-ULID-IDENTITY-001` |
| `aim`        | `AIM`    | AIM env manager modules in `aim/`                                      | `DOC-AIM-PROFILE-LOADER-001`         |
| `pm`         | `PM`     | Project management docs / plans                                        | `DOC-PM-PHASE-PLAN-001`              |
| `infra`      | `INFRA`  | Infra / deployment in `infra/`                                         | `DOC-INFRA-PIPELINE-SETUP-001`       |
| `config`     | `CONFIG` | Configuration files in `config/`                                       | `DOC-CONFIG-QUALITY-GATE-001`        |
| `script`     | `SCRIPT` | Automation scripts in `scripts/`                                       | `DOC-SCRIPT-DOC-ID-REGISTRY-CLI-001` |
| `test`       | `TEST`   | Test suites in `tests/`                                                | `DOC-TEST-CORE-ENGINE-001`           |
| `guide`      | `GUIDE`  | User-facing docs in `docs/`                                            | `DOC-GUIDE-DOC-ID-FRAMEWORK-001`     |

> **Rule (MUST):** Every `doc_id` **MUST** belong to exactly one category in `DOC_ID_REGISTRY.yaml`.

> **Rule (SHOULD):** New files **SHOULD** pick the category that matches where the file lives in the repo and how it's used (code vs spec vs script vs guide).

---

## 4. How IDs Are Minted (Categorical Minting Logic)

Minting is handled by `DocIDRegistry` in `doc_id/doc_id_registry_cli.py`.

### 4.1 Inputs to mint

When you call `mint`, you provide:

* `category` – **category key** (e.g., `core`, `patterns`)
* `name` – name segment(s) (e.g., `state_db`, `save_file`)
* `title` – human-readable title
* `artifacts` – list of `{type, path}` entries
* `tags` – free-form tags (e.g., `["core", "db"]`)

### 4.2 Minting steps (simplified)

1. Lookup category:

   ```python
   cat_data = self.data["categories"][category_lower]
   prefix = cat_data["prefix"]        # e.g., "CORE"
   next_num = cat_data["next_id"]     # e.g., 5
   ```

2. Normalize name:

   ```python
   name_upper = name.upper().replace("_", "-").replace(" ", "-")
   # "state_db" → "STATE-DB"
   ```

3. Construct `doc_id`:

   ```python
   doc_id = f"DOC-{prefix}-{name_upper}-{next_num:03d}"
   # "DOC-CORE-STATE-DB-005"
   ```

4. Validate format + duplicates, append to `docs:` list, and bump:

   ```yaml
   categories:
     core:
       next_id: 6  # incremented

   docs:
     - doc_id: DOC-CORE-STATE-DB-005
       category: core
       name: state_db
       title: Database Initialization and Connection Management
       artifacts:
         - type: source
           path: core/state/db.py
         - type: doc
           path: core/state/db.md
       tags:
         - core
         - db
   ```

> **Rule (MUST):** Only the registry's `mint` logic may generate new `doc_id` values. IDs MUST NOT be hand-crafted.

---

## 5. Domain IDs vs `doc_id` (Patterns & Mapping)

### 5.1 Pattern IDs (`pattern_id` / `PAT-*`)

For UET patterns you also have a **domain-level ID** like:

* `pattern_id: PAT-SAVE-FILE-001`
* `pattern_id: PAT-ATOMIC-CREATE-001`
* Legacy "migrated" forms like `PAT-MIGRATED-CORE-010`

These live primarily in the **pattern registry** and pattern specs.

### 5.2 Mapping file (`doc_id_mapping.json`)

To keep the system coherent, you have:

```json
{
  "PAT-ATOMIC-CREATE-001": "DOC-ATOMIC-CREATE-001",
  "PAT-REFACTOR-PATCH-001": "DOC-REFACTOR-PATCH-001"
}
```

This means:

* **Domain key:** `PAT-ATOMIC-CREATE-001`
* **Doc key:** `DOC-ATOMIC-CREATE-001` (or `DOC-PAT-ATOMIC-CREATE-001` in the fully category-prefixed world)

> **Rule (MUST):** Domain-specific IDs like `PAT-*` MAY exist and SHOULD be kept, but `doc_id` remains the **primary join key** for cross-artifact linkage and validation.

> **Rule (SHOULD):** For new work, keep **pattern IDs** and **doc IDs** aligned in naming to reduce cognitive load (e.g., `PAT-SAVE-FILE-001` ↔ `DOC-PAT-SAVE-FILE-001`).

---

## 6. Where IDs Live in Files (Embedding Rules)

These rules are already defined in the framework; this is the **cheatsheet view**:

| File type    | Placement                          | Example                                              |
| ------------ | ---------------------------------- | ---------------------------------------------------- |
| Markdown     | YAML frontmatter                   | `doc_id: DOC-GUIDE-DOC-ID-FRAMEWORK-001`             |
| Python       | Module docstring or header comment | `DOC_ID: DOC-CORE-ORCHESTRATOR-001` or `# DOC_LINK:` |
| YAML         | Top-level field                    | `doc_id: DOC-CONFIG-QUALITY-GATE-001`                |
| JSON         | Top-level field                    | `"doc_id": "DOC-SPEC-WORKSTREAM-SCHEMA-001"`         |
| PowerShell   | Header comment                     | `# DOC_LINK: DOC-SCRIPT-VALIDATE-001`                |
| Shell script | Header comment                     | `# DOC_LINK: DOC-SCRIPT-DEPLOY-PIPELINE-001`         |
| Text         | Optional frontmatter               | `doc_id: DOC-GUIDE-NOTES-001`                        |

Your scanner + auto-assigner (`doc_id_scanner.py`, `doc_id_assigner.py`) enforce this:

* Scanner reads **from files → inventory**
* Registry and auto-assigner write **from inventory → registry + files**

---

## 7. Practical Rules for Humans & AI

### 7.1 When creating a new unit

1. Decide **what it is**:

   * Core module, config, script, guide, pattern, test, etc.

2. Pick the right **category key** from the table (e.g., `core`, `patterns`, `script`).

3. Pick a **name**:

   * Short, stable noun phrase: `state_db`, `save_file`, `doc_id_preflight`.

4. Call the registry:

   ```bash
   python doc_id/doc_id_registry_cli.py mint \
     --category core \
     --name state_db \
     --title "Database Initialization and Connection Management"
   ```

5. Embed the `doc_id` in:

   * All related spec/doc files
   * Code files
   * Configs/tests

### 7.2 When wiring tools or prompts

* **Always pass `doc_id`** (not just filenames) when describing artifacts.
* For patterns, include both:

  * `pattern_id`: `PAT-ATOMIC-CREATE-001`
  * `doc_id`: `DOC-PAT-ATOMIC-CREATE-001` (or mapped legacy form)
* Use `category` + `prefix` if you need to **mint**, **search**, or **filter**:

  * Filter core modules: `category == "core"`
  * Filter scripts: `category == "script"`

### 7.3 Do / Don't

* ✅ **Do** treat `doc_id` as the primary key everywhere.

* ✅ **Do** use categories to keep `doc_id` space organized and human-readable.

* ✅ **Do** keep pattern IDs and doc IDs aligned and mapped.

* ❌ **Don't** hand-craft `doc_id` strings. Always use `mint`.

* ❌ **Don't** use `pattern_id` or filenames as the primary join key across systems.

* ❌ **Don't** create multiple `doc_id` values for the same logical unit.

---

## 8. TL;DR for Agents

> * Use **`doc_id`** as your **only** cross-file join key.
> * Use **categories** (core / patterns / script / config / guide / etc.) to pick the right namespace.
> * Use the registry to **mint**, and ensure file contents + registry + inventory stay in sync.
> * For patterns, treat `pattern_id` as a **domain label** and `doc_id` as the **canonical key**.
