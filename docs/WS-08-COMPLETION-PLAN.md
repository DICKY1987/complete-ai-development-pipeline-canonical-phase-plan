# WS-08 Refactor Completion Plan

**Status**: In Progress
**Last Updated**: 2025-01-17
**Owner**: Pipeline Team

## Executive Summary

WS-08 refactored the prompt/aider subsystem, moving files from `src/pipeline/` to `aider/`. This plan addresses the **4 regression bugs discovered** during testing, documents fixes applied, and outlines remaining validation work.

## Background

### WS-08 Refactor Scope
- **Moved**: `src/pipeline/prompts.py` → `aider/engine.py`
- **Moved**: `src/pipeline/prompt_templates/` → `aider/templates/`
- **Created**: Compatibility shims in `src/pipeline/prompts.py`
- **Updated**: Import paths across codebase

### Regression Bugs Discovered (4 total)

| # | Bug | Status | Commit |
|---|-----|--------|--------|
| 1 | Template naming mismatch | ✅ Fixed | `03db88c` |
| 2 | Function signature incompatibility | ✅ Fixed | `6bbe22a` |
| 3 | Context key mismatch (`cwd` → `worktree_path`) | ✅ Fixed | `6bbe22a` |
| 4 | Template variable mismatch (empty file scope) | ✅ Fixed | `2df28e3` |

---

## Phase 1: Validation & Testing (Current)

**Goal**: Verify all WS-08 regression fixes work end-to-end

### Tasks

#### 1.1 Verify Prompt Rendering
```bash
# Test that prompts render with full context
python -c "
from pathlib import Path
from aider.engine import build_edit_prompt

prompt = build_edit_prompt(
    tasks=['Task 1', 'Task 2'],
    repo_path=Path.cwd(),
    ws_id='test-ws',
    run_id='test-run',
    worktree_path=Path('.worktrees/test'),
    files_scope=['file1.py', 'file2.py'],
    files_create=['new_file.py'],
    acceptance_tests=['pytest -q'],
    openspec_change='TEST-001',
    ccpm_issue='#123',
    gate=1
)
print(prompt)
"
```

**Expected**: Prompt contains all variables (no empty lists/values)

#### 1.2 Test Aider Invocation (Dry Run)
```bash
# Create minimal test workstream bundle
cat > workstreams/ws-test-aider.json <<'EOF'
{
  "id": "ws-test-aider",
  "openspec_change": "TEST",
  "ccpm_issue": "N/A",
  "gate": 0,
  "files_scope": ["README.md"],
  "files_create": [],
  "tasks": ["Add a comment to README.md"],
  "acceptance_tests": ["test -f README.md"],
  "depends_on": [],
  "tool": "aider"
}
EOF

# Run with dry-run (if supported) or check prompt file
python run_ws_wrapper.py --ws-id ws-test-aider --dry-run
```

**Expected**: Prompt file `.worktrees/ws-test-aider/.aider/prompts/edit.txt` contains full context

#### 1.3 Full Pipeline Smoke Test
```bash
# Re-run WS-11 and WS-12 (previously passed acceptance tests)
python run_ws_wrapper.py --ws-id ws-11-spec-docs
python run_ws_wrapper.py --ws-id ws-12-error-shared-utils
```

**Expected**: Both complete successfully (may skip aider step if not needed)

### Acceptance Criteria
- [x] Prompt rendering includes all template variables
- [x] Aider receives files in scope (not empty list)
- [x] WS-11 and WS-12 pass acceptance tests again (dry-run)
- [x] No import errors or module resolution issues

**Duration**: 1-2 hours
**Blockers**: None
**Risk**: Low

---

## Phase 2: WS-10 Completion (Deferred)

**Goal**: Complete WS-10 OpenSpec integration

### Background
WS-10 was skipped due to:
1. Aider taking too long to execute
2. Windows console Unicode encoding issues
3. Initial attempts hit all 4 regression bugs

### Approach Options

#### Option A: Manual Implementation
Execute WS-10 tasks manually without aider:
1. ✅ Already validated: `scripts/generate_spec_index.py` works
2. ✅ Already validated: `scripts/generate_spec_mapping.py` works
3. Create `src/pipeline/openspec_parser.py` manually
4. Create `src/pipeline/openspec_convert.py` manually
5. Update `scripts/generate_workstreams_from_openspec.py`
6. Document in `docs/ccpm-openspec-workflow.md`

**Pros**: Direct control, faster, no aider dependencies
**Cons**: More manual work, doesn't validate aider integration

#### Option B: Retry with Aider (After Fixes)
Now that all 4 regressions are fixed, retry WS-10 with aider:
```bash
python run_ws_wrapper.py --ws-id ws-10-openspec-integration
```

**Pros**: Validates full aider integration pipeline
**Cons**: May still be slow, Unicode issues may persist on Windows

#### Option C: Hybrid Approach
1. Use aider to generate initial implementation
2. Review and refine manually
3. Run acceptance tests to validate

**Pros**: Best of both worlds
**Cons**: More steps

### Recommended: Option A (Manual)
Given previous aider issues and the fact that the work is well-defined, manual implementation is most practical.

### Tasks (Option A)

#### 2.1 Implement OpenSpec Parser
```bash
# Create src/pipeline/openspec_parser.py
# Requirements:
# - Read openspec/ directory structure
# - Parse spec files (markdown + YAML sidecar)
# - Extract change metadata
# - Generate bundle YAML
```

#### 2.2 Implement OpenSpec Converter
```bash
# Create src/pipeline/openspec_convert.py
# Requirements:
# - Convert OpenSpec bundle → workstream JSON
# - Validate against schema/workstream.schema.json
# - Map spec metadata to workstream fields
```

#### 2.3 Update Workstream Generator Script
```bash
# Update scripts/generate_workstreams_from_openspec.py
# - Integrate openspec_parser and openspec_convert
# - Add CLI for interactive conversion
# - Support dry-run mode
```

#### 2.4 Documentation
Update `docs/ccpm-openspec-workflow.md`:
- Document parser and converter
- Provide examples
- Document edge cases

#### 2.5 Run Acceptance Tests
```bash
python -m src.pipeline.openspec_parser --change-id test-001 --generate-bundle
python scripts/generate_workstreams_from_openspec.py --bundle bundles/openspec-test-001.yaml --echo
python scripts/validate_workstreams.py
```

### Acceptance Criteria
- [ ] All acceptance tests pass
- [ ] OpenSpec → Bundle → Workstream round-trip works
- [ ] Documentation complete
- [ ] No schema validation errors

**Duration**: 4-6 hours
**Blockers**: Requires understanding of OpenSpec structure
**Risk**: Medium (new code, complex transformation)

---

## Phase 3: Missing Workstream Bundles

**Goal**: Create missing WS-04, WS-06, WS-13 through WS-17 bundles to unblock WS-18-21

### Background
WS-18-21 were moved to `.deferred/` because they depend on bundles that don't exist yet:
- **WS-18**: Depends on WS-04, WS-13, WS-14
- **WS-19**: Depends on WS-15, WS-16
- **WS-20**: Depends on WS-06, WS-17
- **WS-21**: Depends on earlier CI/infrastructure work

### Tasks

#### 3.1 Analyze Bundle Requirements
```bash
# Read WS-18-21 to understand what they expect from dependencies
for ws in 18 19 20 21; do
  echo "=== WS-$ws dependencies ==="
  jq '.depends_on, .tasks' "workstreams/.deferred/ws-${ws}-*.json"
done
```

#### 3.2 Define Missing Bundle Scopes

**WS-04**: (Inferred from WS-18 dependencies)
- Likely: Infrastructure setup or tooling foundation
- **Action**: Review phase plans to determine scope

**WS-06**: (Inferred from WS-20 dependencies)
- Likely: Documentation or spec work
- **Action**: Review phase plans to determine scope

**WS-13 through WS-17**: (Inferred from WS-18-19 dependencies)
- Likely: Test suite, CI gates, or plugin work
- **Action**: Review phase plans to determine scope

#### 3.3 Create Stub Bundles
For each missing bundle:
```bash
# Template
cat > workstreams/ws-XX-name.json <<'EOF'
{
  "id": "ws-XX-name",
  "openspec_change": "WS-XX",
  "ccpm_issue": "TBD",
  "gate": N,
  "files_scope": [],
  "files_create": [],
  "tasks": ["TODO: Define tasks based on phase plan"],
  "acceptance_tests": [],
  "depends_on": [],
  "tool": "manual",
  "metadata": {
    "notes": "Stub created to unblock WS-18-21"
  }
}
EOF
```

#### 3.4 Move WS-18-21 Back
```bash
# After creating dependencies
mv workstreams/.deferred/ws-*.json workstreams/
python scripts/validate_workstreams.py  # Should pass
```

### Acceptance Criteria
- [ ] All missing bundles created with realistic scope
- [ ] WS-18-21 moved back from `.deferred/`
- [ ] Validation passes (no dependency errors)
- [ ] Phase plan alignment confirmed

**Duration**: 3-4 hours
**Blockers**: Need to review original phase plans for WS-04, 06, 13-17 scope
**Risk**: Medium (scope definition requires context)

---

## Phase 4: Execute Deferred Workstreams

**Goal**: Complete WS-18-21 after dependencies are ready

### Prerequisites
- Phase 3 complete (all dependencies exist)
- WS-04, WS-06, WS-13-17 executed (or marked as done if manual)

### Tasks

#### 4.1 Execute in Dependency Order
```bash
# Determine execution order
python scripts/validate_workstreams.py --show-order

# Execute each workstream
for ws_id in $(python scripts/validate_workstreams.py --show-order | grep "ws-"); do
  python run_ws_wrapper.py --ws-id "$ws_id"
done
```

#### 4.2 Validation
```bash
# Run full test suite
python -m pytest -q

# Check for path standard violations
python scripts/validate_workstreams.py --check-paths

# Verify CI gates
pwsh scripts/test.ps1
```

### Acceptance Criteria
- [ ] WS-18: Infrastructure scripts updated
- [ ] WS-19: Test suite updated
- [ ] WS-20: Documentation mapping complete
- [ ] WS-21: CI gate path standards enforced
- [ ] All acceptance tests pass
- [ ] No regressions in existing functionality

**Duration**: 4-8 hours (depending on complexity)
**Blockers**: Phase 3 completion
**Risk**: Medium-High (cross-cutting changes)

---

## Phase 5: Cleanup & Consolidation

**Goal**: Clean up temporary files and consolidate fixes

### Tasks

#### 5.1 Remove Temporary Files
```bash
# Clean up from debugging sessions
rm -f ws*.log nul pipeline_errors.jsonl
rm -f "C:UsersrichgAppDataLocalTemporiginal_prompts.py"
rm -rf workstreams/.tmp_ws_10_12/
```

#### 5.2 Consolidate WS-18-21 Move
```bash
# If bundles are staying in .deferred/, commit the move
git add workstreams/.deferred/
git commit -m "chore: move WS-18-21 to deferred (awaiting dependencies)"

# OR if bundles moved back after Phase 3
git add workstreams/ws-*.json
git rm workstreams/.deferred/
git commit -m "chore: restore WS-18-21 after creating dependencies"
```

#### 5.3 Document Lessons Learned
Create `docs/lessons-learned-ws-08.md`:
- Refactoring risks and mitigations
- Importance of comprehensive testing
- Compatibility layer patterns
- Template rendering best practices

#### 5.4 Update CLAUDE.md
Add WS-08 learnings to `CLAUDE.md`:
- New aider/ directory structure
- Compatibility shim patterns
- Common pitfalls to avoid

### Acceptance Criteria
- [ ] No temporary files in working directory
- [ ] All workstream bundles in correct location
- [ ] Documentation updated
- [ ] Lessons learned documented

**Duration**: 1-2 hours
**Blockers**: None
**Risk**: Low

---

## Phase 6: Regression Test Suite (Optional)

**Goal**: Prevent future regressions with automated tests

### Tasks

#### 6.1 Add Unit Tests for Prompt Rendering
```python
# tests/aider/test_engine.py
def test_build_edit_prompt_includes_all_variables():
    """Ensure prompt template receives all expected variables."""
    from pathlib import Path
    from aider.engine import build_edit_prompt

    prompt = build_edit_prompt(
        tasks=["task1"],
        repo_path=Path("/repo"),
        ws_id="test",
        run_id="run1",
        worktree_path=Path("/worktree"),
        files_scope=["file1.py"],
        files_create=["new.py"],
        acceptance_tests=["pytest"],
        openspec_change="CHG-001",
        ccpm_issue="#123",
        gate=1,
    )

    # Verify all variables rendered
    assert "test" in prompt  # ws_id
    assert "run1" in prompt  # run_id
    assert "/repo" in prompt  # repo_root
    assert "/worktree" in prompt  # worktree_path
    assert "file1.py" in prompt  # files_scope
    assert "new.py" in prompt  # files_create
    assert "pytest" in prompt  # acceptance_tests
    assert "CHG-001" in prompt  # openspec_change
    assert "#123" in prompt  # ccpm_issue
    assert "1" in prompt  # gate
```

#### 6.2 Add Integration Test for Aider Invocation
```python
# tests/pipeline/test_prompts_integration.py
def test_aider_edit_prompt_rendering(tmp_path):
    """Test full prompt rendering via compatibility wrapper."""
    # Create mock bundle
    bundle = WorkstreamBundle(
        id="test",
        files_scope=["test.py"],
        files_create=[],
        tasks=["task1"],
        acceptance_tests=["echo ok"],
        depends_on=[],
        openspec_change="TEST",
        ccpm_issue="#1",
        gate=1,
    )

    # Create prompt via compatibility wrapper
    from src.pipeline.prompts import run_aider_edit

    # Mock run_tool to capture prompt file
    # Assert prompt contains expected content
```

#### 6.3 Add Workstream Validation Tests
```python
# tests/integration/test_workstream_validation.py
def test_all_bundles_validate():
    """Ensure all workstream bundles pass schema validation."""
    import subprocess
    result = subprocess.run(
        ["python", "scripts/validate_workstreams.py"],
        capture_output=True,
    )
    assert result.returncode == 0, "Workstream validation failed"
```

### Acceptance Criteria
- [ ] Unit tests for prompt rendering (90%+ coverage)
- [ ] Integration tests for aider invocation
- [ ] CI runs tests on every commit
- [ ] No flaky tests

**Duration**: 4-6 hours
**Blockers**: None
**Risk**: Low

---

## Summary Timeline

| Phase | Duration | Dependencies | Risk |
|-------|----------|--------------|------|
| **Phase 1**: Validation & Testing | 1-2 hrs | None | Low |
| **Phase 2**: WS-10 Completion | 4-6 hrs | Phase 1 | Medium |
| **Phase 3**: Missing Bundles | 3-4 hrs | Phase 2 | Medium |
| **Phase 4**: Execute Deferred WS | 4-8 hrs | Phase 3 | Medium-High |
| **Phase 5**: Cleanup | 1-2 hrs | Phase 4 | Low |
| **Phase 6**: Regression Tests (Opt) | 4-6 hrs | Phase 1 | Low |

**Total Estimated Time**: 17-28 hours (2-3.5 days)

---

## Current Status

**Completed**:
- ✅ Fixed all 4 WS-08 regression bugs
- ✅ WS-11 acceptance tests passed
- ✅ WS-12 acceptance tests passed
- ✅ Deferred WS-18-21 (moved to `.deferred/`)

**In Progress**:
- 🔄 Phase 1: Validation & Testing

**Blocked**:
- 🚫 WS-10: Awaiting validation decision (manual vs. aider)
- 🚫 WS-18-21: Awaiting missing dependency bundles

**Next Steps**:
1. Complete Phase 1 validation
2. Decide on WS-10 approach (Option A, B, or C)
3. Review phase plans to define WS-04, 06, 13-17 scope
4. Execute remaining phases

---

## Open Questions

1. **WS-10 Approach**: Should we retry with aider (now that bugs are fixed) or implement manually?
2. **Missing Bundle Scope**: Where are the original specs for WS-04, 06, 13-17?
3. **Aider Windows Issues**: Should we investigate Unicode console fix or migrate to WSL?
4. **Regression Test Coverage**: Is Phase 6 (optional) worth prioritizing now or defer?

---

## Success Metrics

- [ ] All workstream bundles (WS-10 through WS-21) completed
- [ ] No validation errors across entire bundle set
- [ ] All acceptance tests passing
- [ ] Zero open WS-08 regression bugs
- [ ] Documentation updated and accurate
- [ ] Lessons learned documented for future refactors

---

_Document maintained by: Pipeline Team_
_Next Review: After Phase 1 completion_

