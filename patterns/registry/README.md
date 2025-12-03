---
doc_id: DOC-PAT-README-817
---

# Registry Directory

**Purpose**: Generated registries and schemas describing available patterns and operation kinds.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `PATTERN_INDEX.yaml` | Primary registry of all patterns (24 total) |
| `PATTERN_INDEX.schema.json` | JSON Schema for validating the pattern index |
| `PATTERN_INDEX.yaml.backup_*` | Dated backups of the pattern index |
| `OPERATION_KIND_REGISTRY.yaml` | Catalog of operation kinds used across patterns |
| `doc_id_mapping.json` | Mapping of document IDs |
| `template_doc_id_mapping.json` | Template-specific document ID mapping |
| `README.yaml` | Machine-readable directory metadata |

---

## Pattern Index

The `PATTERN_INDEX.yaml` contains:

- **24 patterns total** (7 core + 17 migrated)
- Pattern IDs (e.g., `PAT-ATOMIC-CREATE-001`)
- Pattern metadata (name, category, status)
- Cross-references to specs, executors, schemas

---

## Usage

### View All Patterns

```powershell
# Via CLI
..\scripts\pattern_cli.ps1 -Action list
```

### Validate Pattern Index

```bash
# Validate against schema
jsonschema -i PATTERN_INDEX.yaml PATTERN_INDEX.schema.json
```

### Update Registry

After adding or modifying patterns:

1. Update `PATTERN_INDEX.yaml`
2. Validate against `PATTERN_INDEX.schema.json`
3. Create backup with timestamp

---

## Operation Kinds

The `OPERATION_KIND_REGISTRY.yaml` catalogs:

- File operations (create, edit, delete)
- Git operations (commit, branch, merge)
- Validation operations (lint, test, verify)
- Custom operations

---

## Related

- `../specs/` - Pattern specifications
- `../schemas/` - Validation schemas
- `../scripts/pattern_cli.ps1` - CLI for registry operations
