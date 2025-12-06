---
doc_id: DOC-CORE-DEPRECATED-879
---

# DEPRECATED: Bootstrap Orchestrator Consolidated

**Date:** 2025-12-04
**Status:** ARCHIVED

## Summary

This module previously contained duplicate implementation of bootstrap orchestration.
All bootstrap code has been consolidated into: **`core/bootstrap/`**

## Migration

### Old Import (DEPRECATED)
```python
from phase0_bootstrap.modules.bootstrap_orchestrator.src.orchestrator import Orchestrator
from phase0_bootstrap.modules.bootstrap_orchestrator.src.discovery import discover
```

### New Import (USE THIS)
```python
from core.bootstrap.orchestrator import Orchestrator
from core.bootstrap.discovery import discover
```

## Archive Location
```
_ARCHIVE/phase0_bootstrap_orchestrator_duplicate_20251204_143705/
```

## Rationale

- **core/bootstrap/** is newer (2025-12-04 vs 2025-12-03)
- **core/bootstrap/** follows canonical import patterns
- Eliminates duplicate maintenance
