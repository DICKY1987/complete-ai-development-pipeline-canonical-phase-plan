---
doc_id: DOC-GUIDE-PROJECT-AIM-TESTS-README-1574
---

# AIM Tests Module

> **Directory**: `aim/tests/`  
> **Purpose**: Test suite for AIM+ modules  
> **Parent**: `aim/`  
> **Layer**: Testing  
> **Status**: Production

---

## Overview

The `aim/tests/` directory contains comprehensive test coverage for all AIM+ modules. Tests follow pytest conventions and are organized by module structure.

**Key Responsibilities**:
- Unit tests for all AIM components
- Integration tests for multi-component workflows
- Fixture definitions and test utilities
- Test configuration and markers

---

## Directory Structure

```
aim/tests/
├── conftest.py               # Pytest configuration and shared fixtures
├── environment/              # Environment module tests
│   ├── __init__.py
│   ├── test_audit.py         # Audit logging tests
│   ├── test_health.py        # Health monitoring tests
│   ├── test_installer.py     # Tool installer tests
│   ├── test_scanner.py       # Environment scanner tests
│   ├── test_secrets.py       # Secret management tests
│   └── test_version_control.py  # Version control tests
├── registry/                 # Registry module tests
│   ├── __init__.py
│   └── test_config_loader.py # Config loader tests
└── README.md                 # This file
```

---

## Test Organization

### By Module

Tests are organized to mirror the source code structure:

- `aim/registry/` → `aim/tests/registry/`
- `aim/environment/` → `aim/tests/environment/`
- `aim/cli/` → `aim/tests/cli/` (planned)
- `aim/services/` → `aim/tests/services/` (planned)

This makes it easy to locate tests for any given module.

### By Type

Tests are categorized using pytest markers:

- **Unit tests** - Test individual functions/classes in isolation
- **Integration tests** - Test multiple components working together
- **Functional tests** - Test end-to-end workflows

---

## Running Tests

### All AIM Tests

```bash
# Run all AIM tests
pytest aim/tests/ -v

# Run with coverage
pytest aim/tests/ --cov=aim --cov-report=html

# Run in parallel (faster)
pytest aim/tests/ -n auto
```

### Specific Module Tests

```bash
# Registry tests
pytest aim/tests/registry/ -v

# Environment tests
pytest aim/tests/environment/ -v

# Specific test file
pytest aim/tests/environment/test_health.py -v

# Specific test function
pytest aim/tests/environment/test_health.py::test_health_check -v
```

### By Marker

```bash
# Tests requiring AIM registry
pytest aim/tests/ -m aim -v

# Tests requiring external tools (aider, ollama)
pytest aim/tests/ -m aider -v

# Skip slow tests
pytest aim/tests/ -m "not slow" -v
```

---

## Test Configuration (`conftest.py`)

Shared fixtures and configuration for all AIM tests.

**Key Fixtures**:

```python
import pytest

@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary configuration directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def mock_aim_config():
    """Mock AIM configuration."""
    return {
        "metadata": {"version": "1.0", "contract": "AIM_PLUS_V1"},
        "tools": [],
        "capabilities": {},
        "settings": {}
    }

@pytest.fixture
def mock_secrets_manager():
    """Mock secrets manager for testing."""
    # Implementation details
    pass
```

**Markers Defined**:

```python
# In conftest.py or pytest.ini
markers = [
    "aim: Tests requiring AIM registry/tools",
    "aider: Tests invoking aider or Ollama",
    "slow: Tests that take >5 seconds",
    "integration: Integration tests",
    "unit: Unit tests"
]
```

---

## Test Modules

### Registry Tests (`registry/`)

Tests for configuration loading and validation.

**Coverage**:
- Configuration file loading
- Schema validation
- Environment variable expansion
- Error handling for invalid configs

**Key Tests**:
```python
# test_config_loader.py
def test_load_default_config()
def test_load_custom_config()
def test_schema_validation()
def test_env_var_expansion()
def test_missing_config_error()
```

**Running**:
```bash
pytest aim/tests/registry/test_config_loader.py -v
```

---

### Environment Tests (`environment/`)

Tests for environment management components.

#### Audit Tests (`test_audit.py`)

**Coverage**:
- Audit log writing
- Log querying and filtering
- Log export functionality
- Cost tracking

**Key Tests**:
```python
def test_log_invocation()
def test_query_logs_by_tool()
def test_query_logs_by_date()
def test_export_logs()
```

---

#### Health Tests (`test_health.py`)

**Coverage**:
- Health check execution
- Tool detection
- Status aggregation
- Health monitoring

**Key Tests**:
```python
def test_check_health_all()
def test_check_tool_health()
def test_health_status_calculation()
def test_missing_tools_detection()
```

**Example**:
```bash
# Run health tests
pytest aim/tests/environment/test_health.py -v

# Run with AIM marker (requires registry)
pytest aim/tests/environment/test_health.py -m aim -v
```

---

#### Installer Tests (`test_installer.py`)

**Coverage**:
- Tool installation
- Version-specific installation
- Uninstallation
- Update checking

**Key Tests**:
```python
def test_install_tool()
def test_install_specific_version()
def test_uninstall_tool()
def test_check_for_updates()
```

**Note**: May require network access or mock external package managers.

---

#### Scanner Tests (`test_scanner.py`)

**Coverage**:
- Duplicate detection
- Cache scanning
- Cleanup recommendations

**Key Tests**:
```python
def test_scan_duplicates()
def test_scan_caches()
def test_get_cleanup_recommendations()
```

---

#### Secrets Tests (`test_secrets.py`)

**Coverage**:
- Secret storage and retrieval
- Platform-specific backends
- Secret deletion
- Error handling

**Key Tests**:
```python
def test_store_secret()
def test_retrieve_secret()
def test_delete_secret()
def test_list_secrets()
def test_backend_fallback()
```

**Platform Considerations**:
- Tests may use in-memory backend to avoid system keyring
- Windows-specific tests for DPAPI may be skipped on other platforms

---

#### Version Control Tests (`test_version_control.py`)

**Coverage**:
- Version parsing
- Compatibility checking
- Version pinning
- Version constraints

**Key Tests**:
```python
def test_parse_version()
def test_check_compatibility()
def test_pin_version()
def test_get_recommended_version()
```

---

## Writing New Tests

### Test File Template

```python
"""Tests for aim.<module>.<component>"""

import pytest
from aim.<module>.<component> import ComponentClass


class TestComponentClass:
    """Test suite for ComponentClass."""
    
    def test_basic_functionality(self):
        """Test basic functionality works."""
        component = ComponentClass()
        result = component.do_something()
        assert result is not None
    
    def test_error_handling(self):
        """Test error handling."""
        component = ComponentClass()
        with pytest.raises(ValueError):
            component.do_invalid_operation()
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes time."""
        # Long-running test
        pass
```

### Test Naming Conventions

- **Test files**: `test_<module>.py`
- **Test classes**: `TestClassName`
- **Test functions**: `test_<what_it_tests>`

**Examples**:
- `test_health.py::TestHealthMonitor::test_check_health_success`
- `test_secrets.py::test_store_secret_with_invalid_key`

### Using Fixtures

```python
def test_with_temp_config(temp_config_dir):
    """Test using temporary config directory fixture."""
    config_file = temp_config_dir / "config.json"
    config_file.write_text('{"key": "value"}')
    
    # Test logic here
    assert config_file.exists()
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mocked_subprocess():
    """Test with mocked subprocess call."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="success")
        
        # Test logic that calls subprocess.run
        result = some_function_that_uses_subprocess()
        
        assert result == "success"
        mock_run.assert_called_once()
```

---

## Test Markers

### Standard Markers

```python
@pytest.mark.aim          # Requires AIM registry/tools
@pytest.mark.aider        # Requires aider installed
@pytest.mark.slow         # Takes >5 seconds
@pytest.mark.integration  # Integration test
@pytest.mark.unit         # Unit test
```

### Usage Examples

```python
# Skip if AIM not available
@pytest.mark.aim
def test_requires_aim_registry():
    pass

# Skip if aider not installed
@pytest.mark.aider
def test_requires_aider():
    pass

# Mark as slow test
@pytest.mark.slow
def test_long_operation():
    pass
```

### Running by Marker

```bash
# Only AIM tests
pytest -m aim

# Only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Integration tests only
pytest -m integration
```

---

## Coverage Requirements

### Target Coverage

- **Overall**: 80%+ coverage
- **Critical modules**: 90%+ coverage (secrets, health, installer)
- **UI modules**: 60%+ coverage acceptable (CLI)

### Generating Coverage Report

```bash
# Generate HTML coverage report
pytest aim/tests/ --cov=aim --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage by Module

```bash
# Show coverage summary
pytest aim/tests/ --cov=aim --cov-report=term-missing

# Coverage for specific module
pytest aim/tests/environment/ --cov=aim.environment --cov-report=term
```

---

## Continuous Integration

Tests are automatically run on:

- Pull request creation/update
- Merge to main branch
- Scheduled nightly runs

**CI Configuration**: See `.github/workflows/` (if configured)

**Required Checks**:
- All tests must pass
- Coverage must meet minimum threshold
- No security vulnerabilities in dependencies

---

## Best Practices

1. **Isolation**: Each test should be independent and idempotent
2. **Cleanup**: Use fixtures for setup/teardown
3. **Mocking**: Mock external dependencies (network, filesystem)
4. **Assertions**: One logical assertion per test
5. **Documentation**: Add docstrings explaining what is tested
6. **Fast Tests**: Keep tests fast; mark slow ones appropriately

---

## Troubleshooting

### Tests Fail Locally But Pass in CI

**Causes**:
- Platform-specific behavior
- Environment variable differences
- File path differences (Windows vs Unix)

**Solutions**:
- Use `tmp_path` fixture for temporary files
- Use `pathlib.Path` for cross-platform paths
- Mock platform-specific code

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'aim'`

**Solution**:
```bash
# Ensure PYTHONPATH includes repository root
export PYTHONPATH=.
pytest aim/tests/

# Or install in development mode
pip install -e .
pytest aim/tests/
```

### Fixture Not Found

**Problem**: `fixture 'some_fixture' not found`

**Solutions**:
1. Check fixture is defined in `conftest.py`
2. Ensure `conftest.py` is in test directory or parent
3. Check fixture name spelling matches exactly

---

## See Also

- [aim/README.md](../README.md) - Main AIM documentation
- [pytest.ini](../../pytest.ini) - Pytest configuration
- [QUALITY_GATE.yaml](../../QUALITY_GATE.yaml) - Quality requirements
- Pytest documentation: https://docs.pytest.org/
