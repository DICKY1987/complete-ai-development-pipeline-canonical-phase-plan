---
doc_id: DOC-PAT-PAT-LINT-001-327
---

# PAT-LINT-001: Static Linting

## Purpose
Run linting tools to catch style and correctness issues early.

## Steps
1. Use tool configuration from `config/tool_profiles.json`.
2. Run the configured lint command for the current language.
3. Capture and record any findings.
4. Do not halt overall execution on lint failures (NO STOP MODE).

## Success Criteria
- Lint command executes.
- Findings, if any, are captured for reporting.
- Pipeline continues even when lint errors occur.
