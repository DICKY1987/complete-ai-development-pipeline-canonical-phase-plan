---
doc_id: DOC-CORE-UET-BOOTSTRAP-SPEC-191
---

# BOOTSTRAP_SPEC - Framework Self-Installation Guide for AI Agents

```yaml
---
meta_version: "doc-meta.v1"
doc_ulid: "01JDCQM8XXXXXXXXXXXXXXXXXXX"  # Generate actual ULID on commit
doc_type: "core_spec"
doc_layer: "framework"
title: "Universal Execution Templates Bootstrap Specification"
summary: "Defines how an AI agent autonomously analyzes, profiles, and instantiates this framework on any new project or module."
version: "1.0.0"
status: "active"
schema_ref: "schema/bootstrap_spec.v1.json"
created_at: "2025-11-20T20:29:00Z"
updated_at: "2025-11-20T20:29:00Z"
author_type: "mixed"
owner: "SYSTEM:FRAMEWORK_CORE"
security_tier: "public"

project_id: null
module_id: null
phase_id: null
workstream_id: null
spec_refs: []
tags:
  - "bootstrap"
  - "autonomous"
  - "project-agnostic"
  - "spec"

patch_policy:
  patch_required: true
  require_issue_ref: true
  min_reviewers: 1

ascii_only: true
max_line_length: 120
---
```

## 1. Purpose & Scope

**BOOTSTRAP_SPEC** is the **single entry point** for AI agents to autonomously apply the Universal Execution Templates Framework to any project or module.

**What this enables:**
- Point an AI agent at a new codebase, data pipeline, ops system, or documentation suite
- Agent discovers project characteristics without human guidance
- Agent generates appropriate specs, profiles, and infrastructure
- Framework becomes operational with minimal human intervention

**What this does NOT do:**
- Make business decisions about what work should be done
- Replace domain expertise (AI still needs task definitions)
- Bypass security/approval gates (those are configured, not removed)

---

## 2. AI Agent Entry Protocol

When an AI agent encounters a new project, follow this exact sequence:

### Step 0: Pre-Flight Check

**Action:** Verify framework prerequisites

**Tasks:**
```bash
# Check you have access to framework core
[ -d "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/" ] || exit 1

# Verify core specs exist
required_specs=(
  "UET_COOPERATION_SPEC.md"
  "UET_PHASE_SPEC_MASTER.md"
  "UET_WORKSTREAM_SPEC.md"
  "UET_TASK_ROUTING_SPEC.md"
  "UET_PROMPT_RENDERING_SPEC.md"
  "UET_PATCH_MANAGEMENT_SPEC.md"
)

for spec in "${required_specs[@]}"; do
  [ -f "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/$spec" ] || exit 1
done
```

**Decision point:**
- ✅ All core specs present → Proceed to Step 1
- ❌ Missing specs → STOP, report error to human

---

### Step 1: Project Discovery

**Action:** Analyze target project to determine characteristics

**1.1 Identify Project Root**
```yaml
project_root_indicators:
  - ".git/"               # Git repository
  - "pyproject.toml"      # Python project
  - "package.json"        # Node.js project
  - "Cargo.toml"          # Rust project
  - "pom.xml"             # Java/Maven project
  - "go.mod"              # Go project
  - "README.md"           # Documentation project
  - ".project_root"       # Explicit marker file
```

**1.2 Scan Directory Structure**
```python
# Conceptual discovery algorithm
def discover_project(root_path):
    return {
        "structure": {
            "src_dirs": find_dirs(["src/", "lib/", "core/", "app/"]),
            "test_dirs": find_dirs(["tests/", "test/", "__tests__/"]),
            "doc_dirs": find_dirs(["docs/", "documentation/"]),
            "config_dirs": find_dirs(["config/", "conf/", ".config/"]),
            "script_dirs": find_dirs(["scripts/", "tools/", "bin/"]),
        },
        "languages": detect_languages(),  # Count files by extension
        "frameworks": detect_frameworks(),  # pytest, jest, django, etc.
        "vcs": detect_vcs(),  # git, hg, svn
        "ci": detect_ci(),  # .github/workflows, .gitlab-ci.yml, etc.
    }
```

**1.3 Classify Domain**
```yaml
domain_classification:
  software-dev:
    indicators:
      - has_source_code: true
      - has_tests: true
      - has_build_system: true
    resource_types: ["files", "modules", "packages"]
    
  data-pipeline:
    indicators:
      - has_sql_files: true
      - has_etl_configs: true
      - has_schema_definitions: true
    resource_types: ["tables", "schemas", "queries", "datasets"]
    
  operations:
    indicators:
      - has_dockerfiles: true
      - has_k8s_manifests: true
      - has_terraform: true
    resource_types: ["services", "deployments", "configs", "infrastructure"]
    
  documentation:
    indicators:
      - has_markdown_files: true
      - no_source_code: true
      - has_doc_structure: true
    resource_types: ["documents", "assets", "templates"]
    
  mixed:
    indicators:
      - multiple_domains: true
    resource_types: ["files", "modules", "documents", "configs"]
```

**1.4 Detect Existing Tools**
```yaml
tool_detection:
  code_editors:
    - aider: check_command("aider --version")
    - cursor: check_command("cursor --version")
    
  ai_tools:
    - codex_cli: check_command("codex --version")
    - claude_cli: check_in_path("claude")
    
  testing:
    - pytest: check_file("pytest.ini") or check_file("pyproject.toml")
    - jest: check_file("jest.config.js")
    - go_test: check_language("go")
    
  linting:
    - ruff: check_file("ruff.toml")
    - eslint: check_file(".eslintrc")
    - pylint: check_file(".pylintrc")
    
  vcs:
    - git: check_dir(".git/")
```

**1.5 Infer Constraints**
```yaml
constraint_inference:
  from_ci_config:
    - tests_required: has_ci_test_step
    - lint_required: has_ci_lint_step
    - coverage_threshold: extract_from_ci_config
    
  from_project_structure:
    - isolated_tests: tests_dir_separate_from_src
    - monorepo: multiple_package_json_files
    
  from_existing_docs:
    - patch_only: check_for_contributing_md_patch_rules
    - approval_required: check_for_codeowners_file
```

**Output of Step 1:**
```json
{
  "project_root": "/path/to/project",
  "project_name": "detected-from-package-json-or-dirname",
  "domain": "software-dev",
  "languages": ["python", "javascript"],
  "resource_types": ["files", "modules"],
  "available_tools": ["aider", "pytest", "ruff", "git"],
  "existing_ci": "github-actions",
  "inferred_constraints": {
    "tests_must_pass": true,
    "lint_required": true,
    "patch_only": false  # Not yet enforced, framework will add this
  }
}
```

---

### Step 2: Profile Selection

**Action:** Choose or compose profile based on discovery results

**2.1 Profile Decision Tree**
```yaml
profile_selection:
  if domain == "software-dev":
    if "python" in languages:
      profile: "software-dev-python"
    elif "javascript" in languages:
      profile: "software-dev-js"
    else:
      profile: "software-dev-generic"
      
  elif domain == "data-pipeline":
    profile: "data-pipeline"
    
  elif domain == "operations":
    profile: "operations"
    
  elif domain == "documentation":
    profile: "documentation"
    
  elif domain == "mixed":
    profile: "mixed"
    compose_from:
      - "software-dev-generic"
      - "documentation"
```

**2.2 Load Profile Extensions**
```yaml
# Example: software-dev-python profile
profile_id: "software-dev-python"
profile_version: "1.0.0"

extends_core:
  - "COOPERATION_SPEC"
  - "PHASE_SPEC_MASTER"
  - "WORKSTREAM_SPEC"
  - "TASK_ROUTING_SPEC"
  - "PROMPT_RENDERING_SPEC"
  - "PATCH_MANAGEMENT_SPEC"

adds_resource_types:
  - type: "files"
    scope_format: "glob_patterns"
    operations: ["read", "write", "create", "delete"]
    
adds_change_types:
  - kind: "file_patch"
    format: "unified_diff"
    validation: ["syntax_check", "tests"]
    
adds_task_kinds:
  - "code_edit"
  - "code_review"
  - "refactor"
  - "analysis"
  - "documentation"
  
adds_constraints:
  - patch_only: true
  - max_lines_changed: 300
  - max_files_changed: 10
  - tests_must_pass: true
  - ascii_only: true
  
adds_validation_types:
  - type: "pytest"
    command: "pytest -q"
  - type: "ruff"
    command: "ruff check"
```

**2.3 Profile Composition (for mixed domains)**
```yaml
# When domain is "mixed", compose profile
composed_profile:
  profile_id: "custom-mixed-profile"
  base_profiles:
    - "software-dev-python"  # For src/
    - "documentation"        # For docs/
    
  resource_scope_mapping:
    "src/**/*":
      profile: "software-dev-python"
    "docs/**/*":
      profile: "documentation"
    "scripts/**/*":
      profile: "software-dev-python"
```

**Output of Step 2:**
```json
{
  "selected_profile": "software-dev-python",
  "profile_path": "framework/profiles/software-dev-python/",
  "extensions_loaded": true,
  "resource_types": ["files"],
  "change_types": ["file_patch"],
  "task_kinds": ["code_edit", "code_review", "refactor", "analysis"],
  "constraint_defaults": {
    "patch_only": true,
    "tests_must_pass": true,
    "max_lines_changed": 300
  }
}
```

---

### Step 3: Generate Core Artifacts

**Action:** Create project-specific instances of framework specs

**3.1 Generate PROJECT_PROFILE_SPEC**
```yaml
# Auto-generated: PROJECT_PROFILE.yaml
meta_version: "doc-meta.v1"
doc_ulid: "01JDCQM9AAAAAAAAAAAAAAAA"  # Generated
doc_type: "project_profile"
doc_layer: "project"
title: "Project Profile: [detected-project-name]"
version: "1.0.0"
status: "active"
schema_ref: "schema/project_profile.v1.json"

# Project identity
project_id: "PRJ-[generated-id]"
project_name: "[detected-project-name]"
project_root: "/absolute/path/to/project"

# Domain & profile
domain: "software-dev"
profile_id: "software-dev-python"
profile_version: "1.0.0"

# Resource configuration
resource_types:
  files:
    root: "."
    tracked_by: "git"
    exclusions:
      - ".git/"
      - "node_modules/"
      - "__pycache__/"
      - "*.pyc"

# Tool registry
available_tools:
  - tool_id: "aider"
    command: "aider"
    capabilities: ["code_edit", "refactor"]
    max_parallel: 2
    
  - tool_id: "pytest"
    command: "pytest"
    capabilities: ["test_execution"]
    
  - tool_id: "ruff"
    command: "ruff check"
    capabilities: ["linting"]

# Framework paths
framework_paths:
  tasks_dir: ".tasks/"
  ledger_dir: ".ledger/"
  worktrees_dir: ".worktrees/"
  quarantine_dir: ".quarantine/"
  registry_file: "registry/project.registry.yaml"

# Global constraints (from profile + inference)
constraints:
  patch_only: true
  tests_must_pass: true
  ascii_only: true
  max_lines_changed: 300
  max_files_changed: 10
  require_issue_ref: false  # Can be enabled later
```

**3.2 Generate Initial Phase Specs**

Based on domain, create starter phases:

```yaml
# For software-dev domain, generate:

# PH-CORE-01: Core Development
meta_version: "doc-meta.v1"
doc_type: "phase_spec_instance"
phase_id: "PH-CORE-01"
name: "Core Development"
category: "core_dev"

resource_scope:
  type: "files"
  read: ["src/**/*", "tests/**/*", "docs/**/*"]
  write: ["src/**/*"]
  create: ["src/**/*"]
  forbidden: [".git/**", "secrets/**"]

constraints:
  patch:
    patch_required: true
    max_lines_changed: 300
    max_files_changed: 10
  tests:
    tests_must_run: true
    tests_must_pass: true
    test_command: "pytest -q"
  behavior:
    ascii_only: true
    require_doc_update: false

acceptance:
  mode: "all"
  checks:
    - id: "tests_pass"
      type: "test_command"
      command: "pytest -q"
      required: true
      severity: "error"

---

# PH-REFACTOR-01: Refactoring & Code Quality
phase_id: "PH-REFACTOR-01"
name: "Refactoring & Code Quality"
category: "refactor"
# ... similar structure, different scope/constraints

---

# PH-DOC-01: Documentation Updates
phase_id: "PH-DOC-01"
name: "Documentation Updates"
category: "documentation"
resource_scope:
  write: ["docs/**/*", "README.md"]
constraints:
  tests:
    tests_must_pass: false  # Docs don't need code tests
# ... etc
```

**3.3 Generate router.config.yaml**
```yaml
# Auto-generated: config/router.config.yaml
version: "1.0.0"

apps:
  aider:
    kind: "tool"
    command: "aider"
    capabilities:
      task_kinds: ["code_edit", "refactor"]
      domains: ["general", "python"]
    limits:
      max_parallel: 2
      timeout_seconds: 1200
    safety_tier: "high"
    
  pytest:
    kind: "validator"
    command: "pytest -q"
    capabilities:
      task_kinds: ["test_execution"]
    limits:
      timeout_seconds: 300

routing:
  rules:
    - id: "route_code_edit_default"
      match:
        task_kind: ["code_edit"]
        risk_tier: ["R1", "R2"]
      select_from: ["aider"]
      strategy: "fixed"
      
    - id: "validate_with_tests"
      match:
        task_kind: ["code_edit", "refactor"]
      validate_with: ["pytest"]
      required: true

defaults:
  max_attempts: 3
  timeout_seconds: 900
  strategy: "auto"
```

**3.4 Create Directory Structure**
```bash
# Execute these directory creations
mkdir -p .tasks/inbox
mkdir -p .tasks/running
mkdir -p .tasks/done
mkdir -p .tasks/failed
mkdir -p .ledger/patches
mkdir -p .ledger/runs
mkdir -p .worktrees
mkdir -p .quarantine
mkdir -p registry
mkdir -p schema
mkdir -p config

# Create initial registry file
cat > registry/project.registry.yaml <<EOF
version: "1.0.0"
project_id: "PRJ-[generated-id]"
docs: {}
phases: {}
workstreams: {}
EOF
```

**Output of Step 3:**
```json
{
  "generated_artifacts": [
    "PROJECT_PROFILE.yaml",
    "phases/PH-CORE-01.yaml",
    "phases/PH-REFACTOR-01.yaml",
    "phases/PH-DOC-01.yaml",
    "config/router.config.yaml",
    "registry/project.registry.yaml"
  ],
  "directories_created": [
    ".tasks/",
    ".ledger/",
    ".worktrees/",
    ".quarantine/",
    "registry/",
    "schema/",
    "config/"
  ],
  "status": "artifacts_generated"
}
```

---

### Step 4: Validation Loop

**Action:** Validate all generated specs against schemas

**4.1 Schema Validation**
```python
# Conceptual validation process
def validate_generated_specs():
    errors = []
    
    # Validate PROJECT_PROFILE
    if not validate_schema("PROJECT_PROFILE.yaml", "schema/project_profile.v1.json"):
        errors.append("PROJECT_PROFILE.yaml failed schema validation")
    
    # Validate each phase
    for phase_file in glob("phases/*.yaml"):
        if not validate_schema(phase_file, "schema/phase_spec.v1.json"):
            errors.append(f"{phase_file} failed schema validation")
    
    # Validate router config
    if not validate_schema("config/router.config.yaml", "schema/router_config.v1.json"):
        errors.append("router.config.yaml failed schema validation")
    
    return errors
```

**4.2 Constraint Consistency Check**
```yaml
consistency_checks:
  - name: "Profile constraints not relaxed"
    check: |
      PROJECT_PROFILE.constraints should be >= selected_profile.constraints
    
  - name: "Phase scopes within project scope"
    check: |
      All phase.resource_scope must be subset of PROJECT_PROFILE.resource_types
    
  - name: "Tools are available"
    check: |
      All router.config.apps must be in available_tools
    
  - name: "No circular phase dependencies"
    check: |
      Phase dependency graph is acyclic
```

**4.3 Auto-Fix Attempts**
```yaml
auto_fix_rules:
  - error: "Schema validation failed"
    fix: "Regenerate artifact with corrected structure"
    
  - error: "Constraint relaxation detected"
    fix: "Restore stricter constraint from profile"
    
  - error: "Tool not available"
    fix: "Remove tool from router config or mark as optional"
    
  - error: "Invalid resource scope"
    fix: "Narrow scope to valid patterns"
```

**4.4 Human Escalation Points**
```yaml
cannot_auto_fix:
  - "Multiple equally valid profile choices"
    → Ask human to select profile
    
  - "Critical tools missing (no editors detected)"
    → Report blockage, request tool installation
    
  - "Project structure doesn't match any known pattern"
    → Request human guidance on domain classification
    
  - "Security tier ambiguous (contains secrets/)"
    → Ask human to define security policy
```

**Output of Step 4:**
```json
{
  "validation_status": "passed",  // or "failed" or "needs_human"
  "errors": [],
  "warnings": [
    "Tool 'codex_cli' not found, removed from router config"
  ],
  "auto_fixes_applied": 1,
  "human_decisions_needed": 0
}
```

---

### Step 5: Report & Handoff

**Action:** Generate human-readable report and mark framework as ready

**5.1 Generate Bootstrap Report**
```markdown
# Framework Bootstrap Report

**Project:** [project-name]
**Domain:** software-dev (Python)
**Profile:** software-dev-python v1.0.0
**Status:** ✅ READY

## Discovery Summary
- **Languages:** Python (87%), Markdown (13%)
- **Frameworks:** pytest, ruff
- **Version Control:** git
- **CI/CD:** GitHub Actions

## Generated Artifacts
- ✅ PROJECT_PROFILE.yaml
- ✅ 3 Phase Specs (CORE-01, REFACTOR-01, DOC-01)
- ✅ Router Config (1 tool: aider)
- ✅ Directory Structure (.tasks/, .ledger/, .worktrees/)

## Configuration
- **Patch-only mode:** Enabled
- **Test requirement:** All code changes must pass pytest
- **Max lines per patch:** 300
- **Available tools:** aider, pytest, ruff

## Next Steps for Human Operator
1. Review PROJECT_PROFILE.yaml and adjust constraints if needed
2. Define first workstream in `.tasks/` or via orchestrator
3. Run validation: `python tools/validate_specs.py`
4. Start orchestrator: `python core/engine/orchestrator.py`

## Next Steps for AI Agent
Framework is ready. You can now:
- Accept workstream definitions
- Route tasks to aider
- Validate patches against generated constraints
- Execute within phase boundaries
```

**5.2 Mark Framework Initialized**
```yaml
# Create .framework_initialized marker
cat > .framework_initialized <<EOF
initialized_at: "2025-11-20T20:29:00Z"
bootstrap_version: "1.0.0"
project_profile: "PROJECT_PROFILE.yaml"
status: "ready"
EOF
```

**5.3 Agent Self-Check**
```python
def verify_bootstrap_complete():
    required = [
        ".framework_initialized",
        "PROJECT_PROFILE.yaml",
        "config/router.config.yaml",
        ".tasks/inbox/",
        ".ledger/",
    ]
    return all(os.path.exists(path) for path in required)
```

**Output of Step 5:**
```json
{
  "bootstrap_complete": true,
  "report_generated": "BOOTSTRAP_REPORT.md",
  "framework_status": "ready",
  "initialization_time": "2025-11-20T20:29:00Z",
  "ready_for_workstreams": true
}
```

---

## 3. Domain-Specific Bootstrap Variations

### 3.1 Software Development Projects

**Additional discovery:**
- Detect testing frameworks (pytest, jest, go test)
- Identify linters (ruff, eslint, pylint)
- Find CI configurations
- Detect dependency management (requirements.txt, package.json, go.mod)

**Generated phases:**
- PH-CORE-01: Core Development
- PH-REFACTOR-01: Refactoring
- PH-TEST-01: Test Development
- PH-DOC-01: Documentation
- PH-ERR-01: Error Handling (if framework error pipeline is available)

**Constraints:**
- `patch_only: true`
- `tests_must_pass: true`
- Language-specific linting required

---

### 3.2 Data Pipeline Projects

**Additional discovery:**
- Detect SQL files and dialects
- Find schema definitions
- Identify ETL orchestration tools (Airflow, Dagster)
- Detect data validation tools (Great Expectations)

**Generated phases:**
- PH-SCHEMA-01: Schema Changes
- PH-ETL-01: ETL Development
- PH-VALIDATE-01: Data Validation
- PH-MIGRATE-01: Data Migration

**Resource types:**
- `tables`, `views`, `schemas`, `queries`, `datasets`

**Change types:**
- `schema_migration` (SQL DDL)
- `query_update` (SQL DML)
- `config_change` (YAML/JSON ETL configs)

**Constraints:**
- `migration_reversible: true`
- `schema_validated: true`
- `dry_run_required: true`

---

### 3.3 Operations/Infrastructure Projects

**Additional discovery:**
- Detect container definitions (Dockerfile, docker-compose.yml)
- Find K8s manifests
- Identify IaC tools (Terraform, Ansible, CloudFormation)
- Detect monitoring configs

**Generated phases:**
- PH-INFRA-01: Infrastructure Changes
- PH-DEPLOY-01: Deployment
- PH-CONFIG-01: Configuration Management
- PH-MONITOR-01: Monitoring Setup

**Resource types:**
- `services`, `deployments`, `configs`, `infrastructure_resources`

**Change types:**
- `infra_change` (Terraform/HCL)
- `config_update` (YAML/JSON configs)
- `deployment_manifest` (K8s YAML)

**Constraints:**
- `dry_run_required: true`
- `approval_required: true` (for prod)
- `rollback_plan_required: true`

---

### 3.4 Documentation Projects

**Additional discovery:**
- Detect doc generators (Sphinx, MkDocs, Docusaurus)
- Find asset directories (images, diagrams)
- Identify link validators

**Generated phases:**
- PH-CONTENT-01: Content Development
- PH-STRUCTURE-01: Structure/Organization
- PH-REVIEW-01: Review & Quality

**Resource types:**
- `documents`, `assets`, `templates`

**Change types:**
- `doc_update` (Markdown/RST patches)
- `asset_add` (Image/diagram files)

**Constraints:**
- `tests_must_pass: false` (no code tests)
- `link_validation_required: true`
- `spell_check_required: true`

---

## 4. Error Handling & Recovery

### 4.1 Bootstrap Failures

**If Step 1 (Discovery) fails:**
```yaml
failure_mode: "cannot_detect_project"
recovery:
  - Ask human: "What type of project is this?"
  - Options: ["software-dev", "data-pipeline", "operations", "documentation", "mixed"]
  - Proceed with manual classification
```

**If Step 2 (Profile Selection) fails:**
```yaml
failure_mode: "no_matching_profile"
recovery:
  - Use profile: "generic"
  - Generate minimal PROJECT_PROFILE
  - Request human customization
```

**If Step 3 (Artifact Generation) fails:**
```yaml
failure_mode: "cannot_generate_artifacts"
recovery:
  - Log errors to .bootstrap_errors.log
  - Generate partial artifacts where possible
  - Mark framework as "partial_init"
  - Request human completion
```

**If Step 4 (Validation) fails:**
```yaml
failure_mode: "validation_errors"
recovery:
  - Apply auto-fixes (up to 3 iterations)
  - If still failing:
    - Save broken artifacts to .bootstrap_attempts/
    - Report validation errors to human
    - Do NOT mark framework as ready
```

### 4.2 Partial Initialization

```yaml
# .framework_initialized marker for partial init
initialized_at: "2025-11-20T20:29:00Z"
bootstrap_version: "1.0.0"
status: "partial"
completed_steps: ["discovery", "profile_selection"]
failed_step: "artifact_generation"
error_log: ".bootstrap_errors.log"
human_action_required: true
```

---

## 5. Validation & Conformance

### 5.1 Bootstrap Success Criteria

Framework bootstrap is considered **successful** when:

```yaml
success_criteria:
  - PROJECT_PROFILE.yaml exists and validates
  - At least 1 phase spec exists and validates
  - router.config.yaml exists and references available tools
  - Directory structure created (.tasks/, .ledger/, .worktrees/)
  - No validation errors in generated artifacts
  - .framework_initialized marker exists with status: "ready"
```

### 5.2 Post-Bootstrap Validation

After bootstrap, run conformance checks:

```bash
# Validate all generated specs
python tools/validate_specs.py

# Check directory structure
python tools/check_structure.py

# Verify tool availability
python tools/verify_tools.py

# Run conformance suite
python tools/bootstrap_conformance.py
```

### 5.3 Bootstrap Audit Trail

```yaml
# .ledger/bootstrap.log (JSONL format)
{"event": "bootstrap_started", "ts": "2025-11-20T20:29:00Z", "project_root": "/path"}
{"event": "discovery_complete", "ts": "2025-11-20T20:29:05Z", "domain": "software-dev"}
{"event": "profile_selected", "ts": "2025-11-20T20:29:06Z", "profile": "software-dev-python"}
{"event": "artifacts_generated", "ts": "2025-11-20T20:29:10Z", "count": 5}
{"event": "validation_passed", "ts": "2025-11-20T20:29:12Z", "errors": 0}
{"event": "bootstrap_complete", "ts": "2025-11-20T20:29:13Z", "status": "ready"}
```

---

## 6. AI Agent Behavioral Rules During Bootstrap

### 6.1 Mandatory Behaviors

**DO:**
- ✅ Generate ULIDs for all new artifacts
- ✅ Validate every generated spec against its schema
- ✅ Log all decisions to bootstrap audit trail
- ✅ Preserve any existing framework artifacts (don't overwrite)
- ✅ Use conservative constraint defaults (stricter is safer)
- ✅ Create comprehensive documentation of bootstrap process
- ✅ Report errors clearly with recovery suggestions

**DON'T:**
- ❌ Overwrite existing PROJECT_PROFILE or phase specs
- ❌ Relax profile constraints (only tighten)
- ❌ Generate artifacts without schema validation
- ❌ Proceed if critical tools are missing (unless human approves)
- ❌ Mark framework as ready if any validation fails
- ❌ Make security decisions (always ask human)

### 6.2 Decision Making Guidelines

**When you encounter ambiguity:**

1. **Multiple valid choices exist**
   - Choose most conservative option
   - Document alternatives in bootstrap report
   - Mark as "human_review_suggested"

2. **Insufficient information**
   - Use framework defaults
   - Mark as "default_used, human_review_suggested"
   - Log gap in bootstrap report

3. **Conflicting signals**
   - Prefer explicit over implicit (e.g., config file > directory structure)
   - Prefer strict over permissive
   - Log conflict resolution in audit trail

### 6.3 Human Interaction Points

**Required human approval:**
- Security tier classification (if secrets detected)
- Production deployment constraints
- Approval workflows
- External integrations (GitHub, Jira, etc.)

**Suggested human review:**
- Profile selection (when confidence < 80%)
- Resource scope boundaries
- Test coverage requirements
- Tool timeout values

**Optional human review:**
- Directory naming conventions
- Tag assignments
- Documentation structure

---

## 7. Incremental Bootstrap (Partial/Progressive Installation)

### 7.1 Minimal Viable Framework

Sometimes full bootstrap isn't needed. Support minimal initialization:

```yaml
bootstrap_mode: "minimal"

minimal_artifacts:
  - PROJECT_PROFILE.yaml     # Required
  - config/router.config.yaml  # Required
  - .tasks/inbox/             # Required
  - .ledger/                  # Required

optional_artifacts:
  - phases/*.yaml             # Can be added later
  - .worktrees/               # Created on-demand
  - .quarantine/              # Created if error pipeline used
```

### 7.2 Progressive Enhancement

Framework can be enhanced over time:

```yaml
enhancement_sequence:
  1_minimal:
    - PROJECT_PROFILE
    - router.config
    - directory structure
    
  2_basic_phases:
    - Add 1-2 core phases
    - Enable task routing
    
  3_full_governance:
    - Add all domain phases
    - Enable patch management
    - Enable error pipeline
    
  4_advanced:
    - Add custom phases
    - Configure approval workflows
    - Integrate external tools
```

---

## 8. Framework Versioning & Migration

### 8.1 Framework Version Detection

```yaml
# In PROJECT_PROFILE.yaml
framework_version: "1.0.0"  # Which UET version this project uses

upgrade_path:
  from_version: "0.9.0"
  to_version: "1.0.0"
  migration_script: "tools/migrate_framework.py"
  breaking_changes: false
```

### 8.2 Auto-Migration Support

When framework versions change, AI should:

```python
def check_framework_version():
    current = read_framework_version("PROJECT_PROFILE.yaml")
    latest = read_framework_version("FRAMEWORK_VERSION")
    
    if current < latest:
        return {
            "upgrade_available": True,
            "migration_required": has_breaking_changes(current, latest),
            "migration_script": get_migration_script(current, latest)
        }
```

---

## 9. Example Bootstrap Session (Complete Flow)

```plaintext
AI Agent: Starting framework bootstrap for /home/user/new-project

[Step 0: Pre-Flight]
✅ Framework core specs found
✅ All required specs validated

[Step 1: Discovery]
🔍 Scanning project structure...
✅ Detected: Python project (87% .py files)
✅ Found: pytest, ruff, git, GitHub Actions
✅ Classified as: software-dev domain

[Step 2: Profile Selection]
🎯 Selected profile: software-dev-python v1.0.0
✅ Profile extensions loaded
✅ Constraint defaults: patch_only=true, tests_required=true

[Step 3: Artifact Generation]
📝 Generating PROJECT_PROFILE.yaml...
✅ PROJECT_PROFILE.yaml created (ULID: 01JDCR00...)

📝 Generating phase specs...
✅ PH-CORE-01.yaml (Core Development)
✅ PH-REFACTOR-01.yaml (Refactoring)
✅ PH-DOC-01.yaml (Documentation)

📝 Generating router.config.yaml...
✅ router.config.yaml created (1 tool: aider)

📁 Creating directory structure...
✅ .tasks/ .ledger/ .worktrees/ .quarantine/ created

[Step 4: Validation]
🔍 Validating generated artifacts...
✅ All schemas validated successfully
✅ Constraint consistency verified
✅ No circular dependencies detected

⚠️  Warning: Tool 'codex_cli' not found, removed from config
✅ Auto-fix applied

[Step 5: Report]
📊 Bootstrap complete!
✅ Framework status: READY
📄 Report saved to: BOOTSTRAP_REPORT.md
🔐 Marker created: .framework_initialized

Next steps:
1. Review PROJECT_PROFILE.yaml
2. Define your first workstream
3. Run: python core/engine/orchestrator.py

Bootstrap completed in 14 seconds.
```

---

## 10. Schema References

This spec requires the following schemas to exist:

```yaml
required_schemas:
  - schema/bootstrap_spec.v1.json         # This spec's schema
  - schema/project_profile.v1.json        # PROJECT_PROFILE
  - schema/phase_spec.v1.json             # Phase instances
  - schema/router_config.v1.json          # Router config
  - schema/doc-meta.v1.json               # Doc metadata
  
profile_schemas:
  - profiles/software-dev/extensions.json
  - profiles/data-pipeline/extensions.json
  - profiles/operations/extensions.json
  - profiles/documentation/extensions.json
```

---

## 11. Future Enhancements

**Planned for v1.1:**
- Cloud project detection (AWS, GCP, Azure structures)
- Monorepo support (multiple subprojects)
- Legacy project migration strategies
- Interactive bootstrap mode (CLI wizard)

**Planned for v2.0:**
- Multi-language project composition
- Custom profile builder (AI-assisted)
- Integration marketplace (pre-built tool profiles)
- Bootstrap from existing frameworks (migrate from other systems)

---

## END OF BOOTSTRAP_SPEC

**This specification is the single entry point for autonomous framework application.**

When an AI agent encounters a new project and sees this spec, it knows exactly:
1. How to analyze the project
2. How to select appropriate profiles
3. How to generate conformant artifacts
4. How to validate its work
5. When to ask for human help

**The framework is now self-installing.**
