
---

## 1. Re-map your old architecture onto “patterns”

From the auto-docs system you already designed:

* **Doc Card → Ledger → Registry** as the identity spine
* **Micro-kernel + plugins** (`docs.scan`, `docs.validate`, `docs.registry.build`, `docs.guard`, etc.)
* **Suite index + sidecars + MFIDs + spec_indexer/spec_guard/spec_patcher** for structured suites
* **Event hooks** like `on_doc_changed`, `on_registry_built`, `on_runtime_snapshot`, plus a proposed `docs.propagate` plugin with `rules/propagation.map.yml`

You don’t need a new paradigm; you just need a *“pattern family”* on top of this.

### Direct mapping

* **Doc Card (committed)** → **Pattern Card**
  `ids/patterns/cards/<ULID>.yaml`

  * `pattern_id` (ULID)
  * `pattern_key` (e.g. `PAT_ATOMIC_CREATE_FILES`)
  * description, tags, operation_kinds, doc suite membership

* **Doc Registry** → **Pattern Registry**
  `registry/patterns.registry.yaml` generated from cards + suite index

* **Doc Suite (final_spec_docs)** → **Pattern Doc Suite**
  Per-pattern folder, plus a **pattern-suite index** & optional sidecars.

* **docs.propagate plugin** → **patterns.propagate plugin**
  Triggered when a Pattern Card or Pattern Spec changes, applies mapping rules and updates all derived pattern docs.

* **VERSIONING_OPERATING_CONTRACT + docs-guard + doc-tags** →
  **PATTERN_VERSIONING_CONTRACT + pattern-guard + pattern-tags** (same behavior, different domain).

So the big idea is:

> **Patterns are just one more document family inside your existing auto-docs system, with their own Cards, Registries, and propagation rules.**

---

## 2. Single source of truth: “Pattern Card” as the control file

To get “touch one file, update the rest”, you need a *single controlling artifact* per pattern.

### 2.1 Pattern Card shape (committed)

Exactly like your Doc Cards, but for patterns:

```yaml
# ids/patterns/cards/01HXYZ...yaml
schema_version: 1
pattern_id: 01HXYZABCDEF...          # ULID
pattern_key: PAT_ATOMIC_CREATE_FILES # human key, stable
semver: 1.0.0
status: active                       # active|experimental|deprecated
layer: execution|planning|meta
operation_kinds:
  - OPK_ATOMIC_CREATE
  - OPK_WRITE_FILE
summary: "Create 1–3 files with tests in one atomic step."
primary_spec: patterns/specs/atomic_create.pattern.yaml
suite:
  folder: patterns/atomic_create/
  docs:
    spec: specs/atomic_create.pattern.yaml
    schema: schemas/atomic_create.schema.json
    executor_doc: docs/atomic_create_executor.md
    examples: docs/atomic_create_examples.md
    tests_doc: docs/atomic_create_tests.md
links:
  delivers: ["DEL-PATTERNS-AUTOMATION"]
  acceptance: ["AC-PAT-ATOMIC-CREATE"]
```

This is your **Pattern Card**, analogous to the Doc Card in the auto-doc system.

Everything else in the individual pattern suite should be **derived from this + a few templates**.

---

## 3. Pattern Suite as a generated “doc suite”

Borrow directly from your **Document Suite Transformation** plan:

* **Suite Index:** a `patterns/.index/pattern-suite-index.yaml` that lists all patterns, their ULIDs, and the doc suite layout.
* **Sidecars / MFIDs (optional but powerful):** you *can* add `.sidecar.yaml` per pattern-spec or README if you want paragraph-level tracking later, exactly like the spec suite.

At minimum, do this:

```yaml
# patterns/.index/pattern-suite-index.yaml
suite_id: PATTERNS_SUITE
version: 1.0.0
patterns:
  - pattern_id: 01HXYZ...
    pattern_key: PAT_ATOMIC_CREATE_FILES
    folder: patterns/atomic_create/
    docs:
      card: ids/patterns/cards/01HXYZ...yaml
      spec: patterns/specs/atomic_create.pattern.yaml
      schema: patterns/schemas/atomic_create.schema.json
      executor_doc: patterns/atomic_create/EXECUTOR.md
      examples_doc: patterns/atomic_create/EXAMPLES.md
      tests_doc: patterns/atomic_create/TESTS.md
```

This index lets a generator know **exactly** what to touch for each pattern.

---

## 4. How “change one file, update many” actually works

Your old MRP architecture already defined a plugin like `docs.propagate` that listens for `on_doc_changed` and runs mapping rules.

We re-use that *exact* idea:

### 4.1 New plugin: `patterns.propagate`

Directory structure (directly mirroring your plugin anatomy):

```text
plugins/patterns/
  └─ PLG_PATTERNS_PROPAGATE/
     ├─ plugin.spec.json
     ├─ schemas/
     │   ├─ input.schema.json
     │   └─ output.schema.json
     ├─ rules/
     │   └─ propagation.map.yml
     └─ src/
         └─ patterns_propagate.py
```

**Hook:** `on_doc_changed` (same as `docs.propagate`).
**Filter:** only fire when the changed doc is:

* a `Pattern Card` (`ids/patterns/cards/*.yaml`), or
* a `pattern.spec` file (`patterns/specs/*.pattern.yaml`).

### 4.2 Mapping rules (the real magic)

In `rules/propagation.map.yml`, you define **how fields in the Pattern Card / Spec map to other files**:

```yaml
# plugins/patterns/PLG_PATTERNS_PROPAGATE/rules/propagation.map.yml
patterns:
  # When a Pattern Card changes…
  - match:
      doc_type: pattern_card
    propagate_to:
      - target_type: pattern_spec
        template: templates/pattern/spec.j2
        overwrite_sections:
          - id: "PATTERN_META"
          - id: "PATTERN_INPUT_OUTPUT"
      - target_type: executor_doc
        template: templates/pattern/executor_doc.j2
        overwrite_sections:
          - id: "EXECUTOR_SIGNATURE"
          - id: "OPERATION_KIND_TABLE"
      - target_type: examples_doc
        template: templates/pattern/examples_doc.j2
        overwrite_sections:
          - id: "CANONICAL_EXAMPLES"
      - target_type: global_pattern_index
        handler: "patterns_propagate.update_global_index"
      - target_type: operation_kind_registry
        handler: "patterns_propagate.sync_operation_kinds"
```

So when the Pattern Card changes:

1. Plugin gets `pattern_id`, `pattern_key`, updated fields.
2. Loads `pattern-suite-index.yaml` to know where all the docs live.
3. Applies templates / handlers to update those docs **only in the templated sections** (using section IDs or markers), leaving freehand text intact.

This is exactly the “Design by Contract” idea per file: clearly defined inputs/outputs/invariants for the `patterns.propagate` plugin and each target file.

---

## 5. Minimize touched files via generated_sections

To keep Git diffs small and avoid merge hell:

* Each generated file (README, EXECUTOR doc, etc.) gets **marked regions** like:

```markdown
<!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:BEGIN -->
…generated content…
<!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:END -->
```

The `patterns_propagate.py` plugin:

* Only rewrites content between those markers.
* Validates invariants like “pattern_id in card == pattern_id in target doc”.

That way:

* **Human can edit the rest** of the document freely.
* **Automation only touches known blocks** → fewer conflicts, smaller diffs, deterministic behavior.

---

## 6. Re-using the Doc Registry & CI Guards

Your auto-doc system already has:

* `build_doc_registry.py` → scans docs, builds fast lookup, enforces unique `doc_key`.
* `docs-guard.yml` → one-doc rule, semver bump, front-matter validation, unique `doc_key`, intent checks.
* `doc-tags.yml` → post-merge tagging `docs-{doc_key}-{semver}`.

For patterns:

1. **Pattern Registry Builder**
   Clone the DocumentRegistry design into `build_pattern_registry.py` using front-matter / cards the same way you do for docs:

   ```bash
   python scripts/build_pattern_registry.py --check-only
   ```

   Output: `registry/patterns.registry.yaml` (keyed by `pattern_key` and `pattern_id`).

2. **pattern-guard.yml** (CI workflow)

   * Verify:

     * Pattern Card schema valid
     * Pattern Spec matches Pattern Card (pattern_id, key, semver)
     * Pattern Suite index references are consistent
   * Optionally enforce:

     * One-pattern rule: PR only changes one Pattern Card + its derived docs
     * `patterns.propagate --check` is clean (no drift)

3. **pattern-tags.yml** (optional)

   * Create tags like: `pattern-{pattern_key}-{semver}`
   * Gives you immutable history for each pattern, same as docs.

Basically: **copy the doc governance, but for Pattern Cards + pattern suite**.

---

## 7. Where OPERATION_KIND_REGISTRY.yaml fits

Your new log-extraction scripts feed into a “discover operation kinds / patterns” flow. The old architecture already defined hooks like `on_runtime_snapshot` and suggested plugins that react to it.

You can:

* Add plugin **`ops.discover`** that:

  * Reads aggregated logs / terminal transcripts.
  * Clusters commands / behaviors into candidate *operation kinds*.
  * Writes **draft entries** into `OPERATION_KIND_REGISTRY.drafts.yaml`.

* Then the **Pattern Card** references those operation kinds:

  ```yaml
  operation_kinds:
    - OPK_ATOMIC_CREATE
    - OPK_WRITE_FILE
  ```

* `patterns.propagate.sync_operation_kinds` keeps **OPERATION_KIND_REGISTRY.yaml** in sync with the **union of operation_kinds used across all Pattern Cards** (plus human-approved metadata).

So the flow becomes:

1. Logs → `ops.discover` → candidate operation kinds
2. Human reviews → promotes to real entries in `OPERATION_KIND_REGISTRY.yaml`
3. Pattern Card references those IDs
4. `patterns.propagate` keeps global registry + pattern docs current

---

## 8. Concrete “first implementation” path

If you want a minimal, shippable version:

1. **Define the Pattern Card schema + a few cards**

   * `ids/patterns/cards/*.yaml` + JSON Schema
2. **Create `patterns/.index/pattern-suite-index.yaml`**

   * One entry per pattern, pointing to suite files (even if some are empty placeholders).
3. **Write a simple `pattern_suite_sync.py` (not full plugin yet)**

   * Input: `pattern_key` or `pattern_id`
   * Behavior:

     * Read card + suite index.
     * Render spec / executor / examples docs using templates + markers.
     * Update `PATTERN_INDEX.yaml` + `OPERATION_KIND_REGISTRY.yaml`.
4. **Wrap it in `pattern_cli.ps1`**

   * `pattern sync PAT_ATOMIC_CREATE_FILES`
   * `pattern sync --all`
5. **Add a CI check**

   * Run `pattern_suite_sync.py --check` on PRs that touch pattern cards/specs; fail if it would change anything → forces devs to run sync locally.

Later, when you’re ready, you can:

* Promote `pattern_suite_sync.py` into a proper **`patterns.propagate` plugin** hanging off your existing micro-kernel.
* Add sidecars and suite-index MFIDs exactly like your spec suite if you want paragraph-level tracking for patterns too.

---
Here you go — all three pieces in one place and aligned with your existing doc/card style.

---

## 1. Pattern Card schema

### 1.1 Canonical Pattern Card YAML shape

This lives in something like:

`ids/patterns/cards/<ULID>.yaml`

```yaml
schema_version: 1

# Identity
ulid: 01JC4PATTERNXYZABCDEF123456      # immutable ULID for this pattern
pattern_key: PAT_ATOMIC_CREATE_FILES   # human key, globally unique, never reused
pattern_id: PAT-ATOMIC-CREATE-001      # matches PATTERN_INDEX.pattern_id
doc_id: DOC-PAT-ATOMIC-CREATE-001      # doc suite id, matches PATTERN_INDEX.doc_id (if present)

# Versioning & lifecycle
semver: 1.0.0                          # pattern version
status: draft                          # draft|active|spec_only|migrated|deprecated|experimental
category: file_creation                # e.g. file_creation|code_modification|module_setup|infra
layer: execution                       # execution|planning|meta|infra

# Behavior & scope
operation_kinds:                       # must map to OPERATION_KIND_REGISTRY entries
  - OPK-ATOMIC-CREATE
summary: >
  Create 1–3 files with tests in one atomic step.
description: |
  This pattern is used when the user wants to create a small number
  of files (1–3) along with basic tests and optional docs in a single,
  atomic operation. It enforces consistent layout and naming.

# Pattern suite layout (single source of truth for all docs)
suite:
  folder: patterns/atomic_create/
  spec: patterns/specs/atomic_create.pattern.yaml
  schema: patterns/schemas/atomic_create.schema.json
  executor: patterns/executors/atomic_create_executor.ps1
  tests:
    - patterns/tests/test_atomic_create_executor.ps1
  examples_dir: patterns/examples/atomic_create/
  docs:
    executor_doc: patterns/atomic_create/EXECUTOR.md
    examples_doc: patterns/atomic_create/EXAMPLES.md
    tests_doc: patterns/atomic_create/TESTS.md

# Global registries (for propagation)
registry:
  pattern_index: patterns/registry/PATTERN_INDEX.yaml
  operation_kind_registry: patterns/registry/OPERATION_KIND_REGISTRY.yaml

# Ownership, tags, links
owners:
  - "richg"
  - "patterns-team@project"
tags:
  - core
  - high-usage

links:
  delivers: ["DEL-PATTERNS-AUTOMATION"]
  acceptance: ["AC-PAT-ATOMIC-CREATE"]
  evidence:
    - "tests/patterns/test_atomic_create.feature"
    - "reports/patterns/atomic_create_coverage.xml"
```

---

### 1.2 JSON Schema for Pattern Card (`pattern_card.schema.json`)

This is a **sketch**, but strict enough for validation:

```json
{
  "$id": "schemas/pattern_card.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Pattern Card",
  "type": "object",
  "required": [
    "schema_version",
    "ulid",
    "pattern_key",
    "pattern_id",
    "doc_id",
    "semver",
    "status",
    "category",
    "layer",
    "operation_kinds",
    "suite"
  ],
  "properties": {
    "schema_version": {
      "type": "integer",
      "const": 1
    },
    "ulid": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "pattern_key": {
      "type": "string",
      "pattern": "^PAT_[A-Z0-9_]+$"
    },
    "pattern_id": {
      "type": "string",
      "pattern": "^PAT-[A-Z0-9-]+$"
    },
    "doc_id": {
      "type": "string",
      "pattern": "^DOC-PAT-[A-Z0-9-]+$"
    },
    "semver": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "status": {
      "type": "string",
      "enum": [
        "draft",
        "active",
        "spec_only",
        "migrated",
        "deprecated",
        "experimental"
      ]
    },
    "category": {
      "type": "string"
    },
    "layer": {
      "type": "string",
      "enum": ["execution", "planning", "meta", "infra"]
    },
    "operation_kinds": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "summary": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "suite": {
      "type": "object",
      "required": ["folder", "spec", "schema", "executor", "tests", "examples_dir"],
      "properties": {
        "folder": { "type": "string" },
        "spec":   { "type": "string" },
        "schema": { "type": "string" },
        "executor": { "type": "string" },
        "tests": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1
        },
        "examples_dir": { "type": "string" },
        "docs": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        }
      },
      "additionalProperties": false
    },
    "registry": {
      "type": "object",
      "properties": {
        "pattern_index": { "type": "string" },
        "operation_kind_registry": { "type": "string" }
      },
      "additionalProperties": false
    },
    "owners": {
      "type": "array",
      "items": { "type": "string" }
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "links": {
      "type": "object",
      "properties": {
        "delivers": {
          "type": "array",
          "items": { "type": "string" }
        },
        "acceptance": {
          "type": "array",
          "items": { "type": "string" }
        },
        "evidence": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

## 2. Example `propagation.map.yml` for 1–2 pattern docs

This is the config that tells a plugin / sync tool how to propagate changes from the Pattern Card (and optionally the spec) into other artifacts.

Put it at:

`plugins/patterns/PLG_PATTERNS_PROPAGATE/rules/propagation.map.yml`

```yaml
version: 1

# When a Pattern Card changes, which files do we update and how?
rules:

  # 1) Card → Pattern Spec (meta block)
  - name: card_to_spec_meta
    when:
      source_type: pattern_card
    targets:
      - target_type: pattern_spec
        # Use `suite.spec` path from the card as target
        target_path_from: "suite.spec"
        mode: patch_yaml_block
        yaml_block:
          # Fields in the spec that MUST mirror the card
          pattern_id: "{{ pattern_id }}"
          doc_id: "{{ doc_id }}"
          name: "{{ pattern_key | lower | replace('pat_', '') }}"
          version: "{{ semver }}"
          status: "{{ status }}"
          category: "{{ category }}"
          operation_kinds: "{{ operation_kinds }}"

  # 2) Card → PATTERN_INDEX entry
  - name: card_to_pattern_index
    when:
      source_type: pattern_card
    targets:
      - target_type: pattern_index
        # Use `registry.pattern_index` path from the card
        target_path_from: "registry.pattern_index"
        mode: update_pattern_index_entry
        # pattern_index entry is matched by pattern_id
        match_key: "pattern_id"
        update_fields:
          pattern_id: "{{ pattern_id }}"
          doc_id: "{{ doc_id }}"
          name: "{{ pattern_key | lower | replace('pat_', '') }}"
          version: "{{ semver }}"
          status: "{{ status }}"
          category: "{{ category }}"
          spec_path: "{{ suite.spec }}"
          schema_path: "{{ suite.schema }}"
          executor_path: "{{ suite.executor }}"
          test_path: "{{ suite.tests[0] }}"
          example_dir: "{{ suite.examples_dir }}"

  # 3) Card → Executor doc (generated header section only)
  - name: card_to_executor_doc
    when:
      source_type: pattern_card
    targets:
      - target_type: executor_doc
        target_path_from: "suite.docs.executor_doc"
        mode: patch_marked_section
        section_id: "EXECUTOR_SIGNATURE"
        template: |
          <!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:BEGIN -->
          Pattern: {{ pattern_key }} ({{ pattern_id }})
          Doc ID: {{ doc_id }}
          Version: {{ semver }}
          Status: {{ status }}
          Category: {{ category }}
          Operation Kinds:
          {% for opk in operation_kinds %}
          - {{ opk }}
          {% endfor %}
          <!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:END -->

  # 4) Spec → Pattern Card (optional one-way sync for semver/status)
  - name: spec_to_card_version
    when:
      source_type: pattern_spec
    targets:
      - target_type: pattern_card
        mode: patch_yaml_fields
        match_field: "pattern_id"
        fields_from_spec:
          # map spec.version → card.semver, spec.status → card.status
          semver: "version"
          status: "status"
```

This is intentionally high-level; your actual plugin/sync script will interpret:

* `source_type` (pattern_card vs pattern_spec),
* `mode` (`patch_yaml_block`, `update_pattern_index_entry`, `patch_marked_section`, etc.),
* And do the concrete file manipulations.

---

## 3. Skeleton `pattern_suite_sync.py`

This is a Python skeleton you can drop into `scripts/pattern_suite_sync.py` and call from `pattern_cli.ps1`.

Assumptions:

* You have `PyYAML` (`pip install pyyaml`).
* You have `pattern-suite-index` at `patterns/.index/pattern-suite-index.yaml`.
* Pattern Cards live under `ids/patterns/cards/*.yaml`.

```python
#!/usr/bin/env python
"""
pattern_suite_sync.py

Synchronize per-pattern doc suite files (spec, PATTERN_INDEX entry, executor docs, etc.)
from the canonical Pattern Card.

Usage:
  python pattern_suite_sync.py --pattern-id PAT-ATOMIC-CREATE-001
  python pattern_suite_sync.py --pattern-key PAT_ATOMIC_CREATE_FILES
  python pattern_suite_sync.py --all
  python pattern_suite_sync.py --check --all
"""

import argparse
import copy
import dataclasses
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # requires PyYAML

ROOT = Path(__file__).resolve().parents[1]  # adjust as needed (e.g. repo root)


# ----------------------------
# Data models
# ----------------------------

@dataclasses.dataclass
class PatternCard:
    raw: Dict[str, Any]
    path: Path

    @property
    def pattern_id(self) -> str:
        return self.raw["pattern_id"]

    @property
    def pattern_key(self) -> str:
        return self.raw["pattern_key"]

    @property
    def doc_id(self) -> str:
        return self.raw["doc_id"]

    @property
    def semver(self) -> str:
        return self.raw["semver"]

    @property
    def status(self) -> str:
        return self.raw["status"]

    @property
    def category(self) -> str:
        return self.raw["category"]

    @property
    def operation_kinds(self) -> List[str]:
        return list(self.raw.get("operation_kinds", []))

    @property
    def suite(self) -> Dict[str, Any]:
        return self.raw["suite"]

    @property
    def registry(self) -> Dict[str, Any]:
        return self.raw.get("registry", {})


@dataclasses.dataclass
class PatternSuiteEntry:
    pattern_id: str
    pattern_key: str
    doc_id: Optional[str]
    suite: Dict[str, Any]
    card_path: Path


# ----------------------------
# Helpers
# ----------------------------

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(data: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def load_pattern_suite_index() -> Dict[str, Any]:
    idx_path = ROOT / "patterns" / ".index" / "pattern-suite-index.yaml"
    if not idx_path.exists():
        raise SystemExit(f"pattern suite index not found at {idx_path}")
    return load_yaml(idx_path)


def find_suite_entry(
    index: Dict[str, Any],
    pattern_id: Optional[str] = None,
    pattern_key: Optional[str] = None,
) -> PatternSuiteEntry:
    candidates = []
    for p in index.get("patterns", []):
        if pattern_id and p.get("pattern_id") == pattern_id:
            candidates.append(p)
        elif pattern_key and p.get("pattern_key") == pattern_key:
            candidates.append(p)

    if not candidates:
        raise SystemExit(f"No suite entry found for pattern_id={pattern_id} pattern_key={pattern_key}")
    if len(candidates) > 1:
        raise SystemExit(f"Multiple suite entries found; please disambiguate pattern_id/pattern_key")

    entry = candidates[0]
    card_path = ROOT / entry["docs"]["card"]
    return PatternSuiteEntry(
        pattern_id=entry["pattern_id"],
        pattern_key=entry["pattern_key"],
        doc_id=entry.get("doc_id"),
        suite=entry["docs"],
        card_path=card_path,
    )


def load_pattern_card(path: Path) -> PatternCard:
    raw = load_yaml(path)
    return PatternCard(raw=raw, path=path)


# ----------------------------
# Sync operations
# ----------------------------

def sync_spec_from_card(card: PatternCard, check_only: bool = False) -> bool:
    """Ensure spec metadata matches the Pattern Card (doc_id, pattern_id, version, status, category, operation_kinds)."""
    spec_path = ROOT / card.suite["spec"]
    if not spec_path.exists():
        print(f"[WARN] Spec not found for {card.pattern_id}: {spec_path}")
        return False

    spec = load_yaml(spec_path)
    original = copy.deepcopy(spec)

    spec.setdefault("doc_id", card.doc_id)
    spec.setdefault("pattern_id", card.pattern_id)
    spec["name"] = spec.get("name") or card.pattern_key.lower().replace("pat_", "")
    spec["version"] = card.semver
    spec["status"] = card.status
    spec["category"] = card.category
    spec["operation_kinds"] = card.operation_kinds

    if spec != original:
        print(f"[SYNC] Updating spec: {spec_path}")
        if not check_only:
            dump_yaml(spec, spec_path)
        return True

    return False


def sync_pattern_index_entry(card: PatternCard, check_only: bool = False) -> bool:
    """Update PATTERN_INDEX entry for this pattern to reflect the card & spec paths."""
    reg_path = ROOT / card.registry.get("pattern_index", "patterns/registry/PATTERN_INDEX.yaml")
    reg_path = reg_path if reg_path.is_absolute() else ROOT / reg_path

    if not reg_path.exists():
        print(f"[WARN] PATTERN_INDEX not found at {reg_path}")
        return False

    reg = load_yaml(reg_path)
    changed = False

    for entry in reg.get("patterns", []):
        if entry.get("pattern_id") == card.pattern_id:
            original = copy.deepcopy(entry)
            entry["doc_id"] = card.doc_id
            entry["name"] = entry.get("name") or card.pattern_key.lower().replace("pat_", "")
            entry["version"] = card.semver
            entry["status"] = card.status
            entry["category"] = card.category
            entry["spec_path"] = card.suite["spec"]
            entry["schema_path"] = card.suite["schema"]
            entry["executor_path"] = card.suite["executor"]
            # use first test as canonical; you can expand later
            tests = card.suite.get("tests", [])
            if tests:
                entry["test_path"] = tests[0]
            entry["example_dir"] = card.suite["examples_dir"]
            if entry != original:
                changed = True
            break
    else:
        print(f"[WARN] No PATTERN_INDEX entry found for {card.pattern_id} in {reg_path}")
        return False

    if changed:
        print(f"[SYNC] Updating PATTERN_INDEX entry for {card.pattern_id}")
        if not check_only:
            dump_yaml(reg, reg_path)
        return True

    return False


def sync_executor_doc_from_card(card: PatternCard, check_only: bool = False) -> bool:
    """Update auto-generated header section in the executor doc, if configured."""
    docs = card.suite.get("docs", {})
    exec_doc_rel = docs.get("executor_doc")
    if not exec_doc_rel:
        return False

    exec_doc_path = ROOT / exec_doc_rel
    if not exec_doc_path.exists():
        print(f"[WARN] Executor doc not found at {exec_doc_path}")
        return False

    content = exec_doc_path.read_text(encoding="utf-8")
    original = content

    begin_marker = "<!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:BEGIN -->"
    end_marker = "<!-- PATTERN_AUTO:EXECUTOR_SIGNATURE:END -->"

    if begin_marker not in content or end_marker not in content:
        print(f"[WARN] No auto-gen markers in {exec_doc_path}")
        return False

    header_block = [
        begin_marker,
        f"Pattern: {card.pattern_key} ({card.pattern_id})",
        f"Doc ID: {card.doc_id}",
        f"Version: {card.semver}",
        f"Status: {card.status}",
        f"Category: {card.category}",
        "Operation Kinds:",
    ]
    header_block.extend([f"- {opk}" for opk in card.operation_kinds])
    header_block.append(end_marker)

    new_block = "\n".join(header_block)

    # Replace block
    pre, _, rest = content.partition(begin_marker)
    _, _, post = rest.partition(end_marker)
    content = pre + new_block + post

    if content != original:
        print(f"[SYNC] Updating executor doc: {exec_doc_path}")
        if not check_only:
            exec_doc_path.write_text(content, encoding="utf-8")
        return True

    return False


def sync_pattern_suite(
    pattern_id: Optional[str] = None,
    pattern_key: Optional[str] = None,
    check_only: bool = False,
) -> bool:
    """Sync all derived artifacts for one pattern. Returns True if any changes would be made."""
    index = load_pattern_suite_index()
    entry = find_suite_entry(index, pattern_id=pattern_id, pattern_key=pattern_key)
    card = load_pattern_card(entry.card_path)

    changed = False
    changed |= sync_spec_from_card(card, check_only=check_only)
    changed |= sync_pattern_index_entry(card, check_only=check_only)
    changed |= sync_executor_doc_from_card(card, check_only=check_only)

    return changed


def sync_all(check_only: bool = False) -> bool:
    """Sync all patterns. Returns True if any changes would be made."""
    index = load_pattern_suite_index()
    any_changed = False
    for p in index.get("patterns", []):
        entry = PatternSuiteEntry(
            pattern_id=p["pattern_id"],
            pattern_key=p["pattern_key"],
            doc_id=p.get("doc_id"),
            suite=p["docs"],
            card_path=ROOT / p["docs"]["card"],
        )
        card = load_pattern_card(entry.card_path)
        print(f"\n[SYNC] Pattern {card.pattern_id} ({card.pattern_key})")
        changed = False
        changed |= sync_spec_from_card(card, check_only=check_only)
        changed |= sync_pattern_index_entry(card, check_only=check_only)
        changed |= sync_executor_doc_from_card(card, check_only=check_only)
        any_changed |= changed

    return any_changed


# ----------------------------
# CLI
# ----------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Sync pattern suites from Pattern Cards.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pattern-id", help="Pattern ID (e.g. PAT-ATOMIC-CREATE-001)")
    group.add_argument("--pattern-key", help="Pattern key (e.g. PAT_ATOMIC_CREATE_FILES)")
    group.add_argument("--all", action="store_true", help="Sync all patterns in the suite index")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: do not write files, just report if changes would be made",
    )

    args = parser.parse_args(argv)

    if args.all:
        changed = sync_all(check_only=args.check)
    else:
        changed = sync_pattern_suite(
            pattern_id=args.pattern_id,
            pattern_key=args.pattern_key,
            check_only=args.check,
        )

    if args.check and changed:
        # In CI you can treat this as "out-of-sync" and fail
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Wiring to `pattern_cli.ps1` (conceptual)

In `pattern_cli.ps1` you’d add something like:

```powershell
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("sync")]
  [string]$Command,
  [string]$PatternId,
  [string]$PatternKey,
  [switch]$All,
  [switch]$Check
)

if ($Command -eq "sync") {
  $argsList = @()
  if ($PatternId) { $argsList += "--pattern-id"; $argsList += $PatternId }
  if ($PatternKey) { $argsList += "--pattern-key"; $argsList += $PatternKey }
  if ($All) { $argsList += "--all" }
  if ($Check) { $argsList += "--check" }

  python scripts/pattern_suite_sync.py @argsList
}
```

---

If you want, next step we can take a **real pattern** from your PATTERN_INDEX (e.g. `PAT-PATCH-001`) and:

* Draft an actual Pattern Card YAML for it, and
* Show what the spec + PATTERN_INDEX entry look like *before and after* a sync run.
