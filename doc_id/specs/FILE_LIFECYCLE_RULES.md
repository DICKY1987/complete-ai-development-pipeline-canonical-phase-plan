# DOC_ID File Lifecycle Rules

**Version**: 1.0  
**Status**: Canonical  
**Created**: 2025-11-29  
**Purpose**: Define how doc_ids behave during file splits, merges, moves, renames, and deletions

---

## Core Principles

1. **doc_id is immutable** - Once assigned, never changes meaning
2. **doc_id travels with content** - Stays with the primary conceptual artifact
3. **Registry is source of truth** - All lifecycle events recorded
4. **Git tracks history** - File operations visible in git log
5. **Metadata preserves lineage** - Relationships between old/new IDs tracked

---

## Lifecycle Events

### 1. File Move (Path Change)

**Scenario**: File relocates to different directory, content unchanged

```
Before:  docs/ARCHITECTURE.md (DOC-GUIDE-ARCHITECTURE-025)
After:   docs/architecture/DOC_ARCHITECTURE.md (DOC-GUIDE-ARCHITECTURE-025)
```

**Rule**: `doc_id` **UNCHANGED**

**Process**:
1. Move file using `git mv`
2. doc_id in front matter stays the same
3. Update registry entry:
   ```yaml
   - doc_id: DOC-GUIDE-ARCHITECTURE-025
     path: docs/architecture/DOC_ARCHITECTURE.md  # Updated
     previous_paths:
       - docs/ARCHITECTURE.md  # Tracked
     last_modified: 2025-11-29
   ```

**Git commit message**:
```
refactor: Move architecture docs to subdirectory

DOC_ID: DOC-GUIDE-ARCHITECTURE-025
Operation: move
Old path: docs/ARCHITECTURE.md
New path: docs/architecture/DOC_ARCHITECTURE.md
```

---

### 2. File Rename (Filename Change)

**Scenario**: Filename changes, content and location unchanged

```
Before:  docs/ARCHITECTURE.md (DOC-GUIDE-ARCHITECTURE-025)
After:   docs/DOC_SYSTEM_ARCHITECTURE.md (DOC-GUIDE-ARCHITECTURE-025)
```

**Rule**: `doc_id` **UNCHANGED**

**Process**:
1. Rename file using `git mv`
2. doc_id in front matter stays the same
3. Update registry entry (same as move)

**Git commit message**:
```
refactor: Rename architecture doc for consistency

DOC_ID: DOC-GUIDE-ARCHITECTURE-025
Operation: rename
Old name: ARCHITECTURE.md
New name: DOC_SYSTEM_ARCHITECTURE.md
```

---

### 3. File Split (One → Many)

**Scenario**: Single file becomes multiple files

```
Before:  orchestrator.py (DOC-CORE-ORCHESTRATOR-001)
         - OrchestratorCore class
         - Helper functions
         - Utility classes

After:   orchestrator_core.py (DOC-CORE-ORCHESTRATOR-001)  ← Primary keeps ID
         orchestrator_helpers.py (DOC-CORE-ORCHESTRATOR-HELPERS-002)  ← New ID
         orchestrator_utils.py (DOC-CORE-ORCHESTRATOR-UTILS-003)  ← New ID
```

**Rule**: 
- **Primary file** (main concept) **RETAINS** original `doc_id`
- **Derived files** receive **NEW** `doc_ids`
- Metadata tracks derivation relationship

**Process**:
1. Identify which file is "primary" (contains main concept)
2. Primary file keeps original `doc_id`
3. Create batch spec for derived files:
   ```yaml
   batch_id: DOCID-SPLIT-ORCHESTRATOR-001
   description: Assign IDs to files split from orchestrator
   category: core
   items:
     - logical_name: ORCHESTRATOR_HELPERS
       title: "Orchestrator Helper Functions"
       artifacts:
         - path: core/orchestrator_helpers.py
       metadata:
         derived_from: DOC-CORE-ORCHESTRATOR-001
         split_date: 2025-11-29
     - logical_name: ORCHESTRATOR_UTILS
       title: "Orchestrator Utility Classes"
       artifacts:
         - path: core/orchestrator_utils.py
       metadata:
         derived_from: DOC-CORE-ORCHESTRATOR-001
         split_date: 2025-11-29
   ```
4. Run batch mint → merge → write
5. Update original file's registry entry:
   ```yaml
   - doc_id: DOC-CORE-ORCHESTRATOR-001
     path: core/orchestrator_core.py
     status: active
     split_into:
       - DOC-CORE-ORCHESTRATOR-HELPERS-002
       - DOC-CORE-ORCHESTRATOR-UTILS-003
     split_date: 2025-11-29
   ```

**Git commit message**:
```
refactor: Split orchestrator into focused modules

DOC_ID: DOC-CORE-ORCHESTRATOR-001 (retained in orchestrator_core.py)
Operation: split
Derived files:
  - DOC-CORE-ORCHESTRATOR-HELPERS-002 (orchestrator_helpers.py)
  - DOC-CORE-ORCHESTRATOR-UTILS-003 (orchestrator_utils.py)
Reason: Improve modularity and separation of concerns
```

---

### 4. File Merge (Many → One)

**Scenario**: Multiple files combined into single file

```
Before:  orchestrator_core.py (DOC-CORE-ORCHESTRATOR-001)
         orchestrator_helpers.py (DOC-CORE-ORCHESTRATOR-HELPERS-002)
         orchestrator_utils.py (DOC-CORE-ORCHESTRATOR-UTILS-003)

After:   orchestrator.py (DOC-CORE-ORCHESTRATOR-MERGED-004)  ← New ID
```

**Rule**:
- **Merged file** receives **NEW** `doc_id`
- **Original files** marked as `superseded_by` new ID
- All original IDs retained in registry as `retired`

**Process**:
1. Create merged file with content from all sources
2. Create batch spec for merged file:
   ```yaml
   batch_id: DOCID-MERGE-ORCHESTRATOR-001
   description: Assign ID to merged orchestrator file
   category: core
   items:
     - logical_name: ORCHESTRATOR_MERGED
       title: "Unified Orchestrator Module"
       artifacts:
         - path: core/orchestrator.py
       metadata:
         supersedes:
           - DOC-CORE-ORCHESTRATOR-001
           - DOC-CORE-ORCHESTRATOR-HELPERS-002
           - DOC-CORE-ORCHESTRATOR-UTILS-003
         merge_date: 2025-11-29
         merge_reason: "Consolidate related functionality"
   ```
3. Run batch mint → merge → write
4. Update original files' registry entries:
   ```yaml
   - doc_id: DOC-CORE-ORCHESTRATOR-001
     path: core/orchestrator_core.py
     status: retired
     superseded_by: DOC-CORE-ORCHESTRATOR-MERGED-004
     superseded_date: 2025-11-29
   
   - doc_id: DOC-CORE-ORCHESTRATOR-HELPERS-002
     status: retired
     superseded_by: DOC-CORE-ORCHESTRATOR-MERGED-004
     superseded_date: 2025-11-29
   
   - doc_id: DOC-CORE-ORCHESTRATOR-UTILS-003
     status: retired
     superseded_by: DOC-CORE-ORCHESTRATOR-MERGED-004
     superseded_date: 2025-11-29
   ```

**Git commit message**:
```
refactor: Merge orchestrator modules into unified file

DOC_ID: DOC-CORE-ORCHESTRATOR-MERGED-004
Operation: merge
Supersedes:
  - DOC-CORE-ORCHESTRATOR-001 (orchestrator_core.py)
  - DOC-CORE-ORCHESTRATOR-HELPERS-002 (orchestrator_helpers.py)
  - DOC-CORE-ORCHESTRATOR-UTILS-003 (orchestrator_utils.py)
Reason: Reduce file count, improve cohesion
```

---

### 5. File Delete (Permanent Removal)

**Scenario**: File no longer needed, removed from repository

```
Before:  temp_migration_script.py (DOC-SCRIPT-TEMP-MIGRATION-042)

After:   [file deleted]
```

**Rule**:
- `doc_id` marked as **RETIRED** in registry
- Registry entry **PRESERVED** (never deleted)
- Git history shows deletion

**Process**:
1. Delete file using `git rm`
2. Update registry entry:
   ```yaml
   - doc_id: DOC-SCRIPT-TEMP-MIGRATION-042
     path: scripts/temp_migration_script.py
     status: retired
     retired_date: 2025-11-29
     retired_reason: "Migration complete, script no longer needed"
     deleted_in_commit: d15fb4b7a8c9e2f1d4b6a9c8e7f5d3a2b1c0e9f8
   ```
3. Do NOT remove from registry (preserves history)

**Git commit message**:
```
chore: Remove temporary migration script

DOC_ID: DOC-SCRIPT-TEMP-MIGRATION-042
Operation: delete
Reason: Migration to new module structure complete
Status: Retired
```

---

### 6. File Archive (Legacy Preservation)

**Scenario**: File moved to archive/, no longer active but preserved

```
Before:  core/legacy_parser.py (DOC-CORE-LEGACY-PARSER-015)

After:   archive/2025/legacy_parser.py (DOC-CORE-LEGACY-PARSER-015)
```

**Rule**: 
- `doc_id` **UNCHANGED**
- Status changed to `archived`
- Path updated to archive location

**Process**:
1. Move file to archive/ using `git mv`
2. Update registry entry:
   ```yaml
   - doc_id: DOC-CORE-LEGACY-PARSER-015
     path: archive/2025/legacy_parser.py
     status: archived
     archived_date: 2025-11-29
     archived_reason: "Replaced by new parser implementation"
     replaced_by: DOC-CORE-PARSER-V2-050
     previous_paths:
       - core/legacy_parser.py
   ```

**Git commit message**:
```
archive: Move legacy parser to archive

DOC_ID: DOC-CORE-LEGACY-PARSER-015
Operation: archive
Replaced by: DOC-CORE-PARSER-V2-050
Old path: core/legacy_parser.py
Archive path: archive/2025/legacy_parser.py
```

---

## Registry Status Values

```yaml
status:
  - active      # Current, in-use file
  - retired     # Deleted or superseded
  - archived    # Preserved but inactive
  - deprecated  # Marked for future removal
```

---

## Metadata Fields for Lifecycle Tracking

### For All Files
```yaml
doc_id: DOC-CATEGORY-NAME-001
path: current/path/to/file.ext
status: active
created: 2025-11-29
last_modified: 2025-11-29
previous_paths: []  # List of old paths if moved/renamed
```

### For Split Files
```yaml
# Original file
split_into:
  - DOC-CATEGORY-DERIVED-001
  - DOC-CATEGORY-DERIVED-002
split_date: 2025-11-29

# Derived files
derived_from: DOC-CATEGORY-ORIGINAL-001
split_date: 2025-11-29
```

### For Merged Files
```yaml
# New merged file
supersedes:
  - DOC-CATEGORY-OLD-001
  - DOC-CATEGORY-OLD-002
merge_date: 2025-11-29
merge_reason: "Description of why files were merged"

# Original files
status: retired
superseded_by: DOC-CATEGORY-MERGED-001
superseded_date: 2025-11-29
```

### For Deleted Files
```yaml
status: retired
retired_date: 2025-11-29
retired_reason: "Why file was removed"
deleted_in_commit: <git-sha>
```

### For Archived Files
```yaml
status: archived
archived_date: 2025-11-29
archived_reason: "Why file was archived"
replaced_by: DOC-CATEGORY-NEW-001  # Optional
```

---

## Conflict Resolution

### Same File, Different doc_ids (Merge Conflict)

**Scenario**: Two branches independently assign different doc_ids to the same file

```
Branch A: health.py → DOC-CORE-HEALTH-001
Branch B: health.py → DOC-CORE-HEALTH-002
```

**Rule**: **First merged wins**

**Process**:
1. First branch merges: DOC-CORE-HEALTH-001 becomes canonical
2. Second branch merge detects conflict
3. Resolve by:
   - Keep first doc_id (001)
   - Mark second doc_id (002) as `never_used` in registry:
     ```yaml
     - doc_id: DOC-CORE-HEALTH-002
       status: never_used
       conflicted_with: DOC-CORE-HEALTH-001
       resolution: "First merged wins policy"
       resolution_date: 2025-11-29
     ```
4. Update file to use first doc_id

### Same doc_id, Different Files (Duplicate)

**Scenario**: Two different files somehow assigned the same doc_id

```
File A: health.py → DOC-CORE-HEALTH-001
File B: status.py → DOC-CORE-HEALTH-001  (ERROR!)
```

**Rule**: **Hard error - must be fixed**

**Process**:
1. Validation detects duplicate
2. Error report generated
3. Manual resolution required:
   - Determine which assignment was correct
   - Assign new doc_id to the incorrect file
   - Update registry with correction metadata
4. Commit fix with explanation

---

## Validation Rules

### Registry Validation
```python
# validate_registry.py additions
def validate_lifecycle():
    """Validate lifecycle metadata consistency."""
    
    # Check 1: superseded_by points to valid doc_id
    for doc in registry['docs']:
        if doc.get('superseded_by'):
            if not find_doc_by_id(doc['superseded_by']):
                error(f"{doc['doc_id']} superseded_by invalid ID")
    
    # Check 2: split_into all exist
    for doc in registry['docs']:
        for split_id in doc.get('split_into', []):
            if not find_doc_by_id(split_id):
                error(f"{doc['doc_id']} split_into invalid ID")
    
    # Check 3: derived_from exists
    for doc in registry['docs']:
        if doc.get('derived_from'):
            if not find_doc_by_id(doc['derived_from']):
                error(f"{doc['doc_id']} derived_from invalid ID")
    
    # Check 4: No duplicate active doc_ids
    active_ids = [d['doc_id'] for d in registry['docs'] 
                  if d.get('status') == 'active']
    if len(active_ids) != len(set(active_ids)):
        error("Duplicate active doc_ids found")
```

---

## Automation Support

### Script: lifecycle_helper.py

```python
#!/usr/bin/env python3
"""
Helper script for file lifecycle operations
"""

def split_file(original_path, primary_path, derived_paths):
    """
    Handle file split operation
    - Keeps original doc_id on primary
    - Creates batch spec for derived files
    - Updates registry with relationships
    """
    pass

def merge_files(source_paths, target_path):
    """
    Handle file merge operation
    - Creates batch spec for merged file
    - Marks original files as retired
    - Updates registry with supersession
    """
    pass

def retire_file(file_path, reason):
    """
    Handle file deletion
    - Marks doc_id as retired in registry
    - Preserves history
    """
    pass

def archive_file(file_path, archive_path, replaced_by=None):
    """
    Handle file archival
    - Moves to archive/
    - Updates status and path
    - Links to replacement if provided
    """
    pass
```

---

## Summary

### Quick Reference Table

| Operation | doc_id Changes | Status | Registry Action |
|-----------|---------------|--------|-----------------|
| **Move** | No change | active | Update path, track previous_paths |
| **Rename** | No change | active | Update path, track previous_paths |
| **Split** | Primary keeps, derived get new | active | Add split_into, derived_from |
| **Merge** | All get new | retired → active | Mark old as retired, link supersedes |
| **Delete** | No change | retired | Mark retired, preserve entry |
| **Archive** | No change | archived | Update path to archive/, mark archived |

### Principles Recap

1. ✅ **doc_id is stable** - Survives moves and renames
2. ✅ **doc_id tracks lineage** - Split/merge relationships preserved
3. ✅ **Registry is comprehensive** - Never delete entries, only retire
4. ✅ **Git is canonical** - All operations use git mv/rm for traceability
5. ✅ **Metadata is rich** - Relationships and reasons documented

---

**Version**: 1.0  
**Status**: Canonical  
**Last Updated**: 2025-11-29  
**Next Review**: As needed when encountering new lifecycle patterns
