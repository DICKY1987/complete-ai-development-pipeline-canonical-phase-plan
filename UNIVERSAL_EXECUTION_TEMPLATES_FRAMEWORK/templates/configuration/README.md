# Configuration Templates

> **Project and Runtime Configuration Templates**  
> **Purpose**: Define project setup and execution policies  
> **Layer**: Configuration (Foundation)

---

## 📋 Overview

Configuration templates provide starting points for project profiles, tool routing rules, and execution constraints. They define how projects are configured and how the framework behaves at runtime.

### What's in This Directory

```
configuration/
├── README.md                    # This file
├── SCHEMA_REFERENCE.md          # Configuration schema reference
│
├── profiles/                    # Project profile templates
├── routers/                     # Tool routing templates
└── constraints/                 # Execution constraint templates
```

---

## 🎯 Template Categories

### 1. Project Profiles (`profiles/`)

**Purpose**: Define project type and tools

**Use Cases**:
- Python software projects
- Data pipeline projects
- Documentation projects
- Generic/unknown projects

**Key Templates**:
- `profile-python-template.yaml` - Python project configuration
- `profile-data-template.yaml` - Data pipeline configuration
- `profile-docs-template.yaml` - Documentation project
- `profile-generic-template.yaml` - Generic/fallback profile

**Example**:
```yaml
# profile-python-template.yaml
profile_id: "software-dev-python"
domain: "software-dev"
languages: ["python"]
tools:
  code_edit: ["aider"]
  testing: ["pytest"]
  linting: ["ruff", "mypy"]
```

---

### 2. Router Configurations (`routers/`)

**Purpose**: Define tool selection rules

**Use Cases**:
- Simple single-tool routing
- Multi-tool fallback routing
- Capability-based selection

**Key Templates**:
- `router-basic-template.json` - Simple tool routing
- `router-multi-tool-template.json` - Multiple tool options
- `router-fallback-template.json` - Fallback mechanisms

**Example**:
```json
{
  "routes": [
    {
      "capability": "code_edit",
      "tools": ["aider"],
      "fallback": "manual"
    }
  ]
}
```

---

### 3. Constraints (`constraints/`)

**Purpose**: Define execution limits and policies

**Use Cases**:
- Time-limited execution
- Resource constraints (CPU, memory)
- Quality gates and thresholds

**Key Templates**:
- `constraints-time-template.yaml` - Time limits
- `constraints-resource-template.yaml` - Resource limits
- `constraints-quality-template.yaml` - Quality gates

**Example**:
```yaml
# constraints-time-template.yaml
constraints:
  time:
    max_phase_duration: 3600  # 1 hour
    max_task_duration: 600    # 10 minutes
    timeout_action: "abort"
```

---

## 🚀 Quick Start

### Creating a Project Profile

```bash
# 1. Copy template for your project type
cp templates/configuration/profiles/profile-python-template.yaml \
   PROJECT_PROFILE.yaml

# 2. Customize
# - Set project_id
# - List your tools
# - Define constraints

# 3. Validate
python core/bootstrap/validator.py \
  --schema schema/project_profile.v1.json \
  --file PROJECT_PROFILE.yaml
```

### Creating a Router Config

```bash
# 1. Copy template
cp templates/configuration/routers/router-basic-template.json \
   router_config.json

# 2. Define routes
# - Map capabilities to tools
# - Set fallback behaviors

# 3. Test
python -c "import json; json.load(open('router_config.json'))"
```

### Defining Constraints

```bash
# 1. Copy constraint template
cp templates/configuration/constraints/constraints-time-template.yaml \
   constraints.yaml

# 2. Set limits
# - Timeouts
# - Retry policies
# - Failure thresholds

# 3. Include in profile
# Reference in PROJECT_PROFILE.yaml
```

---

## 📐 Profile Structure

### Complete Profile Example

```yaml
# PROJECT_PROFILE.yaml
profile_id: "my-python-project"
profile_version: "1.0.0"
domain: "software-dev"

# Project metadata
project:
  name: "My Python Project"
  type: "python"
  description: "Example Python application"

# Languages and frameworks
languages:
  primary: "python"
  others: ["yaml", "markdown"]

frameworks:
  - "pytest"
  - "fastapi"

# Tool configuration
tools:
  code_edit:
    - name: "aider"
      version: ">=0.40.0"
      config: ".aider.conf.yml"
  
  testing:
    - name: "pytest"
      version: ">=7.0.0"
      config: "pytest.ini"
  
  linting:
    - name: "ruff"
      version: ">=0.1.0"
    - name: "mypy"
      version: ">=1.0.0"

# Execution constraints
constraints:
  time:
    max_phase_duration: 3600
    max_task_duration: 600
  
  resources:
    max_parallel_tasks: 3
    max_memory_mb: 4096
  
  quality:
    min_test_coverage: 80
    max_lint_errors: 0

# File patterns
file_patterns:
  source: ["src/**/*.py"]
  tests: ["tests/**/*.py"]
  config: ["*.yaml", "*.toml", "*.ini"]

# Dependencies
dependencies:
  - "pytest>=7.0.0"
  - "ruff>=0.1.0"
```

---

## 🔧 Router Configuration

### Router Structure

```json
{
  "router_id": "default-router",
  "version": "1.0.0",
  
  "routes": [
    {
      "capability": "code_edit",
      "tools": [
        {
          "name": "aider",
          "priority": 1,
          "conditions": {
            "languages": ["python", "javascript"]
          }
        }
      ],
      "fallback": "manual"
    },
    
    {
      "capability": "testing",
      "tools": [
        {
          "name": "pytest",
          "priority": 1,
          "conditions": {
            "languages": ["python"]
          }
        }
      ]
    }
  ],
  
  "global_settings": {
    "max_retries": 3,
    "timeout": 300,
    "fallback_behavior": "fail"
  }
}
```

### Routing Logic

1. **Capability Match**: Find routes for required capability
2. **Condition Check**: Verify tool conditions (language, etc.)
3. **Priority Order**: Select highest priority available tool
4. **Fallback**: Use fallback if primary fails

---

## 🎯 Bootstrap Process

### How Profiles Are Used

```python
from core.bootstrap.orchestrator import BootstrapOrchestrator

# 1. Scan project
bootstrap = BootstrapOrchestrator("/path/to/project")

# 2. Detect project type
project_type = bootstrap.detect_project_type()
# Returns: "python", "data-pipeline", "documentation", etc.

# 3. Select profile template
template = bootstrap.select_profile_template(project_type)
# Returns path to appropriate template

# 4. Instantiate profile
profile = bootstrap.instantiate_profile(template)
# Generates PROJECT_PROFILE.yaml

# 5. Generate router config
router = bootstrap.generate_router_config(profile)
# Generates router_config.json
```

---

## ✅ Validation

### Profile Validation

```bash
# Validate against schema
python core/bootstrap/validator.py \
  --schema schema/project_profile.v1.json \
  --file PROJECT_PROFILE.yaml

# Check tool availability
python scripts/check_tool_availability.py \
  --profile PROJECT_PROFILE.yaml
```

### Router Validation

```bash
# Validate JSON structure
python core/bootstrap/validator.py \
  --schema schema/router_config.v1.json \
  --file router_config.json

# Test routing logic
python scripts/test_router.py \
  --config router_config.json \
  --capability code_edit
```

---

## 🎓 Best Practices

### Profile Organization

- **One profile per project**: Don't share profiles
- **Version your profile**: Track changes over time
- **Document customizations**: Comment non-obvious choices
- **Keep tools updated**: Review tool versions regularly

### Router Design

- **Prefer explicit over implicit**: List tools explicitly
- **Define clear fallbacks**: What happens when tools fail?
- **Test routing logic**: Verify expected tool selection
- **Use conditions wisely**: Don't over-complicate

### Constraints

- **Be realistic**: Set achievable limits
- **Monitor and adjust**: Review constraint violations
- **Document rationale**: Why these limits?
- **Environment-specific**: Dev vs. prod constraints

---

## 📚 Related Documentation

- **[Templates Main README](../README.md)** - Overview
- **[SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md)** - Schema details
- **[Orchestration Templates](../orchestration/README.md)** - Workflow definition
- **[UET Bootstrap Spec](../../specs/UET_BOOTSTRAP_SPEC.md)** - Bootstrap process

---

## 📞 Support

**Q: How do I create a profile for my project?**  
A: Run `python core/bootstrap/orchestrator.py /path/to/project` for automatic detection, or copy the appropriate template.

**Q: What if my project uses multiple languages?**  
A: Use `profile-generic-template.yaml` and list all languages in `languages.others`.

**Q: How do I add a new tool?**  
A: Add it to `tools` section in profile and create routing entry in router config.

---

**Last Updated**: 2025-11-23  
**Related**: [Adapter Templates](../adapters/README.md), [Examples](../examples/README.md)
