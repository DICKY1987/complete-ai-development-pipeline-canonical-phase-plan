# Validation Scripts

This directory contains validation scripts for verifying compliance with the orchestration specification requirements.

## Overview

Each validator checks specific requirement IDs (STATE-OBS-*, TASK-DEF-*, etc.) and provides:
- **PASS/FAIL** status per requirement
- **Specific violations** with file:line references
- **Suggested fixes** for common issues
- **Exit code 0** for pass, non-zero for fail

## Available Validators

### validate_state_obs.ps1
Validates **State Observability Requirements** (STATE-OBS-001 through STATE-OBS-006):
- State snapshot file existence and validity
- Transition log format and completeness
- Atomicity guarantees (no abandoned .tmp files)
- Event schema compliance
- Index file generation

**Usage**:
```powershell
./validate_state_obs.ps1 -StateDir .state
./validate_state_obs.ps1 -StateDir .state -VerboseOutput
```

### validate_task_defs.ps1
Validates **Task Definition Requirements** (TASK-DEF-001 through TASK-DEF-002):
- Task file naming conventions
- Directory structure (tasks/{workstream_id}/{task_id}.json)
- Task schema compliance
- Required fields presence
- Schema version compatibility

**Usage**:
```powershell
./validate_task_defs.ps1 -TasksDir tasks
./validate_task_defs.ps1 -TasksDir tasks -SchemaVersion "2.0.0"
```

### validate_dag_structure.ps1
Validates **DAG and Execution Plan Requirements** (DAG-VIEW-001 through DAG-VIEW-003):
- DAG file structure and schema
- Execution plan format
- Dependency cycle detection
- Critical path information
- v2.0.0 enhancements (parallelism, estimates)

**Usage**:
```powershell
./validate_dag_structure.ps1 -StateDir .state
./validate_dag_structure.ps1 -StateDir .state -VerboseOutput
```

### validate_failure_modes.ps1
Validates **Failure Mode Documentation** (ERR-FM-001 through ERR-FM-003):
- Failure mode documentation completeness
- Required sections (Detection, Probability, Impact, etc.)
- Failure mode catalog existence
- Recovery decision trees

**Usage**:
```powershell
./validate_failure_modes.ps1 -DocsDir docs/failure_modes
./validate_failure_modes.ps1 -DocsDir docs/failure_modes -VerboseOutput
```

### validate_compliance.ps1 (Master Validator)
Runs **all validators** and provides comprehensive compliance report:
- Executes all individual validators
- Validates documentation structure
- Validates capability registry
- Provides overall compliance statistics

**Usage**:
```powershell
./validate_compliance.ps1
./validate_compliance.ps1 -StateDir .state -TasksDir tasks -VerboseOutput
```

## Exit Codes

All validators follow this convention:
- **0**: All checks passed
- **1**: One or more checks failed

This makes them suitable for CI/CD pipelines:
```bash
# In CI pipeline
./scripts/validate/validate_compliance.ps1
if [ $? -ne 0 ]; then
    echo "Compliance validation failed"
    exit 1
fi
```

## Output Format

Validators produce color-coded output:
- **[✓]** Green: Requirement passed
- **[✗]** Red: Requirement failed
- **Warning**: Yellow: Non-critical issues

Example output:
```
=== Validating State Observability Requirements ===
State Directory: .state

STATE-OBS-001: State Snapshot Requirements
[✓] STATE-OBS-001 : State snapshot file exists and is queryable

STATE-OBS-002: Transition Log Requirements
[✓] STATE-OBS-002 : Transition log is append-only and valid JSONL

=== Validation Summary ===
PASSED: 6
FAILED: 0

✓ Validation PASSED. All state observability requirements met.
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Validate Orchestration Compliance
  run: |
    pwsh -File scripts/validate/validate_compliance.ps1
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
pwsh -File scripts/validate/validate_compliance.ps1 || exit 1
```

### Make Target

```makefile
.PHONY: validate
validate:
	pwsh -File scripts/validate/validate_compliance.ps1

.PHONY: validate-verbose
validate-verbose:
	pwsh -File scripts/validate/validate_compliance.ps1 -VerboseOutput
```

## Requirements

- **PowerShell Core 7.0+** (pwsh)
- Read access to state, tasks, and docs directories

Install PowerShell:
```bash
# Ubuntu/Debian
sudo apt-get install -y powershell

# macOS
brew install powershell

# Windows
# PowerShell is pre-installed
```

## Troubleshooting

### "Validator not found" error
Ensure you're running from repository root:
```bash
cd /path/to/repository
pwsh -File scripts/validate/validate_compliance.ps1
```

### Permission denied
Make scripts executable:
```bash
chmod +x scripts/validate/*.ps1
```

### PowerShell not installed
Install PowerShell Core (see Requirements section above).

### False positives
Use `-VerboseOutput` to see detailed validation logic:
```powershell
./validate_state_obs.ps1 -VerboseOutput
```

## Development

### Adding New Validators

1. Create new validator script: `validate_{component}.ps1`
2. Follow existing structure:
   - Accept parameters for directories
   - Use `Write-Result` for consistent output
   - Return exit code 0 for pass, 1 for fail
3. Add to `validate_compliance.ps1` master validator
4. Update this README

### Testing Validators

```powershell
# Test individual validator
./validate_state_obs.ps1 -StateDir .state -VerboseOutput

# Test with non-existent directory (should fail)
./validate_state_obs.ps1 -StateDir /nonexistent

# Test master validator
./validate_compliance.ps1 -VerboseOutput
```

## See Also

- [Orchestration Specification](../../specifications/content/orchestration/spec.md)
- [State Observability Requirements](../../specifications/content/orchestration/spec.md#state-observability)
- [Compliance Validation Requirements](../../specifications/content/orchestration/spec.md#compliance-validation)
