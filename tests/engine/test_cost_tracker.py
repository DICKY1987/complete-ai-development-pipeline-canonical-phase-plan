"""
Tests for CostTracker cost recording and aggregation.

Tests cost recording, retrieval, aggregation,
and breakdown functionality.

Author: AI Development Pipeline
Created: 2025-11-23
WS: WS-NEXT-002-004 (Testing)
"""
# DOC_ID: DOC-TEST-ENGINE-TEST-COST-TRACKER-173

import pytest
import sys
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.cost_tracker import CostTracker, UsageInfo


class MockDB:
    """Mock database for testing"""
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize test schema"""
        # Create runs table (for foreign key)
        self.conn.execute("""
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY
            )
        """)

        # Create costs table
        schema_path = Path(__file__).parent.parent.parent / 'schema' / 'migrations' / '005_add_costs_table.sql'
        with open(schema_path, 'r') as f:
            self.conn.executescript(f.read())
        self.conn.commit()


@pytest.fixture
def db():
    """Create test database"""
    return MockDB()


@pytest.fixture
def tracker(db):
    """Create CostTracker instance"""
    return CostTracker(db)


@pytest.fixture
def cost_id():
    """Generate test cost ID"""
    return "01HQCOST00000000000000001"


@pytest.fixture
def request_id():
    """Generate test request ID"""
    return "01HQREQ000000000000000001"


@pytest.fixture
def project_id():
    """Generate test project ID"""
    return "test-project"


class TestUsageInfo:
    """Test UsageInfo dataclass"""

    def test_usage_cost_calculation(self):
        """Test cost calculation from quantity and rate"""
        usage = UsageInfo(quantity=1000, unit="tokens", rate=0.002)
        assert usage.cost == 2.0  # 1000 * 0.002

    def test_usage_to_dict(self):
        """Test conversion to dictionary"""
        usage = UsageInfo(quantity=500, unit="seconds", rate=0.01)
        data = usage.to_dict()

        assert data['quantity'] == 500
        assert data['unit'] == "seconds"
        assert data['rate'] == 0.01


class TestCostRecording:
    """Test cost recording"""

    def test_record_basic_cost(self, tracker, cost_id):
        """Test recording a basic cost"""
        result = tracker.record_cost(
            cost_id=cost_id,
            resource_type="api_call",
            amount=1.50,
            currency="USD"
        )

        assert result == cost_id

        # Verify cost was recorded
        cost = tracker.get_cost(cost_id)
        assert cost is not None
        assert cost['cost_id'] == cost_id
        assert cost['resource_type'] == "api_call"
        assert cost['amount'] == 1.50
        assert cost['currency'] == "USD"

    def test_record_cost_with_request(self, tracker, cost_id, request_id):
        """Test recording cost with execution request"""
        tracker.record_cost(
            cost_id=cost_id,
            resource_type="api_call",
            amount=2.00,
            execution_request_id=request_id
        )

        cost = tracker.get_cost(cost_id)
        assert cost['execution_request_id'] == request_id

    def test_record_cost_with_usage(self, tracker, cost_id):
        """Test recording cost with usage info"""
        usage = UsageInfo(quantity=1000, unit="tokens", rate=0.002)

        tracker.record_cost(
            cost_id=cost_id,
            resource_type="api_call",
            amount=usage.cost,
            usage=usage
        )

        cost = tracker.get_cost(cost_id)
        assert cost['usage'] is not None
        assert cost['usage']['quantity'] == 1000
        assert cost['usage']['unit'] == "tokens"

    def test_record_cost_with_metadata(self, tracker, cost_id):
        """Test recording cost with metadata"""
        metadata = {
            'model': 'gpt-4',
            'tokens_input': 500,
            'tokens_output': 200
        }

        tracker.record_cost(
            cost_id=cost_id,
            resource_type="api_call",
            amount=1.50,
            resource_name="gpt-4",
            metadata=metadata
        )

        cost = tracker.get_cost(cost_id)
        assert cost['resource_name'] == "gpt-4"
        assert cost['metadata']['model'] == "gpt-4"

    def test_record_all_resource_types(self, tracker):
        """Test recording costs for all resource types"""
        types = ['api_call', 'compute_time', 'storage', 'network', 'tool_usage', 'custom']

        for i, resource_type in enumerate(types):
            cost_id = f"01HQCOST000000000000000{i:02d}"
            tracker.record_cost(cost_id, resource_type, 1.00)

            cost = tracker.get_cost(cost_id)
            assert cost['resource_type'] == resource_type

    def test_record_invalid_resource_type(self, tracker, cost_id):
        """Test recording with invalid resource type"""
        with pytest.raises(ValueError, match="Invalid resource_type"):
            tracker.record_cost(cost_id, "invalid_type", 1.00)

    def test_record_negative_amount(self, tracker, cost_id):
        """Test cannot record negative amount"""
        with pytest.raises(ValueError, match="non-negative"):
            tracker.record_cost(cost_id, "api_call", -1.00)

    def test_record_invalid_currency(self, tracker, cost_id):
        """Test recording with invalid currency code"""
        with pytest.raises(ValueError, match="Currency"):
            tracker.record_cost(cost_id, "api_call", 1.00, currency="US")  # Too short

        with pytest.raises(ValueError, match="Currency"):
            tracker.record_cost(cost_id, "api_call", 1.00, currency="usd")  # Not uppercase


class TestCostRetrieval:
    """Test cost retrieval"""

    def test_get_cost(self, tracker, cost_id):
        """Test getting a cost by ID"""
        tracker.record_cost(cost_id, "api_call", 1.50)
        cost = tracker.get_cost(cost_id)

        assert cost is not None
        assert cost['cost_id'] == cost_id

    def test_get_nonexistent_cost(self, tracker):
        """Test getting a cost that doesn't exist"""
        cost = tracker.get_cost('nonexistent')
        assert cost is None


class TestCostAggregation:
    """Test cost aggregation"""

    def test_total_cost_empty(self, tracker):
        """Test total cost when no costs recorded"""
        total = tracker.get_total_cost()
        assert total == 0.0

    def test_total_cost_all(self, tracker):
        """Test total cost for all records"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50)
        tracker.record_cost("01HQCOST00000000000000002", "compute_time", 2.00)
        tracker.record_cost("01HQCOST00000000000000003", "storage", 0.50)

        total = tracker.get_total_cost()
        assert total == 4.00

    def test_total_cost_by_request(self, tracker, request_id):
        """Test total cost filtered by execution request"""
        tracker.record_cost(
            "01HQCOST00000000000000001",
            "api_call",
            1.50,
            execution_request_id=request_id
        )
        tracker.record_cost(
            "01HQCOST00000000000000002",
            "api_call",
            2.00,
            execution_request_id=request_id
        )
        tracker.record_cost(
            "01HQCOST00000000000000003",
            "api_call",
            1.00,
            execution_request_id="other_request"
        )

        total = tracker.get_total_cost(execution_request_id=request_id)
        assert total == 3.50

    def test_total_cost_by_project(self, tracker, project_id):
        """Test total cost filtered by project"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50, project_id=project_id)
        tracker.record_cost("01HQCOST00000000000000002", "api_call", 2.00, project_id=project_id)
        tracker.record_cost("01HQCOST00000000000000003", "api_call", 1.00, project_id="other")

        total = tracker.get_total_cost(project_id=project_id)
        assert total == 3.50

    def test_total_cost_by_resource_type(self, tracker):
        """Test total cost filtered by resource type"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50)
        tracker.record_cost("01HQCOST00000000000000002", "api_call", 2.00)
        tracker.record_cost("01HQCOST00000000000000003", "compute_time", 3.00)

        total = tracker.get_total_cost(resource_type="api_call")
        assert total == 3.50

    def test_total_cost_different_currency(self, tracker):
        """Test total cost only includes specified currency"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50, currency="USD")
        tracker.record_cost("01HQCOST00000000000000002", "api_call", 2.00, currency="EUR")

        usd_total = tracker.get_total_cost(currency="USD")
        eur_total = tracker.get_total_cost(currency="EUR")

        assert usd_total == 1.50
        assert eur_total == 2.00


class TestCostBreakdown:
    """Test cost breakdown by resource type"""

    def test_breakdown_empty(self, tracker):
        """Test breakdown when no costs recorded"""
        breakdown = tracker.get_cost_breakdown()
        assert len(breakdown) == 0

    def test_breakdown_all_types(self, tracker):
        """Test breakdown across multiple resource types"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50)
        tracker.record_cost("01HQCOST00000000000000002", "api_call", 2.00)
        tracker.record_cost("01HQCOST00000000000000003", "compute_time", 3.00)
        tracker.record_cost("01HQCOST00000000000000004", "storage", 0.50)

        breakdown = tracker.get_cost_breakdown()

        assert breakdown['api_call'] == 3.50
        assert breakdown['compute_time'] == 3.00
        assert breakdown['storage'] == 0.50

    def test_breakdown_by_request(self, tracker, request_id):
        """Test breakdown filtered by execution request"""
        tracker.record_cost(
            "01HQCOST00000000000000001",
            "api_call",
            1.50,
            execution_request_id=request_id
        )
        tracker.record_cost(
            "01HQCOST00000000000000002",
            "compute_time",
            2.00,
            execution_request_id=request_id
        )

        breakdown = tracker.get_cost_breakdown(execution_request_id=request_id)

        assert len(breakdown) == 2
        assert breakdown['api_call'] == 1.50
        assert breakdown['compute_time'] == 2.00


class TestCostListing:
    """Test cost listing"""

    def test_list_costs_empty(self, tracker):
        """Test listing costs when none exist"""
        costs = tracker.list_costs()
        assert len(costs) == 0

    def test_list_all_costs(self, tracker):
        """Test listing all costs"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50)
        tracker.record_cost("01HQCOST00000000000000002", "compute_time", 2.00)
        tracker.record_cost("01HQCOST00000000000000003", "storage", 0.50)

        costs = tracker.list_costs()
        assert len(costs) == 3

    def test_list_costs_by_request(self, tracker, request_id):
        """Test filtering costs by execution request"""
        tracker.record_cost(
            "01HQCOST00000000000000001",
            "api_call",
            1.50,
            execution_request_id=request_id
        )
        tracker.record_cost(
            "01HQCOST00000000000000002",
            "api_call",
            2.00,
            execution_request_id="other"
        )

        costs = tracker.list_costs(execution_request_id=request_id)
        assert len(costs) == 1
        assert costs[0]['execution_request_id'] == request_id

    def test_list_costs_by_project(self, tracker, project_id):
        """Test filtering costs by project"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50, project_id=project_id)
        tracker.record_cost("01HQCOST00000000000000002", "api_call", 2.00, project_id="other")

        costs = tracker.list_costs(project_id=project_id)
        assert len(costs) == 1

    def test_list_costs_by_resource_type(self, tracker):
        """Test filtering costs by resource type"""
        tracker.record_cost("01HQCOST00000000000000001", "api_call", 1.50)
        tracker.record_cost("01HQCOST00000000000000002", "compute_time", 2.00)

        costs = tracker.list_costs(resource_type="api_call")
        assert len(costs) == 1
        assert costs[0]['resource_type'] == "api_call"

    def test_list_costs_with_limit(self, tracker):
        """Test listing costs with limit"""
        for i in range(5):
            cost_id = f"01HQCOST000000000000000{i:02d}"
            tracker.record_cost(cost_id, "api_call", 1.00)

        costs = tracker.list_costs(limit=3)
        assert len(costs) == 3


class TestCostDeletion:
    """Test cost deletion"""

    def test_delete_cost(self, tracker, cost_id):
        """Test deleting a cost"""
        tracker.record_cost(cost_id, "api_call", 1.50)

        result = tracker.delete_cost(cost_id)
        assert result is True

        # Verify cost was deleted
        cost = tracker.get_cost(cost_id)
        assert cost is None

    def test_delete_nonexistent_cost(self, tracker):
        """Test deleting nonexistent cost"""
        result = tracker.delete_cost('nonexistent')
        assert result is False
