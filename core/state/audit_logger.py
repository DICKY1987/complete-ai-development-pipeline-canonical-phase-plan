"""
Audit Logger and Patch Ledger for Pipeline Plus
Structured logging infrastructure with JSONL format
"""
# DOC_ID: DOC-CORE-STATE-AUDIT-LOGGER-167
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator


@dataclass
class AuditEvent:
    """Single audit event"""
    timestamp: str
    event_type: str
    task_id: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class EventFilters:
    """Filters for querying audit events"""
    task_id: Optional[str] = None
    event_type: Optional[str] = None
    since: Optional[str] = None
    until: Optional[str] = None
    limit: Optional[int] = None


class AuditLogger:
    """
    Structured audit logging to JSONL files

    Supported event types:
    - task_received
    - task_routed
    - process_started
    - patch_captured
    - patch_validated
    - patch_applied
    - scope_violation
    - oscillation_detected
    - circuit_breaker_trip
    - completed
    - failed
    """

    EVENT_TYPES = {
        "task_received",
        "task_routed",
        "process_started",
        "stdout_chunk",
        "timeout",
        "patch_captured",
        "patch_validated",
        "patch_applied",
        "scope_violation",
        "oscillation_detected",
        "circuit_breaker_trip",
        "retry_scheduled",
        "completed",
        "failed"
    }

    def __init__(self, log_path: str = ".runs/audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        event_type: str,
        task_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an event to the audit log

        Args:
            event_type: Type of event (should be in EVENT_TYPES)
            task_id: Associated task ID
            data: Additional event data
        """
        if event_type not in self.EVENT_TYPES:
            # Log unknown event types but warn
            if data is None:
                data = {}
            data['_warning'] = f'Unknown event type: {event_type}'

        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            event_type=event_type,
            task_id=task_id,
            data=data or {}
        )

        # Append to JSONL file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')

    def query_events(self, filters: Optional[EventFilters] = None) -> List[AuditEvent]:
        """
        Query audit events with optional filters

        Args:
            filters: EventFilters object to filter results

        Returns:
            List of matching AuditEvent objects
        """
        if not self.log_path.exists():
            return []

        filters = filters or EventFilters()
        events = []

        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event_data = json.loads(line.strip())
                    event = AuditEvent.from_dict(event_data)

                    # Apply filters
                    if filters.task_id and event.task_id != filters.task_id:
                        continue
                    if filters.event_type and event.event_type != filters.event_type:
                        continue
                    if filters.since and event.timestamp < filters.since:
                        continue
                    if filters.until and event.timestamp > filters.until:
                        continue

                    events.append(event)

                    # Limit results
                    if filters.limit and len(events) >= filters.limit:
                        break

                except (json.JSONDecodeError, KeyError):
                    # Skip malformed lines
                    continue

        return events

    def _iter_events(self) -> Iterator[AuditEvent]:
        """Iterate over all events in the log"""
        if not self.log_path.exists():
            return

        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event_data = json.loads(line.strip())
                    yield AuditEvent.from_dict(event_data)
                except (json.JSONDecodeError, KeyError):
                    continue


@dataclass
class PatchArtifact:
    """Patch artifact metadata"""
    patch_id: str
    patch_file: Path
    diff_hash: str
    files_modified: List[str]
    line_count: int
    created_at: str
    ws_id: Optional[str] = None
    run_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['patch_file'] = str(self.patch_file)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatchArtifact':
        """Create from dictionary"""
        if 'patch_file' in data and isinstance(data['patch_file'], str):
            data['patch_file'] = Path(data['patch_file'])
        return cls(**data)


class PatchLedger:
    """
    Manages patch artifact storage in .ledger/patches/
    """

    def __init__(self, ledger_path: str = ".ledger/patches"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.ledger_path / "metadata.jsonl"

    def store_patch(self, patch: PatchArtifact) -> Path:
        """
        Store patch artifact and metadata

        Args:
            patch: PatchArtifact to store

        Returns:
            Path to stored patch file
        """
        # Ensure patch file is in ledger directory
        if not patch.patch_file.is_absolute():
            target_file = self.ledger_path / patch.patch_file.name
        else:
            target_file = patch.patch_file

        # Store metadata
        with open(self.metadata_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(patch.to_dict()) + '\n')

        return target_file

    def get_patch(self, patch_id: str) -> Optional[PatchArtifact]:
        """
        Retrieve patch artifact by ID

        Args:
            patch_id: Patch ID to retrieve

        Returns:
            PatchArtifact or None if not found
        """
        if not self.metadata_file.exists():
            return None

        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    patch_data = json.loads(line.strip())
                    if patch_data.get('patch_id') == patch_id:
                        return PatchArtifact.from_dict(patch_data)
                except (json.JSONDecodeError, KeyError):
                    continue

        return None

    def get_history(self, ws_id: str) -> List[PatchArtifact]:
        """
        Get all patches for a workstream

        Args:
            ws_id: Workstream ID

        Returns:
            List of PatchArtifact objects for the workstream
        """
        if not self.metadata_file.exists():
            return []

        patches = []
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    patch_data = json.loads(line.strip())
                    if patch_data.get('ws_id') == ws_id:
                        patches.append(PatchArtifact.from_dict(patch_data))
                except (json.JSONDecodeError, KeyError):
                    continue

        return sorted(patches, key=lambda p: p.created_at)
