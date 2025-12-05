"""
Unit tests for routing strategies.

DOC_ID: DOC-TEST-AIM-ROUTING-001
"""

import pytest

from phase4_routing.modules.aim_tools.src.aim.routing import (
    LeastBusyRouter,
    RoundRobinRouter,
    RoutingStrategy,
    StickyRouter,
    create_router,
)


class TestRoundRobinRouter:
    """Test round-robin routing strategy."""

    def test_cycles_through_instances(self):
        """Test round-robin cycles through all instances."""
        router = RoundRobinRouter()

        # With 3 instances, should cycle 0, 1, 2, 0, 1, 2, ...
        assert router.select_instance(3) == 0
        assert router.select_instance(3) == 1
        assert router.select_instance(3) == 2
        assert router.select_instance(3) == 0  # Wraps around
        assert router.select_instance(3) == 1

    def test_handles_single_instance(self):
        """Test round-robin with only 1 instance."""
        router = RoundRobinRouter()

        assert router.select_instance(1) == 0
        assert router.select_instance(1) == 0
        assert router.select_instance(1) == 0

    def test_raises_on_zero_instances(self):
        """Test error when no instances available."""
        router = RoundRobinRouter()

        with pytest.raises(ValueError, match="No instances available"):
            router.select_instance(0)


class TestLeastBusyRouter:
    """Test least-busy routing strategy."""

    def test_selects_least_busy(self):
        """Test selects instance with fewest pending."""
        router = LeastBusyRouter()

        # All equal initially, should select 0
        idx = router.select_instance(3)
        assert idx == 0

        # Record work on instance 0
        router.record_assignment(0)

        # Should now select 1 or 2 (both have 0 pending)
        idx = router.select_instance(3)
        assert idx in [1, 2]

    def test_tracks_pending_correctly(self):
        """Test pending count tracking."""
        router = LeastBusyRouter()

        # Assign work to instance 0
        router.select_instance(2)
        router.record_assignment(0)

        # Instance 1 should be selected (less busy)
        assert router.select_instance(2) == 1

        # Complete work on instance 0
        router.record_completion(0)

        # Now both equal, should select 0 again
        assert router.select_instance(2) == 0

    def test_handles_completion_without_underflow(self):
        """Test completion doesn't go negative."""
        router = LeastBusyRouter()

        # Complete work without assignment
        router.record_completion(0)
        router.record_completion(0)

        # Should still work
        assert router.select_instance(1) == 0


class TestStickyRouter:
    """Test sticky routing strategy."""

    def test_always_selects_zero(self):
        """Test sticky always routes to instance 0."""
        router = StickyRouter()

        assert router.select_instance(5) == 0
        assert router.select_instance(5) == 0
        assert router.select_instance(5) == 0

    def test_raises_on_zero_instances(self):
        """Test error when no instances."""
        router = StickyRouter()

        with pytest.raises(ValueError, match="No instances available"):
            router.select_instance(0)


class TestCreateRouter:
    """Test router factory function."""

    def test_creates_round_robin(self):
        """Test factory creates round-robin router."""
        router = create_router(RoutingStrategy.ROUND_ROBIN)

        assert isinstance(router, RoundRobinRouter)
        assert router.select_instance(3) == 0
        assert router.select_instance(3) == 1

    def test_creates_least_busy(self):
        """Test factory creates least-busy router."""
        router = create_router(RoutingStrategy.LEAST_BUSY)

        assert isinstance(router, LeastBusyRouter)

    def test_creates_sticky(self):
        """Test factory creates sticky router."""
        router = create_router(RoutingStrategy.STICKY)

        assert isinstance(router, StickyRouter)
        assert router.select_instance(3) == 0
