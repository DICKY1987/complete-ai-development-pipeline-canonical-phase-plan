---
doc_id: DOC-GUIDE-AI-CODEBASE-STRUCTURE-FEASIBILITY-1188
---

# AI Codebase Structure Specification - Feasibility Analysis

**Analysis Date:** 2025-11-22  
**Repository:** Complete AI Development Pipeline – Canonical Phase Plan  
**Source Spec:** `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`  
**Status:** ✅ **HIGHLY FEASIBLE** with excellent foundation already in place

---

## Executive Summary

**Overall Feasibility:** 95% - The repository is exceptionally well-positioned to implement the AI Codebase Structure Specification with minimal disruption.

**Key Strengths:**
- ✅ Already has comprehensive documentation system (Phase K)
- ✅ Section-based organization matches ACS requirements
- ✅ Existing quality gates (pytest, CI path standards)
- ✅ Strong metadata foundation (PROJECT_PROFILE.yaml, schemas)
- ✅ Clear architecture documentation already present

**Implementation Effort:** LOW to MEDIUM
- Most requirements are ~70% complete
- Can incrementally adopt missing pieces
- No major architectural changes needed

---

## Requirement-by-Requirement Analysis

### ✅ ACS-A01: CODEBASE_INDEX.yaml (85% Complete)

**Status:** **EXCELLENT** - Strong foundation exists

**What Exists:**
- ✅ `PROJECT_PROFILE.yaml` - Contains project metadata
- ✅ `DIRECTORY_GUIDE.md` - Comprehensive module documentation
- ✅ `core/`, `engine/`, `error/`, `aim/`, `pm/`, `specifications/` - Clear section structure
- ✅ Section boundaries well-defined
- ✅ Module responsibilities documented

**What's Needed:**
- 🔶 Convert existing docs to YAML format with explicit dependencies
- 🔶 Add `depends_on` relationships for each module
- 🔶 Define layers (api/domain/infra/ui) explicitly

**Implementation Plan:**
1. Create `CODEBASE_INDEX.yaml` based on existing `DIRECTORY_GUIDE.md`
2. Extract module relationships from import patterns
3. Document layer architecture (already implicit in structure)

**Effort:** 2-4 hours - Mostly reformatting existing information

**Example (Based on Existing Structure):**
```yaml
project:
  name: "Complete AI Development Pipeline – Canonical Phase Plan"
  language: "python"
  description: "Phase-based AI development pipeline with section-based organization"

modules:
  - id: "mod-core-state"
    name: "Core State"
    path: "core/state/"
    layer: "domain"
    responsibility: "Database operations, state persistence, bundle management"
    depends_on: []
    public_entrypoints:
      - path: "core/state/db.py"
        description: "Database initialization"
      - path: "core/state/crud.py"
        description: "CRUD operations"
  
  - id: "mod-core-engine"
    name: "Core Engine"
    path: "core/engine/"
    layer: "domain"
    responsibility: "Orchestration, execution, and recovery logic"
    depends_on: ["mod-core-state"]
    
  - id: "mod-error-engine"
    name: "Error Detection Engine"
    path: "error/engine/"
    layer: "domain"
    responsibility: "Error detection and analysis system"
    depends_on: ["mod-core-state"]
```

---

### ✅ ACS-A02: ARCHITECTURE_LAYERING (90% Complete)

**Status:** **EXCELLENT** - Already exists and well-maintained

**What Exists:**
- ✅ `README.md` - Comprehensive root overview with quick start
- ✅ `docs/ARCHITECTURE.md` - Detailed architecture documentation
- ✅ `DIRECTORY_GUIDE.md` - Section-by-section navigation
- ✅ `core/README.md` - Module-level documentation exists
- ✅ Clear component descriptions and data flows

**What's Needed:**
- 🔶 Add MODULE.md to other major sections (engine/, error/, aim/, pm/)
- 🔶 Ensure each module doc references CODEBASE_INDEX.yaml module IDs

**Implementation Plan:**
1. Use `core/README.md` as template
2. Create MODULE.md for: `engine/`, `error/`, `aim/`, `pm/`, `specifications/`
3. Cross-reference module IDs in all docs

**Effort:** 2-3 hours - Copy/adapt existing template

**Note:** You're already ahead of the curve here!

---

### ✅ ACS-A03: AI_IGNORE_RULES (75% Complete)

**Status:** **GOOD** - Solid foundation, minor additions needed

**What Exists:**
- ✅ `.gitignore` - Comprehensive, well-organized (150 lines)
- ✅ `.aiderignore` - Aider-specific ignore rules
- ✅ Sections clearly labeled (Local Dev, Python, Node, Build Artifacts, Pipeline Runtime)
- ✅ Runtime artifacts properly excluded (.worktrees/, .ledger/, .tasks/, .runs/)

**What's Needed:**
- 🔶 Create unified `.toolignore` or `.aiignore` for all AI tools
- 🔶 Add explicit "AI context" comments explaining why certain paths are excluded

**Implementation Plan:**
1. Create `.aiignore` that imports `.gitignore` patterns
2. Add AI-specific exclusions (if any beyond .gitignore)
3. Document in `.meta/AI_GUIDANCE.md`

**Effort:** 30 minutes - Mostly documentation

**Current .gitignore Quality:** EXCELLENT - Already separates noise from signal clearly

---

### ⚠️ ACS-A04: AI_CONTEXT_ARTIFACTS (40% Complete)

**Status:** **NEEDS WORK** - Directory structure needed

**What Exists:**
- ✅ `docs/` - Comprehensive documentation
- ✅ `docs/DOCUMENTATION_INDEX.md` - Central doc hub
- ✅ `PROJECT_PROFILE.yaml` - Project metadata
- ⚠️ No dedicated `.meta/ai_context/` directory

**What's Needed:**
- 🔴 Create `.meta/ai_context/` directory
- 🔴 Generate `repo_summary.md` and `repo_summary.json`
- 🔶 Generate `code_graph.json` from CODEBASE_INDEX.yaml

**Implementation Plan:**
1. Create `.meta/ai_context/` directory structure
2. Write script to auto-generate summaries from existing docs
3. Extract code graph from module dependencies
4. Add to `.gitignore` or commit as build artifact (decision needed)

**Effort:** 4-6 hours - New infrastructure

**Recommendation:** Generate these as build artifacts in CI

---

### ✅ ACS-A05: QUALITY_GATE_CONFIG (80% Complete)

**Status:** **VERY GOOD** - Strong foundation, needs formalization

**What Exists:**
- ✅ `pytest.ini` - Test configuration
- ✅ `pyproject.toml` - Project metadata and tool config
- ✅ `scripts/test.ps1` - Test runner script
- ✅ `scripts/bootstrap.ps1` - Setup script
- ✅ CI path standards enforcement (documented in docs/CI_PATH_STANDARDS.md)
- ⚠️ No centralized QUALITY_GATE.yaml

**What's Needed:**
- 🔶 Create `QUALITY_GATE.yaml` formalizing existing commands
- 🔶 Document which commands are required vs optional

**Implementation Plan:**
1. Extract commands from scripts/ and document in YAML
2. Add to CI pipeline as canonical reference
3. Reference in AGENTS.md

**Effort:** 1-2 hours - Documentation of existing practice

**Example (Based on Existing Scripts):**
```yaml
# QUALITY_GATE.yaml
commands:
  test:
    description: "Run full test suite"
    run: "pytest -q"
    required: true
  
  validate-workstreams:
    description: "Validate workstream bundles"
    run: "python ./scripts/validate_workstreams.py"
    required: true
  
  validate-authoring:
    description: "Validate workstream authoring"
    run: "python ./scripts/validate_workstreams_authoring.py"
    required: true
  
  path-standards:
    description: "Check deprecated import paths"
    run: "python ./scripts/check_deprecated_paths.py"  # (if exists or add to CI)
    required: true

policy:
  fail_on:
    - test
    - validate-workstreams
    - path-standards
```

---

### ✅ ACS-A06: DOC_LAYOUT_INDEX (95% Complete)

**Status:** **EXCELLENT** - Already exists and well-structured!

**What Exists:**
- ✅ `docs/DOCUMENTATION_INDEX.md` - **Comprehensive doc index!**
- ✅ Stable categories: Architecture, ADRs, Guidelines, Reference, Execution
- ✅ Cross-links to code
- ✅ Use-case oriented navigation
- ✅ Clear sections for different audiences (developers, AI tools)

**What's Needed:**
- 🔶 Optionally convert to YAML format (`docs/index.yaml`)
- 🔶 Add module ID cross-references

**Implementation Plan:**
1. Create parallel `docs/index.yaml` (optional - Markdown is fine!)
2. Add module ID references where applicable
3. Keep existing DOCUMENTATION_INDEX.md as human-friendly version

**Effort:** 1 hour - Optional enhancement

**Note:** Your existing doc index is **better** than what most repos have!

---

### ⚠️ ACS-A07: AI_POLICIES (30% Complete)

**Status:** **NEEDS WORK** - New infrastructure required

**What Exists:**
- ✅ `AGENTS.md` - Strong coding conventions and guidelines
- ✅ Clear section boundaries in documentation
- ⚠️ No machine-readable edit policies
- ⚠️ No explicit safe/unsafe zone definitions

**What's Needed:**
- 🔴 Create `ai_policies.yaml` with edit zones
- 🔴 Create `.meta/AI_GUIDANCE.md` with human-readable summary
- 🔶 Define invariants (e.g., "DB schema changes require migrations")

**Implementation Plan:**
1. Analyze repository structure to define zones
2. Create `ai_policies.yaml` with safe/review/read-only paths
3. Document invariants based on existing architecture
4. Create `.meta/AI_GUIDANCE.md` referencing the YAML

**Effort:** 3-4 hours - New policy definition

**Example (Based on Repository Structure):**
```yaml
# ai_policies.yaml
zones:
  safe_to_modify:
    - "core/**/*.py"
    - "engine/**/*.py"
    - "error/plugins/**/*.py"
    - "tests/**"
    - "scripts/**"
  
  review_required:
    - "schema/**"
    - "config/**"
    - "core/state/db.py"
    - "core/state/db_sqlite.py"
  
  read_only:
    - "legacy/**"
    - "docs/adr/**"
    - "docs/DOCUMENTATION_INDEX.md"
    - ".worktrees/**"
    - ".ledger/**"

invariants:
  - id: "INV-DB-SCHEMA"
    description: "Database schema changes MUST be accompanied by migrations"
    affected_paths:
      - "core/state/db_sqlite.py"
      - "schema/**/*.sql"
  
  - id: "INV-SECTION-IMPORTS"
    description: "Must use section-based imports (enforced by CI)"
    affected_paths:
      - "core/**"
      - "error/**"
      - "aim/**"
  
  - id: "INV-PHASE-K-DOCS"
    description: "Phase K docs are canonical reference"
    affected_paths:
      - "docs/DOCUMENTATION_INDEX.md"
      - "docs/IMPLEMENTATION_LOCATIONS.md"
```

---

## Overall Implementation Roadmap

### Phase 1: Quick Wins (1 day)
**Priority:** HIGH  
**Dependencies:** None

1. ✅ Create `CODEBASE_INDEX.yaml` from existing `DIRECTORY_GUIDE.md`
2. ✅ Create `QUALITY_GATE.yaml` from existing scripts
3. ✅ Add MODULE.md to major sections using `core/README.md` template
4. ✅ Create `.meta/AI_GUIDANCE.md` summarizing repository guidelines

**Deliverables:**
- `CODEBASE_INDEX.yaml` ← ACS-A01
- `QUALITY_GATE.yaml` ← ACS-A05
- `engine/MODULE.md`, `error/MODULE.md`, `aim/MODULE.md`, `pm/MODULE.md`
- `.meta/AI_GUIDANCE.md`

---

### Phase 2: AI Context Infrastructure (2-3 days)
**Priority:** MEDIUM  
**Dependencies:** Phase 1 complete

1. Create `.meta/ai_context/` directory structure
2. Write generator script for `repo_summary.json`
3. Generate `code_graph.json` from CODEBASE_INDEX.yaml
4. Create `ai_policies.yaml` with edit zones and invariants
5. Update `.gitignore` with AI context artifact rules

**Deliverables:**
- `.meta/ai_context/repo_summary.md`
- `.meta/ai_context/repo_summary.json` ← ACS-A04
- `.meta/ai_context/code_graph.json`
- `ai_policies.yaml` ← ACS-A07
- `scripts/generate_ai_context.py` (automation script)

---

### Phase 3: Refinement & Validation (1 day)
**Priority:** LOW  
**Dependencies:** Phase 1 & 2 complete

1. Cross-link all docs with module IDs
2. Validate CODEBASE_INDEX against actual code structure
3. Add CI check for AI context freshness
4. Update AGENTS.md to reference new artifacts
5. Create validation script for ACS conformance

**Deliverables:**
- Updated cross-references in all docs
- `scripts/validate_acs_conformance.py`
- CI integration for ACS checks
- Updated `AGENTS.md` and `DOCUMENTATION_INDEX.md`

---

## Risks & Mitigation

### Risk 1: Maintenance Overhead
**Likelihood:** MEDIUM  
**Impact:** MEDIUM

**Mitigation:**
- Auto-generate `CODEBASE_INDEX.yaml` from code analysis where possible
- Use git hooks to regenerate AI context on commit
- Add CI checks to ensure artifacts stay in sync

### Risk 2: YAML Duplication with Existing Docs
**Likelihood:** HIGH  
**Impact:** LOW

**Current State:**
- `DIRECTORY_GUIDE.md` already documents modules
- `DOCUMENTATION_INDEX.md` already indexes docs
- Adding YAML creates parallel documentation

**Mitigation:**
- Treat YAML as "machine-readable source of truth"
- Auto-generate Markdown summaries from YAML
- Keep human docs as "views" of YAML data
- OR: Keep Markdown as primary, generate YAML from it

**Recommendation:** Since your Markdown docs are excellent, consider:
1. Markdown = human-maintained source of truth
2. YAML = auto-generated from Markdown for AI tools
3. Script: `generate_acs_artifacts.py` to create YAML from MD

### Risk 3: Developer Adoption
**Likelihood:** LOW  
**Impact:** MEDIUM

**Mitigation:**
- Phase in gradually (you already have most pieces!)
- Clear documentation of "why" (AI tool effectiveness)
- Minimal disruption to existing workflows

---

## Integration with Existing Systems

### Phase K Documentation Enhancement
**Status:** ✅ **PERFECT ALIGNMENT**

The AI Codebase Structure Spec **complements** Phase K:
- Phase K: Human-friendly docs, term maps, examples
- ACS: Machine-readable metadata, graph structure, edit policies

**Integration Points:**
- `CODEBASE_INDEX.yaml` references Phase K module docs
- `docs/index.yaml` builds on `DOCUMENTATION_INDEX.md`
- `ai_policies.yaml` codifies guidelines from `AGENTS.md`

### CI Path Standards
**Status:** ✅ **ALREADY ENFORCED**

Your existing CI path standards check is **exactly** what ACS recommends:
- ✅ Enforces section-based imports
- ✅ Blocks deprecated patterns
- ✅ Validates code structure

**Enhancement:** Add ACS conformance check to same pipeline

### UET Framework Integration
**Status:** ✅ **COMPATIBLE**

The UET Framework and ACS work together:
- UET: Project auto-detection, orchestration templates
- ACS: Codebase structure, AI context, edit policies

**No conflicts** - UET can read ACS artifacts!

---

## Recommendations

### Immediate Actions (Do First)
1. ✅ **Create `CODEBASE_INDEX.yaml`** - Foundation for everything else
2. ✅ **Create `QUALITY_GATE.yaml`** - Codify existing practice
3. ✅ **Create `.meta/AI_GUIDANCE.md`** - Human-readable summary
4. ✅ **Add MODULE.md files** - Quick wins using existing template

### Short-term (Next Sprint)
5. 🔶 **Create `ai_policies.yaml`** - Define edit zones and invariants
6. 🔶 **Build AI context generation** - Automate artifact creation
7. 🔶 **Add CI validation** - Ensure artifacts stay fresh

### Long-term (Optional Enhancements)
8. 🔵 **Auto-generate from code** - Parse imports to build dependency graph
9. 🔵 **LLM-friendly embeddings** - Pre-compute vector embeddings for RAG
10. 🔵 **Tool-specific profiles** - Copilot vs Claude vs Aider configs

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `CODEBASE_INDEX.yaml` exists with all modules documented
- [ ] `QUALITY_GATE.yaml` formalizes test/lint/validate commands
- [ ] All major sections have MODULE.md files
- [ ] `.meta/AI_GUIDANCE.md` provides human-readable overview

### Phase 2 Complete When:
- [ ] `.meta/ai_context/` directory exists with summaries
- [ ] `ai_policies.yaml` defines safe/review/read-only zones
- [ ] Generator script automates artifact creation
- [ ] CI can validate ACS conformance

### Phase 3 Complete When:
- [ ] All docs cross-reference module IDs
- [ ] CI enforces artifact freshness
- [ ] AGENTS.md updated to reference ACS artifacts
- [ ] External AI tools (Copilot, Claude) can consume artifacts

---

## Conclusion

**Verdict: ✅ HIGHLY FEASIBLE - STRONGLY RECOMMENDED**

Your repository is in an **exceptional** position to adopt the AI Codebase Structure Specification:

1. **You already have ~70% of the requirements** - Most work is formalizing existing practices
2. **Strong Phase K foundation** - Documentation is far ahead of typical repos
3. **Clear architecture** - Section-based organization maps perfectly to ACS modules
4. **Active CI enforcement** - Path standards check proves you value machine-readable rules
5. **Low risk** - Incremental adoption, no breaking changes required

**Biggest Value-Adds:**
- 🎯 `CODEBASE_INDEX.yaml` - Makes module relationships explicit for AI tools
- 🎯 `ai_policies.yaml` - Prevents AI agents from modifying sensitive areas
- 🎯 `.meta/ai_context/` - Pre-computed summaries reduce AI context costs

**Estimated Total Effort:** 3-5 days spread over 2-3 sprints

**ROI:** HIGH - Dramatically improves AI tool effectiveness with minimal disruption

---

## Next Steps

1. **Review this analysis** with team/maintainers
2. **Prioritize Phase 1** quick wins (1 day effort)
3. **Create tracking issue** for ACS implementation
4. **Start with CODEBASE_INDEX.yaml** - Foundation for everything else

**Questions? Issues?**
- See source spec: `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`
- Reference this analysis: `docs/AI_CODEBASE_STRUCTURE_FEASIBILITY.md`
- Open discussion in project planning channels

---

**END OF FEASIBILITY ANALYSIS**
