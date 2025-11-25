# Example 02: Parallel Execution - Multi-Step Utilities

**Pattern**: Multi-step workstream with parallel execution  
**Complexity**: Intermediate  
**Estimated Duration**: 3-6 minutes (parallel) vs 9-18 min (sequential)  
**Tool**: Aider (3 concurrent instances)

---

## Purpose

This example demonstrates **parallel step execution** for independent tasks. Use this pattern when you need to:

- Create multiple independent files simultaneously
- Perform batch operations across different modules
- Maximize throughput for non-dependent tasks
- Reduce total execution time by 2-3x

---

## What This Example Demonstrates

✅ **Parallel Execution**
- Multiple steps running concurrently
- Dependency-free task scheduling
- Worker pool management

✅ **Step Structure**
- Individual step configuration
- Per-step circuit breakers
- Step-level acceptance tests

✅ **Performance Optimization**
- Configurable worker count
- Per-step timeout management
- Execution time comparison

---

## Architecture: Parallel vs Sequential

### Sequential Execution (Traditional)
```
Step 1: Math Utils  [====] 3min
Step 2: String Utils      [====] 3min  
Step 3: File Utils              [====] 3min
----------------------------------------
Total: 9 minutes
```

### Parallel Execution (This Example)
```
Step 1: Math Utils   [====]
Step 2: String Utils [====]  } All execute
Step 3: File Utils   [====]  } concurrently
-------------------------
Total: ~3 minutes (3x faster!)
```

---

## Workstream File Breakdown

### Step Definition Structure

Each step is an independent unit of work:

```json
{
  "id": "step-01-math-utils",
  "description": "Create math utilities module",
  "tool": "aider",
  "tasks": [...],
  "depends_on": [],  // ← Empty = can run in parallel
  "acceptance_tests": [...]
}
```

---

### Key Innovation: `depends_on` Array

**Empty dependencies enable parallelism**:

```json
// All three steps have empty depends_on
"steps": [
  { "id": "step-01", "depends_on": [] },  // Runs immediately
  { "id": "step-02", "depends_on": [] },  // Runs immediately  
  { "id": "step-03", "depends_on": [] }   // Runs immediately
]
```

**How orchestrator schedules**:
1. Scan all steps for `depends_on: []`
2. Launch up to `max_workers` steps concurrently
3. Wait for any step to complete
4. Check newly-unblocked steps
5. Repeat until all steps done

---

### Execution Configuration

```json
{
  "execution": {
    "parallel": true,           // Enable parallel mode
    "max_workers": 3,          // Max concurrent steps
    "timeout_per_step": 300    // 5min timeout each
  }
}
```

**Why configure this?**:
- `parallel: false` → Force sequential (useful for debugging)
- `max_workers` → Limit concurrency (avoid API rate limits)
- `timeout_per_step` → Prevent hung steps from blocking others

---

## How Dependency Resolution Works

### Example with Dependencies

```json
"steps": [
  { "id": "A", "depends_on": [] },         // Runs first
  { "id": "B", "depends_on": ["A"] },      // Waits for A
  { "id": "C", "depends_on": ["A"] },      // Waits for A (parallel with B)
  { "id": "D", "depends_on": ["B", "C"] }  // Waits for both B and C
]
```

**Execution Timeline**:
```
Time 0: Launch A
Time 1: A completes → Launch B and C (parallel)
Time 2: B completes
Time 3: C completes → Launch D
Time 4: D completes → Done
```

**Our Example (All Independent)**:
```
Time 0: Launch step-01, step-02, step-03 (all parallel)
Time 3: All complete → Done
```

---

## Execution Methods

### Method 1: Using Pipeline Script

```bash
python scripts/run_workstream.py --ws-id ws-example-02-parallel-execution
```

**Expected Output**:
```
✓ Loading workstream: ws-example-02-parallel-execution
✓ Validating schema
✓ Checking file scope conflicts
✓ Building dependency graph (3 steps, 0 dependencies)
✓ Initializing worker pool (max_workers=3)

⟳ Executing steps in parallel:
  → [step-01-math-utils] Starting...
  → [step-02-string-utils] Starting...
  → [step-03-file-utils] Starting...

✓ [step-02-string-utils] Complete (2m 45s)
✓ [step-01-math-utils] Complete (2m 52s)
✓ [step-03-file-utils] Complete (3m 01s)

✓ All steps complete
✓ Running acceptance tests (3/3)
  → step-01: PASS
  → step-02: PASS
  → step-03: PASS

✓ Workstream complete in 3m 01s
  (Sequential would have taken ~9min - 66% time saved)
```

---

### Method 2: Monitor Individual Steps

```bash
# Watch orchestrator logs in real-time
tail -f .worktrees/ws-example-02-parallel-execution/orchestrator.log

# Check step status
python scripts/check_step_status.py ws-example-02-parallel-execution
```

---

## Expected Results

### Created Files

**1. examples/math_utils.py**
```python
"""Math utility functions."""

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**2. examples/string_utils.py**
```python
"""String utility functions."""

def reverse(s: str) -> str:
    """Reverse a string."""
    if s is None:
        return ""
    return s[::-1]

def capitalize_words(s: str) -> str:
    """Capitalize first letter of each word."""
    if s is None:
        return ""
    return s.title()

def remove_whitespace(s: str) -> str:
    """Remove all whitespace from string."""
    if s is None:
        return ""
    return "".join(s.split())
```

**3. examples/file_utils.py**
```python
"""File utility functions."""
from pathlib import Path
from typing import Optional

def safe_read(path: Path) -> Optional[str]:
    """Safely read file contents."""
    try:
        return path.read_text()
    except FileNotFoundError:
        return None

def safe_write(path: Path, content: str) -> bool:
    """Safely write content to file."""
    try:
        path.write_text(content)
        return True
    except Exception:
        return False

def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
```

---

## Performance Characteristics

### Execution Time Breakdown

| Metric | Sequential | Parallel | Improvement |
|--------|-----------|----------|-------------|
| **Step 1** | 3min | 3min | Same |
| **Step 2** | 3min | 3min (concurrent) | Same |
| **Step 3** | 3min | 3min (concurrent) | Same |
| **Total** | 9min | 3min | **66% faster** |

### Resource Usage

| Resource | Sequential | Parallel |
|----------|-----------|----------|
| **CPU** | 25% avg | 75% avg |
| **Memory** | 500MB | 1.5GB (3x) |
| **API Calls** | 3 total | 3 concurrent |
| **Disk I/O** | Sequential writes | Parallel writes |

---

## Troubleshooting

### Issue: "Worker pool exhausted"

**Cause**: More steps than `max_workers`  
**Fix**:
```json
{
  "execution": {
    "max_workers": 5  // Increase from default 3
  }
}
```

---

### Issue: "Step deadlock detected"

**Cause**: Circular dependencies (A depends on B, B depends on A)  
**Fix**: Review and fix dependency graph:
```bash
python scripts/visualize_dependencies.py ws-example-02-parallel-execution
# Outputs: dependency_graph.png
```

---

### Issue: "One step blocks all others"

**Cause**: One step taking much longer than others  
**Solution**: Adjust timeouts or split into smaller steps:
```json
{
  "execution": {
    "timeout_per_step": 600  // Increase to 10min
  }
}
```

---

### Issue: "API rate limits exceeded"

**Cause**: Too many concurrent API calls (e.g., OpenAI)  
**Fix**:
```json
{
  "execution": {
    "max_workers": 2,  // Reduce concurrency
    "rate_limit_delay": 5  // Add 5s delay between starts
  }
}
```

---

## Customization Examples

### Add Dependencies for Ordering

```json
"steps": [
  { "id": "step-01", "depends_on": [] },
  { "id": "step-02", "depends_on": [] },
  { "id": "step-03", "depends_on": ["step-01", "step-02"] }
]
```

**Result**: Steps 1 and 2 run in parallel, step 3 waits for both.

---

### Force Sequential Execution

```json
{
  "execution": {
    "parallel": false  // Disable parallelism
  }
}
```

**Use when**: Debugging, avoiding race conditions, single-threaded tools.

---

### Limit Concurrency for Rate Limits

```json
{
  "execution": {
    "max_workers": 1,  // Effectively sequential
    "parallel": true   // But maintains parallel infrastructure
  }
}
```

---

## Learning Points

### ✅ When to Use Parallel Execution

**Good Candidates**:
- Creating multiple independent files
- Running tests on different modules
- Batch processing of unrelated data
- Multi-file refactoring (different files)

**Bad Candidates**:
- Sequential build steps (compile → test → package)
- Database migrations with dependencies
- File operations with conflicts (same file)
- Tasks that must preserve order

---

### ⚠️ Common Pitfalls

1. **Hidden Dependencies**
   - Two steps modifying same global state
   - Race conditions on shared resources
   - **Fix**: Make dependencies explicit

2. **Unbalanced Load**
   - One step takes 10min, others take 1min
   - **Fix**: Split long steps, adjust workers

3. **Resource Exhaustion**
   - Too many workers → OOM or API limits
   - **Fix**: Profile resource usage, limit workers

4. **Flaky Tests**
   - Acceptance tests depend on execution order
   - **Fix**: Make tests truly independent

---

## Advanced Patterns

### Dynamic Parallelism

```json
{
  "execution": {
    "max_workers": "auto",  // CPU count
    "adaptive_scaling": true  // Adjust based on load
  }
}
```

---

### Step Groups

```json
{
  "step_groups": [
    {
      "id": "group-utils",
      "steps": ["step-01", "step-02", "step-03"],
      "execute": "parallel",
      "max_workers": 3
    }
  ]
}
```

---

### Conditional Parallelism

```json
{
  "execution": {
    "parallel": "${env.CI == 'true'}",  // Parallel in CI, sequential locally
    "max_workers": "${env.MAX_WORKERS:-3}"  // From environment
  }
}
```

---

## Next Steps

After mastering parallel execution, explore:

- **Example 03**: Error Handling - Recovery from failures in parallel steps
- **Example 04**: Multi-Phase - Complex dependency graphs
- **Example 05**: SAGA Pattern - Distributed transactions with rollback

---

## Related Documentation

- [Orchestrator Architecture](../ARCHITECTURE.md#orchestrator)
- [Dependency Resolution](../ENGINE_QUICK_REFERENCE.md#dependency-graph)
- [Worker Pool Management](../core/engine/executor.py)
- [Circuit Breakers](../ARCHITECTURE.md#circuit-breakers)

---

## Validation Checklist

Before using parallel execution in production:

- [ ] All steps are truly independent (no hidden dependencies)
- [ ] Resource limits configured (`max_workers`, timeouts)
- [ ] Acceptance tests don't rely on execution order
- [ ] Error handling works for partial failures
- [ ] Monitoring in place for parallel execution
- [ ] Rate limits considered for external APIs

---

**Last Updated**: 2025-11-22  
**Difficulty**: ⭐⭐ Intermediate  
**Execution Time**: 3-6 minutes (parallel) vs 9-18 min (sequential)  
**Success Rate**: ~90% (failures usually in dependency specification)
