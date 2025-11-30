# Scripts Directory - Doc ID Related Tools Discovery

**Date**: 2025-11-30  
**Location**: `scripts/`

## Found Doc ID Related Scripts

### Existing Scripts (Before Our Implementation)

1. **`scripts/doc_id_registry_cli.py`** (432 bytes)
   - **Type**: Compatibility wrapper
   - **Purpose**: Redirects to `doc_id.doc_id_registry_cli.main()`
   - **Created**: 2025-11-25
   - **Status**: Wrapper for the actual CLI in `doc_id/tools/`

2. **`scripts/doc_triage.py`** (9,811 bytes)
   - **Type**: Documentation triage tool
   - **Purpose**: Classifies Markdown docs with `DOC_`, `PLAN_`, `_DEV_` prefixes
   - **Pattern**: `PAT-DOCID-TRIAGE-001`
   - **Created**: 2025-11-25
   - **Status**: Different system - focuses on file naming conventions, not doc_id embedding
   - **Categories**: needs_move, needs_rename, needs_mint, needs_fix, ok

### New Scripts (Created Today)

3. **`scripts/doc_id_scanner.py`** (10,358 bytes)
   - **Type**: Repository scanner for doc_id coverage
   - **Purpose**: Scans files for embedded doc_ids, generates inventory
   - **Pattern**: `PAT-DOC-ID-SCANNER-001`
   - **Created**: 2025-11-30
   - **Status**: ✅ NEW - Part of Phase 0 auto-assignment system

4. **`scripts/doc_id_assigner.py`** (17,633 bytes)
   - **Type**: Auto-assignment tool
   - **Purpose**: Assigns doc_ids to files missing them
   - **Pattern**: `PAT-DOC-ID-AUTOASSIGN-002`
   - **Created**: 2025-11-30
   - **Status**: ✅ NEW - Part of Phase 0 auto-assignment system

## Relationship Between Tools

```
┌─────────────────────────────────────────────────────────────┐
│                 Doc ID Ecosystem                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Registry Management (Central Authority)                 │
│     └─ doc_id/tools/doc_id_registry_cli.py                 │
│        └─ scripts/doc_id_registry_cli.py (wrapper)         │
│        └─ Manages DOC_ID_REGISTRY.yaml                     │
│                                                              │
│  2. Phase 0 Auto-Assignment (NEW - Our Implementation)      │
│     ├─ scripts/doc_id_scanner.py                           │
│     │  └─ Scans repository, generates inventory            │
│     └─ scripts/doc_id_assigner.py                          │
│        └─ Assigns IDs, calls registry to mint              │
│                                                              │
│  3. Documentation Triage (Separate System)                  │
│     └─ scripts/doc_triage.py                               │
│        └─ Classifies files by naming convention            │
│        └─ Focuses on DOC_, PLAN_, _DEV_ prefixes           │
│        └─ Migration queue generation                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Differences

### doc_triage.py vs doc_id_scanner.py

| Feature | doc_triage.py | doc_id_scanner.py |
|---------|--------------|-------------------|
| **Focus** | File naming conventions | Embedded doc_id content |
| **Scope** | Markdown files only | 8 file types (py, md, yaml, json, etc.) |
| **Output** | Classification categories | JSONL inventory with status |
| **Purpose** | Migration planning | Coverage tracking |
| **Pattern** | `DOC_`, `PLAN_`, `_DEV_` prefixes | `DOC-XXX-YYY-NNN` format |
| **Action** | Suggests moves/renames | Tracks presence/absence |

### Complementary Use Cases

These tools can work together:

1. **doc_triage.py** → Identifies documentation that needs organization
2. **doc_id_scanner.py** → Finds which files lack doc_ids
3. **doc_id_assigner.py** → Assigns doc_ids to those files
4. **doc_id_registry_cli.py** → Manages the registry

## Scripts Directory Statistics

**Total Scripts**: 103 files  
**Python Scripts**: ~80  
**PowerShell Scripts**: ~20  
**Doc ID Related**: 4 (2 existing, 2 new)

### Doc ID Scripts by Category

```yaml
doc_id_tools:
  registry:
    - scripts/doc_id_registry_cli.py (wrapper)
    - doc_id/tools/doc_id_registry_cli.py (actual)
  
  phase_0_automation:
    - scripts/doc_id_scanner.py (NEW)
    - scripts/doc_id_assigner.py (NEW)
  
  triage_migration:
    - scripts/doc_triage.py (existing)
```

## Integration Opportunities

### Potential Workflow

```bash
# Step 1: Triage documentation structure
python scripts/doc_triage.py --report-only

# Step 2: Scan for doc_id coverage
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# Step 3: Auto-assign missing doc_ids
python scripts/doc_id_assigner.py auto-assign --dry-run
python scripts/doc_id_assigner.py auto-assign

# Step 4: Validate registry
python scripts/doc_id_registry_cli.py validate
python scripts/doc_id_registry_cli.py stats
```

## Recommendations

### 1. Update SCRIPT_INDEX.yaml

Add new scripts to the index:

```yaml
doc_id_management:
  - doc_id: DOC-SCRIPT-DOC-ID-SCANNER-XXX
    name: doc_id_scanner
    file: scripts/doc_id_scanner.py
    language: python
    purpose: "Scan repository for doc_id coverage and generate inventory"
    usage: "python scripts/doc_id_scanner.py scan"
    priority: high
    
  - doc_id: DOC-SCRIPT-DOC-ID-ASSIGNER-XXX
    name: doc_id_assigner
    file: scripts/doc_id_assigner.py
    language: python
    purpose: "Auto-assign doc_ids to files missing them"
    usage: "python scripts/doc_id_assigner.py auto-assign"
    priority: high
    
  - doc_id: DOC-SCRIPT-DOC-ID-REGISTRY-CLI-XXX
    name: doc_id_registry_cli
    file: scripts/doc_id_registry_cli.py
    language: python
    purpose: "Wrapper for doc_id registry CLI"
    usage: "python scripts/doc_id_registry_cli.py <command>"
    priority: high
    
  - doc_id: DOC-SCRIPT-DOC-TRIAGE-XXX
    name: doc_triage
    file: scripts/doc_triage.py
    language: python
    purpose: "Triage documentation files by naming convention"
    usage: "python scripts/doc_triage.py"
    priority: medium
```

### 2. Create Unified Documentation

Consider creating `docs/DOC_ID_TOOLS_GUIDE.md` that explains:
- When to use each tool
- How they work together
- Complete workflows
- Troubleshooting

### 3. Consider Merging/Renaming

If `doc_triage.py` and `doc_id_scanner.py` have overlapping concerns:
- Option A: Keep separate (different purposes)
- Option B: Merge into `doc_id_scanner.py` with `--mode triage` flag
- Option C: Rename `doc_triage.py` to `doc_naming_triage.py` for clarity

## Summary

✅ **Found 2 existing doc_id related scripts**  
✅ **Created 2 new Phase 0 automation scripts**  
✅ **All 4 tools serve different but complementary purposes**  
✅ **No conflicts or duplicates**  

The scripts directory is well-organized with distinct tools for:
1. **Registry management** (doc_id_registry_cli.py)
2. **Coverage tracking** (doc_id_scanner.py) - NEW
3. **Auto-assignment** (doc_id_assigner.py) - NEW
4. **Naming triage** (doc_triage.py)

---

**Next Action**: Update SCRIPT_INDEX.yaml to include the new scripts
