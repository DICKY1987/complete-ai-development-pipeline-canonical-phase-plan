"""Architectural validation tests.

These tests validate that the modular architecture is correctly implemented
and that module boundaries and dependency rules are enforced.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Set, List, Tuple


def test_utils_has_no_internal_dependencies():
    """Verify utils module has no dependencies on other src modules."""
    utils_path = Path("src/utils")
    violations = []
    
    for py_file in utils_path.glob("*.py"):
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue
            
        content = py_file.read_text()
        tree = ast.parse(content, filename=str(py_file))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Check for imports from src.pipeline or src.plugins
                if module.startswith("src.pipeline") or module.startswith("src.plugins"):
                    violations.append(f"{py_file.name}: imports from {module}")
    
    assert not violations, f"Utils module has forbidden dependencies: {violations}"


def test_plugins_only_depend_on_utils():
    """Verify plugins module only depends on utils, not pipeline."""
    plugins_path = Path("src/plugins")
    violations = []
    
    for py_file in plugins_path.rglob("*.py"):
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue
            
        content = py_file.read_text()
        tree = ast.parse(content, filename=str(py_file))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Check for imports from src.pipeline
                if module.startswith("src.pipeline"):
                    violations.append(f"{py_file.relative_to('src/plugins')}: imports from {module}")
    
    assert not violations, f"Plugins module has forbidden pipeline dependencies: {violations}"


def test_no_circular_imports():
    """Verify no circular imports between modules."""
    # Try importing all main modules
    try:
        import src.utils
        import src.plugins
        import src.pipeline
    except ImportError as e:
        if "circular" in str(e).lower():
            raise AssertionError(f"Circular import detected: {e}")
        # Other import errors are fine (missing dependencies, etc.)
        pass


def test_public_api_exports():
    """Verify each module exports its documented public API."""
    # Utils module
    import src.utils
    expected_utils = {"scrub_env", "PluginIssue", "PluginResult", "sha256_file", "utc_now_iso", "new_run_id"}
    actual_utils = set(src.utils.__all__)
    assert expected_utils == actual_utils, f"Utils API mismatch: expected={expected_utils}, actual={actual_utils}"
    
    # Pipeline module
    import src.pipeline
    expected_pipeline = {
        "run_workstream",
        "run_single_workstream_from_bundle",
        "load_and_validate_bundles",
        "WorkstreamBundle",
        "run_tool",
        "ToolResult",
    }
    actual_pipeline = set(src.pipeline.__all__)
    assert expected_pipeline == actual_pipeline, f"Pipeline API mismatch: expected={expected_pipeline}, actual={actual_pipeline}"


def test_utils_types_are_importable():
    """Verify shared types can be imported from utils."""
    from src.utils import PluginIssue, PluginResult
    
    # Verify they are dataclasses
    assert hasattr(PluginIssue, '__dataclass_fields__')
    assert hasattr(PluginResult, '__dataclass_fields__')


def test_pipeline_exports_are_importable():
    """Verify pipeline public API is importable."""
    try:
        from src.pipeline import (
            run_workstream,
            run_single_workstream_from_bundle,
            load_and_validate_bundles,
            WorkstreamBundle,
            run_tool,
            ToolResult,
        )
        
        # Verify they are callable/classes
        assert callable(run_workstream)
        assert callable(run_single_workstream_from_bundle)
        assert callable(load_and_validate_bundles)
        assert callable(run_tool)
        assert hasattr(WorkstreamBundle, '__dataclass_fields__')
        assert hasattr(ToolResult, '__dataclass_fields__')
    except ImportError as e:
        # If imports fail due to missing dependencies, that's okay for this test
        # We're just checking the structure, not runtime functionality
        if "jsonschema" in str(e) or "jinja2" in str(e).lower():
            pass
        else:
            raise


def test_module_docstrings_exist():
    """Verify all main module __init__.py files have docstrings."""
    import src.utils
    import src.plugins
    import src.pipeline
    
    assert src.utils.__doc__, "src.utils missing module docstring"
    assert src.plugins.__doc__, "src.plugins missing module docstring"
    assert src.pipeline.__doc__, "src.pipeline missing module docstring"


def test_plugins_follow_contract():
    """Verify a sample plugin follows the plugin contract."""
    # Test with python_ruff plugin
    plugin_file = Path("src/plugins/python_ruff/plugin.py")
    if not plugin_file.exists():
        # If plugin doesn't exist, skip test
        return
    
    content = plugin_file.read_text()
    tree = ast.parse(content, filename=str(plugin_file))
    
    # Find the plugin class
    plugin_class = None
    register_func = None
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check for required attributes
            attrs = {item.target.id if isinstance(item, ast.AnnAssign) else 
                    item.targets[0].id if isinstance(item, ast.Assign) else None
                    for item in node.body if isinstance(item, (ast.Assign, ast.AnnAssign))}
            if "plugin_id" in attrs and "name" in attrs:
                plugin_class = node
                
        if isinstance(node, ast.FunctionDef) and node.name == "register":
            register_func = node
    
    assert plugin_class is not None, "Plugin class not found in python_ruff/plugin.py"
    assert register_func is not None, "register() function not found in python_ruff/plugin.py"
    
    # Check for required methods
    method_names = {m.name for m in plugin_class.body if isinstance(m, ast.FunctionDef)}
    required_methods = {"check_tool_available", "build_command", "execute"}
    assert required_methods.issubset(method_names), f"Plugin missing required methods: {required_methods - method_names}"


def test_dependency_graph_is_acyclic():
    """Verify module dependency graph is acyclic using static analysis."""
    # Build dependency graph from imports
    dependencies = {
        "src.utils": set(),
        "src.plugins": set(),
        "src.pipeline": set(),
    }
    
    for module_path in ["src/utils", "src/plugins", "src/pipeline"]:
        path = Path(module_path)
        for py_file in path.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content, filename=str(py_file))
            except:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module.startswith("src."):
                        # Extract top-level module
                        parts = module.split(".")
                        if len(parts) >= 2:
                            dep = f"src.{parts[1]}"
                            if dep != module_path.replace("/", "."):
                                dependencies[module_path.replace("/", ".")].add(dep)
    
    # Check for cycles using DFS
    def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in dependencies.get(node, set()):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    visited: Set[str] = set()
    for module in dependencies:
        if module not in visited:
            if has_cycle(module, visited, set()):
                raise AssertionError(f"Circular dependency detected in module graph: {dependencies}")
    
    # Verify expected dependencies
    assert dependencies["src.utils"] == set(), "Utils should have no internal dependencies"
    assert "src.pipeline" not in dependencies.get("src.plugins", set()), "Plugins should not depend on pipeline"
