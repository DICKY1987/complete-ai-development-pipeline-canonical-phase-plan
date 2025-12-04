---
doc_id: DOC-GUIDE-SPEC-090
---

# Plugin System Specification

## Purpose
Modular, extensible validation framework supporting multiple languages and tools.

## Plugin Interface
Each plugin must provide:
- `manifest.json` - Metadata (name, version, capabilities, dependencies)
- `plugin.py` or `plugin.ps1` - Executable implementing standard interface
- Operating Contract compliance for error reports

## Current Plugins (as of Phase 07)
- python_ruff - Linting
- python_black_fix - Formatting (autofix capable)
- python_isort_fix - Import sorting (autofix capable)
- python_mypy - Type checking
- python_pyright - Type checking
- python_pylint - Linting
- python_bandit - Security scanning
- python_safety - Dependency vulnerability checks
- echo - Sample/test plugin

## Plugin Execution
- DAG-based ordering (resolve dependencies)
- Parallel execution where possible
- Graceful degradation if tool missing
- Per-file error tracking

## Scenarios

### WHEN a new plugin is added
- THEN it must include manifest.json with valid schema
- AND it must output errors in Operating Contract format
- AND it must be registered in plugin discovery system

### WHEN plugin has autofix capability
- THEN manifest.json must declare "autofix": true
- AND plugin must apply fixes when invoked with --fix flag
- AND fixes must be idempotent (repeatable)
