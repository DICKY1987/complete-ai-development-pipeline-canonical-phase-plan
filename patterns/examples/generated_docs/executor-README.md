---
doc_id: DOC-PAT-EXECUTOR-README-912
---

# Module Documentation Template
# TEMPLATE: module-readme
# Variables: Executor, Execute individual workstream steps via tool adapters with retry logic, Domain (core.engine), - Exponential backoff retry
- Tool profile support
- Error capture and logging
- Timeout handling, from core.engine.executor import Executor

exec = Executor()
result = exec.execute_step(step)
# Pattern: EXEC-004 (Doc Standardizer)
# Time savings: 60-65% vs manual docs

---
doc_id: DOC-EXECUTOR-README-001
module: Executor
status: active
---

# Executor

## Purpose

Execute individual workstream steps via tool adapters with retry logic

## Architecture

- **Layer**: Domain (core.engine)
- **Dependencies**: core.engine.tools, config
- **Responsibilities**: Tool invocation, retry management, error capture, result logging

## Key Features

- Exponential backoff retry
- Tool profile support
- Error capture and logging
- Timeout handling

## Quick Start

```python
from core.engine.executor import Executor

exec = Executor()
result = exec.execute_step(step)
```

## API Reference

### Main Classes

#### Executor

Single step executor with retry and error handling

**Methods:**
- `execute_step(step: Step)`: Execute step via appropriate tool
- `execute_with_retry(step: Step)`: Execute with configurable retry logic

## Configuration

Configure retry behavior in `config/executor.yaml`

## Common Tasks

### Execute a Step

```python
exec = Executor()
result = exec.execute_step(step_obj)
```

### Execute with Custom Retries

```python
exec = Executor(max_retries=5)
result = exec.execute_with_retry(step_obj)
```

## Gotchas

- Timeout defaults to 300 seconds
- Retry delay doubles after each attempt

## Testing

```bash
pytest tests/engine/test_executor.py
```

## Related Modules

- Orchestrator
- Scheduler

---

**Status**: stable
**Owner**: @core-team
**Last Updated**: 2025-11-24
