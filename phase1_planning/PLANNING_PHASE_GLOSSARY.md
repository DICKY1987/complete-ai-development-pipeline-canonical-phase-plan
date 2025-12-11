# Planning Phase Glossary – AI Development Pipeline

**Last Updated**: 2025-12-10
**Purpose**: Comprehensive glossary of planning phase terminology extracted from Turn Archive conversations
**Audience**: Developers, AI agents, and documentation readers
**Source**: `C:\Users\richg\ALL_AI\PROCESS_FOR_ALL\PLANNING_Turn_1_Archive.md` through `PLANNING_Turn_6_Archive.md`

---

## Planning Phase Terms

### Acceptance Hint / Definition of Done
**Category**: Planning
**Definition**: A minimal success description included in CCIS to inform downstream planning and ensure objective verification of completed work.

**Context**: Part of CCIS minimum required fields that guides task completion validation.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [Task Plan](#task-plan-tp)

---

### Blocking Change
**Category**: Planning
**Definition**: A change flagged in CCIS that must occur before the system continues with further execution phases.

**Context**: Appears in CCIS schema as a boolean guiding scheduling decisions. Used to prioritize critical work.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [Task Queue](#task-queue)

---

### CCIS (Canonical Change Intent Specification)
**Category**: Planning – Core Boundary Object
**Definition**: The formal, validated schema that wraps a UCI and marks the transition from flexible, creative input into the strictly deterministic planning system. This is the standardized input that enters all deterministic planning stages.

**Minimum Required Fields**:
1. **Identity & routing**: `ccis_id`, `project_id`, `version`
2. **Origin**: `source` (user/looping_prompt), `created_at`
3. **Summary**: `title`, `description`, `change_kind[]`, `severity`, `blocking`
4. **Scope**: At least one of `modules[]`, `paths[]`, `patterns_impacted[]`
5. **Intent**: `problem_statement`, `desired_outcome`, `rationale`
6. **Acceptance**: `definition_of_done[]` (at least one item)

**Purpose**: Acts as the gateway between non-deterministic creative input and deterministic structured planning.

**Schema Fields**:
```yaml
ccis:
  ccis_id: "CCIS-2025-0001"
  project_id: "PROJ-CANONICAL-001"
  type: "UCI"
  version: 1
  origin:
    source: "user" | "looping_prompt"
    created_at: "2025-12-10T03:21:00Z"
  summary:
    title: "..."
    description: "..."
    change_kind: ["new_feature", "automation_gap", etc.]
    blocking: true|false
    severity: "low|medium|high|critical"
  scope:
    modules: []
    paths: []
    patterns_impacted: []
  intent:
    problem_statement: "..."
    desired_outcome: "..."
    rationale: "..."
  acceptance:
    definition_of_done: []
  project_overrides: {}
  ai_guidance: {}
  validation:
    schema_valid: true
    ready_for_planning: true
```

**Context**: Introduced in Turn 4 when defining the need for a standardized placeholder structure for pipeline entry.

**Related Terms**: [UCI](#uci-unified-change-intent), [UCP](#ucp-unified-change-pipeline), [CTRS](#ctrs-canonical-technical-requirements-specification), [Creative Input Zone](#creative-input-zone), [Deterministic Planning Phase](#deterministic-planning-phase)

---

### Change Intent
**Category**: Planning
**Definition**: A generic description of a desired modification before being normalized into CCIS; may originate from users or the LCP.

**Context**: The raw, unstructured description of what needs to change before it's formalized into CCIS.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [UCI](#uci-unified-change-intent)

---

### Change Kind
**Category**: Planning
**Definition**: A classification tag applied to CCIS describing the nature of the change.

**Valid Values**:
- `new_feature` - Adding new functionality
- `modify_existing` - Changing existing code
- `bug_fix` - Fixing defects
- `refactor` - Code restructuring
- `pattern_update` - Updating execution patterns
- `automation_gap` - Addressing missing automation

**Context**: Defined in CCIS placeholder schema to categorize work types.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification)

---

### Creative Input Zone
**Category**: Planning – Phase Boundary
**Definition**: The pre-CCIS stage where user + AI conversation or LCP analysis may be exploratory and non-deterministic.

**Characteristics**:
- Highly exploratory
- AI-assisted brainstorming
- Natural language requirements
- Flexible iteration
- No strict schema enforcement

**Context**: Defined when contrasting with deterministic planning. Everything before CCIS creation happens in this zone.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [Deterministic Planning Phase](#deterministic-planning-phase)

---

### CTRS (Canonical Technical Requirements Specification)
**Category**: Planning
**Definition**: The first machine-readable artifact produced by Open Spec that turns user's broad description into a structured technical specification. The single source of truth for what the application must satisfy.

**Produces**:
- Feature list
- Functional & non-functional requirements
- Interface boundaries
- Resources needed
- Acceptance criteria for each feature
- Constraints and validation rules

**Context**: Introduced in Turn 1 as the official name for the stage where Open Spec refines user requirements.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [Technical Requirements](#technical-requirements-tr), [Phase Plan](#phase-plan)

---

### Deterministic Planning Phase
**Category**: Planning – Phase Boundary
**Definition**: All steps following the creation of CCIS, during which the system performs structured, rule-bound transformations with no free-form reasoning.

**Characteristics**:
- Strict schema enforcement
- Rule-based transformations
- No hallucination space
- Predictable outputs
- Machine-executable steps

**Pipeline Steps** (all deterministic):
1. Requirements Normalization
2. Pattern Classification
3. Task Plan Generation
4. Workstream Integration
5. Phase Plan Insertion
6. Master JSON Fitting
7. PSJP Generation

**Context**: Highlighted when describing the strict boundary between creative input and deterministic planning.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [UCP](#ucp-unified-change-pipeline), [Creative Input Zone](#creative-input-zone)

---

### Execution Boundary
**Category**: Planning – Phase Boundary
**Definition**: The precise stage where planning ends (PSJP) and execution begins (task fulfillment via AI tools).

**Characteristics**:
- PSJP is the only artifact that crosses this boundary
- No freeform instructions allowed
- No raw prompts
- All changes must satisfy acceptance criteria in PSJP
- Produces deterministic execution

**Context**: Clarified when emphasizing PSJP as the formal handoff between planning and execution.

**Related Terms**: [PSJP](#psjp-project-specific-json-package), [Deterministic Planning Phase](#deterministic-planning-phase)

---

### LCP (Looping Chain Prompt)
**Category**: Planning – Autonomous Analysis
**Definition**: A multi-stage, rotating prompt system that repeatedly analyzes the repository from different perspectives, identifying issues or opportunities, and generating new change intents. The center of autonomous development automation.

**Purpose**:
- Detect issues
- Detect missing wiring
- Detect improvement opportunities
- Detect mismatches between spec and implementation
- Detect automatable work
- Detect gaps in patterns
- Detect structural drifts

**Architecture**: Plug-in based with configurable sub-cycles

**Sub-cycle Examples**:
- Automation gap check
- Pattern drift detection
- File-structure validation
- Execution-pattern completeness check
- Merge safety analysis
- Dependency graph review
- Spec–code mismatch detection
- Import correctness pass
- Missing state/wiring check
- Dead code detection
- Doc-ID or metadata validation

**Output**: Generates UCIs that feed into the same planning pipeline as user requirements.

**Configuration**:
- User determines number of cycles
- Each cycle contains multiple sub-cycles
- Prompts can change per cycle
- Can target different code areas (whole repo, specific folders, etc.)
- Can use different perspectives and angles

**Context**: Discussed extensively in Turn 1 as an autonomous mechanism for detecting issues and feeding them into planning.

**Related Terms**: [UCI](#uci-unified-change-intent), [CCIS](#ccis-canonical-change-intent-specification), [Automation Gap](#automation-gap), [Pattern Drift](#pattern-drift)

---

### Automation Gap
**Category**: Planning
**Definition**: A missing automation or incomplete automation step detected by the LCP, requiring formulation into a CCIS.

**Context**: Discussed as one class of LCP-detected issue that enters the planning pipeline.

**Related Terms**: [LCP](#lcp-looping-chain-prompt), [CCIS](#ccis-canonical-change-intent-specification)

---

### Master JSON Template
**Category**: Planning
**Definition**: The canonical schema used to standardize the representation of planning artifacts before they are assembled into the PSJP. A universal schema with standard field names, workstream patterns, and execution-rule sections.

**Purpose**:
- Eliminate ambiguity
- Eliminate hallucination space
- Ensure every execution cycle uses the same predictable structure

**Context**: Discussed when defining how PSJP fragments are fitted into a uniform structure.

**Related Terms**: [PSJP](#psjp-project-specific-json-package), [PSJP Fragment](#psjp-fragment-pjf)

---

### Merge Queue
**Category**: Execution
**Definition**: A controlled integration step for executing outputs (e.g., branches or worktrees) back into the mainline safely and deterministically.

**Purpose**:
- Safely merge completed workstreams
- Maintain code integrity
- Prevent conflicts

**Context**: Introduced when contextualizing execution flow and safe merging.

**Related Terms**: [Task Queue](#task-queue), [Workstream](#workstream-ws)

---

### PA (Pattern Assignment)
**Category**: Planning – UCP Stage 2
**Definition**: The classification output that determines which execution patterns apply, what tools to use, and how the work should be structured based on the TR.

**Output Structure**:
```yaml
pattern_assignment:
  id: PA-xxxx
  derived_from: TR-xxxx
  matched_patterns:
    - PAT-xxx
    - PAT-yyy
  workstream_type:
    - "creation"
    - "modification"
    - "migration"
    - "validation"
    - "refactor"
  required_tools:
    - "claude_code"
    - "copilot"
    - "python_executor"
  estimated_complexity: 1–5
  suggested_parallelization_group: "<worktree-group-id>"
```

**Purpose**:
- Which template to use
- Which agent(s) to invoke
- How hard the change is
- Which folder boundaries it touches
- Whether it can execute in parallel

**Context**: Part of the UCP stages following requirements normalization.

**Related Terms**: [UCP](#ucp-unified-change-pipeline), [TR](#tr-technical-requirements), [TP](#tp-task-plan)

---

### Pattern Drift
**Category**: Planning
**Definition**: A condition in which existing code diverges from expected execution patterns, requiring correction.

**Context**: Referenced within LCP analysis responsibilities as a type of issue to detect.

**Related Terms**: [LCP](#lcp-looping-chain-prompt), [CCIS](#ccis-canonical-change-intent-specification)

---

### Phase Category
**Category**: Planning
**Definition**: A planning attribute that determines which major phase (e.g., PH-03, PH-04) a workstream belongs to.

**Context**: Appears in workstream and phase plan discussions for organizing work.

**Related Terms**: [Phase Plan](#phase-plan), [Workstream](#workstream-ws)

---

### Phase Plan
**Category**: Planning
**Definition**: The dependency-ordered arrangement of workstreams into project phases, used to manage execution sequencing and project flow. Created from the CTRS using pre-existing execution patterns and independent workstreams.

**Structure**:
```yaml
phase_plan:
  phases:
    - phase_id: "PH-04"
      workstreams:
        - WS-xxxx
      depends_on:
        - "PH-03"
      status: "pending"
      acceptance: [...]
```

**Characteristics**:
- Divided into Phases (e.g., Phase 0: Bootstrap, Phase 1: Foundations, Phase 2: Core logic)
- Composed of Execution Patterns
- Split into Independent Workstreams
- Assigned GitHub Project metadata (Epic → Task → Subtask)
- Mapped dependencies (DAG graph)
- Assigned resource boundaries (pattern inputs, outputs, prerequisites)

**Context**: Mentioned when describing integration of workstreams into phases.

**Related Terms**: [CTRS](#ctrs-canonical-technical-requirements-specification), [Workstream](#workstream-ws), [PSJP](#psjp-project-specific-json-package)

---

### Planning Engine
**Category**: Planning
**Definition**: The structured processor that transforms CCISs into PSJP artifacts using deterministic steps and schemas.

**Context**: Mentioned conceptually as the system between CCIS and PSJP.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [PSJP](#psjp-project-specific-json-package), [UCP](#ucp-unified-change-pipeline)

---

### PSJP (Project-Specific JSON Package)
**Category**: Planning – Final Output
**Definition**: The authoritative, fully structured planning output that aggregates all phases, tasks, workstreams, and patterns. The final output of the Planning Phase and the ONLY allowed input to the Execution Engine.

**Structure**:
```yaml
project_specific_json_package:
  doc_id: PSJP-xxxx
  version: <incremented>
  phases: [...]
  workstreams: [...]
  tasks: [...]
  patterns: [...]
  registry: [...]
  validation:
    schema_passed: true
    reference_integrity: true
    no_cycles_in_dag: true
```

**Purpose**:
- Single source of truth for execution
- Eliminates ambiguity
- Provides deterministic execution context
- Contains all task instructions, context, and acceptance rules

**Key Invariant**: The PSJP is always regenerated before execution begins, even if tasks accumulate.

**Context**: Defined repeatedly throughout planning-flow discussion as the final output of planning and input to execution.

**Related Terms**: [Master JSON Template](#master-json-template), [PSJP Fragment](#psjp-fragment-pjf), [Execution Boundary](#execution-boundary), [Phase Plan](#phase-plan)

---

### PSJP Fragment (PJF)
**Category**: Planning
**Definition**: A partial JSON structure representing a piece of the project plan prior to merging into the full PSJP.

**Output Structure**:
```yaml
project_specific_json_fragment:
  id: PJF-xxxx
  phases: [...]
  workstreams: [...]
  tasks: [...]
  patterns_in_use: [...]
  metadata: {...}
```

**Context**: Introduced in UCP as the output of Master JSON Fitting stage.

**Related Terms**: [PSJP](#psjp-project-specific-json-package), [Master JSON Template](#master-json-template)

---

### Task Queue
**Category**: Planning
**Definition**: A structure (FIFO or priority-based) that retains tasks awaiting execution when the executor cannot keep up with new tasks generated from planning or the LCP.

**Behavior**:
- Tasks wait until previous dependencies complete
- Executor consumes tasks at its own pace
- Merge Queue integrates results safely

**Purpose**:
- Handle overflow when LCP generates tasks faster than execution
- Prioritize work
- Manage backlog

**Context**: Mentioned during discussion of pipeline dynamics and backlog management.

**Related Terms**: [LCP](#lcp-looping-chain-prompt), [PSJP](#psjp-project-specific-json-package), [Merge Queue](#merge-queue)

---

### TP (Task Plan)
**Category**: Planning – UCP Stage 3
**Definition**: A list of actionable, dependent tasks derived from pattern assignments, each with tool instructions and acceptance conditions. The smallest unit the execution engine works with.

**Output Structure**:
```yaml
task_plan:
  id: TP-xxxx
  derived_from: PA-xxxx
  tasks:
    - task_id: T-001
      description: "Edit file X to add Y"
      pattern: PAT-xxx
      inputs: {}
      outputs: {}
      tool: "claude_code"
      acceptance:
        - "no compile errors"
        - "pattern_validator passes"
    - task_id: T-002
      ...
  dependencies:
    - T-001 must finish before T-002
  estimated_runtime: "5 minutes"
  blocking: true|false
```

**Purpose**: Decomposes UCI into real executable steps.

**Context**: Appears in the UCP as the step that decomposes pattern assignments.

**Related Terms**: [UCP](#ucp-unified-change-pipeline), [PA](#pa-pattern-assignment), [Workstream](#workstream-ws)

---

### TR (Technical Requirements)
**Category**: Planning – UCP Stage 1
**Definition**: A structured, machine-readable articulation of the problem, constraints, and acceptance criteria derived from a CCIS.

**Output Structure**:
```yaml
technical_requirements:
  id: TR-xxxx
  derived_from: UCI-xxxx
  problem_statement: "<cleaned, clarified version>"
  functional_requirements: []
  nonfunctional_requirements: []
  constraints: []
  domain_context: {}
  acceptance_criteria: []
```

**Answers**:
- What EXACTLY must change?
- What constraints govern the change?
- What must be true for this change to be "done"?

**Context**: Introduced as Step 1 after CCIS in the deterministic planning process.

**Related Terms**: [UCP](#ucp-unified-change-pipeline), [CCIS](#ccis-canonical-change-intent-specification), [PA](#pa-pattern-assignment)

---

### UCI (Unified Change Intent)
**Category**: Planning – Input Stream Convergence
**Definition**: A structured representation of a proposed modification—originating either from user requirements or from the Looping Chain Prompt—that acts as the standardized input to the deterministic planning phase. The common format that both input streams converge into.

**Structure**:
```yaml
change_intent:
  id: UCI-xxxx
  source: "user" | "looping_prompt"
  description: "<natural language description of needed change>"
  change_type:
    - "new_feature"
    - "modify_existing"
    - "bug_fix"
    - "refactor"
    - "pattern_update"
  affected_scope:
    files: []
    modules: []
    patterns: []
  severity: low|medium|high|critical
  blocking: true|false
  rationale: "<why this change is needed>"
  acceptance_hint: "<what success looks like>"
  metadata: {}
```

**Two Input Streams**:
1. **User-driven requirements**: New feature, new app, "Please add X", "Please change Y"
2. **Looping Chain Prompt (LCP) discoveries**: Automation gaps, broken wiring, refactors, spec drift, missing tests

**Key Insight**: Whether it's a new file or editing an existing file is irrelevant—it's just a different shape of modification. All work is "a set of modifications that must be made to the repo."

**Context**: Introduced when describing the convergence of user and LCP inputs into a single planning pipeline.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [LCP](#lcp-looping-chain-prompt), [UCP](#ucp-unified-change-pipeline)

---

### UCP (Unified Change Pipeline)
**Category**: Planning – Core Process
**Definition**: The deterministic transformation pipeline that processes CCIS → Technical Requirements → Pattern Assignment → Task Plan → Workstream → Phase Plan → PSJP. The single, deterministic funnel for all change intents entering the system.

**Complete Flow**:
```
CCIS
  ↓
Requirements Normalization → TR
  ↓
Pattern Classification → PA
  ↓
Task Plan Generation → TP
  ↓
Workstream Integration → WS
  ↓
Phase Plan Insertion → Updated Phase Plan
  ↓
Master JSON Fitting → PJF
  ↓
PSJP Generation → PSJP
  ↓
Execution Engine
```

**Key Convergence Point**: Once a change intent is converted into Technical Requirements (TR), the rest of the pipeline is always identical—regardless of origin (user or LCP).

**Characteristics**:
- Modular
- Pattern-driven
- Execution-engine-ready
- Deterministic
- Auditable
- Extensible
- Safe

**Context**: Named and formalized in Turn 3 when describing the unified deterministic process after input convergence.

**Related Terms**: [CCIS](#ccis-canonical-change-intent-specification), [UCI](#uci-unified-change-intent), [PSJP](#psjp-project-specific-json-package), [TR](#tr-technical-requirements), [PA](#pa-pattern-assignment), [TP](#tp-task-plan), [Workstream](#workstream-ws)

---

### Worktree Group / Parallelization Group
**Category**: Planning
**Definition**: A classification used to assign related workstreams to Git worktrees to support parallel execution without conflict.

**Context**: Introduced when discussing planning metadata and execution routing.

**Related Terms**: [Workstream](#workstream-ws), [PA](#pa-pattern-assignment)

---

### WS (Workstream)
**Category**: Planning – UCP Stage 4
**Definition**: A coherent group of tasks assigned to a phase and branch/worktree boundary, representing a unit of execution in the planning system.

**Output Structure**:
```yaml
workstream:
  id: WS-xxxx
  derived_from: TP-xxxx
  phase_category: "PH-x"
  tasks: [list of task_ids]
  parallelizable: true|false
  git_boundary:
    branch: "feature/..."
    worktree: ".worktrees/wt-..."
  success_criteria:
    - "all tasks succeed"
    - "branch passes safe-merge check"
```

**Purpose**: Groups tasks into construction-ready execution units.

**Context**: Defined as the grouping stage after task planning.

**Related Terms**: [UCP](#ucp-unified-change-pipeline), [TP](#tp-task-plan), [Phase Plan](#phase-plan)

---

## Data Flow Summary

The complete planning phase follows this data flow:

```
┌─────────────────────────────────────────┐
│  User Input or LCP Finding              │
│  (Creative Input Zone)                  │
└──────────────────┬──────────────────────┘
                   ↓
         ┌─────────────────────┐
         │  UCI (Convergence)  │
         └─────────┬───────────┘
                   ↓
         ┌─────────────────────┐
         │  CCIS (Validation)  │ ← Deterministic Boundary
         └─────────┬───────────┘
                   ↓
    ╔══════════════════════════════╗
    ║  UNIFIED CHANGE PIPELINE     ║
    ╠══════════════════════════════╣
    ║  1. TR (Requirements)        ║
    ║  2. PA (Pattern Assignment)  ║
    ║  3. TP (Task Plan)           ║
    ║  4. WS (Workstream)          ║
    ║  5. Phase Plan Integration   ║
    ║  6. Master JSON Fitting      ║
    ║  7. PSJP Generation          ║
    ╚══════════════╤═══════════════╝
                   ↓
         ┌─────────────────────┐
         │  PSJP (Final Output)│
         └─────────┬───────────┘
                   ↓
         ┌─────────────────────┐
         │  Execution Engine   │ ← Execution Boundary
         └─────────────────────┘
```

---

## Event Flows

### New Project Flow
```
User Requirements → CTRS → Phase Plan → Fit to Master JSON →
→ PSJP → Executor → Completed Code
```

### Looping Prompt Flow (Ongoing)
```
LCP Cycle → Issue Detected → Convert to Requirement →
→ Convert to Task → Fit to Master JSON →
→ Regenerate PSJP → Execution Queue → Executor → Merge
```

### User Feature Request Flow
```
User Feature → Requirement → CTRS Update → Phase Plan Update →
→ PSJP Update → Execution → Merge
```

**Key Invariant**: In all cases, PSJP is the single output of planning AND the single input to execution.

---

## Critical Boundaries

### 1. Creative → Deterministic Boundary
**Location**: CCIS creation
**Before**: Exploratory, conversational, flexible AI interaction
**After**: Strict schema validation, rule-based transformations

### 2. Planning → Execution Boundary
**Location**: PSJP handoff
**Before**: Plan generation, task structuring, dependency resolution
**After**: Code execution, testing, merging

---

## Quick Reference

### Planning Phase Stages (in order)
1. **Creative Input** (User + AI or LCP)
2. **UCI Formation** (Convergence)
3. **CCIS Validation** (Gateway to determinism)
4. **TR Normalization** (Requirements)
5. **PA Classification** (Patterns)
6. **TP Generation** (Tasks)
7. **WS Integration** (Workstreams)
8. **Phase Plan Update** (Scheduling)
9. **Master JSON Fitting** (Standardization)
10. **PSJP Generation** (Final output)

### Two Input Streams
1. **User Requirements Stream**: Features, bugs, architectural changes
2. **LCP Stream**: Automated issue detection and improvements

### Three Key Artifacts
1. **CCIS**: Gateway input (validated, standardized)
2. **UCP**: Processing pipeline (deterministic, modular)
3. **PSJP**: Final output (executable, complete)

---

## See Also

**Related Documentation**:
- **PLANNING_Turn_1_Archive.md** - Initial planning stage architecture
- **PLANNING_Turn_2_Archive.md** - Input stream convergence
- **PLANNING_Turn_3_Archive.md** - UCP formalization
- **PLANNING_Turn_4_Archive.md** - CCIS boundary definition
- **PLANNING_Turn_5_Archive.md** - First glossary extraction
- **PLANNING_Turn_6_Archive.md** - Glossary refinement

**Source Location**: `C:\Users\richg\ALL_AI\PROCESS_FOR_ALL\`

**Related Planning Documents** (to be created):
- **CCIS_SCHEMA.json** - Formal JSON Schema for CCIS
- **UCP_PROCESS_SPECIFICATION.md** - Detailed UCP stages
- **MASTER_JSON_TEMPLATE.json** - Standard PSJP structure
- **LCP_DESIGN.md** - Looping Chain Prompt architecture

---

**Last Updated**: 2025-12-10
**Maintained By**: Planning Phase Team
**Glossary Version**: 1.0.0
**Source Conversations**: Turns 1-6
