# Scripts - Automation and Utilities

> **Purpose**: Automation scripts for common operational tasks  
> **Last Updated**: 2025-11-22  
> **Status**: Production

---

## Overview

The `scripts/` directory contains automation scripts for bootstrapping, validation, testing, and maintenance tasks.

## Script Conventions

- **PowerShell first**: Prefer `.ps1` for Windows-first workflows
- **Cross-platform parity**: Provide `.sh` versions where feasible
- **Python for logic**: Use Python for complex cross-platform logic
- **Keep simple**: Complex logic belongs in Python modules, not scripts

## Key Scripts

### Bootstrap & Setup

#### `bootstrap.ps1`
Initialize development environment.

```powershell
pwsh ./scripts/bootstrap.ps1
```

**What it does**:
- Creates necessary directories
- Checks dependencies
- Sets up initial configuration

### Testing

#### `test.ps1`
Run tests in CI-friendly mode.

```powershell
pwsh ./scripts/test.ps1
```

**What it does**:
- Runs pytest with appropriate flags
- Generates test reports
- Returns proper exit codes for CI

### Workstream Operations

#### `validate_workstreams.py`
Validate workstream JSON files against schemas.

```bash
python ./scripts/validate_workstreams.py
```

**What it does**:
- Loads workstream bundles
- Validates against JSON schemas
- Reports errors and warnings

#### `validate_workstreams_authoring.py`
Validate workstream authoring quality.

```bash
python ./scripts/validate_workstreams_authoring.py
```

**What it does**:
- Checks workstream content quality
- Validates step definitions
- Ensures best practices

#### `run_workstream.py`
Execute a workstream.

```bash
python ./scripts/run_workstream.py --ws-id ws-001
```

**Options**:
- `--ws-id` - Workstream ID to run
- `--step` - Specific step to execute
- `--dry-run` - Validate without executing

### Specification Management

#### `generate_spec_index.py`
Generate specification index.

```bash
python ./scripts/generate_spec_index.py
```

**What it does**:
- Scans specification files
- Generates index for quick lookup
- Updates metadata

#### `generate_spec_mapping.py`
Generate specification mapping.

```bash
python ./scripts/generate_spec_mapping.py
```

**What it does**:
- Maps specs to implementations
- Generates cross-reference
- Updates documentation

### Error Pipeline

#### `run_error_engine.py`
Run error detection pipeline.

```bash
python ./scripts/run_error_engine.py
```

**What it does**:
- Executes error detection plugins
- Generates error reports
- Suggests fixes where available

## Engine Validation

#### `validate_engine.py`
Validate engine implementation.

```bash
python ./scripts/validate_engine.py
```

**Coverage**: 7/7 tests for engine architecture

#### `test_state_store.py`
Test state store integration.

```bash
python ./scripts/test_state_store.py
```

**Coverage**: 6/6 tests for state management

## Usage Patterns

### Development Workflow

1. **Initial setup**:
   ```bash
   pwsh ./scripts/bootstrap.ps1
   ```

2. **Before committing**:
   ```bash
   python ./scripts/validate_workstreams.py
   pwsh ./scripts/test.ps1
   ```

3. **Generate indices** (after spec changes):
   ```bash
   python ./scripts/generate_spec_index.py
   python ./scripts/generate_spec_mapping.py
   ```

### CI/CD Integration

Scripts are designed for CI/CD use:
- Proper exit codes (0 = success, non-zero = failure)
- Clear error messages
- Machine-readable output options

## Adding New Scripts

When adding a new script:

1. **Choose the right language**:
   - Simple automation → PowerShell (.ps1)
   - Cross-platform logic → Python (.py)
   - Provide .sh if needed for Linux/WSL

2. **Follow conventions**:
   - Use descriptive names (verb_noun pattern)
   - Add help/usage information
   - Include error handling
   - Return proper exit codes

3. **Document it**:
   - Add to this README
   - Include usage examples
   - Document all options/flags

4. **Test it**:
   - Test on Windows (PowerShell)
   - Test on Linux/WSL if applicable
   - Verify CI integration

## Related Documentation

- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository navigation
- [AGENTS.md](../AGENTS.md) - Coding conventions
- [docs/](../docs/) - Architecture documentation

## Troubleshooting

### Common Issues

**Script not found**:
- Verify you're in repository root
- Check script name and extension

**Permission denied** (Linux/WSL):
```bash
chmod +x ./scripts/script_name.sh
```

**Python module not found**:
```bash
pip install -r requirements.txt
```

**PowerShell execution policy** (Windows):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

**For AI Tools**: MEDIUM priority directory - index when working on automation or running tasks.
