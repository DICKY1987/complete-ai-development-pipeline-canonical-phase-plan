---
doc_id: DOC-GUIDE-SYSTEM-VISUAL-DIAGRAMS-180
---

# System Visual Understanding Diagrams

## 1. Data Flow & State Transitions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                                │
└─────────────────────────────────────────────────────────────────────────┘

                    INPUT SOURCES
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   [Workstream]      [PM Epic]      [Manual Spec]
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ schema/     │ ◄──── Validates format
                  │ validation  │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ core/       │
                  │ planner     │ ◄──── config/ (rules)
                  └──────┬──────┘       templates/ (patterns)
                         │
                         ▼
                  ┌─────────────┐
                  │Decomposition│
                  │  into tasks │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ core/       │
                  │ scheduler   │ ◄──── Dependency resolution
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ engine/     │
                  │ queue       │ ◄──── Priority ordering
                  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   [Task A]         [Task B]         [Task C]
        │                │                │
        ▼                ▼                ▼
  ┌─────────────────────────────────────────┐
  │      engine/adapters/                   │
  │  ┌────────┐  ┌────────┐  ┌────────┐   │
  │  │ aider  │  │ claude │  │ copilot│   │ ◄── aim/ (tool registry)
  │  └────────┘  └────────┘  └────────┘   │
  └────────────────┬────────────────────────┘
                   │
                   ▼
            ┌─────────────┐
            │ EXECUTION   │
            │   PHASE     │
            └──────┬──────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
  [SUCCESS]    [PARTIAL]    [FAILED]
      │            │            │
      │            ▼            │
      │      ┌─────────────┐   │
      │      │ error/      │   │
      │      │ detection   │   │
      │      └──────┬──────┘   │
      │             │           │
      │             ▼           │
      │      ┌─────────────┐   │
      │      │ error/      │   │
      │      │ engine      │   │
      │      │ (auto-fix)  │   │
      │      └──────┬──────┘   │
      │             │           │
      └─────────────┼───────────┘
                    │
                    ▼
             ┌─────────────┐
             │   OUTPUT    │
             │  RECORDING  │
             └──────┬──────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
  [state/]      [logs/]      [modules/]
  runtime       events       artifacts
      │             │             │
      └─────────────┼─────────────┘
                    │
                    ▼
             ┌─────────────┐
             │ gui/        │ ◄──── Visualize
             │ dashboard   │
             └─────────────┘
```

---

## 2. Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE DEPENDENCY HIERARCHY                           │
│                    (Arrows show "depends on")                            │
└─────────────────────────────────────────────────────────────────────────┘

LAYER 0: FOUNDATION (No dependencies)
═══════════════════════════════════
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ schema/  │   │ config/  │   │templates/│
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
LAYER 1: INFRASTRUCTURE
═══════════════════════
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ infra/   │   │ state/   │   │  logs/   │
    │  (CI)    │   │(runtime) │   │(tracking)│
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
LAYER 2: DOMAIN CORE
════════════════════
         ┌──────────────────────┐
         │      core/           │
         │  ┌────────────────┐  │
         │  │ orchestrator   │  │
         │  │ planner        │  │
         │  │ scheduler      │  │
         │  │ executor       │  │
         │  └────────────────┘  │
         └──────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────────┐
   │ error/ │  │  aim/  │  │specifications/│
   │plugins │  │ bridge │  │   tools    │
   │engine  │  │services│  │            │
   └────┬───┘  └───┬────┘  └─────┬──────┘
        │          │             │
        └──────────┼─────────────┘
                   │
                   ▼
LAYER 3: EXECUTION
══════════════════
         ┌──────────────────────┐
         │     engine/          │
         │  ┌────────────────┐  │
         │  │ orchestrator   │  │
         │  │ queue          │  │
         │  │ adapters       │  │
         │  │ state_store    │  │
         │  └────────────────┘  │
         └──────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │  pm/   │  │scripts/│  │workstreams/│
   │(ccpm)  │  │(tools) │  │  (specs)│
   └────────┘  └────────┘  └────────┘
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
LAYER 4: INTERFACE
══════════════════
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   gui/   │   │ modules/ │   │ archive/ │
    │(display) │   │ (output) │   │  (done)  │
    └──────────┘   └──────────┘   └──────────┘

SUPPORTING (Cross-layer)
════════════════════════
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  docs/   │   │registry/ │   │  tools/  │
    │ (guides) │   │(lookups) │   │(utilities)│
    └──────────┘   └──────────┘   └──────────┘
```

---

## 3. Task Lifecycle State Machine

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     TASK STATE MACHINE                                   │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │  START   │
                    └────┬─────┘
                         │
                         ▼
                   ┌───────────┐
                   │ SUBMITTED │ ◄──── workstreams/ws-XX.json
                   └─────┬─────┘       (input)
                         │
                         ▼
                   ┌───────────┐
                   │ VALIDATED │ ◄──── schema/ check
                   └─────┬─────┘
                         │
                         ▼
                   ┌───────────┐
                   │  PLANNED  │ ◄──── core/planner
                   └─────┬─────┘       (decompose)
                         │
                         ▼
                   ┌───────────┐
                   │ SCHEDULED │ ◄──── core/scheduler
                   └─────┬─────┘       (order by deps)
                         │
                         ▼
                   ┌───────────┐
                   │  QUEUED   │ ◄──── engine/queue
                   └─────┬─────┘
                         │
                         ▼
                   ┌───────────┐
                   │  RUNNING  │ ◄──── engine/orchestrator
                   └─────┬─────┘       + adapters
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐     ┌──────────┐    ┌──────────┐
   │SUCCEEDED│     │ PARTIAL  │    │  FAILED  │
   └────┬────┘     └─────┬────┘    └─────┬────┘
        │                │               │
        │                ▼               │
        │          ┌──────────┐          │
        │          │ ERROR    │          │
        │          │ DETECTED │ ◄────────┘
        │          └─────┬────┘
        │                │
        │                ▼
        │          ┌──────────┐
        │          │AUTO-FIX  │ ◄──── error/engine
        │          │ ATTEMPT  │
        │          └─────┬────┘
        │                │
        │    ┌───────────┼───────────┐
        │    │           │           │
        │    ▼           ▼           ▼
        │  [FIXED]   [PARTIAL]   [FAILED]
        │    │           │           │
        │    └───────────┼───────────┘
        │                │
        └────────────────┼────────────────┐
                         │                │
                         ▼                ▼
                   ┌───────────┐    ┌──────────┐
                   │ COMPLETED │    │ ABANDONED│
                   └─────┬─────┘    └─────┬────┘
                         │                │
                         ▼                ▼
                   ┌───────────┐    ┌──────────┐
                   │ RECORDED  │    │ LOGGED   │
                   └─────┬─────┘    └─────┬────┘
                         │                │
                         └────────┬───────┘
                                  │
                                  ▼
                            ┌──────────┐
                            │ ARCHIVED │
                            └──────────┘

STATE STORAGE:
  • SUBMITTED → RUNNING: state/ (runtime)
  • All transitions: logs/ (audit trail)
  • COMPLETED: modules/ (artifacts)
  • ARCHIVED: archive/ (historical)
```

---

## 4. Error Detection & Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  ERROR DETECTION & RECOVERY PIPELINE                     │
└─────────────────────────────────────────────────────────────────────────┘

EXECUTION                  DETECTION                  RECOVERY
═════════                  ═════════                  ════════

┌──────────┐
│ Task     │
│ Executes │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Output   │
│Generated │
└────┬─────┘
     │
     │           ┌─────────────────────────────────────┐
     └──────────►│   error/plugins/                    │
                 │                                      │
                 │  ┌──────────┐  ┌──────────┐        │
                 │  │ python_  │  │  mypy    │        │
                 │  │  ruff    │  │          │        │
                 │  └────┬─────┘  └────┬─────┘        │
                 │       │             │               │
                 │  ┌────┴─────┐  ┌────┴─────┐        │
                 │  │ eslint   │  │  pytest  │        │
                 │  └────┬─────┘  └────┬─────┘        │
                 │       │             │               │
                 │       └──────┬──────┘               │
                 │              │                      │
                 └──────────────┼──────────────────────┘
                                │
                                ▼
                      ┌──────────────────┐
                      │ error/engine/    │
                      │ aggregator       │
                      └─────────┬────────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
                   ▼            ▼            ▼
              [SYNTAX]      [TYPE]      [RUNTIME]
              [ERRORS]      [ERRORS]    [ERRORS]
                   │            │            │
                   └────────────┼────────────┘
                                │
                                ▼
                      ┌──────────────────┐
                      │ error/engine/    │
                      │ classifier       │
                      └─────────┬────────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
                   ▼            ▼            ▼
              [AUTO-      [SUGGEST-     [MANUAL]
               FIXABLE]    FIXABLE]
                   │            │            │
                   │            │            │
                   ▼            ▼            │
         ┌──────────────────────────┐       │
         │ error/plugins/*/fix()    │       │
         │                          │       │
         │ • Apply patch            │       │
         │ • Reformat code          │       │
         │ • Update imports         │       │
         └────────┬─────────────────┘       │
                  │                         │
                  ▼                         │
         ┌──────────────┐                  │
         │ Re-validate  │                  │
         └────┬─────────┘                  │
              │                            │
     ┌────────┼────────┐                   │
     │        │        │                   │
     ▼        ▼        ▼                   │
  [FIXED] [PARTIAL] [FAILED]               │
     │        │        │                   │
     │        └────────┼───────────────────┘
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────────┐
│ logs/    │    │ error/       │
│ success  │    │ reports/     │
└──────────┘    └──────────────┘
     │                 │
     └────────┬────────┘
              │
              ▼
       ┌─────────────┐
       │ Update Task │
       │   State     │
       └─────────────┘
```

---

## 5. Configuration Cascade

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION CASCADE                                 │
│                  (Priority: Bottom → Top)                                │
└─────────────────────────────────────────────────────────────────────────┘

LEVEL 5: RUNTIME OVERRIDES (Highest Priority)
═══════════════════════════════════════════════
    ┌────────────────────────────────────┐
    │ Command-line args                  │
    │ --config custom.yaml               │
    │ --tool aider                       │
    └────────────────┬───────────────────┘
                     │ Overrides
                     ▼
LEVEL 4: WORKSTREAM SPECIFIC
════════════════════════════
    ┌────────────────────────────────────┐
    │ workstreams/ws-XX.json             │
    │ {                                  │
    │   "tool_config": {...},            │
    │   "error_handling": {...}          │
    │ }                                  │
    └────────────────┬───────────────────┘
                     │ Overrides
                     ▼
LEVEL 3: TOOL PROFILES
══════════════════════
    ┌────────────────────────────────────┐
    │ config/tool_profiles.json          │
    │ {                                  │
    │   "aider": {...},                  │
    │   "claude": {...}                  │
    │ }                                  │
    └────────────────┬───────────────────┘
                     │ Overrides
                     ▼
LEVEL 2: MODULE DEFAULTS
════════════════════════
    ┌────────────────────────────────────┐
    │ config/                            │
    │ ├── aim_config.yaml                │
    │ ├── circuit_breakers.yaml          │
    │ ├── router_config.json             │
    │ └── ccpm.yaml                      │
    └────────────────┬───────────────────┘
                     │ Overrides
                     ▼
LEVEL 1: SCHEMA DEFAULTS (Lowest Priority)
═══════════════════════════════════════════
    ┌────────────────────────────────────┐
    │ schema/                            │
    │ ├── workstream.schema.json         │
    │ ├── jobs/job.schema.json           │
    │ └── module.schema.json             │
    └────────────────────────────────────┘

RESOLUTION FLOW:
═══════════════
    USER REQUEST
         │
         ▼
    ┌─────────────────┐
    │ core/config_    │
    │ loader.py       │
    └────┬────────────┘
         │
         ├─► Read schema/ (base defaults)
         ├─► Merge config/* (module configs)
         ├─► Merge tool_profiles (tool settings)
         ├─► Merge workstream (task-specific)
         └─► Apply CLI args (runtime)
         │
         ▼
    ┌─────────────────┐
    │ Final Config    │
    │ Object          │
    └────┬────────────┘
         │
         ▼
    Used by core/, engine/, error/
```

---

## 6. Workstream Execution Timeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   WORKSTREAM EXECUTION TIMELINE                          │
│                    (Parallel Task Execution)                             │
└─────────────────────────────────────────────────────────────────────────┘

TIME →
═══════════════════════════════════════════════════════════════════════════

T0: SUBMISSION
   │
   │ workstreams/ws-25-patch-manager.json
   │
   ▼
   ┌─────────────────────────────────────────────────┐
   │ Phase 0: Validation                             │
   │ • Schema check                                  │
   │ • Dependency resolution                         │
   └───────────────────────┬─────────────────────────┘
                           │
T1: PLANNING               ▼
   ┌─────────────────────────────────────────────────┐
   │ Phase 1: Decomposition                          │
   │ • Task breakdown                                │
   │ • Dependency graph construction                 │
   └───────────────────────┬─────────────────────────┘
                           │
T2: SCHEDULING             ▼
   ┌─────────────────────────────────────────────────┐
   │ Phase 2: Task Ordering                          │
   │                                                 │
   │ ┌────────┐  ┌────────┐  ┌────────┐            │
   │ │ Task 1 │  │ Task 3 │  │ Task 5 │  (Layer 1) │
   │ └───┬────┘  └───┬────┘  └───┬────┘            │
   │     │           │           │                  │
   │     └───────┬───┴───────┬───┘                  │
   │             │           │                      │
   │        ┌────┴───┐  ┌────┴───┐                 │
   │        │ Task 2 │  │ Task 4 │    (Layer 2)    │
   │        └───┬────┘  └───┬────┘                 │
   │            │           │                      │
   │            └─────┬─────┘                      │
   │                  │                            │
   │             ┌────┴───┐                        │
   │             │ Task 6 │         (Layer 3)     │
   │             └────────┘                        │
   └─────────────────────────────────────────────────┘
                           │
T3: EXECUTION              ▼
   ┌─────────────────────────────────────────────────┐
   │ Parallel Execution                              │
   │                                                 │
   │ [Task 1] ████████░░ (80% done)                 │
   │ [Task 3] ██████░░░░ (60% done)                 │
   │ [Task 5] ██████████ (Complete) ✓               │
   │                                                 │
   │ [Task 2] ░░░░░░░░░░ (Waiting on Task 1)        │
   │ [Task 4] ░░░░░░░░░░ (Waiting on Task 3)        │
   │                                                 │
   │ [Task 6] ░░░░░░░░░░ (Waiting on Layer 2)       │
   └─────────────────────────────────────────────────┘
                           │
T4: MONITORING             ▼
   ┌─────────────────────────────────────────────────┐
   │ Real-time State Tracking                        │
   │                                                 │
   │ state/events/                                   │
   │ ├── task-1-started.json                        │
   │ ├── task-3-progress-60pct.json                 │
   │ └── task-5-completed.json                      │
   │                                                 │
   │ logs/                                           │
   │ ├── ws-25-execution.log                        │
   │ └── task-errors.log                            │
   └─────────────────────────────────────────────────┘
                           │
T5: ERROR HANDLING         ▼
   ┌─────────────────────────────────────────────────┐
   │ Task 3 Failed → Error Pipeline                  │
   │                                                 │
   │ error/plugins/python_ruff/                      │
   │   ├── detect() → Found 3 issues                │
   │   └── fix()    → Auto-fixed 2                  │
   │                                                 │
   │ Retry Task 3 → Success ✓                       │
   └─────────────────────────────────────────────────┘
                           │
T6: COMPLETION             ▼
   ┌─────────────────────────────────────────────────┐
   │ All Tasks Complete                              │
   │                                                 │
   │ modules/patch-manager/                          │
   │ ├── patch_scanner.py                           │
   │ ├── patch_applier.py                           │
   │ └── tests/                                     │
   │                                                 │
   │ archive/ws-25-patch-manager/                   │
   │ └── execution_report.json                      │
   └─────────────────────────────────────────────────┘

LEGEND:
  ████ = Completed work
  ░░░░ = Pending work
  ✓    = Success
  ✗    = Failed
```

---

## 7. Tool Adapter Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      TOOL ADAPTER ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │ engine/      │
                        │ orchestrator │
                        └──────┬───────┘
                               │
                               ▼
                   ┌───────────────────────┐
                   │ engine/adapters/      │
                   │ base_adapter.py       │
                   │                       │
                   │ interface:            │
                   │  • execute()          │
                   │  • validate()         │
                   │  • health_check()     │
                   └───────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
  ┌───────────────┐    ┌───────────────┐   ┌───────────────┐
  │ aider_adapter │    │claude_adapter │   │copilot_adapter│
  │               │    │               │   │               │
  │ ┌───────────┐ │    │ ┌───────────┐ │   │ ┌───────────┐ │
  │ │  prepare  │ │    │ │  prepare  │ │   │ │  prepare  │ │
  │ │   args    │ │    │ │   prompt  │ │   │ │  context  │ │
  │ └─────┬─────┘ │    │ └─────┬─────┘ │   │ └─────┬─────┘ │
  │       │       │    │       │       │   │       │       │
  │       ▼       │    │       ▼       │   │       ▼       │
  │ ┌───────────┐ │    │ ┌───────────┐ │   │ ┌───────────┐ │
  │ │  invoke   │ │    │ │  invoke   │ │   │ │  invoke   │ │
  │ │   CLI     │ │    │ │   API     │ │   │ │   API     │ │
  │ └─────┬─────┘ │    │ └─────┬─────┘ │   │ └─────┬─────┘ │
  │       │       │    │       │       │   │       │       │
  │       ▼       │    │       ▼       │   │       ▼       │
  │ ┌───────────┐ │    │ ┌───────────┐ │   │ ┌───────────┐ │
  │ │  parse    │ │    │ │  parse    │ │   │ │  parse    │ │
  │ │  output   │ │    │ │  response │ │   │ │  result   │ │
  │ └─────┬─────┘ │    │ └─────┬─────┘ │   │ └─────┬─────┘ │
  │       │       │    │       │       │   │       │       │
  └───────┼───────┘    └───────┼───────┘   └───────┼───────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                      ┌────────────────┐
                      │ Normalized     │
                      │ Response       │
                      │ {              │
                      │   status,      │
                      │   output,      │
                      │   metadata     │
                      │ }              │
                      └────────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌─────────┐    ┌─────────┐   ┌─────────┐
          │ state/  │    │ logs/   │   │ error/  │
          │ update  │    │ record  │   │ check   │
          └─────────┘    └─────────┘   └─────────┘

ADAPTER DISCOVERY (via aim/):
═════════════════════════════
    aim/.AIM_ai-tools-registry/
    ├── aider.yaml
    │   ├── capabilities: [code-edit, refactor]
    │   ├── interfaces: [cli, api]
    │   └── health_endpoint: /health
    │
    ├── claude.yaml
    │   ├── capabilities: [code-gen, analysis]
    │   ├── interfaces: [api]
    │   └── rate_limits: {...}
    │
    └── copilot.yaml
        ├── capabilities: [completion, chat]
        ├── interfaces: [api, extension]
        └── context_window: 32000

ROUTING DECISION:
════════════════
    Task: "Refactor module X"
         │
         ▼
    config/router_config.json
         │
         ├─► code-edit → aider (preferred)
         ├─► code-gen  → claude (fallback)
         └─► analysis  → copilot (tertiary)
```

---

## 8. Folder Interaction Heatmap

```
┌─────────────────────────────────────────────────────────────────────────┐
│              FOLDER INTERACTION FREQUENCY                                │
│         (Darker = More interactions per execution)                       │
└─────────────────────────────────────────────────────────────────────────┘

                     READ FREQUENCY
                     ═══════════════

    workstreams/  ▓▓▓▓▓▓▓░░░ (80%)  ← Read once per execution
         schema/  ▓▓▓▓▓▓▓▓▓▓ (100%) ← Read for every validation
         config/  ▓▓▓▓▓▓▓▓▓░ (90%)  ← Read at startup + runtime
      templates/  ▓▓▓░░░░░░░ (30%)  ← Read when generating code
          docs/   ▓░░░░░░░░░ (10%)  ← Reference only
       registry/  ▓▓▓▓▓░░░░░ (50%)  ← Lookups during planning
            aim/  ▓▓▓▓▓▓▓░░░ (70%)  ← Tool discovery per task
  specifications/ ▓▓▓▓▓▓░░░░ (60%)  ← Spec resolution

                    WRITE FREQUENCY
                    ════════════════

          state/  ▓▓▓▓▓▓▓▓▓▓ (100%) ← Every state change
           logs/  ▓▓▓▓▓▓▓▓▓▓ (100%) ← Every event
        modules/  ▓▓▓▓▓░░░░░ (50%)  ← Task output
        archive/  ▓▓░░░░░░░░ (20%)  ← End of workstream
           core/  ▓░░░░░░░░░ (10%)  ← Config updates only
         engine/  ▓░░░░░░░░░ (10%)  ← Adapter registration
          error/  ▓▓▓▓░░░░░░ (40%)  ← Error reports

               CROSS-FOLDER DEPENDENCIES
               ═══════════════════════════

    core/ ←→ engine/           ▓▓▓▓▓▓▓▓▓▓ (Constant)
    core/ ←→ error/            ▓▓▓▓▓▓▓░░░ (Frequent)
    engine/ ←→ aim/            ▓▓▓▓▓▓░░░░ (Per-task)
    core/ ←→ specifications/   ▓▓▓▓▓░░░░░ (Planning phase)
    error/ ←→ logs/            ▓▓▓▓▓▓▓▓░░ (Error tracking)
    engine/ ←→ state/          ▓▓▓▓▓▓▓▓▓▓ (Constant)
    scripts/ ←→ core/          ▓▓▓░░░░░░░ (Manual operations)
    gui/ ←→ state/             ▓▓▓▓▓░░░░░ (UI updates)
    pm/ ←→ workstreams/        ▓▓▓▓░░░░░░ (Workstream creation)

                CRITICAL PATH
                ══════════════

    workstreams → schema → core → engine → state → logs
         ▓▓▓       ▓▓▓     ▓▓▓     ▓▓▓      ▓▓▓     ▓▓▓

    (All nodes on critical path are high-frequency)
```

---

## 9. Information Flow by Phase

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  INFORMATION FLOW BY EXECUTION PHASE                     │
└─────────────────────────────────────────────────────────────────────────┘

PHASE 0: INITIALIZATION
═══════════════════════

    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ config/ │────→│  core/  │────→│ engine/ │
    └─────────┘     │ startup │     └─────────┘
         ↓          └─────────┘          ↓
    ┌─────────┐          ↓          ┌─────────┐
    │ schema/ │          │          │  aim/   │
    └─────────┘          │          │ bridge  │
         ↓               │          └─────────┘
    ┌─────────┐          ↓
    │templates│     ┌─────────┐
    └─────────┘     │ state/  │
                    │  init   │
                    └─────────┘

PHASE 1: PLANNING
═════════════════

    ┌────────────┐
    │workstreams/│
    └──────┬─────┘
           │
           ▼
    ┌──────────┐     ┌─────────────┐
    │ schema/  │────→│ core/       │
    │ validate │     │ planner     │
    └──────────┘     └──────┬──────┘
                            │
                     ┌──────┴────────┐
                     │               │
                     ▼               ▼
              ┌─────────────┐  ┌─────────┐
              │specifications│ │registry/│
              └─────────────┘  └─────────┘

PHASE 2: EXECUTION
══════════════════

    ┌──────────┐
    │  core/   │
    │scheduler │
    └────┬─────┘
         │
         ▼
    ┌──────────┐     ┌─────────┐
    │ engine/  │────→│  aim/   │
    │  queue   │     │ lookup  │
    └────┬─────┘     └─────────┘
         │
         ▼
    ┌──────────┐     ┌─────────┐     ┌─────────┐
    │ engine/  │────→│ state/  │────→│  logs/  │
    │orchestrator    │  save   │     │ record  │
    └────┬─────┘     └─────────┘     └─────────┘
         │
         ▼
    ┌──────────┐
    │ modules/ │
    │  output  │
    └──────────┘

PHASE 3: VALIDATION
═══════════════════

    ┌──────────┐
    │ modules/ │
    │  output  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐     ┌─────────┐
    │  error/  │────→│  logs/  │
    │ plugins  │     │  write  │
    └────┬─────┘     └─────────┘
         │
         ▼
    ┌──────────┐
    │  error/  │
    │  engine  │
    └────┬─────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[AUTO-FIX] [REPORT]

PHASE 4: COMPLETION
═══════════════════

    ┌──────────┐     ┌─────────┐
    │  state/  │────→│  logs/  │
    │ finalize │     │  close  │
    └────┬─────┘     └────┬────┘
         │                │
         └────────┬───────┘
                  │
                  ▼
            ┌──────────┐     ┌─────────┐
            │ modules/ │────→│archive/ │
            │packaging │     │  store  │
            └──────────┘     └─────────┘
                  │
                  ▼
            ┌──────────┐
            │   gui/   │
            │ display  │
            └──────────┘
```

This diagram collection provides multiple perspectives on the system's operation, data flow, dependencies, and state management. Each view helps understand different aspects of how folders interact to accomplish the pipeline's goals.
