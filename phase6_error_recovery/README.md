# Phase 6 – Error Analysis, Auto-Fix & Escalation

**Purpose**: Detect errors, classify, auto-fix, and escalate as needed.

## Current Components
- See `error/` for error engine and plugins

## Main Operations
- Collect outputs/logs on FAILED/TIMEOUT
- Run error plugins (ruff, mypy, pytest, semgrep, etc.)
- Classify errors (transient vs permanent vs unknown)
- Generate patches for auto-fixable errors
- Apply patches and re-validate
- Circuit breaker protection
- Escalation for manual intervention

## Related Code
- `error/engine/error_engine.py`
- `error/plugins/*` - per-language and cross-cutting plugins
- `plugin_manager.py`, `error_state_machine.py`
