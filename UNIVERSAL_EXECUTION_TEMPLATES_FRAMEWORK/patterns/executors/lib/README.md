# Executors Library

**Purpose**: Shared helper modules for pattern executor development.

**Status**: Active

---

## Contents

| Module | Description |
|--------|-------------|
| `error_rules.ps1` | Error handling and reporting utilities |
| `parallel.ps1` | Parallel execution utilities |
| `reporting.ps1` | Output and report generation |
| `templates.ps1` | Template processing utilities |
| `testing.ps1` | Test harness utilities |
| `transactions.ps1` | Transaction management |
| `validation.ps1` | Input/output validation |

---

## Usage

Import modules in your executor:

```powershell
# Import specific module
. $PSScriptRoot\lib\validation.ps1
. $PSScriptRoot\lib\reporting.ps1

# Use library functions
$isValid = Validate-PatternInput -InputFile $inputPath
Write-PatternReport -Result $result
```

---

## Module Details

### validation.ps1
- Schema validation
- Input sanitization
- Type checking

### reporting.ps1
- JSON/YAML output
- Summary generation
- Log formatting

### error_rules.ps1
- Standard error codes
- Error message formatting
- Retry logic

### parallel.ps1
- Parallel task execution
- Job management
- Result aggregation

### transactions.ps1
- Rollback support
- State management
- Checkpoint/restore

### templates.ps1
- Template parsing
- Variable substitution
- File generation

### testing.ps1
- Test assertions
- Mock utilities
- Fixture management

---

## Related

- `../` - Executor implementations using this library
- `../../tests/` - Test suites using testing.ps1
