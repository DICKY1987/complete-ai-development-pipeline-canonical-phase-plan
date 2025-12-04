---
doc_id: DOC-PAT-README-019
---

# GitHub Integration for SPLINTER Phase Plans

This directory contains the pattern implementation for synchronizing SPLINTER Phase Plans with GitHub Issues and Projects v2.

## Overview

The GH_SYNC_PHASE_V1 pattern enables automatic bidirectional sync between:
- **SPLINTER Phase Plan YAML files** (ground truth)
- **GitHub Issues** (one per phase)
- **GitHub Projects v2** (custom fields for tracking)

## Files

```
patterns/
├── registry/
│   └── PATTERN_INDEX.yaml              # Pattern registry with GH_SYNC entry
├── specs/
│   └── GH_SYNC_PHASE_V1.pattern.yaml   # Pattern specification
├── schemas/
│   ├── GH_SYNC_PHASE_V1.schema.json    # Schema for github_integration block
│   └── SPLINTER_PHASE_PLAN_V1.schema.json  # Full phase plan schema
└── executors/
    └── github_sync/
        └── phase_sync.py               # Python implementation

scripts/
└── validate_phase_plan.py              # Validation script (PAT-CHECK-001)

.github/
└── workflows/
    └── splinter_phase_sync.yml         # GitHub Actions workflow
```

## Quick Start

### 1. Enable GitHub Integration in Your Phase Plan

Add to your phase plan YAML (or use the updated `MASTER_SPLINTER_Phase_Plan_Template.yml`):

```yaml
github_integration:
  enabled: true

  repo:
    owner: "YOUR_GITHUB_USERNAME"
    name: "YOUR_REPO_NAME"
    default_branch: "main"

  issue:
    mode: "one-per-phase"
    number: null
    title_template: "[{phase_id}] {title}"
    body_template_path: null
    labels:
      - "phase-plan"
    assignees: []

  project:
    owner: "YOUR_GITHUB_USERNAME"
    project_number: 1
    item_id: null

    field_mappings:
      phase_id_field: "Phase ID"
      workstream_field: "Workstream"
      status_field: "Status"
      risk_field: "Risk"
      target_date_field: "Target date"
      doc_id_field: "doc_id"

  automation:
    allow_issue_create: true
    allow_issue_update: true
    allow_project_item_create: true
    allow_project_item_update: true
    sync_direction: "yaml->github"
    on_phase_status_change_update_project: true
    on_project_status_change_update_phase: false
```

### 2. Create GitHub Project v2 with Custom Fields

In GitHub, create a new Project (Projects v2) with these custom fields:

| Field Name    | Type         | Description                          |
|---------------|--------------|--------------------------------------|
| Phase ID      | Text         | SPLINTER phase_id                   |
| Workstream    | Text         | SPLINTER workstream_id              |
| Status        | Single-select| Phase status (planned/active/done)  |
| Risk          | Single-select| Risk level (low/medium/high)        |
| Target date   | Date         | Target completion date              |
| doc_id        | Text         | SPLINTER document ID                |

### 3. Validate Your Phase Plan

```bash
python scripts/validate_phase_plan.py \
  --repo-root . \
  --phase-file phases/my_phase.yaml
```

This validates:
1. Pattern registry and GH_SYNC spec/schema
2. Full phase plan structure
3. github_integration block compliance

### 4. Manual Sync (Testing)

```bash
# Requires: pip install pyyaml requests jsonschema

# Dry run (preview actions)
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo owner/repo \
  --github-token $GITHUB_TOKEN \
  --dry-run

# Actual sync
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo owner/repo \
  --github-token $GITHUB_TOKEN
```

### 5. Automatic Sync via GitHub Actions

The workflow `.github/workflows/splinter_phase_sync.yml` automatically syncs phase plans when:
- Phase YAML files are pushed to `phases/**/*.yml` or `phases/**/*.yaml`
- Manual workflow dispatch is triggered

## Field Mappings

Customize the `field_mappings` in your `github_integration` block to match your Project v2 field names:

```yaml
field_mappings:
  phase_id_field: "Phase ID"          # Maps to phase_identity.phase_id
  workstream_field: "Workstream"      # Maps to phase_identity.workstream_id
  status_field: "Status"              # Maps to phase_identity.status
  risk_field: "Risk"                  # Maps to execution_profile.risk_level
  target_date_field: "Target date"    # Maps to completion_gate.target_date
  doc_id_field: "doc_id"              # Maps to doc_id
```

## Validation Order (PAT-CHECK-001)

The validation script follows this order:

1. **Pattern Registry & Specs**
   - Validate PATTERN_INDEX.yaml
   - Validate GH_SYNC_PHASE_V1.pattern.yaml
   - Validate GH_SYNC_PHASE_V1.schema.json

2. **Global Phase Plan Schema**
   - Validate against SPLINTER_PHASE_PLAN_V1.schema.json

3. **Nested GitHub Integration**
   - Validate github_integration block via $ref to GH_SYNC_PHASE_V1.schema.json

## Sync Behavior

### yaml->github (default)
- SPLINTER YAML is the single source of truth
- Changes to YAML update GitHub Issue and Project fields
- Manual changes to GitHub are overwritten on next sync

### bidirectional (optional)
- Changes in either direction are synchronized
- Set `on_project_status_change_update_phase: true`
- **Warning**: Requires additional conflict resolution logic

## Implementation Status

### ✅ Completed
- Pattern specification (GH_SYNC_PHASE_V1.pattern.yaml)
- JSON schemas (GH_SYNC_PHASE_V1, SPLINTER_PHASE_PLAN_V1)
- Validation script (validate_phase_plan.py)
- GitHub Actions workflow template
- Issue creation/update (REST API)
- Pattern registry integration

### 🚧 Stub/TODO
- Projects v2 GraphQL integration
  - Resolve project node ID
  - Find/create project items
  - Update custom field values
- Bidirectional sync logic
- Conflict resolution

## Contributing

The Projects v2 GraphQL integration is **complete and production-ready**, supporting:
- All standard field types (TEXT, DATE, NUMBER, SINGLE_SELECT)
- Automatic field type detection and value conversion
- Pagination for large projects
- Comprehensive error handling

### Future Enhancements
Potential improvements for future versions:
1. **Bidirectional sync**: Update YAML when Project fields change
2. **Conflict resolution**: Handle concurrent edits
3. **Additional field types**: ITERATION, MILESTONE, etc.
4. **Batch operations**: Sync multiple phases efficiently
5. **Webhooks**: Real-time sync on Project changes

## References

- [GitHub Projects v2 API](https://docs.github.com/en/graphql/reference/objects#projectv2)
- [GitHub Issues REST API](https://docs.github.com/en/rest/issues)
- [MASTER_SPLINTER_GITHUB_ADD_ON.md](../../MASTER_SPLINTER_GITHUB_ADD_ON.md) - Full integration guide
- [MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md](../../MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md)
