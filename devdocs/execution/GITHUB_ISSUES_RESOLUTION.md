# Phase: GitHub Issues Resolution Plan

**Phase ID:** `PHASE-GH-ISSUES-2025-11`  
**Status:** Draft  
**Created:** 2025-11-19  
**Owner:** Development Team  
**Priority:** High (includes 2 P1 issues)

## Overview

This phase plan addresses all 17 open GitHub issues identified in the repository. Issues are categorized by priority and type, with a structured approach to resolution that minimizes disruption to existing functionality while ensuring code quality and workflow stability.

## Objectives

1. **Fix P1 Critical Issues** - Resolve workflow-blocking bugs (#15, #5)
2. **Improve Code Quality** - Address empty except clauses, unused variables, and commented code (#21-28)
3. **Fix Configuration Issues** - Correct tool profiles and path handling (#11, #13, #14)
4. **Improve Script Quality** - Refactor shell patterns and fix portability (#6, #8)
5. **Clean Documentation** - Remove duplicates and align docs with code (#7, #12)

## Issue Categories & Resolution Strategy

### Category 1: P1 Critical Workflow Issues (2 issues)

**Priority:** Immediate  
**Impact:** Blocks execution  
**Target:** Day 1-2

| Issue # | Title | Root Cause | Resolution |
|---------|-------|------------|------------|
| #15 | Fix prompt misses required context variables | Template expects `error_summaries`, `files_scope`, `files_create`, `openspec_change`, `ccpm_issue`, `gate` but `build_fix_prompt()` only provides `error_summary`, `error_details`, `files` | Update `build_fix_prompt()` in `scripts/run_aider_fix.py` to provide all required context variables matching template expectations |
| #5 | OpenSpec conversion crashes without manual files_scope | `bundle_to_workstream()` raises `ValueError` when no file paths inferred, but quickstart docs show running without `--files-scope` flag | Either make `files_scope` optional with sensible defaults, or update `docs/phase-openspec-integration.md` quickstart to include required flag |

### Category 2: Empty Exception Handlers (4 issues)

**Priority:** High  
**Impact:** Poor error handling, debugging difficulty  
**Target:** Day 2-3

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #28 | Empty except clause | TBD from PR #20 | Add explanatory comment or proper error handling |
| #27 | Empty except clause | TBD from PR #20 | Add explanatory comment or proper error handling |
| #26 | Empty except clause | TBD from PR #20 | Add explanatory comment or proper error handling |
| #25 | Empty except clause | TBD from PR #20 | Add explanatory comment or proper error handling |

**Action Items:**
- Locate all instances from PR #20
- For each: determine if error should be logged, re-raised, or genuinely ignored
- Add explanatory comments for intentionally ignored exceptions
- Use proper logging for suppressed errors

### Category 3: Code Quality & Unused Variables (3 issues)

**Priority:** Medium  
**Impact:** Code clarity, maintainability  
**Target:** Day 3-4

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #24 | Name 'types' exported in `__all__` but not defined | TBD from PR #20 | Either define `types` or remove from `__all__` |
| #23 | Variable `plugins` not used | TBD from PR #20 | Remove if truly unused, or use it if intended |
| #22 | Variable `style_only` not used | TBD from PR #20 | Remove if truly unused, or use it if intended |

### Category 4: Commented Code (1 issue)

**Priority:** Medium  
**Impact:** Code clarity  
**Target:** Day 4

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #21 | Commented-out code | TBD from PR #20 | Remove dead code or uncomment and integrate if needed |

### Category 5: Configuration & Metadata (3 issues)

**Priority:** Medium-High  
**Impact:** Tool execution, contract compliance  
**Target:** Day 3-4

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #11 | Missing `--model` argument in aider tool profile | `config/tool_profiles.json` | Either add `--model {model_name}` argument or update `docs/aider_contract.md` to reflect env-var-only model selection |
| #13 | Self-referential IDX mapping entries | TBD from PR #10 | Fix mapping generation to avoid circular references |
| #12 | `run_aider_fix` missing metadata field extraction | `scripts/run_aider_fix.py` | Extract and use metadata fields as documented |

### Category 6: Path & Portability Issues (2 issues)

**Priority:** Medium  
**Impact:** Cross-platform compatibility  
**Target:** Day 4-5

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #14 | Hardcoded Windows path missing backslashes | TBD from PR #10 | Use `pathlib.Path` or `os.path.join` for platform-independent paths |
| #6 | Script uses /tmp (non-portable) | TBD from PR #3 | Use `tempfile.mkdtemp()` or project-specific temp directory |

### Category 7: Shell Script Quality (1 issue)

**Priority:** Low-Medium  
**Impact:** Readability, maintainability  
**Target:** Day 5

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #8 | Complex double negation pattern `${cmd##*[![:space:]]*}` | TBD from PR #3 | Extract to helper function `is_empty_or_whitespace()` with comment |

### Category 8: Documentation (1 issue)

**Priority:** Low  
**Impact:** Documentation clarity  
**Target:** Day 5

| Issue # | Title | File | Resolution |
|---------|-------|------|------------|
| #7 | Duplicated repository layout section | TBD from PR #3 | Remove duplicate section |

## Phase Tasks & Checklist

### Task 1: Identify Affected Files
- [ ] Review PR #20 to identify files with issues #21-28
- [ ] Review PR #10 to identify files with issues #11-15
- [ ] Review PR #3 to identify files with issues #5-8
- [ ] Create file-to-issue mapping document

### Task 2: Fix P1 Critical Issues
- [ ] **Issue #15**: Update `build_fix_prompt()` context
  - [ ] Add `error_summaries` (list format of errors)
  - [ ] Add `files_scope`, `files_create` lists
  - [ ] Add `openspec_change`, `ccpm_issue`, `gate` variables
  - [ ] Test template rendering with new context
  - [ ] Run FIX mode end-to-end test
- [ ] **Issue #5**: Fix OpenSpec conversion
  - [ ] Review `bundle_to_workstream()` requirements
  - [ ] Make `files_scope` optional with defaults OR
  - [ ] Update quickstart docs to require `--files-scope`
  - [ ] Test with bundled `test-001` example
  - [ ] Update acceptance criteria if needed

### Task 3: Fix Exception Handlers
- [ ] Locate all 4 empty except clauses from PR #20
- [ ] For each clause:
  - [ ] Determine error handling strategy
  - [ ] Add logging or comments
  - [ ] Update error handling if needed
- [ ] Run linting to verify compliance

### Task 4: Fix Code Quality Issues
- [ ] **Issue #24**: Fix `types` in `__all__`
  - [ ] Verify if `types` should be defined
  - [ ] Either define or remove from `__all__`
- [ ] **Issue #23**: Remove or use `plugins` variable
- [ ] **Issue #22**: Remove or use `style_only` variable
- [ ] **Issue #21**: Remove commented-out code
- [ ] Run linting and verify no regressions

### Task 5: Fix Configuration Issues
- [ ] **Issue #11**: Fix aider tool profile
  - [ ] Review `docs/aider_contract.md` specification
  - [ ] Add `--model {model_name}` to profile OR
  - [ ] Update contract to reflect env-var approach
  - [ ] Test aider invocation
- [ ] **Issue #13**: Fix self-referential IDX mappings
  - [ ] Review mapping generation logic
  - [ ] Add validation to prevent cycles
  - [ ] Regenerate mappings
- [ ] **Issue #12**: Extract metadata in `run_aider_fix`
  - [ ] Review required metadata fields
  - [ ] Implement extraction
  - [ ] Test metadata usage

### Task 6: Fix Path & Portability Issues
- [ ] **Issue #14**: Fix hardcoded Windows path
  - [ ] Replace with `pathlib.Path`
  - [ ] Test on Windows
- [ ] **Issue #6**: Replace /tmp usage
  - [ ] Use `tempfile.mkdtemp()`
  - [ ] Ensure cleanup on exit
  - [ ] Test cross-platform

### Task 7: Refactor Shell Script
- [ ] **Issue #8**: Extract whitespace check
  - [ ] Create `is_empty_or_whitespace()` helper
  - [ ] Add explanatory comment
  - [ ] Replace pattern usage

### Task 8: Clean Documentation
- [ ] **Issue #7**: Remove duplicate layout section
  - [ ] Identify canonical version
  - [ ] Remove duplicate
  - [ ] Verify formatting consistency

### Task 9: Validation & Testing
- [ ] Run full test suite: `pytest -q`
- [ ] Run workstream validation: `python scripts/validate_workstreams.py`
- [ ] Run authoring validation: `python scripts/validate_workstreams_authoring.py`
- [ ] Test P1 workflows end-to-end:
  - [ ] FIX mode execution (issue #15)
  - [ ] OpenSpec conversion (issue #5)
- [ ] Run bootstrap script: `pwsh scripts/bootstrap.ps1`
- [ ] Verify no new linting errors

### Task 10: Documentation Updates
- [ ] Update `CURRENTREPOSTATE.md` with resolution status
- [ ] Update `docs/ARCHITECTURE.md` if contracts changed
- [ ] Update quickstart guides if workflow changed
- [ ] Add issue resolution notes to CHANGELOG

### Task 11: Issue Closure
- [ ] Create PR with all fixes
- [ ] Reference all 17 issues in PR description
- [ ] Request review
- [ ] Merge and close issues

## Success Criteria

1. **All P1 Issues Resolved**
   - FIX mode executes without template errors
   - OpenSpec quickstart works as documented
   
2. **Code Quality Improved**
   - No empty except clauses without comments
   - No unused variables
   - No commented-out code
   
3. **Configuration Aligned**
   - Tool profiles match documented contracts
   - No circular IDX references
   - Metadata properly extracted
   
4. **Portability Enhanced**
   - No hardcoded paths
   - Cross-platform temp file handling
   
5. **All Tests Pass**
   - `pytest -q` returns 0 exit code
   - All validation scripts succeed
   - No new linting errors
   
6. **All 17 Issues Closed**
   - Each issue linked to resolving commit
   - Verification steps documented

## Timeline

| Day | Focus | Issues |
|-----|-------|--------|
| 1 | File identification, P1 fix planning | All |
| 2 | P1 fixes (#15, #5) | #15, #5 |
| 3 | Exception handlers, config issues | #25-28, #11-13 |
| 4 | Code quality, metadata, paths | #21-24, #12, #14 |
| 5 | Portability, scripts, docs | #6, #8, #7 |
| 6 | Testing, validation, documentation | All |
| 7 | PR review, issue closure | All |

**Estimated Duration:** 5-7 days  
**Dependencies:** None (self-contained)  
**Risks:** 
- PR #20, #10, #3 may have additional unreported issues
- Template changes may affect other workflows
- Path refactoring may expose platform-specific bugs

## Exit Criteria

- [ ] All 17 GitHub issues closed
- [ ] All tests passing
- [ ] No new linting errors
- [ ] Documentation updated
- [ ] Changes reviewed and merged
- [ ] CURRENTREPOSTATE.md updated

## Notes

- This phase is remediation work and should not introduce new features
- Follow minimal-change principle: fix only what's broken
- Maintain backward compatibility where possible
- Document any breaking changes in CHANGELOG
- Consider adding regression tests for P1 issues

## Related Documents

- `docs/aider_contract.md` - Aider integration contract
- `docs/phase-openspec-integration.md` - OpenSpec quickstart
- `Canonical_Phase_Plan_Checklist.md` - Main phase checklist
- `CURRENTREPOSTATE.md` - Current repository state

## Issue References

**P1 Critical:**
- #15: https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan/issues/15
- #5: https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan/issues/5

**Code Quality (PR #20):**
- #28, #27, #26, #25: Empty except clauses
- #24: Undefined 'types' in __all__
- #23: Unused 'plugins' variable
- #22: Unused 'style_only' variable
- #21: Commented-out code

**Configuration (PR #10):**
- #14: Hardcoded Windows path
- #13: Self-referential IDX mappings
- #12: Missing metadata extraction
- #11: Missing --model argument

**Scripts/Docs (PR #3):**
- #8: Complex shell pattern
- #7: Duplicate documentation
- #6: Non-portable /tmp usage
