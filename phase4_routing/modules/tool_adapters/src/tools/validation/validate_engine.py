"""
Validate the engine implementation.

Tests:
1. Job schema validation
2. Protocol compliance
3. Orchestrator CLI
4. Adapter interface
"""
# DOC_ID: DOC-PAT-VALIDATION-VALIDATE-ENGINE-636

import json
import sys
from pathlib import Path


def test_job_schema():
    """Verify job schema exists and is valid JSON."""
    print("Testing job schema...")
    schema_path = Path("schema/jobs/job.schema.json")

    if not schema_path.exists():
        print("  ❌ Schema file not found")
        return False

    try:
        with open(schema_path) as f:
            schema = json.load(f)

        required = ["$schema", "type", "required", "properties"]
        if all(k in schema for k in required):
            print("  ✅ Schema is valid")
            return True
        else:
            print("  ❌ Schema missing required fields")
            return False
    except Exception as e:
        print(f"  ❌ Schema load failed: {e}")
        return False


def test_example_job():
    """Verify example job validates against schema."""
    print("Testing example job...")
    example_path = Path("schema/jobs/examples/aider_job.json")

    if not example_path.exists():
        print("  ❌ Example job not found")
        return False

    try:
        with open(example_path) as f:
            job = json.load(f)

        required = ["job_id", "workstream_id", "tool", "command", "env", "paths"]
        if all(k in job for k in required):
            print(f"  ✅ Example job valid (job_id: {job['job_id']})")
            return True
        else:
            missing = [k for k in required if k not in job]
            print(f"  ❌ Example job missing: {missing}")
            return False
    except Exception as e:
        print(f"  ❌ Example load failed: {e}")
        return False


def test_imports():
    """Test that engine modules can be imported."""
    print("Testing imports...")

    try:
        from engine.types import Job, JobResult, JobStatus
        print("  ✅ engine.types")
    except Exception as e:
        print(f"  ❌ engine.types: {e}")
        return False

    try:
        from engine.interfaces import StateInterface, AdapterInterface, OrchestratorInterface
        print("  ✅ engine.interfaces")
    except Exception as e:
        print(f"  ❌ engine.interfaces: {e}")
        return False

    try:
        from engine.adapters.aider_adapter import AiderAdapter, run_aider_job
        print("  ✅ engine.adapters.aider_adapter")
    except Exception as e:
        print(f"  ❌ engine.adapters.aider_adapter: {e}")
        return False

    try:
        from engine.orchestrator.orchestrator import Orchestrator
        print("  ✅ engine.orchestrator.orchestrator")
    except Exception as e:
        print(f"  ❌ engine.orchestrator.orchestrator: {e}")
        return False

    return True


def test_adapter_interface():
    """Test that AiderAdapter implements AdapterInterface."""
    print("Testing adapter interface compliance...")

    try:
        from engine.adapters.aider_adapter import AiderAdapter

        adapter = AiderAdapter()

        # Check required methods
        methods = ["run_job", "validate_job", "get_tool_info"]
        for method in methods:
            if not hasattr(adapter, method):
                print(f"  ❌ Missing method: {method}")
                return False

        # Test get_tool_info
        info = adapter.get_tool_info()
        if "tool" in info and info["tool"] == "aider":
            print("  ✅ Adapter implements AdapterInterface")
            return True
        else:
            print("  ❌ get_tool_info returned invalid data")
            return False

    except Exception as e:
        print(f"  ❌ Adapter test failed: {e}")
        return False


def test_orchestrator_instance():
    """Test orchestrator instantiation."""
    print("Testing orchestrator...")

    try:
        from engine.orchestrator.orchestrator import Orchestrator

        orch = Orchestrator()

        # Check TOOL_RUNNERS
        if "aider" in orch.TOOL_RUNNERS:
            print("  ✅ Orchestrator instantiated with adapters")
            return True
        else:
            print("  ❌ No adapters registered")
            return False

    except Exception as e:
        print(f"  ❌ Orchestrator test failed: {e}")
        return False


def test_state_store():
    """Test state store integration."""
    print("Testing state store...")

    try:
        from engine.state_store.job_state_store import JobStateStore

        # Initialize with test database
        store = JobStateStore(db_path="state/test_validation.db")

        # Test basic operations
        run_id = store.create_run("ws-validation-test")
        assert run_id is not None

        run = store.get_run(run_id)
        assert run["status"] == "pending"

        print("  ✅ State store integrated")

        # Cleanup
        from pathlib import Path
        test_db = Path("state/test_validation.db")
        if test_db.exists():
            test_db.unlink()

        return True
    except Exception as e:
        print(f"  ❌ State store test failed: {e}")
        return False


def test_orchestrator_with_state():
    """Test orchestrator with state store."""
    print("Testing orchestrator with state...")

    try:
        from engine.orchestrator.orchestrator import Orchestrator
        from engine.state_store.job_state_store import JobStateStore

        # Initialize with test database
        store = JobStateStore(db_path="state/test_validation.db")
        orch = Orchestrator(state_store=store)

        assert orch.state_store is not None
        print("  ✅ Orchestrator using state store")

        # Cleanup
        from pathlib import Path
        test_db = Path("state/test_validation.db")
        if test_db.exists():
            test_db.unlink()

        return True
    except Exception as e:
        print(f"  ❌ Orchestrator with state failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("ENGINE IMPLEMENTATION VALIDATION")
    print("=" * 60)
    print()

    tests = [
        ("Job Schema", test_job_schema),
        ("Example Job", test_example_job),
        ("Module Imports", test_imports),
        ("Adapter Interface", test_adapter_interface),
        ("Orchestrator", test_orchestrator_instance),
        ("State Store", test_state_store),
        ("Orchestrator with State", test_orchestrator_with_state),
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
    print()
    print("Additional Tests:")
    print("  Run: python scripts/test_adapters.py (6 tests)")
    print("  Run: python scripts/test_state_store.py (6 tests)")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
