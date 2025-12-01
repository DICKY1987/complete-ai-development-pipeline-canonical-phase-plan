"""
Compatibility shim for root engine/ → core.engine/

The UET engine in core/engine/ is now canonical.
Some features from the old job queue system are not yet ported.

Deprecated: Use 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.*' directly
Remove after: 2025-12-31
"""

import warnings

warnings.warn(
    "Importing from 'engine' is deprecated. "
    "Use 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.*' instead. "
    "Job queue features are being ported to core.engine.",
    DeprecationWarning,
    stacklevel=2
)

# Map what we can to core.engine
try:
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator import Orchestrator
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.executor import Executor
except ImportError:
    # Fallback to old implementation if needed
    pass

__all__ = ['Orchestrator', 'Executor']
