"""
DEPRECATED: This module has been consolidated into core.planning.ccpm_integration

Redirect for backward compatibility.
Original file archived: _ARCHIVE/phase1_ccpm_integration_duplicate_20251204_143728/
"""

# Explicit imports for clarity
# Redirect to canonical location
from core.planning.ccpm_integration import *
from core.planning.ccpm_integration import (
    HAS_PM,
    detect_conflicts,
    epic_to_parallel_workstreams,
    task_to_workstream,
    validate_parallel_safety,
)
