---
doc_id: DOC-PAT-README-890
---

# Orchestrator integration

Add the hooks to your orchestrator's task execution method:

```python
from automation.integration.orchestrator_hooks import get_hooks

# Initialize once (at orchestrator startup)
hooks = get_hooks(db_path="patterns/metrics/pattern_automation.db")

def execute_task(task_spec):
    context = hooks.on_task_start(task_spec)

    try:
        result = _do_actual_execution(task_spec)
        hooks.on_task_complete(task_spec, result, context)
        return result
    except Exception as exc:
        result = {"success": False, "error": str(exc)}
        hooks.on_task_complete(task_spec, result, context)
        raise
```

Features: non-blocking, fault-tolerant logging, zero dependencies beyond stdlib, minimal overhead.
Disable by setting `enabled=False` on `PatternAutomationHooks`.
