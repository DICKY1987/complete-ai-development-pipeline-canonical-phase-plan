# Batch Create Examples

**Pattern**: `PAT-BATCH-CREATE`

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
..\..\..\executors\batch_create_executor.ps1 -InputFile instance_minimal.json
```

---

## Related

- `../../specs/batch_create.pattern.yaml` - Pattern specification
- `../../executors/batch_create_executor.ps1` - Executor
- `../../schemas/batch_create.schema.json` - Validation schema
