# Automation Directory

**Purpose**: Automation utilities that detect, analyze, and triage pattern execution signals.

**Status**: Active

---

## Contents

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `analyzers/` | Performance analysis scripts (e.g., `performance_analyzer.py`) |
| `config/` | Shared automation configuration and defaults |
| `detectors/` | Anti-pattern and error detectors (`execution_detector.py`, `file_pattern_miner.py`) |
| `generators/` | Pattern generation utilities |
| `integration/` | Orchestrator integration hooks (see `integration/README.md`) |
| `runtime/` | Runtime automation components |
| `tests/` | Test suites for automation modules |

### Key Files

- `__init__.py` - Python package initialization
- `README.yaml` - Machine-readable directory metadata

---

## Usage

Run analyzers and detectors locally to surface performance issues or anti-patterns:

```bash
# Run performance analyzer
python analyzers/performance_analyzer.py

# Run pattern detector
python detectors/execution_detector.py
```

---

## Integration

See `integration/README.md` for orchestrator hook setup instructions.

---

## Related

- `../pattern_event_system/` - Event system for pattern automation
- `../metrics/` - Pattern automation database and SQL scripts
