# Plugin-Based Agent Architecture
## Dynamic CLI Tool Orchestration System

**Date**: 2025-11-29  
**Status**: Implementation Design  
**Complexity**: Medium (200-300 lines core logic)  
**Overhead**: Low (300 MB for 3 workers)  
**Control**: High (kill, monitor, timeout)

---

## 🎯 Design Goal

Create a **self-replicating orchestration pattern** where:
- **Main orchestrator** (`cli_app_0`) launches worker instances (`cli_app_1`, `cli_app_2`, etc.)
- **Worker CLI tool is pluggable** - currently GitHub Copilot CLI, but can be swapped for other tools
- **Each worker** gets isolated worktree, unique configuration, and specific task assignments
- **Future-proof** architecture allows replacing CLI tools without changing orchestration logic

---

## 🏗️ Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Configuration Layer                                │
│ ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│ │ config.yaml │  │ tool_registry│  │ worker_templates │   │
│ └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Orchestration Layer                                │
│ ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│ │ ToolFactory  │→ │ ProcessMgr   │→ │ WorktreeMgr     │   │
│ │ (Plugin Abs) │  │ (Spawn/Kill) │  │ (Isolation)     │   │
│ └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Worker Execution Layer                             │
│ ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│ │ cli_app_1  │  │ cli_app_2  │  │ cli_app_3  │   ...      │
│ │ (Copilot)  │  │ (Copilot)  │  │ (Custom?)  │            │
│ └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Layer 1: Configuration Layer

### config.yaml Structure

```yaml
# Global Settings
orchestrator:
  max_workers: 3
  base_memory_limit_mb: 100
  timeout_minutes: 30
  log_level: "info"

# Worker Settings Template
worker_defaults:
  retry_attempts: 3
  heartbeat_interval_sec: 30
  worktree_base_path: ".worktrees"

# Available CLI Tools Registry
available_tools:
  # Current Tool: GitHub Copilot CLI
  copilot:
    executable_path: "github-copilot-cli"  # Or full path
    base_args:
      - "--mode"
      - "worker"
      - "--log-level"
      - "info"
    supports_worktree: true
    supports_task_input: true
    env_vars:
      COPILOT_WORKER_MODE: "1"
  
  # Future Tool Example: Custom AI Agent
  custom_agent:
    executable_path: "/opt/agents/my-custom-cli"
    base_args:
      - "--env"
      - "prod"
      - "--batch-mode"
    supports_worktree: true
    supports_task_input: true
    env_vars:
      AGENT_MODE: "parallel"
  
  # Future Tool: Aider Fallback
  aider:
    executable_path: "aider"
    base_args:
      - "--yes"
      - "--no-auto-commits"
    supports_worktree: true
    supports_task_input: false  # Uses stdin instead

# Tool Selection Strategy
tool_selection:
  default: "copilot"
  fallback_order:
    - "copilot"
    - "aider"
    - "custom_agent"
```

---

## 🔧 Layer 2: Orchestration Layer

### Component 1: ToolFactory (Plugin Abstraction)

**Purpose**: Generate executable commands for any registered CLI tool

```python
class ToolFactory:
    """Abstracts CLI tool execution - makes tools pluggable"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.available_tools = self.config["available_tools"]
    
    def create_worker_command(
        self, 
        tool_name: str,
        worker_id: str,
        worktree_path: str,
        task_input: str,
        extra_args: dict = None
    ) -> tuple[list[str], dict[str, str]]:
        """
        Returns: (command_args, env_vars)
        
        Example Output for GitHub Copilot:
        (
            ["github-copilot-cli", "--mode", "worker", 
             "--id", "cli_app_1", "--workdir", "/tmp/worktrees/worker_1/",
             "--task", "Refactor core/state module"],
            {"COPILOT_WORKER_MODE": "1"}
        )
        """
        tool_config = self.available_tools.get(tool_name)
        if not tool_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Start with base command
        cmd = [tool_config["executable_path"]] + tool_config["base_args"]
        
        # Add worker-specific arguments
        cmd.extend([
            "--id", worker_id,
            "--workdir", worktree_path
        ])
        
        # Add task input if supported
        if tool_config.get("supports_task_input"):
            cmd.extend(["--task", task_input])
        
        # Add any extra arguments
        if extra_args:
            for key, value in extra_args.items():
                cmd.extend([f"--{key}", str(value)])
        
        # Get environment variables
        env_vars = tool_config.get("env_vars", {})
        
        return cmd, env_vars
    
    def get_fallback_tool(self, failed_tool: str) -> str:
        """Get next tool in fallback order"""
        fallback_order = self.config["tool_selection"]["fallback_order"]
        try:
            idx = fallback_order.index(failed_tool)
            if idx + 1 < len(fallback_order):
                return fallback_order[idx + 1]
        except ValueError:
            pass
        return self.config["tool_selection"]["default"]
```

---

### Component 2: ProcessManager (Spawn/Monitor/Kill)

**Purpose**: Manage worker process lifecycle with high control

```python
import subprocess
import psutil
import time
from typing import Optional

class ProcessManager:
    """Manages worker process lifecycle"""
    
    def __init__(self):
        self.workers: dict[str, subprocess.Popen] = {}
        self.start_times: dict[str, float] = {}
    
    def spawn_worker(
        self,
        worker_id: str,
        command: list[str],
        env_vars: dict[str, str],
        worktree_path: str,
        timeout_minutes: int = 30
    ) -> subprocess.Popen:
        """
        Spawn a new worker process with full control
        
        Returns: Process handle for monitoring
        """
        # Merge environment variables
        env = os.environ.copy()
        env.update(env_vars)
        
        # Spawn process
        process = subprocess.Popen(
            command,
            cwd=worktree_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered for real-time monitoring
        )
        
        self.workers[worker_id] = process
        self.start_times[worker_id] = time.time()
        
        print(f"✅ Spawned worker {worker_id} (PID: {process.pid})")
        return process
    
    def monitor_worker(self, worker_id: str) -> dict:
        """
        Get current worker status
        
        Returns: {
            "status": "running|completed|failed|timeout",
            "runtime_sec": float,
            "memory_mb": float,
            "cpu_percent": float,
            "exit_code": int|None
        }
        """
        process = self.workers.get(worker_id)
        if not process:
            return {"status": "unknown"}
        
        runtime = time.time() - self.start_times[worker_id]
        
        try:
            proc_info = psutil.Process(process.pid)
            memory_mb = proc_info.memory_info().rss / 1024 / 1024
            cpu_percent = proc_info.cpu_percent(interval=0.1)
        except psutil.NoSuchProcess:
            memory_mb = 0
            cpu_percent = 0
        
        # Check if completed
        exit_code = process.poll()
        if exit_code is not None:
            status = "completed" if exit_code == 0 else "failed"
        else:
            status = "running"
        
        return {
            "status": status,
            "runtime_sec": runtime,
            "memory_mb": memory_mb,
            "cpu_percent": cpu_percent,
            "exit_code": exit_code
        }
    
    def kill_worker(self, worker_id: str, graceful: bool = True) -> bool:
        """
        Terminate a worker process
        
        Args:
            graceful: If True, try SIGTERM first, then SIGKILL
        
        Returns: True if killed successfully
        """
        process = self.workers.get(worker_id)
        if not process:
            return False
        
        try:
            if graceful:
                process.terminate()  # SIGTERM
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()  # SIGKILL
            else:
                process.kill()
            
            del self.workers[worker_id]
            del self.start_times[worker_id]
            print(f"🛑 Killed worker {worker_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to kill {worker_id}: {e}")
            return False
    
    def enforce_timeout(self, timeout_minutes: int):
        """Kill workers that exceed timeout"""
        for worker_id in list(self.workers.keys()):
            status = self.monitor_worker(worker_id)
            if status["runtime_sec"] > timeout_minutes * 60:
                print(f"⏰ Timeout: Killing {worker_id}")
                self.kill_worker(worker_id, graceful=False)
    
    def get_worker_output(self, worker_id: str) -> tuple[str, str]:
        """Get stdout and stderr from worker"""
        process = self.workers.get(worker_id)
        if not process:
            return "", ""
        
        stdout, stderr = process.communicate(timeout=1)
        return stdout, stderr
```

---

## 🚀 Layer 3: Worker Execution Pattern

### Self-Replication Example (GitHub Copilot as Worker)

When the orchestrator wants to spawn a worker:

```python
# In main orchestrator (cli_app_0)
from tool_factory import ToolFactory
from process_manager import ProcessManager
from worktree_manager import WorktreeManager

# Initialize managers
tool_factory = ToolFactory("config.yaml")
process_mgr = ProcessManager()
worktree_mgr = WorktreeManager()

# Assign task to Worker 1
worker_id = "cli_app_1"
task = "Refactor core/state module for better separation"

# Create isolated worktree
worktree_path = worktree_mgr.create_worktree(
    branch_name=f"refactor/worker-{worker_id}",
    path=f".worktrees/{worker_id}"
)

# Generate command for current tool (GitHub Copilot)
command, env_vars = tool_factory.create_worker_command(
    tool_name="copilot",
    worker_id=worker_id,
    worktree_path=worktree_path,
    task_input=task,
    extra_args={"timeout": "30m", "max-retries": "3"}
)

# Spawn the worker process
process = process_mgr.spawn_worker(
    worker_id=worker_id,
    command=command,
    env_vars=env_vars,
    worktree_path=worktree_path,
    timeout_minutes=30
)

# Monitor in background
while True:
    status = process_mgr.monitor_worker(worker_id)
    if status["status"] != "running":
        break
    time.sleep(10)  # Check every 10 seconds

print(f"Worker {worker_id} finished with status: {status['status']}")
```

---

## 🔄 Replacing the CLI Tool (Future)

To switch from GitHub Copilot to a custom agent:

1. **Update config.yaml**:
   ```yaml
   tool_selection:
     default: "custom_agent"  # Changed from "copilot"
   ```

2. **No code changes needed** - ToolFactory automatically uses new tool

3. **Verify new tool supports required args**:
   - Must accept `--id` (worker identifier)
   - Must accept `--workdir` (worktree path)
   - Must accept task input (via `--task` or stdin)

---

## 📊 Complexity Analysis

### Development Complexity: **Medium**
- **ToolFactory**: ~80 lines
- **ProcessManager**: ~120 lines
- **Integration**: ~50 lines
- **Total**: ~250 lines core logic

### System Overhead: **Low**
- **Memory per worker**: ~100 MB (Copilot CLI baseline)
- **3 workers total**: ~300 MB
- **CPU**: Minimal orchestration overhead (<5%)

### Control Level: **High**
- ✅ Can kill workers instantly
- ✅ Real-time monitoring (CPU, memory, runtime)
- ✅ Timeout enforcement
- ✅ Graceful shutdown support
- ✅ Output capture (stdout/stderr)

---

## 🛡️ Error Handling & Fallback

```python
def execute_task_with_fallback(task: str, worktree: str):
    """Try tools in fallback order until success"""
    
    fallback_order = ["copilot", "aider", "custom_agent"]
    
    for tool_name in fallback_order:
        print(f"🔄 Trying {tool_name}...")
        
        try:
            cmd, env = tool_factory.create_worker_command(
                tool_name=tool_name,
                worker_id="worker_1",
                worktree_path=worktree,
                task_input=task
            )
            
            process = process_mgr.spawn_worker(
                worker_id="worker_1",
                command=cmd,
                env_vars=env,
                worktree_path=worktree
            )
            
            # Wait for completion
            status = wait_for_completion("worker_1", timeout=30)
            
            if status["exit_code"] == 0:
                print(f"✅ Success with {tool_name}")
                return True
            else:
                print(f"❌ {tool_name} failed, trying next...")
                
        except Exception as e:
            print(f"❌ {tool_name} error: {e}")
            continue
    
    print("❌ All tools failed")
    return False
```

---

## 🎯 Benefits of This Architecture

1. **Future-Proof**: Swap CLI tools by editing config, not code
2. **High Control**: Kill, monitor, timeout any worker instantly
3. **Low Overhead**: Only ~100 MB per worker
4. **Parallel Safe**: Each worker in isolated worktree
5. **Fallback Ready**: Automatic tool switching on failure
6. **Simple**: ~250 lines of orchestration logic

---

## 🚀 Next Steps

1. **Implement ToolFactory** - Plugin abstraction layer
2. **Enhance ProcessManager** - Add timeout/monitoring
3. **Test with GitHub Copilot** - Verify self-replication works
4. **Add Second Tool** - Test plugin swapping (e.g., Aider)
5. **Benchmark Overhead** - Measure 3-worker parallel execution

---

## 📚 Related Documentation

- `AGENT_ARCHITECTURE_DEEP_DIVE.md` - Detailed agent comparison
- `AGENT_FALLBACK_STRATEGIES.md` - Tool fallback logic
- `WORKTREE_ISOLATION_DEEP_DIVE.md` - Isolation mechanics
- `multi_agent_orchestrator.py` - Implementation reference

---

**Status**: Ready for implementation ✅  
**Recommended Start**: ToolFactory + ProcessManager basics (1-2 hours)
