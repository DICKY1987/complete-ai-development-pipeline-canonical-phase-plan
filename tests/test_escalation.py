"""
Unit tests for EscalationManager (Phase 4B)
Tests escalation rules, job creation, and escalation chains.
"""
# DOC_ID: DOC-TEST-TESTS-TEST-ESCALATION-080
# DOC_ID: DOC-TEST-TESTS-TEST-ESCALATION-041
import pytest
from engine.queue.escalation import (
    EscalationManager, ESCALATION_RULES
)
from engine.queue.job_wrapper import JobWrapper, JobPriority


def test_default_escalation_rules():
    """Test default escalation rules are loaded"""
    manager = EscalationManager()
    
    assert "aider" in manager.rules
    assert "tests" in manager.rules
    assert "git" in manager.rules
    assert "codex" in manager.rules


def test_aider_escalation_rule():
    """Test aider escalation configuration"""
    manager = EscalationManager()
    rule = manager.rules["aider"]
    
    assert rule["on_failure"] == "codex"
    assert rule["on_timeout"] == "codex"
    assert rule["max_retries_before_escalation"] == 2
    assert rule["escalate_priority"] == "high"


def test_codex_no_escalation():
    """Test codex has no further escalation"""
    manager = EscalationManager()
    rule = manager.rules["codex"]
    
    assert rule["on_failure"] is None


def test_custom_rules():
    """Test creating manager with custom rules"""
    custom_rules = {
        "custom_tool": {
            "on_failure": "fallback_tool",
            "max_retries_before_escalation": 1
        }
    }
    
    manager = EscalationManager(rules=custom_rules)
    
    assert "custom_tool" in manager.rules
    assert manager.rules["custom_tool"]["on_failure"] == "fallback_tool"


def test_should_escalate_no_rule():
    """Test escalation check for tool without rule"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "unknown_tool"},
        retry_count=5
    )
    
    assert manager.should_escalate(job) is False


def test_should_escalate_no_target():
    """Test escalation when tool has no escalation target"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "codex"},
        retry_count=5
    )
    
    # Codex has on_failure=None
    assert manager.should_escalate(job, reason="failure") is False


def test_should_escalate_not_enough_retries():
    """Test escalation blocked when retry count too low"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "aider"},
        retry_count=1  # Less than max_retries_before_escalation (2)
    )
    
    assert manager.should_escalate(job) is False


def test_should_escalate_enough_retries():
    """Test escalation allowed when retry limit reached"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "aider"},
        retry_count=2  # Meets max_retries_before_escalation
    )
    
    assert manager.should_escalate(job, reason="failure") is True


def test_should_escalate_timeout():
    """Test escalation with timeout reason"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "aider"},
        retry_count=2
    )
    
    assert manager.should_escalate(job, reason="timeout") is True


def test_create_escalation_job_no_rule():
    """Test escalation job creation when no rule exists"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "unknown_tool"}
    )
    
    escalation_job = manager.create_escalation_job(job)
    
    assert escalation_job is None


def test_create_escalation_job_no_target():
    """Test escalation job creation when no target defined"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "codex"}
    )
    
    escalation_job = manager.create_escalation_job(job)
    
    assert escalation_job is None


def test_create_escalation_job_aider_to_codex():
    """Test creating escalation job from aider to codex"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test-123",
        job_data={
            "tool": "aider",
            "command": {
                "exe": "aider",
                "args": ["--yes", "Fix the bug"]
            }
        }
    )
    
    escalation_job = manager.create_escalation_job(job, reason="failure")
    
    assert escalation_job is not None
    assert escalation_job.job_id == "test-123-escalated-codex"
    assert escalation_job.job_data["tool"] == "codex"
    assert escalation_job.priority == JobPriority.HIGH
    assert escalation_job.depends_on == []
    assert escalation_job.metadata["is_escalation"] is True
    assert escalation_job.metadata["escalated_from_job"] == "test-123"
    assert escalation_job.job_data["metadata"]["escalated_from"] == "aider"
    assert escalation_job.job_data["metadata"]["escalation_reason"] == "failure"


def test_aider_to_codex_conversion():
    """Test aider command conversion to codex suggestion"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={
            "tool": "aider",
            "command": {
                "exe": "aider",
                "args": ["--yes", "Refactor", "the", "code"]
            }
        }
    )
    
    escalation_job = manager.create_escalation_job(job)
    
    # Check codex command structure
    cmd = escalation_job.job_data["command"]
    assert cmd["exe"] == "gh"
    assert "copilot" in cmd["args"]
    assert "suggest" in cmd["args"]
    assert "--target" in cmd["args"]
    assert "shell" in cmd["args"]
    # Prompt should contain extracted text
    prompt_arg = [arg for arg in cmd["args"] if "Refactor the code" in arg]
    assert len(prompt_arg) > 0


def test_escalation_priority():
    """Test escalation job inherits correct priority"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="test",
        job_data={"tool": "aider"}
    )
    
    escalation_job = manager.create_escalation_job(job)
    
    # Aider rule specifies "high" priority
    assert escalation_job.priority == JobPriority.HIGH


def test_get_escalation_chain_single():
    """Test escalation chain for tool with no escalation"""
    manager = EscalationManager()
    
    chain = manager.get_escalation_chain("codex")
    
    assert chain == ["codex"]


def test_get_escalation_chain_multi():
    """Test escalation chain for tool with escalation"""
    manager = EscalationManager()
    
    chain = manager.get_escalation_chain("aider")
    
    # aider -> codex -> (no further)
    assert chain == ["aider", "codex"]


def test_get_escalation_chain_circular():
    """Test escalation chain handles circular dependencies"""
    custom_rules = {
        "tool_a": {"on_failure": "tool_b"},
        "tool_b": {"on_failure": "tool_a"}  # Circular!
    }
    manager = EscalationManager(rules=custom_rules)
    
    chain = manager.get_escalation_chain("tool_a")
    
    # Should stop at circular reference
    assert chain == ["tool_a", "tool_b"]


def test_add_rule():
    """Test adding/updating escalation rule"""
    manager = EscalationManager()
    
    new_rule = {
        "on_failure": "backup_tool",
        "max_retries_before_escalation": 1
    }
    
    manager.add_rule("new_tool", new_rule)
    
    assert "new_tool" in manager.rules
    assert manager.rules["new_tool"] == new_rule


def test_get_rule():
    """Test getting escalation rule"""
    manager = EscalationManager()
    
    rule = manager.get_rule("aider")
    
    assert rule is not None
    assert rule["on_failure"] == "codex"
    
    # Non-existent tool
    assert manager.get_rule("nonexistent") is None


def test_to_dict():
    """Test converting rules to dictionary"""
    custom_rules = {
        "tool_a": {"on_failure": "tool_b"}
    }
    manager = EscalationManager(rules=custom_rules)
    
    rules_dict = manager.to_dict()
    
    assert rules_dict == custom_rules
    # Should be a copy, not same object
    assert rules_dict is not manager.rules


def test_from_dict():
    """Test creating manager from dictionary"""
    rules = {
        "tool_a": {"on_failure": "tool_b"},
        "tool_b": {"on_failure": None}
    }
    
    manager = EscalationManager.from_dict(rules)
    
    assert manager.rules == rules


def test_escalation_job_metadata():
    """Test escalation job metadata is properly set"""
    manager = EscalationManager()
    job = JobWrapper(
        job_id="original-123",
        job_data={"tool": "aider"}
    )
    
    escalation_job = manager.create_escalation_job(job, reason="timeout")
    
    # Check job metadata
    assert escalation_job.metadata["is_escalation"] is True
    assert escalation_job.metadata["escalated_from_job"] == "original-123"
    assert escalation_job.metadata["escalation_reason"] == "timeout"
    
    # Check job_data metadata
    assert escalation_job.job_data["metadata"]["escalated_from"] == "aider"
    assert escalation_job.job_data["metadata"]["escalation_reason"] == "timeout"
    assert escalation_job.job_data["metadata"]["original_job_id"] == "original-123"
