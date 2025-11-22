# Complete Documentation Index

**Purpose:** Comprehensive navigation guide to all Phase K and Phase K+ documentation.

**Last Updated:** 2025-11-22  
**Maintainer:** System Architecture Team

---

## Quick Navigation

- [Getting Started](#getting-started) - New users start here
- [Architecture Decisions](#architecture-decisions-adrs) - Why we made key choices
- [Reference Documentation](#reference-documentation) - Deep technical details
- [Guidelines](#guidelines) - Best practices and patterns
- [Execution & Runtime](#execution--runtime) - How the system actually works
- [Legacy Documentation](#legacy-documentation) - Historical context

---

## Getting Started

**For New Users:**
1. Read [README.md](../README.md) - Project overview
2. Review [QUICK_START.md](../QUICK_START.md) - Get running quickly
3. Check [AGENTS.md](../AGENTS.md) - Repository guidelines

**For AI Agents:**
1. Read [AGENTS.md](../AGENTS.md) - Critical operational rules
2. Review [Anti-Patterns Catalog](guidelines/ANTI_PATTERNS.md) - What NOT to do
3. Check [Change Impact Matrix](reference/CHANGE_IMPACT_MATRIX.md) - What breaks when you change X

---

## Architecture Decisions (ADRs)

**Why we made key technical choices:**

| ADR | Title | Key Decision | Impact |
|-----|-------|-------------|--------|
| [0001](adr/0001-workstream-model-choice.md) | Workstream Model Choice | Use workstreams over task graphs | Core execution model |
| [0002](adr/0002-hybrid-architecture.md) | Hybrid Architecture | GUI + Terminal + TUI support | Execution flexibility |
| [0003](adr/0003-sqlite-state-storage.md) | SQLite State Storage | SQLite for state persistence | No external DB needed |
| [0004](adr/0004-section-based-organization.md) | Section-Based Organization | Organize by domain, not layer | Clearer module boundaries |
| [0005](adr/0005-python-primary-language.md) | Python Primary Language | Python for core, scripts for wrappers | Ecosystem compatibility |
| [0006](adr/0006-specifications-unified-management.md) | Specifications Unified Management | Centralized spec system | Consistent documentation |
| [0007](adr/0007-error-plugin-architecture.md) | Error Plugin Architecture | Plugin-based error detection | Extensible linting |
| [0008](adr/0008-database-location-worktree.md) | Database Location Worktree | Store DB in `.worktrees/` | Worktree isolation |

**See also:** [ADR Index](adr/README.md) - Detailed ADR catalog

---

## Reference Documentation

### Core System References

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Change Impact Matrix](reference/CHANGE_IMPACT_MATRIX.md) | What to update when changing X | Before making any code changes |
| [Error Catalog](reference/ERROR_CATALOG.md) | 25 common errors + recovery | When diagnosing errors |
| [State Machines](reference/STATE_MACHINES.md) | State transition rules | When working with state |
| [Data Flows](reference/DATA_FLOWS.md) | How data moves through system | Understanding system behavior |
| [Dependencies](reference/DEPENDENCIES.md) | Module coupling analysis | Before refactoring |

### Reference Details

**Change Impact Matrix** (10 components, 25+ dependencies)
- Schema changes → what breaks
- Database migrations → ripple effects
- Plugin interface changes → impact
- Tool profile changes → affected code

**Error Catalog** (25 errors across 6 categories)
- Database errors (6): locks, schema, constraints
- Workstream errors (5): dependencies, timeout, conflicts
- Plugin errors (4): manifest, execution, discovery
- Spec errors (3): not found, circular refs
- Tool errors (4): circuit breaker, not found
- Config errors (3): missing files, invalid syntax

**State Machines** (3 documented)
- Workstream states: PENDING → RUNNING → SUCCESS/FAILED
- Step states: PENDING → RUNNING → SUCCESS/FAILED
- Circuit breaker: CLOSED → OPEN → HALF_OPEN

---

## Guidelines

### Development Best Practices

| Document | Purpose | Audience |
|----------|---------|----------|
| [Anti-Patterns Catalog](guidelines/ANTI_PATTERNS.md) | 17 common mistakes to avoid | All developers & AI agents |
| [Testing Strategy](guidelines/TESTING_STRATEGY.md) | Section-specific test patterns | Writing tests |

### Anti-Patterns (17 documented)

**Critical:** Missing migrations, hardcoded paths, network calls in tests  
**High:** Direct DB access, missing plugin manifest, printing secrets  
**Medium:** Non-incremental scanning, god objects, copy-paste duplication

### Testing Strategy

**Section-Specific Patterns:**
- Core State: Use in-memory DB (`:memory:`)
- Core Engine: Mock tool adapters
- Error Plugins: Use `tmp_path` fixture
- Specifications: Mock file system

---

## Execution & Runtime

### How the System Actually Works

| Document | Focus | Use Case |
|----------|-------|----------|
| [Execution Traces Summary](EXECUTION_TRACES_SUMMARY.md) | Runtime behavior | Understanding performance |

### Performance Insights

| Trace | Duration | Bottleneck | Speedup |
|-------|----------|------------|---------|
| Workstream Execution | 1.4s | pytest (88%) | Parallel tests (2-3×) |
| Error Detection | 611ms | Plugins (57%) | **Cache: 9.4×** |
| Spec Resolution | 87ms → 3ms | Markdown parse | **Cache: 29×** |
| State Transitions | 1.3s | Retry wait (79%) | Async retry |
| Tool Adapter | 15s | AI tool (99.9%) | User config |

---

## Documentation by Use Case

### "I want to..."

**...understand a design decision**  
→ Check [ADRs](#architecture-decisions-adrs)

**...fix an error**  
→ Search [Error Catalog](reference/ERROR_CATALOG.md)

**...avoid common mistakes**  
→ Review [Anti-Patterns](guidelines/ANTI_PATTERNS.md)

**...know what breaks if I change X**  
→ Consult [Change Impact Matrix](reference/CHANGE_IMPACT_MATRIX.md)

**...understand how data flows**  
→ Read [Data Flows](reference/DATA_FLOWS.md)

**...write tests for component X**  
→ Follow [Testing Strategy](guidelines/TESTING_STRATEGY.md)

**...understand state transitions**  
→ See [State Machines](reference/STATE_MACHINES.md)

**...know what depends on what**  
→ Check [Dependencies](reference/DEPENDENCIES.md)

**...optimize performance**  
→ Review [Execution Traces](EXECUTION_TRACES_SUMMARY.md)

---

## Phase K+ Completion Summary

### Week 1: Critical Foundations ✅
- 8 ADRs documenting key decisions
- Change Impact Matrix (10 components, 25+ dependencies)
- Anti-Patterns Catalog (17 patterns)

### Week 2: Runtime & Testing ✅
- Execution Traces (5 workflows analyzed)
- Testing Strategy Guide (5 sections)
- Performance insights (9.4×, 29× cache speedups)

### Week 3: Dependencies, Errors, Data ✅
- Error Catalog (25 errors, 6 categories)
- Data Flow Diagrams (3 major flows)
- Dependency Analysis (25+ modules, 0 circular deps)

### Week 4: Final Integration ✅
- State Machine Documentation (3 machines)
- Complete Documentation Index (this file)
- Cross-reference updates

**Total Deliverables:** 20+ files, ~120,000 lines of documentation

---

## Legacy Documentation

**Previous documentation is preserved at:** [DOCUMENTATION_INDEX_OLD.md](DOCUMENTATION_INDEX_OLD.md)

For historical context, see original Phase K documentation including:
- Architecture diagrams
- Workflow documentation
- Component summaries
- OpenSpec bridge

---

## File Locations

```
docs/
├── DOCUMENTATION_INDEX.md      # This file (Phase K+)
├── DOCUMENTATION_INDEX_OLD.md  # Original Phase K index
├── adr/                        # Architecture Decision Records (8 files)
├── reference/                  # Technical reference (5 files)
│   ├── CHANGE_IMPACT_MATRIX.md
│   ├── ERROR_CATALOG.md
│   ├── STATE_MACHINES.md
│   ├── DATA_FLOWS.md
│   └── DEPENDENCIES.md
├── guidelines/                 # Development guidelines (2 files)
│   ├── ANTI_PATTERNS.md
│   └── TESTING_STRATEGY.md
└── EXECUTION_TRACES_SUMMARY.md # Performance traces
```

---

## Maintenance

**Update Triggers:**
- New ADR → Update ADR index and this file
- Major refactoring → Update Change Impact Matrix
- New error pattern → Add to Error Catalog
- Performance change → Update Execution Traces

**Review Schedule:**
- Monthly: Check for broken links
- Quarterly: Review metrics
- Per Phase: Major updates

---

**Last Updated:** 2025-11-22  
**Status:** ✅ Phase K+ Complete  
**Next Review:** 2025-12-22
