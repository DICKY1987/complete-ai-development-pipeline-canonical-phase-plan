"""Core State Management

Database operations, CRUD, workstream bundles, and worktree lifecycle.

This module is the data/persistence layer with no internal dependencies.
All other layers depend on it for state management.

Public API:
    Database:
        - db.init_db() - Initialize database schema
        - db.get_connection() - Get database connection
    
    CRUD Operations:
        - crud.create_run()
        - crud.get_run()
        - crud.create_workstream()
        - crud.get_workstream()
        - crud.record_step_attempt()
        - crud.record_error()
        - crud.record_event()
    
    Bundle Management:
        - bundles.WorkstreamBundle - Bundle dataclass
        - bundles.load_and_validate_bundles()
        - bundles.build_dependency_graph()
        - bundles.sync_bundles_to_db()
    
    Worktree:
        - worktree.create_worktree_for_ws()
        - worktree.get_repo_root()

Usage:
    from modules.core_state.m010003_db import init_db
    from modules.core_state.m010003_crud import create_workstream
    from modules.core_state.m010003_bundles import load_and_validate_bundles
    
    init_db()
    bundles = load_and_validate_bundles("workstreams/")
    ws = create_workstream(...)

For details, see:
    - core/state/README.md
    - core/state/dependencies.yaml
"""

__all__ = [
    "db",
    "db_sqlite",
    "crud",
    "bundles",
    "worktree",
    "audit_logger",
    "task_queue",
]
