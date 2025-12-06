# Phase Plan: Error Automation Implementation
# EXEC-ERROR-AUTO-001: Complete Error Recovery Automation

**Status**: READY FOR EXECUTION  
**Risk Level**: MEDIUM (introduces automation, requires testing)  
**Total Time**: 128 hours (~3-4 weeks for 1 developer, ~2 weeks for 2 developers)  
**Expected Outcome**: 60+ hours/month saved, 70% of error patches auto-deployed  
**Pattern**: EXEC-002 (Batch Implementation) + EXEC-004 (Atomic Operations)

---

## 0. Template Parameters

### Project Configuration
```yaml
PROJECT_ROOT: "C:\\Users\\richg\\ALL_AI\\Complete AI Development Pipeline – Canonical Phase Plan"
TARGET_DIRECTORY: "error/"
OUTPUT_DIRECTORY: "DEVELOPMENT_TEMP_DOCS/error_automation_deliverables"
STATE_DIRECTORY: ".state"

# Critical files that must not be modified without review
CRITICAL_FILES:
  - "error/automation/patch_applier.py"  # Core automation logic
  - "error/engine/recovery_validator.py"  # Contract validation
  - "core/engine/orchestrator.py"        # Main orchestrator
  - "core/engine/executor.py"            # Task executor
  - ".github/workflows/quality-gates.yml" # CI/CD pipeline
  - ".state/orchestration.db"            # State database

# Test requirements
TEST_COMMAND: "pytest -q tests/error/"
TEST_TIMEOUT: 300  # 5 minutes
COVERAGE_THRESHOLD: 70

# Automation thresholds (start conservative)
AUTO_MERGE_THRESHOLD: 0.95  # Only perfect scores auto-merge
PR_THRESHOLD: 0.80          # Medium confidence creates PR
MANUAL_REVIEW_THRESHOLD: 0.60  # Below this requires manual review
```

---

## 1. Executive Summary

### Mission
Transform error automation from a library-only, manually-invoked system into a **fully autonomous, event-driven error recovery pipeline** that detects, validates, and deploys error fixes with minimal human intervention.

### Current State (Manual)
- **Automation**: 30% (validation only)
- **Manual time**: 15-20 hours/week
- **MTTR**: 2-4 days
- **Auto-merged patches**: 0%
- **Monitoring**: None

### Target State (Automated)
- **Automation**: 80% (end-to-end)
- **Manual time**: 2-3 hours/week
- **MTTR**: <4 hours
- **Auto-merged patches**: 70%
- **Monitoring**: Real-time dashboard + alerts

### ROI
- **Time savings**: 60+ hours/month
- **Implementation**: 128 hours
- **Payback**: 2 months
- **First year**: 2:1 ROI (improves annually)

---

## 2. Pre-Conditions & Safety Principles

### 2.1 Version Control Requirements
```bash
# Must be on clean working tree
git status

# Create backup branch
git checkout -b backup/exec-error-auto-001-$(date +%Y%m%d)
git push -u origin backup/exec-error-auto-001-$(date +%Y%m%d)

# Create feature branch
git checkout main
git checkout -b feature/error-automation-implementation
```

### 2.2 Environment Setup
```bash
# Verify Python environment
python --version  # Must be 3.11+

# Install dependencies
pip install PyGithub pip-audit bandit coverage

# Verify existing tests pass
pytest -q tests/error/
```

### 2.3 State Backup
```bash
# Backup state files
mkdir -p .state/backups/exec-error-auto-001
cp .state/patch_decisions.jsonl .state/backups/exec-error-auto-001/ 2>/dev/null || true
cp .state/manual_review_queue.jsonl .state/backups/exec-error-auto-001/ 2>/dev/null || true
cp .state/orchestration.db .state/backups/exec-error-auto-001/ 2>/dev/null || true
```

### 2.4 Rollback Strategy
```bash
# Emergency rollback command (bookmark this)
git checkout main && git branch -D feature/error-automation-implementation

# Restore state files
cp .state/backups/exec-error-auto-001/* .state/
```

---

## 3. Implementation Phases

### Overview
```
Phase 1: Quick Wins (Week 1-2)     → 40 hours → 8-10 hours/week saved
Phase 2: High Impact (Week 3-6)    → 48 hours → +10-12 hours/week saved
Phase 3: Quality (Week 7-10)       → 40 hours → Reduced false positives
```

---

## Phase 1: Quick Wins & Foundation (40 hours)

**Execution Pattern**: EXEC-002-BATCH-VALIDATION + EXEC-004-ATOMIC-OPERATIONS  
**Risk**: LOW  
**Time**: 40 hours (Week 1-2)  
**Deliverables**: CLI, monitoring, queue processor, documentation

---

### Task 1.1: Create CLI Entry Point (8 hours)

#### Pattern: EXEC-001-TYPE-SAFE-OPERATIONS

**File**: `scripts/run_error_automation.py`

```python
#!/usr/bin/env python3
"""Error automation orchestrator CLI

EXECUTION PATTERN: EXEC-001 (Type-Safe Operations)
- All inputs validated
- Clear error messages
- Exit codes indicate success/failure
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

# Section-based imports (follows CI_PATH_STANDARDS.md)
from error.automation.patch_applier import PatchApplier
from error.automation.queue_processor import ReviewQueueProcessor
from error.automation.metrics import ErrorAutomationMetrics


def validate_patch_path(path_str: str) -> Path:
    """Validate patch file exists and is readable."""
    path = Path(path_str)
    if not path.exists():
        raise ValueError(f"Patch file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if path.suffix not in ['.patch', '.diff']:
        raise ValueError(f"Invalid patch file extension: {path.suffix}")
    return path


def cmd_apply_patch(args: argparse.Namespace) -> int:
    """Apply and validate patch with confidence scoring."""
    try:
        patch_path = validate_patch_path(args.patch_path)
        
        applier = PatchApplier(
            repo_path=Path.cwd(),
            auto_merge_threshold=args.auto_merge_threshold,
            pr_threshold=args.pr_threshold
        )
        
        print(f"Validating patch: {patch_path}")
        result = applier.apply_with_validation(patch_path)
        
        # Display results
        print(f"\n{'='*60}")
        print(f"Decision: {result['decision']}")
        print(f"Confidence: {result['confidence']['overall']:.1%}")
        print(f"{'='*60}")
        
        # Detailed breakdown
        conf = result['confidence']
        print(f"\nValidation Breakdown:")
        print(f"  Tests:       {'✅' if conf['tests_passed'] == 1.0 else '❌'} {conf['tests_passed']:.1%}")
        print(f"  Linting:     {'✅' if conf['lint_passed'] == 1.0 else '⚠️'} {conf['lint_passed']:.1%}")
        print(f"  Type Check:  {'✅' if conf['type_check_passed'] == 1.0 else '⚠️'} {conf['type_check_passed']:.1%}")
        print(f"  Security:    {'✅' if conf['security_scan_passed'] == 1.0 else '❌'} {conf['security_scan_passed']:.1%}")
        print(f"  Coverage:    {'✅' if conf['coverage_maintained'] >= 0.7 else '⚠️'} {conf['coverage_maintained']:.1%}")
        
        # Action taken
        action = result['action_taken']
        print(f"\nAction: {action.get('status', 'unknown')}")
        if 'message' in action:
            print(f"  {action['message']}")
        
        # Exit code: 0 = success (merged or queued), 1 = rejected
        return 0 if result['decision'] != 'rejected' else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_process_queue(args: argparse.Namespace) -> int:
    """Process manual review queue."""
    try:
        processor = ReviewQueueProcessor()
        
        if args.action == 'list':
            pending = processor.list_pending(min_confidence=args.min_confidence or 0.0)
            
            if not pending:
                print("No pending reviews.")
                return 0
            
            print(f"\n{'='*80}")
            print(f"Manual Review Queue ({len(pending)} items)")
            print(f"{'='*80}\n")
            
            for i, entry in enumerate(pending, 1):
                print(f"{i}. Patch: {entry['patch_path']}")
                print(f"   Confidence: {entry['confidence']['overall']:.1%}")
                print(f"   Queued: {entry['queued_at']}")
                print()
            
            return 0
            
        elif args.action == 'approve':
            if not args.patch_id:
                print("Error: --patch-id required for approve action", file=sys.stderr)
                return 1
            
            result = processor.approve(args.patch_id)
            print(f"Approved: {args.patch_id}")
            print(f"Next steps: {result['next_steps']}")
            return 0
            
        elif args.action == 'reject':
            if not args.patch_id:
                print("Error: --patch-id required for reject action", file=sys.stderr)
                return 1
            
            reason = args.reason or "No reason provided"
            result = processor.reject(args.patch_id, reason)
            print(f"Rejected: {args.patch_id}")
            print(f"Reason: {reason}")
            return 0
        
        else:
            print(f"Unknown action: {args.action}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show error automation status and metrics."""
    try:
        metrics = ErrorAutomationMetrics()
        data = metrics.get_metrics(days=args.days)
        
        print(f"\n{'='*80}")
        print(f"Error Automation Status (Last {args.days} Days)")
        print(f"{'='*80}\n")
        
        print(f"Patches Processed: {data['total_patches']}")
        print(f"  ✅ Auto-merged:    {data['auto_merged']} ({data['auto_merged']/max(data['total_patches'],1)*100:.1f}%)")
        print(f"  🔄 PR created:     {data['pr_created']} ({data['pr_created']/max(data['total_patches'],1)*100:.1f}%)")
        print(f"  👁️  Manual review:  {data['manual_review']} ({data['manual_review']/max(data['total_patches'],1)*100:.1f}%)")
        print(f"  ❌ Rejected:       {data['rejected']} ({data['rejected']/max(data['total_patches'],1)*100:.1f}%)")
        
        print(f"\nAverage Confidence: {data['avg_confidence']:.1%}")
        
        print(f"\n{'='*80}")
        print(f"Manual Review Queue")
        print(f"{'='*80}\n")
        print(f"Pending Reviews: {data['pending_reviews']}")
        
        if data['pending_reviews'] > 0:
            age = data['review_queue_age_hours']
            print(f"Oldest Review: {age:.1f} hours ago")
            
            if age > 72:
                print("⚠️  WARNING: Reviews older than 3 days detected!")
            elif age > 24:
                print("⚠️  NOTICE: Reviews older than 1 day detected")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Error recovery automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply a patch with validation
  %(prog)s apply path/to/fix.patch
  
  # List pending manual reviews
  %(prog)s process-queue --action list
  
  # Approve a patch for merge
  %(prog)s process-queue --action approve --patch-id path/to/fix.patch
  
  # View automation status
  %(prog)s status --days 7
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Apply patch command
    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply and validate patch'
    )
    apply_parser.add_argument(
        'patch_path',
        type=str,
        help='Path to patch file (.patch or .diff)'
    )
    apply_parser.add_argument(
        '--auto-merge-threshold',
        type=float,
        default=0.95,
        help='Confidence threshold for auto-merge (default: 0.95)'
    )
    apply_parser.add_argument(
        '--pr-threshold',
        type=float,
        default=0.80,
        help='Confidence threshold for PR creation (default: 0.80)'
    )
    
    # Process queue command
    queue_parser = subparsers.add_parser(
        'process-queue',
        help='Process manual review queue'
    )
    queue_parser.add_argument(
        '--action',
        choices=['list', 'approve', 'reject'],
        required=True,
        help='Queue action to perform'
    )
    queue_parser.add_argument(
        '--patch-id',
        type=str,
        help='Patch identifier (required for approve/reject)'
    )
    queue_parser.add_argument(
        '--reason',
        type=str,
        help='Rejection reason (optional for reject action)'
    )
    queue_parser.add_argument(
        '--min-confidence',
        type=float,
        help='Minimum confidence to display (list action only)'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show error automation status'
    )
    status_parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to analyze (default: 7)'
    )
    
    args = parser.parse_args()
    
    # Route to command handler
    if args.command == 'apply':
        return cmd_apply_patch(args)
    elif args.command == 'process-queue':
        return cmd_process_queue(args)
    elif args.command == 'status':
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
```

**Validation**:
```bash
# Test CLI exists and runs
python scripts/run_error_automation.py --help

# Test status command (should work even with no data)
python scripts/run_error_automation.py status

# Expected: Status summary with 0 patches processed
```

**Exit Criteria**:
- ✅ CLI runs without errors
- ✅ `--help` displays usage information
- ✅ All subcommands (apply, process-queue, status) are callable
- ✅ Type validation catches invalid inputs

---

### Task 1.2: Implement Queue Processor (16 hours)

#### Pattern: EXEC-002-BATCH-VALIDATION

**File**: `error/automation/queue_processor.py`

```python
"""Manual review queue processor

EXECUTION PATTERN: EXEC-002 (Batch Validation)
- Processes queue entries in batches
- Validates state before updates
- Atomic file operations
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import tempfile
import shutil


class ReviewQueueProcessor:
    """Manages manual review queue for low-confidence patches"""
    
    def __init__(self, queue_path: Optional[Path] = None):
        self.queue_path = queue_path or Path(".state/manual_review_queue.jsonl")
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
    
    def list_pending(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """List pending reviews, optionally filtered by min confidence.
        
        Pattern: EXEC-002 - Batch read with validation
        """
        if not self.queue_path.exists():
            return []
        
        pending = []
        
        with open(self.queue_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                    
                    # Validate entry structure
                    self._validate_entry(entry, line_num)
                    
                    # Filter by status and confidence
                    if entry.get('status') != 'processed':
                        if entry['confidence']['overall'] >= min_confidence:
                            pending.append(entry)
                            
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON at line {line_num}: {e}")
                except KeyError as e:
                    print(f"Warning: Missing key at line {line_num}: {e}")
        
        # Sort by confidence descending
        pending.sort(key=lambda x: x['confidence']['overall'], reverse=True)
        return pending
    
    def approve(self, patch_path: str) -> Dict[str, Any]:
        """Approve a patch for manual merge.
        
        Pattern: EXEC-004 - Atomic update operation
        """
        self._update_status(patch_path, 'approved', {
            'approved_at': datetime.now(timezone.utc).isoformat(),
            'approved_by': os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        })
        
        return {
            'status': 'approved',
            'next_steps': f"Apply patch: git apply {patch_path}"
        }
    
    def reject(self, patch_path: str, reason: str) -> Dict[str, Any]:
        """Reject a patch.
        
        Pattern: EXEC-004 - Atomic update operation
        """
        self._update_status(patch_path, 'rejected', {
            'rejected_at': datetime.now(timezone.utc).isoformat(),
            'rejected_by': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'reason': reason
        })
        
        return {'status': 'rejected'}
    
    def get_queue_metrics(self) -> Dict[str, Any]:
        """Get queue health metrics."""
        pending = self.list_pending()
        
        if not pending:
            return {
                'total_pending': 0,
                'oldest_age_hours': 0,
                'avg_confidence': 0,
                'health': 'good'
            }
        
        # Calculate oldest age
        oldest_ts = min(
            datetime.fromisoformat(e['queued_at'].replace('Z', '+00:00'))
            for e in pending
        )
        age_hours = (datetime.now(timezone.utc) - oldest_ts).total_seconds() / 3600
        
        # Calculate average confidence
        avg_conf = sum(e['confidence']['overall'] for e in pending) / len(pending)
        
        # Determine health
        health = 'good'
        if len(pending) > 10 or age_hours > 72:
            health = 'critical'
        elif len(pending) > 5 or age_hours > 24:
            health = 'warning'
        
        return {
            'total_pending': len(pending),
            'oldest_age_hours': age_hours,
            'avg_confidence': avg_conf,
            'health': health
        }
    
    def _validate_entry(self, entry: Dict[str, Any], line_num: int) -> None:
        """Validate queue entry structure."""
        required_keys = ['patch_path', 'confidence', 'queued_at']
        for key in required_keys:
            if key not in entry:
                raise KeyError(f"Missing required key '{key}' at line {line_num}")
        
        # Validate confidence structure
        conf_keys = ['overall', 'tests_passed', 'lint_passed']
        for key in conf_keys:
            if key not in entry['confidence']:
                raise KeyError(f"Missing confidence key '{key}' at line {line_num}")
    
    def _update_status(self, patch_path: str, status: str, metadata: Dict) -> None:
        """Update entry status in queue atomically.
        
        Pattern: EXEC-004 - Atomic file operation
        - Read all entries
        - Update in memory
        - Write to temp file
        - Atomic rename
        """
        if not self.queue_path.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_path}")
        
        # Read all entries
        entries = []
        found = False
        
        with open(self.queue_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry['patch_path'] == patch_path:
                    entry['status'] = status
                    entry.update(metadata)
                    found = True
                entries.append(entry)
        
        if not found:
            raise ValueError(f"Patch not found in queue: {patch_path}")
        
        # Write to temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.queue_path.parent,
            prefix='.queue_',
            suffix='.tmp'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry) + '\n')
            
            # Atomic rename
            shutil.move(temp_path, self.queue_path)
            
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise
```

**Validation**:
```bash
# Create test queue entry
mkdir -p .state
echo '{"patch_path":"test.patch","confidence":{"overall":0.75,"tests_passed":1.0,"lint_passed":0.5},"queued_at":"2025-12-06T10:00:00Z"}' >> .state/manual_review_queue.jsonl

# Test list command
python scripts/run_error_automation.py process-queue --action list

# Expected: Shows 1 pending review

# Test approve command
python scripts/run_error_automation.py process-queue --action approve --patch-id test.patch

# Expected: Status updated to approved
```

**Exit Criteria**:
- ✅ Queue entries can be listed
- ✅ Entries can be approved/rejected
- ✅ Status updates are atomic (temp file + rename)
- ✅ Invalid entries are skipped with warnings

---

### Task 1.3: Add Monitoring & Metrics (12 hours)

#### Pattern: EXEC-001-TYPE-SAFE-OPERATIONS

**File**: `error/automation/metrics.py`

```python
"""Error automation metrics and monitoring

EXECUTION PATTERN: EXEC-001 (Type-Safe Operations)
- Strong typing for all metrics
- Validated time ranges
- Defensive parsing
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone


class ErrorAutomationMetrics:
    """Collects and reports error automation metrics"""
    
    def __init__(
        self,
        decision_log: Optional[Path] = None,
        review_queue: Optional[Path] = None
    ):
        self.decision_log = decision_log or Path(".state/patch_decisions.jsonl")
        self.review_queue = review_queue or Path(".state/manual_review_queue.jsonl")
    
    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get metrics for last N days.
        
        Args:
            days: Number of days to analyze (must be > 0)
            
        Returns:
            Dictionary with metrics
        """
        if days < 1:
            raise ValueError("days must be >= 1")
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        decisions = self._load_decisions_since(cutoff)
        
        total = len(decisions)
        
        return {
            'total_patches': total,
            'auto_merged': sum(1 for d in decisions if d.get('decision') == 'auto_merge'),
            'pr_created': sum(1 for d in decisions if d.get('decision') == 'auto_merge_pr'),
            'manual_review': sum(1 for d in decisions if d.get('decision') == 'manual_review'),
            'rejected': sum(1 for d in decisions if d.get('decision') == 'rejected'),
            'avg_confidence': self._calculate_avg_confidence(decisions),
            'pending_reviews': self._count_pending_reviews(),
            'review_queue_age_hours': self._oldest_queue_age_hours(),
        }
    
    def get_daily_breakdown(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get per-day breakdown of metrics."""
        if days < 1:
            raise ValueError("days must be >= 1")
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        decisions = self._load_decisions_since(cutoff)
        
        # Group by date
        by_date: Dict[str, List[Dict]] = {}
        
        for decision in decisions:
            try:
                ts = datetime.fromisoformat(
                    decision['timestamp'].replace('Z', '+00:00')
                )
                date_key = ts.date().isoformat()
                
                if date_key not in by_date:
                    by_date[date_key] = []
                
                by_date[date_key].append(decision)
                
            except (KeyError, ValueError) as e:
                print(f"Warning: Invalid decision entry: {e}")
        
        # Build daily breakdown
        breakdown = []
        for date_str in sorted(by_date.keys()):
            day_decisions = by_date[date_str]
            breakdown.append({
                'date': date_str,
                'total': len(day_decisions),
                'auto_merged': sum(1 for d in day_decisions if d.get('decision') == 'auto_merge'),
                'avg_confidence': self._calculate_avg_confidence(day_decisions)
            })
        
        return breakdown
    
    def _load_decisions_since(self, cutoff: datetime) -> List[Dict]:
        """Load decisions since cutoff time."""
        if not self.decision_log.exists():
            return []
        
        decisions = []
        
        with open(self.decision_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    # Parse timestamp
                    ts_str = entry.get('timestamp')
                    if not ts_str:
                        continue
                    
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    
                    if ts >= cutoff:
                        decisions.append(entry)
                        
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid decision entry: {e}")
        
        return decisions
    
    def _calculate_avg_confidence(self, decisions: List[Dict]) -> float:
        """Calculate average confidence score."""
        if not decisions:
            return 0.0
        
        total = 0.0
        count = 0
        
        for d in decisions:
            try:
                conf = d.get('confidence', {}).get('overall')
                if conf is not None:
                    total += float(conf)
                    count += 1
            except (TypeError, ValueError):
                continue
        
        return total / count if count > 0 else 0.0
    
    def _count_pending_reviews(self) -> int:
        """Count pending manual reviews."""
        if not self.review_queue.exists():
            return 0
        
        count = 0
        
        with open(self.review_queue, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('status') != 'processed':
                        count += 1
                except json.JSONDecodeError:
                    continue
        
        return count
    
    def _oldest_queue_age_hours(self) -> float:
        """Get age of oldest pending review in hours."""
        if not self.review_queue.exists():
            return 0.0
        
        oldest = None
        
        with open(self.review_queue, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    if entry.get('status') != 'processed':
                        ts_str = entry.get('queued_at')
                        if ts_str:
                            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                            if oldest is None or ts < oldest:
                                oldest = ts
                                
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        
        if oldest:
            return (datetime.now(timezone.utc) - oldest).total_seconds() / 3600
        
        return 0.0
```

**Validation**:
```bash
# Test metrics with no data
python scripts/run_error_automation.py status

# Create test decision entry
echo '{"timestamp":"2025-12-06T10:00:00Z","decision":"auto_merge","confidence":{"overall":0.95}}' >> .state/patch_decisions.jsonl

# Test metrics with data
python scripts/run_error_automation.py status

# Expected: Shows 1 patch processed, auto-merged
```

**Exit Criteria**:
- ✅ Metrics calculate correctly from decision log
- ✅ Queue age calculated correctly
- ✅ Invalid entries are skipped gracefully
- ✅ Empty files return zero values (no crashes)

---

### Task 1.4: Create Documentation (4 hours)

**File**: `error/automation/README.md`

```markdown
# Error Automation Module

## Overview
Automated error detection, patch generation, validation, and deployment pipeline.

## Architecture

```
[CI Detects Error] → [Parse Logs] → [Generate Patch] → [Validate in Worktree]
                                                              ↓
                               [High Confidence ≥0.95] → [Auto-merge to main]
                               [Med Confidence ≥0.80]  → [Create PR with auto-merge]
                               [Low Confidence <0.80]  → [Queue for manual review]
```

## CLI Usage

### Apply a Patch
```bash
# Validate and apply patch with default thresholds
python scripts/run_error_automation.py apply path/to/fix.patch

# Custom thresholds
python scripts/run_error_automation.py apply fix.patch \\
  --auto-merge-threshold 0.98 \\
  --pr-threshold 0.85
```

### Manage Review Queue
```bash
# List pending reviews
python scripts/run_error_automation.py process-queue --action list

# List high-confidence reviews only
python scripts/run_error_automation.py process-queue --action list --min-confidence 0.75

# Approve a patch
python scripts/run_error_automation.py process-queue --action approve --patch-id path/to/fix.patch

# Reject a patch
python scripts/run_error_automation.py process-queue --action reject --patch-id path/to/fix.patch --reason "Breaks API contract"
```

### View Status
```bash
# Last 7 days (default)
python scripts/run_error_automation.py status

# Last 30 days
python scripts/run_error_automation.py status --days 30
```

## Configuration

### Confidence Thresholds
- **Auto-merge threshold** (default: 0.95): Patches scoring ≥95% auto-merge to main
- **PR threshold** (default: 0.80): Patches scoring 80-94% create PR with auto-merge
- **Manual review**: Patches scoring <80% queue for human review

### Confidence Calculation
Weighted average of validation checks:
- Tests passed: 40%
- Linting passed: 20%
- Type checking passed: 15%
- Security scan passed: 15%
- Coverage maintained: 10%

## State Files
- `.state/patch_decisions.jsonl` - Decision audit log
- `.state/manual_review_queue.jsonl` - Pending manual reviews
- `.state/error_analysis.json` - Phase 6 contract artifact
- `.state/fix_patches.jsonl` - Patch application ledger

## Integration

### With Core Orchestrator
Error automation integrates via `ErrorAutomationAdapter`:
```python
from core.adapters.error_automation_adapter import ErrorAutomationAdapter
from core.adapters.base import ToolConfig

adapter = ErrorAutomationAdapter(ToolConfig(
    tool_id='error_automation',
    params={'auto_merge_threshold': 0.95}
))

result = adapter.execute({
    'task_type': 'apply_patch',
    'patch_path': 'path/to/fix.patch'
})
```

### Event Bus
Emits events:
- `patch_validation_started` - Validation begins
- `patch_validation_completed` - Validation ends with decision
- `patch_auto_merged` - High-confidence patch merged
- `patch_pr_created` - Medium-confidence PR created
- `patch_queued_for_review` - Low-confidence patch queued

### Contract Validation
Phase 6 (Error Recovery) entry/exit contracts validated via:
```python
from error.engine.recovery_validator import ErrorRecoveryContractValidator

validator = ErrorRecoveryContractValidator()
entry_result = validator.validate_entry()
exit_result = validator.validate_exit()
```

## Monitoring

### Health Metrics
```python
from error.automation.queue_processor import ReviewQueueProcessor

processor = ReviewQueueProcessor()
metrics = processor.get_queue_metrics()

# Returns:
# {
#   'total_pending': 5,
#   'oldest_age_hours': 12.5,
#   'avg_confidence': 0.72,
#   'health': 'warning'  # good | warning | critical
# }
```

### Alerting
Configure Slack webhook:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Alerts trigger when:
- Patch validation fails
- Queue depth >10 items
- Queue age >72 hours

## Safety Features

### Worktree Isolation
All validation runs in isolated git worktree:
- No impact on main working tree
- Automatic cleanup after validation
- Parallel validation possible

### Atomic Operations
- Queue updates use temp file + atomic rename
- No partial updates on failure
- Crash-safe state persistence

### Rollback Support
All auto-merged patches logged:
```bash
# View recent auto-merges
grep '"decision":"auto_merge"' .state/patch_decisions.jsonl | tail -10

# Revert last auto-merge
git revert HEAD
```

## Troubleshooting

### Validation Failures
```bash
# Check validation logs
grep '"decision":"rejected"' .state/patch_decisions.jsonl | jq .

# Common issues:
# - Tests failed: Check .validation_results.tests in decision log
# - Security scan failed: Review .validation_results.security
# - Coverage dropped: Check .validation_results.coverage
```

### Queue Growth
```bash
# Check queue health
python scripts/run_error_automation.py status

# Process oldest items first
python scripts/run_error_automation.py process-queue --action list | head -5

# Bulk approve high-confidence items
# (Manual loop - no bulk approve yet)
```

### Confidence Score Tuning
Edit `error/automation/patch_applier.py`:
```python
# Adjust weights in ConfidenceScore.overall property
weights = {
    'tests': 0.4,      # Increase if tests are highly reliable
    'lint': 0.2,       # Decrease if linting is noisy
    'types': 0.15,
    'security': 0.15,  # Increase for security-critical projects
    'coverage': 0.1
}
```

## Development

### Running Tests
```bash
pytest tests/error/test_patch_applier.py -v
pytest tests/error/test_queue_processor.py -v
pytest tests/error/test_metrics.py -v
```

### Adding New Validation Checks
1. Add method to `PatchApplier`: `_run_<check_name>()`
2. Update `ConfidenceScore` dataclass with new field
3. Update `_validate_patch()` to call new check
4. Adjust weights in `ConfidenceScore.overall`

## References
- [Gap Analysis](../../DEVELOPMENT_TEMP_DOCS/ERROR_AUTOMATION_GAP_ANALYSIS.md)
- [Phase Plan](../../DEVELOPMENT_TEMP_DOCS/PHASE_PLAN_ERROR_AUTOMATION.md)
- [CI Path Standards](../../docs/DOC_governance/DOC_CI_PATH_STANDARDS.md)
```

**Exit Criteria**:
- ✅ README created with complete usage examples
- ✅ All CLI commands documented
- ✅ Architecture diagram included
- ✅ Troubleshooting section added

---

## Phase 1 Validation & Delivery

### Validation Checklist
```bash
# 1. All files created
ls scripts/run_error_automation.py
ls error/automation/queue_processor.py
ls error/automation/metrics.py
ls error/automation/README.md

# 2. CLI works
python scripts/run_error_automation.py --help
python scripts/run_error_automation.py status

# 3. Queue processor works
echo '{"patch_path":"test.patch","confidence":{"overall":0.75,"tests_passed":1.0,"lint_passed":0.5},"queued_at":"2025-12-06T10:00:00Z"}' >> .state/manual_review_queue.jsonl
python scripts/run_error_automation.py process-queue --action list

# 4. Metrics work
echo '{"timestamp":"2025-12-06T10:00:00Z","decision":"auto_merge","confidence":{"overall":0.95}}' >> .state/patch_decisions.jsonl
python scripts/run_error_automation.py status
```

### Commit & Push
```bash
git add scripts/run_error_automation.py
git add error/automation/queue_processor.py
git add error/automation/metrics.py
git add error/automation/README.md

git commit -m "feat(error-automation): Phase 1 - CLI, queue processor, metrics, docs

- Add CLI entry point (scripts/run_error_automation.py)
- Implement queue processor with atomic updates
- Add metrics collection and reporting
- Document all features and usage

Closes GAP-001, GAP-004, GAP-007, GAP-009
Execution Pattern: EXEC-001, EXEC-002, EXEC-004
Time: 40 hours
"

git push -u origin feature/error-automation-implementation
```

### Create PR
```bash
# GitHub CLI
gh pr create --title "Phase 1: Error Automation Foundation" \\
  --body "## Phase 1 Deliverables

✅ CLI Entry Point (GAP-001)
✅ Queue Processor (GAP-004)
✅ Monitoring & Metrics (GAP-007)
✅ Documentation (GAP-009)

## Testing
- All CLI commands tested manually
- Queue operations validated
- Metrics calculation verified

## Next Steps
Phase 2: High-impact automation (PR creation, orchestrator integration)

Closes #<issue-number-for-phase-1>"
```

---

## Phase 2: High Impact Automation (48 hours)

**Coming in next section - would you like me to continue with Phase 2 & 3 details?**

---

## Emergency Procedures

### Rollback Phase 1
```bash
# Revert all changes
git checkout main
git branch -D feature/error-automation-implementation

# Restore state files
cp .state/backups/exec-error-auto-001/* .state/
```

### Disable Auto-Merge
```bash
# Edit scripts/run_error_automation.py
# Change default threshold to 1.0 (never auto-merge)
# --auto-merge-threshold 1.0
```

### Clear Queue
```bash
# Backup first
cp .state/manual_review_queue.jsonl .state/manual_review_queue.jsonl.bak

# Clear queue
> .state/manual_review_queue.jsonl
```

---

**Phase 1 Status**: READY FOR EXECUTION  
**Estimated Time**: 40 hours  
**Expected Savings**: 8-10 hours/week after completion
