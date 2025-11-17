"""
Compatibility shim: re-export GitHub sync helpers from pm.integrations.github_sync
"""
from __future__ import annotations

# Re-export public API for backward compatibility
from pm.integrations.github_sync import (  # type: ignore F401
    comment,
    ensure_epic,
    set_status,
    post_lifecycle_comment,
    LifecycleEvent,
)
