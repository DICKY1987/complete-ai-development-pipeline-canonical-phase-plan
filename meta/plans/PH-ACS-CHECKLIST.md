# PH-ACS Quick Reference Checklist

**Phase:** AI Codebase Structure Specification Implementation  
**Duration:** 4-5 days | **Effort:** 30-36 hours | **Cost:** $30-50  
**Full Plan:** `meta/plans/PH-ACS-AI-CODEBASE-STRUCTURE.md`

---

## Phase 1: Quick Wins (1 day) ⚡ HIGH PRIORITY

**Goal:** Create foundational artifacts (2-4 hours each)

### WS-ACS-01: Foundation Artifacts

- [ ] **ACS-01-01: CODEBASE_INDEX.yaml** (2-3h)
  - Extract from `DIRECTORY_GUIDE.md`
  - Add `depends_on` relationships
  - Define module layers (domain/api/infra)
  - Validate against schema

- [ ] **ACS-01-02: QUALITY_GATE.yaml** (1-2h)
  - Extract commands from `scripts/`
  - List: test, validate-workstreams, path-standards
  - Mark required vs optional
  - Test all commands execute

- [ ] **ACS-01-03: MODULE.md files** (2-3h)
  - Copy `core/README.md` template
  - Create for: `engine/`, `error/`, `aim/`, `pm/`, `specifications/`
  - Cross-reference CODEBASE_INDEX module IDs
  - 5 files total

- [ ] **ACS-01-04: .meta/AI_GUIDANCE.md** (1-2h)
  - Synthesize from `AGENTS.md`
  - Reference all ACS artifacts
  - Explain safe/unsafe zones
  - Human-readable summary

**Phase 1 Gate:**
- [ ] CODEBASE_INDEX validates, all modules present
- [ ] QUALITY_GATE commands all pass
- [ ] 5 MODULE.md files exist with cross-refs
- [ ] AI_GUIDANCE.md references all artifacts

---

## Phase 2: Infrastructure (2-3 days) 🔧 MEDIUM PRIORITY

**Goal:** Build AI context generation infrastructure

### WS-ACS-02: AI Context Generation

- [ ] **ACS-02-01: Directory structure** (15m)
  - Create `.meta/ai_context/`
  - Add `.gitkeep`

- [ ] **ACS-02-02: Repo summary generator** (4-6h)
  - Script: `scripts/generate_repo_summary.py`
  - Input: CODEBASE_INDEX, ARCHITECTURE, PROJECT_PROFILE
  - Output: `repo_summary.md` + `repo_summary.json`
  - Validate JSON schema

- [ ] **ACS-02-03: Code graph generator** (4-6h)
  - Script: `scripts/generate_code_graph.py`
  - Use AST to parse imports
  - Output: `code_graph.json`
  - Validate graph is acyclic

- [ ] **ACS-02-04: ai_policies.yaml** (3-4h)
  - Define safe: `core/**`, `engine/**`, `tests/**`
  - Define review: `schema/**`, `config/**`
  - Define read-only: `legacy/**`, `docs/adr/**`
  - Add invariants (DB migrations, section imports)

- [ ] **ACS-02-05: .aiignore** (30m)
  - Merge `.gitignore` + `.aiderignore`
  - Add AI-specific exclusions
  - Document in AI_GUIDANCE.md

- [ ] **ACS-02-06: Update .gitignore** (30m)
  - Decide: commit summaries or regenerate?
  - Add rules for `.meta/ai_context/`
  - Document decision

**Phase 2 Gate:**
- [ ] repo_summary.json validates
- [ ] code_graph.json matches actual imports
- [ ] ai_policies.yaml defines all zones
- [ ] Generator scripts documented
- [ ] .aiignore consolidates rules

---

## Phase 3: Refinement (1 day) 🎯 LOW PRIORITY

**Goal:** Cross-link, validate, and integrate with CI

### WS-ACS-03: Integration & Validation

- [ ] **ACS-03-01: Cross-link docs** (2-3h)
  - Add module ID refs to ARCHITECTURE.md
  - Add module ID refs to DIRECTORY_GUIDE.md
  - Add module ID refs to all MODULE.md
  - Validate all refs resolve

- [ ] **ACS-03-02: Conformance validator** (3-4h)
  - Script: `scripts/validate_acs_conformance.py`
  - Check: modules exist on disk
  - Check: ai_policies paths valid
  - Check: cross-references correct

- [ ] **ACS-03-03: CI checks** (1-2h)
  - Add to CI: ACS validation
  - Add to CI: artifact freshness
  - Add to CI: QUALITY_GATE commands
  - Test in PR

- [ ] **ACS-03-04: Update AGENTS.md** (1h)
  - Add ACS section
  - Reference artifacts
  - Explain usage

- [ ] **ACS-03-05: Update DOCUMENTATION_INDEX.md** (30m)
  - Add ACS artifact entries
  - Link to usage guide

- [ ] **ACS-03-06: Create usage guide** (1-2h)
  - Write `docs/ACS_USAGE_GUIDE.md`
  - How to use artifacts
  - When to regenerate
  - Examples

**Phase 3 Gate:**
- [ ] Validator passes on current state
- [ ] CI runs ACS checks
- [ ] AGENTS.md references ACS
- [ ] DOCUMENTATION_INDEX includes ACS
- [ ] Usage guide is clear

---

## Final Acceptance (All Phases Complete)

### Artifact Checklist (7 Required)
- [ ] ✅ ACS-A01: `CODEBASE_INDEX.yaml`
- [ ] ✅ ACS-A02: `README.md`, `ARCHITECTURE.md`, `MODULE.md` (layering)
- [ ] ✅ ACS-A03: `.aiignore` (ignore rules)
- [ ] ✅ ACS-A04: `.meta/ai_context/` (summaries, graph)
- [ ] ✅ ACS-A05: `QUALITY_GATE.yaml`
- [ ] ✅ ACS-A06: `docs/DOCUMENTATION_INDEX.md` (enhanced)
- [ ] ✅ ACS-A07: `ai_policies.yaml`

### Validation Checklist
- [ ] All YAML validates against schemas
- [ ] All cross-references resolve
- [ ] All generator scripts documented
- [ ] All tests pass (pytest + ACS validator)
- [ ] CI validation passes
- [ ] No broken links in docs

### Integration Checklist
- [ ] Phase K docs reference ACS artifacts
- [ ] AGENTS.md includes ACS usage section
- [ ] DOCUMENTATION_INDEX.md updated
- [ ] UET Framework can read artifacts
- [ ] AI tools (Copilot/Claude/Aider) tested

---

## Quick Start (Copy-Paste Commands)

```bash
# Phase 1: Create foundational artifacts
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# 1. Create CODEBASE_INDEX.yaml (manual from DIRECTORY_GUIDE.md)
# 2. Create QUALITY_GATE.yaml (extract from scripts/)
# 3. Copy core/README.md to engine/MODULE.md, etc.
# 4. Create .meta/AI_GUIDANCE.md

# Validate Phase 1
pytest -q  # Existing tests still pass

# Phase 2: Build generators
python scripts/generate_repo_summary.py
python scripts/generate_code_graph.py

# Create ai_policies.yaml (manual)

# Validate Phase 2
python scripts/validate_acs_conformance.py  # (once created)

# Phase 3: Integrate
# Update docs with cross-references
# Add CI checks
# Update AGENTS.md and DOCUMENTATION_INDEX.md

# Final validation
pytest -q
python scripts/validate_acs_conformance.py
```

---

## Success Metrics

**Completion Criteria:**
- ✅ 7/7 ACS artifacts exist
- ✅ 5 MODULE.md files created
- ✅ 3 generator scripts working
- ✅ CI validation passing
- ✅ 0 broken cross-references

**Value Delivered:**
- 🎯 AI tools discover module boundaries automatically
- 🎯 Edit policies prevent unsafe modifications
- 🎯 Pre-computed summaries reduce AI token costs
- 🎯 Documentation is human AND machine-readable

---

## Troubleshooting

**If CODEBASE_INDEX.yaml validation fails:**
- Check YAML syntax (use online validator)
- Ensure all paths exist on disk
- Verify `depends_on` references valid module IDs

**If code_graph.json is incorrect:**
- Review AST parser logic
- Fall back to manual module relationships
- Validate against actual import statements

**If CI validation fails:**
- Check artifact freshness (regenerate summaries)
- Ensure all commands in QUALITY_GATE.yaml pass
- Review validator script logs

---

**Full Documentation:** `meta/plans/PH-ACS-AI-CODEBASE-STRUCTURE.md`  
**Feasibility Analysis:** `docs/AI_CODEBASE_STRUCTURE_FEASIBILITY.md`  
**Source Spec:** `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`

**Status:** Ready for execution | **Version:** 1.0.0 | **Updated:** 2025-11-22
