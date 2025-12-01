"""PM (Project Management) Section

This section implements CCPM-inspired workflows for spec-driven development:
- PRD (Product Requirements Document) creation and management
- Epic planning and task decomposition
- Optional GitHub issue synchronization
- Parallel task orchestration with worktree support

Architecture:
- pm/models.py - Data classes (PRD, Epic, Task)
- pm/prd.py - PRD management
- pm/epic.py - Epic management
- pm/bridge.py - Format conversions (OpenSpec ↔ CCPM ↔ Workstream)
- pm/github_client.py - GitHub API wrapper (optional)
- pm/event_handler.py - Pipeline event listener

Integration:
- pm/bridge.py ↔ core/planning/ccpm_integration.py
- pm/event_handler.py ← core/engine/orchestrator.py (events)

See pm/CONTRACT.md for detailed interface specifications.
"""
# DOC_ID: DOC-PM-PM-INIT-018
# DOC_ID: DOC-PM-PM-INIT-012

from pathlib import Path

# Package metadata
__version__ = "1.0.0"
__contract_version__ = "CCPM_CONTRACT_V1"

# Public API (will be populated as modules are implemented)
__all__ = [
    "models",
    "prd", 
    "epic",
    "bridge",
    "github_client",
    "event_handler",
]

# Base paths (relative to repository root)
REPO_ROOT = Path(__file__).parent.parent
PM_ROOT = Path(__file__).parent
WORKSPACE_ROOT = PM_ROOT / "workspace"
TEMPLATES_ROOT = PM_ROOT / "templates"

# Ensure workspace directories exist (lazy creation)
def _ensure_workspace_dirs():
    """Create workspace directories if they don't exist."""
    (WORKSPACE_ROOT / "prds").mkdir(parents=True, exist_ok=True)
    (WORKSPACE_ROOT / "epics").mkdir(parents=True, exist_ok=True)

# Don't auto-create on import (explicit opt-in)
# _ensure_workspace_dirs()
