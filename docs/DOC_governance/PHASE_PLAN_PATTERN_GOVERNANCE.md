---
doc_id: DOC-GUIDE-PHASE-PLAN-PATTERN-GOVERNANCE-793
---

# PHASE PLAN: Pattern System Governance Implementation

**Phase ID**: PH-PAT-GOV-001
**Phase Name**: Pattern System Governance & Compliance Framework
**Created**: 2025-11-24
**Status**: READY
**Estimated Duration**: 2.5 hours
**Owner**: DICK

---

## Executive Summary

Implement a complete pattern governance system including operation kind registry, pattern compliance framework, and automated validation tools. This phase transforms the existing ad-hoc pattern system into a governed, spec-driven architecture.

---

## Phase Structure

### Phase 1: Foundation (Registry Infrastructure)
**Duration**: 35 minutes
**Goal**: Build core registry infrastructure

### Phase 2: Compliance (Pattern Conformance)
**Duration**: 55 minutes
**Goal**: Make existing patterns fully compliant

### Phase 3: Automation (Governance Enforcement)
**Duration**: 65 minutes
**Goal**: Build validation and expansion tools

---

## Detailed Steps

### PHASE 1: FOUNDATION (Registry Infrastructure)

#### Step 1.1: Create OPERATION_KIND_REGISTRY.yaml
- **Step ID**: S01
- **Operation Kind**: CREATE_REGISTRY_FILE
- **Duration**: 15 minutes
- **Description**: Create canonical registry of 20-25 core operation kinds
- **Inputs**:
  - `assistant_responses_operation_kinds.md` (reference)
  - OpenSpec/CCPM patterns (reference)
- **Outputs**:
  - `patterns/registry/OPERATION_KIND_REGISTRY.yaml`
- **Success Criteria**:
  - ✅ Valid YAML structure
  - ✅ 20-25 operation kinds defined
  - ✅ Each OPK has: id, name, category, summary, examples, required_params, optional_params
  - ✅ Categories include: filesystem, code_edit, testing, docs, git, orchestration
- **Parameters**:
  ```yaml
  path: patterns/registry/OPERATION_KIND_REGISTRY.yaml
  version: 1.0.0
  status: stable
  categories:
    - filesystem
    - code_edit
    - testing
    - docs
    - git
    - orchestration
    - analysis
  ```

---

#### Step 1.2: Create PATTERN_INDEX.yaml
- **Step ID**: S02
- **Operation Kind**: CREATE_REGISTRY_FILE
- **Duration**: 10 minutes
- **Description**: Create master pattern index registry structure
- **Inputs**:
  - PAT-CHECK-001 spec requirements
  - Existing pattern files (PAT-PATCH-001, PAT-SEARCH-001)
- **Outputs**:
  - `patterns/registry/PATTERN_INDEX.yaml`
- **Success Criteria**:
  - ✅ Valid YAML structure
  - ✅ Schema matches PAT-CHECK-001 requirements
  - ✅ Ready to accept pattern registrations
  - ✅ Includes metadata (version, status, constraints)
- **Parameters**:
  ```yaml
  path: patterns/registry/PATTERN_INDEX.yaml
  version: 1.0.0
  status: stable
  required_fields:
    - doc_id
    - pattern_id
    - name
    - version
    - status
    - spec_path
    - schema_path
    - executor_path
    - test_path
    - example_dir
    - operation_kinds
  ```

---

#### Step 1.3: Create PATTERN_ROUTING.yaml
- **Step ID**: S03
- **Operation Kind**: CREATE_ROUTING_FILE
- **Duration**: 10 minutes
- **Description**: Create operation kind to pattern routing map
- **Inputs**:
  - OPERATION_KIND_REGISTRY.yaml
  - Expected patterns (PAT-PATCH-001, PAT-SEARCH-001)
- **Outputs**:
  - `patterns/registry/PATTERN_ROUTING.yaml`
- **Success Criteria**:
  - ✅ Valid YAML structure
  - ✅ Maps operation kinds to default patterns
  - ✅ Supports variant routing (language-specific, context-based)
  - ✅ Documentation on routing logic
- **Parameters**:
  ```yaml
  path: patterns/registry/PATTERN_ROUTING.yaml
  version: 1.0.0
  routing_keys:
    - operation_kind
    - language
    - context
    - risk_level
  ```

---

### PHASE 2: COMPLIANCE (Pattern Conformance)

#### Step 2.1: Make PAT-PATCH-001 Compliant
- **Step ID**: S04
- **Operation Kind**: REFACTOR_PATTERN_COMPLIANCE
- **Duration**: 25 minutes
- **Description**: Update PAT-PATCH-001 to meet PAT-CHECK-001 requirements
- **Inputs**:
  - `patterns/specs/PAT-PATCH-001_patch_lifecycle_management.md`
  - `scripts/process_patches.py`
  - PAT-CHECK-001 compliance spec
- **Outputs**:
  - `patterns/specs/patch_lifecycle.pattern.yaml` (renamed/restructured)
  - `patterns/schemas/patch_lifecycle.schema.json`
  - `patterns/executors/patch_lifecycle_executor.py` (moved from scripts/)
  - `patterns/tests/test_patch_lifecycle_executor.py`
  - `patterns/examples/patch_lifecycle/instance_minimal.json`
- **Success Criteria**:
  - ✅ Pattern spec has doc_id (DOC-PAT-PATCH-001)
  - ✅ Pattern spec declares operation_kinds
  - ✅ Schema file exists with doc_id reference
  - ✅ Executor has DOC_LINK header
  - ✅ Test file has DOC_LINK header
  - ✅ Example JSON includes doc_id
- **Parameters**:
  ```yaml
  pattern_id: PAT-PATCH-001
  doc_id: DOC-PAT-PATCH-001
  operation_kinds:
    - PROCESS_PATCHES
    - APPLY_PATCH
    - ARCHIVE_PATCH
  ```

---

#### Step 2.2: Make PAT-SEARCH-001 Compliant
- **Step ID**: S05
- **Operation Kind**: REFACTOR_PATTERN_COMPLIANCE
- **Duration**: 20 minutes
- **Description**: Update PAT-SEARCH-001 to meet PAT-CHECK-001 requirements
- **Inputs**:
  - `patterns/specs/PAT-SEARCH-001_deep_directory_search.md`
  - `scripts/deep_search.py`
  - PAT-CHECK-001 compliance spec
- **Outputs**:
  - `patterns/specs/deep_search.pattern.yaml` (renamed/restructured)
  - `patterns/schemas/deep_search.schema.json`
  - `patterns/executors/deep_search_executor.py` (moved from scripts/)
  - `patterns/tests/test_deep_search_executor.py`
  - `patterns/examples/deep_search/instance_minimal.json`
- **Success Criteria**:
  - ✅ Pattern spec has doc_id (DOC-PAT-SEARCH-001)
  - ✅ Pattern spec declares operation_kinds
  - ✅ Schema file exists with doc_id reference
  - ✅ Executor has DOC_LINK header
  - ✅ Test file has DOC_LINK header
  - ✅ Example JSON includes doc_id
- **Parameters**:
  ```yaml
  pattern_id: PAT-SEARCH-001
  doc_id: DOC-PAT-SEARCH-001
  operation_kinds:
    - SEARCH_FILES
    - SEARCH_CONTENT
    - SEARCH_BY_FILTER
  ```

---

#### Step 2.3: Register Patterns in PATTERN_INDEX.yaml
- **Step ID**: S06
- **Operation Kind**: UPDATE_PATTERN_INDEX
- **Duration**: 10 minutes
- **Description**: Add both patterns to the master index
- **Inputs**:
  - PATTERN_INDEX.yaml (from S02)
  - Compliant pattern specs (from S04, S05)
- **Outputs**:
  - Updated `patterns/registry/PATTERN_INDEX.yaml`
- **Success Criteria**:
  - ✅ Both patterns registered with all required fields
  - ✅ All paths validated and correct
  - ✅ operation_kinds properly declared
  - ✅ YAML remains valid
- **Parameters**:
  ```yaml
  patterns:
    - PAT-PATCH-001
    - PAT-SEARCH-001
  ```

---

### PHASE 3: AUTOMATION (Governance Enforcement)

#### Step 3.1: Create PATTERN_DIR_CHECK.ps1 Validation Script
- **Step ID**: S07
- **Operation Kind**: CREATE_VALIDATION_SCRIPT
- **Duration**: 30 minutes
- **Description**: Build automated compliance validation script
- **Inputs**:
  - PAT-CHECK-001 compliance spec
  - PATTERN_INDEX.yaml
  - OPERATION_KIND_REGISTRY.yaml
- **Outputs**:
  - `scripts/PATTERN_DIR_CHECK.ps1`
  - Validation report format specification
- **Success Criteria**:
  - ✅ Validates all PAT-CHECK-001 requirements
  - ✅ Checks directory structure (Section 1)
  - ✅ Validates PATTERN_INDEX.yaml shape (Section 2)
  - ✅ Verifies spec/schema/executor/test/example compliance (Sections 3-7)
  - ✅ Validates doc_id consistency (Section 8)
  - ✅ Outputs PASS/FAIL per requirement ID
  - ✅ Produces summary (total checks, pass/fail count)
  - ✅ Exit code 0 on success, non-zero on failure
- **Parameters**:
  ```yaml
  path: scripts/PATTERN_DIR_CHECK.ps1
  validation_sections:
    - directory_layout
    - pattern_index
    - spec_files
    - schema_files
    - executor_files
    - example_dirs
    - test_files
    - cross_artifact_consistency
  output_format: json
  ```

---

#### Step 3.2: Create OPK Miner Script
- **Step ID**: S08
- **Operation Kind**: CREATE_ANALYSIS_SCRIPT
- **Duration**: 20 minutes
- **Description**: Build operation kind discovery/mining script
- **Inputs**:
  - Logs, phase plans, specs (scan targets)
  - OPERATION_KIND_REGISTRY.yaml (existing registry)
- **Outputs**:
  - `scripts/opk_miner.py`
  - `opk_candidates.json` (output format spec)
- **Success Criteria**:
  - ✅ Scans specified directories for action phrases
  - ✅ Extracts verb phrases and patterns
  - ✅ Counts frequency of each phrase
  - ✅ Outputs candidates in JSON format
  - ✅ Excludes already-registered operation kinds
  - ✅ Supports incremental runs
- **Parameters**:
  ```yaml
  path: scripts/opk_miner.py
  scan_paths:
    - devdocs/
    - logs/
    - master_plan/
    - specs/
  output_path: opk_candidates.json
  min_frequency: 3
  ```

---

#### Step 3.3: Create OPK Normalization Pattern
- **Step ID**: S09
- **Operation Kind**: CREATE_PATTERN_SPEC
- **Duration**: 15 minutes
- **Description**: Formalize OPK normalization as a reusable pattern
- **Inputs**:
  - Strict normalization prompt from `assistant_responses_operation_kinds.md`
  - OPERATION_KIND_REGISTRY.yaml schema
- **Outputs**:
  - `patterns/specs/opk_normalization.pattern.yaml`
  - `patterns/schemas/opk_normalization.schema.json`
  - `patterns/executors/opk_normalization_executor.py`
  - `patterns/tests/test_opk_normalization.py`
  - `patterns/examples/opk_normalization/instance_minimal.json`
- **Success Criteria**:
  - ✅ Pattern spec complete with doc_id
  - ✅ Includes strict normalization prompt as template
  - ✅ Schema validates input phrases and output registry format
  - ✅ Executor can invoke LLM with prompt
  - ✅ Example shows before/after transformation
- **Parameters**:
  ```yaml
  pattern_id: PAT-OPK-NORM-001
  doc_id: DOC-PAT-OPK-NORM-001
  operation_kinds:
    - NORMALIZE_OPERATION_KINDS
  ```

---

#### Step 3.4: Register New Pattern
- **Step ID**: S10
- **Operation Kind**: UPDATE_PATTERN_INDEX
- **Duration**: 5 minutes
- **Description**: Register OPK normalization pattern in index
- **Inputs**:
  - PATTERN_INDEX.yaml
  - OPK normalization pattern (from S09)
- **Outputs**:
  - Updated `patterns/registry/PATTERN_INDEX.yaml`
- **Success Criteria**:
  - ✅ Pattern registered with all required fields
  - ✅ Passes PATTERN_DIR_CHECK.ps1 validation
- **Parameters**:
  ```yaml
  pattern_id: PAT-OPK-NORM-001
  ```

---

#### Step 3.5: Run Full Validation
- **Step ID**: S11
- **Operation Kind**: RUN_VALIDATION
- **Duration**: 5 minutes
- **Description**: Execute validation script against all patterns
- **Inputs**:
  - All pattern files
  - PATTERN_INDEX.yaml
  - OPERATION_KIND_REGISTRY.yaml
  - PATTERN_ROUTING.yaml
- **Outputs**:
  - Validation report
  - Pass/fail status
- **Success Criteria**:
  - ✅ All patterns pass PAT-CHECK-001 compliance
  - ✅ No broken links or missing files
  - ✅ doc_id consistency across artifacts
  - ✅ Zero validation errors
- **Parameters**:
  ```yaml
  script: scripts/PATTERN_DIR_CHECK.ps1
  output: validation_report.json
  ```

---

## Dependencies Graph

```
S01 (OPK Registry) ──┬─→ S04 (PAT-PATCH-001 Compliance)
                     ├─→ S05 (PAT-SEARCH-001 Compliance)
                     └─→ S03 (Routing)

S02 (Pattern Index) ──→ S06 (Register Patterns) ──→ S07 (Validation Script)

S04 ──┐
      ├─→ S06
S05 ──┘

S06 ──→ S07 ──→ S11 (Final Validation)

S01 ──→ S08 (OPK Miner)

S08 ──→ S09 (OPK Norm Pattern) ──→ S10 (Register) ──→ S11
```

---

## Deliverables Checklist

### Phase 1: Foundation
- [ ] `patterns/registry/OPERATION_KIND_REGISTRY.yaml`
- [ ] `patterns/registry/PATTERN_INDEX.yaml`
- [ ] `patterns/registry/PATTERN_ROUTING.yaml`

### Phase 2: Compliance
- [ ] `patterns/specs/patch_lifecycle.pattern.yaml`
- [ ] `patterns/schemas/patch_lifecycle.schema.json`
- [ ] `patterns/executors/patch_lifecycle_executor.py`
- [ ] `patterns/tests/test_patch_lifecycle_executor.py`
- [ ] `patterns/examples/patch_lifecycle/instance_minimal.json`
- [ ] `patterns/specs/deep_search.pattern.yaml`
- [ ] `patterns/schemas/deep_search.schema.json`
- [ ] `patterns/executors/deep_search_executor.py`
- [ ] `patterns/tests/test_deep_search_executor.py`
- [ ] `patterns/examples/deep_search/instance_minimal.json`
- [ ] Updated `patterns/registry/PATTERN_INDEX.yaml` (with 2 patterns)

### Phase 3: Automation
- [ ] `scripts/PATTERN_DIR_CHECK.ps1`
- [ ] `scripts/opk_miner.py`
- [ ] `patterns/specs/opk_normalization.pattern.yaml`
- [ ] `patterns/schemas/opk_normalization.schema.json`
- [ ] `patterns/executors/opk_normalization_executor.py`
- [ ] `patterns/tests/test_opk_normalization.py`
- [ ] `patterns/examples/opk_normalization/instance_minimal.json`
- [ ] Updated `patterns/registry/PATTERN_INDEX.yaml` (with 3 patterns)
- [ ] Validation report (all green)

**Total Files**: 23 files created/modified

---

## Success Criteria

### Phase 1 Success
- ✅ All 3 registry files created
- ✅ Valid YAML structure
- ✅ Core operation kinds defined (20-25)
- ✅ Registry infrastructure ready for pattern registration

### Phase 2 Success
- ✅ Both existing patterns fully PAT-CHECK-001 compliant
- ✅ All required artifacts present (spec, schema, executor, tests, examples)
- ✅ doc_id consistency across all artifacts
- ✅ Patterns registered in PATTERN_INDEX.yaml

### Phase 3 Success
- ✅ Validation script operational
- ✅ OPK mining capability established
- ✅ Normalization pattern documented and reusable
- ✅ Full validation passes with zero errors

### Overall Success
- ✅ Governed pattern system operational
- ✅ All patterns compliant with PAT-CHECK-001
- ✅ Automated validation enforcing compliance
- ✅ Tools for expanding operation kind vocabulary
- ✅ Complete audit trail via doc_id system

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML syntax errors | High | Validate after each file creation |
| Missing doc_id links | High | Run validation after each pattern update |
| Pattern spec ambiguity | Medium | Reference PAT-CHECK-001 continuously |
| Tool script failures | Medium | Test incrementally, add error handling |
| Time overrun | Low | Prioritize critical path, defer nice-to-haves |

---

## Execution Notes

### Order of Execution
Execute steps **sequentially by step ID** (S01 → S11).

### Validation Points
- After S03: Validate all registry files parse correctly
- After S06: Run basic index validation
- After S10: Run full validation script
- After S11: Verify zero errors

### Commit Strategy
- Commit after each phase completes
- Use atomic commits per deliverable where possible
- Tag final state as `v1.0.0-pattern-governance`

---

## Post-Phase Actions

### Immediate Next Steps
1. Add governance to QUALITY_GATE.yaml:
   ```yaml
   pattern_compliance:
     command: scripts/PATTERN_DIR_CHECK.ps1
     required: true
   ```

2. Update CI/CD pipeline to run validation

3. Document pattern authoring workflow

### Future Enhancements
- [ ] Add more operation kinds as discovered
- [ ] Create language-specific pattern variants
- [ ] Build pattern dependency tracking
- [ ] Implement pattern versioning strategy

---

## Estimated Timeline

```
Phase 1: Foundation       |████████░░░░░░░░░░░░░░░░░░| 35 min (23%)
Phase 2: Compliance       |████████████░░░░░░░░░░░░░░| 55 min (37%)
Phase 3: Automation       |████████████████░░░░░░░░░░| 65 min (40%)
                          └────────────────────────────┘
Total: 2.5 hours (155 minutes)
```

---

**Phase Plan Status**: ✅ READY FOR EXECUTION
**Next Action**: Begin Step S01 (Create OPERATION_KIND_REGISTRY.yaml)
