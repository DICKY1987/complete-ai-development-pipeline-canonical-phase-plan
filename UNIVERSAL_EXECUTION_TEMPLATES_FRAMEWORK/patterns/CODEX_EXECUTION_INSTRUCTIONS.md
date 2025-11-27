# CODEX CLI EXECUTION INSTRUCTIONS
# Pattern Automation Activation - Complete Execution Guide

## MISSION

Execute the **Pattern Automation Activation Plan** to activate the 70% complete pattern automation system. Follow the phase plan exactly as documented.

---

## FILE LOCATIONS

### Primary Plan Document
**Location:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PATTERN_AUTOMATION_ACTIVATION_PLAN.md`

This is your **master execution plan**. Read it completely before starting.

### Execution Patterns (Use These to Execute Each Phase)

All patterns are in: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/`

1. **Phase 0 Pattern:** `phase_discovery.pattern.yaml` - PAT-PHASE-DISCOVERY-001
2. **Phase 1 Pattern:** `database_setup.pattern.yaml` - PAT-DATABASE-SETUP-001
3. **Phase 2 Pattern:** `integration_hook.pattern.yaml` - PAT-INTEGRATION-HOOK-001
4. **Phase 3 Pattern:** `configuration_setup.pattern.yaml` - PAT-CONFIG-SETUP-001
5. **Phase 4 Pattern:** `validation_e2e.pattern.yaml` - PAT-E2E-VALIDATION-001

### Existing Automation Code (70% Complete)

**Detectors (Already Built):**
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/execution_detector.py`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/anti_pattern_detector.py`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/file_pattern_miner.py`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/error_learner.py`

**Analyzers (Already Built):**
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/analyzers/`

**Registry:**
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/registry/PATTERN_INDEX.yaml` (24 existing patterns)

### Quick Start Reference
**Location:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/QUICK_START_AUTOMATION.md`

Contains the 30-45 minute quick activation guide (alternative to full plan).

---

## EXECUTION INSTRUCTIONS

### CRITICAL RULES

1. **Read the activation plan first**
   ```bash
   # Read this file completely before starting
   cat UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PATTERN_AUTOMATION_ACTIVATION_PLAN.md
   ```

2. **Execute phases sequentially** - Do NOT skip phases
   - Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4

3. **Use the execution patterns** - Each phase has a corresponding pattern to guide you

4. **Document all findings** - Create the output files specified in each phase

5. **Validate after each phase** - Check success criteria before proceeding

---

## PHASE-BY-PHASE EXECUTION

### PHASE 0: Repository Discovery (15 minutes)

**Goal:** Locate core/engine/state modules in the repository

**Pattern to Use:** `specs/phase_discovery.pattern.yaml` (PAT-PHASE-DISCOVERY-001)

**What to Do:**

1. **Search for orchestrator/executor modules:**
   ```powershell
   Get-ChildItem "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan" `
       -Recurse -Include "*orchestrator*.py","*executor*.py","*engine*.py" -Depth 3 `
       | Select-Object Name, Directory, FullName
   ```

2. **Search for database files:**
   ```powershell
   Get-ChildItem "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan" `
       -Recurse -Include "*.db","*migration*.sql","db.py" -Depth 3 `
       | Select-Object Name, Directory, FullName
   ```

3. **Search for error engine:**
   ```powershell
   Get-ChildItem "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan" `
       -Recurse -Include "*error*engine*.py" -Depth 3 `
       | Select-Object Name, Directory
   ```

4. **List top-level directories:**
   ```powershell
   $root = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
   Get-ChildItem $root -Directory -Depth 1 | Where-Object {$_.Name -notlike ".*"} | Select-Object Name
   ```

5. **Create discovery documentation:**
   ```bash
   # Create this file with your findings
   File: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PATTERN_AUTOMATION_PATHS.md
   
   Include:
   - Location of orchestrator module (if found)
   - Location of database system
   - Location of error engine (if exists)
   - Import paths for each module
   - Directory structure overview
   ```

**Success Criteria:**
- [ ] All search commands executed
- [ ] PATTERN_AUTOMATION_PATHS.md created
- [ ] All required modules located OR documented as missing
- [ ] Actual import paths documented

**Output File:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PATTERN_AUTOMATION_PATHS.md`

---

### PHASE 1: Database Setup (10 minutes)

**Goal:** Create 3 database tables for execution telemetry

**Pattern to Use:** `specs/database_setup.pattern.yaml` (PAT-DATABASE-SETUP-001)

**What to Do:**

1. **Choose database approach** (based on Phase 0 findings):
   - **Option A:** If migrations exist → create migration file
   - **Option B:** If no migration system → direct SQL execution
   - **Option C:** If no central DB → create standalone DB at `patterns/metrics/pattern_automation.db`

2. **Create SQL schema file:**
   ```sql
   -- File: patterns/metrics/004_pattern_automation.sql (or temp_schema.sql)
   
   CREATE TABLE IF NOT EXISTS execution_logs (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
       operation_kind TEXT NOT NULL,
       file_types TEXT,
       tools_used TEXT,
       input_signature TEXT,
       output_signature TEXT,
       success BOOLEAN NOT NULL,
       time_taken_seconds REAL,
       context TEXT
   );
   
   CREATE TABLE IF NOT EXISTS pattern_candidates (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       pattern_id TEXT UNIQUE,
       signature TEXT,
       example_executions TEXT,
       confidence REAL,
       auto_generated_spec TEXT,
       status TEXT DEFAULT 'pending',
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE TABLE IF NOT EXISTS anti_patterns (
       id TEXT PRIMARY KEY,
       name TEXT NOT NULL,
       description TEXT,
       affected_patterns TEXT,
       failure_signature TEXT,
       recommendation TEXT,
       status TEXT DEFAULT 'active',
       occurrences INTEGER DEFAULT 1,
       first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   
   -- Indexes
   CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_logs(timestamp);
   CREATE INDEX IF NOT EXISTS idx_execution_operation ON execution_logs(operation_kind);
   CREATE INDEX IF NOT EXISTS idx_execution_success ON execution_logs(success);
   CREATE INDEX IF NOT EXISTS idx_execution_signature ON execution_logs(input_signature, output_signature);
   CREATE INDEX IF NOT EXISTS idx_pattern_status ON pattern_candidates(status);
   CREATE INDEX IF NOT EXISTS idx_anti_pattern_status ON anti_patterns(status);
   ```

3. **Create rollback script:**
   ```sql
   -- File: patterns/metrics/rollback_pattern_automation.sql
   
   DROP TABLE IF EXISTS execution_logs;
   DROP TABLE IF EXISTS pattern_candidates;
   DROP TABLE IF EXISTS anti_patterns;
   ```

4. **Create database directory:**
   ```powershell
   New-Item -ItemType Directory -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics" -Force
   ```

5. **Execute SQL to create tables:**
   ```powershell
   # For standalone SQLite database (Option C - most likely)
   $dbPath = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics/pattern_automation.db"
   
   # Create database
   sqlite3 $dbPath "SELECT 1;"
   
   # Execute schema
   Get-Content "patterns/metrics/004_pattern_automation.sql" | sqlite3 $dbPath
   ```

6. **Verify tables created:**
   ```powershell
   # Check tables exist
   sqlite3 $dbPath ".tables"
   
   # Should show: anti_patterns  execution_logs  pattern_candidates
   
   # Check schema
   sqlite3 $dbPath ".schema execution_logs"
   ```

**Success Criteria:**
- [ ] Database file created at specified path
- [ ] All 3 tables created (execution_logs, pattern_candidates, anti_patterns)
- [ ] All 6 indexes created
- [ ] Rollback script exists
- [ ] Tables verified with `.tables` command

**Output Files:**
- `patterns/metrics/pattern_automation.db`
- `patterns/metrics/004_pattern_automation.sql`
- `patterns/metrics/rollback_pattern_automation.sql`

---

### PHASE 2: Orchestrator Integration (15 minutes)

**Goal:** Create hook module for execution logging

**Pattern to Use:** `specs/integration_hook.pattern.yaml` (PAT-INTEGRATION-HOOK-001)

**What to Do:**

1. **Create integration directory:**
   ```powershell
   New-Item -ItemType Directory -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/integration" -Force
   ```

2. **Create hook module:**
   ```bash
   # File: automation/integration/orchestrator_hooks.py
   # Copy the code from Phase 2, Step 2.2 in PATTERN_AUTOMATION_ACTIVATION_PLAN.md
   # Lines 438-623 of the plan document
   ```

   **Quick reference - Key parts to include:**
   - `PatternAutomationHooks` class
   - `on_task_start()` method
   - `on_task_complete()` method
   - Helper methods for extraction and hashing
   - Singleton `get_hooks()` function

3. **Create integration README:**
   ```bash
   # File: automation/integration/README.md
   # Copy the integration instructions from Phase 2, Step 2.3 in the plan
   # Lines 625-660
   ```

4. **Create __init__.py files:**
   ```powershell
   # Make it a proper Python package
   New-Item -ItemType File -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/__init__.py" -Force
   New-Item -ItemType File -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/integration/__init__.py" -Force
   ```

5. **Test import:**
   ```powershell
   # Verify the module can be imported
   cd "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns"
   python -c "from automation.integration.orchestrator_hooks import get_hooks; print('Import successful')"
   ```

**Success Criteria:**
- [ ] automation/integration/ directory created
- [ ] orchestrator_hooks.py created with all required code
- [ ] README.md created with integration instructions
- [ ] Module imports without errors
- [ ] No syntax errors in Python code

**Output Files:**
- `automation/integration/orchestrator_hooks.py`
- `automation/integration/README.md`
- `automation/integration/__init__.py`
- `automation/__init__.py`

---

### PHASE 3: Configuration Setup (5 minutes)

**Goal:** Create configuration file with detection thresholds

**Pattern to Use:** `specs/configuration_setup.pattern.yaml` (PAT-CONFIG-SETUP-001)

**What to Do:**

1. **Create config directory:**
   ```powershell
   New-Item -ItemType Directory -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/config" -Force
   ```

2. **Create configuration file:**
   ```yaml
   # File: automation/config/detection_config.yaml
   
   # Pattern Automation Configuration
   # Created: 2025-11-27
   
   version: "1.0.0"
   
   # Feature flags
   automation_enabled: true
   auto_approve_high_confidence: true
   
   # Detection thresholds
   detection:
     min_similar_executions: 3
     similarity_threshold: 0.75
     lookback_days: 30
     auto_approval_confidence: 0.75
   
   # Database
   database:
     path: "patterns/metrics/pattern_automation.db"
   
   # Output
   output:
     drafts_dir: "patterns/drafts"
     reports_dir: "patterns/reports"
   
   # Anti-pattern detection
   anti_patterns:
     enabled: true
     min_occurrences: 3
   
   # File pattern mining
   file_patterns:
     enabled: true
     time_window_hours: 24
     min_similar_files: 3
   ```

3. **Validate YAML syntax:**
   ```powershell
   # Check YAML is valid
   python -c "import yaml; yaml.safe_load(open('automation/config/detection_config.yaml'))"
   ```

**Success Criteria:**
- [ ] automation/config/ directory created
- [ ] detection_config.yaml created
- [ ] YAML syntax is valid
- [ ] All required settings present

**Output Files:**
- `automation/config/detection_config.yaml`

---

### PHASE 4: Validation & Testing (10 minutes)

**Goal:** Verify automation works end-to-end

**Pattern to Use:** `specs/validation_e2e.pattern.yaml` (PAT-E2E-VALIDATION-001)

**What to Do:**

1. **Create tests directory:**
   ```powershell
   New-Item -ItemType Directory -Path "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/tests" -Force
   ```

2. **Create validation test script:**
   ```bash
   # File: automation/tests/test_activation.ps1
   # Copy the test script from Phase 4, Section 4.1 in the plan
   # Lines 771-870
   ```

   **The script should test:**
   - Database tables exist
   - Configuration file loads
   - Integration module imports
   - Execution logging works
   - Database entries can be created

3. **Create demo script (optional but recommended):**
   ```bash
   # File: automation/tests/demo_pattern_detection.ps1
   # Copy demo script from Phase 4, Section 4.3 in the plan
   # Lines 891-937
   ```

4. **Run validation tests:**
   ```powershell
   cd "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns"
   .\automation\tests\test_activation.ps1
   ```

5. **Run demo (if created):**
   ```powershell
   .\automation\tests\demo_pattern_detection.ps1
   ```

6. **Check results:**
   ```powershell
   # Verify execution logs
   sqlite3 patterns/metrics/pattern_automation.db "SELECT COUNT(*) FROM execution_logs;"
   
   # Check for pattern candidates
   sqlite3 patterns/metrics/pattern_automation.db "SELECT pattern_id, confidence, status FROM pattern_candidates;"
   
   # Look for auto-generated patterns
   Get-ChildItem patterns/drafts/AUTO-*.yaml
   ```

**Success Criteria:**
- [ ] All 5 validation tests pass
- [ ] Database contains execution logs
- [ ] No Python import errors
- [ ] Test script runs without errors
- [ ] (Optional) Demo generates pattern after 3 runs

**Output Files:**
- `automation/tests/test_activation.ps1`
- `automation/tests/demo_pattern_detection.ps1` (optional)
- Execution logs in database
- (Optional) AUTO-*.yaml files in patterns/drafts/

---

## POST-ACTIVATION VERIFICATION

After completing all phases, run these checks:

### System Health Check

```powershell
cd "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns"

# 1. Check database
sqlite3 patterns/metrics/pattern_automation.db ".tables"
# Expected: anti_patterns  execution_logs  pattern_candidates

# 2. Check execution logs count
sqlite3 patterns/metrics/pattern_automation.db "SELECT COUNT(*) FROM execution_logs;"
# Expected: > 0

# 3. Check integration module
python -c "from automation.integration.orchestrator_hooks import get_hooks; h = get_hooks('patterns/metrics/pattern_automation.db'); print('✓ Hooks working')"

# 4. Check configuration
python -c "import yaml; c = yaml.safe_load(open('automation/config/detection_config.yaml')); print('✓ Config valid')"

# 5. List all created files
Get-ChildItem -Recurse -Include "*.py","*.yaml","*.sql","*.db","*.ps1" | 
    Where-Object {$_.LastWriteTime -gt (Get-Date).AddHours(-2)} |
    Select-Object FullName, Length
```

### Expected File Structure

After completion, you should have:

```
patterns/
├── PATTERN_AUTOMATION_PATHS.md          ✅ Phase 0 output
├── automation/
│   ├── config/
│   │   └── detection_config.yaml        ✅ Phase 3 output
│   ├── integration/
│   │   ├── __init__.py                  ✅ Phase 2 output
│   │   ├── orchestrator_hooks.py        ✅ Phase 2 output
│   │   └── README.md                    ✅ Phase 2 output
│   ├── tests/
│   │   ├── test_activation.ps1          ✅ Phase 4 output
│   │   └── demo_pattern_detection.ps1   ✅ Phase 4 output (optional)
│   └── detectors/                       ✅ Already exists (70% complete)
├── metrics/
│   ├── pattern_automation.db            ✅ Phase 1 output
│   ├── 004_pattern_automation.sql       ✅ Phase 1 output
│   └── rollback_pattern_automation.sql  ✅ Phase 1 output
└── drafts/                              ✅ Created during demo (optional)
    └── AUTO-*.yaml                      ✅ Auto-generated (optional)
```

---

## TROUBLESHOOTING

### If Phase 0 can't find modules:
- Document as "NOT FOUND" in PATTERN_AUTOMATION_PATHS.md
- Note: This is a standalone pattern system, may not have central orchestrator
- Proceed to Phase 1 with standalone database approach (Option C)

### If database creation fails:
- Ensure sqlite3 is in PATH
- Try direct PowerShell: `sqlite3 patterns/metrics/pattern_automation.db "CREATE TABLE test (id INT);"`
- Use rollback script if needed

### If Python imports fail:
- Check PYTHONPATH includes patterns directory
- Verify __init__.py files exist in all directories
- Check for syntax errors with `python -m py_compile <file>`

### If validation tests fail:
- Check specific error messages
- Verify database path is correct
- Ensure all previous phases completed successfully
- Review Phase 0 findings for correct paths

---

## SUCCESS INDICATORS

You know activation succeeded when:

1. ✅ All 5 phases completed without errors
2. ✅ Database has 3 tables with 6 indexes
3. ✅ Hook module imports successfully
4. ✅ Configuration loads without errors
5. ✅ Validation script shows 5/5 tests passed
6. ✅ (Optional) Demo generates AUTO-*.yaml pattern after 3 similar tasks

---

## FINAL DELIVERABLE

Create a completion report:

```markdown
# File: ACTIVATION_COMPLETION_REPORT.md

# Pattern Automation Activation - Completion Report

**Date:** 2025-11-27
**Status:** [COMPLETE / PARTIAL / FAILED]

## Phase Results

- [x] Phase 0: Discovery - ✅ COMPLETE
  - Found: [list modules found]
  - Output: PATTERN_AUTOMATION_PATHS.md

- [x] Phase 1: Database Setup - ✅ COMPLETE
  - Database: patterns/metrics/pattern_automation.db
  - Tables: 3 created
  - Indexes: 6 created

- [x] Phase 2: Integration - ✅ COMPLETE
  - Hook module: automation/integration/orchestrator_hooks.py
  - Import test: PASSED

- [x] Phase 3: Configuration - ✅ COMPLETE
  - Config file: automation/config/detection_config.yaml
  - Validation: PASSED

- [x] Phase 4: Validation - ✅ COMPLETE
  - Test results: 5/5 PASSED
  - Demo result: [SUCCESS / SKIPPED]

## Files Created

[List all files created during activation]

## System Health

- Database operational: YES/NO
- Hooks importable: YES/NO
- Configuration valid: YES/NO
- Tests passing: YES/NO

## Next Steps

[If complete: Ready for actual orchestrator integration]
[If partial: List remaining work]
[If failed: List blockers]
```

---

## COMMAND SUMMARY

Quick reference of all key commands:

```powershell
# Navigate to patterns directory
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns"

# Phase 0: Discovery
Get-ChildItem .. -Recurse -Include "*orchestrator*.py" -Depth 3

# Phase 1: Database
New-Item -ItemType Directory -Path "metrics" -Force
sqlite3 metrics/pattern_automation.db < 004_pattern_automation.sql

# Phase 2: Integration  
python -c "from automation.integration.orchestrator_hooks import get_hooks"

# Phase 3: Configuration
python -c "import yaml; yaml.safe_load(open('automation/config/detection_config.yaml'))"

# Phase 4: Validation
.\automation\tests\test_activation.ps1

# Health check
sqlite3 metrics/pattern_automation.db ".tables"
```

---

## EXECUTION TIME ESTIMATE

- Phase 0: 15 minutes
- Phase 1: 10 minutes
- Phase 2: 15 minutes
- Phase 3: 5 minutes
- Phase 4: 10 minutes
- **Total: 55 minutes**

---

## YOUR MISSION RESTATED

Execute all 5 phases sequentially, creating all specified output files, and validate that the pattern automation system activates successfully. Document all findings in PATTERN_AUTOMATION_PATHS.md and ACTIVATION_COMPLETION_REPORT.md.

**Start with Phase 0 - Repository Discovery.**

Good luck! 🚀
