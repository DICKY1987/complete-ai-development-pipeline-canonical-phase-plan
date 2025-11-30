---
doc_id: DOC-GUIDE-TASKS-1510
---

# Phase B Tasks - Patch System

## Database Migration

- [ ] Create `schema/migrations/002_uet_alignment.sql`
- [ ] Add `patches` table
- [ ] Add `patch_ledger_entries` table
- [ ] Add ULID columns to runs, workstreams, attempts
- [ ] Install `python-ulid` package
- [ ] Create `scripts/migrate_db_to_uet.py`
- [ ] Create `scripts/rollback_db_migration.py`
- [ ] Test on copy of production database
- [ ] Document in `docs/DATABASE_MIGRATION.md`

## Patch Ledger

- [ ] Create `core/patches/` directory
- [ ] Create `core/patches/patch_artifact.py`
- [ ] Create `core/patches/patch_ledger.py`
- [ ] Implement state machine
- [ ] Add state history tracking
- [ ] Integrate with event bus
- [ ] Write unit tests

## Patch Validator

- [ ] Create `core/patches/patch_validator.py`
- [ ] Implement format validation
- [ ] Implement scope validation
- [ ] Implement constraint validation
- [ ] Write tests

## Patch Policy Engine

- [ ] Create `core/patches/patch_policy.py`
- [ ] Create `config/patch_policies/` directory
- [ ] Create global policy
- [ ] Create python_strict policy
- [ ] Create docs_permissive policy
- [ ] Write tests

## Patch Applier

- [ ] Create `core/patches/patch_applier.py`
- [ ] Implement safe application
- [ ] Add dry-run mode
- [ ] Add rollback support
- [ ] Write tests
