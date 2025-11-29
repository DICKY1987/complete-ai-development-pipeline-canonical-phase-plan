# Automation Configuration

**Purpose**: Shared automation configuration and defaults.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `detection_config.yaml` | Configuration for pattern detection |

---

## Configuration Schema

```yaml
# detection_config.yaml
detection:
  min_occurrences: 3          # Minimum occurrences for pattern detection
  confidence_threshold: 0.75  # Auto-approval threshold
  scan_interval: 60           # Seconds between scans

logging:
  level: INFO
  output: ../../metrics/

patterns:
  include: ["*.pattern.yaml"]
  exclude: ["draft_*"]
```

---

## Usage

Configure detectors and analyzers:

```bash
# Use config with detector
python ../detectors/execution_detector.py --config detection_config.yaml
```

---

## Related

- `../detectors/` - Pattern detectors
- `../analyzers/` - Performance analyzers
- `../runtime/` - Runtime components
