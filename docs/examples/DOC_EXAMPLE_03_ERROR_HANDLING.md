---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-EXAMPLE_ERROR_HANDLING-015
---

# Example 03: Error Handling - Resilient Network Client

**Pattern**: Circuit breaker, retry, and recovery  
**Complexity**: Intermediate  
**Estimated Duration**: 3-8 minutes (with retries)  
**Tool**: Aider with enhanced error handling

---

## Purpose

This example demonstrates **comprehensive error handling and recovery** in workstreams. Use this pattern when you need to:

- Handle unreliable external services (APIs, databases)
- Implement self-healing workflows
- Prevent cascading failures
- Gracefully degrade under load
- Maintain system stability despite errors

---

## What This Example Demonstrates

✅ **Circuit Breaker Pattern**
- Automatic failure detection
- Circuit open/half-open/closed states
- Cooldown periods before retry

✅ **Retry Logic**
- Exponential backoff strategy
- Jitter to prevent thundering herd
- Maximum attempt limits

✅ **Error Recovery**
- Graceful degradation
- Diagnostic collection
- Notification on failure
- Recovery confirmation

---

## Error Handling Architecture

### Circuit Breaker States

```
┌─────────────┐
│   CLOSED    │ ◄── Normal operation
│ (Working)   │
└──────┬──────┘
       │ Failures exceed threshold
       ▼
┌─────────────┐
│    OPEN     │ ◄── Fast-fail mode
│  (Broken)   │
└──────┬──────┘
       │ After cooldown period
       ▼
┌─────────────┐
│ HALF-OPEN   │ ◄── Testing recovery
│  (Testing)  │
└──────┬──────┘
       │ Success → CLOSED
       │ Failure → OPEN
```

### Retry Strategy: Exponential Backoff

```
Attempt 1: Immediate
Attempt 2: Wait 1s  (2^0)
Attempt 3: Wait 2s  (2^1)
Attempt 4: Wait 4s  (2^2)
Attempt 5: Wait 8s  (2^3)
Attempt 6: Wait 16s (2^4) + jitter

Total time: ~31s for 6 attempts
```

---

## Workstream Configuration Breakdown

### 1. Circuit Breaker Configuration

```json
{
  "circuit_breaker": {
    "max_attempts": 5,
    "max_error_repeats": 3,
    "cooldown_seconds": 30,
    "error_patterns": [
      "TimeoutError",
      "ConnectionError",
      "rate limit exceeded"
    ],
    "escalation_strategy": "exponential_backoff"
  }
}
```

**How it works**:
1. **First 3 failures**: Retry with exponential backoff
2. **3 identical errors**: Circuit opens (fast-fail mode)
3. **After 30s cooldown**: Attempt one request (half-open)
4. **If success**: Circuit closes, resume normal operation
5. **If failure**: Circuit reopens, wait another 30s

---

### 2. Retry Configuration

```json
{
  "retry": {
    "enabled": true,
    "strategy": "exponential",
    "initial_delay": 1,
    "max_delay": 60,
    "jitter": true
  }
}
```

**Jitter explained**:
```python
# Without jitter
delay = 2 ** attempt_number  # 1, 2, 4, 8, 16...

# With jitter (prevents thundering herd)
delay = (2 ** attempt_number) * random.uniform(0.5, 1.5)
# Result: 0.5-1.5s, 1-3s, 2-6s, 4-12s...
```

**Why jitter?** If 100 clients fail simultaneously, without jitter they all retry at exactly the same time, potentially overwhelming the service again.

---

### 3. Error Handling Actions

```json
{
  "error_handling": {
    "on_failure": {
      "action": "log_and_continue",
      "collect_diagnostics": true,
      "notify": ["example@team.com"]
    },
    "on_retry": {
      "action": "log",
      "message": "Retrying (attempt ${attempt_number}/${max_attempts})"
    },
    "on_recovery": {
      "action": "log",
      "message": "Recovered after ${attempt_number} attempts"
    },
    "on_circuit_open": {
      "action": "pause_and_notify",
      "pause_duration": 30
    }
  }
}
```

---

## Expected Behavior

### Scenario 1: Success on First Try

```
[INFO] Executing step...
[INFO] Step completed successfully (0 retries)
✓ Workstream complete
```

---

### Scenario 2: Transient Failure with Recovery

```
[INFO] Executing step...
[ERROR] Attempt 1 failed: ConnectionError
[WARN] Retrying in 1s...
[INFO] Attempt 2 succeeded
[INFO] Step recovered after 2 attempts
✓ Workstream complete
```

---

### Scenario 3: Multiple Retries with Backoff

```
[INFO] Executing step...
[ERROR] Attempt 1 failed: TimeoutError
[WARN] Retrying in 1.2s (jitter applied)...
[ERROR] Attempt 2 failed: TimeoutError  
[WARN] Retrying in 2.8s (jitter applied)...
[ERROR] Attempt 3 failed: TimeoutError
[WARN] Circuit breaker: 3 identical errors detected
[WARN] Escalating to exponential backoff...
[WARN] Retrying in 5.4s...
[INFO] Attempt 4 succeeded
[INFO] Step recovered after 4 attempts
✓ Workstream complete (took 9.4s including retries)
```

---

### Scenario 4: Circuit Breaker Opens

```
[INFO] Executing step...
[ERROR] Attempt 1 failed: ConnectionError
[ERROR] Attempt 2 failed: ConnectionError
[ERROR] Attempt 3 failed: ConnectionError (identical)
[WARN] Circuit breaker OPENED (threshold exceeded)
[WARN] Fast-failing all requests for 30s cooldown
[INFO] Collecting diagnostics...
[INFO] Notifying: example@team.com

... 30 seconds pass ...

[INFO] Circuit breaker entering HALF-OPEN state
[INFO] Testing with single request...
[INFO] Test request succeeded
[INFO] Circuit breaker CLOSED - resuming normal operation
✓ Workstream complete
```

---

### Scenario 5: Permanent Failure

```
[INFO] Executing step...
[ERROR] Attempt 1 failed: ConnectionError
[ERROR] Attempt 2 failed: ConnectionError
[ERROR] Attempt 3 failed: ConnectionError
[ERROR] Attempt 4 failed: ConnectionError
[ERROR] Attempt 5 failed: ConnectionError
[ERROR] Max attempts (5) exceeded
[ERROR] Circuit breaker: permanent failure detected
[INFO] Collecting full diagnostics...
[INFO] Notifying: example@team.com
✗ Workstream failed (after 5 attempts, 31s elapsed)

Diagnostic bundle saved to:
.worktrees/ws-example-03-error-handling/diagnostics/
```

---

## Generated Code Example

### examples/network_client.py

```python
"""
Network Client with Retry Logic and Circuit Breaker

Demonstrates robust error handling for unreliable network operations.
"""

import time
import random
import logging
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Fast-fail mode
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation."""
    
    failure_threshold: int = 3
    cooldown_seconds: int = 30
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    consecutive_errors: list = field(default_factory=list)
    
    def record_success(self) -> None:
        """Record successful request."""
        self.failure_count = 0
        self.consecutive_errors.clear()
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker: Test succeeded, closing circuit")
            self.state = CircuitState.CLOSED
    
    def record_failure(self, error: Exception) -> None:
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.consecutive_errors.append(str(error))
        
        # Check for identical consecutive errors
        if len(self.consecutive_errors) >= self.failure_threshold:
            recent_errors = self.consecutive_errors[-self.failure_threshold:]
            if len(set(recent_errors)) == 1:
                logger.warning(
                    f"Circuit breaker: {self.failure_threshold} identical "
                    f"errors detected, opening circuit"
                )
                self.state = CircuitState.OPEN
    
    def can_attempt(self) -> bool:
        """Check if request should be attempted."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if cooldown period elapsed
            if self.last_failure_time is None:
                return False
            
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.cooldown_seconds:
                logger.info("Circuit breaker: Cooldown elapsed, entering half-open state")
                self.state = CircuitState.HALF_OPEN
                return True
            else:
                logger.debug(f"Circuit breaker: Still in cooldown ({elapsed:.1f}s / {self.cooldown_seconds}s)")
                return False
        
        if self.state == CircuitState.HALF_OPEN:
            # Only allow one test request
            return True
        
        return False


class NetworkClient:
    """Network client with retry logic and circuit breaker."""
    
    def __init__(
        self,
        max_attempts: int = 5,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.circuit_breaker = CircuitBreaker()
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        # Exponential backoff: 2^(attempt-1)
        delay = self.initial_delay * (2 ** (attempt - 1))
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (±50%)
        if self.jitter:
            jitter_range = delay * 0.5
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def request_with_retry(
        self,
        operation: Callable[[], Any],
        operation_name: str = "operation"
    ) -> Any:
        """
        Execute operation with retry logic and circuit breaker.
        
        Args:
            operation: Function to execute
            operation_name: Human-readable operation name for logging
            
        Returns:
            Operation result
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            # Check circuit breaker
            if not self.circuit_breaker.can_attempt():
                logger.warning(f"Circuit breaker OPEN - fast failing {operation_name}")
                raise RuntimeError("Circuit breaker open")
            
            try:
                logger.info(f"Attempting {operation_name} (attempt {attempt}/{self.max_attempts})")
                result = operation()
                
                # Success!
                self.circuit_breaker.record_success()
                if attempt > 1:
                    logger.info(f"{operation_name} recovered after {attempt} attempts")
                return result
                
            except Exception as e:
                last_exception = e
                self.circuit_breaker.record_failure(e)
                
                logger.error(f"{operation_name} failed (attempt {attempt}): {e}")
                
                # Don't retry on final attempt
                if attempt == self.max_attempts:
                    logger.error(f"Max attempts ({self.max_attempts}) exceeded for {operation_name}")
                    break
                
                # Calculate and apply backoff delay
                delay = self._calculate_delay(attempt)
                logger.warning(f"Retrying {operation_name} in {delay:.1f}s...")
                time.sleep(delay)
        
        # All attempts failed
        raise last_exception
    
    def get(self, url: str) -> str:
        """HTTP GET with retry logic."""
        def _get():
            # Simulate HTTP request (placeholder)
            import urllib.request
            response = urllib.request.urlopen(url, timeout=10)
            return response.read().decode('utf-8')
        
        return self.request_with_retry(_get, f"GET {url}")


def main():
    """Example usage."""
    client = NetworkClient(max_attempts=5, jitter=True)
    
    try:
        # This would normally make a real HTTP request
        # For demo, it's just a placeholder
        print("Network client initialized with retry logic")
        print(f"Max attempts: {client.max_attempts}")
        print(f"Circuit breaker enabled: threshold={client.circuit_breaker.failure_threshold}")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
```

---

## Execution and Monitoring

### Run the Workstream

```bash
python scripts/run_workstream.py --ws-id ws-example-03-error-handling
```

### Monitor in Real-Time

```bash
# Watch orchestrator logs
tail -f .worktrees/ws-example-03-error-handling/orchestrator.log

# Check circuit breaker state
python scripts/check_circuit_breaker.py ws-example-03-error-handling
```

---

## Troubleshooting

### Issue: Too many retries

**Cause**: `max_attempts` set too high  
**Fix**: Reduce to 3-5 attempts
```json
{
  "circuit_breaker": {
    "max_attempts": 3
  }
}
```

---

### Issue: Circuit breaker opens too quickly

**Cause**: `failure_threshold` too low  
**Fix**: Increase threshold or max_error_repeats
```json
{
  "circuit_breaker": {
    "max_error_repeats": 5  // Allow more errors before opening
  }
}
```

---

### Issue: Retries happen too slowly

**Cause**: Delays are too long  
**Fix**: Reduce initial_delay or use linear backoff
```json
{
  "retry": {
    "strategy": "linear",  // Instead of exponential
    "initial_delay": 0.5   // Start with 500ms
  }
}
```

---

## Best Practices

### ✅ When to Use Circuit Breaker

**Good for**:
- External API calls (may be down/slow)
- Database connections (may timeout)
- File I/O on network drives
- Any operation that can fail transiently

**Not good for**:
- Code compilation (fails permanently)
- Syntax errors (won't fix with retry)
- Validation errors (deterministic)

---

### ⚠️ Common Mistakes

1. **Too aggressive retries** → Overwhelm already-struggling service
2. **No jitter** → Thundering herd problem
3. **Wrong error patterns** → Circuit opens on recoverable errors
4. **Infinite timeouts** → Operations hang forever

---

## Learning Points

**Circuit Breaker prevents**:
- Cascading failures
- Resource exhaustion  
- Degraded performance

**Exponential Backoff provides**:
- Time for services to recover
- Reduced load during outages
- Progressive delay increase

**Jitter avoids**:
- Thundering herd
- Synchronized retries
- Load spikes

---

## Next Steps

- **Example 04**: Multi-Phase - Complex workflows with checkpoints
- **Example 05**: SAGA Pattern - Distributed transactions with compensation

---

**Last Updated**: 2025-11-22  
**Difficulty**: ⭐⭐ Intermediate  
**Execution Time**: 3-8 minutes (varies with retries)  
**Success Rate**: ~85% (designed to demonstrate both success and failure paths)
