---
doc_id: DOC-DIAGRAMS-README-001
created: 2025-12-05T07:45:00Z
purpose: Organization and guidance for visual documentation
---

# 📊 Visual Documentation Structure

**Location**: `docs/diagrams/`
**Tool**: draw.io (diagrams.net)
**Executable**: `C:\Users\richg\draw.io\draw.io.exe`
**Symbol Reference**: [FLOWCHART_SYMBOLS_REFERENCE.md](../reference/FLOWCHART_SYMBOLS_REFERENCE.md)

---

## 📁 Folder Structure

```
docs/diagrams/
├── README.md                    ← This file
├── DIAGRAM_CREATION_GUIDE.md    ← Step-by-step guide
├── source/                      ← Editable .drawio files
│   ├── architecture/
│   ├── phases/
│   ├── data-flow/
│   └── components/
├── exports/                     ← Generated images
│   ├── png/                     ← For documentation embedding
│   └── svg/                     ← Scalable vector graphics
└── templates/                   ← Reusable templates
    ├── flowchart-template.drawio
    ├── phase-template.drawio
    └── architecture-template.drawio
```

---

## 🎯 Diagram Organization

### **1. Architecture Diagrams** (`source/architecture/`)

**Purpose**: Show system structure and relationships

| Diagram | File | Priority | Status |
|---------|------|----------|--------|
| 4-Layer Architecture | `architecture-layers.drawio` | HIGH | ⏳ Planned |
| Module Dependency Graph | `module-dependencies.drawio` | MEDIUM | ⏳ Planned |
| Component Interaction | `component-interactions.drawio` | LOW | ⏳ Planned |
| Adapter Registry | `adapter-registry.drawio` | MEDIUM | ⏳ Planned |

**Symbols Used**:
- Rectangles (processes/modules)
- Cylinders (databases)
- Subroutine boxes (components)
- Arrows (dependencies)

---

### **2. Phase Flow Diagrams** (`source/phases/`)

**Purpose**: Detailed process flow for each of 8 phases

| Phase | File | Priority | Status |
|-------|------|----------|--------|
| Phase 0: Bootstrap | `phase-0-bootstrap.drawio` | HIGH | ⏳ Planned |
| Phase 1: Planning | `phase-1-planning.drawio` | HIGH | ⏳ Planned |
| Phase 2: Request Building | `phase-2-request-building.drawio` | HIGH | ⏳ Planned |
| Phase 3: Scheduling | `phase-3-scheduling.drawio` | MEDIUM | ⏳ Planned |
| Phase 4: Routing | `phase-4-routing.drawio` | MEDIUM | ⏳ Planned |
| Phase 5: Execution | `phase-5-execution.drawio` | HIGH | ⏳ Planned |
| Phase 6: Error Analysis | `phase-6-error-analysis.drawio` | MEDIUM | ⏳ Planned |
| Phase 7: Monitoring | `phase-7-monitoring.drawio` | LOW | ⏳ Planned |
| Phase 8: Completion | `phase-8-completion.drawio` | LOW | ⏳ Planned |
| **E2E Complete Flow** | `end-to-end-complete.drawio` | **CRITICAL** | ⏳ Planned |

**Symbols Used**:
- Ovals (start/end)
- Rectangles (processes)
- Diamonds (decisions)
- Documents (files)
- Cylinders (databases)

---

### **3. Data Flow Diagrams** (`source/data-flow/`)

**Purpose**: Show data transformation and movement

| Diagram | File | Priority | Status |
|---------|------|----------|--------|
| Artifact Lifecycle | `artifact-lifecycle.drawio` | HIGH | ⏳ Planned |
| State Transitions | `state-transitions.drawio` | MEDIUM | ⏳ Planned |
| Database Flow | `database-flow.drawio` | MEDIUM | ⏳ Planned |
| Schema Validation Flow | `schema-validation.drawio` | LOW | ⏳ Planned |
| Error Detection Flow | `error-detection.drawio` | MEDIUM | ⏳ Planned |

**Symbols Used**:
- Parallelograms (data input/output)
- Cylinders (storage)
- Documents (artifacts)
- Arrows with labels (transformations)

---

### **4. Component Diagrams** (`source/components/`)

**Purpose**: Internal workings of key components

| Diagram | File | Priority | Status |
|---------|------|----------|--------|
| Orchestrator Engine | `orchestrator-engine.drawio` | HIGH | ⏳ Planned |
| Scheduler Logic | `scheduler-logic.drawio` | MEDIUM | ⏳ Planned |
| Circuit Breaker Pattern | `circuit-breaker.drawio` | MEDIUM | ⏳ Planned |
| Retry Mechanism | `retry-mechanism.drawio` | LOW | ⏳ Planned |
| Error Plugin System | `error-plugin-system.drawio` | MEDIUM | ⏳ Planned |
| State Machine | `state-machine.drawio` | HIGH | ⏳ Planned |

**Symbols Used**:
- Subroutine boxes (modules)
- Decisions (logic branches)
- Delays (timeouts)
- Loop limits (retry counts)

---

## 🎨 Design Standards

### **Color Palette** (from E2E_PROCESS_VISUAL_DIAGRAM.md)

Apply consistently across all diagrams:

| Color | Hex Code | Usage |
|-------|----------|-------|
| Blue | `#e1f5ff` | Data/Storage (plans, state, profiles, databases) |
| Yellow | `#fff3cd` | Engines/Logic (core/engine, bootstrap, adapters) |
| Green | `#d4edda` | Validation (schema, success states) |
| Purple | `#e8d4f8` | UI/Display (gui, textual, rich) |
| Red | `#f8d7da` | Critical/Output (errors, state transitions, artifacts) |
| Orange | `#ffd4e5` | Support/Plugins (AIM, error plugins, PM) |
| Gray | `#f0f0f0` | External (user, manual steps) |

### **Typography**

- **Font**: Arial or Helvetica
- **Size**:
  - Titles: 14pt bold
  - Node labels: 11pt
  - Edge labels: 9pt
- **Alignment**: Center for nodes, left for descriptions

### **Layout**

- **Flow Direction**: Top-to-bottom (TB) or Left-to-right (LR)
- **Spacing**: Consistent 40px between nodes
- **Arrow Style**: Smooth curves, labeled connections
- **Grouping**: Use swimlanes or subgraphs for phases

---

## 🔧 Workflow

### **Creating a New Diagram**

1. **Open draw.io**
   ```powershell
   & "C:\Users\richg\draw.io\draw.io.exe"
   ```

2. **Use template** (if available)
   - File → Open → `docs/diagrams/templates/`
   - Select appropriate template
   - Save As → `source/{category}/{diagram-name}.drawio`

3. **Apply standards**
   - Use symbols from [FLOWCHART_SYMBOLS_REFERENCE.md](../reference/FLOWCHART_SYMBOLS_REFERENCE.md)
   - Apply color palette
   - Use consistent typography

4. **Export for documentation**
   - File → Export As → PNG
   - Save to: `exports/png/{diagram-name}.png`
   - Resolution: 300 DPI (for print) or 150 DPI (for web)
   - Optional: Export SVG to `exports/svg/`

5. **Update status**
   - Mark diagram as ✅ Complete in this README
   - Reference in relevant documentation

---

## 📝 Naming Conventions

### **Source Files** (`.drawio`)
```
{category}-{specific-name}.drawio

Examples:
- architecture-layers.drawio
- phase-0-bootstrap.drawio
- data-flow-artifact-lifecycle.drawio
- component-orchestrator-engine.drawio
```

### **Export Files** (`.png`, `.svg`)
```
{same-name-as-source}.{extension}

Examples:
- architecture-layers.png
- phase-0-bootstrap.png
- phase-0-bootstrap.svg
```

---

## 📖 Usage in Documentation

### **Embedding in Markdown**

```markdown
## Architecture Overview

![4-Layer Architecture](diagrams/exports/png/architecture-layers.png)

*Figure 1: Complete pipeline architecture showing Foundation → State → Domain → Orchestration layers*

[Edit Source](diagrams/source/architecture/architecture-layers.drawio)
```

### **Linking from Specs**

```markdown
See [Phase 0 Bootstrap Flow](../diagrams/exports/png/phase-0-bootstrap.png) for visual process.
```

---

## ✅ Quality Checklist

Before marking a diagram as complete:

- [ ] Uses standard symbols from FLOWCHART_SYMBOLS_REFERENCE.md
- [ ] Applies correct color palette
- [ ] All nodes are labeled clearly
- [ ] All decision branches are labeled (Yes/No, Success/Fail)
- [ ] Flow direction is consistent
- [ ] Legend included (if using custom symbols)
- [ ] Exported to PNG (150+ DPI)
- [ ] Source file saved to appropriate category
- [ ] Referenced in relevant documentation
- [ ] Peer reviewed for accuracy

---

## 🔗 Related Documentation

- [FLOWCHART_SYMBOLS_REFERENCE.md](../reference/FLOWCHART_SYMBOLS_REFERENCE.md) - Standard symbols
- [E2E_PROCESS_VISUAL_DIAGRAM.md](../E2E_PROCESS_VISUAL_DIAGRAM.md) - Mermaid-based flow (reference for draw.io versions)
- [DIAGRAM_CREATION_GUIDE.md](DIAGRAM_CREATION_GUIDE.md) - Step-by-step creation guide

---

## 📊 Progress Tracking

| Category | Total | Complete | In Progress | Planned |
|----------|-------|----------|-------------|---------|
| Architecture | 4 | 0 | 0 | 4 |
| Phases | 10 | 0 | 0 | 10 |
| Data Flow | 5 | 0 | 0 | 5 |
| Components | 6 | 0 | 0 | 6 |
| **TOTAL** | **25** | **0** | **0** | **25** |

**Target Completion**: TBD
**Priority Focus**: E2E Complete Flow, Phase 0-2, Architecture Layers

---

**Maintained By**: Documentation Team
**Last Updated**: 2025-12-05
**Version**: 1.0
