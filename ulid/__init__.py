# DOC_LINK: DOC-PAT-ULID-INIT-372
# DOC_LINK: DOC-PAT-ULID-INIT-328
from __future__ import annotations

import time


def new() -> str:
    """Generate a simple timestamp-based identifier."""
    stamp = int(time.time() * 1000)
    return f"ULID{stamp:012d}"
