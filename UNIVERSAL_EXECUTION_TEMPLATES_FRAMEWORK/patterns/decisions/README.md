---
doc_id: DOC-PAT-README-788
---

# Decisions Directory

**Purpose**: Decision records and templates for pattern-related choices.

**Status**: Active

---

## Contents

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `examples/` | Sample decision records illustrating expected structure |

### Key Files

- `decision_template.yaml` - Standardized template for documenting decisions
- `README.yaml` - Machine-readable directory metadata

---

## Usage

1. Copy `decision_template.yaml` to create a new decision record
2. Fill in all required fields (context, decision, consequences)
3. File alongside examples in the `examples/` subdirectory

---

## Decision Record Template

```yaml
# Copy decision_template.yaml and fill in:
id: DEC-XXX
title: "Decision Title"
status: proposed | accepted | deprecated | superseded
context: "What is the issue that we're seeing that is motivating this decision?"
decision: "What is the change that we're proposing and/or doing?"
consequences: "What becomes easier or more difficult to do because of this decision?"
```

---

## Related

- `../specs/` - Pattern specifications that may reference decisions
- `../docs/planning/` - Planning documents with architectural decisions
