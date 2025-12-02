---
doc_id: DOC-PAT-ORCHESTRATOR-README-913
---

# Module Documentation Template
# TEMPLATE: module-readme
# Variables: Orchestrator, Coordinate workstream execution across multiple tools with retry and circuit breaker patterns, Domain (core.engine), - Circuit breaker pattern
- Configurable retry logic
- Parallel workstream support
- Tool profile management, from core.engine.orchestrator import Orchestrator

orch = Orchestrator()
result = orch.execute_workstream('WS-001')
# Pattern: EXEC-004 (Doc Standardizer)
# Time savings: 60-65% vs manual docs

---
doc_id: DOC-ORCHESTRATOR-README-001
module: Orchestrator
status: active
---

# Orchestrator

## Purpose

Coordinate workstream execution across multiple tools with retry and circuit breaker patterns

## Architecture

- **Layer**: Domain (core.engine)
- **Dependencies**: core.state, config
- **Responsibilities**: Execute steps, manage tool invocations, handle failures

## Key Features

- Circuit breaker pattern
- Configurable retry logic
- Parallel workstream support
- Tool profile management

## Quick Start

```python
from core.engine.orchestrator import Orchestrator

orch = Orchestrator()
result = orch.execute_workstream('WS-001')
```

## API Reference

### Main Classes

#### Orchestrator

Main orchestration controller for workstream execution

**Methods:**
- `execute_workstream(workstream_id: str)`: Execute all steps in workstream
- `execute_step(workstream_id: str)`: Execute single step with retry

## Configuration

Configure via `config/orchestrator.yaml`

## Common Tasks

### Execute a Workstream

```python
orch = Orchestrator()
orch.execute_workstream('WS-001')
```

### Execute with Custom Config

```python
orch = Orchestrator(config_path='custom.yaml')
orch.execute_workstream('WS-001')
```

## Gotchas

- Circuit breaker opens after 3 consecutive failures
- Ensure database is initialized before use

## Testing

```bash
pytest tests/engine/test_orchestrator.py
```

## Related Modules

- Scheduler
- Executor

---

**Status**: stable  
**Owner**: @core-team  
**Last Updated**: 2025-11-24
