# Multi-CLI Parallelism & Real-Time GUI - Exploration Summary

**Date**: 2025-12-05 04:09
**Status**: Ready to Build
**Estimated Effort**: 3 weeks (Multi-CLI) + 1 week (GUI)

---

## 🎯 OVERVIEW: Two Major Features

### Feature 1: Multi-CLI Instance Parallelism ⚡
**Goal**: Run 3-5 AI agent instances simultaneously (3x-5x speedup)
**Status**: Fully designed, not implemented
**Effort**: 3 weeks (15 working days)

### Feature 2: Real-Time GUI Dashboard 📊
**Goal**: Monitor pipeline execution in real-time
**Status**: Partial implementation exists
**Priority**: Lower (CLI works fine, nice-to-have)

---

## 📋 FEATURE 1: MULTI-CLI PARALLELISM

### What It Enables
- **Parallel refactoring**: Run 3 aider instances on different files
- **Distributed testing**: Generate tests across multiple AI agents
- **Batch operations**: Process 100 files in 15 min instead of 75 min
- **Worktree parallelism**: Work on 4 git worktrees simultaneously

### Core Specs (Already Written ✅)
1. **\core/MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md\** - 3-week implementation plan
2. **\phase1_planning/modules/spec_parser/docs/specifications/specs/MULTI_CLI_WORKTREES_EXECUTION_SPEC.md\** - Worktree + multi-CLI integration
3. **\phase1_planning/modules/spec_parser/docs/specifications/specs/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md\** - DAG parallelism strategy
4. **\docs/DOC_operations/PARALLEL_EXECUTION_STRATEGY.md\** - Practical git worktree guide

---

## 🏗️ WEEK 1: ToolProcessPool Class (5 days)

### Goal
Create \ToolProcessPool\ class to manage 3-5 long-running CLI instances with stdin/stdout communication.

### Deliverables

#### Day 1-2: Core Implementation (10 hours)
**File**: \phase4_routing/modules/aim_tools/src/aim/bridge.py\ (add ~250 lines)

**Classes**:
\\\python
@dataclass
class ProcessInstance:
    index: int
    tool_id: str
    process: subprocess.Popen
    stdout_queue: queue.Queue
    stderr_queue: queue.Queue
    alive: bool = True

class ToolProcessPool:
    def __init__(self, tool_id: str, count: int)
    def send_prompt(self, instance_idx: int, prompt: str) -> bool
    def read_response(self, instance_idx: int, timeout: float) -> Optional[str]
    def get_status(self) -> List[Dict[str, Any]]
    def shutdown(self, timeout: float = 5.0)
\\\

**Key Features**:
- Background threads read stdout/stderr into queues
- Non-blocking prompt sending
- Timeout-based response reading
- Graceful shutdown with fallback to kill

#### Day 3: Unit Tests (4 hours)
**File**: \	ests/aim/test_process_pool.py\

**Tests** (6 test functions):
- test_pool_initialization
- test_send_prompt_success
- test_send_prompt_dead_process
- test_read_response_timeout
- test_shutdown_graceful
- test_get_status

#### Day 4: Integration Test with Real Aider (4 hours)
**File**: \	ests/aim/integration/test_aider_pool.py\

**Test**: Spawn 3 actual aider processes, send commands, verify responses

#### Day 5: Error Handling & Docs (4 hours)
**Additions**:
- \check_health()\ method
- \estart_instance()\ method
- \im/docs/PROCESS_POOL_API.md\ - API docs
- \xamples/aim_pool_usage.py\ - Usage example

### Week 1 Exit Criteria
- ✅ ToolProcessPool spawns 3-5 instances in <2s
- ✅ Send/receive latency <100ms
- ✅ 6/6 unit tests pass
- ✅ Integration test works with real aider
- ✅ API documentation complete

---

## 🏗️ WEEK 2: ClusterManager API (5 days)

### Goal
High-level cluster management with intelligent routing.

### Deliverables

#### Day 6: Design (4 hours)
**Files**:
- \phase4_routing/modules/aim_tools/src/aim/cluster_manager.py\ - Manager class
- \phase4_routing/modules/aim_tools/src/aim/routing.py\ - Routing strategies
- \schema/cluster_config.schema.json\ - Configuration schema

**Classes**:
\\\python
class RoutingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    STICKY = "sticky"

class ClusterManager:
    def __init__(self, tool_id: str, count: int, routing: RoutingStrategy)
    def send(self, prompt: str) -> int  # Auto-routes
    def send_to(self, instance_idx: int, prompt: str) -> bool  # Specific target
    def read_any(self, timeout: float) -> Optional[str]
    def shutdown()

def launch_cluster(tool_id: str, count: int = 3, routing: str = "round_robin") -> ClusterManager
\\\

#### Day 7-8: Implementation & Testing (12 hours)
- Complete ClusterManager implementation
- Routing strategy logic (round-robin, least-busy, sticky)
- Health monitoring and auto-restart
- Unit tests: \	ests/aim/test_cluster_manager.py\ (8 tests)

#### Day 9: Multi-Tool Support (6 hours)
- Test with aider, codex, claude-cli
- Document tool-specific stdin/stdout protocols
- Tool adapters for different response formats

#### Day 10: Examples & Benchmarks (6 hours)
**Files**:
- \xamples/parallel_refactor.py\ - 3 aider instances refactoring in parallel
- \xamples/multi_agent_review.py\ - Distributed code review
- \xamples/distributed_test_gen.py\ - Parallel test generation
- \im/docs/PERFORMANCE.md\ - Benchmarks

### Week 2 Exit Criteria
- ✅ \launch_cluster()\ API working
- ✅ Round-robin distributes evenly (±10%)
- ✅ Cluster handles 50+ prompts/min across 5 instances
- ✅ Multi-tool support (aider, codex, jules)
- ✅ Example applications functional

---

## 🏗️ WEEK 3: Engine Integration (5 days)

### Goal
Integrate pool-based execution into orchestrator for automatic parallelism.

### Deliverables

#### Day 11: Adapter Interface Extension (4 hours)
**File**: \core/engine/adapters/adapter_interface.py\

**Additions**:
\\\python
class AdapterInterface(Protocol):
    def supports_pool_mode(self) -> bool
    def run_job_pooled(self, job: Dict, pool: ToolProcessPool) -> JobResult
\\\

#### Day 12-13: Pooled Adapters (12 hours)
**File**: \core/engine/adapters/aider_pooled_adapter.py\

**Implementation**:
- Job → aider command translation
- Async job submission to pool
- Result collection from pool stdout
- Error handling and retry

**Tests**: \	ests/engine/adapters/test_aider_pooled.py\

#### Day 14: Orchestrator Integration (6 hours)
**File**: \core/engine/orchestrator.py\

**Changes**:
\\\python
class Orchestrator:
    def __init__(self):
        self._tool_pools: Dict[str, ClusterManager] = {}

    def execute_jobs(self, jobs: List[Dict]) -> List[JobResult]:
        # Group jobs by tool
        # Use pool if adapter.supports_pool_mode() and len(jobs) > 1
        # Fall back to one-shot for single jobs
\\\

#### Day 15: E2E Testing & Documentation (6 hours)
**Files**:
- \	ests/integration/test_pooled_pipeline.py\ - Full pipeline test
- \docs/MIGRATION_POOLED_ADAPTERS.md\ - Migration guide
- Performance report (expect 2-5x speedup)

### Week 3 Exit Criteria
- ✅ Orchestrator auto-detects when to use pools
- ✅ 3 parallel jobs complete in 40s (vs 120s sequential)
- ✅ Zero regressions on existing one-shot jobs
- ✅ Migration documentation complete

---

## 🎨 FEATURE 2: REAL-TIME GUI DASHBOARD

### Current State
**Exists**: \gui/src/\ with partial TUI implementation
**Missing**: Real-time monitoring, live event streaming

### What's Needed (1 Week Effort)

#### Components
1. **Event Stream Viewer** (2 days)
   - Subscribe to event bus
   - Display TASK_STARTED, TASK_COMPLETED, TASK_FAILED events in real-time
   - Color-coded status (green=success, red=failed, yellow=running)

2. **DAG Visualizer** (2 days)
   - Render task DAG with status overlay
   - Show dependencies and execution order
   - Highlight current running tasks

3. **Metrics Dashboard** (1 day)
   - Tasks completed/failed/pending
   - Average task duration
   - Resource usage (CPU/RAM)
   - Cost tracking (API calls, tokens)

4. **Log Viewer** (1 day)
   - Tail task stdout/stderr
   - Search and filter logs
   - Export logs to file

5. **Polish & Testing** (1 day)
   - Keyboard shortcuts
   - Error handling
   - Documentation

### Technology Stack Options
**Option A**: Rich TUI (Python) - Already started in \gui/src/tui_app/\
**Option B**: Web dashboard (FastAPI + React) - More powerful but more work
**Option C**: Hybrid - TUI for dev, web for CI/CD

### Priority Assessment
**Verdict**: **Nice-to-have, not critical**
- Current CLI + event logs work fine for dev
- Focus on Multi-CLI first (bigger ROI)
- Consider GUI after parallelism is stable

---

## 📊 COMPARISON: What to Build First?

| Feature | Effort | Impact | ROI | Priority |
|---------|--------|--------|-----|----------|
| **Multi-CLI Parallelism** | 3 weeks | 3-5x speedup | Very High | ⭐⭐⭐⭐⭐ |
| **Real-Time GUI** | 1 week | Better visibility | Medium | ⭐⭐⭐ |

**Recommendation**: Build Multi-CLI parallelism first (Weeks 1-3), then evaluate if GUI is still needed.

---

## 🚀 GETTING STARTED: WEEK 1 DAY 1

### Step 1: Create Feature Branch (5 min)
\\\ash
git checkout -b feature/multi-instance-cli-control
git push -u origin feature/multi-instance-cli-control
\\\

### Step 2: Create Interface Stub (30 min)
**File**: \phase4_routing/modules/aim_tools/src/aim/pool_interface.py\

\\\python
from dataclasses import dataclass
from typing import Protocol, Optional, List, Dict, Any

@dataclass
class ProcessInstance:
    \"\"\"Single tool process instance.\"\"\"
    index: int
    tool_id: str
    process: subprocess.Popen
    stdout_queue: queue.Queue
    stderr_queue: queue.Queue
    alive: bool = True

class ToolProcessPoolInterface(Protocol):
    \"\"\"Interface for managing multiple tool instances.\"\"\"

    def send_prompt(self, instance_idx: int, prompt: str) -> bool:
        \"\"\"Send prompt to specific instance.\"\"\"
        ...

    def read_response(self, instance_idx: int, timeout: float) -> Optional[str]:
        \"\"\"Read response from instance.\"\"\"
        ...
\\\

### Step 3: Create Test Fixtures (1 hour)
**File**: \	ests/aim/fixtures/mock_aider.py\

\\\python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_registry():
    return {
        "tools": {
            "aider": {
                "detectCommands": [["aider", "--yes-always"]],
                "capabilities": ["code_generation"]
            }
        }
    }

@pytest.fixture
def mock_process():
    proc = MagicMock()
    proc.stdin = MagicMock()
    proc.stdout = MagicMock()
    proc.stderr = MagicMock()
    proc.poll.return_value = None  # Still running
    return proc
\\\

### Step 4: Create Schema (30 min)
**File**: \schema/pool_instance.schema.json\

\\\json
{
  "\": "http://json-schema.org/draft-07/schema#",
  "title": "ProcessInstance",
  "type": "object",
  "required": ["index", "tool_id", "alive"],
  "properties": {
    "index": {"type": "integer", "minimum": 0},
    "tool_id": {"type": "string"},
    "alive": {"type": "boolean"},
    "return_code": {"type": ["integer", "null"]}
  }
}
\\\

### Step 5: Validation (15 min)
\\\ash
# Verify interface loads
python -c "from aim.pool_interface import ToolProcessPoolInterface; print(ToolProcessPoolInterface.__doc__)"

# Verify schema valid
python -c "import json; s = json.load(open('schema/pool_instance.schema.json')); print('Schema valid')"

# Verify fixtures load
pytest tests/aim/fixtures/ --collect-only
\\\

**Day 1 Complete**: Contracts defined, ready for implementation

---

## 📚 REFERENCE DOCUMENTS

### Must-Read Before Starting
1. **\core/MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md\** - Complete 3-week plan
2. **\docs/DOC_reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md\** - EXEC-002 pattern
3. **\phase1_planning/modules/spec_parser/docs/specifications/specs/UET_CLI_TOOL_EXECUTION_SPEC.md\** - CLI execution framework

### Supporting Specs
4. **\phase1_planning/modules/spec_parser/docs/specifications/specs/MULTI_CLI_WORKTREES_EXECUTION_SPEC.md\**
5. **\phase1_planning/modules/spec_parser/docs/specifications/specs/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md\**
6. **\docs/DOC_operations/PARALLEL_EXECUTION_STRATEGY.md\**

### Example Code
7. **\phase1_planning/modules/workstream_planner/docs/plans/workstreams/examples/02_parallel_execution.json\**

---

## 🎯 SUCCESS METRICS

### Performance Targets
| Metric | Target | Validation |
|--------|--------|------------|
| **Process Spawn Time** | <2s for 5 instances | \	ime python -c "from aim.bridge import ToolProcessPool; ToolProcessPool('aider', 5)"\ |
| **Prompt Latency** | <100ms per send | Benchmark in \	ests/performance/\ |
| **Throughput** | 50+ prompts/min | Stress test with 100 prompts across 5 instances |
| **Parallel Speedup** | 3-5x vs sequential | 3 parallel aider jobs: 40s vs 120s |
| **Resource Usage** | <500MB RAM for 5 instances | Monitor with psutil |

### Quality Gates
- ✅ Zero test failures after each week
- ✅ 100% test coverage on new code
- ✅ All specs validated against JSON schemas
- ✅ Performance benchmarks meet targets
- ✅ No regressions on existing functionality

---

## 💡 DECISION: WHAT TO BUILD?

### Option A: Full 3-Week Multi-CLI Implementation
**Pros**:
- Complete parallelism solution
- 3-5x speedup immediately
- Unblocks advanced patterns (worktree parallelism)

**Cons**:
- 3 weeks of focused work
- Requires testing across multiple tools

### Option B: Week 1 Only (ToolProcessPool)
**Pros**:
- 1 week effort, useful immediately
- Can manually use pool in scripts
- Proves concept before full commitment

**Cons**:
- Not integrated into orchestrator
- Manual cluster management

### Option C: Build GUI First
**Pros**:
- Better visibility into current system
- Easier debugging

**Cons**:
- Lower ROI than parallelism
- Current CLI logs work fine

---

## ✅ RECOMMENDED PATH

### Phase 1 (This Week): Build ToolProcessPool
- Follow Week 1 plan exactly
- Deliverable: Working pool, manual usage
- Decision point: Continue to Week 2?

### Phase 2 (Next Week): Evaluate Progress
If Week 1 went well:
- Continue to Week 2 (ClusterManager)
- Otherwise: Use manual pools, defer automation

### Phase 3 (Week 3): Full Integration
- Orchestrator auto-parallelism
- Production deployment

### Phase 4 (Optional): GUI Dashboard
- Only if time permits
- Only if Multi-CLI is stable

---

**NEXT ACTION**:
Choose between:
1. ✅ Start Week 1 Day 1 (create feature branch + interfaces)
2. ✅ Review specs in detail first (1-2 hours reading)
3. ✅ Build minimal prototype (1-2 days spike)

Which path do you prefer?

---

**END OF EXPLORATION SUMMARY**
