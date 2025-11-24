# ADR Architecture Decisions Patch Analysis

**Patch ID**: 005-adr-architecture-decisions  
**Created**: 2025-11-23T11:23:26.442Z  
**Priority**: HIGH  
**Operations**: 11

---

## Overview

This patch integrates **10 Architecture Decision Records (ADRs)** that document critical architectural choices, their rationale, consequences, and rejected alternatives. ADRs provide essential context for AI agents and developers to understand WHY decisions were made, not just WHAT was implemented.

---

## Source Files (10 ADRs)

### Core System Architecture
1. **ADR-0001: Workstream Model Choice** - Core orchestration pattern
2. **ADR-0002: Hybrid Architecture** - GUI/Terminal/TUI execution modes
3. **ADR-0003: SQLite State Storage** - Persistent state management
4. **ADR-0008: Database Location Worktree** - Where database is stored

### Code Organization
5. **ADR-0004: Section-Based Organization** - Domain-driven directory structure
6. **ADR-0005: Python Primary Language** - Language choice and rationale
7. **ADR-ERROR-UTILS: Error Utilities Location** - Utility placement strategy

### Subsystem Architecture
8. **ADR-0006: Specifications Unified Management** - Spec system consolidation
9. **ADR-0007: Error Plugin Architecture** - Extensible error detection
10. **ADR-SPEC-TOOLING: Spec Tooling Consolidation** - OpenSpec vs SPEC_MGMT_V1

---

## What This Patch Adds

### 1. Architecture Decisions Catalog (`/meta/architecture_decisions`)

**10 fully documented decisions** including:
- **Decision statement** - What was chosen
- **Rationale** - Why it was chosen
- **Key benefits** - What we gain
- **Rejected alternatives** - What we didn't choose and why
- **Implementation references** - Where to find the code
- **Consequences** (positive, negative, neutral)

### 2. Rejected Alternatives Catalog (`/meta/rejected_alternatives_catalog`)

**Comprehensive list of rejected approaches** to prevent AI agents from re-proposing them:
- Task DAG (too low-level)
- Event-driven architecture (non-deterministic)
- PostgreSQL (overkill)
- Monolithic structures (doesn't scale)
- GUI-only / Terminal-only (excludes users)
- And 15+ more...

### 3. Design Principles (`/meta/design_principles`)

**5 categories of principles** extracted from ADRs:
- **Workstream Execution**: Declarative over imperative, composability, idempotency
- **Code Organization**: Clear ownership, independent evolution
- **AI Compatibility**: Semantic meaning, Python preference, documentation-first
- **State Management**: Single source of truth, crash recovery
- **Extensibility**: Plugin isolation, dynamic discovery, clear interfaces

### 4. ADR Compliance Validation (`/validation/adr_compliance`)

**7 compliance checks** to ensure changes respect architectural decisions:
- Workstream model usage (not imperative scripts)
- Section organization (correct placement)
- Import paths (section-based, not deprecated)
- Python version (3.10+ with modern features)
- SQLite location (.worktrees/pipeline_state.db)
- Plugin architecture (new detectors as plugins)
- Spec URI system (spec:// format)

### 5. Patch Metadata (`/meta/patch_metadata/005`)

Tracking information for this patch application.

---

## Key Architectural Insights

### ADR-0001: Workstream Model

**Why workstreams instead of scripts?**
- **Declarative**: Define WHAT, not HOW
- **Trackable**: Every state transition in database
- **Parallel**: Independent workstreams run concurrently
- **Recoverable**: Step-level retry and checkpoints
- **AI-Friendly**: Clear structure for agents to understand

**Rejected**: Task DAG (too low-level), Event-driven (non-deterministic), Scripts (no parallelism), Makefiles (wrong domain)

### ADR-0002: Hybrid Architecture

**Why three UI modes?**
- **GUI**: Visual learners, complex workflows (planned)
- **Terminal**: Power users, CI/CD, scripting (✅ implemented)
- **TUI**: Remote/SSH users, terminal-first (planned)

**Shared Job-Based Engine**:
- Workstreams → Jobs (atomic, retryable, trackable)
- All modes delegate to `engine/`
- Consistent behavior regardless of UI

**Rejected**: GUI-only (excludes automation), Terminal-only (limits users), Web dashboard (deployment complexity)

### ADR-0003: SQLite State Storage

**Why SQLite?**
- **Zero config**: Embedded, no server
- **Cross-platform**: Identical behavior
- **ACID**: Reliable transactions, crash recovery
- **Single-writer model**: Matches our use case
- **Built-in Python support**: sqlite3 module

**Concurrency**: Single-writer (orchestrator), many-readers (UIs), WAL mode for non-blocking reads

**Rejected**: PostgreSQL (server overhead), Redis (less relational), JSON files (no ACID), DuckDB (less mature)

### ADR-0004: Section-Based Organization

**Why sections instead of monolithic src/?**
- **Clear boundaries**: `core/`, `error/`, `aim/`, `pm/`, `specifications/`
- **Domain-driven**: Aligned with bounded contexts
- **AI navigation**: Semantic paths (`core.state`, `error.engine`)
- **Reduced conflicts**: Teams work in different sections

**CI-Enforced Import Paths**:
- ✅ `from core.state.db import init_db`
- ❌ `from src.pipeline.db import init_db` (CI fails)

**Rejected**: Monolithic src/ (doesn't scale), Microservices (overkill), Feature-based (ambiguous), Layer-based (spreads logic)

### ADR-0007: Error Plugin Architecture

**Why plugins?**
- **Extensibility**: Add detectors without core changes
- **Isolation**: Plugin failures don't crash engine
- **Selective loading**: Only load relevant plugins
- **Parallel execution**: Run detectors concurrently
- **Auto-fix capability**: Plugins can fix what they detect

**Plugin Structure**:
```
error/plugins/python_ruff/
├── manifest.json       # Metadata, capabilities
├── plugin.py           # parse() and fix() functions
├── requirements.txt    # Dependencies
└── tests/             # Plugin tests
```

**5 Current Plugins**: ruff, mypy, eslint, gitleaks, codespell

**Rejected**: Monolithic detector (unmaintainable), Tool-specific scripts (duplicate logic), Config-based (limited flexibility)

---

## Impact on Master Plan

### Metadata Enrichment

**Before**: Master plan had technical specs and phase plans  
**After**: Master plan has architectural context explaining WHY decisions were made

### AI Agent Guidance

**Rejected Alternatives Catalog** prevents AI from proposing:
- "Let's use PostgreSQL for state storage" (already rejected, explained why)
- "How about event-driven architecture?" (already rejected, non-deterministic)
- "Let's organize by layers (api/, business/, data/)" (already rejected, spreads logic)

### Compliance Validation

**7 ADR compliance checks** enable automated/manual review:
- Is code in the right section?
- Using correct import paths?
- Following plugin architecture?
- Respecting database location?

### Design Principles

**5 principle categories** guide all development:
- Declarative over imperative
- Clear ownership and boundaries
- AI compatibility first
- Single source of truth
- Plugin-based extensibility

---

## Integration with Existing Patches

### Complements Patch 001 (Config Integration)
- ADRs provide **WHY** for architecture described in CODEBASE_INDEX
- Explains **three-engine problem** decision context
- Documents **section-based organization** rationale

### Complements Patch 002 (Documentation Integration)
- ADRs document **AI tool configuration** decisions
- Explains **sandbox strategy** architectural choices
- Provides context for documentation structure

### Complements Patch 003 (UET V2 Specifications)
- ADRs explain **WHY workstream model** was chosen
- Documents **state machine** decision rationale
- Provides context for **plugin architecture** in error detection

### Complements Patch 004 (Planning Reference)
- ADRs document decisions that drive **phase plan** structure
- Explains **why 148h estimate** is realistic given architecture
- Provides context for **workstream prompt templates**

---

## Validation After Application

### 1. Check ADR Metadata Structure

```python
import json
plan = json.loads(open("UET_V2_MASTER_PLAN.json").read())

# Should have 10 decisions
decisions = plan["meta"]["architecture_decisions"]["decisions"]
assert len(decisions) == 10

# All should have required fields
for adr_id, adr in decisions.items():
    assert "decision" in adr
    assert "status" in adr
    assert "rejected_alternatives" in adr
```

### 2. Verify Rejected Alternatives Catalog

```python
rejected = plan["meta"]["rejected_alternatives_catalog"]

# Should have 8 categories
assert "execution_model" in rejected
assert "state_storage" in rejected
assert "code_organization" in rejected
# ... etc
```

### 3. Validate Design Principles

```python
principles = plan["meta"]["design_principles"]

# Should have 5 categories
assert "workstream_execution" in principles
assert "ai_compatibility" in principles
assert "extensibility" in principles
```

### 4. Check ADR Compliance Validation

```python
compliance = plan["validation"]["adr_compliance"]

# Should have checks
assert "workstream_model" in compliance["checks"]
assert "section_organization" in compliance["checks"]
assert len(compliance["checks"]) >= 7
```

---

## Benefits of This Patch

### 1. Historical Context Preservation

**Problem**: New contributors don't know why decisions were made  
**Solution**: ADRs document context, rationale, and rejected alternatives

### 2. AI Agent Guidance

**Problem**: AI agents propose solutions already rejected  
**Solution**: Rejected alternatives catalog prevents re-proposal

### 3. Architectural Consistency

**Problem**: Changes may violate architectural decisions  
**Solution**: ADR compliance checks enable validation

### 4. Onboarding Acceleration

**Problem**: Understanding codebase takes weeks  
**Solution**: ADRs explain the "why" behind structure

### 5. Design Principle Documentation

**Problem**: Principles exist implicitly, hard to enforce  
**Solution**: Explicit principles extracted and documented

---

## Related Documentation

### ADR Template
- Location: `docs/adr/template.md`
- Provides structure for future ADRs

### ADR Index
- Location: `docs/adr/README.md`
- Lists all 10 ADRs with status and dates

### References in Other Docs
- `CODEBASE_INDEX.yaml` - Section organization (ADR-0004)
- `ai_policies.yaml` - Import path enforcement (ADR-0004)
- `QUALITY_GATE.yaml` - Validation gates (ADR-0003, ADR-0007)

---

## Next Steps After Applying

1. **Review ADR decisions** in master plan
2. **Use rejected alternatives** when AI suggests something
3. **Cite ADRs** in code reviews ("Per ADR-0007, plugins should...")
4. **Update ADRs** when decisions change (new ADR or amendment)
5. **Add compliance checks** to CI (import paths, section placement)

---

## Migration Notes

### No Code Changes Required

ADRs are **documentation only** - no code migrations needed.

### Affects AI Agent Behavior

AI agents should:
- **Check rejected alternatives** before proposing solutions
- **Reference ADRs** when making architectural suggestions
- **Validate against ADR compliance** before submitting changes

### Informs Future ADRs

When making new architectural decisions:
1. Use ADR template (`docs/adr/template.md`)
2. Add to this catalog via patch
3. Update rejected alternatives if applicable
4. Add compliance checks if enforceable

---

## Statistics

| Metric | Value |
|--------|-------|
| **ADRs Documented** | 10 |
| **Rejected Alternatives** | 30+ |
| **Design Principles** | 20+ |
| **Compliance Checks** | 7 |
| **Decision Categories** | Core (4), Organization (3), Subsystems (3) |
| **Implementation References** | 15+ file/module paths |
| **Status** | All Accepted (2025-11-18 to 2025-11-22) |

---

## Summary

This patch adds **critical architectural context** to the master plan by integrating 10 ADRs. It:

✅ **Documents WHY** decisions were made (not just WHAT)  
✅ **Prevents re-proposal** of rejected alternatives  
✅ **Extracts design principles** for consistent development  
✅ **Enables compliance validation** for architectural integrity  
✅ **Accelerates onboarding** with decision context

**Priority**: HIGH - Essential for AI agent understanding and architectural consistency

**Impact**: Metadata enrichment only - no breaking changes

**Ready to apply**: Yes - validation logic included
