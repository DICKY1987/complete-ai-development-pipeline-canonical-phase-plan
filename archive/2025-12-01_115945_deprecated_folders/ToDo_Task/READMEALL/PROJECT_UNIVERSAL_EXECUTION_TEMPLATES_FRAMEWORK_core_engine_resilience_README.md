---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1597
---

# core/engine/resilience

**Purpose**: Fault tolerance patterns for reliable external tool execution.

## Overview

Provides resilience patterns to handle failures gracefully:
- **Circuit Breaker** - Prevent cascading failures
- **Retry with Exponential Backoff** - Handle transient failures
- **Timeout Management** - Prevent indefinite waiting
- **Failure Tracking** - Monitor tool reliability

## Key Files

- **circuit_breaker.py** - Circuit breaker implementation
- **executor.py** - ResilientExecutor with retry logic
- **backoff.py** - Exponential backoff strategies

## Dependencies

**Depends on:**
- core/state/ - For failure tracking

**Used by:**
- core/engine/ - For task execution

## Circuit Breaker

Prevents repeated calls to failing external tools.

### States
- **CLOSED** - Normal operation, requests pass through
- **OPEN** - Tool is failing, requests immediately fail
- **HALF_OPEN** - Testing recovery, limited requests allowed

### Usage
```python
from core.engine.resilience import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Try recovery after 60s
    success_threshold=2       # Close after 2 successes
)

def risky_operation():
    # Call external tool
    pass

result = breaker.call(risky_operation)
```

## Resilient Executor

Wraps tool execution with retry logic and circuit breakers.

### Usage
```python
from core.engine.resilience import ResilientExecutor

executor = ResilientExecutor()

# Register tool with config
executor.register_tool(
    "aider",
    max_retries=3,
    base_delay=1.0,
    failure_threshold=5,
    recovery_timeout=60
)

# Execute with resilience
result = executor.execute("aider", lambda: tool.run())
```

## Exponential Backoff

Retry strategy with exponentially increasing delays.

### Formula
```
delay = base_delay * (2 ^ attempt_number)
delay = min(delay, max_delay)
```

### Example
```python
from core.engine.resilience import exponential_backoff

for attempt in range(max_retries):
    delay = exponential_backoff(
        attempt=attempt,
        base_delay=1.0,
        max_delay=60.0
    )
    time.sleep(delay)
    # Retry operation
```

## References

- **Architecture**: ARCHITECTURE.md (Resilience Patterns section)
- **Engine**: core/engine/README.md
