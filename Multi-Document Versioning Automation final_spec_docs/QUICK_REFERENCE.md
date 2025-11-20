# Production Readiness - Quick Reference Card

**🎯 Goal:** Transform module from functional spec to production-ready package  
**⏱️ Timeline:** 8-12 days | **👥 Team:** 1.5-2 FTE | **📊 Success:** 85% coverage, pip-installable, docs complete

---

## 📋 Three Phases at a Glance

| Phase | Days | Focus | Gate |
|-------|------|-------|------|
| **1: Foundation** | 3-4 | Tests + README + CI | ≥85% coverage, docs complete |
| **2: Implementation** | 3-4 | BDD + examples + plugins | Integration tests pass |
| **3: Polish** | 2-4 | Performance + package | pip install works |

---

## 🚀 Phase 1: Foundation & Testing (Days 1-4)

### Day 1: Documentation
```bash
# Create these files:
README.md          # Installation, quickstart, architecture
requirements.txt   # pyyaml, pytest, jsonschema, jinja2
CHANGELOG.md       # v1.0.0 baseline
LICENSE            # MIT or Apache 2.0
```

### Days 2-3: Unit Tests
```bash
# Create test files with ≥85% coverage:
tests/unit/test_indexer.py    # Sidecar generation, MFID calc
tests/unit/test_guard.py      # Validation, duplicate detection
tests/unit/test_resolver.py   # spec:// and specid:// URIs
tests/unit/test_patcher.py    # Paragraph editing, MFID updates
tests/unit/test_renderer.py   # Markdown rendering

# Infrastructure:
pytest.ini                    # Coverage config
tests/conftest.py            # Shared fixtures
tests/fixtures/              # Sample data
```

### Day 4: CI Enhancement
```bash
# Update .github/workflows/spec-ci.yml:
- Add pytest with coverage reporting
- Add coverage threshold (80% minimum)
- Add artifact uploads
```

**✅ Phase 1 Gate:**
```bash
pytest tests/unit/ -v --cov=tools --cov-fail-under=85
# All pass, ≥85% coverage
```

---

## 🔧 Phase 2: Implementation & Examples (Days 5-8)

### Day 5: Example Artifacts
```bash
# Create example files:
ids/docs/cards/01JC4ABCDXYZ.yaml     # Sample Doc Card
.ledger/docs.jsonl                    # Sample events
registry/docs.registry.yaml           # Sample registry
plan/deliverables/DEL-DOCS-SPEC.yaml  # Sample DDS
docs-guard.yml                        # Policy config
```

### Days 6-7: BDD Test Suite
```bash
# Add pytest-bdd to requirements.txt
# Create feature files:
tests/behavior/features/suite_integrity.feature  # 3+ scenarios
tests/behavior/features/addressing.feature       # 2+ scenarios
tests/behavior/step_defs/test_suite_steps.py    # Step implementations
```

### Day 7: Integration Tests
```bash
tests/integration/test_full_workflow.py
# Test: markdown → sidecar → validate → patch → re-validate
# Test: CREATE → UPDATE → PUBLISH lifecycle
# Test: registry rebuild
```

### Day 8: Plugin Stubs
```bash
plugins/docs/PLG_DOCS_SCAN/          # Manifest + stub + tests
plugins/docs/PLG_DOCS_VALIDATE/      # Manifest + stub + tests
plugins/docs/PLG_DOCS_REGISTRY_BUILD/ # Manifest + stub + tests
```

**✅ Phase 2 Gate:**
```bash
pytest tests/behavior/ tests/integration/ -v
# All BDD and integration tests pass
```

---

## 💎 Phase 3: Polish & Release (Days 9-12)

### Day 9: Performance Testing
```bash
tests/performance/test_large_suite.py
# Benchmarks: index 100 docs <5s, validate <3s, resolve <100ms
```

### Day 10: Error Handling
```bash
tests/edge_cases/test_error_handling.py
# Test all error paths, recovery strategies
# Enhance error messages with actionable suggestions
```

### Day 11: Documentation Polish
```bash
docs/user-guide.md        # Authoring, versioning, troubleshooting
docs/architecture-guide.md # Design rationale, data flow
docs/tutorial.md          # Step-by-step examples
# Add docstrings to all public functions
```

### Day 12: Package + Final Validation
```bash
# Create setup.py or pyproject.toml
# Define CLI entry points: spec-indexer, spec-guard, etc.
# Create CONTRIBUTING.md

# Final validation:
pytest -v --cov=tools --cov-fail-under=85
black tools/ tests/
ruff check tools/ tests/
mypy tools/
pip install -e .
spec-guard  # Test CLI
```

**✅ Phase 3 Gate:**
```bash
pip install -e .
spec-guard
spec-indexer docs/source
# Package installs, CLIs work
```

---

## 🎯 Success Metrics

### Quantitative
- [ ] ≥85% test coverage
- [ ] 100 docs: index <5s, validate <3s
- [ ] 100% public APIs documented
- [ ] Zero linting errors
- [ ] CI all green

### Qualitative
- [ ] New contributor productive <1 hour
- [ ] Error messages actionable
- [ ] Docs comprehensive
- [ ] No crashes on valid input

---

## ⚡ Quick Commands

### Testing
```bash
# Unit tests
pytest tests/unit/ -v --cov=tools --cov-report=term-missing

# BDD tests
pytest tests/behavior/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest -v --cov=tools --cov-fail-under=85
```

### Quality
```bash
# Format code
black tools/ tests/

# Lint
ruff check tools/ tests/

# Type check
mypy tools/
```

### Tools
```bash
# Generate sidecars
python -m tools.spec_indexer.indexer docs/source

# Validate suite
python -m tools.spec_guard.guard

# Resolve URI
python -m tools.spec_resolver.resolver "spec://ARCH/1#p-3"

# Render spec
python -m tools.spec_renderer.renderer --output build/spec.md
```

### Package (Phase 3)
```bash
# Install locally
pip install -e .

# Use CLI tools
spec-indexer docs/source
spec-guard
spec-resolver "spec://ARCH/1"
spec-patcher --id <ULID> --text "New content"
spec-renderer --output dist/spec.md
```

---

## 📚 Document Index

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **PRODUCTION_READINESS_PLAN.md** | Comprehensive 3-phase plan | Full context, planning |
| **PHASE_CHECKLIST.md** | Daily tracking checklist | Daily standups, progress |
| **PHASE_1_EXECUTION_GUIDE.md** | Day-by-day Phase 1 guide | Phase 1 implementation |
| **IMPLEMENTATION_SUMMARY.md** | Executive summary | Stakeholder updates |
| **This card** | Quick reference | Daily work, commands |

---

## 🚨 Common Issues & Fixes

### Coverage Below Target
```bash
# Find uncovered lines
pytest --cov=tools --cov-report=html
# Open htmlcov/index.html
# Add tests for red lines
```

### Tests Failing
```bash
# Run specific test with verbose output
pytest tests/unit/test_guard.py::test_name -vv

# Check fixtures
pytest --fixtures

# Debug with pdb
pytest --pdb
```

### CI Failing
```bash
# Check requirements.txt complete
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+

# Run CI locally
pytest -v --cov=tools --cov-fail-under=85
```

### Import Errors
```bash
# Install in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 👥 Team Roles

| Role | Responsibilities | Time |
|------|------------------|------|
| **Lead Dev** | Architecture, code review, Phase 3 | 50% (4-6 days) |
| **Test Engineer** | Test suite, coverage, Phases 1-2 | 100% (6-8 days) |
| **Tech Writer** | Docs, tutorials, Phase 3 | 75% (2-3 days) |
| **DevOps** | CI/CD, package setup | 25% (1-2 days) |

---

## 📅 Daily Checklist Template

**Date:** __________ | **Phase:** __ | **Day:** __

**Today's Goals:**
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Completed:**
- [ ] Tests written
- [ ] Tests passing
- [ ] Coverage verified
- [ ] Docs updated
- [ ] Checklist updated

**Blockers:** ___________________________

**Tomorrow:** ___________________________

---

## 🎓 Best Practices

### Writing Tests
- ✅ Test happy path + error paths
- ✅ Use fixtures for setup
- ✅ One assertion per test (mostly)
- ✅ Clear test names: `test_guard_detects_missing_sidecar`
- ❌ Don't test implementation details

### Documentation
- ✅ Code examples that actually work
- ✅ Clear prerequisites
- ✅ Expected output shown
- ✅ Common errors documented
- ❌ Don't assume knowledge

### Code Quality
- ✅ Run black before commit
- ✅ Fix ruff errors
- ✅ Add type hints
- ✅ Write docstrings
- ❌ Don't commit commented code

---

## 🔗 Key Files

**Existing:**
- `docs/source/` - 28 spec documents
- `docs/.index/suite-index.yaml` - Suite metadata
- `tools/spec_indexer/indexer.py` - Sidecar generator
- `tools/spec_guard/guard.py` - Validator
- `.github/workflows/spec-ci.yml` - CI config

**To Create (Phase 1):**
- `README.md`, `requirements.txt`, `CHANGELOG.md`
- `tests/unit/test_*.py` - 5 test files
- `pytest.ini`, `tests/conftest.py`

**To Create (Phase 2):**
- Example artifacts: cards, ledger, registry
- `tests/behavior/`, `tests/integration/`
- Plugin stubs

**To Create (Phase 3):**
- User guides, tutorial, API docs
- `setup.py` or `pyproject.toml`
- `CONTRIBUTING.md`

---

## 📊 Progress Tracking

**Phase 1:** ⬜⬜⬜⬜ (0/4 days)  
**Phase 2:** ⬜⬜⬜⬜ (0/4 days)  
**Phase 3:** ⬜⬜⬜⬜ (0/4 days)

**Overall:** 0% complete

_Update daily: ⬜ Not started | 🔄 In progress | ✅ Complete_

---

## 🎉 Definition of Done (Final Gate)

```bash
# All of these must pass:
pytest -v --cov=tools --cov-fail-under=85        # ✅
black --check tools/ tests/                      # ✅
ruff check tools/ tests/                         # ✅
mypy tools/                                      # ✅
pip install -e .                                 # ✅
spec-guard                                       # ✅
spec-indexer docs/source                         # ✅

# And documentation exists:
ls README.md CHANGELOG.md LICENSE                # ✅
ls docs/user-guide.md docs/tutorial.md           # ✅
```

**When all ✅ → Production Ready → Ship v1.0! 🚀**

---

**Print this card and keep it visible during implementation!**

_Last updated: 2025-11-20_
