# Error Automation Module

**Status**: Phase 1 Complete (Foundation)
**Version**: 1.0.0
**DOC_ID**: DOC-ERROR-AUTO-README-001

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
python scripts/run_error_automation.py apply fix.patch \
  --auto-merge-threshold 0.98 \
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

## Phase 1 Features (Implemented)

### ✅ CLI Entry Point
- `scripts/run_error_automation.py`
- Type-safe input validation (EXEC-001)
- Clear error messages
- Exit codes for automation

### ✅ Queue Processor
- `error/automation/queue_processor.py`
- Atomic queue updates (EXEC-004)
- Batch validation (EXEC-002)
- Health metrics

### ✅ Monitoring & Metrics
- `error/automation/metrics.py`
- Time-based analysis
- Queue health tracking
- Daily breakdown support

### ✅ Documentation
- This README
- Inline code documentation
- Usage examples

## Phase 2 Features (Planned)

### PR Creation
- GitHub API integration
- Auto-merge enablement
- Confidence metrics in PR body

### Orchestrator Integration
- Event-driven automation
- Task adapter pattern
- State machine updates

### Alerting
- Slack/email notifications
- Queue backlog warnings
- Auto-merge success notifications

## Phase 3 Features (Planned)

### Security Scanning
- pip-audit for dependencies
- bandit for Python code
- Real vulnerability detection

### Comprehensive Testing
- 80%+ test coverage
- Integration tests
- Mock GitHub API

### Retry Logic
- Exponential backoff
- Transient failure recovery
- Circuit breaker patterns

### Coverage Checks
- Real coverage delta measurement
- Pytest-cov integration
- Threshold enforcement

## Troubleshooting

### CLI Not Found
```bash
# Use full path
python C:\path\to\scripts\run_error_automation.py status

# Or add to PATH
```

### Module Import Errors
```bash
# Verify __init__.py files exist
ls error/__init__.py
ls error/automation/__init__.py
ls error/engine/__init__.py

# Run from project root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
python scripts/run_error_automation.py status
```

### Queue Not Processing
```bash
# Check queue file exists
ls .state/manual_review_queue.jsonl

# Verify format
cat .state/manual_review_queue.jsonl | jq .

# List with debug
python -c "
from error.automation.queue_processor import ReviewQueueProcessor
proc = ReviewQueueProcessor()
print(proc.list_pending())
"
```

### Metrics Show Zero
```bash
# Check decision log exists
ls .state/patch_decisions.jsonl

# Create test entry
echo '{"timestamp":"2025-12-06T10:00:00Z","decision":"auto_merge","confidence":{"overall":0.95}}' >> .state/patch_decisions.jsonl

# Verify
python scripts/run_error_automation.py status
```

## Development

### Running Tests
```bash
# Run all error automation tests (Phase 3)
pytest tests/error/ -v

# Run with coverage
pytest tests/error/ --cov=error.automation --cov-report=term
```

### Adding New Features
1. Follow EXEC execution patterns
2. Add tests in `tests/error/`
3. Update this README
4. Document in code with DOC_ID

### Code Style
- Python 3.11+
- Type hints required
- Docstrings for public methods
- EXEC patterns documented

## Integration

### With Core Orchestrator (Phase 2)
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

### Event Bus (Phase 2)
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

## Safety Features

### Worktree Isolation (Phase 1+)
All validation runs in isolated git worktree:
- No impact on main working tree
- Automatic cleanup after validation
- Parallel validation possible

### Atomic Operations (Phase 1)
- Queue updates use temp file + atomic rename
- No partial updates on failure
- Crash-safe state persistence

### Rollback Support (Phase 1+)
All auto-merged patches logged:
```bash
# View recent auto-merges
grep '"decision":"auto_merge"' .state/patch_decisions.jsonl | tail -10

# Revert last auto-merge
git revert HEAD
```

## References
- [Gap Analysis](../../DEVELOPMENT_TEMP_DOCS/ERROR_AUTOMATION_GAP_ANALYSIS.md)
- [Phase Plan](../../DEVELOPMENT_TEMP_DOCS/PHASE_PLAN_ERROR_AUTOMATION.md)
- [CI Path Standards](../../docs/DOC_governance/DOC_CI_PATH_STANDARDS.md)

## Changelog

### v1.0.0 (2025-12-06) - Phase 1 Complete
- ✅ CLI entry point with type-safe validation
- ✅ Queue processor with atomic updates
- ✅ Monitoring & metrics
- ✅ Documentation

### Future Releases
- v1.1.0 - Phase 2 (PR creation, orchestrator integration, alerting)
- v1.2.0 - Phase 3 (Security scanning, comprehensive tests, retry logic)
- v2.0.0 - Full autonomous operation

---

**Status**: Phase 1 COMPLETE ✅
**Next**: Phase 2 implementation (48 hours)
**Time Saved**: 8-10 hours/week after full deployment
