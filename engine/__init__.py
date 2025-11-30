"""
Compatibility shim for root engine/ → core.engine/

The UET engine in core/engine/ is now canonical.
Some features from the old job queue system are not yet ported.

Deprecated: Use 'from core.engine.*' directly
Remove after: 2025-12-31
"""

import warnings

warnings.warn(
    "Importing from 'engine' is deprecated. "
    "Use 'from core.engine.*' instead. "
    "Job queue features are being ported to core.engine.",
    DeprecationWarning,
    stacklevel=2
)

# Map what we can to core.engine
try:
    from core.engine.orchestrator import Orchestrator
    from core.engine.executor import Executor
except ImportError:
    # Fallback to old implementation if needed
    pass

__all__ = ['Orchestrator', 'Executor']
