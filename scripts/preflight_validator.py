#!/usr/bin/env python3
"""
Pre-Flight Validator for Multi-Agent Orchestration
Validates prerequisites before execution
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-PREFLIGHT-VALIDATOR-221
# DOC_ID: DOC-SCRIPT-SCRIPTS-PREFLIGHT-VALIDATOR-158

import subprocess
import sys
import shutil
from pathlib import Path


class PreFlightValidator:
    """Validate prerequisites before multi-agent execution"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validations

        Returns:
            True if all validations passed (errors list is empty)
        """
        print("🔍 Running pre-flight validation...\n")

        self.check_git_clean()
        self.check_git_worktree_support()
        self.check_python_packages()
        self.check_tools()
        self.check_workstreams()
        self.check_disk_space()

        self.print_results()

        return len(self.errors) == 0

    def check_git_clean(self):
        """Ensure git working tree is clean"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            self.warnings.append(
                "Git working tree has uncommitted changes. "
                "Consider committing or stashing before running."
            )
        else:
            print("✅ Git working tree is clean")

    def check_git_worktree_support(self):
        """Check git worktree support"""
        result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.repo_root,
            capture_output=True
        )

        if result.returncode == 0:
            print("✅ Git worktree support available")
        else:
            self.errors.append(
                "Git worktree not supported. Upgrade git to version 2.5 or higher."
            )

    def check_python_packages(self):
        """Check required Python packages"""
        packages = {
            "networkx": "networkx",
        }

        for package, pip_name in packages.items():
            try:
                __import__(package)
                print(f"✅ {package} installed")
            except ImportError:
                self.errors.append(
                    f"{package} not installed. Run: pip install {pip_name}"
                )

    def check_tools(self):
        """Check required command-line tools"""
        tools = {
            "aider": "AI code editor (optional - set tool='codex' in workstreams if missing)",
            "sqlite3": "SQLite command-line tool"
        }

        for tool, description in tools.items():
            if sys.platform == "win32":
                cmd = ["where", tool]
            else:
                cmd = ["which", tool]

            result = subprocess.run(
                cmd,
                capture_output=True
            )

            if result.returncode == 0:
                print(f"✅ {tool} found")
            else:
                if tool == "aider":
                    self.warnings.append(f"{tool} not found in PATH - {description}")
                else:
                    self.warnings.append(f"{tool} not found - {description}")

    def check_workstreams(self):
        """Check workstream files exist and validate dependencies"""
        ws_dir = self.repo_root / "workstreams"

        if not ws_dir.exists():
            self.errors.append("workstreams/ directory not found")
            return

        ws_files = list(ws_dir.glob("ws-*.json"))

        if len(ws_files) == 0:
            self.errors.append("No workstream files (ws-*.json) found in workstreams/")
            return
        elif len(ws_files) < 10:
            self.warnings.append(
                f"Only {len(ws_files)} workstream files found (expected ~39)"
            )
        else:
            print(f"✅ Found {len(ws_files)} workstream files")

        # CRITICAL: Validate dependency graph is acyclic
        self.validate_dependencies(ws_files)

    def validate_dependencies(self, ws_files):
        """Validate workstream dependencies are acyclic (no circular deps)"""
        import json

        # Build dependency graph
        graph = {}
        all_ids = set()

        for ws_file in ws_files:
            try:
                data = json.loads(ws_file.read_text())
                ws_id = data.get('id', ws_file.stem)
                all_ids.add(ws_id)
                graph[ws_id] = data.get('depends_on', [])
            except Exception as e:
                self.warnings.append(f"Could not parse {ws_file.name}: {e}")
                continue

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        cycle_path = []

        def has_cycle(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in all_ids:
                    self.warnings.append(
                        f"Workstream {node} depends on non-existent {neighbor}"
                    )
                    continue

                if neighbor not in visited:
                    if has_cycle(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Cycle found!
                    cycle_start = path.index(neighbor)
                    cycle_path.extend(path[cycle_start:] + [neighbor])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        # Check each node
        for node in graph:
            if node not in visited:
                if has_cycle(node, []):
                    cycle_str = " -> ".join(cycle_path)
                    self.errors.append(
                        f"❌ Dependency cycle detected: {cycle_str}\n"
                        f"   This will cause infinite blocking. Fix workstream dependencies."
                    )
                    return

        print("✅ Dependency graph is valid (acyclic)")


    def check_disk_space(self):
        """Check available disk space"""
        try:
            stats = shutil.disk_usage(self.repo_root)
            free_gb = stats.free / (1024**3)

            # CRITICAL: Increased from 5 GB to 10 GB minimum
            # Calculation: 3 worktrees × 500 MB + logs + buffer = ~10 GB needed
            if free_gb < 10:
                self.errors.append(
                    f"Insufficient disk space: {free_gb:.1f} GB free (minimum 10 GB required)\n"
                    f"  Required for: 3 worktrees (~3 GB) + logs (~500 MB) + buffer (~6 GB)"
                )
            elif free_gb < 15:
                self.warnings.append(
                    f"Disk space: {free_gb:.1f} GB free (recommended: 15+ GB for safety margin)"
                )
            else:
                print(f"✅ Disk space: {free_gb:.1f} GB free")
        except Exception as e:
            self.warnings.append(f"Could not check disk space: {e}")

    def print_results(self):
        """Print validation results"""
        print("\n" + "="*70)

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
            print("\n⛔ Fix errors before proceeding.")
        else:
            print("\n✅ All pre-flight checks passed!")
            print("   Ready for multi-agent execution.")

        print("="*70 + "\n")


def main():
    """Main entry point"""
    repo_root = Path.cwd()

    # Check if we're in a git repository
    if not (repo_root / ".git").exists():
        print("❌ Not a git repository. Run from repository root.")
        return 1

    validator = PreFlightValidator(repo_root)
    success = validator.validate_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
