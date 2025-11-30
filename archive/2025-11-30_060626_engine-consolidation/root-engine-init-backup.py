"""
Engine package for the AI Development Pipeline.

This package provides the core execution engine that coordinates
tool adapters, manages job lifecycle, and maintains state.

Architecture:
- orchestrator/: Job orchestration and queue management
- adapters/: Tool-specific adapters (Aider, Codex, tests, git)
- state_store/: Job and workstream state persistence
- interfaces/: Protocol definitions for section contracts
- types.py: Shared type definitions
"""
DOC_ID: DOC-PAT-ENGINE-INIT-353
DOC_ID: DOC-PAT-ENGINE-INIT-309

__version__ = "0.1.0"
