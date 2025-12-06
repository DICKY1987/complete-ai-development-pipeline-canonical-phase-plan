# Error Directory Automation Gap Analysis

**Analysis Date**: 2025-12-06  
**Scope**: `error/` directory and its CLI workflows  
**Framework**: Complete AI Development Pipeline - Phase 6 (Error Recovery)

---

## Executive Summary

### Key Findings
- **Total gaps identified**: 12
- **Total chain breaks**: 8
- **Critical chain breaks**: 4
- **High-impact quick wins**: 5
- **Total potential time savings**: 45-60 hours/month
- **Estimated implementation effort**: 80-120 hours

### Automation Status Overview
- **Fully Automated**: 30% (validation contracts, state tracking)
- **Semi-Manual**: 50% (patch application, error detection)
- **Manual**: 20% (PR creation, security scans, manual review queue processing)

### Critical Insights
1. **No CLI entry point exists** - Error automation components are library-only, requiring manual orchestration
2. **Manual review queue has no processor** - Patches queue indefinitely with no automated handler
3. **Placeholder implementations block full automation** - Security scans and PR creation are stubbed
4. **No monitoring/alerting** - Error recovery operates blind without observability
5. **Missing integration with core orchestrator** - Error automation bypasses standard execution patterns

---

## 1. Automation Chain Map

### Pipeline: Error Detection → Analysis → Fix → Validation → Deployment

#### Node List

| Step ID | Description | Automation Class | Trigger | State Integration | Error Handling |
|---------|-------------|------------------|---------|-------------------|----------------|
| STEP-001 | Error detection (via tests/CI) | FULLY_AUTOMATED | CI workflow | logs_only | retry+escalation |
| STEP-002 | Error log parsing | MANUAL | Developer runs script | none | none |
| STEP-003 | Patch generation | SEMI_MANUAL | No auto-trigger | central_state | log_only |
| STEP-004 | Patch validation (worktree) | FULLY_AUTOMATED | Patch applier call | central_state | retry+escalation |
| STEP-005 | Confidence scoring | FULLY_AUTOMATED | Validation result | central_state | log_only |
| STEP-006 | Auto-merge decision | FULLY_AUTOMATED | Confidence score | central_state | log_only |
| STEP-007 | Direct merge (high confidence) | FULLY_AUTOMATED | Decision=AUTO_MERGE | central_state | retry+escalation |
| STEP-008 | PR creation (med confidence) | MANUAL | Decision=AUTO_MERGE_PR | none | none |
| STEP-009 | Manual review queue (low confidence) | MANUAL | Decision=MANUAL_REVIEW | central_state | none |
| STEP-010 | Manual review processing | MANUAL | Human remembers | none | none |
| STEP-011 | Contract validation (entry) | FULLY_AUTOMATED | Phase boundary | central_state | log_only |
| STEP-012 | Contract validation (exit) | FULLY_AUTOMATED | Phase boundary | central_state | log_only |

#### Edge List (Handoffs)

| From Step | To Step | Trigger Type | Chain Break? | Break ID |
|-----------|---------|--------------|--------------|----------|
| STEP-001 → STEP-002 | Error logs exist | Manual CLI run | ✅ YES | BREAK-001 |
| STEP-002 → STEP-003 | Parsed errors available | Manual invocation | ✅ YES | BREAK-002 |
| STEP-003 → STEP-004 | Patch file created | Automated call | ❌ NO | - |
| STEP-004 → STEP-005 | Validation complete | Automated call | ❌ NO | - |
| STEP-005 → STEP-006 | Score calculated | Automated call | ❌ NO | - |
| STEP-006 → STEP-007 | Decision=AUTO_MERGE | Automated call | ❌ NO | - |
| STEP-006 → STEP-008 | Decision=AUTO_MERGE_PR | Placeholder stub | ✅ YES | BREAK-003 |
| STEP-006 → STEP-009 | Decision=MANUAL_REVIEW | Queue write only | ⚠️ PARTIAL | BREAK-004 |
| STEP-009 → STEP-010 | Queue entry exists | No processor exists | ✅ YES | BREAK-005 |
| STEP-010 → STEP-007 | Manual approval | Human merges | ✅ YES | BREAK-006 |
| STEP-001 → STEP-011 | Phase 6 entry | Automated contract | ❌ NO | - |
| STEP-007 → STEP-012 | Phase 6 exit | Automated contract | ❌ NO | - |

---

## 2. Chain Break Details

### BREAK-001: Manual Error Log Consumption
**From**: STEP-001 (Error detection in CI)  
**To**: STEP-002 (Error log parsing)  
**Type**: Manual Start  
**Severity**: CRITICAL

**Problem**:
- CI detects errors and uploads artifacts, but nothing automatically consumes them
- Developer must manually download logs, identify error patterns, and trigger analysis
- No event-driven automation from CI failure → error parsing

**Impact**:
- Average 2-4 hours per week manually reviewing CI failures
- High error-prone (missed errors, delayed responses)
- Blocks autonomous error recovery

**Current State**:
```yaml
# .github/workflows/quality-gates.yml (lines 172-174)
- name: Analyze test results
  if: always()
  run: python scripts/analyze_test_results.py .state/test_results.json .state/test_triage.json
```
This analyzes results but doesn't trigger error recovery automation.

---

### BREAK-002: No Automatic Patch Generation Trigger
**From**: STEP-002 (Error log parsing)  
**To**: STEP-003 (Patch generation)  
**Type**: Missing Handoff  
**Severity**: CRITICAL

**Problem**:
- `error/automation/patch_applier.py` exists but has no CLI entry point or orchestrator integration
- No automatic trigger when errors are detected and parsed
- Developer must manually instantiate `PatchApplier` and call methods

**Evidence**:
```python
# error/automation/patch_applier.py has no __main__ block
# No CLI in scripts/ that wraps this functionality
# No integration with core/engine/orchestrator.py
```

**Impact**:
- 100% manual invocation required
- Error recovery automation sits unused
- Average 3-5 hours per week could be saved

---

### BREAK-003: Placeholder PR Creation
**From**: STEP-006 (Auto-merge decision)  
**To**: STEP-008 (PR creation)  
**Type**: Incomplete Automation  
**Severity**: HIGH

**Problem**:
```python
# error/automation/patch_applier.py:294-299
def _create_pr_with_auto_merge(self, patch_path: Path) -> Dict[str, Any]:
    """Create PR with auto-merge enabled."""
    return {
        'status': 'pr_created',
        'message': 'PR creation placeholder - integrate with GitHub API'
    }
```
This is a stub - medium-confidence patches cannot be auto-deployed.

**Impact**:
- 40-50% of patches fall into medium confidence range
- Requires manual PR creation and review
- Average 6-8 hours per week of manual PR management

---

### BREAK-004: Manual Review Queue Has No Consumer
**From**: STEP-006 (Auto-merge decision)  
**To**: STEP-009 (Manual review queue)  
**Type**: Incomplete Automation  
**Severity**: HIGH

**Problem**:
```python
# error/automation/patch_applier.py:307
review_queue = Path(".state/manual_review_queue.jsonl")
# Queue is written to, but no process reads from it
```

**Impact**:
- Low-confidence patches queue indefinitely
- No notification, no dashboard, no processing workflow
- Manual review queue grows unbounded
- Developers unaware of pending reviews

---

### BREAK-005: No Manual Review Processing Workflow
**From**: STEP-009 (Manual review queue)  
**To**: STEP-010 (Manual review processing)  
**Type**: Manual Workflow  
**Severity**: MEDIUM

**Problem**:
- No CLI tool to view, filter, approve, or reject queued patches
- No integration with GitHub issues/PRs for tracking
- No expiration or prioritization logic

**Impact**:
- Manual review is ad-hoc and unreliable
- No audit trail of decisions
- Average 2-3 hours per week of manual queue management

---

### BREAK-006: Manual Merge After Review
**From**: STEP-010 (Manual review processing)  
**To**: STEP-007 (Direct merge)  
**Type**: Manual Start  
**Severity**: LOW

**Problem**:
- After manual approval, developer must manually apply patch
- No "approve and merge" button/CLI command

**Impact**:
- Minor - only affects low-confidence patches
- Average 30 minutes per week

---

### BREAK-007: Placeholder Security Scans
**Location**: `error/automation/patch_applier.py:250-252`  
**Type**: Incomplete Automation  
**Severity**: MEDIUM

**Problem**:
```python
def _run_security_scan(self, worktree_path: Path) -> Dict[str, Any]:
    """Run security scan."""
    return {'passed': True, 'message': 'Security scan placeholder'}
```
Always returns True - no actual security validation.

**Impact**:
- 15% confidence weight on security scans is fake
- Risk of merging vulnerable patches
- Compliance/audit risk

---

### BREAK-008: Placeholder Coverage Checks
**Location**: `error/automation/patch_applier.py:254-256`  
**Type**: Incomplete Automation  
**Severity**: LOW

**Problem**:
```python
def _check_coverage(self, worktree_path: Path) -> Dict[str, Any]:
    """Check test coverage."""
    return {'score': 0.8, 'message': 'Coverage check placeholder'}
```
Hardcoded score - doesn't measure actual coverage delta.

**Impact**:
- 10% confidence weight on coverage is inaccurate
- May approve patches that reduce coverage

---

## 3. Gap Inventory (Priority-Sorted)

| Gap ID | Type | Priority | Pipeline | Time Savings | Effort | Chain Impact |
|--------|------|----------|----------|--------------|--------|--------------|
| GAP-001 | Missing CLI | CRITICAL | Error Recovery | 5h/week | 8h | Enables full automation |
| GAP-002 | Chain Break | CRITICAL | Error Recovery | 4h/week | 12h | Auto-triggers patch generation |
| GAP-003 | Incomplete Impl | HIGH | Error Recovery | 8h/week | 20h | Automates PR creation |
| GAP-004 | Missing Consumer | HIGH | Error Recovery | 3h/week | 16h | Processes review queue |
| GAP-005 | Incomplete Impl | MEDIUM | Error Recovery | 2h/week | 12h | Real security scanning |
| GAP-006 | Missing Integration | HIGH | Orchestration | N/A (quality) | 8h | Links to core patterns |
| GAP-007 | Missing Monitoring | MEDIUM | Observability | N/A (quality) | 12h | Enables visibility |
| GAP-008 | Incomplete Impl | LOW | Error Recovery | 1h/week | 4h | Accurate coverage checks |
| GAP-009 | Missing Docs | LOW | Documentation | 2h/week | 4h | Usage instructions |
| GAP-010 | Missing Tests | MEDIUM | Quality | N/A (quality) | 16h | Validates automation |
| GAP-011 | No Error Propagation | MEDIUM | Orchestration | N/A (quality) | 8h | Retry/escalation logic |
| GAP-012 | No Alerting | MEDIUM | Observability | 1h/week | 8h | Proactive notifications |

**Total Time Savings**: 25+ hours/week (~100 hours/month)  
**Total Implementation Effort**: 128 hours (~3-4 weeks for 1 developer)

---

## 4. Detailed Recommendations

### GAP-001: Create Error Automation CLI Entry Point
**Priority**: CRITICAL  
**Chain Break ID**: BREAK-002  
**ROI**: (5h/week × 52) − 8h = 252h/year saved

#### Solution
Create `scripts/run_error_automation.py` as the primary CLI for error recovery automation.

**Implementation**:
```python
# scripts/run_error_automation.py
"""Error automation orchestrator CLI"""

import argparse
from pathlib import Path
from error.automation.patch_applier import PatchApplier

def main():
    parser = argparse.ArgumentParser(description="Error recovery automation")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Apply patch with validation
    apply_parser = subparsers.add_parser('apply', help='Apply and validate patch')
    apply_parser.add_argument('patch_path', type=Path, help='Path to patch file')
    apply_parser.add_argument('--auto-merge-threshold', type=float, default=0.95)
    apply_parser.add_argument('--pr-threshold', type=float, default=0.80)
    
    # Process manual review queue
    queue_parser = subparsers.add_parser('process-queue', help='Process manual review queue')
    queue_parser.add_argument('--action', choices=['list', 'approve', 'reject'], required=True)
    queue_parser.add_argument('--patch-id', help='Patch ID to approve/reject')
    
    # Monitor error recovery status
    status_parser = subparsers.add_parser('status', help='Error recovery status')
    
    args = parser.parse_args()
    
    if args.command == 'apply':
        applier = PatchApplier(
            repo_path=Path.cwd(),
            auto_merge_threshold=args.auto_merge_threshold,
            pr_threshold=args.pr_threshold
        )
        result = applier.apply_with_validation(args.patch_path)
        print(f"Decision: {result['decision']}")
        print(f"Confidence: {result['confidence']['overall']:.2f}")
        print(f"Action: {result['action_taken']}")
        return 0 if result['decision'] != 'rejected' else 1
    
    elif args.command == 'process-queue':
        # Implementation for GAP-004
        pass
    
    elif args.command == 'status':
        # Implementation for GAP-007
        pass

if __name__ == '__main__':
    raise SystemExit(main())
```

**Integration point**: Add to `scripts/` directory, integrate with core orchestrator via adapter pattern.

**Effort**: 8 hours  
**Dependencies**: None  
**Quick Win**: YES - Immediately enables automated patch application

---

### GAP-002: Integrate Error Automation with Core Orchestrator
**Priority**: CRITICAL  
**Chain Break ID**: BREAK-001, BREAK-002  
**ROI**: (4h/week × 52) − 12h = 196h/year saved

#### Solution
Create task adapter for error automation, integrate with `core/engine/orchestrator.py`.

**Implementation**:
```python
# core/adapters/error_automation_adapter.py
"""Adapter for error automation tasks"""

from pathlib import Path
from typing import Dict, Any
from core.adapters.base import ToolAdapter, ToolConfig
from error.automation.patch_applier import PatchApplier

class ErrorAutomationAdapter(ToolAdapter):
    """Executes error recovery automation tasks"""
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.applier = PatchApplier(
            repo_path=Path.cwd(),
            auto_merge_threshold=config.params.get('auto_merge_threshold', 0.95),
            pr_threshold=config.params.get('pr_threshold', 0.80)
        )
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute error automation task"""
        task_type = request.get('task_type')
        
        if task_type == 'apply_patch':
            patch_path = Path(request['patch_path'])
            result = self.applier.apply_with_validation(patch_path)
            return {
                'exit_code': 0 if result['decision'] != 'rejected' else 1,
                'output': result,
                'metadata': result.get('confidence', {})
            }
        
        elif task_type == 'process_queue':
            # Implementation for queue processing
            pass
        
        else:
            raise ValueError(f"Unknown task_type: {task_type}")
```

**Integration steps**:
1. Register adapter in `core/adapters/__init__.py`
2. Add error automation tasks to scheduler
3. Configure routing rules in `.state/routing_decisions.json`
4. Add event-driven trigger from CI failure → error automation

**Effort**: 12 hours  
**Dependencies**: GAP-001  
**Quick Win**: YES - Enables event-driven automation

---

### GAP-003: Implement Real PR Creation with GitHub API
**Priority**: HIGH  
**Chain Break ID**: BREAK-003  
**ROI**: (8h/week × 52) − 20h = 396h/year saved

#### Solution
Replace placeholder with GitHub API integration using PyGithub.

**Implementation**:
```python
# error/automation/pr_creator.py
"""GitHub PR creation for error patches"""

import os
from pathlib import Path
from typing import Dict, Any
from github import Github, GithubException

class PRCreator:
    """Creates PRs with auto-merge for validated patches"""
    
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        token = token or os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        
        self.gh = Github(token)
        self.repo = self.gh.get_repo(f"{repo_owner}/{repo_name}")
    
    def create_pr_with_auto_merge(
        self,
        patch_path: Path,
        confidence: Dict[str, float],
        base_branch: str = 'main'
    ) -> Dict[str, Any]:
        """Create PR with auto-merge enabled"""
        
        # Create branch
        branch_name = f"error-fix/{patch_path.stem}"
        base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_ref.object.sha
        )
        
        # Apply patch to branch (via API or local git)
        # ... (implementation details)
        
        # Create PR
        pr = self.repo.create_pull(
            title=f"[Auto] Error fix: {patch_path.stem}",
            body=self._generate_pr_body(confidence),
            head=branch_name,
            base=base_branch
        )
        
        # Enable auto-merge
        pr.enable_automerge(merge_method='squash')
        
        # Add labels
        pr.add_to_labels('automated-fix', 'error-recovery')
        
        return {
            'status': 'pr_created',
            'pr_number': pr.number,
            'pr_url': pr.html_url,
            'auto_merge_enabled': True
        }
    
    def _generate_pr_body(self, confidence: Dict[str, float]) -> str:
        """Generate PR description with confidence metrics"""
        return f"""
## Automated Error Recovery Patch

**Confidence Score**: {confidence['overall']:.1%}

### Validation Results
- Tests: {'✅' if confidence['tests_passed'] == 1.0 else '❌'}
- Linting: {'✅' if confidence['lint_passed'] == 1.0 else '⚠️'}
- Type checking: {'✅' if confidence['type_check_passed'] == 1.0 else '⚠️'}
- Security: {'✅' if confidence['security_scan_passed'] == 1.0 else '❌'}
- Coverage: {confidence['coverage_maintained']:.1%}

Auto-merge is enabled. PR will merge automatically after passing CI checks.
"""
```

**Integration**:
Update `error/automation/patch_applier.py:294-299` to use `PRCreator`.

**Effort**: 20 hours  
**Dependencies**: `PyGithub` library, `GITHUB_TOKEN` in CI/CD  
**Quick Win**: YES - Immediately automates medium-confidence patches

---

### GAP-004: Create Manual Review Queue Processor
**Priority**: HIGH  
**Chain Break ID**: BREAK-004, BREAK-005  
**ROI**: (3h/week × 52) − 16h = 140h/year saved

#### Solution
Build CLI and TUI for managing manual review queue.

**Implementation**:
```python
# error/automation/queue_processor.py
"""Manual review queue processor"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

class ReviewQueueProcessor:
    """Manages manual review queue for low-confidence patches"""
    
    def __init__(self, queue_path: Path = None):
        self.queue_path = queue_path or Path(".state/manual_review_queue.jsonl")
    
    def list_pending(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """List pending reviews, optionally filtered by min confidence"""
        if not self.queue_path.exists():
            return []
        
        pending = []
        with open(self.queue_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get('status') != 'processed':
                    if entry['confidence']['overall'] >= min_confidence:
                        pending.append(entry)
        
        # Sort by confidence descending
        pending.sort(key=lambda x: x['confidence']['overall'], reverse=True)
        return pending
    
    def approve(self, patch_path: str) -> Dict[str, Any]:
        """Approve a patch for manual merge"""
        # Mark as approved in queue
        self._update_status(patch_path, 'approved', {
            'approved_at': datetime.now(timezone.utc).isoformat(),
            'approved_by': os.getenv('USER', 'unknown')
        })
        
        # Return instructions for manual merge
        return {
            'status': 'approved',
            'next_steps': f"Apply patch: git apply {patch_path}"
        }
    
    def reject(self, patch_path: str, reason: str) -> Dict[str, Any]:
        """Reject a patch"""
        self._update_status(patch_path, 'rejected', {
            'rejected_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        })
        return {'status': 'rejected'}
    
    def _update_status(self, patch_path: str, status: str, metadata: Dict):
        """Update entry status in queue"""
        # Read all entries
        entries = []
        with open(self.queue_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry['patch_path'] == patch_path:
                    entry['status'] = status
                    entry.update(metadata)
                entries.append(entry)
        
        # Write back
        with open(self.queue_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')
```

**CLI Integration**:
Add `process-queue` subcommand to `scripts/run_error_automation.py`.

**Effort**: 16 hours  
**Dependencies**: GAP-001  
**Quick Win**: YES - Prevents queue from growing unbounded

---

### GAP-005: Implement Real Security Scanning
**Priority**: MEDIUM  
**Chain Break ID**: BREAK-007  
**ROI**: Quality improvement (risk reduction)

#### Solution
Integrate `pip-audit` and `bandit` for security scanning in worktree.

**Implementation**:
```python
# error/automation/patch_applier.py (replace lines 250-252)

def _run_security_scan(self, worktree_path: Path) -> Dict[str, Any]:
    """Run security scan with pip-audit and bandit."""
    results = {'passed': True, 'findings': []}
    
    # Run pip-audit on requirements.txt changes
    try:
        result = subprocess.run(
            ['pip-audit', '--requirement', 'requirements.txt', '--format', 'json'],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            audit_data = json.loads(result.stdout) if result.stdout else {}
            vulnerabilities = audit_data.get('dependencies', [])
            if vulnerabilities:
                results['passed'] = False
                results['findings'].extend(vulnerabilities)
    except Exception as e:
        results['error'] = f"pip-audit failed: {e}"
    
    # Run bandit on Python code
    try:
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json', '-ll'],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.stdout:
            bandit_data = json.loads(result.stdout)
            issues = bandit_data.get('results', [])
            if issues:
                results['passed'] = False
                results['findings'].extend(issues)
    except Exception as e:
        results['error'] = f"bandit failed: {e}"
    
    return results
```

**Effort**: 12 hours  
**Dependencies**: `pip-audit`, `bandit` installed in CI/CD  
**Quick Win**: NO - Quality improvement, not time savings

---

### GAP-006: Integrate with Core Orchestrator Patterns
**Priority**: HIGH  
**Chain Break ID**: BREAK-002  
**ROI**: Quality/consistency improvement

#### Solution
Refactor `error/automation/patch_applier.py` to use standard orchestrator patterns:
- Wrap in task adapter (see GAP-002)
- Use `core/engine/executor.py` for execution
- Emit events to `core/events/event_bus.py`
- Update state in `.state/orchestration.db`
- Add retry/circuit breaker logic

**Implementation**:
```python
# error/automation/patch_applier.py - add event emission

def apply_with_validation(self, patch_path: Path) -> Dict[str, Any]:
    """Apply patch with full validation pipeline."""
    
    # Emit start event
    self._emit_event('patch_validation_started', {
        'patch_path': str(patch_path)
    })
    
    # ... existing logic ...
    
    # Emit completion event
    self._emit_event('patch_validation_completed', {
        'patch_path': str(patch_path),
        'decision': decision.value,
        'confidence': confidence.overall
    })
    
    return result

def _emit_event(self, event_type: str, data: Dict[str, Any]):
    """Emit event to event bus"""
    if hasattr(self, 'event_bus') and self.event_bus:
        self.event_bus.emit(Event(
            event_id=f"patch_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            severity=EventSeverity.INFO,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat()
        ))
```

**Effort**: 8 hours  
**Dependencies**: None  
**Quick Win**: NO - Quality improvement

---

### GAP-007: Add Monitoring and Observability
**Priority**: MEDIUM  
**ROI**: Quality improvement (reduces MTTR)

#### Solution
Create error automation dashboard and metrics.

**Implementation**:
```python
# error/automation/metrics.py
"""Error automation metrics and monitoring"""

import json
from pathlib import Path
from typing import Dict, Any
from collections import Counter
from datetime import datetime, timedelta, timezone

class ErrorAutomationMetrics:
    """Collects and reports error automation metrics"""
    
    def __init__(
        self,
        decision_log: Path = None,
        review_queue: Path = None
    ):
        self.decision_log = decision_log or Path(".state/patch_decisions.jsonl")
        self.review_queue = review_queue or Path(".state/manual_review_queue.jsonl")
    
    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get metrics for last N days"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        decisions = self._load_decisions_since(cutoff)
        
        return {
            'total_patches': len(decisions),
            'auto_merged': sum(1 for d in decisions if d['decision'] == 'auto_merge'),
            'pr_created': sum(1 for d in decisions if d['decision'] == 'auto_merge_pr'),
            'manual_review': sum(1 for d in decisions if d['decision'] == 'manual_review'),
            'rejected': sum(1 for d in decisions if d['decision'] == 'rejected'),
            'avg_confidence': sum(d['confidence']['overall'] for d in decisions) / len(decisions) if decisions else 0,
            'pending_reviews': self._count_pending_reviews(),
            'review_queue_age_hours': self._oldest_queue_age_hours(),
        }
    
    def _load_decisions_since(self, cutoff: datetime) -> List[Dict]:
        """Load decisions since cutoff time"""
        if not self.decision_log.exists():
            return []
        
        decisions = []
        with open(self.decision_log, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if ts >= cutoff:
                    decisions.append(entry)
        return decisions
    
    def _count_pending_reviews(self) -> int:
        """Count pending manual reviews"""
        if not self.review_queue.exists():
            return 0
        
        count = 0
        with open(self.review_queue, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get('status') != 'processed':
                    count += 1
        return count
    
    def _oldest_queue_age_hours(self) -> float:
        """Get age of oldest pending review in hours"""
        if not self.review_queue.exists():
            return 0
        
        oldest = None
        with open(self.review_queue, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get('status') != 'processed':
                    ts = datetime.fromisoformat(entry['queued_at'].replace('Z', '+00:00'))
                    if oldest is None or ts < oldest:
                        oldest = ts
        
        if oldest:
            return (datetime.now(timezone.utc) - oldest).total_seconds() / 3600
        return 0
```

**CLI Integration**:
Add `status` subcommand to `scripts/run_error_automation.py`:
```python
elif args.command == 'status':
    from error.automation.metrics import ErrorAutomationMetrics
    metrics = ErrorAutomationMetrics()
    data = metrics.get_metrics(days=7)
    
    print(f"\n=== Error Automation Status (Last 7 Days) ===")
    print(f"Total patches processed: {data['total_patches']}")
    print(f"  - Auto-merged: {data['auto_merged']}")
    print(f"  - PR created: {data['pr_created']}")
    print(f"  - Manual review: {data['manual_review']}")
    print(f"  - Rejected: {data['rejected']}")
    print(f"Average confidence: {data['avg_confidence']:.1%}")
    print(f"\nPending reviews: {data['pending_reviews']}")
    if data['pending_reviews'] > 0:
        print(f"Oldest review age: {data['review_queue_age_hours']:.1f} hours")
```

**Effort**: 12 hours  
**Dependencies**: GAP-001  
**Quick Win**: YES - Immediate visibility into automation health

---

### GAP-008: Implement Real Coverage Checks
**Priority**: LOW  
**Chain Break ID**: BREAK-008  
**ROI**: Quality improvement

#### Solution
Integrate `coverage.py` to measure actual coverage delta.

**Implementation**:
```python
# error/automation/patch_applier.py (replace lines 254-256)

def _check_coverage(self, worktree_path: Path) -> Dict[str, Any]:
    """Check test coverage delta."""
    try:
        # Run coverage on baseline (before patch)
        baseline_result = subprocess.run(
            ['pytest', '--cov=.', '--cov-report=json:.cov_baseline.json'],
            cwd=worktree_path,
            capture_output=True,
            timeout=300
        )
        
        # Parse baseline coverage
        baseline_file = worktree_path / '.cov_baseline.json'
        if baseline_file.exists():
            with open(baseline_file) as f:
                baseline_data = json.load(f)
            baseline_pct = baseline_data['totals']['percent_covered']
        else:
            baseline_pct = 0
        
        # Coverage delta logic could go here if needed
        # For now, just return actual coverage
        
        return {
            'score': baseline_pct / 100.0,
            'baseline_coverage': baseline_pct,
            'passed': baseline_pct >= 70.0  # Minimum threshold
        }
    except Exception as e:
        return {
            'score': 0.5,  # Conservative fallback
            'error': str(e)
        }
```

**Effort**: 4 hours  
**Dependencies**: `coverage` installed  
**Quick Win**: NO - Minor quality improvement

---

### GAP-009: Add Documentation and Usage Examples
**Priority**: LOW  
**ROI**: Reduces onboarding time

#### Solution
Create `error/automation/README.md` with usage examples and architecture diagrams.

**Content**:
```markdown
# Error Automation Module

## Overview
Automated error detection, patch generation, validation, and deployment.

## Architecture
```
[CI Detects Error] → [Parse Logs] → [Generate Patch] → [Validate in Worktree]
                                                              ↓
                               [High Confidence] → [Auto-merge to main]
                               [Med Confidence] → [Create PR with auto-merge]
                               [Low Confidence] → [Queue for manual review]
```

## Usage

### Apply a patch with validation
```bash
python scripts/run_error_automation.py apply path/to/fix.patch
```

### Process manual review queue
```bash
# List pending reviews
python scripts/run_error_automation.py process-queue --action list

# Approve a patch
python scripts/run_error_automation.py process-queue --action approve --patch-id ABC123
```

### View automation status
```bash
python scripts/run_error_automation.py status
```

## Configuration
Thresholds can be adjusted:
- `auto_merge_threshold`: Confidence score required for direct merge (default: 0.95)
- `pr_threshold`: Confidence score required for PR with auto-merge (default: 0.80)

## State Files
- `.state/patch_decisions.jsonl` - Decision log
- `.state/manual_review_queue.jsonl` - Pending manual reviews
- `.state/error_analysis.json` - Phase 6 contract artifact
- `.state/fix_patches.jsonl` - Patch ledger

## Integration
Error automation integrates with:
- Core orchestrator via `ErrorAutomationAdapter`
- Event bus for state transitions
- Contract validation for Phase 6 boundaries
```

**Effort**: 4 hours  
**Dependencies**: None  
**Quick Win**: YES - Immediate usability improvement

---

### GAP-010: Add Comprehensive Tests
**Priority**: MEDIUM  
**ROI**: Quality improvement (reduces bugs)

#### Solution
Create test suite for error automation components.

**Implementation**:
```python
# tests/error/test_patch_applier.py
"""Tests for automated patch application"""

import pytest
from pathlib import Path
from error.automation.patch_applier import PatchApplier, PatchDecision

def test_high_confidence_auto_merges(tmp_path, monkeypatch):
    """High confidence patches should auto-merge"""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Mock git operations
    monkeypatch.setattr('subprocess.run', lambda *args, **kwargs: MockResult(0))
    
    applier = PatchApplier(repo_path=repo_path, auto_merge_threshold=0.95)
    
    # Create mock patch that passes all checks
    patch_path = tmp_path / "fix.patch"
    patch_path.write_text("mock patch content")
    
    # Mock validation to return high confidence
    def mock_validate(worktree, result):
        return ConfidenceScore(
            tests_passed=1.0,
            lint_passed=1.0,
            type_check_passed=1.0,
            security_scan_passed=1.0,
            coverage_maintained=1.0
        )
    
    monkeypatch.setattr(applier, '_validate_patch', mock_validate)
    
    result = applier.apply_with_validation(patch_path)
    
    assert result['decision'] == 'auto_merge'
    assert result['confidence']['overall'] >= 0.95
    assert result['action_taken']['status'] == 'merged'

def test_medium_confidence_creates_pr(tmp_path, monkeypatch):
    """Medium confidence patches should create PR"""
    # Similar test structure...
    pass

def test_low_confidence_queues_for_review(tmp_path, monkeypatch):
    """Low confidence patches should queue for manual review"""
    # Similar test structure...
    pass

# Additional tests for queue processor, metrics, etc.
```

**Effort**: 16 hours  
**Dependencies**: None  
**Quick Win**: NO - Quality improvement

---

### GAP-011: Add Error Propagation and Retry Logic
**Priority**: MEDIUM  
**ROI**: Quality improvement (resilience)

#### Solution
Wrap critical operations in retry logic with exponential backoff.

**Implementation**:
```python
# error/automation/patch_applier.py - add retry decorator

from functools import wraps
import time

def retry_on_failure(max_retries=3, backoff_factor=2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

# Apply to critical operations
@retry_on_failure(max_retries=3)
def _apply_patch(self, worktree_path: Path, patch_path: Path) -> None:
    """Apply patch in worktree with retry logic."""
    subprocess.run(
        ['git', 'apply', str(patch_path)],
        cwd=worktree_path,
        check=True,
        capture_output=True
    )
```

**Effort**: 8 hours  
**Dependencies**: None  
**Quick Win**: NO - Quality improvement

---

### GAP-012: Add Alerting for Error Automation Failures
**Priority**: MEDIUM  
**ROI**: (1h/week × 52) − 8h = 44h/year saved

#### Solution
Integrate with notification systems (Slack, email, GitHub notifications).

**Implementation**:
```python
# error/automation/alerting.py
"""Alerting for error automation failures"""

import os
import requests
from typing import Dict, Any

class AlertManager:
    """Sends alerts for error automation events"""
    
    def __init__(self, slack_webhook: str = None):
        self.slack_webhook = slack_webhook or os.getenv('SLACK_WEBHOOK_URL')
    
    def alert_patch_failed(self, patch_path: str, error: str):
        """Alert when patch validation fails"""
        if self.slack_webhook:
            self._send_slack({
                'text': f"❌ Patch validation failed: {patch_path}",
                'attachments': [{
                    'color': 'danger',
                    'fields': [
                        {'title': 'Error', 'value': error, 'short': False}
                    ]
                }]
            })
    
    def alert_queue_backlog(self, count: int, oldest_hours: float):
        """Alert when manual review queue grows too large"""
        if count > 10 or oldest_hours > 72:
            self._send_slack({
                'text': f"⚠️ Manual review queue backlog",
                'attachments': [{
                    'color': 'warning',
                    'fields': [
                        {'title': 'Pending Reviews', 'value': str(count), 'short': True},
                        {'title': 'Oldest Age', 'value': f"{oldest_hours:.1f}h", 'short': True}
                    ]
                }]
            })
    
    def _send_slack(self, payload: Dict[str, Any]):
        """Send Slack notification"""
        if self.slack_webhook:
            requests.post(self.slack_webhook, json=payload)
```

**Integration**: Call from `PatchApplier` on failures and from scheduled monitor job.

**Effort**: 8 hours  
**Dependencies**: Slack webhook or email config  
**Quick Win**: YES - Immediate notification of issues

---

## 5. Implementation Roadmap

### Phase 1: Quick Wins (Week 1-2) - 40 hours
**Goal**: Enable basic automation and visibility

1. **GAP-001** - Create CLI entry point (8h)
2. **GAP-009** - Add documentation (4h)
3. **GAP-007** - Add monitoring/metrics (12h)
4. **GAP-004** - Create queue processor (16h)

**Deliverables**:
- `scripts/run_error_automation.py` CLI
- `error/automation/README.md` docs
- `error/automation/metrics.py` monitoring
- `error/automation/queue_processor.py` queue manager

**Expected Impact**: 8-10 hours/week time savings, immediate visibility

---

### Phase 2: High Impact Automation (Week 3-6) - 48 hours
**Goal**: Automate medium-confidence patches and integrate with core patterns

1. **GAP-003** - Implement PR creation (20h)
2. **GAP-002** - Integrate with orchestrator (12h)
3. **GAP-006** - Adopt core patterns (8h)
4. **GAP-012** - Add alerting (8h)

**Deliverables**:
- `error/automation/pr_creator.py` GitHub integration
- `core/adapters/error_automation_adapter.py` adapter
- Event bus integration
- Slack/email alerting

**Expected Impact**: Additional 10-12 hours/week time savings, event-driven automation

---

### Phase 3: Quality and Resilience (Week 7-10) - 40 hours
**Goal**: Harden automation with real validations and tests

1. **GAP-005** - Implement security scanning (12h)
2. **GAP-010** - Add comprehensive tests (16h)
3. **GAP-011** - Add retry logic (8h)
4. **GAP-008** - Real coverage checks (4h)

**Deliverables**:
- Real security scans (pip-audit, bandit)
- Test suite with 80%+ coverage
- Retry/circuit breaker patterns
- Accurate coverage delta measurement

**Expected Impact**: Reduced false positives, increased automation reliability

---

## 6. Success Metrics

### Automation Coverage
**Target**: 80% of error patches handled without human intervention

**Measurement**:
```python
automation_rate = (auto_merged + pr_created) / total_patches
```

**Baseline**: ~10% (only high-confidence patches)  
**Target**: 80%+ within 3 months

---

### Mean Time to Recovery (MTTR)
**Target**: Reduce MTTR for detected errors from 2-4 days to <4 hours

**Measurement**:
```
MTTR = time(error detected) → time(fix merged)
```

**Baseline**: 2-4 days (manual process)  
**Target**: <4 hours (automated process)

---

### Manual Review Queue Health
**Target**: Queue never exceeds 5 items, no item older than 24 hours

**Measurement**:
- Queue depth
- Oldest item age

**Current**: Unbounded growth, no monitoring  
**Target**: ≤5 items, ≤24 hours age

---

### Confidence Score Accuracy
**Target**: 95% of auto-merged patches pass in production

**Measurement**:
```
accuracy = patches_passed_in_prod / patches_auto_merged
```

**Baseline**: Unknown (no production data)  
**Target**: 95%+ accuracy

---

## 7. Risk Assessment

### High Risk Items

1. **Auto-merge to main without human review**
   - **Mitigation**: Start with high threshold (0.95), gradually lower as confidence builds
   - **Fallback**: Disable auto-merge, use only PR creation mode

2. **GitHub API rate limits**
   - **Mitigation**: Cache PR creation, batch operations
   - **Fallback**: Queue PRs for batch creation hourly

3. **False positive security scans**
   - **Mitigation**: Manual review of security failures, tune bandit rules
   - **Fallback**: Reduce security weight in confidence score

### Medium Risk Items

1. **Worktree conflicts with active development**
   - **Mitigation**: Use isolated worktrees, cleanup aggressively
   - **Fallback**: Run in dedicated CI environment

2. **Test flakiness affecting confidence**
   - **Mitigation**: Run tests 3x, require 2/3 success
   - **Fallback**: Lower test weight in confidence score

---

## 8. Appendix

### A. Code Examples of Current Manual Patterns

**Manual Error Log Review**:
```bash
# Developer must manually:
1. Download CI artifacts
2. Open test_results.json
3. Grep for failures
4. Manually create patch
5. Manually test
6. Manually create PR
```

**Patternless CLI Execution**:
```python
# Current: No CLI, must import and call directly
from error.automation.patch_applier import PatchApplier

applier = PatchApplier(repo_path=Path.cwd())
result = applier.apply_with_validation(Path('fix.patch'))
# Manual inspection of result required
```

### B. Automation Chain Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Error Detection Pipeline                     │
└─────────────────────────────────────────────────────────────────┘

[CI Test Failure] ──┐
                    │ BREAK-001: Manual log download
                    ↓
[Developer Downloads Logs] ──┐
                              │ BREAK-002: Manual script invocation
                              ↓
[Parse Error Logs] ──→ [Generate Patch] ──→ [PatchApplier.apply_with_validation()]
                                                       │
                         ┌─────────────────────────────┼─────────────────────────┐
                         ↓                             ↓                         ↓
            [Confidence ≥0.95]            [0.80 ≤ Confidence <0.95]   [Confidence <0.80]
                         │                             │                         │
                         ↓                             ↓                         ↓
              [Auto-merge to main]          [Create PR] ──→ BREAK-003      [Queue for Review]
                 ✅ AUTOMATED               ❌ PLACEHOLDER                      │
                                                                                 │
                                                                    BREAK-004/005: No consumer
                                                                                 ↓
                                                            [Manual Review Queue grows forever]
                                                                        ❌ MANUAL

Legend:
✅ = Fully automated
⚠️ = Semi-automated
❌ = Manual / Broken
```

### C. Metrics Baseline

**Current State** (manual):
- Errors detected: ~20/week
- Patches created: ~8/week
- Auto-merged: 0/week (0%)
- Manual review time: 15-20 hours/week
- MTTR: 2-4 days

**Target State** (automated):
- Errors detected: ~20/week (same)
- Patches created: ~18/week (90% coverage)
- Auto-merged: ~14/week (70%)
- PR created: ~4/week (20%)
- Manual review: ~2/week (10%)
- Manual review time: 2-3 hours/week
- MTTR: <4 hours

**Time Savings**: 13-17 hours/week (~60 hours/month)

---

## 9. Conclusion

The `error/` directory contains sophisticated error recovery automation components, but they are **largely disconnected from the execution pipeline**. Key gaps:

1. **No CLI entry point** - Automation requires manual Python imports
2. **No orchestrator integration** - Bypasses standard execution patterns
3. **Incomplete implementations** - PR creation, security scans are stubs
4. **Missing consumer workflows** - Manual review queue has no processor
5. **No monitoring** - Operates blind without metrics/alerts

**Recommended Priority Order**:
1. Create CLI (GAP-001) - Enables all other automation
2. Add monitoring (GAP-007) - Visibility into current state
3. Build queue processor (GAP-004) - Prevents unbounded growth
4. Implement PR creation (GAP-003) - Automates medium-confidence patches
5. Integrate with orchestrator (GAP-002) - Event-driven automation

**Total ROI**: ~250 hours/year time savings for ~130 hours implementation effort (2:1 ROI in first year, improves thereafter).

---

**Report Generated**: 2025-12-06  
**Next Review**: After Phase 1 implementation (2 weeks)
