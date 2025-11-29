# Automation Detectors

**Purpose**: Anti-pattern and error detection scripts.

**Status**: Active

---

## Contents

| Script | Description |
|--------|-------------|
| `execution_detector.py` | Detect patterns in execution logs |
| `file_pattern_miner.py` | Mine patterns from file operations |
| `anti_pattern_detector.py` | Detect anti-patterns |
| `error_learner.py` | Learn from error patterns |
| `multi_ai_log_miner.py` | Mine patterns from multi-AI logs |

---

## Usage

```bash
# Run execution detector
python execution_detector.py --log execution.log

# Run anti-pattern detector
python anti_pattern_detector.py --db ../../metrics/pattern_automation.db

# Mine file patterns
python file_pattern_miner.py --path /path/to/analyze
```

---

## Detection Capabilities

### execution_detector.py
- Identifies recurring execution patterns
- Suggests pattern candidates

### anti_pattern_detector.py
- Detects known anti-patterns
- Flags potential issues

### error_learner.py
- Learns from execution failures
- Builds error knowledge base

### file_pattern_miner.py
- Analyzes file operations
- Discovers file-based patterns

### multi_ai_log_miner.py
- Processes logs from multiple AI tools
- Extracts cross-tool patterns

---

## Configuration

See `../config/detection_config.yaml` for detector settings.

---

## Related

- `../config/` - Configuration files
- `../analyzers/` - Performance analyzers
- `../../metrics/` - Pattern database
