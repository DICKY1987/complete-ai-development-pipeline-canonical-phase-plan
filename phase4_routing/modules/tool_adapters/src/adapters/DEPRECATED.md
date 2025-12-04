# DEPRECATED: Adapters Consolidated

**Date:** 2025-12-04
**Status:** ARCHIVED

## Summary

This directory previously contained duplicate implementations of tool adapters.
All adapter code has been consolidated into the canonical location: **`core/adapters/`**

## Migration

### Old Import (DEPRECATED)
```python
from phase4_routing.modules.tool_adapters.src.adapters.base import ToolAdapter
from phase4_routing.modules.tool_adapters.src.adapters.registry import AdapterRegistry
```

### New Import (USE THIS)
```python
from core.adapters.base import ToolAdapter
from core.adapters.registry import AdapterRegistry
```

## Archive Location

Original files moved to:
```
_ARCHIVE/phase4_tool_adapters_duplicate_20251204_143544/
```

## Rationale

- **core/adapters/** is newer (2025-12-04 vs 2025-12-03)
- **core/adapters/** already used by core.engine.executor
- **core/adapters/** follows canonical import patterns per CI_PATH_STANDARDS.md
- Eliminates maintenance burden of parallel implementations
