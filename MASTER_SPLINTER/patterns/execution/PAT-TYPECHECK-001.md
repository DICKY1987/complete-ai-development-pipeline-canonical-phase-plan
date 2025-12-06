---
doc_id: DOC-PAT-PAT-TYPECHECK-001-332
---

# PAT-TYPECHECK-001: Type Checking

## Purpose
Verify type correctness using the configured type checker.

## Steps
1. Run the type checker specified in `config/tool_profiles.json`.
2. Capture output and return code.
3. Record any type errors for reporting.
4. Continue execution regardless of failures (NO STOP MODE).

## Success Criteria
- Type checker runs to completion.
- Output captured for review.
- No unexpected interruption to the pipeline.
