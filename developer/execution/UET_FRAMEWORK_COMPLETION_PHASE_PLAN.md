---
doc_id: DOC-GUIDE-UET-FRAMEWORK-COMPLETION-PHASE-PLAN-1212
---

# Universal Execution Templates Framework - Completion Phase Plan

```yaml
---
meta_version: "doc-meta.v1"
doc_ulid: "01JDCR8KXXXXXXXXXXXXXXXXXXX"  # Generate actual ULID on commit
doc_type: "phase_spec_instance"
doc_layer: "framework"
title: "UET Framework Completion Phase Plan"
summary: "Defines the phases and workstreams required to complete the Universal Execution Templates Framework from current state to production-ready, autonomous installation capability."
version: "1.0.0"
status: "active"
schema_ref: "schema/phase_plan.v1.json"
created_at: "2025-11-20T20:39:00Z"
updated_at: "2025-11-20T20:39:00Z"
author_type: "ai"
owner: "FRAMEWORK_CORE"
security_tier: "internal"

project_id: "PRJ-UET-FRAMEWORK"
module_id: null
phase_id: null
workstream_id: null
spec_refs:
  - "UET_BOOTSTRAP_SPEC.md"
  - "UET_COOPERATION_SPEC.md"
  - "UET_PHASE_SPEC_MASTER.md"
  - "UET_WORKSTREAM_SPEC.md"
tags:
  - "framework"
  - "phase-plan"
  - "completion"
  - "roadmap"

patch_policy:
  patch_required: true
  require_issue_ref: false  # Internal framework work
  min_reviewers: 1

ascii_only: true
max_line_length: 120
---
```

## Executive Summary

**Current State:** Framework has comprehensive specifications but lacks implementation artifacts
**Target State:** Fully autonomous framework that can bootstrap itself onto any project
**Timeline:** 4 phases, estimated 8-12 weeks
**Success Metric:** AI agent can point at any project and generate working framework instance

---

## Phase 0: Foundation & Schema Layer (Week 1-2)

**Objective:** Create the schema foundation that validates all framework artifacts

### PH-00-01: Core Schema Development

**Priority:** CRITICAL (Blocks all other work)
**Risk:** Low (Pure schema definition)
**Dependencies:** None

#### Workstreams

**WS-00-01A: Document Metadata Schema**
```yaml
workstream_id: "WS-00-01A"
name: "Create doc-meta.v1.json schema"
category: "schema_development"
complexity: "low"
estimated_effort: "2 days"

deliverables:
  - schema/doc-meta.v1.json
  - tests/schema/test_doc_meta.py
  - examples/valid_doc_meta.yaml
  - examples/invalid_doc_meta.yaml

tasks:
  - id: "T1"
    name: "Extract doc-meta spec from UET_meta_layer.md"
    kind: "analysis"
    
  - id: "T2"
    name: "Create JSON Schema file"
    kind: "code_edit"
    constraints:
      max_lines_changed: 200
      tests_must_pass: true
    
  - id: "T3"
    name: "Write validation tests"
    kind: "code_edit"
    depends_on: ["T2"]
    
  - id: "T4"
    name: "Create example artifacts"
    kind: "documentation"
    depends_on: ["T2"]

acceptance:
  - All existing UET specs validate against doc-meta.v1.json
  - Test suite covers all required/optional fields
  - Examples demonstrate valid/invalid cases
```

**WS-00-01B: Core Spec Schemas**
```yaml
workstream_id: "WS-00-01B"
name: "Create schemas for 6 core specs"
category: "schema_development"
complexity: "medium"
estimated_effort: "5 days"
depends_on: ["WS-00-01A"]

deliverables:
  - schema/cooperation_spec.v1.json
  - schema/phase_spec.v1.json
  - schema/workstream_spec.v1.json
  - schema/task_spec.v1.json
  - schema/task_routing_spec.v1.json
  - schema/execution_request.v1.json
  - schema/prompt_instance.v1.json
  - schema/patch_artifact.v1.json
  - schema/patch_ledger_entry.v1.json
  - schema/patch_policy.v1.json
  - schema/run_record.v1.json
  - schema/step_attempt.v1.json
  - schema/run_event.v1.json
  - tests/schema/test_all_schemas.py

tasks:
  - id: "T1"
    name: "Extract schema definitions from UET_COOPERATION_SPEC.md"
    kind: "analysis"
    
  - id: "T2"
    name: "Extract schema definitions from UET_PHASE_SPEC_MASTER.md"
    kind: "analysis"
    
  - id: "T3"
    name: "Extract schema definitions from UET_WORKSTREAM_SPEC.md"
    kind: "analysis"
    
  - id: "T4"
    name: "Create all JSON Schema files"
    kind: "code_edit"
    depends_on: ["T1", "T2", "T3"]
    constraints:
      max_lines_changed: 1500
      
  - id: "T5"
    name: "Write comprehensive validation tests"
    kind: "code_edit"
    depends_on: ["T4"]
    constraints:
      tests_must_pass: true

acceptance:
  - All 13 schema files created and valid JSON Schema draft-07
  - Test suite validates all required/optional fields
  - No conflicts between related schemas
  - Documentation examples validate successfully
```

**WS-00-01C: Bootstrap Schema**
```yaml
workstream_id: "WS-00-01C"
name: "Create bootstrap-specific schemas"
category: "schema_development"
complexity: "medium"
estimated_effort: "3 days"
depends_on: ["WS-00-01B"]

deliverables:
  - schema/bootstrap_spec.v1.json
  - schema/project_profile.v1.json
  - schema/router_config.v1.json
  - schema/profile_extension.v1.json
  - tests/schema/test_bootstrap_schemas.py

tasks:
  - id: "T1"
    name: "Extract bootstrap schema from UET_BOOTSTRAP_SPEC.md"
    kind: "analysis"
    
  - id: "T2"
    name: "Create bootstrap schemas"
    kind: "code_edit"
    constraints:
      max_lines_changed: 800
      
  - id: "T3"
    name: "Write bootstrap validation tests"
    kind: "code_edit"
    depends_on: ["T2"]

acceptance:
  - All bootstrap schemas created
  - Schemas align with bootstrap spec Step 3 artifacts
  - Test coverage for all bootstrap outputs
```

### Phase 0 Completion Criteria
- ✅ 17 JSON Schema files created and validated
- ✅ Test suite with >90% coverage of schema rules
- ✅ All existing UET specs validate against their schemas
- ✅ Example artifacts demonstrate schema usage

---

## Phase 1: Profile System (Week 3-4)

**Objective:** Create domain-specific profile extensions that customize framework behavior

### PH-01-01: Profile Architecture

**Priority:** HIGH
**Risk:** Medium (Defines extensibility model)
**Dependencies:** Phase 0

#### Workstreams

**WS-01-01A: Software-Dev Profile**
```yaml
workstream_id: "WS-01-01A"
name: "Create software-dev profile (Python variant)"
category: "profile_development"
complexity: "medium"
estimated_effort: "4 days"

deliverables:
  - profiles/software-dev-python/profile.yaml
  - profiles/software-dev-python/extensions.json
  - profiles/software-dev-python/phase_templates/
  - profiles/software-dev-python/examples/
  - profiles/software-dev-python/README.md

tasks:
  - id: "T1"
    name: "Define profile structure and extension points"
    kind: "planning"
    
  - id: "T2"
    name: "Create software-dev-python profile.yaml"
    kind: "code_edit"
    output:
      - Defines resource_types: ["files"]
      - Defines change_types: ["file_patch"]
      - Defines task_kinds: ["code_edit", "code_review", "refactor", "analysis"]
      - Defines constraints: patch_only, tests_must_pass, max_lines_changed
      
  - id: "T3"
    name: "Create extensions.json (schema extensions)"
    kind: "code_edit"
    depends_on: ["T2"]
    
  - id: "T4"
    name: "Create phase templates"
    kind: "code_edit"
    depends_on: ["T2"]
    output:
      - PH-CORE-01 template (Core Development)
      - PH-REFACTOR-01 template (Refactoring)
      - PH-TEST-01 template (Test Development)
      - PH-DOC-01 template (Documentation)
      
  - id: "T5"
    name: "Create example project using this profile"
    kind: "documentation"
    depends_on: ["T3", "T4"]

acceptance:
  - Profile validates against profile_extension.v1.json
  - All 4 phase templates validate against phase_spec.v1.json
  - Example project demonstrates profile usage
  - README explains when to use this profile
```

**WS-01-01B: Additional Profiles**
```yaml
workstream_id: "WS-01-01B"
name: "Create profiles for other domains"
category: "profile_development"
complexity: "medium"
estimated_effort: "5 days"
depends_on: ["WS-01-01A"]

deliverables:
  - profiles/data-pipeline/
  - profiles/operations/
  - profiles/documentation/
  - profiles/generic/

tasks:
  - id: "T1"
    name: "Create data-pipeline profile"
    kind: "code_edit"
    resource_types: ["tables", "schemas", "queries"]
    change_types: ["schema_migration", "query_update"]
    
  - id: "T2"
    name: "Create operations profile"
    kind: "code_edit"
    resource_types: ["services", "deployments", "configs"]
    change_types: ["infra_change", "config_update", "deployment_manifest"]
    
  - id: "T3"
    name: "Create documentation profile"
    kind: "code_edit"
    resource_types: ["documents", "assets"]
    change_types: ["doc_update", "asset_add"]
    
  - id: "T4"
    name: "Create generic profile (fallback)"
    kind: "code_edit"
    resource_types: ["resources"]
    change_types: ["change_artifact"]

acceptance:
  - All 4 profiles validate against schema
  - Each profile has phase templates
  - Each profile has example usage
  - Profile selection decision tree documented
```

**WS-01-01C: Profile Composition**
```yaml
workstream_id: "WS-01-01C"
name: "Implement profile composition for mixed domains"
category: "profile_development"
complexity: "high"
estimated_effort: "3 days"
depends_on: ["WS-01-01B"]

deliverables:
  - profiles/mixed/composition_rules.yaml
  - examples/mixed_profile_project/
  - docs/profile_composition_guide.md

tasks:
  - id: "T1"
    name: "Define composition rules"
    kind: "planning"
    
  - id: "T2"
    name: "Create composition schema"
    kind: "code_edit"
    
  - id: "T3"
    name: "Create example mixed project"
    kind: "documentation"
    example: "Project with src/ (software-dev) and docs/ (documentation)"

acceptance:
  - Composition rules validate
  - Example demonstrates path-based profile mapping
  - Guide explains when/how to compose profiles
```

### Phase 1 Completion Criteria
- ✅ 5 domain profiles created (software-dev, data-pipeline, ops, docs, generic)
- ✅ Each profile has 2-4 phase templates
- ✅ Profile composition system works
- ✅ Examples demonstrate each profile

---

## Phase 2: Bootstrap Implementation (Week 5-7)

**Objective:** Implement the autonomous bootstrap process from BOOTSTRAP_SPEC

### PH-02-01: Discovery Engine

**Priority:** CRITICAL
**Risk:** Medium (Complex detection logic)
**Dependencies:** Phase 1

#### Workstreams

**WS-02-01A: Project Scanner**
```yaml
workstream_id: "WS-02-01A"
name: "Implement project discovery (Step 1)"
category: "core_development"
complexity: "high"
estimated_effort: "5 days"

deliverables:
  - tools/bootstrap/discover_project.py
  - tools/bootstrap/detectors/language_detector.py
  - tools/bootstrap/detectors/framework_detector.py
  - tools/bootstrap/detectors/tool_detector.py
  - tools/bootstrap/detectors/ci_detector.py
  - tests/bootstrap/test_discovery.py

tasks:
  - id: "T1"
    name: "Create project scanner framework"
    kind: "code_edit"
    files_scope:
      create: ["tools/bootstrap/*.py"]
      
  - id: "T2"
    name: "Implement language detection"
    kind: "code_edit"
    logic:
      - Count files by extension
      - Detect package manifests (package.json, pyproject.toml, etc.)
      - Classify as software-dev/data-pipeline/ops/docs
      
  - id: "T3"
    name: "Implement framework/tool detection"
    kind: "code_edit"
    depends_on: ["T1"]
    
  - id: "T4"
    name: "Implement CI/VCS detection"
    kind: "code_edit"
    depends_on: ["T1"]
    
  - id: "T5"
    name: "Write comprehensive discovery tests"
    kind: "code_edit"
    depends_on: ["T2", "T3", "T4"]
    test_cases:
      - Pure Python project → software-dev
      - SQL + Airflow → data-pipeline
      - Terraform → operations
      - Only markdown → documentation

acceptance:
  - Scanner correctly classifies 10+ test projects
  - Detection confidence scores reported
  - Handles edge cases (empty dirs, mixed content)
  - Test coverage >85%
```

**WS-02-01B: Profile Selector**
```yaml
workstream_id: "WS-02-01B"
name: "Implement profile selection (Step 2)"
category: "core_development"
complexity: "medium"
estimated_effort: "3 days"
depends_on: ["WS-02-01A"]

deliverables:
  - tools/bootstrap/select_profile.py
  - tools/bootstrap/load_profile.py
  - tests/bootstrap/test_profile_selection.py

tasks:
  - id: "T1"
    name: "Implement profile decision tree"
    kind: "code_edit"
    logic: "Match discovery results to profile indicators"
    
  - id: "T2"
    name: "Implement profile loader"
    kind: "code_edit"
    depends_on: ["T1"]
    
  - id: "T3"
    name: "Implement profile composition for mixed domains"
    kind: "code_edit"
    depends_on: ["T2"]

acceptance:
  - Selector chooses correct profile for test cases
  - Confidence < 80% triggers human review flag
  - Profile extensions loaded correctly
  - Composition works for mixed domains
```

### PH-02-02: Artifact Generator

**WS-02-02A: Core Artifact Generation**
```yaml
workstream_id: "WS-02-02A"
name: "Implement artifact generation (Step 3)"
category: "core_development"
complexity: "high"
estimated_effort: "6 days"
depends_on: ["WS-02-01B"]

deliverables:
  - tools/bootstrap/generate_project_profile.py
  - tools/bootstrap/generate_phases.py
  - tools/bootstrap/generate_router_config.py
  - tools/bootstrap/create_directories.py
  - tests/bootstrap/test_generation.py

tasks:
  - id: "T1"
    name: "Generate PROJECT_PROFILE.yaml from discovery + profile"
    kind: "code_edit"
    constraints:
      - Must validate against project_profile.v1.json
      - Must include all detected tools
      - Must apply profile constraints
      
  - id: "T2"
    name: "Generate phase specs from profile templates"
    kind: "code_edit"
    depends_on: ["T1"]
    logic:
      - Load phase templates from selected profile
      - Substitute project-specific values
      - Apply discovered tool constraints
      
  - id: "T3"
    name: "Generate router.config.yaml"
    kind: "code_edit"
    depends_on: ["T1"]
    
  - id: "T4"
    name: "Create directory structure"
    kind: "code_edit"
    directories:
      - .tasks/inbox, running, done, failed
      - .ledger/patches, runs
      - .worktrees/
      - .quarantine/
      - registry/, schema/, config/
      
  - id: "T5"
    name: "Generate initial registry file"
    kind: "code_edit"
    depends_on: ["T4"]

acceptance:
  - All artifacts validate against schemas
  - Generated PROJECT_PROFILE matches discovery
  - Phase specs inherit from profile templates correctly
  - Directory structure complete
```

### PH-02-03: Validation Engine

**WS-02-03A: Schema Validator**
```yaml
workstream_id: "WS-02-03A"
name: "Implement validation loop (Step 4)"
category: "core_development"
complexity: "medium"
estimated_effort: "4 days"
depends_on: ["WS-02-02A"]

deliverables:
  - tools/bootstrap/validate_artifacts.py
  - tools/bootstrap/auto_fix.py
  - tools/bootstrap/check_consistency.py
  - tests/bootstrap/test_validation.py

tasks:
  - id: "T1"
    name: "Implement schema validation"
    kind: "code_edit"
    logic: "Validate all generated artifacts against their schemas"
    
  - id: "T2"
    name: "Implement consistency checks"
    kind: "code_edit"
    checks:
      - Profile constraints not relaxed
      - Phase scopes within project scope
      - Tools are available
      - No circular dependencies
      
  - id: "T3"
    name: "Implement auto-fix rules"
    kind: "code_edit"
    depends_on: ["T1", "T2"]
    fixes:
      - Regenerate if schema fails
      - Remove unavailable tools
      - Narrow invalid scopes
      
  - id: "T4"
    name: "Implement human escalation logic"
    kind: "code_edit"
    depends_on: ["T3"]

acceptance:
  - Validator catches all schema violations
  - Consistency checks detect common errors
  - Auto-fix successfully repairs 80%+ of issues
  - Human escalation clear and actionable
```

### PH-02-04: Bootstrap Orchestrator

**WS-02-04A: Main Bootstrap Flow**
```yaml
workstream_id: "WS-02-04A"
name: "Implement bootstrap orchestrator (Steps 0-5)"
category: "core_development"
complexity: "high"
estimated_effort: "5 days"
depends_on: ["WS-02-03A"]

deliverables:
  - tools/bootstrap/bootstrap.py (main entry point)
  - tools/bootstrap/report_generator.py
  - tools/bootstrap/audit_logger.py
  - tests/bootstrap/test_end_to_end.py
  - CLI: bootstrap.ps1 / bootstrap.sh

tasks:
  - id: "T1"
    name: "Create main bootstrap orchestrator"
    kind: "code_edit"
    flow:
      - Step 0: Pre-flight check
      - Step 1: Discovery
      - Step 2: Profile selection
      - Step 3: Artifact generation
      - Step 4: Validation
      - Step 5: Report & mark ready
      
  - id: "T2"
    name: "Implement bootstrap report generator"
    kind: "code_edit"
    depends_on: ["T1"]
    
  - id: "T3"
    name: "Implement audit trail logger"
    kind: "code_edit"
    output: ".ledger/bootstrap.log (JSONL)"
    
  - id: "T4"
    name: "Create CLI wrappers"
    kind: "code_edit"
    
  - id: "T5"
    name: "Write end-to-end tests"
    kind: "code_edit"
    depends_on: ["T1", "T2", "T3", "T4"]
    test_scenarios:
      - Bootstrap on fresh Python project
      - Bootstrap on data pipeline
      - Bootstrap on mixed project
      - Handle partial failures

acceptance:
  - Bootstrap completes successfully on 5+ test projects
  - Report is human-readable and accurate
  - Audit trail captures all decisions
  - CLI works on Windows + Linux
  - .framework_initialized marker created correctly
```

### Phase 2 Completion Criteria
- ✅ Bootstrap tool successfully installs framework on test projects
- ✅ All 5 steps execute autonomously
- ✅ Validation catches and auto-fixes common errors
- ✅ Human escalation works for ambiguous cases
- ✅ End-to-end tests pass on multiple project types

---

## Phase 3: Orchestration Engine (Week 8-10)

**Objective:** Implement the runtime orchestration system that executes workstreams

### PH-03-01: Core Orchestrator

**Priority:** CRITICAL
**Risk:** High (Complex state management)
**Dependencies:** Phase 2

#### Workstreams

**WS-03-01A: Run Management**
```yaml
workstream_id: "WS-03-01A"
name: "Implement RunRecord lifecycle"
category: "core_development"
complexity: "high"
estimated_effort: "6 days"

deliverables:
  - core/engine/orchestrator.py
  - core/state/db.py (SQLite backend)
  - core/state/models.py (RunRecord, StepAttempt, RunEvent)
  - core/engine/state_machine.py
  - tests/engine/test_run_lifecycle.py

tasks:
  - id: "T1"
    name: "Create database schema for runs"
    kind: "code_edit"
    tables:
      - runs (RunRecord)
      - step_attempts (StepAttempt)
      - run_events (RunEvent)
      
  - id: "T2"
    name: "Implement Run state machine"
    kind: "code_edit"
    states: ["pending", "running", "succeeded", "failed", "quarantined", "canceled"]
    
  - id: "T3"
    name: "Implement Run CRUD operations"
    kind: "code_edit"
    depends_on: ["T1", "T2"]
    
  - id: "T4"
    name: "Implement event emission"
    kind: "code_edit"
    events: ["run_created", "run_started", "run_state_changed", etc.]

acceptance:
  - Run lifecycle follows COOPERATION_SPEC state machine
  - Events emitted for all state transitions
  - Database persists run state correctly
  - Test coverage >90%
```

**WS-03-01B: Task Router**
```yaml
workstream_id: "WS-03-01B"
name: "Implement task routing engine"
category: "core_development"
complexity: "high"
estimated_effort: "5 days"
depends_on: ["WS-03-01A"]

deliverables:
  - core/engine/router.py
  - core/engine/execution_request_builder.py
  - tests/engine/test_routing.py

tasks:
  - id: "T1"
    name: "Load and parse router.config.yaml"
    kind: "code_edit"
    
  - id: "T2"
    name: "Implement routing rules engine"
    kind: "code_edit"
    logic:
      - Match ExecutionRequest to routing rules
      - Select tool based on strategy (fixed, round_robin, auto)
      - Apply fallback rules
      
  - id: "T3"
    name: "Implement ExecutionRequest builder"
    kind: "code_edit"
    input: "TaskSpec from workstream"
    output: "Valid ExecutionRequest"
    
  - id: "T4"
    name: "Implement phase constraint validation"
    kind: "code_edit"
    checks:
      - files_scope subset of phase scope
      - constraints tightened, not relaxed
      - tools allowed by phase

acceptance:
  - Router selects correct tool for test cases
  - Phase constraints enforced
  - Routing failures escalate to error pipeline
  - ExecutionRequests validate against schema
```

**WS-03-01C: Worker System**
```yaml
workstream_id: "WS-03-01C"
name: "Implement worker queue system"
category: "core_development"
complexity: "medium"
estimated_effort: "4 days"
depends_on: ["WS-03-01B"]

deliverables:
  - core/engine/workers/tool_worker.py
  - core/engine/workers/patch_worker.py
  - core/engine/queue_manager.py
  - tests/engine/test_workers.py

tasks:
  - id: "T1"
    name: "Implement queue manager"
    kind: "code_edit"
    queues: [".tasks/inbox/", ".tasks/running/", ".tasks/done/", ".tasks/failed/"]
    
  - id: "T2"
    name: "Implement tool worker"
    kind: "code_edit"
    depends_on: ["T1"]
    logic:
      - Watch .tasks/inbox/
      - Execute tool command
      - Capture output
      - Normalize to PatchArtifact
      - Move to done/failed
      
  - id: "T3"
    name: "Implement patch worker"
    kind: "code_edit"
    depends_on: ["T1"]
    logic:
      - Validate patch
      - Apply to worktree
      - Run tests
      - Update ledger
      - Quarantine on failure

acceptance:
  - Workers process tasks from queues
  - Tool worker captures outputs correctly
  - Patch worker validates and applies patches
  - Failed tasks route to error pipeline
```

### PH-03-02: Patch Management

**WS-03-02A: Patch Pipeline**
```yaml
workstream_id: "WS-03-02A"
name: "Implement patch management system"
category: "core_development"
complexity: "high"
estimated_effort: "6 days"
depends_on: ["WS-03-01C"]

deliverables:
  - core/patch/patch_validator.py
  - core/patch/patch_applier.py
  - core/patch/ledger_manager.py
  - core/patch/quarantine_manager.py
  - tests/patch/test_patch_lifecycle.py

tasks:
  - id: "T1"
    name: "Implement patch validation"
    kind: "code_edit"
    checks:
      - Valid unified diff format
      - Files within scope
      - Lines within limits
      - No forbidden paths
      
  - id: "T2"
    name: "Implement patch application"
    kind: "code_edit"
    depends_on: ["T1"]
    logic:
      - Apply to git worktree
      - Run tests
      - Update ledger
      
  - id: "T3"
    name: "Implement ledger management"
    kind: "code_edit"
    storage: ".ledger/patches/*.json"
    
  - id: "T4"
    name: "Implement quarantine system"
    kind: "code_edit"
    logic:
      - Move failing patches to .quarantine/
      - Create PatchLedgerEntry with quarantined state
      - Trigger error pipeline

acceptance:
  - Patches validate against PATCH_MANAGEMENT_SPEC
  - Application succeeds in clean worktrees
  - Ledger tracks all patch states
  - Quarantine prevents bad patches from retrying
```

### Phase 3 Completion Criteria
- ✅ Orchestrator can execute workstreams end-to-end
- ✅ Task routing works for multiple tools
- ✅ Workers process tasks asynchronously
- ✅ Patch pipeline validates, applies, and tracks patches
- ✅ Error cases route to quarantine correctly

---

## Phase 4: Documentation & Examples (Week 11-12)

**Objective:** Create comprehensive documentation and example projects

### PH-04-01: Documentation Suite

**Priority:** HIGH
**Risk:** Low
**Dependencies:** Phase 3

#### Workstreams

**WS-04-01A: User Documentation**
```yaml
workstream_id: "WS-04-01A"
name: "Create user-facing documentation"
category: "documentation"
complexity: "medium"
estimated_effort: "4 days"

deliverables:
  - docs/README.md (Framework overview)
  - docs/quickstart.md (Get started in 5 minutes)
  - docs/bootstrap_guide.md (How bootstrap works)
  - docs/profile_guide.md (Choosing/creating profiles)
  - docs/workstream_authoring.md (Writing workstreams)
  - docs/troubleshooting.md (Common issues)

tasks:
  - id: "T1"
    name: "Write framework overview"
    kind: "documentation"
    
  - id: "T2"
    name: "Write quickstart guide"
    kind: "documentation"
    
  - id: "T3"
    name: "Write bootstrap guide"
    kind: "documentation"
    
  - id: "T4"
    name: "Write profile guide"
    kind: "documentation"
    
  - id: "T5"
    name: "Write workstream authoring guide"
    kind: "documentation"
    
  - id: "T6"
    name: "Write troubleshooting guide"
    kind: "documentation"

acceptance:
  - All docs use consistent style
  - Examples are tested and working
  - Links are valid
  - AI-readable (structured, clear sections)
```

**WS-04-01B: Developer Documentation**
```yaml
workstream_id: "WS-04-01B"
name: "Create developer documentation"
category: "documentation"
complexity: "medium"
estimated_effort: "3 days"
depends_on: ["WS-04-01A"]

deliverables:
  - docs/dev/ARCHITECTURE.md
  - docs/dev/CONTRIBUTING.md
  - docs/dev/API_REFERENCE.md
  - docs/dev/TESTING.md
  - docs/dev/PROFILE_DEVELOPMENT.md

tasks:
  - id: "T1"
    name: "Document architecture"
    kind: "documentation"
    
  - id: "T2"
    name: "Create contribution guide"
    kind: "documentation"
    
  - id: "T3"
    name: "Generate API reference"
    kind: "documentation"
    
  - id: "T4"
    name: "Document testing approach"
    kind: "documentation"
    
  - id: "T5"
    name: "Document profile development"
    kind: "documentation"

acceptance:
  - Architecture diagrams included
  - API reference covers all public interfaces
  - Testing guide explains test categories
  - Profile development shows end-to-end example
```

### PH-04-02: Example Projects

**WS-04-02A: Reference Implementations**
```yaml
workstream_id: "WS-04-02A"
name: "Create example projects for each profile"
category: "documentation"
complexity: "medium"
estimated_effort: "5 days"
depends_on: ["WS-04-01A"]

deliverables:
  - examples/software-dev-python-project/
  - examples/data-pipeline-project/
  - examples/operations-project/
  - examples/documentation-project/
  - examples/mixed-project/

tasks:
  - id: "T1"
    name: "Create software-dev example"
    kind: "documentation"
    includes:
      - Simple Python app
      - Tests with pytest
      - Bootstrap applied
      - Sample workstream executed
      
  - id: "T2"
    name: "Create data-pipeline example"
    kind: "documentation"
    
  - id: "T3"
    name: "Create operations example"
    kind: "documentation"
    
  - id: "T4"
    name: "Create documentation example"
    kind: "documentation"
    
  - id: "T5"
    name: "Create mixed example"
    kind: "documentation"

acceptance:
  - Each example bootstraps successfully
  - Each example includes working workstream
  - Each example demonstrates profile features
  - README explains what each example shows
```

**WS-04-02B: Tutorial Projects**
```yaml
workstream_id: "WS-04-02B"
name: "Create step-by-step tutorials"
category: "documentation"
complexity: "low"
estimated_effort: "3 days"
depends_on: ["WS-04-02A"]

deliverables:
  - tutorials/01_bootstrap_your_first_project.md
  - tutorials/02_create_a_workstream.md
  - tutorials/03_customize_a_profile.md
  - tutorials/04_handle_errors.md
  - tutorials/05_advanced_routing.md

tasks:
  - id: "T1-T5"
    name: "Write 5 tutorials"
    kind: "documentation"

acceptance:
  - Tutorials tested with real users (AI + human)
  - Each tutorial builds on previous
  - Code examples are copy-pasteable
```

### Phase 4 Completion Criteria
- ✅ Complete user documentation
- ✅ Complete developer documentation
- ✅ 5 example projects (one per domain)
- ✅ 5 step-by-step tutorials
- ✅ All docs validate and render correctly

---

## Cross-Phase Activities

### Testing Strategy

**Unit Tests:**
- Every Python module has >85% coverage
- Schema validators have 100% coverage
- Run in CI on every commit

**Integration Tests:**
- Bootstrap on 10+ real projects
- End-to-end workstream execution
- Profile composition scenarios
- Error handling and recovery

**Conformance Tests:**
- All generated artifacts validate against schemas
- Bootstrap outputs match spec requirements
- Phase constraints enforced correctly

### CI/CD Pipeline

```yaml
ci_stages:
  - name: "Lint & Format"
    tools: ["ruff", "black", "yamllint"]
    
  - name: "Schema Validation"
    script: "python tools/validate_all_schemas.py"
    
  - name: "Unit Tests"
    script: "pytest tests/ -v --cov"
    coverage_threshold: 85
    
  - name: "Integration Tests"
    script: "pytest tests/integration/ -v"
    
  - name: "Bootstrap Tests"
    script: "pytest tests/bootstrap/test_e2e.py -v"
    
  - name: "Documentation Build"
    script: "mkdocs build --strict"
```

### Risk Mitigation

**High-Risk Areas:**
1. **Profile extensibility** - May need refactoring if design doesn't scale
   - Mitigation: Start with 2 profiles, validate design, then expand
   
2. **Bootstrap complexity** - Many edge cases in real projects
   - Mitigation: Test on diverse projects early, maintain fallback to manual

3. **Orchestrator state management** - Complex concurrency/persistence
   - Mitigation: Start with single-threaded, add concurrency in v1.1

4. **Cross-platform compatibility** - Windows vs Linux differences
   - Mitigation: Use pathlib, test on both platforms in CI

---

## Success Metrics

### Phase 0 Success
- All schemas exist and validate
- Test suite passes
- No schema conflicts

### Phase 1 Success
- 5 profiles created and tested
- Each profile has phase templates
- Composition works

### Phase 2 Success
- Bootstrap completes on 5+ test projects
- <20% human intervention rate
- Generated artifacts validate 100%

### Phase 3 Success
- Orchestrator executes workstreams successfully
- Patch pipeline works end-to-end
- Error handling robust

### Phase 4 Success
- Documentation complete and accurate
- Examples work without modification
- Tutorials tested by users

### Overall Success
**Framework is production-ready when:**
- ✅ AI agent can bootstrap any project autonomously
- ✅ Generated artifacts validate against schemas
- ✅ Workstreams execute correctly
- ✅ Error cases handled gracefully
- ✅ Documentation enables self-service
- ✅ 3+ real projects using framework successfully

---

## Timeline & Resource Allocation

```yaml
total_duration: "12 weeks"
total_effort: "~400 hours"

phase_breakdown:
  Phase_0: "2 weeks (80 hours)"
  Phase_1: "2 weeks (80 hours)"
  Phase_2: "3 weeks (120 hours)"
  Phase_3: "3 weeks (120 hours)"
  Phase_4: "2 weeks (80 hours)"

parallel_work:
  - "Phase 1 profiles can start before Phase 0 100% complete"
  - "Phase 4 docs can start during Phase 3"
  - "Examples can be created as features complete"

critical_path:
  - "Phase 0 → Phase 1 → Phase 2 → Phase 3"
  - "Phase 4 can overlap with Phase 3"
```

---

## Post-Completion Roadmap (v1.1+)

**v1.1 (Q1 2026):**
- Parallel worker execution
- Multi-repository support
- Cloud detection (AWS, GCP, Azure)
- Interactive bootstrap mode (CLI wizard)

**v1.2 (Q2 2026):**
- GUI/Web interface for framework management
- Advanced profile builder (AI-assisted)
- Integration marketplace (pre-built tool profiles)
- Metrics & observability dashboard

**v2.0 (Q3 2026):**
- Multi-language project composition
- Custom constraint DSL
- Plugin system for custom workers
- Federation across multiple framework instances

---

## Appendix: Deliverable Checklist

### Phase 0 Deliverables (17 items)
- [ ] schema/doc-meta.v1.json
- [ ] schema/cooperation_spec.v1.json
- [ ] schema/phase_spec.v1.json
- [ ] schema/workstream_spec.v1.json
- [ ] schema/task_spec.v1.json
- [ ] schema/task_routing_spec.v1.json
- [ ] schema/execution_request.v1.json
- [ ] schema/prompt_instance.v1.json
- [ ] schema/patch_artifact.v1.json
- [ ] schema/patch_ledger_entry.v1.json
- [ ] schema/patch_policy.v1.json
- [ ] schema/run_record.v1.json
- [ ] schema/step_attempt.v1.json
- [ ] schema/run_event.v1.json
- [ ] schema/bootstrap_spec.v1.json
- [ ] schema/project_profile.v1.json
- [ ] schema/router_config.v1.json

### Phase 1 Deliverables (5 profiles)
- [ ] profiles/software-dev-python/
- [ ] profiles/data-pipeline/
- [ ] profiles/operations/
- [ ] profiles/documentation/
- [ ] profiles/generic/

### Phase 2 Deliverables (Bootstrap system)
- [ ] tools/bootstrap/bootstrap.py
- [ ] tools/bootstrap/discover_project.py
- [ ] tools/bootstrap/select_profile.py
- [ ] tools/bootstrap/generate_*.py (4 files)
- [ ] tools/bootstrap/validate_artifacts.py
- [ ] bootstrap.ps1 / bootstrap.sh

### Phase 3 Deliverables (Orchestrator)
- [ ] core/engine/orchestrator.py
- [ ] core/state/db.py
- [ ] core/engine/router.py
- [ ] core/engine/workers/ (2 workers)
- [ ] core/patch/ (4 modules)

### Phase 4 Deliverables (Docs + Examples)
- [ ] docs/ (11 documents)
- [ ] examples/ (5 projects)
- [ ] tutorials/ (5 tutorials)

**Total: ~60 major deliverables**

---

## END OF PHASE PLAN

This phase plan transforms the Universal Execution Templates Framework from specification to implementation, enabling autonomous AI-driven project governance.
