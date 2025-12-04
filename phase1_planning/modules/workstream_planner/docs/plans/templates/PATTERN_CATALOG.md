---
doc_id: DOC-GUIDE-PATTERN-CATALOG-1620
---

# Pattern Catalog
**Generated**: 2025-11-23
**Total Patterns**: 3
**Categories**: Execution Patterns (1), Verification (2)

---

## Execution Patterns

### atomic_create_v1
**Category**: file_creation
**Time Savings**: 60% (30 min → 12 min)
**Proven Uses**: Manual extraction from case study

**Use Case**: Creating 1-3 implementation files with complete test suites atomically

**Tool Sequence**:
1. Verify parent directories
2. Create implementation files
3. Create test files
4. Verify creation
5. Run tests

**Key Decisions**:
- `max_files_per_phase: 3`
- `always_include_tests: true`
- `no_placeholders: true`
- `include_docstrings: true`
- `include_type_hints: true`

**Example Usage**:
```yaml
context:
  files:
    - path: "src/error/detector.py"
      type: "implementation"
    - path: "tests/error/test_detector.py"
      type: "test_suite"

expected_duration: 12 minutes
expected_outcome:
  - 2 files created
  - 3+ tests passing
```

---

## Verification Templates

### pytest_green_v1
**Category**: testing
**Time Savings**: 90% (30 sec → 2 sec)
**Purpose**: Ground truth verification that all tests pass

**Command**: `python -m pytest ${test_path} -v --tb=short --color=no`

**Success Criteria**:
- Exit code == 0
- Output contains "passed"
- Output contains "0 failed"
- No ERROR patterns

**Metrics Extracted**:
- Passed count
- Failed count
- Error count
- Duration

**Example**:
```bash
# Input
python -m pytest tests/error/test_detector.py -v

# Success Output
===== test session starts =====
collected 5 items

test_detector.py::test_detect_syntax_error PASSED  [ 20%]
test_detector.py::test_detect_import_error PASSED  [ 40%]
...

===== 5 passed in 0.34s =====

# Result: ✅ SUCCESS
```

---

### preflight_v1
**Category**: environment
**Time Savings**: Prevents 15-30 min debugging sessions
**Purpose**: Verify environment ready before execution

**Checks** (10 total):
1. Project root exists
2. Git repo initialized
3. Base repo clean
4. Python 3.12+ available
5. pytest available
6. git available
7. Working directory writable
8. Core directories exist
9. Optional directories exist
10. Python path configured

**Criticality Levels**:
- **Blocker**: Must pass (stops execution)
- **Warning**: Should pass (logged)
- **Info**: Nice to have (silent)

**Auto-Fix Scenarios**:
- Missing directories → Create automatically
- Module not installed → pip install (if authorized)

**Example**:
```bash
# Run preflight checks
python verify_preflight.py

# Success
✅ Pre-flight checks passed (10/10)
Environment ready for execution

# Failure
❌ Pre-flight checks failed (2/10)

Blockers:
- base_repo_clean: Git has uncommitted changes
- pytest_available: pytest not installed

Quick fixes:
- git stash
- pip install pytest
```

---

## Usage Statistics

```
Pattern Type          | Count | Avg Time Savings
----------------------|-------|------------------
Execution Patterns    |     1 | 60%
Verification          |     2 | 82.5%
----------------------|-------|------------------
Total                 |     3 | 77.5% average
```

---

## Pattern Relationships

```
atomic_create.pattern.yaml
    ├─ Uses: pytest_green.verify.yaml (verify tests pass)
    └─ Uses: preflight.verify.yaml (environment check)

pytest_green.verify.yaml
    └─ Used by: atomic_create, test_first, refactor_patch

preflight.verify.yaml
    └─ Used by: ALL phase templates
```

---

## Creating New Patterns

### From Logs (Automated)
```bash
python scripts/extract_patterns_from_logs.py \
  --copilot-logs ~/.copilot/session-state \
  --output templates/patterns \
  --min-frequency 3
```

### Manual Creation
1. Execute phase and track decisions
2. Identify invariant structure
3. Extract variable sections
4. Define ground truth verification
5. Document time savings

**Template**: See existing patterns in `templates/execution_patterns/`

---

## Pattern Quality Criteria

✅ **Good Pattern**:
- Frequency ≥ 3 uses
- Time savings measurable
- Ground truth verifiable
- No subjective assessments
- Decisions pre-made

❌ **Bad Pattern**:
- One-off usage
- No time data
- Manual verification required
- "Looks good" assessments
- Runtime decisions needed

---

## Next Patterns to Extract

**High Priority** (from logs):
1. `view_edit_verify` - Sequential pattern (view → edit → verify)
2. `parallel_file_read` - Read multiple files simultaneously
3. `grep_view_edit` - Search → inspect → modify workflow
4. `create_test_commit` - Atomic unit creation
5. `batch_module_create` - Parallel module generation

**Medium Priority**:
6. `refactor_safe` - Safe refactoring with tests
7. `doc_generation` - Auto-generate documentation
8. `dependency_install` - Install missing packages
9. `git_worktree_create` - Create isolated worktree
10. `scope_validate` - Verify file scope compliance

---

## References

- **UET Execution Acceleration Guide**: Decision elimination principles
- **Decision Elimination Case Study**: 17 manifests in 12 hours
- **Pattern Extraction Report**: `docs/PATTERN_EXTRACTION_REPORT.md`
- **Template Implementation Plan**: `TEMPLATE_IMPLEMENTATION_PLAN.md`

---

**Status**: ✅ Initial catalog complete
**Next Update**: After automated log extraction completes
