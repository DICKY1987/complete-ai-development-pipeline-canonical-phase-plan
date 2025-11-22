# Documentation Index - AI Development Pipeline

> **Purpose:** Central navigation hub for all documentation  
> **Last Updated:** 2025-11-22  
> **For AI Agents:** Start here for system understanding  
> **Auto-generated:** This file is partially auto-generated. See `scripts/generate_doc_index.py`

---

## Quick Navigation

| I need to... | Go to... | Type |
|--------------|----------|------|
| Understand architecture | [ARCHITECTURE.md](ARCHITECTURE.md) | Overview |
| Learn terminology | [TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md) | Reference |
| Execute workstreams | [Workstream Guide](workstream_authoring_guide.md) | How-To |
| Debug errors | [Error Pipeline](../error/README.md) | System |
| Integrate tools | [AIM Integration](AIM_docs/AIM_INTEGRATION_CONTRACT.md) | Contract |
| Find implementations | [Implementation Locations](IMPLEMENTATION_LOCATIONS.md) | Reference |
| View diagrams | [Visual Architecture Guide](VISUAL_ARCHITECTURE_GUIDE.md) | Diagrams |

---

## Documentation Categories

### 1. Architecture & Design (Current State)

**Core Architecture:**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[HYBRID_WORKFLOW.md](HYBRID_WORKFLOW.md)** - Execution model (GUI/TUI/Terminal)
- **[TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md)** - Canonical terminology (47 terms)
- **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** - Visual architecture references
- **[VISUAL_ARCHITECTURE_GUIDE.md](VISUAL_ARCHITECTURE_GUIDE.md)** - Interactive diagram navigation

**Data & State:**
- **[analysis/Data Flow Analysis.md](analysis/Data%20Flow%20Analysis.md)** - System data flows
- **[state_machine.md](state_machine.md)** - State machine documentation

**Component Architecture:**
- **[ENGINE_IMPLEMENTATION_SUMMARY.md](ENGINE_IMPLEMENTATION_SUMMARY.md)** - Job execution engine
- **[UI_IMPLEMENTATION_SUMMARY.md](UI_IMPLEMENTATION_SUMMARY.md)** - UI infrastructure
- **[plugin-ecosystem-summary.md](plugin-ecosystem-summary.md)** - Plugin architecture

---

### 2. Workflows (How Things Work)

#### OpenSpec → Workstream Flow
1. **Start**: [openspec_bridge.md](Project_Management_docs/openspec_bridge.md) - Create proposals
2. **Process**: [BRIDGE_SUMMARY.md](../specifications/bridge/BRIDGE_SUMMARY.md) - Conversion workflow
3. **Execute**: [workstream_authoring_guide.md](workstream_authoring_guide.md) - Execution guide

**Files:**
- `docs/Project_Management_docs/openspec_bridge.md`
- `specifications/bridge/BRIDGE_SUMMARY.md`
- `core/openspec_convert.py` (implementation)

#### Error Detection & Escalation
1. **Detection**: [error/plugins/README.md](../error/README.md) - 21 validation plugins
2. **State Machine**: `error/engine/error_engine.py` - 4-tier escalation
3. **Recovery**: `core/engine/recovery.py` - Self-healing logic

**Files:**
- `error/plugins/` (21 detection plugins)
- `error/engine/error_engine.py` (state machine)
- `core/engine/recovery.py` (recovery manager)

#### Tool Selection & Execution
1. **Capability Routing**: `aim/bridge.py` - AIM resolution
2. **Adapter Execution**: `core/engine/adapters/base.py` - Tool wrappers
3. **Profile Loading**: `core/engine/tools.py` - Configuration

**Files:**
- `aim/bridge.py` (AIM integration)
- `core/engine/adapters/` (tool adapters)
- `invoke.yaml` (tool profiles)

#### Workstream Execution
1. **Orchestration**: `core/engine/orchestrator.py` - Main execution loop
2. **DAG Building**: Task dependency resolution
3. **Worktree Isolation**: `core/state/worktree.py` - Parallel safety

**Files:**
- `core/engine/orchestrator.py`
- `core/state/worktree.py`
- `.worktrees/` (runtime isolation)

---

### 3. Decision Records (Why Things Are)

**Architecture Decision Records (ADRs):**
- **[adr-0005-spec-tooling-consolidation.md](adr/adr-0005-spec-tooling-consolidation.md)** - Specs → specifications/
- **[adr-error-utils-location.md](adr/adr-error-utils-location.md)** - Error utilities placement

**Migration & Refactor Decisions:**
- **[DEPRECATION_PLAN.md](DEPRECATION_PLAN.md)** - Shim removal strategy
- **[SPEC_MIGRATION_GUIDE.md](SPEC_MIGRATION_GUIDE.md)** - Spec consolidation rationale
- **[CI_PATH_STANDARDS.md](CI_PATH_STANDARDS.md)** - Import path enforcement

**Design Rationale:**
- **[HYBRID_WORKFLOW.md](HYBRID_WORKFLOW.md)** - Why hybrid execution model
- **[COORDINATION_GUIDE.md](COORDINATION_GUIDE.md)** - Multi-agent coordination

---

### 4. Implementation Guides

**Core Systems:**
- **[core/README.md](../core/README.md)** - Core pipeline (state, engine, planning)
- **[error/README.md](../error/README.md)** - Error detection system
- **[engine/README.md](../engine/README.md)** - Job-based execution engine
- **[specifications/README.md](../specifications/README.md)** - Spec management
- **[aim/DEPLOYMENT_GUIDE.md](../aim/DEPLOYMENT_GUIDE.md)** - AIM integration

**Feature Guides:**
- **[GUI_DEVELOPMENT_GUIDE.md](GUI_DEVELOPMENT_GUIDE.md)** - UI development
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - System configuration
- **[workstream_authoring_guide.md](workstream_authoring_guide.md)** - Workstream creation

**Quick References:**
- **[ENGINE_QUICK_REFERENCE.md](ENGINE_QUICK_REFERENCE.md)** - Engine commands
- **[plugin-quick-reference.md](plugin-quick-reference.md)** - Plugin usage

---

### 5. Migration & Deprecation

**Active Migrations:**
- **[DEPRECATION_PLAN.md](DEPRECATION_PLAN.md)** - Shim removal timeline (Phase 1: Silent)
- **[SPEC_MIGRATION_GUIDE.md](SPEC_MIGRATION_GUIDE.md)** - openspec/ + spec/ → specifications/
- **[CI_PATH_STANDARDS.md](CI_PATH_STANDARDS.md)** - Import path enforcement

**Completed Migrations:**
- **[specifications/MIGRATION_COMPLETE.md](../specifications/MIGRATION_COMPLETE.md)** - Spec consolidation complete
- **[SPEC_CONSOLIDATION_INVENTORY.md](SPEC_CONSOLIDATION_INVENTORY.md)** - Inventory of changes

**Legacy Archive:**
- **[LEGACY_ARCHIVE_CANDIDATES.md](LEGACY_ARCHIVE_CANDIDATES.md)** - Files for archival
- **[archive/](archive/)** - Archived documentation

---

### 6. Phase Completion Reports

**Recent Phases (Reverse Chronological):**
- **[Phase I](PHASE_I_COMPLETE.md)** - UET Integration Complete
- **[Phase H](PHASE_G_COMPLETE_REPORT.md)** - Directory Consolidation Complete
- **[Phase G](PHASE_G_FINAL_SUMMARY.md)** - Invoke Adoption Complete
- **[Phase F](PHASE_F_CHECKLIST.md)** - Post-Refactor Cleanup
- **[Phase E](../specifications/MIGRATION_COMPLETE.md)** - Section Refactor Complete

**Component Completion:**
- **[AIM_PLUS_FINAL_REPORT.md](AIM_PLUS_FINAL_REPORT.md)** - AIM+ Integration COMPLETE
- **[UET_IMPLEMENTATION_COMPLETE.md](UET_IMPLEMENTATION_COMPLETE.md)** - UET Framework COMPLETE
- **[ENGINE_IMPLEMENTATION_SUMMARY.md](ENGINE_IMPLEMENTATION_SUMMARY.md)** - Engine Implementation COMPLETE
- **[UI_IMPLEMENTATION_SUMMARY.md](UI_IMPLEMENTATION_SUMMARY.md)** - UI Infrastructure COMPLETE

**Current Phase:**
- **[PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md](PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md)** - Documentation Enhancement (IN PROGRESS)

---

### 7. Reference Documentation

**Terminology:**
- **[TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md)** - 47 canonical terms (v1.1)
- **[IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md)** - Terms → code mapping
- **[TERM_RELATIONSHIPS.md](TERM_RELATIONSHIPS.md)** - Term dependency graphs

**Specifications:**
- **[SPEC_MANAGEMENT_CONTRACT.md](SPEC_MANAGEMENT_CONTRACT.md)** - Spec system contract
- **[PATH_ABSTRACTION_SPEC.md](PATH_ABSTRACTION_SPEC.md)** - Path handling standards

**Integration Contracts:**
- **[AIM_docs/AIM_INTEGRATION_CONTRACT.md](AIM_docs/AIM_INTEGRATION_CONTRACT.md)** - AIM contract
- **[aider_contract.md](aider_contract.md)** - Aider integration

---

### 8. Project Management

**Phase Planning:**
- **[PHASE_PLAN.md](PHASE_PLAN.md)** - Overall phase roadmap
- **[PHASE_ROADMAP.md](PHASE_ROADMAP.md)** - Development roadmap
- **[planning/](planning/)** - Phase planning documents

**CCPM & PM:**
- **[Project_Management_docs/](Project_Management_docs/)** - PM documentation
- **[pm/CONTRACT.md](../pm/CONTRACT.md)** - PM contract

---

## For AI Agents

### Context Loading Priority

**HIGH** (always load for system understanding):
1. **[TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md)** - Terminology foundation
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
3. **[AGENTS.md](../AGENTS.md)** - Coding standards
4. **[DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md)** - Repository structure

**MEDIUM** (load for specific domains):
- **[core/README.md](../core/README.md)** - Core pipeline
- **[error/README.md](../error/README.md)** - Error system
- **[engine/README.md](../engine/README.md)** - Execution engine
- **[specifications/README.md](../specifications/README.md)** - Spec management

**LOW** (load on explicit request):
- Phase completion reports
- Migration guides (unless working on migrations)
- Archived documentation

---

### Finding Information

| Question Type | Go To |
|---------------|-------|
| **"How do I..."** | Workflows section above |
| **"What is..."** | [TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md) |
| **"Why is..."** | Decision Records section |
| **"Where is..."** | [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md) |
| **"Show me..."** | [VISUAL_ARCHITECTURE_GUIDE.md](VISUAL_ARCHITECTURE_GUIDE.md) |

---

### Common Questions Map

| Question | Answer Location |
|----------|-----------------|
| How does workstream execution work? | `core/engine/orchestrator.py` + [HYBRID_WORKFLOW.md](HYBRID_WORKFLOW.md) |
| What tools are available? | `aim/registry/` + `invoke.yaml` |
| How are errors handled? | [error/README.md](../error/README.md) + `error/engine/error_engine.py` |
| What do these terms mean? | [TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md) |
| How do I create a workstream? | [workstream_authoring_guide.md](workstream_authoring_guide.md) |
| Where is X implemented? | [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md) |
| What's the data flow? | [VISUAL_ARCHITECTURE_GUIDE.md](VISUAL_ARCHITECTURE_GUIDE.md) |
| How do I integrate a tool? | [AIM_docs/AIM_INTEGRATION_CONTRACT.md](AIM_docs/AIM_INTEGRATION_CONTRACT.md) |
| What's deprecated? | [DEPRECATION_PLAN.md](DEPRECATION_PLAN.md) |
| What changed in Phase X? | Phase Completion Reports section |

---

### Navigation Tips

**Start with the right entry point:**
- New to codebase? → [ARCHITECTURE.md](ARCHITECTURE.md)
- Need to implement feature? → [Workflows](#2-workflows-how-things-work)
- Debugging issue? → [error/README.md](../error/README.md)
- Understanding term? → [TERMS_SPEC_V1.md](../TERMS_SPEC_V1.md)
- Looking for code? → [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md)

**Follow the documentation hierarchy:**
```
DOCUMENTATION_INDEX.md (you are here)
  ├── High-level: ARCHITECTURE.md, TERMS_SPEC_V1.md
  ├── Workflows: How things work end-to-end
  ├── Implementation: Section READMEs (core/, error/, etc.)
  └── Code: IMPLEMENTATION_LOCATIONS.md (file:line references)
```

---

## Maintenance

**Daily (Automated):**
- Documentation index validation (broken links)
- Cross-reference index generation
- Implementation location scanning

**Weekly:**
- Review for stale content
- Update phase completion status
- Check for new ADRs

**On Major Changes:**
- Refactor → Update architecture docs
- New feature → Update workflows section
- API change → Update implementation locations

---

## Index Statistics

**Last Updated:** 2025-11-22  
**Total Documents:** 80+  
**Categories:** 8  
**Auto-generated Sections:** Implementation Locations, Cross-References  
**Manual Sections:** All others

---

**END OF DOCUMENTATION INDEX**
