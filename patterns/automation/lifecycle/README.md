# Pattern Lifecycle Automation

Automated approval and deployment workflows for patterns.

## Components

- **auto_approval.py**: Automatic approval engine for high-confidence patterns

## Usage

```bash
python auto_approval.py
```

## Configuration

Auto-approval is controlled by `automation/config/detection_config.yaml`:

```yaml
auto_approve_high_confidence: true
detection:
  auto_approval_confidence: 0.75  # 75% threshold
```

## Workflow

1. Scans pending pattern candidates
2. Checks confidence score against threshold
3. Validates spec completeness
4. Deploys approved patterns to `specs/`
5. Updates pattern registry
6. Logs approval decisions
