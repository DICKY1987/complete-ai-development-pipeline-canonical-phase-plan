---
doc_id: DOC-PAT-EXEC-011-WORKTREE-WORKFLOW-992
---

# EXEC-011: Git Worktree Workflow Pattern
# Pattern for commit and merge workflows in parallel worktrees

**Pattern ID**: EXEC-011
**Name**: Git Worktree Workflow
**Category**: Version Control
**Time Savings**: 60-70% vs sequential branching
**Difficulty**: Medium
**Prerequisites**: Git worktrees created, changes ready

---

## Purpose

Systematically commit changes in feature branches and merge back to main without conflicts.

---

## Pattern Structure

### Pre-Commit Phase (5 minutes per worktree)

**Input**: Modified files in worktree

**Actions**:
1. Verify you're on correct branch
2. Check what files changed
3. Ensure registry changes are minimal
4. Stage only relevant files

**Output**: Staged changes ready to commit

**Example**:
```powershell
# In worktree
cd .worktrees/wt-docid-specs

# Verify branch
git branch --show-current
# Output: feature/docid-specs ✅

# Check status
git status --short
# Output:
# M  DOC_ID_REGISTRY.yaml (only spec section changed)
# A  specifications/SPEC_INDEX.yaml (new file)

# Stage files
git add DOC_ID_REGISTRY.yaml
git add specifications/SPEC_INDEX.yaml

# Verify staged
git diff --cached --stat
```

### Commit Phase (2 minutes per worktree)

**Input**: Staged changes

**Actions**:
1. Write descriptive commit message
2. Follow conventional commit format
3. Include counts and scope
4. Commit changes

**Output**: Committed changes on feature branch

**Commit Message Template**:
```
feat: register {category} doc_ids ({count} files)

- Register {count} {file_type} files with doc_ids
- Create {CATEGORY}_INDEX.yaml with dependencies
- Update registry metadata (total: {new_total})
- Time saved: {percentage}% vs manual

Categories: {DOC-CATEGORY-*}
Pattern: EXEC-009, EXEC-010
```

**Example**:
```powershell
git commit -m "feat: register specification doc_ids (8 schemas)

- Register 8 JSON schema files with doc_ids
- Create SPEC_INDEX.yaml with validation metadata
- Update registry metadata (total: 37 docs)
- Time saved: 85% vs manual

Categories: DOC-SPEC-*
Pattern: EXEC-009, EXEC-010"

# Verify commit
git log -1 --oneline
```

### Verification Phase (3 minutes per worktree)

**Input**: Committed changes

**Actions**:
1. Validate registry with CLI
2. Check for conflicts with main
3. Ensure tests pass (if applicable)
4. Push branch (optional)

**Output**: Validated feature branch

**Example**:
```powershell
# Validate registry
python ../../scripts/doc_id_registry_cli.py validate
# Output: ✅ Registry valid

# Check for conflicts with main
git fetch origin main
git diff main...feature/docid-specs --stat
# Look for conflicts in DOC_ID_REGISTRY.yaml

# If no conflicts, branch is ready to merge
Write-Host "✅ Branch ready for merge" -ForegroundColor Green
```

---

## Merge Strategy

### Sequential Merge (Recommended)

**Why**: Minimizes registry conflicts, easy to resolve issues

**Order**:
1. Merge specs first (smallest, least likely to conflict)
2. Merge scripts second (clear boundaries)
3. Merge tests/docs third (many files, simple)
4. Merge modules last (largest, verify carefully)

### Merge Phase (5 minutes per branch)

**Input**: Validated feature branch

**Actions**:
1. Switch to main
2. Pull latest changes
3. Merge feature branch
4. Resolve conflicts (if any)
5. Validate merged result
6. Push to remote

**Output**: Changes merged to main

**Example**:
```powershell
# Return to main branch
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Ensure main is clean
git status
# Output: nothing to commit, working tree clean

# Pull latest (if working with team)
git pull origin main

# Merge feature branch
git merge feature/docid-specs --no-ff

# If conflicts occur:
git status
# Look for conflicted files (usually DOC_ID_REGISTRY.yaml)

# Resolve conflicts manually
# Edit DOC_ID_REGISTRY.yaml to combine changes

# After resolving
git add DOC_ID_REGISTRY.yaml
git commit -m "merge: resolve registry conflicts from feature/docid-specs"

# Validate merged registry
python scripts/doc_id_registry_cli.py validate
# Output: ✅ Registry valid

# Push to remote
git push origin main
```

---

## Conflict Resolution

### Registry Conflicts (Most Common)

**Problem**: Multiple branches update `DOC_ID_REGISTRY.yaml`

**Solution**: Category-based merging

```yaml
# Conflict in DOC_ID_REGISTRY.yaml
<<<<<<< HEAD
  spec:
    prefix: "SPEC"
    count: 0
    next_id: 1
=======
  spec:
    prefix: "SPEC"
    count: 8
    next_id: 9
>>>>>>> feature/docid-specs
```

**Resolution**:
```yaml
# Take incoming changes (feature branch)
  spec:
    prefix: "SPEC"
    count: 8
    next_id: 9
```

**Why**: Feature branch has the correct counts

### Document Conflicts (Rare)

**Problem**: Two branches modify same doc_id entry

**Solution**: Prefer newer/more complete information

### File Conflicts (Very Rare)

**Problem**: Two branches create files with same name

**Solution**: Usually impossible with proper worktree setup

---

## Decision Elimination

### Pre-Decisions (Make Once)
- ✅ **Commit message format**: Conventional commits
- ✅ **Merge order**: Specs → Scripts → Tests → Modules
- ✅ **Conflict resolution**: Take feature branch changes
- ✅ **Verification**: Always validate registry after merge

### Not Decisions (Don't Waste Time)
- ❌ **Perfect commit messages**: Clear and consistent is enough
- ❌ **Squash commits**: Keep history, it's informative
- ❌ **Rebase before merge**: Merge commits are fine
- ❌ **Wait for all branches**: Merge ready branches immediately

---

## Time Breakdown

**For 4 worktrees:**

| Phase | Sequential | Parallel + Merge | Savings |
|-------|-----------|------------------|---------|
| Work in branches | 7 hours | 1.5 hours | 79% |
| Commit | 16 min (4 min × 4) | 8 min (parallel) | 50% |
| Merge | N/A | 20 min (5 min × 4) | N/A |
| **Total** | **7 hr 16 min** | **1 hr 58 min** | **73%** |

---

## Complete Workflow Example

```powershell
# ============================================================
# PHASE 1: WORK IN WORKTREES (Parallel - 1.5 hours)
# ============================================================

# Worktree 1: Specs (30 min)
cd .worktrees/wt-docid-specs
# ... register 8 schemas, create index ...
git add DOC_ID_REGISTRY.yaml specifications/SPEC_INDEX.yaml
git commit -m "feat: register specification doc_ids (8 schemas)"

# Worktree 2: Scripts (30 min)
cd ../wt-docid-scripts
# ... register 26 scripts, create index ...
git add DOC_ID_REGISTRY.yaml scripts/SCRIPT_INDEX.yaml
git commit -m "feat: register script doc_ids (26 files)"

# Worktree 3: Tests (45 min)
cd ../wt-docid-tests-docs
# ... register 70 tests/docs, create indexes ...
git add DOC_ID_REGISTRY.yaml tests/TEST_INDEX.yaml docs/GUIDE_INDEX.yaml
git commit -m "feat: register test and guide doc_ids (70 files)"

# Worktree 4: Modules (1 hour)
cd ../wt-docid-modules
# ... register 107 modules, update indexes ...
git add DOC_ID_REGISTRY.yaml core/CORE_MODULE_INDEX.yaml error/ERROR_PLUGIN_INDEX.yaml
git commit -m "feat: register remaining module doc_ids (107 files)"

# ============================================================
# PHASE 2: MERGE TO MAIN (Sequential - 20 minutes)
# ============================================================

cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Merge 1: Specs (5 min)
git merge feature/docid-specs --no-ff
python scripts/doc_id_registry_cli.py validate
git push origin main

# Merge 2: Scripts (5 min)
git merge feature/docid-scripts --no-ff
python scripts/doc_id_registry_cli.py validate
git push origin main

# Merge 3: Tests (5 min)
git merge feature/docid-tests-docs --no-ff
python scripts/doc_id_registry_cli.py validate
git push origin main

# Merge 4: Modules (5 min)
git merge feature/docid-modules --no-ff
python scripts/doc_id_registry_cli.py validate
git push origin main

# ============================================================
# PHASE 3: CLEANUP (5 minutes)
# ============================================================

# Remove worktrees
.\scripts\create_docid_worktrees.ps1 -Cleanup

# Verify final state
python scripts/doc_id_registry_cli.py stats
# Output: Total docs: 247 ✅

git log --oneline --graph -10
# See merge history

Write-Host "`n✅ All worktrees merged successfully!" -ForegroundColor Green
Write-Host "   Total time: 1 hour 58 minutes" -ForegroundColor Cyan
Write-Host "   Modules registered: 218" -ForegroundColor Cyan
Write-Host "   Time saved: 73% vs sequential" -ForegroundColor Cyan
```

---

## Anti-Patterns to Avoid

❌ **Merge all branches at once** → Merge sequentially
❌ **Skip validation after merge** → Always validate
❌ **Auto-resolve conflicts** → Review each conflict
❌ **Delete branches immediately** → Keep until verified
❌ **Work on main directly** → Always use branches

---

## Success Criteria

- ✅ All 4 branches merged to main
- ✅ No orphaned commits
- ✅ Registry validates without errors
- ✅ All index files present
- ✅ Worktrees cleaned up
- ✅ Total time < 2 hours

---

## Troubleshooting

### Problem: Merge conflict in registry
**Solution**: Take feature branch changes (higher counts, newer doc_ids)

### Problem: Validation fails after merge
**Solution**: Check for duplicate doc_ids, fix sequence numbers

### Problem: Worktree won't delete
**Solution**: `git worktree remove --force {path}`

### Problem: Branch behind main
**Solution**: `git merge main` in worktree before final merge

---

## Integration with EXEC-009 and EXEC-010

```
EXEC-009 (Register) → EXEC-010 (Index) → EXEC-011 (Commit & Merge)
     ↓                     ↓                      ↓
Register doc_ids     Create index         Merge to main
     (30 min)           (15 min)             (5 min)

Total per category: 50 minutes
4 categories in parallel: 1.5 hours + 20 min merge = 1 hr 50 min
```

---

## Metrics

**Proven from setup:**
- 4 worktrees created in 2 minutes
- 0 conflicts during setup
- Clean branch isolation

**Projected for full workflow:**
- 218 modules registered across 4 worktrees
- 4 index files created
- 4 sequential merges
- Total time: <2 hours (vs 7+ hours sequential)
- **Speedup: 3.5x-4x**

---

**DOC_LINK**: DOC-PAT-EXECUTION-GIT-WORKTREE-WORKFLOW-001
