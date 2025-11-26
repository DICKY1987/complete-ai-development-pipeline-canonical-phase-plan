"""Scheduler - Backward Compatibility Adapter

Redirects to UET scheduler implementation.
"""

from .uet_scheduler import UETScheduler as Scheduler

__all__ = ['Scheduler']
