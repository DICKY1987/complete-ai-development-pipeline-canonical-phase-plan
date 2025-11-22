# Phase K+: Decision Context Enhancement

**Phase:** K+ (Knowledge Enhancement)  
**Status:** Planning  
**Priority:** Critical  
**Timeline:** 4 weeks  
**Dependencies:** Phase K1-K2 (Documentation Index & Examples)

## Executive Summary

Phase K excels at navigation (WHERE/WHAT) but lacks decision-making context (WHY/WHEN/HOW/WHAT CAN GO WRONG). This phase adds critical decision-support documentation to reduce AI decision time from 5-10 minutes to <2 minutes, wrong decisions from ~20% to <5%, and make breaking changes rare instead of frequent.

## Objectives

1. **Architecture Decision Records (ADRs)** - Document WHY decisions were made
2. **Change Impact Matrix** - Predict ripple effects before coding
3. **Anti-Patterns Catalog** - Document what NOT to do
4. **Runtime Execution Traces** - Show how the system actually works
5. **Testing Strategy Guide** - Proper testing patterns per component
6. **Dependency Graphs** - Code and conceptual dependencies
7. **Error Catalog & Recovery Playbook** - Known errors and fixes
8. **Data Flow Diagrams** - Runtime behavior visualization
9. **Performance Profiles** - Bottlenecks and optimization opportunities
10. **State Machine Catalog** - All valid transitions

## Prerequisites

- ✅ Phase K1 (Documentation Index) - Complete
- ✅ Phase K2 (Examples & Patterns) - Complete
- ✅ Repository stabilization
- ✅ Core documentation structure in `docs/`

## Week-by-Week Plan

### Week 1: Critical Foundations (🔴 CRITICAL)

**Focus:** ADRs, Change Impact Matrix, Anti-Patterns (80% value, 20% effort)

#### Tasks

1. **Architecture Decision Records (ADRs)**
   - Create `docs/adr/` structure with template
   - Document 8 essential ADRs:
     - `0001-workstream-model-choice.md` - Why workstream over task graph
     - `0002-hybrid-architecture.md` - GUI/Terminal/TUI decision
     - `0003-sqlite-state-storage.md` - Why SQLite vs PostgreSQL/Redis
     - `0004-section-based-organization.md` - Why `core/`, `error/`, `aim/` structure
     - `0005-python-primary-language.md` - Python + PowerShell strategy
     - `0006-specifications-unified-management.md` - Spec system design
     - `0007-error-plugin-architecture.md` - Plugin vs monolith
     - `0008-database-location-worktree.md` - Why `.worktrees/pipeline_state.db`
   - Link ADRs from `docs/DOCUMENTATION_INDEX.md`

2. **Change Impact Matrix**
   - Create `docs/reference/CHANGE_IMPACT_MATRIX.md`
   - Document critical dependencies:
     - Schema changes → Regenerate indices
     - `core/state/db.py` → Update tests, migration scripts
     - `schema/` updates → Validate all workstreams
     - `error/plugins/` new plugin → Update manifest, docs
     - `specifications/tools/` → Update spec index
   - Add to Phase K cross-reference system

3. **Anti-Patterns Catalog**
   - Create `docs/guidelines/ANTI_PATTERNS.md`
   - Document by section:
     - **Core State:** Direct file DB access, missing migrations
     - **Error Engine:** Skipping plugin manifest, non-incremental scans
     - **Specifications:** Circular spec dependencies, missing URI resolution
     - **Scripts:** Hardcoded paths, missing error handling
     - **Testing:** Network calls in unit tests, non-deterministic assertions
   - Add examples from historical bugs

#### Deliverables
- [ ] `docs/adr/` with 8 ADRs
- [ ] `docs/adr/template.md` for future ADRs
- [ ] `docs/reference/CHANGE_IMPACT_MATRIX.md`
- [ ] `docs/guidelines/ANTI_PATTERNS.md`
- [ ] Updated `docs/DOCUMENTATION_INDEX.md` with new sections

#### Success Metrics
- ADRs answer "why" for 8 major decisions
- Impact matrix covers 20+ critical dependencies
- Anti-patterns catalog has 15+ documented mistakes

---

### Week 2: Runtime & Testing (🔴 CRITICAL)

**Focus:** Execution traces, testing strategy

#### Tasks

1. **Runtime Execution Traces**
   - Create `docs/architecture/EXECUTION_TRACES.md`
   - Trace 5 key workflows:
     - Workstream execution end-to-end
     - Error detection plugin lifecycle
     - Specification resolution process
     - Database state transitions
     - Tool adapter invocation flow
   - Include timing data, state snapshots, data flow
   - Add sequence diagrams for each trace

2. **Testing Strategy Guide**
   - Create `docs/guidelines/TESTING_STRATEGY.md`
   - Document patterns per section:
     - **Core State:** DB fixture setup, transaction handling
     - **Core Engine:** Mocking tool adapters, step execution
     - **Error Plugins:** Sample file fixtures, hash caching
     - **Specifications:** Mock spec content, resolver testing
   - Add mock/fixture library guide
   - Document test data management

3. **Update Existing Docs**
   - Annotate K2 examples with anti-patterns
   - Link K1 index to ADRs
   - Add execution traces to architecture diagrams

#### Deliverables
- [ ] `docs/architecture/EXECUTION_TRACES.md` with 5 workflows
- [ ] `docs/guidelines/TESTING_STRATEGY.md`
- [ ] Updated `docs/ARCHITECTURE.md` with trace links
- [ ] Sequence diagrams in `docs/diagrams/`

#### Success Metrics
- 5 complete execution traces with timing data
- Testing patterns for all major components
- Reduced test-writing friction

---

### Week 3: Dependencies & Errors (🟠 HIGH VALUE)

**Focus:** Dependency graphs, error catalog, data flows

#### Tasks

1. **Dependency Graphs**
   - Create `docs/architecture/DEPENDENCY_GRAPH.md`
   - Generate code dependency graph:
     - Use `pydeps` or similar for Python dependencies
     - Visualize cross-section imports
     - Highlight circular dependencies (if any)
   - Create conceptual dependency graph:
     - Component interaction map
     - Data ownership boundaries
     - Event flow between sections

2. **Error Catalog & Recovery Playbook**
   - Create `docs/reference/ERROR_CATALOG.md`
   - Document error categories:
     - Database errors (locked, corrupted, missing)
     - Plugin errors (load failure, parse errors)
     - Tool adapter errors (timeout, not found, failure)
     - Specification errors (missing, circular, invalid)
   - Add recovery procedures for each
   - Link to error detection plugins

3. **Data Flow Diagrams**
   - Create `docs/architecture/DATA_FLOWS.md`
   - Diagram runtime data flows:
     - Workstream → DB → Engine → Tools → Results
     - Error detection → Plugin → Engine → Report
     - Spec resolution → Cache → Renderer → Output
   - Show data transformations at each stage
   - Document data validation points

#### Deliverables
- [ ] `docs/architecture/DEPENDENCY_GRAPH.md` with visualizations
- [ ] Generated dependency graphs in `docs/diagrams/`
- [ ] `docs/reference/ERROR_CATALOG.md` with 20+ errors
- [ ] `docs/architecture/DATA_FLOWS.md` with 3+ flows

#### Success Metrics
- Visual dependency graphs for code and concepts
- Recovery procedures for all common errors
- Clear data transformation documentation

---

### Week 4: Performance & State (🟠 HIGH VALUE)

**Focus:** Performance profiles, state machines, integration

#### Tasks

1. **Performance Profiles**
   - Create `docs/architecture/PERFORMANCE_PROFILES.md`
   - Profile critical paths:
     - Workstream execution bottlenecks
     - Database query performance
     - Plugin scan overhead
     - Spec resolution caching
   - Document optimization opportunities
   - Add profiling guide for developers

2. **State Machine Catalog**
   - Create `docs/reference/STATE_MACHINES.md`
   - Document all state machines:
     - Workstream execution states (already in `docs/state_machine.md`)
     - Error detection states
     - Tool adapter states
     - Specification lifecycle states
   - Add valid transition diagrams
   - Document illegal transitions and guards

3. **Integration & Automation**
   - Create automation script: `scripts/validate_decision_context.py`
     - Check ADRs have required sections
     - Validate change impact matrix completeness
     - Verify anti-patterns have examples
   - Update CI to run validation
   - Create developer checklist

4. **Documentation Integration**
   - Update `docs/DOCUMENTATION_INDEX.md` with all new docs
   - Create `docs/guidelines/DECISION_MAKING_GUIDE.md` (meta-guide)
   - Link Phase K documents to decision context
   - Add navigation from AGENTS.md

#### Deliverables
- [ ] `docs/architecture/PERFORMANCE_PROFILES.md`
- [ ] `docs/reference/STATE_MACHINES.md`
- [ ] `scripts/validate_decision_context.py`
- [ ] `docs/guidelines/DECISION_MAKING_GUIDE.md`
- [ ] Updated CI configuration
- [ ] Complete DOCUMENTATION_INDEX update

#### Success Metrics
- Performance bottlenecks identified and documented
- All state machines cataloged with diagrams
- Automated validation in CI
- Complete integration with Phase K

---

## Document Structure Standards

### ADR Template (`docs/adr/template.md`)
```markdown
# ADR-NNNN: [Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [Names]
**Context:** [What triggered this decision]

## Decision
[What we decided]

## Rationale
[Why we decided this]

## Consequences
**Positive:**
- [Benefit 1]

**Negative:**
- [Tradeoff 1]

## Alternatives Considered
- **[Option 1]:** Rejected because...
- **[Option 2]:** Rejected because...

## Related Decisions
- [Links to related ADRs]
```

### Change Impact Entry Format
```markdown
## Component: [Name]

**Triggering Changes:**
- [What changed]

**Mandatory Updates:**
- [ ] [File/system to update]
- [ ] [Test to update]
- [ ] [Doc to update]

**Validation:**
- Run: `[command]`
- Expected: [outcome]
```

### Anti-Pattern Entry Format
```markdown
## [Pattern Name]

**Category:** [Section name]
**Severity:** Critical | High | Medium | Low

**Problem:**
[What the anti-pattern is]

**Example:**
```python
# BAD
[code example]
```

**Why It's Wrong:**
[Explanation]

**Correct Approach:**
```python
# GOOD
[correct code]
```

**Historical Incidents:**
- [Link to commit/issue where this caused problems]
```

## Automation Opportunities

### Week 1
- ADR template generator script
- Change impact matrix validator

### Week 2
- Execution trace collector (decorator-based)
- Test pattern linter

### Week 3
- Dependency graph auto-generator
- Error catalog extractor from code

### Week 4
- Performance profiler integration
- State machine diagram generator

## Success Metrics

### Quantitative
- **Decision Speed:** <2 minutes (from 5-10 minutes)
- **Wrong Decision Rate:** <5% (from ~20%)
- **Breaking Changes:** <1 per month (from frequent)
- **Documentation Coverage:** 100% for critical decisions
- **ADR Count:** 8+ essential ADRs
- **Anti-Pattern Count:** 15+ documented patterns
- **Error Catalog:** 20+ errors with recovery procedures

### Qualitative
- AI can explain WHY decisions were made
- Developers can predict change impacts
- New contributors avoid common mistakes
- Testing friction reduced
- Onboarding time reduced by 50%

## Integration with Phase K

Phase K+ enhances existing K documentation:

| Phase K Item | K+ Enhancement |
|--------------|----------------|
| K-1 (Index) | Links to ADRs, impact matrix |
| K-2 (Examples) | Annotated with anti-patterns |
| K-3 (Diagrams) | Execution traces added |
| K-4 (Cross-refs) | Impact matrix integration |

## Risks & Mitigation

### Risk: Documentation Drift
**Mitigation:** CI validation scripts, regular reviews

### Risk: Overwhelming Detail
**Mitigation:** Focus on high-impact items first (weeks 1-2)

### Risk: Maintenance Burden
**Mitigation:** Automate generation where possible, templates for consistency

## Future Phases

### Phase K++ Candidates
- Interactive decision trees
- AI-assisted ADR generation
- Real-time impact analysis tooling
- Automated trace collection in CI
- Performance regression detection

## References

- Original gap analysis: `C:\Users\richg\TODO_TONIGHT\Phase K Gap Analysis While Phase K.txt`
- Phase K1 completion: `docs/PHASE_K1_COMPLETE.md`
- Phase K2 completion: `docs/PHASE_K2_COMPLETE.md`
- Architecture docs: `docs/ARCHITECTURE.md`
- State machine: `docs/state_machine.md`

## Completion Criteria

- [ ] All Week 1 deliverables complete (ADRs, impact matrix, anti-patterns)
- [ ] All Week 2 deliverables complete (traces, testing strategy)
- [ ] All Week 3 deliverables complete (dependencies, errors, data flows)
- [ ] All Week 4 deliverables complete (performance, state machines, automation)
- [ ] CI validation passing
- [ ] Documentation index updated
- [ ] Success metrics achieved
- [ ] Phase K+ completion document created
