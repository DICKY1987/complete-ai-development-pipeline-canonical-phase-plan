"""Scheduler - Backward Compatibility Adapter

Redirects to UET scheduler implementation.
"""
DOC_ID: DOC-PAT-CORE-ENGINE-SCHEDULER-401

from .uet_scheduler import UETScheduler as Scheduler

__all__ = ['Scheduler']
