"""Orchestrator - Backward Compatibility Adapter

This module provides backward compatibility for code importing
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator.

The actual implementation has been replaced by the UET (Universal
Execution Templates) engine in core.engine.uet_orchestrator.

Migration path:
  OLD: from modules.core_engine.m010001_orchestrator import Orchestrator
  NEW: from modules.core_engine.m010001_uet_orchestrator import Orchestrator

This adapter will be removed in a future release.
"""
DOC_ID: DOC-PAT-CORE-ENGINE-ORCHESTRATOR-393

import warnings

# Import UET orchestrator
from .uet_orchestrator import Orchestrator as UETOrchestrator

# Backward compatibility alias
Orchestrator = UETOrchestrator

# Deprecation warning (commented out for now to avoid noise)
# warnings.warn(
#     "core.engine.orchestrator is deprecated. "
#     "Use core.engine.uet_orchestrator instead.",
#     DeprecationWarning,
#     stacklevel=2
# )

__all__ = ['Orchestrator']
