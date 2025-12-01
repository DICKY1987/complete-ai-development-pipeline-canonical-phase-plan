# ToolProcessPool API Reference

**Module**: `aim.bridge`  
**Class**: `ToolProcessPool`  
**Version**: 1.0.0  
**Status**: Production-ready ✅

---

## Overview

`ToolProcessPool` manages multiple long-lived CLI tool instances with interactive stdin/stdout communication. It enables parallel execution of commands across multiple tool processes.

**Key Features**:
- ✅ Multi-instance process management
- ✅ Interactive stdin/stdout via queues
- ✅ Background I/O threads (non-blocking)
- ✅ Health monitoring and crash recovery
- ✅ Graceful shutdown with force-kill fallback
- ✅ Thread-safe operations

---

## Quick Start

```python
from aim.bridge import ToolProcessPool

# Create pool with 3 aider instances
pool = ToolProcessPool("aider", count=3)

try:
    # Send commands to different instances
    pool.send_prompt(0, "/add core/state.py")
    pool.send_prompt(1, "/add error/engine.py")
    pool.send_prompt(2, "/help")
    
    # Read responses
    import time
    time.sleep(1.0)
    
    resp0 = pool.read_response(0, timeout=5.0)
    resp1 = pool.read_response(1, timeout=5.0)
    resp2 = pool.read_response(2, timeout=5.0)
    
    print(f"Instance 0: {resp0}")
    print(f"Instance 1: {resp1}")
    print(f"Instance 2: {resp2}")
    
finally:
    pool.shutdown()
```

---

## Constructor

### `__init__(tool_id: str, count: int, registry: Optional[Dict] = None)`

Initialize a process pool for a specific tool.

**Parameters**:
- `tool_id` (str): Tool identifier from AIM registry (e.g., "aider", "jules", "codex")
- `count` (int): Number of instances to spawn (1-10 recommended)
- `registry` (Optional[Dict]): Override AIM registry (for testing)

**Raises**:
- `ValueError`: If tool_id not found in registry
- `RuntimeError`: If process spawn fails

**Example**:
```python
pool = ToolProcessPool("aider", count=5)
```

---

## Core Methods

### `send_prompt(instance_idx: int, prompt: str) -> bool`

Send a command/prompt to a specific instance via stdin.

**Parameters**:
- `instance_idx` (int): Instance index (0 to count-1)
- `prompt` (str): Command to send (newline appended automatically)

**Returns**:
- `bool`: True if sent successfully, False if instance dead or invalid index

**Thread Safety**: ✅ Safe to call from multiple threads

**Example**:
```python
success = pool.send_prompt(0, "/add myfile.py")
if success:
    print("Command sent")
else:
    print("Instance unavailable")
```

---

### `read_response(instance_idx: int, timeout: float = 5.0) -> Optional[str]`

Read a line of output from instance stdout queue.

**Parameters**:
- `instance_idx` (int): Instance index
- `timeout` (float): Max seconds to wait for output

**Returns**:
- `str`: Output line (without trailing newline)
- `None`: If timeout or invalid index

**Thread Safety**: ✅ Safe to call from multiple threads

**Example**:
```python
# Wait up to 10 seconds for response
response = pool.read_response(0, timeout=10.0)

if response:
    print(f"Got: {response}")
else:
    print("Timeout or no output")
```

**Note**: For multi-line output, call in a loop:
```python
responses = []
for _ in range(10):
    line = pool.read_response(0, timeout=2.0)
    if line:
        responses.append(line)
    else:
        break
```

---

### `get_status() -> List[Dict[str, Any]]`

Get current status of all instances.

**Returns**:
- `List[Dict]`: Status for each instance with keys:
  - `index` (int): Instance index
  - `alive` (bool): Whether process is running
  - `return_code` (int|None): Exit code if terminated, None if running

**Example**:
```python
statuses = pool.get_status()

for s in statuses:
    print(f"Instance {s['index']}: {'alive' if s['alive'] else 'dead'}")
```

---

### `check_health() -> Dict[str, Any]`

Get aggregate health report for the pool.

**Returns**:
- `Dict`: Health summary with keys:
  - `total` (int): Total instance count
  - `alive` (int): Number of running instances
  - `dead` (int): Number of terminated instances
  - `instances` (List[Dict]): Per-instance status

**Example**:
```python
health = pool.check_health()
print(f"Health: {health['alive']}/{health['total']} alive")

if health['dead'] > 0:
    print(f"Warning: {health['dead']} instances dead")
```

---

### `restart_instance(instance_idx: int) -> bool`

Restart a crashed or dead instance.

**Parameters**:
- `instance_idx` (int): Instance to restart

**Returns**:
- `bool`: True if restarted successfully, False on failure

**Behavior**:
- Kills old process if still running
- Spawns new process with same configuration
- Replaces instance in pool

**Example**:
```python
# Check if instance is dead
if not pool.instances[0].alive:
    # Restart it
    if pool.restart_instance(0):
        print("Instance 0 restarted")
    else:
        print("Restart failed")
```

---

### `shutdown(timeout: float = 5.0) -> None`

Gracefully shutdown all instances.

**Parameters**:
- `timeout` (float): Seconds to wait for graceful exit before force kill

**Behavior**:
1. Send `terminate()` to all processes
2. Wait up to `timeout` seconds
3. Force `kill()` any remaining processes
4. Wait for all to exit

**Example**:
```python
# Give 10 seconds for graceful shutdown
pool.shutdown(timeout=10.0)
```

**Best Practice**: Always call in `finally` block:
```python
pool = ToolProcessPool("aider", count=3)
try:
    # ... work ...
finally:
    pool.shutdown()
```

---

## Instance Data

Each instance is represented by a `ProcessInstance` dataclass:

```python
@dataclass
class ProcessInstance:
    index: int                  # 0-based index
    tool_id: str               # Tool identifier
    process: subprocess.Popen  # Process handle
    stdout_queue: queue.Queue  # Buffered stdout
    stderr_queue: queue.Queue  # Buffered stderr
    alive: bool               # Responsive flag
```

**Access**:
```python
instance = pool.instances[0]
print(f"Tool: {instance.tool_id}")
print(f"PID: {instance.process.pid}")
print(f"Alive: {instance.alive}")
```

---

## Error Handling

### Common Errors

#### ValueError: Tool not in registry
```python
try:
    pool = ToolProcessPool("invalid_tool", count=1)
except ValueError as e:
    print(f"Tool not found: {e}")
```

#### BrokenPipeError: Process died
```python
success = pool.send_prompt(0, "/command")
if not success:
    # Process is dead, restart it
    pool.restart_instance(0)
```

#### Timeout: No response
```python
response = pool.read_response(0, timeout=5.0)
if response is None:
    # Either timeout or process produced no output
    # Check if process is alive
    status = pool.get_status()[0]
    if not status['alive']:
        print("Process died")
    else:
        print("Timeout - process slow or no output")
```

---

## Performance Considerations

### Resource Usage

**Per Instance**:
- Memory: ~200-300 MB (tool-dependent)
- Threads: 2 (stdout reader, stderr reader)
- File Descriptors: 3 (stdin, stdout, stderr)

**Recommended Limits**:
- Small tasks: 3-5 instances
- Medium tasks: 5-10 instances
- Large tasks: 10-20 instances (monitor RAM)

### Optimization Tips

1. **Reuse pools** instead of recreating:
   ```python
   # Good: Create once, use many times
   pool = ToolProcessPool("aider", count=3)
   for task in tasks:
       pool.send_prompt(task.instance, task.command)
   pool.shutdown()
   
   # Bad: Create per task
   for task in tasks:
       pool = ToolProcessPool("aider", count=1)
       pool.send_prompt(0, task.command)
       pool.shutdown()
   ```

2. **Batch reads** to reduce overhead:
   ```python
   # Read multiple lines at once
   responses = []
   while True:
       line = pool.read_response(0, timeout=1.0)
       if not line:
           break
       responses.append(line)
   ```

3. **Use appropriate timeouts**:
   - Fast commands: 2-3 seconds
   - Slow commands: 10-30 seconds
   - Long-running: 60+ seconds

---

## Thread Safety

**Thread-Safe Operations**:
- ✅ `send_prompt()` - Multiple threads can send to different instances
- ✅ `read_response()` - Queue operations are thread-safe
- ✅ `get_status()` - Read-only, safe
- ✅ `check_health()` - Read-only, safe

**Not Thread-Safe**:
- ❌ `shutdown()` - Call only once from main thread
- ❌ `restart_instance()` - Modifies pool state

**Example Multi-threaded Usage**:
```python
import threading

pool = ToolProcessPool("aider", count=3)

def worker(instance_idx, command):
    pool.send_prompt(instance_idx, command)
    time.sleep(0.5)
    response = pool.read_response(instance_idx, timeout=10.0)
    print(f"[{instance_idx}] {response}")

# Safe: Different instances
threads = [
    threading.Thread(target=worker, args=(0, "/help")),
    threading.Thread(target=worker, args=(1, "/tokens")),
    threading.Thread(target=worker, args=(2, "/add file.py")),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

pool.shutdown()
```

---

## Testing

### Unit Tests
```bash
pytest tests/aim/test_process_pool.py -v
# 23 tests, all mocked
```

### Integration Tests
```bash
pytest tests/aim/integration/test_aider_pool.py -v -m integration
# 7 tests with real aider
```

### Manual Testing
```python
python tests/aim/validate_pool.py
```

---

## Examples

### Example 1: Parallel File Analysis

```python
from aim.bridge import ToolProcessPool
import time

files = ["core/state.py", "error/engine.py", "aim/bridge.py"]
pool = ToolProcessPool("aider", count=len(files))

try:
    # Send analyze commands
    for i, filepath in enumerate(files):
        pool.send_prompt(i, f"/add {filepath}")
        time.sleep(0.2)
        pool.send_prompt(i, "/ask 'Summarize this file'")
    
    # Collect results
    time.sleep(2.0)
    results = {}
    for i, filepath in enumerate(files):
        response = pool.read_response(i, timeout=10.0)
        results[filepath] = response
    
    # Print results
    for filepath, summary in results.items():
        print(f"{filepath}: {summary}")

finally:
    pool.shutdown()
```

### Example 2: Health Monitoring Loop

```python
from aim.bridge import ToolProcessPool
import time

pool = ToolProcessPool("aider", count=5)

try:
    while True:
        health = pool.check_health()
        
        if health['dead'] > 0:
            print(f"Warning: {health['dead']} instances dead")
            
            # Restart dead instances
            for instance in health['instances']:
                if not instance['alive']:
                    print(f"Restarting instance {instance['index']}")
                    pool.restart_instance(instance['index'])
        
        time.sleep(5.0)  # Check every 5 seconds

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    pool.shutdown()
```

### Example 3: Load Balancing

```python
from aim.bridge import ToolProcessPool
import time

pool = ToolProcessPool("aider", count=3)
pending_work = [0, 0, 0]  # Track work per instance

try:
    tasks = ["/help", "/tokens", "/add a.py", "/add b.py", "/add c.py"]
    
    for task in tasks:
        # Find least busy instance
        instance_idx = pending_work.index(min(pending_work))
        
        # Send work
        pool.send_prompt(instance_idx, task)
        pending_work[instance_idx] += 1
        
        print(f"Sent '{task}' to instance {instance_idx}")
    
    # Wait and collect
    time.sleep(2.0)
    for i in range(3):
        while True:
            resp = pool.read_response(i, timeout=1.0)
            if not resp:
                break
            print(f"[{i}] {resp}")
            pending_work[i] -= 1

finally:
    pool.shutdown()
```

---

## Troubleshooting

### Issue: Timeout on first read

**Cause**: Tool startup buffering  
**Solution**: Wait longer before first read or use longer timeout

```python
pool = ToolProcessPool("aider", count=1)
time.sleep(2.0)  # Wait for startup
response = pool.read_response(0, timeout=5.0)
```

### Issue: Process dies immediately

**Cause**: Tool not installed or wrong command  
**Solution**: Verify tool is in PATH

```python
import shutil
if not shutil.which("aider"):
    print("Aider not installed!")
```

### Issue: Memory leak

**Cause**: Not calling `shutdown()`  
**Solution**: Always use try/finally

```python
pool = ToolProcessPool("aider", count=5)
try:
    # ... work ...
finally:
    pool.shutdown()  # Critical!
```

### Issue: Responses incomplete

**Cause**: Only reading one line of multi-line output  
**Solution**: Loop until timeout

```python
responses = []
for _ in range(20):  # Read up to 20 lines
    line = pool.read_response(0, timeout=1.0)
    if not line:
        break
    responses.append(line)
```

---

## Version History

- **v1.0.0** (2025-12-01): Initial release
  - Multi-instance process management
  - Interactive stdin/stdout
  - Health monitoring
  - 30 passing tests (23 unit + 7 integration)

---

## See Also

- [Aider Protocol Documentation](AIDER_PROTOCOL.md)
- [Integration Tests](../../tests/aim/integration/test_aider_pool.py)
- [Unit Tests](../../tests/aim/test_process_pool.py)

---

**Maintainer**: AI Development Pipeline Team  
**License**: Internal use  
**Support**: See [AIM README](../README.md)
