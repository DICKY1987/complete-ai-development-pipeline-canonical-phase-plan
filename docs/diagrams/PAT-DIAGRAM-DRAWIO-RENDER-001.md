---
pattern_id: PAT-DIAGRAM-DRAWIO-RENDER-001
title: AI-Generated Diagram Automation with draw.io CLI
category: Automation
created: 2025-12-05
status: Active
---

# Pattern: AI-Generated Diagram Automation with draw.io CLI

**Pattern ID**: PAT-DIAGRAM-DRAWIO-RENDER-001
**Category**: Automation / Documentation
**Status**: ✅ Active

---

## 🎯 Problem Statement

AI agents (Claude Code, Codex, Copilot) cannot directly manipulate GUI applications like draw.io Desktop. However, we need to:

1. Generate architecture and process flow diagrams programmatically
2. Keep diagrams version-controlled and reproducible
3. Export diagrams to PNG/PDF/SVG for documentation embedding
4. Integrate diagram generation into the automated pipeline

**Anti-pattern**: Manually creating diagrams in GUI → Screenshots → Manual updates

---

## 💡 Solution Pattern

**Two-phase approach**:

### **Phase 1: AI generates diagram source**
- AI tools (Claude/Codex/Copilot) generate `.drawio` XML or SVG files
- Source files are version-controlled in `docs/diagrams/source/`
- Changes tracked via git diffs

### **Phase 2: Automated rendering**
- draw.io CLI (headless) exports diagrams to PNG/PDF/SVG
- Triggered automatically via orchestrator or manual script
- Outputs stored in `docs/diagrams/exports/`

**Key insight**: AI doesn't "draw boxes" — it generates **data files** that draw.io CLI renders.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Phase 1: AI Generation                                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Architecture Description / Phase Plan (JSON/YAML)      │
│                    ↓                                     │
│  AI Agent (Claude Code / Codex / Copilot)               │
│                    ↓                                     │
│  diagram_source.drawio (XML) or diagram.svg             │
│                    ↓                                     │
│  Saved to: docs/diagrams/source/{category}/              │
│                                                          │
└──────────────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2: Automated Rendering                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  scripts/render_diagrams.ps1                             │
│                    ↓                                     │
│  C:\Tools\drawio-cli.ps1 (wrapper)                      │
│                    ↓                                     │
│  draw.io.exe -x -f png --output ... (headless)          │
│                    ↓                                     │
│  diagram.png / diagram.pdf                               │
│                    ↓                                     │
│  Saved to: docs/diagrams/exports/{format}/               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
docs/diagrams/
├── source/                      ← Version-controlled .drawio files
│   ├── architecture/
│   ├── phases/
│   ├── data-flow/
│   └── components/
├── exports/                     ← Generated images (git-ignored)
│   ├── png/
│   ├── pdf/
│   └── svg/
└── templates/                   ← Reusable templates for AI

scripts/
└── render_diagrams.ps1          ← Automated rendering script

C:\Tools\
└── drawio-cli.ps1               ← CLI wrapper (system-wide)
```

---

## 🔧 Components

### **1. draw.io CLI Wrapper** (`C:\Tools\drawio-cli.ps1`)

**Purpose**: Consistent interface to draw.io CLI across all scripts.

**Parameters**:
- `-InputPath` - Source .drawio or .svg file
- `-OutputPath` - Target output file
- `-Format` - Export format (png, pdf, svg)
- `-Export` - Enable export mode
- `-ExtraArgs` - Additional CLI arguments (e.g., "--scale 2.5")

**Example**:
```powershell
pwsh -File C:\Tools\drawio-cli.ps1 -Export `
  -Format png `
  -InputPath .\diagram.drawio `
  -OutputPath .\diagram.png `
  -ExtraArgs "--scale 2.5"
```

---

### **2. Diagram Rendering Script** (`scripts/render_diagrams.ps1`)

**Purpose**: Batch-process all diagrams in source/ to exports/.

**Features**:
- Scans `docs/diagrams/source/` recursively for `.drawio` files
- Exports to multiple formats (png, pdf, svg)
- Maintains directory structure in exports/
- Configurable scale factor
- Exit non-zero on failures

**Usage**:
```powershell
# Default: PNG export at 2.5x scale
.\scripts\render_diagrams.ps1

# Multiple formats
.\scripts\render_diagrams.ps1 -Format "png,pdf,svg"

# High-resolution export
.\scripts\render_diagrams.ps1 -Scale 3.0
```

---

### **3. AI Agent Instructions**

**For Claude Code / Codex / Copilot**:

When generating diagrams, follow this pattern:

#### **Step 1: Generate .drawio XML**

Prompt template:
```
Generate a .drawio XML file representing this architecture:

- Modules: [list from master_plan.json]
- Layers: Foundation → State → Domain → Orchestration
- Color scheme:
  - Blue (#e1f5ff) for data/storage
  - Yellow (#fff3cd) for engines
  - Green (#d4edda) for validation
  - Red (#f8d7da) for critical paths

Output valid draw.io XML (mxGraphModel format).
Save to: docs/diagrams/source/architecture/architecture-layers.drawio
```

#### **Step 2: Update render script**

If adding new diagram, ensure `render_diagrams.ps1` will process it (it auto-scans, so usually no changes needed).

#### **Step 3: Trigger rendering**

Add to orchestrator or manual execution:
```powershell
.\scripts\render_diagrams.ps1 -Format "png,pdf"
```

---

## 📝 Example Workflow

### **Scenario: Generate Phase 0 Bootstrap Diagram**

#### **1. AI Generation (Claude Code)**

Prompt:
```
Create a flowchart diagram for Phase 0: Bootstrap & Initialization.

Process flow:
1. User: New Project (start - oval, gray #f0f0f0)
2. core/bootstrap/orchestrator.py (process - rectangle, yellow #fff3cd)
3. profiles/Select Profile (data - cylinder, blue #e1f5ff)
4. core/bootstrap/discovery.py (process - rectangle, yellow)
5. schema/Validate (process - rectangle, green #d4edda)
6. Generate PROJECT_PROFILE.yaml (data - cylinder, red #f8d7da - critical output)
7. End (oval, green)

Use standard flowchart symbols.
Output as .drawio XML.
Save to: docs/diagrams/source/phases/phase-0-bootstrap.drawio
```

**Output**: `phase-0-bootstrap.drawio` (valid XML)

#### **2. Automated Rendering**

```powershell
.\scripts\render_diagrams.ps1 -Format "png"
```

**Result**: `docs/diagrams/exports/png/phases/phase-0-bootstrap.png`

#### **3. Embed in Documentation**

```markdown
## Phase 0: Bootstrap & Initialization

![Phase 0 Flow](diagrams/exports/png/phases/phase-0-bootstrap.png)

[Edit Source](diagrams/source/phases/phase-0-bootstrap.drawio)
```

---

## ✅ Contract for AI Agents

Any AI agent using this pattern MUST:

1. **Generate valid .drawio XML** or SVG
   - Follow draw.io mxGraphModel schema
   - Use standard flowchart shapes
   - Apply color palette from `docs/reference/FLOWCHART_SYMBOLS_REFERENCE.md`

2. **Save to correct location**
   - `docs/diagrams/source/{category}/{name}.drawio`
   - Categories: architecture, phases, data-flow, components

3. **Never modify GUI directly**
   - All changes via file generation
   - No manual draw.io Desktop interaction in automation

4. **Exit non-zero on failure**
   - Validate XML before saving
   - Check file write success

---

## 🎨 Diagram Standards

Follow these rules (enforced by review):

### **Color Palette**
```
External/User:   #f0f0f0
Engine/Logic:    #fff3cd
Data/Storage:    #e1f5ff
Validation/OK:   #d4edda
Critical/Error:  #f8d7da
Support/Plugin:  #ffd4e5
UI/Display:      #e8d4f8
```

### **Symbol Usage**
- **Oval**: Start/End terminals
- **Rectangle**: Process steps
- **Diamond**: Decisions
- **Cylinder**: Databases/storage
- **Parallelogram**: Input/output
- **Double-border rectangle**: Subroutines/modules

See: `docs/reference/FLOWCHART_SYMBOLS_REFERENCE.md`

---

## 🔄 Integration with Orchestrator

### **Option A: On-Demand Rendering**

Add to workstream:
```yaml
- id: TASK-RENDER-DIAGRAMS
  type: script
  command: pwsh -File scripts/render_diagrams.ps1 -Format png
  depends_on: [TASK-GENERATE-DIAGRAMS]
```

### **Option B: Pre-commit Hook**

Automatically render diagrams before git commit:
```powershell
# .git/hooks/pre-commit (PowerShell)
pwsh -File scripts/render_diagrams.ps1 -Format png
if ($LASTEXITCODE -ne 0) {
  Write-Error "Diagram rendering failed"
  exit 1
}
```

### **Option C: CI/CD Pipeline**

GitHub Actions / Azure DevOps:
```yaml
- name: Render Diagrams
  run: |
    pwsh -File scripts/render_diagrams.ps1 -Format png,pdf

- name: Upload Artifacts
  uses: actions/upload-artifact@v3
  with:
    name: diagrams
    path: docs/diagrams/exports/
```

---

## 🚫 Anti-Patterns

### **DON'T**
❌ Manually edit diagrams in GUI and take screenshots
❌ Store binary .drawio files without XML version
❌ Hardcode paths to draw.io.exe in scripts
❌ Mix diagram generation and rendering logic
❌ Skip version control of .drawio source files

### **DO**
✅ Generate .drawio XML programmatically
✅ Use `C:\Tools\drawio-cli.ps1` wrapper consistently
✅ Separate source (.drawio) from exports (PNG/PDF)
✅ Track .drawio in git, ignore exports/
✅ Validate XML before saving

---

## 📊 Benefits

| Aspect | Benefit |
|--------|---------|
| **Reproducibility** | Diagrams regenerated from source, no manual steps |
| **Version Control** | Git tracks XML changes, easy diffs |
| **Automation** | CI/CD can render diagrams automatically |
| **Consistency** | AI enforces color/symbol standards |
| **Scalability** | Generate 25+ diagrams in minutes |
| **Documentation** | Always up-to-date with code/specs |

---

## 🔗 Related Patterns

- **PAT-DOC-GENERATION-001**: Automated documentation generation
- **EXEC-001 to EXEC-006**: Execution patterns for batch operations
- **FLOWCHART_SYMBOLS_REFERENCE.md**: Standard symbol definitions

---

## 📚 References

- **draw.io CLI Documentation**: https://www.drawio.com/doc/faq/export-to-png-cli
- **Diagram Creation Guide**: `docs/diagrams/DIAGRAM_CREATION_GUIDE.md`
- **Symbol Reference**: `docs/reference/FLOWCHART_SYMBOLS_REFERENCE.md`

---

## 🎯 Success Criteria

Pattern is successfully implemented when:

- [ ] `C:\Tools\drawio-cli.ps1` wrapper exists and works
- [ ] `scripts/render_diagrams.ps1` can render all diagrams
- [ ] AI agents generate valid .drawio XML files
- [ ] Exports are created automatically (PNG/PDF)
- [ ] Documentation embeds exported images
- [ ] Git tracks source, ignores exports
- [ ] CI/CD pipeline includes diagram rendering (optional)

---

**Status**: ✅ Active
**Maintained By**: Automation Team
**Last Updated**: 2025-12-05
**Version**: 1.0
