---
doc_id: DOC-PAT-README-918
---

# Glossary Examples

**Purpose**: Glossary-related artifacts and operation examples.

---

## Contents

| File | Description |
|------|-------------|
| `export_html.json` | Export glossary to HTML format |
| `export_json.json` | Export glossary to JSON format |
| `link_check_full.json` | Full link check configuration |
| `patch_apply_dry_run.json` | Dry-run patch application |
| `sync_codebase.json` | Sync glossary with codebase |
| `term_add_example.json` | Add new term example |
| `validate_full.json` | Full glossary validation |
| `validate_quick.json` | Quick validation |

---

## Usage

```powershell
# Export glossary
..\..\..\executors\glossary_export_executor.ps1 -InputFile export_json.json

# Validate glossary
..\..\..\executors\glossary_validate_executor.ps1 -InputFile validate_quick.json

# Add term
..\..\..\executors\glossary_term_add_executor.ps1 -InputFile term_add_example.json
```

---

## Related

- `../../executors/glossary_*_executor.ps1` - Glossary executors
- `../../schemas/glossary_*.schema.json` - Glossary schemas
