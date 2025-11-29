# Verification Directory

**Purpose**: Ground-truth templates and examples for validating pattern outputs.

**Status**: Active

---

## Contents

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `examples/` | Sample verification artifacts |

### Key Files

| File | Description |
|------|-------------|
| `ground_truth_template.yaml` | Baseline structure for verification documents |
| `README.yaml` | Machine-readable directory metadata |

---

## Ground Truth Verification

Ground truth verification ensures pattern outputs match expected results:

1. **Define expected outputs** in verification documents
2. **Execute pattern** to generate actual outputs
3. **Compare** actual vs expected
4. **Report** differences

---

## Usage

### Create Verification Document

```bash
# Copy template
cp ground_truth_template.yaml my_pattern_verification.yaml

# Edit expected outputs
```

### Template Structure

```yaml
pattern_id: PAT-XXX-001
expected_outputs:
  - file: output/file.txt
    checksum: sha256:abc123...
    content_checks:
      - contains: "expected text"
      - matches_regex: "pattern.*"
verification_steps:
  - description: Step description
    expected_result: What should happen
```

### Run Verification

```powershell
# Use pattern CLI
..\scripts\pattern_cli.ps1 -Action validate -PatternId PAT-XXX-001 -VerificationFile my_pattern_verification.yaml
```

---

## Examples

See `examples/` for sample verification artifacts demonstrating:

- File content verification
- Structure validation
- Checksum comparison
- Regex matching

---

## Related

- `../specs/` - Pattern specifications (define verification requirements)
- `../tests/` - Executor tests
- `../executors/` - Executor implementations
