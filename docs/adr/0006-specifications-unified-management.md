# ADR-0006: Specifications Unified Management

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need centralized, discoverable system for managing all project specifications, requirements, and design documents

---

## Decision

We will consolidate all specifications into a **unified `specifications/` section** with:
- `content/` - Specification documents organized by domain
- `tools/` - Processing utilities (indexer, resolver, guard, patcher, renderer)
- `changes/` - Active OpenSpec change proposals
- `bridge/` - OpenSpec → Workstream integration layer

---

## Rationale

### Problems with Scattered Specs

Previously, specifications were spread across:
- `openspec/` - Some specs
- `docs/spec/` - Other specs  
- `docs/` root - ADRs and design docs
- `meta/` - Planning documents
- Individual section READMEs

This caused:
- **Duplication:** Same concepts documented in multiple places
- **Discovery Issues:** Hard to find "the spec" for a feature
- **Versioning Chaos:** No clear source of truth
- **Broken Links:** Cross-references frequently broke
- **Tool Integration:** Each tool parsed specs differently

### Unified System Benefits

1. **Single Source of Truth:** One place for all specifications
2. **Tooling Integration:** Consistent format enables automation
3. **URI Resolution:** Specs reference each other via URIs (`spec://core/state/db`)
4. **Discoverability:** AI agents know where to find specifications
5. **Change Management:** `changes/` directory tracks proposals before acceptance
6. **Bridge Pattern:** Clear path from OpenSpec proposals → workstream execution

---

## Consequences

### Positive

- **Reduced Duplication:** Consolidation eliminates redundant docs
- **Better Navigation:** Hierarchical organization (`content/core/`, `content/error/`)
- **Automation-Friendly:** Tools can generate indices, validate references
- **Version Control:** All specs in one tree, easier to track changes
- **AI Understanding:** Clear structure helps agents find relevant specs

### Negative

- **Migration Effort:** Must move existing specs to new structure
- **Learning Curve:** Contributors must understand spec URI system
- **Tool Dependencies:** Some automation requires spec tooling to work

### Neutral

- **Maintenance Overhead:** Spec index must be regenerated when specs change
- **Governance Needed:** Process for proposing and accepting spec changes

---

## Alternatives Considered

### Alternative 1: Keep Specs in Each Section

**Description:** Store specs next to code (`core/specs/`, `error/specs/`)

**Pros:**
- Locality - specs close to implementation
- Section independence

**Rejected because:**
- Cross-section specs don't fit (where does "workstream" spec go?)
- Difficult to get project-wide view of specifications
- Tooling must scan entire tree to find all specs

### Alternative 2: Wiki or External System

**Description:** Use GitHub Wiki, Confluence, or Notion for specs

**Pros:**
- Rich editing features
- Collaboration tools
- Search capabilities

**Rejected because:**
- Specs separated from code version control
- No offline access
- Difficult to reference from code
- External dependencies for critical documentation

### Alternative 3: README-Only Documentation

**Description:** Put all specs in README.md files throughout tree

**Pros:**
- Simple, no special tooling
- GitHub renders nicely

**Rejected because:**
- Hard to enforce structure
- No cross-referencing capabilities
- Difficult to generate indices
- READMEs serve different purpose (getting started, not formal specs)

---

## Related Decisions

- [ADR-0004: Section-Based Organization](0004-section-based-organization.md) - Where `specifications/` fits
- [Phase K+ Plan](../../meta/plans/phase-K-plus-decision-context.md) - Documentation enhancement

---

## References

- **Specification Content:** `specifications/content/`
- **Spec Tooling:** `specifications/tools/`
  - `indexer/` - Generates spec index
  - `resolver/` - Resolves spec URIs
  - `guard/` - Validates spec references
  - `patcher/` - Applies spec patches
  - `renderer/` - Renders specs to different formats
- **OpenSpec Bridge:** `specifications/bridge/` - Converts OpenSpec → Workstreams
- **Change Proposals:** `specifications/changes/` - Active proposals

---

## Notes

### Specification URI System

Specs reference each other using URIs:

```markdown
See [Database State](spec://core/state/db#initialization) for details.
```

The resolver:
1. Parses `spec://core/state/db`
2. Resolves to `specifications/content/core/state/db.md`
3. Finds anchor `#initialization`
4. Returns resolved path or content

### Spec Content Organization

```
specifications/
├── content/
│   ├── core/
│   │   ├── state/
│   │   │   ├── db.md
│   │   │   └── migrations.md
│   │   ├── engine/
│   │   │   ├── orchestrator.md
│   │   │   └── scheduler.md
│   │   └── planning/
│   ├── error/
│   │   ├── engine.md
│   │   └── plugins/
│   ├── aim/
│   ├── pm/
│   └── specifications/
│       └── spec-system.md (meta-spec)
```

### OpenSpec Bridge

OpenSpec proposals in `openspec/` are:
1. Reviewed and discussed
2. Converted to specifications via `bridge/`
3. Moved to `specifications/content/` when accepted
4. Transformed into workstreams for implementation

### Spec Validation

The `guard` tool validates:
- All spec URIs resolve to real files
- No circular dependencies
- Required sections present (for formal specs)
- Code references are accurate

Run with:
```bash
python specifications/tools/guard/guard.py --validate-all
```

### Spec Index Generation

Auto-generated index at `specifications/INDEX.md`:
```bash
python specifications/tools/indexer/indexer.py
```

Shows:
- All specs hierarchically
- Cross-references between specs
- Implementation status (planned/in-progress/complete)

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
