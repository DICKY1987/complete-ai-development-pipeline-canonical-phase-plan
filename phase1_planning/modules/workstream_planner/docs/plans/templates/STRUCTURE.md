---
doc_id: DOC-GUIDE-STRUCTURE-074
---

# Templates Directory Structure

> **Detailed Organization Guide for UET Framework Templates**
> **Purpose**: Explain the structural organization, navigation patterns, and design decisions
> **Last Updated**: 2025-11-23

---

## 📐 Architectural Overview

The templates directory follows a **layered architecture** that mirrors the UET Framework's execution model:

```
┌─────────────────────────────────────────┐
│           UI Layer                      │  ← ui/
│  (Dashboards, Reports, Monitoring)      │
├─────────────────────────────────────────┤
│        Configuration Layer              │  ← configuration/
│  (Profiles, Routing, Constraints)       │
├─────────────────────────────────────────┤
│       Orchestration Layer               │  ← orchestration/
│  (Phases, Workstreams, DAGs, Tasks)     │
├─────────────────────────────────────────┤
│         Adapter Layer                   │  ← adapters/
│  (Tool Integration, API Clients)        │
└─────────────────────────────────────────┘
```

This structure ensures:
- **Clear Separation of Concerns**: Each layer has distinct responsibilities
- **Predictable Navigation**: AI and human users can infer location from purpose
- **Dependency Flow**: Lower layers don't depend on upper layers

---

## 🗺️ Directory Tree (Detailed)

### Root Level

```
templates/
├── README.md                    # Master index and quick start
├── STRUCTURE.md                 # This file - detailed organization
├── CONTEXT.md                   # Execution model and usage patterns
├── dependencies.yaml            # Cross-template dependencies
└── __init__.py                  # Python package initialization (if needed)
```

**Purpose**: Root level provides **entry points** and **overview documentation**.

---

### Orchestration Layer

```
orchestration/
├── README.md                    # Orchestration patterns guide
├── INTERFACE.md                 # Public interface definitions
│
├── phases/                      # Phase specification templates
│   ├── README.md
│   ├── phase-core-template.yaml
│   ├── phase-analysis-template.yaml
│   ├── phase-implementation-template.yaml
│   └── phase-validation-template.yaml
│
├── workstreams/                 # Workstream bundle templates
│   ├── README.md
│   ├── workstream-single-template.json
│   ├── workstream-parallel-template.json
│   └── workstream-sequential-template.json
│
├── dags/                        # Dependency graph templates
│   ├── README.md
│   ├── dag-simple-template.yaml
│   ├── dag-parallel-template.yaml
│   └── dag-complex-template.yaml
│
└── tasks/                       # Task specification templates
    ├── README.md
    ├── task-analysis-template.yaml
    ├── task-code-edit-template.yaml
    └── task-testing-template.yaml
```

**Purpose**: Define **what gets executed** and **in what order**.

**Key Concepts**:
- **Phases**: Major workflow stages (e.g., analysis, implementation, validation)
- **Workstreams**: Parallel execution bundles within phases
- **DAGs**: Dependency graphs defining execution order
- **Tasks**: Atomic units of work

**Interface Boundaries**:
- Input: Project requirements, constraints
- Output: Executable workflow definitions
- Dependencies: Configuration layer (profiles, constraints)

---

### Adapter Layer

```
adapters/
├── README.md                    # Adapter development guide
├── INTERFACE.md                 # Adapter interface contract
│
├── subprocess/                  # CLI tool adapters
│   ├── README.md
│   ├── tool-adapter-template.py
│   ├── aider-adapter-example.py
│   └── pytest-adapter-example.py
│
├── api/                         # REST/HTTP API adapters
│   ├── README.md
│   ├── rest-adapter-template.py
│   └── graphql-adapter-template.py
│
└── custom/                      # Custom integration adapters
    ├── README.md
    ├── custom-adapter-template.py
    └── batch-processor-template.py
```

**Purpose**: Bridge between **orchestration layer** and **external tools**.

**Key Concepts**:
- **Subprocess Adapters**: Wrap CLI tools (aider, pytest, ruff, etc.)
- **API Adapters**: Integrate REST/GraphQL services
- **Custom Adapters**: Special-purpose integrations

**Interface Contract**:
```python
class ToolAdapter:
    def detect_capabilities() -> Dict[str, Any]
    def execute(request: ExecutionRequest) -> ExecutionResult
    def validate_result(result: Any) -> ValidationResult
```

**Dependencies**: None (lowest layer, pure integration)

---

### Configuration Layer

```
configuration/
├── README.md                    # Configuration guide
├── SCHEMA_REFERENCE.md          # Configuration schema reference
│
├── profiles/                    # Project profile templates
│   ├── README.md
│   ├── profile-python-template.yaml
│   ├── profile-data-template.yaml
│   ├── profile-docs-template.yaml
│   └── profile-generic-template.yaml
│
├── routers/                     # Tool routing templates
│   ├── README.md
│   ├── router-basic-template.json
│   ├── router-multi-tool-template.json
│   └── router-fallback-template.json
│
└── constraints/                 # Execution constraint templates
    ├── README.md
    ├── constraints-time-template.yaml
    ├── constraints-resource-template.yaml
    └── constraints-quality-template.yaml
```

**Purpose**: Define **project configuration** and **execution policies**.

**Key Concepts**:
- **Profiles**: Project type configurations (Python, data pipeline, docs, etc.)
- **Routers**: Tool routing rules (which tool for which task)
- **Constraints**: Execution limits (time, resources, quality gates)

**Used By**:
- Bootstrap system (project initialization)
- Orchestration layer (runtime configuration)
- Adapter layer (tool selection)

**Dependencies**: None (configuration is foundational)

---

### UI Layer

```
ui/
├── README.md                    # UI component guide
├── STYLING_GUIDE.md             # Design and styling standards
│
├── dashboards/                  # Dashboard layout templates
│   ├── README.md
│   ├── dashboard-progress-template.html
│   ├── dashboard-metrics-template.html
│   └── dashboard-errors-template.html
│
├── reports/                     # Report generation templates
│   ├── README.md
│   ├── report-execution-template.md
│   ├── report-summary-template.md
│   └── report-detailed-template.html
│
└── monitoring/                  # Monitoring view templates
    ├── README.md
    ├── monitoring-realtime-template.json
    └── monitoring-historical-template.json
```

**Purpose**: **User-facing** components for visualization and reporting.

**Key Concepts**:
- **Dashboards**: Interactive real-time views
- **Reports**: Static generated summaries
- **Monitoring**: Observability and telemetry views

**Dependencies**:
- Orchestration layer (execution data)
- Configuration layer (display preferences)

---

### Examples Layer

```
examples/
├── README.md                    # Examples catalog and usage guide
│
├── simple-pipeline/             # Minimal working example
│   ├── README.md
│   ├── profile.yaml
│   ├── phase-01.yaml
│   ├── workstream-001.json
│   └── run.sh
│
├── multi-phase/                 # Multi-phase workflow
│   ├── README.md
│   ├── profile.yaml
│   ├── phase-01-analysis.yaml
│   ├── phase-02-implementation.yaml
│   ├── phase-03-validation.yaml
│   ├── workstreams/
│   └── run.sh
│
└── advanced/                    # Advanced patterns
    ├── README.md
    ├── profile.yaml
    ├── parallel-execution/
    ├── error-recovery/
    ├── custom-adapters/
    └── run.sh
```

**Purpose**: **Complete working implementations** demonstrating patterns.

**Key Concepts**:
- **Simple Pipeline**: Bare minimum to understand basics
- **Multi-Phase**: Realistic multi-stage workflow
- **Advanced**: Complex patterns (parallel, recovery, custom)

**Use Cases**:
- Learning UET patterns
- Quick-start new projects
- Testing framework features
- Reference implementations

---

## 🔗 Dependency Flow

### Layer Dependencies (Bottom-up)

```
┌─────────────────┐
│    Examples     │  ← Uses all layers (reference only)
├─────────────────┤
│       UI        │  ← Depends on: Orchestration, Configuration
├─────────────────┤
│  Orchestration  │  ← Depends on: Adapters, Configuration
├─────────────────┤
│    Adapters     │  ← No dependencies (pure integration)
├─────────────────┤
│ Configuration   │  ← No dependencies (foundational)
└─────────────────┘
```

### Cross-Template Dependencies

Defined in `dependencies.yaml`:

```yaml
phase-template:
  requires:
    - workstream-template
    - task-template
  optional:
    - constraints-template

workstream-template:
  requires:
    - task-template
    - dag-template
  optional:
    - adapter-template

adapter-template:
  requires:
    - router-config-template
```

---

## 🎯 Navigation Patterns

### For AI Tools

AI tools can infer structure from paths:

```python
# Pattern recognition examples
"templates/orchestration/phases/" → "This contains phase definitions"
"templates/adapters/subprocess/" → "This contains CLI tool wrappers"
"templates/configuration/profiles/" → "This contains project configs"
"templates/ui/dashboards/" → "This contains UI layouts"
```

**Inference Rules**:
1. Top-level dir = architectural layer
2. Second level = component category
3. Third level = specific templates

### For Human Users

**By Use Case**: Navigate via README.md quick links
**By Category**: Browse subdirectory structure
**By Example**: Start with `examples/` and work backward

### Entry Points

1. **Quick Start**: `templates/README.md`
2. **Detailed Structure**: `templates/STRUCTURE.md` (this file)
3. **Context & Usage**: `templates/CONTEXT.md`
4. **Examples**: `templates/examples/README.md`
5. **Category-Specific**: `templates/{layer}/README.md`

---

## 📋 Manifest Files

Every directory level has documentation:

### Root Level
- `README.md` - Overview and quick start
- `STRUCTURE.md` - Structural organization
- `CONTEXT.md` - Execution context
- `dependencies.yaml` - Dependency graph

### Layer Level (e.g., `orchestration/`)
- `README.md` - Layer purpose and component list
- `INTERFACE.md` - Public interface definitions
- Local index files where applicable

### Category Level (e.g., `orchestration/phases/`)
- `README.md` - Component guide and usage
- Template files with inline documentation

---

## 🏗️ Template File Structure

### Standard Template Format

```yaml
# Template Header (REQUIRED)
# Template: {Name}
# Purpose: {One-line description}
# Version: {Version number}
# Schema: {Reference to JSON schema}
# Dependencies: {List of required components}
# Last Updated: {Date}

# Configuration Section
{template_id}: "{{TEMPLATE_ID}}"
description: "{{DESCRIPTION}}"

# Main Content
# (Structured according to schema)

# Validation Section
# (Reference validation rules)

# Example Section
# Example usage:
# {Realistic example with actual values}
```

### Placeholder Convention

All customizable values use `{{DOUBLE_BRACES}}`:

```yaml
phase_id: "{{PHASE_ID}}"           # User must replace
description: "{{DESCRIPTION}}"      # User must replace
version: "1.0.0"                    # Default provided
```

---

## ✅ Quality Standards

### Every Template Must Have

1. **Header Comment Block**: Purpose, version, schema, dependencies
2. **Documented Placeholders**: Clear explanation of `{{VARIABLES}}`
3. **Default Values**: Sensible defaults where applicable
4. **Example Section**: Realistic usage example
5. **Validation Reference**: Link to JSON schema
6. **Related Links**: Links to specs, docs, related templates

### Every Directory Must Have

1. **README.md**: Purpose, component list, usage guide
2. **Clear Naming**: Descriptive, consistent directory names
3. **Logical Grouping**: Related templates grouped together
4. **Navigation Aids**: Links to parent and child directories

---

## 🔄 Maintenance

### Adding New Templates

1. **Determine Layer**: Which architectural layer?
2. **Choose Category**: Which existing category or new one?
3. **Follow Naming**: Use standard naming convention
4. **Add Documentation**: Header comments and README updates
5. **Update Dependencies**: Add to dependencies.yaml
6. **Add Example**: Include usage example
7. **Validate**: Run validation scripts

### Deprecating Templates

1. **Mark as Deprecated**: Add deprecation notice
2. **Provide Alternative**: Link to replacement template
3. **Maintain Backward Compatibility**: Don't remove immediately
4. **Update Documentation**: Update README and STRUCTURE.md
5. **Migration Guide**: Provide migration path

---

## 📊 Metrics and Monitoring

### Template Usage Tracking

Templates can include usage tracking metadata:

```yaml
# Template Metadata (Optional)
meta:
  template_id: "phase-core-v1"
  created: "2025-11-23"
  last_modified: "2025-11-23"
  usage_count: 0  # Auto-updated by framework
  success_rate: 0.0  # Auto-updated by framework
```

### Quality Metrics

- **Completeness**: All required sections present
- **Documentation Coverage**: Header, examples, validation
- **Usage**: How often template is used
- **Success Rate**: Validation pass rate

---

## 🔍 Discoverability Features

### Index Files

Python-style index files for programmatic access:

```python
# templates/__init__.py
from .orchestration import phase_templates, workstream_templates
from .adapters import subprocess_adapters, api_adapters
from .configuration import profile_templates, router_templates

__all__ = [
    'phase_templates',
    'workstream_templates',
    'subprocess_adapters',
    # ...
]
```

### Conventional Entry Points

Standard entry points for common operations:

- `templates/orchestration/phases/phase-core-template.yaml` - Default phase
- `templates/configuration/profiles/profile-generic-template.yaml` - Default profile
- `templates/adapters/subprocess/tool-adapter-template.py` - Default adapter

### Search Metadata

Templates include searchable metadata:

```yaml
meta:
  tags: ["phase", "core", "analysis"]
  keywords: ["discovery", "planning", "requirements"]
  use_cases: ["new project", "analysis phase", "discovery"]
  difficulty: "beginner"  # beginner | intermediate | advanced
```

---

## 🎨 Design Decisions

### Why Layer-Based Organization?

**Decision**: Organize by architectural layer (orchestration, adapters, config, ui)
**Rationale**:
- Mirrors execution architecture
- Clear dependency flow
- Predictable navigation
- Separation of concerns

**Alternative Considered**: Organize by use case (new-project, add-tool, create-phase)
**Why Not**: Less clear boundaries, harder to maintain, duplicate templates

### Why Manifest Files Everywhere?

**Decision**: Every directory has README.md explaining contents
**Rationale**:
- Self-documenting structure
- Context for AI tools
- Onboarding for new users
- Single source of truth per directory

**Alternative Considered**: Single top-level documentation
**Why Not**: Harder to navigate, context lost, harder to maintain

### Why Examples Separate from Templates?

**Decision**: `examples/` separate from template categories
**Rationale**:
- Examples combine multiple templates
- Different purpose (learning vs. reuse)
- Complete working implementations
- Easier to run and test

**Alternative Considered**: Examples inline with templates
**Why Not**: Mixes learning materials with components, clutters template dirs

---

## 📚 Related Documentation

- **[Main README](README.md)** - Quick start and overview
- **[CONTEXT.md](CONTEXT.md)** - Execution model and context management
- **[dependencies.yaml](dependencies.yaml)** - Dependency graph
- **[UET Framework Docs](../docs/)** - Framework documentation
- **[UET Specifications](../specs/)** - Detailed specifications

---

**Last Updated**: 2025-11-23
**Maintained By**: UET Framework Team
**Feedback**: Submit issues or PRs with suggested improvements
