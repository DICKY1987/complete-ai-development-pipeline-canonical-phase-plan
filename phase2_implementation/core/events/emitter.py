"""
Event emission and logging system.

Implements the canonical event schema and transition logging rules
per SSOT §7 (Event & Audit Model).

Reference: DOC-SSOT-STATE-MACHINES-001 §7
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


class EventEmitter:
    """
    Event emitter for state machine transitions and system events.

    Implements dual logging per SSOT §7.2.1:
    1. File-based append-only log (.state/transitions.jsonl)
    2. Database state_transitions table (handled separately)

    Reference: SSOT §7.1 (Canonical Event Schema)
    """

    def __init__(self, log_dir: str = ".state"):
        """
        Initialize event emitter.

        Args:
            log_dir: Directory for event logs
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "transitions.jsonl"

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def emit(self, event: Dict[str, Any]) -> str:
        """
        Emit event to all configured sinks.

        Implements SSOT §7.1 canonical event schema:
        {
          "event_id": "evt_<ULID>",
          "timestamp": "2025-12-09T...",
          "event_type": "task_state_transition|...",
          "severity": "debug|info|warning|error|critical",
          "entity_type": "run|workstream|task|...",
          "entity_id": "...",
          "from_state": "...",
          "to_state": "...",
          "trigger": "...",
          "reason": "...",
          "metadata": {...},
          "operator": null|"username"
        }

        Args:
            event: Event dictionary

        Returns:
            Generated event_id
        """
        # Generate event ID (simplified - use ULID in production)
        event_id = self._generate_event_id()

        # Add required fields if missing
        event.setdefault("event_id", event_id)
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        event.setdefault("severity", "info")

        # Validate required fields
        required = ["event_type", "entity_type", "entity_id"]
        missing = [f for f in required if f not in event]
        if missing:
            raise ValueError(f"Event missing required fields: {missing}")

        # Write to file-based log (SSOT §7.2.1)
        self._write_to_file(event)

        # TODO: Write to database state_transitions table
        # self._write_to_database(event)

        # TODO: Emit to monitoring system (Prometheus metrics)
        # self._update_metrics(event)

        return event_id

    def _generate_event_id(self) -> str:
        """
        Generate unique event ID.

        In production, use ULID for globally unique, sortable IDs.
        For now, use timestamp-based ID.

        Returns:
            Event ID string
        """
        ts = datetime.now(timezone.utc)
        return f"evt_{ts.strftime('%Y%m%d%H%M%S%f')}"

    def _write_to_file(self, event: Dict[str, Any]):
        """
        Append event to JSONL log file.

        Implements append-only logging per SSOT §7.2.1.

        Args:
            event: Event to write
        """
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                json.dump(event, f, default=str)
                f.write("\n")
        except IOError as e:
            # Log to stderr if file writing fails
            print(f"ERROR: Failed to write event to log: {e}", flush=True)
            print(f"Event: {json.dumps(event, default=str)}", flush=True)

    def get_recent_events(self, limit: int = 100) -> list:
        """
        Get most recent events from log.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        if not self.log_file.exists():
            return []

        events = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                # Read last N lines
                lines = f.readlines()
                for line in lines[-limit:]:
                    if line.strip():
                        events.append(json.loads(line))
        except (IOError, json.JSONDecodeError) as e:
            print(f"ERROR: Failed to read event log: {e}", flush=True)

        return events

    def query_events(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 1000,
    ) -> list:
        """
        Query events with filters.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            event_type: Filter by event type
            severity: Filter by severity
            limit: Maximum results

        Returns:
            List of matching events
        """
        if not self.log_file.exists():
            return []

        matches = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)

                        # Apply filters
                        if entity_type and event.get("entity_type") != entity_type:
                            continue
                        if entity_id and event.get("entity_id") != entity_id:
                            continue
                        if event_type and event.get("event_type") != event_type:
                            continue
                        if severity and event.get("severity") != severity:
                            continue

                        matches.append(event)

                        if len(matches) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

        except IOError as e:
            print(f"ERROR: Failed to query event log: {e}", flush=True)

        return matches


# Global event emitter instance
_emitter = EventEmitter()


def emit_event(event: Dict[str, Any]) -> str:
    """
    Emit event using global emitter.

    This is the primary API for emitting events per SSOT §7.2.

    Args:
        event: Event dictionary following canonical schema

    Returns:
        Generated event_id

    Example:
        >>> emit_event({
        ...     'event_type': 'task_state_transition',
        ...     'entity_type': 'task',
        ...     'entity_id': 'task-001',
        ...     'from_state': 'running',
        ...     'to_state': 'completed',
        ...     'severity': 'info'
        ... })
        'evt_20251209...'
    """
    return _emitter.emit(event)


def get_event_emitter() -> EventEmitter:
    """
    Get global event emitter instance.

    Returns:
        EventEmitter instance
    """
    return _emitter


def configure_emitter(log_dir: str = ".state"):
    """
    Configure global event emitter.

    Args:
        log_dir: Directory for event logs
    """
    global _emitter
    _emitter = EventEmitter(log_dir)
