"""Test Decision Registry

Validates decision logging, querying, and statistics functionality.
"""

# DOC_ID: DOC-TEST-DECISION-REGISTRY-001

from datetime import datetime, timedelta, timezone

import pytest

from patterns.decisions.decision_registry import Decision, DecisionRegistry


@pytest.fixture
def registry():
    """Create in-memory decision registry for testing"""
    reg = DecisionRegistry(storage_path=":memory:")
    yield reg
    reg.close()


def test_decision_registry_logs_decisions(registry):
    """Test basic decision logging"""
    decision = Decision(
        decision_id="DEC-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        category="routing",
        context={"task": "edit"},
        options=["aider", "claude"],
        selected_option="aider",
        rationale="First in sorted list",
        metadata={},
    )

    registry.log_decision(decision)

    retrieved = registry.query_decisions(category="routing")
    assert len(retrieved) == 1
    assert retrieved[0].decision_id == "DEC-001"
    assert retrieved[0].category == "routing"
    assert retrieved[0].selected_option == "aider"


def test_query_decisions_by_category(registry):
    """Test filtering decisions by category"""
    decisions = [
        Decision(
            decision_id=f"DEC-{i}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=cat,
            context={},
            options=["opt1", "opt2"],
            selected_option="opt1",
            rationale="test",
            metadata={},
        )
        for i, cat in enumerate(
            ["routing", "scheduling", "routing", "circuit_breaker", "routing"]
        )
    ]

    for dec in decisions:
        registry.log_decision(dec)

    routing = registry.query_decisions(category="routing")
    scheduling = registry.query_decisions(category="scheduling")

    assert len(routing) == 3
    assert len(scheduling) == 1
    assert all(d.category == "routing" for d in routing)


def test_query_decisions_by_run_id(registry):
    """Test filtering decisions by run_id in metadata"""
    decisions = [
        Decision(
            decision_id=f"DEC-{i}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category="routing",
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={"run_id": run_id},
        )
        for i, run_id in enumerate(["RUN-A", "RUN-B", "RUN-A", "RUN-C", "RUN-A"])
    ]

    for dec in decisions:
        registry.log_decision(dec)

    run_a = registry.query_decisions(run_id="RUN-A")
    run_b = registry.query_decisions(run_id="RUN-B")

    assert len(run_a) == 3
    assert len(run_b) == 1


def test_query_decisions_by_time_range(registry):
    """Test filtering decisions by timestamp"""
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=2)
    future = now + timedelta(hours=2)

    decisions = [
        Decision(
            decision_id=f"DEC-{i}",
            timestamp=ts.isoformat(),
            category="routing",
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={},
        )
        for i, ts in enumerate([past, now, future])
    ]

    for dec in decisions:
        registry.log_decision(dec)

    recent = registry.query_decisions(since=now.isoformat())

    # Should get 'now' and 'future' decisions
    assert len(recent) >= 2


def test_query_decisions_with_limit(registry):
    """Test limit parameter in query"""
    for i in range(20):
        decision = Decision(
            decision_id=f"DEC-{i:03d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category="routing",
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={},
        )
        registry.log_decision(decision)

    results = registry.query_decisions(limit=5)

    assert len(results) == 5


def test_query_decisions_returns_newest_first(registry):
    """Test decisions returned in reverse chronological order"""
    base_time = datetime.now(timezone.utc)

    for i in range(5):
        ts = (base_time + timedelta(minutes=i)).isoformat()
        decision = Decision(
            decision_id=f"DEC-{i}",
            timestamp=ts,
            category="routing",
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={},
        )
        registry.log_decision(decision)

    results = registry.query_decisions()

    # Newest first
    assert results[0].decision_id == "DEC-4"
    assert results[-1].decision_id == "DEC-0"


def test_get_decision_stats(registry):
    """Test decision statistics calculation"""
    categories = ["routing", "scheduling", "routing", "circuit_breaker", "routing"]

    for i, cat in enumerate(categories):
        decision = Decision(
            decision_id=f"DEC-{i}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=cat,
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={},
        )
        registry.log_decision(decision)

    stats = registry.get_decision_stats()

    assert stats["total"] == 5
    assert stats["by_category"]["routing"] == 3
    assert stats["by_category"]["scheduling"] == 1
    assert stats["by_category"]["circuit_breaker"] == 1


def test_decision_to_dict(registry):
    """Test Decision.to_dict() conversion"""
    decision = Decision(
        decision_id="DEC-001",
        timestamp="2024-01-01T00:00:00Z",
        category="routing",
        context={"key": "value"},
        options=["opt1", "opt2"],
        selected_option="opt1",
        rationale="test rationale",
        metadata={"meta_key": "meta_value"},
    )

    d = decision.to_dict()

    assert d["decision_id"] == "DEC-001"
    assert d["category"] == "routing"
    assert d["context"] == {"key": "value"}
    assert d["selected_option"] == "opt1"


def test_complex_query_combination(registry):
    """Test combining multiple query filters"""
    now = datetime.now(timezone.utc)

    # Add various decisions
    decisions = [
        ("DEC-1", "routing", "RUN-A", now - timedelta(hours=1)),
        ("DEC-2", "routing", "RUN-B", now),
        ("DEC-3", "scheduling", "RUN-A", now),
        ("DEC-4", "routing", "RUN-A", now + timedelta(hours=1)),
    ]

    for dec_id, cat, run_id, ts in decisions:
        decision = Decision(
            decision_id=dec_id,
            timestamp=ts.isoformat(),
            category=cat,
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="test",
            metadata={"run_id": run_id},
        )
        registry.log_decision(decision)

    # Query: routing decisions for RUN-A since now
    results = registry.query_decisions(
        category="routing", run_id="RUN-A", since=now.isoformat()
    )

    # Should only get DEC-4
    assert len(results) == 1
    assert results[0].decision_id == "DEC-4"


def test_registry_context_manager(registry):
    """Test registry works as context manager"""
    with DecisionRegistry(":memory:") as reg:
        decision = Decision(
            decision_id="DEC-CTX",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category="test",
            context={},
            options=["opt1"],
            selected_option="opt1",
            rationale="context manager test",
            metadata={},
        )
        reg.log_decision(decision)

        results = reg.query_decisions()
        assert len(results) == 1

    # Registry should be closed after context
