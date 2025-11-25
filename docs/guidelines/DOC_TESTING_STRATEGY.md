# Testing Strategy Guide

**Purpose:** Define testing patterns for each component to ensure quality and prevent regressions.

**Last Updated:** 2025-11-22  
**Maintainer:** System Architecture Team

---

## Overview

This guide provides **section-specific testing patterns**, mock/fixture guidance, and test data management strategies.

---

## Section-Specific Testing Patterns

### Core State (`core/state/`)

**What to Test:**
- Database CRUD operations
- State machine transitions
- Migration execution
- Transaction handling

**Testing Pattern:**
```python
# tests/core/test_db.py
import pytest
from core.state.db import init_db, get_connection
from core.state.workstreams import create_workstream, get_workstream

@pytest.fixture
def in_memory_db():
    """Use in-memory SQLite for fast, isolated tests."""
    conn = init_db(":memory:")
    yield conn
    conn.close()

def test_create_workstream(in_memory_db):
    # Arrange
    ws_data = {"ws_id": "WS-001", "name": "Test", "state": "S_PENDING"}
    
    # Act
    create_workstream(in_memory_db, ws_data)
    result = get_workstream(in_memory_db, "WS-001")
    
    # Assert
    assert result["ws_id"] == "WS-001"
    assert result["state"] == "S_PENDING"
```

**Key Principles:**
- ✅ Use in-memory DB (`:memory:`) for speed
- ✅ Test state transitions independently
- ✅ Verify migration idempotency
- ❌ Don't test SQLite itself (trust the library)

---

### Core Engine (`core/engine/`)

**What to Test:**
- Orchestration logic
- Step dependency resolution
- Tool adapter invocation
- Circuit breaker behavior

**Testing Pattern:**
```python
# tests/core/test_orchestrator.py
from unittest.mock import Mock, patch
from core.engine.orchestrator import Orchestrator

def test_execute_workstream_success(in_memory_db):
    # Mock tool adapter to avoid subprocess calls
    with patch('core.engine.tools.execute_tool') as mock_tool:
        mock_tool.return_value = {"status": "success", "exit_code": 0}
        
        orchestrator = Orchestrator(in_memory_db)
        workstream = {
            "ws_id": "WS-TEST",
            "steps": [
                {"step_id": "s1", "tool_profile_id": "echo"}
            ]
        }
        
        result = orchestrator.execute_workstream(workstream)
        
        assert result.status == "success"
        assert mock_tool.call_count == 1
```

**Key Principles:**
- ✅ Mock external tool calls (avoid subprocess)
- ✅ Test dependency resolution logic
- ✅ Verify retry/circuit breaker states
- ❌ Don't make real subprocess calls

---

### Error Engine (`error/engine/`, `error/plugins/`)

**What to Test:**
- Plugin discovery
- Error parsing
- File hash caching
- Parallel execution

**Testing Pattern:**
```python
# tests/error/plugins/test_python_ruff.py
from error.plugins.python_ruff.plugin import parse

def test_parse_errors():
    # Arrange
    file_path = "test.py"
    content = "import os\nimport sys  # unused import"
    
    # Act
    errors = parse(file_path, content)
    
    # Assert
    assert len(errors) > 0
    assert any("unused" in e.message.lower() for e in errors)
    assert all(e.file_path == file_path for e in errors)
```

**Plugin Test Template:**
```python
@pytest.fixture
def sample_python_file(tmp_path):
    """Create temporary Python file with known errors."""
    file = tmp_path / "sample.py"
    file.write_text("import os\nprint x  # NameError")
    return str(file)

def test_plugin_parse(sample_python_file):
    errors = parse(sample_python_file, file.read_text())
    assert len(errors) == 1  # NameError detected
```

**Key Principles:**
- ✅ Use `tmp_path` fixture for temporary files
- ✅ Test against real tool output (run actual linter)
- ✅ Verify error location (line, column)
- ❌ Don't test the linter itself (e.g., ruff's correctness)

---

### Specifications (`specifications/tools/`)

**What to Test:**
- URI parsing
- Spec resolution
- Cross-reference validation
- Index generation

**Testing Pattern:**
```python
# tests/specifications/test_resolver.py
from specifications.tools.resolver import resolve_uri

@pytest.fixture
def mock_spec_content(tmp_path):
    spec_dir = tmp_path / "specifications" / "content" / "core" / "state"
    spec_dir.mkdir(parents=True)
    spec_file = spec_dir / "db.md"
    spec_file.write_text("""
# Database Module

## Initialization

Details here.
""")
    return tmp_path

def test_resolve_spec_uri(mock_spec_content, monkeypatch):
    monkeypatch.chdir(mock_spec_content)
    
    resolved = resolve_uri("spec://core/state/db#initialization")
    
    assert resolved.uri == "spec://core/state/db#initialization"
    assert "Initialization" in resolved.content
    assert resolved.line_number > 0
```

**Key Principles:**
- ✅ Use `tmp_path` for spec file fixtures
- ✅ Test URI parsing edge cases
- ✅ Verify cache behavior
- ❌ Don't test markdown rendering itself

---

## Mock & Fixture Library

### Common Fixtures

```python
# conftest.py (shared across all tests)
import pytest
from core.state.db import init_db

@pytest.fixture
def in_memory_db():
    """In-memory SQLite database."""
    conn = init_db(":memory:")
    yield conn
    conn.close()

@pytest.fixture
def sample_workstream():
    """Sample workstream for testing."""
    return {
        "ws_id": "WS-TEST",
        "name": "Test Workstream",
        "steps": [
            {"step_id": "s1", "name": "Setup", "tool_profile_id": "echo"},
            {"step_id": "s2", "name": "Test", "tool_profile_id": "pytest", "depends_on": ["s1"]}
        ]
    }

@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run to avoid actual process execution."""
    from unittest.mock import Mock
    mock = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr("subprocess.run", mock)
    return mock
```

### Mocking Patterns

**Mock Subprocess Calls:**
```python
from unittest.mock import patch, Mock

def test_tool_execution():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="Success")
        # Test code that calls subprocess
```

**Mock File System:**
```python
def test_file_operations(tmp_path):
    # tmp_path is a pytest fixture for temporary directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    # Test code that reads/writes files
```

**Mock Time/Datetime:**
```python
from unittest.mock import patch
import datetime

def test_time_dependent():
    fixed_time = datetime.datetime(2025, 11, 22, 12, 0, 0)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        # Test code that depends on current time
```

---

## Test Data Management

### Small Test Data (Inline)

```python
def test_parse_config():
    config = {"key": "value", "nested": {"item": 42}}
    result = parse_config(config)
    assert result.key == "value"
```

### Medium Test Data (Fixtures)

```python
@pytest.fixture
def sample_spec():
    return {
        "spec_id": "core-state-db",
        "title": "Database Module",
        "content": "..."
    }
```

### Large Test Data (Files)

```
tests/
├── data/
│   ├── sample_workstream.json
│   ├── sample_spec.md
│   └── error_output.txt
└── conftest.py
```

```python
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "data"

def test_parse_workstream(test_data_dir):
    workstream_file = test_data_dir / "sample_workstream.json"
    workstream = json.loads(workstream_file.read_text())
    # Test parsing logic
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── core/
│   ├── test_db.py          # Database tests
│   ├── test_orchestrator.py
│   └── test_state_machine.py
├── error/
│   ├── test_engine.py
│   └── plugins/
│       ├── test_python_ruff.py
│       └── test_python_mypy.py
├── specifications/
│   ├── test_resolver.py
│   └── test_indexer.py
└── data/                    # Test data files
    ├── workstreams/
    └── specs/
```

### Test Naming Convention

```python
# Pattern: test_<function>_<scenario>_<expected>

def test_create_workstream_valid_input_success():
    """Test creating workstream with valid input succeeds."""
    pass

def test_create_workstream_missing_id_raises_error():
    """Test creating workstream without ID raises ValueError."""
    pass

def test_transition_workstream_invalid_state_raises_error():
    """Test invalid state transition raises InvalidTransition."""
    pass
```

---

## Running Tests

### All Tests

```bash
pytest
```

### Specific Section

```bash
pytest tests/core/
pytest tests/error/plugins/
```

### With Coverage

```bash
pytest --cov=core --cov=error --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Verbose Output

```bash
pytest -v  # Show test names
pytest -vv  # Very verbose with diffs
```

### Failed Tests Only

```bash
pytest --lf  # Re-run last failed
pytest --ff  # Failed first, then others
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## Coverage Goals

| Section | Target Coverage | Current | Status |
|---------|----------------|---------|--------|
| `core/state/` | 90% | TBD | ⏳ |
| `core/engine/` | 85% | TBD | ⏳ |
| `error/engine/` | 80% | TBD | ⏳ |
| `error/plugins/` | 70% (per plugin) | TBD | ⏳ |
| `specifications/tools/` | 75% | TBD | ⏳ |

**Note:** Don't aim for 100% coverage. Focus on critical paths and edge cases.

---

## Related Documentation

- [Anti-Patterns: Testing](ANTI_PATTERNS.md#testing-anti-patterns) - Common testing mistakes
- [Change Impact Matrix](CHANGE_IMPACT_MATRIX.md#testing) - When to update tests
- [ADR-0005: Python Primary Language](adr/0005-python-primary-language.md) - Why pytest

---

**Last Updated:** 2025-11-22  
**Next Review:** When new sections are added or testing patterns change
