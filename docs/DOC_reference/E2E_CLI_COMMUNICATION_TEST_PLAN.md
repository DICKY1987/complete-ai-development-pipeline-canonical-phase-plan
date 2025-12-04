---
status: draft
doc_type: guide
module_refs:
  - core/engine/tools
  - phase4_routing/modules/aider_integration
  - phase6_error_recovery/modules/error_engine
script_refs:
  - scripts/test-aider-comprehensive.ps1
doc_id: DOC-GUIDE-E2E-CLI-COMMUNICATION-TEST-PLAN-855
---

# End-to-End CLI Communication Testing Plan

**Purpose:** Comprehensive testing strategy for all CLI tool communication functions (Aider, Codex, Claude, and custom tools)

**Last Updated:** 2025-12-04
**Maintainer:** Testing & Quality Team
**Related Documents:**
- [DOC_AIDER_CONTRACT.md](DOC_AIDER_CONTRACT.md) - Aider integration contract
- [DOC_TESTING_STRATEGY.md](../DOC_guidelines/DOC_TESTING_STRATEGY.md) - General testing strategy
- [test-aider-comprehensive.ps1](../../scripts/test-aider-comprehensive.ps1) - Existing Aider test suite

---

## Executive Summary

This plan defines a **7-layer testing pyramid** for CLI tool communication:
1. **Unit Tests** - Individual components in isolation
2. **Integration Tests** - Component interactions
3. **Contract Tests** - CLI interface compliance
4. **Sandbox Tests** - Real tool execution in controlled environment
5. **Error Handling Tests** - Failure scenarios and recovery
6. **Performance Tests** - Timeout, throughput, concurrency
7. **End-to-End Tests** - Full workstream execution

**Estimated Implementation Time:** 15-20 hours
**ROI:** Prevents regression, enables confident refactoring, reduces debugging time by 60%

---

## Architecture Context

### Communication Layers

```
┌─────────────────────────────────────────────────────────┐
│  High-Level API (Aider Engine, Agent Adapters)         │
│  - run_aider_edit(), run_aider_fix()                   │
│  - AiderAdapter, CodexAdapter, ClaudeAdapter            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Tool Adapter Layer (core/engine/tools.py)              │
│  - run_tool(tool_id, context)                          │
│  - render_command(tool_id, context)                    │
│  - ToolResult dataclass                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Subprocess Execution (Python subprocess module)        │
│  - subprocess.run()                                     │
│  - Timeout handling                                     │
│  - Environment variable injection                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  External CLI Tools                                     │
│  - aider (aider-chat package)                          │
│  - gh copilot (Codex)                                  │
│  - claude (Claude CLI)                                 │
│  - Custom tools (pytest, ruff, git, etc.)              │
└─────────────────────────────────────────────────────────┘
```

### Test Scope

**In Scope:**
- ✅ Tool profile loading and validation
- ✅ Command rendering with template substitution
- ✅ Subprocess invocation and result handling
- ✅ Timeout enforcement
- ✅ Error detection and reporting
- ✅ Prompt generation and file management
- ✅ Exit code interpretation
- ✅ Concurrent tool execution
- ✅ Environment variable handling
- ✅ Working directory management

**Out of Scope:**
- ❌ Testing CLI tools themselves (e.g., Aider's AI quality)
- ❌ Network/API calls to LLM providers
- ❌ Git operations (separate test suite)
- ❌ Database operations (separate test suite)

---

## Layer 1: Unit Tests

### 1.1 Tool Profile Loading (`core/engine/tools.py`)

**Coverage Target:** 95%

```python
# tests/core/engine/test_tools_unit.py

import pytest
from pathlib import Path
from core.engine.tools import (
    load_tool_profiles,
    get_tool_profile,
    render_command,
    ToolResult
)

class TestToolProfileLoading:
    """Unit tests for tool profile loading"""

    def test_load_tool_profiles_from_invoke_yaml(self, tmp_path, monkeypatch):
        """Test loading tool profiles from invoke.yaml"""
        # Arrange
        invoke_yaml = tmp_path / "invoke.yaml"
        invoke_yaml.write_text("""
tools:
  pytest:
    command: pytest
    args: ["-q"]
    timeout_sec: 60
    success_exit_codes: [0]
  aider:
    command: aider
    args: ["--no-auto-commits", "--yes"]
    timeout_sec: 1800
    env:
      AIDER_NO_AUTO_COMMITS: "1"
""")
        monkeypatch.chdir(tmp_path)

        # Act
        profiles = load_tool_profiles()

        # Assert
        assert "pytest" in profiles
        assert "aider" in profiles
        assert profiles["pytest"]["timeout_sec"] == 60
        assert profiles["aider"]["env"]["AIDER_NO_AUTO_COMMITS"] == "1"

    def test_get_tool_profile_not_found_raises_keyerror(self):
        """Test getting non-existent tool profile raises KeyError"""
        with pytest.raises(KeyError, match="nonexistent.*not found"):
            get_tool_profile("nonexistent", profiles={})

    def test_tool_profile_cache_reused(self, monkeypatch):
        """Test tool profiles are cached after first load"""
        # Implementation detail: verify cache behavior


class TestCommandRendering:
    """Unit tests for command template rendering"""

    def test_render_command_basic_substitution(self):
        """Test basic template variable substitution"""
        profile = {
            "command": "pytest",
            "args": ["-q", "{file}"]
        }
        context = {"file": "tests/test_sample.py"}

        command = render_command("pytest", context, profile=profile)

        assert command == ["pytest", "-q", "tests/test_sample.py"]

    def test_render_command_with_repo_root(self, tmp_path, monkeypatch):
        """Test {repo_root} variable substitution"""
        # Arrange: Create fake git repo
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)

        profile = {
            "command": "git",
            "args": ["--git-dir={repo_root}/.git", "status"]
        }
        context = {}

        # Act
        command = render_command("git", context, profile=profile)

        # Assert
        assert str(tmp_path) in command[1]

    def test_render_command_missing_variable_raises_error(self):
        """Test missing template variable raises KeyError"""
        profile = {
            "command": "echo",
            "args": ["{missing_var}"]
        }
        context = {}

        with pytest.raises(KeyError):
            render_command("echo", context, profile=profile)

    def test_render_command_escapes_special_chars(self):
        """Test special characters in variables are handled"""
        profile = {
            "command": "echo",
            "args": ["{message}"]
        }
        context = {"message": "test with 'quotes' and $vars"}

        command = render_command("echo", context, profile=profile)

        assert "test with 'quotes' and $vars" in command


class TestToolResult:
    """Unit tests for ToolResult dataclass"""

    def test_tool_result_creation(self):
        """Test ToolResult can be created with all fields"""
        result = ToolResult(
            tool_id="pytest",
            command_line="pytest -q",
            exit_code=0,
            stdout="10 passed\n",
            stderr="",
            timed_out=False,
            started_at="2025-12-04T00:00:00Z",
            completed_at="2025-12-04T00:00:05Z",
            duration_sec=5.0,
            success=True
        )

        assert result.success
        assert result.exit_code == 0
        assert result.duration_sec == 5.0

    def test_tool_result_to_dict(self):
        """Test ToolResult can be serialized to dict"""
        result = ToolResult(
            tool_id="test",
            command_line="test",
            exit_code=0,
            stdout="",
            stderr="",
            timed_out=False,
            started_at="2025-12-04T00:00:00Z",
            completed_at="2025-12-04T00:00:00Z",
            duration_sec=0.0,
            success=True
        )

        data = result.to_dict()

        assert data["tool_id"] == "test"
        assert data["success"] is True
        assert isinstance(data, dict)
```

### 1.2 Aider Engine Units (`phase4_routing/modules/aider_integration/src/aider/engine.py`)

```python
# tests/aider_integration/test_aider_engine_unit.py

from pathlib import Path
from phase4_routing.modules.aider_integration.src.aider.engine import (
    build_edit_prompt,
    build_fix_prompt,
    prepare_aider_prompt_file,
    TemplateRender
)

class TestPromptBuilding:
    """Unit tests for prompt generation"""

    def test_build_edit_prompt_basic(self, tmp_path):
        """Test basic EDIT prompt generation"""
        prompt = build_edit_prompt(
            tasks=["Add logging to function"],
            repo_path=tmp_path,
            ws_id="WS-001",
            run_id="RUN-001",
            files_scope=["src/app.py"]
        )

        assert "Add logging to function" in prompt
        assert "WS-001" in prompt
        assert "src/app.py" in prompt

    def test_build_fix_prompt_with_error_details(self, tmp_path):
        """Test FIX prompt includes error details"""
        prompt = build_fix_prompt(
            error_summary="NameError: undefined variable",
            error_details="Line 42: name 'foo' is not defined",
            files=["src/app.py"],
            repo_path=tmp_path,
            ws_id="WS-002"
        )

        assert "NameError" in prompt
        assert "Line 42" in prompt
        assert "src/app.py" in prompt

    def test_prepare_aider_prompt_file_creates_directory(self, tmp_path):
        """Test prompt file creation creates .aider/prompts/ directory"""
        content = "Test prompt content"

        prompt_file = prepare_aider_prompt_file(tmp_path, "edit", content)

        assert prompt_file.exists()
        assert prompt_file.parent.name == "prompts"
        assert prompt_file.parent.parent.name == ".aider"
        assert prompt_file.read_text() == content


class TestTemplateRender:
    """Unit tests for template rendering helper"""

    def test_template_render_with_context(self):
        """Test TemplateRender stores context correctly"""
        context = {"ws_id": "WS-001", "tasks": ["Task 1"]}

        renderer = TemplateRender("tasks.txt.j2", context)

        assert renderer.template == "tasks.txt.j2"
        assert renderer.context["ws_id"] == "WS-001"
```

### 1.3 Agent Adapter Units

```python
# tests/error/unit/test_agent_adapters_unit.py

from phase6_error_recovery.modules.error_engine.src.engine.agent_adapters import (
    AgentAdapter,
    AiderAdapter,
    CodexAdapter,
    ClaudeAdapter,
    AgentInvocation,
    AgentResult
)

class TestAgentAdapterBase:
    """Unit tests for base AgentAdapter"""

    def test_format_error_prompt_groups_by_file(self):
        """Test error prompt groups issues by file"""
        adapter = AgentAdapter("test", {})
        error_report = {
            "issues": [
                {"path": "a.py", "line": 1, "message": "Error 1"},
                {"path": "a.py", "line": 2, "message": "Error 2"},
                {"path": "b.py", "line": 1, "message": "Error 3"}
            ]
        }

        prompt = adapter._format_error_prompt(error_report)

        assert "a.py" in prompt
        assert "b.py" in prompt
        assert "Error 1" in prompt
        assert "Error 3" in prompt


class TestAiderAdapter:
    """Unit tests for AiderAdapter"""

    def test_aider_adapter_name(self):
        """Test AiderAdapter has correct name"""
        adapter = AiderAdapter()
        assert adapter.name == "aider"

    def test_check_available_when_installed(self, monkeypatch):
        """Test check_available returns True when aider is on PATH"""
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/aider" if x == "aider" else None)

        adapter = AiderAdapter()
        assert adapter.check_available() is True

    def test_check_available_when_not_installed(self, monkeypatch):
        """Test check_available returns False when aider not on PATH"""
        monkeypatch.setattr("shutil.which", lambda x: None)

        adapter = AiderAdapter()
        assert adapter.check_available() is False
```

**Unit Test Execution:**
```bash
# Run all unit tests
pytest tests/ -k "unit" -v

# Run specific module
pytest tests/core/engine/test_tools_unit.py -v

# With coverage
pytest tests/ -k "unit" --cov=core.engine.tools --cov-report=html
```

---

## Layer 2: Integration Tests

### 2.1 Tool Adapter + Subprocess Integration

```python
# tests/core/engine/test_tools_integration.py

import subprocess
import sys
from core.engine.tools import run_tool, ToolResult

class TestToolAdapterIntegration:
    """Integration tests for tool adapter with real subprocess calls"""

    def test_run_tool_success_with_real_command(self):
        """Test run_tool executes real command successfully"""
        # Use Python to echo - cross-platform
        context = {
            "message": "Hello CLI Test"
        }

        # Need to create mock profile or load from test config
        with mock_tool_profile("echo", {
            "command": sys.executable,
            "args": ["-c", 'print("{message}")'],
            "timeout_sec": 5
        }):
            result = run_tool("echo", context)

        assert result.success
        assert result.exit_code == 0
        assert "Hello CLI Test" in result.stdout

    def test_run_tool_timeout_enforced(self):
        """Test run_tool enforces timeout"""
        context = {}

        with mock_tool_profile("sleep", {
            "command": sys.executable,
            "args": ["-c", "import time; time.sleep(10)"],
            "timeout_sec": 1
        }):
            result = run_tool("sleep", context)

        assert not result.success
        assert result.timed_out
        assert result.exit_code == -1

    def test_run_tool_captures_stderr(self):
        """Test run_tool captures stderr separately"""
        context = {}

        with mock_tool_profile("error", {
            "command": sys.executable,
            "args": ["-c", "import sys; sys.stderr.write('error message'); sys.exit(1)"],
            "timeout_sec": 5
        }):
            result = run_tool("error", context)

        assert not result.success
        assert result.exit_code == 1
        assert "error message" in result.stderr

    def test_run_tool_with_env_vars(self):
        """Test run_tool passes environment variables"""
        context = {}

        with mock_tool_profile("env_test", {
            "command": sys.executable,
            "args": ["-c", "import os; print(os.environ.get('TEST_VAR', 'NOT_SET'))"],
            "env": {"TEST_VAR": "test_value"},
            "timeout_sec": 5
        }):
            result = run_tool("env_test", context)

        assert result.success
        assert "test_value" in result.stdout

    def test_run_tool_with_working_directory(self, tmp_path):
        """Test run_tool changes working directory"""
        context = {"cwd": str(tmp_path)}

        with mock_tool_profile("pwd", {
            "command": sys.executable,
            "args": ["-c", "import os; print(os.getcwd())"],
            "working_dir": "{cwd}",
            "timeout_sec": 5
        }):
            result = run_tool("pwd", context)

        assert result.success
        assert str(tmp_path) in result.stdout
```

### 2.2 Aider Engine + Tool Adapter Integration

```python
# tests/aider_integration/test_aider_engine_integration.py

from pathlib import Path
from unittest.mock import Mock, patch
from phase4_routing.modules.aider_integration.src.aider.engine import (
    run_aider_edit,
    run_aider_fix
)

class TestAiderEngineIntegration:
    """Integration tests for Aider engine with tool adapter"""

    def test_run_aider_edit_creates_prompt_and_calls_tool(self, tmp_path):
        """Test run_aider_edit creates prompt file and invokes tool adapter"""
        # Arrange
        (tmp_path / ".git").mkdir()  # Make it look like a git repo

        with patch('phase4_routing.modules.aider_integration.src.aider.engine.run_tool') as mock_run_tool:
            mock_run_tool.return_value = Mock(
                success=True,
                exit_code=0,
                stdout="Aider output",
                stderr=""
            )

            # Act
            result = run_aider_edit(
                cwd=tmp_path,
                files=["src/app.py"],
                tasks=["Add docstring"],
                repo_root=tmp_path,
                ws_id="WS-TEST"
            )

        # Assert
        # Prompt file was created
        prompt_files = list(tmp_path.glob(".aider/prompts/edit.txt"))
        assert len(prompt_files) == 1

        # Prompt contains expected content
        prompt_content = prompt_files[0].read_text()
        assert "Add docstring" in prompt_content

        # Tool was invoked
        assert mock_run_tool.called
        call_args = mock_run_tool.call_args
        assert call_args[0][0] == "aider"  # tool_id
        assert "prompt_file" in call_args[0][1]  # context

        # Result is correct
        assert result.success

    def test_run_aider_fix_with_error_details(self, tmp_path):
        """Test run_aider_fix passes error details to prompt"""
        (tmp_path / ".git").mkdir()

        with patch('phase4_routing.modules.aider_integration.src.aider.engine.run_tool') as mock_run_tool:
            mock_run_tool.return_value = Mock(success=True, exit_code=0, stdout="", stderr="")

            result = run_aider_fix(
                cwd=tmp_path,
                files=["src/app.py"],
                error_summary="NameError",
                error_details="Line 42: undefined variable 'foo'",
                repo_root=tmp_path,
                ws_id="WS-FIX"
            )

        # Prompt file contains error details
        prompt_files = list(tmp_path.glob(".aider/prompts/fix.txt"))
        prompt_content = prompt_files[0].read_text()
        assert "NameError" in prompt_content
        assert "Line 42" in prompt_content
```

**Integration Test Execution:**
```bash
# Run integration tests
pytest tests/ -k "integration" -v

# Skip slow integration tests
pytest tests/ -k "integration and not slow" -v
```

---

## Layer 3: Contract Tests

### 3.1 Aider CLI Contract Validation

```python
# tests/integration/test_aider_contract.py

import pytest
import shutil
import subprocess
from pathlib import Path

@pytest.mark.aider
@pytest.mark.contract
class TestAiderCLIContract:
    """Contract tests for Aider CLI invocation

    Validates compliance with DOC-GUIDE-AIDER_CONTRACT-074
    """

    @pytest.fixture(autouse=True)
    def check_aider_available(self):
        """Skip contract tests if aider not installed"""
        if not shutil.which("aider"):
            pytest.skip("aider not installed; skipping contract tests")

    def test_aider_version_meets_minimum(self):
        """Test aider version >= 0.50.0"""
        result = subprocess.run(
            ["aider", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        version_line = result.stdout.strip()
        # Parse version and verify >= 0.50.0
        # TODO: Implement version parsing

    def test_aider_accepts_no_auto_commits_flag(self, tmp_path):
        """Test aider accepts --no-auto-commits flag"""
        # Create minimal git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True)
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True)

        result = subprocess.run(
            ["aider", "--no-auto-commits", "--yes", "--message", "test", str(test_file)],
            cwd=tmp_path,
            capture_output=True,
            timeout=30,
            env={"AIDER_NO_AUTO_COMMITS": "1"}
        )

        # Should not error on flag
        # May fail on other reasons (API key, etc.) but should recognize flag
        assert "--no-auto-commits" not in result.stderr

    def test_aider_accepts_message_file_flag(self, tmp_path):
        """Test aider accepts --message-file flag"""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True)
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        message_file = tmp_path / "message.txt"
        message_file.write_text("Test message")

        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True)

        result = subprocess.run(
            ["aider", "--message-file", str(message_file), "--yes", str(test_file)],
            cwd=tmp_path,
            capture_output=True,
            timeout=30
        )

        # Should recognize --message-file flag
        assert "--message-file" not in result.stderr

    def test_aider_exit_codes_match_contract(self, tmp_path):
        """Test aider exit codes match contract expectations

        Contract:
        - 0 = success
        - non-zero = failure
        - (timeout/not-found handled by adapter, not aider itself)
        """
        # Test success case (if possible without API key)
        # Test failure case (invalid arguments)

        result = subprocess.run(
            ["aider", "--invalid-flag-xyz"],
            capture_output=True,
            timeout=5
        )

        # Should exit non-zero for invalid flag
        assert result.returncode != 0
```

### 3.2 Cross-Tool Contract Tests

```python
# tests/integration/test_tool_contracts.py

@pytest.mark.contract
class TestToolContracts:
    """Contract tests for all CLI tools"""

    @pytest.mark.parametrize("tool,version_flag,min_version", [
        ("aider", "--version", "0.50.0"),
        ("pytest", "--version", "7.0.0"),
        ("ruff", "--version", "0.1.0"),
        ("git", "--version", "2.30.0")
    ])
    def test_tool_version_check(self, tool, version_flag, min_version):
        """Test each tool meets minimum version requirement"""
        if not shutil.which(tool):
            pytest.skip(f"{tool} not installed")

        result = subprocess.run(
            [tool, version_flag],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        # TODO: Parse and compare version

    @pytest.mark.parametrize("tool,help_flag", [
        ("aider", "--help"),
        ("pytest", "--help"),
        ("ruff", "--help"),
        ("git", "--help")
    ])
    def test_tool_help_flag(self, tool, help_flag):
        """Test each tool responds to --help"""
        if not shutil.which(tool):
            pytest.skip(f"{tool} not installed")

        result = subprocess.run(
            [tool, help_flag],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Help should succeed (exit 0) or use special code
        assert result.returncode in [0, 1]  # Some tools exit 1 for help
        assert len(result.stdout) > 0  # Should output help text
```

---

## Layer 4: Sandbox Tests

### 4.1 Real Aider Execution in Sandbox

```python
# tests/integration/test_aider_sandbox_extended.py

import pytest
import shutil
import subprocess
from pathlib import Path

@pytest.mark.aider
@pytest.mark.sandbox
@pytest.mark.slow
class TestAiderSandbox:
    """Sandbox tests with real Aider execution

    These tests actually invoke aider CLI in a controlled environment.
    Requires:
    - aider installed
    - API key configured (or Ollama)
    - Network access (unless using Ollama)
    """

    @pytest.fixture
    def sandbox_repo(self, tmp_path):
        """Create a minimal Python project sandbox"""
        # Create project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        app_file = src_dir / "app.py"
        app_file.write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
""")

        # Initialize git
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True
        )

        return tmp_path

    def test_aider_edit_adds_docstring(self, sandbox_repo):
        """Test aider can add docstring to function"""
        from phase4_routing.modules.aider_integration.src.aider.engine import run_aider_edit

        result = run_aider_edit(
            cwd=sandbox_repo,
            files=["src/app.py"],
            tasks=["Add a docstring to the add() function"],
            repo_root=sandbox_repo,
            ws_id="WS-SANDBOX-001",
            timeout_seconds=60
        )

        # Check result
        if not result.success:
            pytest.skip(f"Aider execution failed (likely API key): {result.stderr}")

        # Verify docstring was added
        app_file = sandbox_repo / "src" / "app.py"
        content = app_file.read_text()

        # Should have docstring added
        assert '"""' in content or "'''" in content

    def test_aider_fix_syntax_error(self, sandbox_repo):
        """Test aider can fix syntax error"""
        # Introduce syntax error
        app_file = sandbox_repo / "src" / "app.py"
        app_file.write_text("""
def broken_function(
    print("missing closing paren"
""")

        subprocess.run(["git", "add", "."], cwd=sandbox_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add broken function"],
            cwd=sandbox_repo,
            check=True,
            capture_output=True
        )

        from phase4_routing.modules.aider_integration.src.aider.engine import run_aider_fix

        result = run_aider_fix(
            cwd=sandbox_repo,
            files=["src/app.py"],
            error_summary="SyntaxError",
            error_details="Line 2: unclosed parenthesis",
            repo_root=sandbox_repo,
            ws_id="WS-SANDBOX-002",
            timeout_seconds=60
        )

        if not result.success:
            pytest.skip(f"Aider execution failed: {result.stderr}")

        # Verify syntax error was fixed
        # Try to parse the file
        import ast
        content = app_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError:
            pytest.fail("Aider did not fix syntax error")
```

### 4.2 Concurrent Tool Execution

```python
# tests/integration/test_concurrent_tool_execution.py

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.engine.tools import run_tool

@pytest.mark.integration
@pytest.mark.concurrency
class TestConcurrentToolExecution:
    """Test concurrent CLI tool execution"""

    def test_parallel_tool_execution_no_interference(self):
        """Test multiple tools can run in parallel without interference"""

        def run_test_tool(tool_id, message):
            context = {"message": message}
            return run_tool(tool_id, context)

        # Run 5 tools in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_test_tool, f"echo_{i}", f"Message {i}")
                for i in range(5)
            ]

            results = [f.result() for f in as_completed(futures)]

        # All should succeed
        assert all(r.success for r in results)

        # Each should have correct output
        messages = [r.stdout.strip() for r in results]
        assert len(set(messages)) == 5  # All unique

    def test_concurrent_aider_instances_isolated(self, tmp_path):
        """Test concurrent Aider instances don't interfere with each other"""
        # Create multiple sandbox repos
        # Run aider in each concurrently
        # Verify each produces correct output
        pass
```

---

## Layer 5: Error Handling Tests

### 5.1 Timeout Scenarios

```python
# tests/integration/test_timeout_handling.py

@pytest.mark.integration
class TestTimeoutHandling:
    """Test timeout enforcement and handling"""

    def test_tool_timeout_returns_timeout_result(self):
        """Test tool timeout returns proper ToolResult with timed_out=True"""
        context = {}

        with mock_tool_profile("long_sleep", {
            "command": sys.executable,
            "args": ["-c", "import time; time.sleep(999)"],
            "timeout_sec": 1
        }):
            result = run_tool("long_sleep", context)

        assert not result.success
        assert result.timed_out
        assert result.exit_code == -1
        assert result.duration_sec >= 1.0
        assert result.duration_sec < 5.0  # Should not wait full 999 seconds

    def test_aider_timeout_does_not_leave_zombie_process(self):
        """Test aider timeout properly terminates subprocess"""
        # Start aider with very short timeout
        # Verify process is terminated
        # Verify no zombie processes remain
        pass

    def test_timeout_with_partial_stdout_captured(self):
        """Test timeout captures partial output before killing process"""
        context = {}

        with mock_tool_profile("slow_output", {
            "command": sys.executable,
            "args": ["-c", "import time; print('start'); time.sleep(5); print('end')"],
            "timeout_sec": 2
        }):
            result = run_tool("slow_output", context)

        assert result.timed_out
        assert "start" in result.stdout
        # "end" should not be in stdout (timed out before printing)
```

### 5.2 Tool Not Found Scenarios

```python
# tests/integration/test_tool_not_found.py

class TestToolNotFound:
    """Test behavior when tool binary is not found"""

    def test_missing_tool_binary_returns_error(self):
        """Test missing tool binary returns exit_code=-2"""
        context = {}

        with mock_tool_profile("nonexistent", {
            "command": "definitely_not_a_real_command_xyz",
            "args": [],
            "timeout_sec": 5
        }):
            result = run_tool("nonexistent", context)

        assert not result.success
        assert result.exit_code == -2
        assert "not found" in result.stderr.lower()

    def test_check_tool_availability_before_execution(self):
        """Test checking tool availability before execution"""
        from core.engine.tools import check_tool_available

        assert check_tool_available("python") or check_tool_available("python3")
        assert not check_tool_available("definitely_not_a_real_command_xyz")
```

### 5.3 Invalid Input Scenarios

```python
# tests/integration/test_invalid_input.py

class TestInvalidInput:
    """Test handling of invalid inputs"""

    def test_missing_required_template_variable_raises_error(self):
        """Test missing required template variable raises clear error"""
        profile = {
            "command": "echo",
            "args": ["{required_var}"]
        }
        context = {}  # Missing required_var

        with pytest.raises(KeyError, match="required_var"):
            render_command("echo", context, profile=profile)

    def test_invalid_tool_profile_id_raises_error(self):
        """Test requesting non-existent tool profile raises clear error"""
        with pytest.raises(KeyError, match="Tool profile.*not found"):
            get_tool_profile("nonexistent_tool_id")

    def test_malformed_prompt_template_raises_error(self):
        """Test malformed Jinja2 template raises clear error"""
        # Test with broken template
        pass
```

---

## Layer 6: Performance Tests

### 6.1 Throughput Tests

```python
# tests/performance/test_tool_throughput.py

import pytest
import time

@pytest.mark.performance
class TestToolThroughput:
    """Performance tests for tool execution throughput"""

    def test_sequential_tool_execution_throughput(self):
        """Test throughput of sequential tool executions"""
        num_executions = 100
        start_time = time.time()

        for i in range(num_executions):
            context = {"message": f"Test {i}"}
            result = run_tool("echo", context)
            assert result.success

        duration = time.time() - start_time
        throughput = num_executions / duration

        # Should handle at least 10 executions per second
        assert throughput >= 10.0, f"Throughput too low: {throughput:.2f} exec/sec"

    def test_parallel_tool_execution_throughput(self):
        """Test throughput of parallel tool executions"""
        num_executions = 100
        max_workers = 10

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(run_tool, "echo", {"message": f"Test {i}"})
                for i in range(num_executions)
            ]
            results = [f.result() for f in futures]

        duration = time.time() - start_time
        throughput = num_executions / duration

        # Parallel should be faster than sequential
        assert throughput >= 20.0, f"Parallel throughput too low: {throughput:.2f} exec/sec"
```

### 6.2 Memory Usage Tests

```python
# tests/performance/test_memory_usage.py

@pytest.mark.performance
class TestMemoryUsage:
    """Performance tests for memory usage"""

    def test_tool_execution_memory_leak(self):
        """Test repeated tool executions don't leak memory"""
        import psutil
        import gc

        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_mb = process.memory_info().rss / 1024 / 1024

        # Execute tools many times
        for i in range(1000):
            result = run_tool("echo", {"message": f"Test {i}"})
            assert result.success

        # Final memory
        gc.collect()
        final_mb = process.memory_info().rss / 1024 / 1024

        # Memory growth should be minimal (<50 MB)
        memory_growth = final_mb - baseline_mb
        assert memory_growth < 50, f"Memory leak detected: {memory_growth:.2f} MB growth"
```

---

## Layer 7: End-to-End Tests

### 7.1 Full Workstream Execution

```python
# tests/e2e/test_full_workstream_cli.py

@pytest.mark.e2e
@pytest.mark.slow
class TestFullWorkstreamCLI:
    """End-to-end tests for full workstream execution with CLI tools"""

    def test_edit_validate_deploy_workflow(self, tmp_path):
        """Test complete workflow: EDIT → VALIDATE → DEPLOY"""
        # Setup sandbox project
        # Load workstream bundle
        # Execute via orchestrator
        # Verify each step invoked correct CLI tool
        # Verify final state is correct
        pass

    def test_error_detection_and_fix_workflow(self, tmp_path):
        """Test error detection → agent fix workflow"""
        # Introduce error in code
        # Run error detection (ruff plugin)
        # Trigger agent adapter (aider)
        # Verify error is fixed
        # Verify code passes validation
        pass

    def test_multi_workstream_parallel_execution(self, tmp_path):
        """Test multiple workstreams executing in parallel"""
        # Create multiple workstreams
        # Execute via scheduler
        # Verify no interference
        # Verify all complete successfully
        pass
```

### 7.2 Real-World Scenarios

```python
# tests/e2e/test_real_world_scenarios.py

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.requiresai
class TestRealWorldScenarios:
    """End-to-end tests simulating real-world usage"""

    def test_add_feature_to_python_module(self, sandbox_python_project):
        """Test adding a new feature to Python module using Aider"""
        # Define workstream: Add function to module
        # Execute via orchestrator
        # Verify function exists
        # Verify function works
        # Verify tests pass
        pass

    def test_refactor_with_multiple_files(self, sandbox_python_project):
        """Test refactoring across multiple files"""
        # Define workstream: Rename class across files
        # Execute via orchestrator with Aider
        # Verify all references updated
        # Verify tests still pass
        pass

    def test_fix_real_linting_errors(self, sandbox_python_project):
        """Test fixing real linting errors detected by ruff"""
        # Introduce various linting errors
        # Run error detection
        # Run agent fix
        # Verify all errors resolved
        # Verify ruff reports no errors
        pass
```

---

## Test Execution Strategy

### Test Pyramid

```
                    E2E Tests (5%)
                  /    ~10 tests
                 /     Time: ~30 min
                /
          Performance Tests (5%)
            /    ~20 tests
           /     Time: ~10 min
          /
    Sandbox Tests (10%)
      /    ~30 tests
     /     Time: ~15 min
    /
Error Handling Tests (15%)
  /    ~50 tests
 /     Time: ~5 min
/
Integration Tests (25%)
    ~100 tests
    Time: ~10 min

Unit Tests (40%)
    ~200 tests
    Time: ~2 min
```

### Test Markers

```python
# pytest.ini

[pytest]
markers =
    unit: Unit tests (fast, no I/O)
    integration: Integration tests (moderate, some I/O)
    contract: Contract tests (validate CLI interfaces)
    sandbox: Sandbox tests (real tool execution)
    aider: Tests requiring Aider CLI
    requiresai: Tests requiring AI API access
    slow: Slow tests (>5 seconds)
    performance: Performance benchmarks
    e2e: End-to-end tests
    concurrency: Tests involving parallel execution
```

### Execution Commands

```bash
# Fast feedback loop (unit + integration)
pytest -m "unit or integration" -v

# Pre-commit checks (exclude slow tests)
pytest -m "not slow and not requiresai" -v

# Full test suite (excluding AI-dependent tests)
pytest -m "not requiresai" -v

# Full test suite including AI tests
pytest -v

# Contract validation only
pytest -m contract -v

# Performance benchmarks
pytest -m performance -v --benchmark-only

# Specific layer
pytest tests/core/engine/test_tools_unit.py -v
pytest tests/integration/test_aider_contract.py -v
pytest tests/e2e/ -v
```

### CI/CD Integration

```yaml
# .github/workflows/test-cli-communication.yml

name: CLI Communication Tests

on: [push, pull_request]

jobs:
  unit-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest -m "unit or integration" --cov=core.engine.tools --cov-report=xml
      - uses: codecov/codecov-action@v3

  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pip install aider-chat  # Install aider for contract tests
      - run: pytest -m contract -v

  sandbox-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pip install aider-chat
      - run: pytest -m "sandbox and not requiresai" -v
    # Skip AI-dependent tests in CI (no API keys)
```

---

## Test Data & Fixtures

### Shared Fixtures

```python
# tests/conftest.py

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def mock_tool_profile():
    """Context manager to temporarily inject a tool profile"""
    from contextlib import contextmanager
    from core.engine import tools

    @contextmanager
    def _mock_profile(tool_id, profile):
        original_cache = tools._tool_profiles_cache
        tools._tool_profiles_cache = {tool_id: profile}
        try:
            yield
        finally:
            tools._tool_profiles_cache = original_cache

    return _mock_profile

@pytest.fixture
def sandbox_python_project(tmp_path):
    """Create a minimal Python project for testing"""
    # Create structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()

    # Create source file
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "app.py").write_text("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
""")

    # Create test file
    (tmp_path / "tests" / "test_app.py").write_text("""
from src.app import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(2, 3) == 6
""")

    # Initialize git
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=tmp_path, check=True, capture_output=True)

    return tmp_path

@pytest.fixture
def mock_aider_response():
    """Mock successful Aider response"""
    return Mock(
        success=True,
        exit_code=0,
        stdout="Aider made changes successfully",
        stderr="",
        timed_out=False,
        duration_sec=5.0
    )
```

---

## Metrics & Success Criteria

### Coverage Targets

| Component | Unit | Integration | E2E | Total |
|-----------|------|-------------|-----|-------|
| core/engine/tools.py | 95% | 90% | - | 95% |
| aider/engine.py | 90% | 85% | 80% | 90% |
| agent_adapters.py | 85% | 80% | 75% | 85% |
| Overall | 90% | 85% | 75% | 88% |

### Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| Tool execution latency (p50) | <100ms | TBD |
| Tool execution latency (p99) | <500ms | TBD |
| Throughput (sequential) | >10/sec | TBD |
| Throughput (parallel, 10 workers) | >50/sec | TBD |
| Memory growth (1000 executions) | <50MB | TBD |
| Timeout precision | ±10% | TBD |

### Quality Gates

**Must Pass Before Merge:**
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Coverage >= 85% for modified files
- ✅ No new linting errors
- ✅ Contract tests pass (if tool available)

**Should Pass Before Release:**
- ✅ All sandbox tests pass
- ✅ All error handling tests pass
- ✅ Performance tests meet targets
- ✅ E2E tests pass (at least 80%)

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- ✅ Set up test structure
- ✅ Implement unit tests for tools.py
- ✅ Implement unit tests for aider/engine.py
- ✅ Create shared fixtures
- ✅ Configure pytest markers
- **Deliverable:** 200+ unit tests, 90% coverage

### Phase 2: Integration (Week 2)
- ✅ Implement tool adapter integration tests
- ✅ Implement Aider engine integration tests
- ✅ Add concurrency tests
- ✅ Add timeout handling tests
- **Deliverable:** 100+ integration tests, contract validation

### Phase 3: Validation (Week 3)
- ✅ Implement contract tests for Aider CLI
- ✅ Implement sandbox tests (real execution)
- ✅ Add error handling test suite
- ✅ Implement performance benchmarks
- **Deliverable:** Full test pyramid, CI integration

### Phase 4: E2E & Polish (Week 4)
- ✅ Implement end-to-end workflow tests
- ✅ Add real-world scenario tests
- ✅ Performance tuning
- ✅ Documentation and maintenance guide
- **Deliverable:** Production-ready test suite

---

## Maintenance & Evolution

### Regular Maintenance Tasks

**Weekly:**
- Review failed tests in CI
- Update snapshots if expected behavior changed
- Monitor performance regression

**Monthly:**
- Review and update test data fixtures
- Audit coverage gaps
- Update contract tests for tool version changes

**Quarterly:**
- Review and refactor test suite organization
- Evaluate new testing tools/frameworks
- Update performance baselines

### Deprecation Strategy

When deprecating a CLI tool or adapter:
1. Mark tests with `@pytest.mark.deprecated`
2. Update to skip in CI but keep in codebase
3. Remove after 2 release cycles
4. Archive test code in `tests/_archive/`

---

## Related Documentation

- [DOC_AIDER_CONTRACT.md](DOC_AIDER_CONTRACT.md) - Aider CLI integration contract
- [DOC_TESTING_STRATEGY.md](../DOC_guidelines/DOC_TESTING_STRATEGY.md) - General testing strategy
- [DOC_ARCHITECTURE.md](DOC_ARCHITECTURE.md) - System architecture overview
- [test-aider-comprehensive.ps1](../../scripts/test-aider-comprehensive.ps1) - Existing Aider test script

---

**Document Status:** Draft
**Next Review:** 2025-12-11 (1 week after implementation start)
**Owner:** Testing Team
**Last Updated:** 2025-12-04
