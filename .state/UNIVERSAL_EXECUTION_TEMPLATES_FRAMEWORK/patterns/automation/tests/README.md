---
doc_id: DOC-TEST-README-165
---

# Automation Tests

**Purpose**: Test suites for automation modules.

**Status**: Active

---

## Contents

| Script | Description |
|--------|-------------|
| `demo_pattern_detection.ps1` | Demonstration of pattern detection |
| `test_activation.ps1` | Tests for automation activation |

---

## Usage

```powershell
# Run activation tests
.\test_activation.ps1

# Run pattern detection demo
.\demo_pattern_detection.ps1
```

---

## Test Coverage

- Pattern detection accuracy
- Automation activation
- Integration with orchestrator hooks

---

## Related

- `../detectors/` - Pattern detectors under test
- `../integration/` - Orchestrator hooks
- `../../tests/` - Executor tests
