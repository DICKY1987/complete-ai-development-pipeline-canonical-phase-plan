"""Core Pipeline Implementation

The core module provides the central pipeline functionality:
- State management and persistence (core.state)
- Orchestration and execution (core.engine)
- Workstream planning and archiving (core.planning)
- AST parsing and code analysis (core.ast)

Public API:
    State Layer:
        - core.state.db.init_db()
        - core.state.crud.*
        - core.state.bundles.*
    
    Engine Layer:
        - core.engine.orchestrator.run_workstream()
        - core.engine.orchestrator.execute_workstreams_parallel()
        - core.engine.scheduler.build_execution_plan()
    
    Planning Layer:
        - core.planning.archive.auto_archive()
        - core.planning.ccpm_integration.*
        - core.planning.parallelism_detector.*
    
    AST Layer:
        - core.ast.extractors.*
        - core.ast.languages.python.*

For detailed documentation, see:
    - core/STRUCTURE.md - Architecture overview
    - core/dependencies.yaml - Module dependencies
    - core/{layer}/README.md - Layer-specific documentation
"""

__version__ = "2.0.0"

# Submodules
__all__ = [
    "state",
    "engine", 
    "planning",
    "ast",
]

