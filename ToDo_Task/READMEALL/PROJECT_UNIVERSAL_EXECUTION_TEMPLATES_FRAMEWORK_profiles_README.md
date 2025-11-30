---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1600
---

# Project Profiles

Pre-built configuration templates for different project types. Each profile contains tool routing, phase definitions, and domain-specific workflows.

## Available Profiles

### software-dev-python/
**When to use**: Python projects with testing, linting, code editing needs

**Languages**: Python (primary)

**Tools**: 
- **Code editing**: aider, cursor
- **Testing**: pytest, unittest
- **Linting**: ruff, pylint, black
- **Type checking**: mypy, pyright
- **Version control**: git

**Phases**:
1. **analyze** - Code analysis, dependency checking
2. **implement** - Code editing, refactoring
3. **test** - Unit testing, integration testing
4. **integrate** - Git operations, CI integration

**Typical use cases**:
- Web applications (Flask, Django, FastAPI)
- CLI tools
- Libraries and packages
- API services

**Example project structures**:
```
project/
├── src/ or app/
├── tests/
├── requirements.txt or pyproject.toml
├── setup.py (optional)
└── README.md
```

**Learn more**: See `profiles/software-dev-python/README.md`

---

### data-pipeline/
**When to use**: ETL/ML pipelines, data processing, analytics workflows

**Languages**: Python, SQL

**Tools**:
- **Data processing**: pandas, polars, dask
- **Orchestration**: airflow, prefect, dagster
- **Testing**: pytest, great_expectations
- **SQL**: dbt, sqlfluff
- **Notebooks**: jupyter, papermill

**Phases**:
1. **extract** - Data ingestion, source connections
2. **transform** - Data transformation, cleaning
3. **validate** - Data quality checks, schema validation
4. **load** - Data loading, warehouse operations

**Typical use cases**:
- ETL pipelines
- ML model training pipelines
- Data validation workflows
- Analytics dashboards

**Example project structures**:
```
project/
├── dags/ or workflows/
├── sql/
├── notebooks/
├── tests/
└── config/
```

---

### documentation/
**When to use**: Documentation projects, technical writing, content management

**Languages**: Markdown, reStructuredText

**Tools**:
- **Generators**: mkdocs, sphinx, docusaurus
- **Linting**: markdownlint, vale
- **Formatting**: prettier
- **Link checking**: linkchecker

**Phases**:
1. **draft** - Content creation, writing
2. **review** - Proofreading, style checking
3. **build** - Static site generation
4. **publish** - Deployment, hosting

**Typical use cases**:
- Project documentation
- Technical blogs
- API documentation
- User guides

**Example project structures**:
```
project/
├── docs/
├── mkdocs.yml or conf.py
├── README.md
└── assets/
```

---

### operations/
**When to use**: DevOps, SRE, infrastructure management, automation

**Languages**: YAML, HCL (Terraform), Shell

**Tools**:
- **IaC**: terraform, pulumi, cloudformation
- **Config management**: ansible, chef, puppet
- **Containers**: docker, docker-compose, kubernetes
- **CI/CD**: github-actions, gitlab-ci, jenkins
- **Monitoring**: prometheus, grafana

**Phases**:
1. **plan** - Infrastructure planning, design
2. **provision** - Resource creation, configuration
3. **validate** - Testing, security scanning
4. **deploy** - Application deployment, rollout

**Typical use cases**:
- Infrastructure as Code
- CI/CD pipelines
- Kubernetes manifests
- Ansible playbooks

**Example project structures**:
```
project/
├── terraform/ or ansible/
├── .github/workflows/
├── docker/
├── k8s/
└── scripts/
```

---

### generic/
**When to use**: Multi-language projects, custom workflows, mixed technology stacks

**Languages**: Any (auto-detected)

**Tools**: Universal tools that work across languages
- **Version control**: git
- **Formatting**: prettier (JS/TS/JSON/MD), black (Python)
- **Linting**: configured based on detected languages
- **Testing**: configured based on detected frameworks

**Phases**: Customizable based on project needs

**Typical use cases**:
- Monorepos with multiple languages
- Prototype/experimental projects
- Projects with custom build systems
- Mixed frontend/backend applications

**Example project structures**: Any structure

---

## Profile Structure

Each profile directory contains:

```
profile-name/
├── profile.json           # Profile metadata and configuration
├── router_config.json     # Tool routing rules
├── phases/               # Phase definitions
│   ├── analyze.json
│   ├── implement.json
│   └── test.json
├── templates/            # Optional templates
│   ├── workflow.yaml
│   └── tasks.json
└── README.md             # Profile documentation
```

### profile.json
Defines profile metadata:
```json
{
  "name": "software-dev-python",
  "version": "1.0.0",
  "description": "Python software development",
  "languages": ["python"],
  "frameworks": ["pytest", "flask", "django"],
  "phases": ["analyze", "implement", "test", "integrate"],
  "constraints": {
    "max_parallel_tasks": 3,
    "timeout_default": 300
  }
}
```

### router_config.json
Defines tool routing:
```json
{
  "tools": {
    "aider": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python", "code"],
        "actions": ["edit", "refactor"]
      }
    }
  },
  "routing_rules": {
    "python_code_edit": ["aider"],
    "python_testing": ["pytest"]
  }
}
```

### phases/
Contains phase definitions:
```json
{
  "name": "implement",
  "description": "Implementation phase",
  "inputs": {
    "required": ["analysis_results"]
  },
  "outputs": {
    "artifacts": ["source_code", "tests"]
  },
  "workstreams": [
    {
      "name": "code_editing",
      "tasks": [...]
    }
  ]
}
```

## Profile Selection

The bootstrap process selects profiles based on:

1. **Explicit override**: `--profile` flag
2. **Language detection**: Dominant language percentage
3. **Framework detection**: Detected frameworks
4. **Project structure**: Directory patterns
5. **Tool presence**: Available tools in project

### Selection Algorithm

```python
if python_detected and testing_framework:
    if pandas or pyspark or airflow:
        return "data-pipeline"
    else:
        return "software-dev-python"
elif markdown_detected and (mkdocs or sphinx):
    return "documentation"
elif terraform or ansible:
    return "operations"
else:
    return "generic"
```

## Creating a Custom Profile

### Step 1: Create Directory
```bash
mkdir profiles/my-profile
cd profiles/my-profile
```

### Step 2: Create profile.json
```json
{
  "name": "my-profile",
  "version": "1.0.0",
  "description": "My custom profile",
  "languages": ["javascript", "typescript"],
  "frameworks": ["react", "jest"],
  "phases": ["analyze", "build", "test", "deploy"]
}
```

### Step 3: Create router_config.json
```json
{
  "tools": {
    "eslint": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["javascript", "code"],
        "actions": ["lint"]
      },
      "config": {
        "command": "eslint",
        "args": ["--fix"]
      }
    },
    "jest": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["javascript", "testing"],
        "actions": ["test"]
      }
    }
  },
  "routing_rules": {
    "javascript_lint": ["eslint"],
    "javascript_test": ["jest"]
  }
}
```

### Step 4: Create Phase Definitions
```bash
mkdir phases
# Create analyze.json, build.json, test.json, deploy.json
```

### Step 5: Document
```bash
# Create README.md with usage guide
```

### Step 6: Use Profile
```bash
python core/bootstrap/orchestrator.py /path/to/project --profile my-profile
```

## Profile Inheritance

Profiles can inherit from other profiles:

```json
{
  "name": "my-python-profile",
  "extends": "software-dev-python",
  "overrides": {
    "tools": {
      "my_custom_tool": {...}
    }
  }
}
```

## Profile Validation

Validate a profile before use:

```bash
python scripts/validate_profile.py profiles/my-profile
```

Expected output:
```
✓ profile.json valid
✓ router_config.json valid
✓ All phase definitions valid
✓ All referenced tools available
Profile 'my-profile' is valid
```

## Profile Migration

When schemas change, migrate profiles:

```bash
python scripts/migrate_profile.py \
  --profile profiles/my-profile \
  --from-version 1.0 \
  --to-version 2.0
```

## Common Customizations

### Add a Tool
Edit `router_config.json`:
```json
{
  "tools": {
    "new_tool": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python"],
        "actions": ["custom_action"]
      }
    }
  }
}
```

### Add a Phase
Create `phases/new_phase.json`:
```json
{
  "name": "new_phase",
  "description": "Custom phase",
  "workstreams": [...]
}
```

Update `profile.json`:
```json
{
  "phases": ["analyze", "implement", "test", "new_phase"]
}
```

### Modify Constraints
Edit `profile.json`:
```json
{
  "constraints": {
    "max_parallel_tasks": 5,
    "timeout_default": 600,
    "retry_max": 5
  }
}
```

## Testing Profiles

Test a profile against a sample project:

```bash
# Bootstrap test project
python core/bootstrap/orchestrator.py \
  test_projects/python_sample \
  --profile software-dev-python \
  --dry-run

# Verify generated artifacts
cat test_projects/python_sample/.uet/PROJECT_PROFILE.yaml
```

## References

- **Bootstrap specification**: `specs/UET_BOOTSTRAP_SPEC.md`
- **Profile schema**: `schema/profile.v1.json`
- **Router config schema**: `schema/router_config.v1.json`
- **Example profile**: `profiles/software-dev-python/`
