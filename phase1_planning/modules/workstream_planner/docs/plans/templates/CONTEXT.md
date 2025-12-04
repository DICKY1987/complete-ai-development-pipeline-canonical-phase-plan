---
doc_id: DOC-GUIDE-CONTEXT-891
---

# Templates Context & Execution Model

> **Context Management and Execution Patterns for UET Framework Templates**
> **Purpose**: Explain how templates fit into the execution model and provide context for AI tools
> **Last Updated**: 2025-11-23

---

## 🎯 Execution Model Overview

The UET Framework follows a **phase-based execution model** with templates defining each component:

```
┌────────────────────────────────────────────────────┐
│  Project Bootstrap (Configuration Templates)       │
│  • Detect project type                            │
│  • Select profile                                  │
│  • Generate PROJECT_PROFILE.yaml                   │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│  Phase Definition (Orchestration Templates)        │
│  • Load phase specs                               │
│  • Define workstreams                             │
│  • Build dependency DAG                           │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│  Task Routing (Adapter Templates)                 │
│  • Match task → tool                              │
│  • Select capable adapter                         │
│  • Configure execution parameters                 │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│  Execution & Monitoring (UI Templates)            │
│  • Execute tasks                                  │
│  • Track progress                                 │
│  • Report results                                 │
└────────────────────────────────────────────────────┘
```

Each stage uses specific template types to define its behavior.

---

## 📦 Template Lifecycle

### 1. Template Discovery

**When**: Bootstrap or initialization phase
**How**: Framework scans template directories
**Templates Used**:
- Configuration templates (profiles, routers)
- Orchestration templates (phases, workstreams)

```python
# Framework discovers templates
from templates.configuration.profiles import load_profile_template
from templates.orchestration.phases import load_phase_template

# Select appropriate template
profile = select_profile_for_project(project_path)
template = load_profile_template(profile)
```

---

### 2. Template Instantiation

**When**: Creating project-specific configuration
**How**: Replace placeholders with actual values
**Templates Used**: All template types

```python
# Instantiate template with real values
phase_spec = phase_template.instantiate({
    'PHASE_ID': 'PH-IMPL-01',
    'DESCRIPTION': 'Core implementation phase',
    'WORKSTREAMS': ['ws-001', 'ws-002']
})
```

**Placeholder Resolution**:
```yaml
# Template
phase_id: "{{PHASE_ID}}"
description: "{{DESCRIPTION}}"

# Becomes
phase_id: "PH-IMPL-01"
description: "Core implementation phase"
```

---

### 3. Template Validation

**When**: After instantiation, before execution
**How**: Validate against JSON schemas
**Templates Used**: All templates

```python
# Validate instantiated template
from core.bootstrap.validator import validate_against_schema

result = validate_against_schema(
    phase_spec,
    schema='schema/phase_spec.v1.json'
)

if not result.valid:
    raise ValidationError(result.errors)
```

---

### 4. Template Execution

**When**: Runtime execution
**How**: Framework interprets template and executes defined behavior
**Templates Used**: Orchestration and adapter templates

```python
# Execute based on template
from core.engine.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.execute_phase(phase_spec)
```

---

### 5. Template Monitoring

**When**: During and after execution
**How**: UI templates render progress and results
**Templates Used**: UI templates (dashboards, reports)

```python
# Render monitoring view from template
from templates.ui.dashboards import render_progress_dashboard

dashboard = render_progress_dashboard(
    run_id=result.run_id,
    template='dashboard-progress-template.html'
)
```

---

## 🔄 Template Composition

Templates can be **composed** to build complex workflows:

### Example: Multi-Phase Workflow

```yaml
# High-level workflow (composed from templates)
workflow:
  name: "Complete Development Pipeline"

  # Phase 1: Uses orchestration/phases/phase-analysis-template.yaml
  phases:
    - phase_id: "PH-ANALYSIS-01"
      template: "phase-analysis-template"
      workstreams:
        # Uses orchestration/workstreams/workstream-single-template.json
        - workstream_id: "ws-discovery"
          template: "workstream-single-template"
          tasks:
            # Uses orchestration/tasks/task-analysis-template.yaml
            - task_id: "task-001"
              template: "task-analysis-template"
              tool: "aider"  # Uses adapters/subprocess/aider-adapter.py

    # Phase 2: Uses orchestration/phases/phase-implementation-template.yaml
    - phase_id: "PH-IMPL-01"
      template: "phase-implementation-template"
      # ... nested templates ...
```

### Composition Patterns

**Sequential Composition**:
```
Phase-1 → Phase-2 → Phase-3
```

**Parallel Composition**:
```
Workstream-A ─┐
Workstream-B ─┼→ Phase
Workstream-C ─┘
```

**Hierarchical Composition**:
```
Project
 ├─ Phase-1
 │   ├─ Workstream-A
 │   │   ├─ Task-1
 │   │   └─ Task-2
 │   └─ Workstream-B
 └─ Phase-2
```

---

## 🧩 Template Context Requirements

### What Templates Need to Know

Each template type has specific **context requirements**:

#### Orchestration Templates
**Need**:
- Project profile (language, frameworks, tools)
- Available tools and their capabilities
- Execution constraints (time, resources)
- Previous phase outputs (if applicable)

**Example Context**:
```json
{
  "project": {
    "type": "python",
    "tools": ["pytest", "ruff", "aider"],
    "constraints": {"max_parallel": 3}
  },
  "runtime": {
    "current_phase": "PH-IMPL-01",
    "previous_outputs": {
      "PH-ANALYSIS-01": {
        "requirements": "file://docs/requirements.md"
      }
    }
  }
}
```

#### Adapter Templates
**Need**:
- Tool capabilities and limitations
- Execution environment (paths, credentials)
- Task requirements (input, output formats)

**Example Context**:
```json
{
  "tool": {
    "name": "aider",
    "version": "0.40.0",
    "capabilities": ["code_edit", "refactor"]
  },
  "environment": {
    "work_dir": "/project/.worktrees/ws-001",
    "config": "file://.aider.conf.yml"
  },
  "task": {
    "type": "code_edit",
    "files": ["src/main.py"],
    "instructions": "Refactor using async/await"
  }
}
```

#### Configuration Templates
**Need**:
- Project metadata (type, size, complexity)
- Tool availability (installed tools)
- User preferences (conventions, constraints)

**Example Context**:
```json
{
  "project": {
    "path": "/path/to/project",
    "type": "python",
    "size": "medium",
    "tests": true
  },
  "tools": {
    "available": ["pytest", "ruff", "mypy"],
    "preferred": "pytest"
  },
  "preferences": {
    "naming": "snake_case",
    "max_line_length": 100
  }
}
```

#### UI Templates
**Need**:
- Execution state (running, completed, failed)
- Metrics (progress, performance, errors)
- Historical data (for trends)

**Example Context**:
```json
{
  "run": {
    "id": "run-123",
    "status": "running",
    "progress": 67.5
  },
  "metrics": {
    "tasks_total": 20,
    "tasks_completed": 13,
    "duration": 245.3
  },
  "errors": []
}
```

---

## 🌐 Template Discovery Patterns

### How AI Tools Find Templates

#### 1. By Path Convention

AI can infer template purpose from path:

```python
# Path → Purpose mapping
"templates/orchestration/phases/phase-*.yaml" → Phase templates
"templates/adapters/subprocess/*.py" → CLI tool adapters
"templates/configuration/profiles/*.yaml" → Project profiles
```

#### 2. By Naming Convention

Template names follow patterns:

```
{component}-{variant}-template.{ext}

Examples:
- phase-core-template.yaml        → Core phase template
- workstream-parallel-template.json → Parallel workstream
- adapter-subprocess-template.py   → Subprocess adapter
```

#### 3. By Metadata

Templates include discovery metadata:

```yaml
# Template header
meta:
  template_type: "phase"
  template_id: "phase-core-v1"
  tags: ["core", "analysis", "discovery"]
  schema_version: "1.0.0"
  applicable_to: ["python", "javascript", "generic"]
```

AI can search templates by:
- Type: `template_type: "phase"`
- Tags: `"analysis" in tags`
- Applicability: `"python" in applicable_to`

---

## 📂 Template Storage & Organization

### File System Layout

Templates are organized for **predictable discovery**:

```
templates/
├── {layer}/              # Architectural layer
│   ├── {category}/       # Component category
│   │   ├── README.md     # Category guide
│   │   └── {template}.ext # Template files
```

**Example Queries**:
- "Find all phase templates" → `templates/orchestration/phases/*.yaml`
- "Find Python adapters" → `templates/adapters/subprocess/*python*.py`
- "Find profile for data pipelines" → `templates/configuration/profiles/profile-data*.yaml`

### Version Management

Templates include version information:

```yaml
# Version header
version: "1.0.0"
schema_version: "1.0.0"
compatible_with: ["uet-framework >= 1.0.0"]
```

**Backward Compatibility**:
- Old templates work with new framework (minor versions)
- Breaking changes increment major version
- Framework validates version compatibility

---

## 🔗 Template Wiring

### How Templates Connect

Templates reference each other via **well-defined interfaces**:

#### Phase → Workstream

```yaml
# Phase template references workstreams
phase_id: "PH-IMPL-01"
workstreams:
  - workstream_id: "ws-001"
    workstream_ref: "file://workstreams/ws-001.json"
```

#### Workstream → Task

```json
// Workstream template references tasks
{
  "workstream_id": "ws-001",
  "tasks": [
    {
      "task_id": "task-001",
      "task_ref": "file://tasks/task-001.yaml"
    }
  ]
}
```

#### Task → Adapter

```yaml
# Task template specifies tool requirement
task_id: "task-001"
tool_requirement:
  capability: "code_edit"
  tool_preference: "aider"  # Resolved via router config
```

### Wiring Resolution

Framework resolves references at runtime:

```python
# Framework wiring engine
from core.engine.wiring import resolve_references

# Load phase template
phase = load_template('phase-impl-template.yaml')

# Resolve all references
resolved_phase = resolve_references(phase, context={
    'project_root': '/path/to/project',
    'workstreams_dir': 'workstreams/',
    'tasks_dir': 'schema/tasks/'
})

# Now all nested templates are loaded and validated
```

---

## 🎓 Template Usage Patterns

### Pattern 1: Bootstrap New Project

**Scenario**: Initialize a new Python project

**Templates Used**:
1. `configuration/profiles/profile-python-template.yaml`
2. `configuration/routers/router-basic-template.json`

**Flow**:
```bash
# 1. Detect project type
python core/bootstrap/orchestrator.py /path/to/project

# 2. Framework selects profile template
# 3. Instantiate profile with project specifics
# 4. Generate PROJECT_PROFILE.yaml and router_config.json
```

### Pattern 2: Create Custom Phase

**Scenario**: Add a security scanning phase

**Templates Used**:
1. `orchestration/phases/phase-core-template.yaml` (base)
2. `orchestration/workstreams/workstream-single-template.json`
3. `orchestration/tasks/task-analysis-template.yaml`

**Flow**:
```bash
# 1. Copy phase template
cp templates/orchestration/phases/phase-core-template.yaml \
   my-project/phases/PH-SECURITY-01.yaml

# 2. Customize for security scanning
# Replace {{PHASE_ID}} → "PH-SECURITY-01"
# Replace {{DESCRIPTION}} → "Security vulnerability scan"
# Define workstreams for: SAST, dependency check, secrets scan

# 3. Validate
python core/bootstrap/validator.py phases/PH-SECURITY-01.yaml

# 4. Reference in project workflow
```

### Pattern 3: Add Tool Integration

**Scenario**: Integrate a new linter (e.g., bandit)

**Templates Used**:
1. `adapters/subprocess/tool-adapter-template.py` (base)
2. `configuration/routers/router-multi-tool-template.json`

**Flow**:
```bash
# 1. Copy adapter template
cp templates/adapters/subprocess/tool-adapter-template.py \
   my-project/adapters/bandit_adapter.py

# 2. Implement adapter methods
# - detect_capabilities() → returns ["security_scan"]
# - execute() → runs bandit CLI
# - validate_result() → parses output

# 3. Register in router config
# Add entry: {"capability": "security_scan", "tool": "bandit"}

# 4. Test adapter
pytest tests/adapters/test_bandit_adapter.py
```

### Pattern 4: Custom Dashboard

**Scenario**: Create security-focused dashboard

**Templates Used**:
1. `ui/dashboards/dashboard-progress-template.html` (base)

**Flow**:
```bash
# 1. Copy dashboard template
cp templates/ui/dashboards/dashboard-progress-template.html \
   my-project/ui/dashboard-security.html

# 2. Customize for security metrics
# Add sections: Vulnerabilities found, severity breakdown, remediation status

# 3. Wire to orchestration
# Dashboard consumes data from security phase execution

# 4. Preview
python -m http.server --directory my-project/ui 8000
```

---

## 🧪 Testing with Templates

### Template Validation Testing

```python
# tests/templates/test_phase_templates.py
import pytest
from core.bootstrap.validator import validate_against_schema

def test_phase_core_template_valid():
    """Phase core template should pass schema validation"""
    with open('templates/orchestration/phases/phase-core-template.yaml') as f:
        template = yaml.safe_load(f)

    # Replace placeholders with test values
    instantiated = instantiate_template(template, {
        'PHASE_ID': 'TEST-01',
        'DESCRIPTION': 'Test phase'
    })

    result = validate_against_schema(instantiated, 'schema/phase_spec.v1.json')
    assert result.valid, f"Validation errors: {result.errors}"
```

### Integration Testing

```python
# tests/integration/test_template_composition.py
def test_full_pipeline_from_templates():
    """Complete pipeline can be built from templates"""
    # 1. Bootstrap from profile template
    profile = instantiate_profile_template('profile-python-template.yaml')

    # 2. Create phase from template
    phase = instantiate_phase_template('phase-core-template.yaml')

    # 3. Execute
    orchestrator = Orchestrator(profile)
    result = orchestrator.execute_phase(phase)

    assert result.status == 'success'
```

---

## 📚 Context Documentation

### For Template Authors

When creating templates, provide:

1. **Header Comments**: Explain purpose and usage
2. **Placeholder Documentation**: Describe all `{{VARIABLES}}`
3. **Example Values**: Show realistic examples
4. **Context Requirements**: List required context
5. **Validation Schema**: Reference JSON schema

### For Template Users

When using templates, understand:

1. **Template Purpose**: What problem it solves
2. **Context Needs**: What information to provide
3. **Customization Points**: Which values to change
4. **Validation**: How to verify correctness
5. **Integration**: How it connects to other components

---

## 🔍 Telemetry & State

### Template Usage Tracking

Framework tracks template usage:

```yaml
# .state/template_usage.yaml
templates:
  - id: "phase-core-template"
    path: "orchestration/phases/phase-core-template.yaml"
    usage_count: 47
    last_used: "2025-11-23T10:30:00Z"
    success_rate: 0.96

  - id: "adapter-subprocess-template"
    path: "adapters/subprocess/tool-adapter-template.py"
    usage_count: 12
    last_used: "2025-11-22T14:15:00Z"
    success_rate: 1.0
```

### State Artifacts

Templates can query state:

```python
# Adapter template can check tool state
from core.state.db import get_tool_usage

usage = get_tool_usage('aider')
if usage.failure_rate > 0.5:
    # Fallback to alternative tool
    pass
```

---

## 📞 Support & Resources

### Getting Help with Templates

- **Documentation**: Check category-specific README.md
- **Examples**: Review `templates/examples/`
- **Specifications**: Consult UET specs in `../specs/`
- **Validation**: Use `core/bootstrap/validator.py`

### Common Template Questions

**Q: How do I know which template to use?**
A: See [Templates README.md](README.md#-finding-the-right-template)

**Q: How do I customize a template?**
A: Copy template, replace `{{PLACEHOLDERS}}`, validate with schema

**Q: Can templates be composed?**
A: Yes! See [Template Composition](#-template-composition)

**Q: How are templates validated?**
A: Against JSON schemas in `../schema/` directory

---

## 🔄 Template Evolution

Templates evolve with the framework:

### Version Compatibility

```yaml
# Template declares compatibility
version: "1.2.0"
compatible_with:
  framework: ">= 1.0.0, < 2.0.0"
  schema: "1.0.0"
```

### Migration Paths

When templates change:

```yaml
# Migration metadata
migrations:
  - from_version: "1.0.0"
    to_version: "1.1.0"
    breaking_changes: false
    migration_guide: "docs/migrations/v1.0-to-v1.1.md"
```

---

**Last Updated**: 2025-11-23
**Related Documentation**:
- [Templates README](README.md) - Overview and quick start
- [STRUCTURE.md](STRUCTURE.md) - Structural organization
- [UET Framework Specs](../specs/) - Detailed specifications
