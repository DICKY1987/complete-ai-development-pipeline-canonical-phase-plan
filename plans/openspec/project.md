---
doc_id: DOC-GUIDE-PROJECT-432
---

# AI Development Pipeline - Project Conventions

## Overview
Complete AI Development Pipeline using phase-based execution, error pipelines, and plugin-based validation.

## Technology Stack
- **Languages:** Python 3.11+, PowerShell 7+
- **Database:** SQLite (pipeline state)
- **Version Control:** Git with worktrees
- **AI Tools:** Aider, Claude Code, Gemini
- **Testing:** pytest, PowerShell Pester
- **Validation:** Ruff, Black, MyPy, Pyright, Bandit

## Architecture Principles
1. **Deterministic State Machine:** 12 states from S_INIT → S_SUCCESS/S4_QUARANTINE
2. **Plugin-Based Validation:** Modular error detection (MOD_ERROR_PIPELINE)
3. **Multi-Tier AI Escalation:** S1_AIDER → S2_CODEX → S3_CLAUDE
4. **Dual Persistence:** SQLite + JSON file-based storage
5. **Incremental Processing:** Per-file error tracking with caching

## Coding Standards
- Python: PEP 8 via Black, type hints via MyPy
- PowerShell: PSScriptAnalyzer compliant
- Paths: Forward slashes, absolute when possible
- Timestamps: ISO 8601 format
- Error Reports: JSON conforming to Operating Contract schema

## Testing Standards
- Unit tests for all plugins (MOD_ERROR_PIPELINE)
- Integration tests for state machine transitions
- Determinism tests for error engine
- 80%+ code coverage target

## Workflow
1. **EDIT Phase:** Implement changes per spec
2. **STATIC Phase:** Run linters, formatters, type checkers
3. **RUNTIME Phase:** Execute tests
4. **Pipeline Validation:** Error pipeline with AI-assisted fixes