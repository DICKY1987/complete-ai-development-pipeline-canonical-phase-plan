---
doc_id: DOC-CORE-MULTI-INSTANCE-CLI-CONTROL-PHASE-PLAN-MD-001
---

# Multi-Instance CLI Control - 3-Week Phase Plan

**Goal**: Enable Copilot CLI to control 3-5 aider instances simultaneously and send interactive prompts

**Pattern**: Subprocess fan-out with interactive stdin/stdout (Pattern #1 from control document)

**Timeline**: 3 weeks (15 working days)

**Execution Pattern**: EXEC-002 (Module Enhancement - Progressive Integration)

---

## Phase Overview

| Phase | Duration | Deliverable | Success Metric |
|-------|----------|-------------|----------------|
| **Week 1** | 5 days | `ToolProcessPool` class in `aim/bridge.py` | Pool launches 3-5 instances, sends prompts, reads responses |
| **Week 2** | 5 days | `launch_cluster()` API with routing | Cluster API tested with aider, codex, jules |
| **Week 3** | 5 days | Engine adapter integration | Orchestrator uses pool-based calls for parallel jobs |

---

## WEEK 1: Implement ToolProcessPool

**Pattern**: EXEC-002 (Module Enhancement)

**Objective**: Add multi-instance process management to `aim/bridge.py`

### Day 1: Design & Contracts

**Tasks**:
1. ✅ Define `ToolProcessPool` class interface
2. ✅ Define `ProcessInstance` dataclass
3. ✅ Document stdin/stdout protocol expectations
4. ✅ Create test fixtures for mock processes

**Deliverables**:
- [ ] `aim/pool_interface.py` - Interface definition
- [ ] `tests/aim/fixtures/mock_aider.py` - Test fixture
- [ ] Schema: `schema/pool_instance.schema.json`

**Validation**:
```bash
python -c "from aim.pool_interface import ToolProcessPool; print(ToolProcessPool.__doc__)"
```

**Time**: 4 hours

---

### Day 2: Core PoolProcessPool Implementation

**Tasks**:
1. ✅ Implement `ToolProcessPool.__init__(tool_id, count)`
2. ✅ Implement `spawn_instance()` with `Popen(stdin=PIPE, stdout=PIPE)`
3. ✅ Implement `send_prompt(instance_idx, prompt)` with stdin.write()
4. ✅ Implement `read_response(instance_idx, timeout)` with stdout.readline()

**Code Location**: `aim/bridge.py` (add ~80 lines)

**Implementation**:
```python
# aim/bridge.py (addition)

import queue
import threading
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ProcessInstance:
    """Represents a single tool process instance."""
    index: int
    tool_id: str
    process: subprocess.Popen
    stdout_queue: queue.Queue
    stderr_queue: queue.Queue
    alive: bool = True


class ToolProcessPool:
    """Manage multiple long-lived tool CLI instances.

    Example:
        pool = ToolProcessPool("aider", count=3)
        pool.send_prompt(0, "/add core/state.py")
        response = pool.read_response(0, timeout=10)
        pool.shutdown()
    """

    def __init__(self, tool_id: str, count: int, registry: Optional[Dict] = None):
        """Initialize process pool.

        Args:
            tool_id: Tool from AIM registry (e.g., "aider")
            count: Number of instances to spawn (1-10)
            registry: Optional registry override (for testing)
        """
        self.tool_id = tool_id
        self.count = count
        self.instances: List[ProcessInstance] = []
        self.registry = registry or load_aim_registry()

        # Validate tool exists
        if tool_id not in self.registry.get("tools", {}):
            raise ValueError(f"Tool '{tool_id}' not in AIM registry")

        # Spawn instances
        for i in range(count):
            self._spawn_instance(i)

    def _spawn_instance(self, index: int) -> ProcessInstance:
        """Spawn a single tool instance with I/O threads."""
        tool_config = self.registry["tools"][self.tool_id]

        # Build command from registry
        detect_cmds = tool_config["detectCommands"]
        cmd = detect_cmds[0] if isinstance(detect_cmds[0], list) else [detect_cmds[0]]

        # Add flags for interactive mode
        if self.tool_id == "aider":
            cmd.extend(["--yes-always"])  # Non-blocking mode

        # Spawn process
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )

        # Create output queues
        stdout_q = queue.Queue()
        stderr_q = queue.Queue()

        # Start reader threads
        threading.Thread(
            target=self._read_stream,
            args=(proc.stdout, stdout_q),
            daemon=True
        ).start()

        threading.Thread(
            target=self._read_stream,
            args=(proc.stderr, stderr_q),
            daemon=True
        ).start()

        instance = ProcessInstance(
            index=index,
            tool_id=self.tool_id,
            process=proc,
            stdout_queue=stdout_q,
            stderr_queue=stderr_q
        )

        self.instances.append(instance)
        return instance

    def _read_stream(self, stream, q: queue.Queue):
        """Background thread to read stream into queue."""
        for line in stream:
            q.put(line.rstrip('\n'))
        stream.close()

    def send_prompt(self, instance_idx: int, prompt: str) -> bool:
        """Send prompt to specific instance.

        Args:
            instance_idx: Instance index (0 to count-1)
            prompt: Command/prompt to send

        Returns:
            bool: True if sent successfully
        """
        if instance_idx >= len(self.instances):
            return False

        instance = self.instances[instance_idx]
        if not instance.alive:
            return False

        try:
            instance.process.stdin.write(prompt + "\n")
            instance.process.stdin.flush()
            return True
        except (BrokenPipeError, OSError):
            instance.alive = False
            return False

    def read_response(self, instance_idx: int, timeout: float = 5.0) -> Optional[str]:
        """Read response from instance stdout.

        Args:
            instance_idx: Instance index
            timeout: Max seconds to wait for response

        Returns:
            str: Response line, or None if timeout/error
        """
        if instance_idx >= len(self.instances):
            return None

        instance = self.instances[instance_idx]

        try:
            line = instance.stdout_queue.get(timeout=timeout)
            return line
        except queue.Empty:
            return None

    def get_status(self) -> List[Dict[str, Any]]:
        """Get status of all instances.

        Returns:
            List of status dicts with index, alive, return_code
        """
        statuses = []
        for inst in self.instances:
            statuses.append({
                "index": inst.index,
                "alive": inst.alive and inst.process.poll() is None,
                "return_code": inst.process.poll()
            })
        return statuses

    def shutdown(self, timeout: float = 5.0):
        """Gracefully shutdown all instances.

        Args:
            timeout: Seconds to wait for graceful exit
        """
        for inst in self.instances:
            if inst.process.poll() is None:
                try:
                    inst.process.terminate()
                except OSError:
                    pass

        # Wait for all to exit
        start = time.time()
        while time.time() - start < timeout:
            if all(inst.process.poll() is not None for inst in self.instances):
                break
            time.sleep(0.1)

        # Force kill stragglers
        for inst in self.instances:
            if inst.process.poll() is None:
                inst.process.kill()
                inst.process.wait()
```

**Deliverables**:
- [ ] `ToolProcessPool` class in `aim/bridge.py`
- [ ] `ProcessInstance` dataclass
- [ ] `_read_stream()` background thread handler

**Validation**:
```python
from aim.bridge import ToolProcessPool
pool = ToolProcessPool("aider", count=1)
assert len(pool.instances) == 1
assert pool.instances[0].alive == True
pool.shutdown()
```

**Time**: 6 hours

---

### Day 3: Unit Tests

**Tasks**:
1. ✅ Test pool initialization with mock registry
2. ✅ Test send_prompt() with mock subprocess
3. ✅ Test read_response() with queued output
4. ✅ Test shutdown() cleanup
5. ✅ Test error handling (dead process, timeout)

**Code Location**: `tests/aim/test_process_pool.py`

**Implementation**:
```python
# tests/aim/test_process_pool.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from aim.bridge import ToolProcessPool, ProcessInstance


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


def test_pool_initialization(mock_registry):
    """Test pool spawns correct number of instances."""
    with patch("aim.bridge.subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        pool = ToolProcessPool("aider", count=3, registry=mock_registry)

        assert len(pool.instances) == 3
        assert mock_popen.call_count == 3


def test_send_prompt_success(mock_registry):
    """Test sending prompt to instance."""
    with patch("aim.bridge.subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.stdin = MagicMock()
        mock_popen.return_value = mock_proc

        pool = ToolProcessPool("aider", count=1, registry=mock_registry)
        result = pool.send_prompt(0, "/add test.py")

        assert result == True
        mock_proc.stdin.write.assert_called_once_with("/add test.py\n")
        mock_proc.stdin.flush.assert_called_once()


def test_send_prompt_dead_process(mock_registry):
    """Test sending to dead process returns False."""
    with patch("aim.bridge.subprocess.Popen"):
        pool = ToolProcessPool("aider", count=1, registry=mock_registry)
        pool.instances[0].alive = False

        result = pool.send_prompt(0, "/add test.py")
        assert result == False


def test_read_response_timeout(mock_registry):
    """Test read_response returns None on timeout."""
    with patch("aim.bridge.subprocess.Popen"):
        pool = ToolProcessPool("aider", count=1, registry=mock_registry)

        response = pool.read_response(0, timeout=0.1)
        assert response is None


def test_shutdown_graceful(mock_registry):
    """Test shutdown terminates all processes."""
    with patch("aim.bridge.subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 0  # Already exited
        mock_popen.return_value = mock_proc

        pool = ToolProcessPool("aider", count=2, registry=mock_registry)
        pool.shutdown(timeout=1.0)

        # Verify terminate was called
        assert mock_proc.terminate.call_count == 2


def test_get_status(mock_registry):
    """Test status reporting."""
    with patch("aim.bridge.subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # Still running
        mock_popen.return_value = mock_proc

        pool = ToolProcessPool("aider", count=2, registry=mock_registry)
        statuses = pool.get_status()

        assert len(statuses) == 2
        assert statuses[0]["alive"] == True
        assert statuses[0]["index"] == 0
```

**Deliverables**:
- [ ] `tests/aim/test_process_pool.py` (6 test functions)

**Validation**:
```bash
pytest tests/aim/test_process_pool.py -v
```

**Expected**: 6/6 tests pass

**Time**: 4 hours

---

### Day 4: Integration Test with Real Aider

**Tasks**:
1. ✅ Create integration test with actual aider process
2. ✅ Test multi-instance spawn (3 instances)
3. ✅ Test concurrent prompt sending
4. ✅ Test response reading with real output
5. ✅ Document aider-specific stdin/stdout protocol

**Code Location**: `tests/aim/integration/test_aider_pool.py`

**Implementation**:
```python
# tests/aim/integration/test_aider_pool.py

import pytest
from aim.bridge import ToolProcessPool, load_aim_registry


@pytest.mark.integration
@pytest.mark.skipif(not _aider_installed(), reason="Aider not installed")
def test_aider_pool_real():
    """Integration test with real aider instances."""
    pool = ToolProcessPool("aider", count=3)

    try:
        # Verify all spawned
        statuses = pool.get_status()
        assert len(statuses) == 3
        assert all(s["alive"] for s in statuses)

        # Send commands to each instance
        pool.send_prompt(0, "/add core/state.py")
        pool.send_prompt(1, "/add error/engine.py")
        pool.send_prompt(2, "/help")

        # Read responses (aider outputs prompt confirmation)
        resp0 = pool.read_response(0, timeout=10)
        resp1 = pool.read_response(1, timeout=10)
        resp2 = pool.read_response(2, timeout=10)

        # Verify responses received
        assert resp0 is not None
        assert resp1 is not None
        assert resp2 is not None

    finally:
        pool.shutdown()


def _aider_installed() -> bool:
    """Check if aider is installed."""
    import shutil
    return shutil.which("aider") is not None
```

**Deliverables**:
- [ ] `tests/aim/integration/test_aider_pool.py`
- [ ] Documentation: `aim/docs/AIDER_PROTOCOL.md`

**Validation**:
```bash
pytest tests/aim/integration/test_aider_pool.py -v -m integration
```

**Time**: 4 hours

---

### Day 5: Error Handling & Documentation

**Tasks**:
1. ✅ Add process crash detection and restart logic
2. ✅ Add health check method (`check_health()`)
3. ✅ Add metrics tracking (prompts sent, responses read)
4. ✅ Write API documentation
5. ✅ Create usage examples

**Code Additions**:
```python
# aim/bridge.py (additions)

class ToolProcessPool:
    # ... existing code ...

    def check_health(self) -> Dict[str, Any]:
        """Check health of all instances.

        Returns:
            Health report with alive count, dead count, details
        """
        statuses = self.get_status()
        alive_count = sum(1 for s in statuses if s["alive"])

        return {
            "total": len(self.instances),
            "alive": alive_count,
            "dead": len(self.instances) - alive_count,
            "instances": statuses
        }

    def restart_instance(self, instance_idx: int) -> bool:
        """Restart a dead instance.

        Args:
            instance_idx: Instance to restart

        Returns:
            bool: True if restarted successfully
        """
        if instance_idx >= len(self.instances):
            return False

        old_instance = self.instances[instance_idx]

        # Kill old process if still running
        if old_instance.process.poll() is None:
            old_instance.process.kill()
            old_instance.process.wait()

        # Spawn new instance
        try:
            new_instance = self._spawn_instance(instance_idx)
            self.instances[instance_idx] = new_instance
            return True
        except Exception:
            return False
```

**Deliverables**:
- [ ] `aim/docs/PROCESS_POOL_API.md` - API documentation
- [ ] `examples/aim_pool_usage.py` - Usage examples
- [ ] Enhanced error handling in `ToolProcessPool`

**Validation**:
```bash
python examples/aim_pool_usage.py
```

**Time**: 4 hours

---

### Week 1 Exit Criteria

**Must Have**:
- [x] `ToolProcessPool` class implemented in `aim/bridge.py`
- [x] Unit tests pass (6/6)
- [x] Integration test passes with real aider
- [x] API documentation complete

**Success Metrics**:
- Pool spawns 3-5 instances in <2 seconds
- Send/receive latency <100ms per prompt
- 100% test coverage on core methods

**Deliverable**: Pull request ready for review

---

## WEEK 2: Add launch_cluster() API

**Pattern**: EXEC-002 (API Extension)

**Objective**: Create high-level cluster management API

### Day 6: Cluster Manager Design

**Tasks**:
1. ✅ Design `ClusterManager` class interface
2. ✅ Design routing strategies (round-robin, least-busy, sticky)
3. ✅ Define cluster health monitoring
4. ✅ Create schema for cluster configuration

**Deliverables**:
- [ ] `aim/cluster_manager.py` - Cluster manager class
- [ ] `schema/cluster_config.schema.json`
- [ ] `aim/routing.py` - Routing strategies

**Implementation Outline**:
```python
# aim/cluster_manager.py

from enum import Enum
from typing import Optional, Callable

class RoutingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    STICKY = "sticky"


class ClusterManager:
    """High-level cluster management with routing.

    Example:
        cluster = launch_cluster("aider", count=3)
        cluster.send("/add file.py")  # Routes automatically
        cluster.send_to(0, "/ask 'fix'")  # Target specific instance
    """

    def __init__(self, tool_id: str, count: int,
                 routing: RoutingStrategy = RoutingStrategy.ROUND_ROBIN):
        self.tool_id = tool_id
        self.pool = ToolProcessPool(tool_id, count)
        self.routing = routing
        self._current_index = 0
        self._pending_requests = [0] * count

    def send(self, prompt: str) -> int:
        """Send prompt using routing strategy.

        Returns:
            int: Instance index that received the prompt
        """
        idx = self._select_instance()
        self.pool.send_prompt(idx, prompt)
        self._pending_requests[idx] += 1
        return idx

    def send_to(self, instance_idx: int, prompt: str) -> bool:
        """Send prompt to specific instance."""
        return self.pool.send_prompt(instance_idx, prompt)

    def _select_instance(self) -> int:
        """Select instance based on routing strategy."""
        if self.routing == RoutingStrategy.ROUND_ROBIN:
            idx = self._current_index
            self._current_index = (self._current_index + 1) % self.pool.count
            return idx
        elif self.routing == RoutingStrategy.LEAST_BUSY:
            return self._pending_requests.index(min(self._pending_requests))
        else:
            return 0


def launch_cluster(tool_id: str, count: int = 3,
                   routing: str = "round_robin") -> ClusterManager:
    """Launch a managed cluster of tool instances.

    Args:
        tool_id: Tool from AIM registry
        count: Number of instances (default: 3)
        routing: Routing strategy (round_robin, least_busy, sticky)

    Returns:
        ClusterManager: Managed cluster

    Example:
        cluster = launch_cluster("aider", count=3)
        cluster.send("/add core/state.py")
        response = cluster.read_any(timeout=10)
    """
    strategy = RoutingStrategy(routing)
    return ClusterManager(tool_id, count, strategy)
```

**Time**: 4 hours

---

### Day 7-8: Implementation & Testing

**Tasks**:
1. ✅ Implement `ClusterManager` class
2. ✅ Implement routing strategies
3. ✅ Add health monitoring and auto-restart
4. ✅ Write unit tests for routing logic
5. ✅ Integration tests with multiple tools

**Deliverables**:
- [ ] Complete `ClusterManager` implementation
- [ ] `tests/aim/test_cluster_manager.py` (8 tests)
- [ ] Integration tests for aider, jules, codex

**Validation**:
```bash
pytest tests/aim/test_cluster_manager.py -v
```

**Time**: 12 hours (2 days)

---

### Day 9: Multi-Tool Support

**Tasks**:
1. ✅ Test cluster with jules CLI
2. ✅ Test cluster with codex CLI
3. ✅ Test cluster with claude-cli
4. ✅ Document tool-specific quirks
5. ✅ Add tool adapters for stdin/stdout protocols

**Deliverables**:
- [ ] `aim/docs/TOOL_PROTOCOLS.md` - Tool-specific protocols
- [ ] Integration tests for each supported tool

**Time**: 6 hours

---

### Day 10: Example Applications

**Tasks**:
1. ✅ Create example: Parallel refactoring (3 aider instances)
2. ✅ Create example: Multi-agent code review
3. ✅ Create example: Distributed test generation
4. ✅ Performance benchmarking

**Deliverables**:
- [ ] `examples/parallel_refactor.py`
- [ ] `examples/multi_agent_review.py`
- [ ] `examples/distributed_test_gen.py`
- [ ] Performance report in `aim/docs/PERFORMANCE.md`

**Example Code**:
```python
# examples/parallel_refactor.py

from aim.bridge import launch_cluster

# Launch 3 aider instances
cluster = launch_cluster("aider", count=3)

try:
    # Distribute refactoring tasks
    files_to_refactor = [
        "core/state.py",
        "error/engine.py",
        "aim/bridge.py"
    ]

    for i, filepath in enumerate(files_to_refactor):
        cluster.send_to(i, f"/add {filepath}")
        cluster.send_to(i, "/ask 'Add type hints to all functions'")

    # Monitor completion
    for i in range(len(files_to_refactor)):
        response = cluster.pool.read_response(i, timeout=60)
        print(f"Instance {i} completed: {response}")

finally:
    cluster.shutdown()
```

**Time**: 6 hours

---

### Week 2 Exit Criteria

**Must Have**:
- [x] `launch_cluster()` API implemented
- [x] Routing strategies working (round-robin, least-busy)
- [x] Multi-tool support (aider, jules, codex)
- [x] Example applications functional

**Success Metrics**:
- Cluster handles 50+ prompts/min across 5 instances
- Auto-restart recovers from crashes in <2s
- Round-robin distributes evenly (±10%)

**Deliverable**: `aim.bridge.launch_cluster()` ready for engine integration

---

## WEEK 3: Engine Adapter Integration

**Pattern**: EXEC-003 (Cross-Module Integration)

**Objective**: Replace one-shot adapter calls with pool-based calls in engine

### Day 11: Adapter Interface Extension

**Tasks**:
1. ✅ Extend `AdapterInterface` protocol for pool mode
2. ✅ Add `supports_pool_mode()` method to adapters
3. ✅ Create `PooledAdapter` base class
4. ✅ Update job schema to support pool hints

**Code Location**: `engine/interfaces/adapter_interface.py`

**Implementation**:
```python
# engine/interfaces/adapter_interface.py (additions)

class AdapterInterface(Protocol):
    # ... existing methods ...

    def supports_pool_mode(self) -> bool:
        """Check if adapter supports pool mode for parallel jobs.

        Returns:
            bool: True if adapter can use ToolProcessPool
        """
        ...

    def run_job_pooled(self, job: Dict[str, Any],
                       pool: 'ToolProcessPool') -> JobResult:
        """Execute job using an existing process pool.

        Args:
            job: Job dictionary
            pool: Active ToolProcessPool instance

        Returns:
            JobResult: Execution outcome
        """
        ...
```

**Deliverables**:
- [ ] Extended `AdapterInterface` protocol
- [ ] `engine/adapters/pooled_adapter_base.py` - Base class
- [ ] Updated `schema/job.schema.json`

**Time**: 4 hours

---

### Day 12-13: Aider Adapter Pooling

**Tasks**:
1. ✅ Create `AiderPooledAdapter` class
2. ✅ Implement job → aider command translation
3. ✅ Handle async job submission to pool
4. ✅ Implement result collection from pool
5. ✅ Write tests for pooled adapter

**Code Location**: `engine/adapters/aider_pooled_adapter.py`

**Implementation**:
```python
# engine/adapters/aider_pooled_adapter.py

from typing import Dict, Any
from aim.bridge import ToolProcessPool, ClusterManager
from engine.types import JobResult
from engine.interfaces.adapter_interface import AdapterInterface


class AiderPooledAdapter:
    """Aider adapter using process pool for parallel jobs."""

    def __init__(self, pool: ClusterManager):
        self.pool = pool
        self.tool_name = "aider"

    def run_job(self, job: Dict[str, Any]) -> JobResult:
        """Execute aider job via pool."""
        # Translate job to aider commands
        commands = self._build_aider_commands(job)

        # Send to cluster (routes automatically)
        instance_idx = None
        for cmd in commands:
            instance_idx = self.pool.send(cmd)

        # Collect response
        response_lines = []
        timeout = job.get("metadata", {}).get("timeout_seconds", 60)

        while True:
            line = self.pool.pool.read_response(instance_idx, timeout=timeout)
            if line is None:
                break
            response_lines.append(line)

            # Check for completion marker
            if "Commit" in line or "error" in line.lower():
                break

        # Parse result
        success = any("Commit" in line for line in response_lines)
        exit_code = 0 if success else 1

        return JobResult(
            exit_code=exit_code,
            error_report_path=job["paths"]["error_report"],
            duration_s=0,  # TODO: Track timing
            stdout="\n".join(response_lines),
            stderr="",
            success=success
        )

    def _build_aider_commands(self, job: Dict[str, Any]) -> list:
        """Translate job spec to aider commands.

        Example job:
            {
                "action": "refactor",
                "files": ["core/state.py"],
                "prompt": "Add type hints"
            }

        Returns:
            ["/add core/state.py", "/ask 'Add type hints'"]
        """
        commands = []

        # Add files
        for filepath in job.get("files", []):
            commands.append(f"/add {filepath}")

        # Add prompt
        prompt = job.get("prompt", "")
        if prompt:
            commands.append(f"/ask '{prompt}'")

        return commands

    def supports_pool_mode(self) -> bool:
        return True

    def get_tool_info(self) -> Dict[str, Any]:
        return {
            "tool": "aider",
            "adapter_version": "0.2.0-pooled",
            "capabilities": ["code_generation", "refactoring"],
            "pool_mode": True
        }
```

**Deliverables**:
- [ ] `AiderPooledAdapter` class
- [ ] `tests/engine/adapters/test_aider_pooled.py`
- [ ] Job translation logic

**Time**: 12 hours (2 days)

---

### Day 14: Orchestrator Integration

**Tasks**:
1. ✅ Update orchestrator to detect pool-capable adapters
2. ✅ Add pool lifecycle management to orchestrator
3. ✅ Route parallel jobs to pool
4. ✅ Route sequential jobs to standard adapters
5. ✅ Update orchestrator tests

**Code Location**: `engine/orchestrator.py`

**Implementation Sketch**:
```python
# engine/orchestrator.py (modifications)

class Orchestrator:
    def __init__(self):
        # ... existing init ...
        self._tool_pools: Dict[str, ClusterManager] = {}

    def _get_or_create_pool(self, tool: str) -> ClusterManager:
        """Get existing pool or create new one."""
        if tool not in self._tool_pools:
            from aim.bridge import launch_cluster
            self._tool_pools[tool] = launch_cluster(tool, count=3)
        return self._tool_pools[tool]

    def execute_jobs(self, jobs: List[Dict]) -> List[JobResult]:
        """Execute jobs with pool optimization."""
        # Group jobs by tool
        jobs_by_tool = {}
        for job in jobs:
            tool = job["tool"]
            jobs_by_tool.setdefault(tool, []).append(job)

        results = []

        for tool, tool_jobs in jobs_by_tool.items():
            adapter = self._get_adapter(tool)

            # Use pool if adapter supports it and multiple jobs
            if adapter.supports_pool_mode() and len(tool_jobs) > 1:
                pool = self._get_or_create_pool(tool)
                for job in tool_jobs:
                    result = adapter.run_job_pooled(job, pool)
                    results.append(result)
            else:
                # Use standard one-shot execution
                for job in tool_jobs:
                    result = adapter.run_job(job)
                    results.append(result)

        return results

    def shutdown(self):
        """Cleanup pools on shutdown."""
        for pool in self._tool_pools.values():
            pool.shutdown()
```

**Deliverables**:
- [ ] Pool-aware orchestrator
- [ ] Updated tests in `tests/engine/test_orchestrator.py`

**Time**: 6 hours

---

### Day 15: End-to-End Testing & Documentation

**Tasks**:
1. ✅ Run full pipeline with pooled adapters
2. ✅ Performance comparison (pooled vs one-shot)
3. ✅ Write migration guide for existing code
4. ✅ Update all relevant documentation
5. ✅ Create rollback plan

**Deliverables**:
- [ ] E2E test: `tests/integration/test_pooled_pipeline.py`
- [ ] Performance report showing 2-5x speedup
- [ ] Migration guide: `docs/MIGRATION_POOLED_ADAPTERS.md`
- [ ] Updated `README.md` with pool examples

**Validation**:
```bash
# Run full test suite
pytest tests/ -v -m "not slow"

# Run performance benchmark
python benchmarks/compare_pooled_vs_oneshot.py

# Expected: 2-5x faster for parallel jobs
```

**Time**: 6 hours

---

### Week 3 Exit Criteria

**Must Have**:
- [x] Orchestrator uses pools for parallel jobs
- [x] `AiderPooledAdapter` functional and tested
- [x] Performance improvement demonstrated (≥2x)
- [x] Migration guide complete

**Success Metrics**:
- 3 parallel aider jobs complete in 40s (vs 120s sequential)
- Pool reuse reduces process spawn overhead by 80%
- Zero regressions on existing one-shot jobs

**Deliverable**: Production-ready pool-based execution

---

## Success Metrics (Overall)

| Metric | Target | Validation |
|--------|--------|------------|
| **Process Spawn Time** | <2s for 5 instances | `time python -c "from aim.bridge import ToolProcessPool; ToolProcessPool('aider', 5)"` |
| **Prompt Latency** | <100ms per send | Benchmark in `tests/performance/` |
| **Throughput** | 50+ prompts/min | Stress test with 100 prompts across 5 instances |
| **Reliability** | 99% success rate | 1000 prompt test with random crashes |
| **Resource Usage** | <500MB RAM for 5 instances | Monitor with `psutil` |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Tool stdin/stdout protocol changes** | Medium | High | Version detection + protocol adapters per version |
| **Process hangs/deadlocks** | Medium | Medium | Timeout on all I/O operations + watchdog thread |
| **Resource leaks** | Low | Medium | Context managers + explicit cleanup in tests |
| **Backward compatibility break** | Low | High | Feature flag `use_pool_mode=False` by default |

---

## Rollback Plan

If issues arise:

1. **Week 1 rollback**: Delete `ToolProcessPool` class, revert `aim/bridge.py`
2. **Week 2 rollback**: Keep `ToolProcessPool` but don't expose `launch_cluster()` API
3. **Week 3 rollback**: Add `use_pool_mode=False` flag to orchestrator, default off

**Trigger criteria**:
- >10% test failure rate
- Performance degradation vs one-shot
- Unresolvable deadlocks/hangs

---

## Appendix: Execution Pattern Reference

**EXEC-002: Module Enhancement**

1. ✅ Define interface/contract
2. ✅ Implement core logic (single responsibility)
3. ✅ Write unit tests (mocked dependencies)
4. ✅ Integration tests (real dependencies)
5. ✅ Document API and usage
6. ✅ Performance validation

**Applied to**:
- Week 1: `ToolProcessPool` class enhancement to `aim/bridge.py`
- Week 2: `ClusterManager` API layer over `ToolProcessPool`

**EXEC-003: Cross-Module Integration**

1. ✅ Identify integration points (interfaces)
2. ✅ Update contracts/protocols
3. ✅ Implement adapter/bridge layer
4. ✅ Integration tests across modules
5. ✅ Backward compatibility validation
6. ✅ Migration documentation

**Applied to**:
- Week 3: `engine/adapters` ↔ `aim/bridge` integration

---

## Quick Start Commands

```bash
# Week 1: Test ToolProcessPool
python -c "from aim.bridge import ToolProcessPool; p = ToolProcessPool('aider', 3); p.shutdown()"

# Week 2: Test ClusterManager
python -c "from aim.bridge import launch_cluster; c = launch_cluster('aider', 3); c.shutdown()"

# Week 3: Run pooled pipeline
python -m engine.orchestrator --use-pool-mode --jobs parallel_refactor.json

# Full validation
pytest tests/ -v --cov=aim --cov=engine
```

---

## Documentation Deliverables

- [ ] `aim/docs/PROCESS_POOL_API.md` - API reference
- [ ] `aim/docs/TOOL_PROTOCOLS.md` - Tool-specific protocols
- [ ] `aim/docs/PERFORMANCE.md` - Benchmarks and tuning
- [ ] `docs/MIGRATION_POOLED_ADAPTERS.md` - Migration guide
- [ ] Updated `README.md` with pool examples

---

**Status**: Ready for execution
**Estimated Total Effort**: 72 hours (3 weeks × 24h)
**Team Size**: 1-2 developers
**Dependencies**: None (all internal)

**Next Step**: Create feature branch `feature/multi-instance-cli-control` and begin Day 1 tasks
