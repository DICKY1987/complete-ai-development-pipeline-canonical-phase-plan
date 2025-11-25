# Orchestration Templates

> **Workflow Definition Templates - Phases, Workstreams, DAGs, and Tasks**  
> **Purpose**: Define what gets executed and in what order  
> **Layer**: Orchestration (Domain Logic)

---

## 📋 Overview

Orchestration templates define the **structure and flow** of your AI development pipelines. They specify phases, workstreams, dependency graphs, and individual tasks that make up complete workflows.

### What's in This Directory

```
orchestration/
├── README.md                    # This file
├── INTERFACE.md                 # Public interface definitions
│
├── phases/                      # Phase specification templates
├── workstreams/                 # Workstream bundle templates
├── dags/                        # Dependency graph templates
└── tasks/                       # Task specification templates
```

---

## 🎯 Template Categories

### 1. Phase Templates (`phases/`)

**Purpose**: Define major workflow stages

**Use Cases**:
- Analysis phase (discovery, requirements)
- Implementation phase (code generation, refactoring)
- Validation phase (testing, quality checks)
- Custom phases (security scan, documentation)

**Key Templates**:
- `phase-core-template.yaml` - Basic phase structure
- `phase-analysis-template.yaml` - Analysis/discovery phase
- `phase-implementation-template.yaml` - Code implementation phase
- `phase-validation-template.yaml` - Testing/validation phase

**Example**:
```yaml
# phase-analysis-template.yaml
phase_id: "{{PHASE_ID}}"
description: "{{DESCRIPTION}}"
workstreams:
  - workstream_id: "ws-discovery"
    tasks: ["analyze-requirements", "identify-components"]
```

---

### 2. Workstream Templates (`workstreams/`)

**Purpose**: Define parallel execution bundles

**Use Cases**:
- Single-threaded sequential execution
- Multi-threaded parallel execution
- Mixed sequential + parallel patterns

**Key Templates**:
- `workstream-single-template.json` - Simple sequential execution
- `workstream-parallel-template.json` - Parallel task execution
- `workstream-sequential-template.json` - Strict step-by-step execution

**Example**:
```json
{
  "workstream_id": "{{WORKSTREAM_ID}}",
  "description": "{{DESCRIPTION}}",
  "execution_mode": "parallel",
  "max_parallel": 3,
  "tasks": [...]
}
```

---

### 3. DAG Templates (`dags/`)

**Purpose**: Define task dependency graphs

**Use Cases**:
- Simple linear dependencies (A → B → C)
- Parallel branches (A → [B, C] → D)
- Complex multi-level graphs

**Key Templates**:
- `dag-simple-template.yaml` - Linear dependency chain
- `dag-parallel-template.yaml` - Parallel execution branches
- `dag-complex-template.yaml` - Multi-level dependency graph

**Example**:
```yaml
# dag-parallel-template.yaml
dag:
  nodes:
    - task_id: "analyze"
      depends_on: []
    - task_id: "impl-a"
      depends_on: ["analyze"]
    - task_id: "impl-b"
      depends_on: ["analyze"]
    - task_id: "validate"
      depends_on: ["impl-a", "impl-b"]
```

---

### 4. Task Templates (`tasks/`)

**Purpose**: Define atomic units of work

**Use Cases**:
- Code analysis tasks
- Code editing tasks
- Testing tasks
- Custom tool invocations

**Key Templates**:
- `task-analysis-template.yaml` - Analysis/discovery task
- `task-code-edit-template.yaml` - Code modification task
- `task-testing-template.yaml` - Test execution task

**Example**:
```yaml
# task-code-edit-template.yaml
task_id: "{{TASK_ID}}"
description: "{{DESCRIPTION}}"
tool_requirement:
  capability: "code_edit"
  tool_preference: "aider"
input:
  files: ["{{FILE_PATTERN}}"]
  instructions: "{{INSTRUCTIONS}}"
```

---

## 🚀 Quick Start

### Creating a New Phase

```bash
# 1. Copy the template
cd templates/orchestration/phases/
cp phase-core-template.yaml my-custom-phase.yaml

# 2. Edit the file (replace placeholders)
# {{PHASE_ID}} → "PH-CUSTOM-01"
# {{DESCRIPTION}} → "My custom phase"
# {{WORKSTREAMS}} → List your workstreams

# 3. Validate
python ../../../core/bootstrap/validator.py my-custom-phase.yaml
```

### Creating a Workstream Bundle

```bash
# 1. Copy the template
cd templates/orchestration/workstreams/
cp workstream-parallel-template.json my-workstream.json

# 2. Edit the file
# {{WORKSTREAM_ID}} → "ws-my-task"
# {{DESCRIPTION}} → "My parallel workstream"
# Add your tasks

# 3. Validate
python ../../../core/bootstrap/validator.py my-workstream.json
```

### Defining a Task

```bash
# 1. Copy the template
cd templates/orchestration/tasks/
cp task-analysis-template.yaml my-task.yaml

# 2. Edit the file
# {{TASK_ID}} → "task-001"
# {{DESCRIPTION}} → "Analyze codebase"
# Set tool requirements

# 3. Validate
python ../../../core/bootstrap/validator.py my-task.yaml
```

---

## 🔗 How Templates Connect

### Hierarchy

```
Phase (PH-IMPL-01)
 │
 ├─ Workstream (ws-001)
 │   ├─ Task (task-001)
 │   └─ Task (task-002)
 │
 └─ Workstream (ws-002)
     ├─ Task (task-003)
     └─ Task (task-004)
```

### References

Templates reference each other via:
- **File paths**: `workstream_ref: "file://workstreams/ws-001.json"`
- **IDs**: `workstream_id: "ws-001"` (resolved at runtime)

Framework resolves all references during orchestration.

---

## 📐 Template Structure

### Common Pattern

All orchestration templates follow this structure:

```yaml
# HEADER: Template metadata
# Template: {name}
# Purpose: {description}
# Schema: {schema reference}
# Version: {version}

# IDENTIFICATION
{id_field}: "{{ID}}"
description: "{{DESCRIPTION}}"

# CONFIGURATION
# Template-specific configuration

# EXECUTION
# Execution parameters (timeouts, retries, etc.)

# VALIDATION
# Validation rules and quality gates

# EXAMPLE
# Example values demonstrating usage
```

---

## 🎓 Usage Patterns

### Pattern 1: Simple Sequential Pipeline

```yaml
# Phase: PH-SIMPLE-01
workstreams:
  - workstream_id: "ws-sequential"
    tasks:
      - task_id: "task-1"  # Runs first
      - task_id: "task-2"  # Runs after task-1
      - task_id: "task-3"  # Runs after task-2
```

### Pattern 2: Parallel Execution

```yaml
# Phase: PH-PARALLEL-01
workstreams:
  - workstream_id: "ws-parallel"
    execution_mode: "parallel"
    max_parallel: 3
    tasks:
      - task_id: "task-a"  # Run in parallel
      - task_id: "task-b"  # Run in parallel
      - task_id: "task-c"  # Run in parallel
```

### Pattern 3: Mixed Sequential + Parallel

```yaml
# Phase: PH-MIXED-01
workstreams:
  - workstream_id: "ws-phase-1"  # Sequential
    tasks: ["task-1", "task-2"]
  
  - workstream_id: "ws-phase-2a"  # Parallel
    depends_on: ["ws-phase-1"]
    tasks: ["task-3a", "task-3b"]
  
  - workstream_id: "ws-phase-2b"  # Parallel
    depends_on: ["ws-phase-1"]
    tasks: ["task-3c", "task-3d"]
  
  - workstream_id: "ws-phase-3"  # Sequential
    depends_on: ["ws-phase-2a", "ws-phase-2b"]
    tasks: ["task-4"]
```

---

## ✅ Validation

### Schema Validation

All templates validate against JSON schemas:

```bash
# Validate phase
python core/bootstrap/validator.py \
  --schema schema/phase_spec.v1.json \
  --file my-phase.yaml

# Validate workstream
python core/bootstrap/validator.py \
  --schema schema/workstream_spec.v1.json \
  --file my-workstream.json

# Validate task
python core/bootstrap/validator.py \
  --schema schema/task_spec.v1.json \
  --file my-task.yaml
```

### Dependency Validation

Check dependencies between templates:

```bash
# Validate dependency graph
python scripts/validate_template_dependencies.py \
  --template my-phase.yaml
```

---

## 🔍 Finding the Right Template

### By Use Case

| I want to... | Use Template |
|--------------|-------------|
| Create a new phase | `phases/phase-core-template.yaml` |
| Define analysis phase | `phases/phase-analysis-template.yaml` |
| Define implementation phase | `phases/phase-implementation-template.yaml` |
| Define validation phase | `phases/phase-validation-template.yaml` |
| Create sequential workflow | `workstreams/workstream-sequential-template.json` |
| Create parallel workflow | `workstreams/workstream-parallel-template.json` |
| Define simple DAG | `dags/dag-simple-template.yaml` |
| Define complex DAG | `dags/dag-complex-template.yaml` |
| Create analysis task | `tasks/task-analysis-template.yaml` |
| Create code edit task | `tasks/task-code-edit-template.yaml` |
| Create testing task | `tasks/task-testing-template.yaml` |

---

## 📚 Related Documentation

- **[Templates Main README](../README.md)** - Overview of all templates
- **[STRUCTURE.md](../STRUCTURE.md)** - Detailed structure guide
- **[CONTEXT.md](../CONTEXT.md)** - Execution model and context
- **[INTERFACE.md](INTERFACE.md)** - Public interface definitions
- **[UET Specs](../../specs/)** - Detailed specifications
- **[JSON Schemas](../../schema/)** - Validation schemas

---

## 🎯 Best Practices

### Naming Conventions

- **Phases**: `PH-{CATEGORY}-{NUMBER}` (e.g., `PH-IMPL-01`)
- **Workstreams**: `ws-{description}` (e.g., `ws-discovery`)
- **Tasks**: `task-{number}` or `task-{description}` (e.g., `task-001` or `task-analyze-code`)

### Organization

- Keep phases focused (one major goal per phase)
- Group related tasks in same workstream
- Use parallel execution where tasks are independent
- Document dependencies clearly in DAGs

### Error Handling

- Define timeout values for all tasks
- Specify retry policies for critical tasks
- Add fallback mechanisms for tools
- Include validation steps after major changes

---

## 📞 Support

### Common Questions

**Q: How do I create a multi-phase workflow?**  
A: Create multiple phase templates and reference them in sequence in your project configuration.

**Q: How do I make tasks run in parallel?**  
A: Use `workstream-parallel-template.json` and set `execution_mode: "parallel"`.

**Q: How do I define dependencies between tasks?**  
A: Use DAG templates to specify `depends_on` relationships.

**Q: What's the difference between a workstream and a phase?**  
A: A phase is a major workflow stage. A workstream is a bundle of tasks within a phase that can execute in parallel.

### Getting Help

- Check [CONTEXT.md](../CONTEXT.md) for execution model details
- Review [examples](../examples/) for complete implementations
- Consult [UET Specifications](../../specs/) for detailed specs
- Report issues via GitHub

---

**Last Updated**: 2025-11-23  
**Related**: [Adapter Templates](../adapters/README.md), [Configuration Templates](../configuration/README.md)
