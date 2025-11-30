---
doc_id: DOC-GUIDE-TASK-V1-TO-V2-1366
---

# Schema Migration: Task Definition v1 to v2

## Overview

This document describes the migration path from Task Definition Schema v1.0.0 to v2.0.0.

**Version 1.0.0**: Initial task definition schema  
**Version 2.0.0**: Enhanced with context requirements and validation rules  
**Migration Status**: Backward compatible with automatic upgrade  
**Compatibility Window**: v1.0.0 supported until 2025-12-31

## Changes in v2.0.0

### New Fields (Optional)

```json
{
  "context_requirements": {
    "max_context_tokens": 8000,
    "required_files": ["src/auth/handler.py"],
    "optional_files": ["src/auth/utils.py"],
    "exclude_patterns": ["tests/**", "*.pyc"]
  },
  
  "validation_rules": {
    "pre_execution": ["git_clean", "tests_passing"],
    "post_execution": ["no_lint_errors", "tests_still_passing"]
  }
}
```

### Changed Fields

None. All v1.0.0 fields remain unchanged.

### Deprecated Fields

None in v2.0.0.

### Removed Fields

None in v2.0.0.

## Migration Procedure

### Automatic Migration

The orchestration system automatically migrates v1.0.0 task definitions to v2.0.0 on load:

1. Detect schema version from `schema_version` field
2. If version < 2.0.0:
   - Add default `context_requirements` if task type is `aider`
   - Add default `validation_rules` based on task type
   - Update `schema_version` to `2.0.0`
3. Write migrated definition back to disk (optional, controlled by config)

**Default Context Requirements** (for Aider tasks):
```json
{
  "max_context_tokens": 8000,
  "required_files": [],
  "optional_files": [],
  "exclude_patterns": ["**/__pycache__/**", "**/*.pyc", "**/node_modules/**"]
}
```

**Default Validation Rules** (by task type):
```json
// For type: aider
{
  "pre_execution": ["git_clean"],
  "post_execution": ["no_lint_errors"]
}

// For type: pytest
{
  "pre_execution": [],
  "post_execution": ["tests_passing"]
}

// For type: lint
{
  "pre_execution": [],
  "post_execution": []
}
```

### Manual Migration

To manually migrate task definitions:

```bash
python scripts/migrate_task_schema.py --from 1.0.0 --to 2.0.0 --directory tasks/
```

**Options**:
- `--from`: Source schema version
- `--to`: Target schema version
- `--directory`: Directory containing task definitions
- `--dry-run`: Preview changes without writing
- `--backup`: Create backups before migration (default: true)

### Validation

After migration, validate all task definitions:

```bash
python scripts/validate/validate_task_defs.py --schema-version 2.0.0
```

## Example Migration

### Before (v1.0.0)

```json
{
  "schema_version": "1.0.0",
  "task_id": "task-ulid-002",
  "workstream_id": "ws-ulid-001",
  "name": "Implement authentication",
  "description": "Add JWT authentication",
  "type": "aider",
  "status": "pending",
  
  "dependencies": [],
  "blocks": [],
  
  "worker_requirements": {
    "capabilities": ["aider"],
    "min_version": "1.0.0"
  },
  
  "execution": {
    "command": "aider --yes --message '{prompt}'",
    "working_directory": "src/auth",
    "timeout_seconds": 600,
    "max_retries": 3,
    "retry_delay_seconds": 10
  },
  
  "state": {
    "created_at": "2024-01-15T10:00:00.000Z",
    "started_at": null,
    "completed_at": null,
    "assigned_worker": null,
    "retry_count": 0,
    "last_error": null
  }
}
```

### After (v2.0.0)

```json
{
  "schema_version": "2.0.0",
  "schema_url": "https://schemas.orchestration.local/task/v2.0.0",
  "task_id": "task-ulid-002",
  "workstream_id": "ws-ulid-001",
  "name": "Implement authentication",
  "description": "Add JWT authentication",
  "type": "aider",
  "status": "pending",
  
  "dependencies": [],
  "blocks": [],
  
  "worker_requirements": {
    "capabilities": ["aider"],
    "min_version": "1.0.0"
  },
  
  "execution": {
    "command": "aider --yes --message '{prompt}'",
    "working_directory": "src/auth",
    "timeout_seconds": 600,
    "max_retries": 3,
    "retry_delay_seconds": 10
  },
  
  "context_requirements": {
    "max_context_tokens": 8000,
    "required_files": ["src/auth/handler.py", "src/auth/models.py"],
    "optional_files": ["src/auth/utils.py"],
    "exclude_patterns": ["tests/**", "*.pyc", "**/__pycache__/**"]
  },
  
  "validation_rules": {
    "pre_execution": ["git_clean"],
    "post_execution": ["no_lint_errors", "tests_still_passing"]
  },
  
  "state": {
    "created_at": "2024-01-15T10:00:00.000Z",
    "started_at": null,
    "completed_at": null,
    "assigned_worker": null,
    "retry_count": 0,
    "last_error": null
  }
}
```

## Rollback Procedure

If migration causes issues, rollback to v1.0.0:

```bash
python scripts/migrate_task_schema.py --from 2.0.0 --to 1.0.0 --directory tasks/ --restore-backup
```

Or manually restore from backups:

```bash
cp tasks/.backups/20240115-120000/task-ulid-002.json tasks/ws-ulid-001/task-ulid-002.json
```

## Testing

### Test Plan

1. **Unit Tests**: Verify schema migration logic
   ```bash
   pytest tests/schema/test_task_migration.py
   ```

2. **Integration Tests**: Migrate sample tasks and execute
   ```bash
   pytest tests/integration/test_task_migration_integration.py
   ```

3. **Validation Tests**: Ensure migrated tasks validate correctly
   ```bash
   python scripts/validate/validate_task_defs.py --schema-version 2.0.0
   ```

### Test Cases

- [x] Migrate task with no context requirements → Adds defaults
- [x] Migrate task with no validation rules → Adds type-specific defaults
- [x] Migrate task that's already v2.0.0 → No changes
- [x] Migrate invalid v1.0.0 task → Reports error
- [x] Rollback v2.0.0 to v1.0.0 → Removes new fields
- [x] Execute migrated task → Works correctly

## Compatibility Matrix

| Schema Version | Supported By | Support Until | Notes |
|----------------|--------------|---------------|-------|
| 1.0.0 | All versions | 2025-12-31 | Auto-migrated on load |
| 2.0.0 | v1.1.0+ | Current | Recommended |

## FAQ

**Q: Do I need to migrate manually?**  
A: No. The system auto-migrates v1.0.0 tasks on load. Manual migration is optional for permanent upgrade.

**Q: Will v1.0.0 tasks still work?**  
A: Yes. v1.0.0 tasks are supported until 2025-12-31 and auto-migrate at runtime.

**Q: Can I use v2.0.0 features in v1.0.0 tasks?**  
A: No. You must set `schema_version: "2.0.0"` to use new fields.

**Q: What happens if I downgrade from v2.0.0 to v1.0.0?**  
A: New fields (context_requirements, validation_rules) are removed. Data is lost unless backed up.

**Q: Are there breaking changes?**  
A: No. v2.0.0 is backward compatible with v1.0.0.

## See Also

- [Task Definition Schema v2.0.0](../../specifications/content/orchestration/spec.md#task-definitions)
- [Schema Versioning Policy](./VERSIONING_POLICY.md)
- [Migration Tools Reference](../../scripts/migrate_task_schema.py)
