---
doc_id: DOC-GUIDE-COMPLETE-PHASE-PLAN-403
---

# Complete Phase Plan - Doc ID System Completion

**Date**: 2025-11-30  
**Status**: Active Roadmap  
**Purpose**: Synthesize all historical work + current progress into definitive completion plan

---

## Executive Summary

### Current State
- **Phase 3 Complete** (Nov 29): 271 docs, documentation governance established
- **Phase 0 In Progress** (Nov 30): 984 docs (34%), auto-assignment tools built and tested
- **Analysis Complete**: Comprehensive framework analysis and validation

### Final Target
- **100% Coverage**: All 2,894 eligible files with doc_ids
- **Production Ready**: Full ID Suite operational with CI/CD integration
- **Documentation Complete**: All specs, guides, and tools documented

### Remaining Effort
- **2-3 hours**: Complete Phase 0 (file assignment)
- **2-4 hours**: CI/CD integration and documentation
- **Total**: 4-7 hours to full completion

---

## Phase Overview

```
✅ Phase 3 (Nov 29)    Documentation Governance      COMPLETE
⏳ Phase 0 (Nov 30)    Universal Coverage           60% COMPLETE
🔜 Phase 1             CI/CD Integration            NOT STARTED
🔜 Phase 1.5           Module ID Extension          NOT STARTED
🔜 Phase 2             Production Hardening         NOT STARTED
🔜 Phase 3.5           Documentation Consolidation  NOT STARTED
```

---

## PHASE 0: Universal Coverage (In Progress)

### Goal
**100% doc_id coverage** across all eligible files before any structural refactoring.

### Status
- **Current Coverage**: 25.0% (724/2,894 files)
- **Registry Size**: 984 docs (was 271)
- **Tools**: ✅ Built and tested

### Completed Work ✅

1. **Tools Built**
   - `doc_id_scanner.py` (334 lines) - Repository scanning
   - `doc_id_assigner.py` (550 lines) - Auto-assignment
   - Both tools tested and operational

2. **Files Assigned**
   - YAML/YML: 210 files (84.4% coverage) ✅
   - JSON: 336 files (75.0% coverage) ✅
   - PowerShell: 143 files (94.5% coverage) ✅
   - Text: ~17 files (partial) ✅

3. **Documentation Created**
   - `ID_KEY_CHEATSHEET.md` - Complete reference
   - `COMPLETE_IMPLEMENTATION_REPORT.md` - Status report
   - `DEVELOPMENT_ROADMAP.md` - Step-by-step guide
   - `QUICK_START_CHECKLIST.md` - Actionable checklist
   - `ANALYSIS_VS_IMPLEMENTATION_COMPARISON.md` - Historical comparison
   - `HISTORICAL_VS_CURRENT_SESSION_COMPARISON.md` - Session analysis

### Remaining Work ⏳

**Task 0.1: Fix Name Sanitization** (15 min)
- Issue: Files with special characters/leading dashes fail validation
- Solution: Improve regex in `doc_id_assigner.py` line 175
- Files affected: ~5-10 edge cases

**Task 0.2: Complete Python Assignment** (60 min)
```bash
# 812 Python files in 4 batches of 200
python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_1.json
git add . && git commit -m "chore: Phase 0 - Python batch 1 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_2.json
git add . && git commit -m "chore: Phase 0 - Python batch 2 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_3.json
git add . && git commit -m "chore: Phase 0 - Python batch 3 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_4.json
git add . && git commit -m "chore: Phase 0 - Python batch 4 (200 files)"

# Remaining ~12 files
python scripts/doc_id_assigner.py auto-assign --types py --report reports/batch_py_final.json
git add . && git commit -m "chore: Phase 0 - Python final (~12 files)"
```
**Expected**: ~812 files, Coverage: 25% → 55%

**Task 0.3: Complete Markdown Assignment** (90 min)
```bash
# 1,099 Markdown files in 5 batches of 250
# Note: ~90 files already have IDs from Phase 3 (will be skipped)
python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_1.json
git add . && git commit -m "chore: Phase 0 - Markdown batch 1 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_2.json
git add . && git commit -m "chore: Phase 0 - Markdown batch 2 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_3.json
git add . && git commit -m "chore: Phase 0 - Markdown batch 3 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_4.json
git add . && git commit -m "chore: Phase 0 - Markdown batch 4 (250 files)"

# Remaining ~100 files
python scripts/doc_id_assigner.py auto-assign --types md --report reports/batch_md_final.json
git add . && git commit -m "chore: Phase 0 - Markdown final (~100 files)"
```
**Expected**: ~1,000 new files (90 already done), Coverage: 55% → 95%

**Task 0.4: Complete Shell/Text Files** (15 min)
```bash
# Fix edge cases, then assign remaining ~112 files
python scripts/doc_id_assigner.py auto-assign --types sh txt --report reports/batch_sh_txt_final.json
git add . && git commit -m "chore: Phase 0 - Shell and Text files (~112 files)"
```
**Expected**: ~112 files, Coverage: 95% → 100%

**Task 0.5: Final Validation** (15 min)
```bash
# Final scan
python scripts/doc_id_scanner.py scan

# Verify 100% coverage
python scripts/doc_id_scanner.py stats
# Expected: Files with doc_id: 2894 (100.0%)

# Validate registry
python doc_id/tools/doc_id_registry_cli.py validate
# Expected: No errors

# Generate final reports
python scripts/doc_id_scanner.py scan > reports/final_coverage_report.txt
python doc_id/tools/doc_id_registry_cli.py stats > reports/final_registry_stats.txt
```

**Task 0.6: Merge to Main** (15 min)
```bash
# Final commit on feature branch
git add .
git commit -m "chore: Phase 0 complete - 100% doc_id coverage

- Total files assigned: 2,726 new doc_ids
- Coverage: 5.6% → 100%
- Registry: 274 → ~3,160 docs
- All eligible file types covered
- Tools: scanner + auto-assigner operational
- Ready for production use"

# Switch to main and merge
git checkout main
git merge feature/phase0-docid-assignment --no-ff
git push origin main

# Tag release
git tag -a v1.0.0-docid-phase0 -m "Phase 0: Universal doc_id coverage achieved"
git push origin v1.0.0-docid-phase0
```

### Success Criteria
- [ ] Coverage = 100% (2,894/2,894 files)
- [ ] Registry validates with 0 errors
- [ ] No duplicate doc_ids
- [ ] All commits pushed to main
- [ ] Release tagged

**Estimated Time**: 3 hours total

---

## PHASE 1: CI/CD Integration

### Goal
Enforce doc_id coverage and health as **automated gates** in CI/CD pipeline.

### Tasks

**Task 1.1: Create Preflight Validator** (45 min)

Create `scripts/doc_id_preflight.py`:
```python
#!/usr/bin/env python3
"""
Doc ID Preflight Validator
Runs before refactors and in CI to ensure ID health.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-coverage', type=float, default=1.0)
    parser.add_argument('--skip-registry', action='store_true')
    args = parser.parse_args()
    
    # 1. Check inventory exists
    # 2. Verify coverage >= min_coverage
    # 3. Run registry validation
    # 4. Exit non-zero on failure
```

Create `scripts/doc_id_preflight.ps1`:
```powershell
# PowerShell wrapper
param(
    [double]$MinCoverage = 1.0,
    [switch]$SkipRegistry
)

# Refresh inventory
python scripts/doc_id_scanner.py scan

# Run preflight
$params = @("--min-coverage", $MinCoverage)
if ($SkipRegistry) { $params += "--skip-registry" }
python scripts/doc_id_preflight.py @params
exit $LASTEXITCODE
```

**Task 1.2: Add GitHub Actions Workflow** (30 min)

Create `.github/workflows/doc_id_preflight.yml`:
```yaml
name: Doc ID Preflight

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Run Doc ID Preflight
        run: |
          python scripts/doc_id_scanner.py scan
          python scripts/doc_id_preflight.py --min-coverage 1.0
```

**Task 1.3: Add Pre-commit Hook** (optional, 15 min)

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check doc_id coverage before commit
python scripts/doc_id_scanner.py scan --quiet
python scripts/doc_id_preflight.py --min-coverage 1.0
```

**Task 1.4: Update Documentation** (30 min)
- Add CI/CD section to `DEVELOPMENT_ROADMAP.md`
- Update `README.md` with build badge
- Document preflight usage in `QUICK_START_CHECKLIST.md`

### Success Criteria
- [ ] Preflight validator working locally
- [ ] CI workflow passing on main
- [ ] Documentation updated
- [ ] Pre-commit hook (optional)

**Estimated Time**: 2 hours

---

## PHASE 1.5: Module ID Extension

### Goal
Extend DOC_ID_REGISTRY.yaml with `module_id` field for every doc entry to enable module-centric organization.

### Background
After achieving 100% doc_id coverage (Phase 0) and establishing CI/CD gates (Phase 1), we need to add module ownership metadata. This prepares the codebase for future module-centric refactoring.

**Specification**: See `MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1.md`  
**Integration Plan**: See `MODULE_ID_INTEGRATION_PLAN.md`

### Prerequisites
- ✅ Phase 0 complete (100% coverage)
- ✅ Phase 1 complete (CI/CD gates active)
- ✅ Registry validates with 0 errors

### Tasks

**Task 1.5.1: Create Module Assignment Script** (60 min)

Create `scripts/module_id_assigner.py`:
- Parse DOC_ID_REGISTRY.yaml
- Implement path-based inference rules
- Support dry-run and apply modes
- Generate assignment reports

**Path inference rules**:
```python
# Core modules
'core/engine/' → 'core.engine'
'core/state/' → 'core.state'
'error/' → 'core.error'

# AIM
'aim/adapters/' → 'aim.adapters'
'aim/core/' → 'aim.core'

# Patterns
'patterns/specs/' → 'patterns.specs'
'patterns/executors/' → 'patterns.executors'

# Docs/Guides
'doc_id/', 'docs/' → 'docs.guides'

# ADR
'adr/' → 'adr.architecture'

# Config/Infra
'config/' → 'config.global'
'infra/', '.github/' → 'infra.ci'

# Tests inherit from source module
'tests/engine/' → 'core.engine'
```

**Task 1.5.2: Create Module Taxonomy** (30 min)

Create `doc_id/specs/module_taxonomy.yaml`:
```yaml
module_taxonomy:
  core.engine:
    description: Core execution engine components
    root_paths:
      - core/engine
      - tests/engine
  
  core.state:
    description: State management and persistence
    root_paths:
      - core/state
      - tests/state
  
  # ... 12 total modules defined
```

**Task 1.5.3: Dry-Run Assignment** (15 min)
```bash
# Run dry-run
python scripts/module_id_assigner.py --dry-run

# Review reports
cat doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md
cat doc_id/reports/MODULE_ID_UNASSIGNED.jsonl

# Verify distribution looks reasonable
```

**Task 1.5.4: Apply Module ID Assignment** (30 min)
```bash
# Backup registry
cp doc_id/specs/DOC_ID_REGISTRY.yaml \
   doc_id/specs/DOC_ID_REGISTRY.backup.$(date +%Y%m%d_%H%M).yaml

# Apply assignment
python scripts/module_id_assigner.py --apply

# Validate
python doc_id/tools/doc_id_registry_cli.py validate

# Review final stats
cat doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json

# Commit
git add doc_id/specs/ doc_id/reports/
git commit -m "feat: Add module_id to all docs in registry"
```

**Task 1.5.5: Create Module Map** (30 min)

Create `scripts/build_module_map.py` and generate:
```bash
# Generate module-centric map
python scripts/build_module_map.py

# Output: modules/MODULE_DOC_MAP.yaml
# Structure: modules grouped by module_id

# Commit
git add modules/MODULE_DOC_MAP.yaml
git commit -m "feat: Create module-centric documentation map"
```

**Task 1.5.6: Extend Registry CLI** (Optional, 45 min)

Add to `doc_id/tools/doc_id_registry_cli.py`:
```python
@cli.command()
def module_assign():
    """Assign module_id to all docs"""
    
@cli.command()
def build_module_map():
    """Build MODULE_DOC_MAP.yaml"""
```

**Task 1.5.7: Final Validation** (15 min)
```bash
# Validate all module_ids assigned
python scripts/validate_module_ids.py

# Generate summary
python scripts/module_id_summary.py > doc_id/reports/MODULE_ID_SUMMARY.md

# Final checks
python scripts/doc_id_scanner.py stats
python doc_id/tools/doc_id_registry_cli.py validate
```

### Success Criteria
- [ ] Every doc has `module_id` field
- [ ] `module_taxonomy` section in registry
- [ ] MODULE_DOC_MAP.yaml created
- [ ] ≤ 5% docs marked `unassigned`
- [ ] Registry validates
- [ ] All reports generated

### Outputs
- Updated `DOC_ID_REGISTRY.yaml` with module_id
- New `module_taxonomy` in registry
- `modules/MODULE_DOC_MAP.yaml`
- Reports in `doc_id/reports/MODULE_ID_*`

**Estimated Time**: 3 hours

---

## PHASE 2: Production Hardening

### Goal
Address edge cases, improve robustness, add monitoring.

### Tasks

**Task 2.1: Edge Case Fixes** (60 min)

1. **Better Name Sanitization**
   ```python
   # In doc_id_assigner.py
   def sanitize_name(name: str) -> str:
       # Remove leading special chars
       name = re.sub(r'^[^A-Za-z0-9]+', '', name)
       # Replace special chars with dashes
       name = re.sub(r'[^A-Za-z0-9-]+', '-', name)
       # Collapse multiple dashes
       name = re.sub(r'-+', '-', name)
       # Remove trailing dashes
       name = name.strip('-')
       # Limit length
       return name[:40].upper()
   ```

2. **Submodule Exclusion**
   ```python
   # In doc_id_scanner.py
   EXCLUDE_PATTERNS = [
       '.git/',
       '.venv/',
       '__pycache__/',
       '.worktrees/',
       'ccpm/',  # Exclude submodules
       # ... existing patterns
   ]
   ```

3. **Registry YAML Validation**
   ```python
   # Pre-commit check for valid YAML
   try:
       yaml.safe_load(registry_content)
   except yaml.YAMLError as e:
       print(f"Registry YAML invalid: {e}")
       exit(1)
   ```

**Task 2.2: Add Coverage Tracking** (45 min)

Create `scripts/doc_id_coverage_trend.py`:
```python
"""Track doc_id coverage over time."""

def save_snapshot():
    stats = get_current_stats()
    with open('doc_id/reports/coverage_history.jsonl', 'a') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': stats['total'],
            'files_with_docid': stats['covered'],
            'coverage_pct': stats['coverage']
        }, f)
        f.write('\n')

def generate_trend_report():
    # Read coverage_history.jsonl
    # Generate markdown report with trend
    pass
```

**Task 2.3: Add Conflict Detection** (30 min)

Enhance registry CLI:
```python
def detect_conflicts(self):
    """Detect duplicate doc_ids or inconsistent paths."""
    seen_ids = {}
    conflicts = []
    for doc in self.registry['docs']:
        doc_id = doc['doc_id']
        if doc_id in seen_ids:
            conflicts.append({
                'doc_id': doc_id,
                'paths': [seen_ids[doc_id], doc['path']]
            })
        seen_ids[doc_id] = doc['path']
    return conflicts
```

**Task 2.4: Improve Error Messages** (30 min)
- User-friendly error messages
- Suggestions for fixes
- Links to documentation

### Success Criteria
- [ ] All edge cases handled
- [ ] Coverage tracking operational
- [ ] Conflict detection working
- [ ] Error messages improved

**Estimated Time**: 2.5 hours

---

## PHASE 3.5: Documentation Consolidation

### Goal
Consolidate, organize, and finalize all documentation for the ID Suite.

### Tasks

**Task 3.5.1: Create ID Suite Master Overview** (60 min)

Create `doc_id/ID_SUITE_FEATURES_OVERVIEW.md` (use provided draft):
- Complete overview of all ID Suite components
- Integration guide for humans and AI
- TL;DR for agents
- Reference to all tools and specs

**Task 3.5.2: Organize Documentation** (45 min)

```
doc_id/
├── README.md                              # High-level overview
├── ID_SUITE_FEATURES_OVERVIEW.md          # Master reference (NEW)
├── ID_KEY_CHEATSHEET.md                   # Quick reference
├── specs/
│   ├── README.md
│   ├── DOC_ID_FRAMEWORK.md
│   ├── DOC_ID_REGISTRY.yaml
│   ├── FILE_LIFECYCLE_RULES.md
│   └── UTE_ID_SYSTEM_SPEC.md              # To be created
├── analysis/                              # Historical analysis
│   ├── README.md
│   ├── ID_FRAMEWORK_EXPLORATION_SUMMARY.md
│   ├── ID_FRAMEWORK_ANALYSIS_AND_ROADMAP.md
│   ├── AI_EVAL_REALITY_CHECK.md
│   ├── CONFLICT_ANALYSIS_AND_RESOLUTION.md
│   └── [other analysis files]
├── implementation/                        # Current implementation docs
│   ├── README.md                          # NEW
│   ├── COMPLETE_IMPLEMENTATION_REPORT.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── QUICK_START_CHECKLIST.md
│   ├── ASSIGNER_IMPLEMENTATION_SUMMARY.md
│   ├── SCRIPTS_DISCOVERY_SUMMARY.md
│   ├── ANALYSIS_VS_IMPLEMENTATION_COMPARISON.md
│   └── HISTORICAL_VS_CURRENT_SESSION_COMPARISON.md
├── session_reports/                       # Phase completion reports
│   ├── README.md
│   ├── DOC_ID_PROJECT_PHASE3_COMPLETE.md
│   ├── ALL_REMAINING_FILES_COMPLETE.md
│   └── DOC_ID_PROJECT_PHASE0_COMPLETE.md  # To be created
├── reports/                               # Generated reports
│   ├── README.md
│   ├── docs_inventory.jsonl
│   ├── DOC_ID_COVERAGE_REPORT.md
│   └── DOC_ID_FOLDER_INDEX.md
├── tools/
│   ├── README.md
│   ├── doc_id_registry_cli.py
│   └── [other tools]
└── archive/                               # Archived tools/docs
    ├── phase3_tools/
    │   ├── batch_mint.py
    │   ├── merge_deltas.py
    │   └── write_doc_ids_to_files.py
    ├── phase3_batches/
    └── phase3_deltas/
```

**Task 3.5.3: Create Missing Specs** (60 min)

1. **UTE_ID_SYSTEM_SPEC.md**
   - General-purpose ID system specification
   - Repo-agnostic rules
   - Namespace and domain concepts

2. **DOC_ID_PARALLEL_EXECUTION_GUIDE.md** (if doesn't exist)
   - Multi-worktree workflows
   - Parallel assignment procedures
   - Conflict resolution

**Task 3.5.4: Update All READMEs** (30 min)
- Update `doc_id/README.md` with Phase 0 completion
- Update `scripts/README.md` with new tools
- Update main `README.md` with doc_id section

**Task 3.5.5: Create Phase 0 Completion Report** (45 min)

Create `doc_id/session_reports/DOC_ID_PROJECT_PHASE0_COMPLETE.md`:
- Phase objectives and outcomes
- Tools created
- Coverage achieved
- Lessons learned
- Next steps (Phase 1)

**Task 3.5.6: Archive Phase 3 Tools** (30 min)
```bash
# Create archive directory
mkdir -p doc_id/archive/phase3_tools
mkdir -p doc_id/archive/phase3_batches
mkdir -p doc_id/archive/phase3_deltas

# Move files
mv batch_mint.py doc_id/archive/phase3_tools/
mv merge_deltas.py doc_id/archive/phase3_tools/
mv write_doc_ids_to_files.py doc_id/archive/phase3_tools/
mv doc_id/batches/*.yaml doc_id/archive/phase3_batches/
mv doc_id/deltas/*.jsonl doc_id/archive/phase3_deltas/

# Create archive README
cat > doc_id/archive/README.md << 'EOF'
# Archived Doc ID Tools

This directory contains tools and artifacts from earlier phases.

## Phase 3 Tools (Nov 29, 2025)
- **batch_mint.py**: Batch-based ID minting (superseded by auto-assigner)
- **merge_deltas.py**: Delta file merging (superseded by direct assignment)
- **write_doc_ids_to_files.py**: File writing (integrated into auto-assigner)

These tools used a 4-step batch-driven workflow with delta files.
Phase 0 (Nov 30, 2025) replaced this with a 2-step automated workflow.

See `../implementation/HISTORICAL_VS_CURRENT_SESSION_COMPARISON.md` for details.
EOF

git add doc_id/archive/
git commit -m "chore: Archive Phase 3 batch-based tools"
```

### Success Criteria
- [ ] ID_SUITE_FEATURES_OVERVIEW.md created
- [ ] Documentation reorganized
- [ ] All READMEs updated
- [ ] Phase 0 completion report written
- [ ] Phase 3 tools archived
- [ ] Missing specs created

**Estimated Time**: 4 hours

---

## Timeline & Dependencies

```
Phase 0 (Current)  ─────┬──────────────────┐
                        │ 3 hours          │
                        └─────────────┐    │
                                      ▼    │
Phase 1 (CI/CD)  ────────────────────┬────┘
                        │ 2 hours    │
                        └────────────┐
                                     ▼
Phase 1.5 (Module)  ─────────────────┬────┐
                        │ 3 hours    │    │
                        └────────────┐    │
                                     ▼    │
Phase 2 (Hardening) ─────────────────┬────┤
                        │ 2.5 hours  │    │
                        └────────────┐    │
                                     ▼    │
Phase 3.5 (Docs)  ───────────────────┴────┘
                        │ 4 hours
                        └────────────▼
                                  COMPLETE
```

**Total Estimated Time**: 14.5 hours (1.8 workdays)

---

## Success Metrics

### Phase 0 Complete
- ✅ 100% coverage (2,894/2,894 files)
- ✅ Registry: ~3,160 docs
- ✅ 0 validation errors
- ✅ All tools operational

### Phase 1 Complete
- ✅ CI/CD enforcing coverage
- ✅ Preflight gates working
- ✅ Build badge on README

### Phase 1.5 Complete
- ✅ All docs have module_id
- ✅ Module taxonomy defined
- ✅ MODULE_DOC_MAP.yaml created
- ✅ ≤ 5% unassigned docs

### Phase 2 Complete
- ✅ Edge cases handled
- ✅ Coverage tracking automated
- ✅ Conflict detection working

### Phase 3.5 Complete
- ✅ All documentation consolidated
- ✅ ID Suite master overview created
- ✅ Phase 0 completion report published
- ✅ Phase 3 tools archived

---

## Quick Start Commands

### Continue Phase 0 Now
```bash
# Fix name sanitization
# Edit scripts/doc_id_assigner.py line 175-185

# Python batch 1
python scripts/doc_id_assigner.py auto-assign --types py --limit 200
git add . && git commit -m "chore: Phase 0 - Python batch 1"

# Continue with remaining batches...
```

### Start Phase 1 After Phase 0
```bash
# Create preflight validator
cp doc_id/templates/doc_id_preflight.py scripts/
# Edit and customize

# Add CI workflow
mkdir -p .github/workflows
cp doc_id/templates/doc_id_preflight.yml .github/workflows/

# Test locally
python scripts/doc_id_preflight.py --min-coverage 1.0
```

---

## Risk Mitigation

### Risk 1: Time Overruns
**Mitigation**: Phases can be completed independently; prioritize Phase 0 completion.

### Risk 2: Edge Case Files
**Mitigation**: Use `--dry-run` extensively; manual review of problematic files.

### Risk 3: Registry Corruption
**Mitigation**: Git commits after each batch; backup branch maintained.

### Risk 4: CI Integration Issues
**Mitigation**: Test preflight locally before pushing to CI; use transitional coverage thresholds.

---

## Final Deliverables

1. ✅ **100% doc_id coverage** - All files assigned
2. ✅ **Working CI/CD gates** - Automated enforcement
3. ✅ **Complete documentation** - Master overview + guides
4. ✅ **Production tools** - Scanner, assigner, validator
5. ✅ **Historical record** - Phase reports and analysis

---

**Status**: Ready to execute  
**Next Action**: Continue Phase 0 with Python batch assignment  
**Estimated Completion**: 1-2 workdays from now

