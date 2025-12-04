---
doc_id: DOC-GLOSS-SSOT-POLICY-001
role: spec
status: active
ssot: true
ssot_scope:
  - glossary_system
  - policy_enforcement
---

# GLOSSARY_SSOT_POLICY_SPEC_V1

## 1. Purpose

This spec defines how "single source of truth" (SSOT) documents are
represented and enforced in the glossary system.

**Goal**: Eliminate the need for humans to remember that SSOT docs must have
corresponding glossary entries. The system enforces this autonomously via CI.

## 2. Definitions

### SSOT Document
A document that defines global or cross-cutting rules, contracts, or invariants.

**Examples**:
- `master_plan.json` - Global plan structure
- ID system spec - Document identifier rules
- Phase spec - Pipeline phase contracts
- Patch spec - Change propagation rules
- Path abstraction spec - Path indirection layer
- Execution kernel spec - Core execution contracts

**Characteristics**:
- Contains normative "MUST"/"MUST NOT" requirements
- Referenced across multiple modules/phases
- Changes have system-wide impact
- Serves as contract between components

## 3. Requirements (MUST)

### 3.1 SSOT Document Front-Matter
Every SSOT document MUST declare itself in front-matter:

```yaml
---
doc_id: DOC-SPEC-XXX-YYY-NNN
ssot: true
ssot_scope:
  - scope_tag_1
  - scope_tag_2
---
```

**Fields**:
- `ssot: true` - Marks document as SSOT (triggers policy enforcement)
- `doc_id` - Unique document identifier (required)
- `ssot_scope` - List of scope tags (optional but recommended)

### 3.2 Glossary Term Requirement
For every SSOT document, there MUST exist at least one glossary term that:

1. References the document's path under `implementation.files`
2. Uses a category from `ssot_categories` (see policy config)
3. Has a valid `term_id` in the glossary metadata

**Example**:
```yaml
TERM-SPEC-MASTER-PLAN:
  name: "Master Plan"
  category: "Specifications"
  implementation:
    files:
      - "master_plan.json"
      - "master_plan.md"
```

### 3.3 Lifecycle Consistency
SSOT documents may NOT be:

1. **Deleted** without:
   - Removing/updating glossary term's `implementation.files`
   - Updating any path registry entries
   - Documenting deprecation if applicable

2. **Moved/Renamed** without:
   - Updating glossary term's `implementation.files`
   - Updating path registry (if applicable)
   - Preserving `doc_id` (content identity unchanged)

## 4. Validation

Validation is performed by `scripts/glossary_ssot_policy.py`, which:

1. **Discovers** all documents with `ssot: true` in front-matter
2. **Validates** each SSOT doc has ≥1 glossary term referencing it
3. **Validates** each SSOT glossary term points to existing file(s)
4. **Fails CI** if any violation found

### 4.1 Validation Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `SSOT_DOC_NO_TERM` | ERROR | SSOT doc exists but no glossary term references it |
| `TERM_MISSING_FILE` | ERROR | Glossary term references non-existent SSOT file |
| `SSOT_NO_DOC_ID` | ERROR | SSOT doc missing required `doc_id` field |
| `TERM_WRONG_CATEGORY` | WARNING | SSOT term uses non-SSOT category |

### 4.2 CI Integration

**Pre-commit** (local):
```yaml
- id: glossary-ssot-policy
  name: Glossary SSOT Policy
  entry: python scripts/glossary_ssot_policy.py
  language: system
  pass_filenames: false
```

**GitHub Actions** (remote):
```yaml
- name: Validate glossary SSOT policy
  run: python scripts/glossary_ssot_policy.py
```

## 5. Configuration

Policy behavior controlled by `glossary/config/glossary_ssot_policy.yaml`:

```yaml
ssot_policy:
  term_categories:
    - Specifications
    - Framework
    - GlobalService
    - Contract

  ssot_frontmatter_field: "ssot"
  ssot_scope_field: "ssot_scope"
  
  glossary_metadata_file: "glossary/.glossary-metadata.yaml"
  
  ci:
    fail_on_missing_term_for_ssot_doc: true
    fail_on_missing_doc_for_ssot_term: true
    warn_on_wrong_category: true
```

## 6. Workflow

### Adding New SSOT Document

1. Create document with front-matter:
   ```yaml
   ---
   doc_id: DOC-SPEC-NEW-001
   ssot: true
   ssot_scope: [new_system]
   ---
   ```

2. Add glossary term:
   ```yaml
   TERM-SPEC-NEW-SYSTEM:
     name: "New System Spec"
     category: "Specifications"
     implementation:
       files: ["path/to/new_spec.md"]
   ```

3. Commit → pre-commit validates → CI validates

### Moving SSOT Document

1. Update glossary term's `implementation.files`
2. Move file
3. Commit → policy validates path exists

### Removing SSOT Document

1. Either:
   - Remove `ssot: true` from front-matter (if doc still exists), OR
   - Remove glossary term (if doc being deleted)
2. Commit → policy validates consistency

## 7. Benefits

**For Humans**:
- ✅ No need to remember rule
- ✅ Immediate feedback (pre-commit)
- ✅ Clear error messages pointing to fix

**For System**:
- ✅ Glossary always reflects SSOT docs
- ✅ SSOT docs always discoverable
- ✅ Path consistency enforced
- ✅ Documentation drift prevented

## 8. Future Enhancements

### 8.1 Auto-Fix Mode
```bash
python scripts/glossary_ssot_policy.py --autofix
```
- Auto-generate glossary term stubs for new SSOT docs
- Auto-update paths when files moved

### 8.2 Path Registry Integration
Enforce 3-way consistency:
```
SSOT doc ↔ glossary term ↔ path_registry key
```

### 8.3 Scope Validation
Validate `ssot_scope` tags against allowed taxonomy.

### 8.4 Impact Analysis
Report which glossary terms/modules affected by SSOT doc change.

## 9. Compliance

This spec is **self-enforcing**: it is itself an SSOT document with a
corresponding glossary term (`TERM-GLOSS-SSOT-POLICY`), validated by the
same policy it defines.

**Meta-validation**: The policy validator must validate itself.
