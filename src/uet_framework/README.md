# Universal Execution Templates (UET) Framework

The UET Framework provides a standardized approach to execution templates and autonomous intelligence management.

## Contents

### `aim/` - Autonomous Intelligence Management
Contains modules for managing autonomous AI operations:
- `bridge.py` - Bridge functionality for connecting AI components
- `pool_interface.py` - Interface for managing AI resource pools

## Purpose

The UET Framework enables:
- Standardized execution templates across the pipeline
- Autonomous intelligence management and coordination
- Resource pooling and management for AI operations
- Bridge functionality for component integration

## Architecture

The framework follows a modular architecture:
1. **AIM Module**: Manages autonomous intelligence operations
2. **Bridge Layer**: Connects different AI components and systems
3. **Pool Interface**: Manages shared resources and coordination

## Usage

Import UET Framework modules in your code:

```python
from src.uet_framework.aim import bridge
from src.uet_framework.aim.pool_interface import PoolInterface
```

## Integration

The UET Framework integrates with:
- Master Splinter for workstream coordination
- Core engine for execution
- Pattern system for standardized behaviors
