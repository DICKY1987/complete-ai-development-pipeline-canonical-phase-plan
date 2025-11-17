"""Utils Module - Shared utility functions and data structures.

This module provides common utilities used across the pipeline and plugin modules.
It has no business logic dependencies and serves as a foundation layer.

Modules:
    - env: Environment variable scrubbing for subprocess execution
    - types: Shared data structures (PluginResult, PluginIssue)
    - hashing: Hash computation utilities (sha256_file)
    - time: Time and timestamp utilities (utc_now_iso, new_run_id)
    - jsonl_manager: JSONL file operations (append, rotate_if_needed)

Public API:
    All utilities are public and can be imported by higher-level modules.
"""

from __future__ import annotations

from .env import scrub_env
from .types import PluginIssue, PluginResult
from .hashing import sha256_file
from .time import utc_now_iso, new_run_id

__all__ = [
    # Environment
    "scrub_env",
    # Types
    "PluginIssue",
    "PluginResult",
    # Hashing
    "sha256_file",
    # Time
    "utc_now_iso",
    "new_run_id",
]

