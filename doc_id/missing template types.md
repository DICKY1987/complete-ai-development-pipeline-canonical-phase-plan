---
doc_id: DOC-GUIDE-MISSING-TEMPLATE-TYPES-411
---

Yes — there are a few **big missing template types** that would make the whole doc_id system *way* more standardized and “AI-safe.”

You already have:

* The **framework spec** (`DOC_ID_FRAMEWORK.md`)
* A **system spec** (`UTE_ID_SYSTEM_SPEC.md`)
* A **registry** (`DOC_ID_REGISTRY.yaml`)
* One-off **reports** (coverage, conflict analysis, exploration summary, roadmap)
* Scripts / scanners / validators

What’s missing are **reusable, copy-pasteable templates** that turn those ideas into **repeatable patterns**.

Below I’ll list the templates I think you *should* have, plus a minimal skeleton for each.

---

## 1. File-Level `doc_id` Placement Templates (per language)

**Why needed**

Right now, there’s no single canonical “this is *exactly* how a file should declare its doc_id” per file type. That makes auto-injection, scanning, and validation harder.

You want templates like:

* `TEMPLATE_doc_id_header.python.txt`
* `TEMPLATE_doc_id_header.powershell.txt`
* `TEMPLATE_doc_id_header.yaml.txt`
* `TEMPLATE_doc_id_header.md.txt`
* `TEMPLATE_doc_id_header.json.txt`

**Example: Python**

```text
# TEMPLATE_doc_id_header.python.txt

# DOC_ID: {{DOC_ID}}
"""
{{TITLE}}
{{SHORT_DESCRIPTION}}
"""
```

**Example: PowerShell**

```text
# TEMPLATE_doc_id_header.powershell.txt

# DOC_LINK: {{DOC_ID}}
param(
    # parameters...
)
```

**Example: YAML / JSON config**

```text
# TEMPLATE_doc_id_header.yaml.txt

doc_id: {{DOC_ID}}
# other keys below...
```

```text
# TEMPLATE_doc_id_header.json.txt

{
  "doc_id": "{{DOC_ID}}",
  // other keys...
}
```

**Example: Markdown**

```text
<!-- TEMPLATE_doc_id_header.md.txt -->

---
doc_id: {{DOC_ID}}
title: {{TITLE}}
status: {{STATUS}}
---

# {{H1_TITLE}}
```

👉 These let AI tools **inject or enforce** doc_id placement with zero ambiguity.

---

## 2. Canonical `DOC_ID_REGISTRY` Entry Template

**Why needed**

You have a **registry file**, but not a **formal “this is one entry” template** for humans/AI to follow. That leads to drift in which fields are present.

Create something like `TEMPLATE_DOC_ID_REGISTRY_ENTRY.yaml`:

```yaml
# TEMPLATE_DOC_ID_REGISTRY_ENTRY.yaml

- doc_id: DOC-{{CATEGORY}}-{{NAME}}-{{NNN}}
  category: {{category_slug}}        # e.g. core | spec | guide | adr | pattern | script
  name: {{short_machine_name}}       # e.g. orchestrator_state
  title: {{human_readable_title}}
  status: active                     # active | draft | deprecated
  module_id: {{module.namespace}}    # e.g. core.engine, docs.guides
  artifacts:
    - type: {{artifact_type}}        # doc | spec | source | test | schema | config | script
      path: {{relative/path.ext}}
    # add more artifacts here if needed
  created: "{{YYYY-MM-DD}}"
  last_modified: "{{YYYY-MM-DD}}"
  tags:
    - {{tag_1}}
    - {{tag_2}}
  notes: >
    {{freeform_notes_if_any}}
```

You can then tell AI:

> “Whenever you mint a new doc_id, populate a new registry entry using `TEMPLATE_DOC_ID_REGISTRY_ENTRY.yaml`.”

---

## 3. Pattern Suite Templates for Doc-ID Operations (PAT-DOC-ID-*)

You already *name* patterns like:

* `PAT-DOC-ID-SCAN-001`
* `PAT-DOC-ID-AUTOASSIGN-002`
* `PAT-DOC-ID-PREFLIGHT-003`

…but they aren’t yet formal **UET Pattern Doc Suites** (spec + schema + executor + tests + examples).

You want a **generic pattern template** for doc_id operations, e.g.
`UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/TEMPLATE_doc_id_pattern.pattern.yaml`:

```yaml
# TEMPLATE_doc_id_pattern.pattern.yaml

pattern_id: PAT-DOC-ID-{{OPERATION}}-{{NNN}}
version: 1.0.0
status: draft

name: {{operation_name}}             # e.g. "Doc ID Repository Scanner"
summary: >
  {{one_line_summary}}

category: doc_id                     # or governance, infra, etc.
operation_kind: DOC_ID_{{OPERATION}} # e.g. DOC_ID_SCAN, DOC_ID_AUTOASSIGN, DOC_ID_PREFLIGHT

inputs:
  repo_root:
    type: path
    required: true
  config_path:
    type: path
    required: false
  # etc.

outputs:
  report_path:
    type: path
  stats:
    type: json

constraints:
  - MUST use doc_id as canonical join key
  - MUST NOT modify files when mode=dry-run

steps:
  - id: scan
    description: "Scan all eligible files and collect doc_id info"
  - id: classify
    description: "Classify entries as registered, missing, invalid"
  - id: write_report
    description: "Write JSONL + Markdown reports"

validation:
  - type: script
    path: patterns/tests/{{test_script}}
  - type: schema
    path: patterns/schemas/{{schema_file}}

examples:
  - name: "Full repo scan"
    command: >
      uet run PAT-DOC-ID-SCAN-001 --repo_root=. --mode=dry-run
```

Then instantiate:

* `PAT-DOC-ID-SCAN-001.pattern.yaml`
* `PAT-DOC-ID-AUTOASSIGN-002.pattern.yaml`
* `PAT-DOC-ID-PREFLIGHT-003.pattern.yaml`

All using this template.

---

## 4. Operational Report Templates (Coverage, Preflight, Conflict/Migration)

You have **instance reports** (coverage report, conflict analysis) but no reusable **templates**. Standardizing these lets AI emit consistent outputs every time.

### 4.1 Coverage report template

`TEMPLATE_DOC_ID_COVERAGE_REPORT.md`:

```markdown
# Doc ID Coverage Report
**Generated**: {{timestamp}}
**Inventory**: {{inventory_file}}

---

## Summary

| Metric           | Value        |
|------------------|--------------|
| Total Files      | {{total}}    |
| With doc_id      | {{with}}     |
| Without doc_id   | {{without}}  |
| Invalid doc_id   | {{invalid}}  |
| Coverage         | {{coverage}} |

---

## By Directory (Top N)

| Directory               | Files | With doc_id | Coverage |
|-------------------------|-------|------------|----------|
| {{dir}}                 | {{}}  | {{}}       | {{}}    |

## Recommendations

1. {{recommendation_1}}
2. {{recommendation_2}}
```

### 4.2 Preflight gate report

`TEMPLATE_DOC_ID_PREFLIGHT_GATE_REPORT.md`:

```markdown
# Doc ID Preflight Gate – Refactor Readiness
**Run ID**: {{run_id}}
**Date**: {{timestamp}}
**Target Operation**: {{operation_name}}

---

## Gate Result

- **Status**: {{PASSED|FAILED}}
- **Coverage**: {{coverage_percent}}%
- **Threshold**: {{required_threshold}}%

## Key Metrics

- Total files: {{total_files}}
- Eligible files: {{eligible_files}}
- Files with doc_id: {{with_doc_id}}
- Files without doc_id: {{without_doc_id}}

## Blocking Issues (if any)

- [ ] {{issue_1}}
- [ ] {{issue_2}}

## Decision

- ☐ Proceed with refactor
- ☐ Block refactor until issues are resolved
```

### 4.3 Conflict / migration log template

`TEMPLATE_DOC_ID_CONFLICT_LOG.md`:

```markdown
# Doc ID Conflict & Migration Log
**Date**: {{timestamp}}
**Context**: {{refactor_name_or_branch}}

---

## Summary

- Total conflicts detected: {{count}}
- Auto-resolved: {{auto_resolved_count}}
- Manual resolution required: {{manual_count}}

---

## Conflict Details

| doc_id | Old Path              | New Path Candidate      | Conflict Type     | Resolution |
|--------|-----------------------|-------------------------|-------------------|------------|
| {{}}   | {{}}                  | {{}}                    | path_collision    | {{}}       |
| {{}}   | {{}}                  | {{}}                    | divergent_metadata| {{}}       |

---

## Follow-Up Actions

1. {{action_1}}
2. {{action_2}}
```

---

## 5. Module Reflection & Refactor Plan Templates

To tie IDs into the module-centric architecture, you want:

1. A **module map template** (module → doc list)
2. A **refactor plan template** (per-doc_id move plan)

### 5.1 Module doc map template

`TEMPLATE_MODULE_DOC_MAP.yaml`:

```yaml
metadata:
  generated_at: "{{timestamp}}"
  source_registry: "DOC_ID_REGISTRY.yaml"
  source_inventory: "docs_inventory.jsonl"

modules:
  {{module_id}}:
    description: {{human_description}}
    docs:
      - doc_id: {{DOC_ID}}
        category: {{category}}
        kind: {{artifact_kind}}      # source | test | doc | schema | config | script
        path: {{relative_path}}
```

### 5.2 Refactor plan template (JSONL)

`TEMPLATE_DOC_ID_REFACTOR_PLAN.jsonl`:

```json
{"op": "move",
 "doc_id": "DOC-CORE-ORCHESTRATOR-001",
 "module_id": "core.engine",
 "from": "core/engine/orchestrator.py",
 "to":   "modules/core.engine/src/orchestrator.py"}
{"op": "move",
 "doc_id": "DOC-TEST-CORE-ORCHESTRATOR-010",
 "module_id": "core.engine",
 "from": "tests/engine/test_orchestrator.py",
 "to":   "modules/core.engine/tests/test_orchestrator.py"}
```

AI can then:

* Generate this file for a given refactor.
* Use it as the **single source of truth** for automated moves.
* Roll back by inverting the same plan.

---

## 6. ID Rollout / Implementation Plan Template

Finally, you want a **project-agnostic rollout template** for new repos or big refactors:

`TEMPLATE_DOC_ID_IMPLEMENTATION_PLAN.md`:

```markdown
# Doc ID Implementation Plan
**Repo**: {{repo_name}}
**Owner**: {{owner}}
**Date**: {{date}}

---

## Goals

- [ ] Achieve {{target_coverage}}% doc_id coverage
- [ ] Integrate preflight gate into CI
- [ ] Enable module-centric refactors using doc_id + module_id

## Phases

### Phase 0 – Scan & Baseline

- [ ] Run PAT-DOC-ID-SCAN-001
- [ ] Generate DOC_ID_COVERAGE_REPORT.md
- [ ] Identify high-priority directories

### Phase 1 – Auto-Assignment

- [ ] Run PAT-DOC-ID-AUTOASSIGN-002 in dry-run
- [ ] Review proposed IDs
- [ ] Apply in batches

### Phase 2 – Enforcement

- [ ] Implement PAT-DOC-ID-PREFLIGHT-003
- [ ] Wire preflight gate into CI
- [ ] Block refactors below {{coverage_threshold}}%

### Phase 3 – Module Mapping

- [ ] Assign module_id for all docs
- [ ] Generate MODULE_DOC_MAP.yaml

### Phase 4 – Refactor Execution

- [ ] Generate refactor plan JSONL
- [ ] Execute moves per module
- [ ] Log conflicts using DOC_ID_CONFLICT_LOG.md
```

---

## TL;DR – Highest-Value Missing Templates

If you only add a handful next:

1. **File-level doc_id header templates** (per language)
2. **`TEMPLATE_DOC_ID_REGISTRY_ENTRY.yaml`** for new registry entries
3. **Pattern doc templates for `PAT-DOC-ID-*` patterns**
4. **Standard report templates**:

   * Coverage
   * Preflight gate
   * Conflict/migration
5. **Module map + refactor plan templates** to bridge IDs → module-centric refactor

Once these exist in the repo, you can tell any AI:

> “Only inject IDs, update the registry, write reports, and plan refactors using these templates.”

…and the whole doc_id framework becomes deterministic instead of vibe-based.
