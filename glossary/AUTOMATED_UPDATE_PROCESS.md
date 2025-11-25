# Automated Glossary Update Process

**Purpose**: Structured, automated process for updating glossary terms using patches  
**Tool**: `glossary/scripts/update_term.py`  
**Status**: ✅ Ready to use

---

## Quick Start

```bash
cd glossary

# 1. Create patch specification
cat > updates/my-update.yaml <<EOF
patch_id: "01J..."
description: "Add missing schema refs"
date: "2025-11-25"
author: "your-name"
terms:
  - term_id: TERM-ENGINE-001
    action: add
    field: schema_refs
    value: ["schema/new.json"]
EOF

# 2. Preview changes (dry run)
python scripts/update_term.py --spec updates/my-update.yaml --dry-run

# 3. Apply changes
python scripts/update_term.py --spec updates/my-update.yaml --apply

# 4. Validate
python scripts/validate_glossary.py
```

---

## Update Workflows

### Workflow 1: Bulk Updates via Patch Spec

**Use Case**: Update multiple terms with similar changes

**Steps**:

1. **Create Patch Specification**
   ```yaml
   # updates/add-schemas.yaml
   patch_id: "01J5XY..."
   description: "Add UET schema references"
   date: "2025-11-25"
   author: "architecture-team"
   
   terms:
     - term_id: TERM-ENGINE-001
       action: add
       field: schema_refs
       value: ["schema/uet/execution_request.v1.json"]
     
     - term_id: TERM-PATCH-001
       action: add
       field: schema_refs
       value: ["schema/uet/patch_artifact.v1.json"]
   ```

2. **Dry Run (Preview)**
   ```bash
   python scripts/update_term.py --spec updates/add-schemas.yaml --dry-run
   ```
   
   **Output**:
   ```
   📖 Loading glossary files...
      ✓ Loaded glossary.md
      ✓ Loaded .glossary-metadata.yaml
   
   🔧 Applying patch: 01J5XY...
      Description: Add UET schema references
      Terms to update: 2
      🔍 DRY RUN MODE - No changes will be saved
   
   📝 TERM-ENGINE-001: add schema_refs
      ✅ Updated
   📝 TERM-PATCH-001: add schema_refs
      ✅ Updated
   
   🔍 DRY RUN - Changes preview:
   [shows YAML preview of changes]
      Total changes: 2
      Run with --apply to save changes
   ```

3. **Review Changes**
   - Check the preview output
   - Verify term IDs are correct
   - Confirm values are accurate

4. **Apply Patch**
   ```bash
   python scripts/update_term.py --spec updates/add-schemas.yaml --apply
   ```
   
   **Output**:
   ```
   📖 Loading glossary files...
   🔧 Applying patch: 01J5XY...
   📝 TERM-ENGINE-001: add schema_refs ✅
   📝 TERM-PATCH-001: add schema_refs ✅
   💾 Saving changes...
      ✅ Saved .glossary-metadata.yaml
      ✅ Updated 2 terms
   📋 Updating changelog...
      ✅ Updated DOC_GLOSSARY_CHANGELOG.md
   ✅ Patch applied successfully
   ```

5. **Validate**
   ```bash
   python scripts/validate_glossary.py
   ```

6. **Commit**
   ```bash
   git add .glossary-metadata.yaml docs/DOC_GLOSSARY_CHANGELOG.md
   git commit -m "glossary: add UET schema references (patch 01J5XY...)"
   ```

---

### Workflow 2: Single Term Quick Update

**Use Case**: Quick update to one term's field

**Steps**:

1. **Update Single Field**
   ```bash
   python scripts/update_term.py \
     --term TERM-ENGINE-001 \
     --field implementation.files \
     --value "core/engine/orchestrator.py" \
     --apply
   ```

2. **Validate**
   ```bash
   python scripts/validate_glossary.py --quick
   ```

3. **Commit**
   ```bash
   git commit -am "glossary: update TERM-ENGINE-001 implementation path"
   ```

---

### Workflow 3: CI/CD Automated Updates

**Use Case**: Automatically apply patches on merge to main

**GitHub Actions** (`.github/workflows/glossary-patch.yml`):

```yaml
name: Apply Glossary Patches

on:
  push:
    branches: [main]
    paths:
      - 'glossary/updates/*.yaml'

jobs:
  apply-patches:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Find new patches
        id: find_patches
        run: |
          cd glossary
          NEW_PATCHES=$(git diff --name-only HEAD~1 HEAD -- updates/*.yaml)
          echo "patches=$NEW_PATCHES" >> $GITHUB_OUTPUT
      
      - name: Apply patches
        if: steps.find_patches.outputs.patches
        run: |
          cd glossary
          for patch in ${{ steps.find_patches.outputs.patches }}; do
            echo "Applying $patch"
            python scripts/update_term.py --spec "$patch" --apply --validate
          done
      
      - name: Commit changes
        if: steps.find_patches.outputs.patches
        run: |
          git config user.name "Glossary Bot"
          git config user.email "bot@example.com"
          git add glossary/.glossary-metadata.yaml glossary/docs/DOC_GLOSSARY_CHANGELOG.md
          git commit -m "glossary: auto-apply patches" || exit 0
          git push
```

---

## Patch Actions

### 1. `add` - Add values to field

**Use**: Add items to lists or create new fields

```yaml
- term_id: TERM-ENGINE-001
  action: add
  field: schema_refs
  value: ["schema/new.json"]
```

**Behavior**:
- If field exists (list): Appends values
- If field doesn't exist: Creates list with values
- Removes duplicates automatically

### 2. `update` - Update/extend field

**Use**: Update existing field or extend lists

```yaml
- term_id: TERM-ENGINE-001
  action: update
  field: implementation.files
  value: ["core/engine/orchestrator.py"]
```

**Behavior**:
- For lists: Extends (like `add`)
- For strings: Replaces value
- For dicts: Merges values

### 3. `replace` - Complete replacement

**Use**: Replace entire field value

```yaml
- term_id: TERM-ENGINE-001
  action: replace
  field: related_terms
  value:
    - term_id: TERM-ENGINE-002
      relationship: uses
```

**Behavior**:
- Completely replaces field value
- Use for restructuring

### 4. `remove` - Remove values

**Use**: Remove items from lists or delete fields

```yaml
- term_id: TERM-ENGINE-001
  action: remove
  field: aliases
  value: "Old Name"
```

**Behavior**:
- For lists: Removes specific value
- For fields: Deletes field entirely

---

## Automated Workflows

### Weekly Schema Sync

**Automate**: Keep schema references up-to-date

**Script** (`scripts/sync_schemas.sh`):

```bash
#!/bin/bash
# Auto-generate patch for new schemas

cd glossary

# Find terms missing schema refs
python scripts/find_missing_schemas.py > updates/weekly-schema-sync.yaml

# Apply
python scripts/update_term.py --spec updates/weekly-schema-sync.yaml --apply --validate

# Commit
git commit -am "glossary: weekly schema sync"
```

**Cron**: Weekly on Sunday
```cron
0 0 * * 0 cd /path/to/repo && ./scripts/sync_schemas.sh
```

---

### PR-Based Updates

**Process**:

1. **Create Branch**
   ```bash
   git checkout -b glossary/add-examples
   ```

2. **Create Patch Spec**
   ```bash
   cat > glossary/updates/add-examples.yaml <<EOF
   patch_id: "01J..."
   description: "Add usage examples to core terms"
   terms:
     - term_id: TERM-ENGINE-001
       action: add
       field: usage_examples
       value:
         - language: python
           code: |
             from core.engine.orchestrator import Orchestrator
             orch = Orchestrator()
           description: "Basic usage"
   EOF
   ```

3. **Apply and Test**
   ```bash
   cd glossary
   python scripts/update_term.py --spec updates/add-examples.yaml --apply --validate
   ```

4. **Create PR**
   ```bash
   git add -A
   git commit -m "glossary: add usage examples to core terms"
   git push origin glossary/add-examples
   # Create PR on GitHub
   ```

5. **CI Validates**
   - Runs validation automatically
   - Checks for conflicts
   - Verifies patch format

6. **Merge**
   - On merge, changes applied
   - Changelog auto-updated

---

## Batch Processing

### Process Multiple Patches

```bash
#!/bin/bash
# Apply all pending patches

cd glossary/updates

for patch in pending-*.yaml; do
  echo "Applying $patch..."
  python ../scripts/update_term.py --spec "$patch" --apply
  
  if [ $? -eq 0 ]; then
    # Move to applied folder
    mv "$patch" applied/
  else
    echo "Failed: $patch"
  fi
done

# Validate all
cd ..
python scripts/validate_glossary.py
```

---

## Quality Checks

### Pre-Apply Validation

```bash
# 1. Validate patch spec format
python scripts/validate_patch_spec.py updates/my-patch.yaml

# 2. Dry run
python scripts/update_term.py --spec updates/my-patch.yaml --dry-run

# 3. Check for conflicts
python scripts/check_patch_conflicts.py updates/my-patch.yaml

# 4. Apply
python scripts/update_term.py --spec updates/my-patch.yaml --apply

# 5. Validate result
python scripts/validate_glossary.py
```

### Post-Apply Checks

```bash
# Check orphaned terms
python scripts/validate_glossary.py --check-orphans

# Verify implementation paths
python scripts/validate_glossary.py --check-paths

# Generate metrics
python scripts/generate_glossary_metrics.py
```

---

## Rollback

### Undo Last Patch

```bash
# 1. Git revert
git revert HEAD

# 2. Or manual rollback
python scripts/rollback_patch.py --patch-id 01J5XY...
```

### Restore from Backup

```bash
# Auto-backup before each patch
cp .glossary-metadata.yaml .glossary-metadata.yaml.backup

# Restore
cp .glossary-metadata.yaml.backup .glossary-metadata.yaml
```

---

## Integration with Git

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate glossary if changed
if git diff --cached --name-only | grep -q "glossary/"; then
  cd glossary
  python scripts/validate_glossary.py --quick
  if [ $? -ne 0 ]; then
    echo "❌ Glossary validation failed"
    exit 1
  fi
fi
```

### Commit Message Template

```
glossary: <action> <description>

Patch ID: <patch_id>
Terms affected: <count>

Changes:
- <term_id>: <action> <field>
- <term_id>: <action> <field>

Relates-to: #<issue_number>
```

---

## Monitoring

### Track Patch Application

```bash
# View recent patches
grep "^### Patch:" glossary/docs/DOC_GLOSSARY_CHANGELOG.md | head -5

# Count patches this month
grep "2025-11" glossary/docs/DOC_GLOSSARY_CHANGELOG.md | grep "### Patch:" | wc -l

# List terms updated most frequently
python scripts/most_updated_terms.py
```

### Metrics Dashboard

```bash
# Generate weekly report
python scripts/generate_glossary_metrics.py --output docs/glossary_metrics.md

# Includes:
# - Patches applied
# - Terms updated
# - Quality trends
# - Coverage improvements
```

---

## Best Practices

### ✅ DO

1. **Always dry-run first**
   ```bash
   python scripts/update_term.py --spec patch.yaml --dry-run
   ```

2. **Validate after applying**
   ```bash
   python scripts/update_term.py --spec patch.yaml --apply --validate
   ```

3. **Use descriptive patch IDs**
   - Include date: `01J5XY...` (ULID format)
   - Use semantic naming for manual: `manual-add-schemas-20251125`

4. **Keep patches small**
   - 5-10 terms per patch
   - Single purpose per patch

5. **Document in description**
   - Clear what and why
   - Reference issues/PRs

### ❌ DON'T

1. **Don't skip dry-run**
2. **Don't edit metadata directly** - use patches
3. **Don't apply conflicting patches** - check first
4. **Don't delete patch specs** - keep for audit trail

---

## Examples

See `/glossary/updates/` for examples:
- `example-add-uet-schemas.yaml` - Add schema references
- `example-add-implementation-paths.yaml` - Add code paths

---

## Troubleshooting

### "Term not found"
- Check term ID is correct
- Verify term exists in `.glossary-metadata.yaml`

### "Validation failed"
- Review validation errors
- Fix issues in patch spec
- Re-run with `--dry-run`

### "Patch conflicts"
- Check if another patch modified same fields
- Merge or separate patches

---

## Summary

The automated patch system provides:

✅ **Structured updates** via YAML specs  
✅ **Safe application** with dry-run mode  
✅ **Automatic tracking** in changelog  
✅ **Quality validation** built-in  
✅ **Git-friendly** workflow  
✅ **CI/CD ready** for automation  

**Status**: Production ready, tested, documented
