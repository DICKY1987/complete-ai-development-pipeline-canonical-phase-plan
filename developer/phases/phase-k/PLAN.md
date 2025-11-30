---
doc_id: DOC-GUIDE-PLAN-1305
---

# Phase K: Documentation Enhancement & AI Understanding Improvement

**Status**: Planning  
**Timeline**: 8-12 days  
**Dependencies**: Phase J (Error Detection Integration)  
**Created**: 2025-11-22

## Overview

This phase addresses the critical need for better documentation structure and AI agent comprehension. The current system has 47 specialized terms, complex cross-references, and implementation scattered across multiple sections. AI agents struggle to locate implementations and understand relationships between components.

## Goals

1. Create a centralized documentation index with navigation to all key concepts
2. Map every specialized term to its exact implementation location (file:line)
3. Provide concrete, executable examples for common use cases
4. Visualize architecture and data flows with Mermaid diagrams
5. Build auto-generation scripts to keep documentation synchronized with code
6. Establish cross-reference system showing term relationships and dependencies

## Success Metrics

- ✅ AI agents can answer "where is X implemented?" in <10 seconds
- ✅ All 47 specialized terms mapped to exact file:line locations
- ✅ All example workstreams execute without modification
- ✅ Visual diagrams auto-validated against code structure
- ✅ Zero broken cross-references in documentation
- ✅ Documentation index updated automatically via CI

## Sub-Phases

### K-1: Foundation & Index (Days 1-3)

**Objective**: Create master documentation index and implementation location mappings.

#### Deliverables

1. **DOCUMENTATION_INDEX.md**
   - Central navigation hub for all documentation
   - Organized by concern: Core Engine, Error Detection, Specifications, Integrations
   - Links to all phase plans, architecture docs, and guides
   - Quick reference section for common tasks

2. **IMPLEMENTATION_LOCATIONS.md**
   - Every specialized term mapped to implementation
   - Format: `Term → File:Line → Description`
   - Example:
     ```
     Circuit Breaker → core/engine/circuit_breaker.py:45 → Class definition
     Circuit Breaker → config/circuit_breaker.yaml:1 → Configuration schema
     Circuit Breaker → docs/ADR_CIRCUIT_BREAKER.md → Design rationale
     ```
   - Cross-references to related terms

3. **scripts/generate_doc_index.py**
   - Scans all markdown files in docs/
   - Generates hierarchical index
   - Validates internal links
   - Outputs warnings for orphaned docs

4. **scripts/generate_implementation_map.py**
   - Parses Python/YAML/JSON for known terms
   - Uses AST analysis to find class/function definitions
   - Outputs markdown table with file:line references
   - Integrates with grep/ripgrep for fast searching

#### Tasks

- [x] Create DOCUMENTATION_INDEX.md structure
- [x] Audit all docs/ files and categorize by concern
- [x] Extract all 47 specialized terms from existing docs
- [x] Write generate_doc_index.py script
- [x] Write generate_implementation_map.py script
- [x] Generate initial IMPLEMENTATION_LOCATIONS.md
- [x] Manually verify top 20 term mappings
- [x] Add CI job to validate doc index on PR

#### Validation

- [x] All docs/ files listed in index
- [x] All 47 terms have at least one implementation mapping
- [x] Scripts run in <30 seconds
- [ ] No broken internal links in index (74 broken links detected, cleanup needed)

---

### K-2: Concrete Examples (Days 4-6)

**Objective**: Provide real-world, executable examples covering common patterns.

#### Deliverables

1. **workstreams/examples/01_simple_task.json** + **docs/examples/01_simple_task.md**
   - Single-step workstream
   - Basic tool profile usage (Aider)
   - Inline comments explaining each field
   - Expected output and validation steps

2. **workstreams/examples/02_parallel_execution.json** + **docs/examples/02_parallel_execution.md**
   - Multi-step workstream with parallel tasks
   - Demonstrates step dependencies
   - Shows executor pool behavior
   - Performance notes (expected duration)

3. **workstreams/examples/03_error_handling.json** + **docs/examples/03_error_handling.md**
   - Workstream with intentional failure
   - Circuit breaker activation
   - Retry logic demonstration
   - Recovery strategy walkthrough

4. **workstreams/examples/04_multi_phase.json** + **docs/examples/04_multi_phase.md**
   - Complex workstream spanning multiple phases
   - State transitions and checkpointing
   - Archive and resume functionality
   - OpenSpec integration example

5. **workstreams/examples/05_saga_pattern.json** + **docs/examples/05_saga_pattern.md**
   - SAGA pattern with compensation
   - Demonstrates rollback on failure
   - Tool profile compensation actions
   - State machine visualization

6. **config/examples/tool_profile_annotated.yaml**
   - Fully commented tool profile example
   - Explains every configuration option
   - Common patterns (timeout, retry, circuit breaker)
   - Environment variable usage

#### Tasks

- [x] Create workstreams/examples/ directory
- [x] Create docs/examples/ directory
- [x] Write 01_simple_task workstream and guide
- [x] Write 02_parallel_execution workstream and guide
- [x] Write 03_error_handling workstream and guide
- [x] Write 04_multi_phase workstream and guide
- [x] Write 05_saga_pattern workstream and guide
- [x] Create tool_profile_annotated.yaml
- [ ] Validate all examples execute successfully
- [ ] Add examples to test suite (tests/examples/)

#### Validation

- All 5 workstreams pass validation via `validate_workstreams.py`
- Each example executes in <5 minutes on test environment
- Markdown guides include: purpose, setup, execution, expected output, troubleshooting
- Examples referenced in DOCUMENTATION_INDEX.md

---

### K-3: Visual Architecture (Days 7-9)

**Objective**: Create visual diagrams showing architecture, data flow, and state machines.

#### Deliverables

1. **docs/diagrams/SYSTEM_ARCHITECTURE.md**
   - High-level Mermaid diagram of entire system
   - Shows: Core Engine, Error Detection, Specifications, Integrations
   - Data flow between components
   - External dependencies (Git, Aider, etc.)

2. **docs/diagrams/TASK_LIFECYCLE.md**
   - State machine diagram for workstream task execution
   - States: PENDING → IN_PROGRESS → COMPLETED/FAILED/SKIPPED
   - Transition conditions and triggers
   - Retry and circuit breaker integration

3. **docs/diagrams/ERROR_ESCALATION.md**
   - Error detection and escalation flow
   - Plugin architecture visualization
   - Error state machine (DETECTED → ANALYZED → FIXED/IGNORED)
   - Integration with core engine

4. **docs/diagrams/TOOL_SELECTION.md**
   - Decision tree for tool profile selection
   - Profile matching algorithm visualization
   - Timeout and retry configuration flow
   - Fallback chain diagram

5. **docs/diagrams/SPEC_INTEGRATION.md**
   - OpenSpec → Workstream conversion flow
   - Specification resolution and indexing
   - Change proposal workflow
   - Bridge architecture

6. **docs/VISUAL_ARCHITECTURE_GUIDE.md**
   - Index of all diagrams with descriptions
   - Diagram conventions and notation guide
   - How to update diagrams when code changes
   - Auto-validation script documentation

7. **scripts/validate_diagrams.py**
   - Parses Mermaid diagrams from markdown
   - Validates referenced components exist in code
   - Checks for orphaned nodes
   - Warns on outdated state transitions

#### Tasks

- [ ] Create docs/diagrams/ directory
- [ ] Design and create SYSTEM_ARCHITECTURE.md
- [ ] Design and create TASK_LIFECYCLE.md
- [ ] Design and create ERROR_ESCALATION.md
- [ ] Design and create TOOL_SELECTION.md
- [ ] Design and create SPEC_INTEGRATION.md
- [ ] Write VISUAL_ARCHITECTURE_GUIDE.md
- [ ] Write validate_diagrams.py script
- [ ] Run validation and fix any issues
- [ ] Add diagram validation to CI

#### Validation

- All diagrams render correctly in GitHub/VS Code
- validate_diagrams.py reports zero errors
- Each diagram references actual code paths
- VISUAL_ARCHITECTURE_GUIDE.md links to all 5 diagrams
- Diagrams referenced in relevant ADRs and phase plans

---

### K-4: Cross-References (Days 10-12)

**Objective**: Build term relationship graphs and bi-directional reference system.

#### Deliverables

1. **docs/TERM_RELATIONSHIPS.md**
   - Hierarchical graph of all 47 terms
   - Parent-child relationships (e.g., "Workstream" contains "Steps")
   - Dependency relationships (e.g., "Circuit Breaker" depends on "Retry Logic")
   - Usage frequency and context
   - Example:
     ```
     Workstream (core concept)
       ├─ Steps (contains)
       │  ├─ Tool Profile (uses)
       │  └─ Dependencies (references)
       ├─ Bundle (packaged as)
       └─ Orchestrator (executed by)
          ├─ Executor (uses)
          └─ Circuit Breaker (monitors via)
     ```

2. **docs/CROSS_REFERENCE_INDEX.md**
   - Auto-generated bi-directional links
   - For each term: "Used by", "Uses", "Related to"
   - Code references (file:line)
   - Documentation references (section links)
   - Example references (workstream links)

3. **scripts/generate_term_graph.py**
   - Analyzes docs/ and code for term co-occurrence
   - Builds relationship graph (NetworkX or similar)
   - Outputs hierarchical markdown
   - Generates Mermaid relationship diagram

4. **scripts/generate_cross_references.py**
   - Scans all markdown files for term usage
   - Finds code references via AST/grep
   - Builds bi-directional reference map
   - Outputs markdown with backlinks

5. **docs/ADR_DOCUMENTATION_STRUCTURE.md**
   - Architecture Decision Record for doc organization
   - Rationale for index/mapping/examples/diagrams structure
   - Maintenance guidelines
   - CI integration strategy

#### Tasks

- [ ] Identify parent-child relationships for all 47 terms
- [ ] Identify dependency relationships
- [ ] Write generate_term_graph.py script
- [ ] Generate initial TERM_RELATIONSHIPS.md
- [ ] Write generate_cross_references.py script
- [ ] Generate initial CROSS_REFERENCE_INDEX.md
- [ ] Manually verify relationship accuracy for top 20 terms
- [ ] Write ADR_DOCUMENTATION_STRUCTURE.md
- [ ] Add cross-reference generation to CI
- [ ] Update DOCUMENTATION_INDEX.md with new deliverables

#### Validation

- All 47 terms appear in relationship graph
- Each term has at least one relationship
- Cross-reference index includes code and doc links
- Scripts run in <60 seconds
- ADR approved by stakeholders

---

## Implementation Order

1. **Day 1-3**: K-1 Foundation & Index
   - Build navigation and mapping infrastructure
   - Enables faster work in later phases

2. **Day 4-6**: K-2 Concrete Examples
   - Provides practical reference material
   - Examples inform diagram creation

3. **Day 7-9**: K-3 Visual Architecture
   - Diagrams benefit from examples and mappings
   - Visual validation easier with concrete cases

4. **Day 10-12**: K-4 Cross-References
   - Ties everything together
   - Benefits from all previous deliverables

## Integration Points

### With Existing Phases

- **Phase A-J**: All existing documentation updated with cross-references
- **AGENTS.md**: Add section-specific agent instructions for doc updates
- **DIRECTORY_GUIDE.md**: Enhanced with implementation mappings
- **README.md**: Link to DOCUMENTATION_INDEX.md prominently

### With CI Pipeline

- `scripts/bootstrap.ps1`: Include doc validation
- `scripts/test.ps1`: Run diagram and link validation
- GitHub Actions: Auto-generate indices on PR, fail on broken links

### With Error Detection

- Error plugins reference IMPLEMENTATION_LOCATIONS.md
- Error messages include links to relevant docs
- Diagram validation detects missing error states

## Rollout Strategy

### Week 1 (Days 1-3): Foundation

- Create index and mapping scripts
- Generate initial mappings
- Begin manual verification

### Week 2 (Days 4-9): Examples & Diagrams

- Create example workstreams in parallel with diagram work
- Use examples to validate diagrams
- Iterate on clarity and completeness

### Week 3 (Days 10-12): Cross-References & Polish

- Generate cross-references
- Write ADR
- Final validation and CI integration

## Maintenance Plan

### Automated Updates

- **On PR**: Regenerate DOCUMENTATION_INDEX.md, validate links
- **Weekly**: Regenerate IMPLEMENTATION_LOCATIONS.md and CROSS_REFERENCE_INDEX.md
- **Monthly**: Manual audit of relationship graph accuracy

### Manual Updates

- **New term added**: Update TERM_RELATIONSHIPS.md, run generators
- **New example needed**: Follow template in docs/examples/
- **Diagram outdated**: Update diagram, run validate_diagrams.py

### Ownership

- **Tech Lead**: Approve ADRs, review relationship graph
- **Documentation Team**: Maintain examples and guides
- **CI Maintainers**: Keep auto-generation scripts working
- **All Contributors**: Update docs when changing code structure

## Risk Mitigation

### Risk: Documentation becomes outdated

- **Mitigation**: Auto-generation scripts in CI, fail PRs on broken links
- **Fallback**: Weekly audit report, monthly manual review

### Risk: Scripts too slow for CI

- **Mitigation**: Performance budgets (<30s for index, <60s for cross-refs)
- **Fallback**: Cache intermediate results, run on push to main only

### Risk: Term relationships disputed

- **Mitigation**: ADR documents rationale, stakeholder review
- **Fallback**: Community voting process, prioritize most-used terms

### Risk: Examples break due to code changes

- **Mitigation**: Examples in test suite, CI validates execution
- **Fallback**: Automated notifications to example owners

## Future Enhancements (Post-Phase K)

- **Interactive Documentation**: Web-based term explorer with live search
- **AI Training Corpus**: Export structured docs for fine-tuning
- **Video Walkthroughs**: Record example executions with narration
- **Localization**: Translate key documentation to other languages
- **Metrics Dashboard**: Track doc quality and AI agent query success rates

## Definition of Done

- [ ] All K-1 deliverables created and validated
- [ ] All K-2 deliverables created and validated
- [ ] All K-3 deliverables created and validated
- [ ] All K-4 deliverables created and validated
- [ ] All scripts integrated into CI
- [ ] ADR_DOCUMENTATION_STRUCTURE.md approved
- [ ] README.md and DIRECTORY_GUIDE.md updated
- [ ] All 47 terms mapped to implementations
- [ ] Zero broken links in documentation
- [ ] All examples execute successfully
- [ ] All diagrams validate against code
- [ ] AI agent query time <10 seconds for implementation lookups

## Appendix: The 47 Specialized Terms

### Core Engine (12 terms)
1. Workstream
2. Step
3. Bundle
4. Orchestrator
5. Executor
6. Scheduler
7. Tool Profile
8. Circuit Breaker
9. Retry Logic
10. Recovery Strategy
11. Timeout Handling
12. Dependency Resolution

### Error Detection (10 terms)
13. Error Engine
14. Error Plugin
15. Detection Rule
16. Error State Machine
17. Fix Strategy
18. Incremental Detection
19. File Hash Cache
20. Error Escalation
21. Plugin Manifest
22. Error Context

### Specifications (8 terms)
23. OpenSpec
24. Specification Index
25. Spec Resolver
26. Spec Guard
27. Spec Patcher
28. Change Proposal
29. Spec Bridge
30. URI Resolution

### State Management (8 terms)
31. Pipeline Database
32. Worktree Management
33. State Transition
34. Checkpoint
35. Archive
36. CRUD Operations
37. Bundle Loading
38. Sidecar Metadata

### Integrations (9 terms)
39. AIM Bridge
40. CCPM Integration
41. Aider Adapter
42. Git Adapter
43. Test Adapter
44. Tool Registry
45. Profile Matching
46. Compensation Action (SAGA)
47. Rollback Strategy

---

**Next Steps**: Begin K-1 implementation by creating DOCUMENTATION_INDEX.md structure and extracting term list from existing documentation.
