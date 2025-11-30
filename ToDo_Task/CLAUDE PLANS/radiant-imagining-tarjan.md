---
doc_id: DOC-GUIDE-RADIANT-IMAGINING-TARJAN-1560
---

# Pattern Automation Master Plan - Gap Analysis & Improvements

## Executive Summary

The Pattern Automation Master Plan is **architecturally sound but has critical implementation gaps**. This analysis identifies 7 major gaps and proposes concrete improvements to make the automation achievable.

**Current State**: 60% Foundation Ready, 0% Automation Implemented
**Key Finding**: Plan assumes infrastructure that doesn't exist yet
**Recommendation**: 3-phase approach with foundation-first strategy

---

## Critical Gaps Identified

### Gap 1: Missing Backend Infrastructure (BLOCKER)

**Problem**: Master plan assumes Python backend exists at:
- `core/executor.py` - Empty stub only
- `core/orchestrator.py` - Multiple versions, unclear which to hook
- `core/state/db.py` - Has legacy DB, but no telemetry schema
- `error/engine/error_engine.py` - Does NOT exist

**Impact**: Cannot implement AUTO-001 through AUTO-008 without this foundation

**What Actually Exists**:
- `core/engine/orchestrator.py` - Has execution flow and event system
- `core/state/db.py` - Has `record_event()`, `record_step_attempt()`, `record_error()`
- `core/engine/monitoring/run_monitor.py` - Has metrics aggregation
- No centralized error engine

**Fix Required**:
1. Create `error/engine/error_engine.py` with centralized error registry
2. Add telemetry tables to existing `core/state/db.py`:
   - `execution_logs` (operation signatures)
   - `pattern_metrics` (success rates)
   - `pattern_candidates` (auto-detected patterns)
   - `anti_patterns` (failure patterns)
3. Hook orchestrator events into pattern detection

---

### Gap 2: Executor Implementation Gap (HIGH PRIORITY)

**Problem**: Only 1 of 24 core patterns has working executor

**Status**:
- ✅ 1 complete: `atomic_create_executor.ps1` (430 lines)
- ✅ 6 complete: Glossary patterns (1,981 lines total)
- ❌ 23 incomplete: Skeleton files only

**Impact**: Pattern automation has nothing to learn from (need 3+ executions)

**Why This Matters**:
- AUTO-001 (ExecutionPatternDetector) needs execution data to detect patterns
- Can't capture patterns from patterns that don't execute
- Chicken-and-egg problem: Need executors to learn automation

**Fix Required**:
1. **Phase 1** (1-2 weeks): Complete top 3 patterns
   - `batch_create_executor.ps1` (template-based, straightforward)
   - `self_heal_executor.ps1` (error recovery, critical for AUTO-003)
   - `verify_commit_executor.ps1` (validation, needed for CI/CD)

2. **Phase 2** (2-3 weeks): Complete remaining 5 core patterns
   - refactor_patch, worktree_lifecycle, module_creation

3. **Phase 3** (Later): Implement 14 additional + 17 migrated patterns

---

### Gap 3: No Error Recovery Learning System (CRITICAL)

**Problem**: Master plan proposes AUTO-003 (ErrorRecoveryPatternLearner) but:
- No error engine exists to hook into
- Error rules exist (`error_rules.ps1`) but don't log success/failure
- Circuit breaker and retry logic exist but don't emit learning events

**Current Error Handling**:
- ✅ Pattern-based error detection (6 rules for Python)
- ✅ Circuit breaker (prevents cascading failures)
- ✅ Retry with exponential backoff
- ✅ State machines for recovery (Run, Patch, Worker)
- ❌ No error telemetry or analytics
- ❌ No learning loop from successful fixes

**The Missing Loop**:
```
CURRENT: Error → Fix → Success → ❌ Pattern LOST
NEEDED:  Error → Fix → Success → Learn → Auto-apply next time
```

**Fix Required**:
1. Create `error/engine/error_engine.py` with:
   - Error classification system
   - Error telemetry collection
   - Integration with orchestrator events

2. Implement ErrorRecoveryPatternLearner (AUTO-003):
   - Hook `core/orchestrator.py::complete_step_attempt()` for error logging
   - Track successful fixes in `error_patterns` table
   - Detect 3+ similar errors with same fix
   - Auto-create recovery rules

3. Add error telemetry to database:
   ```sql
   CREATE TABLE error_patterns (
       error_signature TEXT,
       occurrences INTEGER,
       successful_resolutions INTEGER,
       success_rate REAL,
       recovery_method TEXT
   );
   ```

---

### Gap 4: Validation Infrastructure Missing (MEDIUM)

**Problem**: Validation framework exists but validators not implemented

**What Exists**:
- ✅ JSON schemas for all 24 patterns
- ✅ `validation.ps1` library with `Validate-PatternInstance`
- ✅ Ground truth criteria defined in pattern specs
- ❌ No JSON schema validator (to validate instances against schemas)
- ❌ No pattern registry validator
- ❌ No automated ground truth verification

**Impact**:
- Can't verify pattern instances before execution
- Risk of executing invalid patterns
- No quality gate for auto-generated patterns

**Fix Required**:
1. Create `scripts/validate_pattern_instance.ps1`:
   - Load JSON schema for pattern
   - Validate instance against schema
   - Return validation errors

2. Create `scripts/validate_pattern_registry.ps1`:
   - Validate PATTERN_INDEX.yaml structure
   - Check all referenced files exist
   - Verify pattern IDs follow naming convention

3. Create `scripts/verify_ground_truth.ps1`:
   - Execute ground truth checks from pattern specs
   - Report pass/fail for each criterion
   - Integrate with orchestrator

---

### Gap 5: No Telemetry Collection System (BLOCKER FOR AUTOMATION)

**Problem**: Master plan assumes telemetry system exists, but it doesn't

**What's Missing**:
- No `execution_logs` table to store operation signatures
- No hook in orchestrator to capture execution patterns
- No file operation tracking in `core/file_lifecycle.py`
- No pattern usage metrics collection

**What Exists**:
- ✅ Event system in orchestrator (`record_event()`)
- ✅ Step attempt tracking (`record_step_attempt()`)
- ✅ Run monitoring (`RunMonitor.get_run_metrics()`)
- ❌ Not connected to pattern detection

**Fix Required**:
1. Add telemetry schema to `core/state/db.py`:
   ```sql
   CREATE TABLE execution_logs (
       timestamp DATETIME,
       operation_kind TEXT,
       pattern_id TEXT,
       file_types TEXT,
       tools_used TEXT,
       input_signature TEXT,
       output_signature TEXT,
       success BOOLEAN,
       time_taken_seconds INTEGER
   );
   ```

2. Hook orchestrator to log executions:
   ```python
   # In core/orchestrator.py::complete_step_attempt()
   if pattern_id:
       signature = extract_execution_signature(step_result)
       db.log_execution(pattern_id, signature, success, duration)
   ```

3. Instrument pattern executors to emit telemetry:
   - Add to each executor's result.json output
   - Include operation signature, timing, success

---

### Gap 6: Unclear Hook Points in Orchestrator (INTEGRATION)

**Problem**: Multiple orchestrator versions exist, unclear which to hook

**Files Found**:
- `core/engine/orchestrator.py` (131 lines, has execution flow)
- `core/orchestrator.py` (re-exports from core/engine)
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py` (stub)
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/orchestrator.py`
- `engine/orchestrator/orchestrator.py`

**Confusion**: Which is the "main" orchestrator to instrument?

**What We Know**:
- `core/engine/orchestrator.py` has the execution methods
- `run_edit_step()`, `run_static_step()`, `run_runtime_step()` exist
- Event emission already present (`record_event()`)
- Need to add pattern detection hooks here

**Fix Required**:
1. Clarify which orchestrator is canonical (likely `core/engine/orchestrator.py`)
2. Document hook points in master plan with specific file paths:
   - Line 78: After `run_edit_step()` completion
   - Line 172: After `run_static_step()` completion
   - Line 210: After `run_runtime_step()` completion
3. Add pattern detector integration:
   ```python
   # After step completion
   if pattern_detector:
       pattern_detector.on_execution_complete({
           'step': step_name,
           'result': result,
           'duration': duration,
           'context': execution_context
       })
   ```

---

### Gap 7: No CI/CD Integration (INFRASTRUCTURE)

**Problem**: Master plan proposes GitHub Actions workflows, but none exist

**What's Missing**:
- `.github/workflows/pattern-automation.yml` (scheduled analysis)
- Cron jobs for pattern detection (every 6 hours)
- Weekly performance report generation
- Monthly pattern cleanup

**Impact**: Automation won't run automatically without scheduling

**Fix Required**:
1. Create `.github/workflows/pattern-automation.yml`:
   ```yaml
   on:
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours: Pattern detection
       - cron: '0 0 * * 0'    # Weekly: Performance reports

   jobs:
     detect_patterns:
       steps:
         - run: python scripts/auto_pattern_detector.py --analyze
         - run: python scripts/auto_pattern_detector.py --suggest
   ```

2. Create scripts:
   - `scripts/auto_pattern_detector.py` (AUTO-001 implementation)
   - `scripts/analyze_pattern_usage.py` (AUTO-004 implementation)
   - `scripts/update_anti_patterns.py` (AUTO-005 implementation)

3. Set up local cron jobs for development:
   - Windows Task Scheduler for local testing
   - PowerShell scheduled tasks

---

## Improved Implementation Roadmap

### Phase 0: Foundation Prerequisites (Week 1-2) **[NEW]**

**Goal**: Build infrastructure that master plan assumes exists

1. **Create Error Engine**
   - File: `error/engine/error_engine.py`
   - Classes: `ErrorEngine`, `ErrorRegistry`, `ErrorClassifier`
   - Integration: Hook into orchestrator events

2. **Add Telemetry Schema**
   - File: `core/state/migrations/add_pattern_telemetry.sql`
   - Tables: `execution_logs`, `pattern_metrics`, `pattern_candidates`, `anti_patterns`
   - Indexes: On pattern_id, timestamp, status

3. **Implement Core Validators**
   - File: `scripts/validate_pattern_instance.ps1`
   - File: `scripts/validate_pattern_registry.ps1`
   - File: `scripts/verify_ground_truth.ps1`

4. **Complete Top 3 Pattern Executors**
   - `batch_create_executor.ps1` (needed for pattern generation)
   - `self_heal_executor.ps1` (needed for error learning)
   - `verify_commit_executor.ps1` (needed for CI/CD)

**Deliverable**: Infrastructure ready for automation

---

### Phase 1: Telemetry Collection (Week 3) **[REVISED]**

**Goal**: Start capturing execution data

1. **Instrument Orchestrator**
   - Hook `core/engine/orchestrator.py::complete_step_attempt()`
   - Call `db.log_execution()` with signature
   - Emit pattern execution events

2. **Update Pattern Executors**
   - Add telemetry to result.json output
   - Include operation signature
   - Track timing per step

3. **Verify Data Collection**
   - Run existing patterns (atomic_create, glossary)
   - Check `execution_logs` table populates
   - Validate signature extraction

**Deliverable**: 2+ weeks of execution data

---

### Phase 2: Pattern Detection (Week 4-5) **[REVISED]**

**Goal**: Implement AUTO-001, AUTO-002, AUTO-003

1. **ExecutionPatternDetector (AUTO-001)**
   - File: `patterns/automation/detectors/execution_detector.py`
   - Analyze `execution_logs` for 3+ similar executions
   - Generate pattern candidates in `patterns/drafts/`

2. **FilePatternMiner (AUTO-002)**
   - File: `patterns/automation/detectors/file_pattern_miner.py`
   - Watch file creation via Git hooks
   - Detect 2+ similar files, suggest templates

3. **ErrorRecoveryPatternLearner (AUTO-003)**
   - File: `patterns/automation/detectors/error_learner.py`
   - Hook into error engine resolution tracking
   - Extract patterns from 3+ successful fixes

4. **Set Up Scheduled Analysis**
   - Create cron job / Task Scheduler
   - Run detection every 6 hours
   - Output: `patterns/reports/pattern_candidates_weekly.md`

**Deliverable**: Auto-generated pattern candidates

---

### Phase 3: Intelligence Layer (Week 6) **[REVISED]**

**Goal**: Implement AUTO-004, AUTO-005, AUTO-006

1. **PatternPerformanceAnalyzer (AUTO-004)**
   - File: `patterns/automation/analyzers/performance_analyzer.py`
   - Generate weekly reports from `pattern_metrics`
   - Rank patterns by usage, time savings
   - Identify underused patterns

2. **AntiPatternDetector (AUTO-005)**
   - File: `patterns/automation/detectors/anti_pattern_detector.py`
   - Analyze failed executions
   - Detect recurring failure patterns
   - Update `anti_patterns` registry

3. **PatternSuggester (AUTO-006)**
   - File: `patterns/automation/detectors/pattern_suggester.py`
   - Hook into CLI before execution
   - Suggest patterns based on context
   - Real-time recommendations

**Deliverable**: Weekly automated reports + real-time suggestions

---

### Phase 4: Self-Improvement (Week 7-8) **[UNCHANGED]**

**Goal**: Implement AUTO-007, AUTO-008

1. **PatternEvolutionTracker (AUTO-007)**
   - Monitor pattern success rates
   - Flag patterns needing improvement
   - Propose v1.1, v1.2 versions

2. **TemplateAutoGenerator (AUTO-008)**
   - Generate templates from 2-3 examples
   - Extract invariants and variables
   - Auto-create template files

**Deliverable**: Self-improving pattern system

---

## Concrete Improvements to Master Plan

### Improvement 1: Add Phase 0 (Foundation Prerequisites)

**Current Plan**: Starts with Phase 1 (Telemetry Foundation)
**Problem**: Assumes infrastructure exists
**Fix**: Add Phase 0 to build missing infrastructure

**Addition to Plan** (insert before current Phase 1):
```markdown
### Phase 0: Foundation Prerequisites (Week 1-2)
- Create error/engine/error_engine.py
- Add telemetry schema to database
- Implement validation scripts
- Complete top 3 pattern executors
```

---

### Improvement 2: Clarify Hook Points with Specific Files

**Current Plan**: References `core/executor.py`, `core/orchestrator.py`
**Problem**: Multiple files with these names, unclear which to hook
**Fix**: Specify exact file paths and line numbers

**Revision to Hook Points Table** (line 620):
```markdown
| Component | File | Lines | Purpose | Hook Type |
|---|---|---|---|---|
| **Main Orchestrator** | `core/engine/orchestrator.py` | 57-322 | EDIT→STATIC→RUNTIME flow | Execution hooks |
| **Step Recording** | `core/state/db.py` | 114-122 | Capture step lifecycle | Telemetry hook |
| **Error Tracking** | `error/engine/error_engine.py` | NEW | Record error signatures | Observability hook |
```

---

### Improvement 3: Add Error Engine Creation Task

**Current Plan**: Assumes `error/engine/error_engine.py` exists
**Problem**: File does not exist
**Fix**: Add creation task to Phase 0

**Addition to Plan** (Phase 0 checklist):
```markdown
- [ ] Create error/engine/error_engine.py with:
  - ErrorEngine class (centralized registry)
  - ErrorClassifier (categorize errors)
  - Resolution tracking (learn from fixes)
  - Integration hooks for orchestrator
```

---

### Improvement 4: Add Executor Completion Prerequisite

**Current Plan**: Assumes patterns are executable
**Problem**: Only 1/24 core patterns has working executor
**Fix**: Add executor implementation to Phase 0

**Addition to Plan** (Phase 0):
```markdown
### Complete Critical Pattern Executors

Before automation can learn, we need patterns to execute:

1. batch_create_executor.ps1 (template-based operations)
2. self_heal_executor.ps1 (error recovery patterns)
3. verify_commit_executor.ps1 (validation patterns)

**Why These 3**:
- batch_create: Generates repetitive work (pattern goldmine)
- self_heal: Provides error recovery data (AUTO-003 needs this)
- verify_commit: CI/CD integration (enables automation)
```

---

### Improvement 5: Add Validation Infrastructure Tasks

**Current Plan**: Doesn't mention validation
**Problem**: No quality gates for auto-generated patterns
**Fix**: Add validation to Phase 0

**Addition to Plan** (Phase 0):
```markdown
### Build Validation Infrastructure

1. scripts/validate_pattern_instance.ps1
   - Validate JSON instances against schemas
   - Return validation errors
   - Exit code 0 (valid) or 1 (invalid)

2. scripts/validate_pattern_registry.ps1
   - Validate PATTERN_INDEX.yaml structure
   - Verify all file references exist
   - Check pattern ID naming convention

3. scripts/verify_ground_truth.ps1
   - Execute ground truth criteria from specs
   - Report pass/fail per criterion
   - Integrate with orchestrator
```

---

### Improvement 6: Revise Success Metrics with Baseline

**Current Plan**: Shows target metrics but unclear baseline
**Problem**: No way to measure progress
**Fix**: Add current state baseline

**Revision to Success Metrics** (line 602):
```markdown
## Success Metrics

### Baseline (Current State)
- Pattern executors: 7/24 complete (29%)
- Execution telemetry: 0% (no collection)
- Pattern detection: 0% (no automation)
- Template creation: 100% manual (2 hours per pattern)
- Error learning: 0% (no capture)
- Anti-pattern identification: 0% (manual only)

### Milestone 1 (After Phase 0) - Week 2
- Pattern executors: 10/24 complete (42%)
- Execution telemetry: 100% (infrastructure ready)
- Validation: 100% (scripts implemented)
- Error engine: 100% (foundation complete)

### Milestone 2 (After Phase 2) - Week 5
- Pattern detection: 80% automatic
- Pattern candidates: 5+ per week auto-generated
- Error learning: Active (AUTO-003 running)
- Telemetry: 4+ weeks of data collected

### Target (After Phase 4) - Week 8
- Pattern detection: 90% automatic
- Template creation: 60% auto-generated (15 min review)
- Error recovery: 70% self-healing success rate
- Anti-pattern identification: 90% automatic
- User time savings: 70% reduction in pattern management
```

---

### Improvement 7: Add Rollback Plan & Aggressive Mode Safety

**Current Plan**: No mention of rollback or failure handling
**Problem**: If automation goes wrong, how to recover?
**Fix**: Add rollback strategy with aggressive mode safeguards

**Addition to Plan** (new section after Phase 4):
```markdown
## Rollback and Safety (Aggressive Mode)

### Aggressive Mode Configuration

**User Preference**: Auto-approve patterns, monitor for failures

**Safety Parameters**:
- Auto-approve patterns with confidence ≥75% (not 90%)
- Auto-quarantine if failure rate >40% (within first 10 uses)
- Auto-rollback if critical failure (data loss, security issue)
- Manual review required only for quarantined patterns

### Safety Mechanisms

1. **Auto-Approval with Monitoring**
   - All auto-generated patterns with confidence ≥75% → `patterns/specs/` (production)
   - Patterns with confidence <75% → `patterns/drafts/` (require review)
   - First 10 uses heavily monitored for failure patterns
   - Confidence calculation: similarity score × success rate × test coverage

2. **Automatic Pattern Quarantine**
   - If pattern failure rate >40% in first 10 uses → auto-quarantine
   - Move to `patterns/quarantined/` with failure report
   - Emit alert with failure analysis
   - Require manual fix and re-approval

3. **Circuit Breaker Integration**
   - Pattern execution uses existing circuit breaker
   - After 3 consecutive failures → circuit opens (pattern disabled)
   - Half-open after 60 seconds (retry once)
   - If retry fails → quarantine pattern

4. **Automation Kill Switch**
   - Environment variable: `DISABLE_PATTERN_AUTOMATION=1`
   - Stops all AUTO-* features immediately
   - Falls back to manual pattern execution
   - Emergency use only

5. **Rollback Procedure**
   - Keep 90 days of execution logs (not 30, for better forensics)
   - Version all pattern changes (v1.0, v1.1, etc.)
   - Auto-rollback on critical failure: `scripts/auto_rollback_pattern.ps1`
   - Manual rollback: `scripts/rollback_pattern.ps1 -PatternId PAT-XXX -ToVersion 1.0`

### Monitoring Alerts (Aggressive Mode)

- **CRITICAL**: Pattern failure rate >50% (auto-quarantine + alert)
- **HIGH**: Pattern failure rate >40% (monitor closely)
- **MEDIUM**: Auto-generated pattern has no usage after 7 days (may be irrelevant)
- **LOW**: Anti-pattern count increases by 50%+ in a week (learning opportunity)

### Confidence Scoring (For Auto-Approval)

```python
confidence = (
    0.4 × similarity_score +      # How similar are the 3+ executions?
    0.3 × success_rate +           # Historical success of similar operations
    0.2 × test_coverage +          # Does generated pattern have tests?
    0.1 × schema_completeness      # Is schema fully defined?
)

# Auto-approve if confidence ≥ 0.75 (75%)
```
```

---

### Improvement 8: Add Testing Strategy

**Current Plan**: No mention of testing the automation
**Problem**: How to verify AUTO-* features work correctly?
**Fix**: Add testing requirements

**Addition to Plan** (new section):
```markdown
## Testing Strategy

### Unit Tests (Per AUTO-* Feature)

1. **ExecutionPatternDetector (AUTO-001)**
   - Test: Extract signature from execution
   - Test: Detect 3+ similar executions
   - Test: Generate pattern YAML correctly
   - Test: Handle edge cases (partial matches)

2. **ErrorRecoveryPatternLearner (AUTO-003)**
   - Test: Classify error types correctly
   - Test: Learn from 3+ similar fixes
   - Test: Generate recovery rules
   - Test: Don't learn from failed fixes

3. **PatternPerformanceAnalyzer (AUTO-004)**
   - Test: Calculate success rates correctly
   - Test: Rank patterns by usage
   - Test: Generate valid markdown reports

### Integration Tests

1. **End-to-End Pattern Detection**
   - Run atomic_create 3 times with similar inputs
   - Verify pattern candidate generated
   - Validate candidate schema
   - Test approval workflow

2. **Error Learning Loop**
   - Inject known error 3 times
   - Apply same fix each time
   - Verify auto-healing rule created
   - Test auto-application on 4th occurrence

### Test Data

- Create `patterns/test_data/` directory
- 10 sample executions for pattern detection
- 5 sample error scenarios for error learning
- 3 sample pattern candidates for validation
```

---

## Summary of Improvements

| # | Improvement | Impact | Effort |
|---|-------------|--------|--------|
| 1 | Add Phase 0 (Foundation) | **CRITICAL** - Unblocks all automation | 2 weeks |
| 2 | Clarify hook points | High - Removes ambiguity | 2 hours |
| 3 | Add error engine creation | **CRITICAL** - Enables AUTO-003 | 3 days |
| 4 | Add executor completion | **CRITICAL** - Provides data for learning | 1-2 weeks |
| 5 | Add validation infrastructure | High - Quality gates | 3 days |
| 6 | Revise success metrics | Medium - Measurable progress | 1 hour |
| 7 | Add rollback plan | High - Risk mitigation | 2 days |
| 8 | Add testing strategy | High - Verify automation works | 1 week |

**Total Additional Effort**: 4-5 weeks (on top of original 8-week plan)
**Revised Timeline**: 12-13 weeks for complete, tested automation

---

## Recommended Implementation Approach

**Based on User Preferences**:
- ✅ Priority: Foundation-first (build infrastructure before automation)
- ✅ Scope: Full 12-13 week plan (all 8 AUTO-* features)
- ✅ Risk Tolerance: Aggressive (auto-approve patterns, monitor for failures)
- ✅ Executors: Prioritize batch_create and self_heal in Phase 0

### Phase 0: Foundation Prerequisites (Week 1-2)

**Critical Path Items**:

1. **Create Error Engine** (3 days)
   - File: `error/engine/error_engine.py`
   - Classes: `ErrorEngine`, `ErrorRegistry`, `ErrorClassifier`
   - Hook into `core/engine/orchestrator.py::complete_step_attempt()`
   - Emit error events to event bus

2. **Add Telemetry Schema** (1 day)
   - File: `core/state/migrations/add_pattern_telemetry.sql`
   - Tables: `execution_logs`, `pattern_metrics`, `pattern_candidates`, `anti_patterns`
   - Run migration script

3. **Complete Priority Executors** (5-7 days)
   - `batch_create_executor.ps1` - Template-based operations (3 days)
   - `self_heal_executor.ps1` - Error recovery patterns (4 days)
   - Test with example instances

4. **Build Validation Infrastructure** (2 days)
   - `scripts/validate_pattern_instance.ps1` - JSON schema validation
   - `scripts/validate_pattern_registry.ps1` - Registry validation
   - `scripts/verify_ground_truth.ps1` - Ground truth checks

**Deliverable**: Infrastructure ready for automation

### Phase 1: Telemetry Collection (Week 3)

1. **Instrument Orchestrator** (2 days)
   - Hook `core/engine/orchestrator.py::complete_step_attempt()` (line 114-122)
   - Call `db.log_execution()` with signature
   - Test with atomic_create and glossary patterns

2. **Update Pattern Executors** (2 days)
   - Add telemetry to result.json in batch_create and self_heal
   - Include operation signature, timing, file types
   - Verify data collection

3. **Run Baseline Collection** (1-2 weeks ongoing)
   - Execute patterns during normal development
   - Target: 20+ executions for pattern detection
   - Validate data quality

**Deliverable**: 2+ weeks of execution data collected

### Phase 2: Pattern Detection (Week 4-5)

1. **ExecutionPatternDetector (AUTO-001)** (4 days)
   - File: `patterns/automation/detectors/execution_detector.py`
   - Analyze `execution_logs` for 3+ similar executions
   - Generate pattern candidates in `patterns/drafts/`
   - **Aggressive Mode**: Auto-approve confidence >75%, quarantine if failure rate >40%

2. **FilePatternMiner (AUTO-002)** (2 days)
   - File: `patterns/automation/detectors/file_pattern_miner.py`
   - Git pre-commit hook to detect file patterns
   - Suggest templates after 2+ similar files

3. **ErrorRecoveryPatternLearner (AUTO-003)** (4 days)
   - File: `patterns/automation/detectors/error_learner.py`
   - Hook into error engine resolution tracking
   - Learn from successful fixes in self_heal_executor
   - **Aggressive Mode**: Auto-create recovery rules after 3 successes

4. **Set Up Scheduled Analysis** (1 day)
   - Windows Task Scheduler job (every 6 hours)
   - Run `scripts/auto_pattern_detector.py --analyze`
   - Output to `patterns/reports/pattern_candidates_weekly.md`

**Deliverable**: Auto-generated pattern candidates (5+ per week expected)

### Phase 3: Intelligence Layer (Week 6)

1. **PatternPerformanceAnalyzer (AUTO-004)** (3 days)
   - File: `patterns/automation/analyzers/performance_analyzer.py`
   - Weekly reports from `pattern_metrics`
   - Rank by usage, time savings, success rate
   - Dashboard: `patterns/reports/weekly/performance_report.md`

2. **AntiPatternDetector (AUTO-005)** (3 days)
   - File: `patterns/automation/detectors/anti_pattern_detector.py`
   - Analyze failed executions (failure rate >40%)
   - Auto-quarantine problematic patterns
   - Update `patterns/anti_patterns/registry.yaml`

3. **PatternSuggester (AUTO-006)** (3 days)
   - File: `patterns/automation/detectors/pattern_suggester.py`
   - CLI interceptor for real-time suggestions
   - Context-aware recommendations before execution
   - Integration hook: Pre-command execution

**Deliverable**: Weekly automated reports + real-time pattern suggestions

### Phase 4: Self-Improvement (Week 7-8)

1. **PatternEvolutionTracker (AUTO-007)** (3 days)
   - File: `patterns/automation/analyzers/evolution_tracker.py`
   - Monitor pattern success rates over time
   - Flag patterns with <80% success for improvement
   - Propose v1.1, v1.2 versions automatically

2. **TemplateAutoGenerator (AUTO-008)** (4 days)
   - File: `patterns/automation/analyzers/template_generator.py`
   - Extract templates from 2-3 example files
   - Identify invariants and variables
   - Auto-create template files in `templates/auto-*`

3. **Feedback Loop Integration** (2 days)
   - Connect metrics → improvements → pattern updates
   - Auto-generate improvement PRs
   - Continuous evolution based on usage data

**Deliverable**: Self-improving pattern system with continuous evolution

### Week 9-10: Testing & Hardening

1. **Unit Tests** (3 days)
   - Test all 8 AUTO-* features
   - Edge cases: partial matches, low confidence, errors
   - Target: 80% code coverage

2. **Integration Tests** (3 days)
   - End-to-end pattern detection flow
   - Error learning loop validation
   - Auto-approval and quarantine workflows

3. **Performance Testing** (2 days)
   - Database query optimization
   - Pattern detection speed (target: <5 seconds)
   - Memory usage with 1000+ executions

**Deliverable**: Production-ready automation with full test coverage

### Week 11-12: CI/CD & Documentation

1. **GitHub Actions Workflows** (2 days)
   - `.github/workflows/pattern-automation.yml`
   - Scheduled jobs: Every 6 hours (detection), Weekly (reports), Monthly (cleanup)

2. **Monitoring & Alerting** (2 days)
   - Alert if pattern failure rate >40%
   - Alert if no new patterns detected in 7 days
   - Dashboard integration

3. **Documentation** (3 days)
   - User guide: How to use pattern automation
   - Developer guide: How to extend AUTO-* features
   - Runbook: Troubleshooting and rollback procedures

4. **Final Review** (2 days)
   - Security audit
   - Performance review
   - Stakeholder demo

**Deliverable**: Complete, documented, production-ready pattern automation system

### Week 13: Deployment & Monitoring

1. **Production Deployment** (2 days)
   - Enable automation in production
   - Monitor first week closely
   - Collect baseline metrics

2. **Tuning** (3 days)
   - Adjust confidence thresholds based on real data
   - Fine-tune quarantine triggers
   - Optimize scheduled job timing

**Deliverable**: Pattern automation live in production with monitoring

### Continuous (Ongoing)

1. **Weekly Reviews**: Check auto-generated pattern quality, adjust thresholds
2. **Monthly Audits**: Review anti-pattern registry, update recovery rules
3. **Quarterly Assessment**: Measure ROI vs manual pattern creation, report to stakeholders

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Executor completion takes longer than 2 weeks | High | High | Start with glossary patterns (already work) |
| Pattern detection yields low-quality candidates | Medium | Medium | Manual review gate, confidence thresholds |
| Error learning captures wrong patterns | Medium | High | Require 5+ occurrences instead of 3 |
| CI/CD overhead slows development | Low | Medium | Make automation opt-in initially |
| Database performance issues with telemetry | Low | Medium | Add indexes, archive old logs after 90 days |

**Overall Risk Level**: Medium (manageable with mitigations)

---

## Critical Files to Modify

Based on analysis, these files require changes for automation:

### Phase 0 (Foundation)
1. **Create**: `error/engine/error_engine.py` (new, 300+ lines)
2. **Create**: `core/state/migrations/add_pattern_telemetry.sql` (new, 100 lines)
3. **Complete**: `patterns/executors/batch_create_executor.ps1` (expand from stub to 400+ lines)
4. **Complete**: `patterns/executors/self_heal_executor.ps1` (expand from stub to 350+ lines)
5. **Create**: `scripts/validate_pattern_instance.ps1` (new, 150 lines)
6. **Create**: `scripts/validate_pattern_registry.ps1` (new, 100 lines)
7. **Create**: `scripts/verify_ground_truth.ps1` (new, 200 lines)

### Phase 1 (Telemetry)
8. **Modify**: `core/engine/orchestrator.py` (add hooks at lines 78, 172, 210)
9. **Modify**: `core/state/db.py` (add `log_execution()` method)

### Phase 2 (Detection)
10. **Create**: `patterns/automation/detectors/execution_detector.py` (new, 400+ lines)
11. **Create**: `patterns/automation/detectors/file_pattern_miner.py` (new, 250 lines)
12. **Create**: `patterns/automation/detectors/error_learner.py` (new, 350 lines)
13. **Create**: `scripts/auto_pattern_detector.py` (new, 200 lines)

### Phase 3 (Intelligence)
14. **Create**: `patterns/automation/analyzers/performance_analyzer.py` (new, 300 lines)
15. **Create**: `patterns/automation/detectors/anti_pattern_detector.py` (new, 250 lines)
16. **Create**: `patterns/automation/detectors/pattern_suggester.py` (new, 300 lines)

### Phase 4 (Self-Improvement)
17. **Create**: `patterns/automation/analyzers/evolution_tracker.py` (new, 250 lines)
18. **Create**: `patterns/automation/analyzers/template_generator.py` (new, 400 lines)

### Testing & CI/CD
19. **Create**: `tests/automation/test_execution_detector.py` (new, 200 lines)
20. **Create**: `tests/automation/test_error_learner.py` (new, 200 lines)
21. **Create**: `.github/workflows/pattern-automation.yml` (new, 100 lines)

**Total**: ~21 files, ~5,000 lines of new code + modifications

---

## Conclusion

The Pattern Automation Master Plan is **well-designed but incomplete**. By adding Phase 0 (foundation prerequisites) and addressing the 7 critical gaps, the plan becomes **implementable and realistic**.

**Key Changes from Original Plan**:
1. ✅ Add Phase 0 for missing infrastructure (2 weeks)
2. ✅ Extend timeline from 8 weeks to 13 weeks (deployment + monitoring)
3. ✅ Prioritize batch_create and self_heal executors (user preference)
4. ✅ Add aggressive mode with auto-approval at 75% confidence (user preference)
5. ✅ Add testing strategy and enhanced rollback plan (2 weeks)
6. ✅ Clarify hook points with specific file paths and line numbers
7. ✅ Set measurable success metrics with clear baselines
8. ✅ Full implementation scope - all 8 AUTO-* features (user preference)

**Implementation Approach**: Foundation-first (user preference)
- Build complete infrastructure before automation
- Prioritize stability over speed
- Comprehensive testing before production

**Risk Management**: Aggressive mode with safeguards
- Auto-approve patterns at 75% confidence
- Auto-quarantine at 40% failure rate
- Circuit breaker integration for resilience
- 90-day execution logs for forensics

**Go/No-Go Decision**: ✅ **GO** - With revised plan, automation is achievable and aligned with user preferences

**Expected ROI**: 70% reduction in pattern management overhead (unchanged)
**Revised Effort**: 13 weeks (1 developer, foundation-first approach)
**Risk Level**: Medium-Low (manageable with aggressive mode safeguards)
**Confidence**: High (foundation-first reduces implementation risk)
