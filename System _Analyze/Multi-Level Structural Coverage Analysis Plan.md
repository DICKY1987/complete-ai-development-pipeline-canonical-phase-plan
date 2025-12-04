---
doc_id: DOC-GUIDE-MULTI-LEVEL-STRUCTURAL-COVERAGE-515
---

## **Expanded 5-Layer Test Coverage Framework**

### **Layer 0: Pre-Execution Static Analysis (Foundation
Layer)**

**Static Code Analysis - Code Structure & Quality**

**Core Principle:**
Analyze code structure, complexity, and quality *before* any
test execution to identify high-risk areas requiring intensive
testing coverage.

**Python Implementation:**
- **Radon** - Cyclomatic complexity, maintainability index
- **Prospector** - Combines pylint, pyflakes, mccabe for
comprehensive analysis
- **Bandit** - Security-focused SAST for Python
- **mypy** - Static type checking

**PowerShell Implementation:**
- **PSScriptAnalyzer** - Built-in static analysis with
customizable rules
- **Pester's ScriptAnalyzer integration** - Automated best
practice validation

**Unique Contribution:**
Static Code Analysis systematically examines source code
without executing it, identifying code smells, excessive
complexity, security vulnerabilities, dead code, and
control/data flow issues. This layer identifies *where to focus
 testing efforts* by flagging complex functions (high
cyclomatic complexity), security-sensitive code paths, and
maintainability issues.

**Integration with Other Layers:**
- Functions with high cyclomatic complexity (>10) get
prioritized for path coverage analysis (Layer 3)
- Security vulnerabilities flagged by SAST require dedicated
test cases in structural coverage (Layer 1)
- Code smells guide mutation testing targets (Layer 2)

---

### **Layer 0.5: Dependency & Component Coverage**

**Software Composition Analysis (SCA) - Third-Party Risk
Assessment**

**Core Principle:**
SCA systematically analyzes external, third-party, and
open-source components used within a codebase, creating a
Software Bill of Materials (SBOM) and validating security,
licensing, and maintenance status.

**Python Implementation:**
- **Safety** - Checks dependencies against known CVE databases
- **pip-audit** - Scans Python dependencies for vulnerabilities
- **Snyk** - Comprehensive SCA with license compliance
- **OWASP Dependency-Check** - Cross-language dependency
scanning

**PowerShell Implementation:**
- **PSDepend** - PowerShell module dependency management
- Custom scripts to audit PowerShellGallery modules against
known issues
- Integration with Snyk or WhiteSource for PowerShell module
scanning

**Unique Contribution:**
SCA generates an SBOM inventory, cross-references components
against vulnerability databases like NVD, validates license
compliance, and identifies outdated or unmaintained components.
 This ensures your testing framework includes validation of
*third-party risk* - a gap often missed by code-focused
coverage tools.

**Integration with Other Layers:**
- Vulnerable dependencies require integration tests verifying
mitigation (Layer 4)
- High-risk external libraries need additional
mocking/isolation in unit tests
- Generates test cases for dependency upgrade scenarios

---

### **Layers 1-3: [Your Original Framework]**

These remain as described:
1. **Multi-Level Structural Coverage** (Statement + Branch)
2. **Mutation Testing** (Test Quality Validation)
3. **Cyclomatic Complexity & Path Coverage** (Logical Flow
Validation)

---

### **Layer 4: Operational Validation Coverage**

**System-Level & Production Environment Testing**

**Core Principle:**
Operational Validation confirms that software, when used in its
 intended operational environment, meets the needs and
expectations of end-users and stakeholders.

**Python Implementation:**
- **pytest with production fixtures** - E2E test scenarios
- **Locust/k6** - Load and performance testing
- **TestContainers** - Docker-based integration testing with
real dependencies
- **Schemathesis** - API contract testing

**PowerShell Implementation:**
- **Pester integration tests** - Test operational scenarios
- **PSate** - Infrastructure state validation
- **Operation Validation Framework (OVF)** - Microsoft's
framework for operational testing

**Unique Contribution:**
Operational validation includes User Acceptance Testing,
Operational Qualification verifying functional and
non-functional requirements under specified operating
conditions, system and end-to-end testing, and NFR validation
for performance, reliability, scalability, security, and
usability.

**Coverage Categories:**

1. **End-to-End Flow Coverage:**
   - Validate complete business processes from start to finish
   - Test interactions with external systems (databases, APIs,
message queues)

2. **Non-Functional Requirement Coverage:**
   - Performance: Load testing scenarios (concurrent users,
data volume)
   - Reliability: Chaos engineering tests (network failures,
service outages)
   - Security: Penetration testing,
authentication/authorization flows
   - Usability: UI/UX validation in production-like
environments

3. **Environmental Coverage:**
   - Test across different OS versions, hardware configurations
   - Cloud platform variations (AWS vs Azure vs GCP)
   - Network topology scenarios

4. **Compliance & Regulatory Coverage:**
   - Audit trail validation
   - Data retention policy verification
   - Regulatory requirement fulfillment tests

**Integration with Other Layers:**
- Operational failures discovered in production trigger new
unit tests (Layer 1)
- Performance bottlenecks guide complexity reduction efforts
(Layer 3)
- Security findings from pen-testing create new mutation
operators (Layer 2)

---

## **Unified Execution Strategy**

### **Single Test Cycle Workflow:**

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 0: Static Analysis (Pre-Execution)               │
│ • PSScriptAnalyzer / Prospector                        │
│ • Identify complexity hotspots & security issues       │
│ • Generate complexity metrics for path coverage        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 0.5: Dependency Analysis (Pre-Execution)         │
│ • Safety / pip-audit / Snyk                            │
│ • Generate SBOM                                         │
│ • Flag vulnerable dependencies requiring tests         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: Structural Coverage (Test Execution)          │
│ • coverage.py / Pester CodeCoverage                    │
│ • Baseline: What code was executed?                    │
│ • Target: High-complexity functions from Layer 0       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: Mutation Testing (Test Quality)               │
│ • mutmut (Python only)                                 │
│ • Validate: Do tests catch behavior changes?          │
│ • Focus: Security-critical code from Layer 0           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: Path Coverage Analysis (Logical Complexity)   │
│ • Calculate cyclomatic complexity from Layer 0         │
│ • Design test cases matching CC value                  │
│ • Verify: All independent paths tested?                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: Operational Validation (System Testing)       │
│ • E2E tests with TestContainers / Pester Integration   │
│ • Performance testing with Locust                      │
│ • Security testing for vulnerabilities from Layer 0.5  │
│ • Validate: Works in production environment?           │
└─────────────────────────────────────────────────────────┘
```

### **Feedback Loop:**
- Layer 4 failures → New Layer 1 test cases
- Layer 2 surviving mutants → Enhance Layer 1 assertions
- Layer 0 complexity warnings → Additional Layer 3 path tests
- Layer 0.5 CVEs → Layer 4 integration tests for mitigations

---

## **PowerShell-Specific Adaptations**

Since PowerShell lacks mature mutation testing:

**Alternative Layer 2 Approach:**
1. **Assertion-Based Testing with Pester's Should Commands:**
   - Use comprehensive assertions (-Be, -BeOfType, -Match,
-Contain, -Throw)
   - Implement negative testing (test what *shouldn't* happen)

2. **Manual Mutation Testing for Critical Functions:**
   - Create test variants with intentional bugs
   - Verify tests catch them before removing mutations

3. **Property-Based Testing:**
   - Use **PSCheck** (if available) or custom property
generators
   - Generate random inputs to find edge cases tests miss

---

## **Comprehensive Coverage Metrics**

This 5-layer framework provides:

1. **Structural Metrics:** Line/branch/function coverage (Layer
 1)
2. **Quality Metrics:** Mutation score, surviving mutants
(Layer 2)
3. **Complexity Metrics:** Cyclomatic complexity, path coverage
 (Layers 0 & 3)
4. **Security Metrics:** SAST findings, CVE count (Layers 0 &
0.5)
5. **Operational Metrics:** NFR compliance, E2E success rate
(Layer 4)

**Result:** A deterministic, audit-trailed test execution that
identifies gaps at structural, behavioral, logical, security,
dependency, and operational levels in a single comprehensive


---

# Implementation Plan

## Executive Summary

This plan implements a **5-layer progressive test coverage framework** for the AI Development Pipeline.

**Pre-Execution Layers (Shift-Left Security):**
- Layer 0: Static Analysis (SAST) - Code quality & security
- Layer 0.5: Software Composition Analysis (SCA) - Dependency vulnerabilities

**Execution Layers (Dynamic Testing):**
- Layer 1: Structural Coverage - What code was executed
- Layer 2: Mutation Testing - Whether tests verify correctness
- Layer 3: Path Coverage - All logical paths exercised

**Post-Execution Layer (Production Readiness):**
- Layer 4: Operational Validation - System-level NFR testing

**Delivery:** 8 independent workstreams, 7 reusable patterns (EXEC-031 through EXEC-037), 10 implementation phases over 9-10 weeks.

---

## Independent Workstreams: Core Infrastructure → then WS2
  (Structural), WS3 (Mutation), WS4 (Complexity) in parallel →
  WS5 (Reporting/CLI)
  - 4 Reusable Patterns: EXEC-031 (Structural), EXEC-032
  (Mutation), EXEC-033 (Complexity), EXEC-034 (Combined)
  - 7 Implementation Phases: Progressive delivery over 6-7
  weeks
  - 32 Critical Files: ~6,500 total lines of code + tests +
  documentation
  - 90%+ Test Coverage Target: Quality gates enforced at each
  phase

  The plan is ready for execution with clear success criteria,
  testing strategy, and integration points with existing UET
  Framework infrastructure.

───────────────────────────────────────────────────────────────────
 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Test Coverage Analyzer Submodule - Implementation Plan

 Executive Summary

 Create a comprehensive test coverage analysis tool at
 tools/coverage_analyzer/ that implements three complementary
 methodologies for Python and PowerShell:
 1. Structural Coverage (statement + branch) - identifies what
 code was executed
 2. Mutation Testing - validates whether tests verify correctness
 3. Cyclomatic Complexity & Path Coverage - ensures all logical
 paths are tested

 Approach: Build all three methodologies together with parallel
 Python/PowerShell support. Focus on CLI usage first, defer CI
 integration.

 Delivery: 4 independent workstreams with reusable execution
 patterns (EXEC-031, EXEC-032, EXEC-033, EXEC-034).

 ---
 Module Structure

 tools/coverage_analyzer/
 ├── src/
 │   └── coverage_analyzer/
 │       ├── __init__.py                 # Public API:
 CoverageAnalyzer, AnalyzerRegistry, *Metrics
 │       ├── base.py                     # Data models:
 CoverageMetrics, MutationMetrics, ComplexityMetrics
 │       ├── registry.py                 # AnalyzerRegistry
 (adapter factory)
 │       ├── analyzers/
 │       │   ├── __init__.py
 │       │   ├── structural.py           #
 StructuralCoverageAnalyzer
 │       │   ├── mutation.py             # MutationTestingAnalyzer
 │       │   └── complexity.py           # ComplexityAnalyzer
 │       ├── adapters/
 │       │   ├── __init__.py
 │       │   ├── base_adapter.py         # Abstract BaseAdapter
 │       │   ├── coverage_py_adapter.py  # Python structural
 (coverage.py)
 │       │   ├── pester_adapter.py       # PowerShell structural
 (Pester)
 │       │   ├── mutmut_adapter.py       # Python mutation
 (mutmut)
 │       │   ├── radon_adapter.py        # Python complexity
 (radon)
 │       │   └── pssa_adapter.py         # PowerShell complexity
 (PSScriptAnalyzer)
 │       ├── reporters/
 │       │   ├── __init__.py
 │       │   ├── json_reporter.py        # JSON output
 │       │   ├── html_reporter.py        # HTML reports
 │       │   └── terminal_reporter.py    # Terminal output
 │       └── cli.py                      # Command-line interface
 ├── tests/
 │   ├── conftest.py                     # Fixtures:
 mock_coverage_config, sample_module, temp_project
 │   ├── test_base.py                    # Data model tests
 │   ├── test_registry.py                # Registry tests
 │   ├── analyzers/
 │   │   ├── test_structural.py
 │   │   ├── test_mutation.py
 │   │   └── test_complexity.py
 │   ├── adapters/
 │   │   ├── test_coverage_py_adapter.py
 │   │   ├── test_pester_adapter.py
 │   │   ├── test_mutmut_adapter.py
 │   │   ├── test_radon_adapter.py
 │   │   └── test_pssa_adapter.py
 │   ├── reporters/
 │   │   ├── test_json_reporter.py
 │   │   ├── test_html_reporter.py
 │   │   └── test_terminal_reporter.py
 │   └── test_cli.py
 ├── docs/
 │   ├── architecture.md                 # Design and components
 │   ├── usage.md                        # CLI reference and
 examples
 │   └── methodologies.md                # Coverage methodology
 explanations
 ├── config/
 │   └── coverage_analyzer.yaml          # Default configuration
 └── README.md                            # Module overview

 Integration Point: Add to tools/__init__.py exports

 ---
 Independent Workstreams

 Workstream 1: Core Infrastructure (Foundation)

 Owner: Can be developed independently
 Dependencies: None
 Files:
 - src/coverage_analyzer/base.py - Data models (CoverageMetrics,
 MutationMetrics, ComplexityMetrics, AnalysisConfiguration)
 - src/coverage_analyzer/registry.py - AnalyzerRegistry
 - src/coverage_analyzer/adapters/base_adapter.py - Abstract
 BaseAdapter
 - tests/test_base.py, tests/test_registry.py
 - config/coverage_analyzer.yaml

 Deliverable: Foundation classes and data models that all other
 workstreams depend on

 Test Coverage Target: 95%+

 ---
 Workstream 2: Structural Coverage (Python + PowerShell)

 Owner: Can be developed in parallel with WS3, WS4
 Dependencies: WS1 (core infrastructure)
 Files:
 - src/coverage_analyzer/analyzers/structural.py
 - src/coverage_analyzer/adapters/coverage_py_adapter.py (Python)
 - src/coverage_analyzer/adapters/pester_adapter.py (PowerShell)
 - tests/analyzers/test_structural.py
 - tests/adapters/test_coverage_py_adapter.py
 - tests/adapters/test_pester_adapter.py

 Key Pattern:
 # Execute coverage.py for Python
 subprocess.run(["coverage", "run", "-m", "pytest", test_path],
 ...)
 subprocess.run(["coverage", "json", "-o", output_path], ...)

 # Execute Pester for PowerShell
 subprocess.run(["pwsh", "-NoProfile", "-Command",
                 "Invoke-Pester -Path test_path -CodeCoverage
 script_path -Output Detailed"], ...)

 Deliverable: Working structural coverage analysis for both Python
  and PowerShell

 Test Coverage Target: 90%+

 ---
 Workstream 3: Mutation Testing (Python + PowerShell)

 Owner: Can be developed in parallel with WS2, WS4
 Dependencies: WS1 (core infrastructure)
 Files:
 - src/coverage_analyzer/analyzers/mutation.py
 - src/coverage_analyzer/adapters/mutmut_adapter.py (Python)
 - tests/analyzers/test_mutation.py
 - tests/adapters/test_mutmut_adapter.py

 Key Pattern:
 # Execute mutmut for Python
 subprocess.run(["mutmut", "run", "--paths-to-mutate",
 module_path], ...)
 subprocess.run(["mutmut", "results"], ...)  # Get mutation score

 # PowerShell: Manual mutation patterns (optional, limited
 tooling)
 # Document approach in docs/methodologies.md

 Deliverable: Working mutation testing analysis for Python
 (PowerShell: documented approach)

 Test Coverage Target: 85%+ (PowerShell deferred)

 ---
 Workstream 4: Complexity & Path Coverage (Python + PowerShell)

 Owner: Can be developed in parallel with WS2, WS3
 Dependencies: WS1 (core infrastructure)
 Files:
 - src/coverage_analyzer/analyzers/complexity.py
 - src/coverage_analyzer/adapters/radon_adapter.py (Python)
 - src/coverage_analyzer/adapters/pssa_adapter.py (PowerShell)
 - tests/analyzers/test_complexity.py
 - tests/adapters/test_radon_adapter.py
 - tests/adapters/test_pssa_adapter.py

 Key Pattern:
 # Calculate complexity with radon (Python)
 subprocess.run(["radon", "cc", "-j", module_path], ...)  #
 Cyclomatic complexity
 subprocess.run(["radon", "mi", "-j", module_path], ...)  #
 Maintainability index

 # Analyze with PSScriptAnalyzer (PowerShell)
 subprocess.run(["pwsh", "-NoProfile", "-Command",
                 "Invoke-ScriptAnalyzer -Path script_path
 -IncludeRule PSAvoidUsingCmdletAliases"], ...)

 Deliverable: Working complexity analysis for both Python and
 PowerShell

 Test Coverage Target: 90%+

 ---
 Workstream 5: Reporting & CLI (Integration Layer)

 Owner: Depends on all other workstreams
 Dependencies: WS1, WS2, WS3, WS4
 Files:
 - src/coverage_analyzer/reporters/json_reporter.py
 - src/coverage_analyzer/reporters/html_reporter.py
 - src/coverage_analyzer/reporters/terminal_reporter.py
 - src/coverage_analyzer/cli.py
 - tests/reporters/test_json_reporter.py
 - tests/reporters/test_html_reporter.py
 - tests/reporters/test_terminal_reporter.py
 - tests/test_cli.py

 CLI Interface:
 # Run all analyses
 python -m coverage_analyzer analyze --path=core/ --output=json

 # Run specific analysis
 python -m coverage_analyzer structural --path=core/
 --language=python
 python -m coverage_analyzer mutation --path=core/
 python -m coverage_analyzer complexity --path=core/
 --threshold=10

 # Generate reports
 python -m coverage_analyzer report --format=html
 --output=coverage_report.html

 Deliverable: Complete CLI with all reporting formats

 Test Coverage Target: 85%+

 ---
 Reusable Execution Patterns

 Pattern: EXEC-031 - Structural Coverage Analysis

 Purpose: Execute structural coverage analysis (statement +
 branch) for a module
 Location:
 patterns/specs/EXEC-031_structural_coverage.pattern.yaml
 Executor:
 patterns/executors/EXEC-031_structural_coverage_executor.ps1

 Inputs:
 - target_path - Module path to analyze
 - language - "python" or "powershell"
 - output_format - "json", "html", or "terminal"

 Outputs:
 - Coverage metrics (statement %, branch %, function %)
 - Untested files list
 - Coverage report in specified format

 Success Criteria: Exit code 0, coverage report generated

 ---
 Pattern: EXEC-032 - Mutation Testing

 Purpose: Execute mutation testing to validate test quality
 Location: patterns/specs/EXEC-032_mutation_testing.pattern.yaml
 Executor:
 patterns/executors/EXEC-032_mutation_testing_executor.ps1

 Inputs:
 - target_path - Module path to mutate
 - language - "python" (PowerShell not supported)
 - output_format - "json", "html", or "terminal"

 Outputs:
 - Mutation score (killed %, survived %, timeout %)
 - List of survived mutants
 - Test quality report

 Success Criteria: Exit code 0, mutation report generated

 ---
 Pattern: EXEC-033 - Complexity Analysis

 Purpose: Analyze cyclomatic complexity and identify
 high-complexity functions
 Location:
 patterns/specs/EXEC-033_complexity_analysis.pattern.yaml
 Executor:
 patterns/executors/EXEC-033_complexity_analysis_executor.ps1

 Inputs:
 - target_path - Module path to analyze
 - language - "python" or "powershell"
 - complexity_threshold - Flag functions above this threshold
 (default: 10)
 - output_format - "json", "html", or "terminal"

 Outputs:
 - Complexity metrics by function/file
 - List of high-complexity functions
 - Recommendations for additional testing

 Success Criteria: Exit code 0, complexity report generated

 ---
 Pattern: EXEC-034 - Combined Coverage Report

 Purpose: Execute all three analyses and generate comprehensive
 coverage report
 Location: patterns/specs/EXEC-034_combined_coverage.pattern.yaml
 Executor:
 patterns/executors/EXEC-034_combined_coverage_executor.ps1

 Inputs:
 - target_path - Module path to analyze
 - language - "python" or "powershell"
 - output_format - "json", "html", or "terminal"

 Outputs:
 - Combined report with all three methodologies
 - Overall test quality score (0-100)
 - Prioritized recommendations

 Success Criteria: Exit code 0, all three analyses complete,
 combined report generated

 ---
 Implementation Phases

 Phase 1: Core Infrastructure (Week 1)

 Workstream: WS1
 Goal: Foundation classes and data models

 Tasks:
 1. Create module structure:
 tools/coverage_analyzer/src/coverage_analyzer/
 2. Implement data models in base.py:
   - CoverageMetrics (statement_pct, branch_pct, function_pct,
 missing_lines)
   - MutationMetrics (total, killed, survived, timeout, score)
   - ComplexityMetrics (avg_complexity, max_complexity,
 high_complexity_functions)
   - AnalysisConfiguration (target_path, language, output_format,
 thresholds)
   - CoverageReport (combines all metrics)
 3. Implement AnalyzerRegistry in registry.py
 4. Implement BaseAdapter abstract class in
 adapters/base_adapter.py
 5. Create default configuration: config/coverage_analyzer.yaml
 6. Write tests: tests/test_base.py, tests/test_registry.py
 7. Create tests/conftest.py with shared fixtures

 Success Criteria:
 - All data models defined with type hints
 - Registry can register and retrieve adapters
 - Tests pass (pytest tests/test_base.py tests/test_registry.py
 -q)
 - 95%+ test coverage for Phase 1 files

 ---
 Phase 2: Structural Coverage - Python (Week 2)

 Workstream: WS2 (Python portion)
 Goal: Working structural coverage for Python using coverage.py

 Tasks:
 1. Implement StructuralCoverageAnalyzer in
 analyzers/structural.py
 2. Implement CoveragePyAdapter in
 adapters/coverage_py_adapter.py:
   - Tool availability check: shutil.which("coverage")
   - Execute: coverage run -m pytest <test_path>
   - Generate JSON: coverage json -o <output_path>
   - Parse JSON output to CoverageMetrics
 3. Write tests: tests/analyzers/test_structural.py,
 tests/adapters/test_coverage_py_adapter.py
 4. Mock subprocess.run() in tests with sample coverage.py output

 Success Criteria:
 - Can analyze Python modules with pytest + coverage.py
 - Returns accurate CoverageMetrics
 - Handles missing coverage tool gracefully
 - Tests pass with 90%+ coverage

 ---
 Phase 3: Structural Coverage - PowerShell (Week 2-3)

 Workstream: WS2 (PowerShell portion)
 Goal: Working structural coverage for PowerShell using Pester

 Tasks:
 1. Implement PesterAdapter in adapters/pester_adapter.py:
   - Tool availability check: shutil.which("pwsh")
   - Execute Pester with CodeCoverage: Invoke-Pester -CodeCoverage
  <script_path>
   - Parse Pester output to CoverageMetrics
   - Handle Pester JSON/XML output format
 2. Write tests: tests/adapters/test_pester_adapter.py
 3. Mock pwsh execution with sample Pester output

 Success Criteria:
 - Can analyze PowerShell scripts with Pester
 - Returns accurate CoverageMetrics compatible with Python format
 - Tests pass with 90%+ coverage
 - Handles Windows/cross-platform differences

 ---
 Phase 4: Mutation Testing - Python (Week 3)

 Workstream: WS3
 Goal: Working mutation testing for Python using mutmut

 Tasks:
 1. Implement MutationTestingAnalyzer in analyzers/mutation.py
 2. Implement MutmutAdapter in adapters/mutmut_adapter.py:
   - Tool availability check: shutil.which("mutmut")
   - Execute: mutmut run --paths-to-mutate <module_path>
   - Parse results: mutmut results or mutmut json-report
   - Generate MutationMetrics
 3. Write tests: tests/analyzers/test_mutation.py,
 tests/adapters/test_mutmut_adapter.py
 4. Document PowerShell mutation approach in docs/methodologies.md
  (manual patterns)

 Success Criteria:
 - Can run mutation testing on Python modules
 - Returns accurate MutationMetrics (killed, survived, timeout,
 score)
 - Tests pass with 85%+ coverage
 - Documentation explains PowerShell limitations

 ---
 Phase 5: Complexity Analysis (Week 4)

 Workstream: WS4
 Goal: Working complexity analysis for Python and PowerShell

 Tasks:
 1. Implement ComplexityAnalyzer in analyzers/complexity.py
 2. Implement RadonAdapter for Python in
 adapters/radon_adapter.py:
   - Tool availability: shutil.which("radon")
   - Execute: radon cc -j <module_path> (cyclomatic complexity)
   - Execute: radon mi -j <module_path> (maintainability index)
   - Parse JSON to ComplexityMetrics
 3. Implement PSSAAdapter for PowerShell in
 adapters/pssa_adapter.py:
   - Tool availability: shutil.which("pwsh")
   - Execute: Invoke-ScriptAnalyzer -Path <script_path>
   - Parse output to identify high-complexity functions
   - Generate ComplexityMetrics
 4. Write tests for all complexity adapters

 Success Criteria:
 - Can calculate complexity for Python and PowerShell
 - Identifies high-complexity functions (threshold configurable)
 - Tests pass with 90%+ coverage
 - Complexity scores align with actual code structure

 ---
 Phase 6: Reporting & CLI (Week 5)

 Workstream: WS5
 Goal: Complete CLI interface with all reporting formats

 Tasks:
 1. Implement reporters:
   - json_reporter.py - Serialize to JSON
   - html_reporter.py - Generate HTML with charts
   - terminal_reporter.py - Colored terminal output
 2. Implement cli.py with argparse:
   - Commands: analyze, structural, mutation, complexity, report
   - Options: --path, --language, --format, --output, --threshold
 3. Add entry point in src/coverage_analyzer/__init__.py
 4. Write comprehensive CLI tests: tests/test_cli.py
 5. Test end-to-end workflows

 Success Criteria:
 - CLI accepts all commands and options
 - All reporting formats work correctly
 - Help text is clear and accurate
 - Tests pass with 85%+ coverage
 - Can run from command line: python -m coverage_analyzer

 ---
 Phase 7: Execution Patterns & Documentation (Week 6)

 Goal: Reusable patterns and comprehensive documentation

 Tasks:
 1. Create pattern specifications (YAML):
   - patterns/specs/EXEC-031_structural_coverage.pattern.yaml
   - patterns/specs/EXEC-032_mutation_testing.pattern.yaml
   - patterns/specs/EXEC-033_complexity_analysis.pattern.yaml
   - patterns/specs/EXEC-034_combined_coverage.pattern.yaml
 2. Create executors (PowerShell):
   - patterns/executors/EXEC-031_structural_coverage_executor.ps1
   - patterns/executors/EXEC-032_mutation_testing_executor.ps1
   - patterns/executors/EXEC-033_complexity_analysis_executor.ps1
   - patterns/executors/EXEC-034_combined_coverage_executor.ps1
 3. Write documentation:
   - README.md - Module overview, quick start
   - docs/architecture.md - Design, components, data flow
   - docs/usage.md - CLI reference, examples
   - docs/methodologies.md - Explanation of three coverage
 approaches
 4. Test all patterns execute standalone

 Success Criteria:
 - All patterns execute via ./patterns/executors/EXEC-0XX_*.ps1
 - Documentation is comprehensive and accurate
 - Examples work as written
 - Patterns follow existing UET pattern format

 ---
 Critical Files to Create

 Priority 1 - Foundation (Phase 1)

 1. tools/coverage_analyzer/src/coverage_analyzer/base.py (~200
 lines)
 2. tools/coverage_analyzer/src/coverage_analyzer/registry.py
 (~100 lines)
 3. tools/coverage_analyzer/src/coverage_analyzer/adapters/base_ad
 apter.py (~80 lines)
 4. tools/coverage_analyzer/config/coverage_analyzer.yaml (~60
 lines)
 5. tools/coverage_analyzer/tests/conftest.py (~120 lines)

 Priority 2 - Structural Coverage (Phase 2-3)

 6. tools/coverage_analyzer/src/coverage_analyzer/analyzers/struct
 ural.py (~150 lines)
 7. tools/coverage_analyzer/src/coverage_analyzer/adapters/coverag
 e_py_adapter.py (~200 lines)
 8. tools/coverage_analyzer/src/coverage_analyzer/adapters/pester_
 adapter.py (~220 lines)
 9. tools/coverage_analyzer/tests/adapters/test_coverage_py_adapte
 r.py (~180 lines)
 10. tools/coverage_analyzer/tests/adapters/test_pester_adapter.py
  (~200 lines)

 Priority 3 - Mutation & Complexity (Phase 4-5)

 11. tools/coverage_analyzer/src/coverage_analyzer/analyzers/mutat
 ion.py (~130 lines)
 12. tools/coverage_analyzer/src/coverage_analyzer/adapters/mutmut
 _adapter.py (~180 lines)
 13. tools/coverage_analyzer/src/coverage_analyzer/analyzers/compl
 exity.py (~160 lines)
 14. tools/coverage_analyzer/src/coverage_analyzer/adapters/radon_
 adapter.py (~200 lines)
 15. tools/coverage_analyzer/src/coverage_analyzer/adapters/pssa_a
 dapter.py (~210 lines)

 Priority 4 - Reporting & CLI (Phase 6)

 16. tools/coverage_analyzer/src/coverage_analyzer/reporters/json_
 reporter.py (~80 lines)
 17. tools/coverage_analyzer/src/coverage_analyzer/reporters/html_
 reporter.py (~250 lines)
 18. tools/coverage_analyzer/src/coverage_analyzer/reporters/termi
 nal_reporter.py (~180 lines)
 19. tools/coverage_analyzer/src/coverage_analyzer/cli.py (~300
 lines)
 20. tools/coverage_analyzer/tests/test_cli.py (~250 lines)

 Priority 5 - Patterns & Documentation (Phase 7)

 21. patterns/specs/EXEC-031_structural_coverage.pattern.yaml (~80
  lines)
 22. patterns/executors/EXEC-031_structural_coverage_executor.ps1
 (~120 lines)
 23. patterns/specs/EXEC-032_mutation_testing.pattern.yaml (~75
 lines)
 24. patterns/executors/EXEC-032_mutation_testing_executor.ps1
 (~100 lines)
 25. patterns/specs/EXEC-033_complexity_analysis.pattern.yaml (~80
  lines)
 26. patterns/executors/EXEC-033_complexity_analysis_executor.ps1
 (~110 lines)
 27. patterns/specs/EXEC-034_combined_coverage.pattern.yaml (~90
 lines)
 28. patterns/executors/EXEC-034_combined_coverage_executor.ps1
 (~150 lines)
 29. tools/coverage_analyzer/README.md (~250 lines)
 30. tools/coverage_analyzer/docs/architecture.md (~300 lines)
 31. tools/coverage_analyzer/docs/usage.md (~400 lines)
 32. tools/coverage_analyzer/docs/methodologies.md (~350 lines)

 Total New Files: 32 primary files + 15 additional test files = 47
  files
 Estimated Total Lines: ~6,500 lines of code + tests +
 documentation

 ---
 Testing Strategy

 Test Organization

 tools/coverage_analyzer/tests/
 ├── conftest.py              # Shared fixtures
 ├── test_base.py             # Data model tests
 ├── test_registry.py         # Registry tests
 ├── analyzers/               # Analyzer tests
 ├── adapters/                # Adapter tests (subprocess mocking)
 ├── reporters/               # Reporter tests
 └── test_cli.py              # CLI integration tests

 Key Fixtures (conftest.py)

 @pytest.fixture
 def mock_coverage_config():
     """Mock configuration with test defaults"""
     return AnalysisConfiguration(...)

 @pytest.fixture
 def sample_python_module(tmp_path):
     """Create a sample Python module for testing"""
     # Creates temp Python files with known coverage
 characteristics

 @pytest.fixture
 def sample_powershell_script(tmp_path):
     """Create a sample PowerShell script for testing"""
     # Creates temp .ps1 files with known coverage characteristics

 @pytest.fixture
 def mock_coverage_py_output():
     """Sample coverage.py JSON output"""
     return {...}  # Realistic coverage JSON

 @pytest.fixture
 def mock_pester_output():
     """Sample Pester coverage output"""
     return {...}  # Realistic Pester XML/JSON

 @pytest.fixture
 def mock_mutmut_output():
     """Sample mutmut results"""
     return {...}  # Realistic mutation results

 @pytest.fixture
 def mock_radon_output():
     """Sample radon complexity JSON"""
     return {...}  # Realistic complexity metrics

 Mocking Strategy

 Adapter Tests: Mock subprocess.run() with realistic tool output
 def test_coverage_py_adapter(mocker, mock_coverage_py_output):
     mock_run = mocker.patch('subprocess.run')
     mock_run.return_value.returncode = 0
     mock_run.return_value.stdout =
 json.dumps(mock_coverage_py_output)

     adapter = CoveragePyAdapter(config)
     result = adapter.execute(request)

     assert result.success
     assert result.metrics.statement_pct == 85.5

 CLI Tests: Use click.testing.CliRunner
 def test_cli_analyze_command():
     runner = CliRunner()
     result = runner.invoke(cli, ['analyze', '--path=core/',
 '--format=json'])
     assert result.exit_code == 0
     assert 'coverage_metrics' in result.output

 Test Coverage Targets

 - Core Infrastructure (WS1): 95%+ coverage
 - Adapters (WS2, WS3, WS4): 90%+ coverage
 - Analyzers (WS2, WS3, WS4): 90%+ coverage
 - Reporters (WS5): 85%+ coverage
 - CLI (WS5): 85%+ coverage
 - Overall Module: 90%+ coverage

 Integration Testing

 - Test end-to-end workflows with real tools (conditional on tool
 availability)
 - Skip tests if tools not installed: @pytest.mark.skipif(not
 tool_available("coverage"))
 - Test pattern executors in real environment

 ---
 Success Criteria

 Phase Completion Criteria

 Phase 1 Complete When:
 - All data models defined in base.py
 - Registry can register/retrieve adapters
 - BaseAdapter abstract class defined
 - Tests pass: pytest tests/test_base.py tests/test_registry.py -q
 - Coverage ≥ 95% for Phase 1 files

 Phase 2 Complete When:
 - Can analyze Python modules with coverage.py
 - Returns accurate CoverageMetrics
 - Tests pass: pytest tests/adapters/test_coverage_py_adapter.py
 -q
 - Coverage ≥ 90% for Python structural files

 Phase 3 Complete When:
 - Can analyze PowerShell scripts with Pester
 - Returns CoverageMetrics compatible with Python
 - Tests pass: pytest tests/adapters/test_pester_adapter.py -q
 - Coverage ≥ 90% for PowerShell structural files

 Phase 4 Complete When:
 - Can run mutation testing with mutmut
 - Returns accurate MutationMetrics
 - Tests pass: pytest tests/adapters/test_mutmut_adapter.py -q
 - Coverage ≥ 85% for mutation files
 - PowerShell approach documented

 Phase 5 Complete When:
 - Can calculate complexity for Python and PowerShell
 - Identifies high-complexity functions
 - Tests pass: pytest tests/adapters/test_radon_adapter.py
 tests/adapters/test_pssa_adapter.py -q
 - Coverage ≥ 90% for complexity files

 Phase 6 Complete When:
 - CLI accepts all commands
 - All reporting formats work (JSON, HTML, terminal)
 - Tests pass: pytest tests/test_cli.py -q
 - Coverage ≥ 85% for CLI files
 - Can run: python -m coverage_analyzer analyze --path=core/

 Phase 7 Complete When:
 - All 4 execution patterns execute standalone
 - Pattern specs follow UET format
 - Documentation complete (README, architecture, usage,
 methodologies)
 - Examples in docs work as written

 Overall Success Criteria

 Module Complete When:
 - All 196 existing tests still pass
 - New module has 90%+ test coverage
 - All 4 EXEC-* patterns execute successfully
 - CLI works for all three methodologies (Python + PowerShell)
 - Documentation is comprehensive
 - Can analyze the coverage_analyzer module itself (dogfooding)
 - Integration with tools/init.py complete

 Quality Gates

 Before Each Commit:
 # All tests must pass
 pytest tests/ -q

 # New module tests must pass
 pytest tools/coverage_analyzer/tests/ -q

 # No deprecated import paths
 python scripts/paths_index_cli.py gate --db refactor_paths.db

 # Coverage check (after Phase 6)
 python -m coverage_analyzer analyze
 --path=tools/coverage_analyzer/ --language=python

 Performance Benchmarks:
 - Structural coverage analysis: < 30 seconds for 10,000 LOC
 module
 - Mutation testing: < 5 minutes for 1,000 LOC module
 - Complexity analysis: < 10 seconds for 10,000 LOC module
 - Combined report generation: < 1 minute

 ---
 Integration Points

 With Existing Infrastructure

 Test Configuration (pytest.ini):
 - Module tests use existing pytest configuration
 - Support existing markers (unit, integration, etc.)
 - Compatible with multiple pytest.ini files (root, CI,
 project-specific)

 Adapter Pattern (follows core/adapters/):
 - Use SubprocessAdapter pattern for tool execution
 - Use Registry pattern for adapter management
 - Follow ExecutionResult data structure

 Import Standards:
 # Correct imports
 from tools.coverage_analyzer import CoverageAnalyzer,
 AnalyzerRegistry
 from tools.coverage_analyzer.base import CoverageMetrics,
 MutationMetrics
 from tools.coverage_analyzer.adapters import CoveragePyAdapter

 # Add to tools/__init__.py
 from tools.coverage_analyzer import CoverageAnalyzer,
 AnalyzerRegistry

 Documentation Standards:
 - Add DOC_ID comments linking to specs
 - Follow existing markdown structure
 - Include architecture.md and usage.md
 - Cross-reference with existing docs

 Future CI Integration (Deferred)

 When Ready (Phase 8 - Future):
 - Create .github/workflows/coverage-analysis.yml
 - Add coverage checks to PR workflow
 - Generate coverage comments on PRs
 - Track coverage trends in database

 ---
 Key Architectural Decisions

 1. Location: tools/coverage_analyzer/ - Treats as development
 tool, not phase module
 2. Parallel Language Support: Python and PowerShell adapters
 developed simultaneously
 3. Three-Layer Result Pattern: ToolResult → ExecutionResult →
 CoverageReport
 4. Registry Pattern: Central adapter management with discovery
 5. CLI-First: Focus on local usage before CI automation
 6. Subprocess Execution: All external tools via subprocess.run()
 with mocking in tests
 7. JSON as Primary Output: Structured data for programmatic
 access
 8. Progressive Enhancement: HTML and terminal output as secondary
  formats

 ---
 Next Steps

 1. Start with Phase 1: Build core infrastructure (base.py,
 registry.py, base_adapter.py)
 2. Parallel Development: After Phase 1, kickoff WS2, WS3, WS4
 simultaneously
 3. Test as You Go: 90%+ coverage requirement for each phase
 4. Document Progressively: Update docs/ as features are
 implemented
 5. Dogfood Early: Use the tool to analyze itself starting in
 Phase 6

 Estimated Timeline: 6-7 weeks for full implementation with
 comprehensive testing and documentation.

 Ready to Execute: This plan is complete and actionable. Begin
 with Phase 1 (Core Infrastructure) and expand to parallel
 workstreams.
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Would you like to proceed?

 ❯ 1. Yes, and bypass permissions
   2. Yes, and manually approve edits
  3. Type here to tell Claude what to change


 ctrl-g to edit in Notepad
