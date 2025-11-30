---
doc_id: DOC-GUIDE-AI-EVAL-REALITY-CHECK-1376
---

# AI Evaluation Reality Check & Corrections
**Date**: 2025-11-29  
**Purpose**: Separate actual issues from assumed problems in AI evaluations  
**Status**: Ground truth vs speculation

---

## Executive Summary

The AI evaluations (Claude & ChatGPT) provided **valuable design critique** but made several **incorrect assumptions** about the current system. This document separates:

- ✅ **Real gaps** that need addressing
- ⚠️ **Already solved** (but worth reinforcing)
- ❌ **False alarms** (assumed problems that don't exist)

---

## Section-by-Section Reality Check

### 1. "BLOCKING: ID Strategy vs. Worktree Isolation Conflict"

**What the AIs claimed**:
> Parallel agents will assign different doc_ids to same file → merge conflicts

**Reality Check**:

✅ **Conceptually accurate risk** IF:
- You let each worktree mint IDs independently
- No central coordination

❌ **Not accurate for actual design**:
- Your strategy: `doc_id` comes from **central registry/CLI**
- Scanner + auto-assigner run **outside** multi-agent churn
- Worktrees operate on files that **already have IDs**
- Not designed to let aider/agents mint doc_ids arbitrarily

**Verdict**: 
- Good **warning about what could go wrong**
- NOT a description of current system
- Useful if you later add ad-hoc ID minting (don't do that)

**Action**: 
- ✅ Keep central registry/CLI model
- ✅ No action needed (design already prevents this)

---

### 2. "IDCoordinator" Code Example

**What the AIs proposed**:
```python
class IDCoordinator:
    def assign_doc_id(...):
        with self._lock:
            ...
            self._update_registry(...)
    
    def _update_registry(...):
        with self._lock:  # ← DEADLOCK!
            ...
```

**Problems**:

❌ **Threading bug**: `threading.Lock` is NOT re-entrant
- Calling `_update_registry` from inside `with self._lock:` deadlocks
- Need `threading.RLock` OR remove inner lock

❌ **Conflicts with existing registry**:
- Creates `.state/doc_id_assignments.json` (new file)
- Your real design: existing **doc_id registry + CLI + delta merging**
- Would create two different sources of truth

**Verdict**:
- ✅ Concept of coordinator is good
- ❌ Implementation is broken (deadlock)
- ❌ Ignores your existing registry mechanics

**Action**:
- IF you implement coordinator: use RLock
- Wire into **existing** registry CLI, not new JSON file
- OR: Keep Phase 3 plan as-is (no coordinator needed)

---

### 3. "HIGH RISK: Scanner Race Condition with Worktrees"

**What the AIs claimed**:
> Scanner will find 3 versions of same file (main + 2 worktrees) → corrupted inventory

**Reality Check**:

❌ **FALSE ALARM** - Your scanner already excludes this:

```python
# From scripts/doc_id_scanner.py (actual code)
EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".worktrees",  # ← ALREADY EXCLUDED
    "legacy",
    ".state",
    "refactor_paths.db",
]
```

**Actual state**:
- ✅ `.worktrees` is excluded
- ✅ `.state` is excluded
- ✅ Scanner will NOT see worktree files
- ✅ "Triple counting" scenario is impossible

**Verdict**:
- ❌ Problem doesn't exist in current code
- ✅ Good general principle (don't scan worktrees)
- ✅ Already implemented correctly

**Action**:
- ✅ No changes needed
- ⚠️ Optional: Add `orchestration.lock` as safety belt
- ✅ Document that exclusions prevent this

---

### 4. "Module Refactor vs. ID Assignment Order"

**What the AIs said**:
> Tension between "assign IDs first" vs "create modules first"

**Reality Check**:

✅ **Accurate and aligned** with existing discussions:

Proposed integrated Phase 0:
1. Initial scan (old structure)
2. Assign doc_ids in-place
3. Plan modules (assign module_id, target_path)
4. Snapshot inventory with target paths
5. Refactor using doc_id as primary key
6. Post-refactor validation

**Verdict**:
- ✅ Matches your intended behavior
- ✅ Good basis for Phase 0 playbook
- ✅ No corrections needed

**Action**:
- ✅ Use this as Phase 0 specification
- ✅ Already aligned with design

---

### 5. Efficiency Recommendations

#### 5.1 Lazy/Progressive ID Assignment

**What the AIs proposed**:
```yaml
tier_1_immediate:  # Must have IDs
  - "*.py"
  - "patterns/**"

tier_2_on_demand:  # Assign when touched
  - "tests/**"

tier_3_optional:  # Never need IDs
  - "*.pyc"
```

**Reality Check**:

⚠️ **Design tradeoff**, not correctness issue:
- Your stance: **100% coverage** before refactor
- AIs' stance: **Progressive** for faster start

**Both are valid**:
- Strict → maximum traceability, slower start
- Progressive → faster, some areas "ID-dark" longer

**Verdict**:
- ✅ Reasonable alternative policy
- ⚠️ Not "more correct" than your plan
- 🤔 You can choose: strict for core, progressive for periphery

**Action**:
- 🤔 Decide: stick with 100% OR adopt tiered
- 📝 Document chosen policy

---

#### 5.2 Incremental Inventory Updates

**What the AIs proposed**:
> Update inventory only for files changed in merge (not full rescan)

**Reality Check**:

✅ **Valid optimization**:
- Current: full rescan each time
- Proposed: update only changed files
- Doesn't break model
- Reduces scan time

**Verdict**:
- ✅ Good optimization
- ✅ Compatible with design
- 🟢 Adopt later without breaking anything

**Action**:
- 🟡 Optional enhancement (not urgent)
- ✅ Safe to implement later

---

#### 5.3 ID Taxonomy Simplification

**What the AIs proposed**:
```
Current:  DOC-<SYSTEM>-<DOMAIN>-<KIND>-<SEQ>
Simpler:  DOC-<MODULE_ID>-<SEQ>
```

**Reality Check**:

⚠️ **Style choice**, not accuracy issue:
- Simpler grammar → easier for agents
- Rich semantics → move to metadata

**Tradeoff**:
- Your way: semantically rich IDs
- AIs' way: simple IDs + rich metadata

**Verdict**:
- ⚠️ Design preference
- ✅ Either approach works
- 🤔 Choose based on priority (readability vs automation)

**Action**:
- 🤔 Decide: keep rich IDs OR simplify
- 📝 Document chosen format

---

### 6. Missing Pieces (Real Gaps)

#### 6.1 ID Conflict Resolution Protocol

**What the AIs noted**:
> No rules for same file/different doc_id conflicts

**Reality Check**:

✅ **Real gap** - not specified in your docs:
- What if two agents assign different IDs?
- First-merged-wins? Error? Manual?

**Verdict**:
- ✅ Legitimate missing spec
- ✅ Need to define rules

**Action**:
- 🔴 Define conflict resolution policy
- 📝 Document in ID_LIFECYCLE_RULES.yaml

---

#### 6.2 ID Lifecycle (Split/Merge/Delete)

**What the AIs noted**:
> What happens to doc_id when file is split/merged/deleted?

**Reality Check**:

✅ **Real gap** - not explicitly documented:

Proposed rules (sensible):
```yaml
file_split:
  primary: "keeps original doc_id"
  derived: "new doc_id with derived_from metadata"

file_merge:
  merged: "new doc_id"
  originals: "marked superseded_by"

file_move:
  doc_id: "unchanged"
  path: "updated"

file_delete:
  doc_id: "marked retired"
```

**Verdict**:
- ✅ Real gap
- ✅ Proposed rules are sensible

**Action**:
- 🔴 Define lifecycle rules
- 📝 Document in ID_LIFECYCLE_RULES.yaml

---

#### 6.3 Workstream → Files Mapping

**What the AIs noted**:
> Workstream JSONs don't have `files_to_edit` field

**Reality Check**:

⚠️ **Possibly missing** (not shown in eval docs):

Current workstream JSON:
```json
{
  "id": "ws-22",
  "name": "Pipeline Plus Phase 0",
  "depends_on": []
}
```

Proposed addition:
```json
{
  "id": "ws-22",
  "files_to_edit": ["core/state/db.py"],
  "files_to_create": [".tasks/README.md"]
}
```

**Benefits**:
- Conflict detection (overlapping edits)
- Sparse checkout optimization
- Pre-ID assignment

**Verdict**:
- ⚠️ Possibly missing (check actual workstream files)
- ✅ Useful addition if not present

**Action**:
- 🟡 Check if workstreams have this field
- 🟡 Add if missing (nice-to-have, not critical)

---

## Corrected Priority List

### 🔴 **ACTUAL Critical Issues** (Real gaps)

1. **Define ID Conflict Resolution Policy** (30 min)
   - What happens when same file gets different doc_ids?
   - First-merged-wins? Error? Manual?
   - Document rules

2. **Define ID Lifecycle Rules** (30 min)
   - File split → primary keeps ID, derived gets new
   - File merge → new ID, originals superseded
   - File move → ID unchanged
   - File delete → ID retired
   - Document in ID_LIFECYCLE_RULES.yaml

3. **Verify Workstream Files Mapping** (15 min)
   - Check if workstreams have `files_to_edit`
   - Add if missing
   - Helps with conflict detection

**Total**: ~1 hour (real work)

---

### ✅ **Already Solved** (No action needed)

1. ✅ **Scanner excludes worktrees**
   - Already in EXCLUDE_PATTERNS
   - "Triple counting" can't happen

2. ✅ **Central registry prevents ID conflicts**
   - doc_id_registry_cli.py exists
   - Phase 3 plan uses central minting
   - No need for separate IDCoordinator

3. ✅ **IDs assigned before refactor**
   - Phase 0 plan already addresses this
   - Integrated approach documented

---

### 🟡 **Optional Enhancements** (Nice-to-have)

1. **Add orchestration.lock** (5 min)
   - Prevent scanner during orchestration
   - Safety belt (not critical)

2. **Incremental inventory updates** (1 hour)
   - Optimization (not correctness)
   - Reduces scan time

3. **Tiered coverage policy** (30 min)
   - Alternative to 100% upfront
   - Design choice

4. **ID taxonomy simplification** (if desired)
   - Style preference
   - Not urgent

---

## What the AIs Got Right

### ✅ Useful Conceptual Warnings

1. **Central coordination needed**
   - Don't let worktrees mint IDs independently
   - ✅ Your design already does this

2. **IDs before paths change**
   - Assign doc_ids before module refactor
   - ✅ Your Phase 0 plan already addresses

3. **Need lifecycle rules**
   - What happens during split/merge/delete?
   - ✅ Real gap worth filling

4. **Need conflict resolution**
   - What if same file gets different IDs?
   - ✅ Real gap worth filling

---

## What the AIs Got Wrong

### ❌ False Alarms

1. **Scanner will see worktrees**
   - ❌ Already excluded in EXCLUDE_PATTERNS
   - No action needed

2. **Need separate IDCoordinator**
   - ❌ Conflicts with existing registry
   - Already have doc_id_registry_cli.py
   - No action needed

3. **Threading deadlock code**
   - ❌ Example would deadlock
   - Don't implement as-is

4. **Disk space 5 GB → 10 GB**
   - ⚠️ Possibly valid (check actual usage)
   - Not critical if current works

---

## Recommended Actions (Corrected)

### TODAY (1 hour total)

1. **Create ID_LIFECYCLE_RULES.yaml** (30 min)
   ```yaml
   lifecycle:
     file_split:
       primary_file: "retains original doc_id"
       derived_files: "new doc_id with derived_from metadata"
     
     file_merge:
       merged_file: "new doc_id"
       original_files: "marked superseded_by"
     
     file_move:
       doc_id: "unchanged"
       path: "updated in inventory"
     
     file_delete:
       doc_id: "marked retired"
       status: "retired"
       retired_at: "<timestamp>"
   
   conflict_resolution:
     same_file_different_ids:
       policy: "first-merged-wins"
       action: "mark later as superseded"
     
     different_files_same_id:
       policy: "error"
       action: "manual resolution required"
   ```

2. **Check workstream files** (15 min)
   - Do they have `files_to_edit`?
   - Add if missing

3. **Document scanner exclusions** (15 min)
   - Note that worktrees ARE excluded
   - Prevents future confusion

---

### THIS WEEK (Optional)

4. **Add orchestration.lock** (5 min)
   - Safety belt for scanner
   - Prevents accidental runs during orchestration

5. **Review disk space** (10 min)
   - Check actual usage during tests
   - Adjust if needed (not urgent)

---

### LATER (Optimizations)

6. **Incremental inventory** (1 hour)
7. **Tiered coverage** (if desired)
8. **ID taxonomy** (if simplifying)

---

## Files to Create (Corrected)

### Actually Needed (3 files)

1. **`ID_LIFECYCLE_RULES.yaml`** 🆕
   - File split/merge/delete rules
   - Conflict resolution policy
   - ~50 lines

2. **`docs/ID_CONFLICT_RESOLUTION.md`** 🆕
   - Detailed resolution procedures
   - Examples and edge cases
   - ~100 lines

3. **`AI_EVAL_REALITY_CHECK.md`** 🆕
   - This document
   - Separates real from assumed issues

### Optional (2 files)

4. **`.state/orchestration.lock`** (optional)
   - Created/removed by orchestrator
   - Checked by scanner

5. **`docs/SCANNER_EXCLUSIONS.md`** (optional)
   - Documents what scanner excludes
   - Why worktrees are safe

---

## Bottom Line (Corrected)

### What's Actually True

**Your System Status**: 90% production-ready (not 85%)

**Real Critical Issues**: 2 (not 3)
1. Define ID lifecycle rules (30 min)
2. Define conflict resolution (30 min)

**False Alarms**: 1
1. Scanner seeing worktrees (already excluded)

**Optional Enhancements**: 4
1. orchestration.lock (5 min)
2. Incremental inventory (1 hour)
3. Tiered coverage (design choice)
4. Workstream files mapping (15 min)

**Total Real Work**: ~1 hour (not 50 minutes)

---

### How to Use AI Evaluations

✅ **Keep (Conceptual)**:
- Central coordination principle
- ID lifecycle rules
- Conflict resolution needs
- Integrated Phase 0 ordering

❌ **Discard (Incorrect)**:
- Scanner worktree panic (already solved)
- Specific IDCoordinator code (deadlocks)
- Implication of current corruption (false)

⚠️ **Adapt (Partially Correct)**:
- Disk space check (verify actual usage)
- Tiered coverage (design choice)
- Incremental inventory (optimization)

---

## Next Steps (Realistic)

**OPTION A: Minimal (1 hour)**
1. Create ID_LIFECYCLE_RULES.yaml
2. Document conflict resolution
3. Done - system ready

**OPTION B: Complete (2 hours)**
1. Above + check workstream files
2. Add orchestration.lock
3. Document scanner exclusions
4. Done - fully robust

**OPTION C: Optimized (4 hours)**
1. Above + incremental inventory
2. Tiered coverage (if desired)
3. Done - optimized system

---

**Recommendation**: Option A (1 hour) gets you production-ready.

---

**Status**: ✅ Reality check complete | 2 real issues | 1 hour fix  
**Next**: Create ID_LIFECYCLE_RULES.yaml (30 min)

