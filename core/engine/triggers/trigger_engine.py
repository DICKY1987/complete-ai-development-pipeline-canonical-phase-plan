"""Event-driven trigger engine for automated workflow execution."""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern
from datetime import datetime, timezone

from core.events.event_bus import EventBus


@dataclass
class TriggerRule:
    """Rule for triggering workstreams based on events."""
    
    rule_id: str
    event_pattern: str
    workstream_id: str
    enabled: bool = True
    description: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    
    _compiled_pattern: Optional[Pattern] = None
    
    def matches(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> bool:
        """Check if event matches this trigger rule.
        
        Args:
            event_type: Event type string (e.g., "phase.1.completed")
            event_data: Optional event payload data
            
        Returns:
            True if event matches pattern and conditions
        """
        if not self.enabled:
            return False
        
        if self._compiled_pattern is None:
            pattern = self.event_pattern.replace('.', r'\.').replace('*', '.*')
            self._compiled_pattern = re.compile(f'^{pattern}$')
        
        if not self._compiled_pattern.match(event_type):
            return False
        
        if self.condition:
            if not event_data:
                return False
            for key, expected_value in self.condition.items():
                if key not in event_data or event_data[key] != expected_value:
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rule_id': self.rule_id,
            'event_pattern': self.event_pattern,
            'workstream_id': self.workstream_id,
            'enabled': self.enabled,
            'description': self.description,
            'condition': self.condition
        }


class TriggerEngine:
    """Engine for registering and evaluating event-driven triggers."""
    
    def __init__(
        self,
        event_bus: EventBus,
        orchestrator: Optional[Any] = None,
        config_path: Optional[Path] = None
    ):
        """Initialize trigger engine.
        
        Args:
            event_bus: Event bus to subscribe to
            orchestrator: Optional orchestrator for launching workstreams
            config_path: Optional path to triggers configuration file (set to None to disable)
        """
        self.event_bus = event_bus
        self.orchestrator = orchestrator
        self.config_path = config_path if config_path is not False else Path("config/triggers.yaml")
        self.rules: Dict[str, TriggerRule] = {}
        self.trigger_log = Path(".state/trigger_executions.jsonl")
        self.trigger_log.parent.mkdir(parents=True, exist_ok=True)
        
        if config_path is not None:
            self._load_config()
        self._subscribe_to_events()
    
    def register_trigger(
        self,
        rule_id: str,
        event_pattern: str,
        workstream_id: str,
        enabled: bool = True,
        description: Optional[str] = None,
        condition: Optional[Dict[str, Any]] = None
    ) -> TriggerRule:
        """Register a new trigger rule.
        
        Args:
            rule_id: Unique identifier for this rule
            event_pattern: Glob-style pattern for event types (e.g., "phase.*.completed")
            workstream_id: Workstream to launch when triggered
            enabled: Whether rule is active
            description: Human-readable description
            condition: Optional additional conditions on event data
            
        Returns:
            Created TriggerRule
        """
        rule = TriggerRule(
            rule_id=rule_id,
            event_pattern=event_pattern,
            workstream_id=workstream_id,
            enabled=enabled,
            description=description,
            condition=condition
        )
        self.rules[rule_id] = rule
        return rule
    
    def evaluate_triggers(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """Evaluate all triggers against an event.
        
        Args:
            event_type: Event type string
            event_data: Optional event payload
            
        Returns:
            List of workstream IDs that were triggered
        """
        triggered_workstreams = []
        
        for rule in self.rules.values():
            if rule.matches(event_type, event_data):
                triggered_workstreams.append(rule.workstream_id)
                self._execute_trigger(rule, event_type, event_data)
        
        return triggered_workstreams
    
    def _execute_trigger(
        self,
        rule: TriggerRule,
        event_type: str,
        event_data: Optional[Dict[str, Any]]
    ) -> None:
        """Execute a matched trigger by launching the workstream.
        
        Args:
            rule: Matched trigger rule
            event_type: Event that triggered the rule
            event_data: Event payload
        """
        execution_record = {
            'rule_id': rule.rule_id,
            'workstream_id': rule.workstream_id,
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if self.orchestrator:
            try:
                run_id = self.orchestrator.launch_workstream(
                    workstream_id=rule.workstream_id,
                    triggered_by=event_type,
                    metadata={'trigger_rule': rule.rule_id}
                )
                execution_record['run_id'] = run_id
                execution_record['status'] = 'launched'
            except Exception as e:
                execution_record['status'] = 'failed'
                execution_record['error'] = str(e)
        else:
            execution_record['status'] = 'skipped_no_orchestrator'
        
        with open(self.trigger_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(execution_record) + '\n')
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to all events on the event bus."""
        self.event_bus.subscribe('*', self._on_event)
    
    def _on_event(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle incoming events from event bus.
        
        Args:
            event_type: Event type
            event_data: Event payload
        """
        self.evaluate_triggers(event_type, event_data)
    
    def _load_config(self) -> None:
        """Load trigger rules from configuration file."""
        if not self.config_path or not self.config_path.exists():
            return
        
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            for rule_data in config.get('triggers', []):
                self.register_trigger(**rule_data)
        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Failed to load triggers config: {e}")
    
    def get_active_rules(self) -> List[TriggerRule]:
        """Get all active trigger rules.
        
        Returns:
            List of enabled TriggerRule objects
        """
        return [rule for rule in self.rules.values() if rule.enabled]
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a trigger rule.
        
        Args:
            rule_id: ID of rule to disable
            
        Returns:
            True if rule was found and disabled
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a trigger rule.
        
        Args:
            rule_id: ID of rule to enable
            
        Returns:
            True if rule was found and enabled
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False
