---
doc_id: DOC-GUIDE-POOL-INTEGRATION-GUIDE-183
---

# Multi-CLI Cluster Integration Guide

**DOC_ID**: DOC-GUIDE-POOL-INTEGRATION-001

## Overview

This guide shows how to integrate the multi-CLI cluster (`ClusterManager`) with existing code.

**Value Proposition**: 3-5x speedup on batch tasks by reusing process pools instead of spawning new processes for each job.

---

## Quick Start (Standalone)

The simplest way to use the cluster is standalone:

```python
from phase4_routing.modules.aim_tools.src.aim.cluster_manager import launch_cluster

# Launch cluster
cluster = launch_cluster("aider", count=3)

# Use it
cluster.send("/add my_file.py")
cluster.send("/ask 'Add type hints'")
response = cluster.read_any(timeout=30)

# Cleanup
cluster.shutdown()
```

**When to use**: Scripts, one-off tasks, manual workflows

---

## Integration Approaches

### Approach 1: Pool-Aware Mixin (Recommended)

Add pool support to existing adapters with minimal changes:

```python
from phase4_routing.modules.aim_tools.src.aim.pool_adapter_mixin import PoolAwareMixin

class MyAiderAdapter(PoolAwareMixin, ExistingAdapter):
    def invoke(self, request):
        if self.is_pool_enabled():
            return self._invoke_with_pool(request)
        else:
            return super().invoke(request)  # Fallback

    def _invoke_with_pool(self, request):
        # Send to cluster
        self._cluster.send(f"/add {request.file}")
        response = self._cluster.read_any(timeout=30)
        return response

# Usage
adapter = MyAiderAdapter()
adapter.use_pool(count=3)  # Enable pool mode
result = adapter.invoke(request)
```

**Pros**:
- Minimal code changes
- Backward compatible (falls back to one-shot)
- Easy to enable/disable

**Cons**:
- Requires adapter modification
- Not automatic

---

### Approach 2: Wrapper Function

Wrap existing adapters without modification:

```python
from phase4_routing.modules.aim_tools.src.aim.pool_adapter_mixin import make_pool_aware

# Existing adapter
adapter = AiderAdapter()

# Make it pool-aware
pool_adapter = make_pool_aware(adapter, pool_count=3)

# Use normally - now uses pool!
result = pool_adapter.invoke(request)
```

**Pros**:
- No adapter modification needed
- Works with any adapter

**Cons**:
- Runtime patching (less explicit)
- May need customization per adapter type

---

### Approach 3: Orchestrator Integration (Future)

For full automation, integrate with the orchestrator:

```python
class Orchestrator:
    def __init__(self):
        self._tool_pools = {}  # Cache pools by tool

    def execute_jobs(self, jobs):
        # Group jobs by tool
        by_tool = self._group_by_tool(jobs)

        for tool_id, tool_jobs in by_tool.items():
            # Use pool if multiple jobs for same tool
            if len(tool_jobs) > 1:
                pool = self._get_or_create_pool(tool_id)
                results = self._execute_with_pool(pool, tool_jobs)
            else:
                results = self._execute_one_shot(tool_jobs)

        return results

    def _get_or_create_pool(self, tool_id):
        if tool_id not in self._tool_pools:
            self._tool_pools[tool_id] = launch_cluster(tool_id, count=3)
        return self._tool_pools[tool_id]
```

**Pros**:
- Fully automatic
- Optimal resource usage
- Transparent to users

**Cons**:
- More complex
- Requires orchestrator changes
- **Status**: Planned for Week 4

---

## Performance Comparison

### Before (One-Shot)

```python
# Sequential execution
for file in files:
    subprocess.run(["aider", file, "--message", prompt])

# 3 files × 40s each = 120s total
```

### After (Cluster)

```python
cluster = launch_cluster("aider", count=3)

for file in files:
    cluster.send(f"/add {file}")
    cluster.send(f"/ask '{prompt}'")

# 3 files in parallel ≈ 40s total
# Speedup: 3x!
```

---

## Real-World Example: DOC_ID Rollout

**Task**: Add doc_id headers to 218 files

**Before (Sequential)**:
- 218 files × 15s each = 3,270s (54 minutes)

**After (Cluster with 5 workers)**:
- 218 files ÷ 5 workers × 15s ≈ 654s (11 minutes)
- **Speedup: 5x faster!**

```python
cluster = launch_cluster("aider", count=5, routing="least_busy")

for filepath in files:
    cluster.send(f"/add {filepath}")
    cluster.send("/ask 'Add DOC_ID header'")

# Collect results
for i in range(len(files)):
    response = cluster.read_any(timeout=30)
    # Process response

cluster.shutdown()
```

---

## Best Practices

### 1. Pool Sizing

```python
# Too few: Underutilized
cluster = launch_cluster("aider", count=1)  # ❌ No parallelism

# Good: Match task count
cluster = launch_cluster("aider", count=3)  # ✅ 3 tasks

# Too many: Resource waste
cluster = launch_cluster("aider", count=20) # ❌ Overkill
```

**Rule of thumb**: 3-5 workers for most tasks

### 2. Routing Strategy

```python
# Round-robin: Even distribution
cluster = launch_cluster("aider", routing="round_robin")  # ✅ Default

# Least-busy: Load balancing
cluster = launch_cluster("aider", routing="least_busy")   # ✅ Variable loads

# Sticky: Debugging
cluster = launch_cluster("aider", routing="sticky")        # 🔧 Debug only
```

### 3. Error Handling

```python
cluster = launch_cluster("aider", count=3)

try:
    for file in files:
        cluster.send(f"/add {file}")

    results = []
    for _ in files:
        response = cluster.read_any(timeout=30)
        if response is None:
            # Handle timeout
            print("Warning: Timeout on response")
        results.append(response)

finally:
    # Always cleanup!
    cluster.shutdown()
```

### 4. Monitoring

```python
# Check cluster health
health = cluster.check_health()
print(f"{health['alive']}/{health['total']} alive")

# Get metrics
status = cluster.get_status()
print(f"Sent: {status['metrics']['total_sent']}")
print(f"Received: {status['metrics']['total_received']}")

# Restart dead instances
if health['dead'] > 0:
    cluster.restart_instance(0)  # Restart instance 0
```

---

## Migration Path

### Phase 1: Standalone Usage (Now)

Use clusters in scripts and manual tasks:

```python
# scripts/batch_refactor.py
cluster = launch_cluster("aider", count=3)
# ... use cluster ...
cluster.shutdown()
```

**Effort**: Minimal
**Value**: Immediate 3-5x speedup

### Phase 2: Adapter Integration (Week 3)

Add pool support to adapters:

```python
class AiderAdapter(PoolAwareMixin, BaseAdapter):
    pass
```

**Effort**: 1-2 hours per adapter
**Value**: Reusable across codebase

### Phase 3: Orchestrator Integration (Week 4)

Make orchestrator pool-aware:

```python
orchestrator.execute_jobs(jobs)  # Auto uses pools!
```

**Effort**: 1-2 days
**Value**: Fully automatic, system-wide benefit

---

## Troubleshooting

### Pool instances won't start

**Symptom**: `health['alive'] == 0`

**Fix**:
```python
# Check tool is installed
import shutil
print(shutil.which("aider"))  # Should print path

# Check registry
from phase4_routing.modules.aim_tools.src.aim.process_pool import load_aim_registry
registry = load_aim_registry()
print(registry["tools"]["aider"])
```

### Responses always None

**Symptom**: `read_any()` returns None

**Fix**:
```python
# Increase timeout
response = cluster.read_any(timeout=60)  # Not 5!

# Check instances are alive
health = cluster.check_health()
print(health)
```

### Memory leaks

**Symptom**: RAM grows over time

**Fix**:
```python
# Always call shutdown!
try:
    cluster.send(...)
finally:
    cluster.shutdown()

# Or use context manager (future):
# with launch_cluster("aider") as cluster:
#     cluster.send(...)
```

---

## Next Steps

1. **Try standalone example**: Run `examples/parallel_refactor.py`
2. **Measure your speedup**: Use on a real batch task
3. **Integrate with adapter**: Add `PoolAwareMixin` to your adapter
4. **Week 4**: Full orchestrator integration

---

## Files Reference

- `phase4_routing/modules/aim_tools/src/aim/cluster_manager.py` - ClusterManager class
- `phase4_routing/modules/aim_tools/src/aim/routing.py` - Routing strategies
- `phase4_routing/modules/aim_tools/src/aim/pool_adapter_mixin.py` - Adapter mixin
- `examples/parallel_refactor.py` - Standalone example
- `tests/aim/test_cluster_manager.py` - Usage examples in tests

---

**Status**: Production Ready
**Last Updated**: 2025-12-05
**Speedup**: 3-5x on batch tasks
