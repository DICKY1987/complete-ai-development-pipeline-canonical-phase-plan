"""
Modules package - Module-centric architecture

All 33 modules organized with ULID-based file naming.

Import from module level:
    from modules.core_state import get_connection  # ✅
    from modules.core_state.010003_db import get_connection  # ❌ (won't work)

Module organization:
- Core: core-state, core-engine, core-planning, core-ast
- Error: error-engine, error-plugin-*
- AIM: aim-cli, aim-environment, aim-registry, aim-tests
- PM: pm-integrations
- Specifications: specifications-tools
"""

__version__ = "1.0.0"
__all__ = [
    # Core modules
    "core_state",
    "core_engine",
    "core_planning",
    "core_ast",
    
    # Error modules
    "error_engine",
    
    # Error plugins
    "error_plugin_codespell",
    "error_plugin_echo",
    "error_plugin_gitleaks",
    "error_plugin_json_jq",
    "error_plugin_js_eslint",
    "error_plugin_js_prettier_fix",
    "error_plugin_md_markdownlint",
    "error_plugin_md_mdformat_fix",
    "error_plugin_path_standardizer",
    "error_plugin_powershell_pssa",
    "error_plugin_python_bandit",
    "error_plugin_python_black_fix",
    "error_plugin_python_isort_fix",
    "error_plugin_python_mypy",
    "error_plugin_python_pylint",
    "error_plugin_python_pyright",
    "error_plugin_python_ruff",
    "error_plugin_python_safety",
    "error_plugin_semgrep",
    "error_plugin_test_runner",
    "error_plugin_yaml_yamllint",
    
    # AIM modules
    "aim_cli",
    "aim_environment",
    "aim_registry",
    "aim_tests",
    
    # PM modules
    "pm_integrations",
    
    # Specifications
    "specifications_tools",
]

# Register underscore-friendly aliases for hyphenated module directories.
import importlib.util
import importlib.abc
import sys
from pathlib import Path

_modules_dir = Path(__file__).parent
_alias_map = {
    d.name.replace("-", "_"): d
    for d in _modules_dir.iterdir()
    if d.is_dir() and not d.name.startswith("_") and d.name != "__pycache__"
}


class _HyphenModuleFinder(importlib.abc.MetaPathFinder):
    """Resolve modules.<alias> to hyphenated directories under modules/."""

    def find_spec(self, fullname, path=None, target=None):
        prefix = __name__ + "."
        if not fullname.startswith(prefix):
            return None
        remainder = fullname[len(prefix) :]
        alias = remainder.split(".", 1)[0]
        subdir = _alias_map.get(alias)
        if not subdir:
            return None
        init_path = subdir / "__init__.py"
        if not init_path.exists():
            return None
        # Only handle package-level import; let package __init__ manage submodules.
        if "." in remainder:
            return None
        return importlib.util.spec_from_file_location(
            fullname,
            init_path,
            submodule_search_locations=[str(subdir)],
        )


_finder = _HyphenModuleFinder()
if not any(isinstance(f, _HyphenModuleFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _finder)
