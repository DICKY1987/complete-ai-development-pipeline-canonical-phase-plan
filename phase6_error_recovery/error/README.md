# error

**Module Path**: `error`  
**Layer**: Domain  
**Status**: Active

## Purpose

Error detection and analysis system with plugin architecture for multiple error types (Python, shell, TypeScript, etc.)

## Contents

- `__init__.py` - File
- `engine/` - Directory
- `plugins/` - Directory
- `shared/` - Directory

## Key Components

- `engine/` - Error detection engine
- `plugins/` - Pluggable error detectors (python_ruff, shell, typescript)
- `shared/` - Shared utilities for error handling


## Dependencies

core.state (for persistence), schema/ (for validation)

## Usage

```python
from error.engine.error_engine import ErrorEngine
engine = ErrorEngine()
errors = engine.detect(log_file="pipeline.log")
```


## Integration Points

Integrates with core.engine for task execution error analysis

## Related Documentation

docs/error_detection_guide.md, ANTI_PATTERN_GUARDS.md

---

**Generated**: 2025-12-02 22:40:27 UTC  
**Framework**: Universal Execution Templates (UET)
