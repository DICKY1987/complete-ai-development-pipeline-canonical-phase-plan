---
doc_id: DOC-GUIDE-COMMON-PATTERNS-190
---

# Common Patterns

**Purpose**: Standard coding patterns and best practices for this repository  
**Audience**: Developers and AI code assistants  
**Last Updated**: 2025-11-25

---

## Code Style

### Python

**Follow**:
- PEP 8 style guide
- Black formatting (line length: 100)
- Type hints on public APIs
- Docstrings for public functions/classes

**Example**:
```python
from typing import List, Optional

def process_workstream(
    workstream_id: str,
    options: Optional[dict] = None
) -> List[str]:
    """
    Process a workstream and return task IDs.
    
    Args:
        workstream_id: Unique workstream identifier
        options: Optional processing options
        
    Returns:
        List of task IDs created
        
    Raises:
        ValueError: If workstream_id is invalid
    """
    if not workstream_id:
        raise ValueError("workstream_id cannot be empty")
    
    # Implementation...
    return ["task-001", "task-002"]
```

---

## Error Handling

### Pattern: Circuit Breaker

**Used in**: `engine/executor.py`, `core/engine/orchestrator.py`

**Purpose**: Prevent cascading failures in distributed systems

**Implementation**:
```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, reject requests
    - HALF_OPEN: Testing recovery, allow limited requests
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )
```

**Usage**:
```python
# Wrap unreliable operations
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

def call_external_api():
    # Unreliable operation
    ...

# Protected call
try:
    result = breaker.call(call_external_api)
except Exception:
    # Circuit is open or call failed
    logger.error("API call failed")
```

---

## Testing Patterns

### Pattern: AAA (Arrange-Act-Assert)

**Standard test structure**:

```python
def test_workstream_creation():
    # Arrange - Set up test data
    manager = WorkstreamManager(db_path=":memory:")
    workstream_data = {
        "id": "WS-001",
        "name": "Test Workstream",
        "status": "pending"
    }
    
    # Act - Execute the operation
    result = manager.create_workstream(workstream_data)
    
    # Assert - Verify expectations
    assert result.id == "WS-001"
    assert result.status == "pending"
    assert manager.get_workstream("WS-001") is not None
```

### Pattern: Fixtures for Common Setup

**Location**: `tests/conftest.py`

```python
import pytest
from core.state.db import StateManager

@pytest.fixture
def db_manager():
    """Provide in-memory database for tests."""
    manager = StateManager(":memory:")
    manager.init_schema()
    yield manager
    manager.close()

@pytest.fixture
def sample_workstream():
    """Provide sample workstream data."""
    return {
        "id": "WS-TEST-001",
        "name": "Test Workstream",
        "phases": ["phase1", "phase2"]
    }
```

**Usage**:
```python
def test_with_fixtures(db_manager, sample_workstream):
    # Use fixtures directly
    db_manager.save_workstream(sample_workstream)
    loaded = db_manager.get_workstream(sample_workstream["id"])
    assert loaded["name"] == "Test Workstream"
```

---

## Plugin Architecture

### Pattern: Abstract Base Class for Plugins

**Used in**: `error/plugins/base.py`

```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class Error:
    """Detected error."""
    file: str
    line: int
    message: str
    severity: str
    fixable: bool = False

class Plugin(ABC):
    """
    Base class for error detection plugins.
    
    All plugins must implement parse() method.
    Plugins that can auto-fix should implement fix().
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Languages this plugin supports."""
        pass
    
    @abstractmethod
    def parse(self, log_content: str) -> List[Error]:
        """
        Parse error output and return structured errors.
        
        Args:
            log_content: Raw output from linter/checker
            
        Returns:
            List of detected errors
        """
        pass
    
    def fix(self, error: Error) -> bool:
        """
        Attempt to automatically fix an error.
        
        Args:
            error: Error to fix
            
        Returns:
            True if fixed, False otherwise
            
        Note:
            Override this method if plugin supports auto-fix.
        """
        return False
```

**Implementing a plugin**:
```python
from error.plugins.base import Plugin, Error
import re

class PythonRuffPlugin(Plugin):
    """Ruff linter plugin for Python."""
    
    @property
    def name(self) -> str:
        return "python_ruff"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def parse(self, log_content: str) -> List[Error]:
        """Parse Ruff output."""
        errors = []
        pattern = r"(.+):(\d+):(\d+): (.+) \[(.+)\]"
        
        for line in log_content.split('\n'):
            match = re.match(pattern, line)
            if match:
                file, line_num, col, message, code = match.groups()
                errors.append(Error(
                    file=file,
                    line=int(line_num),
                    message=message,
                    severity=self._get_severity(code),
                    fixable=code.startswith("F")  # F-codes are auto-fixable
                ))
        
        return errors
    
    def fix(self, error: Error) -> bool:
        """Auto-fix using ruff --fix."""
        if not error.fixable:
            return False
        # Implementation...
        return True
```

---

## State Management

### Pattern: Repository Pattern for Database Access

**Used in**: `core/state/db.py`

```python
from typing import Optional, List
import sqlite3

class WorkstreamRepository:
    """Repository for workstream persistence."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def save(self, workstream: dict) -> None:
        """Save or update workstream."""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO workstreams (id, name, status, data)
            VALUES (?, ?, ?, ?)
            """,
            (
                workstream["id"],
                workstream["name"],
                workstream["status"],
                json.dumps(workstream)
            )
        )
        self.conn.commit()
    
    def find_by_id(self, workstream_id: str) -> Optional[dict]:
        """Find workstream by ID."""
        cursor = self.conn.execute(
            "SELECT data FROM workstreams WHERE id = ?",
            (workstream_id,)
        )
        row = cursor.fetchone()
        return json.loads(row["data"]) if row else None
    
    def find_by_status(self, status: str) -> List[dict]:
        """Find all workstreams with given status."""
        cursor = self.conn.execute(
            "SELECT data FROM workstreams WHERE status = ?",
            (status,)
        )
        return [json.loads(row["data"]) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
```

---

## Logging

### Pattern: Structured Logging

```python
import logging
from typing import Any

# Configure logger
logger = logging.getLogger(__name__)

def log_operation(operation: str, **context: Any):
    """Log operation with structured context."""
    logger.info(
        f"Operation: {operation}",
        extra={
            "operation": operation,
            **context
        }
    )

# Usage
log_operation(
    "workstream_created",
    workstream_id="WS-001",
    phase="planning",
    duration_ms=150
)
```

**Output format**:
```
2025-11-25 10:30:45 INFO Operation: workstream_created operation=workstream_created workstream_id=WS-001 phase=planning duration_ms=150
```

---

## Async Patterns (if needed)

### Pattern: Async/Await for I/O

```python
import asyncio
from typing import List

async def fetch_workstream_status(workstream_id: str) -> dict:
    """Async fetch workstream status."""
    # Simulate async I/O
    await asyncio.sleep(0.1)
    return {"id": workstream_id, "status": "running"}

async def fetch_all_statuses(workstream_ids: List[str]) -> List[dict]:
    """Fetch multiple statuses concurrently."""
    tasks = [fetch_workstream_status(ws_id) for ws_id in workstream_ids]
    return await asyncio.gather(*tasks)

# Usage
async def main():
    ids = ["WS-001", "WS-002", "WS-003"]
    statuses = await fetch_all_statuses(ids)
    print(statuses)

# Run
asyncio.run(main())
```

---

## Configuration

### Pattern: Dataclass-based Config

```python
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class ExecutorConfig:
    """Executor configuration."""
    max_workers: int = 4
    retry_attempts: int = 3
    timeout_seconds: int = 300
    circuit_breaker_threshold: int = 5
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExecutorConfig":
        """Load config from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data.get("executor", {}))

# Usage
config = ExecutorConfig.from_yaml("config/settings.yaml")
executor = Executor(config)
```

---

## Anti-Patterns to Avoid

### ❌ Don't: God Objects
```python
# Bad - one class does everything
class WorkstreamManager:
    def create(self): ...
    def update(self): ...
    def delete(self): ...
    def validate(self): ...
    def execute(self): ...
    def monitor(self): ...
    def report(self): ...
```

### ✅ Do: Single Responsibility
```python
# Good - separate concerns
class WorkstreamRepository:
    def create(self): ...
    def update(self): ...
    def delete(self): ...

class WorkstreamValidator:
    def validate(self): ...

class WorkstreamExecutor:
    def execute(self): ...
```

### ❌ Don't: Bare Except
```python
# Bad
try:
    dangerous_operation()
except:  # Catches everything, even KeyboardInterrupt!
    pass
```

### ✅ Do: Specific Exceptions
```python
# Good
try:
    dangerous_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except IOError as e:
    logger.error(f"IO error: {e}")
```

### ❌ Don't: Magic Numbers
```python
# Bad
if retry_count > 5:  # What does 5 mean?
    ...
```

### ✅ Do: Named Constants
```python
# Good
MAX_RETRY_ATTEMPTS = 5

if retry_count > MAX_RETRY_ATTEMPTS:
    ...
```

---

## Quick Reference

### Import Order
```python
# 1. Standard library
import os
import sys
from typing import List

# 2. Third-party
import yaml
import pytest

# 3. Local modules
from core.engine.orchestrator import Orchestrator
from error.plugins.base import Plugin
```

### Naming Conventions
- **Classes**: `PascalCase` (WorkstreamManager)
- **Functions/Variables**: `snake_case` (get_workstream)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_RETRY_ATTEMPTS)
- **Private**: `_leading_underscore` (_internal_method)

---

**Last Updated**: 2025-11-25  
**Maintained By**: Development team  
**Next Review**: After major architectural changes
