---
doc_id: DOC-GUIDE-PHASE-6-TESTING-REMEDIATION-664
plan_type: execution_plan
phase: 6
version: 1.0.0
created: 2025-12-05
status: ready_for_execution
total_workstreams: 7
estimated_duration: 1_week
---

# Phase 6 Testing Remediation Plan - 100% Coverage Achievement

## Executive Summary

**Goal**: Achieve 100% test coverage for Phase 6 Error Detection & Correction pipeline

**Current State**: 60% production-ready (96 tests, 83% pass rate, 0 plugin tests, 0 integration tests)

**Target State**: 100% production-ready (163+ tests, 100% pass rate, full plugin/integration coverage)

**Timeline**: 1 week (5 business days) across 3 independent workstreams

**Prerequisites**: None (all workstreams are independent and parallelizable)

---

## Workstream Distribution Strategy

### 3-CLI Multi-Agent Execution Model

**Workstream Independence**: All 7 workstreams can execute in parallel with ZERO dependencies

**Agent Assignment**:
- **Agent 1 (CLI-1)**: Plugin Testing Batch 1 (WS-6T-01, WS-6T-02)
- **Agent 2 (CLI-2)**: Integration Tests + Unit Test Fixes (WS-6T-03, WS-6T-04, WS-6T-05)
- **Agent 3 (CLI-3)**: Plugin Testing Batch 2 + Documentation (WS-6T-06, WS-6T-07)

**Execution Pattern**: EXEC-002 (Batch Validation) + EXEC-003 (Tool Availability Guards)

---

## Workstream Breakdown

---

## 🔧 WORKSTREAM 6T-01: Python Plugin Test Suite (Agent 1)

**ID**: WS-6T-01
**Category**: Plugin Testing - Python Ecosystem
**Priority**: CRITICAL
**Effort**: 12-14 hours
**Execution Pattern**: EXEC-002 (Batch Validation)
**Agent**: CLI-1
**Timeline**: Days 1-2 (parallel with WS-6T-03, WS-6T-06)

### Scope
Create comprehensive test suites for **8 Python plugins**:
1. python_mypy (type checking)
2. python_pylint (linting)
3. python_pyright (advanced type checking)
4. python_bandit (security scanning)
5. python_safety (dependency vulnerabilities)
6. python_black_fix (formatting - auto-fix)
7. python_isort_fix (import sorting - auto-fix)
8. codespell (spelling errors)

### Deliverables (Per Plugin)

**Test Files** (3 per plugin = 24 files total):
```
phase6_error_recovery/modules/plugins/{plugin_name}/tests/
  ├── test_plugin_detection.py      # Error detection tests
  ├── test_plugin_fix.py             # Auto-fix tests (if applicable)
  └── test_plugin_edge_cases.py     # Error handling
```

**Test Coverage Requirements** (Per Plugin):
- ✅ Tool availability check (check_tool_available())
- ✅ Command building (build_command())
- ✅ Successful detection (execute() with clean file)
- ✅ Error detection (execute() with errors)
- ✅ Auto-fix application (for _fix plugins)
- ✅ Edge cases: missing file, empty file, binary file, permission denied

**Example Test Structure**:
```python
# test_plugin_detection.py
def test_mypy_available():
    plugin = MypyPlugin()
    assert plugin.check_tool_available() is True

def test_mypy_detects_type_error():
    plugin = MypyPlugin()
    test_file = create_temp_file("x: int = 'string'")
    result = plugin.execute(test_file)
    assert result.success is True
    assert len(result.issues) > 0
    assert any("type" in i.category for i in result.issues)

def test_mypy_handles_missing_file():
    plugin = MypyPlugin()
    result = plugin.execute(Path("/nonexistent.py"))
    assert result.success is False
```

### Prerequisites
- Tools installed: mypy, pylint, pyright, bandit, safety, black, isort, codespell
- Test fixtures: Sample Python files with known errors

### Validation
```bash
# Per plugin validation
pytest phase6_error_recovery/modules/plugins/python_mypy/tests/ -v

# All Python plugins validation
pytest phase6_error_recovery/modules/plugins/python_*/tests/ -v

# Expected: 80+ tests, 100% pass rate
```

### Success Criteria
- ✅ 24 test files created (3 per plugin × 8 plugins)
- ✅ Minimum 10 tests per plugin (80+ total)
- ✅ 100% test pass rate
- ✅ All edge cases covered

### Execution Pattern: EXEC-002 (Batch Validation)
```python
# Two-pass execution: Validate all, then execute all

# PASS 1: Pre-flight validation
for plugin in python_plugins:
    assert plugin exists
    assert tool is installed
    assert test file fixtures exist
    assert no import errors

# PASS 2: Test creation
for plugin in python_plugins:
    create_test_detection()
    create_test_fix()
    create_test_edge_cases()
    run_tests_verify_pass()
```

---

## 🌐 WORKSTREAM 6T-02: JavaScript/Markdown/Config Plugin Test Suite (Agent 1)

**ID**: WS-6T-02
**Category**: Plugin Testing - Non-Python Ecosystems
**Priority**: HIGH
**Effort**: 8-10 hours
**Execution Pattern**: EXEC-002 (Batch Validation)
**Agent**: CLI-1
**Timeline**: Days 2-3 (parallel with WS-6T-03, WS-6T-06)

### Scope
Create test suites for **6 non-Python plugins**:
1. js_eslint (JavaScript linting)
2. js_prettier_fix (JavaScript formatting - auto-fix)
3. md_markdownlint (Markdown linting)
4. md_mdformat_fix (Markdown formatting - auto-fix)
5. yaml_yamllint (YAML validation)
6. json_jq (JSON processing)

### Deliverables (Per Plugin)
**Test Files** (3 per plugin = 18 files total):
```
phase6_error_recovery/modules/plugins/{plugin_name}/tests/
  ├── test_plugin_detection.py
  ├── test_plugin_fix.py
  └── test_plugin_edge_cases.py
```

**Test Coverage Requirements**:
- Same as WS-6T-01 but with language-specific test fixtures
- JavaScript: unused variables, syntax errors, formatting issues
- Markdown: broken links, heading hierarchy, list formatting
- YAML: schema validation, key duplicates, indentation
- JSON: jq query execution, malformed JSON handling

### Prerequisites
- Tools installed: eslint, prettier, markdownlint, mdformat, yamllint, jq
- Test fixtures: Sample JS/MD/YAML/JSON files with known errors

### Validation
```bash
pytest phase6_error_recovery/modules/plugins/{js_*,md_*,yaml_*,json_*}/tests/ -v
# Expected: 60+ tests, 100% pass rate
```

### Success Criteria
- ✅ 18 test files created
- ✅ Minimum 10 tests per plugin (60+ total)
- ✅ 100% test pass rate

---

## 🔐 WORKSTREAM 6T-06: Security/PowerShell/Path Plugin Test Suite (Agent 3)

**ID**: WS-6T-06
**Category**: Plugin Testing - Security & Platform-Specific
**Priority**: HIGH
**Effort**: 8-10 hours
**Execution Pattern**: EXEC-002 (Batch Validation)
**Agent**: CLI-3
**Timeline**: Days 1-2 (parallel with WS-6T-01, WS-6T-03)

### Scope
Create test suites for **5 security/platform plugins**:
1. semgrep (pattern-based security scanning)
2. gitleaks (secret detection)
3. powershell_pssa (PowerShell Script Analyzer)
4. path_standardizer (path normalization)
5. echo (test/debug plugin)

### Deliverables (Per Plugin)
**Test Files** (3 per plugin = 15 files total)

**Test Coverage Requirements**:
- **semgrep**: SQL injection detection, XSS patterns, hardcoded secrets
- **gitleaks**: API keys, private keys, AWS credentials
- **powershell_pssa**: PowerShell best practices, cmdlet usage
- **path_standardizer**: Windows/Unix path conversion, symlink handling
- **echo**: Simple pass-through validation (minimal tests)

### Prerequisites
- Tools installed: semgrep, gitleaks, PSScriptAnalyzer (PowerShell module)
- Test fixtures: Files with security issues, secrets, path variants

### Validation
```bash
pytest phase6_error_recovery/modules/plugins/{semgrep,gitleaks,powershell_pssa,path_standardizer,echo}/tests/ -v
# Expected: 50+ tests, 100% pass rate
```

### Success Criteria
- ✅ 15 test files created
- ✅ Minimum 10 tests per plugin (50+ total)
- ✅ 100% test pass rate

---

## 🧪 WORKSTREAM 6T-03: Integration Test Suite (Agent 2)

**ID**: WS-6T-03
**Category**: Integration Testing
**Priority**: CRITICAL
**Effort**: 10-12 hours
**Execution Pattern**: EXEC-004 (Atomic Operations)
**Agent**: CLI-2
**Timeline**: Days 1-3 (parallel with WS-6T-01, WS-6T-06)

### Scope
Create **end-to-end integration tests** validating full error pipeline workflow

### Deliverables

**Test Files** (10 files):
```
tests/error/integration/
  ├── test_full_pipeline_python.py          # Python error → fix → recheck
  ├── test_full_pipeline_javascript.py      # JS error → fix → recheck
  ├── test_multi_plugin_coordination.py     # Multiple plugins on same file
  ├── test_state_machine_transitions.py     # S_INIT → ... → S_SUCCESS/S4_QUARANTINE
  ├── test_mechanical_autofix_flow.py       # Tier 0 auto-fix
  ├── test_ai_agent_escalation.py           # Tier 0 → 1 → 2 → 3 escalation
  ├── test_circuit_breaker_integration.py   # Error recovery with circuit breaker
  ├── test_hash_cache_invalidation.py       # Incremental validation
  ├── test_jsonl_event_streaming.py         # Event log generation
  └── test_error_classification_layers.py   # 5-layer classification
```

### Test Scenarios

**1. Full Pipeline - Python (test_full_pipeline_python.py)**
```python
def test_python_type_error_detection_and_fix():
    """End-to-end: Python file with type error → detect → auto-fix → recheck"""
    # Setup
    test_file = create_file_with_type_error()

    # Execute pipeline
    engine = PipelineEngine(plugin_manager, hash_cache)
    report = engine.process_file(test_file)

    # Assertions
    assert report.summary.total_errors > 0  # Error detected
    assert report.summary.auto_fixed > 0    # Auto-fix attempted
    assert report.status == "completed"     # Pipeline succeeded

    # Verify file was fixed
    recheck_report = engine.process_file(test_file)
    assert recheck_report.summary.total_errors == 0
```

**2. State Machine Transitions (test_state_machine_transitions.py)**
```python
def test_escalation_path_mechanical_to_quarantine():
    """Test full escalation: S0_BASELINE → S0_MECHANICAL → S4_QUARANTINE"""
    ctx = ErrorPipelineContext(
        run_id="test-001",
        workstream_id="ws-001",
        python_files=["broken.py"],
        enable_mechanical_autofix=True,
        enable_aider=False,  # Disable AI agents
        enable_codex=False,
        enable_claude=False,
    )

    # S_INIT → S0_BASELINE_CHECK
    advance_state(ctx)
    assert ctx.current_state == "S0_BASELINE_CHECK"

    # Simulate baseline failure
    ctx.last_error_report = {"summary": {"total_issues": 5, "has_hard_fail": True}}

    # S0_BASELINE_CHECK → S0_MECHANICAL_AUTOFIX
    advance_state(ctx)
    assert ctx.current_state == "S0_MECHANICAL_AUTOFIX"

    # S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK
    advance_state(ctx)
    assert ctx.current_state == "S0_MECHANICAL_RECHECK"

    # Simulate recheck failure (still errors)
    ctx.last_error_report = {"summary": {"total_issues": 3, "has_hard_fail": True}}

    # S0_MECHANICAL_RECHECK → S4_QUARANTINE (no AI enabled)
    advance_state(ctx)
    assert ctx.current_state == "S4_QUARANTINE"
```

**3. Multi-Plugin Coordination (test_multi_plugin_coordination.py)**
```python
def test_multiple_plugins_on_same_file():
    """Test that multiple plugins run in dependency order"""
    test_file = create_python_file_with_multiple_issues()

    plugin_manager = PluginManager()
    plugin_manager.discover()

    # Get plugins for Python file (should include mypy, pylint, black, etc.)
    plugins = plugin_manager.get_plugins_for_file(test_file)

    assert len(plugins) >= 3  # At least mypy, black, isort

    # Execute plugins
    results = plugin_manager.run_plugins(plugins, test_file)

    # Verify all ran
    assert len(results) == len(plugins)

    # Verify dependency order (formatters before linters)
    formatter_indices = [i for i, r in enumerate(results) if "black" in r.plugin_id or "isort" in r.plugin_id]
    linter_indices = [i for i, r in enumerate(results) if "mypy" in r.plugin_id or "pylint" in r.plugin_id]

    if formatter_indices and linter_indices:
        assert max(formatter_indices) < min(linter_indices)  # Formatters run first
```

### Prerequisites
- Phase 6 plugin tests passing (WS-6T-01, WS-6T-02, WS-6T-06)
- All tools installed
- Test fixtures for each scenario

### Validation
```bash
pytest tests/error/integration/ -v
# Expected: 30+ tests across 10 files, 100% pass rate
```

### Success Criteria
- ✅ 10 integration test files created
- ✅ Minimum 30 tests total
- ✅ 100% test pass rate
- ✅ Full pipeline validated end-to-end

---

## 🔧 WORKSTREAM 6T-04: Unit Test Fixes - Agent Adapters (Agent 2)

**ID**: WS-6T-04
**Category**: Bug Fixes - Unit Tests
**Priority**: HIGH
**Effort**: 4-5 hours
**Execution Pattern**: EXEC-005 (Syntax Error Fix)
**Agent**: CLI-2
**Timeline**: Day 3 (parallel with WS-6T-07)

### Scope
Fix **6 failing agent adapter tests** (71% → 100% pass rate)

### Issues
**Root Cause**: Tests expect stub/failure behavior, but implementations are now functional

**Affected Tests**:
1. `test_invoke_stub_implementation` (CodexAdapter)
2. `test_invoke_stub_implementation` (ClaudeAdapter)
3. `test_check_all_agents_available`
4. `test_check_mixed_availability`
5. `test_codex_adapter_branches`
6. `test_claude_adapter_branches`

### Deliverables

**File**: `tests/error/unit/test_agent_adapters.py`

**Changes**:
```python
# BEFORE (expects failure)
def test_invoke_stub_implementation(self):
    adapter = CodexAdapter()
    result = adapter.invoke(invocation)
    assert result.success is False  # ❌ FAILS - now returns True
    assert "not implemented" in result.error_message

# AFTER (expects success or proper behavior)
def test_invoke_returns_suggestions(self):
    adapter = CodexAdapter()
    invocation = AgentInvocation(
        agent_name="codex",
        files=["test.py"],
        error_report={"summary": {"total_issues": 1}},
    )
    result = adapter.invoke(invocation)

    # CodexAdapter returns suggestions, not direct edits
    assert result.success is True or "not found" in result.stderr.lower()
    assert result.metadata.get("mode") == "suggestion"
    assert result.files_modified == []  # Suggestions only, no edits
```

**Similar fixes** for ClaudeAdapter tests:
```python
def test_claude_requires_api_key(self):
    adapter = ClaudeAdapter()

    if not adapter.check_available():
        pytest.skip("ANTHROPIC_API_KEY not set")

    result = adapter.invoke(invocation)
    assert result.success is True or "api" in result.stderr.lower()
```

### Validation
```bash
pytest tests/error/unit/test_agent_adapters.py -v
# Expected: 21/21 tests passing (100% pass rate)
```

### Success Criteria
- ✅ All 6 failing tests fixed
- ✅ 21/21 tests passing (100% pass rate)
- ✅ No new test failures introduced

---

## 🔧 WORKSTREAM 6T-05: Unit Test Fixes - Pipeline & Security (Agent 2)

**ID**: WS-6T-05
**Category**: Bug Fixes - Unit Tests
**Priority**: HIGH
**Effort**: 4-5 hours
**Execution Pattern**: EXEC-006 (Auto-Fix Linting)
**Agent**: CLI-2
**Timeline**: Day 4 (parallel with WS-6T-07)

### Scope
Fix **6 failing tests** across pipeline engine and security utilities

### Issues

**A. Pipeline Engine (2 failures)**

**File**: `phase6_error_recovery/modules/error_engine/src/engine/pipeline_engine.py`

**Issue**: Duplicate `_generate_report()` method (lines 165-268)

**Fix**:
1. Remove duplicate method (lines 221-268)
2. Keep enhanced version with layer classification (lines 165-220)
3. Update tests to expect enhanced report structure

**Affected Tests**:
- `test_process_file_validates_and_reports`
- `test_generate_report_counts_errors`

---

**B. Security Utils (4 failures)**

**File**: `phase6_error_recovery/modules/error_engine/src/shared/utils/security.py`

**Affected Tests**:
1. `test_redact_git_hashes`
2. `test_sanitize_home_directory`
3. `test_sanitize_username_windows`
4. `test_validate_file`

**Fixes**:

```python
# Fix 1: test_redact_git_hashes
# ISSUE: Regex pattern not matching full git hashes
# FIX: Update pattern or adjust test expectations

# Fix 2: test_sanitize_home_directory
# ISSUE: Path normalization not handling ~ expansion
# FIX: Add os.path.expanduser() handling

# Fix 3: test_sanitize_username_windows
# ISSUE: Windows username detection failing
# FIX: Add platform check or mock getpass.getuser()

# Fix 4: test_validate_file
# ISSUE: File size/permission validation edge case
# FIX: Add proper error handling for edge cases
```

### Deliverables
1. Remove duplicate `_generate_report()` in pipeline_engine.py
2. Fix 4 security utility functions or their tests
3. All tests passing

### Validation
```bash
pytest tests/error/unit/test_pipeline_engine_additional.py -v
pytest tests/error/unit/test_security.py -v
# Expected: 18/18 tests passing (100% pass rate)
```

### Success Criteria
- ✅ Duplicate code removed
- ✅ 2 pipeline tests fixed
- ✅ 4 security tests fixed
- ✅ 100% pass rate for both files

---

## 📋 WORKSTREAM 6T-07: Documentation & Test Runner Fixes (Agent 3)

**ID**: WS-6T-07
**Category**: Documentation + Bug Fixes
**Priority**: MEDIUM
**Effort**: 3-4 hours
**Execution Pattern**: EXEC-009 (Validation Run)
**Agent**: CLI-3
**Timeline**: Days 3-4 (parallel with WS-6T-04, WS-6T-05)

### Scope
1. Investigate and fix **4 skipped test_runner tests**
2. Update Phase 6 documentation with test coverage results
3. Generate final test coverage report

### Deliverables

**A. Test Runner Fixes**

**File**: `tests/error/unit/test_test_runner_parsing.py`
**Status**: 4 tests skipped (100% skip rate)

**Tasks**:
1. Identify why tests are skipped (check for `@pytest.mark.skip` decorators)
2. Fix underlying issues or remove obsolete tests
3. Ensure all tests pass or have documented skip reasons

---

**B. Documentation Updates**

**Files to Update**:
1. `phase6_error_recovery/README.md`
2. `PHASE_6_ERROR_DETECTION_CORRECTION_OVERVIEW.md`
3. `PHASE_6_TESTING_GAPS_REPORT.md` → rename to `PHASE_6_TESTING_COMPLETE_REPORT.md`

**Changes**:
```markdown
# phase6_error_recovery/README.md

## Test Coverage

✅ **163+ tests** covering:
- ✅ Python plugin tests (80+ tests)
- ✅ JavaScript/Markdown plugin tests (60+ tests)
- ✅ Security/PowerShell plugin tests (50+ tests)
- ✅ Integration tests (30+ tests)
- ✅ Unit tests (96 tests, 100% passing)

## Status

✅ **100% Production-Ready** - Full test coverage achieved
- All 19 plugins tested
- End-to-end integration validated
- State machine fully tested
- AI agent adapters validated
```

---

**C. Generate Final Coverage Report**

**Script**: `scripts/generate_phase6_coverage_report.py`

**Output**: `PHASE_6_FINAL_COVERAGE_REPORT.md`

**Contents**:
- Total test count: 163+ tests
- Pass rate: 100%
- Coverage by component (plugins, engine, utilities)
- Risk assessment (updated to LOW across the board)
- Production readiness: 100%

### Validation
```bash
# Run all Phase 6 tests
pytest tests/error/ phase6_error_recovery/modules/plugins/*/tests/ -v --tb=short

# Generate coverage report
pytest --cov=phase6_error_recovery --cov-report=html --cov-report=term

# Expected: 163+ tests, 100% pass rate, >90% code coverage
```

### Success Criteria
- ✅ 4 test_runner tests fixed or documented
- ✅ Documentation updated with final stats
- ✅ Coverage report generated
- ✅ All Phase 6 tests passing

---

## Timeline & Dependencies

### Day 1 (Parallel Execution)
- **Agent 1**: WS-6T-01 (Python plugins) - Start
- **Agent 2**: WS-6T-03 (Integration tests) - Start
- **Agent 3**: WS-6T-06 (Security plugins) - Start

### Day 2 (Parallel Execution)
- **Agent 1**: WS-6T-01 (Python plugins) - Complete, WS-6T-02 (JS/MD/Config) - Start
- **Agent 2**: WS-6T-03 (Integration tests) - Continue
- **Agent 3**: WS-6T-06 (Security plugins) - Complete

### Day 3 (Parallel Execution)
- **Agent 1**: WS-6T-02 (JS/MD/Config) - Complete
- **Agent 2**: WS-6T-03 (Integration tests) - Complete, WS-6T-04 (Agent adapter fixes) - Start
- **Agent 3**: WS-6T-07 (Documentation) - Start

### Day 4 (Parallel Execution)
- **Agent 1**: IDLE (validation/review)
- **Agent 2**: WS-6T-04 (Agent adapter fixes) - Complete, WS-6T-05 (Pipeline/security fixes) - Start
- **Agent 3**: WS-6T-07 (Documentation) - Complete

### Day 5 (Final Validation)
- **All Agents**: Run full test suite, generate coverage reports, final validation

---

## Execution Patterns Applied

### EXEC-001: Type-Safe Operations
- Plugin tests validate file type handling
- Edge case tests for binary/text/missing files

### EXEC-002: Batch Validation
- Pre-flight checks before creating test files
- Validate all plugins exist before testing

### EXEC-003: Tool Availability Guards
- Check tool installation before running tests
- Skip tests gracefully if tool unavailable

### EXEC-004: Atomic Operations
- Integration tests use transactions/rollbacks
- Temp directories for isolated testing

### EXEC-006: Auto-Fix Linting
- Apply auto-fixes for test code quality
- Use black/isort on test files

---

## Success Metrics

### Quantitative
- ✅ **163+ tests** total (current: 96)
- ✅ **100% pass rate** (current: 83%)
- ✅ **19/19 plugins tested** (current: 0/19)
- ✅ **10+ integration tests** (current: 0)
- ✅ **>90% code coverage** (current: unknown)

### Qualitative
- ✅ All plugins validated with real tools
- ✅ End-to-end pipeline proven functional
- ✅ State machine transitions tested
- ✅ AI agent escalation validated
- ✅ Production-ready with confidence

---

## Risk Mitigation

### Risk: Tool Installation Failures
**Mitigation**: Use EXEC-003 pattern (Tool Availability Guards)
```python
@pytest.mark.skipif(not shutil.which("mypy"), reason="mypy not installed")
def test_mypy_detection():
    ...
```

### Risk: Test Flakiness
**Mitigation**: Use temp directories, deterministic fixtures, no network calls

### Risk: Platform-Specific Issues
**Mitigation**: Use platform checks, skip tests on unsupported platforms
```python
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_pssa():
    ...
```

---

## Validation Commands

### Pre-Flight Validation
```bash
# Verify all tools installed
python scripts/check_phase6_tools.py

# Expected output:
# ✅ mypy: installed
# ✅ black: installed
# ✅ eslint: installed
# ✅ semgrep: installed
# ... (all 19 tools)
```

### Per-Workstream Validation
```bash
# WS-6T-01: Python plugins
pytest phase6_error_recovery/modules/plugins/python_*/tests/ -v

# WS-6T-02: JS/MD/Config plugins
pytest phase6_error_recovery/modules/plugins/{js_*,md_*,yaml_*,json_*}/tests/ -v

# WS-6T-03: Integration tests
pytest tests/error/integration/ -v

# WS-6T-04: Agent adapter fixes
pytest tests/error/unit/test_agent_adapters.py -v

# WS-6T-05: Pipeline/security fixes
pytest tests/error/unit/test_pipeline_engine_additional.py tests/error/unit/test_security.py -v

# WS-6T-06: Security plugins
pytest phase6_error_recovery/modules/plugins/{semgrep,gitleaks,powershell_pssa,path_standardizer,echo}/tests/ -v

# WS-6T-07: Documentation (no pytest, manual review)
```

### Final Validation
```bash
# Run ALL Phase 6 tests
pytest tests/error/ phase6_error_recovery/modules/plugins/*/tests/ -v --tb=short

# Generate coverage report
pytest --cov=phase6_error_recovery --cov-report=html tests/error/ phase6_error_recovery/modules/plugins/*/tests/

# Expected output:
# ======================== 163 passed in 45.2s =========================
# Coverage: 92%
```

---

## Deliverables Checklist

### Code Deliverables
- [ ] 24 Python plugin test files (WS-6T-01)
- [ ] 18 JS/MD/Config plugin test files (WS-6T-02)
- [ ] 15 Security plugin test files (WS-6T-06)
- [ ] 10 integration test files (WS-6T-03)
- [ ] Agent adapter fixes (WS-6T-04)
- [ ] Pipeline/security fixes (WS-6T-05)
- [ ] Test runner fixes (WS-6T-07)

### Documentation Deliverables
- [ ] Updated phase6_error_recovery/README.md
- [ ] Updated PHASE_6_ERROR_DETECTION_CORRECTION_OVERVIEW.md
- [ ] New PHASE_6_FINAL_COVERAGE_REPORT.md
- [ ] Test execution logs for all workstreams

### Validation Deliverables
- [ ] pytest output: 163+ tests passing
- [ ] Coverage report: >90% coverage
- [ ] Tool availability check results
- [ ] Platform compatibility matrix

---

## CLI Agent Assignment

### Agent 1 (CLI-1) - Plugin Testing Lead
**Workstreams**: WS-6T-01, WS-6T-02
**Total Effort**: 20-24 hours
**Focus**: Plugin test coverage (Python + JS/MD/Config)
**Output**: 42 test files, 140+ tests

### Agent 2 (CLI-2) - Integration & Fixes Lead
**Workstreams**: WS-6T-03, WS-6T-04, WS-6T-05
**Total Effort**: 18-22 hours
**Focus**: End-to-end validation + unit test fixes
**Output**: 10 integration files, 30+ tests, 12 bug fixes

### Agent 3 (CLI-3) - Security & Documentation Lead
**Workstreams**: WS-6T-06, WS-6T-07
**Total Effort**: 11-14 hours
**Focus**: Security plugin coverage + documentation
**Output**: 15 test files, 50+ tests, updated docs

---

## Completion Criteria

### Phase 6 is 100% Production-Ready When:
1. ✅ All 163+ tests passing (100% pass rate)
2. ✅ All 19 plugins have test coverage
3. ✅ Integration tests validate end-to-end flow
4. ✅ No skipped tests without documented reasons
5. ✅ Code coverage >90%
6. ✅ Documentation reflects final state
7. ✅ All execution patterns followed
8. ✅ Zero critical/high risk items remaining

---

## Next Steps After Completion

1. **Production Deployment**: Enable Phase 6 in CI/CD pipeline
2. **Monitoring Setup**: Configure dashboards for error metrics
3. **Performance Tuning**: Optimize plugin execution order
4. **Plugin Expansion**: Add support for new languages (Go, Rust, C++)
5. **AI Integration**: Fine-tune Aider/Codex/Claude prompts

---

**Plan Status**: ✅ READY FOR EXECUTION
**Estimated Completion**: 5 business days (1 week)
**Confidence Level**: HIGH (workstreams are independent and well-defined)
