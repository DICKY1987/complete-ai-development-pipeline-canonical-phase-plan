# Decision Examples

**Purpose**: Sample decision records illustrating expected structure.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `example_decision.yaml` | Example decision record |

---

## Usage

Use as a template when creating new decision records:

```bash
# Copy example
cp example_decision.yaml ../DEC-XXX-my-decision.yaml

# Edit for your decision
```

---

## Example Structure

```yaml
id: DEC-001
title: "Example Decision Title"
status: accepted
date: 2025-11-27
context: |
  Describe the context and forces at play.
  What is motivating this decision?
decision: |
  The decision that was made.
  Be specific and actionable.
consequences: |
  What becomes easier or harder?
  What are the trade-offs?
```

---

## Related

- `../decision_template.yaml` - Base template
- `../../docs/` - Supporting documentation
