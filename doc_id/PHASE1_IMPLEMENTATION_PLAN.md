# Phase 1: CI/CD Integration - Implementation Plan

**Date**: 2025-12-01  
**Status**: 🚀 STARTING  
**Estimated Time**: 2 hours

---

## Goals

1. **Protect Phase 0 & 1.5 work** - Prevent regression of doc_id system
2. **Automate validation** - Registry and module_id consistency checks
3. **Enforce standards** - Block commits that violate doc_id rules
4. **Enable monitoring** - Track coverage and quality metrics

---

## Prerequisites

✅ Phase 0 complete (100% doc_id coverage)  
✅ Phase 1.5 complete (92% module_id coverage)  
✅ Existing path_standards.yml workflow  
✅ doc_id_scanner.py and module_id_assigner.py available

---

## Deliverables

### 1. GitHub Actions Workflows (3)

#### 1.1 doc_id_validation.yml
**Purpose**: Validate doc_id coverage and registry consistency on every PR/push

**Checks**:
- ✅ All new files have doc_ids
- ✅ Registry YAML is valid
- ✅ No duplicate doc_ids
- ✅ Coverage doesn't decrease
- ✅ Doc_id format compliance

#### 1.2 module_id_validation.yml
**Purpose**: Validate module_id assignments and taxonomy

**Checks**:
- ✅ All docs have module_id field
- ✅ Module IDs match taxonomy
- ✅ No invalid module references
- ✅ Module coverage reporting

#### 1.3 registry_integrity.yml
**Purpose**: Deep validation of DOC_ID_REGISTRY.yaml

**Checks**:
- ✅ YAML syntax valid
- ✅ All required fields present
- ✅ No orphaned doc_ids
- ✅ Artifact paths exist
- ✅ Category consistency

### 2. Pre-commit Hooks (2)

#### 2.1 pre-commit-doc-id
**Purpose**: Local validation before commit

**Checks**:
- Scan staged files for doc_ids
- Warn if new files lack doc_ids
- Validate doc_id format

#### 2.2 pre-commit-registry
**Purpose**: Registry consistency check

**Checks**:
- YAML syntax
- No duplicate IDs
- Basic field validation

### 3. Validation Scripts (2)

#### 3.1 validate_doc_id_coverage.py
**Purpose**: CI-friendly coverage validation

**Features**:
- Fast scan of repository
- Compare against baseline
- Exit code 1 if coverage drops
- JSON report output

#### 3.2 validate_registry.py
**Purpose**: Comprehensive registry validation

**Features**:
- YAML structure validation
- Duplicate detection
- Orphan detection
- Module_id validation
- Detailed error reporting

### 4. Documentation (1)

#### 4.1 PHASE1_CI_CD_GUIDE.md
**Purpose**: Setup and usage guide

**Contents**:
- Workflow descriptions
- How to fix common failures
- Local testing instructions
- Maintenance procedures

---

## Implementation Steps

### Step 1: Create Validation Scripts (45 min)

**Task 1.1**: Create `validate_doc_id_coverage.py`
- Reuse doc_id_scanner.py logic
- Add baseline comparison
- CI-friendly output

**Task 1.2**: Create `validate_registry.py`
- YAML validation
- Duplicate checks
- Module_id validation
- Comprehensive error messages

### Step 2: Create GitHub Workflows (45 min)

**Task 2.1**: Create `.github/workflows/doc_id_validation.yml`
- Run on PR and push to main
- Execute validate_doc_id_coverage.py
- Report results as PR comment

**Task 2.2**: Create `.github/workflows/module_id_validation.yml`
- Validate module assignments
- Check taxonomy consistency

**Task 2.3**: Create `.github/workflows/registry_integrity.yml`
- Deep registry validation
- Runs on registry file changes

### Step 3: Create Pre-commit Hooks (20 min)

**Task 3.1**: Create `.githooks/pre-commit-doc-id`
- Lightweight local check
- Installation instructions

**Task 3.2**: Create `.githooks/pre-commit-registry`
- Registry-specific validation

### Step 4: Documentation (10 min)

**Task 4.1**: Create `PHASE1_CI_CD_GUIDE.md`
- Setup instructions
- Troubleshooting guide
- Maintenance procedures

---

## Success Criteria

- [ ] doc_id_validation.yml workflow passing
- [ ] module_id_validation.yml workflow passing
- [ ] registry_integrity.yml workflow passing
- [ ] Pre-commit hooks functional
- [ ] Documentation complete
- [ ] All workflows tested on sample PR

---

## Testing Plan

### Test 1: Coverage Regression
```bash
# Remove doc_id from a file
# Expect: CI fails with clear error

# Fix and commit
# Expect: CI passes
```

### Test 2: Duplicate Detection
```bash
# Add duplicate doc_id to registry
# Expect: registry_integrity.yml fails

# Fix duplicate
# Expect: CI passes
```

### Test 3: Invalid Module ID
```bash
# Add doc with module_id: "invalid.module"
# Expect: module_id_validation.yml fails

# Fix to valid module
# Expect: CI passes
```

---

## Integration Points

**With Phase 0**:
- Uses doc_id_scanner.py
- Validates coverage metrics

**With Phase 1.5**:
- Uses module_id_assigner.py for validation
- Enforces module taxonomy

**With Existing Workflows**:
- Complements path_standards.yml
- Similar structure for consistency

---

## Rollback Plan

If workflows cause issues:
1. Disable workflows (comment out `on:` triggers)
2. Keep validation scripts for manual use
3. Document issues for future iteration

---

## Timeline

```
Hour 1:
  0:00-0:45  Create validation scripts
  0:45-1:00  Test validation scripts locally

Hour 2:
  1:00-1:45  Create GitHub workflows
  1:45-2:00  Create pre-commit hooks + documentation
```

---

## Next Steps After Phase 1

With CI/CD in place:
- **Phase 2**: Production hardening with confidence
- **Continuous validation**: Automatic protection
- **Team enforcement**: Standards automatically applied

---

**Ready to begin implementation!**
