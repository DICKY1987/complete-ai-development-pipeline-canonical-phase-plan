"""
Escalation Manager - Job escalation rules and logic.

Provides automatic escalation when jobs fail:
- Tool-specific escalation rules
- Escalation job creation
- Escalation history tracking
"""
DOC_ID: DOC-PAT-QUEUE-ESCALATION-452

from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

from engine.queue.job_wrapper import JobWrapper, JobPriority


# Escalation rules: tool -> escalation_target
ESCALATION_RULES = {
    "aider": {
        "on_failure": "codex",
        "on_timeout": "codex",
        "max_retries_before_escalation": 2,
        "escalate_priority": "high"
    },
    "tests": {
        "on_failure": None,  # No escalation for test failures
        "max_retries_before_escalation": 1
    },
    "git": {
        "on_failure": None,  # No escalation for git failures
        "max_retries_before_escalation": 1
    },
    "codex": {
        "on_failure": None,  # Codex is final escalation
        "max_retries_before_escalation": 1
    }
}


class EscalationManager:
    """
    Manages job escalation rules and logic.
    
    Features:
    - Tool-specific escalation rules
    - Automatic escalation job creation
    - Escalation history tracking
    """
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """
        Initialize escalation manager.
        
        Args:
            rules: Custom escalation rules (defaults to ESCALATION_RULES)
        """
        self.rules = rules or ESCALATION_RULES
    
    def should_escalate(self, job: JobWrapper, reason: str = "failure") -> bool:
        """
        Check if job should be escalated.
        
        Args:
            job: Job to check
            reason: Escalation reason ('failure' or 'timeout')
            
        Returns:
            True if should escalate
        """
        tool = job.job_data.get("tool")
        if tool not in self.rules:
            return False
        
        rule = self.rules[tool]
        
        # Check if tool has escalation target
        escalation_key = f"on_{reason}"
        if escalation_key not in rule or rule[escalation_key] is None:
            return False
        
        # Check if retry limit reached
        max_retries = rule.get("max_retries_before_escalation", 2)
        return job.retry_count >= max_retries
    
    def create_escalation_job(
        self,
        failed_job: JobWrapper,
        reason: str = "failure"
    ) -> Optional[JobWrapper]:
        """
        Create escalation job from failed job.
        
        Args:
            failed_job: Job that failed
            reason: Escalation reason
            
        Returns:
            New escalation job or None if no escalation
        """
        tool = failed_job.job_data.get("tool")
        if tool not in self.rules:
            return None
        
        rule = self.rules[tool]
        escalation_key = f"on_{reason}"
        escalation_tool = rule.get(escalation_key)
        
        if escalation_tool is None:
            return None
        
        # Create new job with escalated tool
        escalation_job_data = failed_job.job_data.copy()
        escalation_job_data["tool"] = escalation_tool
        escalation_job_data["metadata"] = escalation_job_data.get("metadata", {})
        escalation_job_data["metadata"]["escalated_from"] = tool
        escalation_job_data["metadata"]["escalation_reason"] = reason
        escalation_job_data["metadata"]["original_job_id"] = failed_job.job_id
        
        # Update command if needed (tool-specific logic)
        if escalation_tool == "codex" and tool == "aider":
            # Convert aider command to codex suggestion
            escalation_job_data = self._convert_aider_to_codex(escalation_job_data)
        
        # Determine priority
        priority_str = rule.get("escalate_priority", "high")
        priority = JobPriority[priority_str.upper()]
        
        # Create escalation job
        escalation_job = JobWrapper(
            job_id=f"{failed_job.job_id}-escalated-{escalation_tool}",
            job_data=escalation_job_data,
            priority=priority,
            depends_on=[],  # Escalation jobs don't wait for dependencies
            max_retries=rule.get("max_retries_before_escalation", 1),
            metadata={
                "is_escalation": True,
                "escalated_from_job": failed_job.job_id,
                "escalation_reason": reason
            }
        )
        
        return escalation_job
    
    def _convert_aider_to_codex(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Aider job to Codex suggestion.
        
        Args:
            job_data: Original job data
            
        Returns:
            Modified job data for Codex
        """
        # Extract prompt from aider args
        aider_args = job_data.get("command", {}).get("args", [])
        prompt = " ".join(arg for arg in aider_args if not arg.startswith("--"))
        
        # Build codex command
        job_data["command"] = {
            "exe": "gh",
            "args": [
                "copilot",
                "suggest",
                "--target",
                "shell",
                f"Fix the issue: {prompt}"
            ]
        }
        
        return job_data
    
    def get_escalation_chain(self, tool: str) -> list:
        """
        Get full escalation chain for a tool.
        
        Args:
            tool: Tool name
            
        Returns:
            List of tools in escalation chain
        """
        chain = [tool]
        current = tool
        
        while current in self.rules:
            next_tool = self.rules[current].get("on_failure")
            if next_tool is None or next_tool in chain:
                break
            chain.append(next_tool)
            current = next_tool
        
        return chain
    
    def add_rule(self, tool: str, rule: Dict[str, Any]):
        """
        Add or update escalation rule.
        
        Args:
            tool: Tool name
            rule: Escalation rule
        """
        self.rules[tool] = rule
    
    def get_rule(self, tool: str) -> Optional[Dict[str, Any]]:
        """
        Get escalation rule for tool.
        
        Args:
            tool: Tool name
            
        Returns:
            Escalation rule or None
        """
        return self.rules.get(tool)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rules to dictionary."""
        return self.rules.copy()
    
    @classmethod
    def from_dict(cls, rules: Dict[str, Any]) -> 'EscalationManager':
        """
        Create escalation manager from dictionary.
        
        Args:
            rules: Escalation rules
            
        Returns:
            EscalationManager instance
        """
        return cls(rules=rules)
