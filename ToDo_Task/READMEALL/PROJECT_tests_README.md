# Test Suite

**Purpose**: Comprehensive testing infrastructure for core pipeline, error engine, plugins, and integrations.

## Overview

The test suite validates pipeline orchestration, error detection, plugin execution, workstream parsing, and CI enforcement. Tests are organized by domain and run via pytest.

## Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── pipeline/                        # Core pipeline tests
│   ├── test_bundles.py
│   ├── test_fix_loop.py
│   ├── test_orchestrator_single.py
│   ├── test_workstream_authoring.py
│   └── test_openspec_parser_src.py
├── error/                           # Error engine tests
│   ├── test_error_engine.py
│   ├── test_state_machine.py
│   └── test_file_hash_cache.py
├── plugins/                         # Plugin-specific tests
│   ├── test_python_ruff.py
│   ├── test_plugin_manager.py
│   └── ...
├── integration/                     # Cross-system integration tests
│   ├── test_full_workstream_run.py
│   └── test_end_to_end.py
├── orchestrator/                    # Orchestrator tests
│   ├── test_parallel_orchestrator.py
│   └── test_orchestrator_lifecycle.py
├── ast/                            # AST analysis tests
│   └── test_ast_parser.py
├── test_*.py                       # Top-level standalone tests
└── .aicontext                      # AI assistant context for tests
```

## Test Categories

### Pipeline Tests (`tests/pipeline/`)

Core workstream execution and orchestration.

**Key Tests**:
- `test_bundles.py` - Bundle loading and validation
- `test_fix_loop.py` - Error fix escalation loop
- `test_orchestrator_single.py` - Single workstream execution
- `test_workstream_authoring.py` - Workstream creation and editing
- `test_openspec_parser_src.py` - OpenSpec parsing

**Example**:
```python
def test_load_workstream_bundle(temp_db):
    from core.state.bundles import load_workstream_bundle
    
    bundle_path = "workstreams/example_single.json"
    bundle = load_workstream_bundle(bundle_path)
    
    assert bundle["workstream_id"] == "example-single"
    assert len(bundle["steps"]) > 0
```

### Error Engine Tests (`tests/error/`)

Error detection state machine and plugin execution.

**Key Tests**:
- `test_error_engine.py` - End-to-end error pipeline
- `test_state_machine.py` - State transitions
- `test_file_hash_cache.py` - Incremental validation

**Example**:
```python
def test_state_machine_transitions():
    from error.engine.error_state_machine import advance_state
    from error.engine.error_context import ErrorPipelineContext
    
    ctx = ErrorPipelineContext()
    ctx.current_state = "S_INIT"
    
    advance_state(ctx)
    assert ctx.current_state == "S0_BASELINE_CHECK"
```

### Plugin Tests (`tests/plugins/`)

Individual plugin behavior and output parsing.

**Key Tests**:
- `test_plugin_manager.py` - Plugin discovery and DAG ordering
- `test_python_ruff.py` - Ruff plugin execution
- `test_python_mypy.py` - Mypy plugin execution

**Example**:
```python
def test_ruff_plugin_execute(tmp_path):
    from error.plugins.python_ruff.plugin import register
    
    test_file = tmp_path / "test.py"
    test_file.write_text("import os\nimport sys\n")  # Unused imports
    
    plugin = register()
    result = plugin.execute(test_file)
    
    assert result.plugin_id == "python_ruff"
    assert len(result.issues) > 0
```

### Integration Tests (`tests/integration/`)

Cross-system tests validating full workflows.

**Key Tests**:
- `test_full_workstream_run.py` - Complete workstream execution
- `test_end_to_end.py` - Pipeline + error engine + agents

**Example**:
```python
def test_full_workstream_execution(temp_db):
    from scripts.run_workstream import run_workstream
    
    result = run_workstream(
        workstream_id="test-workstream",
        dry_run=True
    )
    
    assert result["status"] == "success"
```

### Orchestrator Tests (`tests/orchestrator/`)

Parallel execution and lifecycle management.

**Key Tests**:
- `test_parallel_orchestrator.py` - Parallel step execution
- `test_orchestrator_lifecycle.py` - Orchestrator startup/shutdown

### CI Enforcement Tests

Tests that enforce repository standards.

**Key Tests**:
- `test_ci_path_standards.py` - Import path validation
- `test_validators.py` - Schema validation
- `test_integration.py` - CI pipeline simulation

**Example**:
```python
def test_no_deprecated_imports():
    """Ensure no code uses deprecated import paths."""
    from pathlib import Path
    import ast
    
    for py_file in Path("core").rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not node.module.startswith("src.pipeline")
                assert not node.module.startswith("MOD_ERROR_PIPELINE")
```

## Running Tests

### All Tests

```bash
# Run entire test suite
pytest

# Verbose output
pytest -v

# Quiet mode
pytest -q
```

### Specific Categories

```bash
# Pipeline tests only
pytest tests/pipeline/ -v

# Error engine tests
pytest tests/error/ -v

# Plugin tests
pytest tests/plugins/ -v

# Integration tests
pytest tests/integration/ -v
```

### Specific Test Files

```bash
# Single test file
pytest tests/test_ci_path_standards.py -v

# Single test function
pytest tests/pipeline/test_bundles.py::test_load_workstream_bundle -v
```

### Markers

```bash
# Run only AIM tests (requires AIM registry)
pytest -m aim

# Run only Aider tests (requires Aider/Ollama)
pytest -m aider

# Skip AIM tests
pytest -m "not aim"
```

### Coverage

```bash
# Generate coverage report
pytest --cov=core --cov=error --cov=specifications

# HTML coverage report
pytest --cov=core --cov=error --cov-report=html
```

## Configuration

### pytest.ini

```ini
[pytest]
minversion = 7.0
addopts = -ra
testpaths = tests
pythonpath = .
norecursedirs = sandbox_repos .git .venv venv build dist
asyncio_mode = auto
markers =
    aim: tests requiring AIM registry/tools; skipped if unavailable
    aider: tests invoking aider or Ollama; skipped if unavailable
```

### conftest.py

Global fixtures available to all tests:

**`temp_db` fixture**:
```python
@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    os.environ['PIPELINE_DB_PATH'] = db_path
    
    from core.state.db import init_db
    init_db(db_path)
    
    yield db_path
    
    try:
        os.unlink(db_path)
    except Exception:
        pass
```

**`worker_pool` fixture**:
```python
@pytest.fixture(scope="function")
def worker_pool(temp_db):
    """Create a worker pool with temp database."""
    from core.engine.worker import WorkerPool
    return WorkerPool(max_workers=4)
```

## Test Organization

### Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Fixtures: Descriptive names without `test_` prefix

### Directory Mapping

| Test Directory | Source Code |
|----------------|-------------|
| `tests/pipeline/` | `core/state/`, `core/planning/` |
| `tests/error/` | `error/engine/` |
| `tests/plugins/` | `error/plugins/` |
| `tests/orchestrator/` | `core/engine/` |
| `tests/integration/` | Cross-system |

### Test Types

1. **Unit Tests**: Single function/class behavior
2. **Integration Tests**: Multiple components working together
3. **End-to-End Tests**: Full pipeline workflows
4. **CI Tests**: Repository standards enforcement

## CI Integration

Tests run automatically on every commit via GitHub Actions.

**Workflow** (`.github/workflows/ci.yml` → `infra/ci/workflows/ci.yml`):
```yaml
- name: Run tests
  run: pytest -v --cov=core --cov=error --cov=specifications
  
- name: Check CI path standards
  run: pytest tests/test_ci_path_standards.py -v
```

**CI Script**:
```bash
# Run via PowerShell script
pwsh ./scripts/test.ps1
```

## Sandbox Repositories

**Location**: `tests/sandbox_repos/`

Self-contained toy repositories for integration testing.

**Features**:
- Excluded from pytest by default (`norecursedirs`)
- Used for end-to-end workflow validation
- Each sandbox has its own `.git`, dependencies, etc.

**Usage**:
```bash
# Run tests that use sandbox repos
pytest tests/integration/ --sandbox-repos
```

## Mock Data

**Location**: `tests/fixtures/`

Example workstreams, bundles, and config files for testing.

```
tests/fixtures/
├── workstreams/
│   ├── example_single.json
│   └── example_multi.json
├── configs/
│   ├── tool_profiles.json
│   └── agent_profiles.json
└── plugins/
    └── test_plugin/
```

## Best Practices

1. **Isolation**: Each test is independent; no shared state
2. **Fixtures**: Use `temp_db`, `tmp_path` for file system operations
3. **Determinism**: Tests produce same results on every run
4. **Fast feedback**: Unit tests run in <1s, integration tests <10s
5. **Clear assertions**: Use descriptive assertion messages
6. **Mock external calls**: No network or external tool dependencies in unit tests

## Troubleshooting

**Issue**: Import errors
- Ensure `pythonpath = .` in `pytest.ini`
- Check `sys.path` includes project root

**Issue**: Database locked
- Use `temp_db` fixture for isolated database
- Clean up temp files in fixture teardown

**Issue**: Tests hang
- Check for infinite loops in orchestrator
- Use `pytest-timeout` plugin: `pytest --timeout=60`

**Issue**: Flaky tests
- Review for race conditions in parallel execution
- Use deterministic seeds for randomness
- Mock time-dependent behavior

## Adding New Tests

1. **Create test file** in appropriate directory
2. **Import fixtures** from `conftest.py`
3. **Write test functions** with descriptive names
4. **Use assertions** with clear messages
5. **Run locally** before committing: `pytest <file> -v`
6. **Check coverage**: `pytest --cov=<module> <file>`

**Template**:
```python
def test_my_feature(temp_db, tmp_path):
    """Test description."""
    # Arrange
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    # Act
    result = my_function(test_file)
    
    # Assert
    assert result == expected_value, "Result should match expected value"
```

## Related Sections

- **Core State**: `core/state/` - Database operations tested in `tests/pipeline/`
- **Error Engine**: `error/engine/` - Error pipeline tested in `tests/error/`
- **Plugins**: `error/plugins/` - Plugin behavior tested in `tests/plugins/`
- **CI**: `infra/ci/` - CI workflows

## See Also

- [pytest.ini](../pytest.ini)
- [conftest.py](./conftest.py)
- [CI Path Standards](../docs/CI_PATH_STANDARDS.md)
- [Testing Guide](../docs/testing_guide.md)
