# ADR-0004: Section-Based Organization

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need clear code organization that supports multiple concerns (state, orchestration, error detection, integrations) while avoiding monolithic structure

---

## Decision

We will organize code into **domain-driven sections** at the repository root:
- `core/` - State management, orchestration engine, planning
- `error/` - Error detection engine and plugins
- `aim/` - AI environment manager (registry, secrets, health checks)
- `pm/` - Project management and CCPM integrations
- `specifications/` - Unified specification management
- `aider/` - Aider integration and prompt templates
- `openspec/` - OpenSpec proposals before conversion

Supporting infrastructure remains separate:
- `docs/` - Documentation
- `scripts/` - Automation scripts
- `tests/` - Test suites
- `schema/` - JSON/YAML/SQL schemas
- `config/` - Configuration files

---

## Rationale

### Problems with Previous Structure

The old `src/pipeline/` monolithic structure had issues:
- **Unclear boundaries** - Where does "pipeline" end and other systems begin?
- **Tight coupling** - Error detection mixed with orchestration mixed with state
- **Difficult navigation** - AI agents struggled to find relevant code
- **Merge conflicts** - Multiple concerns in single directory caused conflicts

### Section-Based Benefits

1. **Clear Ownership:** Each section has focused responsibility
2. **Independent Evolution:** Sections can change without affecting others
3. **AI Navigation:** Agents use section names to find code (`core.state`, `error.engine`)
4. **Test Organization:** Tests mirror structure (`tests/core/`, `tests/error/`)
5. **Import Clarity:** `from core.state import db` is more semantic than `from src.pipeline.db`

### Domain-Driven Design Influence

Sections align with **bounded contexts** from DDD:
- **core** = Execution context (orchestration, state, planning)
- **error** = Quality context (detection, validation, fixing)
- **aim** = Environment context (tools, secrets, configuration)
- **pm** = Project context (planning, scheduling, tracking)
- **specifications** = Requirements context (specs, indexing, resolution)

---

## Consequences

### Positive

- **Faster Onboarding:** New contributors understand structure quickly
- **Reduced Conflicts:** Teams work in different sections without collisions
- **Clearer Dependencies:** Cross-section imports are explicit and auditable
- **Better AI Understanding:** Agents navigate by semantic meaning, not file paths
- **Modular Testing:** Can test sections in isolation

### Negative

- **Import Path Changes:** Refactor from `src.pipeline` to `core.*`, `error.*`
- **Migration Effort:** Must update all existing imports and tests
- **Initial Confusion:** Existing contributors need to learn new structure

### Neutral

- **Documentation Updates:** All guides must reference new paths
- **CI Path Enforcement:** Need automated checks for deprecated imports

---

## Alternatives Considered

### Alternative 1: Monolithic `src/` Structure

**Description:** Keep everything under `src/pipeline/`

**Rejected because:**
- Doesn't scale as project grows
- Unclear where to add new systems (error detection, PM, specs)
- AI agents struggle with large flat namespaces
- Encourages tight coupling between concerns

### Alternative 2: Microservices Architecture

**Description:** Separate repositories for each concern

**Rejected because:**
- Overkill for current project size
- Deployment complexity (multiple repos, versioning, releases)
- Shared code becomes difficult (duplicated utils, schemas)
- Testing integration becomes harder

### Alternative 3: Feature-Based Structure

**Description:** Organize by feature (e.g., `features/workstream_execution/`, `features/error_detection/`)

**Rejected because:**
- "Feature" is ambiguous and subjective
- Cross-cutting concerns (state, config) don't map to features
- Doesn't align with how users think about the system

### Alternative 4: Layer-Based Structure

**Description:** Organize by technical layer (`api/`, `business/`, `data/`)

**Rejected because:**
- Spreads domain logic across multiple directories
- Harder to understand business capabilities
- Encourages thinking about technology before domain

---

## Related Decisions

- [ADR-0001: Workstream Model Choice](0001-workstream-model-choice.md) - What `core/` orchestrates
- [ADR-0007: Error Plugin Architecture](0007-error-plugin-architecture.md) - How `error/` is organized
- [ADR-0006: Specifications Unified Management](0006-specifications-unified-management.md) - Why `specifications/` exists

---

## References

- **Refactor Mapping:** `docs/SECTION_REFACTOR_MAPPING.md`
- **CI Path Standards:** `docs/CI_PATH_STANDARDS.md`
- **Import Guidelines:** `AGENTS.md` (section-specific instructions)
- **Legacy Code:** `legacy/` (deprecated code for reference)

---

## Notes

### Migration Timeline (Phase E - November 2025)

1. **Phase E-1:** Create new section directories
2. **Phase E-2:** Copy code to new locations (keep old for compatibility)
3. **Phase E-3:** Update all imports to new paths
4. **Phase E-4:** Add CI enforcement to prevent old paths
5. **Phase E-5:** Archive old code to `legacy/`

### Import Path Rules (CI-Enforced)

**✅ Correct:**
```python
from core.state.db import init_db
from error.engine.error_engine import ErrorEngine
from specifications.tools.indexer import generate_index
```

**❌ Deprecated (will fail CI):**
```python
from src.pipeline.db import init_db
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine
from spec.tools.spec_indexer import generate_index
```

### Section Responsibilities

| Section | Responsibility | Key Modules |
|---------|----------------|-------------|
| `core/` | Execution orchestration | `state/`, `engine/`, `planning/` |
| `error/` | Quality assurance | `engine/`, `plugins/` |
| `aim/` | Environment management | `registry/`, `secrets/`, `health/` |
| `pm/` | Project planning | `ccpm/`, `estimator/` |
| `specifications/` | Requirements | `tools/`, `content/`, `bridge/` |

### Future Sections

As project grows, may add:
- `monitoring/` - Observability and metrics
- `deployment/` - Release and deployment automation
- `analytics/` - Data analysis and reporting

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
