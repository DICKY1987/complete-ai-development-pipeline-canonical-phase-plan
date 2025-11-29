---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-PLUGIN_TEST_SUITE_SUMMARY-090
---

# Plugin Test Suite Summary

## Overview
Comprehensive test suite for all 19 error pipeline plugins covering unit tests, integration tests, and live tests.

## Test Structure

```
tests/plugins/
├── conftest.py                  # Common fixtures and utilities
├── run_tests.py                 # Test runner script
├── test_python_fix.py          # Python fix plugins (isort, black)
├── test_python_lint.py         # Python lint plugins (ruff, pylint)
├── test_python_type.py         # Python type checkers (mypy, pyright)
├── test_python_security.py     # Python security (bandit, safety)
├── test_powershell_js.py       # PowerShell + JS/TS plugins
├── test_markup_data.py         # YAML, Markdown, JSON plugins
├── test_cross_cutting.py       # Codespell, Semgrep, Gitleaks
└── test_integration.py         # Integration and workflow tests
```

## Test Coverage

### Python Plugins (M1-M2) - 8 plugins
| Plugin | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| python_isort_fix | test_python_fix.py | 6 | ✅ Unit + Live |
| python_black_fix | test_python_fix.py | 7 | ✅ Unit + Live |
| python_ruff | test_python_lint.py | 5 | ✅ Unit + Parsing |
| python_pylint | test_python_lint.py | 4 | ✅ Unit + Parsing |
| python_mypy | test_python_type.py | 4 | ✅ Unit + Parsing |
| python_pyright | test_python_type.py | 4 | ✅ Unit + Parsing |
| python_bandit | test_python_security.py | 4 | ✅ Unit + Parsing |
| python_safety | test_python_security.py | 5 | ✅ Unit + Parsing |

### PowerShell (M3) - 1 plugin
| Plugin | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| powershell_pssa | test_powershell_js.py | 3 | ✅ Unit + Parsing |

### JavaScript/TypeScript (M4) - 2 plugins
| Plugin | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| js_prettier_fix | test_powershell_js.py | 3 | ✅ Unit + Live |
| js_eslint | test_powershell_js.py | 4 | ✅ Unit + Parsing |

### Markup/Data (M5) - 4 plugins
| Plugin | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| yaml_yamllint | test_markup_data.py | 3 | ✅ Unit + Parsing |
| md_mdformat_fix | test_markup_data.py | 3 | ✅ Unit + Live |
| md_markdownlint | test_markup_data.py | 4 | ✅ Unit + Parsing |
| json_jq | test_markup_data.py | 4 | ✅ Unit + Validation |

### Cross-Cutting (M6) - 3 plugins
| Plugin | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| codespell | test_cross_cutting.py | 3 | ✅ Unit + Parsing |
| semgrep | test_cross_cutting.py | 4 | ✅ Unit + Parsing |
| gitleaks | test_cross_cutting.py | 4 | ✅ Unit + Parsing |

### Integration Tests
| Test Area | Test File | Tests | Coverage |
|-----------|-----------|-------|----------|
| Plugin Discovery | test_integration.py | 2 | ⏸️ Pending engine |
| Plugin Ordering | test_integration.py | 4 | ⏸️ Pending engine |
| Mechanical Autofix | test_integration.py | 2 | ⏸️ Pending engine |
| Issue Aggregation | test_integration.py | 2 | ⏸️ Pending engine |
| Non-Destructive | test_integration.py | 2 | ⏸️ Pending engine |
| Security | test_integration.py | 3 | ✅ Unit tests |

## Test Statistics

- **Total Test Files**: 10
- **Total Test Functions**: ~95
- **Total Plugins Covered**: 18 (excluding echo)
- **Unit Tests**: ~70 (mocked subprocess)
- **Live Tests**: ~15 (require tools installed)
- **Integration Tests**: ~10 (pending engine implementation)

## Test Categories

### 1. Unit Tests (Mocked)
- **Purpose**: Test plugin logic without requiring tools installed
- **Method**: Mock `subprocess.run` to return canned output
- **Coverage**: All plugins have unit tests
- **Example**:
  ```python
  with patch("subprocess.run") as mock_run:
      mock_proc = MagicMock()
      mock_proc.returncode = 0
      mock_proc.stdout = sample_json
      mock_run.return_value = mock_proc
      
      result = plugin.execute(test_file)
      assert result.success is True
  ```

### 2. Parser Tests
- **Purpose**: Verify JSON/text output parsing and normalization
- **Coverage**: All lint/check plugins
- **Key Aspects**:
  - Category mapping (syntax, style, type, security)
  - Severity mapping (error, warning, info)
  - Line/column extraction
  - Tool-specific code extraction

### 3. Live Tests
- **Purpose**: Test with actual tools installed
- **Marker**: `@skip_if_tool_missing("tool_name")`
- **Coverage**: Fix plugins and validators
- **Note**: Skipped automatically if tool not installed

### 4. Integration Tests
- **Purpose**: Test plugin discovery, ordering, and workflows
- **Status**: Pending engine/plugin_manager implementation
- **Coverage**: FSM transitions, mechanical autofix, aggregation

## Running Tests

### Run All Tests
```bash
pytest tests/plugins/
```

### Run Specific Plugin Category
```bash
pytest tests/plugins/test_python_fix.py      # Python fix plugins
pytest tests/plugins/test_python_lint.py     # Python lint plugins
pytest tests/plugins/test_cross_cutting.py   # Cross-cutting plugins
```

### Run Only Unit Tests (No Tools Required)
```bash
pytest tests/plugins/ -m "not live"
```

### Run Only Live Tests (Tools Required)
```bash
pytest tests/plugins/ -k "live or execute"
```

### Run with Coverage
```bash
pytest tests/plugins/ --cov=src/plugins --cov-report=html
```

### Verbose Output
```bash
pytest tests/plugins/ -v -s
```

## Test Fixtures (conftest.py)

### Common Fixtures
- `mock_subprocess_success` - Mock successful subprocess
- `mock_subprocess_with_issues` - Mock subprocess with issues (returncode 1)

### Utility Functions
- `tool_available(tool_name)` - Check if tool installed
- `skip_if_tool_missing(tool_name)` - Pytest skip marker
- `create_sample_file(tmp_path, filename, content)` - Create test file
- `assert_plugin_result_valid(result, expected_success)` - Validate PluginResult
- `assert_issue_valid(issue, expected_tool)` - Validate PluginIssue

## Key Test Patterns

### 1. Plugin Attributes
```python
def test_plugin_has_required_attributes(self):
    plugin = PluginClass()
    assert plugin.plugin_id == "expected_id"
    assert plugin.name == "Expected Name"
    assert hasattr(plugin, "check_tool_available")
    assert hasattr(plugin, "build_command")
    assert hasattr(plugin, "execute")
```

### 2. Tool Availability
```python
def test_check_tool_available(self):
    plugin = PluginClass()
    result = plugin.check_tool_available()
    assert result == tool_available("tool_name")
```

### 3. Parsing with Mocks
```python
def test_parse_output(self, tmp_path: Path):
    plugin = PluginClass()
    test_file = create_sample_file(tmp_path, "test.ext", "content")
    
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = SAMPLE_OUTPUT
        mock_run.return_value = mock_proc
        
        result = plugin.execute(test_file)
        
        assert len(result.issues) > 0
        assert result.issues[0].category == "expected"
```

### 4. Success Codes
```python
def test_success_codes(self, tmp_path: Path):
    plugin = PluginClass()
    test_file = create_sample_file(tmp_path, "test.ext", "content")
    
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.stdout = "[]"
        mock_run.return_value = mock_proc
        
        # Test valid codes
        for code in [0, 1]:
            mock_proc.returncode = code
            result = plugin.execute(test_file)
            assert result.success is True
```

## Sample Output Formats

Each test file includes sample outputs for parsing tests:
- `RUFF_SAMPLE_OUTPUT` - Ruff JSON
- `PYLINT_SAMPLE_OUTPUT` - Pylint JSON
- `MYPY_SAMPLE_OUTPUT` - mypy JSONL
- `PYRIGHT_SAMPLE_OUTPUT` - Pyright JSON
- `PSSA_SAMPLE_OUTPUT` - PSScriptAnalyzer JSON
- `ESLINT_SAMPLE_OUTPUT` - ESLint JSON
- `YAMLLINT_SAMPLE_OUTPUT` - yamllint parsable
- `MARKDOWNLINT_SAMPLE_JSON` - markdownlint JSON
- `SEMGREP_SAMPLE_OUTPUT` - Semgrep JSON
- `GITLEAKS_SAMPLE_OUTPUT` - Gitleaks JSON

## Acceptance Criteria Coverage

✅ Plugin structure tests (all plugins)
✅ Tool availability checks (all plugins)
✅ Command building (all plugins)
✅ Output parsing (all lint/check plugins)
✅ Category mapping (syntax, style, type, security)
✅ Severity mapping (error, warning, info)
✅ Success code handling (all plugins)
✅ Exception handling (all plugins)
✅ Timeout enforcement (security plugins)
✅ Environment scrubbing (integration tests)
✅ No shell=True usage (integration tests)
⏸️ Plugin discovery (pending engine)
⏸️ Topological ordering (pending engine)
⏸️ Mechanical autofix (pending engine)
⏸️ Issue aggregation (pending engine)

## Dependencies

### Required for Tests
```bash
pip install pytest pytest-cov
```

### Optional for Live Tests
```bash
# Python tools
pip install black isort ruff pylint mypy pyright bandit safety

# PowerShell
Install-Module -Name PSScriptAnalyzer

# JS/TS tools
npm install -g prettier eslint

# Markup/Data
pip install yamllint mdformat
npm install -g markdownlint-cli

# Cross-cutting
pip install codespell semgrep
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Plugin Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/plugins/ -v --cov=src/plugins
```

## Next Steps

1. ✅ Implement remaining plugins (DONE)
2. ✅ Create comprehensive test suite (DONE)
3. ⏭️ Implement plugin_manager.py
4. ⏭️ Implement pipeline_engine.py
5. ⏭️ Enable integration tests
6. ⏭️ Run full test suite with all tools installed
7. ⏭️ Add coverage reporting
8. ⏭️ Set up CI/CD pipeline

## References

- Test Specifications: `plans/test-specs-plugins.md`
- Plugin Documentation: `src/plugins/README.md`
- Phase 08 Guide: `plans/phase-08-copilot-execution-guide.md`
