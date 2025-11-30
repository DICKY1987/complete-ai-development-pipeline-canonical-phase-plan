---
doc_id: DOC-GUIDE-README-1408
---

# Glossary Updates (Patch Specifications)

**Purpose**: Store patch specifications for bulk glossary updates

---

## Overview

This directory contains YAML specifications for bulk glossary updates that are applied using the patch-based workflow.

Each patch spec defines:
- Which terms to update
- What fields to change
- New values or additions

---

## Patch Format

```yaml
# updates/add-uet-schemas.yaml

patch_id: "01J4XY9F2X4E1D9RL8G4JB3CDE"
description: "Add UET schema references to all relevant terms"
date: "2025-11-25"
author: "architecture-team"

terms:
  - term_id: TERM-ENGINE-001
    action: update
    field: schema_refs
    value:
      - "schema/uet/execution_request.v1.json"
  
  - term_id: TERM-PATCH-001
    action: update
    field: schema_refs
    value:
      - "schema/uet/patch_artifact.v1.json"
  
  - term_id: TERM-PATCH-003
    action: update
    field: schema_refs
    value:
      - "schema/uet/patch_ledger_entry.v1.json"
```

---

## Usage

### 1. Create Patch Specification

Create a YAML file in this directory:

```bash
cat > updates/my-update.yaml <<EOF
patch_id: "01J..."
description: "Description of changes"
terms:
  - term_id: TERM-XXX-NNN
    action: update
    field: implementation
    value: ["path/to/file.py"]
EOF
```

### 2. Generate Patch

```bash
python ../scripts/update_term.py --spec updates/my-update.yaml --dry-run
```

### 3. Review Generated Patch

Check `updates/my-update.patch` for the generated diff.

### 4. Apply Patch

```bash
python ../scripts/update_term.py --spec updates/my-update.yaml --apply
```

---

## Action Types

| Action | Description | Example |
|--------|-------------|---------|
| `update` | Update existing field | Change definition |
| `add` | Add new field or value | Add schema reference |
| `remove` | Remove field or value | Remove deprecated alias |
| `replace` | Replace entire field | Replace related terms list |

---

## Common Update Patterns

### Add Implementation Paths

```yaml
terms:
  - term_id: TERM-ENGINE-001
    action: update
    field: implementation.files
    value:
      - "core/engine/orchestrator.py"
```

### Add Schema References

```yaml
terms:
  - term_id: TERM-PATCH-001
    action: update
    field: schema_refs
    value:
      - "schema/uet/patch_artifact.v1.json"
```

### Update Related Terms

```yaml
terms:
  - term_id: TERM-ENGINE-001
    action: update
    field: related_terms
    value:
      - term_id: TERM-ENGINE-002
        relationship: uses
      - term_id: TERM-STATE-003
        relationship: depends_on
```

### Add Usage Examples

```yaml
terms:
  - term_id: TERM-ENGINE-001
    action: add
    field: usage_examples
    value:
      - language: python
        code: |
          from core.engine.orchestrator import Orchestrator
          orch = Orchestrator()
          orch.run_workstream(ws_id)
        description: "Basic orchestrator usage"
```

---

## Files in This Directory

After patches are created, you'll see:

```
updates/
├── README.md                    # This file
├── add-uet-schemas.yaml         # Patch specification
├── add-uet-schemas.patch        # Generated patch file
├── add-implementation-paths.yaml
├── add-implementation-paths.patch
└── ...
```

---

## Best Practices

1. **Small patches** - Update 5-10 terms per patch
2. **Clear descriptions** - Explain what and why
3. **Review before apply** - Always use `--dry-run` first
4. **Keep specs** - Don't delete YAML specs (audit trail)
5. **Test after apply** - Run validation after patch

---

## Related

- [../scripts/README.md](../scripts/README.md) - Tooling documentation
- [../docs/DOC_GLOSSARY_GOVERNANCE.md](../docs/DOC_GLOSSARY_GOVERNANCE.md) - Update mechanisms
- [../GLOSSARY_SYSTEM_OVERVIEW.md](../GLOSSARY_SYSTEM_OVERVIEW.md) - System overview

---

**Status**: Ready for use (tool: update_term.py - planned)
