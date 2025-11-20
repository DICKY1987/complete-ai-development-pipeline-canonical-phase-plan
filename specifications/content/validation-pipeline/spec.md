# Validation Pipeline Specification

## Purpose
Deterministic error detection and AI-assisted remediation system.

## Components
- Error Engine (src/pipeline/error_engine.py)
- State Machine (src/pipeline/error_state_machine.py)
- Service Layer (src/pipeline/error_pipeline_service.py)
- Context Management (src/pipeline/error_context.py)

## State Flow
```
S_INIT → S0_BASELINE_CHECK → S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK
       ↓                                                                ↓
[no errors] ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← [errors cleared]
                                                                       ↓
                                                                S1_AIDER_FIX
                                                                       ↓
                                                                S1_AIDER_RECHECK
                                                                       ↓
                                                            [success] → S_SUCCESS
                                                            [fail] ↓
                                                                S2_CODEX_FIX
                                                                       ↓
                                                                S2_CODEX_RECHECK
                                                                       ↓
                                                            [success] → S_SUCCESS
                                                            [fail] ↓
                                                                S3_CLAUDE_FIX
                                                                       ↓
                                                                S3_CLAUDE_RECHECK
                                                                       ↓
                                                            [success] → S_SUCCESS
                                                            [fail] ↓
                                                                S4_QUARANTINE
```

## Scenarios

### WHEN baseline validation is run
- THEN execute all plugins in DAG order
- AND aggregate errors by tool/category/severity
- AND produce normalized JSON report (Operating Contract schema)

### WHEN mechanical autofixes are available
- THEN apply fixes from autofix-capable plugins (black, isort, prettier)
- AND re-validate to confirm errors cleared
- AND transition to S_SUCCESS if clean

### WHEN AI agent fixes are needed
- THEN escalate through 3-tier system: Aider → Codex → Claude
- AND provide full error context to each agent
- AND re-validate after each fix attempt
- AND track attempts in database

### WHEN all fix attempts fail
- THEN transition to S4_QUARANTINE
- AND create GitHub issue with error details
- AND preserve context for manual review
