---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1608
---

# UET Framework Templates

> **Universal Execution Templates - Reusable Components for AI Development Pipelines**  
> **Last Updated**: 2025-11-23  
> **Version**: 1.0.0

---

## 📋 Overview

This directory contains reusable templates for the Universal Execution Templates (UET) Framework. These templates provide starting points for common pipeline components, following AI-codebase structure principles for maximum discoverability and maintainability.

### Purpose

The templates directory serves as a **single source of truth** for:
- Project configuration templates
- Orchestration patterns (phases, workstreams, DAGs)
- Tool adapter implementations
- UI/dashboard components
- Example implementations

### Design Principles

1. **Explicit Hierarchy**: Directory structure mirrors architectural layers
2. **Self-Documenting**: Each directory has clear documentation
3. **Consistent Naming**: Same operations use same naming patterns
4. **Single Responsibility**: Each template focuses on one concept
5. **Dependency Declarations**: Clear dependency metadata
6. **Discoverability**: Index files and conventional entry points

---

## 🗂️ Directory Structure

```
templates/
├── README.md                    # This file - master template index
├── STRUCTURE.md                 # Detailed organization guide
├── CONTEXT.md                   # Execution model and usage patterns
├── dependencies.yaml            # Template dependencies
│
├── orchestration/              # 📊 Orchestration & Workflow Templates
│   ├── README.md               # Orchestration template guide
│   ├── phases/                 # Phase specification templates
│   ├── workstreams/            # Workstream bundle templates
│   ├── dags/                   # DAG definition templates
│   └── tasks/                  # Task specification templates
│
├── adapters/                   # 🔌 Tool Adapter Templates
│   ├── README.md               # Adapter template guide
│   ├── subprocess/             # Subprocess-based adapters
│   ├── api/                    # API-based adapters
│   └── custom/                 # Custom adapter templates
│
├── configuration/              # ⚙️ Configuration Templates
│   ├── README.md               # Configuration template guide
│   ├── profiles/               # Project profile templates
│   ├── routers/                # Router configuration templates
│   └── constraints/            # Constraint definition templates
│
├── ui/                         # 🎨 UI Component Templates
│   ├── README.md               # UI template guide
│   ├── dashboards/             # Dashboard layout templates
│   ├── reports/                # Report generation templates
│   └── monitoring/             # Monitoring view templates
│
└── examples/                   # 📚 Complete Example Implementations
    ├── README.md               # Examples guide
    ├── simple-pipeline/        # Minimal working example
    ├── multi-phase/            # Multi-phase workflow example
    └── advanced/               # Advanced patterns example
```

---

## 🚀 Quick Start

### Using Templates

1. **Browse by Category**: Navigate to the appropriate subdirectory
2. **Read Documentation**: Check the local README.md for usage instructions
3. **Copy Template**: Copy the template file to your project
4. **Customize**: Modify placeholders and configuration
5. **Validate**: Use UET validation tools to verify

### Example: Creating a New Phase Template

```bash
# 1. Navigate to orchestration templates
cd templates/orchestration/phases/

# 2. Copy a base template
cp phase-template.yaml my-new-phase.yaml

# 3. Edit the template
# Replace placeholders: {{PHASE_ID}}, {{DESCRIPTION}}, etc.

# 4. Validate
python ../../core/bootstrap/validator.py my-new-phase.yaml
```

### Example: Creating a Tool Adapter

```bash
# 1. Navigate to adapter templates
cd templates/adapters/subprocess/

# 2. Copy the template
cp tool-adapter-template.py my_tool_adapter.py

# 3. Implement required methods
# - detect_capabilities()
# - execute()
# - validate_result()

# 4. Register in adapter registry
```

---

## 📖 Template Categories

### 1. Orchestration Templates (`orchestration/`)

**Purpose**: Define workflow structure and execution patterns

**Use Cases**:
- Creating new phase specifications
- Defining workstream bundles
- Building task DAGs
- Configuring execution order

**Key Templates**:
- `phase-template.yaml` - Phase specification
- `workstream-bundle-template.json` - Workstream bundle
- `dag-template.yaml` - Dependency graph
- `task-template.yaml` - Task definition

**See**: [orchestration/README.md](orchestration/README.md)

---

### 2. Adapter Templates (`adapters/`)

**Purpose**: Integrate external tools and services

**Use Cases**:
- Adding new CLI tool support
- Integrating REST APIs
- Creating custom tool wrappers
- Implementing retry/resilience patterns

**Key Templates**:
- `subprocess-adapter-template.py` - CLI tool wrapper
- `api-adapter-template.py` - REST API client
- `custom-adapter-template.py` - Custom integration

**See**: [adapters/README.md](adapters/README.md)

---

### 3. Configuration Templates (`configuration/`)

**Purpose**: Project and runtime configuration

**Use Cases**:
- Bootstrapping new projects
- Defining tool routing
- Setting up constraints
- Configuring execution policies

**Key Templates**:
- `project-profile-template.yaml` - Project configuration
- `router-config-template.json` - Tool routing rules
- `constraints-template.yaml` - Execution constraints

**See**: [configuration/README.md](configuration/README.md)

---

### 4. UI Templates (`ui/`)

**Purpose**: User interface and reporting components

**Use Cases**:
- Creating dashboards
- Generating reports
- Building monitoring views
- Visualizing progress

**Key Templates**:
- `dashboard-template.html` - Dashboard layout
- `report-template.md` - Report format
- `monitoring-view-template.json` - Monitor config

**See**: [ui/README.md](ui/README.md)

---

### 5. Examples (`examples/`)

**Purpose**: Complete working implementations

**Use Cases**:
- Learning UET patterns
- Starting new projects
- Reference implementations
- Testing new features

**Key Examples**:
- `simple-pipeline/` - Minimal example
- `multi-phase/` - Complex workflow
- `advanced/` - Advanced patterns

**See**: [examples/README.md](examples/README.md)

---

## 🔍 Finding the Right Template

### By Use Case

| I want to... | Use Template | Location |
|--------------|-------------|----------|
| Create a new execution phase | Phase Template | `orchestration/phases/` |
| Add a new CLI tool | Subprocess Adapter | `adapters/subprocess/` |
| Configure a new project | Project Profile | `configuration/profiles/` |
| Build a monitoring dashboard | Dashboard Template | `ui/dashboards/` |
| See a complete example | Simple Pipeline | `examples/simple-pipeline/` |

### By Architecture Layer

| Layer | Templates | Purpose |
|-------|-----------|---------|
| **Orchestration** | `orchestration/` | Workflow definition |
| **Adapters** | `adapters/` | Tool integration |
| **Configuration** | `configuration/` | Project setup |
| **UI** | `ui/` | User interface |
| **Examples** | `examples/` | Reference implementations |

---

## 📚 Documentation

### Core Documents

- **[STRUCTURE.md](STRUCTURE.md)** - Detailed structural organization
- **[CONTEXT.md](CONTEXT.md)** - Execution model and context management
- **[dependencies.yaml](dependencies.yaml)** - Template dependency graph

### Related Documentation

- **[UET Framework README](../README.md)** - Main framework documentation
- **[UET Specifications](../specs/)** - Detailed specifications
- **[UET Schemas](../schema/)** - JSON schemas for validation
- **[UET Profiles](../profiles/)** - Project type profiles

---

## 🎯 Template Naming Conventions

### File Naming Pattern

```
{component-type}-{variant}-template.{extension}

Examples:
- phase-core-template.yaml
- workstream-parallel-template.json
- adapter-subprocess-template.py
- dashboard-progress-template.html
```

### Directory Naming Pattern

```
{layer}/{category}/{subcategory}/

Examples:
- orchestration/phases/
- adapters/subprocess/
- configuration/profiles/
- ui/dashboards/
```

---

## ✅ Template Quality Standards

All templates must:

1. **Include Header Comments**: Explain purpose, usage, and parameters
2. **Provide Examples**: Show realistic usage scenarios
3. **Document Placeholders**: Clear `{{PLACEHOLDER}}` syntax
4. **Include Validation**: Reference validation schemas
5. **Show Dependencies**: List required components
6. **Link to Specs**: Reference relevant specifications

### Template Checklist

```markdown
- [ ] Header comment with purpose and usage
- [ ] All placeholders documented
- [ ] Example values provided
- [ ] Validation schema referenced
- [ ] Dependencies listed
- [ ] Related specs linked
- [ ] Test example included
```

---

## 🔗 Integration Points

### With UET Framework Components

Templates integrate with:
- **Bootstrap System**: Used during project initialization
- **Orchestration Engine**: Loaded at runtime for execution
- **Tool Adapters**: Implement adapter interface
- **Validation System**: Validated against JSON schemas
- **Documentation**: Referenced in specs and guides

### With External Systems

Templates support:
- **Version Control**: Git-friendly formats
- **CI/CD**: Automated validation and deployment
- **IDEs**: Syntax highlighting and autocomplete
- **AI Tools**: Machine-readable structure

---

## 🛠️ Contributing Templates

### Adding a New Template

1. **Choose Category**: Select appropriate subdirectory
2. **Follow Naming Convention**: Use standard naming pattern
3. **Add Documentation**: Include header comments and examples
4. **Update Index**: Add entry to category README.md
5. **Validate**: Run validation scripts
6. **Submit PR**: Include usage example and tests

### Template Guidelines

- **Keep It Simple**: Focus on one concept per template
- **Use Clear Placeholders**: `{{VARIABLE}}` format
- **Provide Defaults**: Sensible default values
- **Document Thoroughly**: Explain non-obvious choices
- **Link to Specs**: Reference canonical specifications

---

## 📞 Support

### Getting Help

- **Documentation**: Check category-specific README.md
- **Examples**: Review working examples in `examples/`
- **Specifications**: Consult [UET Specs](../specs/)
- **Issues**: Report problems via GitHub issues

### Common Questions

**Q: Which template should I use?**  
A: See [Finding the Right Template](#-finding-the-right-template)

**Q: How do I customize a template?**  
A: Copy the template, replace `{{PLACEHOLDERS}}`, validate with schemas

**Q: Can I create my own templates?**  
A: Yes! Follow [Contributing Templates](#-contributing-templates) guidelines

---

## 📄 License

Templates are part of the UET Framework and follow the same license.

---

**Built with**: AI-Codebase Structure Principles  
**Status**: Initial Release (v1.0.0)  
**Next**: Expand template library with community contributions
