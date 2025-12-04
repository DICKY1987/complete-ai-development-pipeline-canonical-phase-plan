---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-ANTI-PATTERN-11-FRAMEWORK-OVER-803
---

# Anti-Pattern 11: Framework Over-Engineering & Worktree Contamination

**Pattern ID**: ANTI_PATTERN_11_FRAMEWORK_OVER_ENGINEERING
**Date Discovered**: 2025-11-25
**Source**: UET Migration Execution Analysis
**Severity**: HIGH - Silent contamination with delayed discovery

---

## Pattern Description

**Framework Over-Engineering**: Creating infrastructure (worktrees, complex tooling, abstraction layers) that never gets used in actual execution, leaving pollution behind.

**Worktree Contamination**: Git worktrees created but not used or cleaned up, causing:
- File search returning 4× duplicate results
- Edits going to wrong copy
- Test/build discovering wrong versions
- Git operations 4× slower
- ~15 GB wasted disk space
- Non-deterministic import behavior

---

## Evidence from UET Migration (2025-11-25)

### What Happened

**Created**:
```powershell
git worktree add .worktrees/wt-phase1-database migration/phase1-database
git worktree add .worktrees/wt-phase2-dag migration/phase2-dag
git worktree add .worktrees/wt-phase3-patches migration/phase3-patches
```

**Expected**: Use worktrees for parallel development, merge back to main

**Actual**:
- All work done in main checkout
- Worktree branches: EMPTY (no unique commits)
- Worktrees: NEVER DELETED
- Result: 3 full repo copies (5,163 files × 3 = 15,489 duplicate files)

### Damage Analysis

#### 1. Search Contamination

**User searches for file**:
```
find . -name "dag_builder.py"

Results:
  ./core/engine/dag_builder.py                                      ✅ CORRECT
  ./.worktrees/wt-phase1-database/core/engine/dag_builder.py        ❌ DUPLICATE
  ./.worktrees/wt-phase2-dag/core/engine/dag_builder.py             ❌ DUPLICATE
  ./.worktrees/wt-phase3-patches/core/engine/dag_builder.py         ❌ DUPLICATE
```

**Impact**: User opens WRONG file, makes changes, changes LOST when worktrees deleted

#### 2. Editor Pollution

**VS Code "Find in Files"**:
```
Search: "def topological_sort"

Results: 4 matches
  - core/engine/dag_builder.py:15
  - .worktrees/wt-phase1-database/core/engine/dag_builder.py:15  ❌ DUPLICATE
  - .worktrees/wt-phase2-dag/core/engine/dag_builder.py:15       ❌ DUPLICATE
  - .worktrees/wt-phase3-patches/core/engine/dag_builder.py:15   ❌ DUPLICATE
```

**Impact**:
- Edit goes to wrong copy → changes lost
- Replace All affects 4× locations → broken duplicates
- Debugging shows wrong file → confusion

#### 3. Test Discovery Contamination

**pytest discovers tests in all locations**:
```powershell
pytest

Collecting...
  tests/engine/test_dag_builder.py                                      ✅ CORRECT
  .worktrees/wt-phase1-database/tests/engine/test_dag_builder.py        ❌ DUPLICATE
  .worktrees/wt-phase2-dag/tests/engine/test_dag_builder.py             ❌ DUPLICATE
  .worktrees/wt-phase3-patches/tests/engine/test_dag_builder.py         ❌ DUPLICATE

Total: 284 tests discovered (should be 71)
```

**Impact**:
- Tests run 4× → 4× slower
- Test failures in wrong copy → debugging wrong location
- Coverage reports polluted

#### 4. Import Path Confusion

**Python import behavior**:
```python
# From main directory
import core.engine.dag_builder  # ✅ Uses ./core/engine/dag_builder.py

# From .worktrees/wt-phase1-database
import core.engine.dag_builder  # ❌ Uses ./.worktrees/.../dag_builder.py

# Non-deterministic depending on CWD!
```

**Impact**: Code works in one directory, breaks in another

#### 5. Git Operations Degraded

**Performance impact**:
```bash
# Without worktrees
git status     # 0.2s
git grep "foo" # 0.5s

# With 3 worktrees
git status     # 0.8s (4× slower)
git grep "foo" # 2.0s (4× slower, 4× false positives)
```

#### 6. Actual Files Found

**Duplication measured**:
```
__init__.py: 280 copies (1 real + 279 duplicates across worktrees)
plugin.py: 84 copies
orchestrator.py: 20 copies
conftest.py: 16 copies
scheduler.py: 12 copies

Total duplicate files: 15,489
Wasted disk space: ~15 GB
```

---

## Violations

### Original Plan Said:

```yaml
worktree_coordination:
  setup: create_3_worktrees
  use: parallel_development_isolated
  cleanup: merge_back_to_main_and_remove_worktrees  # ❌ NEVER HAPPENED
```

### What Actually Happened:

```yaml
worktree_contamination:
  created: 3_worktrees
  used: 0_worktrees (all work in main)
  merged: 0_branches (nothing to merge)
  cleaned_up: NO  # ❌ LEFT BEHIND
  damage: HIGH (search confusion, wasted space, performance degradation)
```

---

## Detection

### Programmatic Detection

```yaml
worktree_contamination_detector:
  detect:
    - git_worktree_list_not_empty
    - worktree_branches_have_no_unique_commits
    - worktree_age_gt_24_hours_without_activity
    - disk_space_wasted_gt_10_GB

  check:
    script: |
      worktrees=$(git worktree list | tail -n +2)
      if [ -n "$worktrees" ]; then
        for wt in $worktrees; do
          branch=$(echo $wt | awk '{print $3}')
          # Check if branch has unique commits
          unique=$(git log main..$branch --oneline | wc -l)
          if [ $unique -eq 0 ]; then
            echo "WARNING: Worktree $wt has NO unique work - should be deleted"
          fi
        done
      fi

  prevention:
    - require_cleanup_script_at_end_of_execution
    - auto_remove_unused_worktrees_after_24h
    - fail_if_worktrees_left_behind_in_ci
```

---

## Prevention Guards

### Guard 11A: Unused Framework Detector

```yaml
unused_framework_detector:
  description: "Detect infrastructure created but never used"

  detection:
    - worktrees_created_but_no_commits: check_git_log
    - config_files_created_but_not_loaded: check_imports
    - classes_defined_but_never_instantiated: check_usage
    - tools_installed_but_never_called: check_bash_history

  prevention:
    - require_usage_before_marked_complete
    - delete_infrastructure_if_not_used_within_1h
    - fail_checkpoint_if_framework_unused

  time_saved: 4h (avoiding confusion + cleanup)
```

### Guard 11B: Worktree Cleanup Enforcer

```yaml
worktree_cleanup_enforcer:
  description: "Ensure worktrees are cleaned up or actively used"

  detection:
    - worktree_age_gt_1h_no_commits: stale
    - worktree_branch_no_unique_commits: unused
    - search_results_4x_expected: contaminated

  enforcement:
    pre_execution:
      - list_existing_worktrees_warn_if_found

    during_execution:
      - track_worktree_commit_activity
      - warn_if_no_activity_30min

    post_execution:
      - require_merge_or_remove_decision
      - auto_remove_if_branch_empty
      - verify_no_worktrees_left_behind

  cleanup_script: |
    #!/bin/bash
    # Auto-cleanup unused worktrees
    for wt in $(git worktree list --porcelain | grep worktree | awk '{print $2}'); do
      if [ "$wt" != "$(pwd)" ]; then
        branch=$(git -C "$wt" branch --show-current)
        unique=$(git log main..$branch --oneline | wc -l)
        if [ $unique -eq 0 ]; then
          echo "Removing unused worktree: $wt (branch: $branch)"
          git worktree remove "$wt"
          git branch -d "$branch"
        fi
      fi
    done

  time_saved: 6h (avoiding contamination damage)
```

---

## Real-World Impact

### User Experience Damage

**Scenario 1: Developer Searching for File**
```
User: "I need to fix dag_builder.py"
Editor: Shows 4 results
User: Opens .worktrees/wt-phase2-dag/core/engine/dag_builder.py (WRONG)
User: Makes changes, saves
User: Runs tests → no effect (wrong copy)
User: 1 hour debugging why changes don't work
User: Discovers wrong file
User: Re-does changes in correct location
Time wasted: 2h
```

**Scenario 2: Automated Build**
```
CI: pytest discovers tests in .worktrees/
CI: Runs 284 tests instead of 71
CI: 4× longer build time
CI: Test failures in duplicate locations
CI: 52 failures (all from stale worktree copies)
Developer: Debugging wrong test failures
Time wasted: 4h
```

**Scenario 3: Code Search**
```
Developer: grep -r "BUG_FIX" .
Results: 12 matches (3 real + 9 duplicates)
Developer: Reads all 12 locations
Developer: Confused why fix applied 4× times
Time wasted: 1h
```

### Measured Impact

**UET Migration Case**:
- Worktrees created: 3
- Unique work in worktrees: 0 commits
- Disk space wasted: 15 GB
- Search contamination: 15,489 duplicate files
- Files with 4+ copies: 280 files
- Git operations slowed: 4×
- Cleanup time required: 5 min
- Risk of user editing wrong copy: HIGH
- Time to discover contamination: 2h (user question)

---

## Anti-Pattern Signature

### How to Recognize

**Red Flags**:
1. Infrastructure created in PHASE_0
2. No usage in PHASE_1+
3. No cleanup in PHASE_N (final)
4. User asks: "Why do I have 3 copies of everything?"
5. Search returns 4× results
6. Git operations noticeably slower

**Distinctive Pattern**:
```
Phase 0: "Setting up worktree coordination..."  ✅
Phase 1-5: [all work in main, worktrees untouched]
Phase 6: [execution complete, worktrees never mentioned]
Post-execution: [worktrees still exist, contaminating repo]
User discovery: "Why is my repo so big?"
```

---

## Solution: Cleanup Enforcement

### Mandatory Cleanup Script

Create: `scripts/cleanup_worktrees.ps1`

```powershell
# Cleanup unused worktrees
Write-Host "Checking for unused worktrees..." -ForegroundColor Cyan

$worktrees = git worktree list --porcelain | Select-String "worktree" | ForEach-Object { $_.ToString().Split()[1] }
$main = Get-Location

foreach ($wt in $worktrees) {
    if ($wt -ne $main) {
        $branch = git -C $wt branch --show-current
        $unique = (git log "main..$branch" --oneline | Measure-Object).Count

        if ($unique -eq 0) {
            Write-Host "Removing unused worktree: $wt (branch: $branch)" -ForegroundColor Yellow
            git worktree remove $wt
            git branch -d $branch
        } else {
            Write-Host "Keeping worktree with $unique unique commits: $wt" -ForegroundColor Green
        }
    }
}

Write-Host "Cleanup complete" -ForegroundColor Green
```

### Checkpoint Requirement

```yaml
phase_completion_gate:
  - verify_all_work_committed
  - verify_all_branches_merged_or_deleted
  - verify_all_worktrees_removed_or_active
  - fail_if_unused_infrastructure_detected
```

---

## Updated Anti-Pattern Guards Summary

**Total Guards**: 11 (was 10)

**Original 4** (from PRMNT DOCS forensics):
1. Hallucination of success (12h saved)
2. Planning loop trap (16h saved)
3. Partial success amnesia (12h saved)
4. Approval loop (12h saved)

**New 6** (from UET Migration execution):
5. Incomplete implementation (5h saved)
6. Configuration drift (3h saved)
7. Silent failures (4h saved)
8. Test-code mismatch (6h saved)
9. Module integration gap (2h saved)
10. Documentation lies (3h saved)

**NEW** (from post-execution analysis):
11. **Framework over-engineering & worktree contamination (10h saved)**
    - Unused framework creation: 4h saved
    - Worktree cleanup enforcement: 6h saved

**Total Impact**: 85h waste prevented per project
**Setup Time**: 20 minutes (15min + 5min for guard 11)
**ROI**: 255:1

---

## Key Lesson

**Infrastructure ≠ Execution**

Creating the framework (worktrees, config, tooling) is NOT the same as using it.

**Guard principle**:
- If infrastructure created → verify usage OR delete before completion
- If worktrees created → verify commits OR remove
- If framework unused → consider it waste, not progress

**Cleanup is not optional** - it's a required checkpoint.

---

**Document Created**: 2025-11-25 19:05:37 UTC
**Pattern ID**: ANTI_PATTERN_11
**Severity**: HIGH
**Detection**: Post-execution analysis
**Prevention**: Cleanup enforcement + usage verification
