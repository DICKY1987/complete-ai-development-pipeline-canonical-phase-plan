---
doc_id: DOC-GUIDE-PROPOSAL-081
---

# Phase B: Patch System - UET Implementation

**Change ID**: uet-001-phase-b-patch-system
**Parent**: uet-001-complete-implementation
**Depends On**: uet-001-phase-a-quick-wins
**Type**: Core Infrastructure
**Priority**: HIGH (Critical Path)
**Estimated Duration**: 2-3 weeks
**Effort**: 42 hours

---

## Problem Statement

Current patch handling is basic - patches are created but not tracked through a lifecycle. Missing:

- **Patch Ledger**: No state machine tracking (created → validated → applied → committed)
- **Validation**: Only basic parsing, no scope/constraint enforcement
- **Policy Engine**: No configurable constraints per file type
- **Database Integration**: Patches not stored with ULID tracking
- **Audit Trail**: No comprehensive history of patch operations

---

## Requirements

**Patch Ledger**:
- SHALL implement full state machine: created → validated → queued → applied → verified → committed
- SHALL track state history as JSON array
- SHALL emit events for all state transitions
- SHALL integrate with event bus

**Patch Validator**:
- SHALL validate unified diff format
- SHALL enforce scope constraints (allowed files only)
- SHALL enforce policy constraints (max lines, file patterns)
- SHALL quarantine invalid patches

**Database Migration**:
- SHALL create `patches` table with ULID primary key
- SHALL create `patch_ledger_entries` table
- SHALL add ULID columns to existing tables
- MUST provide tested rollback script

**Policy Engine**:
- SHALL load policies from `config/patch_policies/*.json`
- SHALL support per-file-type policies (python_strict, docs_permissive)
- SHALL enforce: max_lines_changed, allowed_file_patterns, forbidden_patterns

---

## Implementation Tasks

### Database Migration (6 hours)

```sql
-- patches table
CREATE TABLE patches (
    patch_id TEXT PRIMARY KEY,  -- ULID
    format TEXT NOT NULL DEFAULT 'unified_diff',
    target_repo TEXT,
    base_commit TEXT,
    tool_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    diff_text TEXT NOT NULL,
    files_touched TEXT,  -- JSON array
    line_insertions INTEGER DEFAULT 0,
    line_deletions INTEGER DEFAULT 0
);

-- patch_ledger_entries table
CREATE TABLE patch_ledger_entries (
    ledger_id TEXT PRIMARY KEY,  -- ULID
    patch_id TEXT NOT NULL,
    state TEXT NOT NULL,
    state_history TEXT,  -- JSON array
    validation_format_ok INTEGER,
    validation_scope_ok INTEGER,
    validation_constraints_ok INTEGER,
    quarantine_is_quarantined INTEGER DEFAULT 0,
    quarantine_reason TEXT,
    FOREIGN KEY (patch_id) REFERENCES patches(patch_id)
);
```

### Core/Patches Module (16 hours)

**Files to Create**:
- `core/patches/__init__.py`
- `core/patches/patch_artifact.py` - Wrap existing PatchArtifact
- `core/patches/patch_ledger.py` - State machine
- `core/patches/patch_validator.py` - Validation logic
- `core/patches/patch_policy.py` - Policy engine
- `core/patches/patch_applier.py` - Safe application

### Policy Configurations (8 hours)

**`config/patch_policies/global.json`**:
```json
{
  "max_lines_changed": 500,
  "max_files_per_patch": 10,
  "allowed_file_patterns": ["**/*.py", "**/*.md", "**/*.yaml"],
  "forbidden_patterns": [".env", "**/*.pyc", "**/__pycache__/**"]
}
```

**`config/patch_policies/python_strict.json`**:
```json
{
  "max_lines_changed": 200,
  "max_files_per_patch": 5,
  "allowed_file_patterns": ["**/*.py"],
  "require_tests": true,
  "forbidden_patterns": ["**/*_test.py"]
}
```

---

## Success Criteria

- ✅ Database migration executed successfully
- ✅ Rollback script tested and working
- ✅ Patch ledger tracking state transitions
- ✅ Validator catching format/scope/constraint violations
- ✅ Policies loading and enforcing
- ✅ All tests passing (≥85% coverage for new code)

---

## Dependencies

**Requires**: Phase A complete (schemas needed)
**Blocks**: Phase C, Phase D (need patch system)

---

## Files Created

- `core/patches/__init__.py`
- `core/patches/patch_artifact.py`
- `core/patches/patch_ledger.py`
- `core/patches/patch_validator.py`
- `core/patches/patch_policy.py`
- `core/patches/patch_applier.py`
- `schema/migrations/002_uet_alignment.sql`
- `schema/migrations/002_rollback.sql`
- `scripts/migrate_db_to_uet.py`
- `scripts/rollback_db_migration.py`
- `config/patch_policies/global.json`
- `config/patch_policies/python_strict.json`
- `config/patch_policies/docs_permissive.json`
- `docs/PATCH_WORKFLOW.md`
- `docs/DATABASE_MIGRATION.md`
