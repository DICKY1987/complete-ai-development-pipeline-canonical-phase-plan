---
doc_id: DOC-GUIDE-E2E-CLI-TEST-PLAN-SUMMARY-547
---

# E2E CLI Communication Testing Plan - Executive Summary

**Full Plan:** [E2E_CLI_COMMUNICATION_TEST_PLAN.md](E2E_CLI_COMMUNICATION_TEST_PLAN.md)
**Created:** 2025-12-04
**Status:** Ready for Implementation

---

## Overview

Comprehensive 7-layer testing pyramid for all CLI tool communication (Aider, Codex, Claude, custom tools).

**Total Estimated Tests:** ~500
**Implementation Time:** 15-20 hours
**Expected Coverage:** 88% overall

---

## 7-Layer Test Pyramid

```
Layer 7: E2E Tests (~10 tests, 30 min)
  - Full workstream execution
  - Real-world scenarios

Layer 6: Performance Tests (~20 tests, 10 min)
  - Throughput benchmarks
  - Memory leak detection

Layer 5: Error Handling Tests (~50 tests, 5 min)
  - Timeout scenarios
  - Tool not found
  - Invalid input

Layer 4: Sandbox Tests (~30 tests, 15 min)
  - Real Aider execution
  - Concurrent tool execution

Layer 3: Contract Tests (~30 tests, 5 min)
  - Aider CLI contract (DOC-074)
  - Cross-tool contracts

Layer 2: Integration Tests (~100 tests, 10 min)
  - Tool adapter + subprocess
  - Aider engine + tool adapter

Layer 1: Unit Tests (~200 tests, 2 min)
  - Profile loading
  - Command rendering
  - Prompt building
```

---

## Key Testing Areas

### 1. Core Tool Adapter (`core/engine/tools.py`)
- ✅ Profile loading from invoke.yaml
- ✅ Template substitution (`{repo_root}`, `{cwd}`, etc.)
- ✅ Subprocess execution with timeout
- ✅ Exit code handling (-1=timeout, -2=not found, -3=error)
- ✅ Environment variable injection
- ✅ Working directory management

### 2. Aider Engine (`phase4_routing/modules/aider_integration/`)
- ✅ Prompt generation (EDIT and FIX templates)
- ✅ Prompt file creation (`.aider/prompts/`)
- ✅ Integration with tool adapter
- ✅ Jinja2 template rendering

### 3. Agent Adapters (`phase6_error_recovery/modules/error_engine/`)
- ✅ AiderAdapter, CodexAdapter, ClaudeAdapter
- ✅ Error prompt formatting
- ✅ Tool availability checking
- ✅ Result parsing

### 4. Contract Compliance
- ✅ Aider CLI flags (`--no-auto-commits`, `--yes`, `--message-file`)
- ✅ Exit code standards
- ✅ Version requirements

---

## Quick Start Commands

```bash
# Fast feedback (2 min)
pytest -m "unit" -v

# Pre-commit (12 min)
pytest -m "not slow and not requiresai" -v

# Full suite without AI (30 min)
pytest -m "not requiresai" -v

# Contract validation (5 min)
pytest -m contract -v

# Performance benchmarks (10 min)
pytest -m performance -v
```

---

## Implementation Roadmap

### Week 1: Foundation
- Set up test structure
- 200+ unit tests
- Shared fixtures
- **Deliverable:** 90% unit coverage

### Week 2: Integration
- 100+ integration tests
- Concurrency tests
- Timeout handling
- **Deliverable:** Full integration suite

### Week 3: Validation
- Contract tests
- Sandbox tests
- Error handling suite
- **Deliverable:** Test pyramid complete

### Week 4: E2E & Polish
- End-to-end workflows
- Real-world scenarios
- CI integration
- **Deliverable:** Production-ready

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Unit Coverage | 95% | ⏳ |
| Integration Coverage | 85% | ⏳ |
| E2E Coverage | 75% | ⏳ |
| Tool Latency (p50) | <100ms | ⏳ |
| Throughput (parallel) | >50/sec | ⏳ |
| Memory Growth (1000x) | <50MB | ⏳ |

---

## Quality Gates

**Pre-Merge:**
- ✅ All unit + integration tests pass
- ✅ Coverage >= 85% on modified files
- ✅ No linting errors

**Pre-Release:**
- ✅ All sandbox tests pass
- ✅ Performance targets met
- ✅ 80%+ E2E tests pass

---

## Next Steps

1. **Review & Approve Plan** (1 day)
   - Technical review by team
   - Adjust timelines if needed

2. **Phase 1 Implementation** (Week 1)
   - Create test structure
   - Implement unit tests
   - Set up CI pipeline

3. **Phase 2-4 Implementation** (Weeks 2-4)
   - Follow roadmap
   - Weekly progress reviews
   - Adjust based on findings

4. **Maintenance Mode** (Ongoing)
   - Weekly CI monitoring
   - Monthly coverage audits
   - Quarterly performance reviews

---

## Files Created

- ✅ `E2E_CLI_COMMUNICATION_TEST_PLAN.md` - Full 500-test plan
- ✅ `E2E_CLI_TEST_PLAN_SUMMARY.md` - This summary

**Ready to begin implementation!**
