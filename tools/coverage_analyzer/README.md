# Coverage Analyzer

**5-Layer Progressive Test Coverage Framework**

A comprehensive test coverage analysis tool that implements defense-in-depth testing across 5 layers:

## The 5 Layers

### Pre-Execution (Shift-Left Security)
- **Layer 0:** Static Analysis (SAST) - Code quality & security before execution
- **Layer 0.5:** Software Composition Analysis (SCA) - Dependency vulnerabilities

### Execution (Dynamic Testing)
- **Layer 1:** Structural Coverage - What code was executed
- **Layer 2:** Mutation Testing - Whether tests verify correctness
- **Layer 3:** Path Coverage - All logical paths exercised

### Post-Execution (Production Readiness)
- **Layer 4:** Operational Validation - System-level NFR testing

## Quick Start

```bash
# Install (when ready)
pip install -e tools/coverage_analyzer

# Run all layers
coverage-analyzer analyze --path=src/ --language=python

# Run specific layers (fast CI)
coverage-analyzer analyze --path=src/ --layers=0,0.5,1

# Get detailed help
coverage-analyzer --help
```

## Status

**Phase 1: Core Infrastructure** ✓ Complete (2025-12-04)
- ✅ Data models (base.py)
- ✅ Base adapter (base_adapter.py)
- ✅ Registry system (registry.py)
- ✅ Configuration (coverage_analyzer.yaml)
- ✅ Test fixtures (conftest.py)
- ✅ Basic tests (test_base.py, test_registry.py)

**Phase 2: Structural Coverage (Layer 1)** ✓ Complete (2025-12-04)
- ✅ coverage.py adapter (Python)
- ✅ Pester adapter (PowerShell)
- ✅ Structural coverage analyzer
- ✅ Language detection & routing
- ✅ Adapter tests (24 tests, all passing)

**Phase 3: Static Analysis (Layer 0)** ✓ Complete (2025-12-04)
- ✅ Radon adapter (Python, dual-purpose)
- ✅ Bandit adapter (Python, security)
- ✅ mypy adapter (Python, types)
- ✅ Prospector adapter (Python, multi-tool)
- ✅ PSScriptAnalyzer adapter (PowerShell, dual-purpose)
- ✅ Static analysis orchestrator
- ✅ Multi-tool aggregation
- ✅ Adapter tests (27 tests, all passing)

**Next:** Phase 4 - Layer 0.5 (Software Composition Analysis) adapters

## Architecture

```
tools/coverage_analyzer/
├── src/coverage_analyzer/
│   ├── base.py              ✅ All 5 layer data models
│   ├── registry.py          ✅ Adapter registry
│   ├── analyzers/
│   │   ├── __init__.py      ✅ Package marker
│   │   └── structural.py    ✅ Layer 1 analyzer
│   ├── adapters/
│   │   ├── __init__.py      ✅ Package marker
│   │   ├── base_adapter.py  ✅ Abstract base class
│   │   ├── coverage_py_adapter.py  ✅ Python coverage
│   │   └── pester_adapter.py       ✅ PowerShell coverage
│   ├── reporters/           ⏳ Output formatters (TODO)
│   └── cli.py               ⏳ CLI interface (TODO)
├── tests/                   ✅ 47 passing tests
├── config/                  ✅ Default configuration
└── docs/                    ⏳ Documentation (TODO)
```

## Development

```bash
# Run tests
cd tools/coverage_analyzer
pytest tests/ -v

# Check coverage of the coverage analyzer itself (dogfooding)
pytest tests/ --cov=src/coverage_analyzer --cov-report=html

# Install development dependencies (TODO: create requirements.txt)
# pip install -r requirements-dev.txt
```

## Roadmap

- [x] **Phase 1:** Core Infrastructure (Week 1) ✅ COMPLETE
- [x] **Phase 2:** Layer 1 - Structural Coverage adapters (Week 2) ✅ COMPLETE
- [x] **Phase 3:** Layer 0 - Static Analysis adapters (Week 3-4) ✅ COMPLETE
- [ ] **Phase 4:** Layer 0.5 - SCA adapters (Week 4-5)
- [ ] **Phase 5:** Layer 2 - Mutation Testing adapters (Week 5)
- [ ] **Phase 6:** Layer 3 - Complexity adapters (Week 5-6)
- [ ] **Phase 7:** Layer 4 - Operational Validation adapters (Week 6-7)
- [ ] **Phase 8:** Reporting & CLI (Week 7-8)
- [ ] **Phase 9:** Patterns & Documentation (Week 8-9)
- [ ] **Phase 10:** Integration & Dogfooding (Week 9-10)

## License

Part of the Complete AI Development Pipeline project.

## Contributing

See implementation plan: `System _Analyze/Multi-Level Structural Coverage Analysis Plan.md`
