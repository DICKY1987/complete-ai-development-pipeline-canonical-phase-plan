# Multi-Document Versioning Automation - Production Readiness Plan

**Module:** Multi-Document Versioning Automation  
**Current Status:** Specification Complete, Tools Functional, Tests Missing  
**Target:** Production-Ready Package  
**Timeline:** 3 Phases (8-12 days)  
**Owner:** Documentation Automation Team

---

## Executive Summary

This module implements a contract-driven documentation-as-code system with excellent architecture (microkernel + plugins, immutable identity, deterministic fingerprinting). Five Python tools are functional and validated. However, critical gaps prevent production deployment: no test coverage, missing README/examples, and incomplete plugin framework. This plan delivers a production-ready version through three focused phases.

**Current State:**
- ✅ 28 specification documents with sidecar metadata
- ✅ 5 operational Python tools (indexer, guard, resolver, patcher, renderer)
- ✅ Validation passing (`spec_guard` confirms suite integrity)
- ✅ CI workflow configured (GitHub Actions)
- ❌ Zero test coverage (unit, integration, BDD)
- ❌ No README or onboarding documentation
- ❌ Plugin framework specified but not implemented
- ❌ Missing example artifacts (cards, ledger, registry)

---

## Phase 1: Foundation & Testing (3-4 days)

**Objective:** Close critical gaps preventing production use - add comprehensive tests, documentation, and dependency management.

### Deliverables

#### 1.1 Documentation & Onboarding (Day 1)
- **README.md**
  - Installation instructions (`pip install -r requirements.txt`)
  - Quickstart: scanning docs, generating sidecars, validating suite
  - Tool usage examples for all 5 utilities
  - Architecture overview with links to spec sections
  - Contributing guidelines
  - License information

- **requirements.txt**
  ```
  pyyaml>=6.0.1,<7.0
  pytest>=7.4.0,<8.0
  pytest-cov>=4.1.0,<5.0
  jsonschema>=4.19.0,<5.0
  jinja2>=3.1.2,<4.0  # for spec_renderer templates
  ```

- **CHANGELOG.md**
  - Version 1.0.0 baseline entry
  - Format follows Keep a Changelog

#### 1.2 Unit Test Suite (Days 2-3)
- **tests/unit/test_indexer.py**
  - Test sidecar generation from markdown
  - Verify MFID calculation accuracy
  - Test paragraph detection (edge cases: empty files, single para, nested lists)
  - Test preservation of existing paragraph IDs
  - Coverage target: 90%+

- **tests/unit/test_guard.py**
  - Test validation of suite integrity
  - Test duplicate ID detection
  - Test file existence checks
  - Test MFID mismatch detection
  - Test anchor ordering validation
  - Coverage target: 90%+

- **tests/unit/test_resolver.py**
  - Test `spec://` URI resolution (volume, section, paragraph)
  - Test `specid://` ULID resolution
  - Test error cases (invalid URIs, missing sections)
  - Test anchor-based navigation
  - Coverage target: 90%+

- **tests/unit/test_patcher.py**
  - Test paragraph replacement
  - Test MFID recalculation after patch
  - Test index update propagation
  - Test error handling (invalid IDs, file locks)
  - Coverage target: 85%+

- **tests/unit/test_renderer.py**
  - Test markdown rendering from suite index
  - Test template processing
  - Test output file generation
  - Coverage target: 85%+

#### 1.3 Test Infrastructure (Day 3)
- **pytest.ini**
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = -v --cov=tools --cov-report=html --cov-report=term-missing
  markers =
      unit: Unit tests
      integration: Integration tests
      bdd: Behavior-driven tests
  ```

- **tests/conftest.py**
  - Fixtures for sample markdown files
  - Fixtures for suite index structures
  - Temporary directory management
  - Mock sidecar data

- **tests/fixtures/**
  - Sample markdown files (simple, complex, edge cases)
  - Sample sidecar YAML files
  - Sample suite index fragments

#### 1.4 CI Enhancement (Day 4)
- **Update .github/workflows/spec-ci.yml**
  - Add pytest with coverage reporting
  - Add coverage threshold enforcement (80% minimum)
  - Add test result artifacts upload
  - Add badge generation for README

### Acceptance Criteria
- [ ] All 5 tools have ≥85% test coverage
- [ ] `pytest` runs clean (all tests pass)
- [ ] README provides clear onboarding path
- [ ] CI pipeline runs tests and reports coverage
- [ ] Documentation builds without errors

---

## Phase 2: Implementation & Examples (3-4 days)

**Objective:** Complete the plugin framework, add BDD tests matching DDS acceptance criteria, and generate example artifacts demonstrating the full workflow.

### Deliverables

#### 2.1 Example Artifacts (Day 1)
- **ids/docs/cards/01JC4ABCDXYZ.yaml** (sample Doc Card)
  ```yaml
  schema_version: 1
  ulid: 01JC4ABCDXYZ
  key: DOC_ARCH_OVERVIEW
  semver: 1.0.0
  status: active
  effective_date: 2025-11-20
  path: docs/source/01-architecture/00-overview.md
  owners: ["docs@project"]
  links:
    delivers: ["DEL-DOCS-SPEC"]
    acceptance: ["AC-DOCS-001"]
    evidence: ["reports/spec-validate.xml"]
  card_version: 1
  ```

- **.ledger/docs.jsonl** (sample ledger events)
  ```jsonl
  {"event_ulid":"01JC4EVT001","ts":"2025-11-20T00:00:00Z","type":"CREATE","subject_ulid":"01JC4ABCDXYZ","payload":{"semver":"1.0.0"},"actor":{"by":"system","via":"docs.init@1.0.0"}}
  {"event_ulid":"01JC4EVT002","ts":"2025-11-20T01:00:00Z","type":"PUBLISH","subject_ulid":"01JC4ABCDXYZ","payload":{"semver":"1.0.0","ci_run":"01JC4RUN001"},"actor":{"by":"ci@repo","via":"docs.publish@1.0.0"}}
  ```

- **registry/docs.registry.yaml** (sample registry)
  ```yaml
  by_ulid:
    "01JC4ABCDXYZ":
      key: DOC_ARCH_OVERVIEW
      semver: 1.0.0
      status: active
      path: docs/source/01-architecture/00-overview.md
  by_key:
    DOC_ARCH_OVERVIEW:
      ulid: 01JC4ABCDXYZ
      semver: 1.0.0
      status: active
  ```

- **plan/deliverables/DEL-DOCS-SPEC.yaml** (sample DDS)
  ```yaml
  id: DEL-DOCS-SPEC
  name: "Documentation Specification Suite"
  purpose: "Complete technical specification for doc automation"
  acceptance:
    - id: AC-DOCS-001
      gherkin: |
        Feature: Spec suite integrity
          Scenario: All docs have valid sidecars
            Given committed markdown files
            When spec_guard validates suite
            Then zero integrity errors reported
  evidence:
    tests: ["tests/integration/test_suite_integrity.py"]
    reports: ["reports/spec-validate.xml"]
  ```

- **docs-guard.yml** (policy configuration)
  ```yaml
  version: 1
  policies:
    coverage:
      enabled: true
      min_percentage: 80
    one_artifact_rule:
      enabled: false  # optional future feature
    required_fields:
      - owners
      - semver
      - status
  ```

#### 2.2 BDD Test Suite (Days 2-3)
- **tests/behavior/features/suite_integrity.feature**
  ```gherkin
  Feature: Specification Suite Integrity
    As a documentation author
    I want automated validation of spec consistency
    So that broken references and drift are caught early

    Scenario: Valid suite passes all checks
      Given a complete specification suite
      When I run spec_guard validation
      Then the validation succeeds
      And zero errors are reported

    Scenario: Missing sidecar is detected
      Given a markdown file without a sidecar
      When I run spec_guard validation
      Then the validation fails
      And a "sidecar missing" error is reported

    Scenario: MFID drift is detected
      Given a markdown file modified after indexing
      When I run spec_guard validation
      Then the validation fails
      And a "MFID mismatch" error is reported
  ```

- **tests/behavior/features/addressing.feature**
  ```gherkin
  Feature: Specification Addressing
    As a documentation user
    I want stable URIs for sections and paragraphs
    So that references remain valid across versions

    Scenario: Resolve section by spec URI
      Given suite index with section ARCH/1
      When I resolve "spec://ARCH/1"
      Then the file path is returned
      And the section metadata is included

    Scenario: Resolve paragraph by anchor
      Given suite index with paragraph p-3 in ARCH/1
      When I resolve "spec://ARCH/1#p-3"
      Then the paragraph line range is returned
  ```

- **tests/behavior/step_defs/test_suite_steps.py** (pytest-bdd implementation)

- **Install pytest-bdd**
  ```txt
  pytest-bdd>=6.1.1,<7.0
  ```

#### 2.3 Integration Tests (Day 3)
- **tests/integration/test_full_workflow.py**
  - Test: create new markdown → generate sidecar → validate suite → patch paragraph → re-validate
  - Test: complete doc lifecycle (CREATE → UPDATE → PUBLISH events)
  - Test: registry rebuild from cards
  - Uses temporary directories, no side effects

#### 2.4 Plugin Framework Stubs (Day 4)
- **plugins/docs/PLG_DOCS_SCAN/**
  ```
  manifest.yaml
  README.md
  src/__init__.py
  src/scan.py  # stub implementation
  schemas/in.schema.json
  schemas/out.schema.json
  tests/test_scan.py
  examples/scan_output.json
  ```

- **plugins/docs/PLG_DOCS_VALIDATE/**
  - Similar structure, validation logic stub

- **plugins/docs/PLG_DOCS_REGISTRY_BUILD/**
  - Registry construction logic stub

- **Note:** Full plugin implementation optional; stubs demonstrate contract compliance

### Acceptance Criteria
- [ ] Example artifacts generated and documented
- [ ] BDD tests execute and pass (≥5 scenarios)
- [ ] Integration tests cover full workflow
- [ ] At least 2 plugin stubs with passing contract validation
- [ ] Policy configuration documented and functional

---

## Phase 3: Polish & Release (2-4 days)

**Objective:** Production hardening, performance validation, documentation polish, and package preparation for release.

### Deliverables

#### 3.1 Performance & Scale Testing (Day 1)
- **tests/performance/test_large_suite.py**
  - Generate suite with 100+ documents
  - Measure indexing time (target: <5s for 100 docs)
  - Measure validation time (target: <3s for 100 docs)
  - Measure resolution time (target: <100ms per query)
  - Memory profiling for large suites

- **Performance benchmarks documented in README**

#### 3.2 Error Handling & Edge Cases (Day 2)
- **Enhanced error messages**
  - spec_guard: actionable suggestions (e.g., "Run spec_indexer to regenerate sidecars")
  - spec_resolver: clear URI format examples on error
  - spec_patcher: file backup before modification

- **Robustness improvements**
  - Handle Unicode in markdown gracefully
  - Handle concurrent access (file locking)
  - Handle malformed YAML (clear parse errors)
  - Handle missing dependencies (graceful degradation)

- **tests/edge_cases/test_error_handling.py**
  - Test all error paths
  - Test recovery strategies
  - Test error message clarity

#### 3.3 Documentation Polish (Day 3)
- **User Guide** (`docs/user-guide.md`)
  - Authoring workflow
  - Versioning strategy
  - URI addressing best practices
  - Troubleshooting common issues

- **Architecture Guide** (`docs/architecture-guide.md`)
  - Microkernel design rationale
  - Plugin contract specification
  - Data flow diagrams
  - Extension points

- **API Reference** (auto-generated)
  - Docstrings for all public functions
  - Type hints throughout
  - Usage examples in docstrings

- **Tutorial** (`docs/tutorial.md`)
  - Step-by-step: create first spec doc
  - Step-by-step: version and publish doc
  - Step-by-step: create custom plugin

#### 3.4 Package Preparation (Day 4)
- **setup.py / pyproject.toml**
  ```toml
  [project]
  name = "multi-doc-versioning"
  version = "1.0.0"
  description = "Contract-driven documentation-as-code with versioning and traceability"
  authors = [{name = "Your Name", email = "you@example.com"}]
  license = {text = "MIT"}
  requires-python = ">=3.10"
  dependencies = [
      "pyyaml>=6.0.1,<7.0",
      "jsonschema>=4.19.0,<5.0",
      "jinja2>=3.1.2,<4.0"
  ]
  
  [project.optional-dependencies]
  test = ["pytest>=7.4.0", "pytest-cov>=4.1.0", "pytest-bdd>=6.1.1"]
  dev = ["black>=23.0.0", "ruff>=0.1.0", "mypy>=1.7.0"]
  
  [project.scripts]
  spec-indexer = "tools.spec_indexer.indexer:main"
  spec-guard = "tools.spec_guard.guard:main"
  spec-resolver = "tools.spec_resolver.resolver:main"
  spec-patcher = "tools.spec_patcher.patcher:main"
  spec-renderer = "tools.spec_renderer.renderer:main"
  ```

- **LICENSE** (MIT or Apache 2.0)

- **CONTRIBUTING.md**
  - Development setup
  - Running tests
  - Submitting PRs
  - Code style guidelines

- **Release checklist** (`RELEASE.md`)

#### 3.5 Final Validation (Day 4)
- **Complete test run**
  ```bash
  pytest -v --cov=tools --cov-report=html
  # Target: ≥85% coverage, all tests pass
  ```

- **Linting**
  ```bash
  black tools/ tests/
  ruff check tools/ tests/
  mypy tools/
  ```

- **Documentation build**
  ```bash
  python -m tools.spec_renderer.renderer --output build/spec.md
  # Verify no broken links, proper formatting
  ```

- **Manual workflow test**
  - Fresh clone → install → run quickstart → verify output

### Acceptance Criteria
- [ ] Performance benchmarks meet targets
- [ ] All error paths tested and documented
- [ ] User guide, architecture guide, API reference complete
- [ ] Package installable via pip (local test)
- [ ] Complete test suite passes with ≥85% coverage
- [ ] Linting clean (black, ruff, mypy)
- [ ] Manual workflow test succeeds

---

## Success Metrics

### Quantitative
- **Test Coverage:** ≥85% (unit + integration)
- **Performance:** Index 100 docs in <5s, validate in <3s
- **Documentation:** 100% of public APIs documented
- **CI Health:** All checks green on main branch
- **Code Quality:** Zero linting errors

### Qualitative
- **Onboarding Time:** New contributor productive in <1 hour
- **Error Messages:** Actionable and clear
- **Documentation Quality:** Comprehensive, examples-driven
- **Stability:** No crashes on valid input, graceful degradation on invalid input

---

## Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Test coverage slips below target | High | Medium | Daily coverage reports, PR gates at 80% |
| Performance regressions | Medium | Low | Benchmark tests in CI, performance budgets |
| Incomplete plugin framework | Medium | Medium | Stub implementations acceptable for v1.0, full impl in v1.1 |
| Documentation drift from code | High | Medium | Auto-generated API docs, CI checks for broken links |
| Dependency conflicts | Low | Low | Pin major versions, test with fresh virtualenv |

---

## Dependencies & Prerequisites

### Required
- Python 3.10+
- Git
- PyYAML, pytest, jsonschema (see requirements.txt)

### Optional
- GitHub Actions (for CI)
- Read the Docs / MkDocs (for doc hosting)

### External
- None (self-contained module)

---

## Post-Release Plan (Phase 4 - Future)

### v1.1 Enhancements (1-2 weeks)
- Complete plugin framework implementation
- REST API for spec queries
- Web UI for spec browsing
- Advanced policy engine (compliance rules)

### v1.2 Integrations (2-3 weeks)
- Integration with parent repository's `spec/` section
- OpenSpec parser integration
- CI/CD plugin for automated versioning
- Slack/Teams notifications for spec changes

### v2.0 Advanced Features (4-6 weeks)
- Multi-repo spec federation
- Diff viewer for spec versions
- Automated migration tools
- Translation/i18n support via plugins

---

## Timeline Summary

| Phase | Duration | Key Deliverables | Blocker Risk |
|-------|----------|------------------|--------------|
| **Phase 1: Foundation** | 3-4 days | Tests, README, requirements.txt, CI | Low |
| **Phase 2: Implementation** | 3-4 days | BDD tests, examples, plugin stubs | Medium |
| **Phase 3: Polish** | 2-4 days | Performance, docs, package | Low |
| **Total** | **8-12 days** | Production-ready v1.0 | **Low** |

**Recommended Approach:** Sequential phases with daily checkpoint reviews. Each phase gate requires acceptance criteria met before proceeding.

---

## Roles & Responsibilities

| Role | Responsibilities | Time Commitment |
|------|------------------|-----------------|
| **Lead Developer** | Architecture decisions, code review, Phase 3 | 50% (4-6 days) |
| **Test Engineer** | Test suite implementation, coverage analysis, Phases 1-2 | 100% (6-8 days) |
| **Technical Writer** | Documentation, tutorials, user guide, Phase 3 | 75% (2-3 days) |
| **DevOps** | CI/CD enhancements, package setup, Phase 1 & 3 | 25% (1-2 days) |

**Total Effort:** ~13-19 person-days across 8-12 calendar days (assuming 1.5-2 FTE)

---

## Appendix A: Current vs. Target State

| Aspect | Current State | Target State (v1.0) |
|--------|---------------|---------------------|
| **Tests** | 0 tests | ≥50 tests, 85% coverage |
| **Documentation** | Specs only | README, guides, API docs, tutorial |
| **Tools** | 5 tools, manual | 5 tools, CLI scripts, pip-installable |
| **Examples** | None | Cards, ledger, registry, DDS |
| **CI** | Basic validation | Full test suite, coverage, linting |
| **Package** | Directory | Installable package with entry points |
| **Plugins** | Specified only | ≥2 stub implementations |
| **Performance** | Unknown | Benchmarked, budgeted |

---

## Appendix B: Repository Integration Strategy

**Option 1: Standalone Package (Recommended for v1.0)**
- Publish to PyPI as `multi-doc-versioning`
- Parent repo uses as dependency
- Maintains clean separation of concerns
- Easier to version independently

**Option 2: Integrated Submodule**
- Move to `Complete AI Development Pipeline/spec/multi_doc_versioning/`
- Shares test infrastructure with parent
- Tighter integration with parent's `spec/` tools
- Requires coordination on breaking changes

**Recommendation:** Start with Option 1 (standalone), migrate to Option 2 in v1.2 if tight integration proves beneficial.

---

## Appendix C: Quick Start Commands (Post-Delivery)

```bash
# Installation
pip install multi-doc-versioning

# Generate sidecars for your docs
spec-indexer docs/source

# Validate suite integrity
spec-guard

# Resolve a spec URI
spec-resolver "spec://ARCH/1#p-3"

# Render complete spec
spec-renderer --output dist/specification.md

# Run tests (development)
pytest -v --cov=tools
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-20  
**Status:** APPROVED  
**Next Review:** End of Phase 1
