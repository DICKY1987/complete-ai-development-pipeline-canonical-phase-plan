"""Core framework modules

Public API:
- BootstrapOrchestrator: Main entry point for project setup
- ExecutionScheduler: Task dependency resolution and scheduling
- ResilientExecutor: Fault-tolerant tool execution
- ProgressTracker: Real-time execution monitoring
- AdapterRegistry: Tool adapter management

Usage:
    from core import BootstrapOrchestrator, ExecutionScheduler

    # Bootstrap a project
    bootstrap = BootstrapOrchestrator("/path/to/project")
    result = bootstrap.run()

    # Schedule and execute tasks
    scheduler = ExecutionScheduler()
    scheduler.add_tasks(tasks)
    order = scheduler.get_execution_order()

Internal modules (use at your own risk):
- core.state: State management internals
- core.adapters: Tool adapter implementations  
- core.engine: Orchestration engine internals
- core.bootstrap: Bootstrap implementation
"""

# Public API exports
try:
    from core.bootstrap.orchestrator import BootstrapOrchestrator
except ImportError:
    BootstrapOrchestrator = None

try:
    from modules.core_engine.m010001_scheduler import ExecutionScheduler
except ImportError:
    ExecutionScheduler = None

try:
    from core.engine.resilience.executor import ResilientExecutor
except ImportError:
    ResilientExecutor = None

try:
    from core.engine.monitoring.progress import ProgressTracker
except ImportError:
    ProgressTracker = None

try:
    from core.adapters.registry import AdapterRegistry
except ImportError:
    AdapterRegistry = None

__all__ = [
    'BootstrapOrchestrator',
    'ExecutionScheduler',
    'ResilientExecutor',
    'ProgressTracker',
    'AdapterRegistry',
]
