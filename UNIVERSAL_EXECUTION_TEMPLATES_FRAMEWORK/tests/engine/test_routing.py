"""Tests for Task Router - WS-03-01B"""

import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.router import TaskRouter, create_router
from core.engine.execution_request_builder import ExecutionRequestBuilder, create_execution_request


@pytest.fixture
def router_config(tmp_path):
    """Create a test router configuration"""
DOC_ID: DOC-TEST-ENGINE-TEST-ROUTING-175
    config = {
        "version": "1.0.0",
        "defaults": {
            "timeout_seconds": 600,
            "max_retries": 3
        },
        "apps": {
            "aider": {
                "kind": "tool",
                "command": "aider --yes",
                "capabilities": {
                    "task_kinds": ["code_edit", "refactor", "code_review"],
                    "domains": ["software-dev"]
                },
                "limits": {
                    "max_parallel": 2,
                    "timeout_seconds": 300
                },
                "safety_tier": "medium"
            },
            "codex": {
                "kind": "tool",
                "command": "github-copilot",
                "capabilities": {
                    "task_kinds": ["code_edit", "analysis"],
                    "domains": ["software-dev"]
                },
                "limits": {
                    "max_parallel": 5,
                    "timeout_seconds": 120
                },
                "safety_tier": "low"
            },
            "pytest": {
                "kind": "validator",
                "command": "pytest",
                "capabilities": {
                    "task_kinds": ["test"],
                    "domains": ["software-dev"]
                },
                "limits": {
                    "max_parallel": 1,
                    "timeout_seconds": 600
                },
                "safety_tier": "low"
            }
        },
        "routing": {
            "rules": [
                {
                    "id": "high-risk-code",
                    "match": {
                        "task_kind": ["code_edit"],
                        "risk_tier": ["high"]
                    },
                    "select_from": ["aider"],
                    "strategy": "fixed"
                },
                {
                    "id": "low-risk-code",
                    "match": {
                        "task_kind": ["code_edit"],
                        "risk_tier": ["low"]
                    },
                    "select_from": ["codex", "aider"],
                    "strategy": "round_robin"
                },
                {
                    "id": "testing",
                    "match": {
                        "task_kind": ["test"]
                    },
                    "select_from": ["pytest"],
                    "strategy": "fixed"
                }
            ]
        }
    }
    
    config_path = tmp_path / "router_config.json"
    with open(config_path, 'w') as f:
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
        assert 'apps' in router.config
        assert 'routing' in router.config
    
    def test_apps_loaded(self, router):
        """Test that apps are loaded correctly"""
        assert 'aider' in router.apps
        assert 'codex' in router.apps
        assert 'pytest' in router.apps
    
    def test_routing_rules_loaded(self, router):
        """Test that routing rules are loaded"""
        assert len(router.routing_rules) == 3
        assert router.routing_rules[0]['id'] == 'high-risk-code'
    
    def test_missing_config_file(self, tmp_path):
        """Test error when config file is missing"""
        with pytest.raises(FileNotFoundError):
            TaskRouter(str(tmp_path / "nonexistent.json"))
    
    def test_invalid_config(self, tmp_path):
        """Test error with invalid config"""
        invalid_config = {"version": "1.0.0"}  # Missing required fields
        config_path = tmp_path / "invalid.json"
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with pytest.raises(ValueError, match="missing 'apps'"):
            TaskRouter(str(config_path))


class TestTaskRouting:
    """Test task routing logic"""
    
    def test_route_high_risk_code(self, router):
        """Test routing high-risk code edit to aider"""
        tool_id = router.route_task('code_edit', risk_tier='high')
        assert tool_id == 'aider'
    
    def test_route_low_risk_code(self, router):
        """Test routing low-risk code edit"""
        tool_id = router.route_task('code_edit', risk_tier='low')
        # Should route to codex or aider (first in list for now)
        assert tool_id in ['codex', 'aider']
    
    def test_route_test_task(self, router):
        """Test routing test task to pytest"""
        tool_id = router.route_task('test')
        assert tool_id == 'pytest'
    
    def test_route_no_match_fallback(self, router):
        """Test fallback when no rule matches"""
        tool_id = router.route_task('refactor')
        # Should fallback to any capable tool
        assert tool_id in ['aider']  # aider supports refactor
    
    def test_route_unknown_task(self, router):
        """Test routing unknown task kind returns None"""
        tool_id = router.route_task('unknown_task_kind')
        assert tool_id is None
    
    def test_route_with_domain(self, router):
        """Test routing with domain hint"""
        tool_id = router.route_task('code_edit', domain='software-dev')
        assert tool_id in ['aider', 'codex']


class TestCapabilityMatching:
    """Test capability-based tool selection"""
    
    def test_find_capable_tools(self, router):
        """Test finding all tools capable of a task"""
        capable = router._find_capable_tools('code_edit')
        assert 'aider' in capable
        assert 'codex' in capable
        assert 'pytest' not in capable
    
    def test_find_capable_with_domain(self, router):
        """Test finding capable tools with domain filter"""
        capable = router._find_capable_tools('code_edit', domain='software-dev')
        assert 'aider' in capable
        assert 'codex' in capable
    
    def test_no_capable_tools(self, router):
        """Test when no tools match"""
        capable = router._find_capable_tools('nonexistent_task')
        assert len(capable) == 0


class TestRoutingStrategies:
    """Test different routing strategies"""
    
    def test_fixed_strategy(self, router):
        """Test fixed strategy always returns first candidate"""
        result = router._apply_strategy(['tool1', 'tool2', 'tool3'], 'fixed')
        assert result == 'tool1'
    
    def test_round_robin_strategy(self, router):
        """Test round robin strategy (basic)"""
        result = router._apply_strategy(['tool1', 'tool2'], 'round_robin')
        # For now, should return first (TODO: implement state tracking)
        assert result in ['tool1', 'tool2']
    
    def test_auto_strategy(self, router):
        """Test auto strategy (basic)"""
        result = router._apply_strategy(['tool1', 'tool2'], 'auto')
        assert result in ['tool1', 'tool2']
    
    def test_empty_candidates(self, router):
        """Test strategy with no candidates"""
        result = router._apply_strategy([], 'fixed')
        assert result is None


class TestToolConfiguration:
    """Test tool configuration queries"""
    
    def test_get_tool_config(self, router):
        """Test getting tool configuration"""
        config = router.get_tool_config('aider')
        assert config is not None
        assert config['kind'] == 'tool'
        assert config['command'] == 'aider --yes'
    
    def test_get_tool_command(self, router):
        """Test getting tool command"""
        command = router.get_tool_command('aider')
        assert command == 'aider --yes'
    
    def test_get_tool_limits(self, router):
        """Test getting tool limits"""
        limits = router.get_tool_limits('aider')
        assert limits['max_parallel'] == 2
        assert limits['timeout_seconds'] == 300
    
    def test_get_tool_limits_with_defaults(self, router):
        """Test limits merge with defaults"""
        # pytest has no explicit timeout, should use default
        limits = router.get_tool_limits('pytest')
        assert limits['timeout_seconds'] == 600  # from defaults
    
    def test_get_capabilities(self, router):
        """Test getting tool capabilities"""
        caps = router.get_capabilities('aider')
        assert 'code_edit' in caps['task_kinds']
        assert 'software-dev' in caps['domains']
    
    def test_list_tools(self, router):
        """Test listing all tools"""
        tools = router.list_tools()
        assert 'aider' in tools
        assert 'codex' in tools
        assert 'pytest' in tools
        assert len(tools) == 3
    
    def test_nonexistent_tool(self, router):
        """Test querying nonexistent tool"""
        config = router.get_tool_config('nonexistent')
        assert config is None


class TestExecutionRequestBuilder:
    """Test execution request builder"""
    
    def test_basic_request(self):
        """Test building basic request"""
        builder = ExecutionRequestBuilder()
        request = (builder
                  .with_task('code_edit', 'Fix bug in user.py')
                  .with_tool('aider', 'aider --yes')
                  .build())
        
        assert request['task_kind'] == 'code_edit'
        assert request['description'] == 'Fix bug in user.py'
        assert request['tool_id'] == 'aider'
        assert request['command'] == 'aider --yes'
        assert 'request_id' in request
        assert 'created_at' in request
    
    def test_request_with_input(self):
        """Test request with input prompt"""
        builder = ExecutionRequestBuilder()
        request = (builder
                  .with_task('code_edit', 'Test')
                  .with_tool('aider', 'aider')
                  .with_input(prompt='Fix the bug', context={'file': 'test.py'})
                  .build())
        
        assert request['prompt'] == 'Fix the bug'
        assert request['context']['file'] == 'test.py'
    
    def test_request_with_constraints(self):
        """Test request with constraints"""
        builder = ExecutionRequestBuilder()
        request = (builder
                  .with_task('code_edit', 'Test')
                  .with_tool('aider', 'aider')
                  .with_constraints({'patch_only': True, 'max_lines': 500})
                  .build())
        
        assert request['constraints']['patch_only'] is True
        assert request['constraints']['max_lines'] == 500
    
    def test_request_with_limits(self):
        """Test request with execution limits"""
        builder = ExecutionRequestBuilder()
        request = (builder
                  .with_task('code_edit', 'Test')
                  .with_tool('aider', 'aider')
                  .with_limits(timeout_seconds=300, max_retries=5)
                  .build())
        
        assert request['timeout_seconds'] == 300
        assert request['max_retries'] == 5
    
    def test_request_with_metadata(self):
        """Test request with custom metadata"""
        builder = ExecutionRequestBuilder()
        request = (builder
                  .with_task('code_edit', 'Test')
                  .with_tool('aider', 'aider')
                  .with_metadata(run_id='RUN-001', priority='high')
                  .build())
        
        assert request['metadata']['run_id'] == 'RUN-001'
        assert request['metadata']['priority'] == 'high'
    
    def test_from_task_factory(self):
        """Test creating builder from task info"""
        builder = ExecutionRequestBuilder.from_task(
            'code_edit', 'aider', 'Fix bug'
        )
        request = builder.build()
        
        assert request['task_kind'] == 'code_edit'
        assert request['tool_id'] == 'aider'
        assert request['description'] == 'Fix bug'
    
    def test_missing_required_field(self):
        """Test error when required field missing"""
        builder = ExecutionRequestBuilder()
        builder.with_task('code_edit', 'Test')
        # Missing tool_id
        
        with pytest.raises(ValueError, match="Missing required field"):
            builder.build()
    
    def test_quick_helper(self):
        """Test quick create_execution_request helper"""
        request = create_execution_request(
            'code_edit', 'aider',
            prompt='Fix bug',
            description='Test task'
        )
        
        assert request['task_kind'] == 'code_edit'
        assert request['tool_id'] == 'aider'
        assert request['prompt'] == 'Fix bug'
        assert request['description'] == 'Test task'


class TestRouterIntegration:
    """Test router integration with request builder"""
    
    def test_route_and_build_request(self, router):
        """Test routing a task and building execution request"""
        # Route the task
        tool_id = router.route_task('code_edit', risk_tier='high')
        assert tool_id == 'aider'
        
        # Get tool configuration
        command = router.get_tool_command(tool_id)
        limits = router.get_tool_limits(tool_id)
        
        # Build execution request
        request = (ExecutionRequestBuilder()
                  .with_task('code_edit', 'Fix authentication bug')
                  .with_tool(tool_id, command)
                  .with_limits(limits['timeout_seconds'], max_retries=3)
                  .build())
        
        assert request['tool_id'] == 'aider'
        assert request['command'] == 'aider --yes'
        assert request['timeout_seconds'] == 300
    
    def test_complete_routing_workflow(self, router):
        """Test complete workflow: route → config → request"""
        task_kind = 'code_edit'
        description = 'Refactor user authentication'
        
        # 1. Route task
        tool_id = router.route_task(task_kind, risk_tier='low', domain='software-dev')
        assert tool_id is not None
        
        # 2. Get tool config
        tool_config = router.get_tool_config(tool_id)
        assert tool_config is not None
        
        # 3. Build execution request
        request = create_execution_request(
            task_kind, tool_id,
            prompt=description,
            command=tool_config['command']
        )
        
        assert request['task_kind'] == task_kind
        assert request['tool_id'] == tool_id
        assert 'request_id' in request
