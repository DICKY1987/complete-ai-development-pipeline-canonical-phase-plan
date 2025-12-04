---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-AUDIT_RETENTION-100
---

# Audit Retention Policy

## Overview

This policy defines retention periods, archival procedures, and compliance requirements for audit data in the repository.

## Retention Periods

### Active Audit Data

**Location**: `.state/transitions.jsonl`

**Retention**: Indefinite (all transitions retained)

**Rationale**:
- Transition history is append-only and compact
- Full history needed for state reconstruction
- Critical for compliance and forensics

### State Snapshots

**Location**: `.state/snapshots/`

**Retention Schedule**:
- **Last 7 days**: All snapshots retained (hourly granularity)
- **8-30 days**: Daily snapshots retained
- **31-90 days**: Weekly snapshots retained
- **90+ days**: Monthly snapshots retained
- **1+ year**: Annual snapshots retained

**Cleanup**: Automated via scheduled task (not yet implemented)

### Index Files

**Location**: `.state/indices/`

**Retention**: Current indices only

**Archival**:
- Previous index versions moved to snapshots
- Indices regeneratable from current.json

## Data Lifecycle

### Phase 1: Active

- All recent data immediately accessible
- Performance optimized for queries
- No compression

### Phase 2: Archived (90+ days)

- Older snapshots moved to compressed archive
- Still queryable but slower access
- Compression: gzip

### Phase 3: Long-term Storage (1+ years)

- Annual snapshots retained indefinitely
- Compressed and potentially off-site backup
- Retrieved only for historical analysis

## Compliance Requirements

### Minimum Retention

- **State transitions**: Must retain all (no deletion)
- **Snapshots**: Minimum 30 days
- **Validation results**: Minimum 90 days
- **Error logs**: Minimum 90 days

### Maximum Retention

- No maximum for audit trails (append-only, compact)
- Snapshots pruned per schedule above
- Large files (>100MB) subject to review

## Archival Procedures

### Manual Archival

```powershell
# Archive snapshots older than 90 days
$cutoff = (Get-Date).AddDays(-90)
Get-ChildItem .state\snapshots -Directory | Where-Object {
    $_.CreationTime -lt $cutoff
} | ForEach-Object {
    Compress-Archive -Path $_.FullName -DestinationPath ".state\archive\$($_.Name).zip"
    Remove-Item $_.FullName -Recurse
}
```

### Automated Archival

**Status**: Not yet implemented

**Planned**: Scheduled task runs weekly to prune old snapshots per retention schedule

## Restoration Procedures

### Restore from Snapshot

```powershell
# Restore specific snapshot
$snapshotDate = "2025-11-23_16-04-25"
Copy-Item -Path ".state\snapshots\$snapshotDate\*" -Destination ".state\" -Force
```

### Rebuild from Audit Trail

```powershell
# Rebuild current.json from transitions.jsonl
# (Implementation pending)
.\scripts\state_rebuild.ps1 -FromTransitions
```

## Access and Security

### Access Control

- **Read**: All team members
- **Write**: Automated systems only
- **Delete**: Requires manager approval

### Audit of Audits

- Changes to retention policy logged
- Archival operations logged
- Restoration operations logged

## Storage Management

### Current Usage

```powershell
# Check .state directory size
Get-ChildItem .state -Recurse | Measure-Object -Property Length -Sum
```

### Growth Projections

- **Transitions.jsonl**: ~1KB per transition, ~100 transitions/day = ~36MB/year
- **Snapshots**: ~100KB per snapshot, daily = ~36MB/year
- **Indices**: ~50KB per index, regenerated = negligible

**Total projected growth**: ~75MB/year (minimal)

## Compliance Verification

### Monthly Review

- Verify retention schedule followed
- Check archival automation status
- Review storage usage
- Validate audit trail integrity

### Validation Commands

```powershell
# Verify audit trail
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-003,AUDIT-001,AUDIT-002"
```

## Exceptions and Overrides

### Legal Hold

In case of legal proceedings:
- Suspend all deletion and archival
- Preserve all data indefinitely
- Document hold with start/end dates

### Emergency Cleanup

If storage exceeds capacity:
1. Get manager approval
2. Document reason and scope
3. Compress/archive instead of delete
4. Update this policy with exception

## References

- **AUDIT_TRAIL.md** - Audit trail structure
- **STATE-OBS-003** - Transitions validation
- **.state/** - Audit data location

## Version History

- **1.0.0** (2025-11-23) - Initial policy
