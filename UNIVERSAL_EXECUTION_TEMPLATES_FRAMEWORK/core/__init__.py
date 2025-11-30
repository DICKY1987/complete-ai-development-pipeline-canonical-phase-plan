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
# DOC_ID: DOC-CORE-CORE-INIT-131

import importlib
import importlib.util
import sys
from pathlib import Path

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
    "BootstrapOrchestrator",
    "ExecutionScheduler",
    "ResilientExecutor",
    "ProgressTracker",
    "AdapterRegistry",
]


def _alias_module(fullname: str, target_path: Path):
    """Load a module from an absolute path and register it under fullname."""
    if fullname in sys.modules:
        return sys.modules[fullname]
    spec = importlib.util.spec_from_file_location(fullname, target_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[fullname] = module
        spec.loader.exec_module(module)
        return module
    return None


def _alias_existing(fullname: str, target: str):
    """Alias an already importable module under a new name."""
    try:
        module = importlib.import_module(target)
    except Exception:
        return None
    sys.modules[fullname] = module
    return module


def _install_compatibility_aliases():
    """Provide legacy import paths when UETF shadows the repo root."""
    repo_root = Path(__file__).resolve().parents[2]
    compat_files = {
        "core.prompts": repo_root / "core" / "prompts.py",
        "core.openspec_parser": repo_root / "core" / "openspec_parser.py",
        "core.invoke_utils": repo_root / "core" / "invoke_utils.py",
    }
    for fullname, path in compat_files.items():
        if path.exists():
            _alias_module(fullname, path)

    # Keep legacy aliases for specific files; prefer native core package for engine/ast.


_install_compatibility_aliases()
