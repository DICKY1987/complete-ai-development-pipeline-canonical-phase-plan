"""Test plan execution engine - DOC-TESTS-ENGINE-PLAN-EXEC-001"""

import json
import subprocess
from pathlib import Path

import pytest

from core.engine.orchestrator import Orchestrator
from core.engine.plan_schema import Plan, StepDef


def test_plan_schema_loads_valid_plan(tmp_path):
    """Test Plan.from_file loads valid JSON plan.

    # DOC_ID: DOC-ENGINE-ENGINE-TEST-PLAN-EXECUTION-001
    """
    plan_data = {
        "plan_id": "TEST-001",
        "version": "1.0",
        "globals": {"max_concurrency": 1, "default_timeout_sec": 60},
        "steps": [
            {
                "id": "step1",
                "name": "Echo test",
                "command": "python",
                "args": ["-c", "print('hello')"],
                "depends_on": [],
            }
        ],
    }

    plan_file = tmp_path / "test.json"
    plan_file.write_text(json.dumps(plan_data))

    plan = Plan.from_file(str(plan_file))

    assert plan.plan_id == "TEST-001"
    assert plan.version == "1.0"
    assert len(plan.steps) == 1
    assert plan.steps[0].id == "step1"


def test_plan_schema_variable_substitution(tmp_path):
    """Test variable substitution in plan loading."""
    plan_data = {
        "plan_id": "TEST-002",
        "version": "1.0",
        "globals": {"max_concurrency": 1},
        "steps": [
            {
                "id": "echo_var",
                "name": "Echo variable",
                "command": "python",
                "args": ["-c", "print('${MESSAGE}')"],
                "depends_on": [],
            }
        ],
    }

    plan_file = tmp_path / "test.json"
    plan_file.write_text(json.dumps(plan_data))

    plan = Plan.from_file(str(plan_file), variables={"MESSAGE": "test_value"})

    assert plan.steps[0].args == ["-c", "print('test_value')"]


def test_plan_schema_detects_circular_dependency(tmp_path):
    """Test Plan validation detects circular dependencies."""
    plan_data = {
        "plan_id": "TEST-003",
        "version": "1.0",
        "globals": {"max_concurrency": 1},
        "steps": [
            {
                "id": "a",
                "name": "A",
                "command": "python",
                "args": ["-c", "print('a')"],
                "depends_on": ["b"],
            },
            {
                "id": "b",
                "name": "B",
                "command": "python",
                "args": ["-c", "print('b')"],
                "depends_on": ["a"],
            },
        ],
    }

    plan_file = tmp_path / "test.json"
    plan_file.write_text(json.dumps(plan_data))

    with pytest.raises(ValueError, match="Circular dependency"):
        Plan.from_file(str(plan_file))


def test_plan_schema_detects_missing_dependency(tmp_path):
    """Test Plan validation detects missing dependency reference."""
    plan_data = {
        "plan_id": "TEST-004",
        "version": "1.0",
        "globals": {"max_concurrency": 1},
        "steps": [
            {
                "id": "a",
                "name": "A",
                "command": "python",
                "args": ["-c", "print('a')"],
                "depends_on": ["missing"],
            }
        ],
    }

    plan_file = tmp_path / "test.json"
    plan_file.write_text(json.dumps(plan_data))

    with pytest.raises(ValueError, match="unknown step 'missing'"):
        Plan.from_file(str(plan_file))


def test_execute_simple_plan(tmp_path):
    """Test orchestrator executes a simple plan successfully."""
    plan_data = {
        "plan_id": "TEST-EXEC-001",
        "version": "1.0",
        "metadata": {"project": "test"},
        "globals": {"max_concurrency": 1, "default_timeout_sec": 60},
        "steps": [
            {
                "id": "echo_step",
                "name": "Echo hello",
                "command": "python",
                "args": ["-c", "print('hello')"],
                "depends_on": [],
                "timeout_sec": 10,
                "retries": 0,
                "critical": True,
                "on_failure": "abort",
            }
        ],
    }

    plan_file = tmp_path / "test_exec.json"
    plan_file.write_text(json.dumps(plan_data))

    orch = Orchestrator()
    run_id = orch.execute_plan(str(plan_file))

    run = orch.get_run_status(run_id)
    assert run is not None
    assert run["state"] == "succeeded"

    steps = orch.get_run_steps(run_id)
    assert len(steps) == 1
    assert steps[0]["state"] == "succeeded"


def test_execute_plan_with_dependencies(tmp_path):
    """Test orchestrator respects step dependencies."""
    plan_data = {
        "plan_id": "TEST-EXEC-002",
        "version": "1.0",
        "metadata": {"project": "test"},
        "globals": {"max_concurrency": 2, "default_timeout_sec": 60},
        "steps": [
            {
                "id": "step1",
                "name": "First",
                "command": "python",
                "args": ["-c", "print('first')"],
                "depends_on": [],
            },
            {
                "id": "step2",
                "name": "Second",
                "command": "python",
                "args": ["-c", "print('second')"],
                "depends_on": ["step1"],
            },
            {
                "id": "step3",
                "name": "Third",
                "command": "python",
                "args": ["-c", "print('third')"],
                "depends_on": ["step2"],
            },
        ],
    }

    plan_file = tmp_path / "test_deps.json"
    plan_file.write_text(json.dumps(plan_data))

    orch = Orchestrator()
    run_id = orch.execute_plan(str(plan_file))

    run = orch.get_run_status(run_id)
    assert run["state"] == "succeeded"

    steps = orch.get_run_steps(run_id)
    assert len(steps) == 3


def test_execute_plan_handles_failure_abort(tmp_path):
    """Test orchestrator aborts on critical step failure."""
    # Use a command that will fail
    plan_data = {
        "plan_id": "TEST-EXEC-003",
        "version": "1.0",
        "metadata": {"project": "test"},
        "globals": {"max_concurrency": 1, "default_timeout_sec": 60},
        "steps": [
            {
                "id": "fail_step",
                "name": "Failing step",
                "command": "python",
                "args": ["-c", "import sys; sys.exit(1)"],
                "depends_on": [],
                "critical": True,
                "on_failure": "abort",
                "retries": 0,
            },
            {
                "id": "should_cancel",
                "name": "Should be canceled",
                "command": "python",
                "args": ["-c", "print('should not run')"],
                "depends_on": ["fail_step"],
            },
        ],
    }

    plan_file = tmp_path / "test_fail.json"
    plan_file.write_text(json.dumps(plan_data))

    orch = Orchestrator()
    run_id = orch.execute_plan(str(plan_file))

    run = orch.get_run_status(run_id)
    assert run["state"] == "failed"


def test_execute_plan_with_retry(tmp_path):
    """Test orchestrator retries failed steps."""
    # Create a script that fails first time, succeeds second
    script = tmp_path / "flaky.py"
    flag_file = tmp_path / "attempt.flag"

    script.write_text(
        f"""
import sys
from pathlib import Path

flag = Path(r"{flag_file}")
if flag.exists():
    sys.exit(0)  # Success on retry
else:
    flag.touch()
    sys.exit(1)  # Fail first time
"""
    )

    plan_data = {
        "plan_id": "TEST-EXEC-004",
        "version": "1.0",
        "metadata": {"project": "test"},
        "globals": {"max_concurrency": 1, "default_timeout_sec": 60},
        "steps": [
            {
                "id": "retry_step",
                "name": "Flaky step",
                "command": "python",
                "args": [str(script)],
                "depends_on": [],
                "retries": 2,
                "retry_delay_sec": 1,
                "critical": True,
                "on_failure": "abort",
            }
        ],
    }

    plan_file = tmp_path / "test_retry.json"
    plan_file.write_text(json.dumps(plan_data))

    orch = Orchestrator()
    run_id = orch.execute_plan(str(plan_file))

    run = orch.get_run_status(run_id)
    assert run["state"] == "succeeded"
