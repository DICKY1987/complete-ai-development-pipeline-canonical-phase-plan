---
doc_id: DOC-PAT-README-904
---

# Batch Create 001 Examples

**Pattern**: `PAT-BATCH-CREATE-001`

---

## Contents

| File | Description |
|------|-------------|
| `instance_full.json` | Full example with all options |
| `instance_minimal.json` | Minimal required inputs |
| `instance_test.json` | Test case input |

---

## Usage

```powershell
# Execute with example
..\..\..\executors\batch_create_001_executor.ps1 -InputFile instance_minimal.json
```

---

## Related

- `../../specs/batch_create.pattern.yaml` - Pattern specification
- `../../executors/batch_create_001_executor.ps1` - Executor
- `../../schemas/batch_create_001.schema.json` - Validation schema
