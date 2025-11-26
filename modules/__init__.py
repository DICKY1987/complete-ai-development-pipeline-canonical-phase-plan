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
