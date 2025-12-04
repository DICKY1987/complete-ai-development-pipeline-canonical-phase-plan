---
doc_id: DOC-GUIDE-GLOSSARY-422
---

# Glossary – AI Development Pipeline

**Last Updated**: 2025-11-27
**Purpose**: Comprehensive alphabetical reference of all specialized terms
**Audience**: Developers, AI agents, and documentation readers

> **Quick Navigation**: Jump to [A](#a) [B](#b) [C](#c) [D](#d) [E](#e) [F](#f) [G](#g) [H](#h) [I](#i) [J](#j) [L](#l) [M](#m) [O](#o) [P](#p) [R](#r) [S](#s) [T](#t) [U](#u) [W](#w)

**Related Documents**:
- [IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md) - Code locations for each term
- [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - All documentation references
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture overview

---

## A

### Adapter
**Category**: Integrations
**Definition**: Abstraction layer that wraps external tools (Aider, Codex, Claude) to provide a uniform interface for the orchestrator.

**Types**:
- **Aider Adapter** - Integrates Aider CLI for code editing
- **Codex Adapter** - Integrates GitHub Copilot CLI
- **Claude Adapter** - Integrates Claude Code CLI
- **Git Adapter** - Wraps Git operations
- **Test Adapter** - Wraps test runners (pytest, Pester)

**Implementation**: `core/engine/adapters/`
**Schema**: `schema/uet/execution_request.v1.json`

**Usage**:
```python
from core.engine.adapters.aider_adapter import AiderAdapter
adapter = AiderAdapter(config={'model': 'gpt-4'})
result = adapter.execute_task(task, worktree_path)
```

**Related Terms**: [Tool Profile](#tool-profile), [Executor](#executor), [UET Integration](#uet-universal-execution-templates)

---

### AIM (AI Environment Manager)
**Category**: Integrations
**Definition**: AI Metadata Integration Manager - a system for discovering, registering, and routing tasks to AI CLI tools.

**Purpose**:
- Auto-discover AI tools installed on system
- Maintain tool capability registry
- Match tasks to appropriate tools
- Manage tool profiles and preferences

**Implementation**: `aim/`
**CLI**: `python -m aim`

**Commands**:
```bash
python -m aim status           # Show available tools
python -m aim discover         # Scan for new tools
python -m aim register <tool>  # Register a tool manually
```

**Related Terms**: [Tool Registry](#tool-registry), [Tool Profile](#tool-profile), [AIM Bridge](#aim-bridge)

---

### AIM Bridge
**Category**: Integrations
**Definition**: Integration layer between AIM and the execution engine that translates tool metadata into executable configurations.

**Implementation**: `aim/bridge.py`

**Related Terms**: [AIM](#aim-ai-environment-manager), [Tool Registry](#tool-registry)

---

### Archive
**Category**: State Management
**Definition**: Process of moving completed workstreams and their artifacts to long-term storage.

**Purpose**:
- Clean up active state database
- Preserve historical execution records
- Enable workstream replay/analysis

**Implementation**: `core/planning/archive.py`

**Related Terms**: [Worktree Management](#worktree-management), [State Transition](#state-transition)

---

### Artifact-Type Organization
**Category**: Architecture
**Definition**: Legacy code organization pattern where artifacts are grouped by type (code/, tests/, docs/, schema/) rather than by module. Being migrated to module-centric architecture.

**Status**: DEPRECATED - replaced by [Module-Centric Architecture](#module-centric-architecture)

**Legacy Structure**:
```
core/state/db.py
tests/state/test_db.py
docs/STATE_GUIDE.md
schema/state.schema.json
```

**Problems**:
- AI must load context from 4+ directories
- SafePatch worktrees need complex file tracking
- No atomic module boundaries
- Cross-directory coordination required

**Migration Status**: In progress - see `MIGRATION_STATUS_SUMMARY.md`

**Related Terms**: [Module-Centric Architecture](#module-centric-architecture), [Module](#module)

**References**: `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md`

---

## B

### Bundle
**Category**: Core Engine
**Definition**: A collection of one or more workstreams packaged together as a single unit for execution.

**Structure**:
```json
{
  "bundle_id": "phase-k-plus",
  "bundle_name": "Phase K+: Decision Context Enhancement",
  "version": "1.0.0",
  "workstreams": [...]
}
```

**Types**:
- **Single Workstream Bundle** - Contains one workstream
- **Multi-Workstream Bundle** - Contains multiple related workstreams
- **Phase Bundle** - All workstreams for a development phase

**Implementation**: `core/state/bundles.py`
**Schema**: `schema/bundle.schema.json`
**Examples**: `workstreams/phase-k-plus-bundle.json`

**Related Terms**: [Workstream](#workstream), [Bundle Loading](#bundle-loading)

---

### Bundle Loading
**Category**: State Management
**Definition**: Process of reading, validating, and preparing a bundle for execution.

**Steps**:
1. Read JSON file
2. Validate against schema
3. Extract workstreams
4. Register in database
5. Return ready-to-execute bundle

**Implementation**: `core/state/bundles.py:15`

**Usage**:
```python
from core.state.bundles import load_bundle
bundle = load_bundle("workstreams/phase-k-plus-bundle.json")
```

**Related Terms**: [Bundle](#bundle), [Workstream](#workstream), [Schema Validation](#schema-validation)

---

## C

### CCPM (Critical Chain Project Management)
**Category**: Integrations
**Definition**: Project management methodology integrated with the pipeline for task scheduling, buffer management, and critical path analysis.

**Features**:
- Critical chain identification
- Buffer management
- Resource leveling
- Progress tracking

**Implementation**: `pm/`
**Documentation**: `docs/Project_Management_docs/`

**Related Terms**: [OpenSpec](#openspec), [Phase](#phase)

---

### Change Proposal
**Category**: Specifications
**Definition**: Structured document proposing changes to specifications, tracked through the OpenSpec workflow.

**Location**: `specifications/changes/`

**Related Terms**: [OpenSpec](#openspec), [Spec Bridge](#spec-bridge)

---

### Checkpoint
**Category**: State Management
**Definition**: Snapshot of execution state that enables rollback or recovery.

**Types**:
- **Workstream Checkpoint** - Before/after workstream execution
- **Phase Checkpoint** - At phase boundaries
- **Manual Checkpoint** - User-triggered savepoint

**Implementation**: `core/state/checkpoint.py`

**Related Terms**: [Rollback Strategy](#rollback-strategy), [Compensation Action](#compensation-action-saga)

---

### Circuit Breaker
**Category**: Core Engine
**Definition**: Resilience pattern that prevents cascading failures by "opening" (stopping) execution when error thresholds are exceeded.

**States**:
- **CLOSED** - Normal operation
- **OPEN** - Blocking all requests (circuit "broken")
- **HALF_OPEN** - Testing if recovery is possible

**Configuration**:
```yaml
circuit_breaker:
  max_attempts: 3
  max_error_repeats: 2
  timeout_sec: 300
  reset_timeout_sec: 600
```

**Implementation**: `core/engine/circuit_breakers.py`
**Config**: `config/circuit_breaker.yaml`

**Related Terms**: [Retry Logic](#retry-logic), [Recovery Strategy](#recovery-strategy)

---

### Compensation Action (Saga)
**Category**: Integrations
**Definition**: Undo operation that reverses the effects of a completed action, part of the Saga pattern for distributed transactions.

**Purpose**:
- Enable rollback of multi-step workflows
- Maintain consistency across failures
- Support human-in-the-loop corrections

**Implementation**: `core/engine/compensation.py`

**Example**:
```yaml
forward_action: "Create database table"
compensation_action: "DROP TABLE users"
```

**Related Terms**: [Rollback Strategy](#rollback-strategy), [Saga Pattern](#saga-pattern), [UET Integration](#uet-universal-execution-templates)

---

### CRUD Operations
**Category**: State Management
**Definition**: Create, Read, Update, Delete operations for database entities (workstreams, steps, runs).

**Implementation**: `core/state/crud.py`

**Functions**:
- `create_workstream()` - Create new workstream record
- `get_workstream()` - Retrieve workstream by ID
- `update_workstream()` - Update workstream state
- `delete_workstream()` - Remove workstream (soft delete)

**Related Terms**: [Pipeline Database](#pipeline-database), [State Transition](#state-transition)

---

## D

### DAG (Directed Acyclic Graph)
**Category**: Core Engine
**Definition**: Graph structure representing task dependencies where edges point from prerequisite to dependent tasks, with no cycles.

**Purpose**:
- Model task dependencies
- Enable parallel execution
- Detect circular dependencies
- Calculate critical path

**Implementation**: `core/engine/scheduler.py` (UET: DAG-based scheduler)

**Related Terms**: [Dependency Resolution](#dependency-resolution), [Scheduler](#scheduler), [UET Integration](#uet-universal-execution-templates)

---

### Dependency Resolution
**Category**: Core Engine
**Definition**: Process of analyzing task dependencies to determine valid execution order.

**Algorithm**:
1. Parse `depends_on` from each step
2. Build dependency graph (DAG)
3. Topological sort for execution order
4. Identify parallelizable tasks

**Implementation**: `core/engine/orchestrator.py:120`

**Related Terms**: [DAG](#dag-directed-acyclic-graph), [Scheduler](#scheduler), [Step](#step)

---

### Detection Rule
**Category**: Error Detection
**Definition**: Pattern or logic that identifies a specific type of error in code, logs, or execution output.

**Format**:
```json
{
  "rule_id": "RUFF001",
  "pattern": "F401: '.*' imported but unused",
  "severity": "warning",
  "auto_fix": true
}
```

**Location**: `error/plugins/*/manifest.json`

**Related Terms**: [Error Plugin](#error-plugin), [Plugin Manifest](#plugin-manifest)

---

## E

### Error Context
**Category**: Error Detection
**Definition**: Contextual information about an error including stack trace, file location, surrounding code, and execution state.

**Structure**:
```python
{
  'error_id': 'ERR-001',
  'file': 'core/engine/executor.py',
  'line': 45,
  'message': 'Timeout exceeded',
  'stack_trace': '...',
  'context_lines': ['...'],
  'execution_state': {...}
}
```

**Implementation**: `error/engine/error_context.py`

**Related Terms**: [Error Engine](#error-engine), [Error Escalation](#error-escalation)

---

### Error Engine
**Category**: Error Detection
**Definition**: Core system that orchestrates error detection across multiple plugins and manages the error lifecycle.

**Responsibilities**:
- Load and manage error plugins
- Run detection on files/outputs
- Track error state (detected → fixed → verified)
- Escalate unresolved errors

**Implementation**: `error/engine/error_engine.py`
**CLI**: `python scripts/run_error_engine.py`

**Related Terms**: [Error Plugin](#error-plugin), [Error State Machine](#error-state-machine)

---

### Error Escalation
**Category**: Error Detection
**Definition**: Process of promoting errors through escalation levels when automatic fixes fail.

**Levels**:
1. **Auto-retry** - Plugin attempts fix
2. **Context repair** - Add context, retry
3. **Agent review** - AI agent analyzes
4. **Human escalation** - Require human input
5. **Quarantine** - Isolate problematic code

**Implementation**: `error/engine/error_engine.py`

**Related Terms**: [Error State Machine](#error-state-machine), [Human Review](#human-review)

---

### Error Plugin
**Category**: Error Detection
**Definition**: Modular component that detects and optionally fixes specific types of errors (linting, type checking, security scans).

**Structure**:
```
error/plugins/python_ruff/
├── __init__.py
├── plugin.py          # parse() and fix() methods
└── manifest.json      # Metadata and rules
```

**Required Methods**:
- `parse(file_path)` → List of errors
- `fix(error)` → Boolean success (optional)

**Examples**:
- `error/plugins/python_ruff/` - Python linting
- `error/plugins/javascript_eslint/` - JavaScript linting
- `error/plugins/security_bandit/` - Security scanning

**Implementation**: `error/plugins/`
**Documentation**: `docs/plugin-quick-reference.md`

**Related Terms**: [Plugin Manifest](#plugin-manifest), [Detection Rule](#detection-rule)

---

### Error State Machine
**Category**: Error Detection
**Definition**: State machine managing error lifecycle from detection to resolution.

**States**:
- **DETECTED** - Error found
- **AUTO_FIX_ATTEMPTED** - Plugin tried to fix
- **FIXED** - Fix applied
- **VERIFIED** - Fix confirmed
- **ESCALATED** - Sent to higher level
- **QUARANTINED** - Isolated from main code
- **RESOLVED** - Final resolution

**Implementation**: `error/engine/state_machine.py`

**Related Terms**: [Error Engine](#error-engine), [Error Escalation](#error-escalation)

---

### Event Bus
**Category**: Core Engine
**Definition**: Pub/sub messaging system for coordinating workers, tracking execution events, and enabling event sourcing.

**Event Types**:
- **Worker Events**: `WORKER_SPAWNED`, `WORKER_IDLE`, `WORKER_BUSY`, `WORKER_TERMINATED`
- **Task Events**: `TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED`
- **Patch Events**: `PATCH_CREATED`, `PATCH_APPLIED`, `PATCH_QUARANTINED`
- **Gate Events**: `GATE_PASSED`, `GATE_FAILED`

**Implementation**: `core/engine/event_bus.py`
**Storage**: `run_events` table (UET alignment)

**Usage**:
```python
event_bus.emit(EventType.TASK_COMPLETED, run_id, {'task_id': 'T1'})
events = event_bus.get_events(run_id, EventType.TASK_FAILED)
```

**Related Terms**: [Worker Lifecycle](#worker-lifecycle), [Event Sourcing](#event-sourcing), [UET Integration](#uet-universal-execution-templates)

---

### Event Sourcing
**Category**: State Management
**Definition**: Architectural pattern where all state changes are stored as a sequence of events, enabling replay and audit.

**Benefits**:
- Complete audit trail
- Event replay for debugging
- Time-travel debugging
- State reconstruction

**Implementation**: `run_events` table in database

**Related Terms**: [Event Bus](#event-bus), [Pipeline Database](#pipeline-database)

---

### Executor
**Category**: Core Engine
**Definition**: Component responsible for executing individual steps by invoking tools and handling results.

**Responsibilities**:
- Invoke tool adapters
- Handle timeouts
- Capture output
- Report results to orchestrator

**Implementation**: `core/engine/executor.py`

**Related Terms**: [Orchestrator](#orchestrator), [Adapter](#adapter), [Timeout Handling](#timeout-handling)

---

## F

### Feedback Loop
**Category**: Core Engine
**Definition**: Test-driven execution pattern where test results automatically create fix tasks.

**Workflow**:
1. Task executes
2. Tests run
3. If tests fail → Create fix task
4. Fix task prioritized
5. Rerun tests after fix

**Implementation**: `core/engine/feedback_loop.py` (UET alignment)

**Related Terms**: [Test Gates](#test-gates), [UET Integration](#uet-universal-execution-templates)

---

### File Hash Cache
**Category**: Error Detection
**Definition**: Cache of file content hashes used for incremental detection (only check changed files).

**Purpose**:
- Skip unchanged files during detection
- Reduce detection time
- Avoid redundant work

**Implementation**: `error/shared/utils/hash_utils.py`

**Related Terms**: [Incremental Detection](#incremental-detection)

---

### Fix Strategy
**Category**: Error Detection
**Definition**: Plugin-specific logic for automatically fixing detected errors.

**Implementation**: `fix()` method in error plugins

**Example** (Python Ruff):
```python
def fix(self, error):
    """Auto-fix import errors."""
    if error['code'] == 'F401':  # Unused import
        return remove_import_line(error['file'], error['line'])
    return False
```

**Related Terms**: [Error Plugin](#error-plugin), [Recovery Strategy](#recovery-strategy)

---

## G

### Gate
See [Test Gates](#test-gates)

---

## H

### Human Review
**Category**: Core Engine
**Definition**: Structured escalation workflow where complex issues are presented to humans for decision.

**Trigger Conditions**:
- Gate failure after N retries
- Merge conflict detected
- Patch quarantined
- Budget threshold exceeded

**Review Format**:
```yaml
issue_summary: "Merge conflict in core/engine/executor.py"
error_context: [list of error events]
prior_attempts: [self-heal attempts]
proposed_options:
  - approve: "Accept changes from feature branch"
  - reject: "Revert to main branch"
  - adjust: "Manual merge required"
```

**Implementation**: `core/engine/human_review.py` (UET alignment)

**Related Terms**: [Error Escalation](#error-escalation), [UET Integration](#uet-universal-execution-templates)

---

## I

### Incremental Detection
**Category**: Error Detection
**Definition**: Optimization where error detection only runs on files that have changed since last check.

**Mechanism**:
1. Compute file hash
2. Compare to cached hash
3. Skip if unchanged
4. Update cache after detection

**Implementation**: `error/shared/utils/hash_utils.py`

**Related Terms**: [File Hash Cache](#file-hash-cache), [Error Engine](#error-engine)

---

### Integration Worker
**Category**: Core Engine
**Definition**: Dedicated worker responsible for merging parallel workstream results in deterministic order.

**Responsibilities**:
- Collect patches from parallel workers
- Merge in priority order
- Detect merge conflicts
- Run validation after each merge
- Rollback on failure

**Implementation**: `core/engine/integration_worker.py`

**Related Terms**: [Worker Lifecycle](#worker-lifecycle), [Merge Strategy](#merge-strategy), [UET Integration](#uet-universal-execution-templates)

---

## L

### Ledger
See [Patch Ledger](#patch-ledger)

---

### Layer
**Category**: Architecture
**Definition**: Architectural layer assignment (infra, domain, api, ui) that enforces dependency rules. Modules can only depend on same or lower layers.

**Layers** (low to high):

1. **Infrastructure (`infra`)**
   - Description: Database, state, schemas, configuration
   - Dependencies: None
   - Modules: `core.state`, `schema`, `config`

2. **Domain Logic (`domain`)**
   - Description: Core business logic and orchestration
   - Dependencies: infra
   - Modules: `core.engine`, `core.planning`, `error.engine`, `specifications.tools`

3. **API & Integrations (`api`)**
   - Description: External tool integrations and bridges
   - Dependencies: infra, domain
   - Modules: `aim`, `pm`, `specifications.bridge`

4. **User Interface (`ui`)**
   - Description: CLI, GUI, user-facing tools
   - Dependencies: infra, domain, api (all lower layers)
   - Modules: `engine`, `error.plugins`, `scripts`, `gui`

**Dependency Rules**:
- No circular dependencies between modules
- Modules can only depend on same or lower layer
- Infrastructure layer has no dependencies
- UI layer can depend on all lower layers

**Implementation**: `docs/CODEBASE_INDEX.yaml`, `schema/module.schema.json`

**Related Terms**: [Module](#module), [Module Dependencies](#module-dependencies)

---

## M

### Merge Strategy
**Category**: Core Engine
**Definition**: Algorithm for deterministically merging parallel workstream results.

**Decision Tree**:
1. Identify ready branches (tests passed, tasks succeeded)
2. Sort by: critical path, dependency count, age
3. Merge in order
4. Validate after each merge
5. Rollback on failure

**Implementation**: `core/engine/merge_strategy.py` (UET alignment)

**Related Terms**: [Integration Worker](#integration-worker), [DAG](#dag-directed-acyclic-graph), [UET Integration](#uet-universal-execution-templates)

---

### Module
**Category**: Architecture
**Definition**: Self-contained functional unit with ULID-prefixed artifacts, clear boundaries, and layer assignment. All related code, tests, schemas, and docs colocated in one directory.

**Structure**:
```
modules/core-state/
  010003_db.py                    # Code with ULID prefix
  010003_db.test.py               # Test oracle
  010003_db.schema.json           # Contract
  010003_module.manifest.yaml     # Module identity
  .state/current.json             # Module state
```

**Module Boundaries Determined By**:
- **Functional cohesion** - Related capabilities grouped together
- **Layer rules** - Can only depend on same or lower layers
- **Import independence** - Clear import contracts
- **AI context size** - Optimized for AI tool loading

**Implementation**: `modules/*/`, `schema/module.schema.json`, `MODULES_INVENTORY.yaml`

**Related Terms**: [Module-Centric Architecture](#module-centric-architecture), [ULID Prefix](#ulid-universally-unique-lexicographically-sortable-identifier), [Module Manifest](#module-manifest), [Layer](#layer), [Submodule](#submodule)

**References**: `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md`

---

### Module-Centric Architecture
**Category**: Architecture
**Definition**: Code organization pattern where all module artifacts (code, tests, schemas, docs) are colocated in a single directory, enabling deterministic AI context loading and atomic SafePatch operations.

**Benefits**:
- **Deterministic context loading**: `load_module("modules/core-state/")`
- **Atomic SafePatch**: Clone just one directory
- **ULID-based identity**: Machine-verifiable relationships
- **Parallel AI execution**: No shared bottlenecks

**vs Artifact-Type Organization**:

| Aspect | Artifact-Type (Legacy) | Module-Centric (Current) |
|--------|------------------------|--------------------------|
| Structure | `core/state/db.py`<br>`tests/state/test_db.py`<br>`docs/STATE_GUIDE.md`<br>`schema/state.schema.json` | `modules/core-state/`<br>`010003_db.py`<br>`010003_db.test.py`<br>`010003_db.md`<br>`010003_db.schema.json` |
| Context Loading | 4 separate locations | Single directory |
| Relationships | Implicit (naming convention) | Explicit (ULID prefix) |
| SafePatch | Complex file tracking | Atomic clone |

**Implementation**: `modules/`, `MODULES_INVENTORY.yaml`

**Related Terms**: [Module](#module), [Artifact-Type Organization](#artifact-type-organization), [ULID Prefix](#ulid-universally-unique-lexicographically-sortable-identifier)

**References**: `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md`, `Module-Centric/architecture/WHY_MODULE_CENTRIC_WORKS.md`

---

### Module Dependencies
**Category**: Architecture
**Definition**: Explicit dependencies between modules, tracked in module manifests and enforced by layer rules.

**Dependency Types**:
- **Module Dependencies**: Other modules required (by `module_id`)
- **External Dependencies**: Third-party packages (pip, npm, etc.)

**Example** (from `core-engine` manifest):
```yaml
dependencies:
  modules:
    - "aim-environment"
    - "aim-registry"
    - "core-planning"
    - "core-state"
  external:
    - name: "pyyaml"
      version: ">=6.0"
```

**Enforcement**: Layer rules + CI validation

**Related Terms**: [Module](#module), [Layer](#layer), [Module Manifest](#module-manifest)

---

### Module Manifest
**Category**: Architecture
**Definition**: YAML file (`module.manifest.yaml`) defining module identity, dependencies, artifacts, contracts, and AI metadata. Machine-readable module specification.

**Required Fields**:
- `module_id` - Kebab-case identifier (e.g., `core-state`)
- `ulid_prefix` - 6-character prefix (e.g., `010003`)
- `purpose` - Concise purpose statement
- `layer` - Architectural layer (`infra`/`domain`/`api`/`ui`)

**Example**:
```yaml
module_id: "core-state"
ulid_prefix: "010003"
purpose: "Database operations and state management"
layer: "infra"
artifacts:
  code:
    - path: "010003_db.py"
      ulid: "01000300000000000000000001"
  tests:
    - path: "010003_db.test.py"
      ulid: "01000300000000000000000002"
dependencies:
  modules: []
  external:
    - name: "sqlite3"
```

**Schema**: `schema/module.schema.json`
**Template**: `templates/module.manifest.template.yaml`

**Related Terms**: [Module](#module), [ULID Prefix](#ulid-universally-unique-lexicographically-sortable-identifier), [Layer](#layer)

---

## O

### OpenSpec
**Category**: Specifications
**Definition**: System for managing specification changes through a structured proposal, review, and integration workflow.

**Workflow**:
1. Create change proposal
2. Review and approval
3. Generate workstream from spec
4. Execute changes
5. Update specification index

**Implementation**: `specifications/bridge/`
**Documentation**: `docs/Project_Management_docs/openspec_bridge.md`

**Related Terms**: [Spec Bridge](#spec-bridge), [Change Proposal](#change-proposal)

---

### Orchestrator
**Category**: Core Engine
**Definition**: Central coordinator that manages workstream execution, dependency resolution, and worker assignment.

**Responsibilities**:
- Load workstream bundles
- Build dependency DAG
- Schedule tasks
- Coordinate workers
- Handle errors and retries

**Types**:
- **Workstream Orchestrator** - `core/engine/orchestrator.py`
- **Job Orchestrator** - `engine/orchestrator/orchestrator.py`

**Related Terms**: [Executor](#executor), [Scheduler](#scheduler), [Worker Lifecycle](#worker-lifecycle)

---

## P

### Patch
**Category**: Patch Management
**Definition**: Unified diff representing code changes, used as the primary artifact for code modifications.

**Format**: Unified diff (GNU diff format)
```diff
diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
+# New line
 def foo():
     pass
```

**Related Terms**: [Patch Artifact](#patch-artifact), [Patch Ledger](#patch-ledger), [Patch-First Workflow](#patch-first-workflow)

---

### Patch Artifact
**Category**: Patch Management
**Definition**: Canonical representation of a patch with metadata (UET-aligned).

**Structure**:
```json
{
  "patch_id": "01J2ZB...",
  "format": "unified_diff",
  "target_repo": "/path/to/repo",
  "origin": {
    "execution_request_id": "01J2Z9...",
    "tool_id": "aider",
    "created_at": "2025-11-23T00:00:00Z"
  },
  "diff_text": "diff --git...",
  "scope": {
    "files_touched": ["file.py"],
    "line_insertions": 5,
    "line_deletions": 2,
    "hunks": 1
  }
}
```

**Implementation**: `core/patches/patch_artifact.py` (UET alignment)
**Schema**: `schema/uet/patch_artifact.v1.json`

**Related Terms**: [Patch Ledger](#patch-ledger), [UET Integration](#uet-universal-execution-templates)

---

### Patch-First Workflow
**Category**: Patch Management
**Definition**: Development workflow where all code changes are represented as patches (unified diffs) before application.

**Workflow**:
1. Tool generates patch (not direct edit)
2. Orchestrator creates PatchArtifact
3. Validate patch (format, scope, constraints)
4. Apply patch to worktree
5. Run language-aware validation (tests, linters)
6. If tests pass → commit
7. If tests fail → quarantine patch

**Benefits**:
- Full audit trail
- Reviewable before application
- Rollback support
- Language-agnostic

**Related Terms**: [Patch Artifact](#patch-artifact), [Patch Ledger](#patch-ledger), [UET Integration](#uet-universal-execution-templates)

---

### Patch Ledger
**Category**: Patch Management
**Definition**: Audit trail tracking the complete lifecycle of a patch from creation to commit.

**State Machine**:
```
created → validated → queued → applied → verified → committed
   ↓         ↓          ↓         ↓         ↓
apply_failed, rolled_back, quarantined, dropped
```

**Tracked Data**:
- State history with timestamps
- Validation results (format, scope, constraints, tests)
- Application attempts and errors
- Quarantine status

**Implementation**: `core/patches/patch_ledger.py` (UET alignment)
**Schema**: `schema/uet/patch_ledger_entry.v1.json`

**Related Terms**: [Patch Artifact](#patch-artifact), [Patch Policy](#patch-policy), [UET Integration](#uet-universal-execution-templates)

---

### Patch Policy
**Category**: Patch Management
**Definition**: Constraints and rules governing what patches are allowed, enforced at validation time.

**Scope Levels**:
- **Global** - Apply to all patches
- **Project** - Specific to a project
- **Phase** - Specific to a development phase
- **Document** - Specific to individual files

**Constraints**:
```json
{
  "allowed_formats": ["unified_diff"],
  "max_lines_changed": 500,
  "max_files_changed": 10,
  "forbid_binary_patches": true,
  "forbid_touching_paths": ["\\.git/", "\\.env"],
  "require_tests_for_paths": ["core/.*\\.py"],
  "oscillation_threshold": 3
}
```

**Implementation**: `core/patches/patch_policy.py` (UET alignment)
**Schema**: `schema/uet/patch_policy.v1.json`
**Config**: `config/patch_policies/*.json`

**Related Terms**: [Patch Ledger](#patch-ledger), [Patch Validator](#patch-validator)

---

### Patch Validator
**Category**: Patch Management
**Definition**: Component that validates patches against format, scope, and policy constraints.

**Validation Checks**:
1. **Format** - Must be unified diff
2. **Scope** - Files/lines within limits
3. **Constraints** - No forbidden paths, binary patches
4. **Tests** - Required tests exist for modified code

**Implementation**: `core/patches/patch_validator.py` (UET alignment)

**Related Terms**: [Patch Artifact](#patch-artifact), [Patch Policy](#patch-policy)

---

### Pattern Automation Hooks
**Category**: Framework
**Definition**: Self-learning automation layer that attaches to the UET orchestrator to capture execution telemetry, persist it to the pattern automation database, and generate pattern drafts/approvals.

**Features**:
- Orchestrator hooks for task start/finish events with graceful fallback when automation is unavailable
- Detection-config-driven behavior (drafts, approvals, database writes)
- Telemetry capture for future automation and pattern refinement

**Implementation**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/` (hooks, config, database), integration in `modules/core-engine/m010001_uet_orchestrator.py`

**Related Terms**: [UET (Universal Execution Templates)](#uet-universal-execution-templates), [Orchestrator](#orchestrator)

---

### Phase
**Category**: Project Management
**Definition**: Major development milestone containing multiple related workstreams.

**Structure**:
```yaml
phase_id: PH-UET
name: "Universal Execution Templates Integration"
duration: "9-10 weeks"
workstreams:
  - WS-UET-A1: Schema Foundation
  - WS-UET-A2: Worker Health Checks
  - ...
```

**Examples**:
- **Phase K** - Documentation foundation
- **Phase UET** - UET framework integration
- **Phase 09** - CCPM integration

**Documentation**: `docs/planning/`

**Related Terms**: [Workstream](#workstream), [CCPM](#ccpm-critical-chain-project-management)

---

### Pipeline Database
**Category**: State Management
**Definition**: SQLite database storing execution state (runs, workstreams, steps, attempts).

**Location**: `.worktrees/pipeline_state.db` (configurable via `PIPELINE_DB_PATH`)

**Schema**: `schema/schema.sql`

**Tables**:
- `runs` - Execution runs
- `workstreams` - Workstream records
- `attempts` - Step execution attempts
- `patches` - Patch artifacts (UET)
- `patch_ledger_entries` - Patch lifecycle (UET)
- `run_events` - Event sourcing log (UET)

**Implementation**: `core/state/db.py`

**Related Terms**: [CRUD Operations](#crud-operations), [State Transition](#state-transition), [UET Integration](#uet-universal-execution-templates)

---

### Plugin Manifest
**Category**: Error Detection
**Definition**: JSON file describing an error plugin's capabilities, rules, and metadata.

**Structure**:
```json
{
  "plugin_id": "python_ruff",
  "name": "Python Ruff Linter",
  "version": "1.0.0",
  "language": "python",
  "file_patterns": ["*.py"],
  "detection_rules": [...],
  "auto_fix_supported": true
}
```

**Location**: `error/plugins/*/manifest.json`

**Related Terms**: [Error Plugin](#error-plugin), [Detection Rule](#detection-rule)

---

### Profile Matching
**Category**: Integrations
**Definition**: Algorithm for matching a task/step to the most appropriate tool profile.

**Matching Criteria**:
- Task type (code_edit, testing, linting)
- File extensions (.py, .ps1)
- Tool capabilities
- User preferences

**Implementation**: `core/engine/tools.py`

**Related Terms**: [Tool Profile](#tool-profile), [AIM](#aim-ai-environment-manager)

---

## R

### Recovery Strategy
**Category**: Core Engine
**Definition**: Logic for recovering from step failures through retry, context repair, or alternative approaches.

**Strategies**:
- **Immediate Retry** - Retry with exponential backoff
- **Context Repair** - Add more context, retry
- **Alternative Tool** - Try different tool
- **Reduced Scope** - Simplify task
- **Escalate** - Promote to higher level

**Implementation**: `core/engine/recovery.py`

**Related Terms**: [Retry Logic](#retry-logic), [Circuit Breaker](#circuit-breaker), [Error Escalation](#error-escalation)

---

### Retry Logic
**Category**: Core Engine
**Definition**: Mechanism for retrying failed operations with exponential backoff.

**Configuration**:
```yaml
max_attempts: 3
backoff_multiplier: 2
initial_delay_sec: 1
max_delay_sec: 60
```

**Implementation**: `core/engine/retry.py`

**Related Terms**: [Circuit Breaker](#circuit-breaker), [Recovery Strategy](#recovery-strategy)

---

### Rollback Strategy
**Category**: Integrations
**Definition**: Method for undoing changes when failures occur (Saga pattern).

**Scopes**:
- **Patch Rollback** - Git revert of single patch
- **Task Rollback** - Undo single task
- **Phase Rollback** - Compensation cascade across phase
- **Multi-Phase Rollback** - Full rollback of multiple phases

**Implementation**: `core/engine/compensation.py` (UET alignment)

**Related Terms**: [Compensation Action](#compensation-action-saga), [Checkpoint](#checkpoint), [UET Integration](#uet-universal-execution-templates)

---

## S

### Saga Pattern
**Category**: Integrations
**Definition**: Design pattern for managing distributed transactions through compensating actions.

**Components**:
- **Forward Actions** - Normal execution steps
- **Compensation Actions** - Undo/rollback steps

**Example**:
```yaml
saga_steps:
  - step: create_table
    compensation: drop_table
  - step: insert_data
    compensation: delete_data
```

**Implementation**: `core/engine/compensation.py`

**Related Terms**: [Compensation Action](#compensation-action-saga), [Rollback Strategy](#rollback-strategy)

---

### Scheduler
**Category**: Core Engine
**Definition**: Component that determines execution order of tasks based on dependencies and parallelism.

**Types**:
- **Sequential Scheduler** - Current implementation
- **DAG Scheduler** - UET alignment (dependency-aware parallel execution)

**Implementation**: `core/engine/scheduler.py`

**Related Terms**: [DAG](#dag-directed-acyclic-graph), [Dependency Resolution](#dependency-resolution), [UET Integration](#uet-universal-execution-templates)

---

### Schema Validation
**Category**: Specifications
**Definition**: Process of validating JSON/YAML artifacts against JSON Schema definitions.

**Schemas**:
- `schema/workstream.schema.json` - Workstream structure
- `schema/sidecar.schema.json` - Sidecar metadata
- `schema/uet/*.json` - UET framework schemas (17 total)

**Validation**:
```bash
python scripts/validate_workstreams.py
python scripts/validate_workstreams_authoring.py
```

**Related Terms**: [Workstream](#workstream), [UET Integration](#uet-universal-execution-templates)

---

### Sidecar Metadata
**Category**: State Management
**Definition**: Metadata file (`.sidecar.yaml`) accompanying a specification or workstream with execution history and context.

**Structure**:
```yaml
spec_id: "SPEC-001"
last_modified: "2025-11-23"
execution_history:
  - run_id: "RUN-123"
    status: "SUCCESS"
    timestamp: "2025-11-23T00:00:00Z"
```

**Schema**: `schema/sidecar_metadata.schema.yaml`

**Related Terms**: [OpenSpec](#openspec), [Specification Index](#specification-index)

---

### Shared Module
**Category**: Architecture
**Definition**: Standalone module providing common utilities/types to other modules. Listed explicitly in `dependencies.modules` of consuming modules. Has independent lifecycle.

**Example** (`error-shared` module):
```
modules/error-shared/
  010021_types.py
  010021_time.py
  010021_hashing.py
  010021_jsonl_manager.py
  010021_security.py
  010021_module.manifest.yaml
```

**Usage** (in consuming module):
```yaml
dependencies:
  modules: ["error-shared"]
```

**vs Submodule**:

| Aspect | Shared Module | Submodule |
|--------|---------------|-----------|
| Ownership | Independent module | Parent module controls |
| Dependency | Explicit in manifest | Implicit (internal) |
| Lifecycle | Independent versioning | Follows parent |
| Example | `error-shared` (ULID 010021) | `error-engine/submodules/state-machine` |

**Implementation**: `modules/error-shared/`

**Related Terms**: [Module](#module), [Submodule](#submodule), [Module Dependencies](#module-dependencies)

**References**: `AGENT_3_COMPLETION_REPORT.md`, `MODULES_INVENTORY.yaml`

---

### Spec Bridge
**Category**: Specifications
**Definition**: Integration layer between OpenSpec change proposals and workstream generation.

**Workflow**:
1. OpenSpec proposal approved
2. Spec Bridge generates workstream JSON
3. Workstream executed
4. Specification updated with results

**Implementation**: `specifications/bridge/`

**Related Terms**: [OpenSpec](#openspec), [Change Proposal](#change-proposal)

---

### Submodule
**Category**: Architecture
**Definition**: Hierarchical organization within a complex module. Each submodule has its own manifest and is controlled by parent module. Used for internal structure, not external dependencies.

**Example Structure**:
```
modules/error-engine/
  010004_module.manifest.yaml
  submodules/
    state-machine/
      manifest.yaml
      010004_state_machine.py
    plugin-manager/
      manifest.yaml
      010004_plugin_manager.py
```

**vs Shared Module**:

| Aspect | Submodule | Shared Module |
|--------|-----------|---------------|
| Purpose | Internal organization | External dependency |
| Control | Parent module controls | Independent lifecycle |
| Dependencies | No external dependencies | Listed in `dependencies.modules` |
| Example | `error-engine/submodules/state-machine` | `error-shared` (ULID 010021) |

**Schema**: `schema/module.schema.json` (lines 331-346)

**Related Terms**: [Module](#module), [Shared Module](#shared-module), [Module Manifest](#module-manifest)

---

### Spec Guard
**Category**: Specifications
**Definition**: Validation layer that prevents invalid changes to specifications.

**Checks**:
- Schema compliance
- Cross-reference integrity
- Breaking change detection

**Implementation**: `specifications/tools/guard/`

**Related Terms**: [Spec Resolver](#spec-resolver), [Specification Index](#specification-index)

---

### Spec Patcher
**Category**: Specifications
**Definition**: Tool for applying patches to specification documents.

**Implementation**: `specifications/tools/patcher/`

**Related Terms**: [Patch](#patch), [Spec Guard](#spec-guard)

---

### Spec Resolver
**Category**: Specifications
**Definition**: Tool that resolves URI references between specifications.

**Purpose**:
- Resolve `spec://` URIs
- Validate cross-references
- Generate dependency graph

**Implementation**: `specifications/tools/resolver/`

**Related Terms**: [URI Resolution](#uri-resolution), [Specification Index](#specification-index)

---

### Specification Index
**Category**: Specifications
**Definition**: Auto-generated index of all specifications with metadata and cross-references.

**Generated By**: `scripts/generate_spec_index.py`

**Implementation**: `specifications/tools/indexer/`

**Related Terms**: [Spec Resolver](#spec-resolver), [OpenSpec](#openspec)

---

### State Transition
**Category**: State Management
**Definition**: Change of execution state for a workstream, step, or patch.

**Workstream States**:
- `PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED`

**Patch States** (UET):
- `created` → `validated` → `queued` → `applied` → `verified` → `committed`

**Implementation**: `core/state/crud.py`

**Related Terms**: [Pipeline Database](#pipeline-database), [Patch Ledger](#patch-ledger)

---

### Step
**Category**: Core Engine
**Definition**: Atomic unit of work within a workstream, executed by a single tool invocation.

**Structure**:
```json
{
  "step_id": "step-01",
  "name": "Fix linting errors",
  "description": "Run ruff and fix auto-fixable issues",
  "files": ["core/engine/executor.py"],
  "validation": {
    "command": "ruff check --fix",
    "expected_exit_code": 0
  },
  "depends_on": []
}
```

**States**: `PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`

**Schema**: `schema/workstream.schema.json`

**Related Terms**: [Workstream](#workstream), [Executor](#executor), [Dependency Resolution](#dependency-resolution)

---

## T

### Test Adapter
**Category**: Integrations
**Definition**: Adapter that wraps test runners (pytest, Pester, etc.) for consistent test execution.

**Implementation**: `engine/adapters/test_adapter.py`

**Related Terms**: [Adapter](#adapter), [Test Gates](#test-gates)

---

### Test Gates
**Category**: Core Engine
**Definition**: Synchronization points where tests must pass before execution can proceed (UET pattern).

**Gate Types**:
- **GATE_LINT** - All linting must pass
- **GATE_UNIT** - All unit tests must pass
- **GATE_INTEGRATION** - All integration tests must pass
- **GATE_SECURITY** - Security scans must pass

**Behavior**:
- Dependent tasks blocked until gate cleared
- Gate failures trigger error escalation
- Fix tasks auto-created on failures

**Implementation**: `core/engine/test_gates.py`

**Related Terms**: [Feedback Loop](#feedback-loop), [UET Integration](#uet-universal-execution-templates)

---

### Timeout Handling
**Category**: Core Engine
**Definition**: Mechanism for enforcing time limits on tool execution.

**Configuration**:
```yaml
timeouts:
  wall_clock_sec: 600
  cpu_limit_sec: 300
```

**Implementation**: `core/engine/executor.py:120`

**Related Terms**: [Executor](#executor), [Tool Profile](#tool-profile)

---

### Tool Profile
**Category**: Core Engine
**Definition**: Configuration defining how to invoke a specific tool (Aider, Codex, pytest, etc.).

**Structure**:
```yaml
aider:
  command: "aider"
  model: "gpt-4"
  args:
    - "--no-auto-commits"
    - "--yes"
  timeout_sec: 600
  capabilities: ["code_edit", "refactor"]
```

**Location**: `invoke.yaml`, `config/tool_profiles.yaml`

**Implementation**: `core/engine/tools.py`

**Related Terms**: [Profile Matching](#profile-matching), [Adapter](#adapter)

---

### Tool Registry
**Category**: Integrations
**Definition**: Central registry of available AI tools and their capabilities.

**Managed By**: AIM (AI Environment Manager)

**Implementation**: `aim/registry/`

**Related Terms**: [AIM](#aim-ai-environment-manager), [Tool Profile](#tool-profile)

---

## U

### UET (Universal Execution Templates)
**Category**: Framework
**Definition**: Reference implementation framework providing canonical schemas and patterns for AI orchestration.

**Key Concepts**:
- **Worker Lifecycle** - SPAWNING → IDLE → BUSY → DRAINING → TERMINATED
- **Patch Management** - PatchArtifact, PatchLedger, PatchPolicy
- **Event Sourcing** - Full event history in `run_events` table
- **DAG Scheduler** - Dependency-aware parallel execution
- **Test Gates** - Synchronization points (LINT, UNIT, INTEGRATION)
- **Human Review** - Structured escalation workflow
- **Compensation** - Saga pattern rollback

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`

**Schemas**: 17 JSON schemas in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/`

**Integration Status**: ~40% aligned (see `UET_INTEGRATION_PLAN_ANALYSIS.md`)

**Related Terms**: [Patch-First Workflow](#patch-first-workflow), [Worker Lifecycle](#worker-lifecycle), [Test Gates](#test-gates)

---

### UET Compatibility Shim
**Category**: Framework
**Definition**: Backward-compatibility adapters that re-export UET implementations under legacy import paths so existing tools continue working after the module-centric migration.

**Behavior**:
- Reuses UET orchestrator and scheduler while keeping old module names
- Keeps tests and scripts running without immediate refactors
- Emits optional warnings for future migration

**Implementation**: `modules/core-engine/m010001_orchestrator.py`, `modules/core-engine/m010001_pipeline_plus_orchestrator.py`, shared fallbacks under `modules/error-shared/__init__.py`

**Related Terms**: [Module-Centric Architecture](#module-centric-architecture), [Orchestrator](#orchestrator), [UET (Universal Execution Templates)](#uet-universal-execution-templates)

---

### ULID (Universally Unique Lexicographically Sortable Identifier)
**Category**: Framework
**Definition**: 26-character globally unique identifier with lexicographic sorting (timestamp-based). Used for run IDs and module identity. First 6 characters serve as module prefix.

**Format**: 26 uppercase alphanumeric characters (base32, Base32-Crockford)
- **Example**: `01JDZX2A3B4C5D6E7F8G9H0J1K`

**Properties**:
- **Globally unique** - No collisions across systems
- **Lexicographically sortable** - Chronological order
- **Timestamp-based** - First 48 bits encode millisecond timestamp
- **Compact** - More compact than UUID v4 (26 vs 36 chars)
- **URL-safe** - No special characters

**Module Usage**:

1. **ULID Prefix** (first 6 chars):
   - Identifies module: `010003` = `core-state` module
   - Shared by all artifacts in module
   - Examples: `010003_db.py`, `010003_db.test.py`

2. **Full ULID** (26 chars):
   - Identifies specific artifact
   - Example: `01000300000000000000000001`

**Benefits for Modules**:
- Machine-verifiable relationships (same prefix = same module)
- Lexicographic sorting (chronological order)
- Globally unique (no collisions)

**Database Usage**:
- `run_ulid` - Run identifier
- `patch_id` - Patch artifact identifier
- `ledger_id` - Patch ledger entry ID
- `event_id` - Event identifier

**Implementation**: `python-ulid` package

**Related Terms**: [Module](#module), [Module Manifest](#module-manifest), [ULID Prefix](#ulid-prefix), [Patch Artifact](#patch-artifact)

**References**: `schema/module.schema.json`

---

### ULID Prefix
**Category**: Architecture
**Definition**: First 6 characters of a ULID used to identify a module. All artifacts within a module share the same prefix.

**Examples**:
- `010003` - `core-state` module
- `010004` - `error-engine` module
- `010021` - `error-shared` module

**Usage in File Naming**:
```
modules/core-state/
  010003_db.py
  010003_db.test.py
  010003_db.schema.json
  010003_module.manifest.yaml
```

**Benefits**:
- Machine-verifiable module membership
- Consistent naming convention
- Enables tooling to auto-detect module boundaries

**Assigned in**: `module.manifest.yaml` (`ulid_prefix` field)

**Related Terms**: [ULID](#ulid-universally-unique-lexicographically-sortable-identifier), [Module](#module), [Module Manifest](#module-manifest)

---

### URI Resolution
**Category**: Specifications
**Definition**: Process of resolving `spec://` URIs to actual specification documents.

**Format**: `spec://core/engine/orchestrator#section-name`

**Implementation**: `specifications/tools/resolver/`

**Related Terms**: [Spec Resolver](#spec-resolver), [Specification Index](#specification-index)

---

## W

### Worker
**Category**: Core Engine
**Definition**: Process or thread that executes tasks assigned by the orchestrator.

**Types**:
- **Tool Worker** - Executes tasks via adapters (Aider, Codex, etc.)
- **Integration Worker** - Dedicated to merging parallel results

**Related Terms**: [Worker Lifecycle](#worker-lifecycle), [Worker Pool](#worker-pool)

---

### Worker Health
**Category**: Core Engine
**Definition**: Monitoring system tracking worker availability and performance via heartbeat.

**Health Checks**:
- Heartbeat timeout (default: 300 seconds)
- Error count threshold
- Resource usage

**Actions**:
- Quarantine unhealthy workers
- Reassign tasks
- Spawn replacement workers

**Implementation**: `core/engine/worker_health.py` (UET alignment)

**Related Terms**: [Worker Lifecycle](#worker-lifecycle), [UET Integration](#uet-universal-execution-templates)

---

### Worker Lifecycle
**Category**: Core Engine
**Definition**: State machine managing worker lifetime from spawn to termination (UET pattern).

**States**:
- **SPAWNING** - Worker being created
- **IDLE** - Worker ready for tasks
- **BUSY** - Worker executing task
- **DRAINING** - Worker finishing current task before shutdown
- **TERMINATED** - Worker stopped

**Implementation**: `core/engine/worker.py`

**Related Terms**: [Worker Pool](#worker-pool), [Worker Health](#worker-health), [UET Integration](#uet-universal-execution-templates)

---

### Worker Pool
**Category**: Core Engine
**Definition**: Manager for a collection of workers, handling spawning, assignment, and termination.

**Responsibilities**:
- Spawn workers on demand
- Assign tasks to idle workers
- Monitor worker health
- Drain and terminate workers gracefully

**Implementation**: `core/engine/worker.py` (WorkerPool class)

**Related Terms**: [Worker Lifecycle](#worker-lifecycle), [Orchestrator](#orchestrator)

---

### Workstream
**Category**: Core Engine
**Definition**: Sequence of steps (tasks) executed to achieve a specific goal, the fundamental unit of work execution.

**Structure**:
```json
{
  "ws_id": "WS-UET-A1",
  "name": "Schema Foundation",
  "description": "Copy UET schemas to production",
  "steps": [...],
  "depends_on": [],
  "estimated_context_tokens": 5000,
  "max_cost_usd": 10.0
}
```

**States**: `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`

**Schema**: `schema/workstream.schema.json`
**Examples**: `workstreams/*.json`

**Related Terms**: [Step](#step), [Bundle](#bundle), [Orchestrator](#orchestrator)

---

### Worktree Management
**Category**: State Management
**Definition**: Management of Git worktrees for isolated execution environments.

**Purpose**:
- Isolate parallel workstreams
- Enable safe concurrent execution
- Facilitate branch-based workflows

**Implementation**: `core/state/worktree.py`

**Related Terms**: [Bundle](#bundle), [Archive](#archive)

---

## Index by Category

### Core Engine (12 terms)
- [Adapter](#adapter)
- [Bundle](#bundle)
- [Circuit Breaker](#circuit-breaker)
- [DAG (Directed Acyclic Graph)](#dag-directed-acyclic-graph)
- [Dependency Resolution](#dependency-resolution)
- [Event Bus](#event-bus)
- [Executor](#executor)
- [Feedback Loop](#feedback-loop)
- [Integration Worker](#integration-worker)
- [Merge Strategy](#merge-strategy)
- [Orchestrator](#orchestrator)
- [Recovery Strategy](#recovery-strategy)
- [Retry Logic](#retry-logic)
- [Scheduler](#scheduler)
- [Step](#step)
- [Test Gates](#test-gates)
- [Timeout Handling](#timeout-handling)
- [Tool Profile](#tool-profile)
- [Worker](#worker)
- [Worker Health](#worker-health)
- [Worker Lifecycle](#worker-lifecycle)
- [Worker Pool](#worker-pool)
- [Workstream](#workstream)

### Error Detection (10 terms)
- [Detection Rule](#detection-rule)
- [Error Context](#error-context)
- [Error Engine](#error-engine)
- [Error Escalation](#error-escalation)
- [Error Plugin](#error-plugin)
- [Error State Machine](#error-state-machine)
- [File Hash Cache](#file-hash-cache)
- [Fix Strategy](#fix-strategy)
- [Incremental Detection](#incremental-detection)
- [Plugin Manifest](#plugin-manifest)

### Patch Management (8 terms)
- [Patch](#patch)
- [Patch Artifact](#patch-artifact)
- [Patch-First Workflow](#patch-first-workflow)
- [Patch Ledger](#patch-ledger)
- [Patch Policy](#patch-policy)
- [Patch Validator](#patch-validator)

### Specifications (8 terms)
- [Change Proposal](#change-proposal)
- [OpenSpec](#openspec)
- [Schema Validation](#schema-validation)
- [Sidecar Metadata](#sidecar-metadata)
- [Spec Bridge](#spec-bridge)
- [Spec Guard](#spec-guard)
- [Spec Patcher](#spec-patcher)
- [Spec Resolver](#spec-resolver)
- [Specification Index](#specification-index)
- [URI Resolution](#uri-resolution)

### State Management (8 terms)
- [Archive](#archive)
- [Checkpoint](#checkpoint)
- [CRUD Operations](#crud-operations)
- [Bundle Loading](#bundle-loading)
- [Event Sourcing](#event-sourcing)
- [Pipeline Database](#pipeline-database)
- [State Transition](#state-transition)
- [Worktree Management](#worktree-management)

### Integrations (9 terms)
- [AIM (AI Environment Manager)](#aim-ai-environment-manager)
- [AIM Bridge](#aim-bridge)
- [CCPM (Critical Chain Project Management)](#ccpm-critical-chain-project-management)
- [Compensation Action (Saga)](#compensation-action-saga)
- [Human Review](#human-review)
- [Profile Matching](#profile-matching)
- [Rollback Strategy](#rollback-strategy)
- [Saga Pattern](#saga-pattern)
- [Test Adapter](#test-adapter)
- [Tool Registry](#tool-registry)

### Framework (2 terms)
### Framework (4 terms)
- [Pattern Automation Hooks](#pattern-automation-hooks)
- [UET Compatibility Shim](#uet-compatibility-shim)
- [UET (Universal Execution Templates)](#uet-universal-execution-templates)
- [ULID](#ulid-universally-unique-lexicographically-sortable-identifier)

---

## Quick Reference Commands

```bash
# Search for a term in this glossary
grep -i "search term" GLOSSARY.md

# Find implementation locations
cat docs/IMPLEMENTATION_LOCATIONS.md | grep -i "term"

# Validate workstreams
python scripts/validate_workstreams.py

# Generate specification index
python scripts/generate_spec_index.py

# Run error detection
python scripts/run_error_engine.py

# Check AIM tool status
python -m aim status
```

---

## See Also

- **[IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md)** - Exact code locations for each term
- **[DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** - Complete documentation catalog
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture overview
- **[UET_INTEGRATION_PLAN_ANALYSIS.md](UET_INTEGRATION_PLAN_ANALYSIS.md)** - UET integration roadmap
- **[UET_INTEGRATION_GUIDE.md](UET_INTEGRATION_GUIDE.md)** - Two-system architecture guide
- **[CLAUDE.md](CLAUDE.md)** - Agent instructions and repository guidelines

---

**Last Updated**: 2025-11-27
**Maintained By**: Architecture Team
**Glossary Version**: 1.0.0
