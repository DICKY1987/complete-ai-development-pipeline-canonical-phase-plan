# DOC_ID Parallel Execution Guide
# Complete workflow using EXEC-009, EXEC-010, and EXEC-011

**Purpose**: Register all 218 remaining modules with doc_ids in ~2 hours using parallel execution  
**Patterns Used**: EXEC-009, EXEC-010, EXEC-011  
**Time Savings**: 73% vs sequential approach

---

## 🎯 Overview

**Goal**: Complete repository-wide doc_id registration

**Strategy**: 
- 4 parallel git worktrees
- Each handles one category independently
- Sequential merge at end
- Total time: ~2 hours (vs 7+ hours sequential)

**Success Criteria**:
- ✅ 247/247 modules documented (100%)
- ✅ Registry validates without errors
- ✅ All index files created
- ✅ No merge conflicts

---

## 📋 Preparation Checklist

### Before Starting

- [ ] All current work committed to main
- [ ] Registry currently valid: `python scripts/doc_id_registry_cli.py validate`
- [ ] 4 worktrees created: `git worktree list`
- [ ] 4 terminal windows or VS Code instances ready
- [ ] Patterns reviewed: EXEC-009, EXEC-010, EXEC-011

### Verify Current State

```powershell
# Check current progress
python scripts/doc_id_registry_cli.py stats
# Expected: Total docs: 29

# List worktrees
git worktree list
# Expected: 4 docid worktrees + main
```

---

## 🚀 Phase 1: Parallel Registration (1-1.5 hours)

Each worktree works independently. **Choose a worktree below and execute:**

### Worktree 1: Specifications & Schemas (30 min)

**Terminal 1:**
```powershell
cd .worktrees/wt-docid-specs

# 1. Discover schema files
$schemas = Get-ChildItem ../../schema -Filter "*.json"
Write-Host "Found $($schemas.Count) schema files"

# 2. Register schemas (EXEC-009)
$schemaList = @(
    @{name="workstream-schema"; title="Workstream JSON Schema Definition"},
    @{name="step-schema"; title="Step JSON Schema Definition"},
    @{name="error-schema"; title="Error JSON Schema Definition"},
    @{name="run-schema"; title="Run JSON Schema Definition"},
    @{name="event-schema"; title="Event JSON Schema Definition"},
    @{name="tool-profile-schema"; title="Tool Profile Schema Definition"},
    @{name="config-schema"; title="Configuration Schema Definition"},
    @{name="quality-gate-schema"; title="Quality Gate Schema Definition"}
)

foreach ($schema in $schemaList) {
    python ../../scripts/doc_id_registry_cli.py mint `
        --category spec `
        --name $schema.name `
        --title $schema.title `
        --tags "spec,schema,validation"
    Write-Host "✓ Registered: $($schema.name)" -ForegroundColor Green
}

# 3. Discover config files
$configs = Get-ChildItem ../../config -Filter "*.yaml"
Write-Host "Found $($configs.Count) config files"

# Register configs
foreach ($config in $configs) {
    $name = $config.BaseName
    python ../../scripts/doc_id_registry_cli.py mint `
        --category config `
        --name $name `
        --title "$name Configuration" `
        --tags "config,configuration"
}

# 4. Create SPEC_INDEX.yaml (EXEC-010)
# Copy template from CORE_MODULE_INDEX.yaml and adapt

Copy-Item ../../core/CORE_MODULE_INDEX.yaml ../../specifications/SPEC_INDEX.yaml
# Edit file to match specifications category structure

# 5. Commit (EXEC-011)
git add ../../DOC_ID_REGISTRY.yaml
git add ../../specifications/SPEC_INDEX.yaml
git commit -m "feat: register specification and config doc_ids (25 files)

- Register 8 JSON schema files
- Register 17 config files
- Create SPEC_INDEX.yaml with validation metadata
- Update registry metadata (total: 54 docs)

Categories: DOC-SPEC-*, DOC-CONFIG-*
Pattern: EXEC-009, EXEC-010, EXEC-011"

Write-Host "`n✅ Worktree 1 complete!" -ForegroundColor Green
```

### Worktree 2: Scripts & Tools (30 min)

**Terminal 2:**
```powershell
cd .worktrees/wt-docid-scripts

# 1. Discover script files
$scripts = Get-ChildItem ../../scripts -Filter "*.py" | 
           Where-Object { $_.BaseName -ne "__init__" }
Write-Host "Found $($scripts.Count) script files"

# 2. Register scripts (EXEC-009)
foreach ($script in $scripts) {
    $name = $script.BaseName
    
    # Try to extract purpose from docstring
    $firstLines = Get-Content $script.FullName -First 10
    $purpose = ($firstLines | Where-Object { $_ -match "Purpose:|DOC_LINK:" } | Select-Object -First 1)
    
    if ($purpose -match "Purpose:\s*(.+)") {
        $title = $matches[1].Trim()
    } else {
        $title = "$name Script"
    }
    
    python ../../scripts/doc_id_registry_cli.py mint `
        --category script `
        --name $name `
        --title $title `
        --tags "automation,tools,script"
    
    Write-Host "✓ Registered: $name" -ForegroundColor Green
}

# 3. Create SCRIPT_INDEX.yaml (EXEC-010)
# Group by function: validation, generation, analysis, etc.

@"
# SCRIPT_INDEX.yaml
# Index of automation scripts and tools
# Generated: $(Get-Date -Format 'yyyy-MM-dd')

metadata:
  category: script
  description: "Automation scripts and CLI tools"
  total_scripts: $($scripts.Count)
  last_updated: "$(Get-Date -Format 'yyyy-MM-dd')"

validation_scripts:
  - doc_id: DOC-SCRIPT-VALIDATE-WORKSTREAMS-004
    name: validate_workstreams
    file: scripts/validate_workstreams.py
    purpose: "Validate workstream JSON files"
    usage: "python scripts/validate_workstreams.py [path]"
  
# ... add remaining scripts ...

"@ | Out-File ../../scripts/SCRIPT_INDEX.yaml

# 4. Commit (EXEC-011)
git add ../../DOC_ID_REGISTRY.yaml
git add ../../scripts/SCRIPT_INDEX.yaml
git commit -m "feat: register script doc_ids (26 files)

- Register 26 automation scripts
- Create SCRIPT_INDEX.yaml with usage info
- Group by function (validation, generation, analysis)

Categories: DOC-SCRIPT-*
Pattern: EXEC-009, EXEC-010, EXEC-011"

Write-Host "`n✅ Worktree 2 complete!" -ForegroundColor Green
```

### Worktree 3: Tests & Documentation (45 min)

**Terminal 3:**
```powershell
cd .worktrees/wt-docid-tests-docs

# 1. Discover test files
$tests = Get-ChildItem ../../tests -Filter "test_*.py" -Recurse
Write-Host "Found $($tests.Count) test files"

# 2. Register tests (EXEC-009)
foreach ($test in $tests) {
    $name = $test.BaseName -replace "^test_", ""
    $module = $test.Directory.Name
    $title = "Tests for $module.$name"
    
    python ../../scripts/doc_id_registry_cli.py mint `
        --category test `
        --name "$module-$name" `
        --title $title `
        --tags "test,testing,quality"
    
    Write-Host "✓ Registered: test_$name" -ForegroundColor Green
}

# 3. Discover guide files
$guides = Get-ChildItem ../../docs -Filter "*.md"
Write-Host "Found $($guides.Count) guide files"

# Register guides
foreach ($guide in $guides) {
    $name = $guide.BaseName
    # Extract title from first heading
    $title = (Get-Content $guide.FullName -First 1) -replace "^#\s*", ""
    
    python ../../scripts/doc_id_registry_cli.py mint `
        --category guide `
        --name $name `
        --title $title `
        --tags "documentation,guide"
}

# 4. Create TEST_INDEX.yaml and GUIDE_INDEX.yaml (EXEC-010)
# ... create index files ...

# 5. Commit (EXEC-011)
git add ../../DOC_ID_REGISTRY.yaml
git add ../../tests/TEST_INDEX.yaml
git add ../../docs/GUIDE_INDEX.yaml
git commit -m "feat: register test and guide doc_ids (70 files)

- Register 60 test files
- Register 10 guide/documentation files
- Create TEST_INDEX.yaml and GUIDE_INDEX.yaml

Categories: DOC-TEST-*, DOC-GUIDE-*
Pattern: EXEC-009, EXEC-010, EXEC-011"

Write-Host "`n✅ Worktree 3 complete!" -ForegroundColor Green
```

### Worktree 4: Remaining Modules (1 hour)

**Terminal 4:**
```powershell
cd .worktrees/wt-docid-modules

# 1. Discover remaining core modules
$coreRemaining = Get-ChildItem ../../core -Filter "*.py" -Recurse | 
                 Where-Object { 
                     $_.Name -ne "__init__.py" -and
                     $_.DirectoryName -notmatch "state|engine"  # Already registered
                 }
Write-Host "Found $($coreRemaining.Count) remaining core modules"

# 2. Discover AIM modules
$aimModules = Get-ChildItem ../../aim -Filter "*.py" -Recurse |
              Where-Object { $_.Name -ne "__init__.py" }
Write-Host "Found $($aimModules.Count) AIM modules"

# 3. Discover PM modules
$pmModules = Get-ChildItem ../../pm -Filter "*.py" -Recurse |
             Where-Object { $_.Name -ne "__init__.py" }
Write-Host "Found $($pmModules.Count) PM modules"

# 4. Register all (EXEC-009)
# Core modules
foreach ($mod in $coreRemaining) {
    $category = $mod.Directory.Name
    $name = "$category-$($mod.BaseName)"
    
    python ../../scripts/doc_id_registry_cli.py mint `
        --category core `
        --name $name `
        --title "$category Module: $($mod.BaseName)"
}

# AIM modules
foreach ($mod in $aimModules) {
    python ../../scripts/doc_id_registry_cli.py mint `
        --category aim `
        --name $mod.BaseName `
        --title "AIM: $($mod.BaseName)"
}

# PM modules
foreach ($mod in $pmModules) {
    python ../../scripts/doc_id_registry_cli.py mint `
        --category pm `
        --name $mod.BaseName `
        --title "PM: $($mod.BaseName)"
}

# 5. Update index files (EXEC-010)
# Update CORE_MODULE_INDEX.yaml with new entries
# Create AIM_INDEX.yaml
# Create PM_INDEX.yaml

# 6. Commit (EXEC-011)
git add ../../DOC_ID_REGISTRY.yaml
git add ../../core/CORE_MODULE_INDEX.yaml
git add ../../aim/AIM_INDEX.yaml
git add ../../pm/PM_INDEX.yaml
git commit -m "feat: register remaining module doc_ids (107 files)

- Register 64 remaining core modules
- Register 28 AIM modules
- Register 15 PM modules
- Update CORE_MODULE_INDEX.yaml
- Create AIM_INDEX.yaml and PM_INDEX.yaml

Categories: DOC-CORE-*, DOC-AIM-*, DOC-PM-*
Pattern: EXEC-009, EXEC-010, EXEC-011"

Write-Host "`n✅ Worktree 4 complete!" -ForegroundColor Green
```

---

## 🔄 Phase 2: Sequential Merge (20 minutes)

**Return to main repository:**

```powershell
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Ensure all worktrees are committed
git worktree list
# All should show same commit hash

# Merge in recommended order (EXEC-011)

# 1. Merge specs (5 min)
Write-Host "`n1️⃣ Merging feature/docid-specs..." -ForegroundColor Cyan
git merge feature/docid-specs --no-ff -m "merge: add specification and config doc_ids"
python scripts/doc_id_registry_cli.py validate
Write-Host "✅ Specs merged" -ForegroundColor Green

# 2. Merge scripts (5 min)
Write-Host "`n2️⃣ Merging feature/docid-scripts..." -ForegroundColor Cyan
git merge feature/docid-scripts --no-ff -m "merge: add script doc_ids"
python scripts/doc_id_registry_cli.py validate
Write-Host "✅ Scripts merged" -ForegroundColor Green

# 3. Merge tests/docs (5 min)
Write-Host "`n3️⃣ Merging feature/docid-tests-docs..." -ForegroundColor Cyan
git merge feature/docid-tests-docs --no-ff -m "merge: add test and guide doc_ids"
python scripts/doc_id_registry_cli.py validate
Write-Host "✅ Tests/docs merged" -ForegroundColor Green

# 4. Merge modules (5 min)
Write-Host "`n4️⃣ Merging feature/docid-modules..." -ForegroundColor Cyan
git merge feature/docid-modules --no-ff -m "merge: add remaining module doc_ids"
python scripts/doc_id_registry_cli.py validate
Write-Host "✅ Modules merged" -ForegroundColor Green

Write-Host "`n✅ All merges complete!" -ForegroundColor Green
```

---

## 🧹 Phase 3: Cleanup & Verification (5 minutes)

```powershell
# 1. Clean up worktrees
Write-Host "`n🧹 Cleaning up worktrees..." -ForegroundColor Yellow
.\scripts\create_docid_worktrees.ps1 -Cleanup

# 2. Final verification
Write-Host "`n📊 Final Statistics:" -ForegroundColor Cyan
python scripts/doc_id_registry_cli.py stats

# Expected output:
# Total docs: 247
# By category:
#   core: 74
#   error: 10
#   spec: 8
#   config: 17
#   script: 30
#   test: 60
#   guide: 10
#   aim: 28
#   pm: 15
#   patterns: 4

# 3. Validate final state
python scripts/doc_id_registry_cli.py validate
# Expected: ✅ Registry valid

# 4. Check created index files
$indexes = @(
    "specifications/SPEC_INDEX.yaml",
    "scripts/SCRIPT_INDEX.yaml",
    "tests/TEST_INDEX.yaml",
    "docs/GUIDE_INDEX.yaml",
    "aim/AIM_INDEX.yaml",
    "pm/PM_INDEX.yaml"
)

foreach ($index in $indexes) {
    if (Test-Path $index) {
        Write-Host "✅ $index" -ForegroundColor Green
    } else {
        Write-Host "❌ $index missing" -ForegroundColor Red
    }
}

# 5. Final commit
git add .
git commit -m "chore: complete doc_id project (247/247 modules documented)

- All repository modules registered with doc_ids
- 6 category index files created
- Registry validated and verified
- Time saved: 73% vs sequential approach

Patterns: EXEC-009, EXEC-010, EXEC-011"

Write-Host "`n🎉 DOC_ID Project Complete!" -ForegroundColor Green
Write-Host "   Modules documented: 247/247 (100%)" -ForegroundColor Cyan
Write-Host "   Time invested: ~2 hours" -ForegroundColor Cyan
Write-Host "   Time saved: ~5 hours (73%)" -ForegroundColor Cyan
```

---

## ⏱️ Time Tracking

| Phase | Estimated | Actual |
|-------|-----------|--------|
| Worktree 1: Specs | 30 min | ___ |
| Worktree 2: Scripts | 30 min | ___ |
| Worktree 3: Tests/Docs | 45 min | ___ |
| Worktree 4: Modules | 60 min | ___ |
| **Parallel Work** | **1.5 hours** | **___** |
| Sequential Merges | 20 min | ___ |
| Cleanup & Verify | 5 min | ___ |
| **Total** | **~2 hours** | **___** |

---

## ✅ Completion Checklist

- [ ] All 4 worktrees completed
- [ ] All branches merged to main
- [ ] Registry validates: `python scripts/doc_id_registry_cli.py validate`
- [ ] Total docs = 247: `python scripts/doc_id_registry_cli.py stats`
- [ ] 6 index files created
- [ ] Worktrees cleaned up
- [ ] Final commit pushed
- [ ] Celebration! 🎉

---

## 🆘 Troubleshooting

### Problem: Merge conflicts in registry
**Solution**: See EXEC-011 conflict resolution section

### Problem: Validation fails after merge
**Solution**: Check for duplicate doc_ids, fix sequence numbers manually

### Problem: Missing index file
**Solution**: Re-create using EXEC-010 pattern in that worktree

### Problem: Worktree shows uncommitted changes
**Solution**: Commit all changes before merging to main

---

## 📊 Success Metrics

**Target Outcomes:**
- ✅ 247 modules documented (100% coverage)
- ✅ 6 category indexes created
- ✅ Registry validated
- ✅ Total time < 2.5 hours
- ✅ 73% time savings

**Quality Gates:**
- All doc_ids match regex pattern
- No duplicate IDs
- All sequence numbers correct
- All file paths valid
- Dependencies documented

---

**This guide combines EXEC-009, EXEC-010, and EXEC-011 into a complete workflow.**  
**Follow terminal-by-terminal for parallel execution and systematic completion.**

**DOC_LINK**: DOC-GUIDE-DOCID-PARALLEL-EXECUTION-001
