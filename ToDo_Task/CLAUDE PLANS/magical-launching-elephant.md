# Documentation Discovery and Creation Plan for Module-Centric Refactoring

## Executive Summary

This plan provides a systematic approach to:
1. **Locate** existing documentation scattered across the repository
2. **Identify gaps** in documentation needed for module-centric architecture
3. **Create missing documentation** to support later refactoring efforts
4. **Organize** documentation in a logical, discoverable structure

**Goal:** Ensure all necessary documentation exists before executing the module-centric refactoring, enabling smooth transformation with minimal friction.

---

## Current State Analysis

### Documentation Already Exists

Based on repository exploration, the following documentation is already in place:

**Module-Centric Architecture (5 documents):**
- `docs/MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md` (391 lines) - Phase 1 status
- `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md` (523 lines) - 4-phase migration plan
- `Why Module-Centric Works Better_CHAT-AND_PLAN.md` - Planning document
- `schema/module.schema.json` - Module manifest schema
- `MODULES_INVENTORY.yaml` - Inventory of 33 modules

**Migration Documentation (6 documents):**
- `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md` - Migration procedures
- `docs/migration/UET_MIGRATION_GUIDE.md` - UET-specific guide
- `docs/migration/UET_OPERATOR_GUIDE.md` - Operations guide
- `docs/migration/UET_DEVELOPER_GUIDE.md` - Developer guide
- `MIGRATION_COMPLETION_REPORT.md` - Status tracking
- `Why Module-Centric Works Better_CHAT-AND_PLAN.md` - Execution plan

**Architecture Decision Records (8 ADRs):**
- ADR-0001 through ADR-0008 in `adr/` directory
- Cover: workstream model, hybrid architecture, SQLite storage, Python choice, etc.

**Developer Guides (12+ documents):**
- `docs/AGENT_GUIDE_START_HERE.md`
- `docs/QUICK_START.md`
- `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/README.md`
- Multiple phase guides in `developer/phases/`

**Pattern/Execution Documentation (15+ documents):**
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/` - Extensive pattern library
- `docs/PATTERN_EVENT_SPEC.md`
- Multiple EXEC-* specifications

### Critical Documentation Gaps

**Priority 1 - CRITICAL for Refactoring:**
1. **Module Contract Specification Template** - How modules declare interfaces
2. **ULID Naming Conventions Guide** - Detailed ULID prefix reference
3. **DAG Generation & Validation Spec** - How DAG files are created/validated
4. **Module Development Quickstart** - Step-by-step new module creation
5. **Module Testing Strategy** - Test organization patterns
6. **Import Path Update Guide** - Systematic import refactoring procedures
7. **ADR-0009: Module-Centric Architecture Decision** - Formal decision record
8. **ADR-0010: ULID Identity System** - Why ULID-based identity
9. **ADR-0011: Hybrid Import Strategy** - Why ULID files + __init__.py

**Priority 2 - HIGH for Operations:**
10. **Module State Management Specification** - How `.state/` works
11. **Module Health & Monitoring Guide** - Detecting unhealthy modules
12. **DAG Refresh Workflow** - When/how DAGs regenerate
13. **Migration Rollback Procedures** - Step-by-step rollback
14. **Breaking Change Policy** - Module version evolution
15. **Module Layer Architecture** - How infra/domain/api/ui interact

**Priority 3 - MEDIUM for Completeness:**
16. **Performance Guidelines** - Context token budgets, optimization
17. **Module Dependency Graph Visualization** - How to visualize deps
18. **Error/Exception Contracts** - What exceptions modules raise
19. **Schema Migration Guide** - Evolving module manifests
20. **Module-Specific Anti-Patterns** - Common mistakes

---

## Recommended Approach

### Phase 1: Documentation Discovery & Inventory (Day 1)

**Goal:** Create a comprehensive map of ALL existing documentation

**Actions:**
1. **Scan Repository for Documentation**
   - Search for all `.md` files: `find . -name "*.md"`
   - Search for all `.yaml` schema files: `find . -name "*.schema.*"`
   - Search for all ADR files: `ls adr/`
   - Search for pattern documentation: `ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/`

2. **Create Documentation Inventory**
   - File: `docs/navigation/DOCUMENTATION_INVENTORY.md`
   - Categorize by:
     - Module-Centric Architecture
     - Migration & Refactoring
     - Architecture Decision Records
     - Developer Guides
     - API/Contract Documentation
     - Patterns & Execution
     - Operations & Maintenance

3. **Identify Gaps**
   - Compare inventory against required documentation list
   - Mark each item as: ✅ Exists | ⚠️ Partial | ❌ Missing
   - Prioritize gaps: CRITICAL | HIGH | MEDIUM | LOW

**Output:**
- `docs/navigation/DOCUMENTATION_INVENTORY.md` - Complete inventory
- `docs/navigation/DOCUMENTATION_GAPS.md` - Prioritized gap list

---

### Phase 2: Create Critical ADRs (Day 2)

**Goal:** Document architectural decisions that justify module-centric approach

**ADR Template Structure:**
```markdown
# ADR-XXXX: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What forces are at play? What problem are we solving?]

## Decision
[What is the change we're proposing/making?]

## Consequences
[What becomes easier or harder after this change?]

## Alternatives Considered
[What other options did we evaluate?]
```

**Documents to Create:**

1. **adr/0009-module-centric-architecture.md**
   - Context: Why artifact-type organization (core/, error/, aim/) is problematic
   - Decision: Organize by module boundary, not artifact type
   - Consequences: AI context loading, SafePatch worktrees, parallel execution
   - Alternatives: Keep artifact-type, hybrid approach, monorepo tools

2. **adr/0010-ulid-identity-system.md**
   - Context: Need machine-verifiable relationships between artifacts
   - Decision: Use ULID prefixes (010001, 010002, etc.) for file identity
   - Consequences: File grouping, human/AI recognition, Git tracking
   - Alternatives: UUIDs, sequential numbers, hash-based names

3. **adr/0011-hybrid-import-strategy.md**
   - Context: Python cannot import numeric-prefixed files (010001_db.py)
   - Decision: ULID files + __init__.py re-exports for clean imports
   - Consequences: Import compatibility, ULID identity preserved
   - Alternatives: Rename files, wrapper modules, symlinks

4. **adr/0012-dag-driven-execution.md**
   - Context: Need deterministic execution order across modules
   - Decision: Generate DAGs from manifests, not hand-edit
   - Consequences: Auto-refresh, staleness detection, validation
   - Alternatives: Manual DAG editing, runtime computation, database storage

**Templates:** Use existing ADR format from `adr/0001-workstream-model-choice.md`

---

### Phase 3: Create Module Development Documentation (Day 3-4)

**Goal:** Enable developers to create, test, and maintain modules

**Documents to Create:**

1. **docs/developer/MODULE_DEVELOPMENT_QUICKSTART.md**
   ```markdown
   # Module Development Quickstart

   ## Creating Your First Module
   1. Choose ULID prefix (check MODULES_INVENTORY.yaml)
   2. Create module directory: modules/my-module/
   3. Generate manifest: python scripts/generate_module_manifest.py
   4. Add implementation files with ULID prefix
   5. Create __init__.py for clean imports
   6. Write tests colocated with code

   ## Module Structure
   [Directory tree example]

   ## Module Manifest
   [YAML template with explanations]

   ## Testing Your Module
   [Test patterns and commands]

   ## Integration with Existing Modules
   [How to declare dependencies]
   ```

2. **docs/developer/MODULE_TESTING_STRATEGY.md**
   ```markdown
   # Module Testing Strategy

   ## Test Organization
   - Colocate tests with code (010001_db.test.py)
   - Use module-level fixtures
   - Isolate module state

   ## Test Patterns
   - Unit tests for individual functions
   - Integration tests for module interactions
   - Contract tests for API boundaries

   ## Running Tests
   [Commands for different test scopes]

   ## Test Coverage Requirements
   [Coverage thresholds per layer]
   ```

3. **docs/reference/MODULE_CONTRACT_SPECIFICATION.md**
   ```markdown
   # Module Contract Specification

   ## Contract Template
   [YAML template for module contracts]

   ## Input Contracts
   - Parameter types
   - Preconditions
   - Validation rules

   ## Output Contracts
   - Return types
   - Postconditions
   - Error states

   ## Exceptions
   [Exception contract specification]

   ## Versioning
   [Semantic versioning for contracts]
   ```

4. **docs/reference/ULID_NAMING_CONVENTIONS.md**
   ```markdown
   # ULID Naming Conventions

   ## ULID Format
   - 6 hexadecimal characters: 010001, 010002, etc.
   - Globally unique within repository

   ## Assignment Rules
   - Infrastructure layer: 01000X
   - Domain layer: 01000X - 01001X
   - API layer: 01001X - 01002X
   - UI layer: 01002X+

   ## File Naming
   - Implementation: {ULID}_filename.py
   - Tests: {ULID}_filename.test.py
   - Schemas: {ULID}_filename.schema.json
   - Docs: {ULID}_filename.md
   - Manifest: {ULID}_module.manifest.yaml

   ## ULID Registry
   [Table mapping ULID → Module]
   ```

---

### Phase 4: Create DAG System Documentation (Day 5)

**Goal:** Document how DAGs are generated, validated, and used

**Documents to Create:**

1. **docs/architecture/DAG_ARCHITECTURE.md**
   ```markdown
   # DAG Architecture - Three-Tier System

   ## Overview
   Directed Acyclic Graphs (DAGs) are DERIVED STATE, not hand-edited.

   ## Three Tiers

   ### Tier 1: Global Module Dependency DAG
   - Location: .state/dag/repo_modules.dag.json
   - Source: Module manifests (dependencies.modules)
   - Purpose: Determine module execution order

   ### Tier 2: Per-Module Task DAGs
   - Location: modules/{module}/.state/module_tasks.dag.json
   - Source: Pattern registry + module artifacts
   - Purpose: Determine operations applicable to module

   ### Tier 3: Pipeline Workflow DAGs
   - Location: .state/dag/pipelines/{pipeline}.dag.json
   - Source: Pipeline specifications
   - Purpose: Drive end-to-end workflows

   ## DAG JSON Schema
   [Schema with examples]

   ## DAG Refresh Triggers
   - Git hooks (post-merge, post-checkout)
   - CI validation (pre-commit check)
   - Manual: python scripts/refresh_repo_dag.py
   ```

2. **docs/architecture/DAG_GENERATION_SPECIFICATION.md**
   ```markdown
   # DAG Generation Specification

   ## Generation Algorithm
   1. Load module manifests
   2. Build dependency graph using dag_utils.analyze_bundles()
   3. Detect cycles
   4. Compute topological levels
   5. Calculate critical path
   6. Write JSON with metadata

   ## Staleness Detection
   - Compute manifest hash (SHA256)
   - Store in DAG JSON: "source_hash": "abc123..."
   - Compare on read: hash mismatch → stale

   ## Validation Rules
   - No cycles allowed
   - All modules must have valid manifests
   - DAG must have at least one root node

   ## Schema Validation
   [JSON Schema reference]
   ```

3. **docs/operations/DAG_REFRESH_WORKFLOW.md**
   ```markdown
   # DAG Refresh Workflow

   ## Automatic Refresh
   - Post-merge hook: Regenerate after git pull
   - Post-checkout hook: Regenerate on branch switch
   - Pre-commit hook: Validate freshness before commit

   ## Manual Refresh
   ```bash
   # Regenerate all DAGs
   python scripts/refresh_repo_dag.py

   # Validate freshness
   python scripts/validate_dag_freshness.py
   ```

   ## CI Integration
   [GitHub Actions workflow]

   ## Troubleshooting
   [Common issues and solutions]
   ```

---

### Phase 5: Create Migration Support Documentation (Day 6)

**Goal:** Provide step-by-step procedures for safe migration

**Documents to Create:**

1. **docs/migration/IMPORT_PATH_UPDATE_GUIDE.md**
   ```markdown
   # Import Path Update Guide

   ## Old vs New Import Paths
   | Old | New |
   |-----|-----|
   | from core.state.db import X | from modules.core_state import X |
   | from error.plugins.ruff.plugin import Y | from modules.error_plugin_python_ruff import Y |

   ## Automated Update Procedure
   ```bash
   # Step 1: Analyze current imports
   python scripts/analyze_imports.py

   # Step 2: Batch rewrite (dry-run first)
   python scripts/rewrite_imports_v2.py --dry-run

   # Step 3: Execute rewrite
   python scripts/rewrite_imports_v2.py --execute

   # Step 4: Validate
   python -m compileall modules/ -q
   ```

   ## Manual Update Checklist
   [Step-by-step for complex cases]
   ```

2. **docs/migration/MIGRATION_ROLLBACK_PROCEDURES.md**
   ```markdown
   # Migration Rollback Procedures

   ## Phase-by-Phase Rollback

   ### Phase 1 Rollback: Undo __init__.py Generation
   ```bash
   git restore modules/*/__init__.py
   ```

   ### Phase 2 Rollback: Restore Old Imports
   ```bash
   git restore modules/
   ```

   ### Phase 3 Rollback: Restore Old Structure
   ```bash
   # Move from archive back to root
   mv archive/structure_archived_*/core/ ./
   mv archive/structure_archived_*/error/ ./
   ```

   ### Complete Rollback
   ```bash
   git reset --hard <commit_before_migration>
   ```

   ## Validation After Rollback
   [Tests to run]
   ```

3. **docs/migration/MIGRATION_SUCCESS_CRITERIA.md**
   ```markdown
   # Migration Success Criteria

   ## Checklist for Phase 1
   - [ ] All 34 __init__.py files created
   - [ ] All compile without errors: exit code 0
   - [ ] No TODO placeholders in generated files
   - [ ] Checkpoints created: .execution/checkpoints/

   ## Checklist for Phase 2
   - [ ] All 179 imports rewritten
   - [ ] All 4 batches validated
   - [ ] All modules compile: python -m compileall modules/ -q
   - [ ] No ULID imports in code
   - [ ] All tests pass: 196/196

   ## Checklist for Phase 3
   - [ ] Old structure archived
   - [ ] Archive verified: 5 directories in archive/
   - [ ] CODEBASE_INDEX.yaml updated
   - [ ] Documentation reflects new paths

   ## Checklist for Phase 4
   - [ ] All validation gates pass
   - [ ] Git commit created
   - [ ] No untracked files
   - [ ] Worktrees cleaned up
   ```

---

### Phase 6: Create Architecture & Operations Docs (Day 7)

**Goal:** Document system architecture and operational procedures

**Documents to Create:**

1. **docs/architecture/MODULE_LAYER_ARCHITECTURE.md**
   ```markdown
   # Module Layer Architecture

   ## Four-Layer Design

   ### Infrastructure Layer (Layer 1)
   - Modules: core-state
   - Responsibility: Database, CRUD, state management
   - Dependencies: None (foundation)

   ### Domain Layer (Layer 2)
   - Modules: core-engine, core-planning, error-engine, specifications-tools
   - Responsibility: Business logic, orchestration
   - Dependencies: Infrastructure layer

   ### API Layer (Layer 3)
   - Modules: aim-*, pm-*
   - Responsibility: External interfaces, CLI, services
   - Dependencies: Domain layer

   ### UI Layer (Layer 4)
   - Modules: error-plugin-*
   - Responsibility: Plugins, user-facing components
   - Dependencies: API + Domain layers

   ## Dependency Rules
   - Lower layers cannot depend on upper layers
   - Cross-layer dependencies must be explicit in manifests

   ## Communication Patterns
   [How layers interact]
   ```

2. **docs/operations/MODULE_STATE_MANAGEMENT.md**
   ```markdown
   # Module State Management

   ## .state/ Directory Structure
   ```
   modules/{module}/.state/
   ├── current.json          # Current module state
   ├── module_tasks.dag.json # Task DAG (generated)
   └── history/              # State history (optional)
   ```

   ## State Schema
   [JSON schema for current.json]

   ## State Transitions
   [State machine diagram]

   ## State Persistence
   [When state is written to disk]

   ## State Recovery
   [How to recover from corrupted state]
   ```

3. **docs/operations/MODULE_HEALTH_MONITORING.md**
   ```markdown
   # Module Health Monitoring

   ## Health Indicators
   - Test pass rate
   - Import resolution success
   - Compilation errors
   - Dependency freshness
   - State corruption

   ## Health Check Command
   ```bash
   python scripts/check_module_health.py --module core-engine
   python scripts/check_module_health.py --all
   ```

   ## Remediation Procedures
   [What to do when module is unhealthy]

   ## Monitoring Dashboard
   [Integration with monitoring tools]
   ```

---

## Implementation Strategy

### Execution Sequence

**Week 1: Core Documentation**
- Day 1: Phase 1 - Documentation Discovery & Inventory
- Day 2: Phase 2 - Create Critical ADRs (4 ADRs)
- Day 3-4: Phase 3 - Module Development Documentation (4 docs)
- Day 5: Phase 4 - DAG System Documentation (3 docs)

**Week 2: Migration & Operations**
- Day 6: Phase 5 - Migration Support Documentation (3 docs)
- Day 7: Phase 6 - Architecture & Operations Docs (3 docs)

**Total Output:**
- 4 ADRs
- 13 comprehensive documentation files
- 2 navigation/inventory files
- ~3,000-5,000 lines of documentation

### Documentation Organization

**Proposed Structure:**
```
docs/
├── navigation/
│   ├── DOCUMENTATION_INVENTORY.md       # Complete inventory
│   ├── DOCUMENTATION_GAPS.md            # Gap analysis
│   └── MASTER_NAVIGATION_INDEX.md       # Top-level navigation
│
├── architecture/
│   ├── MODULE_LAYER_ARCHITECTURE.md     # Layer design
│   ├── DAG_ARCHITECTURE.md              # DAG system overview
│   └── DAG_GENERATION_SPECIFICATION.md  # DAG generation details
│
├── developer/
│   ├── MODULE_DEVELOPMENT_QUICKSTART.md # New module creation
│   ├── MODULE_TESTING_STRATEGY.md       # Testing patterns
│   └── IMPORT_PATH_UPDATE_GUIDE.md      # Import refactoring
│
├── reference/
│   ├── MODULE_CONTRACT_SPECIFICATION.md # Contract template
│   ├── ULID_NAMING_CONVENTIONS.md       # ULID reference
│   └── API_INDEX.md                     # API documentation index
│
├── migration/
│   ├── MIGRATION_ROLLBACK_PROCEDURES.md # Rollback guide
│   └── MIGRATION_SUCCESS_CRITERIA.md    # Success checklist
│
├── operations/
│   ├── MODULE_STATE_MANAGEMENT.md       # State management
│   ├── MODULE_HEALTH_MONITORING.md      # Health checks
│   └── DAG_REFRESH_WORKFLOW.md          # DAG refresh procedures
│
└── adr/
    ├── 0009-module-centric-architecture.md
    ├── 0010-ulid-identity-system.md
    ├── 0011-hybrid-import-strategy.md
    └── 0012-dag-driven-execution.md
```

---

## Success Criteria

### Documentation Completeness
- ✅ All CRITICAL gaps (9 items) filled
- ✅ All HIGH priority gaps (6 items) filled
- ✅ Documentation organized in logical structure
- ✅ Navigation index created for discoverability

### Documentation Quality
- ✅ Each document has clear purpose and audience
- ✅ Examples and code snippets included
- ✅ Cross-references to related documentation
- ✅ Follows consistent template/format

### Enablement for Refactoring
- ✅ Developers can create new modules independently
- ✅ Migration procedures are unambiguous
- ✅ Rollback procedures are tested and documented
- ✅ Health monitoring enables proactive maintenance

### Maintenance
- ✅ Documentation source files tracked in Git
- ✅ Update procedures documented
- ✅ Ownership assigned (in each doc header)

---

## Tools and Scripts Needed

### Documentation Generation
1. **scripts/generate_doc_inventory.py** - Auto-scan repo for .md files
2. **scripts/validate_doc_links.py** - Check cross-references are valid
3. **scripts/generate_ulid_registry.py** - Create ULID → Module mapping table

### Documentation Validation
1. **scripts/check_doc_completeness.py** - Verify all critical docs exist
2. **scripts/lint_documentation.py** - Check markdown formatting
3. **scripts/generate_doc_metrics.py** - Count lines, coverage, etc.

---

## Risk Mitigation

### Risk: Documentation Becomes Stale
**Mitigation:**
- Documentation lives in Git, versioned with code
- CI validation checks for broken links
- Quarterly documentation review process

### Risk: Duplication with Existing Docs
**Mitigation:**
- Phase 1 inventory identifies overlaps
- Consolidate duplicate content
- Create cross-references instead of copying

### Risk: Too Much Documentation
**Mitigation:**
- Focus on CRITICAL and HIGH priority gaps only
- Keep documentation concise (400-800 lines per doc)
- Use templates to avoid over-explaining

### Risk: Documentation Not Discoverable
**Mitigation:**
- Create MASTER_NAVIGATION_INDEX.md
- Add README.md in each docs/ subdirectory
- Reference from main README.md

---

## Next Steps After Plan Approval

1. **Execute Phase 1** - Create documentation inventory (Day 1)
2. **Review with user** - Validate gaps identified are correct
3. **Execute Phases 2-6** - Create documentation systematically
4. **Final review** - User validates documentation completeness
5. **Ready for refactoring** - All documentation in place

---

## Open Questions for User

1. **Prioritization:** Do you agree with CRITICAL/HIGH/MEDIUM prioritization, or should any gaps be elevated?
2. **Scope:** Should we create ALL missing documentation, or focus only on CRITICAL items for now?
3. **Format:** Preference for documentation format (Markdown, RST, Wiki)?
4. **Ownership:** Who should be listed as document owners/maintainers?
5. **Existing Docs:** Should we consolidate/refactor existing docs, or only create missing ones?
