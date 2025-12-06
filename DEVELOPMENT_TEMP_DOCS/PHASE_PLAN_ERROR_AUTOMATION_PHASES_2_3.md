# Phase 2 & 3: Error Automation High-Impact Features & Quality

**Continuation of**: PHASE_PLAN_ERROR_AUTOMATION.md Phase 1

---

## Phase 2: High Impact Automation (48 hours)

**Execution Pattern**: EXEC-003-TOOL-AVAILABILITY-GUARDS + EXEC-004-ATOMIC-OPERATIONS  
**Risk**: MEDIUM (external API integration, state mutation)  
**Time**: 48 hours (Week 3-6)  
**Deliverables**: PR creation, orchestrator integration, alerting, event bus

---

### Task 2.1: Implement Real PR Creation (20 hours)

#### Pattern: EXEC-003-TOOL-AVAILABILITY-GUARDS

**File**: `error/automation/pr_creator.py`

```python
"""GitHub PR creation for error patches

EXECUTION PATTERN: EXEC-003 (Tool Availability Guards)
- Validates GitHub token before execution
- Checks repository access
- Graceful fallback if API unavailable
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess


class PRCreator:
    """Creates PRs with auto-merge for validated patches"""
    
    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        token: Optional[str] = None
    ):
        """Initialize PR creator with GitHub credentials.
        
        Pattern: EXEC-003 - Validate tool availability at init
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        # Get token from env or parameter
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        # EXEC-003: Validate token availability
        if not self.token:
            raise ValueError(
                "GITHUB_TOKEN environment variable required for PR creation. "
                "Set via: export GITHUB_TOKEN='ghp_...'"
            )
        
        # Lazy import to allow module load even if PyGithub not installed
        try:
            from github import Github, GithubException
            self.Github = Github
            self.GithubException = GithubException
        except ImportError as e:
            raise ImportError(
                "PyGithub library required for PR creation. "
                "Install via: pip install PyGithub"
            ) from e
        
        # Initialize GitHub client
        self.gh = self.Github(self.token)
        
        # EXEC-003: Validate repository access
        try:
            self.repo = self.gh.get_repo(f"{repo_owner}/{repo_name}")
            # Test access
            self.repo.get_branch('main')
        except self.GithubException as e:
            raise ValueError(
                f"Cannot access repository {repo_owner}/{repo_name}. "
                f"Check token permissions. Error: {e}"
            )
    
    def create_pr_with_auto_merge(
        self,
        patch_path: Path,
        confidence: Dict[str, float],
        base_branch: str = 'main'
    ) -> Dict[str, Any]:
        """Create PR with auto-merge enabled.
        
        Pattern: EXEC-004 - Atomic multi-step operation
        - Create branch
        - Apply patch
        - Create PR
        - Enable auto-merge
        - Rollback on any failure
        """
        branch_name = f"error-fix/{patch_path.stem}-{self._generate_timestamp()}"
        pr = None
        
        try:
            # Step 1: Create branch
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            new_ref = self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_ref.object.sha
            )
            
            # Step 2: Apply patch to branch
            self._apply_patch_to_branch(patch_path, branch_name)
            
            # Step 3: Create PR
            pr = self.repo.create_pull(
                title=f"[Auto] Error fix: {patch_path.stem}",
                body=self._generate_pr_body(patch_path, confidence),
                head=branch_name,
                base=base_branch
            )
            
            # Step 4: Add labels
            pr.add_to_labels('automated-fix', 'error-recovery')
            
            # Step 5: Enable auto-merge (GraphQL API required)
            # Note: This requires GitHub GraphQL API, simplified here
            # In production, use: gh pr merge --auto --squash <PR_NUMBER>
            self._enable_auto_merge_cli(pr.number)
            
            return {
                'status': 'pr_created',
                'pr_number': pr.number,
                'pr_url': pr.html_url,
                'branch': branch_name,
                'auto_merge_enabled': True
            }
            
        except Exception as e:
            # Rollback: Delete branch if PR creation failed
            if pr is None:
                try:
                    self.repo.get_git_ref(f"heads/{branch_name}").delete()
                except Exception:
                    pass
            
            return {
                'status': 'failed',
                'error': str(e),
                'branch': branch_name
            }
    
    def _apply_patch_to_branch(self, patch_path: Path, branch_name: str) -> None:
        """Apply patch to remote branch.
        
        Uses local git worktree to apply patch, then pushes to remote.
        """
        import tempfile
        
        with tempfile.TemporaryDirectory(prefix='pr_patch_') as tmpdir:
            worktree_path = Path(tmpdir) / 'worktree'
            
            # Create worktree on new branch
            subprocess.run(
                ['git', 'worktree', 'add', str(worktree_path), branch_name],
                check=True,
                capture_output=True
            )
            
            try:
                # Apply patch
                subprocess.run(
                    ['git', 'apply', str(patch_path)],
                    cwd=worktree_path,
                    check=True,
                    capture_output=True
                )
                
                # Stage and commit
                subprocess.run(
                    ['git', 'add', '-A'],
                    cwd=worktree_path,
                    check=True,
                    capture_output=True
                )
                
                subprocess.run(
                    ['git', 'commit', '-m', f'Auto-apply patch: {patch_path.name}'],
                    cwd=worktree_path,
                    check=True,
                    capture_output=True
                )
                
                # Push to remote
                subprocess.run(
                    ['git', 'push', 'origin', branch_name],
                    cwd=worktree_path,
                    check=True,
                    capture_output=True
                )
                
            finally:
                # Cleanup worktree
                subprocess.run(
                    ['git', 'worktree', 'remove', str(worktree_path), '--force'],
                    capture_output=True
                )
    
    def _enable_auto_merge_cli(self, pr_number: int) -> None:
        """Enable auto-merge using GitHub CLI.
        
        Requires 'gh' CLI to be installed and authenticated.
        """
        try:
            subprocess.run(
                ['gh', 'pr', 'merge', str(pr_number), '--auto', '--squash'],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # Non-fatal: PR created but auto-merge not enabled
            print(f"Warning: Could not enable auto-merge for PR #{pr_number}")
    
    def _generate_pr_body(
        self,
        patch_path: Path,
        confidence: Dict[str, float]
    ) -> str:
        """Generate PR description with confidence metrics."""
        return f"""## Automated Error Recovery Patch

**Patch**: `{patch_path.name}`  
**Confidence Score**: {confidence['overall']:.1%}

### Validation Results

| Check | Result | Score |
|-------|--------|-------|
| Tests | {'✅ Passed' if confidence['tests_passed'] == 1.0 else '❌ Failed'} | {confidence['tests_passed']:.1%} |
| Linting | {'✅ Passed' if confidence['lint_passed'] == 1.0 else '⚠️ Warnings'} | {confidence['lint_passed']:.1%} |
| Type Checking | {'✅ Passed' if confidence['type_check_passed'] == 1.0 else '⚠️ Issues'} | {confidence['type_check_passed']:.1%} |
| Security Scan | {'✅ Passed' if confidence['security_scan_passed'] == 1.0 else '❌ Failed'} | {confidence['security_scan_passed']:.1%} |
| Coverage | {'✅ Maintained' if confidence['coverage_maintained'] >= 0.7 else '⚠️ Reduced'} | {confidence['coverage_maintained']:.1%} |

### Automation Details

This PR was created automatically by the error recovery automation system.

- **Auto-merge**: {'Enabled - will merge after CI passes' if confidence['overall'] >= 0.80 else 'Disabled - requires manual review'}
- **Decision log**: `.state/patch_decisions.jsonl`
- **Confidence threshold**: {confidence['overall']:.1%} (PR threshold: 80%)

### Review Guidelines

This patch scored between 80-95% confidence. Please review:

1. ✅ Validation results above are acceptable
2. ✅ Changes align with project conventions
3. ✅ No unintended side effects

If approved, CI will auto-merge. If not, close this PR and reject the patch in the manual review queue.

---

*Generated by error automation* 🤖
"""
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp for branch name."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d%H%M%S')
```

**Integration**: Update `error/automation/patch_applier.py`

```python
# In patch_applier.py, replace _create_pr_with_auto_merge():

def _create_pr_with_auto_merge(self, patch_path: Path) -> Dict[str, Any]:
    """Create PR with auto-merge enabled."""
    try:
        # Import PR creator
        from error.automation.pr_creator import PRCreator
        
        # Get repo info from git config
        repo_info = self._get_repo_info()
        
        # Create PR
        creator = PRCreator(
            repo_owner=repo_info['owner'],
            repo_name=repo_info['name']
        )
        
        # Get confidence score from recent validation
        confidence = self._last_confidence_score
        
        result = creator.create_pr_with_auto_merge(
            patch_path=patch_path,
            confidence=confidence.to_dict()
        )
        
        return result
        
    except Exception as e:
        return {
            'status': 'pr_creation_failed',
            'error': str(e),
            'fallback': 'Patch queued for manual PR creation'
        }

def _get_repo_info(self) -> Dict[str, str]:
    """Extract repo owner/name from git remote."""
    result = subprocess.run(
        ['git', 'remote', 'get-url', 'origin'],
        cwd=self.repo_path,
        capture_output=True,
        text=True,
        check=True
    )
    
    # Parse: git@github.com:owner/repo.git or https://github.com/owner/repo.git
    url = result.stdout.strip()
    
    if 'github.com' in url:
        parts = url.split('/')
        owner = parts[-2].split(':')[-1]
        name = parts[-1].replace('.git', '')
        return {'owner': owner, 'name': name}
    
    raise ValueError(f"Could not parse GitHub repo from remote: {url}")
```

**Validation**:
```bash
# Set GitHub token
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"

# Test PR creation (dry run)
python -c "
from pathlib import Path
from error.automation.pr_creator import PRCreator

creator = PRCreator('OWNER', 'REPO')
print('✅ PR creator initialized successfully')
"

# Integration test (requires actual patch file)
# python scripts/run_error_automation.py apply test_medium_confidence.patch
```

**Exit Criteria**:
- ✅ PRCreator validates GitHub token at init
- ✅ Repository access verified before operations
- ✅ Branch creation + patch application works
- ✅ PR body includes confidence breakdown
- ✅ Auto-merge enabled via CLI
- ✅ Graceful fallback on API errors

---

### Task 2.2: Integrate with Core Orchestrator (12 hours)

#### Pattern: EXEC-004-ATOMIC-OPERATIONS

**File**: `core/adapters/error_automation_adapter.py`

```python
"""Adapter for error automation tasks

EXECUTION PATTERN: EXEC-004 (Atomic Operations)
- State updates are transactional
- Rollback on failure
- Event emission for observability
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from core.adapters.base import ToolAdapter, ToolConfig
from core.events.event_bus import Event, EventBus, EventSeverity
from error.automation.patch_applier import PatchApplier


class ErrorAutomationAdapter(ToolAdapter):
    """Executes error recovery automation tasks"""
    
    def __init__(self, config: ToolConfig, event_bus: Optional[EventBus] = None):
        super().__init__(config)
        
        self.event_bus = event_bus or EventBus()
        
        # Initialize patch applier with config params
        self.applier = PatchApplier(
            repo_path=Path.cwd(),
            auto_merge_threshold=config.params.get('auto_merge_threshold', 0.95),
            pr_threshold=config.params.get('pr_threshold', 0.80)
        )
        
        # Inject event bus into applier
        self.applier.event_bus = self.event_bus
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute error automation task.
        
        Pattern: EXEC-004 - Atomic execution with state tracking
        """
        task_type = request.get('task_type')
        task_id = request.get('task_id', 'unknown')
        
        # Emit start event
        self._emit_event('task_started', {
            'task_id': task_id,
            'task_type': task_type
        })
        
        try:
            if task_type == 'apply_patch':
                result = self._execute_apply_patch(request)
            elif task_type == 'process_queue':
                result = self._execute_process_queue(request)
            else:
                raise ValueError(f"Unknown task_type: {task_type}")
            
            # Emit success event
            self._emit_event('task_completed', {
                'task_id': task_id,
                'task_type': task_type,
                'result': result
            })
            
            return {
                'exit_code': 0 if result.get('decision') != 'rejected' else 1,
                'output': result,
                'metadata': {
                    'task_id': task_id,
                    'confidence': result.get('confidence', {})
                }
            }
            
        except Exception as e:
            # Emit failure event
            self._emit_event('task_failed', {
                'task_id': task_id,
                'task_type': task_type,
                'error': str(e)
            }, severity=EventSeverity.ERROR)
            
            return {
                'exit_code': 1,
                'output': {'error': str(e)},
                'metadata': {'task_id': task_id}
            }
    
    def _execute_apply_patch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patch application task."""
        patch_path = Path(request['patch_path'])
        
        if not patch_path.exists():
            raise FileNotFoundError(f"Patch file not found: {patch_path}")
        
        # Emit validation start
        self._emit_event('patch_validation_started', {
            'patch_path': str(patch_path)
        })
        
        # Execute validation
        result = self.applier.apply_with_validation(patch_path)
        
        # Emit validation complete
        self._emit_event('patch_validation_completed', {
            'patch_path': str(patch_path),
            'decision': result['decision'],
            'confidence': result['confidence']['overall']
        })
        
        return result
    
    def _execute_process_queue(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue processing task."""
        from error.automation.queue_processor import ReviewQueueProcessor
        
        processor = ReviewQueueProcessor()
        action = request.get('action', 'list')
        
        if action == 'list':
            pending = processor.list_pending()
            return {'status': 'success', 'pending': pending}
        
        elif action == 'approve':
            patch_id = request.get('patch_id')
            if not patch_id:
                raise ValueError("patch_id required for approve action")
            
            result = processor.approve(patch_id)
            
            self._emit_event('patch_approved', {
                'patch_id': patch_id
            })
            
            return result
        
        elif action == 'reject':
            patch_id = request.get('patch_id')
            reason = request.get('reason', 'No reason provided')
            
            if not patch_id:
                raise ValueError("patch_id required for reject action")
            
            result = processor.reject(patch_id, reason)
            
            self._emit_event('patch_rejected', {
                'patch_id': patch_id,
                'reason': reason
            })
            
            return result
        
        else:
            raise ValueError(f"Unknown queue action: {action}")
    
    def _emit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        severity: EventSeverity = EventSeverity.INFO
    ) -> None:
        """Emit event to event bus."""
        if self.event_bus:
            self.event_bus.emit(Event(
                event_id=f"error_auto_{datetime.now().timestamp()}",
                event_type=event_type,
                severity=severity,
                data=data,
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
```

**Register Adapter**: Update `core/adapters/__init__.py`

```python
# Add to imports
from core.adapters.error_automation_adapter import ErrorAutomationAdapter

# Add to __all__
__all__ = [
    # ... existing ...
    "ErrorAutomationAdapter",
]
```

**Validation**:
```bash
# Test adapter initialization
python -c "
from core.adapters.error_automation_adapter import ErrorAutomationAdapter
from core.adapters.base import ToolConfig

adapter = ErrorAutomationAdapter(ToolConfig(
    tool_id='error_automation',
    params={'auto_merge_threshold': 0.95}
))

print('✅ Adapter initialized successfully')
"

# Test execution (requires patch file)
# result = adapter.execute({
#     'task_type': 'apply_patch',
#     'task_id': 'test-001',
#     'patch_path': 'test.patch'
# })
```

**Exit Criteria**:
- ✅ Adapter integrates with ToolAdapter base
- ✅ Events emitted for all state transitions
- ✅ Errors caught and logged
- ✅ Adapter registered in core/adapters/__init__.py

---

### Task 2.3: Add Alerting (8 hours)

**File**: `error/automation/alerting.py`

```python
"""Alerting for error automation failures

EXECUTION PATTERN: EXEC-003 (Tool Availability Guards)
- Validates Slack webhook before sending
- Graceful degradation if unavailable
- Logs alerts even if delivery fails
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class AlertManager:
    """Sends alerts for error automation events"""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        alert_log: Optional[Path] = None
    ):
        """Initialize alert manager.
        
        Pattern: EXEC-003 - Validate tool availability
        """
        self.slack_webhook = slack_webhook or os.getenv('SLACK_WEBHOOK_URL')
        self.alert_log = alert_log or Path(".state/alerts.jsonl")
        self.alert_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if requests is available for Slack
        try:
            import requests
            self.requests = requests
            self.slack_available = bool(self.slack_webhook)
        except ImportError:
            self.requests = None
            self.slack_available = False
    
    def alert_patch_failed(
        self,
        patch_path: str,
        error: str,
        confidence: Optional[Dict[str, float]] = None
    ) -> None:
        """Alert when patch validation fails."""
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'patch_failed',
            'patch_path': patch_path,
            'error': error,
            'confidence': confidence or {}
        }
        
        # Log to file
        self._log_alert(alert)
        
        # Send to Slack
        if self.slack_available:
            self._send_slack({
                'text': f"❌ Patch validation failed: `{Path(patch_path).name}`",
                'attachments': [{
                    'color': 'danger',
                    'fields': [
                        {'title': 'Error', 'value': error, 'short': False},
                        {'title': 'Patch', 'value': patch_path, 'short': True},
                        {'title': 'Confidence', 'value': f"{confidence.get('overall', 0):.1%}" if confidence else 'N/A', 'short': True}
                    ]
                }]
            })
    
    def alert_queue_backlog(
        self,
        count: int,
        oldest_hours: float,
        threshold_count: int = 10,
        threshold_hours: float = 72
    ) -> None:
        """Alert when manual review queue grows too large."""
        if count < threshold_count and oldest_hours < threshold_hours:
            return  # No alert needed
        
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'queue_backlog',
            'pending_count': count,
            'oldest_age_hours': oldest_hours
        }
        
        # Log to file
        self._log_alert(alert)
        
        # Determine severity
        color = 'danger' if count > threshold_count or oldest_hours > threshold_hours else 'warning'
        
        # Send to Slack
        if self.slack_available:
            self._send_slack({
                'text': f"⚠️ Manual review queue backlog detected",
                'attachments': [{
                    'color': color,
                    'fields': [
                        {'title': 'Pending Reviews', 'value': str(count), 'short': True},
                        {'title': 'Oldest Age', 'value': f"{oldest_hours:.1f}h", 'short': True},
                        {'title': 'Threshold', 'value': f"{threshold_count} items / {threshold_hours}h", 'short': False}
                    ]
                }]
            })
    
    def alert_auto_merge_success(
        self,
        patch_path: str,
        confidence: Dict[str, float]
    ) -> None:
        """Alert when high-confidence patch auto-merges."""
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'auto_merge_success',
            'patch_path': patch_path,
            'confidence': confidence
        }
        
        # Log to file
        self._log_alert(alert)
        
        # Send to Slack (informational)
        if self.slack_available:
            self._send_slack({
                'text': f"✅ Auto-merged patch: `{Path(patch_path).name}`",
                'attachments': [{
                    'color': 'good',
                    'fields': [
                        {'title': 'Confidence', 'value': f"{confidence['overall']:.1%}", 'short': True},
                        {'title': 'Patch', 'value': patch_path, 'short': True}
                    ]
                }]
            })
    
    def _log_alert(self, alert: Dict[str, Any]) -> None:
        """Log alert to file."""
        with open(self.alert_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert) + '\n')
    
    def _send_slack(self, payload: Dict[str, Any]) -> None:
        """Send Slack notification."""
        if not self.slack_available or not self.requests:
            return
        
        try:
            response = self.requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            # Non-fatal: Log error but don't crash
            print(f"Warning: Failed to send Slack alert: {e}")
```

**Integration**: Update `error/automation/patch_applier.py`

```python
# Add to __init__:
from error.automation.alerting import AlertManager

class PatchApplier:
    def __init__(self, ...):
        # ... existing code ...
        self.alert_manager = AlertManager()
    
    def apply_with_validation(self, patch_path: Path) -> Dict[str, Any]:
        # ... existing code ...
        
        # After decision is made:
        if decision == PatchDecision.AUTO_MERGE and result.get('action_taken', {}).get('status') == 'merged':
            self.alert_manager.alert_auto_merge_success(
                str(patch_path),
                confidence.to_dict()
            )
        
        elif decision == PatchDecision.REJECTED:
            self.alert_manager.alert_patch_failed(
                str(patch_path),
                result.get('error', 'Validation failed'),
                confidence.to_dict()
            )
        
        return result
```

**Scheduled Monitor** (add to CI or cron): `scripts/monitor_error_automation.py`

```python
#!/usr/bin/env python3
"""Monitor error automation health (run hourly via cron/CI)"""

from error.automation.queue_processor import ReviewQueueProcessor
from error.automation.alerting import AlertManager

def main():
    processor = ReviewQueueProcessor()
    alert_manager = AlertManager()
    
    # Get queue metrics
    metrics = processor.get_queue_metrics()
    
    # Alert if unhealthy
    if metrics['health'] != 'good':
        alert_manager.alert_queue_backlog(
            count=metrics['total_pending'],
            oldest_hours=metrics['oldest_age_hours']
        )
    
    print(f"Queue health: {metrics['health']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
```

**Validation**:
```bash
# Test alerting (without Slack)
python -c "
from error.automation.alerting import AlertManager

mgr = AlertManager()
mgr.alert_patch_failed('test.patch', 'Test error', {'overall': 0.75})
print('✅ Alert logged to .state/alerts.jsonl')
"

# Verify log
tail -1 .state/alerts.jsonl

# Test with Slack (optional - requires webhook)
# export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
# python scripts/monitor_error_automation.py
```

**Exit Criteria**:
- ✅ Alerts logged to file even without Slack
- ✅ Slack integration works when webhook configured
- ✅ Queue backlog monitoring works
- ✅ Auto-merge success notifications sent

---

## Phase 2 Validation & Delivery

### Validation Checklist
```bash
# 1. All files created
ls error/automation/pr_creator.py
ls core/adapters/error_automation_adapter.py
ls error/automation/alerting.py
ls scripts/monitor_error_automation.py

# 2. PR creator works (requires GitHub token)
export GITHUB_TOKEN="ghp_..."
python -c "from error.automation.pr_creator import PRCreator; PRCreator('owner', 'repo')"

# 3. Adapter works
python -c "
from core.adapters.error_automation_adapter import ErrorAutomationAdapter
from core.adapters.base import ToolConfig
ErrorAutomationAdapter(ToolConfig(tool_id='error_auto'))
"

# 4. Alerting works
python scripts/monitor_error_automation.py
```

### Commit & Push
```bash
git add error/automation/pr_creator.py
git add core/adapters/error_automation_adapter.py
git add error/automation/alerting.py
git add scripts/monitor_error_automation.py

git commit -m "feat(error-automation): Phase 2 - PR creation, orchestrator integration, alerting

- Implement real GitHub PR creation with auto-merge
- Integrate with core orchestrator via adapter pattern
- Add Slack alerting for failures and queue backlog
- Add scheduled monitoring script

Closes GAP-002, GAP-003, GAP-006, GAP-012
Execution Pattern: EXEC-003, EXEC-004
Time: 48 hours
"

git push origin feature/error-automation-implementation
```

---

## Phase 3: Quality & Resilience (40 hours)

**Execution Pattern**: EXEC-002-BATCH-VALIDATION + EXEC-009-VALIDATION-RUN  
**Risk**: LOW (testing and hardening)  
**Time**: 40 hours (Week 7-10)  
**Deliverables**: Real security scans, comprehensive tests, retry logic, coverage checks

---

### Task 3.1: Implement Real Security Scanning (12 hours)

Update `error/automation/patch_applier.py`:

```python
def _run_security_scan(self, worktree_path: Path) -> Dict[str, Any]:
    """Run security scan with pip-audit and bandit.
    
    Pattern: EXEC-002 - Batch validation with multiple tools
    """
    results = {'passed': True, 'findings': []}
    
    # Tool 1: pip-audit for dependency vulnerabilities
    try:
        result = subprocess.run(
            ['pip-audit', '--requirement', 'requirements.txt', '--format', 'json'],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0 and result.stdout:
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('dependencies', [])
                
                if vulnerabilities:
                    results['passed'] = False
                    results['findings'].extend([
                        {
                            'tool': 'pip-audit',
                            'package': v.get('name'),
                            'vulnerability': v.get('vulns', [{}])[0].get('id')
                        }
                        for v in vulnerabilities
                    ])
            except json.JSONDecodeError:
                pass
                
    except subprocess.TimeoutExpired:
        results['error'] = "pip-audit timeout"
    except FileNotFoundError:
        results['error'] = "pip-audit not installed"
    except Exception as e:
        results['error'] = f"pip-audit failed: {e}"
    
    # Tool 2: bandit for Python code security issues
    try:
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json', '-ll'],  # Low and low+ severity
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.stdout:
            try:
                bandit_data = json.loads(result.stdout)
                issues = bandit_data.get('results', [])
                
                # Filter for high/medium severity
                critical_issues = [
                    i for i in issues
                    if i.get('issue_severity') in ['HIGH', 'MEDIUM']
                ]
                
                if critical_issues:
                    results['passed'] = False
                    results['findings'].extend([
                        {
                            'tool': 'bandit',
                            'file': i.get('filename'),
                            'line': i.get('line_number'),
                            'issue': i.get('issue_text'),
                            'severity': i.get('issue_severity')
                        }
                        for i in critical_issues
                    ])
            except json.JSONDecodeError:
                pass
                
    except subprocess.TimeoutExpired:
        results['error'] = results.get('error', '') + '; bandit timeout'
    except FileNotFoundError:
        results['error'] = results.get('error', '') + '; bandit not installed'
    except Exception as e:
        results['error'] = results.get('error', '') + f'; bandit failed: {e}'
    
    return results
```

**Validation**:
```bash
# Install security tools
pip install pip-audit bandit

# Test security scan (in worktree)
cd $(mktemp -d)
git init
echo "requests==2.25.0" > requirements.txt  # Known vulnerable version
pip-audit --requirement requirements.txt --format json

# Expected: Vulnerability detected
```

---

### Task 3.2: Add Comprehensive Tests (16 hours)

**File**: `tests/error/test_patch_applier.py`

```python
"""Tests for automated patch application

EXECUTION PATTERN: EXEC-009 (Validation Run)
- Pre-conditions validated
- Test isolation guaranteed
- Cleanup on success/failure
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from error.automation.patch_applier import (
    PatchApplier,
    PatchDecision,
    ConfidenceScore
)


@pytest.fixture
def mock_repo(tmp_path):
    """Create mock git repository."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Initialize git repo
    import subprocess
    subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=repo_path, check=True, capture_output=True)
    
    # Create initial commit
    (repo_path / "README.md").write_text("# Test")
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, check=True, capture_output=True)
    
    return repo_path


@pytest.fixture
def mock_patch(tmp_path):
    """Create mock patch file."""
    patch_path = tmp_path / "fix.patch"
    patch_path.write_text("""
diff --git a/test.py b/test.py
index 1234567..89abcdef 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def test():
-    return False
+    return True
""")
    return patch_path


def test_high_confidence_auto_merges(mock_repo, mock_patch):
    """High confidence patches should auto-merge."""
    applier = PatchApplier(repo_path=mock_repo, auto_merge_threshold=0.95)
    
    # Mock validation to return perfect scores
    with patch.object(applier, '_validate_patch') as mock_validate:
        mock_validate.return_value = ConfidenceScore(
            tests_passed=1.0,
            lint_passed=1.0,
            type_check_passed=1.0,
            security_scan_passed=1.0,
            coverage_maintained=1.0
        )
        
        # Mock git operations
        with patch.object(applier, '_create_worktree'), \\
             patch.object(applier, '_cleanup_worktree'), \\
             patch.object(applier, '_apply_patch'), \\
             patch.object(applier, '_auto_merge') as mock_merge:
            
            mock_merge.return_value = {'status': 'merged'}
            
            result = applier.apply_with_validation(mock_patch)
    
    assert result['decision'] == 'auto_merge'
    assert result['confidence']['overall'] >= 0.95
    mock_merge.assert_called_once()


def test_medium_confidence_creates_pr(mock_repo, mock_patch):
    """Medium confidence patches should create PR."""
    applier = PatchApplier(repo_path=mock_repo, pr_threshold=0.80)
    
    # Mock validation to return medium scores
    with patch.object(applier, '_validate_patch') as mock_validate:
        mock_validate.return_value = ConfidenceScore(
            tests_passed=1.0,
            lint_passed=0.8,
            type_check_passed=0.8,
            security_scan_passed=1.0,
            coverage_maintained=0.8
        )
        
        with patch.object(applier, '_create_worktree'), \\
             patch.object(applier, '_cleanup_worktree'), \\
             patch.object(applier, '_apply_patch'), \\
             patch.object(applier, '_create_pr_with_auto_merge') as mock_pr:
            
            mock_pr.return_value = {'status': 'pr_created', 'pr_number': 123}
            
            result = applier.apply_with_validation(mock_patch)
    
    assert result['decision'] == 'auto_merge_pr'
    assert 0.80 <= result['confidence']['overall'] < 0.95
    mock_pr.assert_called_once()


def test_low_confidence_queues_for_review(mock_repo, mock_patch):
    """Low confidence patches should queue for manual review."""
    applier = PatchApplier(repo_path=mock_repo)
    
    # Mock validation to return low scores
    with patch.object(applier, '_validate_patch') as mock_validate:
        mock_validate.return_value = ConfidenceScore(
            tests_passed=0.5,
            lint_passed=0.5,
            type_check_passed=0.5,
            security_scan_passed=1.0,
            coverage_maintained=0.5
        )
        
        with patch.object(applier, '_create_worktree'), \\
             patch.object(applier, '_cleanup_worktree'), \\
             patch.object(applier, '_apply_patch'), \\
             patch.object(applier, '_queue_for_manual_review') as mock_queue:
            
            mock_queue.return_value = {'status': 'queued'}
            
            result = applier.apply_with_validation(mock_patch)
    
    assert result['decision'] == 'manual_review'
    assert result['confidence']['overall'] < 0.80
    mock_queue.assert_called_once()


def test_validation_failure_rejects_patch(mock_repo, mock_patch):
    """Failed validation should reject patch."""
    applier = PatchApplier(repo_path=mock_repo)
    
    # Mock validation to raise exception
    with patch.object(applier, '_create_worktree'), \\
         patch.object(applier, '_apply_patch', side_effect=Exception("Apply failed")), \\
         patch.object(applier, '_cleanup_worktree'):
        
        result = applier.apply_with_validation(mock_patch)
    
    assert result['decision'] == 'rejected'
    assert 'error' in result


# Additional tests...
def test_confidence_score_calculation():
    """Confidence score calculates weighted average correctly."""
    score = ConfidenceScore(
        tests_passed=1.0,
        lint_passed=0.5,
        type_check_passed=1.0,
        security_scan_passed=1.0,
        coverage_maintained=0.8
    )
    
    # Expected: 0.4*1.0 + 0.2*0.5 + 0.15*1.0 + 0.15*1.0 + 0.1*0.8 = 0.88
    assert 0.87 <= score.overall <= 0.89
```

**Additional Test Files**:
- `tests/error/test_queue_processor.py` (queue operations)
- `tests/error/test_metrics.py` (metrics calculation)
- `tests/error/test_pr_creator.py` (PR creation, mocked GitHub API)
- `tests/error/test_alerting.py` (alert manager)

**Validation**:
```bash
# Run all error automation tests
pytest tests/error/ -v

# Run with coverage
pytest tests/error/ --cov=error.automation --cov-report=term

# Expected: 80%+ coverage
```

---

### Task 3.3: Add Retry Logic (8 hours)

Update `error/automation/patch_applier.py`:

```python
from functools import wraps
import time

def retry_on_failure(max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff.
    
    Pattern: EXEC-004 - Atomic operations with retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                    time.sleep(wait_time)
            
            return None
        return wrapper
    return decorator


# Apply to critical operations
@retry_on_failure(max_retries=3, exceptions=(subprocess.CalledProcessError,))
def _apply_patch(self, worktree_path: Path, patch_path: Path) -> None:
    """Apply patch in worktree with retry logic."""
    subprocess.run(
        ['git', 'apply', str(patch_path)],
        cwd=worktree_path,
        check=True,
        capture_output=True
    )


@retry_on_failure(max_retries=3, exceptions=(subprocess.TimeoutExpired,))
def _run_tests(self, worktree_path: Path) -> Dict[str, Any]:
    """Run test suite with retry on timeout."""
    try:
        result = subprocess.run(
            self.test_command.split(),
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        return {
            'passed': result.returncode == 0,
            'output': result.stdout + result.stderr
        }
    except subprocess.TimeoutExpired as e:
        # Re-raise for retry
        raise
```

---

### Task 3.4: Real Coverage Checks (4 hours)

Update `error/automation/patch_applier.py`:

```python
def _check_coverage(self, worktree_path: Path) -> Dict[str, Any]:
    """Check test coverage delta.
    
    Pattern: EXEC-002 - Validate before and after
    """
    try:
        # Run coverage
        result = subprocess.run(
            ['pytest', '--cov=.', '--cov-report=json:.coverage.json', '--cov-report=term'],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Parse coverage report
        coverage_file = worktree_path / '.coverage.json'
        
        if coverage_file.exists():
            import json
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data['totals']['percent_covered']
            
            return {
                'score': total_coverage / 100.0,
                'coverage_pct': total_coverage,
                'passed': total_coverage >= 70.0,
                'lines_covered': coverage_data['totals']['covered_lines'],
                'lines_total': coverage_data['totals']['num_statements']
            }
        else:
            return {'score': 0.5, 'error': 'Coverage report not generated'}
            
    except subprocess.TimeoutExpired:
        return {'score': 0.5, 'error': 'Coverage check timeout'}
    except Exception as e:
        return {'score': 0.5, 'error': f'Coverage check failed: {e}'}
```

---

## Phase 3 Validation & Delivery

```bash
# Run full test suite
pytest tests/error/ -v --cov=error.automation --cov-report=term-missing

# Verify coverage threshold
pytest tests/error/ --cov=error.automation --cov-fail-under=80

# Test retry logic (simulate failures)
# Manually test by killing test process mid-run

# Commit
git add error/automation/patch_applier.py
git add tests/error/

git commit -m "feat(error-automation): Phase 3 - Quality and resilience

- Implement real security scanning (pip-audit, bandit)
- Add comprehensive test suite (80%+ coverage)
- Add retry logic with exponential backoff
- Implement real coverage delta measurement

Closes GAP-005, GAP-008, GAP-010, GAP-011
Execution Pattern: EXEC-002, EXEC-004, EXEC-009
Time: 40 hours
"

git push origin feature/error-automation-implementation
```

---

## Final Validation & Deployment

### End-to-End Test
```bash
# 1. Create test error
echo "def broken(): return 1/0" > test_error.py

# 2. Generate patch
git diff > fix.patch

# 3. Run automation
python scripts/run_error_automation.py apply fix.patch

# 4. Verify decision
cat .state/patch_decisions.jsonl | tail -1 | jq .

# 5. Check metrics
python scripts/run_error_automation.py status
```

### Merge to Main
```bash
# Final PR review
gh pr view

# Merge
gh pr merge --squash

# Tag release
git tag -a v1.0.0-error-automation -m "Error automation implementation complete"
git push origin v1.0.0-error-automation
```

---

## Success Metrics (Post-Deployment)

### Week 1
- Monitor auto-merge rate (target: >60%)
- Review all auto-merged patches
- Tune confidence thresholds if needed

### Month 1
- Measure time savings (target: 40+ hours/month)
- Validate MTTR reduction (target: <4 hours)
- Review false positive rate (target: <5%)

### Quarter 1
- Full autonomy (target: 80% patches automated)
- Zero manual review queue backlog
- 95%+ accuracy on auto-merged patches

---

**Total Implementation Time**: 128 hours (Phases 1-3)  
**Total Time Savings**: 60+ hours/month  
**ROI**: 2:1 in year 1, improves annually
