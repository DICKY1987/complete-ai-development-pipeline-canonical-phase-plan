---
doc_id: DOC-GUIDE-UET-DEVELOPER-GUIDE-807
---

# UET Developer Guide
**Version**: 1.0.0

## Architecture
- DAG Builder: Topological sort for parallel execution
- Parallel Orchestrator: ThreadPoolExecutor with wave-based execution
- Patch Ledger: Unified diff tracking with state machine

## Testing
```powershell
pytest tests/integration/test_uet_migration.py -v
```
