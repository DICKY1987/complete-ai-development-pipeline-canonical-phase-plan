# Phase H: Directory Consolidation & Structure Cleanup Plan

**Version:** 1.0.0  
**Status:** Draft  
**Created:** 2025-11-21  
**Owner:** Repository Maintainer

## Executive Summary

This phase addresses duplicate, deprecated, and misplaced directories in the repository structure. The goal is to consolidate spec-related folders, eliminate legacy duplicates, and ensure all code follows the canonical section-based organization defined in AGENTS.md.

## Objectives

1. **Consolidate spec-related directories** (`spec/`, `specs/` → `specifications/`)
2. **Eliminate root-level duplicates** of `core/` subdirectories
3. **Archive legacy/temporary folders** that are no longer active
4. **Reclassify infrastructure folders** for clarity
5. **Update all import paths** to reflect new structure
6. **Validate CI/build systems** after consolidation

## Phase Structure

### Phase H1: Specification Consolidation (Priority: HIGH)
**Goal:** Merge all spec-related folders into canonical `specifications/` structure

### Phase H2: Core Structure Cleanup (Priority: HIGH)
**Goal:** Remove duplicate core infrastructure folders

### Phase H3: Legacy Archive (Priority: MEDIUM)
**Goal:** Archive or remove deprecated/temporary folders

### Phase H4: Infrastructure Reclassification (Priority: LOW)
**Goal:** Reorganize infrastructure and documentation folders

### Phase H5: Validation & Migration (Priority: HIGH)
**Goal:** Update imports, validate build/test systems, update documentation

---

## Phase H1: Specification Consolidation

### H1.1: Audit Current Spec Folders

**Tasks:**
- [ ] Inventory all files in `spec/`
- [ ] Inventory all files in `specs/`
- [ ] Inventory all files in `specifications/`
- [ ] Identify duplicates and unique content
- [ ] Map dependencies (imports, references)

**Deliverables:**
- `SPEC_CONSOLIDATION_INVENTORY.md` - Complete file mapping
- `SPEC_CONSOLIDATION_DEPENDENCIES.txt` - Import/reference analysis

**Success Criteria:**
- All files catalogued with source/destination mapping
- All import dependencies identified
- No duplicate functionality between folders

### H1.2: Merge spec/ → specifications/

**Tasks:**
- [ ] Move `spec/tools/*` → `specifications/tools/`
- [ ] Merge `spec/__init__.py` into `specifications/`
- [ ] Update imports in all files referencing `spec.*`
- [ ] Run import validator: `python scripts/validate_error_imports.py`
- [ ] Run tests: `pytest tests/ -k spec`

**Pre-conditions:**
- H1.1 complete
- Backup created: `git checkout -b backup/pre-spec-consolidation`

**Rollback Plan:**
- Restore from branch: `git checkout backup/pre-spec-consolidation`

**Success Criteria:**
- All files moved without data loss
- All imports updated and validated
- Tests pass
- No references to old `spec/` paths remain

### H1.3: Merge specs/ → specifications/

**Tasks:**
- [ ] Analyze `specs/jobs/` content and purpose
- [ ] Determine if `specs/jobs/` is active or legacy
- [ ] If active: Move to `specifications/content/jobs/` or appropriate subdirectory
- [ ] If legacy: Move to `specifications/archive/legacy-jobs/`
- [ ] Update any references to `specs/`
- [ ] Run full test suite

**Success Criteria:**
- `specs/` folder content properly integrated or archived
- No broken references
- Tests pass

### H1.4: Consolidate Root tools/ → specifications/tools/

**Tasks:**
- [ ] Audit `tools/hardcoded_path_indexer.py` for spec-related functionality
- [ ] Move spec-related tools from `tools/` → `specifications/tools/`
- [ ] Keep non-spec tools in root `tools/` (if any)
- [ ] Update imports across codebase
- [ ] Update `scripts/` that reference these tools
- [ ] Run: `python scripts/check_deprecated_usage.py`

**Success Criteria:**
- Clear separation: spec tools in `specifications/tools/`, other utilities in root `tools/`
- All imports working
- Scripts execute successfully

### H1.5: Update Documentation

**Tasks:**
- [ ] Update `docs/SECTION_REFACTOR_MAPPING.md` with spec consolidation
- [ ] Update `AGENTS.md` to remove deprecated paths
- [ ] Update `README.md` if it references old structure
- [ ] Create `specifications/MIGRATION_COMPLETE.md` with final structure

**Deliverables:**
- Updated documentation reflecting new canonical structure

---

## Phase H2: Core Structure Cleanup

### H2.1: Audit Root-Level Core Duplicates

**Tasks:**
- [ ] Compare `engine/` (root) vs `core/engine/`
- [ ] Compare `state/` (root) vs `core/state/`
- [ ] Identify if root-level versions are:
  - Exact duplicates (delete)
  - Legacy versions (archive)
  - Different implementations (reconcile)
- [ ] Check for imports referencing root-level versions
- [ ] Document findings in `CORE_DUPLICATE_ANALYSIS.md`

**Success Criteria:**
- Clear understanding of relationship between duplicate folders
- Decision matrix for each: keep/merge/archive/delete

### H2.2: Resolve engine/ Duplication

**Decision Tree:**
- **If `engine/` == `core/engine/`:** Delete `engine/`, ensure all imports use `core.engine`
- **If `engine/` is legacy:** Move to `docs/archive/legacy-engine/`
- **If `engine/` has unique code:** Merge unique functionality into `core/engine/`

**Tasks:**
- [ ] Execute decision based on H2.1 findings
- [ ] Update imports: `from engine.* → from core.engine.*`
- [ ] Run import migration: `python scripts/auto_migrate_imports.py`
- [ ] Validate: `python scripts/validate_engine.py`
- [ ] Run tests: `pytest tests/ -k engine`

**Rollback Plan:**
- Git branch: `backup/pre-engine-consolidation`

### H2.3: Resolve state/ Duplication

**Decision Tree:**
- **If `state/` is just database file:** Move `pipeline_state.db` → `core/state/` or `.worktrees/`
- **If `state/` has code:** Merge into `core/state/`

**Tasks:**
- [ ] Execute decision based on H2.1 findings
- [ ] Update database path references in code
- [ ] Update `.gitignore` if needed for new db location
- [ ] Run: `python scripts/db_inspect.py` to validate database integrity
- [ ] Run state tests: `pytest tests/ -k state`

**Success Criteria:**
- Single source of truth for state management in `core/state/`
- Database accessible and validated
- Tests pass

---

## Phase H3: Legacy Archive

### H3.1: Identify Legacy/Temporary Folders

**Candidates:**
- `build/` - Contains only `spec.md` (build artifact?)
- `bundles/` - Single test file (merge into `workstreams/` or `tests/`)
- `pipeline_plus/` - Prototype/archived code
- Root-level markdown files (various notes/cleanup reports)

**Tasks:**
- [ ] Review each folder's last modification date
- [ ] Check git history for recent activity
- [ ] Identify folders untouched for >90 days
- [ ] Cross-reference with active development docs

**Deliverables:**
- `LEGACY_ARCHIVE_CANDIDATES.md` - List with disposition (archive/delete/keep)

### H3.2: Archive Legacy Folders

**Tasks:**
- [ ] Create `docs/archive/phase-h-legacy/` directory
- [ ] Move identified legacy folders:
  - `build/` → `docs/archive/phase-h-legacy/build/`
  - `pipeline_plus/` → `docs/archive/phase-h-legacy/pipeline_plus/`
- [ ] Document in `docs/archive/phase-h-legacy/README.md`:
  - What was archived
  - Why (reason/criteria)
  - Date of archival
  - Where to find if needed

**Success Criteria:**
- Legacy code preserved but out of active structure
- Archive documented
- Root directory cleaner

### H3.3: Consolidate bundles/

**Decision:**
- If `bundles/openspec-test-001.yaml` is active test → move to `tests/fixtures/`
- If example workstream → move to `workstreams/examples/`
- If legacy → archive

**Tasks:**
- [ ] Determine purpose of `bundles/openspec-test-001.yaml`
- [ ] Move to appropriate location
- [ ] Update references in code/docs
- [ ] Remove empty `bundles/` directory

---

## Phase H4: Infrastructure Reclassification

### H4.1: Reorganize Documentation Resources

**Current Scattered Locations:**
- `Prompt/` - Prompt engineering guides
- `CMD/` - Task automation configs
- `gui/` - GUI design docs
- Root-level markdown files

**Proposed Structure:**
```
docs/
├── reference/
│   ├── prompts/           # From Prompt/
│   └── task-automation/   # From CMD/
├── design/
│   └── gui/               # From gui/
└── archive/
    └── cleanup-reports/   # Root-level cleanup reports
```

**Tasks:**
- [ ] Move `Prompt/*` → `docs/reference/prompts/`
- [ ] Move `CMD/*` → `docs/reference/task-automation/`
- [ ] Move `gui/*` → `docs/design/gui/`
- [ ] Move root-level cleanup reports → `docs/archive/cleanup-reports/`
- [ ] Update any references to old paths
- [ ] Update `docs/.index` with new structure

### H4.2: Classify Sub-Modules

**Current Sub-Module Candidates:**
- `AGENTIC_DEV_PROTOTYPE/` - Prototype system
- `AI_MANGER/` - Another AI orchestration prototype
- `PROCESS_DEEP_DIVE_OPTOMIZE/` - Analysis/optimization
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` - Template framework
- `Multi-Document Versioning Automation final_spec_docs/` - Versioning system

**Tasks:**
- [ ] Create `docs/SUB_MODULE_REGISTRY.md` documenting:
  - Each sub-module's purpose
  - Status (active/experimental/deprecated)
  - Relationship to main pipeline
  - Maintenance owner
- [ ] Add AGENTS.md to each sub-module if missing
- [ ] Add README.md to each sub-module if missing

**Deliverables:**
- Clear sub-module taxonomy
- Documentation for each sub-module

### H4.3: Consolidate AUX_mcp-data/ → aim/

**Tasks:**
- [ ] Audit `AUX_mcp-data/` contents
- [ ] Identify MCP-related AIM integration files
- [ ] Move to `aim/mcp-data/` or `aim/aux/`
- [ ] Update references in `aim/` code
- [ ] Update documentation in `docs/AIM_docs/`

**Success Criteria:**
- All AIM-related data in `aim/` section
- No orphaned references
- AIM integration tests pass

### H4.4: Classify infra/

**Current Structure:**
- `infra/ci/` - CI/CD configuration

**Proposed:**
- Keep as-is: `infra/` is a valid repository infrastructure folder
- Add `infra/README.md` documenting purpose

**Tasks:**
- [ ] Create `infra/README.md`
- [ ] Document CI/CD structure
- [ ] Ensure AGENTS.md reflects `infra/` as valid section

---

## Phase H5: Validation & Migration

### H5.1: Update All Import Paths

**Tasks:**
- [ ] Run: `python scripts/auto_migrate_imports.py --dry-run`
- [ ] Review migration plan
- [ ] Run: `python scripts/auto_migrate_imports.py --execute`
- [ ] Run: `python scripts/check_deprecated_usage.py`
- [ ] Fix any remaining deprecated imports manually
- [ ] Run: `python scripts/validate_error_imports.py`

**Success Criteria:**
- No deprecated import paths remain
- All imports follow section-based pattern (per CI_PATH_STANDARDS.md)
- Import validators pass

### H5.2: Update Build & CI Systems

**Tasks:**
- [ ] Update `.github/workflows/` if they reference old paths
- [ ] Update `pytest.ini` with new paths/exclusions
- [ ] Update `.aiderignore` with archived paths
- [ ] Update `invoke.yaml` task configurations
- [ ] Run full build: `pwsh scripts/bootstrap.ps1`
- [ ] Run full test suite: `pytest -v`

**Success Criteria:**
- Build completes successfully
- All tests pass
- No path-related errors in CI

### H5.3: Update Scripts

**Tasks:**
- [ ] Audit all scripts in `scripts/` for hardcoded paths
- [ ] Update path references to new structure
- [ ] Test each script:
  - `python scripts/generate_spec_index.py`
  - `python scripts/generate_spec_mapping.py`
  - `python scripts/run_workstream.py`
  - `python scripts/run_error_engine.py`
  - `pwsh scripts/test.ps1`

**Success Criteria:**
- All scripts execute without path errors
- Generated outputs reflect new structure

### H5.4: Update Documentation

**Critical Files to Update:**
- [ ] `AGENTS.md` - Remove deprecated paths, update examples
- [ ] `README.md` - Update project structure section
- [ ] `docs/ARCHITECTURE.md` - Update directory tree
- [ ] `docs/SECTION_REFACTOR_MAPPING.md` - Add Phase H changes
- [ ] `docs/CI_PATH_STANDARDS.md` - Update enforced paths
- [ ] All phase plans referencing old paths

**Tasks:**
- [ ] Update each file systematically
- [ ] Cross-reference with new structure
- [ ] Run markdown linter if configured
- [ ] Review for broken internal links

### H5.5: Final Validation

**Tasks:**
- [ ] Run full test suite: `pytest -v --tb=short`
- [ ] Run all validators:
  - `python scripts/validate_workstreams.py`
  - `python scripts/validate_workstreams_authoring.py`
  - `python scripts/validate_engine.py`
  - `python scripts/check_deprecated_usage.py`
- [ ] Run build: `pwsh scripts/bootstrap.ps1`
- [ ] Generate fresh indices:
  - `python scripts/generate_spec_index.py`
  - `python scripts/generate_spec_mapping.py`
- [ ] Smoke test core workflows:
  - Load workstream
  - Run single step
  - Check error detection
- [ ] Review git status for untracked/leftover files

**Success Criteria:**
- ✅ All tests pass
- ✅ All validators pass
- ✅ Build succeeds
- ✅ Indices generated successfully
- ✅ Core workflows execute
- ✅ No orphaned files

---

## Risk Assessment

### High Risk
- **Import path breakage** - Mitigated by comprehensive test suite and import validators
- **Lost functionality** - Mitigated by careful inventory and backup branches
- **Database corruption** - Mitigated by database backups before state/ changes

### Medium Risk
- **Documentation drift** - Mitigated by systematic doc updates in H5.4
- **CI/build failures** - Mitigated by incremental testing and rollback plans

### Low Risk
- **Sub-module confusion** - Mitigated by registry documentation
- **Archive access** - Mitigated by clear archive documentation

## Rollback Strategy

Each phase has a backup branch:
- `backup/pre-spec-consolidation` (H1)
- `backup/pre-engine-consolidation` (H2)
- `backup/pre-legacy-archive` (H3)
- `backup/pre-infra-reorg` (H4)
- `backup/pre-validation` (H5)

**Rollback Procedure:**
```bash
# Identify which phase to roll back to
git log --oneline --graph
# Reset to backup branch
git reset --hard backup/pre-<phase>-<name>
# Force push if already pushed (use with caution)
git push origin main --force-with-lease
```

## Dependencies

- **Blocks:** Any new feature development referencing spec structure
- **Blocked By:** None (can start immediately)
- **Parallel:** Can run alongside documentation updates

## Resource Requirements

- **Time Estimate:** 2-3 weeks (with validation)
  - H1: 4-5 days
  - H2: 3-4 days
  - H3: 2-3 days
  - H4: 3-4 days
  - H5: 3-4 days (includes buffer for issues)
- **Personnel:** 1 developer with repository knowledge
- **Tools:** Git, Python, pytest, grep/ripgrep for search

## Success Metrics

1. **Structure Clarity:** Single canonical location for each concern
2. **Import Compliance:** 100% adherence to section-based imports
3. **Test Coverage:** All tests pass post-migration
4. **Documentation:** All docs reflect new structure
5. **Developer Experience:** Clear, logical directory structure

## Completion Checklist

- [ ] All spec folders consolidated into `specifications/`
- [ ] Root-level `engine/` and `state/` resolved
- [ ] Legacy folders archived with documentation
- [ ] Infrastructure folders properly classified
- [ ] All imports updated and validated
- [ ] All tests passing
- [ ] All validators passing
- [ ] Build system updated
- [ ] CI/CD updated
- [ ] Documentation updated
- [ ] Sub-module registry created
- [ ] Final validation complete
- [ ] Phase H completion report written

## Post-Phase Activities

1. **Announcement:** Communicate structure changes to team
2. **Training:** Update onboarding docs with new structure
3. **Monitoring:** Watch for issues in first 2 weeks post-merge
4. **Optimization:** Identify any remaining redundancies for future phases

## Appendices

### Appendix A: Pre-Phase Checklist

- [ ] Create all backup branches
- [ ] Run full test suite to establish baseline
- [ ] Document current test pass rate
- [ ] Backup database files
- [ ] Create inventory of all folders to be modified
- [ ] Notify team of upcoming changes

### Appendix B: Communication Plan

- **Pre-Phase:** Email team with timeline and scope
- **During Phase:** Daily standups noting progress/blockers
- **Post-Phase:** Completion report and updated contribution guidelines

### Appendix C: Validation Commands Quick Reference

```bash
# Import validation
python scripts/check_deprecated_usage.py
python scripts/validate_error_imports.py
python scripts/auto_migrate_imports.py --dry-run

# Build & test
pwsh scripts/bootstrap.ps1
pwsh scripts/test.ps1
pytest -v

# Workstream validation
python scripts/validate_workstreams.py
python scripts/validate_workstreams_authoring.py

# Index generation
python scripts/generate_spec_index.py
python scripts/generate_spec_mapping.py

# Engine validation
python scripts/validate_engine.py
```

---

**Document Version History:**
- v1.0.0 (2025-11-21): Initial phase plan created based on directory analysis
