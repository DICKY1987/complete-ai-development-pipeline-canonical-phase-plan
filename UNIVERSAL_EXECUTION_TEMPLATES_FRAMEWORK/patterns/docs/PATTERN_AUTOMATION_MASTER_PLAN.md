# Pattern Automation Master Plan

**DOC_ID:** DOC-PAT-AUTO-MASTER-001  
**Created:** 2025-11-25  
**Status:** PROPOSAL  
**Purpose:** Remove user from pattern capture loop and automate execution learning

---

## Vision

**Current State:** Manual pattern discovery → Manual template creation → Manual execution  
**Target State:** Automatic pattern detection → Auto-generated templates → Self-improving execution system

---

## Automation Opportunities

### 🎯 **Tier 1: Zero-Touch Pattern Capture** (Highest Impact)

#### 1.1 Execution Telemetry System
**Integration Point:** `core/executor.py`, `core/orchestrator.py`

```python
# AUTO-001: Execution Pattern Detector
# Hook into existing execution engine to capture repetitive work

from core.executor import Executor
from core.state.db import get_db

class ExecutionPatternDetector:
    """Automatically detect repetitive execution patterns."""
    
    def __init__(self):
        self.db = get_db()
        self.similarity_threshold = 0.75
    
    def on_execution_complete(self, execution_record):
        """Called by orchestrator after each execution."""
        # Log execution signature
        signature = self._extract_signature(execution_record)
        self._store_execution(signature)
        
        # Check for pattern (3+ similar executions)
        similar = self._find_similar_executions(signature)
        
        if len(similar) >= 3:
            # AUTO-GENERATE pattern template
            pattern = self._synthesize_pattern(similar)
            self._create_pattern_draft(pattern)
            self._notify_user(pattern)
    
    def _extract_signature(self, record):
        """Extract execution fingerprint."""
        return {
            'operation_kind': record.get('operation_kind'),
            'file_types': self._extract_file_types(record),
            'tool_sequence': record.get('tools_used', []),
            'input_structure': self._extract_input_shape(record),
            'output_structure': self._extract_output_shape(record),
            'verification_method': record.get('verification')
        }
    
    def _synthesize_pattern(self, executions):
        """Generate pattern YAML from execution history."""
        # Extract invariants (same across all)
        # Extract variables (different per execution)
        # Generate template structure
        return {
            'pattern_id': self._generate_pattern_id(),
            'name': self._infer_pattern_name(executions),
            'invariants': self._extract_invariants(executions),
            'variables': self._extract_variables(executions),
            'template': self._generate_template(executions),
            'confidence': self._calculate_confidence(executions),
            'time_savings_estimate': self._estimate_savings(executions)
        }
```

**Hook Points:**
- `core/orchestrator.py::execute()` - Add `detector.on_execution_complete(result)`
- `core/state/db.py` - Add `executions_log` table
- `error/engine/error_engine.py` - Learn from error patterns

**Output:**
- `patterns/drafts/AUTO-{timestamp}-{name}.pattern.yaml` (auto-generated)
- `patterns/reports/pattern_candidates_weekly.md` (digest report)

---

#### 1.2 File Operation Pattern Miner
**Integration Point:** `core/file_lifecycle.py`

```python
# AUTO-002: File Creation Pattern Learner
# Detect when user creates N similar files manually

class FilePatternMiner:
    """Watch file operations for repetitive patterns."""
    
    def on_file_created(self, filepath, content):
        """Hook into file creation."""
        # Extract file metadata
        signature = {
            'extension': filepath.suffix,
            'structure': self._analyze_structure(content),
            'sections': self._extract_sections(content),
            'directory': filepath.parent
        }
        
        # Store in time window (last 24 hours)
        recent = self._get_recent_similar(signature, hours=24)
        
        if len(recent) >= 2:  # After 3rd similar file
            template = self._extract_template(recent + [content])
            self._propose_batch_pattern(template, filepath.parent)
```

**Hook Points:**
- `core/file_lifecycle.py` - Instrument all file writes
- Git hooks (pre-commit) - Analyze staged files

**Output:**
- "🤖 Detected pattern: You've created 3 similar YAML files. Generate template?"
- Auto-create `templates/auto-{name}.template.yaml`

---

#### 1.3 Error Recovery Pattern Learner
**Integration Point:** `error/engine/error_engine.py`

```python
# AUTO-003: Self-Healing Pattern Extractor
# Learn successful error fixes and create recovery patterns

class ErrorRecoveryPatternLearner:
    """Extract patterns from successful error recoveries."""
    
    def on_error_resolved(self, error_record, resolution):
        """Called when error fixed successfully."""
        # Store error signature + resolution
        pattern = {
            'error_type': error_record['type'],
            'error_signature': error_record['signature'],
            'resolution_steps': resolution['steps'],
            'success_rate': 1.0
        }
        
        # Find similar past errors
        similar = self._find_similar_errors(error_record)
        
        if len(similar) >= 3 and self._all_same_fix(similar):
            # Auto-create self-healing pattern
            healing_pattern = self._create_healing_pattern(similar)
            self._register_auto_fix(healing_pattern)
```

**Hook Points:**
- `error/engine/error_engine.py::resolve_error()` - Log resolution
- `error/plugins/*` - Track fix success rates

**Output:**
- `patterns/specs/self_heal/AUTO-{error-type}.yaml`
- Auto-apply on next occurrence (with confirmation)

---

### ⚡ **Tier 2: Execution Intelligence** (High Impact)

#### 2.1 Execution Report Generator
**Automation:** Generate pattern improvement reports from execution data

```python
# AUTO-004: Pattern Performance Analyzer
# Automatic weekly reports on pattern usage and effectiveness

class PatternPerformanceAnalyzer:
    """Generate insights from pattern execution data."""
    
    def generate_weekly_report(self):
        """Run as scheduled job (cron/Task Scheduler)."""
        patterns = self._load_all_patterns()
        executions = self._get_executions_last_week()
        
        report = {
            'top_patterns': self._rank_by_usage(executions),
            'time_saved': self._calculate_total_savings(executions),
            'underused_patterns': self._find_underused(patterns, executions),
            'new_pattern_candidates': self._detect_manual_work(executions),
            'anti_patterns': self._detect_failures(executions)
        }
        
        self._write_report(report, 'patterns/reports/weekly/')
        self._update_pattern_index(report)
```

**Schedule:** Weekly cron job
```bash
# .github/workflows/pattern-analysis.yml
- cron: '0 0 * * 0'  # Every Sunday
  run: python scripts/analyze_pattern_usage.py --report
```

**Output:**
```markdown
# Pattern Usage Report - Week 47 2025

## 🏆 Top Patterns (by usage)
1. PAT-ATOMIC-CREATE-001: 47 uses, 23 hours saved
2. PAT-BATCH-CREATE-001: 31 uses, 18 hours saved
3. PAT-SELF-HEAL-001: 28 uses, 14 hours saved

## 📈 New Pattern Candidates
- **File pattern detected**: 12 similar test files created manually
  → Suggest: PAT-TEST-CREATE-002
- **Execution pattern detected**: 8 similar refactor operations
  → Suggest: PAT-REFACTOR-STANDARD-001

## ⚠️ Anti-Patterns Detected
- PAT-BATCH-CREATE-001 failed 3 times (template too rigid)
  → Recommendation: Add flexibility to variable substitution
- Manual workarounds detected for PAT-SELF-HEAL-001
  → Gap: Can't handle async errors

## 🔧 Recommended Actions
1. Create template for test file pattern (73% similar)
2. Improve PAT-BATCH-CREATE-001 variable handling
3. Add async error support to PAT-SELF-HEAL-001
```

---

#### 2.2 Anti-Pattern Detector
**Automation:** Learn from failures and blocked patterns

```python
# AUTO-005: Anti-Pattern Learning System
# Automatically detect and document what NOT to do

class AntiPatternDetector:
    """Learn from pattern failures and execution mistakes."""
    
    def detect_anti_patterns(self):
        """Run after execution failures."""
        failures = self._get_failed_executions(last_days=7)
        
        anti_patterns = []
        for failure in failures:
            if self._is_recurring(failure):
                anti_pattern = {
                    'type': 'execution_failure',
                    'pattern_id': failure['pattern_id'],
                    'failure_signature': failure['error'],
                    'frequency': self._count_occurrences(failure),
                    'root_cause': self._infer_cause(failure),
                    'recommendation': self._generate_fix(failure)
                }
                anti_patterns.append(anti_pattern)
        
        self._update_anti_pattern_registry(anti_patterns)
    
    def _infer_cause(self, failure):
        """Use error detection to categorize failure."""
        # Integration with error/engine
        causes = {
            'template_too_rigid': 'Variables not flexible enough',
            'missing_dependency': 'Required tool not available',
            'wrong_context': 'Pattern applied to wrong file type',
            'verification_failed': 'Ground truth criteria too strict'
        }
        return self._classify(failure, causes)
```

**Output:**
- `patterns/anti_patterns/ANTI-PAT-{ID}.md`
- Updates to `ai_policies.yaml` forbidden patterns

Example:
```yaml
# patterns/anti_patterns/registry.yaml
anti_patterns:
  - id: ANTI-PAT-001
    name: "Rigid Template Variables"
    description: "Template requires exact variable format, fails on variations"
    detected: 2025-11-25
    occurrences: 7
    affected_patterns:
      - PAT-BATCH-CREATE-001
    fix: "Use flexible regex for variable substitution"
    status: "fixed_in_v1.1"
  
  - id: ANTI-PAT-002
    name: "Over-Verification"
    description: "Ground truth checks too strict, rejects valid output"
    detected: 2025-11-18
    occurrences: 4
    fix: "Relax verification to existence + basic structure"
    status: "active"
```

---

#### 2.3 Pattern Suggestion Engine
**Automation:** Proactive pattern recommendations during work

```python
# AUTO-006: Context-Aware Pattern Suggester
# Suggest patterns before user starts manual work

class PatternSuggester:
    """Real-time pattern suggestions based on context."""
    
    def on_user_action(self, action, context):
        """Hook into UI/CLI before execution."""
        # User about to create file
        if action == 'create_file':
            similar = self._find_similar_files(context['directory'])
            if len(similar) >= 2:
                self._suggest_batch_pattern(similar, context)
        
        # User about to refactor
        if action == 'refactor':
            if self._matches_known_pattern(context):
                self._suggest_existing_pattern(context)
        
        # User repeating same operation
        recent = self._get_recent_operations(minutes=30)
        if self._is_repetitive(recent):
            self._suggest_automation(recent)
```

**Integration Points:**
- `core/ui_cli.py` - CLI command interceptor
- Git pre-commit hook - Analyze staged changes
- File watcher - Monitor file system events

**Output:**
```bash
$ # User types: "create file core/plugins/new_module.py"

💡 Pattern Suggestion:
   You've created 3 similar plugin files in the last hour.
   
   Use pattern: PAT-MODULE-CREATE-002
   Estimated time savings: 15 minutes per file
   
   Continue manually? (y/n) or Apply pattern? (p)
```

---

### 🔄 **Tier 3: Self-Improving Execution** (Medium Impact)

#### 3.1 Pattern Evolution Tracker

```python
# AUTO-007: Pattern Version Control
# Track pattern effectiveness and auto-suggest improvements

class PatternEvolutionTracker:
    """Monitor pattern performance over time."""
    
    def track_pattern_metrics(self, pattern_id):
        """Continuous monitoring."""
        metrics = {
            'success_rate': self._calculate_success_rate(pattern_id),
            'avg_time_saved': self._calculate_avg_savings(pattern_id),
            'user_satisfaction': self._get_user_feedback(pattern_id),
            'edge_cases': self._collect_edge_cases(pattern_id),
            'workarounds_needed': self._count_workarounds(pattern_id)
        }
        
        if metrics['success_rate'] < 0.8:
            self._flag_for_improvement(pattern_id, metrics)
        
        if metrics['edge_cases'] >= 5:
            self._propose_pattern_variants(pattern_id, metrics)
```

**Output:**
```yaml
# patterns/reports/evolution/{pattern_id}.yaml
pattern_id: PAT-BATCH-CREATE-001
version: "1.0.0"
performance:
  success_rate: 0.73  # Below threshold
  avg_time_saved: 42min
  total_uses: 127
  
issues_detected:
  - "Fails on nested variable substitution (8 occurrences)"
  - "Can't handle multi-line template values (5 occurrences)"
  - "Users manually fix output in 19% of cases"

recommended_improvements:
  - priority: high
    change: "Add recursive variable substitution"
    estimated_impact: "+15% success rate"
  
  - priority: medium
    change: "Support YAML/JSON multi-line values"
    estimated_impact: "+8% success rate"

proposed_version: "1.1.0"
auto_generated_spec: "patterns/drafts/batch_create_v1.1.yaml"
```

---

#### 3.2 Template Auto-Generator

```python
# AUTO-008: Template Generator from Examples
# Skip manual template creation phase

class TemplateAutoGenerator:
    """Generate templates from example files automatically."""
    
    def generate_from_examples(self, example_files):
        """Input: 2-3 example files, Output: Template."""
        # Structural diff analysis
        structures = [self._parse_structure(f) for f in example_files]
        
        # Find invariants (same in all)
        invariants = self._extract_common_elements(structures)
        
        # Find variables (different in each)
        variables = self._extract_varying_elements(structures)
        
        # Generate template with placeholders
        template = self._synthesize_template(invariants, variables)
        
        return {
            'template': template,
            'variables': self._generate_variable_schema(variables),
            'confidence': self._calculate_confidence(structures),
            'suggested_name': self._infer_template_name(example_files)
        }
```

**Usage:**
```bash
# User creates 3 similar files manually
$ git add module1.yaml module2.yaml module3.yaml

# Git hook detects pattern
🤖 Pattern detected in staged files.
   Generated template: templates/auto-module-manifest.yaml
   Variables detected: {module_name}, {purpose}, {layer}
   
   Apply to remaining 14 modules? (y/n)
```

---

### 🛠️ **Tier 4: Infrastructure Automation** (Foundation)

#### 4.1 Scheduled Jobs

```yaml
# .github/workflows/pattern-automation.yml
name: Pattern Automation

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours: Pattern detection
    - cron: '0 0 * * 0'    # Weekly: Performance reports
    - cron: '0 0 1 * *'    # Monthly: Pattern cleanup

jobs:
  detect_patterns:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Analyze executions
        run: python scripts/auto_pattern_detector.py --analyze
      - name: Generate candidates
        run: python scripts/auto_pattern_detector.py --suggest
      - name: Create PR
        run: |
          if [ -d "patterns/drafts" ]; then
            gh pr create --title "Auto-detected patterns" \
                         --body "$(cat patterns/reports/pattern_candidates.md)"
          fi
  
  performance_report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate weekly report
        run: python scripts/analyze_pattern_usage.py --report
      - name: Update docs
        run: python scripts/update_pattern_metrics.py
  
  cleanup_patterns:
    runs-on: ubuntu-latest
    steps:
      - name: Archive unused patterns
        run: python scripts/cleanup_patterns.py --archive-unused
      - name: Update anti-pattern registry
        run: python scripts/update_anti_patterns.py
```

---

#### 4.2 Database Schema for Telemetry

```sql
-- core/state/migrations/add_pattern_telemetry.sql

CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_kind TEXT,
    pattern_id TEXT,
    file_types TEXT,  -- JSON array
    tools_used TEXT,  -- JSON array
    input_signature TEXT,
    output_signature TEXT,
    success BOOLEAN,
    time_taken_seconds INTEGER,
    user_id TEXT
);

CREATE TABLE IF NOT EXISTS pattern_metrics (
    pattern_id TEXT PRIMARY KEY,
    version TEXT,
    total_uses INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    total_time_saved_minutes INTEGER DEFAULT 0,
    last_used DATETIME,
    confidence_score REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS pattern_candidates (
    id INTEGER PRIMARY KEY,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    signature TEXT,
    example_executions TEXT,  -- JSON array
    confidence REAL,
    status TEXT DEFAULT 'pending',  -- pending|approved|rejected
    auto_generated_spec TEXT
);

CREATE TABLE IF NOT EXISTS anti_patterns (
    id TEXT PRIMARY KEY,
    name TEXT,
    detected_at DATETIME,
    occurrences INTEGER,
    affected_patterns TEXT,  -- JSON array
    status TEXT DEFAULT 'active'  -- active|fixed|archived
);

CREATE INDEX idx_executions_pattern ON execution_logs(pattern_id);
CREATE INDEX idx_executions_timestamp ON execution_logs(timestamp);
CREATE INDEX idx_candidates_status ON pattern_candidates(status);
```

---

## Implementation Roadmap

### Phase 1: Telemetry Foundation (Week 1-2)
- ✅ Add execution logging to `core/executor.py`
- ✅ Create database schema
- ✅ Instrument file operations in `core/file_lifecycle.py`
- ✅ Add hooks to error resolution in `error/engine/error_engine.py`

**Deliverable:** Data collection infrastructure

---

### Phase 2: Pattern Detection (Week 3-4)
- ✅ Implement `ExecutionPatternDetector` (AUTO-001)
- ✅ Implement `FilePatternMiner` (AUTO-002)
- ✅ Implement `ErrorRecoveryPatternLearner` (AUTO-003)
- ✅ Set up weekly scheduled jobs

**Deliverable:** Auto-generated pattern candidates

---

### Phase 3: Intelligence Layer (Week 5-6)
- ✅ Implement `PatternPerformanceAnalyzer` (AUTO-004)
- ✅ Implement `AntiPatternDetector` (AUTO-005)
- ✅ Implement `PatternSuggester` (AUTO-006)

**Deliverable:** Automated reports and suggestions

---

### Phase 4: Self-Improvement (Week 7-8)
- ✅ Implement `PatternEvolutionTracker` (AUTO-007)
- ✅ Implement `TemplateAutoGenerator` (AUTO-008)
- ✅ Build feedback loop (metrics → improvements → patterns)

**Deliverable:** Self-improving pattern system

---

## Success Metrics

### Baseline (Current)
- Pattern detection: 100% manual
- Template creation: 100% manual (2 hours per pattern)
- Pattern improvement: Ad-hoc
- Anti-pattern identification: Manual

### Target (After Automation)
- Pattern detection: 80% automatic
- Template creation: 60% auto-generated (15 min review)
- Pattern improvement: Continuous (weekly reports)
- Anti-pattern identification: 90% automatic
- User time savings: 70% reduction in pattern management overhead

---

## Integration Points Summary

| System Component | Hook Point | Automation |
|-----------------|------------|------------|
| `core/executor.py` | `execute()` completion | Log execution signature |
| `core/orchestrator.py` | Job completion | Pattern detection trigger |
| `core/file_lifecycle.py` | File write operations | File pattern mining |
| `error/engine/error_engine.py` | Error resolution | Self-healing pattern extraction |
| `core/ui_cli.py` | Command invocation | Real-time pattern suggestions |
| `core/state/db.py` | Database | Telemetry storage |
| Git hooks | pre-commit | File pattern detection |
| CI/CD | Scheduled workflows | Periodic analysis |

---

## File Structure (New)

```
patterns/
├── automation/                          # NEW
│   ├── detectors/
│   │   ├── execution_detector.py       # AUTO-001
│   │   ├── file_pattern_miner.py       # AUTO-002
│   │   ├── error_learner.py            # AUTO-003
│   │   ├── anti_pattern_detector.py    # AUTO-005
│   │   └── pattern_suggester.py        # AUTO-006
│   ├── analyzers/
│   │   ├── performance_analyzer.py     # AUTO-004
│   │   ├── evolution_tracker.py        # AUTO-007
│   │   └── template_generator.py       # AUTO-008
│   └── config/
│       ├── detection_rules.yaml
│       └── suggestion_rules.yaml
├── drafts/                              # NEW: Auto-generated patterns
│   └── AUTO-*.pattern.yaml
├── reports/                             # ENHANCED
│   ├── weekly/
│   ├── evolution/
│   └── pattern_candidates.md
├── anti_patterns/                       # NEW
│   ├── registry.yaml
│   └── ANTI-PAT-*.md
└── metrics/                             # NEW
    └── pattern_performance.db
```

---

## Quick Start

```bash
# 1. Set up telemetry
python scripts/setup_pattern_telemetry.py

# 2. Enable automation
python scripts/enable_pattern_automation.py --all

# 3. Run first analysis (manual)
python scripts/auto_pattern_detector.py --analyze --suggest

# 4. Review candidates
cat patterns/reports/pattern_candidates.md

# 5. Approve auto-generated pattern
python scripts/approve_pattern.py --id AUTO-2025-11-25-001

# 6. Schedule weekly reports
# (GitHub Actions workflow auto-enabled)
```

---

## Next Steps

1. **Immediate:** Review and approve this plan
2. **Week 1:** Implement telemetry foundation (Phase 1)
3. **Week 2:** Test pattern detection with existing executions
4. **Week 3:** Deploy first automated weekly report
5. **Month 2:** Evaluate automation effectiveness, tune thresholds
6. **Month 3:** Roll out real-time pattern suggestions

---

**Status:** READY FOR IMPLEMENTATION  
**Estimated Effort:** 8 weeks (1 developer)  
**Expected ROI:** 70% reduction in pattern management overhead  
**Risk:** Low (non-invasive instrumentation, opt-in features)
