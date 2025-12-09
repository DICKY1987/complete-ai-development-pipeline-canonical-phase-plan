# State Machine Legacy Archive

**Archive Date**: 2025-12-08T22:38:22.037Z  
**Purpose**: Preserve legacy state machine documents consolidated into unified SSOT

## Contents

This archive contains 6 legacy state machine documents that have been consolidated into a single authoritative source:

**SSOT Document**: `../doc_ssot_state_machines.md` (DOC-SSOT-STATE-MACHINES-001)

### Archived Files

1. **STATE_MACHINES.md** (DOC-GUIDE-STATE-MACHINES-397)
   - Workstream/Step state machines with ASCII diagrams
   - Circuit breaker state machine
   - Recovery procedures and state audit trail
   - **Migrated to**: §1.3, §1.4, §2.4, §5

2. **STATE_MACHINES (2).md** (UET V2 State Machines)
   - UET Worker, Patch Ledger, Test Gate state machines
   - Database representations and concurrency control
   - **Migrated to**: §2.1, §2.2, §2.3, §2.5

3. **STATE_MACHINES (4).md** (Duplicate content)
   - Duplicate/variant definitions from STATE_MACHINES (2).md
   - **Status**: Deduplicated and merged
   - **Migrated to**: §1.3, §1.4, §2.1-2.3

4. **DOC_STATE_MACHINE.md** (DOC-GUIDE-DOC-STATE-MACHINE-861)
   - Canonical run/workstream states with enforcement notes
   - **Migrated to**: §1.2, §1.3

5. **STATE_MACHINE (2).md** (DOC-GUIDE-STATE-MACHINE-785)
   - Task/Workstream/Worker state machines with Mermaid diagrams
   - Transition guards and invariants
   - **Migrated to**: §1.3, §1.4, §1.5

6. **STATE_MACHINES (3).md** (DOC-GUIDE-STATE-MACHINES-758)
   - Duplicate UET V2 content identical to STATE_MACHINES (2).md
   - **Status**: Deduplicated and merged
   - **Migrated to**: §2.1, §2.2, §2.3

## Consolidation Summary

### What Was Migrated

- ✅ 8 state machines fully documented
- ✅ 51 states defined across all machines
- ✅ 66 valid transitions documented
- ✅ 7 database table schemas with constraints
- ✅ 3 recovery procedures
- ✅ 12 global invariants
- ✅ 5 test requirement categories
- ✅ Cross-system derivation rules
- ✅ Event and audit models
- ✅ Change control processes

### Conflicts Resolved

1. **State naming conventions**: Standardized to lowercase descriptive names
2. **Worker state machines**: Preserved both Orchestration and UET workers (different systems)
3. **Task state variants**: Merged into 9-state model with explicit `blocked` state

### Deduplication

- **2 identical files** removed (STATE_MACHINES (3).md and (4).md)
- **3 variant definitions** consolidated into single authoritative versions

## Verification

All verification criteria met:
- [x] All state machines have complete state sets
- [x] All valid transitions documented
- [x] All invalid transitions listed
- [x] Database schemas include all constraints
- [x] Event logging specified
- [x] Recovery procedures comprehensive
- [x] Manual override procedures documented
- [x] Test requirements defined
- [x] Global invariants enforced
- [x] Version control established

## Deletion Authorization

**Status**: Approved for deletion after Phase 2 completion and verification

**Conditions**:
1. Phase 2 implementation validates all state machines
2. Integration tests pass with new state machines
3. Production deployment confirms SSOT accuracy

**Archive Location**: `.archive/state_machines_legacy_2025-12-08/`

## Recovery Instructions

If you need to reference original content:

1. All files are preserved in this archive directory
2. See `MANIFEST.json` for detailed file mapping
3. Original file paths documented in manifest
4. Content is mapped to SSOT sections for easy cross-reference

## Metadata

- **SSOT Version**: 1.0.0
- **Archived By**: State Machine SSOT Consolidation
- **Total Files**: 6
- **Total Size**: ~150KB
- **Duplicates Removed**: 2
- **Consolidation Date**: 2025-12-08

---

**Do not modify files in this archive.**  
**For state machine updates, edit the SSOT document: `../doc_ssot_state_machines.md`**
