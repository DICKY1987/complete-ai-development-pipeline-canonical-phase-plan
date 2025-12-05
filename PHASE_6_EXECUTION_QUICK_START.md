---
doc_id: DOC-GUIDE-PHASE-6-EXECUTION-QUICK-START-665
version: 1.0.0
created: 2025-12-05
---

# Phase 6 Testing Remediation - Quick Start Guide

## 🚀 3-Agent Parallel Execution

**Total Timeline**: 5 days
**Total Workstreams**: 7 (all independent)
**Test Gap**: 96 → 163+ tests (100% coverage)

---

## Agent Assignment

### Agent 1 (CLI-1): Plugin Testing Lead
**Focus**: Python + JS/MD/Config plugins (14 plugins)
**Workstreams**: WS-6T-01, WS-6T-02
**Effort**: 20-24 hours
**Output**: 42 test files, 140+ tests

### Agent 2 (CLI-2): Integration & Fixes Lead
**Focus**: End-to-end tests + unit test fixes
**Workstreams**: WS-6T-03, WS-6T-04, WS-6T-05
**Effort**: 18-22 hours
**Output**: 10 integration files, 30+ tests, 12 bug fixes

### Agent 3 (CLI-3): Security & Documentation Lead
**Focus**: Security plugins (5 plugins) + docs
**Workstreams**: WS-6T-06, WS-6T-07
**Effort**: 11-14 hours
**Output**: 15 test files, 50+ tests, updated docs

---

## Day-by-Day Execution

### Day 1 - Parallel Launch
```bash
# Terminal 1 (Agent 1)
gh copilot "Start WS-6T-01: Create test suites for 8 Python plugins (mypy, pylint, pyright, bandit, safety, black, isort, codespell). Follow EXEC-002 pattern. Create 3 test files per plugin: test_plugin_detection.py, test_plugin_fix.py, test_plugin_edge_cases.py in phase6_error_recovery/modules/plugins/{plugin}/tests/. Minimum 10 tests per plugin."

# Terminal 2 (Agent 2)
gh copilot "Start WS-6T-03: Create integration test suite in tests/error/integration/. Create 10 files: test_full_pipeline_python.py, test_full_pipeline_javascript.py, test_multi_plugin_coordination.py, test_state_machine_transitions.py, test_mechanical_autofix_flow.py, test_ai_agent_escalation.py, test_circuit_breaker_integration.py, test_hash_cache_invalidation.py, test_jsonl_event_streaming.py, test_error_classification_layers.py. Follow EXEC-004 pattern."

# Terminal 3 (Agent 3)
gh copilot "Start WS-6T-06: Create test suites for 5 security/platform plugins (semgrep, gitleaks, powershell_pssa, path_standardizer, echo). Follow EXEC-002 pattern. Create 3 test files per plugin in phase6_error_recovery/modules/plugins/{plugin}/tests/. Minimum 10 tests per plugin."
```

### Day 2 - Continue + Transition
```bash
# Terminal 1 (Agent 1)
# Complete WS-6T-01, start WS-6T-02
gh copilot "Complete WS-6T-01 Python plugin tests. Then start WS-6T-02: Create test suites for 6 non-Python plugins (js_eslint, js_prettier_fix, md_markdownlint, md_mdformat_fix, yaml_yamllint, json_jq). Same pattern: 3 test files per plugin, minimum 10 tests each."

# Terminal 2 (Agent 2)
# Continue WS-6T-03
gh copilot "Continue WS-6T-03 integration tests. Focus on test_multi_plugin_coordination.py and test_state_machine_transitions.py with full end-to-end validation."

# Terminal 3 (Agent 3)
# Complete WS-6T-06
gh copilot "Complete WS-6T-06 security plugin tests. Run validation: pytest phase6_error_recovery/modules/plugins/{semgrep,gitleaks,powershell_pssa,path_standardizer,echo}/tests/ -v"
```

### Day 3 - Integration Complete + Bug Fixes
```bash
# Terminal 1 (Agent 1)
# Complete WS-6T-02
gh copilot "Complete WS-6T-02 JS/MD/Config plugin tests. Run validation: pytest phase6_error_recovery/modules/plugins/{js_*,md_*,yaml_*,json_*}/tests/ -v"

# Terminal 2 (Agent 2)
# Complete WS-6T-03, start WS-6T-04
gh copilot "Complete WS-6T-03 integration tests. Then start WS-6T-04: Fix 6 failing agent adapter tests in tests/error/unit/test_agent_adapters.py. Issue: tests expect stub behavior but implementations are functional. Update tests to match current CodexAdapter/ClaudeAdapter behavior."

# Terminal 3 (Agent 3)
# Start WS-6T-07
gh copilot "Start WS-6T-07: Investigate 4 skipped tests in tests/error/unit/test_test_runner_parsing.py. Fix or document skip reasons. Update phase6_error_recovery/README.md with final test coverage stats."
```

### Day 4 - Final Bug Fixes
```bash
# Terminal 1 (Agent 1)
# IDLE - Review and validation

# Terminal 2 (Agent 2)
# Complete WS-6T-04, start WS-6T-05
gh copilot "Complete WS-6T-04 agent adapter fixes. Then start WS-6T-05: Fix pipeline_engine.py duplicate _generate_report() method (remove lines 221-268, keep enhanced version). Fix 4 failing security tests in test_security.py (git hash redaction, path sanitization, file validation)."

# Terminal 3 (Agent 3)
# Complete WS-6T-07
gh copilot "Complete WS-6T-07 documentation updates. Generate PHASE_6_FINAL_COVERAGE_REPORT.md with final stats: 163+ tests, 100% pass rate, all plugins tested."
```

### Day 5 - Final Validation
```bash
# All Terminals (All Agents)
# Run full test suite
pytest tests/error/ phase6_error_recovery/modules/plugins/*/tests/ -v --tb=short

# Generate coverage report
pytest --cov=phase6_error_recovery --cov-report=html --cov-report=term tests/error/ phase6_error_recovery/modules/plugins/*/tests/

# Expected output:
# ======================== 163 passed in 45.2s =========================
# Coverage: 92%
```

---

## Validation Checkpoints

### After Each Workstream
```bash
# WS-6T-01 validation
pytest phase6_error_recovery/modules/plugins/python_*/tests/ -v
# Expected: 80+ tests passing

# WS-6T-02 validation
pytest phase6_error_recovery/modules/plugins/{js_*,md_*,yaml_*,json_*}/tests/ -v
# Expected: 60+ tests passing

# WS-6T-03 validation
pytest tests/error/integration/ -v
# Expected: 30+ tests passing

# WS-6T-04 validation
pytest tests/error/unit/test_agent_adapters.py -v
# Expected: 21/21 tests passing (was 15/21)

# WS-6T-05 validation
pytest tests/error/unit/test_pipeline_engine_additional.py tests/error/unit/test_security.py -v
# Expected: 18/18 tests passing (was 12/18)

# WS-6T-06 validation
pytest phase6_error_recovery/modules/plugins/{semgrep,gitleaks,powershell_pssa,path_standardizer,echo}/tests/ -v
# Expected: 50+ tests passing

# WS-6T-07 validation
# Manual review of updated documentation
```

---

## Pre-Flight Checklist

### Before Starting
- [ ] All tools installed (mypy, black, eslint, semgrep, etc.)
- [ ] Phase 6 code base is clean (no uncommitted changes)
- [ ] pytest is working (`pytest tests/error/ -v`)
- [ ] 3 CLI terminals available for parallel execution

### Tool Installation Check
```bash
# Create script to verify all tools
cat > scripts/check_phase6_tools.py << 'EOF'
import shutil
tools = [
    'mypy', 'pylint', 'pyright', 'bandit', 'safety', 'black', 'isort', 'codespell',
    'eslint', 'prettier', 'markdownlint', 'mdformat', 'yamllint', 'jq',
    'semgrep', 'gitleaks'
]
for tool in tools:
    status = "✅" if shutil.which(tool) else "❌"
    print(f"{status} {tool}")
EOF

python scripts/check_phase6_tools.py
```

---

## Success Criteria

### All Workstreams Complete When:
- ✅ 163+ tests passing (100% pass rate)
- ✅ 57 test files created (42 plugin + 10 integration + 5 existing)
- ✅ All 19 plugins tested
- ✅ Integration suite validates end-to-end
- ✅ 12 unit test bugs fixed
- ✅ Documentation updated
- ✅ Coverage >90%

---

## Quick Reference

### File Locations
```
Plugin Tests:
  phase6_error_recovery/modules/plugins/{plugin_name}/tests/
    - test_plugin_detection.py
    - test_plugin_fix.py
    - test_plugin_edge_cases.py

Integration Tests:
  tests/error/integration/
    - test_full_pipeline_python.py
    - test_full_pipeline_javascript.py
    - test_multi_plugin_coordination.py
    - test_state_machine_transitions.py
    - ... (6 more files)

Unit Test Fixes:
  tests/error/unit/test_agent_adapters.py (6 fixes)
  tests/error/unit/test_pipeline_engine_additional.py (2 fixes)
  tests/error/unit/test_security.py (4 fixes)
  tests/error/unit/test_test_runner_parsing.py (4 fixes)
```

### Execution Patterns
- **EXEC-001**: Type-Safe Operations (file type validation)
- **EXEC-002**: Batch Validation (validate all, then execute)
- **EXEC-003**: Tool Availability Guards (skip if tool missing)
- **EXEC-004**: Atomic Operations (temp dirs, rollback)
- **EXEC-006**: Auto-Fix Linting (apply formatters to tests)

---

## Rollback Plan

If issues arise:
```bash
# Stash all changes
git stash push -m "Phase 6 testing remediation WIP"

# Create backup branch
git checkout -b phase6-testing-remediation-backup

# Return to main
git checkout main
git stash pop
```

---

**Ready to Execute**: ✅
**Estimated Completion**: 5 days
**Risk Level**: LOW (independent workstreams, well-defined scope)

**Start Command**: See "Day 1 - Parallel Launch" above
