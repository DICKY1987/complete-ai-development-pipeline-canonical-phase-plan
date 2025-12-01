---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1594
---

# core/bootstrap

**Purpose**: Autonomous project discovery and configuration system that analyzes any project and generates appropriate UET configuration.

## Overview

The bootstrap module enables UET to automatically configure itself for any project by:
1. Scanning project structure and detecting technologies
2. Selecting the best-matching profile
3. Generating PROJECT_PROFILE.yaml and router_config.json
4. Validating all generated artifacts

## Key Files

- **`orchestrator.py`** - Main entry point; coordinates entire bootstrap process
- **`scanner.py`** - Project structure analysis and technology detection
- **`profile_selector.py`** - Matches projects to appropriate profiles
- **`artifact_generator.py`** - Generates configuration files from templates
- **`validator.py`** - Validates generated artifacts against schemas

## Dependencies

**Depends on:**
- `schema/` - For profile.v1.json and router_config.v1.json validation
- `core/state/` - For tracking bootstrap execution state
- `profiles/` - For project type templates

**Used by:**
- CLI entry points
- External orchestration systems

## Usage

### CLI
```bash
# Auto-detect and bootstrap
python core/bootstrap/orchestrator.py /path/to/project

# Specify profile explicitly
python core/bootstrap/orchestrator.py /path/to/project --profile software-dev-python

# Dry-run (show what would be generated)
python core/bootstrap/orchestrator.py /path/to/project --dry-run
```

### Programmatic API
```python
from core.bootstrap.orchestrator import BootstrapOrchestrator

# Basic usage
orchestrator = BootstrapOrchestrator("/path/to/project")
result = orchestrator.run()

if result.success:
    print(f"Generated profile: {result.profile_name}")
    print(f"Config written to: {result.config_path}")
else:
    print(f"Bootstrap failed: {result.error}")

# With options
orchestrator = BootstrapOrchestrator(
    project_path="/path/to/project",
    profile_override="software-dev-python",
    output_dir="/custom/output"
)
```

## Bootstrap Process

```
1. SCAN
   ProjectScanner.scan(project_path)
   └─> Detects: languages, frameworks, tools, structure
   
2. SELECT
   ProfileSelector.select(scan_results)
   └─> Chooses best profile from: python, data, docs, ops, generic
   
3. GENERATE
   ArtifactGenerator.generate(profile, scan_results)
   └─> Creates: PROJECT_PROFILE.yaml, router_config.json
   
4. VALIDATE
   Validator.validate(artifacts)
   └─> Checks against JSON schemas
   
5. PERSIST
   Write artifacts to project directory
   └─> Creates: .uet/ directory with config files
```

## Project Scanner

Detects project characteristics:

**Languages detected:**
- Python (*.py, requirements.txt, setup.py, pyproject.toml)
- JavaScript/TypeScript (*.js, *.ts, package.json)
- Go (*.go, go.mod)
- Rust (*.rs, Cargo.toml)
- Java (*.java, pom.xml, build.gradle)

**Frameworks detected:**
- Web: Flask, Django, FastAPI, Express, React, Vue
- Data: Pandas, PySpark, Airflow, DBT
- Testing: pytest, unittest, jest, JUnit
- Docs: MkDocs, Sphinx, Docusaurus

**Tools detected:**
- Version control: git
- Package managers: pip, npm, yarn, cargo, go mod
- Linters: ruff, eslint, pylint, black
- Build systems: Make, CMake, Gradle, Maven

## Profile Selection Logic

```python
# Selection criteria (in priority order):
1. Explicit --profile flag (user override)
2. Dominant language + framework combination
3. Project structure patterns
4. Tool presence
5. Fallback to 'generic' profile

# Example decision tree:
if python_detected and (pytest or unittest) and (flask or django):
    return "software-dev-python"
elif python_detected and (pandas or pyspark or airflow):
    return "data-pipeline"
elif markdown_detected and (mkdocs or sphinx):
    return "documentation"
elif terraform_or_ansible_detected:
    return "operations"
else:
    return "generic"
```

## Generated Artifacts

### PROJECT_PROFILE.yaml
```yaml
profile_name: software-dev-python
version: 1.0.0
project_path: /path/to/project

detected_languages:
  - python: 95%
  - yaml: 5%

detected_frameworks:
  - pytest
  - flask

detected_tools:
  - git
  - ruff
  - mypy

phases:
  - name: analyze
    workstreams: [code_analysis, dependency_check]
  - name: implement
    workstreams: [code_edit, refactor]
  - name: test
    workstreams: [unit_test, integration_test]
```

### router_config.json
```json
{
  "tools": {
    "aider": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python", "code"],
        "actions": ["edit", "refactor"]
      },
      "config": {
        "max_retries": 3,
        "timeout": 300
      }
    },
    "pytest": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python", "testing"],
        "actions": ["test", "verify"]
      }
    }
  },
  "routing_rules": {
    "python_code_edit": ["aider"],
    "python_testing": ["pytest"]
  }
}
```

## Validation

All generated artifacts are validated against JSON schemas:

```python
from core.bootstrap.validator import Validator

validator = Validator()

# Validate profile
profile_valid = validator.validate_profile("PROJECT_PROFILE.yaml")

# Validate router config
router_valid = validator.validate_router_config("router_config.json")

# Get validation errors
if not profile_valid:
    errors = validator.get_errors()
    for error in errors:
        print(f"{error.path}: {error.message}")
```

## Error Handling

Bootstrap handles common failure scenarios:

**Project not found:**
```
BootstrapError: Project path '/path' does not exist
```

**No matching profile:**
```
BootstrapWarning: No specific profile matched, using 'generic'
```

**Schema validation failed:**
```
ValidationError: PROJECT_PROFILE.yaml invalid
  - phases.0.name: Required field missing
  - detected_languages: Must be non-empty
```

**Permission denied:**
```
BootstrapError: Cannot write to /path/.uet/ (permission denied)
```

## Extension Points

### Custom Scanners
```python
from core.bootstrap.scanner import ProjectScanner

class CustomScanner(ProjectScanner):
    def scan_custom_framework(self, project_path):
        # Your custom detection logic
        return framework_info

# Register scanner
orchestrator.register_scanner(CustomScanner())
```

### Custom Profile Selection
```python
from core.bootstrap.profile_selector import ProfileSelector

class CustomSelector(ProfileSelector):
    def select(self, scan_results):
        # Your custom selection logic
        return profile_name

# Use custom selector
orchestrator.profile_selector = CustomSelector()
```

## Testing

Test coverage: 8/8 tests passing

```bash
# Run bootstrap tests
pytest tests/bootstrap/ -v

# Specific test
pytest tests/bootstrap/test_orchestrator.py::test_basic_bootstrap -v

# Integration test (requires sample projects)
pytest tests/bootstrap/test_integration.py -v
```

## Common Use Cases

### Use Case 1: New Python Project
```bash
$ python core/bootstrap/orchestrator.py /new/python/project
Scanning project structure... ✓
Detected: Python 100%, pytest, no framework
Selected profile: software-dev-python
Generating artifacts... ✓
Validating... ✓
Bootstrap complete: /new/python/project/.uet/
```

### Use Case 2: Existing Multi-Language Project
```bash
$ python core/bootstrap/orchestrator.py /existing/project
Scanning project structure... ✓
Detected: Python 60%, JavaScript 30%, YAML 10%
Detected frameworks: FastAPI, React
Selected profile: generic (multi-language detected)
Generating artifacts... ✓
Bootstrap complete: /existing/project/.uet/
```

### Use Case 3: Force Specific Profile
```bash
$ python core/bootstrap/orchestrator.py /project --profile data-pipeline
Using profile: data-pipeline (user override)
Generating artifacts... ✓
Bootstrap complete: /project/.uet/
```

## References

- **Specification**: `specs/UET_BOOTSTRAP_SPEC.md`
- **Schemas**: `schema/profile.v1.json`, `schema/router_config.v1.json`
- **Profiles**: `profiles/` directory
- **Tests**: `tests/bootstrap/`
