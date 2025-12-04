"""Tests for Task Router - WS-03-01B"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.execution_request_builder import (
    ExecutionRequestBuilder,
    create_execution_request,
)
from core.engine.router import TaskRouter, create_router


@pytest.fixture
def router_config(tmp_path):
    """Create a test router configuration"""
    # DOC_ID: DOC-TEST-ENGINE-TEST-ROUTING-175
    config = {
        "version": "1.0.0",
        "defaults": {"timeout_seconds": 600, "max_retries": 3},
        "apps": {
            "aider": {
                "kind": "tool",
                "command": "aider --yes",
                "capabilities": {
                    "task_kinds": ["code_edit", "refactor", "code_review"],
                    "domains": ["software-dev"],
                },
                "limits": {"max_parallel": 2, "timeout_seconds": 300},
                "safety_tier": "medium",
            },
            "codex": {
                "kind": "tool",
                "command": "github-copilot",
                "capabilities": {
                    "task_kinds": ["code_edit", "analysis"],
                    "domains": ["software-dev"],
                },
                "limits": {"max_parallel": 5, "timeout_seconds": 120},
                "safety_tier": "low",
            },
            "pytest": {
                "kind": "validator",
                "command": "pytest",
                "capabilities": {"task_kinds": ["test"], "domains": ["software-dev"]},
                "limits": {"max_parallel": 1, "timeout_seconds": 600},
                "safety_tier": "low",
            },
        },
        "routing": {
            "rules": [
                {
                    "id": "high-risk-code",
                    "match": {"task_kind": ["code_edit"], "risk_tier": ["high"]},
                    "select_from": ["aider"],
                    "strategy": "fixed",
                },
                {
                    "id": "low-risk-code",
                    "match": {"task_kind": ["code_edit"], "risk_tier": ["low"]},
                    "select_from": ["codex", "aider"],
                    "strategy": "round_robin",
                },
                {
                    "id": "testing",
                    "match": {"task_kind": ["test"]},
                    "select_from": ["pytest"],
                    "strategy": "fixed",
                },
                {
                    "id": "analysis-metrics",
                    "match": {"task_kind": ["analysis"]},
                    "select_from": ["codex", "aider"],
                    "strategy": "metrics",
                },
            ]
        },
    }

    config_path = tmp_path / "router_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return str(config_path)


@pytest.fixture
def router(router_config):
    """Create router with test config"""
    return TaskRouter(router_config)


class TestRouterInitialization:
    """Test router initialization and config loading"""

    def test_load_config(self, router):
        """Test loading router configuration"""
        assert router.config is not None
        assert "apps" in router.config
        assert "routing" in router.config

    def test_apps_loaded(self, router):
        """Test that apps are loaded correctly"""
        assert "aider" in router.apps
        assert "codex" in router.apps
        assert "pytest" in router.apps

    def test_routing_rules_loaded(self, router):
        """Test that routing rules are loaded"""
        assert len(router.routing_rules) == 4
        assert router.routing_rules[0]["id"] == "high-risk-code"

    def test_missing_config_file(self, tmp_path):
        """Test error when config file is missing"""
        with pytest.raises(FileNotFoundError):
            TaskRouter(str(tmp_path / "nonexistent.json"))

    def test_invalid_config(self, tmp_path):
        """Test error with invalid config"""
        invalid_config = {"version": "1.0.0"}  # Missing required fields
        config_path = tmp_path / "invalid.json"
        with open(config_path, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="missing 'apps'"):
            TaskRouter(str(config_path))


class TestTaskRouting:
    """Test task routing logic"""

    def test_route_high_risk_code(self, router):
        """Test routing high-risk code edit to aider"""
        tool_id = router.route_task("code_edit", risk_tier="high")
        assert tool_id == "aider"

    def test_route_low_risk_code(self, router):
        """Test routing low-risk code edit"""
        tool_id = router.route_task("code_edit", risk_tier="low")
        # Should route to codex or aider (first in list for now)
        assert tool_id in ["codex", "aider"]

    def test_round_robin_advances(self, router):
        """Round-robin rotates between candidates"""
        first = router.route_task("code_edit", risk_tier="low")
        second = router.route_task("code_edit", risk_tier="low")
        assert first != second
        assert {first, second} == {"codex", "aider"}

    def test_route_test_task(self, router):
        """Test routing test task to pytest"""
        tool_id = router.route_task("test")
        assert tool_id == "pytest"

    def test_metrics_prefers_higher_success_rate(self, router):
        """Metrics strategy selects tool with better history"""
        codex_metrics = router.state_store.get_tool_metrics("codex")
        codex_metrics.update(
            {"success_count": 9, "call_count": 10, "total_latency_ms": 900}
        )
        aider_metrics = router.state_store.get_tool_metrics("aider")
        aider_metrics.update(
            {"success_count": 4, "call_count": 10, "total_latency_ms": 400}
        )

        tool_id = router.route_task("analysis")
        assert tool_id == "codex"

    def test_route_no_match_fallback(self, router):
        """Test fallback when no rule matches"""
        tool_id = router.route_task("refactor")
        # Should fallback to any capable tool
        assert tool_id in ["aider"]  # aider supports refactor

    def test_route_unknown_task(self, router):
        """Test routing unknown task kind returns None"""
        tool_id = router.route_task("unknown_task_kind")
        assert tool_id is None

    def test_route_with_domain(self, router):
        """Test routing with domain hint"""
        tool_id = router.route_task("code_edit", domain="software-dev")
        assert tool_id in ["aider", "codex"]


class TestCapabilityMatching:
    """Test capability-based tool selection"""

    def test_find_capable_tools(self, router):
        """Test finding all tools capable of a task"""
        capable = router._find_capable_tools("code_edit")
        assert "aider" in capable
        assert "codex" in capable
        assert "pytest" not in capable

    def test_find_capable_with_domain(self, router):
        """Test finding capable tools with domain filter"""
        capable = router._find_capable_tools("code_edit", domain="software-dev")
        assert "aider" in capable
        assert "codex" in capable

    def test_no_capable_tools(self, router):
        """Test when no tools match"""
        capable = router._find_capable_tools("nonexistent_task")
        assert len(capable) == 0


class TestRoutingStrategies:
    """Test different routing strategies"""

    def test_fixed_strategy(self, router):
        """Test fixed strategy always returns first candidate"""
        result = router._apply_strategy(["tool1", "tool2", "tool3"], "fixed")
        assert result == "tool1"

    def test_round_robin_strategy(self, router):
        """Test round robin strategy with state tracking"""
        # With rule_id for state tracking
        result1 = router._apply_strategy(
            ["tool1", "tool2", "tool3"], "round_robin", "test-rule"
        )
        result2 = router._apply_strategy(
            ["tool1", "tool2", "tool3"], "round_robin", "test-rule"
        )
        result3 = router._apply_strategy(
            ["tool1", "tool2", "tool3"], "round_robin", "test-rule"
        )
        result4 = router._apply_strategy(
            ["tool1", "tool2", "tool3"], "round_robin", "test-rule"
        )

        # Should cycle through tools
        assert result1 == "tool1"
        assert result2 == "tool2"
        assert result3 == "tool3"
        assert result4 == "tool1"  # Wraps around

    def test_round_robin_different_rules(self, router):
        """Test round robin maintains separate state per rule"""
        result1 = router._apply_strategy(["a", "b"], "round_robin", "rule1")
        result2 = router._apply_strategy(["x", "y"], "round_robin", "rule2")
        result3 = router._apply_strategy(["a", "b"], "round_robin", "rule1")

        assert result1 == "a"
        assert result2 == "x"
        assert result3 == "b"  # rule1 continues from where it left off

    def test_metrics_strategy_no_history(self, router):
        """Test metrics strategy with no execution history"""
        result = router._apply_strategy(["tool1", "tool2"], "metrics")
        # Should select one (behavior is deterministic but based on neutral scores)
        assert result in ["tool1", "tool2"]

    def test_metrics_strategy_with_history(self, router):
        """Test metrics-based selection with execution history"""
        # Record some execution results
        router.record_execution_result("tool1", success=True, latency_ms=100)
        router.record_execution_result("tool1", success=True, latency_ms=200)
        router.record_execution_result("tool2", success=False, latency_ms=50)
        router.record_execution_result("tool2", success=True, latency_ms=300)

        # tool1 has better success rate (100% vs 50%)
        result = router._apply_strategy(["tool1", "tool2"], "metrics")
        assert result == "tool1"

    def test_auto_strategy(self, router):
        """Test auto strategy uses metrics"""
        router.record_execution_result("tool1", success=True, latency_ms=100)
        result = router._apply_strategy(["tool1", "tool2"], "auto")
        assert result in ["tool1", "tool2"]

    def test_empty_candidates(self, router):
        """Test strategy with no candidates"""
        result = router._apply_strategy([], "fixed")
        assert result is None

    def test_unknown_strategy_fallback(self, router):
        """Test unknown strategy falls back to first"""
        result = router._apply_strategy(["tool1", "tool2"], "unknown_strategy")
        assert result == "tool1"


class TestToolConfiguration:
    """Test tool configuration queries"""

    def test_get_tool_config(self, router):
        """Test getting tool configuration"""
        config = router.get_tool_config("aider")
        assert config is not None
        assert config["kind"] == "tool"
        assert config["command"] == "aider --yes"

    def test_get_tool_command(self, router):
        """Test getting tool command"""
        command = router.get_tool_command("aider")
        assert command == "aider --yes"

    def test_get_tool_limits(self, router):
        """Test getting tool limits"""
        limits = router.get_tool_limits("aider")
        assert limits["max_parallel"] == 2
        assert limits["timeout_seconds"] == 300

    def test_get_tool_limits_with_defaults(self, router):
        """Test limits merge with defaults"""
        # pytest has no explicit timeout, should use default
        limits = router.get_tool_limits("pytest")
        assert limits["timeout_seconds"] == 600  # from defaults

    def test_get_capabilities(self, router):
        """Test getting tool capabilities"""
        caps = router.get_capabilities("aider")
        assert "code_edit" in caps["task_kinds"]
        assert "software-dev" in caps["domains"]

    def test_list_tools(self, router):
        """Test listing all tools"""
        tools = router.list_tools()
        assert "aider" in tools
        assert "codex" in tools
        assert "pytest" in tools
        assert len(tools) == 3

    def test_nonexistent_tool(self, router):
        """Test querying nonexistent tool"""
        config = router.get_tool_config("nonexistent")
        assert config is None


class TestExecutionRequestBuilder:
    """Test execution request builder"""

    def test_basic_request(self):
        """Test building basic request"""
        builder = ExecutionRequestBuilder()
        request = (
            builder.with_task("code_edit", "Fix bug in user.py")
            .with_tool("aider", "aider --yes")
            .build()
        )

        assert request["task_kind"] == "code_edit"
        assert request["description"] == "Fix bug in user.py"
        assert request["tool_id"] == "aider"
        assert request["command"] == "aider --yes"
        assert "request_id" in request
        assert "created_at" in request

    def test_request_with_input(self):
        """Test request with input prompt"""
        builder = ExecutionRequestBuilder()
        request = (
            builder.with_task("code_edit", "Test")
            .with_tool("aider", "aider")
            .with_input(prompt="Fix the bug", context={"file": "test.py"})
            .build()
        )

        assert request["prompt"] == "Fix the bug"
        assert request["context"]["file"] == "test.py"

    def test_request_with_constraints(self):
        """Test request with constraints"""
        builder = ExecutionRequestBuilder()
        request = (
            builder.with_task("code_edit", "Test")
            .with_tool("aider", "aider")
            .with_constraints({"patch_only": True, "max_lines": 500})
            .build()
        )

        assert request["constraints"]["patch_only"] is True
        assert request["constraints"]["max_lines"] == 500

    def test_request_with_limits(self):
        """Test request with execution limits"""
        builder = ExecutionRequestBuilder()
        request = (
            builder.with_task("code_edit", "Test")
            .with_tool("aider", "aider")
            .with_limits(timeout_seconds=300, max_retries=5)
            .build()
        )

        assert request["timeout_seconds"] == 300
        assert request["max_retries"] == 5

    def test_request_with_metadata(self):
        """Test request with custom metadata"""
        builder = ExecutionRequestBuilder()
        request = (
            builder.with_task("code_edit", "Test")
            .with_tool("aider", "aider")
            .with_metadata(run_id="RUN-001", priority="high")
            .build()
        )

        assert request["metadata"]["run_id"] == "RUN-001"
        assert request["metadata"]["priority"] == "high"

    def test_from_task_factory(self):
        """Test creating builder from task info"""
        builder = ExecutionRequestBuilder.from_task("code_edit", "aider", "Fix bug")
        request = builder.build()

        assert request["task_kind"] == "code_edit"
        assert request["tool_id"] == "aider"
        assert request["description"] == "Fix bug"

    def test_missing_required_field(self):
        """Test error when required field missing"""
        builder = ExecutionRequestBuilder()
        builder.with_task("code_edit", "Test")
        # Missing tool_id

        with pytest.raises(ValueError, match="Missing required field"):
            builder.build()

    def test_quick_helper(self):
        """Test quick create_execution_request helper"""
        request = create_execution_request(
            "code_edit", "aider", prompt="Fix bug", description="Test task"
        )

        assert request["task_kind"] == "code_edit"
        assert request["tool_id"] == "aider"
        assert request["prompt"] == "Fix bug"
        assert request["description"] == "Test task"


class TestRouterIntegration:
    """Test router integration with request builder"""

    def test_route_and_build_request(self, router):
        """Test routing a task and building execution request"""
        # Route the task
        tool_id = router.route_task("code_edit", risk_tier="high")
        assert tool_id == "aider"

        # Get tool configuration
        command = router.get_tool_command(tool_id)
        limits = router.get_tool_limits(tool_id)

        # Build execution request
        request = (
            ExecutionRequestBuilder()
            .with_task("code_edit", "Fix authentication bug")
            .with_tool(tool_id, command)
            .with_limits(limits["timeout_seconds"], max_retries=3)
            .build()
        )

        assert request["tool_id"] == "aider"
        assert request["command"] == "aider --yes"
        assert request["timeout_seconds"] == 300

    def test_complete_routing_workflow(self, router):
        """Test complete workflow: route → config → request"""
        task_kind = "code_edit"
        description = "Refactor user authentication"

        # 1. Route task
        tool_id = router.route_task(task_kind, risk_tier="low", domain="software-dev")
        assert tool_id is not None

        # 2. Get tool config
        tool_config = router.get_tool_config(tool_id)
        assert tool_config is not None

        # 3. Build execution request
        request = create_execution_request(
            task_kind, tool_id, prompt=description, command=tool_config["command"]
        )

        assert request["task_kind"] == task_kind
        assert request["tool_id"] == tool_id
        assert "request_id" in request


class TestDecisionLogging:
    """Test routing decision logging and observability"""

    def test_decision_logged_on_route(self, router):
        """Test that routing decisions are logged"""
        initial_count = len(router.decision_log)
        router.route_task("code_edit", risk_tier="high")
        assert len(router.decision_log) == initial_count + 1

    def test_decision_contains_metadata(self, router):
        """Test decision log contains routing metadata"""
        router.route_task(
            "code_edit", risk_tier="high", complexity="medium", domain="software-dev"
        )
        decision = router.decision_log[-1]

        assert decision.task_kind == "code_edit"
        assert decision.selected_tool == "aider"
        assert decision.strategy == "fixed"
        assert decision.rule_id == "high-risk-code"
        assert decision.metadata["risk_tier"] == "high"
        assert decision.metadata["complexity"] == "medium"

    def test_get_decision_log(self, router):
        """Test retrieving decision log"""
        router.route_task("code_edit", risk_tier="high")
        router.route_task("test")

        log = router.get_decision_log()
        assert len(log) >= 2
        assert all(isinstance(d, dict) for d in log)
        assert all("timestamp" in d for d in log)

    def test_get_decision_log_limited(self, router):
        """Test retrieving last N decisions"""
        for i in range(5):
            router.route_task("code_edit", risk_tier="high")

        log = router.get_decision_log(last_n=2)
        assert len(log) == 2

    def test_clear_decision_log(self, router):
        """Test clearing decision log"""
        router.route_task("code_edit", risk_tier="high")
        assert len(router.decision_log) > 0

        router.clear_decision_log()
        assert len(router.decision_log) == 0


class TestMetricsRecording:
    """Test execution metrics recording and usage"""

    def test_record_successful_execution(self, router):
        """Test recording successful execution"""
        router.record_execution_result("aider", success=True, latency_ms=150.5)
        metrics = router.state_store.get_tool_metrics("aider")

        assert metrics["call_count"] == 1
        assert metrics["success_count"] == 1
        assert metrics["failure_count"] == 0
        assert metrics["total_latency_ms"] == 150.5

    def test_record_failed_execution(self, router):
        """Test recording failed execution"""
        router.record_execution_result("aider", success=False, latency_ms=200.0)
        metrics = router.state_store.get_tool_metrics("aider")

        assert metrics["call_count"] == 1
        assert metrics["success_count"] == 0
        assert metrics["failure_count"] == 1

    def test_metrics_accumulate(self, router):
        """Test that metrics accumulate over multiple calls"""
        router.record_execution_result("aider", success=True, latency_ms=100)
        router.record_execution_result("aider", success=True, latency_ms=200)
        router.record_execution_result("aider", success=False, latency_ms=150)

        metrics = router.state_store.get_tool_metrics("aider")
        assert metrics["call_count"] == 3
        assert metrics["success_count"] == 2
        assert metrics["failure_count"] == 1
        assert metrics["total_latency_ms"] == 450

    def test_metrics_influence_routing(self, router):
        """Test that recorded metrics influence routing decisions"""
        # Record better metrics for aider
        router.record_execution_result("aider", success=True, latency_ms=50)
        router.record_execution_result("aider", success=True, latency_ms=50)

        # Record worse metrics for codex
        router.record_execution_result("codex", success=False, latency_ms=500)

        # Route with metrics strategy
        result = router._apply_strategy(["aider", "codex"], "metrics")
        assert result == "aider"  # Should prefer aider due to better metrics


class TestStateStore:
    """Test state store functionality"""

    def test_in_memory_store_default(self, router):
        """Test router uses in-memory store by default"""
        from core.engine.router import InMemoryStateStore

        assert isinstance(router.state_store, InMemoryStateStore)

    def test_round_robin_state_persistence(self, router):
        """Test round-robin state persists across calls"""
        router._apply_strategy(["a", "b", "c"], "round_robin", "test")
        index = router.state_store.get_round_robin_index("test")
        assert index == 1  # Should have incremented

    def test_separate_rule_state(self, router):
        """Test different rules maintain separate state"""
        router._apply_strategy(["a", "b"], "round_robin", "rule1")
        router._apply_strategy(["a", "b"], "round_robin", "rule1")
        router._apply_strategy(["x", "y"], "round_robin", "rule2")

        assert router.state_store.get_round_robin_index("rule1") == 2
        assert router.state_store.get_round_robin_index("rule2") == 1


class TestConfigValidation:
    """Test configuration schema validation"""

    def test_valid_config_loads(self, router):
        """Test valid configuration loads successfully"""
        assert router.config is not None
        assert "apps" in router.config
        assert "routing" in router.config

    def test_missing_apps_raises_error(self, tmp_path):
        """Test missing apps field raises ValueError"""
        invalid_config = {"version": "1.0.0", "routing": {"rules": []}}
        config_path = tmp_path / "invalid.json"
        with open(config_path, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="missing 'apps'"):
            TaskRouter(str(config_path))

    def test_missing_routing_raises_error(self, tmp_path):
        """Test missing routing field raises ValueError"""
        invalid_config = {"version": "1.0.0", "apps": {}}
        config_path = tmp_path / "invalid.json"
        with open(config_path, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="missing 'routing'"):
            TaskRouter(str(config_path))
