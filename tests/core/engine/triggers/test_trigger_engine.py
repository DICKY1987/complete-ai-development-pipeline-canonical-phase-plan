"""Tests for trigger engine functionality.

DOC_ID: DOC-CORE-TRIGGERS-TEST-TRIGGER-ENGINE-876
"""

import pytest
from unittest.mock import Mock

from core.engine.triggers.trigger_engine import TriggerEngine, TriggerRule
from core.events.event_bus import EventBus


def test_trigger_rule_matching():
    """Test trigger rule pattern matching."""
    rule = TriggerRule(
        rule_id="test_rule",
        event_pattern="phase.*.completed",
        workstream_id="WS-TEST"
    )
    
    assert rule.matches("phase.1.completed")
    assert rule.matches("phase.2.completed")
    assert not rule.matches("phase.1.started")
    assert not rule.matches("task.completed")


def test_trigger_rule_with_condition():
    """Test trigger rule with condition."""
    rule = TriggerRule(
        rule_id="test_rule",
        event_pattern="error.*",
        workstream_id="WS-ERROR",
        condition={"severity": "critical"}
    )
    
    assert rule.matches("error.detected", {"severity": "critical"})
    assert not rule.matches("error.detected", {"severity": "warning"})
    assert not rule.matches("error.detected", {})


def test_trigger_engine_registration():
    """Test registering triggers."""
    event_bus = Mock(spec=EventBus)
    engine = TriggerEngine(event_bus, config_path=None)
    
    rule = engine.register_trigger(
        rule_id="test",
        event_pattern="test.*",
        workstream_id="WS-TEST"
    )
    
    assert rule.rule_id == "test"
    assert "test" in engine.rules


def test_trigger_engine_evaluation():
    """Test trigger evaluation."""
    event_bus = Mock(spec=EventBus)
    orchestrator = Mock()
    orchestrator.launch_workstream.return_value = "run-123"
    
    engine = TriggerEngine(event_bus, orchestrator, config_path=None)
    engine.register_trigger(
        rule_id="test",
        event_pattern="phase.1.completed",
        workstream_id="WS-PHASE-2"
    )
    
    triggered = engine.evaluate_triggers("phase.1.completed", {})
    
    assert "WS-PHASE-2" in triggered
    orchestrator.launch_workstream.assert_called_once()


def test_trigger_engine_disabled_rule():
    """Test that disabled rules don't trigger."""
    event_bus = Mock(spec=EventBus)
    orchestrator = Mock()
    
    engine = TriggerEngine(event_bus, orchestrator, config_path=None)
    engine.register_trigger(
        rule_id="test",
        event_pattern="test.*",
        workstream_id="WS-TEST",
        enabled=False
    )
    
    triggered = engine.evaluate_triggers("test.event", {})
    
    assert len(triggered) == 0
    orchestrator.launch_workstream.assert_not_called()


def test_trigger_engine_enable_disable():
    """Test enabling and disabling rules."""
    event_bus = Mock(spec=EventBus)
    engine = TriggerEngine(event_bus, config_path=None)
    
    engine.register_trigger(
        rule_id="test",
        event_pattern="test.*",
        workstream_id="WS-TEST"
    )
    
    assert engine.disable_rule("test")
    assert not engine.rules["test"].enabled
    
    assert engine.enable_rule("test")
    assert engine.rules["test"].enabled
