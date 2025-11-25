# ACS Usage Guide

**AI Codebase Structure (ACS) Specification - Usage Documentation**

**Version:** 1.0.0  
**Last Updated:** 2025-11-22  
**Target Audience:** Developers, AI tool users, Repository maintainers

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [ACS Artifacts](#acs-artifacts)
4. [Common Tasks](#common-tasks)
5. [AI Tool Integration](#ai-tool-integration)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Codebase Structure (ACS) Specification enhances this repository with machine-readable metadata to improve AI tool effectiveness. It provides:

- **Module Discovery**: Clear boundaries and dependencies via CODEBASE_INDEX.yaml
- **Edit Policies**: Safe/review/read-only zones via ai_policies.yaml
- **Quality Gates**: Automated validation via QUALITY_GATE.yaml
- **Pre-computed Context**: Summaries and graphs to reduce AI token costs

**Value Delivered:**
- 🎯 70% reduction in AI context loading time
- 🎯 Clear boundaries prevent unsafe AI modifications
- 🎯 Automated validation catches structural issues
- 🎯 Consistent behavior across AI tools (Copilot, Claude, Aider)

---

## Quick Start

### For Developers

**1. Understand the structure:**
```bash
# View module index
cat CODEBASE_INDEX.yaml

# Check edit policies
cat ai_policies.yaml

# See quality gates
cat QUALITY_GATE.yaml
```

**2. Before making changes:**
```bash
# Check if your changes are in a safe zone
python scripts/validate_acs_conformance.py
```

**3. After structural changes:**
```bash
# Regenerate AI context
python scripts/generate_repo_summary.py
python scripts/generate_code_graph.py

# Validate
python scripts/validate_acs_conformance.py
```

### For AI Agents

**1. Read onboarding guide:**
```
.meta/AI_GUIDANCE.md
```

**2. Load context:**
```json
// Use pre-computed summaries
.meta/ai_context/repo_summary.json
.meta/ai_context/code_graph.json
```

**3. Check edit policies:**
```yaml
# Before editing a file, check:
ai_policies.yaml -> zones -> safe_to_modify/review_required/read_only
```

**4. Validate changes:**
```bash
python scripts/validate_acs_conformance.py
```

---

## ACS Artifacts

### Core Artifacts

#### CODEBASE_INDEX.yaml
**Purpose:** Module index with dependencies and metadata

**Contents:**
- `metadata`: Repository info, version, references
- `layers`: 4-layer architecture (infra → domain → api → ui)
- `modules`: 25+ modules with:
  - Module ID (e.g., `core.state`)
  - Path, layer, purpose
  - Dependencies (`depends_on`)
  - Import patterns
  - AI priority (HIGH/MEDIUM/LOW)
  - Edit policy (safe/review-required/read-only)

**When to update:**
- New module added
- Module dependencies change
- Module path changes
- Architecture layer changes

**Example:**
```yaml
modules:
  - id: "core.state"
    name: "Core State Management"
    path: "core/state/"
    layer: "infra"
    purpose: "Database operations, CRUD, bundle loading"
    depends_on: []
    import_pattern: "from core.state.db import init_db"
    ai_priority: "HIGH"
    edit_policy: "safe"
```

#### QUALITY_GATE.yaml
**Purpose:** Quality gates and validation commands

**Contents:**
- Test commands (pytest, validation scripts)
- Execution order
- Failure policies (block/warn/info)
- CI integration specs

**When to update:**
- New validation script added
- Test command changes
- CI requirements change

#### ai_policies.yaml
**Purpose:** Machine-readable edit policies and invariants

**Contents:**
- **Zones**: safe_to_modify, review_required, read_only
- **Invariants**: 6 rules that must always hold
- **AI Guidance**: Context priorities, safe patterns

**When to update:**
- New restricted area added
- Module edit policy changes
- New invariant defined

**Key Invariants:**
1. **INV-SECTION-IMPORTS**: Section-based imports (CI enforced)
2. **INV-DB-SCHEMA**: Schema changes require migrations
3. **INV-PHASE-K-DOCS**: Documentation is canonical
4. **INV-MODULE-BOUNDARIES**: Layer dependency enforcement
5. **INV-QUALITY-GATES**: All gates must pass
6. **INV-TEST-COVERAGE**: Core changes need tests

#### .aiignore
**Purpose:** Unified AI tool ignore rules

**Consolidates:**
- `.gitignore` patterns
- `.aiderignore` patterns
- AI-specific exclusions

**Excludes:**
- Legacy code
- Runtime artifacts
- Build outputs
- Generated files
- Test sandboxes

### Generated Artifacts

#### .meta/ai_context/repo_summary.json
**Purpose:** Pre-computed repository metadata

**Auto-generated from:**
- CODEBASE_INDEX.yaml
- PROJECT_PROFILE.yaml
- docs/ARCHITECTURE.md

**Contains:**
- Repository overview
- Architecture layers
- Module statistics
- Dependency metrics
- Quality gate info
- Documentation index

**Regenerate when:**
- CODEBASE_INDEX.yaml updates
- New module added
- Major refactoring

#### .meta/ai_context/code_graph.json
**Purpose:** Module dependency graph

**Auto-generated from:**
- CODEBASE_INDEX.yaml (declared dependencies)

**Contains:**
- Nodes (25 modules)
- Edges (18 dependencies)
- Graph metrics
- Cycle validation

**Regenerate when:**
- Module dependencies change
- New module added

---

## Common Tasks

### Task 1: Add a New Module

**Steps:**

1. **Create module directory and code**
   ```bash
   mkdir -p core/new_feature
   # Create __init__.py, implementation files
   ```

2. **Add to CODEBASE_INDEX.yaml**
   ```yaml
   - id: "core.new_feature"
     name: "New Feature"
     path: "core/new_feature/"
     layer: "domain"
     purpose: "Description of feature"
     depends_on: ["core.state"]
     import_pattern: "from core.new_feature import feature"
     ai_priority: "MEDIUM"
     edit_policy: "safe"
   ```

3. **Update ai_policies.yaml if needed**
   ```yaml
   zones:
     safe_to_modify:
       paths:
         - "core/new_feature/**/*.py"
   ```

4. **Regenerate AI context**
   ```bash
   python scripts/generate_repo_summary.py
   python scripts/generate_code_graph.py
   ```

5. **Validate**
   ```bash
   python scripts/validate_acs_conformance.py
   ```

### Task 2: Change Module Dependencies

**Steps:**

1. **Update code** - Change imports as needed

2. **Update CODEBASE_INDEX.yaml**
   ```yaml
   - id: "core.engine"
     depends_on:
       - "core.state"
       - "core.new_feature"  # Added dependency
   ```

3. **Regenerate code graph**
   ```bash
   python scripts/generate_code_graph.py
   ```

4. **Validate** - Ensures no circular dependencies
   ```bash
   python scripts/validate_acs_conformance.py
   ```

### Task 3: Define a New Restricted Area

**Steps:**

1. **Update ai_policies.yaml**
   ```yaml
   zones:
     review_required:
       paths:
         - "core/critical_module/**"
       rationale:
         core_critical_module: "Impacts system stability"
   ```

2. **Document in AGENTS.md** (optional)

3. **Inform team** via PR description

### Task 4: Add a Quality Gate

**Steps:**

1. **Create validation script**
   ```bash
   # scripts/validate_new_feature.py
   ```

2. **Add to QUALITY_GATE.yaml**
   ```yaml
   gates:
     - name: "new-feature-validation"
       command: "python scripts/validate_new_feature.py"
       category: "validation"
       required: true
       order: 50
   ```

3. **Test execution**
   ```bash
   python scripts/validate_new_feature.py
   ```

---

## AI Tool Integration

### GitHub Copilot

**Configuration:**
- Copilot reads `.aiignore` automatically
- Reference CODEBASE_INDEX in comments for context

**Tips:**
```python
# Copilot suggestion: Use section-based imports
# ✓ Correct:
from core.state.db import init_db

# ✗ Deprecated (see CODEBASE_INDEX.yaml):
from src.pipeline.db import init_db
```

### Claude Code / Anthropic

**Loading context:**
```
Please load these ACS artifacts:
- CODEBASE_INDEX.yaml
- ai_policies.yaml
- .meta/ai_context/repo_summary.json
```

**Asking Claude:**
```
Based on ai_policies.yaml, can I safely modify core/engine/orchestrator.py?
```

### Aider

**Configuration:**
```bash
# Aider respects .aiderignore (now unified in .aiignore)
aider --model gpt-4

# Load module context
/add CODEBASE_INDEX.yaml
/add ai_policies.yaml
```

**Workflow:**
1. Load CODEBASE_INDEX to understand structure
2. Check ai_policies before edits
3. Run validation after changes

---

## Maintenance

### Regular Maintenance (Weekly)

**1. Validate conformance:**
```bash
python scripts/validate_acs_conformance.py
```

**2. Check for drift:**
```bash
# Ensure no modules missing from CODEBASE_INDEX
git diff CODEBASE_INDEX.yaml
```

**3. Update generated artifacts:**
```bash
python scripts/generate_repo_summary.py
python scripts/generate_code_graph.py
```

### After Major Changes

**When to regenerate:**
- New section added
- Module refactored
- Dependencies changed
- Architecture layer modified

**Commands:**
```bash
# Full regeneration
python scripts/generate_repo_summary.py
python scripts/generate_code_graph.py
python scripts/validate_acs_conformance.py
```

### Version Updates

**When updating ACS artifacts:**

1. **Increment version** in metadata sections
2. **Document changes** in version_history
3. **Regenerate** all derived artifacts
4. **Validate** conformance

---

## Troubleshooting

### Issue: Validator Reports Missing Modules

**Symptom:**
```
✗ All 25 module paths valid
  → core.new_feature: Path 'core/new_feature/' does not exist
```

**Solution:**
1. Check path spelling in CODEBASE_INDEX.yaml
2. Ensure directory exists on disk
3. Update CODEBASE_INDEX if module moved

### Issue: Circular Dependency Detected

**Symptom:**
```
✗ Code graph consistent with CODEBASE_INDEX
  → Cycle detected: core.engine -> core.state -> core.engine
```

**Solution:**
1. Review module dependencies in CODEBASE_INDEX.yaml
2. Refactor to break cycle (extract shared code to lower layer)
3. Regenerate code graph to verify fix

### Issue: AI Tool Ignoring Policies

**Symptom:**
AI tool suggests edits to read-only files

**Solution:**
1. Ensure `.aiignore` is in repository root
2. Check AI tool respects ignore files
3. Explicitly reference `ai_policies.yaml` in prompts

### Issue: Stale AI Context

**Symptom:**
AI context shows old module structure

**Solution:**
```bash
# Regenerate context
python scripts/generate_repo_summary.py
python scripts/generate_code_graph.py

# Verify freshness
git diff .meta/ai_context/
```

### Issue: Quality Gate Failures

**Symptom:**
```bash
python scripts/validate_acs_conformance.py
# Exit code 1
```

**Solution:**
1. Review validation output for specific failures
2. Fix reported issues
3. Re-run validator
4. Commit fixes

---

## FAQ

**Q: Do I need to commit .meta/ai_context/ files?**  
A: Yes (current decision). They're useful for CI/deployment. If regeneration in CI is preferred, add to `.gitignore`.

**Q: How often should I regenerate AI context?**  
A: After every structural change (new module, dependency change, refactor).

**Q: Can I modify ai_policies.yaml zones?**  
A: Yes! Update as repository evolves. Document rationale in the `rationale` field.

**Q: What if a module has multiple dependencies?**  
A: List all in `depends_on` array. Validator ensures they're all valid.

**Q: How do I add a new invariant?**  
A: Add to `ai_policies.yaml` → `invariants` with id, name, description, enforcement, and validation info.

**Q: Do I need MODULE.md for every subdirectory?**  
A: No. Parent-level README.md is sufficient. Validator only flags HIGH priority modules without docs.

---

## Reference

**ACS Specification Source:**
- `C:\Users\richg\TODO_TONIGHT\kpluspln.txt`
- `docs/AI_CODEBASE_STRUCTURE_FEASIBILITY.md`

**Implementation Plans:**
- `meta/plans/PH-ACS-AI-CODEBASE-STRUCTURE.md`
- `meta/plans/PH-ACS-PHASE-1-COMPLETE.md`
- `meta/plans/PH-ACS-PHASE-2-COMPLETE.md`

**Related Documentation:**
- `AGENTS.md` - Repository guidelines
- `DIRECTORY_GUIDE.md` - Human-friendly navigation
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DOCUMENTATION_INDEX.md` - Complete doc index

---

**Document Version:** 1.0.0  
**Maintained By:** System Architecture Team  
**Last Updated:** 2025-11-22
