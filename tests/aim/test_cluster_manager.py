"""
Unit tests for ClusterManager.

DOC_ID: DOC-TEST-AIM-CLUSTER-MANAGER-001
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from phase4_routing.modules.aim_tools.src.aim.cluster_manager import (
    ClusterManager,
    launch_cluster,
)
from phase4_routing.modules.aim_tools.src.aim.routing import RoutingStrategy


@pytest.fixture
def mock_registry():
    """Mock AIM registry."""
    return {
        "tools": {
            "aider": {
                "detectCommands": [["aider", "--yes-always"]],
                "capabilities": ["code_generation"],
            }
        }
    }


class TestClusterManagerInit:
    """Test ClusterManager initialization."""

    def test_initialization_success(self, mock_registry):
        """Test successful cluster initialization."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ):
            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            assert cluster.tool_id == "aider"
            assert cluster.count == 3
            assert cluster.routing_strategy == RoutingStrategy.ROUND_ROBIN

    def test_custom_routing_strategy(self, mock_registry):
        """Test initialization with custom routing."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ):
            cluster = ClusterManager(
                "aider",
                count=3,
                routing=RoutingStrategy.LEAST_BUSY,
                registry=mock_registry,
            )

            assert cluster.routing_strategy == RoutingStrategy.LEAST_BUSY


class TestClusterManagerSend:
    """Test send methods."""

    def test_send_uses_routing(self, mock_registry):
        """Test send() uses routing strategy."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.send_prompt.return_value = True
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            # Send 3 prompts - round-robin should distribute
            idx1 = cluster.send("/add file1.py")
            idx2 = cluster.send("/add file2.py")
            idx3 = cluster.send("/add file3.py")

            assert idx1 == 0
            assert idx2 == 1
            assert idx3 == 2

            # Verify prompts were sent
            assert mock_pool.send_prompt.call_count == 3

    def test_send_to_specific_instance(self, mock_registry):
        """Test send_to() targets specific instance."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.send_prompt.return_value = True
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            result = cluster.send_to(1, "/help")

            assert result is True
            mock_pool.send_prompt.assert_called_with(1, "/help")

    def test_send_increments_metrics(self, mock_registry):
        """Test send increments sent counter."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.send_prompt.return_value = True
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            assert cluster._total_sent == 0

            cluster.send("/add file.py")
            assert cluster._total_sent == 1

            cluster.send("/add file2.py")
            assert cluster._total_sent == 2


class TestClusterManagerRead:
    """Test read methods."""

    def test_read_from_instance(self, mock_registry):
        """Test reading from specific instance."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.read_response.return_value = "response line"
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            response = cluster.read(0, timeout=10)

            assert response == "response line"
            mock_pool.read_response.assert_called_with(0, 10)

    def test_read_any_finds_response(self, mock_registry):
        """Test read_any() returns first response."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()

            # Instance 0 and 1 timeout, instance 2 responds
            mock_pool.read_response.side_effect = [None, None, "response from 2"]
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            result = cluster.read_any(timeout=10)

            assert result == (2, "response from 2")

    def test_read_any_returns_none_on_all_timeout(self, mock_registry):
        """Test read_any() returns None if all timeout."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.read_response.return_value = None
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            result = cluster.read_any(timeout=10)

            assert result is None


class TestClusterManagerStatus:
    """Test status and health methods."""

    def test_get_status(self, mock_registry):
        """Test get_status() returns complete info."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.check_health.return_value = {"alive": 3, "dead": 0, "total": 3}
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            cluster._total_sent = 5
            cluster._total_received = 3

            status = cluster.get_status()

            assert status["tool"] == "aider"
            assert status["instances"] == 3
            assert status["routing"] == "round_robin"
            assert status["metrics"]["total_sent"] == 5
            assert status["metrics"]["total_received"] == 3

    def test_check_health_delegates_to_pool(self, mock_registry):
        """Test check_health() uses pool health."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            health_report = {"alive": 3, "dead": 0, "total": 3}
            mock_pool.check_health.return_value = health_report
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            health = cluster.check_health()

            assert health == health_report


class TestClusterManagerManagement:
    """Test cluster management methods."""

    def test_restart_instance(self, mock_registry):
        """Test restarting instance."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool.restart_instance.return_value = True
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            result = cluster.restart_instance(0)

            assert result is True
            mock_pool.restart_instance.assert_called_with(0)

    def test_shutdown(self, mock_registry):
        """Test shutdown delegates to pool."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ) as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool_class.return_value = mock_pool

            cluster = ClusterManager("aider", count=3, registry=mock_registry)

            cluster.shutdown(timeout=3.0)

            mock_pool.shutdown.assert_called_with(3.0)


class TestLaunchCluster:
    """Test launch_cluster() helper function."""

    def test_launch_with_defaults(self, mock_registry):
        """Test launch_cluster() with default params."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ):
            cluster = launch_cluster("aider")

            assert isinstance(cluster, ClusterManager)
            assert cluster.tool_id == "aider"
            assert cluster.count == 3
            assert cluster.routing_strategy == RoutingStrategy.ROUND_ROBIN

    def test_launch_with_custom_params(self, mock_registry):
        """Test launch_cluster() with custom params."""
        with patch(
            "phase4_routing.modules.aim_tools.src.aim.cluster_manager.ToolProcessPool"
        ):
            cluster = launch_cluster("aider", count=5, routing="least_busy")

            assert cluster.count == 5
            assert cluster.routing_strategy == RoutingStrategy.LEAST_BUSY
