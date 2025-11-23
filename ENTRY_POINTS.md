# Entry Points - Complete AI Development Pipeline

**Purpose**: Map tasks → commands → code entry points

**For AI Tools**: Use this to suggest correct commands and trace code paths.

---

## Quick Reference Table

| Task | Command | Entry File | Key Function |
|------|---------|------------|--------------|
| Run workstream | `python -m core.orchestrator run --plan <file>` | `core/orchestrator.py` | `Orchestrator.run_plan()` |
| Validate workstream | `python -m core.orchestrator validate --plan <file>` | `core/orchestrator.py` | `Orchestrator.validate_plan()` |
| Detect errors | `python -m error.engine --scan <dir>` | `error/engine/error_engine.py` | `ErrorEngine.scan()` |
| Generate spec | `python scripts/spec_generate.py --template <type>` | `specifications/tools/generator.py` | `generate_spec()` |
| Bootstrap project | `python scripts/bootstrap_uet.py .` | `scripts/bootstrap_uet.py` | `main()` |
| Validate imports | `python scripts/paths_index_cli.py gate` | `scripts/paths_index_cli.py` | `gate_command()` |
| Run tests | `pytest tests/` | N/A | pytest |
| Run tests with coverage | `pytest --cov=core --cov=error` | N/A | pytest |

---

## Detailed Entry Points

### 1. Workstream Orchestration

**Command**:
```bash
python -m core.orchestrator run --plan workstreams/example.json
```

**Code Path**:
```
core/orchestrator.py:main()
  ├─ Orchestrator.__init__()
  │   └─ core.state.db:init_db()
  ├─ Orchestrator.run_plan(plan_path)
  │   ├─ core.state.bundle_loader:load_workstream_bundle()
  │   ├─ core.state.crud:create_run()
  │   ├─ core.engine.scheduler:Scheduler.schedule()
  │   └─ core.engine.executor:Executor.execute_step()
  └─ Result logged to .worktrees/<run_id>/pipeline.db
```

**Key Functions**:
- `Orchestrator.run_plan(plan_path: str) -> RunResult`
- `Scheduler.schedule(workstreams: List[Workstream]) -> Schedule`
- `Executor.execute_step(step: Step) -> StepResult`

**State Location**:
- Database: `.worktrees/<run_id>/pipeline.db`
- Logs: `.runs/<run_id>/execution.log`

**Exit Codes**:
- `0` - Success
- `1` - Validation error
- `2` - Execution error
- `3` - State error

---

### 2. Workstream Validation

**Command**:
```bash
python -m core.orchestrator validate --plan workstreams/example.json
```

**Code Path**:
```
core/orchestrator.py:main()
  └─ Orchestrator.validate_plan(plan_path)
      ├─ core.state.bundle_loader:load_workstream_bundle()
      ├─ Validate against schema/workstream_schema.json
      ├─ core.state.dag_utils:validate_dag()
      └─ Return validation result
```

**Key Functions**:
- `Orchestrator.validate_plan(plan_path: str) -> bool`
- `bundle_loader.load_workstream_bundle()` - JSON validation
- `dag_utils.validate_dag()` - Cycle detection

**Use Case**: Dry-run validation before execution

---

### 3. Error Detection

**Command**:
```bash
python -m error.engine --scan path/to/code
```

**Code Path**:
```
error/engine/error_engine.py:main()
  ├─ ErrorEngine.__init__()
  ├─ ErrorEngine.scan(scan_path)
  │   ├─ Load plugins from error/plugins/
  │   ├─ For each plugin: plugin.parse(file)
  │   └─ Collect errors
  └─ ErrorEngine.report()
```

**Key Functions**:
- `ErrorEngine.scan(path: str) -> List[Error]`
- `Plugin.parse(file_path: str) -> List[Error]`
- `ErrorEngine.report(format: str) -> str`

**Available Plugins**:
- `error/plugins/python_ruff/` - Python linting via Ruff
- `error/plugins/import_validator/` - Import path validation

**Output Formats**:
- `--format=json` - Machine-readable JSON
- `--format=text` - Human-readable text
- `--format=github` - GitHub Actions annotations

---

### 4. Specification Generation

**Command**:
```bash
python scripts/spec_generate.py --template workstream --output my_spec.json
```

**Code Path**:
```
scripts/spec_generate.py:main()
  └─ specifications/tools/generator.py:generate_spec()
      ├─ Load template from specifications/templates/<type>.json
      ├─ Populate with user input
      ├─ Validate against schema/workstream_schema.json
      └─ Write to output path
```

**Key Functions**:
- `generate_spec(template: str, output: str) -> None`
- `validate_spec(spec: dict, schema: dict) -> bool`

**Available Templates**:
- `workstream` - Workstream bundle
- `phase` - Phase specification
- `plugin` - Error detection plugin

---

### 5. Project Bootstrap (UET)

**Command**:
```bash
python scripts/bootstrap_uet.py .
```

**Code Path**:
```
scripts/bootstrap_uet.py:main()
  ├─ Detect project type (inspect files)
  ├─ Generate PROJECT_PROFILE.yaml
  ├─ Generate router_config.json
  └─ Create directory structure
```

**Generated Files**:
- `PROJECT_PROFILE.yaml` - Project metadata, constraints
- `router_config.json` - Tool routing configuration

**Detection Logic**:
- Checks for `pyproject.toml`, `package.json`, etc.
- Infers project type, language, tools
- Auto-configures based on detected environment

---

### 6. Import Path Validation (CI Gate)

**Command**:
```bash
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

**Code Path**:
```
scripts/paths_index_cli.py:gate_command()
  ├─ Load deprecated paths from refactor_paths.db
  ├─ Scan codebase for import statements
  ├─ Flag deprecated path usage
  └─ Exit 1 if violations found (CI fails)
```

**Purpose**: Prevent deprecated import paths from merging

**Deprecated Patterns Detected**:
- `src.pipeline.*`
- `MOD_ERROR_PIPELINE.*`
- `legacy.*`

**Used In**: `.github/workflows/path_standards.yml`

---

## Python API Entry Points

### Core Orchestrator

```python
from core.orchestrator import Orchestrator

# Initialize with database path
orch = Orchestrator(db_path=".worktrees/run-001/pipeline.db")

# Run a workstream plan
result = orch.run_plan("workstreams/example.json")

# Validate a plan (dry run)
is_valid = orch.validate_plan("workstreams/example.json")
```

**Key Methods**:
- `__init__(db_path: str = None)` - Initialize orchestrator
- `run_plan(plan_path: str) -> RunResult` - Execute workstream
- `validate_plan(plan_path: str) -> bool` - Validate without executing

---

### State Management

```python
from core.state import crud, db

# Initialize database
db.init_db(db_path=".worktrees/run-001/pipeline.db")

# Create entities
run_id = crud.create_run(plan_name="example", plan_data={})
ws_id = crud.create_workstream(run_id, ws_data)
step_id = crud.create_step(ws_id, step_data)

# Query state
workstream = crud.get_workstream(ws_id)
steps = crud.get_steps_by_workstream(ws_id)
errors = crud.get_errors_by_step(step_id)

# Update state
crud.update_step_status(step_id, "completed")
crud.log_event(run_id, "execution_started", {})
```

**Key Modules**:
- `core.state.db` - Database initialization, connection
- `core.state.crud` - CRUD operations for all entities
- `core.state.bundle_loader` - Workstream JSON loading
- `core.state.dag_utils` - DAG validation, topological sort

---

### Error Detection

```python
from error.engine.error_engine import ErrorEngine

# Initialize engine
engine = ErrorEngine()

# Scan for errors
errors = engine.scan("path/to/code")

# Filter errors
python_errors = [e for e in errors if e.language == "python"]

# Generate report
report = engine.report(format="json")
print(report)
```

**Key Classes**:
- `ErrorEngine` - Main error detection orchestrator
- `Plugin` - Base class for detection plugins
- `Error` - Error data structure

---

### Specification Tools

```python
from specifications.tools.generator import generate_spec
from specifications.tools.validator import validate_spec

# Generate from template
generate_spec(
    template="workstream",
    output="my_workstream.json",
    params={"name": "My Workstream"}
)

# Validate spec
is_valid = validate_spec(
    spec_path="my_workstream.json",
    schema_path="schema/workstream_schema.json"
)
```

---

## Testing Entry Points

### Run All Tests

```bash
pytest tests/
```

### Run Specific Module

```bash
pytest tests/core/
pytest tests/error/
pytest tests/specifications/
```

### Run With Coverage

```bash
pytest --cov=core --cov=error --cov=specifications --cov-report=html
```

**Coverage Report**: `htmlcov/index.html`

---

### Test Entry Point Details

**Test Discovery**: 
- pytest auto-discovers `test_*.py` files
- Tests use fixtures from `tests/conftest.py`
- Database fixtures in `tests/fixtures/test_db_setup.py`

**Running Specific Tests**:
```bash
# By test name pattern
pytest -k "test_orchestrator"

# By marker
pytest -m "integration"

# Specific test file and function
pytest tests/core/test_orchestrator.py::test_run_plan
```

---

## GUI Entry Points (Future)

**Planned**:
```bash
python -m gui.main
```

**Status**: In development  
**Tracking**: `devdocs/phases/phase-h/`

---

## Script Entry Points

### Common Scripts

```bash
# Validate workstreams
python scripts/validate_workstreams.py

# Check ACS conformance
python scripts/validate_acs_conformance.py

# Generate codebase index
python scripts/generate_codebase_index.py

# Spec to workstream converter
python scripts/spec_to_workstream.py --proposal openspec/changes/PROP-001/
```

**All Scripts**: See [scripts/README.md](scripts/README.md)

---

## For AI Tools

### Finding Entry Points

**By task**: Use quick reference table at top  
**By module**: Check module's `.ai-module-manifest` (when available)  
**By code**: Search for `if __name__ == "__main__":`

### Common Patterns

- **CLI tools**: `python -m <module>` (uses `__main__.py`)
- **Scripts**: `python scripts/<script>.py`
- **Python API**: Import and call directly

### Entry Point Conventions

- **Orchestrator**: Single entry via `Orchestrator.run_plan()`
- **Plugins**: Auto-discovered from `<module>/plugins/`
- **State**: All operations via `core.state.crud` functions
- **Tools**: Scripts in `scripts/` directory

### Suggesting Commands

When user asks "how do I...":
1. Check quick reference table
2. Provide exact command
3. Show expected output
4. Link to relevant docs

**Example**:
```
User: "How do I run a workstream?"

AI Response:
"Use the orchestrator:

```bash
python -m core.orchestrator run --plan workstreams/your_workstream.json
```

This will:
1. Load and validate the workstream
2. Create a run in .worktrees/<run_id>/
3. Execute steps according to dependencies
4. Log results to the database

See: QUICK_START.md for more details."
```

---

## Exit Codes Reference

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | All steps completed |
| 1 | Validation error | Invalid JSON schema |
| 2 | Execution error | Step failed |
| 3 | State error | Database corruption |
| 10 | Deprecated path detected | CI gate failure |

---

## Common Execution Patterns

### Sequential Execution

```bash
# Validate first
python -m core.orchestrator validate --plan my_plan.json

# If valid, execute
python -m core.orchestrator run --plan my_plan.json
```

### Error Detection + Fix

```bash
# Detect errors
python -m error.engine --scan src/ --format=json > errors.json

# Review errors, fix code

# Re-scan to verify
python -m error.engine --scan src/
```

### Bootstrap → Validate → Execute

```bash
# Bootstrap project
python scripts/bootstrap_uet.py .

# Generate workstream
python scripts/spec_generate.py --template workstream --output plan.json

# Validate
python -m core.orchestrator validate --plan plan.json

# Execute
python -m core.orchestrator run --plan plan.json
```

---

## Environment Variables

### Core Orchestrator
- `PIPELINE_DB_PATH` - Override default database location
- `PIPELINE_LOG_LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)
- `PIPELINE_DRY_RUN` - If set, validate only without executing

### Error Engine
- `ERROR_ENGINE_PLUGINS_PATH` - Custom plugin directory
- `ERROR_ENGINE_CONFIG` - Path to error engine config

### Testing
- `PYTEST_CURRENT_TEST` - Set by pytest during test execution
- `TEST_DB_PATH` - Test database location

---

## Related Documentation

- **[API_INDEX.md](API_INDEX.md)** - All APIs and interfaces
- **[EXECUTION_INDEX.md](EXECUTION_INDEX.md)** - Execution flow details
- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[.ai-context.md](.ai-context.md)** - Quick orientation

---

**Last Updated**: 2025-11-23  
**Status**: Complete (WS-004)  
**Next**: See [NAVIGATION.md](NAVIGATION.md) for navigation patterns
