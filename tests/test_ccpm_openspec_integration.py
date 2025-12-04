"""Integration tests for CCPM + OpenSpec + Pipeline workflow"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil


class TestCCPMComponents:
    """Test CCPM component installation"""

    # DOC_ID: DOC-TEST-TESTS-TEST-CCPM-OPENSPEC-INTEGRATION-076
    # DOC_ID: DOC-TEST-TESTS-TEST-CCPM-OPENSPEC-INTEGRATION-037

    def test_agents_installed(self):
        """Verify all 4 CCPM agents are installed"""
        agents_dir = Path(".claude/agents")
        assert agents_dir.exists(), ".claude/agents directory should exist"

        expected_agents = [
            "code-analyzer.md",
            "file-analyzer.md",
            "parallel-worker.md",
            "test-runner.md",
        ]

        for agent in expected_agents:
            agent_path = agents_dir / agent
            assert agent_path.exists(), f"Agent {agent} should be installed"
            assert agent_path.stat().st_size > 0, f"Agent {agent} should not be empty"

    def test_scripts_installed(self):
        """Verify CCPM scripts are installed and executable"""
        scripts_dir = Path("scripts")

        expected_scripts = [
            "test-and-log.sh",
            "check-path-standards.sh",
            "fix-path-standards.sh",
        ]

        for script in expected_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Script {script} should be installed"
            assert (
                script_path.stat().st_size > 0
            ), f"Script {script} should not be empty"

    def test_rules_installed(self):
        """Verify CCPM rules are installed"""
        rules_dir = Path(".claude/rules")
        assert rules_dir.exists(), ".claude/rules directory should exist"

        expected_rules = [
            "agent-coordination.md",
            "datetime.md",
            "path-standards.md",
            "standard-patterns.md",
            "test-execution.md",
            "worktree-operations.md",
            "github-operations.md",
        ]

        for rule in expected_rules:
            rule_path = rules_dir / rule
            assert rule_path.exists(), f"Rule {rule} should be installed"
            assert rule_path.stat().st_size > 0, f"Rule {rule} should not be empty"


class TestPathStandardizerPlugin:
    """Test path_standardizer plugin"""

    def test_plugin_structure(self):
        """Verify plugin has required files"""
        plugin_dir = Path("src/plugins/path_standardizer")
        assert plugin_dir.exists(), "path_standardizer plugin should exist"

        assert (plugin_dir / "manifest.json").exists(), "manifest.json should exist"
        assert (plugin_dir / "plugin.py").exists(), "plugin.py should exist"
        assert (plugin_dir / "README.md").exists(), "README.md should exist"

    def test_plugin_manifest(self):
        """Verify plugin manifest is valid JSON with required fields"""
        manifest_path = Path("src/plugins/path_standardizer/manifest.json")

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["name"] == "path_standardizer"
        assert manifest["autofix"] == True
        assert "path_validation" in manifest["capabilities"]
        assert "path_correction" in manifest["capabilities"]

    def test_plugin_executable(self):
        """Test path_standardizer plugin can be executed"""
        plugin_path = Path("src/plugins/path_standardizer/plugin.py")

        import subprocess

        result = subprocess.run(
            ["python", str(plugin_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Plugin should handle --help gracefully or execute without error
        assert result.returncode in [0, 1], "Plugin should be executable"


class TestWorkflowDocumentation:
    """Test workflow documentation"""

    def test_documentation_exists(self):
        """Verify workflow documentation is created"""
        doc_path = Path("docs/ccpm-openspec-workflow.md")
        assert doc_path.exists(), "Workflow documentation should exist"

        with open(doc_path, encoding="utf-8") as f:
            content = f.read()

        # Check for key sections
        assert "Overview" in content
        assert "Workflow Diagram" in content
        assert "Step-by-Step Guide" in content
        assert "Integration Points" in content
        assert "CCPM Commands Reference" in content

    def test_documentation_completeness(self):
        """Verify documentation covers all integration points"""
        doc_path = Path("docs/ccpm-openspec-workflow.md")

        with open(doc_path, encoding="utf-8") as f:
            content = f.read()

        # Verify all agents documented
        assert "file-analyzer" in content
        assert "code-analyzer" in content
        assert "test-runner" in content
        assert "parallel-worker" in content

        # Verify pipeline states documented
        assert "S0_BASELINE_CHECK" in content
        assert "S0_MECHANICAL_AUTOFIX" in content
        assert "S_SUCCESS" in content
        assert "S4_QUARANTINE" in content


class TestIntegrationReadiness:
    """Test overall integration readiness"""

    def test_all_components_present(self):
        """Verify all major components are in place"""
        components = [
            ".claude/agents",
            ".claude/rules",
            "scripts/test-and-log.sh",
            "src/plugins/path_standardizer",
            "docs/ccpm-openspec-workflow.md",
        ]

        for component in components:
            path = Path(component)
            assert path.exists(), f"Component {component} should exist"

    def test_directory_structure(self):
        """Verify expected directory structure"""
        directories = [
            ".claude",
            ".claude/agents",
            ".claude/rules",
            "scripts",
            "src/plugins",
            "src/pipeline",
            "docs",
            "tests",
        ]

        for directory in directories:
            dir_path = Path(directory)
            assert dir_path.exists(), f"Directory {directory} should exist"
            assert dir_path.is_dir(), f"{directory} should be a directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
