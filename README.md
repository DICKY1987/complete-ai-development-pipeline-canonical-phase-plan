---
doc_id: DOC-GUIDE-README-1096
---

# Universal Execution Templates Framework - Documentation Index

**Status**: Framework 78% Complete (Phase 3 Done, Phase 4 Planned)
**Last Updated**: 2025-11-25
**Organization**: 4-Tier Quality System
**Duplication**: 0% (eliminated in cleanup)

---

## Quick Navigation

### 🤖 For AI Agents
- **Start Here**: [Bootstrap Spec](specs/core/UET_BOOTSTRAP_SPEC.md) - Autonomous framework installation
- **Core Protocol**: [Cooperation Spec](specs/core/UET_COOPERATION_SPEC.md) - Multi-tool cooperation
- **Speed Patterns**: [Quick Execution Playbook](QUICK_EXECUTION_PLAYBOOK.md) - 5-37x speedup techniques
- **Phase Plan**: [Documentation Cleanup Plan](UET_DOC_CLEANUP_PHASE_PLAN.md) - Example execution

### 👨‍💻 For Developers
- **Getting Started**: [UET Getting Started](uet/GETTING_STARTED.md)
- **Integration Guide**: [Integration Design](uet/integration/UET_INTEGRATION_DESIGN.md)
- **Component Contracts**: [UET V2 Contracts](uet/uet_v2/COMPONENT_CONTRACTS.md)
- **Examples**: [Phase Instances](specs/instances/)

### 📊 For Project Managers
- **Current Status**: [Framework Status](specs/planning/STATUS.md) (78% complete)
- **Future Plans**: [Phase 4 Enhancement Plan](specs/planning/PHASE_4_AI_ENHANCEMENT_PLAN.md)
- **Analysis Reports**: [Documentation Analysis](UET_DOCUMENTATION_ANALYSIS_REPORT.md)

---



---

## Core Specifications (Tier 1) ![Production](https://img.shields.io/badge/Status-Production-green)

*High-quality, schema-driven specifications - Authoritative source of truth*

### Framework Foundation
1. **[UET_BOOTSTRAP_SPEC.md](specs/core/UET_BOOTSTRAP_SPEC.md)**
   Autonomous framework installation protocol for AI agents

2. **[UET_COOPERATION_SPEC.md](specs/core/UET_COOPERATION_SPEC.md)**
   Multi-tool cooperation protocol (Run/Step/Event model)

3. **[UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md](specs/core/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md)**
   DAG-based parallel execution with worker pools

### Core Components
4. **[UET_PHASE_SPEC_MASTER.md](specs/core/UET_PHASE_SPEC_MASTER.md)**
   Phase template/schema definition (files_scope, constraints, acceptance)

5. **[UET_WORKSTREAM_SPEC.md](specs/core/UET_WORKSTREAM_SPEC.md)**
   Workstream bundle specifications with task dependencies

6. **[UET_TASK_ROUTING_SPEC.md](specs/core/UET_TASK_ROUTING_SPEC.md)**
   ExecutionRequest routing and validation

7. **[UET_PROMPT_RENDERING_SPEC.md](specs/core/UET_PROMPT_RENDERING_SPEC.md)**
   Universal prompt object and rendering rules

8. **[UET_PATCH_MANAGEMENT_SPEC.md](specs/core/UET_PATCH_MANAGEMENT_SPEC.md)**
   Patch artifact, ledger, and policy management

### Tool Integration
9. **[UET_CLI_TOOL_EXECUTION_SPEC.md](specs/core/UET_CLI_TOOL_EXECUTION_SPEC.md)**
   Single CLI instance execution with queue management

10. **[UTE_ID_SYSTEM_SPEC.md](specs/core/UTE_ID_SYSTEM_SPEC.md)**
    Cross-artifact linking ID system (doc_id)

---

## Implementation Guides (Tier 2) ![Stable](https://img.shields.io/badge/Status-Stable-blue)

### UET V2 Component Contracts (Draft)
- **[Component Contracts](uet/uet_v2/COMPONENT_CONTRACTS.md)** - API contracts for parallel development
- **[DAG Scheduler](uet/uet_v2/DAG_SCHEDULER.md)** - DAG-based task scheduling
- **[File Scope](uet/uet_v2/FILE_SCOPE.md)** - File scope management
- **[State Machines](uet/uet_v2/STATE_MACHINES.md)** - State machine definitions
- **[Integration Points](uet/uet_v2/INTEGRATION_POINTS.md)** - System integration

### Integration Documentation
- **[UET Index](uet/integration/UET_INDEX.md)** - Complete framework index
- **[Integration Design](uet/integration/UET_INTEGRATION_DESIGN.md)** - Selective integration approach
- **[Quick Reference](uet/integration/UET_QUICK_REFERENCE.md)** - Quick reference card

### Planning & Analysis
- **[Integration Analysis](uet/planning/INTEGRATION_ANALYSIS.md)** - Integration strategy
- **[Optimization Plan](uet/planning/OPTIMIZATION_PLAN.md)** - Performance optimization
- **[Patch Analysis](uet/planning/PATCH_ANALYSIS.md)** - Patch system analysis
- **[Template Implementation](uet/planning/TEMPLATE_IMPLEMENTATION_PLAN.md)** - Template strategy

### Execution Patterns
- **[Meta Execution Pattern](uet/META_EXECUTION_PATTERN.md)** - 37x speedup achievement
- **[Speed Patterns](uet/SPEED_PATTERNS_EXTRACTED.md)** - Extracted speed patterns
- **[Pattern Extraction Report](uet/PATTERN_EXTRACTION_REPORT.md)** - Pattern analysis

---

## Examples & Instances (Tier 3) ![Reference](https://img.shields.io/badge/Status-Reference-yellow)

### Phase Instances
- **[PH-ERR-01 + WS-ERR-01A](specs/instances/UET_PH-ERR-01%20+%20WS-ERR-01A.md)** - Error pipeline phase example
- **[WS-ERR-01A](specs/instances/UET_WS-ERR-01A.md)** - Error workstream example

### Session Transcripts
- **[Session PH-011](uet/SESSION_TRANSCRIPT_PH-011.md)** - Execution session transcript

---

## Planning & Historical (Tier 4) ![Historical](https://img.shields.io/badge/Status-Historical-gray)

### Current Planning
- **[Status](specs/planning/STATUS.md)** - Framework status (78% complete)
- **[Phase 4 AI Enhancement Plan](specs/planning/PHASE_4_AI_ENHANCEMENT_PLAN.md)** - Advanced AI features
- **[CLI Tool Instructions](specs/planning/CLI_TOOL_INSTRUCTIONS.md)** - Tool usage guide
- **[Framework Inventory](specs/planning/UET_Framework%20File%20Inventory%20(Project-Agnostic%20Core%20+%20Profiles%20+%20Examples.md)** - Complete inventory

### Archive
- Located in \specs/archive/\ - Historical and deprecated documents

---

## Execution Guides

### Quick Execution Resources
1. **[Quick Execution Playbook](QUICK_EXECUTION_PLAYBOOK.md)** - One-page reference for 5-37x speedup
2. **[Documentation Cleanup Phase Plan](UET_DOC_CLEANUP_PHASE_PLAN.md)** - Complete 5-wave execution example
3. **[Visual Execution Map](UET_DOC_CLEANUP_VISUAL_MAP.md)** - ASCII art execution flow
4. **[Documentation Analysis Report](UET_DOCUMENTATION_ANALYSIS_REPORT.md)** - Analysis and recommendations

---

## Quality Tier Legend

| Tier | Badge | Description | Quality Level |
|------|-------|-------------|---------------|
| **Tier 1 (Core)** | ![Production](https://img.shields.io/badge/Status-Production-green) | Production-ready specifications with schemas | **High** - Authoritative source |
| **Tier 2 (Implementation)** | ![Stable](https://img.shields.io/badge/Status-Stable-blue) | Stable implementation guides and contracts | **Medium** - Well-tested |
| **Tier 3 (Examples)** | ![Reference](https://img.shields.io/badge/Status-Reference-yellow) | Reference implementations and examples | **Good** - Learning resources |
| **Tier 4 (Archive)** | ![Historical](https://img.shields.io/badge/Status-Historical-gray) | Planning docs and historical artifacts | **Varies** - Context-dependent |

---

## Architecture Overview

The UET framework provides a complete AI-assisted development orchestration system:

### Key Capabilities
- **Autonomous Bootstrap** - AI agents self-configure for any project
- **DAG-based Parallel Execution** - 3-37x speedup demonstrated in practice
- **Multi-tool Cooperation** - Coordinate Claude, Copilot, Aider simultaneously
- **Patch-first Development** - Unified diff with validation and ledger
- **Production Resilience** - Circuit breakers, retry logic, recovery
- **Decision Elimination** - Pre-compiled templates for instant execution

### Proven Results
- **37x speedup** on pattern extraction (55 min vs 31 hours)
- **2.7x speedup** on module manifests (55 min vs 2.5 hours)
- **5-10x speedup** on documentation cleanup (2-3 hours vs 10+ hours)

### Pattern Applied
- Decision Elimination (all structural decisions pre-made)
- Parallel Execution (independent tasks run simultaneously)
- Infrastructure Over Deliverables (build reusable tools)
- Ground Truth Verification (automated, zero subjective review)

---

## Directory Structure

\\\
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── specs/                      # Specifications (organized by tier)
│   ├── core/                  # Tier 1: Production-ready core specs (10 files)
│   ├── instances/             # Tier 3: Example phase/workstream instances (2 files)
│   ├── planning/              # Tier 4: Planning and status docs (4 files)
│   └── archive/               # Historical/deprecated documents (8 files)
│
├── uet/                        # Implementation documentation
│   ├── integration/           # Integration guides and indexes
│   ├── planning/              # Analysis and planning documents
│   ├── reports/               # Coverage and analysis reports
│   └── uet_v2/                # Version 2 component contracts
│
├── README.md                   # This file - Master index
├── QUICK_EXECUTION_PLAYBOOK.md # One-page speedup guide
├── UET_DOC_CLEANUP_PHASE_PLAN.md # Example 5-wave execution
└── UET_DOCUMENTATION_ANALYSIS_REPORT.md # Analysis report
\\\

---

## Contribution Guidelines

### Adding New Specifications
1. Follow existing spec template structure
2. Include doc metadata (doc_ulid, doc_type, doc_layer)
3. Define JSON schemas for all data structures
4. Add to appropriate tier directory
5. Update this index with link and description

### Quality Standards
- **Tier 1**: Must have JSON schema, validation, and tests
- **Tier 2**: Must have implementation examples
- **Tier 3**: Must demonstrate working usage
- **Tier 4**: Informational only, no strict requirements

### Validation Tools
- Link checker: \scripts/validate_docs.ps1\ (created in Wave 4)
- Schema validator: Coming soon
- Consistency checker: Coming soon

---

## Next Steps

### Immediate (Week 1)
- [x] Consolidate documentation (COMPLETE)
- [x] Eliminate duplication (COMPLETE)
- [x] Create master index (COMPLETE)
- [ ] Add quality badges to all tier 1 specs
- [ ] Create link validation script

### Short-term (Week 2-4)
- [ ] Formalize DRAFT specs (add JSON schemas)
- [ ] Promote uet_v2 contracts to specs/core
- [ ] Create contribution guide
- [ ] Add CI/CD validation

### Long-term (Month 2+)
- [ ] Implement semantic versioning
- [ ] Create migration guides for breaking changes
- [ ] Build MkDocs documentation site
- [ ] Create video tutorials

---

**Last Updated**: 2025-11-25 05:54
**Cleanup Phase**: Completed (5 waves in ~2 hours)
**Pattern Applied**: Decision Elimination + Parallel Execution
**Duplication**: 0% (was 88% before cleanup)
**Organization**: 4-tier quality system (core/instances/planning/archive)
