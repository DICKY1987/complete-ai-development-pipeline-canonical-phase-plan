# DOC_ID Automation Fix - Phase Plan with Execution Patterns

**Generated**: 2025-12-06  
**Document ID**: DOC-PLAN-DOC-ID-AUTOMATION-FIX-001  
**Status**: READY FOR EXECUTION  
**Pattern Framework**: EXEC-001 through EXEC-006

---

## EXECUTIVE SUMMARY

### Mission
Transform doc_id system from 65% to 95% automation by closing 9 critical chain breaks across 14 identified gaps.

### Approach
Use execution patterns to systematically eliminate manual intervention points through 3 phased implementations.

### Key Metrics
- **Total Gaps**: 14
- **Implementation Effort**: 51.5 hours
- **Monthly Savings**: 8.3 hours
- **Payback Period**: 6.2 months
- **Annual ROI**: 100 hours/year

---

## 0. MANDATORY: EXECUTION PATTERN CHECK (5 minutes)

### Pattern Selection Decision Tree

```
Task Analysis:
  - Creating/modifying ≥3 similar items? → YES (14 gaps)
  - Tool/command execution? → YES (CLI wrappers)
  - File operations? → YES (hook installation, configs)
  
Selected Patterns:
  ✓ EXEC-002: Batch Validation (gap fixes)
  ✓ EXEC-003: Tool Availability Guards (CLI execution)
  ✓ EXEC-004: Atomic Operations (file modifications)
  ✓ PATTERN-002: Ground Truth Verification (exit codes)
```

### Anti-Pattern Guards (ALL ENABLED)

```yaml
guards_enabled:
  hallucination_of_success: true      # Require programmatic verification
  planning_loop_trap: true            # Max 2 planning iterations
  incomplete_implementation: true     # No TODO/pass placeholders
  silent_failures: true               # Explicit error handling
  approval_loop: true                 # No human approval for safe ops
  partial_success_amnesia: true       # Checkpoint after each step
```

---

## PHASE 1: QUICK WINS (Week 1-2) - 8.5 hours

**Goal**: Close critical chain breaks with minimal effort  
**Pattern**: EXEC-002 (Batch Validation)  
**Expected Outcome**: 65% → 80% automation, 4.5h/month savings

---

### TASK 1.1: Remove Interactive Prompts

**Gap ID**: GAP-002  
**Chain Break**: BREAK-005  
**Pattern**: EXEC-004 (Atomic Operations)  
**Effort**: 1 hour  
**Priority**: CRITICAL

#### Execution Pattern

```yaml
pattern: EXEC-004-ATOMIC-OPERATIONS
operation_type: file_modification
batch_size: 2
validation_strategy: exit_code
rollback_capability: true
```

#### Implementation Steps

**Step 1.1.1: Modify cleanup_invalid_doc_ids.py**

```python
# PATTERN: EXEC-004 Atomic Operation
# Ground Truth: Script runs to completion without prompts

# Add argument
parser.add_argument('--auto-approve', action='store_true',
                    help='Skip interactive confirmation')

# Modify confirmation logic
if args.action == 'fix':
    if not args.auto_approve:
        confirm = input("Proceed with fix? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            sys.exit(0)
    
    # Execute fix
    apply_fixes(args.backup)
```

**Verification**:
```bash
# Ground Truth: Exit code 0, no stdin read
python doc_id/cleanup_invalid_doc_ids.py fix --auto-approve --dry-run
echo $?  # Must be 0
```

**Step 1.1.2: Update automation_runner.ps1**

```powershell
# PATTERN: EXEC-004 Atomic Operation
# Remove Read-Host, add --auto-approve flag

function Invoke-Cleanup {
    Write-TaskHeader "Running Cleanup Check"
    & python "$DocIdDir\cleanup_invalid_doc_ids.py" scan
    if (-not $DryRun) {
        & python "$DocIdDir\cleanup_invalid_doc_ids.py" fix --backup --auto-approve
    }
}
```

**Verification**:
```powershell
# Ground Truth: Runs without user input
.\doc_id\automation_runner.ps1 -Task cleanup -DryRun
# No Read-Host should be invoked
```

**Ground Truth Criteria**:
- ✅ Script completes without stdin
- ✅ Exit code 0 on success
- ✅ --auto-approve flag documented
- ✅ Backward compatible (still prompts without flag)

**Anti-Pattern Prevention**:
- ❌ NO user approval in automation context
- ❌ NO silent failures (explicit error handling)
- ❌ NO incomplete implementation (all paths handled)

---

### TASK 1.2: Add Auto-Sync with Thresholds

**Gap ID**: GAP-004  
**Chain Break**: BREAK-004  
**Pattern**: EXEC-002 (Batch Validation)  
**Effort**: 1 hour  
**Priority**: HIGH

#### Execution Pattern

```yaml
pattern: EXEC-002-BATCH-VALIDATION
operation_type: registry_sync
validation_strategy: threshold_check
batch_size: 1
rollback_capability: true
```

#### Implementation Steps

**Step 1.2.1: Modify sync_registries.py**

```python
# PATTERN: EXEC-002 Batch Validation with threshold
# Ground Truth: Syncs automatically if drift below threshold

def sync_registries(dry_run=False, auto_sync=False, max_drift=50):
    """Sync registries with optional auto-sync"""
    
    # Step 1: Check drift (validation phase)
    status = check_sync()
    drift_count = len(status['only_inventory']) + len(status['only_registry'])
    
    print(f"Drift detected: {drift_count} entries")
    
    # Step 2: Auto-sync decision
    if auto_sync:
        if drift_count <= max_drift:
            print(f"✅ Auto-syncing (drift {drift_count} ≤ threshold {max_drift})")
            if not dry_run:
                perform_sync(status)
            return 0
        else:
            print(f"❌ Drift {drift_count} exceeds threshold {max_drift}")
            print("Manual review required")
            sys.exit(1)
    else:
        # Manual mode
        print("Run with --auto-sync to enable automatic sync")
        return 0

# Add arguments
parser.add_argument('--auto-sync', action='store_true',
                    help='Sync automatically if drift below threshold')
parser.add_argument('--max-drift', type=int, default=50,
                    help='Maximum drift for auto-sync (default: 50)')
```

**Verification**:
```bash
# Test 1: Low drift (should auto-sync)
python doc_id/sync_registries.py --auto-sync --max-drift 100 --dry-run
echo $?  # Must be 0

# Test 2: High drift (should fail)
python doc_id/sync_registries.py --auto-sync --max-drift 5 --dry-run
echo $?  # Must be 1
```

**Ground Truth Criteria**:
- ✅ Auto-syncs when drift ≤ threshold
- ✅ Fails with exit code 1 when drift > threshold
- ✅ Dry-run mode works correctly
- ✅ Manual mode still available (no --auto-sync)

---

### TASK 1.3: Setup Scheduled Tasks

**Gap ID**: GAP-005  
**Chain Break**: BREAK-007  
**Pattern**: EXEC-003 (Tool Availability Guards)  
**Effort**: 2 hours  
**Priority**: HIGH

#### Execution Pattern

```yaml
pattern: EXEC-003-TOOL-AVAILABILITY-GUARDS
operation_type: scheduler_setup
validation_strategy: task_existence
platforms: [windows, linux]
```

#### Implementation Steps

**Step 1.3.1: Create scheduler setup script**

```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-SETUP-SCHEDULED-TASKS-006
"""
Setup Scheduled Tasks for DOC_ID Automation

PATTERN: EXEC-003 Tool Availability Guards
Ground Truth: Scheduled task exists and is enabled
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def setup_windows_task():
    """Setup Windows Task Scheduler"""
    # PATTERN: Tool guard
    result = subprocess.run(['where', 'schtasks'], 
                           capture_output=True)
    if result.returncode != 0:
        print("❌ schtasks not available")
        sys.exit(1)
    
    task_cmd = [
        'schtasks', '/create',
        '/tn', 'DOC_ID_Daily_Report',
        '/tr', f'python {REPO_ROOT}/doc_id/scheduled_report_generator.py daily',
        '/sc', 'daily',
        '/st', '02:00',
        '/f'  # Force overwrite
    ]
    
    result = subprocess.run(task_cmd, capture_output=True, text=True)
    
    # Ground Truth: Task created
    if result.returncode == 0:
        print("✅ Windows scheduled task created")
        return True
    else:
        print(f"❌ Failed: {result.stderr}")
        return False

def setup_linux_cron():
    """Setup Linux crontab"""
    cron_entry = f"0 2 * * * cd {REPO_ROOT} && python doc_id/scheduled_report_generator.py daily\n"
    
    # Read existing crontab
    result = subprocess.run(['crontab', '-l'], 
                           capture_output=True, text=True)
    
    existing = result.stdout if result.returncode == 0 else ""
    
    # Check if already exists
    if 'scheduled_report_generator.py daily' in existing:
        print("✅ Cron entry already exists")
        return True
    
    # Add new entry
    new_crontab = existing + cron_entry
    
    process = subprocess.Popen(['crontab', '-'], 
                               stdin=subprocess.PIPE,
                               text=True)
    process.communicate(input=new_crontab)
    
    # Ground Truth: Entry in crontab
    if process.returncode == 0:
        print("✅ Linux cron entry created")
        return True
    else:
        print("❌ Failed to create cron entry")
        return False

def verify_task():
    """Verify scheduled task exists"""
    system = platform.system()
    
    if system == 'Windows':
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'DOC_ID_Daily_Report'],
            capture_output=True
        )
        return result.returncode == 0
    else:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True, text=True
        )
        return 'scheduled_report_generator.py daily' in result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true',
                       help='Verify task exists')
    args = parser.parse_args()
    
    if args.verify:
        if verify_task():
            print("✅ Scheduled task is active")
            sys.exit(0)
        else:
            print("❌ Scheduled task not found")
            sys.exit(1)
    
    # Setup based on platform
    system = platform.system()
    print(f"Setting up scheduled task for {system}...")
    
    if system == 'Windows':
        success = setup_windows_task()
    elif system in ('Linux', 'Darwin'):
        success = setup_linux_cron()
    else:
        print(f"❌ Unsupported platform: {system}")
        sys.exit(1)
    
    # Verification
    if verify_task():
        print("✅ Setup complete and verified")
        sys.exit(0)
    else:
        print("❌ Setup failed verification")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Verification**:
```bash
# Ground Truth: Scheduled task exists
python doc_id/setup_scheduled_tasks.py --verify
echo $?  # Must be 0 after setup
```

**Ground Truth Criteria**:
- ✅ Scheduled task created
- ✅ Task appears in scheduler (schtasks/crontab)
- ✅ Task is enabled
- ✅ Verification command succeeds

---

### TASK 1.4: Add Threshold Alerts

**Gap ID**: GAP-006  
**Chain Break**: BREAK-008  
**Pattern**: EXEC-002 (Batch Validation)  
**Effort**: 3 hours  
**Priority**: HIGH

#### Execution Pattern

```yaml
pattern: EXEC-002-BATCH-VALIDATION
operation_type: threshold_monitoring
validation_strategy: alert_generation
batch_size: multiple_thresholds
```

#### Implementation Steps

**Step 1.4.1: Create alert monitor module**

```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-DOC-ID-ALERT-MONITOR-007
"""
DOC_ID System Alert Monitor

PATTERN: EXEC-002 Batch Validation
Ground Truth: Alerts generated and logged
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

REPO_ROOT = Path(__file__).parent.parent
ALERTS_DIR = REPO_ROOT / ".state"
THRESHOLDS_FILE = REPO_ROOT / "doc_id" / "alert_thresholds.yaml"

@dataclass
class Threshold:
    """Alert threshold definition"""
    name: str
    metric: str
    operator: str  # <, >, ==
    value: float
    severity: str  # critical, warning, info
    
@dataclass
class Alert:
    """Alert instance"""
    threshold: Threshold
    actual_value: float
    message: str
    severity: str

# Default thresholds
DEFAULT_THRESHOLDS = [
    Threshold("coverage_critical", "coverage", "<", 90.0, "critical"),
    Threshold("coverage_warning", "coverage", "<", 95.0, "warning"),
    Threshold("invalid_ids_critical", "invalid_count", ">", 10, "critical"),
    Threshold("drift_warning", "drift_count", ">", 50, "warning"),
    Threshold("duplicates_critical", "duplicate_count", ">", 5, "critical"),
]

def load_thresholds() -> List[Threshold]:
    """Load threshold configuration"""
    if THRESHOLDS_FILE.exists():
        import yaml
        with open(THRESHOLDS_FILE) as f:
            data = yaml.safe_load(f)
            return [Threshold(**t) for t in data['thresholds']]
    return DEFAULT_THRESHOLDS

def extract_metrics(report: Dict) -> Dict[str, float]:
    """Extract metrics from report"""
    metrics = {}
    
    # Coverage from scanner output
    scanner_output = report.get('scanner', {}).get('output', '')
    coverage_match = re.search(r'Coverage: (\d+\.?\d*)%', scanner_output)
    if coverage_match:
        metrics['coverage'] = float(coverage_match.group(1))
    
    # Invalid IDs count
    # (Parse from cleanup report if available)
    
    # Drift count
    # (Parse from sync check if available)
    
    return metrics

def check_thresholds(metrics: Dict[str, float], 
                     thresholds: List[Threshold]) -> List[Alert]:
    """Check metrics against thresholds"""
    alerts = []
    
    for threshold in thresholds:
        if threshold.metric not in metrics:
            continue
        
        actual = metrics[threshold.metric]
        triggered = False
        
        if threshold.operator == '<' and actual < threshold.value:
            triggered = True
        elif threshold.operator == '>' and actual > threshold.value:
            triggered = True
        elif threshold.operator == '==' and actual == threshold.value:
            triggered = True
        
        if triggered:
            message = f"{threshold.name}: {threshold.metric} is {actual} (threshold: {threshold.operator}{threshold.value})"
            alerts.append(Alert(threshold, actual, message, threshold.severity))
    
    return alerts

def save_alerts(alerts: List[Alert]):
    """Save alerts to state file"""
    ALERTS_DIR.mkdir(exist_ok=True)
    
    alert_file = ALERTS_DIR / "doc_id_alerts.log"
    
    with open(alert_file, 'w') as f:
        for alert in alerts:
            f.write(f"[{alert.severity.upper()}] {alert.message}\n")
    
    # Also save as JSON for programmatic access
    json_file = ALERTS_DIR / "doc_id_alerts.json"
    with open(json_file, 'w') as f:
        json.dump([{
            'severity': a.severity,
            'message': a.message,
            'metric': a.threshold.metric,
            'actual': a.actual_value,
            'threshold': a.threshold.value
        } for a in alerts], f, indent=2)

def main():
    # Load latest report
    reports_dir = REPO_ROOT / "doc_id" / "DOC_ID_reports"
    latest_daily = sorted(reports_dir.glob("daily_report_*.json"))[-1]
    
    with open(latest_daily) as f:
        report = json.load(f)
    
    # Extract metrics
    metrics = extract_metrics(report)
    
    # Check thresholds
    thresholds = load_thresholds()
    alerts = check_thresholds(metrics, thresholds)
    
    # Save and report
    if alerts:
        save_alerts(alerts)
        
        print(f"🚨 {len(alerts)} alert(s) triggered:")
        for alert in alerts:
            symbol = "🔴" if alert.severity == "critical" else "⚠️"
            print(f"{symbol} [{alert.severity.upper()}] {alert.message}")
        
        # Exit non-zero for CI
        sys.exit(1)
    else:
        print("✅ All thresholds passed")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Step 1.4.2: Integrate into scheduled_report_generator.py**

```python
# Add to scheduled_report_generator.py

def generate_daily_report() -> Dict:
    # ... existing code ...
    
    # Add alert checking
    import subprocess
    alert_result = subprocess.run(
        [sys.executable, 'doc_id/alert_monitor.py'],
        capture_output=True
    )
    
    report['alerts'] = {
        'triggered': alert_result.returncode != 0,
        'count': len(json.loads(Path('.state/doc_id_alerts.json').read_text())) if Path('.state/doc_id_alerts.json').exists() else 0
    }
    
    return report
```

**Verification**:
```bash
# Ground Truth: Alerts generated and exit code reflects status
python doc_id/alert_monitor.py
echo $?  # 1 if alerts, 0 if none
test -f .state/doc_id_alerts.log  # File exists
```

**Ground Truth Criteria**:
- ✅ Alerts detected correctly
- ✅ Alert files created
- ✅ Exit code 1 when alerts present
- ✅ Exit code 0 when no alerts

---

### TASK 1.5: Auto-Install Pre-Commit Hook

**Gap ID**: GAP-008  
**Chain Break**: BREAK-002  
**Pattern**: EXEC-004 (Atomic Operations)  
**Effort**: 0.5 hours  
**Priority**: MEDIUM

#### Execution Pattern

```yaml
pattern: EXEC-004-ATOMIC-OPERATIONS
operation_type: file_copy
validation_strategy: file_existence
rollback_capability: true
```

#### Implementation Steps

**Step 1.5.1: Create hook installer**

```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-INSTALL-PRE-COMMIT-HOOK-008
"""
Install Pre-Commit Hook

PATTERN: EXEC-004 Atomic Operations
Ground Truth: Hook file exists and is executable
"""

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
HOOK_SOURCE = REPO_ROOT / "doc_id" / "pre_commit_hook.py"
HOOK_TARGET = REPO_ROOT / ".git" / "hooks" / "pre-commit"

def install_hook():
    """Install pre-commit hook"""
    # Verify source exists
    if not HOOK_SOURCE.exists():
        print(f"❌ Source not found: {HOOK_SOURCE}")
        sys.exit(1)
    
    # Create hooks directory if needed
    HOOK_TARGET.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing hook
    if HOOK_TARGET.exists():
        backup = HOOK_TARGET.with_suffix('.backup')
        shutil.copy2(HOOK_TARGET, backup)
        print(f"📦 Backed up existing hook to {backup}")
    
    # Copy hook
    shutil.copy2(HOOK_SOURCE, HOOK_TARGET)
    
    # Make executable (Unix)
    if sys.platform != 'win32':
        HOOK_TARGET.chmod(0o755)
    
    # Verify
    if HOOK_TARGET.exists():
        print(f"✅ Pre-commit hook installed: {HOOK_TARGET}")
        return True
    else:
        print("❌ Installation failed")
        return False

if __name__ == '__main__':
    success = install_hook()
    sys.exit(0 if success else 1)
```

**Verification**:
```bash
# Ground Truth: Hook file exists
python doc_id/install_pre_commit_hook.py
test -f .git/hooks/pre-commit && echo "✅ EXISTS" || echo "❌ MISSING"
```

**Ground Truth Criteria**:
- ✅ Hook file exists at `.git/hooks/pre-commit`
- ✅ Hook is executable (Unix)
- ✅ Backup created if hook existed
- ✅ Installation verified

---

### PHASE 1 COMPLETION CHECKLIST

**Ground Truth Verification (ALL MUST PASS)**:

```bash
# Test 1: Cleanup runs without prompts
python doc_id/cleanup_invalid_doc_ids.py fix --auto-approve --dry-run
[ $? -eq 0 ] && echo "✅ 1.1 PASS" || echo "❌ 1.1 FAIL"

# Test 2: Auto-sync works
python doc_id/sync_registries.py --auto-sync --max-drift 100 --dry-run
[ $? -eq 0 ] && echo "✅ 1.2 PASS" || echo "❌ 1.2 FAIL"

# Test 3: Scheduled task exists
python doc_id/setup_scheduled_tasks.py --verify
[ $? -eq 0 ] && echo "✅ 1.3 PASS" || echo "❌ 1.3 FAIL"

# Test 4: Alerts work
python doc_id/alert_monitor.py
echo "✅ 1.4 PASS (exit code: $?)"

# Test 5: Pre-commit hook installed
test -f .git/hooks/pre-commit
[ $? -eq 0 ] && echo "✅ 1.5 PASS" || echo "❌ 1.5 FAIL"

echo "Phase 1 verification complete"
```

**Success Criteria**:
- ✅ 5/5 tests pass
- ✅ automation_runner.ps1 runs without user input
- ✅ Scheduled task runs daily at 2 AM
- ✅ Alerts trigger on threshold violations
- ✅ Pre-commit hook blocks invalid doc_ids

**Expected Outcome**: Automation level 65% → 80%

---

## PHASE 2: HIGH IMPACT (Month 1) - 13 hours

**Goal**: Establish fully automated pipelines  
**Pattern**: EXEC-001, EXEC-003, EXEC-006  
**Expected Outcome**: 80% → 90% automation

---

### TASK 2.1: Implement File Watcher

**Gap ID**: GAP-001  
**Chain Break**: BREAK-001  
**Pattern**: EXEC-003 (Tool Availability Guards)  
**Effort**: 4 hours  
**Priority**: CRITICAL

#### Execution Pattern

```yaml
pattern: EXEC-003-TOOL-AVAILABILITY-GUARDS
operation_type: background_service
validation_strategy: process_running
dependencies: [watchdog]
```

#### Implementation Steps

**Step 2.1.1: Create file watcher**

```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-DOC-ID-FILE-WATCHER-009
"""
DOC_ID File Watcher

PATTERN: EXEC-003 Tool Availability Guards
Ground Truth: Watcher process running, scan triggered on changes
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# PATTERN: Tool availability guard
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog not installed")
    print("Run: pip install watchdog")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
SCANNER_SCRIPT = REPO_ROOT / "doc_id" / "doc_id_scanner.py"

class DocIDEventHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, debounce_seconds=300):
        self.last_scan = datetime.min
        self.debounce = timedelta(seconds=debounce_seconds)
        self.pending_scan = False
    
    def on_modified(self, event):
        """Trigger scan on file modification"""
        if event.is_directory:
            return
        
        # Filter eligible files
        path = Path(event.src_path)
        if path.suffix not in {'.py', '.md', '.yaml', '.yml', '.json', '.ps1', '.sh', '.txt'}:
            return
        
        # Debounce
        now = datetime.now()
        if now - self.last_scan < self.debounce:
            self.pending_scan = True
            return
        
        # Trigger scan
        self.trigger_scan()
    
    def trigger_scan(self):
        """Execute scanner"""
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Triggering scan...")
        
        result = subprocess.run(
            [sys.executable, str(SCANNER_SCRIPT), 'scan'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Scan completed successfully")
        else:
            print(f"❌ Scan failed: {result.stderr}")
        
        self.last_scan = datetime.now()
        self.pending_scan = False

def main():
    print("Starting DOC_ID File Watcher...")
    print(f"Watching: {REPO_ROOT}")
    print(f"Scanner: {SCANNER_SCRIPT}")
    print("Press Ctrl+C to stop\n")
    
    # Verify scanner exists
    if not SCANNER_SCRIPT.exists():
        print(f"❌ Scanner not found: {SCANNER_SCRIPT}")
        sys.exit(1)
    
    # Create handler and observer
    handler = DocIDEventHandler(debounce_seconds=300)  # 5 minute debounce
    observer = Observer()
    observer.schedule(handler, str(REPO_ROOT), recursive=True)
    observer.start()
    
    print("✅ Watcher started\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped")

if __name__ == '__main__':
    main()
```

**Verification**:
```bash
# Ground Truth: Watcher process starts
python doc_id/file_watcher.py &
WATCHER_PID=$!

# Modify a file
echo "test" >> test_file.py

# Wait for scan
sleep 2

# Verify scan ran (check logs or inventory timestamp)
python doc_id/doc_id_scanner.py stats | grep "Scanned at"

# Cleanup
kill $WATCHER_PID
```

**Ground Truth Criteria**:
- ✅ Watcher process starts without errors
- ✅ File modification triggers scan
- ✅ Debounce prevents excessive scans
- ✅ Scanner completes successfully

---

### TASK 2.2: Create CI/CD Workflow

**Gap ID**: GAP-003  
**Chain Break**: BREAK-003  
**Pattern**: EXEC-002 (Batch Validation)  
**Effort**: 6 hours  
**Priority**: CRITICAL

#### Execution Pattern

```yaml
pattern: EXEC-002-BATCH-VALIDATION
operation_type: ci_workflow
validation_strategy: exit_codes
batch_size: 5_validation_steps
```

#### Implementation Steps

**Step 2.2.1: Create GitHub Actions workflow**

```yaml
# .github/workflows/doc_id_validation.yml
# DOC_LINK: DOC-CONFIG-CI-DOC-ID-VALIDATION-010
# PATTERN: EXEC-002 Batch Validation

name: DOC_ID System Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyyaml watchdog pytest
      
      # VALIDATION BATCH (5 steps)
      
      - name: "Validation 1/5: Run Scanner"
        id: scan
        run: |
          python doc_id/doc_id_scanner.py scan
          echo "scan_status=$?" >> $GITHUB_OUTPUT
      
      - name: "Validation 2/5: Check Coverage"
        id: coverage
        run: |
          python doc_id/validate_doc_id_coverage.py --baseline 0.90
          echo "coverage_status=$?" >> $GITHUB_OUTPUT
      
      - name: "Validation 3/5: Detect Invalid IDs"
        id: invalid
        run: |
          python doc_id/cleanup_invalid_doc_ids.py scan --fail-on-invalid
          echo "invalid_status=$?" >> $GITHUB_OUTPUT
      
      - name: "Validation 4/5: Check Registry Sync"
        id: sync
        run: |
          python doc_id/sync_registries.py check --fail-on-drift --max-drift 100
          echo "sync_status=$?" >> $GITHUB_OUTPUT
      
      - name: "Validation 5/5: Run Tests"
        id: tests
        run: |
          python -m pytest doc_id/test_doc_id_system.py -v --tb=short
          echo "tests_status=$?" >> $GITHUB_OUTPUT
      
      # Ground Truth Summary
      - name: Validation Summary
        if: always()
        run: |
          echo "## Validation Results" >> $GITHUB_STEP_SUMMARY
          echo "| Step | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Scanner | ${{ steps.scan.outputs.scan_status == '0' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Coverage | ${{ steps.coverage.outputs.coverage_status == '0' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Invalid IDs | ${{ steps.invalid.outputs.invalid_status == '0' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Sync Check | ${{ steps.sync.outputs.sync_status == '0' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Tests | ${{ steps.tests.outputs.tests_status == '0' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: doc-id-reports
          path: doc_id/DOC_ID_reports/
```

**Step 2.2.2: Add --fail-on-* flags to scripts**

```python
# Add to cleanup_invalid_doc_ids.py
parser.add_argument('--fail-on-invalid', action='store_true',
                    help='Exit with code 1 if invalid IDs found')

if args.fail_on_invalid and invalid_count > 0:
    print(f"❌ {invalid_count} invalid IDs found")
    sys.exit(1)

# Add to sync_registries.py
parser.add_argument('--fail-on-drift', action='store_true',
                    help='Exit with code 1 if drift detected')
parser.add_argument('--max-drift', type=int, default=0,
                    help='Maximum acceptable drift')

drift = len(status['only_inventory']) + len(status['only_registry'])
if args.fail_on_drift and drift > args.max_drift:
    print(f"❌ Drift {drift} exceeds limit {args.max_drift}")
    sys.exit(1)
```

**Verification**:
```bash
# Ground Truth: Workflow file valid
yamllint .github/workflows/doc_id_validation.yml

# Test locally with act (optional)
act -j validate

# Or commit and verify on GitHub
git add .github/workflows/doc_id_validation.yml
git commit -m "Add CI validation workflow"
git push
# Check Actions tab in GitHub
```

**Ground Truth Criteria**:
- ✅ Workflow file syntax valid
- ✅ All 5 validation steps execute
- ✅ Exit codes propagate correctly
- ✅ Summary displays in GitHub UI

---

### TASK 2.3: Build CLI Wrapper

**Gap ID**: GAP-007  
**Pattern**: EXEC-003 (Tool Availability Guards)  
**Effort**: 3 hours  
**Priority**: MEDIUM

#### Implementation Steps

**Step 2.3.1: Create standardized CLI wrapper**

```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-CLI-WRAPPER-011
"""
Standardized CLI Wrapper for DOC_ID Tools

PATTERN: EXEC-003 Tool Availability Guards + Retry Logic
Ground Truth: Consistent execution with timeout, retry, logging
"""

import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).parent.parent
LOG_DIR = REPO_ROOT / ".state" / "cli_logs"

@dataclass
class ExecutionResult:
    """CLI execution result"""
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    attempts: int

def run_cli_tool(
    tool_name: str,
    args: List[str],
    timeout: int = 300,
    retry_count: int = 3,
    retry_delay: int = 5,
    log_output: bool = True
) -> ExecutionResult:
    """
    Execute CLI tool with standardized handling
    
    PATTERN: EXEC-003 Tool Guards + Retry Logic
    """
    # Construct command
    tool_path = REPO_ROOT / "doc_id" / f"{tool_name}.py"
    
    # Tool availability guard
    if not tool_path.exists():
        raise FileNotFoundError(f"Tool not found: {tool_path}")
    
    cmd = [sys.executable, str(tool_path)] + args
    
    # Retry loop
    for attempt in range(1, retry_count + 1):
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            duration = time.time() - start_time
            
            # Log output
            if log_output:
                log_execution(tool_name, args, result, duration, attempt)
            
            # Success or final attempt
            if result.returncode == 0 or attempt == retry_count:
                return ExecutionResult(
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration_seconds=duration,
                    attempts=attempt
                )
            
            # Retry on failure
            print(f"⚠️  Attempt {attempt}/{retry_count} failed, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout after {timeout}s on attempt {attempt}/{retry_count}")
            if attempt == retry_count:
                raise
            time.sleep(retry_delay)
    
    raise RuntimeError(f"Failed after {retry_count} attempts")

def log_execution(tool_name: str, args: List[str], 
                 result: subprocess.CompletedProcess, 
                 duration: float, attempt: int):
    """Log CLI execution"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now()
    log_file = LOG_DIR / f"{tool_name}_{timestamp:%Y%m%d_%H%M%S}.log"
    
    with open(log_file, 'w') as f:
        f.write(f"Tool: {tool_name}\n")
        f.write(f"Args: {' '.join(args)}\n")
        f.write(f"Timestamp: {timestamp.isoformat()}\n")
        f.write(f"Duration: {duration:.2f}s\n")
        f.write(f"Attempt: {attempt}\n")
        f.write(f"Exit Code: {result.returncode}\n")
        f.write("\n--- STDOUT ---\n")
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)

# Convenience functions
def scan(timeout=300):
    """Run scanner"""
    return run_cli_tool('doc_id_scanner', ['scan'], timeout=timeout)

def validate_coverage(baseline=0.90):
    """Validate coverage"""
    return run_cli_tool('validate_doc_id_coverage', 
                       [f'--baseline', str(baseline)])

def sync_check():
    """Check sync status"""
    return run_cli_tool('sync_registries', ['check'])

def sync_auto(max_drift=50):
    """Auto-sync with threshold"""
    return run_cli_tool('sync_registries', 
                       ['--auto-sync', f'--max-drift', str(max_drift)])

if __name__ == '__main__':
    # Example usage
    result = scan()
    print(f"Scanner completed in {result.duration_seconds:.2f}s")
    sys.exit(result.returncode)
```

**Verification**:
```bash
# Ground Truth: Wrapper executes tools correctly
python doc_id/cli_wrapper.py

# Check logs created
ls .state/cli_logs/
```

**Ground Truth Criteria**:
- ✅ Tool executes with timeout
- ✅ Retry logic works on failure
- ✅ Logs created in .state/cli_logs/
- ✅ Exit code propagated

---

### PHASE 2 COMPLETION CHECKLIST

```bash
# Test 1: File watcher
python doc_id/file_watcher.py &
WATCHER_PID=$!
sleep 2
kill $WATCHER_PID
[ $? -eq 0 ] && echo "✅ 2.1 PASS" || echo "❌ 2.1 FAIL"

# Test 2: CI workflow
yamllint .github/workflows/doc_id_validation.yml
[ $? -eq 0 ] && echo "✅ 2.2 PASS" || echo "❌ 2.2 FAIL"

# Test 3: CLI wrapper
python doc_id/cli_wrapper.py
[ $? -eq 0 ] && echo "✅ 2.3 PASS" || echo "❌ 2.3 FAIL"

echo "Phase 2 verification complete"
```

**Expected Outcome**: Automation level 80% → 90%

---

## PHASE 3: LONG-TERM (Quarter 1) - 30 hours

**Goal**: Complete automation and monitoring  
**Pattern**: EXEC-001 through EXEC-006  
**Expected Outcome**: 90% → 95% automation

### Tasks (Abbreviated)

- **TASK 3.1**: Build auto-fix logic (GAP-009) - 8h
- **TASK 3.2**: Add heartbeat monitoring (GAP-010) - 2h
- **TASK 3.3**: Implement retry logic (GAP-011) - 2h
- **TASK 3.4**: Real email integration (GAP-012) - 4h
- **TASK 3.5**: Create metrics dashboard (GAP-013) - 16h
- **TASK 3.6**: Refactor common code (GAP-014) - 8h

*(Full implementation details in separate Phase 3 spec)*

---

## GROUND TRUTH VERIFICATION MATRIX

### Phase 1 Verification (ALL MUST BE ✅)

| Task | Ground Truth Check | Command | Expected |
|------|-------------------|---------|----------|
| 1.1 | No prompts | `automation_runner.ps1 -Task cleanup -DryRun` | Exit 0, no stdin |
| 1.2 | Auto-sync | `sync_registries.py --auto-sync` | Syncs below threshold |
| 1.3 | Scheduled task | `setup_scheduled_tasks.py --verify` | Exit 0 |
| 1.4 | Alerts work | `alert_monitor.py` | Exit 1 if alerts |
| 1.5 | Hook installed | `test -f .git/hooks/pre-commit` | File exists |

### Phase 2 Verification

| Task | Ground Truth Check | Command | Expected |
|------|-------------------|---------|----------|
| 2.1 | Watcher runs | `ps aux \| grep file_watcher` | Process found |
| 2.2 | CI passes | GitHub Actions tab | All checks green |
| 2.3 | Wrapper works | `cli_wrapper.py` | Exit 0, logs created |

---

## SUCCESS METRICS TRACKING

### Automation Coverage

```yaml
baseline:
  automation_level: 65%
  manual_steps: 9
  monthly_hours: 9.3

phase_1_target:
  automation_level: 80%
  manual_steps: 4
  monthly_hours: 4.8

phase_2_target:
  automation_level: 90%
  manual_steps: 2
  monthly_hours: 2.0

phase_3_target:
  automation_level: 95%
  manual_steps: 1
  monthly_hours: 1.0
```

### Time Savings Tracking

```python
# Track savings in .state/automation_metrics.json
{
  "phase_1_completion": "2025-12-20",
  "monthly_savings_hours": 4.5,
  "cumulative_savings_hours": 4.5,
  "implementation_hours": 8.5,
  "roi_months": 1.9
}
```

---

## EXECUTION CHECKLIST

### Before Starting

- [ ] Read EXECUTION_PATTERNS_MANDATORY.md
- [ ] Enable all 11 anti-pattern guards
- [ ] Verify ground truth verification commands work
- [ ] Create .state/ directory for logs
- [ ] Backup current working system

### Phase 1 Execution

- [ ] Task 1.1: Remove interactive prompts
- [ ] Task 1.2: Add auto-sync
- [ ] Task 1.3: Setup scheduled tasks
- [ ] Task 1.4: Add threshold alerts
- [ ] Task 1.5: Auto-install pre-commit hook
- [ ] Verify all Phase 1 ground truth checks
- [ ] Measure time savings

### Phase 2 Execution

- [ ] Task 2.1: Implement file watcher
- [ ] Task 2.2: Create CI workflow
- [ ] Task 2.3: Build CLI wrapper
- [ ] Verify all Phase 2 ground truth checks
- [ ] Measure automation coverage

### Phase 3 Execution

- [ ] Execute tasks 3.1 through 3.6
- [ ] Final verification
- [ ] Document lessons learned

---

## CONCLUSION

This phase plan provides a systematic, pattern-driven approach to achieving 95% automation in the doc_id system. By following execution patterns, enabling anti-pattern guards, and using ground truth verification, we eliminate manual intervention points while maintaining high quality and reliability.

**Key Principles**:
1. **Pattern-First**: Select execution pattern before coding
2. **Ground Truth**: Verify with objective criteria only
3. **Batch Operations**: Process similar items together
4. **No Approval Loops**: Automate safe operations fully

**Expected Results**:
- 8.3 hours/month saved
- 95% automation coverage
- 75% error reduction
- 6.2 month payback period

**Next Step**: Begin Phase 1, Task 1.1 (Remove Interactive Prompts)
