"""
Test all adapters for conformance to AdapterInterface.

Tests:
1. Import all adapters
2. Validate interface compliance
3. Test basic execution (without external tools)
4. Validate error handling
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-ADAPTERS-235
# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-ADAPTERS-172

import sys
from pathlib import Path

__test__ = False  # Prevent pytest from collecting this helper script


def test_adapter_imports():
    """Test that all adapters can be imported."""
    print("Testing adapter imports...")

    adapters = [
        ("aider", "engine.adapters.aider_adapter", "AiderAdapter"),
        ("codex", "engine.adapters.codex_adapter", "CodexAdapter"),
        ("tests", "engine.adapters.tests_adapter", "TestsAdapter"),
        ("git", "engine.adapters.git_adapter", "GitAdapter"),
    ]

    results = []
    for name, module, class_name in adapters:
        try:
            mod = __import__(module, fromlist=[class_name])
            adapter_class = getattr(mod, class_name)
            print(f"  ✅ {name}: {class_name} imported")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {name}: Import failed - {e}")
            results.append(False)

    return all(results)


def test_adapter_interface():
    """Test that all adapters implement AdapterInterface."""
    print("Testing adapter interface compliance...")

    from engine.adapters.aider_adapter import AiderAdapter
    from engine.adapters.codex_adapter import CodexAdapter
    from engine.adapters.tests_adapter import TestsAdapter
    from engine.adapters.git_adapter import GitAdapter

    adapters = [
        ("aider", AiderAdapter()),
        ("codex", CodexAdapter()),
        ("tests", TestsAdapter()),
        ("git", GitAdapter()),
    ]

    required_methods = ["run_job", "validate_job", "get_tool_info"]

    results = []
    for name, adapter in adapters:
        missing = []
        for method in required_methods:
            if not hasattr(adapter, method):
                missing.append(method)

        if missing:
            print(f"  ❌ {name}: Missing methods: {missing}")
            results.append(False)
        else:
            print(f"  ✅ {name}: All interface methods present")
            results.append(True)

    return all(results)


def test_tool_info():
    """Test get_tool_info returns valid metadata."""
    print("Testing tool info...")

    from engine.adapters.aider_adapter import AiderAdapter
    from engine.adapters.codex_adapter import CodexAdapter
    from engine.adapters.tests_adapter import TestsAdapter
    from engine.adapters.git_adapter import GitAdapter

    adapters = [
        ("aider", AiderAdapter()),
        ("codex", CodexAdapter()),
        ("tests", TestsAdapter()),
        ("git", GitAdapter()),
    ]

    results = []
    for name, adapter in adapters:
        try:
            info = adapter.get_tool_info()
            assert "tool" in info
            assert "capabilities" in info
            print(
                f"  ✅ {name}: {info['tool']} - {len(info['capabilities'])} capabilities"
            )
            results.append(True)
        except Exception as e:
            print(f"  ❌ {name}: get_tool_info failed - {e}")
            results.append(False)

    return all(results)


def test_job_validation():
    """Test validate_job method."""
    print("Testing job validation...")

    from engine.adapters.git_adapter import GitAdapter

    adapter = GitAdapter()

    # Valid job
    valid_job = {
        "job_id": "job-test-001",
        "workstream_id": "ws-test",
        "tool": "git",
        "command": {"exe": "git", "args": ["status"]},
        "env": {},
        "paths": {
            "repo_root": ".",
            "working_dir": ".",
            "log_file": "test.log",
            "error_report": "test.error.json",
        },
    }

    if adapter.validate_job(valid_job):
        print("  ✅ Valid job accepted")
    else:
        print("  ❌ Valid job rejected")
        return False

    # Invalid job (wrong tool)
    invalid_job = valid_job.copy()
    invalid_job["tool"] = "wrong_tool"

    if not adapter.validate_job(invalid_job):
        print("  ✅ Invalid job rejected (wrong tool)")
    else:
        print("  ❌ Invalid job accepted (wrong tool)")
        return False

    # Invalid job (missing fields)
    incomplete_job = {"job_id": "test"}

    if not adapter.validate_job(incomplete_job):
        print("  ✅ Incomplete job rejected")
    else:
        print("  ❌ Incomplete job accepted")
        return False

    return True


def test_orchestrator_registration():
    """Test that adapters are registered in orchestrator."""
    print("Testing orchestrator registration...")

    from engine.orchestrator.orchestrator import Orchestrator

    orch = Orchestrator()

    expected_tools = ["aider", "codex", "tests", "git"]

    results = []
    for tool in expected_tools:
        if tool in orch.TOOL_RUNNERS:
            print(f"  ✅ {tool}: Registered")
            results.append(True)
        else:
            print(f"  ❌ {tool}: Not registered")
            results.append(False)

    return all(results)


def test_git_adapter_execution():
    """Test git adapter with simple command."""
    print("Testing git adapter execution...")

    try:
        from engine.adapters.git_adapter import GitAdapter
        from pathlib import Path
        import tempfile

        # Create temp directory for logs
        temp_dir = Path(tempfile.mkdtemp())

        job = {
            "job_id": "job-test-git-001",
            "workstream_id": "ws-test",
            "tool": "git",
            "command": {"exe": "git", "args": ["--version"]},
            "env": {},
            "paths": {
                "repo_root": ".",
                "working_dir": ".",
                "log_file": str(temp_dir / "git.log"),
                "error_report": str(temp_dir / "git.error.json"),
            },
            "metadata": {"timeout_seconds": 10},
        }

        adapter = GitAdapter()
        result = adapter.run_job(job)

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

        if result.exit_code == 0:
            print(f"  ✅ Git adapter executed successfully ({result.duration_s:.2f}s)")
            return True
        else:
            print(f"  ❌ Git adapter failed with exit code {result.exit_code}")
            return False

    except Exception as e:
        print(f"  ❌ Git adapter execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all adapter tests."""
    print("=" * 60)
    print("ADAPTER VALIDATION TESTS")
    print("=" * 60)
    print()

    tests = [
        ("Adapter Imports", test_adapter_imports),
        ("Interface Compliance", test_adapter_interface),
        ("Tool Info", test_tool_info),
        ("Job Validation", test_job_validation),
        ("Orchestrator Registration", test_orchestrator_registration),
        ("Git Adapter Execution", test_git_adapter_execution),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
