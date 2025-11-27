"""Scheduler - Backward Compatibility Adapter

Exposes the UET scheduler primitives under the legacy filename so
downstream tests can import `ExecutionScheduler`, `Task`, and
`create_task_from_spec` from this module path.
"""

from .m010001_uet_scheduler import (
    ExecutionScheduler,
    Task,
    create_task_from_spec,
)

# Preserve the older alias to keep minimal surface changes.
Scheduler = ExecutionScheduler

__all__ = ["ExecutionScheduler", "Task", "create_task_from_spec", "Scheduler"]
