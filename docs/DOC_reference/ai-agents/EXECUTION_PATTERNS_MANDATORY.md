---
doc_id: DOC-GUIDE-EXECUTION-PATTERNS-MANDATORY-551
---

# EXECUTION PATTERNS - MANDATORY FOR ALL AI AGENTS

**Document ID**: DOC-AI-EXECUTION-PATTERNS-001
**Status**: ACTIVE - ENFORCED
**Last Updated**: 2025-11-26T09:27:23Z
**Applies To**: Claude Code, GitHub Copilot, Codex, all AI code assistants
**Priority**: CRITICAL - Must follow before beginning ANY task

---

## 0. Core Principle: Pattern-First Execution

**MANDATORY RULE**: Before beginning any task, create or select an execution pattern.

### The Rule
```
IF task involves creating/modifying ≥ 3 similar items
THEN create execution pattern FIRST
ELSE proceed with single implementation
```

### Why This Matters
- **Decision Elimination**: Make structural decisions once, apply N times
- **Speed**: 3x-10x faster execution through reduced cognitive load
- **Quality**: Consistent output, fewer errors, comprehensive coverage
- **Anti-Pattern Prevention**: Blocks hallucinations, planning loops, approval traps

---

## 1. Execution Pattern Selection (Phase 0)

### Step 1: Identify Task Type (30 seconds)

Before writing ANY code, determine task category:

| Task Type | Pattern | Trigger |
|-----------|---------|---------|
| Create N similar files | EXEC-001 Batch Creator | N ≥ 3 files |
| Generate similar modules | EXEC-002 Module Generator | N ≥ 3 modules |
| Write test suites | EXEC-003 Test Multiplier | N ≥ 5 tests |
| Create documentation | EXEC-004 Doc Standardizer | N ≥ 3 docs |
| Generate configs | EXEC-005 Config Multiplexer | N ≥ 3 configs |
| Build API endpoints | EXEC-006 Endpoint Factory | N ≥ 3 endpoints |

### Step 2: Anti-Pattern Guards (MANDATORY - 11 Critical Guards)

**Enable ALL guards before execution**:

1. **Hallucination of Success** (12h saved) - Require programmatic verification
2. **Planning Loop Trap** (16h saved) - Max 2 planning iterations, then execute
3. **Incomplete Implementation** (5h saved) - Detect TODO/pass placeholders
4. **Silent Failures** (4h saved) - Require explicit error handling
5. **Framework Over-Engineering** (10h saved) - Remove unused infrastructure
6. **Test-Code Mismatch** (6h saved) - Mutation testing required
7. **Configuration Drift** (3h saved) - Ban hardcoded values
8. **Module Integration Gap** (2h saved) - Require integration tests
9. **Documentation Lies** (3h saved) - Type checking enforced
10. **Partial Success Amnesia** (12h saved) - Checkpoint after each step
11. **Approval Loop** (12h saved) - No human approval for safe ops

**Total Impact**: 85 hours waste prevented per project
**Setup Time**: 5-10 minutes
**ROI**: 255:1

---

## 2. Ground Truth Verification (MANDATORY)

**Success = Objective Observable Criterion, NOT subjective quality**

### Ground Truth by Context

| Context | Ground Truth | NOT Ground Truth |
|---------|-------------|------------------|
| File creation | `file.exists()` | Content is perfect |
| Test execution | `exit_code == 0` | All edge cases covered |
| API deployment | `curl returns 200` | Code is elegant |
| Database migration | `table_count == expected` | Schema is normalized |

### Verification Commands

```bash
# File creation
test -f path/to/file && echo "✅ EXISTS" || echo "❌ MISSING"

# Test execution
pytest tests/ -q && echo "✅ PASS" || echo "❌ FAIL"

# Import validation
python -c "import module" && echo "✅ IMPORTS" || echo "❌ BROKEN"
```

---

## 3. Batch Execution (CRITICAL)

### Batch Size Guidelines

```yaml
file_creation: 6_files_per_batch
code_modules: 4_modules_per_batch
test_cases: 8_tests_per_batch
documentation: 6_docs_per_batch
```

### Execution Flow

```
1. Load template ONCE
2. Load ALL context UPFRONT (no mid-batch lookups)
3. Generate batch of N items in SINGLE operation
4. Verify ALL items at END (batch verification)
5. Move to next batch
```

### Anti-Pattern: Sequential Execution

❌ **NEVER DO THIS**:
```
for each item:
    load_template()
    load_context()
    generate_item()
    verify_item()
    ask_user_if_looks_good()  # ← APPROVAL LOOP ANTI-PATTERN
```

✅ **ALWAYS DO THIS**:
```
template = load_template()
context = load_all_context()
items = [generate(template, item_data) for item_data in batch]
verify_all(items)  # Ground truth verification only
```

---

## 4. Decision Elimination Checklist

### Pre-Execution Decisions (Make ONCE)

```markdown
## Structural Decisions (made once, apply N times)
- [ ] Format: {Python|YAML|Markdown|JSON}
- [ ] Length: {50-100|100-200|200+} lines
- [ ] Detail level: {high-level|detailed|exhaustive}
- [ ] Verification: {file_exists|tests_pass|service_responds}
- [ ] Completion criterion: {N files created|all tests green}

## NOT Decisions (don't waste time on these)
- [ ] Perfect grammar: NO (fix later if needed)
- [ ] Exhaustive coverage: NO (start with core cases)
- [ ] Optimal organization: NO (refactor later if needed)
- [ ] Future-proof design: NO (YAGNI principle)
```

---

## 5. Time Savings Metrics

### ROI Calculation

```
Template Creation Cost = 2 hours (first 3 examples + extraction)
Break-Even Point = 5th item

Example (N=17):
  Traditional: 8.5h
  Pattern: 3.4h
  Saved: 5.1h
  Speedup: 2.5x

Example (N=50):
  Traditional: 25h
  Pattern: 6.2h
  Saved: 18.8h
  Speedup: 4x
```

---

## 6. Mandatory Workflow

```
Phase 0: Pattern Selection (30 sec)
  ❓ How many similar items? → If N ≥ 3, use pattern

Phase 1: Template Creation (10-30 min for new patterns)
  1. Create first 2-3 examples manually
  2. Extract invariants
  3. Mark variables
  4. Document ground truth

Phase 2: Enable Guards (5 min)
  Enable 11 anti-pattern guards in config

Phase 3: Batch Execution (5-10 min per item)
  1. Load template ONCE
  2. Generate batches (6 at once)
  3. NO per-item verification

Phase 4: Ground Truth Verification (2 min total)
  Run verification on ALL items
  If passes → DONE, if fails → Fix and re-verify
```

---

## 7. Success Criteria

### Task is Complete When:

✅ All ground truth verifications pass
✅ Anti-pattern guards show 0 violations
✅ Checkpoint file created
✅ Time savings documented

### Task is NOT Complete When:

❌ "Looks good" (subjective)
❌ "Should work" (not verified)
❌ "Tests are running" (not confirmed passed)
❌ Files created but imports fail

---

## 8. Quick Reference

**The Golden Rule**:

> **Decide once → Apply N times → Trust ground truth → Move on**

**Most Common Anti-Patterns to Avoid**:
1. Declaring success without exit code verification
2. Planning for hours without executing atomic step
3. Asking permission instead of executing safe operation
4. Verifying every detail instead of ground truth only
5. Creating infrastructure and leaving it unused

**Source Documents** (in PRMNT DOCS):
- `UET_2025- ANTI-PATTERN FORENSICS.md` - Learn what NOT to do
- `EXECUTION_PATTERNS_CHEATSHEET.md` - Quick reference
- `UTE_decision-elimination-playbook.md` - Core methodology
- `EXECUTION_ACCELERATION_ANALYSIS.md` - Time savings metrics

---

**Remember**: This is MANDATORY and ENFORCED. No exceptions.
