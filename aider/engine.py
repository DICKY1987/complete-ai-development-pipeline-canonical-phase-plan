"""
Compatibility shim: re-export prompt engine from aider.engine
"""
from __future__ import annotations

from aider.engine import (  # type: ignore F401
    run_aider_edit,
    run_aider_fix,
    TemplateRender,
)
