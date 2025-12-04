# DEDUPLICATION REPORT - 2025-12-04 14:35:44

## ADAPTER DEDUPLICATION

### Decision: Keep core/adapters (NEWER, CANONICAL)
- core/adapters/base.py          - LastWrite: 2025-12-04 06:06:27 AM (KEEP)
- core/adapters/registry.py      - LastWrite: 2025-12-04 06:06:27 AM (KEEP)
- core/adapters/subprocess_adapter.py - LastWrite: 2025-12-04 06:06:27 AM (KEEP)

### Archive: phase4_routing/modules/tool_adapters/src/adapters
- base.py          - LastWrite: 2025-12-03 07:05:14 PM (ARCHIVE)
- registry.py      - LastWrite: 2025-12-03 07:05:14 PM (ARCHIVE)
- subprocess_adapter.py - LastWrite: 2025-12-03 07:05:14 PM (ARCHIVE)

### Import Usage:
- core.adapters: ACTIVE (used by core.engine.executor, tests/adapters/*, tests/interfaces/*)
- phase4_routing.modules.tool_adapters.src.adapters: INTERNAL ONLY (used by phase4 tests)

### Action Plan:
1. Archive phase4_routing/modules/tool_adapters/src/adapters to _ARCHIVE
2. Update phase4 tests to import from core.adapters
3. Create redirect/deprecation marker in phase4 location
