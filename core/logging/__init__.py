"""Logging utilities.

DEPRECATED: Import from LOG_REVIEW_SUB_SYS.structured_logger instead.
This module is kept for backward compatibility only.
"""

import sys
from pathlib import Path

# Add LOG_REVIEW_SUB_SYS to path
log_review_path = Path(__file__).parent.parent.parent / "LOG_REVIEW_SUB_SYS"
if str(log_review_path) not in sys.path:
    sys.path.insert(0, str(log_review_path))

from structured_logger import StructuredLogger

__all__ = ["StructuredLogger"]
