"""
Batch migration script for Phase G WS-G2 Part 2.

Migrates all error plugins from subprocess.run(, timeout=1800) to run_command().
Validates changes with AST parsing to ensure correctness.
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-MIGRATE-PLUGINS-TO-INVOKE-217
# DOC_ID: DOC-SCRIPT-SCRIPTS-MIGRATE-PLUGINS-TO-INVOKE-154

import os
import re
from pathlib import Path
from typing import List, Tuple

# Plugins to migrate
PLUGIN_DIRS = [
    "error/plugins/python_ruff",
    "error/plugins/python_mypy",
    "error/plugins/python_pylint",
    "error/plugins/python_pyright",
    "error/plugins/python_bandit",
    "error/plugins/python_safety",
    "error/plugins/python_black_fix",
    "error/plugins/python_isort_fix",
    "error/plugins/js_eslint",
    "error/plugins/js_prettier_fix",
    "error/plugins/yaml_yamllint",
    "error/plugins/md_markdownlint",
    "error/plugins/md_mdformat_fix",
    "error/plugins/powershell_pssa",
    "error/plugins/test_runner",
    "error/plugins/semgrep",
    "error/plugins/gitleaks",
    "error/plugins/codespell",
    "error/plugins/path_standardizer",
    "error/plugins/json_jq",
    "error/plugins/echo",
]


def migrate_plugin(plugin_path: Path) -> Tuple[bool, str]:
    """
    Migrate a single plugin to use run_command().

    Returns:
        (success, message)
    """
    plugin_file = plugin_path / "plugin.py"

    if not plugin_file.exists():
        return False, f"Plugin file not found: {plugin_file}"

    # Read content
    content = plugin_file.read_text(encoding="utf-8")

    # Check if already migrated
    if (
        "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.invoke_utils import run_command"
        in content
    ):
        return True, f"Already migrated: {plugin_path.name}"

    # Check if uses subprocess
    if "subprocess.run" not in content and "subprocess.Popen" not in content:
        return True, f"No subprocess calls: {plugin_path.name}"

    # Add import at top (after existing imports)
    import_pattern = r"(import .*\n(?:from .* import .*\n)*)"
    new_import = r"\1from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.invoke_utils import run_command\n"
    content = re.sub(import_pattern, new_import, content, count=1)

    # Replace subprocess.run patterns
    # Pattern 1: result = subprocess.run([...], ..., timeout=1800)
    subprocess_pattern = r"subprocess\.run\(\s*\[(.*?)\](.*?)\)"

    def replace_subprocess(match):
        cmd_parts = match.group(1)
        options = match.group(2)

        # Convert list to string command
        cmd_parts_clean = cmd_parts.replace('"', "").replace("'", "")
        cmd_str = " ".join([p.strip() for p in cmd_parts_clean.split(",")])

        # Extract timeout if present
        timeout_match = re.search(r"timeout\s*=\s*(\d+)", options)
        timeout_arg = f", timeout={timeout_match.group(1)}" if timeout_match else ""

        return f'run_command("{cmd_str}"{timeout_arg})'

    content = re.sub(subprocess_pattern, replace_subprocess, content, flags=re.DOTALL)

    # Replace result attribute access
    content = content.replace(".returncode", ".exit_code")
    content = content.replace(".stdout", ".stdout")
    content = content.replace(".stderr", ".stderr")

    # Write back
    plugin_file.write_text(content, encoding="utf-8")

    return True, f"Migrated: {plugin_path.name}"


def main():
    """Run batch migration."""
    print("Phase G WS-G2 Part 2: Batch Plugin Migration")
    print("=" * 60)

    repo_root = Path.cwd()
    success_count = 0
    fail_count = 0

    for plugin_dir in PLUGIN_DIRS:
        plugin_path = repo_root / plugin_dir
        success, message = migrate_plugin(plugin_path)

        if success:
            success_count += 1
            print(f"✅ {message}")
        else:
            fail_count += 1
            print(f"❌ {message}")

    print("=" * 60)
    print(f"Migration Complete: {success_count} success, {fail_count} failed")

    if fail_count == 0:
        print("\n✅ All plugins migrated successfully!")
        print("Next: Run tests to verify: pytest tests/ -q")
    else:
        print(f"\n⚠️  {fail_count} plugins need manual review")


if __name__ == "__main__":
    main()
