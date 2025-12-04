---
doc_id: DOC-GUIDE-QUICK-REFERENCE-CARD-1368
---

# 🚀 Execution Patterns Quick Reference Card

**For**: Claude Code, GitHub Copilot, Codex, all AI agents
**Status**: MANDATORY - Read before starting ANY task
**Time Savings**: 3x-10x speedup | 85h waste prevented per project | 255:1 ROI

---

## ⚡ The Golden Rule

> **Decide once → Apply N times → Trust ground truth → Move on**

---

## 🎯 Quick Decision Tree (30 seconds)

```
START
  ↓
Are you creating/modifying ≥ 3 similar items?
  ↓
  YES → Use Execution Pattern (see below)
  NO  → Proceed with single implementation
  ↓
Enable Anti-Pattern Guards? → ALWAYS YES
  ↓
Execute in batches? → YES (6 files, 4 modules, 8 tests at once)
  ↓
Verify ground truth? → YES (exit code, file exists, NOT "looks good")
  ↓
DONE
```

---

## 📋 6 Execution Patterns

| Pattern | Trigger | Savings | Speedup |
|---------|---------|---------|---------|
| **EXEC-001** Batch File Creator | N ≥ 3 files | 62% | 2.5x |
| **EXEC-002** Module Generator | N ≥ 3 modules | 67% | 3x |
| **EXEC-003** Test Multiplier | N ≥ 5 tests | 70% | 4x |
| **EXEC-004** Doc Standardizer | N ≥ 3 docs | 65% | 2.9x |
| **EXEC-005** Config Multiplexer | N ≥ 3 configs | 75% | 4x |
| **EXEC-006** Endpoint Factory | N ≥ 3 endpoints | 83% | 5.9x |

---

## 🛡️ 11 Anti-Pattern Guards

### Tier 1 - CRITICAL ⚠️
1. **Hallucination of Success** (12h) - Require exit_code verification
2. **Incomplete Implementation** (5h) - Detect TODO/pass placeholders
3. **Silent Failures** (4h) - Require check=True on subprocess
4. **Framework Over-Engineering** (10h) - Remove unused infrastructure

### Tier 2 - HIGH ⚠
5. **Planning Loop Trap** (16h) - Max 2 planning iterations
6. **Test-Code Mismatch** (6h) - Mutation testing required

### Tier 3 - MEDIUM
7. **Configuration Drift** (3h) - Ban hardcoded values
8. **Module Integration Gap** (2h) - Require integration tests
9. **Documentation Lies** (3h) - Type checking enforced
10. **Partial Success Amnesia** (12h) - Checkpoint after steps
11. **Approval Loop** (12h) - No approval for safe ops

**Total**: 85h waste prevented

---

## ✅ Ground Truth Verification

**Success = Objective Observable, NOT Subjective Quality**

```bash
# File creation
test -f file.py && echo "✅" || echo "❌"

# Tests
pytest tests/ -q && echo "✅" || echo "❌"

# Imports
python -c "import module" && echo "✅" || echo "❌"

# API
curl -f http://localhost:8000/health && echo "✅" || echo "❌"
```

---

## ❌ Common Mistakes

### WRONG: Subjective Verification
```
"Tests are running... looks good! ✅"
```

### RIGHT: Ground Truth Verification
```
$ pytest tests/ -q
17 passed in 2.3s
✅ exit_code=0
```

---

### WRONG: Sequential Execution
```python
for item in items:
    create(item)      # 30 min each
    verify(item)      # 5 min each
    ask_approval()    # ← APPROVAL LOOP
# Total: 9.9 hours
```

### RIGHT: Batch Execution
```python
template = load_once()
batch = [create(template, i) for i in items]
verify_all(batch)  # Ground truth only
# Total: 3.4 hours
```

---

## 📊 ROI Calculator

```
Template Creation = 2 hours
Break-Even = 5th item

Example (N=17):
  Traditional: 8.5h
  Pattern: 3.4h
  Saved: 5.1h
  ROI: 2.55:1

Example (N=50):
  Traditional: 25h
  Pattern: 6.2h
  Saved: 18.8h
  ROI: 9.4:1
```

---

## 🔧 Quick Commands

```bash
# Verify guards enabled
cat .execution/anti_patterns.yaml | grep "enabled: true" | wc -l
# Expected: 11

# Ground truth check (files)
ls -la output/*.yaml | wc -l  # Count matches expected

# Ground truth check (tests)
pytest tests/ -q && echo "✅ VERIFIED"

# Initialize pattern
python scripts/init_execution_pattern.py \
  --task "Create manifests" \
  --count 17 \
  --pattern EXEC-001
```

---

## 📚 Full Documentation

**Mandatory Reading**:
- `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`

**Quick Reference**:
- `docs/reference/ai-agents/README.md`

**Source Analysis** (PRMNT DOCS):
- `UET_2025- ANTI-PATTERN FORENSICS.md`
- `EXECUTION_PATTERNS_CHEATSHEET.md`
- `UTE_decision-elimination-playbook.md`

---

## 🎯 Success Checklist

Before declaring task complete:

- [ ] Pattern selected (if N ≥ 3)
- [ ] Anti-pattern guards enabled
- [ ] Batch execution used (not sequential)
- [ ] Ground truth verified (exit codes, not "looks good")
- [ ] No hallucinations (programmatic verification only)
- [ ] No planning loops (max 2 iterations)
- [ ] No approval loops (operator mindset)
- [ ] Checkpoint created
- [ ] Time saved documented

---

## ⏱️ Time Savings

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Decisions/hour | 2.8 | 0.2 | 93% fewer |
| Decision overhead | 38.8% | 2.3% | 94% reduction |
| Time/item | 30-45 min | 5-10 min | 3x-5x faster |
| Rework cycles | 2-3 | 0-1 | 66-100% fewer |

**Overall**: 3x-10x speedup, 85h waste prevented, 255:1 ROI

---

## 🚨 Enforcement

This is **MANDATORY** and **ENFORCED**:
- ✅ Pre-execution checklist required
- ✅ Anti-pattern guards automated
- ✅ Ground truth gates mandatory
- ✅ CI blocks non-compliant PRs
- ✅ Metrics tracked and reported

**Non-compliance = Blocked work**

---

**Print this card and keep it visible while coding!**

**Updated**: 2025-11-26T09:27:23Z
**Version**: 1.0.0
