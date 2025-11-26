# AI Agent Instructions - Execution Patterns & Anti-Pattern Guards

**Last Updated**: 2025-11-26T09:27:23Z  
**Status**: ACTIVE - MANDATORY FOR ALL AI AGENTS  
**Source**: `C:\Users\richg\Downloads\PRMNT DOCS\`

---

## Overview

This directory contains **mandatory execution patterns** and **anti-pattern guards** that ALL AI agents (Claude, Copilot, Codex) must follow when working on this project.

### The Problem

Historical analysis shows AI agents waste **85 hours per project** through:
- Hallucinating success without verification (12h)
- Planning loops without execution (16h)
- Creating incomplete implementations (5h)
- Allowing silent failures (4h)
- Over-engineering frameworks (10h)
- Test-code mismatches (6h)
- And 5 other documented failure modes

### The Solution

**Execution Patterns** + **Anti-Pattern Guards** = **3x-10x speedup** with **255:1 ROI**

---

## Quick Start (5 minutes)

### Step 1: Read Mandatory Document (2 minutes)

📋 **[EXECUTION_PATTERNS_MANDATORY.md](./EXECUTION_PATTERNS_MANDATORY.md)**

This document is **REQUIRED READING** before starting ANY task.

### Step 2: Enable Anti-Pattern Guards (1 minute)

```bash
# Guards are already configured in:
# .execution/anti_patterns.yaml

# Verify they're enabled:
cat .execution/anti_patterns.yaml | grep "guards_enabled: true"
```

### Step 3: Check Pattern Selection (30 seconds)

```
IF creating/modifying ≥ 3 similar items
THEN use execution pattern (see EXECUTION_PATTERNS_MANDATORY.md)
ELSE proceed with single implementation
```

### Step 4: Follow Ground Truth Verification (1 minute)

```bash
# File creation?
test -f path/to/file && echo "✅ EXISTS" || echo "❌ MISSING"

# Tests?
pytest tests/ -q && echo "✅ PASS" || echo "❌ FAIL"

# Imports?
python -c "import module" && echo "✅ IMPORTS" || echo "❌ BROKEN"
```

---

## File Structure

```
docs/reference/ai-agents/
├── README.md                          # This file
├── EXECUTION_PATTERNS_MANDATORY.md    # Core execution patterns (MUST READ)
└── templates/                         # Execution templates library
    ├── EXEC-001-batch-file-creator.yaml
    ├── EXEC-002-module-generator.yaml
    ├── EXEC-003-test-multiplier.yaml
    ├── EXEC-004-doc-standardizer.yaml
    ├── EXEC-005-config-multiplexer.yaml
    └── EXEC-006-endpoint-factory.yaml

.execution/
├── anti_patterns.yaml                 # 11 anti-pattern guard configs
├── checkpoints/                       # Phase completion checkpoints
└── metrics/                           # Time savings metrics

.github/
└── copilot-instructions.md            # GitHub Copilot integration

docs/reference/tools/
└── CLAUDE.md                          # Claude Code integration
```

---

## How to Use

### For Claude Code Users

Claude automatically reads `docs/reference/tools/CLAUDE.md` which now includes:
- Reference to EXECUTION_PATTERNS_MANDATORY.md
- Anti-pattern guard enforcement
- Pattern-first workflow requirement

**No additional setup needed** - just start working and Claude will follow patterns.

### For GitHub Copilot Users

Copilot reads `.github/copilot-instructions.md` which now includes:
- Pattern selection checklist
- Anti-pattern guard summary
- Ground truth verification requirement

**Copilot will suggest pattern-based solutions** when you write repetitive code.

### For Codex / Other AI Agents

Add this to your system prompt:

```
Before beginning ANY task, read:
docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md

Follow the pattern-first workflow:
1. Check if N ≥ 3 similar items
2. If yes: Use execution pattern
3. Enable anti-pattern guards
4. Execute in batches
5. Verify ground truth only
```

---

## The 11 Anti-Pattern Guards

### Tier 1 - CRITICAL (Must Have)

1. **Hallucination of Success** (12h saved)
   - Never declare complete without exit_code verification
   - Require programmatic evidence of success

2. **Incomplete Implementation** (5h saved)
   - Detect TODO/pass placeholders
   - Require function body length > 3 lines OR delegation

3. **Silent Failures** (4h saved)
   - Require subprocess.run(..., check=True)
   - Explicit error handling mandatory

4. **Framework Over-Engineering** (10h saved)
   - Remove unused worktrees/infrastructure
   - Verify no search contamination

### Tier 2 - HIGH (Should Have)

5. **Planning Loop Trap** (16h saved)
   - Max 2 planning iterations
   - Force execution after threshold

6. **Test-Code Mismatch** (6h saved)
   - Mutation testing required
   - Branch coverage ≥ 70%

### Tier 3 - MEDIUM (Nice to Have)

7. **Configuration Drift** (3h saved)
8. **Module Integration Gap** (2h saved)
9. **Documentation Lies** (3h saved)
10. **Partial Success Amnesia** (12h saved)
11. **Approval Loop** (12h saved)

**Total Impact**: 85 hours waste prevented per project

---

## Execution Patterns

### EXEC-001: Batch File Creator
**Use When**: Creating N ≥ 3 similar files  
**Time Savings**: 62% (5.3h saved on 17 files)  
**Speedup**: 2.5x

### EXEC-002: Module Generator
**Use When**: Generating N ≥ 3 similar code modules  
**Time Savings**: 67%  
**Speedup**: 3x

### EXEC-003: Test Multiplier
**Use When**: Writing N ≥ 5 similar tests  
**Time Savings**: 70% (10.4h saved on 25 tests)  
**Speedup**: 4x

### EXEC-004: Doc Standardizer
**Use When**: Creating N ≥ 3 similar docs  
**Time Savings**: 65%  
**Speedup**: 2.9x

### EXEC-005: Config Multiplexer
**Use When**: Generating N ≥ 3 config files  
**Time Savings**: 75%  
**Speedup**: 4x

### EXEC-006: Endpoint Factory
**Use When**: Building N ≥ 3 API endpoints  
**Time Savings**: 83%  
**Speedup**: 5.9x

---

## Proven Results

### Case Study: UET Engine Migration (2025-11-25)

**Traditional Estimate**: 300 hours  
**Actual Execution**: 25 hours  
**Speedup**: 12x  
**Time Saved**: 275 hours

**How**:
- PHASE_0: Created 4 execution templates (2 min) → Eliminated 140 decisions
- PHASE_1-5: Batch execution → 104 files in 5 min vs 31h traditional
- Anti-Pattern Guards: Prevented 85h of waste
- Ground Truth Gates: Zero hallucinations detected

### Metrics Summary

```yaml
before_patterns:
  decisions_per_hour: 2.8
  decision_overhead: 38.8%
  time_per_item: 30-45 min
  rework_cycles: 2-3

after_patterns:
  decisions_per_hour: 0.2
  decision_overhead: 2.3%
  time_per_item: 5-10 min
  rework_cycles: 0-1

improvement:
  decision_overhead_reduction: 94%
  speedup: 3x-10x
  roi: 255:1
```

---

## The Golden Rule

> **Decide once → Apply N times → Trust ground truth → Move on**

This is the **ONLY** way to achieve consistent 3x-10x speedup.

---

## Common Mistakes to Avoid

### ❌ WRONG: Sequential Execution
```python
for item in items:
    create_file(item)      # 30 min each
    verify_file(item)      # 5 min each
    ask_user_approval()    # ← APPROVAL LOOP ANTI-PATTERN
# Total: 17 × 35 min = 9.9 hours
```

### ✅ RIGHT: Batch Execution
```python
template = load_once()
batch = [create(template, item) for item in items]
verify_all(batch)  # Ground truth only
# Total: 3.4 hours (2.9x faster)
```

### ❌ WRONG: Subjective Verification
```
"Tests are running... it looks good! ✅ Complete"
```

### ✅ RIGHT: Ground Truth Verification
```bash
$ pytest tests/ -q
17 passed in 2.3s
✅ Ground truth verified: exit_code=0
```

---

## Source Documents (PRMNT DOCS)

All patterns and guards are derived from:

1. **UET_2025- ANTI-PATTERN FORENSICS.md**  
   Forensic analysis of 85h waste across 4 execution sessions

2. **EXECUTION_PATTERNS_CHEATSHEET.md**  
   Quick reference for 6 core execution patterns

3. **UTE_decision-elimination-playbook.md**  
   Core methodology for decision elimination

4. **EXECUTION_ACCELERATION_ANALYSIS.md**  
   Quantified time savings and ROI metrics

5. **EXECUTION_PATTERNS_LIBRARY.md**  
   Complete pattern library with code examples

6. **UTE_execution-acceleration-guide.md**  
   Integration guide for AI Boss programs

---

## Maintenance

### When to Update

Update these instructions when:
- New anti-patterns discovered during execution
- New execution patterns proven effective (3+ uses)
- ROI metrics change significantly
- Guard effectiveness measured

### How to Update

1. Document new pattern/guard in PRMNT DOCS
2. Update EXECUTION_PATTERNS_MANDATORY.md
3. Update .execution/anti_patterns.yaml if needed
4. Add to this README
5. Commit with reference to source analysis

---

## Enforcement

These patterns are **MANDATORY** and **ENFORCED** via:

1. **Pre-execution checklist** - Required before starting work
2. **Anti-pattern guards** - Automated violation detection
3. **Ground truth gates** - No phase completion without verification
4. **CI gates** - Block PRs missing patterns or guards
5. **Metrics tracking** - Measure and report time savings

**Non-compliance** = Blocked work

---

## Quick Reference Commands

```bash
# Check anti-pattern guards enabled
cat .execution/anti_patterns.yaml | grep "enabled: true" | wc -l
# Expected: 11

# Initialize pattern workflow
python scripts/init_execution_pattern.py \
  --task "Create module manifests" \
  --count 17 \
  --pattern EXEC-001

# Verify ground truth
pytest tests/ -q && echo "✅ VERIFIED"

# Check for violations
python scripts/check_anti_patterns.py --phase current

# View time savings
python scripts/guard_metrics.py --summary
```

---

## Support

For questions or issues:
1. Review EXECUTION_PATTERNS_MANDATORY.md
2. Check PRMNT DOCS source files
3. Verify anti-pattern guards enabled
4. Follow pattern-first workflow

**Remember**: This is proven to save 85h per project. Use it.
