import os
import warnings

# Emit a one-time deprecation warning to encourage migration to core.*
if os.environ.get("PIPELINE_DEPRECATION_WARNINGS", "1") not in ("0", "false", "False"):
    warnings.warn(
        "Deprecated import path: 'src.pipeline'. Use 'core.*' modules instead. "
        "The 'src.pipeline' package remains as a compatibility layer during migration.",
        DeprecationWarning,
        stacklevel=2,
    )

__all__ = []
