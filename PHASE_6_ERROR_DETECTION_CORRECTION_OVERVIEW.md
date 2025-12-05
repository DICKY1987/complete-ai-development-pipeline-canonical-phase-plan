# Phase 6 Error Detection & Correction - Comprehensive Overview


---

**UPDATE 2025-12-05**: Agent 3 Testing Complete (WS-6T-06)
- ✅ 5 security/platform plugins tested (semgrep, gitleaks, powershell_pssa, path_standardizer, echo)
- ✅ 15 test files created (3 per plugin)
- ✅ 91 tests total across all 5 plugins
- ✅ All tests follow EXEC-002 pattern (batch validation with tool availability guards)
- 📊 Phase 6 testing progress: 60% → 75% (Agent 3 complete)

**Remaining Work** (Agent 1 & Agent 2):
- Agent 1: Python + JS/MD/Config plugin tests (42 files, 140+ tests)
- Agent 2: Integration tests + unit test fixes (10 files, 30+ tests, 12 bug fixes)
- Target completion: 100% test coverage (163+ tests total)

---
## Architecture Summary

Phase 6 implements a sophisticated multi-tier error recovery pipeline with:
- **21 Error Detection/Fix Plugins** (Python, JS, Markdown, YAML, Security)
- **5-Layer Error Classification** (Infrastructure → Business Logic)
- **Multi-Agent Escalation** (Mechanical → Aider → Codex → Claude)
- **State Machine Orchestration** (12 states with deterministic transitions)
- **Auto-Fix Capabilities** (Formatting, linting, security patches)

## Core Components

### 1. Error Engine (rror_engine.py)
- **Status**: SHIM (imports from UET framework)
- **Purpose**: Main orchestrator for error detection/recovery
- **Location**: phase6_error_recovery/modules/error_engine/src/engine/

### 2. Pipeline Engine (pipeline_engine.py)
- **Core Logic**: File processing, plugin coordination, reporting
- **Features**:
  - Incremental validation (hash-based change detection)
  - Temp directory isolation (no contamination)
  - JSONL event streaming (pipeline_errors.jsonl)
  - Per-file certification artifacts
  - Enhanced metrics (auto-repairable vs requires-human)

### 3. State Machine (rror_state_machine.py)
**12 States with Escalation Path**:
- S_INIT → Initial state
- S0_BASELINE_CHECK → Initial error detection
- S0_MECHANICAL_AUTOFIX → Auto-fix (Black, isort, prettier)
- S0_MECHANICAL_RECHECK → Verify mechanical fixes
- S1_AIDER_FIX → AI fix attempt #1 (Aider)
- S1_AIDER_RECHECK → Verify Aider fixes
- S2_CODEX_FIX → AI fix attempt #2 (Codex)
- S2_CODEX_RECHECK → Verify Codex fixes
- S3_CLAUDE_FIX → AI fix attempt #3 (Claude)
- S3_CLAUDE_RECHECK → Verify Claude fixes
- S4_QUARANTINE → Manual intervention required
- S_SUCCESS → All errors resolved

### 4. Error Context (rror_context.py)
**Dataclass tracking**:
- run_id, workstream_id
- Target files (python_files, powershell_files)
- Agent configuration (enable flags for each tier)
- Attempt tracking (current_agent, attempt_number)
- Error reports (last, previous for comparison)
- AI attempt audit trail

### 5. Plugin Manager (plugin_manager.py)
**Features**:
- Auto-discovery from plugins/ directory
- Manifest-based configuration (manifest.json)
- Topological sorting (dependency-aware execution)
- File extension filtering
- Tool availability checks

## 21 Error Detection/Fix Plugins

### Python Ecosystem (8 plugins)
**Detection**:
- python_mypy → Type checking (JSON output)
- python_pylint → Comprehensive linting
- python_pyright → Advanced type checking
- python_bandit → Security scanning
- python_safety → Dependency vulnerability scanning

**Auto-Fix**:
- python_black_fix → Code formatting
- python_isort_fix → Import sorting
- (Ruff - mentioned in README but not in current listing)

### JavaScript Ecosystem (2 plugins)
- js_eslint → Linting detection
- js_prettier_fix → Code formatting

### Markdown (2 plugins)
- md_markdownlint → Markdown linting
- md_mdformat_fix → Markdown formatting

### Configuration/Data (2 plugins)
- yaml_yamllint → YAML validation
- json_jq → JSON processing

### Security/Cross-Cutting (4 plugins)
- semgrep → Pattern-based security scanning
- gitleaks → Secret detection
- codespell → Spelling errors
- path_standardizer → Path normalization

### Platform Specific (1 plugin)
- powershell_pssa → PowerShell script analysis

### Testing (2 plugins)
- echo → Test/debug plugin
- (test_runner - mentioned in README)

## 5-Layer Error Classification

**From** layer_classifier.py:

### Layer 1 - Infrastructure (Priority 1 - CRITICAL)
- file_not_found, resource_exhausted, disk_full
- **Impact**: Blocks everything
- **Auto-Repairable**: NO

### Layer 2 - Dependencies (Priority 2 - HIGH)
- import_error, module_not_found, version_mismatch
- **Impact**: Blocks execution
- **Auto-Repairable**: NO

### Layer 3 - Configuration (Priority 3 - MEDIUM)
- schema_invalid, config_error, validation_failed
- **Impact**: Runtime errors
- **Auto-Repairable**: Sometimes (schema_invalid)

### Layer 4 - Operational (Priority 4 - MEDIUM)
- permission_denied, timeout, network_error, test_failure
- **Impact**: Intermittent failures
- **Auto-Repairable**: NO

### Layer 5 - Business Logic (Priority 5 - LOW)
- syntax, type, style, formatting, security, logic_error
- **Impact**: Code quality issues
- **Auto-Repairable**: YES (if plugin has fix() method)

## Enhanced Reporting

### PipelineSummary Dataclass
- plugins_run: int
- total_errors: int
- total_warnings: int
- auto_fixed: int
- **auto_repairable**: int (NEW - errors with auto-fix available)
- **requires_human**: int (NEW - manual intervention needed)

### PipelineReport Structure
- run_id: Unique execution ID
- file_in: Input file path
- file_out: Validated output file path
- timestamp_utc: Execution timestamp
- toolchain: Dict of executed plugins
- summary: PipelineSummary
- issues: List[PluginIssue] with layer classification
- status: "completed" | "failed" | "skipped"

### PluginIssue Fields
- tool: Plugin name
- path: File path
- line, column: Location
- code: Error code (e.g., "E501", "no-unused-vars")
- category: Error category (syntax, type, style)
- **layer**: Infrastructure layer (NEW)
- severity: "error" | "warning"
- message: Human-readable description

## Auto-Fix Workflow

### Mechanical Auto-Fix (Tier 0)
**Tools**: Black, isort, prettier, mdformat
**Scope**: Formatting, import sorting, whitespace
**Success Rate**: ~95% for formatting issues
**Execution**: Immediate, no AI required

### AI-Assisted Fix (Tiers 1-3)
**Tier 1 - Aider**: Code-aware AI assistant
**Tier 2 - Codex**: GitHub Copilot engine
**Tier 3 - Claude**: Advanced reasoning
**Scope**: Logic errors, type errors, security issues
**Success Rate**: ~60-80% depending on complexity

### Escalation Logic
`python
if baseline_check_fails:
    if enable_mechanical_autofix and has_formatting_errors:
        apply_mechanical_fixes()
        recheck()

    if still_failing and enable_aider:
        attempt_aider_fix()
        recheck()

    if still_failing and enable_codex:
        attempt_codex_fix()
        recheck()

    if still_failing and enable_claude:
        attempt_claude_fix()
        recheck()

    if still_failing:
        quarantine_for_human_review()
`

## Integration with Pipeline

### Entry Triggers (from Phase 5)
- Task execution failure (FAILED status)
- Task timeout (TIMEOUT status)
- Explicit error recovery request

### Entry Requirements
**Files**:
- .state/execution_results.json (from phase5)
- error/plugins/**/plugin.py (21 plugins)

**Database**:
- tasks table (status = FAILED/TIMEOUT)
- execution_log table

**State Flags**:
- TASK_FAILED or TASK_TIMEOUT

### Exit Artifacts
**Files**:
- .state/error_analysis.json
- .state/fix_patches.json
- logs/error_recovery/*.jsonl

**Database**:
- error_log table (created)
- recovery_attempts table (created)
- tasks table (status updated after fix attempt)

**Events**:
- ERROR_DETECTED
- ERROR_CLASSIFIED
- FIX_APPLIED
- ERROR_ESCALATED

### Retry Loop to Phase 5
If auto-fix succeeds → Re-execute task (phase5)
If auto-fix fails → Escalate or quarantine

## Recent Enhancements (2025-12-04)

### Certification Artifacts (Proposed)
**Certification ID**: CERT-{ULID}
**Purpose**: Release gates, compliance audits
**Contains**:
- Run summary (plugins_run, total_errors, auto_fixed)
- Success rate thresholds
- Failing units list
- Audit trail
- Content hash for integrity

### Health Sweep Mode (Proposed)
**Purpose**: Proactive scanning (not reactive)
**Use Cases**:
- Pre-commit hooks
- Nightly CI health checks
- Developer workspace validation

### Enhanced Metrics
- Auto-repairable classification
- Requires-human tracking
- Layer-based prioritization
- Success rate thresholds for quality gates

## Known Issues & Risks

### Current Limitations
1. **error_engine.py is a SHIM** → Depends on UET framework
2. **Unknown error types** → Cannot auto-fix, escalates
3. **Fix creates new error** → Rollback and escalate
4. **Plugin unavailable** → Skips detection, may miss errors
5. **Circuit breaker open** → Recovery paused

### Risk Profile
- **Execution Risk**: MEDIUM (shim dependency)
- **Data Loss Risk**: LOW (temp directory isolation)
- **Deadlock Risk**: LOW (state machine is deterministic)
- **External Dependency Risk**: HIGH (21 plugins, 3 AI agents)

### Maturity Level
**Status**: OPERATIONAL_BETA (60% complete)
**Production Gate**: ALLOWED_WITH_MONITORING

## Testing Coverage

**~50+ Tests** covering:
- Python plugin tests (ruff, mypy, pylint, etc.)
- JavaScript plugin tests (eslint, prettier)
- Error classification tests
- Pipeline orchestration tests
- Circuit breaker integration tests
- State machine transition tests

## CLI Invocation

### Automatic (from Phase 5)
`ash
# Triggered on task failure
orchestrator recover --task <task_id>
`

### Manual
`ash
# Run error engine directly
python -m error.engine.pipeline_engine

# Health sweep mode (proposed)
python scripts/run_error_engine.py --health-sweep
`

### Programmatic
`python
from error.engine.pipeline_engine import PipelineEngine
from error.engine.plugin_manager import PluginManager
from error.engine.file_hash_cache import FileHashCache

plugin_manager = PluginManager()
hash_cache = FileHashCache()
engine = PipelineEngine(plugin_manager, hash_cache)

report = engine.process_file(Path("my_code.py"))
`

## Observability

### Log Streams
- logs/error_engine.jsonl
- logs/error_recovery/*.jsonl (per-error)
- logs/plugin_execution.jsonl
- pipeline_errors.jsonl (aggregated events)

### Metrics
- errors_detected_total
- errors_classified_total
- fixes_applied_total
- fix_success_rate
- escalations_total
- plugin_execution_duration_seconds

### Health Checks
- error_engine_health
- plugin_availability_check
- circuit_breaker_status

## Key Strengths

1. **Deterministic**: State machine ensures predictable behavior
2. **Incremental**: Hash-based change detection skips unchanged files
3. **Isolated**: Temp directory prevents contamination
4. **Comprehensive**: 21 plugins cover most common error types
5. **Layered**: 5-layer classification prioritizes critical issues
6. **Automated**: 95% formatting issues auto-fixed
7. **Traceable**: JSONL audit trail for every run
8. **Resilient**: Circuit breaker prevents cascading failures

## Next Steps (From Certification Proposal)

1. **Implement Certification Artifacts** → Release gate integration
2. **Add Health Sweep Mode** → Proactive error detection
3. **Expand Auto-Fix Coverage** → More plugin fix() methods
4. **Improve AI Integration** → Better prompt engineering for Tiers 1-3
5. **Remove UET Dependency** → Eliminate error_engine.py shim

---
**Document Generated**: 2025-12-05
**Source**: Phase 6 codebase + README + CERTIFICATION_ENHANCEMENT_PROPOSAL.md
