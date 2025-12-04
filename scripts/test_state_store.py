"""
Test JobStateStore implementation.

Validates state store integration with existing database schema.
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-STATE-STORE-237
# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-STATE-STORE-174

import sys
import json
from pathlib import Path
from datetime import datetime


def test_state_store_import():
    """Test that state store can be imported."""
    print("Testing state store import...")
    try:
        from engine.state_store.job_state_store import JobStateStore

        print("  ✅ JobStateStore imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_state_store_init():
    """Test state store initialization."""
    print("Testing state store initialization...")
    try:
        from engine.state_store.job_state_store import JobStateStore

        # Use a test database
        test_db = "state/test_pipeline.db"
        store = JobStateStore(db_path=test_db)

        print(f"  ✅ State store initialized with db: {test_db}")
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False


def test_run_crud():
    """Test creating and retrieving runs."""
    print("Testing run CRUD operations...")
    try:
        from engine.state_store.job_state_store import JobStateStore

        store = JobStateStore(db_path="state/test_pipeline.db")

        # Create run
        ws_id = "ws-test-001"
        run_id = store.create_run(ws_id, metadata={"test": "data"})
        print(f"  ✅ Created run: {run_id}")

        # Get run
        run = store.get_run(run_id)
        assert run["run_id"] == run_id
        assert run["status"] == "pending"
        print(f"  ✅ Retrieved run: {run['run_id']}")

        # Update run status
        store.update_run_status(run_id, "running")
        updated = store.get_run(run_id)
        assert updated["status"] == "running"
        print(f"  ✅ Updated run status to: {updated['status']}")

        return True
    except Exception as e:
        print(f"  ❌ Run CRUD failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_job_result_update():
    """Test updating job results."""
    print("Testing job result updates...")
    try:
        from engine.state_store.job_state_store import JobStateStore
        from engine.types import JobResult
        from modules.core_state import m010003_crud
        from modules.core_state.m010003_db import get_connection
        from datetime import datetime

        store = JobStateStore(db_path="state/test_pipeline.db")

        # Create run and workstream first
        run_id = "run-test-002"
        ws_id = "ws-test-002"

        # Create run in DB
        crud.create_run(run_id, status="pending", db_path="state/test_pipeline.db")

        # Create workstream in DB
        conn = get_connection("state/test_pipeline.db")
        cur = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            """INSERT INTO workstreams (ws_id, run_id, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (ws_id, run_id, "pending", now, now),
        )
        conn.commit()
        cur.close()
        conn.close()

        # Create a test job
        job = {
            "job_id": "job-test-002",
            "run_id": run_id,
            "workstream_id": ws_id,
            "tool": "aider",
            "command": {"exe": "aider", "args": []},
            "env": {},
            "paths": {
                "repo_root": ".",
                "working_dir": ".",
                "log_file": "test.log",
                "error_report": "test.error.json",
            },
        }

        # Create result
        result = JobResult(
            exit_code=0,
            error_report_path="test.error.json",
            duration_s=1.5,
            success=True,
        )

        # Update state
        store.update_job_result(job, result)
        print(f"  ✅ Updated job result for: {job['job_id']}")

        # Retrieve job
        stored_job = store.get_job(job["job_id"])
        assert stored_job is not None
        assert stored_job["status"] == "completed"
        print(f"  ✅ Retrieved job with status: {stored_job['status']}")

        return True
    except Exception as e:
        print(f"  ❌ Job result update failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_event_logging():
    """Test event logging."""
    print("Testing event logging...")
    try:
        from engine.state_store.job_state_store import JobStateStore
        from modules.core_state import m010003_crud
        from modules.core_state.m010003_db import get_connection
        from datetime import datetime

        store = JobStateStore(db_path="state/test_pipeline.db")

        # Create run and workstream first (events can reference them)
        run_id = "run-test-003"
        ws_id = "ws-test-003"
        crud.create_run(run_id, status="pending", db_path="state/test_pipeline.db")

        # Create workstream
        conn = get_connection("state/test_pipeline.db")
        cur = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            """INSERT INTO workstreams (ws_id, run_id, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (ws_id, run_id, "pending", now, now),
        )
        conn.commit()
        cur.close()
        conn.close()

        # Record event
        store.record_event(
            "test.event", {"run_id": run_id, "ws_id": ws_id, "message": "Test event"}
        )

        print("  ✅ Event logged successfully")
        return True
    except Exception as e:
        print(f"  ❌ Event logging failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_orchestrator_integration():
    """Test that orchestrator uses state store."""
    print("Testing orchestrator integration...")
    try:
        from engine.orchestrator.orchestrator import Orchestrator
        from engine.state_store.job_state_store import JobStateStore

        # Create orchestrator with test state store
        store = JobStateStore(db_path="state/test_pipeline.db")
        orch = Orchestrator(state_store=store)

        assert orch.state_store is not None
        print("  ✅ Orchestrator has state store")

        # Test get_job_status with existing job
        status = orch.get_job_status("job-test-002")
        print(f"  ✅ get_job_status returned: {status}")

        return True
    except Exception as e:
        print(f"  ❌ Orchestrator integration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def cleanup():
    """Clean up test database."""
    print("\nCleaning up test database...")
    test_db = Path("state/test_pipeline.db")
    if test_db.exists():
        test_db.unlink()
        print("  ✅ Test database removed")


def main():
    """Run all state store tests."""
    print("=" * 60)
    print("STATE STORE INTEGRATION TESTS")
    print("=" * 60)
    print()

    tests = [
        ("Import", test_state_store_import),
        ("Initialization", test_state_store_init),
        ("Run CRUD", test_run_crud),
        ("Job Result Update", test_job_result_update),
        ("Event Logging", test_event_logging),
        ("Orchestrator Integration", test_orchestrator_integration),
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

    # Cleanup
    cleanup()

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
