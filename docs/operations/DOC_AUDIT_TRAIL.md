---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-AUDIT_TRAIL-050
---

# Audit Trail

## Purpose

This document defines the audit trail system for tracking all significant repository changes, state transitions, and validation results.

## Audit Events

All audit events are logged to `.state/transitions.jsonl` in append-only JSONL format.

### Event Schema

```json
{
  "transition_id": "TRANS-XXX-NNN",
  "from_state": "STATE-A",
  "to_state": "STATE-B",
  "timestamp": "2025-11-23T16:04:25.348Z",
  "trigger": "event_type",
  "actor": "system|user|tool_name",
  "metadata": {
    "reason": "Description of why transition occurred",
    "context": "Additional context",
    "affected_files": ["list", "of", "files"]
  }
}
```

## Event Types (Triggers)

### System Events

- **`bootstrap`** - Initial system setup
- **`validation_run`** - Validation check executed
- **`state_sync`** - State synchronized with reality
- **`health_check`** - Health monitoring

### User Events

- **`manual_transition`** - User-initiated state change
- **`git_commit`** - Commit to repository
- **`configuration_change`** - Config file modified

### Tool Events

- **`workstream_start`** - Workstream execution began
- **`workstream_complete`** - Workstream execution finished
- **`error_detected`** - Error detection engine found issue
- **`error_fixed`** - Error automatically fixed

## Audit Trail Queries

### Query Recent Transitions

```powershell
# Last 10 transitions
Get-Content .state\transitions.jsonl | Select-Object -Last 10 | ForEach-Object { $_ | ConvertFrom-Json }
```

### Query by Trigger Type

```powershell
# All workstream events
Get-Content .state\transitions.jsonl | ForEach-Object {
    $obj = $_ | ConvertFrom-Json
    if ($obj.trigger -like "workstream_*") { $obj }
}
```

### Query by Date Range

```powershell
# Today's events
$today = (Get-Date).ToString("yyyy-MM-dd")
Get-Content .state\transitions.jsonl | ForEach-Object {
    $obj = $_ | ConvertFrom-Json
    if ($obj.timestamp -like "$today*") { $obj }
}
```

## Audit Compliance

### Requirements

- **Immutability**: Never modify or delete audit logs
- **Completeness**: Log all state transitions
- **Integrity**: Validate JSONL format on write
- **Retention**: See AUDIT_RETENTION.md

### Validation

```powershell
# Validate audit trail integrity
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-003"
```

## Integration Points

### State Management

All state changes in `current.json` must have corresponding entry in `transitions.jsonl`.

### Validation System

Validation runs append results to audit trail with `validation_run` trigger.

### Error Detection

Error detection events are logged with full context for forensics.

## Security

- **Access Control**: Audit logs are read-only after creation
- **Tampering Detection**: JSONL format makes modifications obvious
- **Backup**: Include in snapshot system

## References

- **AUDIT_RETENTION.md** - Retention policy
- **STATE-OBS-003** - Transitions validation requirement
- **.state/transitions.jsonl** - Audit log file
