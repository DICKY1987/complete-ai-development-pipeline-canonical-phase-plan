# Parallel Execution Strategy - Git Worktrees for DOC_ID Project

**Created**: 2025-11-24  
**Purpose**: Speed up doc_id rollout using parallel git worktrees  
**Pattern**: EXEC-001 + Parallel Git Worktrees

---

## 🎯 Strategy Overview

**Goal**: Complete remaining 218 modules in 2-3 hours using parallel execution

**Approach**:
1. Create 4 git worktrees (one per category)
2. Run separate Copilot instances in each
3. Batch process independently
4. Merge all branches when complete

**Expected speedup**: 4x (vs sequential) = **1.5 hours vs 7.5 hours**

---

## 📋 Worktree Plan

### Worktree 1: Specifications & Schemas
- **Branch**: `feature/docid-specs`
- **Path**: `.worktrees/wt-docid-specs`
- **Scope**: 25 specification/schema files
- **Time**: 30 minutes
- **Categories**: SPEC, CONFIG

### Worktree 2: Scripts & Tools
- **Branch**: `feature/docid-scripts`
- **Path**: `.worktrees/wt-docid-scripts`
- **Scope**: 26 script files
- **Time**: 30 minutes
- **Categories**: SCRIPT

### Worktree 3: Tests & Documentation
- **Branch**: `feature/docid-tests-docs`
- **Path**: `.worktrees/wt-docid-tests-docs`
- **Scope**: 60 test files + 10 guides
- **Time**: 45 minutes
- **Categories**: TEST, GUIDE

### Worktree 4: Remaining Modules
- **Branch**: `feature/docid-modules`
- **Path**: `.worktrees/wt-docid-modules`
- **Scope**: 107 remaining core/error/aim/pm modules
- **Time**: 1 hour
- **Categories**: CORE, ERROR, AIM, PM, INFRA

---

## 🚀 Setup Commands

```powershell
# Navigate to repo root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Create worktree directory
New-Item -ItemType Directory -Path ".worktrees" -Force

# Create 4 worktrees for parallel work
git worktree add .worktrees/wt-docid-specs feature/docid-specs
git worktree add .worktrees/wt-docid-scripts feature/docid-scripts
git worktree add .worktrees/wt-docid-tests-docs feature/docid-tests-docs
git worktree add .worktrees/wt-docid-modules feature/docid-modules

# Verify worktrees created
git worktree list
```

---

## 📝 Task Assignments

### Worktree 1: Specifications (25 files)

**Files to register:**
```
schema/workstream.schema.json → DOC-SPEC-WORKSTREAM-SCHEMA-001
schema/step.schema.json → DOC-SPEC-STEP-SCHEMA-001
schema/error.schema.json → DOC-SPEC-ERROR-SCHEMA-001
config/orchestrator.yaml → DOC-CONFIG-ORCHESTRATOR-001
config/executor.yaml → DOC-CONFIG-EXECUTOR-001
... (20 more)
```

**Commands:**
```powershell
cd .worktrees/wt-docid-specs

# Batch register schemas
$schemas = @("workstream-schema", "step-schema", "error-schema", ...)
foreach ($s in $schemas) {
    python ../../scripts/doc_id_registry_cli.py mint --category spec --name $s
}

# Create SPEC_INDEX.yaml
# Commit changes
git add .
git commit -m "feat: register specification and schema doc_ids"
```

### Worktree 2: Scripts (26 files)

**Files to register:**
```
scripts/validate_workstreams.py → DOC-SCRIPT-VALIDATE-WORKSTREAMS-004 (already done)
scripts/generate_*.py → DOC-SCRIPT-GENERATE-*-00X
scripts/check_*.py → DOC-SCRIPT-CHECK-*-00X
... (23 more)
```

**Commands:**
```powershell
cd .worktrees/wt-docid-scripts

# Discover all scripts
$scripts = Get-ChildItem ../../scripts -Filter "*.py" | Select-Object -ExpandProperty BaseName

# Batch register
foreach ($s in $scripts) {
    python ../../scripts/doc_id_registry_cli.py mint --category script --name $s
}

# Create SCRIPT_INDEX.yaml
# Commit changes
git add .
git commit -m "feat: register all script doc_ids"
```

### Worktree 3: Tests & Docs (70 files)

**Files to register:**
```
tests/state/test_db.py → DOC-TEST-STATE-DB-001
tests/engine/test_orchestrator.py → DOC-TEST-ORCHESTRATOR-001
docs/QUICK_START.md → DOC-GUIDE-QUICK-START-001
... (67 more)
```

**Commands:**
```powershell
cd .worktrees/wt-docid-tests-docs

# Register test files
$testFiles = Get-ChildItem ../../tests -Filter "test_*.py" -Recurse
foreach ($t in $testFiles) {
    $name = $t.BaseName -replace "^test_", ""
    python ../../scripts/doc_id_registry_cli.py mint --category test --name $name
}

# Register guides
$guides = @("quick-start", "architecture", "development-guide", ...)
foreach ($g in $guides) {
    python ../../scripts/doc_id_registry_cli.py mint --category guide --name $g
}

# Create TEST_INDEX.yaml and GUIDE_INDEX.yaml
# Commit changes
git add .
git commit -m "feat: register test and guide doc_ids"
```

### Worktree 4: Remaining Modules (107 files)

**Files to register:**
```
core/ast/extractors.py → DOC-CORE-AST-EXTRACTORS-001
aim/bridge.py → DOC-AIM-BRIDGE-001
pm/workstream_manager.py → DOC-PM-WORKSTREAM-MANAGER-001
... (104 more)
```

**Commands:**
```powershell
cd .worktrees/wt-docid-modules

# Register remaining core modules
$coreFiles = Get-ChildItem ../../core -Filter "*.py" -Recurse | 
             Where-Object { $_.Name -ne "__init__.py" }

# Register AIM modules
$aimFiles = Get-ChildItem ../../aim -Filter "*.py" -Recurse

# Register PM modules
$pmFiles = Get-ChildItem ../../pm -Filter "*.py" -Recurse

# Batch register all
# ... (batching logic)

# Update indexes
# Commit changes
git add .
git commit -m "feat: register remaining module doc_ids"
```

---

## 🔄 Execution Workflow

### Phase 1: Setup (5 minutes)

```powershell
# Run once from main branch
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Create worktrees
./scripts/create_docid_worktrees.ps1

# Verify all 4 created
git worktree list
```

### Phase 2: Parallel Execution (1-1.5 hours)

**Open 4 terminal windows:**

```powershell
# Terminal 1 - Specifications
cd .worktrees/wt-docid-specs
# Work on specs...

# Terminal 2 - Scripts
cd .worktrees/wt-docid-scripts
# Work on scripts...

# Terminal 3 - Tests & Docs
cd .worktrees/wt-docid-tests-docs
# Work on tests...

# Terminal 4 - Modules
cd .worktrees/wt-docid-modules
# Work on modules...
```

**Or use tmux/multiple Copilot sessions:**
- Each window runs independent Copilot instance
- No merge conflicts (different files)
- All update same registry (merge later)

### Phase 3: Merge & Cleanup (10 minutes)

```powershell
# Switch to main branch
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Merge all branches
git merge feature/docid-specs
git merge feature/docid-scripts
git merge feature/docid-tests-docs
git merge feature/docid-modules

# Resolve any registry conflicts (unlikely)
# Validate merged registry
python scripts/doc_id_registry_cli.py validate

# Clean up worktrees
git worktree remove .worktrees/wt-docid-specs
git worktree remove .worktrees/wt-docid-scripts
git worktree remove .worktrees/wt-docid-tests-docs
git worktree remove .worktrees/wt-docid-modules

# Delete branches
git branch -d feature/docid-specs
git branch -d feature/docid-scripts
git branch -d feature/docid-tests-docs
git branch -d feature/docid-modules
```

---

## ⚡ Conflict Avoidance Strategy

### Registry Conflicts
**Problem**: All 4 worktrees update `DOC_ID_REGISTRY.yaml`

**Solution**: Category-based partitioning
- Worktree 1: Only adds to `categories.spec` and `categories.config`
- Worktree 2: Only adds to `categories.script`
- Worktree 3: Only adds to `categories.test` and `categories.guide`
- Worktree 4: Only adds to `categories.core`, `categories.aim`, `categories.pm`

**Merge strategy**: Git handles YAML appends cleanly if sections don't overlap

### Index Files
**No conflicts**: Each worktree creates different index files
- `specifications/SPEC_INDEX.yaml`
- `scripts/SCRIPT_INDEX.yaml`
- `tests/TEST_INDEX.yaml`
- `docs/GUIDE_INDEX.yaml`

---

## 📊 Time Comparison

### Sequential Approach (Current Plan)
```
Phase 3: Specs (25 files) - 1 hour
Phase 4: Scripts (26 files) - 1 hour
Phase 5: Tests (50 files) - 1.5 hours
Phase 6: Guides (10 files) - 30 min
Phase 7: Modules (107 files) - 3 hours
Total: 7 hours
```

### Parallel Approach (Worktrees)
```
Setup: 5 minutes
Parallel execution (all 4 at once): 1-1.5 hours
Merge: 10 minutes
Total: 1.5-2 hours
```

**Speedup: 4.4x faster (7 hours → 1.5 hours)**

---

## 🛠️ Helper Script

Create `scripts/create_docid_worktrees.ps1`:

```powershell
#!/usr/bin/env pwsh
# Create git worktrees for parallel doc_id registration

$repoRoot = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
$worktreeBase = "$repoRoot\.worktrees"

# Ensure we're in repo root
Set-Location $repoRoot

# Create worktree directory
New-Item -ItemType Directory -Path $worktreeBase -Force | Out-Null

# Define worktrees
$worktrees = @(
    @{Name="wt-docid-specs"; Branch="feature/docid-specs"},
    @{Name="wt-docid-scripts"; Branch="feature/docid-scripts"},
    @{Name="wt-docid-tests-docs"; Branch="feature/docid-tests-docs"},
    @{Name="wt-docid-modules"; Branch="feature/docid-modules"}
)

# Create each worktree
foreach ($wt in $worktrees) {
    $path = "$worktreeBase\$($wt.Name)"
    $branch = $wt.Branch
    
    Write-Host "Creating worktree: $($wt.Name)" -ForegroundColor Green
    git worktree add $path $branch
}

Write-Host "`nWorktrees created successfully!" -ForegroundColor Green
Write-Host "`nList of worktrees:" -ForegroundColor Yellow
git worktree list

Write-Host "`n✅ Ready for parallel execution" -ForegroundColor Green
Write-Host "Open 4 terminals and cd to each worktree path to begin."
```

---

## 🎯 Execution Checklist

### Pre-execution
- [ ] All current work committed to main
- [ ] Registry validated (no errors)
- [ ] Worktree script created
- [ ] 4 terminal windows ready

### During execution
- [ ] Worktree 1: Specs registered
- [ ] Worktree 2: Scripts registered
- [ ] Worktree 3: Tests/docs registered
- [ ] Worktree 4: Modules registered
- [ ] All changes committed to branches

### Post-execution
- [ ] All branches merged to main
- [ ] Registry conflicts resolved (if any)
- [ ] Final validation passed
- [ ] Worktrees removed
- [ ] Branches deleted

---

## 💡 Best Practices

### For Copilot Instances
1. **One category per instance** - Avoid cross-contamination
2. **Batch register similar items** - Use loops
3. **Commit frequently** - Every 10-15 registrations
4. **Test registry CLI** - Validate before committing

### For Registry Updates
1. **Check next_id** before starting - Avoid number conflicts
2. **Update metadata** - Keep counts accurate
3. **Add to correct section** - Follow YAML structure
4. **Preserve formatting** - Use same indentation

### For Merging
1. **Merge specs first** - Smallest, least conflicts
2. **Merge scripts second** - Clear boundaries
3. **Merge tests third** - Many files, simple
4. **Merge modules last** - Largest, verify carefully

---

## 📈 Success Metrics

### Target Outcomes
- **218 modules registered** in 1.5 hours
- **4 index files created** (SPEC, SCRIPT, TEST, GUIDE)
- **Registry validated** with no errors
- **100% coverage** of critical paths

### Quality Gates
- All doc_ids match regex ✅
- No duplicate IDs ✅
- All categories balanced ✅
- Dependencies documented ✅

---

## 🚀 Ready to Execute

Run this command to start:

```powershell
# Create worktrees
.\scripts\create_docid_worktrees.ps1

# Open 4 terminal windows, then run in each:
# Terminal 1:
cd .worktrees/wt-docid-specs

# Terminal 2:
cd .worktrees/wt-docid-scripts

# Terminal 3:
cd .worktrees/wt-docid-tests-docs

# Terminal 4:
cd .worktrees/wt-docid-modules

# Begin parallel registration!
```

---

**Parallel execution pattern + Git worktrees = 4x speedup**  
**1.5 hours to complete all 218 remaining modules**
