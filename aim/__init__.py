"""AIM (AI Tools Registry) Section

This section contains the AIM bridge and registry for AI tool coordination.
"""

from aim.exceptions import (
    AIMError,
    AIMRegistryNotFoundError,
    AIMCapabilityNotFoundError,
    AIMToolNotFoundError,
    AIMAdapterInvocationError,
    AIMAllToolsFailedError,
)

__all__ = [
    "bridge",
    "exceptions",
    "AIMError",
    "AIMRegistryNotFoundError",
    "AIMCapabilityNotFoundError",
    "AIMToolNotFoundError",
    "AIMAdapterInvocationError",
    "AIMAllToolsFailedError",
]
