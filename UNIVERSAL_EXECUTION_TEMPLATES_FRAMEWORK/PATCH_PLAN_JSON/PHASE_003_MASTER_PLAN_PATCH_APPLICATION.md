# Phase PH-NEXT-003: Master Plan Patch Application

**Created**: 2025-11-24T07:37:30Z  
**Phase ID**: PH-NEXT-003  
**Status**: READY  
**Priority**: CRITICAL  
**Estimated Duration**: 2-3 hours  
**Dependencies**: None (independent operation)

---

## Executive Summary

Apply all 16 JSON patches to the UET V2 base plan to create a complete, validated master plan. This phase uses the existing `apply_patches.py` script and validates the output against framework standards.

**Goal**: Generate `UET_V2_MASTER_PLAN.json` with all patches applied and validated.

---

## Phase Structure

| Workstream | Name | Duration | Priority |
|------------|------|----------|----------|
| **WS-003-001** | Pre-Application Validation | 30min | CRITICAL |
| **WS-003-002** | Patch Application | 45min | CRITICAL |
| **WS-003-003** | Post-Application Validation | 45min | HIGH |
| **WS-003-004** | Documentation & Handoff | 30min | MEDIUM |

**Total**: 2.5 hours

---

## Workstream WS-003-001: Pre-Application Validation

**Duration**: 30 minutes  
**Priority**: CRITICAL  
**Goal**: Verify all inputs are valid before applying patches

### Tasks

#### TSK-003-001-001: Verify Base Plan Exists (5min)

**Commands**:
```bash
# Check base plan exists and is valid JSON
python -c "import json; json.load(open('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan/base_plan.json'))"
```

**Acceptance Criteria**:
- [ ] `base_plan.json` exists
- [ ] Valid JSON syntax
- [ ] Contains required top-level keys: `meta`, `phases`, `validation`

**Output**: ✅ Base plan validated

---

#### TSK-003-001-002: Verify All Patch Files (10min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# List all patch files
Get-ChildItem -Filter "*-*.json" | Where-Object { $_.Name -match '^\d{3}-' } | Select-Object Name, Length

# Validate each patch is valid JSON
foreach ($patch in (Get-ChildItem -Filter "*.json" | Where-Object { $_.Name -match '^\d{3}-' })) {
    Write-Host "Validating $($patch.Name)..."
    python -c "import json; json.load(open('$($patch.Name)'))"
}
```

**Acceptance Criteria**:
- [ ] All 16 patch files exist:
  - 001-config-integration.json
  - 002-documentation-integration.json
  - 003-uet-v2-specifications.json
  - 004-planning-reference.json
  - 005-adr-architecture-decisions.json
  - 005-core-engine-implementation.json
  - 005-development-guidelines.json
  - 006-core-state-implementation.json
  - 006-schema-definitions.json
  - 007-test-infrastructure.json
  - 007-tool-adapter-interface.json
  - 008-resilience-patterns.json
  - 009-subagent-architecture-slash-commands.json
  - 010-docs-reorg-phase-FAST.json
  - 010-docs-reorg-phase.json
  - 011-ai-codebase-optimization.json
- [ ] All files are valid JSON
- [ ] All files are RFC 6902 JSON Patch format (array of operations)

**Output**: `PATCH_VALIDATION_REPORT.txt`

---

#### TSK-003-001-003: Check Dependencies (10min)

**Commands**:
```bash
# Check Python and jsonpatch installed
python --version
python -c "import jsonpatch; print(f'jsonpatch {jsonpatch.__version__}')"

# If not installed:
pip install jsonpatch
```

**Acceptance Criteria**:
- [ ] Python 3.8+ available
- [ ] `jsonpatch` library installed
- [ ] `apply_patches.py` script exists

**Output**: ✅ Dependencies satisfied

---

#### TSK-003-001-004: Backup Existing Master Plan (5min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Backup existing master plan if it exists
if (Test-Path "UET_V2_MASTER_PLAN.json") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item "UET_V2_MASTER_PLAN.json" "archive/UET_V2_MASTER_PLAN_backup_$timestamp.json"
    Write-Host "✅ Backup created: archive/UET_V2_MASTER_PLAN_backup_$timestamp.json"
}
```

**Acceptance Criteria**:
- [ ] Existing master plan backed up (if exists)
- [ ] Backup stored in `archive/` directory
- [ ] Timestamp in filename

**Output**: Backup file created (if needed)

---

## Workstream WS-003-002: Patch Application

**Duration**: 45 minutes  
**Priority**: CRITICAL  
**Goal**: Apply all patches and generate master plan

### Tasks

#### TSK-003-002-001: Run Patch Application Script (20min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Run patch application
python apply_patches.py
```

**Expected Output**:
```
============================================================
UET V2 Master Plan - Patch Application
============================================================

📖 Loading base plan: base_plan.json
   Base plan has X phases

📦 Applying 16 patches...
📄 Loading 001-config-integration.json...
   Applying 22 operations...
   ✅ Applied successfully
📄 Loading 002-documentation-integration.json...
   Applying 15 operations...
   ✅ Applied successfully
...

✅ Applied XXX total operations from 16 patches

🔍 Validating merged plan...
   Checking ULID uniqueness...
   ✅ All XXX ULIDs are unique
   Checking required metadata...
   ✅ All required metadata present
   Checking phases...
   ✅ All referenced phases present (XX total)
   Checking validation...
   ✅ Validation section exists with XX rules

✅ All validation checks passed

   Checking for circular dependencies...
   ✅ No circular dependencies found

💾 Saving merged plan to: UET_V2_MASTER_PLAN.json

============================================================
✅ SUCCESS - UET V2 Master Plan Created
============================================================
📊 Summary:
   - Total phases: XX
   - Total ULIDs: XXX
   - File size: XXX.X KB

📄 Output: UET_V2_MASTER_PLAN.json
```

**Acceptance Criteria**:
- [ ] Script runs without errors
- [ ] All 16 patches applied successfully
- [ ] ULID uniqueness validated
- [ ] No circular dependencies detected
- [ ] `UET_V2_MASTER_PLAN.json` created

**Output**: `UET_V2_MASTER_PLAN.json`

---

#### TSK-003-002-002: Verify Master Plan Structure (10min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Check file size
Get-Item UET_V2_MASTER_PLAN.json | Select-Object Name, Length

# Validate JSON structure
python -c "
import json
plan = json.load(open('UET_V2_MASTER_PLAN.json'))
print(f'✅ Meta sections: {len(plan.get(\"meta\", {}))}')
print(f'✅ Phases: {len(plan.get(\"phases\", {}))}')
print(f'✅ Validation rules: {len(plan.get(\"validation\", {}))}')
print(f'✅ Patches applied: {len(plan.get(\"meta\", {}).get(\"patch_metadata\", {}))}')
"
```

**Acceptance Criteria**:
- [ ] File is 100KB+ (comprehensive plan)
- [ ] Contains `meta`, `phases`, `validation` sections
- [ ] All 16 patches listed in `meta.patch_metadata`
- [ ] Valid JSON structure

**Output**: Structure validation report

---

#### TSK-003-002-003: Extract Key Metrics (15min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Extract metrics
python -c "
import json
from collections import Counter

plan = json.load(open('UET_V2_MASTER_PLAN.json'))

print('=' * 60)
print('UET V2 Master Plan Metrics')
print('=' * 60)

# Meta sections
meta = plan.get('meta', {})
print(f'\\nMeta Sections: {len(meta)}')
for key in sorted(meta.keys()):
    if isinstance(meta[key], dict):
        print(f'  - {key}: {len(meta[key])} items')
    else:
        print(f'  - {key}: {meta[key]}')

# Phases
phases = plan.get('phases', {})
print(f'\\nPhases: {len(phases)}')
phase_states = Counter(p.get('status', 'unknown') for p in phases.values())
for state, count in phase_states.items():
    print(f'  - {state}: {count}')

# Validation
validation = plan.get('validation', {})
print(f'\\nValidation Rules: {len(validation)}')

# Patch metadata
patches = meta.get('patch_metadata', {})
print(f'\\nPatches Applied: {len(patches)}')
for patch_id in sorted(patches.keys()):
    p = patches[patch_id]
    print(f'  - {patch_id}: {p.get(\"description\", \"N/A\")[:50]}...')

print('\\n' + '=' * 60)
" > MASTER_PLAN_METRICS.txt

cat MASTER_PLAN_METRICS.txt
```

**Acceptance Criteria**:
- [ ] Metrics extracted successfully
- [ ] All 16 patches shown in metadata
- [ ] Phase count documented
- [ ] Validation rules documented

**Output**: `MASTER_PLAN_METRICS.txt`

---

## Workstream WS-003-003: Post-Application Validation

**Duration**: 45 minutes  
**Priority**: HIGH  
**Goal**: Validate master plan quality and completeness

### Tasks

#### TSK-003-003-001: Run Script Validation (10min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Run built-in validation
python apply_patches.py --validate-only
```

**Acceptance Criteria**:
- [ ] ULID uniqueness check passes
- [ ] Required metadata present
- [ ] Phase dependency graph valid
- [ ] No circular dependencies
- [ ] Validation rules present

**Output**: ✅ Script validation passed

---

#### TSK-003-003-002: Validate Against Framework Standards (15min)

**Commands**:
```bash
# Check master plan conforms to UET standards
python -c "
import json

plan = json.load(open('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan/UET_V2_MASTER_PLAN.json'))
meta = plan.get('meta', {})

# Required sections per UET framework
required_sections = [
    'architecture',
    'three_engine_problem',
    'system_alignment',
    'ai_policies',
    'project',
    'constraints',
    'patch_metadata'
]

print('Framework Compliance Check')
print('=' * 60)
missing = []
for section in required_sections:
    if section in meta:
        print(f'✅ {section}')
    else:
        print(f'❌ {section} MISSING')
        missing.append(section)

if missing:
    print(f'\\n❌ Missing {len(missing)} required sections')
    exit(1)
else:
    print(f'\\n✅ All {len(required_sections)} required sections present')
"
```

**Acceptance Criteria**:
- [ ] All framework-required sections present
- [ ] Architecture layer definitions included
- [ ] Three-engine problem documented
- [ ] AI policies integrated
- [ ] Project metadata complete

**Output**: Framework compliance report

---

#### TSK-003-003-003: Verify Patch Metadata (10min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Verify each patch is documented
python -c "
import json

plan = json.load(open('UET_V2_MASTER_PLAN.json'))
patches_meta = plan.get('meta', {}).get('patch_metadata', {})

print('Patch Metadata Verification')
print('=' * 60)

for patch_id in sorted(patches_meta.keys()):
    p = patches_meta[patch_id]
    print(f'\\nPatch {patch_id}:')
    print(f'  - Description: {p.get(\"description\", \"N/A\")[:60]}...')
    print(f'  - Operations: {p.get(\"operations_count\", 0)}')
    print(f'  - Priority: {p.get(\"priority\", \"N/A\")}')
    print(f'  - Applied: {p.get(\"applied\", False)}')
    print(f'  - Source files: {len(p.get(\"source_files\", []))}')

print(f'\\n✅ Total patches documented: {len(patches_meta)}')
"
```

**Acceptance Criteria**:
- [ ] All 16 patches documented in metadata
- [ ] Each patch has description, priority, operations count
- [ ] Source files tracked for each patch
- [ ] Applied status recorded

**Output**: Patch metadata verification

---

#### TSK-003-003-004: Check Phase Dependencies (10min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Analyze phase dependency graph
python -c "
import json
from collections import defaultdict, deque

plan = json.load(open('UET_V2_MASTER_PLAN.json'))
phases = plan.get('phases', {})

print('Phase Dependency Analysis')
print('=' * 60)

# Build dependency graph
deps = defaultdict(list)
reverse_deps = defaultdict(list)

for phase_id, phase in phases.items():
    for dep in phase.get('dependencies', []):
        deps[phase_id].append(dep)
        reverse_deps[dep].append(phase_id)

# Find phases with no dependencies (can start immediately)
no_deps = [p for p in phases if not deps[p]]
print(f'\\nPhases with no dependencies ({len(no_deps)}):')
for p in sorted(no_deps):
    print(f'  - {p}')

# Find phases that are blocking others
blocking = {p: reverse_deps[p] for p in reverse_deps if len(reverse_deps[p]) > 2}
if blocking:
    print(f'\\nPhases blocking multiple others ({len(blocking)}):')
    for p, blocked in sorted(blocking.items()):
        print(f'  - {p} blocks {len(blocked)} phases')

# Find leaf phases (no dependents)
leaves = [p for p in phases if p not in reverse_deps]
print(f'\\nLeaf phases ({len(leaves)}):')
for p in sorted(leaves)[:5]:  # Show first 5
    print(f'  - {p}')
if len(leaves) > 5:
    print(f'  ... and {len(leaves) - 5} more')

print(f'\\n✅ Total phases: {len(phases)}')
print(f'✅ Total dependencies: {sum(len(d) for d in deps.values())}')
"
```

**Acceptance Criteria**:
- [ ] Dependency graph is acyclic (no loops)
- [ ] At least one phase has no dependencies (can start)
- [ ] All phase IDs referenced in dependencies exist
- [ ] Reasonable dependency depth (no phase depends on 10+ others)

**Output**: Dependency graph analysis

---

## Workstream WS-003-004: Documentation & Handoff

**Duration**: 30 minutes  
**Priority**: MEDIUM  
**Goal**: Document the patch application and prepare for execution

### Tasks

#### TSK-003-004-001: Create Application Summary (15min)

**File**: `PATCH_APPLICATION_SUMMARY.md`

**Content Template**:
```markdown
# UET V2 Master Plan - Patch Application Summary

**Date**: 2025-11-24T[HH:MM:SS]Z  
**Phase**: PH-NEXT-003  
**Status**: ✅ COMPLETE  
**Duration**: [actual duration]

---

## Overview

Successfully applied 16 JSON patches to base plan, creating comprehensive UET V2 Master Plan.

## Results

### Patches Applied
- Total patches: 16
- Total operations: XXX
- File size: XXX KB
- Validation: ✅ PASSED

### Master Plan Contents
- Meta sections: XX
- Total phases: XX
- Validation rules: XX
- ULIDs: XXX (all unique)

### Key Sections Integrated
- ✅ Configuration (CODEBASE_INDEX, ai_policies, QUALITY_GATE)
- ✅ Documentation patterns
- ✅ UET V2 specifications
- ✅ Planning reference
- ✅ ADR architecture decisions
- ✅ Core engine implementation
- ✅ Development guidelines
- ✅ Core state implementation
- ✅ Schema definitions
- ✅ Test infrastructure
- ✅ Tool adapter interface
- ✅ Resilience patterns
- ✅ Subagent architecture
- ✅ Docs reorganization
- ✅ AI codebase optimization

---

## Validation Results

### Script Validation
- ULID uniqueness: ✅ PASSED
- Required metadata: ✅ PASSED
- Phase dependencies: ✅ PASSED
- Circular dependency check: ✅ PASSED
- Validation rules: ✅ PASSED

### Framework Compliance
- Architecture layers: ✅ PRESENT
- Three-engine problem: ✅ PRESENT
- System alignment: ✅ PRESENT
- AI policies: ✅ PRESENT
- Project metadata: ✅ PRESENT

---

## Files Generated

1. `UET_V2_MASTER_PLAN.json` - Complete master plan (XXX KB)
2. `MASTER_PLAN_METRICS.txt` - Metrics and statistics
3. `PATCH_VALIDATION_REPORT.txt` - Pre-application validation
4. `PATCH_APPLICATION_SUMMARY.md` - This file

---

## Next Steps

1. **Review master plan**: Open `UET_V2_MASTER_PLAN.json` in editor
2. **Begin execution**: Start with phases that have no dependencies
3. **Track progress**: Use patch metadata to mark phases as applied
4. **Monitor compliance**: Validate against framework standards

---

## Issues Encountered

[Document any issues during application]

---

## Time Breakdown

| Workstream | Planned | Actual | Variance |
|------------|---------|--------|----------|
| WS-003-001 | 30min | XXmin | XX |
| WS-003-002 | 45min | XXmin | XX |
| WS-003-003 | 45min | XXmin | XX |
| WS-003-004 | 30min | XXmin | XX |
| **TOTAL** | **2.5h** | **XXh** | **XX** |

---

**Status**: ✅ PHASE COMPLETE  
**Next Phase**: PH-NEXT-004 (Master Plan Execution - Phase 0)
```

**Acceptance Criteria**:
- [ ] Summary document created
- [ ] All metrics populated
- [ ] Validation results documented
- [ ] Next steps clearly defined

**Output**: `PATCH_APPLICATION_SUMMARY.md`

---

#### TSK-003-004-002: Update Phase Tracking (10min)

**Commands**:
```bash
# Mark phase as complete in tracking system
python -c "
import json
from datetime import datetime

# Load or create phase log
try:
    with open('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/PATCH_PLAN_JSON/PHASE_003_SUMMARY.md', 'w') as f:
        f.write(f'''# Phase PH-NEXT-003 Execution Summary

**Date**: {datetime.utcnow().isoformat()}Z
**Phase**: PH-NEXT-003 (Master Plan Patch Application)
**Status**: ✅ COMPLETE
**Duration**: [actual]

## Achievements
- ✅ All 16 patches validated
- ✅ Master plan generated successfully
- ✅ All validation checks passed
- ✅ Framework compliance verified
- ✅ Documentation complete

## Deliverables
1. UET_V2_MASTER_PLAN.json (XXX KB)
2. MASTER_PLAN_METRICS.txt
3. PATCH_APPLICATION_SUMMARY.md
4. PHASE_003_SUMMARY.md

## Next Steps
- Begin Phase 0 execution from master plan
- Track patch application progress
- Monitor framework compliance

**Phase Status**: ✅ SUCCESS
''')
    print('✅ Phase summary created')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Acceptance Criteria**:
- [ ] Phase marked as complete
- [ ] Summary document created
- [ ] Deliverables listed
- [ ] Next steps documented

**Output**: `PHASE_003_SUMMARY.md`

---

#### TSK-003-004-003: Archive Working Files (5min)

**Commands**:
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan

# Ensure archive directory exists
if (!(Test-Path "archive")) {
    New-Item -ItemType Directory -Path "archive"
}

# Copy validation reports to archive
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "MASTER_PLAN_METRICS.txt" "archive/MASTER_PLAN_METRICS_$timestamp.txt"
Copy-Item "PATCH_APPLICATION_SUMMARY.md" "archive/PATCH_APPLICATION_SUMMARY_$timestamp.md"

Write-Host "✅ Working files archived"
```

**Acceptance Criteria**:
- [ ] Archive directory exists
- [ ] Metrics archived with timestamp
- [ ] Summary archived with timestamp
- [ ] Original files remain in place

**Output**: Archived files in `archive/`

---

## Phase Success Criteria

### Overall Acceptance Criteria

- [ ] ✅ All 16 patches applied successfully
- [ ] ✅ `UET_V2_MASTER_PLAN.json` created and validated
- [ ] ✅ No ULID duplicates
- [ ] ✅ No circular dependencies
- [ ] ✅ All framework sections present
- [ ] ✅ Patch metadata complete
- [ ] ✅ Dependency graph valid
- [ ] ✅ Documentation complete
- [ ] ✅ Files archived

### Quality Gates

| Gate | Criteria | Status |
|------|----------|--------|
| **G1: Patch Validation** | All patches valid JSON, RFC 6902 format | ⏳ |
| **G2: Application Success** | All patches apply without errors | ⏳ |
| **G3: ULID Uniqueness** | No duplicate ULIDs in master plan | ⏳ |
| **G4: Dependency Graph** | Acyclic, all references valid | ⏳ |
| **G5: Framework Compliance** | All required sections present | ⏳ |
| **G6: Documentation** | Summary and metrics generated | ⏳ |

---

## Rollback Plan

If patch application fails:

1. **Restore backup**:
   ```bash
   cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/master_plan
   Copy-Item "archive/UET_V2_MASTER_PLAN_backup_*.json" "UET_V2_MASTER_PLAN.json"
   ```

2. **Identify failing patch**:
   - Check error message for patch ID
   - Review patch file for malformed operations
   - Validate patch JSON syntax

3. **Fix or exclude failing patch**:
   - Edit `apply_patches.py` to skip failing patch
   - Or fix the patch file and retry

4. **Retry application**:
   ```bash
   python apply_patches.py
   ```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Patch syntax error | LOW | HIGH | Pre-validate all JSON |
| ULID collision | VERY LOW | HIGH | Built-in validation check |
| Circular dependency | LOW | MEDIUM | Automated detection |
| Missing dependency | LOW | HIGH | Verify all phase IDs exist |
| Large file size | LOW | LOW | Expected, not a problem |

---

## Resources Required

### Tools
- Python 3.8+
- `jsonpatch` library (`pip install jsonpatch`)
- Text editor (VS Code recommended)

### Time
- Developer time: 2.5 hours
- Compute time: <5 minutes (patch application)

### Storage
- Input: ~200KB (base plan + patches)
- Output: ~150KB (master plan)
- Archive: ~50KB (backups, reports)

---

## Timeline

| Time | Activity | Workstream |
|------|----------|------------|
| T+0:00 | Pre-validation start | WS-003-001 |
| T+0:30 | Patch application start | WS-003-002 |
| T+1:15 | Post-validation start | WS-003-003 |
| T+2:00 | Documentation start | WS-003-004 |
| T+2:30 | **Phase complete** | - |

---

## Success Metrics

### Quantitative
- ✅ 16/16 patches applied
- ✅ 0 ULID duplicates
- ✅ 0 circular dependencies
- ✅ 100% framework compliance
- ✅ <5min execution time

### Qualitative
- ✅ Master plan is comprehensive
- ✅ Validation is thorough
- ✅ Documentation is clear
- ✅ Ready for execution

---

## Phase Completion Checklist

- [ ] All workstreams complete
- [ ] All tasks executed
- [ ] All acceptance criteria met
- [ ] All quality gates passed
- [ ] Documentation generated
- [ ] Files archived
- [ ] Phase summary created
- [ ] Next phase planned

---

**Phase Owner**: AI Agent  
**Approver**: Human Reviewer  
**Priority**: CRITICAL  
**Status**: READY FOR EXECUTION

---

## Notes

- This phase is **independent** - no dependencies on other phases
- Patch application is **idempotent** - can be re-run safely
- Validation is **comprehensive** - multiple layers of checks
- Output is **production-ready** - fully validated master plan

---

**END OF PHASE PLAN**
