---
doc_id: DOC-PAT-BEHAVIOR-003-896
pattern_id: PATTERN-003
version: 1.0.0
status: active
created: 2025-12-04
category: behavioral
priority: medium
---

# PATTERN-003: Smart Retry with Backoff

## Overview

**Pattern Name**: Smart Retry with Backoff
**Problem**: Rapid-fire retry attempts waste time without allowing transient issues to resolve
**Solution**: Exponential backoff with max attempts, intelligent error classification
**Impact**: Saves 10-15s per retry cycle, prevents rate limiting

---

## Problem Statement

### Observed Behavior
```
Lines 12-20: Same "apply_patch" command tried 3 times sequentially
21:17:38 - First attempt ❌ FAILED
21:18:18 - Second attempt (40s later) ❌ FAILED
21:18:27 - Third attempt (9s later) ❌ FAILED

Pattern: Immediate retry without delay or error analysis
Result: 3 failures in rapid succession, no time for resolution
```

### Root Cause
Naive retry logic without backoff:
- Immediate retry on failure (no delay)
- No exponential backoff between attempts
- No classification of retryable vs non-retryable errors
- No max retry limit or timeout
- Same operation parameters on each retry (no adaptation)

### Cost
- **10-15 seconds wasted** per rapid-fire retry cycle
- **Resource exhaustion** (network, API rate limits)
- **Log spam** (same error repeated)
- **False hope** (retrying non-retryable errors)

---

## Solution Pattern

### Core Principle
**Retry with exponential backoff, classify errors, adapt parameters**

### Implementation

```python
import time
from typing import Callable, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    """Error classification for retry logic"""
    RETRYABLE = "retryable"           # Network timeout, rate limit, etc.
    NON_RETRYABLE = "non_retryable"   # Invalid input, missing tool, etc.
    UNKNOWN = "unknown"               # Unclassified error

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0            # Initial delay in seconds
    max_delay: float = 60.0            # Maximum delay
    exponential_base: float = 2.0      # Backoff multiplier
    jitter: bool = True                # Add randomness to prevent thundering herd

class RetryableError(Exception):
    """Errors that should be retried"""
    pass

class NonRetryableError(Exception):
    """Errors that should not be retried"""
    pass

class SmartRetry:
    """PATTERN-003: Smart retry with exponential backoff"""

    # Error classification rules
    RETRYABLE_ERRORS = {
        "Connection refused",
        "Connection timed out",
        "Rate limit exceeded",
        "Service unavailable",
        "Temporary failure",
        "Resource temporarily unavailable",
    }

    NON_RETRYABLE_ERRORS = {
        "File not found",
        "Permission denied",
        "Invalid syntax",
        "MISSING_TOOL",
        "UNSUPPORTED_EXT",
    }

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempt_count = 0
        self.total_delay = 0.0

    def classify_error(self, error: Exception) -> ErrorType:
        """Classify error as retryable or not"""
        error_str = str(error)

        # Check retryable patterns
        for pattern in self.RETRYABLE_ERRORS:
            if pattern.lower() in error_str.lower():
                return ErrorType.RETRYABLE

        # Check non-retryable patterns
        for pattern in self.NON_RETRYABLE_ERRORS:
            if pattern.lower() in error_str.lower():
                return ErrorType.NON_RETRYABLE

        # Specific exception types
        if isinstance(error, (FileNotFoundError, PermissionError, SyntaxError)):
            return ErrorType.NON_RETRYABLE

        if isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorType.RETRYABLE

        return ErrorType.UNKNOWN

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt (exponential backoff)"""
        import random

        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)

        # Cap at max_delay
        delay = min(delay, self.config.max_delay)

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_amount = delay * 0.1  # ±10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0.0, delay)

    def execute(
        self,
        operation: Callable[[], Any],
        error_handler: Optional[Callable[[Exception, int], None]] = None
    ) -> Any:
        """Execute operation with smart retry"""

        last_error = None

        for attempt in range(self.config.max_attempts):
            self.attempt_count = attempt + 1

            try:
                # Execute operation
                result = operation()

                # Success
                if attempt > 0:
                    print(f"SUCCESS after {attempt + 1} attempts (total delay: {self.total_delay:.1f}s)")

                return result

            except Exception as e:
                last_error = e

                # Classify error
                error_type = self.classify_error(e)

                # Don't retry non-retryable errors
                if error_type == ErrorType.NON_RETRYABLE:
                    print(f"NON_RETRYABLE_ERROR: {e}")
                    raise

                # Last attempt - don't wait
                if attempt == self.config.max_attempts - 1:
                    break

                # Calculate delay
                delay = self.calculate_delay(attempt)
                self.total_delay += delay

                # Log retry attempt
                print(
                    f"RETRY: Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}\n"
                    f"Error type: {error_type.value}\n"
                    f"Retrying in {delay:.1f}s..."
                )

                # Call error handler if provided
                if error_handler:
                    error_handler(e, attempt)

                # Wait before retry
                time.sleep(delay)

        # All attempts failed
        raise RuntimeError(
            f"RETRY_EXHAUSTED: Operation failed after {self.config.max_attempts} attempts.\n"
            f"Total delay: {self.total_delay:.1f}s\n"
            f"Last error: {last_error}"
        ) from last_error


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Decorator for smart retry with exponential backoff"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay
            )
            retrier = SmartRetry(config)

            return retrier.execute(lambda: func(*args, **kwargs))

        return wrapper

    return decorator


class AdaptiveRetry(SmartRetry):
    """PATTERN-003: Adaptive retry with parameter adjustment"""

    def __init__(self, config: Optional[RetryConfig] = None):
        super().__init__(config)
        self.adaptations = []

    def execute_with_adaptation(
        self,
        operation: Callable[[dict], Any],
        initial_params: dict,
        adapt_func: Optional[Callable[[dict, int], dict]] = None
    ) -> Any:
        """Execute operation with parameter adaptation on retry"""

        params = initial_params.copy()
        last_error = None

        for attempt in range(self.config.max_attempts):
            try:
                # Execute with current parameters
                result = operation(params)

                if attempt > 0:
                    print(f"SUCCESS after {attempt + 1} attempts with adaptations: {self.adaptations}")

                return result

            except Exception as e:
                last_error = e

                # Classify error
                error_type = self.classify_error(e)

                if error_type == ErrorType.NON_RETRYABLE:
                    raise

                if attempt == self.config.max_attempts - 1:
                    break

                # Adapt parameters for next attempt
                if adapt_func:
                    params = adapt_func(params, attempt)
                    self.adaptations.append(f"attempt_{attempt+1}: {params}")

                # Standard backoff
                delay = self.calculate_delay(attempt)
                print(f"ADAPTIVE_RETRY: Attempt {attempt + 1} failed, adapting parameters and retrying...")
                time.sleep(delay)

        raise RuntimeError(
            f"ADAPTIVE_RETRY_EXHAUSTED: Operation failed after {self.config.max_attempts} attempts.\n"
            f"Adaptations tried: {self.adaptations}\n"
            f"Last error: {last_error}"
        ) from last_error
```

---

## Usage Examples

### Example 1: Basic Retry with Backoff

```python
# Simple retry with default config
retrier = SmartRetry()

def flaky_operation():
    import random
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError("Connection timeout")
    return "Success"

try:
    result = retrier.execute(flaky_operation)
    print(result)
except RuntimeError as e:
    print(f"Failed after retries: {e}")
```

### Example 2: Custom Retry Configuration

```python
# Custom config: 5 attempts, start at 2s, max 30s
config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)

retrier = SmartRetry(config)

def network_call():
    # Simulated network call
    response = requests.get("https://api.example.com/data", timeout=5)
    return response.json()

result = retrier.execute(network_call)
```

### Example 3: Decorator Pattern

```python
@retry_with_backoff(max_attempts=3, base_delay=1.0)
def fetch_data(url: str):
    """Automatically retried with exponential backoff"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Usage
data = fetch_data("https://api.example.com/data")
```

### Example 4: Adaptive Retry with Parameter Changes

```python
# Adapt parameters on retry
def adapt_timeout(params: dict, attempt: int) -> dict:
    """Increase timeout on each retry"""
    params['timeout'] = params.get('timeout', 5) * 2
    return params

retrier = AdaptiveRetry()

def api_call(params: dict):
    timeout = params.get('timeout', 5)
    response = requests.get("https://api.example.com/data", timeout=timeout)
    return response.json()

result = retrier.execute_with_adaptation(
    operation=api_call,
    initial_params={'timeout': 5},
    adapt_func=adapt_timeout
)
```

### Example 5: Error Handler Callback

```python
# Track retry attempts
retry_log = []

def error_handler(error: Exception, attempt: int):
    """Log each retry attempt"""
    retry_log.append({
        'attempt': attempt,
        'error': str(error),
        'timestamp': time.time()
    })

retrier = SmartRetry()

result = retrier.execute(
    operation=risky_operation,
    error_handler=error_handler
)

print(f"Retry log: {retry_log}")
```

---

## Integration Points

### With EXEC-003 (Tool Guards)

```python
from core.patterns.exec003 import ToolGuard

def execute_with_retry_and_guard(command: str, guard: ToolGuard):
    """Combine PATTERN-003 with EXEC-003"""

    # Gate 1: Tool exists (EXEC-003)
    tool_name = command.split()[0]
    guard.require_tool(tool_name)

    # Gate 2: Execute with retry (PATTERN-003)
    retrier = SmartRetry()

    def execute_command():
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        return result

    return retrier.execute(execute_command)
```

### With PATTERN-002 (Ground Truth Verification)

```python
from core.patterns.pattern002 import execute_with_verification

def execute_with_retry_and_verification(
    command: str,
    output_file: str,
    max_attempts: int = 3
):
    """Combine PATTERN-003 with PATTERN-002"""

    retrier = SmartRetry(RetryConfig(max_attempts=max_attempts))

    def verified_execution():
        return execute_with_verification(
            command,
            expected_outcome=lambda: Path(output_file).exists(),
            outcome_description=f"{output_file} created"
        )

    return retrier.execute(verified_execution)
```

---

## Decision Tree

```
Operation Can Fail Transiently?
  │
  ├─ Network/API call?
  │   YES → Use SmartRetry (transient failures common)
  │   NO  ↓
  │
  ├─ File I/O?
  │   YES → Use retry for network file systems, skip for local
  │   NO  ↓
  │
  ├─ External tool/command?
  │   YES → Classify error first, then decide retry
  │   NO  ↓
  │
  ├─ Error is retryable?
  │   YES → Use SmartRetry
  │   NO  → Fail fast, don't retry
  │
  └─ Can adapt parameters?
      YES → Use AdaptiveRetry
      NO  → Use SmartRetry
```

---

## Metrics

### Prevents
- **Rapid-fire failures**: 100% elimination
- **Rate limiting**: Prevented by backoff
- **Wasted retry time**: 10-15s saved per cycle

### Performance
- **Overhead**:
  - First attempt: 0ms (no retry needed)
  - Retry attempts: Exponential backoff (1s, 2s, 4s, ...)
- **Savings**: 10-15s per prevented rapid-fire cycle
- **ROI**: Improves success rate by allowing transient issues to resolve

---

## Backoff Schedule

### Default Configuration
```
Attempt 1: Immediate
Attempt 2: Wait 1.0s (total: 1.0s)
Attempt 3: Wait 2.0s (total: 3.0s)
Attempt 4: Wait 4.0s (total: 7.0s)
Attempt 5: Wait 8.0s (total: 15.0s)
```

### Aggressive Configuration (fast fail)
```
max_attempts: 3
base_delay: 0.5s
exponential_base: 1.5

Attempt 1: Immediate
Attempt 2: Wait 0.5s (total: 0.5s)
Attempt 3: Wait 0.75s (total: 1.25s)
```

### Conservative Configuration (resilient)
```
max_attempts: 5
base_delay: 2.0s
exponential_base: 2.0

Attempt 1: Immediate
Attempt 2: Wait 2.0s (total: 2.0s)
Attempt 3: Wait 4.0s (total: 6.0s)
Attempt 4: Wait 8.0s (total: 14.0s)
Attempt 5: Wait 16.0s (total: 30.0s)
```

---

## Anti-Patterns (Don't Do This)

### ❌ Anti-Pattern 1: Immediate Retry
```python
# BAD: No delay between attempts
for attempt in range(3):
    try:
        return operation()
    except:
        pass  # Try again immediately
```

### ❌ Anti-Pattern 2: Fixed Delay
```python
# BAD: Same delay every time
for attempt in range(3):
    try:
        return operation()
    except:
        time.sleep(1)  # Always 1s, no backoff
```

### ❌ Anti-Pattern 3: Retry Non-Retryable Errors
```python
# BAD: Retrying errors that won't resolve
for attempt in range(3):
    try:
        return subprocess.run("nonexistent_command", check=True)
    except FileNotFoundError:
        time.sleep(1)  # Won't help, command doesn't exist!
```

### ✅ Correct Pattern: Smart Retry with Backoff
```python
# GOOD: Exponential backoff, error classification
retrier = SmartRetry()
result = retrier.execute(operation)
```

---

## Testing Strategy

```python
import pytest
from unittest.mock import Mock

def test_retry_success_after_failures():
    """Test PATTERN-003: Success after transient failures"""
    retrier = SmartRetry(RetryConfig(max_attempts=3, base_delay=0.1))

    call_count = 0
    def flaky_op():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Transient error")
        return "Success"

    result = retrier.execute(flaky_op)
    assert result == "Success"
    assert call_count == 3

def test_non_retryable_error_fails_fast():
    """Test PATTERN-003: Non-retryable errors don't retry"""
    retrier = SmartRetry()

    call_count = 0
    def bad_op():
        nonlocal call_count
        call_count += 1
        raise FileNotFoundError("File missing")

    with pytest.raises(FileNotFoundError):
        retrier.execute(bad_op)

    assert call_count == 1  # Only tried once

def test_exponential_backoff():
    """Test PATTERN-003: Delays increase exponentially"""
    config = RetryConfig(max_attempts=4, base_delay=1.0, jitter=False)
    retrier = SmartRetry(config)

    delays = [retrier.calculate_delay(i) for i in range(4)]

    # Should be: 1.0, 2.0, 4.0, 8.0
    assert delays == [1.0, 2.0, 4.0, 8.0]
```

---

## Implementation Checklist

- [ ] Implement SmartRetry class with exponential backoff
- [ ] Implement error classification logic
- [ ] Add RetryConfig for customization
- [ ] Implement retry_with_backoff decorator
- [ ] Implement AdaptiveRetry for parameter adaptation
- [ ] Add jitter to prevent thundering herd
- [ ] Add unit tests for retry logic
- [ ] Add unit tests for error classification
- [ ] Add unit tests for backoff calculation
- [ ] Document retryable vs non-retryable error patterns
- [ ] Add metrics tracking (retry attempts, success rate)

---

## References

- **Source**: `codex_log_analysis_report.md` Section 2.3
- **Related Patterns**: EXEC-003 (Tool Guards), PATTERN-002 (Ground Truth)
- **Implementation**: `core/patterns/pattern003.py`
- **Tests**: `tests/patterns/test_pattern003.py`

---

**Status**: ✅ Ready for Implementation
**Priority**: Medium (improves resilience)
**Effort**: Low (3-4 hours)
