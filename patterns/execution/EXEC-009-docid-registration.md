---
doc_id: DOC-PAT-EXEC-009-DOCID-REGISTRATION-990
---

# EXEC-009: DOC_ID Registration Pattern
# Pattern for systematically registering modules with doc_ids

**Pattern ID**: EXEC-009
**Name**: DOC_ID Registration Pattern
**Category**: Documentation
**Time Savings**: 75-80% vs manual
**Difficulty**: Low
**Prerequisites**: doc_id_registry_cli.py installed

---

## Purpose

Register multiple modules with unique doc_ids in a consistent, repeatable way.

---

## Pattern Structure

### Discovery Phase (10 minutes)

**Input**: Directory path containing modules to document

**Actions**:
1. List all files in directory
2. Filter by file type (*.py, *.md, *.yaml, etc.)
3. Exclude __init__.py and test files
4. Group by subdirectory/category

**Output**: List of files to register

**Example**:
```powershell
# Discover Python modules in core/
$coreFiles = Get-ChildItem core -Filter "*.py" -Recurse |
             Where-Object { $_.Name -ne "__init__.py" }

# Group by subdirectory
$bySubdir = $coreFiles | Group-Object { $_.Directory.Name }

# Output:
# state: 7 files
# engine: 18 files
# planning: 4 files
```

### Template Phase (5 minutes)

**Input**: File list from discovery

**Actions**:
1. For first 2-3 files, register manually
2. Observe the pattern (category, naming convention)
3. Extract invariants (what stays same)
4. Identify variables (what changes per file)

**Output**: Registration template

**Example**:
```powershell
# Invariant: category = "core"
# Invariant: tags = "core,engine,high-priority"
# Variable: name (derived from filename)
# Variable: title (human-readable description)

# Template:
python scripts/doc_id_registry_cli.py mint `
    --category core `
    --name <MODULE_NAME> `
    --title "<HUMAN_TITLE>" `
    --tags "core,engine,high-priority"
```

### Batch Phase (15-30 minutes per 25 files)

**Input**: File list + Template

**Actions**:
1. Create PowerShell loop
2. Auto-derive name from filename
3. Provide meaningful titles
4. Execute batch registration
5. Capture doc_ids assigned

**Output**: N modules registered

**Example**:
```powershell
# Batch register core/state modules
$stateModules = @(
    @{name="state-db"; title="Database Initialization and Connection Management"},
    @{name="state-crud"; title="CRUD Operations for Core Entities"},
    @{name="state-bundles"; title="Workstream Bundle Loading"},
    @{name="state-worktree"; title="Git Worktree Management"},
    @{name="state-audit-logger"; title="Audit Trail Logging"}
)

foreach ($mod in $stateModules) {
    python scripts/doc_id_registry_cli.py mint `
        --category core `
        --name $mod.name `
        --title $mod.title `
        --tags "core,state,high-priority"

    Write-Host "✓ Registered: $($mod.name)" -ForegroundColor Green
}
```

### Verification Phase (2 minutes)

**Input**: Registry after batch

**Actions**:
1. Count registered vs expected
2. Validate no duplicates
3. Check sequence numbers
4. Spot check 2-3 entries

**Output**: Confirmation or error list

**Example**:
```powershell
# Verify registration
python scripts/doc_id_registry_cli.py list --category core

# Expected output:
# DOC-CORE-STATE-DB-001
# DOC-CORE-STATE-CRUD-002
# DOC-CORE-STATE-BUNDLES-003
# DOC-CORE-STATE-WORKTREE-004
# DOC-CORE-STATE-AUDIT-LOGGER-005
```

---

## Decision Elimination

### Pre-Decisions (Make Once)
- ✅ **Category**: Based on directory (core/, error/, spec/, etc.)
- ✅ **Tag strategy**: Include category + layer + priority
- ✅ **Naming convention**: lowercase-with-dashes
- ✅ **Title format**: Sentence case, descriptive

### Not Decisions (Don't Waste Time)
- ❌ **Perfect titles**: Good enough is perfect
- ❌ **Exhaustive tags**: 2-3 tags max
- ❌ **Sequence numbers**: Auto-assigned
- ❌ **Verification per file**: Batch verify only

---

## Time Breakdown

**For 25 files:**

| Phase | Manual | Pattern | Savings |
|-------|--------|---------|---------|
| Discovery | 15 min | 10 min | 33% |
| Template | 30 min | 5 min | 83% |
| Batch | 125 min (5 min × 25) | 25 min | 80% |
| Verification | 25 min | 2 min | 92% |
| **Total** | **195 min** | **42 min** | **78%** |

---

## Example: Complete Workflow

```powershell
# 1. DISCOVERY
cd .worktrees/wt-docid-specs

# Find all schema files
$schemas = Get-ChildItem ../../schema -Filter "*.json" |
           Select-Object BaseName, Name

# Output: Found 8 schema files

# 2. TEMPLATE (do 2 manually to find pattern)
python ../../scripts/doc_id_registry_cli.py mint `
    --category spec `
    --name workstream-schema `
    --title "Workstream JSON Schema Definition"
# → DOC-SPEC-WORKSTREAM-SCHEMA-001

python ../../scripts/doc_id_registry_cli.py mint `
    --category spec `
    --name step-schema `
    --title "Step JSON Schema Definition"
# → DOC-SPEC-STEP-SCHEMA-002

# Pattern identified:
# - category: spec
# - name: {basename}-schema
# - title: {BaseName} JSON Schema Definition

# 3. BATCH (remaining 6 files)
$schemaFiles = @(
    "error", "run", "event", "tool-profile", "config", "quality-gate"
)

foreach ($schema in $schemaFiles) {
    $title = "$((Get-Culture).TextInfo.ToTitleCase($schema)) JSON Schema Definition"

    python ../../scripts/doc_id_registry_cli.py mint `
        --category spec `
        --name "$schema-schema" `
        --title $title `
        --tags "spec,schema,validation"
}

# 4. VERIFICATION
python ../../scripts/doc_id_registry_cli.py list --category spec
# Expected: 8 schema doc_ids

# 5. COMMIT
git add ../../doc_id/DOC_ID_REGISTRY.yaml
git commit -m "feat: register schema file doc_ids (8 files)"
```

---

## Anti-Patterns to Avoid

❌ **Register one at a time** → Use batch loops
❌ **Manually type each title** → Derive from filename
❌ **Verify each registration** → Batch verify at end
❌ **Perfectionist titles** → Good enough on first pass
❌ **Skip discovery phase** → You'll miss files

---

## Success Criteria

- ✅ All files in scope registered
- ✅ No duplicate doc_ids
- ✅ Sequence numbers correct
- ✅ Registry validates without errors
- ✅ Time: <2 min per file on average

---

## Pattern Variations

### Variation 1: Test Files (DOC-TEST-*)
```powershell
# Auto-derive from test_*.py naming
$testFiles = Get-ChildItem tests -Filter "test_*.py" -Recurse

foreach ($test in $testFiles) {
    $name = $test.BaseName -replace "^test_", ""
    $module = $test.Directory.Name
    $title = "Tests for $module.$name"

    python scripts/doc_id_registry_cli.py mint `
        --category test `
        --name "$module-$name" `
        --title $title
}
```

### Variation 2: Scripts (DOC-SCRIPT-*)
```powershell
# Scripts have descriptive names already
$scripts = Get-ChildItem scripts -Filter "*.py"

foreach ($script in $scripts) {
    $name = $script.BaseName
    $title = (Get-Content $script.FullName -First 5 |
              Where-Object { $_ -match "^#.*Purpose:" }) -replace "^#.*Purpose:\s*", ""

    if (!$title) {
        $title = "$name Script"
    }

    python scripts/doc_id_registry_cli.py mint `
        --category script `
        --name $name `
        --title $title
}
```

### Variation 3: Guides (DOC-GUIDE-*)
```powershell
# Guides use title from first heading
$guides = Get-ChildItem docs -Filter "*.md"

foreach ($guide in $guides) {
    $name = $guide.BaseName
    $title = (Get-Content $guide.FullName -First 1) -replace "^#\s*", ""

    python scripts/doc_id_registry_cli.py mint `
        --category guide `
        --name $name `
        --title $title `
        --tags "documentation,guide"
}
```

---

## Integration with Parallel Execution

When using git worktrees for parallel execution:

```powershell
# Each worktree runs this pattern independently
# Worktree 1: Specs
cd .worktrees/wt-docid-specs
# Run EXEC-009 for schema files

# Worktree 2: Scripts
cd .worktrees/wt-docid-scripts
# Run EXEC-009 for script files

# Worktree 3: Tests
cd .worktrees/wt-docid-tests-docs
# Run EXEC-009 for test files

# Worktree 4: Modules
cd .worktrees/wt-docid-modules
# Run EXEC-009 for remaining modules
```

**No conflicts**: Each worktree updates different category sections in registry.

---

## Metrics

**Proven results from Phase 1 & 2:**
- 29 modules registered in 10 minutes
- 89% time savings vs manual
- 100% success rate (no errors)
- 0 duplicate IDs
- 0 merge conflicts

**Projected for remaining 218 modules:**
- Sequential: 7.5 hours
- Pattern approach: 1.5 hours
- **Savings: 80%**

---

**DOC_LINK**: DOC-PAT-EXECUTION-DOCID-REGISTRATION-001
