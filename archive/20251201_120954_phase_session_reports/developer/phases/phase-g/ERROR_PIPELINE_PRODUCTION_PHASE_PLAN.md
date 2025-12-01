---
doc_id: DOC-GUIDE-ERROR-PIPELINE-PRODUCTION-PHASE-PLAN-1285
---

# Error Pipeline Production Readiness Phase Plan

**Document ID**: ERROR-PROD-PLAN-001  
**Created**: 2025-11-20  
**Status**: DRAFT  
**Version**: 1.0.0  
**Dependencies**: [ERROR_PIPELINE_EVALUATION.md](./ERROR_PIPELINE_EVALUATION.md)  
**Estimated Total Effort**: 80-100 hours (2-3 sprints)

---

## Executive Summary

This phase plan transforms the error pipeline from **B+ (85/100) architectural prototype** to **production-ready validation system**. Based on the comprehensive evaluation, this plan addresses critical gaps through 4 focused phases:

- **Phase G1**: Critical Fixes (Priority 1-2 issues) - 16-20 hours
- **Phase G2**: Integration & Testing - 24-32 hours  
- **Phase G3**: Production Hardening - 24-32 hours
- **Phase G4**: Observability & Operations - 16-24 hours

**Success Criteria**: System achieves **A- (90/100)** with full AI agent integration, 80%+ test coverage, production monitoring, and documentation completeness.

---

## Phase Dependencies

```
Phase E (Refactor) ✅ COMPLETE
         ↓
    Phase G1: Critical Fixes (BLOCKING)
         ↓
    Phase G2: Integration & Testing (BLOCKING)
         ↓
    Phase G3: Production Hardening (PARALLEL)
         ↓          ↓
  G3a: Performance  G3b: Security
         ↓
    Phase G4: Observability (OPTIONAL)
```

---

## Phase G1: Critical Fixes & Foundation

**Priority**: 🔴 CRITICAL  
**Estimated Effort**: 16-20 hours  
**Risk Level**: LOW  
**Blockers**: None  

### Objective

Fix all Priority 1-2 issues from evaluation to establish stable foundation for integration work.

### Workstreams

#### WS-G1.1: Fix Import Path Standards (4-6 hours)

**Issue**: Import paths broken across tests and CLI scripts  
**Impact**: Tests cannot run, CLI scripts fail  

**Tasks:**
1. Audit all `error/` module imports
2. Update `scripts/run_error_engine.py`:
   ```python
   # OLD (broken)
   from error.pipeline_engine import PipelineEngine
   from error.plugin_manager import PluginManager
   
   # NEW (correct)
   from error.engine.pipeline_engine import PipelineEngine
   from error.engine.plugin_manager import PluginManager
   from error.engine.file_hash_cache import FileHashCache
   ```
3. Update all test files in `tests/`:
   - `test_ci_path_standards.py`
   - `test_engine_determinism.py`
   - `test_incremental_cache.py`
4. Create import validator script:
   ```python
   # scripts/validate_error_imports.py
   # Check all imports follow error.{engine|plugins|shared}.* pattern
   ```
5. Add to CI pipeline (`.github/workflows/path_standards.yml`)
6. Run full test suite: `pytest tests/ -k error -v`

**Acceptance Criteria:**
- [ ] All `error/` imports use full paths (`error.engine.*`, `error.plugins.*`, `error.shared.*`)
- [ ] `scripts/run_error_engine.py` executes without import errors
- [ ] All error-related tests pass
- [ ] CI gate prevents future violations

**Deliverables:**
- Updated `scripts/run_error_engine.py`
- Fixed test files (3-5 files)
- `scripts/validate_error_imports.py`
- CI workflow update

---

#### WS-G1.2: Fix Plugin Discovery Path (2-3 hours)

**Issue**: `PluginManager` looks for plugins in wrong directory  
**Impact**: Plugins not discovered, validation fails  

**Tasks:**
1. Update `error/engine/plugin_manager.py:22`:
   ```python
   # OLD
   self._plugins_path = plugins_path or (Path.cwd() / "src" / "plugins")
   
   # NEW
   self._plugins_path = plugins_path or (Path(__file__).parent.parent / "plugins")
   ```
2. Add environment variable override:
   ```python
   default_path = Path(__file__).parent.parent / "plugins"
   env_path = os.getenv("PIPELINE_ERROR_PLUGINS_PATH")
   self._plugins_path = plugins_path or (Path(env_path) if env_path else default_path)
   ```
3. Update plugin discovery tests
4. Test with all 21 plugins
5. Document plugin path configuration in README

**Acceptance Criteria:**
- [ ] Plugins discovered from `error/plugins/` by default
- [ ] `PIPELINE_ERROR_PLUGINS_PATH` override works
- [ ] All 21 plugins load successfully
- [ ] Discovery tests pass

**Deliverables:**
- Updated `error/engine/plugin_manager.py`
- Environment variable documentation
- Plugin discovery tests

---

#### WS-G1.3: Create Error Pipeline README (4-5 hours)

**Issue**: No high-level documentation for error pipeline  
**Impact**: New contributors cannot understand system  

**Tasks:**
1. Create `error/README.md` with sections:
   - **Overview** - Purpose and capabilities
   - **Architecture** - State machine diagram (ASCII art)
   - **Quick Start** - Basic usage examples
   - **Plugin System** - How plugins work
   - **State Machine** - Escalation flow explanation
   - **Integration** - How to use from core pipeline
   - **Configuration** - Environment variables
   - **Development** - Adding new plugins
   - **Troubleshooting** - Common issues
2. Create ASCII state machine diagram:
   ```
   S_INIT → S0_BASELINE_CHECK
              ↓ (issues)
           S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK
              ↓ (still failing)
           S1_AIDER_FIX → S1_AIDER_RECHECK
              ↓ (still failing)
           S2_CODEX_FIX → S2_CODEX_RECHECK
              ↓ (still failing)
           S3_CLAUDE_FIX → S3_CLAUDE_RECHECK
              ↓ (still failing)
           S4_QUARANTINE
   
   Any RECHECK → S_SUCCESS (if 0 issues)
   ```
3. Add plugin development tutorial
4. Document Operating Contract schema
5. Add troubleshooting section

**Acceptance Criteria:**
- [ ] README covers all major components
- [ ] Code examples work when copy-pasted
- [ ] State machine flow is clear
- [ ] Plugin development guide complete
- [ ] Links to all sub-documentation

**Deliverables:**
- `error/README.md` (comprehensive)
- Plugin development tutorial
- State machine diagram

---

#### WS-G1.4: Create Error Pipeline Tests Foundation (6-8 hours)

**Issue**: Missing integration tests for state machine flow  
**Impact**: Cannot verify system works end-to-end  

**Tasks:**
1. Create `tests/error/` directory structure:
   ```
   tests/error/
   ├── __init__.py
   ├── conftest.py              # Shared fixtures
   ├── unit/
   │   ├── test_state_machine.py
   │   ├── test_plugin_manager.py
   │   ├── test_hash_cache.py
   │   └── test_error_context.py
   └── integration/
       ├── test_full_pipeline.py
       ├── test_ai_escalation.py
       └── fixtures/
           ├── sample.py        # Valid Python file
           └── broken.py        # File with errors
   ```
2. Create fixtures in `conftest.py`:
   ```python
   @pytest.fixture
   def mock_plugin_manager():
       """Mock plugin manager with test plugins"""
       
   @pytest.fixture
   def error_context():
       """Standard error context for tests"""
       
   @pytest.fixture
   def temp_cache(tmp_path):
       """Temporary hash cache"""
   ```
3. Write state machine unit tests:
   - Test all state transitions
   - Test escalation logic
   - Test strict mode vs permissive
   - Test early exit on success
4. Write plugin manager tests:
   - Test plugin discovery
   - Test dependency resolution
   - Test file extension filtering
5. Write integration tests (with mocks for AI agents)
6. Update `pytest.ini` to include error tests

**Acceptance Criteria:**
- [ ] State machine tests cover all transitions
- [ ] Plugin manager tests achieve 80%+ coverage
- [ ] Integration tests pass with mocked AI
- [ ] Tests run in CI
- [ ] Coverage report generated

**Deliverables:**
- `tests/error/` directory with 8-10 test files
- Test fixtures and mocks
- Updated `pytest.ini`
- Coverage configuration

---

### Phase G1 Acceptance Criteria

**Exit Criteria:**
- [ ] All imports use correct paths (`error.engine.*`, `error.plugins.*`)
- [ ] Plugins discovered from correct directory
- [ ] `error/README.md` exists and is comprehensive
- [ ] Test suite passes: `pytest tests/error/ -v`
- [ ] Code coverage ≥ 60% for `error/` package
- [ ] CI gates prevent import violations
- [ ] All Priority 1 issues resolved

**Validation Commands:**
```bash
# 1. Validate imports
python scripts/validate_error_imports.py

# 2. Run error tests
pytest tests/error/ -v --cov=error --cov-report=term

# 3. Test CLI
python scripts/run_error_engine.py tests/error/fixtures/sample.py

# 4. Check plugin discovery
python -c "from error.engine.plugin_manager import PluginManager; pm = PluginManager(); pm.discover(); print(f'{len(pm._plugins)} plugins loaded')"
```

---

## Phase G2: AI Agent Integration & Testing

**Priority**: 🔴 CRITICAL  
**Estimated Effort**: 24-32 hours  
**Risk Level**: MEDIUM  
**Blockers**: Phase G1  

### Objective

Implement missing AI agent integration layer to enable automated error remediation.

### Workstreams

#### WS-G2.1: Create Agent Adapter Interface (6-8 hours)

**Issue**: State machine has fix states but no actual agent invocation  
**Impact**: Errors cannot be automatically fixed  

**Tasks:**
1. Create `error/engine/agent_adapters.py`:
   ```python
   from dataclasses import dataclass
   from typing import List, Dict, Any, Optional
   from pathlib import Path
   
   @dataclass
   class AgentInvocation:
       agent_name: str
       files: List[str]
       error_report: Dict[str, Any]
       prompt_template: Optional[str] = None
       timeout_seconds: int = 300
   
   @dataclass
   class AgentResult:
       success: bool
       files_modified: List[str]
       stdout: str
       stderr: str
       duration_ms: int
       metadata: Dict[str, Any]
   
   class AgentAdapter:
       """Base class for AI agent adapters"""
       def invoke(self, invocation: AgentInvocation) -> AgentResult:
           raise NotImplementedError
   ```
2. Implement Aider adapter:
   ```python
   class AiderAdapter(AgentAdapter):
       def invoke(self, invocation: AgentInvocation) -> AgentResult:
           # 1. Format error report into prompt
           # 2. Call Aider CLI
           # 3. Parse output
           # 4. Return result
   ```
3. Implement Codex (GitHub Copilot CLI) adapter
4. Implement Claude adapter (via API)
5. Create adapter factory:
   ```python
   def get_agent_adapter(agent_name: str) -> AgentAdapter:
       adapters = {
           "aider": AiderAdapter(),
           "codex": CodexAdapter(),
           "claude": ClaudeAdapter(),
       }
       return adapters.get(agent_name)
   ```
6. Add configuration to `config/agent_profiles.json`

**Acceptance Criteria:**
- [ ] Base `AgentAdapter` interface defined
- [ ] Aider adapter implemented and tested
- [ ] Codex adapter implemented and tested
- [ ] Claude adapter implemented and tested
- [ ] Configuration file created
- [ ] Adapters return structured results

**Deliverables:**
- `error/engine/agent_adapters.py`
- `config/agent_profiles.json`
- Adapter unit tests

---

#### WS-G2.2: Integrate Adapters with State Machine (8-10 hours)

**Issue**: State machine needs to invoke adapters during fix states  
**Impact**: Manual intervention required for fixes  

**Tasks:**
1. Update `error/engine/error_pipeline_service.py`:
   ```python
   from error.engine.agent_adapters import get_agent_adapter, AgentInvocation
   
   def execute_fix_state(ctx: ErrorPipelineContext) -> None:
       """Execute fix based on current state"""
       agent_map = {
           "S1_AIDER_FIX": "aider",
           "S2_CODEX_FIX": "codex",
           "S3_CLAUDE_FIX": "claude",
       }
       
       if ctx.current_state in agent_map:
           adapter = get_agent_adapter(agent_map[ctx.current_state])
           invocation = AgentInvocation(
               agent_name=ctx.current_agent,
               files=ctx.python_files + ctx.powershell_files,
               error_report=ctx.last_error_report,
           )
           result = adapter.invoke(invocation)
           
           # Record attempt
           ctx.record_ai_attempt({
               "agent": ctx.current_agent,
               "attempt": ctx.attempt_number,
               "success": result.success,
               "files_modified": result.files_modified,
               "duration_ms": result.duration_ms,
           })
   ```
2. Update `S0_MECHANICAL_AUTOFIX` to use fix plugins
3. Create prompt templates for each agent in `error/templates/`:
   - `aider_fix_prompt.j2`
   - `codex_fix_prompt.j2`
   - `claude_fix_prompt.j2`
4. Add retry logic with circuit breaker
5. Add timeout enforcement
6. Integrate with DB for event recording

**Acceptance Criteria:**
- [ ] Fix states invoke correct adapters
- [ ] Mechanical fixes apply auto-fix plugins
- [ ] AI attempts recorded in context
- [ ] Prompt templates render correctly
- [ ] Circuit breaker prevents infinite retries
- [ ] DB events recorded

**Deliverables:**
- Updated `error/engine/error_pipeline_service.py`
- Prompt templates (3 files)
- Circuit breaker logic
- DB integration

---

#### WS-G2.3: Complete test_runner Plugin (4-6 hours)

**Issue**: Test runner has stub parsing functions  
**Impact**: Test failures not properly categorized  

**Tasks:**
1. Implement pytest output parser:
   ```python
   def parse_pytest_output(stdout: str) -> List[PluginIssue]:
       """Parse pytest output into structured issues"""
       issues = []
       # Parse pytest's output format
       # Extract: file, line, test name, error message
       return issues
   ```
2. Implement Jest/Node test parser
3. Add support for test frameworks:
   - pytest (Python)
   - Jest (JavaScript)
   - Pester (PowerShell)
   - Go test
4. Create test fixtures with known failures
5. Validate parsing accuracy

**Acceptance Criteria:**
- [ ] pytest output parsed correctly
- [ ] Jest output parsed correctly
- [ ] Test failures categorized as `category: "test_failure"`
- [ ] File paths and line numbers extracted
- [ ] Parser tests have 90%+ accuracy

**Deliverables:**
- Updated `error/plugins/test_runner/plugin.py`
- Test output parsers (3-4 frameworks)
- Parser tests with fixtures

---

#### WS-G2.4: Integration Test Suite (6-8 hours)

**Issue**: No end-to-end tests of full pipeline  
**Impact**: Cannot verify system works in production  

**Tasks:**
1. Create integration test scenarios:
   ```python
   # tests/error/integration/test_full_pipeline.py
   
   def test_successful_mechanical_fix():
       """File with style issues → mechanical fix → success"""
       
   def test_escalation_to_aider():
       """File with logic error → mechanical fails → Aider fixes"""
       
   def test_full_escalation_chain():
       """Complex error → all agents fail → quarantine"""
       
   def test_strict_mode_enforcement():
       """Style-only issues fail in strict mode"""
       
   def test_incremental_skip():
       """Unchanged file skipped on re-run"""
   ```
2. Create test fixtures:
   - Files with known errors
   - Expected error reports
   - Mock AI agent responses
3. Use `pytest-mock` for AI agent mocking
4. Test error report schema compliance
5. Test JSONL event logging
6. Add performance benchmarks

**Acceptance Criteria:**
- [ ] 10+ integration test scenarios
- [ ] Tests cover all state transitions
- [ ] Mocked AI agents behave realistically
- [ ] Tests run in <30 seconds
- [ ] All tests pass in CI

**Deliverables:**
- `tests/error/integration/test_full_pipeline.py`
- Test fixtures (10+ files)
- AI agent mocks
- Performance benchmarks

---

### Phase G2 Acceptance Criteria

**Exit Criteria:**
- [ ] All 3 AI agent adapters implemented
- [ ] State machine invokes adapters correctly
- [ ] test_runner plugin complete
- [ ] Integration tests pass
- [ ] Code coverage ≥ 75% for `error/` package
- [ ] Full state machine flow works end-to-end
- [ ] All Priority 2 issues resolved

**Validation Commands:**
```bash
# 1. Test AI adapter discovery
python -c "from error.engine.agent_adapters import get_agent_adapter; print(get_agent_adapter('aider'))"

# 2. Run integration tests
pytest tests/error/integration/ -v

# 3. Test full pipeline with mock AI
pytest tests/error/integration/test_full_pipeline.py::test_escalation_to_aider -v

# 4. Run pipeline with real files
python scripts/run_error_engine.py --enable-aider tests/error/fixtures/broken.py
```

---

## Phase G3: Production Hardening

**Priority**: 🟡 HIGH  
**Estimated Effort**: 24-32 hours  
**Risk Level**: MEDIUM  
**Blockers**: Phase G2  

### Objective

Harden system for production use with performance optimization, security hardening, and operational tooling.

### Workstreams

#### WS-G3.1: Performance Optimization (8-10 hours)

**Tasks:**
1. **Parallelize Plugin Execution** (4-5 hours)
   ```python
   # error/engine/pipeline_engine.py
   from concurrent.futures import ThreadPoolExecutor
   
   def _run_plugins_parallel(self, file_path: Path, max_workers: int = 4) -> List[PluginResult]:
       plugins = self._plugin_manager.get_plugins_for_file(file_path)
       with ThreadPoolExecutor(max_workers=max_workers) as executor:
           futures = {executor.submit(p.execute, file_path): p for p in plugins}
           results = []
           for future in as_completed(futures):
               results.append(future.result())
       return results
   ```
2. **Cache Plugin Discovery** (2-3 hours)
   - Cache discovered plugins for session
   - Only rediscover on manifest changes
3. **Batch File Processing** (2-3 hours)
   - Process multiple files in parallel
   - Share plugin manager across files
4. **Add Performance Metrics** (1-2 hours)
   - Track plugin execution time
   - Track file processing time
   - Identify bottlenecks

**Acceptance Criteria:**
- [ ] Plugins run in parallel when no dependencies
- [ ] Multi-file batch processing works
- [ ] 50%+ performance improvement vs serial
- [ ] Metrics collection in place

---

#### WS-G3.2: Security Hardening (6-8 hours)

**Tasks:**
1. **Input Validation** (2-3 hours)
   ```python
   def validate_file_path(path: Path) -> None:
       """Validate file path to prevent directory traversal"""
       resolved = path.resolve()
       if not resolved.is_relative_to(Path.cwd()):
           raise SecurityError(f"Path outside project: {path}")
   ```
2. **Resource Limits** (2-3 hours)
   - Max file size (default: 10MB)
   - Max plugin execution time (configurable)
   - Max memory per plugin
3. **Secret Redaction** (2-3 hours)
   ```python
   def redact_secrets(text: str) -> str:
       """Redact potential secrets from error messages"""
       patterns = [
           r"(password|token|key|secret)[\s:=]+[\w\-\.]+",
           r"[a-f0-9]{40}",  # Git SHA-like
           r"sk-[a-zA-Z0-9]{32,}",  # API keys
       ]
       # Apply redaction
   ```
4. **Audit Logging** (1-2 hours)
   - Log all file access
   - Log all plugin executions
   - Log all AI agent invocations

**Acceptance Criteria:**
- [ ] Path validation prevents traversal attacks
- [ ] Resource limits enforced
- [ ] Secrets redacted from logs
- [ ] Audit log complete and queryable

---

#### WS-G3.3: Configuration Management (4-6 hours)

**Tasks:**
1. Create `error/config.py`:
   ```python
   from dataclasses import dataclass, field
   from typing import Optional
   
   @dataclass
   class ErrorPipelineConfig:
       # Plugin settings
       plugins_path: Optional[Path] = None
       plugin_timeout_seconds: int = 120
       max_parallel_plugins: int = 4
       
       # Cache settings
       cache_path: Path = Path(".state/validation_cache.json")
       enable_incremental: bool = True
       
       # AI Agent settings
       enable_aider: bool = True
       enable_codex: bool = False
       enable_claude: bool = False
       max_attempts_per_agent: int = 1
       
       # Performance
       max_file_size_mb: int = 10
       batch_size: int = 10
       
       # Security
       enable_secret_redaction: bool = True
       allowed_file_extensions: list = field(default_factory=lambda: [".py", ".js", ".ps1", ".md", ".yaml", ".json"])
       
       @classmethod
       def from_env(cls) -> "ErrorPipelineConfig":
           """Load from environment variables"""
           
       @classmethod
       def from_file(cls, path: Path) -> "ErrorPipelineConfig":
           """Load from YAML/JSON config file"""
   ```
2. Support multiple config sources (precedence):
   - CLI arguments (highest)
   - Environment variables
   - Config file (`error/config.yaml`)
   - Defaults (lowest)
3. Add validation for config values
4. Document all config options

**Acceptance Criteria:**
- [ ] Config loaded from env/file/defaults
- [ ] CLI args override all other sources
- [ ] Invalid config rejected with clear errors
- [ ] All options documented

---

#### WS-G3.4: Error Recovery & Resilience (6-8 hours)

**Tasks:**
1. **Graceful Plugin Failures** (2-3 hours)
   - Continue if one plugin fails
   - Report partial results
   - Mark failed plugins in report
2. **State Persistence** (2-3 hours)
   ```python
   # error/engine/state_persistence.py
   def save_context(ctx: ErrorPipelineContext) -> None:
       """Save context to disk for recovery"""
       path = Path(".state") / f"error_context_{ctx.run_id}.json"
       path.write_text(json.dumps(ctx.to_json()))
   
   def load_context(run_id: str) -> ErrorPipelineContext:
       """Restore context after crash"""
   ```
3. **Automatic Retry Logic** (2-3 hours)
   - Retry transient failures (network, timeout)
   - Exponential backoff
   - Max retry limit
4. **Crash Recovery** (1-2 hours)
   - Detect incomplete runs
   - Resume from last checkpoint
   - Clean up temp files

**Acceptance Criteria:**
- [ ] System continues after plugin crash
- [ ] Context saved periodically
- [ ] Runs resumable after crash
- [ ] Temp files cleaned up

---

### Phase G3 Acceptance Criteria

**Exit Criteria:**
- [ ] Plugin execution parallelized
- [ ] Security hardening complete
- [ ] Configuration system in place
- [ ] Error recovery mechanisms work
- [ ] Performance improved 50%+ vs baseline
- [ ] Security audit passes
- [ ] All Priority 3 issues resolved

**Validation Commands:**
```bash
# 1. Performance benchmark
python scripts/benchmark_error_pipeline.py --files 100 --compare-serial

# 2. Security scan
python scripts/security_audit.py

# 3. Config validation
python -c "from error.config import ErrorPipelineConfig; cfg = ErrorPipelineConfig.from_env(); print(cfg)"

# 4. Crash recovery test
python scripts/test_crash_recovery.py
```

---

## Phase G4: Observability & Operations

**Priority**: 🟢 MEDIUM (Optional)  
**Estimated Effort**: 16-24 hours  
**Risk Level**: LOW  
**Blockers**: Phase G3  

### Objective

Add production monitoring, metrics, and operational tooling.

### Workstreams

#### WS-G4.1: Structured Logging (4-6 hours)

**Tasks:**
1. Replace print statements with structured logging:
   ```python
   import structlog
   
   logger = structlog.get_logger(__name__)
   
   logger.info("plugin_executed", 
               plugin_id=plugin_id, 
               duration_ms=duration,
               success=success)
   ```
2. Configure log levels (DEBUG, INFO, WARNING, ERROR)
3. Add correlation IDs (run_id, workstream_id)
4. Output formats: JSON (production), console (dev)
5. Log rotation configuration

**Acceptance Criteria:**
- [ ] All modules use structured logging
- [ ] Logs include context (run_id, etc.)
- [ ] Log levels configurable
- [ ] JSON output for production

---

#### WS-G4.2: Metrics Collection (6-8 hours)

**Tasks:**
1. Add Prometheus-compatible metrics:
   ```python
   from prometheus_client import Counter, Histogram, Gauge
   
   FILES_PROCESSED = Counter("error_pipeline_files_processed_total", "Files processed", ["status"])
   PLUGIN_DURATION = Histogram("error_pipeline_plugin_duration_seconds", "Plugin execution time", ["plugin_id"])
   ACTIVE_RUNS = Gauge("error_pipeline_active_runs", "Active pipeline runs")
   ```
2. Track key metrics:
   - Files processed (total, success, failed)
   - Plugin execution time (by plugin)
   - AI agent invocations (by agent, success rate)
   - Cache hit rate
   - Error categories (by category, severity)
3. Create `/metrics` HTTP endpoint
4. Add Grafana dashboard template

**Acceptance Criteria:**
- [ ] Prometheus metrics exposed
- [ ] Key metrics tracked
- [ ] Grafana dashboard created
- [ ] Metrics endpoint works

---

#### WS-G4.3: Health Checks & Status API (3-4 hours)

**Tasks:**
1. Create health check endpoint:
   ```python
   # error/engine/health.py
   def check_health() -> Dict[str, Any]:
       return {
           "status": "healthy",
           "plugins_available": len(pm._plugins),
           "cache_accessible": cache_path.exists(),
           "ai_agents": {
               "aider": check_aider_available(),
               "codex": check_codex_available(),
               "claude": check_claude_available(),
           }
       }
   ```
2. Add status API:
   - Current runs
   - Recent errors
   - Plugin status
   - Cache statistics
3. Create CLI status command:
   ```bash
   python scripts/error_pipeline_status.py
   ```

**Acceptance Criteria:**
- [ ] Health endpoint returns valid JSON
- [ ] Status API shows current state
- [ ] CLI status command works
- [ ] Unhealthy states detected

---

#### WS-G4.4: Operational Runbooks (3-4 hours)

**Tasks:**
1. Create `error/docs/OPERATIONS.md`:
   - Deployment checklist
   - Configuration guide
   - Monitoring setup
   - Troubleshooting guide
   - Incident response procedures
2. Create `error/docs/TROUBLESHOOTING.md`:
   - Common errors and solutions
   - Debug mode instructions
   - Log analysis guide
3. Add playbooks:
   - High error rate response
   - Plugin failure investigation
   - Performance degradation
   - AI agent timeout

**Acceptance Criteria:**
- [ ] Operations guide complete
- [ ] Troubleshooting guide comprehensive
- [ ] Playbooks cover common scenarios
- [ ] Links to logs/metrics

---

### Phase G4 Acceptance Criteria

**Exit Criteria:**
- [ ] Structured logging in place
- [ ] Metrics exposed via Prometheus
- [ ] Health checks implemented
- [ ] Operational documentation complete
- [ ] Grafana dashboard available
- [ ] System observable in production

**Validation Commands:**
```bash
# 1. Check logs
tail -f .state/error_pipeline.log | jq

# 2. Query metrics
curl http://localhost:9090/metrics | grep error_pipeline

# 3. Health check
curl http://localhost:9090/health | jq

# 4. Status
python scripts/error_pipeline_status.py --format json
```

---

## Success Metrics & KPIs

### Code Quality
- [ ] Test coverage ≥ 80% for `error/` package
- [ ] All linters pass (ruff, mypy, black)
- [ ] No critical security vulnerabilities
- [ ] Cyclomatic complexity < 10 for all functions

### Performance
- [ ] Single file validation < 10 seconds (8 plugins)
- [ ] Batch of 100 files < 5 minutes
- [ ] Cache hit rate ≥ 70%
- [ ] Memory usage < 500MB for 100 concurrent files

### Reliability
- [ ] 99% uptime in production
- [ ] Mean time to recovery (MTTR) < 15 minutes
- [ ] 0 data loss incidents
- [ ] < 1% false positive rate for error detection

### Operational
- [ ] All runbooks tested
- [ ] Monitoring dashboard deployed
- [ ] On-call rotation trained
- [ ] Incident response < 30 minutes

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **AI agent API changes** | Medium | High | Abstract behind adapters; version pinning |
| **Plugin performance degradation** | Medium | Medium | Timeout enforcement; parallel execution |
| **State machine edge cases** | Low | High | Comprehensive integration tests |
| **Security vulnerabilities** | Low | Critical | Regular security audits; input validation |
| **Dependency conflicts** | Medium | Medium | Pin versions; test in isolation |
| **Resource exhaustion** | Low | High | Resource limits; monitoring alerts |

---

## Rollout Strategy

### Phase 1: Internal Testing (Week 1-2)
- Deploy to staging environment
- Run against internal codebases
- Collect metrics and feedback
- Fix critical bugs

### Phase 2: Limited Rollout (Week 3-4)
- Enable for 10% of workstreams
- Monitor error rates and performance
- Gradual increase to 50%

### Phase 3: Full Production (Week 5-6)
- Enable for 100% of workstreams
- 24/7 monitoring
- On-call rotation active

### Rollback Plan
- Keep Phase E (current) system running in parallel
- Feature flag to switch between old/new
- Automated rollback on error rate > 5%

---

## Documentation Deliverables

### User Documentation
- [ ] `error/README.md` - High-level overview
- [ ] `error/docs/QUICKSTART.md` - 5-minute tutorial
- [ ] `error/docs/PLUGIN_DEVELOPMENT.md` - Plugin creation guide
- [ ] `error/docs/CONFIGURATION.md` - All config options
- [ ] `error/docs/FAQ.md` - Common questions

### Developer Documentation
- [ ] `error/docs/ARCHITECTURE.md` - System design
- [ ] `error/docs/STATE_MACHINE.md` - State flow details
- [ ] `error/docs/INTEGRATION.md` - How to integrate
- [ ] `error/docs/TESTING.md` - Test strategy
- [ ] `error/docs/CONTRIBUTING.md` - Contribution guide

### Operational Documentation
- [ ] `error/docs/OPERATIONS.md` - Deployment & maintenance
- [ ] `error/docs/TROUBLESHOOTING.md` - Debug guide
- [ ] `error/docs/MONITORING.md` - Metrics & alerts
- [ ] `error/docs/RUNBOOKS.md` - Incident response
- [ ] `error/docs/CHANGELOG.md` - Version history

---

## Phase Timeline

```
Week 1-2:   Phase G1 (Critical Fixes)
Week 3-5:   Phase G2 (Integration & Testing)
Week 6-8:   Phase G3 (Production Hardening)
Week 9-10:  Phase G4 (Observability) [Optional]
Week 11-12: Internal Testing & Rollout
```

**Total Duration**: 10-12 weeks (2.5-3 months)

---

## Definition of Done

### Phase G1
✅ All imports use standard paths  
✅ Plugins discovered correctly  
✅ README.md complete  
✅ Test foundation in place  
✅ CI gates active  

### Phase G2
✅ AI agents integrated  
✅ State machine invokes adapters  
✅ test_runner complete  
✅ Integration tests pass  
✅ 75%+ code coverage  

### Phase G3
✅ Performance optimized (50%+ faster)  
✅ Security hardened  
✅ Config management complete  
✅ Error recovery works  

### Phase G4
✅ Logging structured  
✅ Metrics exposed  
✅ Health checks implemented  
✅ Runbooks complete  

### Production Ready
✅ All phases complete  
✅ 80%+ test coverage  
✅ Security audit passed  
✅ Performance benchmarks met  
✅ Documentation complete  
✅ Staging deployment successful  
✅ Final score ≥ A- (90/100)  

---

## Appendix A: Plugin Priority Matrix

| Plugin | Priority | Complexity | Effort |
|--------|----------|------------|--------|
| python_ruff | HIGH | Low | 0h (complete) |
| python_black_fix | HIGH | Low | 0h (complete) |
| test_runner | CRITICAL | High | 4-6h |
| aider adapter | CRITICAL | High | 6-8h |
| codex adapter | CRITICAL | Medium | 4-6h |
| claude adapter | HIGH | Medium | 4-6h |
| semgrep | MEDIUM | Low | 0h (complete) |
| gitleaks | MEDIUM | Low | 0h (complete) |
| path_standardizer | LOW | Low | 2h (add manifest) |

---

## Appendix B: Test Coverage Targets

| Module | Current | Target | Gap |
|--------|---------|--------|-----|
| `error/engine/error_state_machine.py` | 0% | 90% | 90% |
| `error/engine/plugin_manager.py` | 0% | 85% | 85% |
| `error/engine/pipeline_engine.py` | 0% | 80% | 80% |
| `error/engine/agent_adapters.py` | N/A | 75% | 75% |
| `error/plugins/*/plugin.py` | ~30% | 70% | 40% |
| **Overall** | **~10%** | **80%** | **70%** |

---

## Appendix C: Dependencies

### Required Tools
- Python 3.10+
- pytest 7.0+
- Aider CLI (optional)
- GitHub Copilot CLI (optional)
- Claude API key (optional)

### Python Packages
```
# requirements.txt additions
structlog>=23.0.0
prometheus-client>=0.17.0
pydantic>=2.0.0
jinja2>=3.1.0
pytest-mock>=3.11.0
pytest-cov>=4.1.0
```

---

**Document Status**: DRAFT v1.0.0  
**Next Review**: After Phase G1 completion  
**Owner**: Error Pipeline Team  
**Approvers**: Architecture Review Board

---

**End of Phase Plan**
