# Visual Diagrams Index

This directory contains visual diagrams and documentation for understanding the complete AI development pipeline.

## 📊 Main Diagrams

### 🌟 **NEW: End-to-End Pipeline (Horizontal Layout)**
**File**: [`END_TO_END_PIPELINE_HORIZONTAL.md`](./END_TO_END_PIPELINE_HORIZONTAL.md)  
**Purpose**: Complete horizontal flow diagram showing all 9 stages of the pipeline from input to output  
**Format**: Mermaid diagram with comprehensive documentation  
**Use Case**: High-level system overview, onboarding, architecture review

**Coverage**:
- ✅ All 9 pipeline stages
- ✅ 8 state machines
- ✅ Tool adapters and integrations
- ✅ Error detection and recovery flows
- ✅ State management and persistence
- ✅ Monitoring and observability

---

## 📚 Existing Diagrams

### System Architecture
- **[SYSTEM_VISUAL_DIAGRAMS.md](./SYSTEM_VISUAL_DIAGRAMS.md)** - Collection of ASCII art diagrams showing data flow, module dependencies, state machines, error handling, configuration cascade, and more

### Integration & Data Flow
- **[integration-overview.mmd](./integration-overview.mmd)** - Mermaid diagram of core integration architecture
- **[data-flow-workstream.mmd](./data-flow-workstream.mmd)** - Workstream data flow
- **[data-flow-aim-integration.mmd](./data-flow-aim-integration.mmd)** - AIM integration data flow
- **[data-flow-error-detection.mmd](./data-flow-error-detection.mmd)** - Error detection flow
- **[data-flow-database.mmd](./data-flow-database.mmd)** - Database interaction flow

### Component & Lifecycle Diagrams
- **[DOC_TASK_LIFECYCLE_DIAGRAM.md](./DOC_TASK_LIFECYCLE_DIAGRAM.md)** - Detailed task state lifecycle
- **[TASK_LIFECYCLE.md](./TASK_LIFECYCLE.md)** - Task lifecycle documentation
- **[FOLDER_LIFECYCLE_FLOW.md](./FOLDER_LIFECYCLE_FLOW.md)** - Folder and artifact lifecycle

### Specialized Flows
- **[DOC_TOOL_SELECTION_DIAGRAM.md](./DOC_TOOL_SELECTION_DIAGRAM.md)** - Tool selection and routing logic
- **[DOC_SPEC_INTEGRATION_DIAGRAM.md](./DOC_SPEC_INTEGRATION_DIAGRAM.md)** - Specification integration flow
- **[DOC_ERROR_ESCALATION_DIAGRAM.md](./DOC_ERROR_ESCALATION_DIAGRAM.md)** - Error escalation and handling
- **[UI_FLOW_DIAGRAM.md](./UI_FLOW_DIAGRAM.md)** - User interface interaction flows

### Module Structure
- **[module-dependencies.mmd](./module-dependencies.mmd)** - Module dependency graph
- **[directory-structure.mmd](./directory-structure.mmd)** - Directory organization

### Reference Materials
- **[DIAGRAM_CREATION_GUIDE.md](./DIAGRAM_CREATION_GUIDE.md)** - Guide for creating diagrams with draw.io
- **[PAT-DIAGRAM-DRAWIO-RENDER-001.md](./PAT-DIAGRAM-DRAWIO-RENDER-001.md)** - Pattern for rendering diagrams

### Visual Assets (PNG)
- **Configuration Cascade.png** - Configuration hierarchy visualization
- **Error Detection & Recovery Flow.png** - Error handling flow
- **Folder Interaction Heatmap.png** - Folder usage frequency
- **Information Flow by Phase.png** - Phase-based information flow
- **Module Dependency Graph.png** - Visual module dependencies
- **Task Lifecycle State Machine.png** - Task state transitions
- **Tool Adapter Pattern.png** - Adapter architecture
- **Workstream Execution Timeline.png** - Timeline visualization

### Other Formats
- **E2E_Process_Flow.drawio** - Draw.io source file for end-to-end process
- **AUTOMATION_CHAIN_DIAGRAM.txt** - Text-based automation chain
- **new 3.xml** - XML diagram source

---

## 🎯 Recommended Reading Order

### For New Team Members
1. **END_TO_END_PIPELINE_HORIZONTAL.md** ⭐ - Start here for complete overview
2. **SYSTEM_VISUAL_DIAGRAMS.md** - Deep dive into system components
3. **integration-overview.mmd** - Understand core architecture
4. **DOC_TASK_LIFECYCLE_DIAGRAM.md** - Learn task execution flow

### For Developers
1. **END_TO_END_PIPELINE_HORIZONTAL.md** - System context
2. **module-dependencies.mmd** - Code organization
3. **data-flow-workstream.mmd** - Workstream execution
4. **DOC_TOOL_SELECTION_DIAGRAM.md** - Tool integration

### For Operations
1. **END_TO_END_PIPELINE_HORIZONTAL.md** - Full pipeline view
2. **DOC_ERROR_ESCALATION_DIAGRAM.md** - Error handling procedures
3. **Error Detection & Recovery Flow.png** - Recovery workflows
4. **UI_FLOW_DIAGRAM.md** - Dashboard usage

### For Architecture Review
1. **END_TO_END_PIPELINE_HORIZONTAL.md** - Complete system design
2. **SYSTEM_VISUAL_DIAGRAMS.md** - Detailed component views
3. **Module Dependency Graph.png** - Dependency analysis
4. **Configuration Cascade.png** - Configuration strategy

---

## 🎨 Diagram Standards

### Color Coding (Horizontal Pipeline)
- 🟣 **Purple**: Input sources (user-facing)
- 🔵 **Blue**: Validation (schema/config)
- 🟢 **Green**: Planning (task decomposition)
- 🟠 **Orange**: Scheduling (queue management)
- 🟡 **Yellow**: Execution (core engine)
- 🔴 **Red**: Error Detection (scanning)
- 🟣 **Purple**: Recovery (resilience)
- ⚫ **Gray**: State (persistence)
- 🔵 **Light Blue**: Output (monitoring)

### Formats
- **`.mmd`**: Mermaid diagrams (can be rendered on GitHub)
- **`.md`**: Markdown with embedded diagrams
- **`.png`**: Exported images for presentations
- **`.drawio`**: Editable draw.io source files
- **`.txt`**: ASCII art diagrams

---

## 🔧 Creating New Diagrams

See **[DIAGRAM_CREATION_GUIDE.md](./DIAGRAM_CREATION_GUIDE.md)** for detailed instructions on:
- Using draw.io for flowcharts
- Standard color palette
- Symbol conventions
- Export guidelines
- Quality checklist

---

## 📖 Related Documentation

- **Core Documentation**: `/docs/`
- **Implementation**: `phase2_implementation/`, `phase3_implementation/`
- **State Machines**: `doc_ssot_state_machines.md`
- **System Summary**: `COMPLETE_IMPLEMENTATION_SUMMARY.md`
- **Configuration**: `config/`

---

## 🤝 Contributing

When adding new diagrams:
1. Follow naming convention: `<PURPOSE>_<TYPE>_<VERSION>.md`
2. Include metadata header with `doc_id`, `purpose`, `status`
3. Add entry to this README
4. Use standard color coding where applicable
5. Provide both visual and textual descriptions
6. Update related documentation

---

**Last Updated**: 2025-12-17  
**Maintained By**: Pipeline Architecture Team
