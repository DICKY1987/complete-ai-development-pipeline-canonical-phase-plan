# PH-ACS — AI Codebase Structure Specification Implementation

**Phase ID:** `PH-ACS`  
**Category:** `infrastructure`  
**Created:** 2025-11-22  
**Status:** Ready for Execution  
**Source Spec:** `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`  
**Feasibility Analysis:** `docs/AI_CODEBASE_STRUCTURE_FEASIBILITY.md`

---

## Phase Overview

Implement the AI Codebase Structure Specification (ACS) to enhance AI tool effectiveness by providing machine-readable metadata, explicit module boundaries, and clear edit policies.

### Objectives

1. **Formalize existing documentation** into machine-readable formats (YAML)
2. **Create AI context artifacts** for improved RAG and tool performance
3. **Define edit policies** to guide autonomous AI agents safely
4. **Automate artifact generation** to reduce maintenance overhead
5. **Integrate with existing systems** (Phase K, UET, CI path standards)

### Outcomes

- 7 core artifacts (ACS-A01 through ACS-A07) in place
- AI tools can discover module boundaries, dependencies, and edit zones
- Automated generation scripts reduce manual maintenance
- CI validates artifact freshness and conformance
- Phase K documentation enhanced with machine-readable layer

---

## Estimated Effort & Resources

| Phase | Duration | Effort | Priority | Dependencies |
|-------|----------|--------|----------|--------------|
| Phase 1 (Quick Wins) | 1 day | 8 hours | HIGH | None |
| Phase 2 (Infrastructure) | 2-3 days | 16-20 hours | MEDIUM | Phase 1 |
| Phase 3 (Refinement) | 1 day | 6-8 hours | LOW | Phase 1, 2 |
| **Total** | **4-5 days** | **30-36 hours** | - | - |

**Cost Estimate:** $30-50 USD (AI tool usage for generation scripts)

---

## Phase Breakdown

### Phase 1: Quick Wins (1 day) — HIGH PRIORITY

**Goal:** Create foundational artifacts by formalizing existing documentation.

**Deliverables:**
- ✅ `CODEBASE_INDEX.yaml` (ACS-A01)
- ✅ `QUALITY_GATE.yaml` (ACS-A05)
- ✅ `MODULE.md` files for major sections
- ✅ `.meta/AI_GUIDANCE.md`

#### Workstream WS-ACS-01: Foundation Artifacts

**Steps:**

1. **ACS-01-01: Create CODEBASE_INDEX.yaml**
   - **Input:** `DIRECTORY_GUIDE.md`, existing section structure
   - **Tool:** Manual creation with validation script
   - **Output:** `CODEBASE_INDEX.yaml` at repository root
   - **Validation:** Schema validation, all modules referenced
   - **Time:** 2-3 hours

2. **ACS-01-02: Create QUALITY_GATE.yaml**
   - **Input:** `scripts/`, `pytest.ini`, existing CI
   - **Tool:** Extract and formalize existing commands
   - **Output:** `QUALITY_GATE.yaml` at repository root
   - **Validation:** All commands executable
   - **Time:** 1-2 hours

3. **ACS-01-03: Add MODULE.md to sections**
   - **Input:** `core/README.md` as template
   - **Tool:** Copy/adapt for `engine/`, `error/`, `aim/`, `pm/`, `specifications/`
   - **Output:** `MODULE.md` in each major section
   - **Validation:** Cross-references to CODEBASE_INDEX module IDs
   - **Time:** 2-3 hours

4. **ACS-01-04: Create .meta/AI_GUIDANCE.md**
   - **Input:** `AGENTS.md`, `CODEBASE_INDEX.yaml`, architecture docs
   - **Tool:** Manual synthesis
   - **Output:** `.meta/AI_GUIDANCE.md`
   - **Validation:** Human readability check
   - **Time:** 1-2 hours

**Acceptance Criteria:**
- [ ] `CODEBASE_INDEX.yaml` validates against schema
- [ ] All modules in DIRECTORY_GUIDE.md are represented
- [ ] `QUALITY_GATE.yaml` commands all execute successfully
- [ ] 5 MODULE.md files created (engine, error, aim, pm, specifications)
- [ ] `.meta/AI_GUIDANCE.md` exists and references all artifacts

---

### Phase 2: AI Context Infrastructure (2-3 days) — MEDIUM PRIORITY

**Goal:** Build automated generation infrastructure for AI context artifacts.

**Deliverables:**
- ✅ `.meta/ai_context/` directory with summaries
- ✅ `ai_policies.yaml` (ACS-A07)
- ✅ Generator scripts for automation
- ✅ `.aiignore` unified ignore file

#### Workstream WS-ACS-02: AI Context Generation

**Steps:**

1. **ACS-02-01: Create .meta/ai_context/ structure**
   - **Tool:** Directory creation + .gitkeep
   - **Output:** `.meta/ai_context/` directory
   - **Time:** 15 minutes

2. **ACS-02-02: Build repo summary generator**
   - **Input:** `CODEBASE_INDEX.yaml`, `docs/ARCHITECTURE.md`, `PROJECT_PROFILE.yaml`
   - **Tool:** Python script `scripts/generate_repo_summary.py`
   - **Output:** 
     - `.meta/ai_context/repo_summary.md`
     - `.meta/ai_context/repo_summary.json`
   - **Validation:** JSON schema validation
   - **Time:** 4-6 hours

3. **ACS-02-03: Build code graph generator**
   - **Input:** `CODEBASE_INDEX.yaml`, actual import analysis
   - **Tool:** Python script using AST parsing
   - **Output:** `.meta/ai_context/code_graph.json`
   - **Validation:** Graph is acyclic, all modules present
   - **Time:** 4-6 hours

4. **ACS-02-04: Create ai_policies.yaml**
   - **Input:** Repository structure analysis, AGENTS.md
   - **Tool:** Manual creation with zone analysis
   - **Output:** `ai_policies.yaml` at root
   - **Validation:** All paths valid, no conflicting rules
   - **Time:** 3-4 hours

5. **ACS-02-05: Create unified .aiignore**
   - **Input:** `.gitignore`, `.aiderignore`
   - **Tool:** Merge and document
   - **Output:** `.aiignore` at root
   - **Validation:** No conflicts with .gitignore
   - **Time:** 30 minutes

6. **ACS-02-06: Update .gitignore for AI artifacts**
   - **Tool:** Add rules for generated artifacts
   - **Output:** Updated `.gitignore`
   - **Decision:** Commit summaries or regenerate in CI?
   - **Time:** 30 minutes

**Acceptance Criteria:**
- [ ] `.meta/ai_context/repo_summary.json` validates against schema
- [ ] `code_graph.json` contains all modules with correct dependencies
- [ ] `ai_policies.yaml` defines safe/review/read-only zones
- [ ] Generator scripts are documented and executable
- [ ] `.aiignore` consolidates all AI tool ignore rules

---

### Phase 3: Refinement & Validation (1 day) — LOW PRIORITY

**Goal:** Cross-link artifacts, add CI validation, and update documentation.

**Deliverables:**
- ✅ Cross-linked documentation with module IDs
- ✅ CI checks for ACS conformance
- ✅ Updated AGENTS.md and DOCUMENTATION_INDEX.md
- ✅ Validation script

#### Workstream WS-ACS-03: Integration & Validation

**Steps:**

1. **ACS-03-01: Cross-link docs with module IDs**
   - **Input:** All MODULE.md files, ARCHITECTURE.md, DIRECTORY_GUIDE.md
   - **Tool:** Manual editing + search/replace
   - **Output:** Updated docs with `(mod-core-state)` references
   - **Validation:** All references resolve to CODEBASE_INDEX
   - **Time:** 2-3 hours

2. **ACS-03-02: Create ACS conformance validator**
   - **Tool:** Python script `scripts/validate_acs_conformance.py`
   - **Checks:**
     - All modules in CODEBASE_INDEX exist on disk
     - All paths in ai_policies.yaml are valid
     - MODULE.md cross-references are correct
     - Code graph matches actual imports
   - **Output:** Validation script + report
   - **Time:** 3-4 hours

3. **ACS-03-03: Add CI checks**
   - **Tool:** Update CI workflow (if exists) or create new
   - **Checks:**
     - ACS conformance validation
     - Artifact freshness (repo_summary.json not stale)
     - QUALITY_GATE commands still pass
   - **Output:** `.github/workflows/acs-validation.yml` or similar
   - **Time:** 1-2 hours

4. **ACS-03-04: Update AGENTS.md**
   - **Input:** All new artifacts
   - **Tool:** Add section on ACS artifacts and usage
   - **Output:** Updated AGENTS.md
   - **Time:** 1 hour

5. **ACS-03-05: Update DOCUMENTATION_INDEX.md**
   - **Input:** New artifact locations
   - **Tool:** Add entries for ACS artifacts
   - **Output:** Updated DOCUMENTATION_INDEX.md
   - **Time:** 30 minutes

6. **ACS-03-06: Create ACS usage guide**
   - **Tool:** Write `docs/ACS_USAGE_GUIDE.md`
   - **Content:** How to use artifacts, when to regenerate
   - **Output:** Usage documentation
   - **Time:** 1-2 hours

**Acceptance Criteria:**
- [ ] Validator script passes on current repository state
- [ ] CI runs ACS checks on every PR
- [ ] AGENTS.md references ACS artifacts
- [ ] DOCUMENTATION_INDEX.md includes all ACS docs
- [ ] Usage guide is clear and actionable

---

## Phase Dependencies & Execution Order

```
Phase 1 (Quick Wins)
  ├─ WS-ACS-01 (Foundation Artifacts)
  │    ├─ ACS-01-01: CODEBASE_INDEX.yaml
  │    ├─ ACS-01-02: QUALITY_GATE.yaml
  │    ├─ ACS-01-03: MODULE.md files
  │    └─ ACS-01-04: AI_GUIDANCE.md
  │
  └─ [GATE: Phase 1 Validation]

Phase 2 (Infrastructure)
  ├─ WS-ACS-02 (AI Context Generation)
  │    ├─ ACS-02-01: Create directory
  │    ├─ ACS-02-02: Repo summary generator
  │    ├─ ACS-02-03: Code graph generator
  │    ├─ ACS-02-04: ai_policies.yaml
  │    ├─ ACS-02-05: .aiignore
  │    └─ ACS-02-06: Update .gitignore
  │
  └─ [GATE: Phase 2 Validation]

Phase 3 (Refinement)
  ├─ WS-ACS-03 (Integration & Validation)
  │    ├─ ACS-03-01: Cross-link docs
  │    ├─ ACS-03-02: Conformance validator
  │    ├─ ACS-03-03: CI checks
  │    ├─ ACS-03-04: Update AGENTS.md
  │    ├─ ACS-03-05: Update DOCUMENTATION_INDEX.md
  │    └─ ACS-03-06: Usage guide
  │
  └─ [GATE: Final Validation]
```

**Critical Path:** Phase 1 → Phase 2 (repo summary depends on CODEBASE_INDEX) → Phase 3

**Parallel Opportunities:**
- Within Phase 1: QUALITY_GATE.yaml can be done in parallel with MODULE.md creation
- Within Phase 2: ai_policies.yaml and .aiignore can be done in parallel with generators

---

## Files Scope

### Read Permissions
```yaml
read:
  - "**/*.md"                          # All documentation
  - "**/*.yaml"                        # All YAML configs
  - "core/**/*.py"                     # Code for import analysis
  - "engine/**/*.py"
  - "error/**/*.py"
  - "aim/**/*.py"
  - "pm/**/*.py"
  - "specifications/**/*.py"
  - "scripts/**"                       # Existing scripts
  - "tests/**"                         # Test structure
  - ".gitignore"
  - ".aiderignore"
  - "pytest.ini"
  - "pyproject.toml"
```

### Write Permissions
```yaml
write:
  - "CODEBASE_INDEX.yaml"              # New artifact (ACS-A01)
  - "QUALITY_GATE.yaml"                # New artifact (ACS-A05)
  - "ai_policies.yaml"                 # New artifact (ACS-A07)
  - ".aiignore"                        # New ignore file (ACS-A03)
  - ".gitignore"                       # Update for AI artifacts
  - "engine/MODULE.md"                 # New module doc
  - "error/MODULE.md"                  # New module doc
  - "aim/MODULE.md"                    # New module doc
  - "pm/MODULE.md"                     # New module doc
  - "specifications/MODULE.md"         # New module doc
  - ".meta/AI_GUIDANCE.md"             # New guidance doc
  - ".meta/ai_context/**"              # New context directory (ACS-A04)
  - "scripts/generate_repo_summary.py" # New generator script
  - "scripts/generate_code_graph.py"   # New generator script
  - "scripts/validate_acs_conformance.py" # New validator
  - "docs/ACS_USAGE_GUIDE.md"          # New usage guide
  - "docs/ARCHITECTURE.md"             # Cross-linking updates
  - "docs/DIRECTORY_GUIDE.md"          # Cross-linking updates
  - "AGENTS.md"                        # ACS section
  - "docs/DOCUMENTATION_INDEX.md"      # Add ACS entries

create:
  - ".meta/ai_context/"                # New directory structure
  - ".github/workflows/acs-validation.yml" # CI workflow (optional)
```

### Forbidden (Read-Only)
```yaml
forbidden:
  - "legacy/**"                        # Never modify archived code
  - ".worktrees/**"                    # Runtime artifacts
  - ".ledger/**"
  - ".tasks/**"
  - ".runs/**"
  - "**/__pycache__/**"
  - "**/*.pyc"
```

---

## Constraints

### Patch Requirements
```yaml
patch:
  patch_required: true                 # All changes via patches
  allowed_formats: ["unified_diff"]
  max_lines_changed: 300               # Per file, per patch
  max_files_changed: 8                 # Per patch
  forbid_binary_patches: true
```

### Testing Requirements
```yaml
tests:
  tests_must_pass: true
  test_command: "pytest -q"
  extra_test_commands:
    - "python scripts/validate_acs_conformance.py"  # (once created)
  skip_allowed: false
```

### Behavior Rules
```yaml
behavior:
  ascii_only: false                    # UTF-8 YAML is fine
  forbid_direct_file_writes: true      # Patches only
  require_doc_update: true             # Update DOCUMENTATION_INDEX
  max_attempts_per_step: 3
```

---

## Acceptance Criteria

### Phase 1 Complete When:
- [ ] `CODEBASE_INDEX.yaml` exists with all modules from DIRECTORY_GUIDE.md
- [ ] `QUALITY_GATE.yaml` lists all test/validation commands
- [ ] 5 MODULE.md files created and cross-reference CODEBASE_INDEX
- [ ] `.meta/AI_GUIDANCE.md` summarizes all ACS artifacts
- [ ] All artifacts validate against schemas (if schemas exist)

### Phase 2 Complete When:
- [ ] `.meta/ai_context/repo_summary.json` generated and valid
- [ ] `.meta/ai_context/code_graph.json` matches actual imports
- [ ] `ai_policies.yaml` defines safe/review/read-only zones
- [ ] Generator scripts documented and runnable
- [ ] `.aiignore` consolidates AI tool ignore patterns

### Phase 3 Complete When:
- [ ] All docs cross-reference module IDs from CODEBASE_INDEX
- [ ] `scripts/validate_acs_conformance.py` passes
- [ ] CI runs ACS validation on every commit/PR
- [ ] AGENTS.md updated with ACS section
- [ ] DOCUMENTATION_INDEX.md includes ACS artifacts
- [ ] `docs/ACS_USAGE_GUIDE.md` written and reviewed

### Final Gate (All Phases)
- [ ] ACS-A01 through ACS-A07 artifacts exist
- [ ] Feasibility analysis checkboxes all ✅
- [ ] AI tools (Copilot, Claude, Aider) can consume artifacts
- [ ] No broken links or references in documentation
- [ ] All tests pass (pytest + validation scripts)

---

## Risks & Mitigations

### Risk 1: YAML Duplication with Existing Docs
**Likelihood:** HIGH  
**Impact:** LOW (maintenance overhead)

**Mitigation:**
- Treat Markdown as source of truth, auto-generate YAML from it
- Use generator scripts to keep artifacts in sync
- Add CI check to detect drift

### Risk 2: Import Analysis Complexity
**Likelihood:** MEDIUM  
**Impact:** MEDIUM (code_graph.json accuracy)

**Mitigation:**
- Start with simple AST-based analysis
- Use existing section boundaries as fallback
- Validate against manual review of key modules

### Risk 3: Maintenance Overhead
**Likelihood:** MEDIUM  
**Impact:** MEDIUM (stale artifacts)

**Mitigation:**
- Automate regeneration in CI
- Git hooks to regenerate on commit (optional)
- Clear documentation on when to regenerate

### Risk 4: Developer Adoption
**Likelihood:** LOW  
**Impact:** MEDIUM (unused artifacts)

**Mitigation:**
- Gradual rollout (Phase 1 first)
- Clear documentation in AGENTS.md
- Demonstrate value with AI tool effectiveness

---

## Integration with Existing Systems

### Phase K Documentation Enhancement
**Status:** ✅ PERFECT ALIGNMENT

The ACS complements Phase K:
- Phase K: Human-friendly docs, term maps, examples
- ACS: Machine-readable metadata, graph structure

**Integration Points:**
- `CODEBASE_INDEX.yaml` references Phase K module docs
- `docs/index.yaml` (optional) builds on `DOCUMENTATION_INDEX.md`
- `ai_policies.yaml` codifies `AGENTS.md` guidelines

### CI Path Standards
**Status:** ✅ ALREADY ENFORCED

Existing CI enforces section-based imports. Add ACS validation:
- Check CODEBASE_INDEX matches actual code structure
- Validate artifact freshness
- Ensure MODULE.md cross-references are valid

### UET Framework Integration
**Status:** ✅ COMPATIBLE

UET can orchestrate ACS implementation:
- Use this phase plan as UET workstream bundle
- UET reads PROJECT_PROFILE.yaml (already exists)
- ACS artifacts enhance UET's project understanding

---

## Execution Using UET Framework

### Option 1: Manual Execution
Follow the phase plan step-by-step, executing each workstream in order.

### Option 2: UET Orchestrated Execution

**Step 1:** Convert this phase plan to UET workstream bundle:
```bash
python scripts/convert_phase_to_workstream.py \
  meta/plans/PH-ACS-AI-CODEBASE-STRUCTURE.md \
  --output workstreams/phase-acs-bundle.json
```

**Step 2:** Execute via UET orchestrator:
```bash
python scripts/run_workstream.py workstreams/phase-acs-bundle.json
```

**Step 3:** Monitor progress:
```bash
# Real-time monitoring
python -m engine.orchestrator status --bundle phase-acs-bundle

# View logs
tail -f .runs/phase-acs-*/execution.log
```

---

## Success Metrics

### Quantitative
- **7/7 ACS artifacts created** (A01-A07)
- **5 MODULE.md files** (engine, error, aim, pm, specifications)
- **3 generator scripts** (repo_summary, code_graph, validator)
- **100% CI validation pass rate**
- **0 broken cross-references** in documentation

### Qualitative
- AI tools can discover module boundaries without human guidance
- Edit policies prevent autonomous agents from modifying restricted areas
- Documentation is both human-readable AND machine-parseable
- Maintenance overhead is low (automated generation)

### Value Delivered
- **Improved AI Tool Effectiveness:** Context-aware code suggestions
- **Reduced AI Token Costs:** Pre-computed summaries reduce context size
- **Safer Autonomous Agents:** Clear boundaries prevent destructive edits
- **Better Onboarding:** New developers/AI tools understand structure faster

---

## Next Steps After Phase Complete

1. **Integrate with AI Tools:**
   - Configure Copilot to read `ai_policies.yaml`
   - Update Claude Code config to reference CODEBASE_INDEX
   - Test Aider with .aiignore patterns

2. **Extend ACS:**
   - Add tool-specific profiles (Copilot vs Claude vs Aider)
   - Generate embeddings for RAG systems
   - Create module-specific quality gates

3. **Monitor Impact:**
   - Track AI tool suggestion accuracy
   - Measure reduction in token usage
   - Monitor developer feedback on documentation clarity

---

## References

- **Source Spec:** `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`
- **Feasibility Analysis:** `docs/AI_CODEBASE_STRUCTURE_FEASIBILITY.md`
- **UET Framework:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
- **Phase K Plans:** `meta/plans/phase-K-plus-*.md`
- **Existing Architecture:** `docs/ARCHITECTURE.md`
- **Module Guide:** `DIRECTORY_GUIDE.md`

---

**Phase Owner:** System Architecture Team  
**Stakeholders:** AI Tool Users, Documentation Maintainers, CI/CD Team  
**Phase Version:** 1.0.0  
**Last Updated:** 2025-11-22

---

**END OF PHASE PLAN**
