---
doc_id: DOC-GUIDE-SPEC-1517
---

# Orchestration Specification

## Purpose
Coordinate EDIT → STATIC → RUNTIME → PIPELINE flow across multiple workstreams.

## Phases
1. **EDIT:** Implement changes per spec/task
2. **STATIC:** Run linters, formatters, type checkers
3. **RUNTIME:** Execute tests
4. **PIPELINE:** Error pipeline with AI-assisted fixes

## Workstream Isolation
- Each workstream runs in separate git worktree
- Independent state tracking per workstream
- Parallel execution across workstreams
- Merge on success, preserve on failure

## Scenarios

### WHEN orchestrator starts workstream
- THEN create isolated worktree for changes
- AND initialize error pipeline context
- AND track workstream_id in database

### WHEN static validation completes
- THEN proceed to runtime tests
- OR fix errors via pipeline if failures detected

### WHEN all phases complete successfully
- THEN merge workstream to main branch
- AND archive workstream context
- AND update status tracking
