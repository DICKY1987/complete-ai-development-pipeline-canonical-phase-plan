---
doc_id: DOC-DIAGRAMS-GUIDE-001
created: 2025-12-05T07:45:00Z
purpose: Step-by-step guide for creating pipeline diagrams in draw.io
---

# 📐 Diagram Creation Guide

**Tool**: draw.io (diagrams.net)
**Version**: Desktop application
**Skill Level**: Beginner to Intermediate

---

## 🎯 Quick Start

### **Launch draw.io**

```powershell
# From PowerShell
& "C:\Users\richg\draw.io\draw.io.exe"

# Or use Start Menu
# Start → draw.io
```

---

## 📋 Step-by-Step: Create Your First Diagram

### **Example: Phase 0 Bootstrap Flow**

---

### **Step 1: Create New Diagram**

1. **Launch draw.io**
2. Click **Create New Diagram**
3. Select **Blank Diagram**
4. **File Name**: `phase-0-bootstrap.drawio`
5. **Location**: Save to `docs/diagrams/source/phases/`
6. Click **Create**

---

### **Step 2: Set Up Canvas**

1. **File** → **Page Setup**
   - **Paper Size**: A4 Landscape (or Letter)
   - **Grid Size**: 10px
   - **Background**: White
   - Click **Apply**

2. **View** → **Grid** (enable)
3. **View** → **Snap to Grid** (enable)

---

### **Step 3: Add Shapes**

#### **Find Flowchart Shapes**

1. **Left Panel** → Click **More Shapes**
2. Check ✅ **Flowchart** (if not already enabled)
3. Click **Apply**

Now you'll see flowchart shapes in the left panel.

#### **Insert Start Symbol** (Terminal/Oval)

1. **Drag** the **Terminator** (oval) shape to canvas
2. **Double-click** to edit text: `User: New Project`
3. **Right-click** → **Edit Style**
   - **Fill Color**: `#f0f0f0` (gray - external user)
   - **Stroke Color**: `#666666`
   - **Stroke Width**: `2`
   - Click **Apply**

#### **Insert Process Steps** (Rectangles)

1. **Drag** a **Process** (rectangle) shape
2. Label: `core/bootstrap/orchestrator.py`
3. **Edit Style**:
   - **Fill Color**: `#fff3cd` (yellow - engine)
   - **Stroke Color**: `#333333`
   - **Stroke Width**: `2`

4. **Repeat** for more steps:
   - `core/bootstrap/discovery.py` (yellow)
   - `schema/Validate` (green `#d4edda`)

#### **Insert Document Symbol**

1. **Drag** **Predefined Process** or **Document** shape
2. Label: `profiles/Select Profile`
3. **Edit Style**:
   - **Fill Color**: `#e1f5ff` (blue - data)
   - **Stroke Color**: `#333333`

#### **Insert Database Symbol**

1. **Drag** **Data Store** or **Cylinder** shape
2. Label: `Generate\nPROJECT_PROFILE.yaml\nrouter_config.json`
3. **Edit Style**:
   - **Fill Color**: `#f8d7da` (red - critical output)
   - **Stroke Color**: `#333333`

#### **Insert Decision Symbol**

1. **Drag** **Decision** (diamond) shape
2. Label: `Valid?`
3. **Edit Style**:
   - **Fill Color**: `#f8d7da` (red - critical decision)
   - **Stroke Color**: `#333333`
   - **Stroke Width**: `3` (thicker for emphasis)

---

### **Step 4: Connect Shapes**

1. **Hover** over the first shape (start oval)
2. **Blue arrows** appear on the edges
3. **Click and drag** an arrow to the next shape
4. **Release** when hovering over target

#### **Label Connections**

1. **Double-click** the arrow/connector
2. Type label (e.g., `validates`, `creates`, `Yes`, `No`)
3. **Position** label by dragging

#### **Style Arrows**

1. **Right-click** arrow → **Edit Style**
   - **Line Color**: `#333333`
   - **Line Width**: `2`
   - **Arrow End**: Standard arrow
   - **Line Pattern**: Solid (or dashed for optional paths)

---

### **Step 5: Organize Layout**

#### **Align Shapes**

1. **Select multiple shapes** (Ctrl+Click)
2. **Arrange** → **Align** → **Align Center Horizontally**
3. **Arrange** → **Distribute** → **Vertically**

#### **Use Swimlanes** (Optional for complex diagrams)

1. **Drag** a **Container** or **Swimlane** from left panel
2. Label sections: "Bootstrap Phase", "Validation", "Output"
3. **Drag shapes** into lanes

---

### **Step 6: Add Legend**

1. **Insert** → **Text Box**
2. Type:
   ```
   LEGEND
   ───────
   Gray: External (User)
   Yellow: Engine/Logic
   Blue: Data/Storage
   Green: Validation
   Red: Critical/Output
   ```
3. **Position** in bottom-right corner

---

### **Step 7: Add Title**

1. **Insert** → **Text Box**
2. Type: `Phase 0: Bootstrap & Initialization`
3. **Format**:
   - **Font**: Arial Bold
   - **Size**: 18pt
   - **Alignment**: Center
4. **Position** at top of diagram

---

### **Step 8: Review and Refine**

**Quality Checklist**:

- [ ] All shapes use standard flowchart symbols
- [ ] Colors match the standard palette
- [ ] All connections are labeled
- [ ] Decision branches show Yes/No or Success/Fail
- [ ] Flow direction is clear (top-to-bottom or left-to-right)
- [ ] Legend is present
- [ ] Title is clear
- [ ] Shapes are aligned and evenly spaced
- [ ] No overlapping text

---

### **Step 9: Save Source File**

1. **File** → **Save As**
2. **Location**: `docs/diagrams/source/phases/phase-0-bootstrap.drawio`
3. Click **Save**

---

### **Step 10: Export for Documentation**

#### **Export as PNG**

1. **File** → **Export As** → **PNG**
2. **Settings**:
   - **Zoom**: 100%
   - **Width**: Auto (or 1920px for high-res)
   - **Transparent Background**: No (keep white)
   - **Include a copy of my diagram**: Yes (optional)
3. **Export**
4. Save to: `docs/diagrams/exports/png/phase-0-bootstrap.png`

#### **Export as SVG** (Optional)

1. **File** → **Export As** → **SVG**
2. Save to: `docs/diagrams/exports/svg/phase-0-bootstrap.svg`

---

## 🎨 Advanced Techniques

### **Grouping Shapes**

1. **Select multiple shapes** (Ctrl+Click or drag selection box)
2. **Right-click** → **Group** (Ctrl+G)
3. **Ungroup**: Right-click → **Ungroup** (Ctrl+Shift+U)

### **Creating Subgraphs/Containers**

1. **Drag** a **Rectangle** shape (larger)
2. **Right-click** → **Edit Style** → **Opacity**: 20%
3. **Fill**: Light gray
4. **Send to Back**: Right-click → **To Back**
5. Label: "PHASE 0: Bootstrap"

### **Using Layers**

1. **View** → **Layers**
2. **Add Layer**: Click `+`
3. Name layers: "Flow", "Annotations", "Background"
4. **Toggle visibility** with eye icon

### **Copy Styling**

1. **Select** a styled shape
2. **Right-click** → **Copy Style** (Ctrl+Shift+C)
3. **Select** target shape
4. **Right-click** → **Paste Style** (Ctrl+Shift+V)

---

## 📐 Standard Templates

### **Flowchart Template Structure**

```
┌─────────────────────────────────────┐
│  TITLE: [Phase/Component Name]      │
└─────────────────────────────────────┘

      ╭─────────╮
      │  START  │  ← Terminal (Gray #f0f0f0)
      ╰─────────╯
           ↓
      ┌─────────┐
      │ Process │  ← Process (Yellow #fff3cd)
      └─────────┘
           ↓
         ╱───╲
        ╱ ??? ╲    ← Decision (Red #f8d7da)
        ╲     ╱
         ╲───╱
       ↙       ↘
     Yes       No
      ↓         ↓
┌────────┐  ┌────────┐
│  Path  │  │  Path  │
└────────┘  └────────┘
      ↓         ↓
      └────┬────┘
           ↓
      ╭─────────╮
      │   END   │  ← Terminal (Green #d4edda)
      ╰─────────╯

┌──────────────────┐
│ LEGEND           │
│ • Gray: External │
│ • Yellow: Engine │
│ • Blue: Data     │
│ • Green: Valid   │
│ • Red: Critical  │
└──────────────────┘
```

---

## 🔍 Common Patterns

### **Pattern 1: Linear Process Flow**

```
Start → Process 1 → Process 2 → Process 3 → End
```

**Use for**: Simple sequential operations

### **Pattern 2: Decision Branch**

```
        Process
           ↓
       Decision?
       ↙       ↘
     Yes        No
      ↓          ↓
   Success    Error
      ↓          ↓
      └────┬─────┘
           ↓
         End
```

**Use for**: Error handling, validation

### **Pattern 3: Loop/Retry**

```
   Start
     ↓
   Process
     ↓
  Success?  ─No→ Retry Count < Max? ─Yes→ (loop back)
     │                    │
    Yes                  No
     ↓                    ↓
  Continue             Fail
```

**Use for**: Retry logic, circuit breakers

### **Pattern 4: Parallel Execution**

```
        Start
          ↓
      Scheduler
          ↓
     ┌────┼────┐
     ↓    ↓    ↓
   Task1 Task2 Task3
     ↓    ↓    ↓
     └────┼────┘
          ↓
        Merge
```

**Use for**: Concurrent tasks, fan-out/fan-in

---

## 📊 Diagram-Specific Guidelines

### **Architecture Diagrams**

- **Focus**: Module relationships, dependencies
- **Symbols**: Rectangles (modules), Arrows (dependencies), Cylinders (databases)
- **Layout**: Layered (top-to-bottom) or hierarchical
- **Colors**: Use layer colors (Foundation=blue, State=yellow, etc.)

### **Phase Flow Diagrams**

- **Focus**: Step-by-step process
- **Symbols**: Full flowchart set (start/end, process, decision, data)
- **Layout**: Top-to-bottom linear flow
- **Colors**: Role-based (engine=yellow, data=blue, validation=green)

### **Data Flow Diagrams**

- **Focus**: Data transformation
- **Symbols**: Parallelograms (input/output), Cylinders (storage), Documents (files)
- **Layout**: Left-to-right or circular
- **Colors**: Blue for all data, yellow for transformations

### **Component Diagrams**

- **Focus**: Internal logic
- **Symbols**: Subroutine boxes, decisions, delays
- **Layout**: Swimlanes for different concerns
- **Colors**: Yellow for logic, red for error paths

---

## ✅ Quality Standards

### **Before You Export**

Run through this checklist:

1. **Symbols**
   - [ ] All shapes use standard flowchart symbols
   - [ ] Start/End are ovals (terminals)
   - [ ] Decisions are diamonds
   - [ ] Processes are rectangles

2. **Colors**
   - [ ] Gray (`#f0f0f0`) for external/user
   - [ ] Yellow (`#fff3cd`) for engines/logic
   - [ ] Blue (`#e1f5ff`) for data/storage
   - [ ] Green (`#d4edda`) for validation/success
   - [ ] Red (`#f8d7da`) for critical/errors
   - [ ] Orange (`#ffd4e5`) for plugins/support
   - [ ] Purple (`#e8d4f8`) for UI

3. **Labels**
   - [ ] All nodes have clear labels
   - [ ] All decision branches labeled (Yes/No)
   - [ ] All arrows labeled with action/data

4. **Layout**
   - [ ] Flow direction is consistent
   - [ ] Shapes are aligned
   - [ ] Spacing is even
   - [ ] No overlapping shapes or text

5. **Documentation**
   - [ ] Title is present and clear
   - [ ] Legend included
   - [ ] References to code paths are accurate

---

## 🔗 Quick Reference

### **Color Palette** (Copy/Paste Values)

```
External/User:   #f0f0f0
Engine/Logic:    #fff3cd
Data/Storage:    #e1f5ff
Validation/OK:   #d4edda
Critical/Error:  #f8d7da
Support/Plugin:  #ffd4e5
UI/Display:      #e8d4f8
Stroke:          #333333
User Stroke:     #666666
```

### **Keyboard Shortcuts**

| Action | Shortcut |
|--------|----------|
| Select All | Ctrl+A |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Duplicate | Ctrl+D |
| Delete | Delete |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Group | Ctrl+G |
| Ungroup | Ctrl+Shift+U |
| Bring to Front | Ctrl+Shift+F |
| Send to Back | Ctrl+Shift+B |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Zoom to Fit | Ctrl+H |

---

## 📚 Resources

- **draw.io Documentation**: https://www.drawio.com/doc/
- **Flowchart Symbols**: [FLOWCHART_SYMBOLS_REFERENCE.md](../reference/FLOWCHART_SYMBOLS_REFERENCE.md)
- **E2E Process Visual**: [E2E_PROCESS_VISUAL_DIAGRAM.md](../E2E_PROCESS_VISUAL_DIAGRAM.md)
- **Pipeline Color Palette**: See README.md in this folder

---

## 🎯 Next Steps

1. **Practice**: Create a simple diagram (e.g., Phase 8 Completion - simplest flow)
2. **Reference**: Use E2E_PROCESS_VISUAL_DIAGRAM.md Mermaid code as blueprint
3. **Start Critical**: Begin with "E2E Complete Flow" diagram
4. **Phase by Phase**: Create detailed diagrams for Phase 0-2 (highest priority)
5. **Iterate**: Get feedback, refine, update

---

**Happy Diagramming!** 🎨

**Questions?** Reference [README.md](README.md) or consult FLOWCHART_SYMBOLS_REFERENCE.md

---

**Version**: 1.0
**Last Updated**: 2025-12-05
