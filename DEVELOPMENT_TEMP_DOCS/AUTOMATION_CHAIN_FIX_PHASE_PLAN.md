# Automation Chain Fix - Complete Phase Plan
**DOC_ID**: DOC-TEMP-AUTOMATION-CHAIN-FIX-PHASE-PLAN-001  
**Created**: 2025-12-06  
**Status**: READY_TO_EXECUTE  
**Parent**: DOC-TEMP-AUTOMATION-CHAIN-GAP-ANALYSIS-001

---

## Executive Summary

**Objective**: Transform automation coverage from 35% → 90% by fixing 17 identified chain breaks  
**Duration**: 8 weeks (2 months)  
**Team**: 2 engineers  
**Total Effort**: 91 hours  
**Expected ROI**: 18:1 (140 hrs/month saved ÷ 91 hrs implementation)  
**Phases**: 3 phases (Critical → Quick Wins → Advanced)

### Success Metrics
- **Pattern Execution**: 95% automated (from 0%)
- **Health Monitoring**: Real-time alerting (from weekly manual)
- **Error Auto-Fix**: 70% success rate (from 10%)
- **Manual Interventions**: &lt;5/day (from 35-50/day)
- **MTTR**: &lt;2 minutes (from 30-60 minutes)

---

## Phase Plan Overview

```
Phase 1 (Week 1-2): CRITICAL CHAIN BREAKS
├── Goal: Close 5 highest-impact gaps
├── Effort: 34 hours
├── Savings: 90 hours/month
└── ROI: 26:1

Phase 2 (Week 3): QUICK WINS
├── Goal: Implement 4 high-ROI, low-effort fixes
├── Effort: 9 hours
├── Savings: 16 hours/month
└── ROI: 21:1

Phase 3 (Week 4-8): ADVANCED AUTOMATION
├── Goal: Complete automation chain
├── Effort: 48 hours
├── Savings: 34 hours/month + 3x speedup
└── ROI: 8:1 + performance gains
```

---

## Phase 1: Critical Chain Breaks (Week 1-2)

**Goal**: Fix the 5 most impactful automation gaps  
**Duration**: 2 weeks  
**Effort**: 34 hours  
**Monthly Savings**: 90 hours

### Workstreams

---

### WS-AUTO-001: Pattern Execution Wrapper

**Execution Pattern**: EXEC-001 (Atomic Operations)  
**Priority**: CRITICAL  
**Effort**: 8 hours  
**Savings**: 37.5 hours/month  
**Fixes**: BREAK-001 (Pattern Approval → Executor Invocation)

#### Tasks

**Task 1.1: Create Universal Pattern CLI** (3 hours)
```yaml
operation_kind: create_python_module
inputs:
  - path: patterns/cli/pattern_orchestrate.py
  - template: python_click_cli
  - dependencies:
      - click
      - patterns.automation.integration
      - core.engine.orchestrator
outputs:
  - CLI with commands: execute, list, info, validate
  - Event-driven executor launcher
  - Orchestrator integration hooks
validation:
  - pytest patterns/cli/test_pattern_orchestrate.py
  - Manual test: pattern execute --pattern-id PAT-ATOMIC-CREATE-001
success_criteria:
  - CLI accepts pattern-id and instance path
  - Creates orchestrator run_id
  - Invokes PowerShell executor via adapter
  - Logs telemetry to pattern_automation.db
```

**Implementation**:
```python
# patterns/cli/pattern_orchestrate.py
import click
import subprocess
from pathlib import Path
from patterns.automation.integration import PatternAutomationHooks
from core.engine.orchestrator import Orchestrator
from patterns.registry import PATTERN_INDEX

@click.group()
def cli():
    """Pattern execution CLI with full orchestration."""
    pass

@cli.command()
@click.option('--pattern-id', required=True, help='Pattern ID (e.g., PAT-ATOMIC-CREATE-001)')
@click.option('--instance', type=click.Path(exists=True), help='Instance JSON/YAML')
@click.option('--timeout', default=300, help='Timeout in seconds')
def execute(pattern_id, instance, timeout):
    """Execute pattern via orchestrator."""
    hooks = PatternAutomationHooks(enabled=True)
    orch = Orchestrator()
    
    # Load pattern spec
    pattern = load_pattern_from_registry(pattern_id)
    if not pattern:
        click.echo(f"Error: Pattern {pattern_id} not found in registry", err=True)
        return 1
    
    # Create orchestrator run
    run_id = orch.create_run(
        project_id="patterns",
        phase_id="execution",
        metadata={"pattern_id": pattern_id, "instance": instance}
    )
    
    # Hook: Task start
    task_spec = {
        "pattern_id": pattern_id,
        "executor": pattern['executor'],
        "inputs": {"instance": instance}
    }
    ctx = hooks.on_task_start(task_spec)
    
    # Execute PowerShell executor
    executor_path = Path("patterns/executors") / pattern['executor']
    cmd = ["powershell", "-File", str(executor_path), "-InputFile", instance]
    
    try:
        result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        success = result.returncode == 0
        
        # Hook: Task complete
        hooks.on_task_complete(
            task_spec,
            {"success": success, "exit_code": result.returncode, "output": result.stdout},
            ctx
        )
        
        # Update orchestrator state
        orch.update_run_state(run_id, "completed" if success else "failed")
        
        click.echo(f"Run {run_id}: {'SUCCESS' if success else 'FAILED'}")
        if result.stdout:
            click.echo(result.stdout)
        return result.returncode
        
    except subprocess.TimeoutExpired:
        hooks.on_task_complete(task_spec, {"success": False, "error": "timeout"}, ctx)
        orch.update_run_state(run_id, "failed")
        click.echo(f"Error: Execution timeout after {timeout}s", err=True)
        return 1

@cli.command()
def list():
    """List all available patterns."""
    patterns = load_pattern_registry()
    for p in patterns:
        click.echo(f"{p['id']}: {p['name']} ({p['executor']})")

@cli.command()
@click.argument('pattern_id')
def info(pattern_id):
    """Show pattern details."""
    pattern = load_pattern_from_registry(pattern_id)
    if pattern:
        click.echo(yaml.dump(pattern, default_flow_style=False))
    else:
        click.echo(f"Pattern {pattern_id} not found", err=True)

if __name__ == '__main__':
    cli()
```

**Task 1.2: Auto-Discovery Layer** (2 hours)
```yaml
operation_kind: create_python_module
inputs:
  - path: patterns/automation/discovery/pattern_scanner.py
outputs:
  - Automatic pattern spec → executor mapping
  - Registry auto-update on new patterns
validation:
  - New pattern detected within 5 seconds
  - Registry updated automatically
```

**Task 1.3: Event-Driven Launcher** (2 hours)
```yaml
operation_kind: modify_python_module
inputs:
  - path: patterns/automation/lifecycle/auto_approval.py
changes:
  - Add event emission after approval
  - Emit 'pattern_approved' to event bus
outputs:
  - Event listener auto-invokes pattern_orchestrate.py
validation:
  - Pattern approved → executed within 10 seconds
  - No manual intervention
```

**Task 1.4: Integration Testing** (1 hour)
```yaml
operation_kind: create_test_suite
inputs:
  - path: patterns/cli/test_pattern_orchestrate.py
test_cases:
  - test_execute_pattern_success
  - test_execute_pattern_timeout
  - test_telemetry_logged
  - test_orchestrator_state_updated
  - test_event_driven_launch
validation:
  - pytest coverage ≥90%
  - E2E test: detection → approval → execution
```

**Validation Criteria**:
- [ ] CLI command `pattern execute --pattern-id PAT-ATOMIC-CREATE-001 --instance test.yaml` succeeds
- [ ] Telemetry logged to `patterns/metrics/pattern_automation.db`
- [ ] Orchestrator run state updated
- [ ] Event-driven launch works: auto-approval → auto-execution
- [ ] 95% of patterns execute without manual intervention

---

### WS-AUTO-002: Universal Orchestrator Wrapper

**Execution Pattern**: EXEC-002 (Batch Validation)  
**Priority**: CRITICAL  
**Effort**: 6 hours  
**Savings**: 15 hours/month  
**Fixes**: BREAK-007 (Orchestrator Invocation → Standardization)

#### Tasks

**Task 2.1: Create PowerShell Wrapper** (3 hours)
```powershell
# scripts/run-with-orchestrator.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,
    
    [Parameter(Mandatory=$true)]
    [string]$Phase,
    
    [hashtable]$Params = @{},
    
    [int]$Timeout = 300,
    
    [switch]$NoTelemetry
)

$ErrorActionPreference = "Stop"

# Initialize orchestrator
Write-Host "[orchestrator] Creating run for $ScriptPath in phase $Phase"
$runId = & python -c @"
from core.engine.orchestrator import Orchestrator
orch = Orchestrator()
run_id = orch.create_run('scripts', '$Phase', metadata={'script': '$ScriptPath'})
print(run_id)
"@

if (-not $runId) {
    Write-Error "Failed to create orchestrator run"
    exit 1
}

# Start task telemetry
if (-not $NoTelemetry) {
    & python -c @"
from patterns.automation.integration import get_hooks
hooks = get_hooks()
hooks.on_task_start({'script': '$ScriptPath', 'phase': '$Phase', 'params': $(ConvertTo-Json $Params)})
"@
}

# Execute with timeout
Write-Host "[orchestrator] Executing $ScriptPath with timeout ${Timeout}s"
$job = Start-Job -ScriptBlock {
    param($path, $args)
    & $path @args
} -ArgumentList $ScriptPath, $Params

$completed = Wait-Job -Job $job -Timeout $Timeout
$output = Receive-Job -Job $job
$exitCode = if ($completed.State -eq 'Completed') { 0 } else { 1 }

# Complete task telemetry
if (-not $NoTelemetry) {
    & python -c @"
from patterns.automation.integration import get_hooks
hooks = get_hooks()
hooks.on_task_complete(
    {'script': '$ScriptPath', 'phase': '$Phase'},
    {'success': $($exitCode -eq 0), 'exit_code': $exitCode, 'output': '''$output'''},
    {}
)
"@
}

# Update orchestrator state
$state = if ($exitCode -eq 0) { "completed" } else { "failed" }
& python -c @"
from core.engine.orchestrator import Orchestrator
orch = Orchestrator()
orch.update_run_state('$runId', '$state')
"@

Write-Host "[orchestrator] Run $runId: $state"
Write-Host $output

exit $exitCode
```

**Task 2.2: Migrate Top 10 Scripts** (2 hours)
```yaml
operation_kind: batch_modify_scripts
scripts:
  - scripts/execute_next_workstreams.py
  - scripts/run_workstream.py
  - scripts/run_ws_wrapper.py
  - scripts/sync_workstreams_to_github.py
  - scripts/validate_workstreams.py
  - scripts/spec_to_workstream.py
  - scripts/generate_readmes.py
  - scripts/run_error_engine.py
  - scripts/index_codebase.py
  - scripts/init_db.py
changes:
  - Add wrapper invocation examples to docstrings
  - Create migration guide
outputs:
  - Updated scripts with wrapper examples
  - Migration guide document
```

**Task 2.3: Documentation** (1 hour)
```markdown
# Orchestrator Wrapper Usage Guide

## Quick Start

### Old (Ad-hoc):
```powershell
python scripts/execute_next_workstreams.py --phase phase2
```

### New (Orchestrated):
```powershell
.\scripts\run-with-orchestrator.ps1 `
    -ScriptPath "scripts\execute_next_workstreams.py" `
    -Phase "phase2" `
    -Params @{phase="phase2"}
```

## Benefits
- ✅ Automatic telemetry logging
- ✅ Timeout enforcement (default 300s)
- ✅ Orchestrator state tracking
- ✅ Event bus integration
- ✅ Error recovery hooks

## Options
- `-Timeout`: Override default 300s timeout
- `-NoTelemetry`: Disable telemetry (debugging only)
```

**Validation Criteria**:
- [ ] Top 10 scripts successfully run via wrapper
- [ ] Telemetry logged for all wrapped executions
- [ ] Timeout enforcement works (test with sleep script)
- [ ] State updates visible in orchestrator DB
- [ ] Documentation published

---

### WS-AUTO-003: Real-Time Health Monitoring

**Execution Pattern**: EXEC-003 (Tool Availability Guards)  
**Priority**: CRITICAL  
**Effort**: 4 hours  
**Savings**: 8.7 hours/month  
**Fixes**: BREAK-002 (Health Checks → Monitoring Dashboard)

#### Tasks

**Task 3.1: Health Monitor Daemon** (2 hours)
```python
# patterns/automation/monitoring/health_monitor_daemon.py
import time
import sys
from pathlib import Path
from datetime import datetime
from core.events.event_bus import EventBus, EventSeverity
from core.events.alerting.alert_manager import AlertManager

def run_health_check():
    """Execute health check script and parse results."""
    import subprocess
    result = subprocess.run(
        ["powershell", "-File", "patterns/automation/monitoring/health_check.ps1", "-Json"],
        capture_output=True,
        text=True
    )
    import json
    return json.loads(result.stdout)

def main():
    print(f"[{datetime.now()}] Health monitor daemon starting...")
    
    event_bus = EventBus()
    alerts = AlertManager()
    
    # Load alert config
    alert_config = {
        "critical_threshold": 2,  # Fail if ≥2 critical checks fail
        "warning_threshold": 3,   # Warn if ≥3 checks fail
        "check_interval": 300     # Check every 5 minutes
    }
    
    failure_count = 0
    
    while True:
        try:
            health = run_health_check()
            
            failed_checks = [c for c in health.get('checks', []) if c['status'] != 'PASS']
            critical_failed = [c for c in failed_checks if c.get('severity') == 'CRITICAL']
            
            if len(critical_failed) >= alert_config['critical_threshold']:
                # CRITICAL alert
                event_bus.emit("health.critical", {
                    "checks_failed": [c['name'] for c in critical_failed],
                    "timestamp": datetime.now().isoformat(),
                    "metrics": health.get('metrics', {})
                }, severity=EventSeverity.CRITICAL)
                
                alerts.send_alert(
                    severity="CRITICAL",
                    title="Pattern Automation Health CRITICAL",
                    message=f"Critical checks failed: {', '.join([c['name'] for c in critical_failed])}"
                )
                
                failure_count += 1
                
            elif len(failed_checks) >= alert_config['warning_threshold']:
                # WARNING alert
                event_bus.emit("health.warning", {
                    "checks_failed": [c['name'] for c in failed_checks],
                    "timestamp": datetime.now().isoformat()
                }, severity=EventSeverity.WARNING)
                
                failure_count += 1
            else:
                # HEALTHY
                if failure_count > 0:
                    event_bus.emit("health.recovered", {
                        "timestamp": datetime.now().isoformat(),
                        "previous_failures": failure_count
                    }, severity=EventSeverity.INFO)
                failure_count = 0
            
            print(f"[{datetime.now()}] Health check: {health.get('status', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"[{datetime.now()}] ERROR in health check: {e}", file=sys.stderr)
            event_bus.emit("health.daemon_error", {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, severity=EventSeverity.ERROR)
        
        # Sleep until next check
        time.sleep(alert_config['check_interval'])

if __name__ == '__main__':
    main()
```

**Task 3.2: Windows Task Scheduler Setup** (1 hour)
```powershell
# patterns/automation/monitoring/setup_scheduled_health_monitor.ps1
param(
    [switch]$Uninstall
)

$taskName = "PatternHealthMonitor"
$scriptPath = Join-Path $PSScriptRoot "health_monitor_daemon.py"

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Health monitor task removed"
    exit 0
}

# Create scheduled task
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "python" -Argument "`"$scriptPath`""
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 3

Register-ScheduledTask `
    -TaskName $taskName `
    -Trigger $trigger `
    -Action $action `
    -Principal $principal `
    -Settings $settings `
    -Description "Pattern automation health monitoring daemon"

Write-Host "Health monitor scheduled task created: $taskName"
Write-Host "The task will start automatically at system startup"
Write-Host "To start manually: Start-ScheduledTask -TaskName '$taskName'"
```

**Task 3.3: Alert Routing Configuration** (1 hour)
```yaml
operation_kind: create_config
inputs:
  - path: patterns/automation/config/alert_config.yaml
content: |
  alert_channels:
    email:
      enabled: false
      smtp_host: smtp.gmail.com
      smtp_port: 587
      from_address: alerts@example.com
      to_addresses:
        - admin@example.com
      
    slack:
      enabled: false
      webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
      channel: "#pattern-alerts"
      
    event_bus:
      enabled: true
      log_all_severities: true
  
  alert_rules:
    critical:
      min_failures: 2
      escalation_delay_minutes: 5
      retry_count: 3
      
    warning:
      min_failures: 3
      escalation_delay_minutes: 15
      
    info:
      log_only: true
```

**Validation Criteria**:
- [ ] Daemon runs continuously without crashes
- [ ] Health checks execute every 5 minutes
- [ ] CRITICAL alerts trigger within 1 minute of failure
- [ ] Event bus receives health events
- [ ] Scheduled task auto-starts on system reboot

---

### WS-AUTO-004: Auto-Retry Mechanical Fixes

**Execution Pattern**: EXEC-006 (Auto-Fix Linting)  
**Priority**: HIGH  
**Effort**: 12 hours  
**Savings**: 18.75 hours/month  
**Fixes**: BREAK-004 (Error Detection → Auto-Recovery)

#### Tasks

**Task 4.1: Retry Coordinator** (4 hours)
```python
# phase6_error_recovery/modules/error_engine/src/engine/retry_coordinator.py
from dataclasses import dataclass
from typing import Optional, Callable
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    backoff_base: float = 2.0
    mechanical_only: bool = True
    timeout_per_attempt: int = 60
    
@dataclass
class RetryResult:
    """Result of retry attempts."""
    success: bool
    attempts_made: int
    final_fix_method: str
    error_message: Optional[str] = None
    fix_applied: Optional[str] = None

class RetryCoordinator:
    """Coordinates retry attempts for error fixes with exponential backoff."""
    
    def __init__(self, error_engine, policy: Optional[RetryPolicy] = None):
        self.engine = error_engine
        self.policy = policy or RetryPolicy()
        
    def execute_with_retry(self, error_context) -> RetryResult:
        """
        Execute error fix with retry logic.
        
        Flow:
        1. Attempt mechanical fix
        2. If failed, retry with backoff (up to max_attempts)
        3. If all retries fail, escalate to AI agent
        4. Return result with telemetry
        """
        logger.info(f"Starting retry sequence for error: {error_context.error_type}")
        
        for attempt in range(1, self.policy.max_attempts + 1):
            logger.info(f"Retry attempt {attempt}/{self.policy.max_attempts}")
            
            try:
                # Attempt fix
                fix_result = self.engine.detect_and_fix(
                    error_context,
                    timeout=self.policy.timeout_per_attempt
                )
                
                # Check result
                if fix_result.success:
                    logger.info(f"Fix succeeded on attempt {attempt}")
                    return RetryResult(
                        success=True,
                        attempts_made=attempt,
                        final_fix_method=fix_result.method,
                        fix_applied=fix_result.fix_description
                    )
                
                # If mechanical fix failed, retry with backoff
                if fix_result.method == "mechanical":
                    if attempt < self.policy.max_attempts:
                        sleep_time = self.policy.backoff_base ** (attempt - 1)
                        logger.info(f"Mechanical fix failed, retrying in {sleep_time}s")
                        time.sleep(sleep_time)
                        continue
                    else:
                        logger.warning("All mechanical retry attempts exhausted")
                        # Escalate after final attempt
                        break
                
                # If AI agent method, don't retry (escalation already happened)
                elif fix_result.method == "ai_agent":
                    logger.info("AI agent invoked, no retry needed")
                    return RetryResult(
                        success=fix_result.success,
                        attempts_made=attempt,
                        final_fix_method="ai_agent",
                        error_message=fix_result.error if not fix_result.success else None
                    )
                
            except Exception as e:
                logger.error(f"Exception during retry attempt {attempt}: {e}")
                if attempt == self.policy.max_attempts:
                    break
                time.sleep(self.policy.backoff_base ** (attempt - 1))
        
        # All retries failed, escalate to AI
        logger.warning("Escalating to AI agent after failed retries")
        escalation_result = self.engine.escalate_to_ai_agent(error_context)
        
        return RetryResult(
            success=escalation_result.success if escalation_result else False,
            attempts_made=self.policy.max_attempts,
            final_fix_method="ai_agent_escalation",
            error_message="All mechanical retries failed"
        )
```

**Task 4.2: Orchestrator Integration** (3 hours)
```python
# core/engine/executor.py (modification)

# Add to Executor.__init__:
if enable_recovery:
    from phase6_error_recovery.modules.error_engine.src.engine.retry_coordinator import RetryCoordinator, RetryPolicy
    self.retry_coordinator = RetryCoordinator(
        error_engine=self.recovery_coordinator.error_engine,
        policy=RetryPolicy(max_attempts=3, backoff_base=2.0)
    )

# Modify execute_task error handling:
except Exception as e:
    if self.retry_coordinator:
        # Use retry logic
        retry_result = self.retry_coordinator.execute_with_retry(error_context)
        
        # Log telemetry
        self.event_bus.emit("task.retry_complete", {
            "task_id": task.id,
            "attempts": retry_result.attempts_made,
            "success": retry_result.success,
            "fix_method": retry_result.final_fix_method
        })
        
        if retry_result.success:
            return AdapterResult(exit_code=0, metadata={"retry_fixed": True})
        else:
            return AdapterResult(exit_code=1, error_log=retry_result.error_message)
    else:
        # Original behavior
        raise
```

**Task 4.3: Mechanical Fix Catalog** (3 hours)
```yaml
operation_kind: create_fix_catalog
inputs:
  - path: phase6_error_recovery/modules/error_engine/src/fixes/mechanical_catalog.py
fixes:
  - import_missing: Auto-add missing import statements
  - import_sort: Fix import order (isort)
  - format_black: Apply black formatting
  - trailing_whitespace: Remove trailing spaces
  - unused_import: Remove unused imports
  - undefined_variable: Add variable declarations
  - indentation: Fix indentation errors
  - quote_consistency: Normalize quote style
  - line_length: Break long lines
  - missing_docstring: Add basic docstring
  - type_hint_simple: Add basic type hints
  - f_string_conversion: Convert .format() to f-strings
  - dict_comprehension: Convert loops to comprehensions
  - list_comprehension: Convert loops to comprehensions
  - pathlib_conversion: Convert os.path to pathlib
  - context_manager: Add with statements
  - exception_catching: Add try/except blocks
  - logging_addition: Add logging statements
  - timeout_wrapper: Add timeout decorators
  - retry_decorator: Add retry decorators
outputs:
  - 20 idempotent mechanical fixes
  - Each fix with before/after examples
  - Each fix with test cases
```

**Task 4.4: Testing** (2 hours)
```yaml
operation_kind: create_test_suite
inputs:
  - path: tests/error/integration/test_retry_coordinator.py
test_cases:
  - test_retry_success_first_attempt
  - test_retry_success_second_attempt
  - test_retry_all_failed_escalate
  - test_backoff_timing
  - test_mechanical_only_policy
  - test_ai_agent_no_retry
  - test_timeout_enforcement
  - test_telemetry_logged
validation:
  - pytest coverage ≥90%
  - Integration test with real error engine
```

**Validation Criteria**:
- [ ] 60% of errors auto-fixed without escalation
- [ ] Retry backoff timing correct (2s, 4s, 8s)
- [ ] Telemetry logged for all retry attempts
- [ ] AI escalation only after exhausted retries
- [ ] Mechanical fixes are idempotent

---

### WS-AUTO-005: Standard Orchestrator CLI

**Execution Pattern**: EXEC-004 (Atomic Operations)  
**Priority**: HIGH  
**Effort**: 3 hours  
**Savings**: 5 hours/month  
**Fixes**: BREAK-005 (Orchestrator Invocation → Standardization)

#### Tasks

**Task 5.1: Create Orchestrator CLI** (2 hours)
```python
# core/cli/orchestrator_cli.py
import click
import json
import yaml
from pathlib import Path
from core.engine.orchestrator import Orchestrator
from core.engine.plan_schema import Plan

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Orchestrator CLI for workstream execution."""
    pass

@cli.command()
@click.option('--plan', required=True, type=click.Path(exists=True), help='Path to plan YAML')
@click.option('--phase', required=True, help='Phase ID (e.g., phase2_request_building)')
@click.option('--workstream', default=None, help='Optional workstream ID')
@click.option('--project', default='user', help='Project ID')
@click.option('--timeout', default=3600, help='Timeout in seconds')
def run(plan, phase, workstream, project, timeout):
    """Execute a plan via orchestrator."""
    orch = Orchestrator()
    
    # Load plan
    with open(plan) as f:
        plan_data = yaml.safe_load(f)
    
    # Create run
    run_id = orch.create_run(project, phase, workstream)
    click.echo(f"Created run: {run_id}")
    
    # Execute
    try:
        result = orch.execute_plan(Plan(**plan_data), run_id, timeout=timeout)
        status = "SUCCESS" if result.success else "FAILED"
        click.echo(f"Run {run_id}: {status}")
        return 0 if result.success else 1
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        orch.update_run_state(run_id, "failed")
        return 1

@cli.command()
@click.argument('run_id')
@click.option('--format', type=click.Choice(['json', 'yaml', 'text']), default='text')
def status(run_id, format):
    """Get run status."""
    orch = Orchestrator()
    status = orch.get_run_status(run_id)
    
    if not status:
        click.echo(f"Run {run_id} not found", err=True)
        return 1
    
    if format == 'json':
        click.echo(json.dumps(status, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(status, default_flow_style=False))
    else:
        click.echo(f"Run ID: {status['run_id']}")
        click.echo(f"State: {status['state']}")
        click.echo(f"Phase: {status['phase_id']}")
        click.echo(f"Created: {status['created_at']}")

@cli.command()
@click.option('--phase', help='Filter by phase')
@click.option('--state', help='Filter by state')
@click.option('--limit', default=10, help='Max results')
def list(phase, state, limit):
    """List recent runs."""
    orch = Orchestrator()
    runs = orch.list_runs(phase=phase, state=state, limit=limit)
    
    for run in runs:
        click.echo(f"{run['run_id']}: {run['state']} ({run['phase_id']})")

@cli.command()
@click.argument('run_id')
@click.option('--force', is_flag=True, help='Force cancel without confirmation')
def cancel(run_id, force):
    """Cancel a running execution."""
    if not force:
        click.confirm(f"Cancel run {run_id}?", abort=True)
    
    orch = Orchestrator()
    orch.update_run_state(run_id, "cancelled")
    click.echo(f"Run {run_id} cancelled")

if __name__ == '__main__':
    cli()
```

**Task 5.2: Setup Entry Point** (0.5 hours)
```python
# setup.py addition
entry_points={
    'console_scripts': [
        'orchestrate=core.cli.orchestrator_cli:cli',
        'pattern=patterns.cli.pattern_orchestrate:cli',
    ],
}
```

**Task 5.3: Documentation** (0.5 hours)
```markdown
# Orchestrator CLI Guide

## Installation
```bash
pip install -e .
```

## Usage

### Run a workstream
```bash
orchestrate run --plan plans/phase2.yaml --phase phase2_request_building
```

### Check run status
```bash
orchestrate status RUN-12345
```

### List recent runs
```bash
orchestrate list --phase phase2 --limit 20
```

### Cancel a run
```bash
orchestrate cancel RUN-12345 --force
```

## Migration from Old Scripts
```bash
# Old:
python scripts/run_workstream.py --plan plans/phase2.yaml

# New:
orchestrate run --plan plans/phase2.yaml --phase phase2
```
```

**Validation Criteria**:
- [ ] CLI installed and accessible via `orchestrate` command
- [ ] All subcommands work (run, status, list, cancel)
- [ ] Migration guide published
- [ ] Top 5 scripts migrated to use CLI

---

### Phase 1 Summary

**Workstreams Completed**: 5  
**Total Effort**: 34 hours  
**Chain Breaks Fixed**: 5  
**Monthly Savings**: 90 hours  
**ROI**: 26:1

**Validation Checklist**:
- [ ] WS-AUTO-001: Pattern execution automated (95% success rate)
- [ ] WS-AUTO-002: Top 10 scripts use orchestrator wrapper
- [ ] WS-AUTO-003: Health monitoring daemon running 24/7
- [ ] WS-AUTO-004: 60% errors auto-fixed via retry logic
- [ ] WS-AUTO-005: Orchestrator CLI installed and adopted

---

## Phase 2: Quick Wins (Week 3)

**Goal**: Implement 4 high-ROI, low-effort fixes  
**Duration**: 1 week  
**Effort**: 9 hours  
**Monthly Savings**: 16 hours

### Workstreams

---

### WS-AUTO-006: Scheduled Zero-Touch Automation

**Execution Pattern**: EXEC-003 (Tool Availability Guards)  
**Priority**: MEDIUM  
**Effort**: 2 hours  
**Savings**: 2.5 hours/month  
**Fixes**: BREAK-005 (Zero-Touch Workflow → Scheduled Execution)

#### Tasks

**Task 6.1: GitHub Actions Workflow** (1 hour)
```yaml
# .github/workflows/scheduled-pattern-automation.yml
name: Scheduled Pattern Automation

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  zero-touch-workflow:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Run zero-touch workflow
        run: |
          python patterns/automation/runtime/zero_touch_workflow.py
        timeout-minutes: 30
      
      - name: Upload telemetry
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: automation-telemetry
          path: patterns/metrics/pattern_automation.db
      
      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Zero-touch automation failed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Task 6.2: Windows Task Scheduler** (1 hour)
```powershell
# patterns/automation/runtime/setup_scheduled_zero_touch.ps1
param(
    [switch]$Uninstall,
    [string]$IntervalHours = 6
)

$taskName = "PatternZeroTouchAutomation"
$scriptPath = Join-Path $PSScriptRoot "zero_touch_workflow.py"

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Zero-touch automation task removed"
    exit 0
}

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours $IntervalHours)
$action = New-ScheduledTaskAction -Execute "python" -Argument "`"$scriptPath`""

Register-ScheduledTask `
    -TaskName $taskName `
    -Trigger $trigger `
    -Action $action `
    -Description "Automated pattern detection and deployment"

Write-Host "Zero-touch automation scheduled: every $IntervalHours hours"
```

**Validation Criteria**:
- [ ] GitHub Actions workflow triggers every 6 hours
- [ ] Windows Task Scheduler runs locally every 6 hours
- [ ] Zero-touch workflow executes successfully
- [ ] Telemetry uploaded to artifacts

---

### WS-AUTO-007: Event-Triggered Auto-Approval

**Execution Pattern**: EXEC-004 (Atomic Operations)  
**Priority**: MEDIUM  
**Effort**: 2 hours  
**Savings**: 1 hour/month  
**Fixes**: BREAK-006 (Pattern Detection → Auto-Generation)

#### Tasks

**Task 7.1: Event Listener** (1.5 hours)
```python
# patterns/automation/lifecycle/auto_approval_daemon.py
import time
from datetime import datetime
from core.events.event_bus import EventBus
from patterns.automation.lifecycle.auto_approval import AutoApprovalEngine

def main():
    event_bus = EventBus()
    approval_engine = AutoApprovalEngine(confidence_threshold=0.75)
    
    print(f"[{datetime.now()}] Auto-approval daemon starting...")
    
    # Subscribe to pattern candidate events
    def on_pattern_candidate(event):
        print(f"[{datetime.now()}] New pattern candidate detected: {event.data.get('pattern_id')}")
        
        # Run approval check
        result = approval_engine.check_and_approve(event.data.get('candidate_id'))
        
        if result.approved:
            print(f"[{datetime.now()}] Pattern approved: {result.pattern_id}")
            # Emit approval event (triggers execution via WS-AUTO-001)
            event_bus.emit("pattern_approved", {
                "pattern_id": result.pattern_id,
                "confidence": result.confidence,
                "timestamp": datetime.now().isoformat()
            })
    
    event_bus.subscribe("pattern_candidate_created", on_pattern_candidate)
    
    # Keep daemon running
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
```

**Task 7.2: Integration** (0.5 hours)
```python
# patterns/automation/detectors/execution_detector.py (modification)

# Add event emission after creating candidate:
def create_candidate(self, pattern_data):
    candidate_id = self.db.insert_candidate(pattern_data)
    
    # Emit event
    from core.events.event_bus import EventBus
    event_bus = EventBus()
    event_bus.emit("pattern_candidate_created", {
        "candidate_id": candidate_id,
        "pattern_id": pattern_data['pattern_id'],
        "confidence": pattern_data['confidence']
    })
    
    return candidate_id
```

**Validation Criteria**:
- [ ] Pattern candidate → auto-approval → execution chain works
- [ ] No manual approval trigger needed
- [ ] Latency &lt;30 seconds end-to-end

---

### WS-AUTO-008: Auto-Doc Generation

**Execution Pattern**: EXEC-002 (Batch Validation)  
**Priority**: LOW  
**Effort**: 3 hours  
**Savings**: 3.75 hours/month  
**Fixes**: BREAK-015 (Documentation → Code Sync)

#### Tasks

**Task 8.1: Pre-Commit Hook** (1.5 hours)
```python
# .git/hooks/pre-commit (or .pre-commit-config.yaml)
#!/usr/bin/env python3
import subprocess
import sys

def update_readmes():
    """Auto-generate READMEs for changed modules."""
    # Get staged files
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True)
    changed_files = result.stdout.strip().split('\n')
    
    # Find changed Python modules
    modules = set()
    for f in changed_files:
        if f.endswith('.py') and not f.startswith('tests/'):
            # Extract module path
            parts = f.split('/')
            if len(parts) >= 2:
                modules.add('/'.join(parts[:-1]))
    
    # Generate READMEs
    for module in modules:
        print(f"Updating README for {module}")
        subprocess.run([
            'python', 'scripts/generate_readmes.py', 
            '--module', module, 
            '--auto-stage'
        ])

if __name__ == '__main__':
    try:
        update_readmes()
    except Exception as e:
        print(f"Warning: README generation failed: {e}", file=sys.stderr)
        # Don't block commit
        sys.exit(0)
```

**Task 8.2: CI Integration** (1 hour)
```yaml
# .github/workflows/auto-docs.yml
name: Auto-Generate Documentation

on:
  push:
    paths:
      - '**.py'
      - 'patterns/**'
      - 'core/**'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Generate READMEs
        run: |
          python scripts/generate_readmes.py --all --auto-commit
      
      - name: Commit updated docs
        if: success()
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add '**/README.md'
          git commit -m "docs: Auto-generate READMEs [skip ci]" || echo "No changes"
          git push
```

**Task 8.3: Documentation** (0.5 hours)

**Validation Criteria**:
- [ ] Pre-commit hook generates READMEs
- [ ] CI auto-commits doc updates
- [ ] Docs stay in sync with code changes

---

### WS-AUTO-009: TTL-Based Worktree Cleanup

**Execution Pattern**: EXEC-004 (Atomic Operations)  
**Priority**: LOW  
**Effort**: 2 hours  
**Savings**: 0.42 hours/month  
**Fixes**: BREAK-017 (Worktree Lifecycle → Cleanup)

#### Tasks

**Task 9.1: TTL Cleanup Script** (1 hour)
```powershell
# scripts/cleanup_stale_worktrees.ps1
param(
    [int]$DaysOld = 7,
    [switch]$DryRun
)

$worktrees = git worktree list --porcelain | Select-String "worktree" | ForEach-Object {
    $_.ToString().Replace("worktree ", "")
}

foreach ($wt in $worktrees) {
    if (-not (Test-Path $wt)) { continue }
    
    $lastModified = (Get-Item $wt).LastWriteTime
    $age = (Get-Date) - $lastModified
    
    if ($age.Days -ge $DaysOld) {
        Write-Host "Removing stale worktree: $wt (age: $($age.Days) days)"
        
        if (-not $DryRun) {
            git worktree remove $wt --force
        }
    }
}
```

**Task 9.2: Scheduled Task** (1 hour)
```powershell
# Schedule weekly cleanup
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
$action = New-ScheduledTaskAction -Execute "powershell" -Argument "-File scripts\cleanup_stale_worktrees.ps1 -DaysOld 7"
Register-ScheduledTask -TaskName "CleanupStaleWorktrees" -Trigger $trigger -Action $action
```

**Validation Criteria**:
- [ ] Stale worktrees removed automatically
- [ ] Scheduled task runs weekly
- [ ] Dry-run mode works correctly

---

### Phase 2 Summary

**Workstreams Completed**: 4  
**Total Effort**: 9 hours  
**Chain Breaks Fixed**: 4  
**Monthly Savings**: 16 hours  
**ROI**: 21:1

---

## Phase 3: Advanced Automation (Week 4-8)

**Goal**: Complete automation chain to 90% coverage  
**Duration**: 5 weeks  
**Effort**: 48 hours  
**Monthly Savings**: 34 hours/month + 3x speedup

### Workstreams

---

### WS-AUTO-010: CLI Timeout/Heartbeat Enforcement

**Execution Pattern**: EXEC-003 (Tool Availability Guards)  
**Priority**: HIGH  
**Effort**: 10 hours  
**Savings**: 3 hours/month

#### Implementation Summary
- Create timeout decorator for all CLI functions
- Implement heartbeat reporter for long-running processes
- Add stall detection with auto-kill after 2x expected duration
- Integrate with orchestrator wrapper

---

### WS-AUTO-011: Root Cause Analysis Loop

**Execution Pattern**: EXEC-007 (Dependency Install)  
**Priority**: MEDIUM  
**Effort**: 8 hours  
**Savings**: 10 hours/month

#### Implementation Summary
- Create error pattern learner
- Build root cause database
- Implement anti-pattern detector
- Generate preventive refactoring suggestions

---

### WS-AUTO-012: Auto-Deploy on CI Success

**Execution Pattern**: EXEC-009 (Validation Run)  
**Priority**: MEDIUM  
**Effort**: 6 hours  
**Savings**: 4.7 hours/month

#### Implementation Summary
- Add deploy step to CI workflow
- Implement artifact deployment
- Add rollback mechanism
- Create deployment notifications

---

### WS-AUTO-013: Event-Driven Dashboard

**Execution Pattern**: EXEC-004 (Atomic Operations)  
**Priority**: MEDIUM  
**Effort**: 4 hours  
**Savings**: ROI (real-time monitoring)

#### Implementation Summary
- Create event bus subscriber for dashboard
- Implement WebSocket real-time updates
- Add auto-refresh on DB changes
- Build alert panel

---

### WS-AUTO-014: Error Engine on CI Failures

**Execution Pattern**: EXEC-006 (Auto-Fix Linting)  
**Priority**: MEDIUM  
**Effort**: 5 hours  
**Savings**: 2.7 hours/month

#### Implementation Summary
- Integrate error engine into CI workflow
- Auto-retry test failures with fixes
- Report fix success rate
- Auto-commit successful fixes

---

### WS-AUTO-015: Automated Trend Reports

**Execution Pattern**: EXEC-002 (Batch Validation)  
**Priority**: LOW  
**Effort**: 6 hours  
**Savings**: 2 hours/month

#### Implementation Summary
- Weekly trend analysis SQL queries
- Automated report generation
- Anomaly detection alerts
- Performance regression tracking

---

### WS-AUTO-016: AIM Auto-Distribution

**Execution Pattern**: EXEC-004 (Atomic Operations)  
**Priority**: LOW  
**Effort**: 10 hours  
**Savings**: 3x speedup (parallel execution)

#### Implementation Summary
- Auto-detect parallelizable tasks
- Integrate AIM cluster manager with orchestrator
- Implement task distribution algorithm
- Add load balancing

---

### Phase 3 Summary

**Workstreams Completed**: 7  
**Total Effort**: 48 hours  
**Chain Breaks Fixed**: 7  
**Monthly Savings**: 34 hours + 3x speedup  
**ROI**: 8:1 + performance gains

---

## Complete Implementation Timeline

```
Week 1-2: Phase 1 (Critical Chain Breaks)
├── WS-AUTO-001: Pattern Execution Wrapper (8h)
├── WS-AUTO-002: Orchestrator Wrapper (6h)
├── WS-AUTO-003: Health Monitoring (4h)
├── WS-AUTO-004: Auto-Retry Fixes (12h)
└── WS-AUTO-005: Orchestrator CLI (3h)
Total: 34 hours

Week 3: Phase 2 (Quick Wins)
├── WS-AUTO-006: Scheduled Automation (2h)
├── WS-AUTO-007: Event-Triggered Approval (2h)
├── WS-AUTO-008: Auto-Doc Generation (3h)
└── WS-AUTO-009: Worktree Cleanup (2h)
Total: 9 hours

Week 4-8: Phase 3 (Advanced Automation)
├── WS-AUTO-010: Timeout/Heartbeat (10h)
├── WS-AUTO-011: Root Cause Analysis (8h)
├── WS-AUTO-012: Auto-Deploy (6h)
├── WS-AUTO-013: Event Dashboard (4h)
├── WS-AUTO-014: CI Error Engine (5h)
├── WS-AUTO-015: Trend Reports (6h)
└── WS-AUTO-016: AIM Distribution (10h)
Total: 48 hours

GRAND TOTAL: 91 hours
```

---

## Success Metrics & Validation

### Phase 1 Completion Criteria
- [ ] **Pattern Execution**: 95% automated (target: 37.5 hrs/month saved)
- [ ] **Orchestrator Adoption**: 80% scripts migrated
- [ ] **Health Monitoring**: 24/7 daemon with &lt;5 min alert latency
- [ ] **Error Auto-Fix**: 60% success rate
- [ ] **CLI Standardization**: Single entry point for orchestration

### Phase 2 Completion Criteria
- [ ] **Zero-Touch**: Scheduled automation running every 6 hours
- [ ] **Auto-Approval**: Event-driven with &lt;30s latency
- [ ] **Doc Sync**: 100% auto-generation on commits
- [ ] **Worktree Cleanup**: Weekly automated cleanup

### Phase 3 Completion Criteria
- [ ] **Timeout Enforcement**: 100% CLI coverage
- [ ] **Root Cause DB**: Populated with error patterns
- [ ] **Auto-Deploy**: CI → production with rollback
- [ ] **Real-Time Dashboard**: WebSocket updates
- [ ] **CI Auto-Fix**: Retry with error engine
- [ ] **Trend Analysis**: Weekly automated reports
- [ ] **Parallel Execution**: 3x speedup on compatible tasks

### Overall Success Metrics
- **Automation Coverage**: 90% (from 35%)
- **Manual Interventions/Day**: &lt;5 (from 35-50)
- **MTTR**: &lt;2 minutes (from 30-60 minutes)
- **Time Savings**: 140 hours/month
- **ROI**: 18:1

---

## Risk Management

### High Risk Items
1. **Orchestrator Integration Complexity**: Mitigate with incremental rollout
2. **Event Bus Performance**: Mitigate with load testing
3. **Backward Compatibility**: Maintain dual paths during migration

### Contingency Plans
- **Rollback**: All changes behind feature flags
- **Gradual Adoption**: Opt-in for initial 2 weeks
- **Fallback**: Manual processes remain functional

---

## Execution Strategy

### Team Allocation
- **Engineer 1**: Focus on Phase 1 (orchestration + health monitoring)
- **Engineer 2**: Focus on Phase 1 (error recovery + CLI)
- **Both**: Pair on Phase 2 and Phase 3

### Weekly Cadence
- **Monday**: Planning + task kickoff
- **Wednesday**: Mid-week sync + blockers resolution
- **Friday**: Demo + validation + retrospective

### Communication
- **Daily**: Async updates in Slack
- **Weekly**: Demo to stakeholders
- **Bi-weekly**: Metrics review + course correction

---

## Post-Implementation

### Maintenance
- **Weekly**: Review automation metrics
- **Monthly**: Tune thresholds and policies
- **Quarterly**: Major feature additions

### Continuous Improvement
- Collect user feedback on new CLI
- Monitor automation success rates
- Iterate on error fix catalog
- Expand mechanical fix coverage

---

## Appendix: Execution Pattern Reference

### Pattern Usage by Workstream

| Workstream | Execution Pattern | Rationale |
|------------|-------------------|-----------|
| WS-AUTO-001 | EXEC-001 (Atomic Operations) | Single CLI creation |
| WS-AUTO-002 | EXEC-002 (Batch Validation) | Migrate 10 scripts |
| WS-AUTO-003 | EXEC-003 (Tool Availability) | Daemon + scheduled task |
| WS-AUTO-004 | EXEC-006 (Auto-Fix Linting) | Mechanical fixes |
| WS-AUTO-005 | EXEC-004 (Atomic Operations) | CLI creation |
| WS-AUTO-006 | EXEC-003 (Tool Availability) | Scheduled workflow |
| WS-AUTO-007 | EXEC-004 (Atomic Operations) | Event listener |
| WS-AUTO-008 | EXEC-002 (Batch Validation) | Multi-module docs |
| WS-AUTO-009 | EXEC-004 (Atomic Operations) | Cleanup script |
| WS-AUTO-010 | EXEC-003 (Tool Availability) | Timeout guards |
| WS-AUTO-011 | EXEC-007 (Dependency Install) | ML model for patterns |
| WS-AUTO-012 | EXEC-009 (Validation Run) | CI integration |
| WS-AUTO-013 | EXEC-004 (Atomic Operations) | Dashboard component |
| WS-AUTO-014 | EXEC-006 (Auto-Fix Linting) | Error fixes in CI |
| WS-AUTO-015 | EXEC-002 (Batch Validation) | Multi-report gen |
| WS-AUTO-016 | EXEC-004 (Atomic Operations) | Orchestrator mod |

---

**Status**: ✅ **READY TO EXECUTE**  
**Total Workstreams**: 16  
**Total Effort**: 91 hours  
**Expected Completion**: 8 weeks  
**ROI**: 18:1 (140 hrs/month saved)

---

*Generated by: GitHub Copilot CLI Phase Plan Generator*  
*Creation Date: 2025-12-06*  
*Based on: Automation Chain Gap Analysis Report*
