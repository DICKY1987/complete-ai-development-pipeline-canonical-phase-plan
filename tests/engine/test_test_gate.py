"""
Tests for TestGate quality gate management.

Tests gate creation, execution, criteria evaluation,
and pass/fail decision logic.

Author: AI Development Pipeline
Created: 2025-11-23
WS: WS-NEXT-002-003 (Testing)
"""

# DOC_ID: DOC-TEST-ENGINE-TEST-TEST-GATE-178

import pytest
import sys
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.test_gate import TestGate, GateCriteria, TestResults


class MockDB:
    """Mock database for testing"""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize test schema"""
        # Create runs table (for foreign key)
        self.conn.execute(
            """
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY
            )
        """
        )

        # Create test_gates table
        schema_path = (
            Path(__file__).parent.parent.parent
            / "schema"
            / "migrations"
            / "004_add_test_gates_table.sql"
        )
        with open(schema_path, "r") as f:
            self.conn.executescript(f.read())
        self.conn.commit()


@pytest.fixture
def db():
    """Create test database"""
    return MockDB()


@pytest.fixture
def gate_manager(db):
    """Create TestGate instance"""
    return TestGate(db)


@pytest.fixture
def gate_id():
    """Generate test gate ID"""
    return "01HQGATE00000000000000001"


@pytest.fixture
def project_id():
    """Generate test project ID"""
    return "test-project"


class TestGateCriteria:
    """Test GateCriteria dataclass"""

    def test_default_criteria(self):
        """Test default criteria"""
        criteria = GateCriteria()
        assert criteria.min_coverage is None
        assert criteria.max_failures is None
        assert criteria.required_tests == []

    def test_criteria_with_values(self):
        """Test criteria with specific values"""
        criteria = GateCriteria(
            min_coverage=80.0,
            max_failures=0,
            required_tests=["test_critical"],
            timeout_seconds=300,
        )
        assert criteria.min_coverage == 80.0
        assert criteria.max_failures == 0
        assert len(criteria.required_tests) == 1

    def test_to_dict(self):
        """Test conversion to dictionary"""
        criteria = GateCriteria(min_coverage=90.0, max_failures=2)
        data = criteria.to_dict()

        assert data["min_coverage"] == 90.0
        assert data["max_failures"] == 2


class TestTestResults:
    """Test TestResults dataclass"""

    def test_default_results(self):
        """Test default results"""
        results = TestResults()
        assert results.total_tests == 0
        assert results.passed_tests == 0
        assert results.failed_tests == 0
        assert results.coverage_percent is None

    def test_results_with_values(self):
        """Test results with specific values"""
        results = TestResults(
            total_tests=100, passed_tests=95, failed_tests=5, coverage_percent=87.5
        )
        assert results.total_tests == 100
        assert results.passed_tests == 95
        assert results.coverage_percent == 87.5

    def test_to_dict(self):
        """Test conversion to dictionary"""
        results = TestResults(total_tests=50, passed_tests=48, failed_tests=2)
        data = results.to_dict()

        assert data["total_tests"] == 50
        assert data["passed_tests"] == 48
        assert data["failed_tests"] == 2


class TestGateCreation:
    """Test gate creation"""

    def test_create_gate(self, gate_manager, gate_id, project_id):
        """Test creating a new gate"""
        criteria = GateCriteria(min_coverage=80.0)

        result = gate_manager.create_gate(
            gate_id=gate_id,
            name="Unit Tests",
            gate_type="unit_tests",
            criteria=criteria,
            project_id=project_id,
        )

        assert result == gate_id

        # Verify gate was created
        gate = gate_manager.get_gate(gate_id)
        assert gate is not None
        assert gate["gate_id"] == gate_id
        assert gate["name"] == "Unit Tests"
        assert gate["gate_type"] == "unit_tests"
        assert gate["state"] == "pending"

    def test_create_gate_all_types(self, gate_manager):
        """Test creating gates of all valid types"""
        types = [
            "unit_tests",
            "integration_tests",
            "e2e_tests",
            "security_scan",
            "lint",
            "custom",
        ]

        for i, gate_type in enumerate(types):
            gate_id = f"01HQGATE000000000000000{i:02d}"
            criteria = GateCriteria()
            gate_manager.create_gate(gate_id, f"Test {i}", gate_type, criteria)

            gate = gate_manager.get_gate(gate_id)
            assert gate["gate_type"] == gate_type

    def test_create_gate_invalid_type(self, gate_manager, gate_id):
        """Test creating gate with invalid type"""
        criteria = GateCriteria()
        with pytest.raises(ValueError, match="Invalid gate_type"):
            gate_manager.create_gate(gate_id, "Test", "invalid_type", criteria)

    def test_create_gate_with_metadata(self, gate_manager, gate_id):
        """Test creating gate with metadata"""
        criteria = GateCriteria()
        metadata = {"branch": "main", "commit": "abc123"}

        gate_manager.create_gate(
            gate_id, "Test", "unit_tests", criteria, metadata=metadata
        )

        gate = gate_manager.get_gate(gate_id)
        assert gate["metadata"] == metadata


class TestGateRetrieval:
    """Test gate retrieval"""

    def test_get_gate(self, gate_manager, gate_id):
        """Test getting a gate by ID"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)

        gate = gate_manager.get_gate(gate_id)
        assert gate is not None
        assert gate["gate_id"] == gate_id

    def test_get_nonexistent_gate(self, gate_manager):
        """Test getting a gate that doesn't exist"""
        gate = gate_manager.get_gate("nonexistent")
        assert gate is None


class TestGateExecution:
    """Test gate execution"""

    def test_start_gate(self, gate_manager, gate_id):
        """Test starting gate execution"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)

        result = gate_manager.start_gate(gate_id, command="pytest tests/")
        assert result is True

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "running"
        assert gate["execution"]["command"] == "pytest tests/"
        assert gate["execution"]["started_at"] is not None

    def test_start_nonexistent_gate(self, gate_manager):
        """Test starting nonexistent gate"""
        with pytest.raises(ValueError, match="Gate not found"):
            gate_manager.start_gate("nonexistent")

    def test_start_already_running_gate(self, gate_manager, gate_id):
        """Test cannot start already running gate"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        with pytest.raises(ValueError, match="Cannot start gate"):
            gate_manager.start_gate(gate_id)

    def test_complete_gate_success(self, gate_manager, gate_id):
        """Test completing gate with passing results"""
        criteria = GateCriteria(min_coverage=80.0, max_failures=0)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(
            total_tests=100, passed_tests=100, failed_tests=0, coverage_percent=95.0
        )

        gate_manager.complete_gate(gate_id, results, exit_code=0)

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "passed"
        assert gate["results"]["total_tests"] == 100
        assert gate["decision"]["passed"] is True

    def test_complete_gate_failure(self, gate_manager, gate_id):
        """Test completing gate with failing results"""
        criteria = GateCriteria(min_coverage=80.0, max_failures=0)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(
            total_tests=100, passed_tests=95, failed_tests=5, coverage_percent=70.0
        )

        gate_manager.complete_gate(gate_id, results, exit_code=0)

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "failed"
        assert gate["decision"]["passed"] is False

    def test_complete_gate_error(self, gate_manager, gate_id):
        """Test completing gate with error exit code"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults()
        gate_manager.complete_gate(gate_id, results, exit_code=1)

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "error"
        assert gate["execution"]["exit_code"] == 1

    def test_complete_not_running_gate(self, gate_manager, gate_id):
        """Test cannot complete gate that's not running"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)

        results = TestResults()
        with pytest.raises(ValueError, match="Cannot complete gate"):
            gate_manager.complete_gate(gate_id, results)


class TestGateSkip:
    """Test gate skip functionality"""

    def test_skip_pending_gate(self, gate_manager, gate_id):
        """Test skipping pending gate"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)

        result = gate_manager.skip_gate(gate_id, "Not applicable")
        assert result is True

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "skipped"
        assert "Skipped" in gate["decision"]["reason"]

    def test_skip_running_gate(self, gate_manager, gate_id):
        """Test skipping running gate"""
        criteria = GateCriteria()
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        gate_manager.skip_gate(gate_id, "Timeout")

        gate = gate_manager.get_gate(gate_id)
        assert gate["state"] == "skipped"


class TestCriteriaEvaluation:
    """Test criteria evaluation logic"""

    def test_evaluate_coverage_pass(self, gate_manager, gate_id):
        """Test coverage criteria passes"""
        criteria = GateCriteria(min_coverage=80.0)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(
            total_tests=100, passed_tests=100, failed_tests=0, coverage_percent=85.0
        )

        gate_manager.complete_gate(gate_id, results)

        gate = gate_manager.get_gate(gate_id)
        assert gate["decision"]["passed"] is True
        assert gate["decision"]["criteria_met"]["coverage"] is True

    def test_evaluate_coverage_fail(self, gate_manager, gate_id):
        """Test coverage criteria fails"""
        criteria = GateCriteria(min_coverage=90.0)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(
            total_tests=100, passed_tests=100, failed_tests=0, coverage_percent=75.0
        )

        gate_manager.complete_gate(gate_id, results)

        gate = gate_manager.get_gate(gate_id)
        assert gate["decision"]["passed"] is False
        assert gate["decision"]["criteria_met"]["coverage"] is False

    def test_evaluate_max_failures_pass(self, gate_manager, gate_id):
        """Test max failures criteria passes"""
        criteria = GateCriteria(max_failures=2)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(total_tests=100, passed_tests=98, failed_tests=2)

        gate_manager.complete_gate(gate_id, results)

        gate = gate_manager.get_gate(gate_id)
        assert gate["decision"]["passed"] is True
        assert gate["decision"]["criteria_met"]["failures"] is True

    def test_evaluate_max_failures_fail(self, gate_manager, gate_id):
        """Test max failures criteria fails"""
        criteria = GateCriteria(max_failures=0)
        gate_manager.create_gate(gate_id, "Test", "unit_tests", criteria)
        gate_manager.start_gate(gate_id)

        results = TestResults(total_tests=100, passed_tests=95, failed_tests=5)

        gate_manager.complete_gate(gate_id, results)

        gate = gate_manager.get_gate(gate_id)
        assert gate["decision"]["passed"] is False
        assert gate["decision"]["criteria_met"]["failures"] is False


class TestGateListing:
    """Test gate listing and filtering"""

    def test_list_gates_empty(self, gate_manager):
        """Test listing gates when none exist"""
        gates = gate_manager.list_gates()
        assert len(gates) == 0

    def test_list_all_gates(self, gate_manager):
        """Test listing all gates"""
        criteria = GateCriteria()
        for i in range(3):
            gate_id = f"01HQGATE000000000000000{i:02d}"
            gate_manager.create_gate(gate_id, f"Test {i}", "unit_tests", criteria)

        gates = gate_manager.list_gates()
        assert len(gates) == 3

    def test_list_gates_by_state(self, gate_manager):
        """Test filtering gates by state"""
        criteria = GateCriteria()
        gate_manager.create_gate(
            "01HQGATE00000000000000001", "Test 1", "unit_tests", criteria
        )
        gate_manager.create_gate(
            "01HQGATE00000000000000002", "Test 2", "unit_tests", criteria
        )

        gate_manager.start_gate("01HQGATE00000000000000001")

        pending = gate_manager.list_gates(state="pending")
        running = gate_manager.list_gates(state="running")

        assert len(pending) == 1
        assert len(running) == 1

    def test_list_gates_by_type(self, gate_manager):
        """Test filtering gates by type"""
        criteria = GateCriteria()
        gate_manager.create_gate(
            "01HQGATE00000000000000001", "Test 1", "unit_tests", criteria
        )
        gate_manager.create_gate(
            "01HQGATE00000000000000002", "Test 2", "integration_tests", criteria
        )

        unit = gate_manager.list_gates(gate_type="unit_tests")
        integration = gate_manager.list_gates(gate_type="integration_tests")

        assert len(unit) == 1
        assert len(integration) == 1

    def test_list_gates_by_project(self, gate_manager):
        """Test filtering gates by project"""
        criteria = GateCriteria()
        gate_manager.create_gate(
            "01HQGATE00000000000000001",
            "Test 1",
            "unit_tests",
            criteria,
            project_id="proj-a",
        )
        gate_manager.create_gate(
            "01HQGATE00000000000000002",
            "Test 2",
            "unit_tests",
            criteria,
            project_id="proj-b",
        )

        proj_a_gates = gate_manager.list_gates(project_id="proj-a")
        assert len(proj_a_gates) == 1


class TestStateTransitions:
    """Test state machine transitions"""

    def test_terminal_states_immutable(self, gate_manager):
        """Test that terminal states cannot transition"""
        assert not gate_manager._can_transition("passed", "running")
        assert not gate_manager._can_transition("failed", "pending")
        assert not gate_manager._can_transition("error", "running")
        assert not gate_manager._can_transition("skipped", "running")

    def test_valid_transitions(self, gate_manager):
        """Test all valid state transitions"""
        # pending -> running
        assert gate_manager._can_transition("pending", "running") is True

        # pending -> skipped
        assert gate_manager._can_transition("pending", "skipped") is True

        # running -> passed/failed/error
        assert gate_manager._can_transition("running", "passed") is True
        assert gate_manager._can_transition("running", "failed") is True
        assert gate_manager._can_transition("running", "error") is True

    def test_is_terminal(self):
        """Test terminal state detection"""
        assert TestGate.is_terminal("passed") is True
        assert TestGate.is_terminal("failed") is True
        assert TestGate.is_terminal("error") is True
        assert TestGate.is_terminal("skipped") is True
        assert TestGate.is_terminal("pending") is False
        assert TestGate.is_terminal("running") is False
