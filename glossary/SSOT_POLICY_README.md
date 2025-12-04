# Glossary SSOT Policy System

**Status**: ✅ Active  
**Spec**: `glossary/specs/GLOSSARY_SSOT_POLICY_SPEC.md`  
**Validator**: `scripts/glossary_ssot_policy.py`

## What This Does

Automatically enforces: **"Every SSOT document must have a glossary term."**

No one has to remember this rule—CI will catch violations before merge.

## Usage

### Check Policy Compliance

```bash
# Quick check
python scripts/glossary_ssot_policy.py

# Verbose output (see all SSOT docs found)
python scripts/glossary_ssot_policy.py --verbose
```

### Mark a Document as SSOT

Add front-matter to any `.md` file:

```yaml
---
doc_id: DOC-SPEC-MY-SYSTEM-001
ssot: true
ssot_scope:
  - my_domain
  - cross_cutting_concern
---
```

### Add Corresponding Glossary Term

In `glossary/.glossary-metadata.yaml` under `terms:`:

```yaml
TERM-SPEC-MY-SYSTEM:
  name: "My System Specification"
  category: "Specifications"  # Must be in ssot_categories
  status: "active"
  added_date: "2025-12-04"
  added_by: "your-name"
  implementation:
    files:
      - "path/to/my_spec.md"  # Must match SSOT doc path
```

### Valid SSOT Categories

See `glossary/config/glossary_ssot_policy.yaml`:

- `Specifications`
- `Framework`
- `GlobalService`
- `Contract`
- `CoreConcept`

## Error Messages

### SSOT doc without glossary term

```
❌ ERRORS:

SSOT document without glossary term: path/to/spec.md
doc_id: DOC-SPEC-XXX-001

Fix: Add a glossary term in glossary/.glossary-metadata.yaml under 'terms:' section
```

**Fix**: Add a glossary term that references the file.

### Glossary term references missing file

```
❌ ERRORS:

Glossary term references missing file: TERM-SPEC-XYZ
File: old/path/to/spec.md

Fix: Either:
1. Restore the file, OR
2. Remove the file from term's implementation.files, OR
3. Update the path if file was moved
```

**Fix**: Update the term's `implementation.files` or restore the file.

### SSOT doc missing doc_id

```
❌ ERRORS:

SSOT document missing required doc_id: path/to/spec.md

Fix: Add doc_id to front-matter (format: DOC-CATEGORY-NAME-NNN)
```

**Fix**: Add `doc_id:` field to front-matter.

## CI Integration

### Pre-commit (Local)

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: glossary-ssot-policy
      name: Glossary SSOT Policy
      entry: python scripts/glossary_ssot_policy.py
      language: system
      pass_filenames: false
```

Then run:

```bash
pre-commit install
```

### GitHub Actions (Remote)

Add to workflow:

```yaml
- name: Validate glossary SSOT policy
  run: |
    pip install pyyaml
    python scripts/glossary_ssot_policy.py
```

## Configuration

Edit `glossary/config/glossary_ssot_policy.yaml` to:

- Add/remove SSOT categories
- Change CI enforcement levels
- Exclude file patterns
- Customize error messages

## Examples

### Current SSOT Documents

Run to see all current SSOT docs:

```bash
python scripts/glossary_ssot_policy.py --verbose
```

Output:
```
[SSOT] Found: glossary/specs/GLOSSARY_SSOT_POLICY_SPEC.md (doc_id=DOC-GLOSS-SSOT-POLICY-001)
[SSOT] Found: specs/ID_SYSTEM_SPEC.md (doc_id=DOC-SPEC-ID-001)
...
```

### Workflow: Adding New SSOT Spec

1. **Create spec with front-matter**:

   ```bash
   # In specs/MY_NEW_SPEC.md
   ---
   doc_id: DOC-SPEC-MYNEW-001
   ssot: true
   ssot_scope: [new_system]
   ---
   
   # My New Spec
   ...
   ```

2. **Add glossary term**:

   ```yaml
   # In glossary/.glossary-metadata.yaml
   TERM-SPEC-MYNEW:
     name: "My New System"
     category: "Specifications"
     implementation:
       files: ["specs/MY_NEW_SPEC.md"]
   ```

3. **Validate**:

   ```bash
   python scripts/glossary_ssot_policy.py
   # ✅ All SSOT policy validations passed
   ```

4. **Commit** → pre-commit validates → CI validates

## Benefits

- ✅ **Zero cognitive load**: No need to remember the rule
- ✅ **Fast feedback**: Pre-commit catches issues in <1s
- ✅ **Clear guidance**: Error messages tell you exactly what to fix
- ✅ **Self-enforcing**: The policy spec itself is validated
- ✅ **No drift**: Glossary and SSOT docs stay in sync

## Troubleshooting

### "Policy config not found"

Ensure `glossary/config/glossary_ssot_policy.yaml` exists.

### "Glossary metadata not found"

Ensure `glossary/.glossary-metadata.yaml` exists with `terms:` section.

### "Module 'yaml' not found"

```bash
pip install pyyaml
```

## Future Enhancements

See spec section 8 for planned features:

- `--autofix` mode to auto-generate missing terms
- Path registry integration (3-way consistency)
- Scope tag validation
- Impact analysis on SSOT changes
