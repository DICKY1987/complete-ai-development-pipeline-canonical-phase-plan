---
doc_id: DOC-GUIDE-ARCHITECTURE-MIGRATION-PLAN-1411
---

  Recommended Approach

  Question 1: Interface Type → Python Protocols + Event-Based Messaging

  Why this combination:

  1. Python Protocols (from typing)
    - Define contracts between sections without tight coupling
    - Type-safe, IDE-friendly, no inheritance required
    - Each section implements its protocol independently
    - Easy to mock for testing
  2. Event-Based Messaging (internal event bus)
    - Sections communicate via events, not direct calls
    - Matches your existing events table in the database
    - Natural fit for the orchestrator pattern you already have
    - Enables the GUI "mission control" to subscribe to all section events

  Example structure:
  # core/interfaces/state_interface.py
  from typing import Protocol

  class StateInterface(Protocol):
      def create_run(self, ws_id: str) -> str: ...
      def get_run_status(self, run_id: str) -> dict: ...
      def emit_event(self, event_type: str, payload: dict) -> None: ...

  ---
  Question 2: Connection Pattern → Facade/Gateway with Event Bus

  Why a facade:

  1. Single entry point for external consumers (GUI, CLI, future REST API)
  2. Orchestrates cross-section workflows without sections knowing about
  each other
  3. Translates between section-specific types and unified types
  4. Already fits your architecture - the orchestrator is essentially this
  pattern

  Architecture:

  ┌─────────────────────────────────────┐
  │         Unified Gateway             │
  │   (aggregates all section APIs)     │
  └─────────────┬───────────────────────┘
                │
         ┌──────┴──────┐
         │  Event Bus  │
         └──────┬──────┘
                │
      ┌─────────┼─────────┬─────────┬─────────┐
      ▼         ▼         ▼         ▼         ▼
  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
  │ State │ │Engine │ │Planning│ │ Error │ │ AIM   │
  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘

  Benefits:
  - Sections remain independent (only know about their own interface + event
   bus)
  - Gateway handles cross-cutting concerns (logging, auth, transactions)
  - GUI subscribes to event bus for real-time updates
  - Easy to add new sections without modifying existing ones

  ---
  Core Runtime Sections to Interface

  1. State - Data persistence, bundles, worktrees
  2. Engine - Orchestration, scheduling, execution
  3. Planning - Workstream generation
  4. Error - Error detection and recovery
  5. AIM - Tool registry and invocation
  6. Aider - Prompt generation and AI tool calls

  ---

● This document provides excellent guidance that refines the interface
  approach. Let me update my recommendation based on this architecture.

  Revised Section Interfaces - Aligned with Hybrid Architecture

  Core Runtime Sections (6 total)

  Based on the layout document, the sections should map to:

  | Section  | Directory                           | Role
               |
  |----------|-------------------------------------|------------------------
  -------------|
  | State    | core/state/ → engine/state_store/   | ADAPTER_ROLE: 
  state_store           |
  | Engine   | core/engine/ → engine/orchestrator/ | ADAPTER_ROLE: 
  job_orchestrator      |
  | Adapters | NEW engine/adapters/                | ADAPTER_ROLE: 
  terminal_tool_adapter |
  | Planning | core/planning/                      | Workstream/job
  generation           |
  | Error    | error/                              | Error detection,
  recovery           |
  | AIM      | aim/                                | Tool registry routing
               |

  ---
  Refined Interface Approach

  1. Interface Type → Job Schema + State Store Protocol

  The document establishes a clear contract pattern:

  Job JSON = The interface between sections
  - Every action is a job file conforming to job.schema.json
  - Sections don't call each other directly
  - They read/write through the state store

  State Store Protocol = The shared data layer
  - All sections read/write to job_state_store
  - Provides: list_jobs(), get_job(), mark_running(), update_from_result()

  2. Connection Pattern → Orchestrator as Gateway

  The orchestrator is explicitly the single entry point:

  GUI/CLI → Orchestrator → Adapters → Tools
                ↓
           State Store ← All sections read/write

  Key Rule from doc:
  "GUI code never directly calls tools like Aider/Codex. It only talks to 
  /engine/orchestrator.py and reads state from /engine/job_state_store.py"

  ---
  Proposed Interface Structure

  # engine/interfaces/state_interface.py
  class StateInterface(Protocol):
      def mark_running(self, job_id: str) -> None: ...
      def update_from_result(self, job: dict, result: JobResult) -> None:
  ...
      def list_jobs(self, run_id: str) -> list[dict]: ...
      def get_job(self, job_id: str) -> dict: ...

  # engine/interfaces/adapter_interface.py
  class AdapterInterface(Protocol):
      def run_job(self, job: dict) -> JobResult: ...

  # engine/types.py
  @dataclass
  class JobResult:
      exit_code: int
      error_report_path: str
      duration_s: float

  ---
  
     ╭─────────────────────────────────────────────────────────────────────────╮
     │ Plan: Map core/ Structure to engine/ Hybrid Architecture                │
     │                                                                         │
     │ Overview                                                                │
     │                                                                         │
     │ Reorganize the current core/ structure into the engine/ hybrid          │
     │ architecture described in the layout document, introducing formal       │
     │ Protocol interfaces for each section.                                   │
     │                                                                         │
     │ ---                                                                     │
     │ Current → Target Mapping                                                │
     │                                                                         │
     │ Directory Structure Transformation                                      │
     │                                                                         │
     │ CURRENT                          TARGET                                 │
     │ ─────────────────────────────    ─────────────────────────────          │
     │ core/                            engine/                                │
     │ ├── state/                       ├── state_store/                       │
     │ │   ├── db.py                    │   ├── __init__.py                    │
     │ │   ├── db_sqlite.py             │   ├── job_state_store.py    (new:    │
     │ unified interface)                                                      │
     │ │   ├── crud.py                  │   ├── db.py                          │
     │ │   ├── bundles.py               │   ├── crud.py                        │
     │ │   └── worktree.py              │   └── worktree.py                    │
     │ │                                │                                      │
     │ ├── engine/                      ├── orchestrator/                      │
     │ │   ├── orchestrator.py          │   ├── __init__.py                    │
     │ │   ├── scheduler.py             │   ├── orchestrator.py                │
     │ │   ├── executor.py              │   ├── job_queue.py          (new:    │
     │ from scheduler)                                                         │
     │ │   ├── tools.py                 │   └── job_state_store.py             │
     │ (interface to state_store)                                              │
     │ │   ├── circuit_breakers.py      │                                      │
     │ │   └── recovery.py              ├── adapters/                          │
     │ │                                │   ├── __init__.py                    │
     │ ├── planning/                    │   ├── aider_adapter.py      (from    │
     │ aider/engine.py)                                                        │
     │ │   ├── planner.py               │   ├── codex_adapter.py      (new)    │
     │ │   └── archive.py               │   ├── tests_adapter.py      (new)    │
     │                                  │   ├── git_adapter.py        (new)    │
     │                                  │   └── error_adapter.py      (wraps   │
     │ error/)                                                                 │
     │                                  │                                      │
     │                                  ├── planning/                          │
     │                                  │   ├── planner.py                     │
     │                                  │   └── archive.py                     │
     │                                  │                                      │
     │                                  └── types.py                  (shared  │
     │ types: JobResult, etc.)                                                 │
     │                                                                         │
     │ error/                           error/                        (stays   │
     │ mostly same)                                                            │
     │ ├── engine/                      ├── engine/                            │
     │ ├── plugins/                     ├── plugins/                           │
     │ └── shared/                      └── shared/                            │
     │                                                                         │
     │ aim/                             aim/                          (stays   │
     │ same)                                                                   │
     │ └── bridge.py                    └── bridge.py                          │
     │                                                                         │
     │ aider/                           (absorbed into engine/adapters/)       │
     │ └── engine.py                                                           │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 1: Create Interface Definitions                                   │
     │                                                                         │
     │ Create engine/interfaces/ with Protocol definitions:                    │
     │                                                                         │
     │ 1.1 State Interface (engine/interfaces/state_interface.py)              │
     │                                                                         │
     │ class StateInterface(Protocol):                                         │
     │     def create_run(self, ws_id: str) -> str: ...                        │
     │     def get_run(self, run_id: str) -> dict: ...                         │
     │     def update_run_status(self, run_id: str, status: str) -> None: ...  │
     │     def mark_job_running(self, job_id: str) -> None: ...                │
     │     def update_job_result(self, job: dict, result: JobResult) -> None:  │
     │ ...                                                                     │
     │     def list_jobs(self, run_id: str) -> list[dict]: ...                 │
     │     def get_job(self, job_id: str) -> dict: ...                         │
     │     def record_event(self, event_type: str, payload: dict) -> None: ... │
     │                                                                         │
     │ 1.2 Adapter Interface (engine/interfaces/adapter_interface.py)          │
     │                                                                         │
     │ class AdapterInterface(Protocol):                                       │
     │     def run_job(self, job: dict) -> JobResult: ...                      │
     │                                                                         │
     │ 1.3 Orchestrator Interface                                              │
     │ (engine/interfaces/orchestrator_interface.py)                           │
     │                                                                         │
     │ class OrchestratorInterface(Protocol):                                  │
     │     def run_job(self, job_file: str) -> JobResult: ...                  │
     │     def queue_job(self, job: dict) -> str: ...                          │
     │     def get_job_status(self, job_id: str) -> str: ...                   │
     │                                                                         │
     │ 1.4 Error Interface (engine/interfaces/error_interface.py)              │
     │                                                                         │
     │ class ErrorInterface(Protocol):                                         │
     │     def run_error_pipeline(self, files: list[str], ctx:                 │
     │ ErrorPipelineContext) -> dict: ...                                      │
     │     def get_error_context(self, run_id: str, ws_id: str) ->             │
     │ ErrorPipelineContext: ...                                               │
     │                                                                         │
     │ 1.5 AIM Interface (engine/interfaces/aim_interface.py)                  │
     │                                                                         │
     │ class AIMInterface(Protocol):                                           │
     │     def load_registry(self) -> dict: ...                                │
     │     def invoke_adapter(self, tool_id: str, **kwargs) -> ToolResult: ... │
     │     def get_tool_capabilities(self, tool_id: str) -> list[str]: ...     │
     │                                                                         │
     │ 1.6 Planning Interface (engine/interfaces/planning_interface.py)        │
     │                                                                         │
     │ class PlanningInterface(Protocol):                                      │
     │     def generate_workstream(self, spec: dict) -> dict: ...              │
     │     def archive_workstream(self, ws_id: str) -> None: ...               │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 2: Create Shared Types                                            │
     │                                                                         │
     │ Create engine/types.py with standardized types:                         │
     │                                                                         │
     │ @dataclass                                                              │
     │ class JobResult:                                                        │
     │     exit_code: int                                                      │
     │     error_report_path: str                                              │
     │     duration_s: float                                                   │
     │     stdout: str = ""                                                    │
     │     stderr: str = ""                                                    │
     │     success: bool = False                                               │
     │                                                                         │
     │ @dataclass                                                              │
     │ class Job:                                                              │
     │     job_id: str                                                         │
     │     workstream_id: str                                                  │
     │     tool: str                                                           │
     │     command: dict                                                       │
     │     env: dict                                                           │
     │     paths: dict                                                         │
     │     metadata: dict                                                      │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 3: Create Job Schema                                              │
     │                                                                         │
     │ Create schema/jobs/job.schema.json following the layout document's       │
     │ specification.                                                          │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 4: Create Adapters                                                │
     │                                                                         │
     │ 4.1 Aider Adapter (engine/adapters/aider_adapter.py)                    │
     │                                                                         │
     │ - Wrap aider/engine.py functionality                                    │
     │ - Implement AdapterInterface                                            │
     │ - Add ADAPTER_ROLE: terminal_tool_adapter header                        │
     │                                                                         │
     │ 4.2 Error Adapter (engine/adapters/error_adapter.py)                    │
     │                                                                         │
     │ - Wrap error/engine/error_engine.py                                     │
     │ - Implement AdapterInterface                                            │
     │                                                                         │
     │ 4.3 Tests Adapter (engine/adapters/tests_adapter.py)                    │
     │                                                                         │
     │ - Wrap test runner functionality                                        │
     │ - Implement AdapterInterface                                            │
     │                                                                         │
     │ 4.4 Git Adapter (engine/adapters/git_adapter.py)                        │
     │                                                                         │
     │ - Wrap git operations                                                   │
     │ - Implement AdapterInterface                                            │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 5: Create State Store                                             │
     │                                                                         │
     │ 5.1 Job State Store (engine/state_store/job_state_store.py)             │
     │                                                                         │
     │ - Implement StateInterface                                              │
     │ - Wrap existing core/state/ functionality                               │
     │ - Provide job-centric API (vs workstream-centric)                       │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 6: Refactor Orchestrator                                          │
     │                                                                         │
     │ 6.1 Update Orchestrator (engine/orchestrator/orchestrator.py)           │
     │                                                                         │
     │ - Implement OrchestratorInterface                                       │
     │ - Add CLI: python -m engine.orchestrator run-job --job-file <path>      │
     │ - Use TOOL_RUNNERS mapping to dispatch to adapters                      │
     │ - Add ADAPTER_ROLE: job_orchestrator header                             │
     │                                                                         │
     │ 6.2 Create Job Queue (engine/orchestrator/job_queue.py)                 │
     │                                                                         │
     │ - Extract from scheduler.py                                             │
     │ - Job status transitions: queued → running → completed/failed →         │
     │ quarantined                                                             │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 7: Update Shims                                                   │
     │                                                                         │
     │ Update src/pipeline/ shims to re-export from engine/ instead of core/.  │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 8: Create Gateway (Optional)                                      │
     │                                                                         │
     │ Create engine/gateway.py as unified entry point for GUI/CLI:            │
     │                                                                         │
     │ class EngineGateway:                                                    │
     │     def __init__(self):                                                 │
     │         self.state = JobStateStore()                                    │
     │         self.orchestrator = Orchestrator(self.state)                    │
     │         self.error = ErrorEngine()                                      │
     │         self.aim = AIMBridge()                                          │
     │         self.planning = Planner()                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Files to Create (17 files)                                              │
     │                                                                         │
     │ 1. engine/__init__.py                                                   │
     │ 2. engine/types.py                                                      │
     │ 3. engine/interfaces/__init__.py                                        │
     │ 4. engine/interfaces/state_interface.py                                 │
     │ 5. engine/interfaces/adapter_interface.py                               │
     │ 6. engine/interfaces/orchestrator_interface.py                          │
     │ 7. engine/interfaces/error_interface.py                                 │
     │ 8. engine/interfaces/aim_interface.py                                   │
     │ 9. engine/interfaces/planning_interface.py                              │
     │ 10. engine/adapters/__init__.py                                         │
     │ 11. engine/adapters/aider_adapter.py                                    │
     │ 12. engine/adapters/error_adapter.py                                    │
     │ 13. engine/adapters/tests_adapter.py                                    │
     │ 14. engine/adapters/git_adapter.py                                      │
     │ 15. engine/state_store/job_state_store.py                               │
     │ 16. engine/orchestrator/job_queue.py                                    │
     │ 17. schema/jobs/job.schema.json                                          │
     │                                                                         │
     │ Files to Modify (6 files)                                               │
     │                                                                         │
     │ 1. core/engine/orchestrator.py → add Protocol compliance                │
     │ 2. core/engine/tools.py → align with AdapterInterface                   │
     │ 3. aider/engine.py → extract to adapter                                 │
     │ 4. error/engine/error_engine.py → add Protocol compliance               │
     │ 5. aim/bridge.py → add Protocol compliance                              │
     │ 6. core/planning/planner.py → add Protocol compliance                   │
     │                                                                         │
     │ ---                                                                     │
     │ Backward Compatibility                                                  │
     │                                                                         │
     │ - All existing imports continue to work via shims                       │
     │ - core/ directories remain with re-exports to engine/                   │
     │ - Deprecation warnings guide migration                                  │
     │                                                                         │
     │ ---                                                                     │
     │ Benefits                                                                │
     │                                                                         │
     │ 1. Clear contracts - Protocols define explicit interfaces between       │
     │ sections                                                                │
     │ 2. Job-based architecture - All actions become jobs with JSON schemas   │
     │ 3. GUI-ready - GUI only needs orchestrator CLI + state store            │
     │ 4. Testable - Protocols enable easy mocking                             │
     │ 5. Extensible - New adapters follow established pattern                 │
     ╰─────────────────────────────────────────────────────────────────────────╯



