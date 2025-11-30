"""Core Planning Utilities

Workstream planning, generation, archiving, and lifecycle management.

This module provides utilities for workstream lifecycle:
- Automated planning (future v2.0)
- Archive completed workstreams
- CCPM project management integration
- Parallelism detection and analysis

Public API:
    Planning:
        - planner.plan_workstreams_from_spec() - Automated generation (stub)
    
    Archiving:
        - archive.auto_archive() - Package completed workstream
    
    CCPM Integration:
        - ccpm_integration.CCPMIntegration - Bidirectional sync
        - ccpm_integration.task_to_workstream()
        - ccpm_integration.sync_workstream_result()
    
    Parallelism:
        - parallelism_detector.detect_parallel_opportunities()
        - parallelism_detector.detect_conflict_groups()

Usage:
    from modules.core_planning.m010002_archive import auto_archive
    from modules.core_planning.m010002_parallelism_detector import detect_parallel_opportunities
    
    # Archive completed workstream
    archive_path = auto_archive(worktree_path, archive_dir)
    
    # Analyze parallelism
    profile = detect_parallel_opportunities(bundles)
    print(f"Max concurrent: {profile['max_parallelism']}")

For details, see:
    - core/planning/README.md
    - core/planning/dependencies.yaml
"""
DOC_ID: DOC-PAT-CORE-PLANNING-INIT-408

__all__ = [
    "planner",
    "archive",
    "ccpm_integration",
    "parallelism_detector",
]
