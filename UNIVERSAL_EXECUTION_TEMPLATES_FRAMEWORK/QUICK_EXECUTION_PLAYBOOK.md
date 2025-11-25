# Quick Execution Playbook - One-Page Reference

**Use this for ANY UET phase execution to achieve 5-37x speedup**

---

## The 7 Speed Patterns

### 1. Decision Elimination ⚡ (Most Critical)
**Before Starting**: Make ALL structural decisions
- Directory structure
- File naming conventions
- Quality tiers/categories
- Success criteria
- Tool choices

**During Execution**: Zero ad-hoc decisions
- If not in plan → defer to backlog
- If blocked >5 min → move to archive
- If uncertain → use template

**Speedup**: 3-5x (eliminates analysis paralysis)

---

### 2. Parallel Execution 🔀
**Identify Independent Task Groups**
- Group by: No shared files, no dependencies
- Execute simultaneously in separate terminals/sessions
- Verify all at wave exit (not per-task)

**Example Wave Structure:**
```
Wave 1 (20 min):
├─ Terminal 1: Task A ─────┐
├─ Terminal 2: Task B      │ All run
├─ Terminal 3: Task C      │ in parallel
└─ Terminal 4: Task D ─────┘
   ↓
   Verify wave exit criteria once
```

**Speedup**: 50-75% time reduction per wave

---

### 3. Infrastructure Over Deliverables 🏗️
**Always Ask**: "Can I build a reusable tool instead?"

**Examples:**
- One-time report → Report generator
- Manual validation → Validation script
- File migration → Migration automation
- Link checking → Link checker tool

**Pattern:**
```
Phase Outcome = Deliverable + Reusable Infrastructure
```

**Value**: Infinite future speedup

---

### 4. Ground Truth Verification ✅
**Automate ALL Checks (No Subjective Review)**

**Good Verification:**
- ✅ File exists
- ✅ Markdown syntax valid
- ✅ Link resolves
- ✅ Schema validates
- ✅ Test passes
- ✅ Exit code == 0

**Bad Verification:**
- ❌ "Does this look good?"
- ❌ "Is this the right structure?"
- ❌ Manual inspection

**Speedup**: Eliminates 30+ min of review time

---

### 5. Batch Execution (No Approval Loops) 🎯
**Set "Proceed Without Stopping" Mindset**

**Pattern:**
1. Read plan once (5 min)
2. Execute entire wave (no pauses)
3. Verify at wave exit (automated)
4. Move to next wave

**Anti-Pattern:**
- ❌ Execute task → verify → ask permission → next task
- ❌ "Would you like me to continue?"
- ❌ Manual inspection between tasks

**Speedup**: Eliminates 30+ min of context switching

---

### 6. Defer Low-ROI Work 📊
**80/20 Rule: Focus on 20% That Delivers 80% Value**

**Decision Matrix:**
| Impact | Effort | Action |
|--------|--------|--------|
| High | Low | Do now |
| High | High | Do now |
| Low | Low | Defer |
| Low | High | Skip |

**Example:**
- Parser for 219 files → Do now
- Parser for 3 files → Defer
- Achieve 99% of value with 85% of effort

**Speedup**: 15-30 min saved by skipping low-value work

---

### 7. Pragmatic Pivots 🔄
**If Blocked, Pivot Immediately (Don't Debug)**

**Pivot Triggers:**
- Stuck >5 minutes
- Format issues
- Missing dependencies
- Unclear requirements

**Pivot Actions:**
- Use alternative data source
- Move to archive
- Use template/placeholder
- Skip and continue

**Example:**
- Plan: Extract from 340 logs (format issues)
- Pivot: Extract from docs (ready now)
- Result: Same outcome, 10 min vs 2 hours

**Speedup**: Continuous forward progress

---

## Quick Start Template

### Phase Plan Structure
```markdown
# Phase: [NAME]
Estimated: [TIME] using [PATTERNS]

## Pre-Made Decisions
- [Decision 1]
- [Decision 2]
- [Decision 3]

## Wave 1: [Name] ([TIME]) - PARALLEL
### WS-01A: [Task Name]
Files: [list]
Pattern: [which pattern from 7]
Verification: [automated check]
Time: [minutes]

### WS-01B: [Task Name]
...

Wave 1 Exit Criteria:
- [x] [Criteria 1]
- [x] [Criteria 2]

## Wave 2: ...
```

---

## Execution Checklist

### Pre-Execution (5 min)
- [ ] Read plan once
- [ ] Verify all decisions pre-made
- [ ] Identify parallel task groups
- [ ] Set up terminals/sessions
- [ ] Create execution branch
- [ ] Set "proceed without stopping" mindset

### During Execution
- [ ] No ad-hoc decisions (defer if not in plan)
- [ ] Execute wave tasks in parallel
- [ ] Use automated verification only
- [ ] Pivot if blocked >5 min
- [ ] Log issues to backlog (don't fix now)

### Post-Wave
- [ ] Verify wave exit criteria
- [ ] Commit if all checks pass
- [ ] Move to next wave
- [ ] No manual inspection

### Post-Execution
- [ ] Run all validators
- [ ] Generate completion report
- [ ] Commit with clear message
- [ ] Document speedup achieved

---

## Time Estimation Formula

**Baseline (Sequential, No Plan):**
```
Time = N_tasks × (Analysis + Execution + Verification + Context_Switch)
     = N_tasks × (10 + 15 + 5 + 5) min
     = N_tasks × 35 min
```

**With Speed Patterns:**
```
Time = N_waves × Wave_time + Setup
     = (N_tasks / Parallel_factor) × (Execution + Automated_Verify) + 5 min
     = (N_tasks / 4) × (15 + 2) + 5 min
     = N_tasks × 4.25 min + 5 min
```

**Speedup Factor:** ~8x for 20 tasks

---

## Anti-Patterns to Avoid

### ❌ The Planning Loop Trap
```
Problem: Spend 80k tokens planning before atomic execution
Fix: Pre-make decisions, execute immediately
```

### ❌ The Approval Loop Bottleneck
```
Problem: "Would you like me to..." after every task
Fix: Set "proceed without stopping" and verify at wave exit
```

### ❌ The Perfectionism Blocker
```
Problem: Spend hours perfecting low-value details
Fix: Good enough > perfect, can iterate later
```

### ❌ The Manual Verification Sink
```
Problem: "Does this look right?" for every output
Fix: Automated ground truth checks only
```

### ❌ The Sequential Execution Waste
```
Problem: Execute tasks one-by-one when independent
Fix: Identify parallel groups, run simultaneously
```

---

## Success Metrics

### Minimum Success
- ✅ All quality gates pass (automated)
- ✅ Zero broken state
- ✅ Deliverables exist and valid
- ✅ Time < 2x estimate

### Good Success
- ✅ Minimum + infrastructure created
- ✅ Time < 1.5x estimate
- ✅ Zero manual verification needed
- ✅ Reusable artifacts for future

### Excellent Success
- ✅ Good + 5x+ speedup vs baseline
- ✅ Time < estimate
- ✅ Pattern replication guide created
- ✅ Automation for all verification

---

## Real-World Results

| Phase | Baseline | With Patterns | Speedup |
|-------|----------|---------------|---------|
| Pattern Extraction | 31 hours | 55 min | 37x |
| Module Manifests | 2.5 hours | 55 min | 2.7x |
| Doc Cleanup (est.) | 10 hours | 2 hours | 5x |

**Average Speedup**: 5-10x for planned work, 20-40x for repetitive work

---

## When to Use Which Pattern

| Situation | Primary Pattern | Secondary Pattern |
|-----------|----------------|-------------------|
| New phase (unclear structure) | Decision Elimination | Pragmatic Pivots |
| Many similar tasks | Batch Execution | Infrastructure Over Deliverables |
| Independent work | Parallel Execution | Ground Truth Verification |
| Complex validation | Ground Truth Verification | Infrastructure Over Deliverables |
| Unclear requirements | Pragmatic Pivots | Defer Low-ROI |
| Time pressure | Defer Low-ROI | Parallel Execution |
| Creating reusable system | Infrastructure Over Deliverables | Decision Elimination |

---

## One-Sentence Summary

**Pre-make all decisions, execute in parallel, verify automatically, defer low-value work, pivot when blocked.**

---

## Template Usage

```bash
# Copy this playbook for every new phase
cp QUICK_EXECUTION_PLAYBOOK.md phases/PH-[ID]/EXECUTION_PLAYBOOK.md

# Customize for phase
# Execute using patterns
# Measure speedup
# Update pattern library with learnings
```

---

**Last Updated**: 2025-11-25  
**Pattern Source**: UET META_EXECUTION_PATTERN.md (37x speedup achievement)  
**Applicable To**: Any AI-assisted execution phase with >5 tasks
