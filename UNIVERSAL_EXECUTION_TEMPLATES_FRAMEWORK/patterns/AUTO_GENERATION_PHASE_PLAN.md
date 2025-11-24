# AUTO-GENERATION PHASE PLAN
# Pattern File Generation - Complete Implementation
# Version: 1.0.0
# Created: 2025-11-24T13:28:00Z
# Status: READY_TO_EXECUTE

## 0. Executive Summary

**Goal:** Generate 100+ missing pattern framework files using automated pattern-based generation

**Scope:** 
- 40 schema files
- 46 example JSON instances  
- 10 test scaffolds
- 24 sidecar ID files
- 32 doc_id updates
- 2 validation scripts
- 3 domain schema files

**Time Estimate:** 2-3 hours (vs 40-50 hours manual)
**Success Criteria:** All files pass PAT-CHECK-001 compliance validation

---

## 1. Phase Overview

### Phase Structure

```
PHASE 1: ID System Implementation (CRITICAL PATH)
├── Generate doc_id values for all 24 patterns
├── Update PATTERN_INDEX.yaml with doc_id fields
├── Update 7 spec files with doc_id fields
├── Generate 24 schema sidecar .id.yaml files
└── Add DOC_LINK headers to executor

PHASE 2: Core Pattern Artifacts (HIGH PRIORITY)
├── Generate 6 missing schemas from specs
├── Generate 18 example JSON files (6 patterns × 3 types)
├── Generate 6 missing executors from template
└── Generate 7 test files

PHASE 3: Migrated Pattern Artifacts (MEDIUM PRIORITY)
├── Generate 17 migrated schemas
├── Generate 17 migrated example directories
└── Generate 17 migrated executor scaffolds

PHASE 4: Validation & Domain Schemas (RECOMMENDED)
├── Generate PATTERN_DIR_CHECK.ps1 validator
├── Generate validate_doc_id_consistency.ps1
├── Generate 3 domain schema files
└── Generate pattern test infrastructure
```

---

## 2. Generation Pattern Definition

### Pattern Name: `batch_file_generation_from_spec`

**Purpose:** Generate multiple related files from a single specification source

**Pattern Type:** Parallel execution with sequential validation

**Inputs:**
- Source specifications (pattern specs, schemas, registry)
- Templates (executor template, test template, schema template)
- Generation rules (ID-SYSTEM-SPEC-V1, PAT-CHECK-001)

**Outputs:**
- Generated files in correct directory structure
- Validation report
- Compliance check results

**Pattern Definition:**

```yaml
pattern_id: PAT-BATCH-FILE-GEN-001
name: batch_file_generation_from_spec
version: "1.0.0"

execution_strategy:
  type: parallel_batches
  batch_size: 10
  validation_mode: per_batch
  
steps:
  - step_id: S1_parse_source_specs
    description: Parse all source specifications
    outputs:
      - pattern_metadata[]
      - template_mappings[]
    
  - step_id: S2_generate_doc_ids
    description: Generate RFC-compliant doc_id values
    algorithm: pattern_id_to_doc_id
    rules:
      - "PAT-ATOMIC-CREATE-001 → DOC-ATOMIC-CREATE-001"
      - "PAT-MIGRATED-CORE-003 → DOC-MIGRATED-CORE-003"
    
  - step_id: S3_parallel_file_generation
    description: Generate all files in parallel batches
    parallel_groups:
      - group: schemas
        files: 40
        template: schema_from_spec
      - group: examples
        files: 46
        template: example_from_schema
      - group: tests
        files: 10
        template: test_from_pattern
      - group: sidecars
        files: 24
        template: sidecar_id_from_doc_id
    
  - step_id: S4_batch_validation
    description: Validate each batch after generation
    validations:
      - syntax_check
      - schema_compliance
      - file_exists_check
      
  - step_id: S5_update_existing_files
    description: Update existing files with doc_id
    strategy: surgical_edits
    files:
      - patterns/registry/PATTERN_INDEX.yaml
      - patterns/specs/*.pattern.yaml
      - patterns/executors/atomic_create_executor.ps1
      
  - step_id: S6_final_compliance_check
    description: Run PAT-CHECK-001 compliance validation
    script: PATTERN_DIR_CHECK.ps1
```

---

## 3. Detailed Phase Execution Plan

### PHASE 1: ID System Implementation

**Duration:** 30 minutes  
**Priority:** CRITICAL (blocks other phases)

#### Steps:

**1.1 Generate doc_id Mapping Table**
```powershell
# Input: PATTERN_INDEX.yaml (24 patterns)
# Output: doc_id_mapping.json

pattern_id                    → doc_id
PAT-ATOMIC-CREATE-001         → DOC-ATOMIC-CREATE-001
PAT-BATCH-CREATE-001          → DOC-BATCH-CREATE-001
...
PAT-MIGRATED-CORE-017         → DOC-MIGRATED-CORE-017
```

**1.2 Update PATTERN_INDEX.yaml**
```yaml
# Add doc_id field to each pattern entry
patterns:
  - pattern_id: PAT-ATOMIC-CREATE-001
    doc_id: DOC-ATOMIC-CREATE-001  # <-- ADD THIS
    name: atomic_create
    ...
```

**1.3 Update Spec Files**
```yaml
# Add to each patterns/specs/*.pattern.yaml
doc_id: DOC-ATOMIC-CREATE-001  # <-- ADD AT TOP
pattern_id: PAT-ATOMIC-CREATE-001
name: atomic_create
...
```

**1.4 Generate Schema Sidecar Files**
```yaml
# Create patterns/schemas/*.schema.id.yaml for each pattern
schema_path: patterns/schemas/atomic_create.schema.json
doc_id: DOC-ATOMIC-CREATE-001
pattern_id: PAT-ATOMIC-CREATE-001
role: schema
linked_spec: patterns/specs/atomic_create.pattern.yaml
```

**1.5 Add DOC_LINK Headers**
```powershell
# Add to patterns/executors/atomic_create_executor.ps1
# DOC_LINK: DOC-ATOMIC-CREATE-001
# Pattern: atomic_create (PAT-ATOMIC-CREATE-001)
...
```

**Validation:**
- [ ] All 24 patterns have doc_id in registry
- [ ] All 7 spec files have doc_id field
- [ ] All 24 sidecar files created
- [ ] Executor has DOC_LINK header
- [ ] All doc_id values match format [A-Z0-9]+(-[A-Z0-9]+)*

---

### PHASE 2: Core Pattern Artifacts

**Duration:** 45 minutes  
**Priority:** HIGH

#### 2.1 Generate Schemas (6 files)

**Source:** patterns/specs/*.pattern.yaml  
**Template:** atomic_create.schema.json  
**Output:** patterns/schemas/

```json
// patterns/schemas/batch_create.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "batch_create.schema.json",
  "title": "Batch Create Pattern Instance",
  "description": "Schema for batch_create pattern instances",
  "type": "object",
  "required": ["pattern_id", "doc_id", "inputs"],
  "properties": {
    "doc_id": { "type": "string", "pattern": "^DOC-[A-Z0-9-]+$" },
    "pattern_id": { "const": "PAT-BATCH-CREATE-001" },
    "inputs": { /* derived from spec */ }
  }
}
```

**Generation Algorithm:**
1. Parse spec file's `inputs` section
2. Convert to JSON Schema properties
3. Add required fields: doc_id, pattern_id, inputs, outputs
4. Inject pattern-specific constraints

**Files to Generate:**
- batch_create.schema.json
- refactor_patch.schema.json
- self_heal.schema.json
- verify_commit.schema.json
- worktree_lifecycle.schema.json
- module_creation.schema.json

---

#### 2.2 Generate Examples (18 files)

**Source:** Generated schemas  
**Template:** patterns/examples/atomic_create/  
**Output:** patterns/examples/{pattern_name}/

For each pattern, generate 3 files:

**instance_minimal.json** - Minimal valid instance
```json
{
  "doc_id": "DOC-BATCH-CREATE-001",
  "pattern_id": "PAT-BATCH-CREATE-001",
  "inputs": {
    "project_root": "C:\\Projects\\MyApp",
    "files_to_create": [
      {
        "path": "src/example.py",
        "file_type": "implementation"
      }
    ]
  }
}
```

**instance_full.json** - Comprehensive example
```json
{
  "doc_id": "DOC-BATCH-CREATE-001",
  "pattern_id": "PAT-BATCH-CREATE-001",
  "inputs": { /* all fields populated */ },
  "metadata": { /* optional metadata */ }
}
```

**instance_test.json** - Test scenario
```json
{
  "doc_id": "DOC-BATCH-CREATE-001",
  "pattern_id": "PAT-BATCH-CREATE-001",
  "inputs": { /* test-specific values */ }
}
```

**Patterns:**
- batch_create (3 files)
- refactor_patch (3 files)
- self_heal (3 files)
- verify_commit (3 files)
- worktree_lifecycle (3 files)
- module_creation (3 files)

---

#### 2.3 Generate Executors (6 files)

**Source:** patterns/executors/atomic_create_executor.ps1  
**Template:** Executor scaffold  
**Output:** patterns/executors/

```powershell
# patterns/executors/batch_create_executor.ps1

# DOC_LINK: DOC-BATCH-CREATE-001
# Pattern: batch_create (PAT-BATCH-CREATE-001)
# Version: 1.0.0
# Purpose: Execute batch_create pattern instances

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

# TODO: Implement batch_create execution logic
# See patterns/specs/batch_create.pattern.yaml for details

Write-Host "Executing batch_create pattern..." -ForegroundColor Cyan
# Implementation goes here
```

**Files:**
- batch_create_executor.ps1
- refactor_patch_executor.ps1
- self_heal_executor.ps1
- verify_commit_executor.ps1
- worktree_lifecycle_executor.ps1
- module_creation_executor.ps1

---

#### 2.4 Generate Tests (7 files)

**Source:** Pattern specs + executor files  
**Template:** Pester test scaffold  
**Output:** patterns/tests/

```powershell
# patterns/tests/test_batch_create_executor.ps1

# DOC_LINK: DOC-BATCH-CREATE-001
# Tests for batch_create pattern executor

Describe "batch_create_executor" {
    
    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\batch_create_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\batch_create\instance_minimal.json"
    }
    
    It "Should exist" {
        Test-Path $ExecutorPath | Should -Be $true
    }
    
    It "Should accept InstancePath parameter" {
        # Test parameter validation
    }
    
    It "Should execute minimal instance successfully" {
        # Test execution
    }
    
    It "Should validate instance against schema" {
        # Test schema validation
    }
}
```

**Files:**
- test_atomic_create_executor.ps1
- test_batch_create_executor.ps1
- test_refactor_patch_executor.ps1
- test_self_heal_executor.ps1
- test_verify_commit_executor.ps1
- test_worktree_lifecycle_executor.ps1
- test_module_creation_executor.ps1

---

### PHASE 3: Migrated Pattern Artifacts

**Duration:** 45 minutes  
**Priority:** MEDIUM

#### 3.1 Generate Migrated Schemas (17 files)

**Source:** patterns/legacy_atoms/converted/specs/*.pattern.yaml  
**Output:** patterns/legacy_atoms/converted/schemas/

Same algorithm as Phase 2.1, but for migrated patterns.

**Files:** 17 schema files for migrated_* patterns

---

#### 3.2 Generate Migrated Examples (17 directories)

**Output:** patterns/legacy_atoms/converted/examples/{pattern_name}/

Each directory contains:
- instance_minimal.json

**Files:** 17 directories with 1 file each = 17 files

---

#### 3.3 Generate Migrated Executors (17 files)

**Source:** Template executor  
**Output:** patterns/legacy_atoms/converted/executors/

```python
# patterns/legacy_atoms/converted/executors/migrated_orchestrator_001_executor.py

# DOC_LINK: DOC-MIGRATED-ORCHESTRATE-001
# Pattern: migrated_orchestrator_001 (PAT-MIGRATED-ORCHESTRATE-001)
# Migrated from: atomic-workflow-system

def execute_pattern(instance_path: str):
    """Execute migrated_orchestrator_001 pattern."""
    # TODO: Implement migrated pattern logic
    pass

if __name__ == "__main__":
    import sys
    execute_pattern(sys.argv[1])
```

**Files:** 17 Python executors

---

### PHASE 4: Validation & Domain Schemas

**Duration:** 30 minutes  
**Priority:** RECOMMENDED

#### 4.1 Generate PATTERN_DIR_CHECK.ps1

**Source:** PAT-CHECK-001 spec requirements  
**Output:** scripts/PATTERN_DIR_CHECK.ps1

```powershell
# scripts/PATTERN_DIR_CHECK.ps1
# Validates patterns/ directory against PAT-CHECK-001 compliance

param([switch]$Verbose)

$results = @{}

# Check PAT-CHECK-001-001: patterns/ directory exists
$results["PAT-CHECK-001-001"] = Test-Path "patterns"

# Check PAT-CHECK-001-002: Required subdirectories exist
$requiredDirs = @("registry", "specs", "schemas", "executors", "examples", "tests")
foreach ($dir in $requiredDirs) {
    $results["PAT-CHECK-001-002-$dir"] = Test-Path "patterns/$dir"
}

# Check PAT-CHECK-001-010: PATTERN_INDEX.yaml exists
$results["PAT-CHECK-001-010"] = Test-Path "patterns/registry/PATTERN_INDEX.yaml"

# ... (implement all PAT-CHECK-001 requirements)

# Output results
$passed = ($results.Values | Where-Object { $_ -eq $true }).Count
$failed = ($results.Values | Where-Object { $_ -eq $false }).Count

Write-Host "`nPAT-CHECK-001 Compliance Results:" -ForegroundColor Cyan
Write-Host "  PASSED: $passed" -ForegroundColor Green
Write-Host "  FAILED: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`n✓ FULL COMPLIANCE" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ COMPLIANCE FAILURES" -ForegroundColor Red
    exit 1
}
```

---

#### 4.2 Generate validate_doc_id_consistency.ps1

**Source:** ID-SYSTEM-SPEC-V1  
**Output:** scripts/validate_doc_id_consistency.ps1

```powershell
# scripts/validate_doc_id_consistency.ps1
# Validates doc_id consistency across all artifacts

# Check format compliance (ID-SYS-101)
# Check cross-artifact linkage (PAT-CHECK-001-070)
# Report inconsistencies
```

---

#### 4.3 Generate Domain Schemas (3 files)

**Output:** schema/

**pattern_spec.v1.json** - Schema for pattern specification files
**pattern_instance.v1.json** - Schema for pattern instance files
**pattern_execution_result.v1.json** - Schema for execution results

---

#### 4.4 Generate Pattern Test Infrastructure

**Output:** tests/patterns/

```
tests/patterns/
├── __init__.py
├── test_pattern_registry.py
└── test_doc_id_compliance.py
```

---

## 4. Generation Execution Scripts

### Master Generation Script

**File:** `scripts/generate_all_pattern_files.ps1`

```powershell
# scripts/generate_all_pattern_files.ps1
# Master script to generate all missing pattern files

param(
    [switch]$Phase1Only,
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$baseDir = $PSScriptRoot | Split-Path -Parent

Write-Host "=== PATTERN FILE AUTO-GENERATION ===" -ForegroundColor Cyan
Write-Host "Base Directory: $baseDir" -ForegroundColor Gray
Write-Host ""

# Load generation modules
. "$PSScriptRoot/generators/doc_id_generator.ps1"
. "$PSScriptRoot/generators/schema_generator.ps1"
. "$PSScriptRoot/generators/example_generator.ps1"
. "$PSScriptRoot/generators/executor_generator.ps1"
. "$PSScriptRoot/generators/test_generator.ps1"
. "$PSScriptRoot/generators/validation_generator.ps1"

$totalFiles = 0
$totalGenerated = 0
$totalFailed = 0

# PHASE 1: ID System
Write-Host "[PHASE 1] ID System Implementation" -ForegroundColor Yellow
$phase1 = @{
    "Generate doc_id mappings" = { Generate-DocIdMappings }
    "Update PATTERN_INDEX.yaml" = { Update-PatternIndexWithDocId }
    "Update spec files" = { Update-SpecFilesWithDocId }
    "Generate sidecar files" = { Generate-SchemaSidecarFiles }
    "Add DOC_LINK headers" = { Add-DocLinkHeaders }
}

foreach ($task in $phase1.Keys) {
    Write-Host "  $task..." -NoNewline
    try {
        if (-not $DryRun) {
            $result = & $phase1[$task]
            $totalGenerated += $result.FilesGenerated
        }
        Write-Host " ✓" -ForegroundColor Green
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        $totalFailed++
    }
}

if ($Phase1Only) {
    Write-Host "`nPhase 1 complete. Exiting (Phase1Only flag set)." -ForegroundColor Cyan
    exit 0
}

# PHASE 2: Core Pattern Artifacts
Write-Host "`n[PHASE 2] Core Pattern Artifacts" -ForegroundColor Yellow
# ... (similar structure for remaining phases)

# Final Report
Write-Host "`n=== GENERATION COMPLETE ===" -ForegroundColor Green
Write-Host "Files Generated: $totalGenerated" -ForegroundColor Cyan
Write-Host "Files Failed:    $totalFailed" -ForegroundColor $(if ($totalFailed -eq 0) { "Green" } else { "Red" })
```

---

## 5. Validation Checkpoints

### Per-Phase Validation

**Phase 1 Validation:**
```powershell
# Verify all patterns have doc_id
$index = Get-Content "patterns/registry/PATTERN_INDEX.yaml" -Raw
$patterns = ($index | ConvertFrom-Yaml).patterns
$missingDocId = $patterns | Where-Object { -not $_.doc_id }
if ($missingDocId.Count -gt 0) { throw "Missing doc_id in patterns" }
```

**Phase 2 Validation:**
```powershell
# Verify all schemas are valid JSON
Get-ChildItem "patterns/schemas/*.schema.json" | ForEach-Object {
    $json = Get-Content $_ -Raw | ConvertFrom-Json
    # Validation passed if no error
}
```

**Final Validation:**
```powershell
# Run PAT-CHECK-001 compliance check
& scripts/PATTERN_DIR_CHECK.ps1
if ($LASTEXITCODE -ne 0) {
    throw "PAT-CHECK-001 compliance check failed"
}
```

---

## 6. Success Criteria

- [ ] All 24 patterns have doc_id in PATTERN_INDEX.yaml
- [ ] All 7 spec files have doc_id field
- [ ] All 24 sidecar .id.yaml files exist
- [ ] All 6 core schemas generated and valid
- [ ] All 18 core examples generated and valid
- [ ] All 6 core executors generated with DOC_LINK
- [ ] All 7 test files generated
- [ ] All 17 migrated schemas generated
- [ ] All 17 migrated examples generated
- [ ] All 17 migrated executors generated
- [ ] PATTERN_DIR_CHECK.ps1 passes all checks
- [ ] validate_doc_id_consistency.ps1 passes all checks
- [ ] All 3 domain schemas exist and valid
- [ ] Pattern test infrastructure created

**Total Success:** 100+ files generated, 0 validation errors

---

## 7. Rollback Plan

If generation fails:

1. **Checkpoint Git State:** All changes in feature branch
2. **Restore from Backup:** Pre-generation state saved
3. **Selective Rollback:** Remove failed files only
4. **Re-run Failed Phase:** Isolated phase re-execution

---

## 8. Post-Generation Tasks

1. Run full test suite: `pytest tests/patterns/`
2. Run compliance check: `scripts/PATTERN_DIR_CHECK.ps1`
3. Commit changes: `git commit -m "feat: auto-generate pattern framework files"`
4. Update documentation with new file count
5. Archive generation logs

---

## 9. Estimated Timeline

| Phase | Duration | Files | Status |
|-------|----------|-------|--------|
| Phase 1: ID System | 30 min | 32 | READY |
| Phase 2: Core Patterns | 45 min | 37 | READY |
| Phase 3: Migrated Patterns | 45 min | 51 | READY |
| Phase 4: Validation | 30 min | 8 | READY |
| **TOTAL** | **2.5 hrs** | **128** | **READY** |

---

## 10. Execution Command

```powershell
# Generate all files
./scripts/generate_all_pattern_files.ps1

# Dry run (preview only)
./scripts/generate_all_pattern_files.ps1 -DryRun

# Phase 1 only (ID system)
./scripts/generate_all_pattern_files.ps1 -Phase1Only

# Verbose output
./scripts/generate_all_pattern_files.ps1 -Verbose
```

---

**END OF PHASE PLAN**
