---
doc_id: DOC-GUIDE-KEY-INNOVATIONS-FOR-FILE-PASSING-1134
---

 ● Based on my analysis of these comprehensive specifications in the pipeline_plus directory, here's how this information creates a better way to pass files between CLI tools:

   Key Innovations for File Passing Between CLI Tools

   1. Unified Workstream Template (WORKSTREAM_V1.1)

   The specifications define a universal, tool-agnostic prompt template that standardizes how files and tasks are communicated across different CLI tools (Aider, Codex, Claude Code, etc.):

     - [FILE_SCOPE] section: Explicitly declares which files can be modified (files_scope) and created (files_may_create)
     - Tool-neutral core with optional tool-specific execution hints
     - ASCII-only format that works universally across all CLI tools

   2. Patch Files as Primary Transport Mechanism

   The specs establish unified diff patches as the canonical way to pass code changes between tools:

   Benefits:

     - Deterministic: Same patch produces identical changes across environments
     - Auditable: Every change is explicitly documented
     - Reversible: Easy rollback via reverse patches
     - Language-agnostic: Works for Python, PowerShell, any text-based code
     - Portable: Can be applied on Windows, WSL, CI/CD, anywhere

   Workflow:

     Tool A (Aider) → generates patch → .ledger/patches/ws-{id}.patch
        ↓
     Router validates patch scope & safety
        ↓
     Tool B (Claude) → applies & validates patch → returns results

   3. Central Router/Orchestrator Pattern

   The ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC defines a sophisticated routing system:

   Task Queue Structure:

     .tasks/inbox/     → New tasks as JSON
     .tasks/running/   → Currently executing
     .tasks/done/      → Completed successfully
     .tasks/failed/    → Failed/timeout

   Each task includes:

     - source_app: Who created it
     - target_app: Who should execute it
     - payload.files: File list
     - patch_file: Optional pre-generated patch
     - mode: "prompt" | "patch_review" | "patch_apply_validate"

   4. Enhanced File Passing Modes

   Mode 1: Prompt-Based (Traditional)

     {
       "mode": "prompt",
       "repo_path": "C:/repo",
       "files": ["src/module.py"],
       "description": "Refactor for clarity"
     }

   Tool receives file paths, makes changes directly.

   Mode 2: Patch-Based Review

     {
       "mode": "patch_review",
       "patch_file": ".tasks/patches/ws-10.patch",
       "objective": "Review for correctness"
     }

   Tool receives already-generated changes as a patch, reviews without editing.

   Mode 3: Patch Application & Validation

     {
       "mode": "patch_apply_validate",
       "patch_file": ".tasks/patches/ws-10.patch",
       "validation_tasks": ["pytest", "ruff check"]
     }

   Tool applies patch in isolation, runs tests, reports back.

   5. Agent Operations Specification

   The AGENT_OPERATIONS_SPEC defines strict contracts:

   Patch Metadata Schema:

     {
       "patch_id": "...",
       "task_id": "...",
       "workstream_id": "ws-10",
       "source_tool": "aider",
       "files_modified": ["src/a.py", "src/b.py"],
       "diff_hash": "abc123...",  # For oscillation detection
       "created_at_utc": "2025-11-19T...",
       "validated": true,
       "applied": true
     }

   Scope Validation Before Application:

     - Check patch only modifies files in files_scope
     - Reject patches touching locked/protected areas
     - Detect oscillation (same diff repeating)

   6. Multi-Tool Coordination Workflow

   Example: Edit → Validate → Merge Flow

     Step 1: Aider generates patch
       Command: aider --yes --no-tty --model deepseek-coder src/module.py
       Output: .ledger/patches/ws-10-{run-id}.patch

     Step 2: Router validates scope
       Check: All files in patch are in workstream.files_scope
       Result: VALID

     Step 3: Router delegates to Claude for review
       Task mode: "patch_review"
       Payload: {patch_file, review_instructions}

     Step 4: Claude reviews (no edits)
       Output: Review comments + approval/rejection

     Step 5: If approved, apply patch
       git apply .ledger/patches/ws-10-{run-id}.patch
       git commit -m "AI: Refactor module.py [ws-10]"

   7. Practical Implementation

   For your pipeline, implement:

     - Enhance SubmitTask.ps1 to support patch mode:

     .\SubmitTask.ps1 `
       -Tool router `
       -Mode patch_apply_validate `
       -PatchFile ".ledger/patches/ws-10.patch" `
       -ValidationCommands @("pytest", "ruff check")

     - Create patch capture after every edit:

     # In orchestrator.py after edit step
     patch_content = subprocess.run(
         ['git', 'diff', '--no-ext-diff'],
         capture_output=True, text=True
     ).stdout

     patch_file = Path(f'.ledger/patches/{ws_id}-{run_id}.patch')
     patch_file.write_text(patch_content)

     # Store metadata
     db.record_patch(run_id, ws_id, patch_file, ...)

     - Add scope validation:

     def validate_patch_scope(patch_file, allowed_files):
         modified = parse_patch_files(patch_file)
         violations = [f for f in modified if f not in allowed_files]
         return len(violations) == 0, violations

   Summary: Why This Is Better

   Old way: Tools directly modify files, hard to track/audit/coordinate
   New way: Tools produce/consume patches as explicit change contracts

   Benefits: ✅ Deterministic: Exact same changes across all environments
   ✅ Auditable: Every change is a discrete, reviewable artifact
   ✅ Safe: Validate before apply, easy rollback
   ✅ Multi-tool: Clean handoff between Aider→Claude→Codex
   ✅ Cross-environment: Same patch works on laptop, WSL, CI
   ✅ Guard rails: Scope checking prevents out-of-bounds edits

   This transforms file passing from "tool runs and modifies stuff" to "tool generates change proposal → router validates → apply with full audit trail."

 > what are the sections of this approch that need to be devloped and how do they connect to eacj other

 ✓ List directory core (32 files)

 ✓ List directory src\pipeline (32 files)

 ✓ List directory scripts (46 files)

 ● Based on the comprehensive pipeline_plus specifications and your current codebase, here are the development sections needed and how they connect:

   Architecture Overview: 7 Development Sections

     ┌─────────────────────────────────────────────────────────────────┐
     │                     1. TASK ROUTER/ORCHESTRATOR                 │
     │         (Central brain - routes tasks between tools)            │
     └───────────┬─────────────────────────────────────────┬───────────┘
                 │                                         │
         ┌───────▼────────┐                       ┌────────▼────────┐
         │  2. TASK QUEUE │                       │  3. APP ADAPTERS│
         │   MANAGEMENT   │                       │   (per CLI tool)│
         └───────┬────────┘                       └────────┬────────┘
                 │                                         │
         ┌───────▼─────────────────────────────────────────▼────────┐
         │           4. PROMPT ENGINE & TEMPLATE RENDERER            │
         │        (WORKSTREAM_V1.1 → tool-specific prompts)          │
         └───────┬───────────────────────────────────────────────────┘
                 │
         ┌───────▼────────────────────────────────────────────────┐
         │         5. PATCH MANAGEMENT SYSTEM                     │
         │    (Generate, validate, apply, track patches)          │
         └───────┬────────────────────────────────────────────────┘
                 │
         ┌───────▼────────────────────────────────────────────────┐
         │      6. VALIDATION & CIRCUIT BREAKERS                  │
         │  (Scope check, oscillation detection, timeouts)        │
         └───────┬────────────────────────────────────────────────┘
                 │
         ┌───────▼────────────────────────────────────────────────┐
         │         7. AUDIT & TELEMETRY SYSTEM                    │
         │     (Logs, metrics, patch ledger, compliance)          │
         └────────────────────────────────────────────────────────┘

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 1: Task Router/Orchestrator

   What It Does

   Central coordinator that:

     - Receives task submissions from any source (Codex, Claude, Aider, human)
     - Decides which tool should execute the task
     - Manages task lifecycle (pending → running → done/failed)
     - Applies routing rules from config

   Files to Create/Modify

     NEW: core/engine/task_router.py
     NEW: core/engine/routing_policy.py
     MODIFY: core/orchestrator.py (integrate router)
     NEW: config/router.config.yaml

   Key Classes

     # core/engine/task_router.py

     class TaskRouter:
         """Routes tasks to appropriate CLI tools"""

         def __init__(self, config_path: str):
             self.config = load_yaml(config_path)
             self.app_registry = AppRegistry(self.config['apps'])
             self.routing_policy = RoutingPolicy(self.config['routing'])

         def route_task(self, task: Task) -> ToolSelection:
             """
             Input: Task with source_app, capabilities, constraints
             Output: ToolSelection(primary, fallback, reason)
             """
             # 1. Check delegation rules
             # 2. Match capabilities to tools
             # 3. Apply routing policy
             # 4. Return selected tool

     class ToolSelection:
         primary: str        # e.g., "aider"
         fallback: str       # e.g., "claude-code"
         reason: str         # "Capability: refactor+python"

   Connects To

     - Section 2 (Queue): Reads tasks from queue
     - Section 3 (Adapters): Delegates to selected tool adapter
     - Section 6 (Validation): Applies circuit breaker rules
     - Section 7 (Audit): Logs routing decisions

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 2: Task Queue Management

   What It Does

   Manages task lifecycle through file-based queue:

     - Inbox (new tasks)
     - Running (active execution)
     - Done (completed)
     - Failed (timeout/error)

   Files to Create/Modify

     NEW: core/state/task_queue.py
     NEW: .tasks/inbox/       (directory)
     NEW: .tasks/running/     (directory)
     NEW: .tasks/done/        (directory)
     NEW: .tasks/failed/      (directory)
     MODIFY: scripts/SubmitTask.ps1 (write to queue)

   Key Classes

     # core/state/task_queue.py

     class TaskQueue:
         """File-based task queue manager"""

         def enqueue(self, task: Task) -> str:
             """Write task to .tasks/inbox/{task_id}.json"""

         def dequeue(self) -> Optional[Task]:
             """Read next task from inbox → move to running"""

         def complete(self, task_id: str, result: TaskResult):
             """Move from running → done, store result"""

         def fail(self, task_id: str, error: str):
             """Move from running → failed, store error"""

     class Task:
         task_id: str                    # ULID
         source_app: str                 # "codex", "claude", etc.
         mode: str                       # "prompt" | "patch_review" | "patch_apply_validate"
         capabilities: List[str]         # ["refactor", "python"]
         payload: TaskPayload            # Files, repo path, patch file, etc.
         constraints: TaskConstraints    # allow_delegation, must_stay_local
         timeouts: TaskTimeouts          # wall_clock_sec, idle_output_sec
         routing_state: RoutingState     # current_target, route_history

   Connects To

     - Section 1 (Router): Router reads from queue
     - Section 3 (Adapters): Tasks contain payload for adapters
     - Section 7 (Audit): Queue transitions logged

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 3: App Adapters

   What It Does

   Per-tool adapters that know how to:

     - Execute each CLI tool (Aider, Codex, Claude, etc.)
     - Translate generic Task → tool-specific CLI args
     - Run headless/non-interactive
     - Stream output back to orchestrator

   Files to Create/Modify

     NEW: core/engine/adapters/base.py
     NEW: core/engine/adapters/aider_adapter.py
     NEW: core/engine/adapters/codex_adapter.py
     NEW: core/engine/adapters/claude_adapter.py
     NEW: config/tool_profiles.json (enhance existing)

   Key Classes

     # core/engine/adapters/base.py

     class ToolAdapter(ABC):
         """Base adapter for CLI tools"""

         @abstractmethod
         def build_command(self, task: Task) -> List[str]:
             """Build CLI command from task"""

         @abstractmethod
         def execute(self, cmd: List[str], timeout: int) -> ToolResult:
             """Run tool headless, capture output"""

     # core/engine/adapters/aider_adapter.py

     class AiderAdapter(ToolAdapter):
         def build_command(self, task: Task) -> List[str]:
             if task.mode == "prompt":
                 return [
                     "aider",
                     "--yes",
                     "--no-tty",
                     "--model", "deepseek-coder",
                     "--message-file", task.payload.prompt_file,
                     *task.payload.files
                 ]
             elif task.mode == "patch_apply_validate":
                 # Different command for patch mode
                 pass

         def execute(self, cmd: List[str], timeout: int) -> ToolResult:
             # Run subprocess, capture stdout/stderr
             # Apply timeout monitoring
             # Return ToolResult

   Connects To

     - Section 1 (Router): Router selects adapter based on tool
     - Section 4 (Prompts): Adapters use rendered prompts
     - Section 5 (Patches): Adapters generate or apply patches
     - Section 6 (Validation): Adapters respect timeouts

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 4: Prompt Engine & Template Renderer

   What It Does

   Generates structured prompts from workstream bundles:

     - Renders WORKSTREAM_V1.1 template
     - Infers classification (complexity, domain, quality)
     - Infers role/persona
     - Creates tool-specific variants (Aider vs Codex vs Claude)

   Files to Create/Modify

     MODIFY: core/prompts.py (major refactor)
     NEW: core/engine/prompt_engine.py
     NEW: aider/templates/prompts/edit_prompt_v1.1.txt.j2
     NEW: aider/templates/prompts/edit_prompt_v1.1_aider.txt.j2
     NEW: aider/templates/prompts/edit_prompt_v1.1_codex.txt.j2

   Key Classes

     # core/engine/prompt_engine.py

     class PromptEngine:
         """Enhanced prompt generation with V1.1 templates"""

         def render_edit_prompt_v11(
             self,
             bundle: Dict[str, Any],
             context: PromptContext
         ) -> str:
             """
             Generate WORKSTREAM_V1.1 prompt:
             1. Infer classification if not explicit
             2. Infer role/persona
             3. Determine reasoning mode
             4. Populate template sections
             5. Return rendered ASCII prompt
             """

         def _infer_classification(self, bundle) -> Classification:
             """Derive complexity/quality/domain from bundle metadata"""

         def _infer_role(self, bundle) -> str:
             """Generate persona string (e.g., 'Senior Python engineer')"""

         def _select_template_variant(self, target_app: str) -> str:
             """Choose universal vs tool-specific template"""

     class Classification:
         complexity: str  # simple|moderate|complex|enterprise
         quality: str     # standard|production
         domain: str      # code|docs|tests|analysis

   Connects To

     - Section 3 (Adapters): Adapters use rendered prompts
     - Section 1 (Router): Classification influences routing
     - Existing bundles.py: Loads workstream bundles
     - Existing schema: Validates bundle format

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 5: Patch Management System

   What It Does

   Core patch lifecycle management:

     - Capture patches after edits (git diff)
     - Validate patch scope (only allowed files)
     - Store patches with metadata
     - Apply patches safely
     - Track patch history for oscillation detection

   Files to Create/Modify

     NEW: core/engine/patch_manager.py
     NEW: .ledger/patches/   (directory)
     MODIFY: core/orchestrator.py (capture patches after edit)
     MODIFY: core/db.py (add patch operations)
     NEW: schema/migrations/001_add_patches_table.sql

   Key Classes

     # core/engine/patch_manager.py

     class PatchManager:
         """Manages patch creation, validation, application"""

         def capture_patch(
             self,
             run_id: str,
             ws_id: str,
             worktree_path: str
         ) -> PatchArtifact:
             """
             Generate unified diff:
             1. Run git diff in worktree
             2. Parse affected files
             3. Generate diff hash (for oscillation detection)
             4. Store to .ledger/patches/{ws_id}-{run_id}.patch
             5. Return PatchArtifact
             """

         def validate_scope(
             self,
             patch: PatchArtifact,
             allowed_files: List[str]
         ) -> ValidationResult:
             """
             Check patch only modifies allowed files:
             1. Parse patch to extract modified files
             2. Compare against bundle.files_scope
             3. Return violations or OK
             """

         def apply_patch(
             self,
             patch_file: Path,
             worktree_path: str
         ) -> ApplyResult:
             """
             Apply patch safely:
             1. git apply --check (dry run)
             2. If OK: git apply
             3. Return success/failure
             """

     class PatchArtifact:
         patch_file: Path
         line_count: int
         files_modified: List[str]
         diff_hash: str          # SHA256 for oscillation detection
         created_at: str

   Database Schema Extension

     -- schema/migrations/001_add_patches_table.sql

     CREATE TABLE patches (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         run_id TEXT NOT NULL,
         ws_id TEXT NOT NULL,
         step_name TEXT NOT NULL,      -- 'edit', 'fix_static', 'fix_runtime'
         attempt INTEGER NOT NULL,
         patch_file TEXT NOT NULL,
         diff_hash TEXT NOT NULL,       -- For oscillation detection
         line_count INTEGER NOT NULL,
         files_modified TEXT NOT NULL,  -- JSON array
         created_at TEXT NOT NULL,
         validated INTEGER DEFAULT 0,   -- 0=pending, 1=valid, -1=invalid
         applied INTEGER DEFAULT 0,
         FOREIGN KEY (run_id, ws_id) REFERENCES workstreams(run_id, ws_id)
     );

     CREATE INDEX idx_patches_diff_hash ON patches(ws_id, diff_hash);

   Connects To

     - Section 3 (Adapters): Adapters generate patches during execution
     - Section 6 (Validation): Patch validation before application
     - Section 7 (Audit): Patches logged as artifacts
     - Existing db.py: Database operations for patches table

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 6: Validation & Circuit Breakers

   What It Does

   Safety mechanisms:

     - Scope validation (file boundaries)
     - Oscillation detection (same patch repeating)
     - Timeout enforcement (wall clock, idle output)
     - Retry/fallback logic
     - Circuit breaker trip conditions

   Files to Create/Modify

     MODIFY: core/circuit_breakers.py (add oscillation detection)
     NEW: core/engine/validators.py
     MODIFY: core/orchestrator.py (integrate validation gates)

   Key Enhancements

     # core/circuit_breakers.py (MODIFY)

     class CircuitBreaker:
         """Enhanced with oscillation detection"""

         def check_oscillation(self, ws_id: str, diff_hash: str) -> Optional[CircuitBreakerTrip]:
             """
             Detect if same diff appears repeatedly:
             1. Query last N patches for this workstream
             2. Count occurrences of current diff_hash
             3. If >= threshold: return CircuitBreakerTrip
             """

         def should_stop(
             self,
             run_id: str,
             ws_id: str,
             step_name: str,
             attempt: int,
             error_signature: Optional[str] = None,
             diff_hash: Optional[str] = None
         ) -> Optional[CircuitBreakerTrip]:
             """
             Comprehensive checks:
             1. Exceeded max_attempts?
             2. Error signature repeating?
             3. Oscillation detected (NEW)?
             """

     # core/engine/validators.py (NEW)

     class ScopeValidator:
         """Validates patch/changes stay within declared scope"""

         def validate_patch_scope(
             self,
             patch: PatchArtifact,
             bundle: Dict
         ) -> ScopeValidationResult:
             """Ensure patch only touches files_scope + files_may_create"""

     class TimeoutMonitor:
         """Monitors execution for timeouts"""

         def watch_process(
             self,
             process: subprocess.Popen,
             wall_clock_sec: int,
             idle_output_sec: int
         ) -> TimeoutResult:
             """
             Monitor subprocess:
             1. Track total runtime vs wall_clock_sec
             2. Track time since last output vs idle_output_sec
             3. Kill if exceeded, return timeout reason
             """

   Connects To

     - Section 5 (Patches): Validates patches before apply
     - Section 3 (Adapters): Enforces timeouts during execution
     - Section 1 (Router): Circuit breakers block routing
     - Section 7 (Audit): Logs validation failures and circuit trips

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Section 7: Audit & Telemetry System

   What It Does

   Complete observability:

     - Structured logging (JSONL)
     - Patch ledger (all patches stored)
     - Metrics (success rates, durations, failure reasons)
     - Event tracking (routing, execution, validation)

   Files to Create/Modify

     NEW: core/state/audit_logger.py
     NEW: .runs/audit.jsonl
     NEW: scripts/workstream_metrics.ps1
     MODIFY: core/db.py (enhance event recording)

   Key Classes

     # core/state/audit_logger.py

     class AuditLogger:
         """Structured audit logging"""

         def log_event(
             self,
             event_type: str,
             task_id: str,
             data: Dict[str, Any]
         ):
             """
             Write to .runs/audit.jsonl:
             {
               "timestamp": "2025-11-19T19:45:00Z",
               "event_type": "task_routed",
               "task_id": "01J2XYZ...",
               "data": {
                 "source_app": "codex",
                 "target_app": "aider",
                 "reason": "Capability: refactor+python"
               }
             }
             """

     class MetricsCollector:
         """Aggregate metrics from audit log and database"""

         def compute_metrics(self, days: int = 7) -> Metrics:
             """
             Query database and audit log:
             - First-pass success rate by tool
             - Average fix attempts per workstream
             - Circuit breaker trip reasons
             - Execution time distributions
             """

     class PatchLedger:
         """Manage .ledger/patches/ directory"""

         def store_patch(self, patch: PatchArtifact) -> Path:
             """Store with timestamp + ULID naming"""

         def get_patch_history(self, ws_id: str) -> List[PatchArtifact]:
             """Retrieve all patches for a workstream"""

   Event Types to Track

     EVENT_TYPES = [
         "task_received",
         "task_routed",
         "process_started",
         "stdout_chunk",
         "timeout",
         "patch_captured",
         "patch_validated",
         "patch_applied",
         "scope_violation",
         "oscillation_detected",
         "circuit_breaker_trip",
         "retry_scheduled",
         "completed",
         "failed"
     ]

   Connects To

     - All Sections: Every section logs events
     - Section 5 (Patches): Stores patches in ledger
     - Section 6 (Validation): Logs validation results
     - Existing db.py: Queries database for metrics

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Connection Flow Diagram

     ┌─────────────────────────────────────────────────────────┐
     │  USER/SOURCE APP (Codex, Claude, Human)                 │
     └────────────────────┬────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  scripts/SubmitTask   │──────────┐
              └───────────────────────┘          │
                          │                      │ Creates task JSON
                          ▼                      ▼
              ┌────────────────────────────────────┐
              │  SECTION 2: Task Queue             │
              │  .tasks/inbox/{task_id}.json       │
              └─────────────┬──────────────────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 1: Task Router            │
              │  - Load task from queue            │
              │  - Apply routing policy            │
              │  - Select tool (primary/fallback)  │
              └─────────────┬──────────────────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 4: Prompt Engine          │
              │  - Render WORKSTREAM_V1.1          │
              │  - Infer classification & role     │
              │  - Generate tool-specific prompt   │
              └─────────────┬──────────────────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 3: App Adapter            │
              │  - Build CLI command               │
              │  - Execute tool headless           │
              │  - Capture stdout/stderr           │
              └─────────────┬──────────────────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 5: Patch Manager          │
              │  - Capture git diff → .patch file  │
              │  - Parse modified files            │
              │  - Generate diff hash              │
              └─────────────┬──────────────────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 6: Validation             │
              │  - Validate scope (files allowed?) │
              │  - Check oscillation (hash repeat?)│
              │  - Apply circuit breakers          │
              └─────────────┬──────────────────────┘
                            │
                        ┌───┴───┐
                        │ Valid?│
                        └───┬───┘
                    YES ────┼──── NO
                        │   │   │
                        ▼   │   ▼
              ┌───────────┐ │ ┌──────────────┐
              │ Apply     │ │ │ Quarantine   │
              │ Patch     │ │ │ or Retry     │
              └─────┬─────┘ │ └──────┬───────┘
                    │       │        │
                    ▼       │        │
              ┌───────────┐ │        │
              │ Commit    │ │        │
              └─────┬─────┘ │        │
                    │       │        │
                    └───────┴────────┘
                            │
                            ▼
              ┌────────────────────────────────────┐
              │  SECTION 7: Audit & Telemetry      │
              │  - Log all events to audit.jsonl   │
              │  - Store patch in ledger           │
              │  - Update database tables          │
              │  - Emit metrics                    │
              └────────────────────────────────────┘

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Development Roadmap

   Phase 1: Foundation (Weeks 1-2)

   Goal: Core infrastructure without breaking existing system

   Build:

     - Section 2: Task Queue (file-based queue system)
     - Section 5: Basic Patch Manager (capture + store)
     - Section 7: Audit Logger (structured logging)

   Test: Can submit task → stored in queue → patch captured → logged

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Phase 2: Routing (Weeks 3-4)

   Goal: Multi-tool routing with config

   Build: 4. Section 1: Task Router + Routing Policy 5. Section 3: Base Adapter + Aider Adapter 6. Config: router.config.yaml with apps + routing rules

   Test: Task routed to Aider → executes → returns result

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Phase 3: Enhanced Prompts (Week 5)

   Goal: WORKSTREAM_V1.1 templates

   Build: 7. Section 4: Prompt Engine with V1.1 rendering 8. Templates: Universal + Aider-specific variants 9. Classification inference logic

   Test: Bundle → V1.1 prompt → Aider executes successfully

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Phase 4: Validation (Week 6)

   Goal: Safety gates and circuit breakers

   Build: 10. Section 6: Scope Validator + Oscillation Detection 11. Section 5: Patch scope validation 12. Enhanced Circuit Breakers

   Test: Out-of-scope edit blocked, oscillation detected and stopped

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Phase 5: Integration (Week 7)

   Goal: End-to-end multi-tool workflow

   Build: 13. Additional adapters (Codex, Claude) 14. Patch-based handoff between tools 15. Metrics dashboard

   Test: Codex → patch → Claude reviews → Aider applies → validated → committed

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Quick Start: Minimum Viable Implementation

   If you want to start immediately, build this minimal flow:

     # 1. Create task queue (Section 2)
     task = Task(
         task_id=ulid(),
         source_app="codex",
         mode="prompt",
         payload=TaskPayload(
             repo_path="C:/repo",
             files=["src/module.py"],
             description="Refactor for clarity"
         )
     )
     queue.enqueue(task)

     # 2. Router picks tool (Section 1 - simplified)
     target_app = "aider"  # hardcoded for now

     # 3. Render prompt (Section 4 - basic)
     prompt = render_basic_v11(task.payload.description, task.payload.files)

     # 4. Execute via adapter (Section 3)
     adapter = AiderAdapter()
     result = adapter.execute_with_prompt(prompt, task.payload.files)

     # 5. Capture patch (Section 5)
     patch = capture_patch(task.task_id, worktree_path)

     # 6. Store in ledger (Section 7)
     store_patch(patch, f".ledger/patches/{task.task_id}.patch")
     log_event("patch_captured", task.task_id, {"files": patch.files_modified})

   This gives you the backbone to build on incrementally.