# AI Navigation Enhancement v2 - Workstream Summary

**Phase**: PH-AI-NAV-002  
**Total Workstreams**: 12  
**Parallelization**: ~60% of work can run concurrently

---

## Quick Reference

| ID | Name | Hours | Dependencies | Parallel? |
|----|------|-------|--------------|-----------|
| WS-001 | Root AI Context | 2-3h | None | ✅ |
| WS-002 | Core Module Manifests | 4-5h | None | ✅ |
| WS-003 | Deprecated Cleanup | 2-3h | None | ✅ |
| WS-004 | Entry Points Doc | 2-3h | None | ✅ |
| WS-005 | Nav Consolidation | 3-4h | WS-001 | ⚠️ |
| WS-006 | All Module Manifests | 6-8h | WS-002 template | ✅ |
| WS-007 | README Standardization | 4-5h | WS-002, WS-006 | ⚠️ |
| WS-008 | Root Cleanup | 3-4h | None | ✅ |
| WS-009 | Dependency Visualization | 2-3h | None | ✅ |
| WS-010 | Code Signposts | 5-6h | None | ✅ |
| WS-011 | AI Testing | 3-4h | All above | ⚠️ |
| WS-012 | Doc Index Updates | 2-3h | All above | ⚠️ |

---

## Phase 1: Foundation (Week 1) - All Independent

### **WS-001: Root AI Context & Quick Reference**
**Deliverables**:
- `.ai-context.md` - Single-page repo overview for AI tools
- `NAVIGATION.md` - Unified navigation hub

**Key Features**:
- 30-second repo understanding
- Answers top 5 AI confusion points
- Clear entry points
- Common pitfalls documented

**Acceptance**: Can AI answer "What does this repo do?" in <30 seconds

---

### **WS-002: Module Manifests (Core Modules)**
**Deliverables**:
- `.ai-module-manifest` in 6 core modules:
  - `core/`
  - `core/state/`
  - `core/engine/`
  - `error/`
  - `error/engine/`
  - `specifications/`

**Manifest Contents**:
```yaml
module: "core.state"
purpose: "<one-liner>"
layer: "infra|domain|api|ui"
entry_points:
  - file: "db.py"
    function: "init_db()"
key_patterns: [...]
common_tasks: [...]
gotchas: [...]
deprecated: [...]
```

**Acceptance**: AI can understand module without reading code

---

### **WS-003: Deprecated Code Cleanup**
**Deliverables**:
- `legacy/DEPRECATED.md` - Clear deprecation notice
- Rename `legacy/` → `_archive_deprecated/`
- Update `.aiignore`
- Add deprecation warnings to old code

**Acceptance**: AI never suggests deprecated imports

---

### **WS-004: Entry Points Documentation**
**Deliverables**:
- `ENTRY_POINTS.md` - All CLI/API entry points

**Contents**:
- Command → File → Function mapping
- Code path tracing
- Python API examples
- Testing entry points

**Acceptance**: AI can suggest correct command for any task

---

## Phase 2: Consolidation (Week 2)

### **WS-005: Navigation Document Consolidation** (Depends: WS-001)
**Actions**:
- Merge `DIRECTORY_GUIDE.md` into `NAVIGATION.md`
- Archive `MASTER_NAVIGATION_INDEX.md`
- Update all cross-references
- Keep focused indexes (API, EXECUTION, DEPENDENCY)

**Goal**: Reduce from 6+ nav docs to 1 primary + 3 focused

**Acceptance**: Any code findable in ≤2 navigation hops

---

### **WS-006: Module Manifests (All Remaining)** (Depends: WS-002 for template)
**Deliverables**:
- `.ai-module-manifest` in 11 more modules:
  - `aim/`, `pm/`, `engine/`, `gui/`
  - `scripts/`, `tests/`, `infra/`
  - `schema/`, `config/`
  - `specifications/tools/`, `specifications/bridge/`

**Total Coverage**: 17 modules (100%)

**Acceptance**: Every module has manifest

---

### **WS-007: README Hierarchy Standardization** (Depends: WS-002, WS-006)
**Actions**:
- Create missing module READMEs
- Standardize structure across all READMEs
- Link to manifests
- Update stale information

**Template Sections**:
- Overview, Key Components, Usage
- Architecture, Dependencies, Common Tasks
- Testing, Documentation, Status

**Acceptance**: All READMEs follow template, link to manifests

---

### **WS-008: Root Directory Reorganization** (Independent)
**Actions**:
- Move loose `.txt` files → `docs/notes/` or `devdocs/notes/`
- Move configs → `.config/`
- Move brainstorms → `devdocs/brainstorms/`
- Update tool config paths

**Goal**: Reduce root from 78 → <40 items

**Acceptance**: Root is clean, organized, navigable

---

## Phase 3: Enhancement (Week 3)

### **WS-009: Dependency Visualization** (Independent)
**Deliverables**:
- `docs/diagrams/DEPENDENCY_GRAPH.mmd` - Mermaid diagram
- `docs/diagrams/MODULE_LAYERS.mmd` - Layer visualization
- Update `DEPENDENCY_INDEX.md` with diagrams

**Features**:
- Visual module dependencies
- Color-coded layers (infra/domain/api/ui)
- Renders on GitHub

**Acceptance**: Diagrams render correctly, match CODEBASE_INDEX.yaml

---

### **WS-010: Code Signpost Comments** (Independent)
**Actions**:
- Add 20-30 strategic comments to key files
- Use AI-readable markers:
  - `# ENTRY_POINT:`
  - `# INVARIANT:`
  - `# EDGE_CASE:`
  - `# DEPRECATED:`
  - `# ALGORITHM:`

**Priority Files**:
- `core/orchestrator.py`
- `core/state/db.py`
- `core/state/dag_utils.py`
- `core/engine/scheduler.py`
- `error/engine/error_engine.py`

**Acceptance**: Entry points marked, invariants documented, no obvious comments

---

### **WS-011: AI Navigation Testing & Validation** (Depends: All previous)
**Deliverables**:
- `devdocs/testing/ai_navigation_tests.md` - Test suite
- Results report from 3 AI tools

**Test Scenarios** (8 tests):
1. Quick orientation (<30s)
2. Find entry point (<10s)
3. Understand module (<60s)
4. Avoid deprecated (100% accuracy)
5. Find specific code (<20s)
6. Navigate by task (<15s)
7. Understand dependencies (<30s)
8. Module relationships (<45s)

**Acceptance**: ≥85% pass rate across all AI tools

---

### **WS-012: Documentation Index Updates** (Depends: All previous)
**Actions**:
- Update `CODEBASE_INDEX.yaml`
- Update `docs/DOCUMENTATION_INDEX.md`
- Update `README.md`
- Update all module READMEs
- Update `.github/copilot-instructions.md`

**Goal**: Ensure all indexes reflect new navigation structure

**Acceptance**: No broken links, consistent cross-references

---

## Execution Strategy

### **Week 1: Parallel Execution**
```
Developer A: WS-001 (2-3h) + WS-004 (2-3h) = 4-6h
Developer B: WS-002 (4-5h) = 4-5h  
Developer C: WS-003 (2-3h) = 2-3h

Total: 10-14h (parallelized) vs 12-15h (sequential)
```

### **Week 2: Partial Parallel**
```
Developer A: WS-005 (3-4h) [after WS-001]
Developer B: WS-006 (6-8h) [after WS-002]
Developer C: WS-008 (3-4h) [anytime]

Then all: WS-007 (4-5h) [after WS-006]

Total: 16-21h (parallelized) vs 15-18h (sequential)
```

### **Week 3: Sequential Finale**
```
Parallel:
Developer A: WS-009 (2-3h)
Developer B: WS-010 (5-6h)

Sequential:
Developer A: WS-011 (3-4h) [after all]
Developer A: WS-012 (2-3h) [after all]

Total: 12-16h (parallelized) vs 13-17h (sequential)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Navigation consolidation breaks links | Comprehensive link validation script |
| README standardization time-consuming | Use templates, parallelize per module |
| AI testing subjective | Use consistent test scripts, multiple tools |
| Manifest format inconsistency | Strict template, validation script |

---

## Success Metrics

### Phase 1
- [ ] AI orientation time reduced to <30s (baseline: 5-10 min)
- [ ] 6 core modules have manifests
- [ ] 100% deprecated paths flagged
- [ ] All entry points documented

### Phase 2
- [ ] Navigation hops ≤2 (baseline: 4-5)
- [ ] 100% module manifest coverage
- [ ] 100% modules have READMEs
- [ ] Root <40 items (baseline: 78)

### Phase 3
- [ ] Dependency graph visualized
- [ ] 20-30 strategic comments added
- [ ] AI tests ≥85% pass rate
- [ ] All indexes updated

---

## File Inventory

### To Create (22 files)
- `.ai-context.md`
- `NAVIGATION.md`
- `ENTRY_POINTS.md`
- `legacy/DEPRECATED.md`
- `.ai-module-manifest` ×17
- `docs/diagrams/DEPENDENCY_GRAPH.mmd`
- `docs/diagrams/MODULE_LAYERS.mmd`
- `docs/notes/README.md`
- `devdocs/testing/ai_navigation_tests.md`

### To Update (15+ files)
- `.aiignore`
- `README.md`
- `CODEBASE_INDEX.yaml`
- `docs/DOCUMENTATION_INDEX.md`
- `DEPENDENCY_INDEX.md`
- Module READMEs ×11+
- `.github/copilot-instructions.md`

### To Move (15+ files)
- Text files → `docs/notes/` or `devdocs/notes/`
- Configs → `.config/`
- Nav docs → `docs/archive/navigation/`

### To Rename
- `legacy/` → `_archive_deprecated/`

---

**Next**: See individual workstream specifications for detailed implementation steps.
