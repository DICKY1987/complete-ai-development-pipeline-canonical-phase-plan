---
doc_id: DOC-GUIDE-OPTIMIZATION-PLAN-1657
---

# UET Framework - AI Optimization Plan

## Executive Summary

This document outlines what needs to be done to optimize the Universal Execution Templates Framework folder for AI assistance (Claude Code, GitHub Copilot, etc.).

**Current Status**: 60% optimized
**Priority**: High (improves AI onboarding from ~25min to ~2min per session)

---

## Missing ACS Artifacts

### 1. CODEBASE_INDEX.yaml (Critical - Missing)

**Purpose**: Provides AI with structured understanding of module architecture, dependencies, and layering.

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/CODEBASE_INDEX.yaml`

**Should Include**:
- All modules under `core/`, `profiles/`, `schema/`, `specs/`
- Module purposes, exports, dependencies
- Layer classification (infra/domain/api/ui)
- Import path standards

**Impact**: Without this, AI must re-discover structure each session.

**Estimated Effort**: 30-45 minutes to create comprehensive index

---

### 2. ai_policies.yaml (Critical - Missing)

**Purpose**: Defines edit zones (safe/review/read-only), forbidden patterns, and invariants.

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ai_policies.yaml`

**Should Include**:

#### Edit Zones
- **Safe to modify**: `core/**/*.py`, `tests/**/*.py`, `scripts/**/*.py`, `docs/**/*.md`
- **Review required**: `schema/**/*.json`, `profiles/**/*.yaml`, `specs/UET_*.md`
- **Read-only**: `master_plan/**/*`, `PATCH_PLAN_JSON/**/*`, `.pytest_cache/**/*`, `.worktrees/**/*`, `htmlcov/**/*`

#### Forbidden Patterns
- `from src.pipeline.*` (deprecated)
- Direct DB updates without migration scripts
- Modifying schemas without version bump

#### Invariants
- Schema validation required for all artifacts
- 196/196 tests must pass before commits
- Module dependency graph must be acyclic
- ULID format for IDs (26-char uppercase hex)

**Impact**: Prevents AI from accidentally editing historical/generated files.

**Estimated Effort**: 20-30 minutes

---

### 3. QUALITY_GATE.yaml (Critical - Missing)

**Purpose**: Defines validation commands AI should run before considering task complete.

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/QUALITY_GATE.yaml`

**Should Include**:

```yaml
gates:
  unit_tests:
    command: "pytest tests/ -v"
    required: true
    timeout: 300
    description: "All 196 tests must pass"

  schema_tests:
    command: "pytest tests/schema/ -v"
    required: true
    timeout: 60
    description: "Schema validation tests"

  bootstrap_tests:
    command: "pytest tests/bootstrap/ -v"
    required: true
    timeout: 120
    description: "Bootstrap system tests"

  engine_tests:
    command: "pytest tests/engine/ -v"
    required: true
    timeout: 180
    description: "Orchestration engine tests"

  resilience_tests:
    command: "pytest tests/resilience/ -v"
    required: true
    timeout: 120
    description: "Circuit breaker and retry tests"

  # Future gates (when scripts exist)
  # module_structure:
  #   command: "python scripts/validate_module_structure.py"
  #   required: false
  #   timeout: 30
```

**Impact**: AI will know exactly what validation to run.

**Estimated Effort**: 15-20 minutes

---

### 4. PROJECT_PROFILE.yaml (Optional - Framework Generates These)

**Status**: Not needed for this repository - UET is a *framework* that generates PROJECT_PROFILE.yaml for *target projects*.

**Reasoning**: This folder contains the orchestration engine itself, not a project being orchestrated.

---

## Enhancements to Existing Files

### 5. Update CLAUDE.md (Medium Priority)

**Current**: Comprehensive framework-specific instructions
**Missing**: Global principles from `.claude/CLAUDE.md`

**Action**: Add Section 0.1 with global principles (minimal changes, test awareness, git discipline) - similar to what was done for parent folder.

**Estimated Effort**: 5 minutes (patch existing file)

---

### 6. Create .github/copilot-instructions.md (Low Priority)

**Purpose**: Provide GitHub Copilot with UET-specific guidance.

**Should Include**:
- Simplified version of CLAUDE.md
- Focus on code completion scenarios (not full agent workflows)
- Import path standards
- Schema validation requirements
- Test patterns

**Estimated Effort**: 20 minutes (adapt from CLAUDE.md)

---

### 7. Validation Scripts (Medium Priority)

**Currently Missing Scripts**:
- `scripts/validate_module_structure.py` - Check CODEBASE_INDEX conformance
- `scripts/validate_acs_conformance.py` - Check ai_policies.yaml compliance
- `scripts/generate_codebase_index.py` - Auto-generate/update CODEBASE_INDEX

**Impact**: Enables automated checking of structure compliance.

**Estimated Effort**: 1-2 hours for all three scripts

---

## Implementation Priority

### Phase 1: Critical ACS Artifacts (1-2 hours)
1. ✅ Create `ai_policies.yaml` - Edit zones, forbidden patterns, invariants
2. ✅ Create `CODEBASE_INDEX.yaml` - Module structure and dependencies
3. ✅ Create `QUALITY_GATE.yaml` - Validation commands

### Phase 2: Documentation Enhancement (30 minutes)
4. ✅ Update `CLAUDE.md` - Add global principles section
5. ⚠️ Create `.github/copilot-instructions.md` - Copilot-specific guidance (optional)

### Phase 3: Automation (2-3 hours)
6. ⚠️ Create validation scripts
7. ⚠️ Add pre-commit hooks (optional)
8. ⚠️ Update CI/CD to enforce gates

---

## Benefits After Optimization

### Before Optimization:
- AI spends 20-25 minutes per session discovering structure
- Risk of editing historical/generated files
- No clear validation checklist
- Import path mistakes common

### After Optimization:
- AI onboarding: ~2 minutes (read `.meta/AI_GUIDANCE.md` + quick ref to policies)
- Edit zone violations prevented upfront
- Clear quality gates for task completion
- Import path standards enforced

### Quantified Impact:
- **Time savings**: ~23 minutes per AI session
- **Error reduction**: ~80% fewer scope violations
- **Quality improvement**: Consistent validation before commits

---

## Quick Start Implementation

### Option 1: Manual Creation (Recommended for Control)
```bash
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

# Create ACS artifacts
touch CODEBASE_INDEX.yaml
touch ai_policies.yaml
touch QUALITY_GATE.yaml

# Edit each file according to templates in this document
```

### Option 2: AI-Assisted Generation (Faster)
```bash
# Ask Claude Code to:
# 1. Generate CODEBASE_INDEX.yaml from directory structure
# 2. Generate ai_policies.yaml based on CLAUDE.md
# 3. Generate QUALITY_GATE.yaml from test commands in README
# 4. Update CLAUDE.md with global principles
```

---

## Validation Checklist

After creating artifacts, verify:

- [ ] `CODEBASE_INDEX.yaml` exists and validates
- [ ] `ai_policies.yaml` exists with all 3 sections (edit_zones, forbidden_patterns, invariants)
- [ ] `QUALITY_GATE.yaml` exists with test gates
- [ ] `CLAUDE.md` includes global principles section
- [ ] `.meta/AI_GUIDANCE.md` references new artifacts
- [ ] All paths in artifacts use correct format (forward slashes, globs)

---

## Maintenance Notes

**Update triggers** for CODEBASE_INDEX.yaml:
- New module added to `core/`, `profiles/`, etc.
- Module dependencies changed
- Major refactoring completed

**Update triggers** for ai_policies.yaml:
- New directories become read-only (e.g., archived phases)
- New forbidden patterns discovered
- Invariants change

**Update triggers** for QUALITY_GATE.yaml:
- New test suites added
- New validation scripts created
- CI/CD requirements change

---

## Next Steps

1. **Decision**: Manual creation vs AI-assisted generation?
2. **Phase 1**: Create critical ACS artifacts (1-2 hours)
3. **Validation**: Run quality gates to ensure correctness
4. **Phase 2**: Documentation enhancements (30 min)
5. **Phase 3**: Automation scripts (optional, 2-3 hours)

**Estimated Total Time**: 2-5 hours (depending on automation scope)
**ROI**: Saves 23 minutes per AI session × sessions per week × team size

---

**Document Version**: 1.0
**Created**: 2025-11-23
**Author**: AI Optimization Analysis
