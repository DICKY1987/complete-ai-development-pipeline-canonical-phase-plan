---
doc_id: DOC-GUIDE-README-507
---

# Phase 6 – Error Analysis, Auto-Fix & Escalation

**Purpose**: Detect errors, classify, auto-fix, and escalate as needed.

## Phase Contents

Located in: `phase6_error_recovery/`

- `error/` - Error engine and 21 error detection/fix plugins
  - `error/engine/` - Error detection and orchestration
  - `error/plugins/` - Language-specific and cross-cutting plugins
  - `error/shared/` - Shared utilities
- `README.md` - This file

## Current Components

### Error Engine (`error/engine/`)
- `error_engine.py` - Main error engine ⚠️ (SHIM - imports from UET framework)
- `error_state_machine.py` - Error lifecycle states ✅
- `error_context.py` - Error context capture ✅
- `pipeline_engine.py` - Error pipeline orchestration ✅
- `plugin_manager.py` - Plugin discovery/loading ✅
- `file_hash_cache.py` - Change detection ✅

### Error Plugins (`error/plugins/`) - 21 Plugins ✅
**Python:**
- python_ruff/, python_mypy/, python_pylint/, python_pyright/
- python_bandit/, python_safety/
- python_black_fix/, python_isort_fix/

**JavaScript:**
- js_eslint/, js_prettier_fix/

**Markdown:**
- md_markdownlint/, md_mdformat_fix/

**Other:**
- yaml_yamllint/, powershell_pssa/
- semgrep/, gitleaks/
- path_standardizer/, test_runner/
- codespell/, json_jq/

### Shared Utilities (`error/shared/`)
- Common error handling functions
- Plugin base classes and utilities

### Supporting Components (`core/engine/resilience/`)
Located in cross-cutting `core/` directory:
- `circuit_breaker.py` - Circuit breaker (CLOSED/OPEN/HALF_OPEN) ✅
- `retry.py` - Exponential backoff, retry logic ✅
- `recovery.py` - Recovery handlers ✅

## Main Operations
- Collect outputs/logs on FAILED/TIMEOUT
- Run error plugins (ruff, mypy, pytest, semgrep, etc.)
- Classify errors (transient vs permanent vs unknown)
- Generate patches for auto-fixable errors
- Apply patches and re-validate
- Circuit breaker protection
- Escalation for manual intervention

## Error Lifecycle States
NEW → ANALYZED → FIXED/VERIFIED/ESCALATED/CIRCUIT_OPEN

## Test Coverage
~50+ tests for plugins and pipeline

## Status
⚠️ Partial (60%) - Engine is a shim; needs full implementation
