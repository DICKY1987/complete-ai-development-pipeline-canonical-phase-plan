# How Remaining Documents Get IDs

**Question**: How do the rest of the documents get doc_ids?  
**Answer**: Through the same batch workflow, after cleanup.

---

## Current State

From the triage report:
- **Already ID'd**: 61 documents (Phase 3 complete)
- **Needs Move**: 22 files (in wrong locations)
- **Needs Rename**: 110 files (don't follow DOC_/PLAN_ convention)

**Total remaining**: ~132 files need cleanup before ID assignment

---

## The Process (Step by Step)

### Step 1: Cleanup Files (Manual or Scripted)

#### For "NEEDS MOVE" Files (22 files)
Files like `DOC_ID_COMPLETE_EXECUTION_SUMMARY.md` that are in the root but should be in `docs/`:

```bash
# Move to correct location
mv DOC_ID_COMPLETE_EXECUTION_SUMMARY.md docs/

# Or for dev files
mv _DEV_NOTES.md developer/
```

#### For "NEEDS RENAME" Files (110 files)
Files like `MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md` in `docs/` that need DOC_ prefix:

```bash
# Rename to follow convention
mv docs/MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md docs/DOC_MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md

# Add front matter
cat << EOF > docs/DOC_MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md
---
status: draft
doc_type: guide
---

$(cat docs/DOC_MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md)
EOF
```

### Step 2: Create New Batch Specifications

Once files are cleaned up, create batch specs like we did in Phase 3:

**Example**: `doc_id/batches/batch_module_centric_docs.yaml`
```yaml
batch_id: DOCID-BATCH-MODULE-CENTRIC-001
description: Assign doc_ids to module-centric documentation
category: guide
items:
  - logical_name: MODULE_CENTRIC_IMPLEMENTATION_SUMMARY
    title: "Module-Centric Implementation Summary"
    artifacts:
      - path: docs/DOC_MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md
  - logical_name: MODULE_CENTRIC_ARCHITECTURE_OVERVIEW
    title: "Module-Centric Architecture Overview"
    artifacts:
      - path: docs/DOC_MODULE_CENTRIC_ARCHITECTURE_OVERVIEW.md
  # ... more items
tags:
  - type:guide
  - module:module-centric
```

### Step 3: Run Batch Mint

```bash
python batch_mint.py
```

This generates a new delta file like:
- `doc_id/deltas/delta_batch_mint_20251130_XXXXXX.jsonl`

### Step 4: Merge Deltas

```bash
python merge_deltas.py doc_id/deltas/delta_batch_mint_20251130_XXXXXX.jsonl
```

This updates the registry and increments counters.

### Step 5: Write IDs to Files

```bash
python write_doc_ids_to_files.py
```

This adds the `doc_id` field to each file's front matter.

### Step 6: Commit

```bash
git add -A
git commit -m "feat(doc_id): Assign IDs to module-centric documentation (32 files)"
```

---

## Automated Batch Script

You can automate the entire process for a specific category:

**Example**: `assign_ids_to_module_docs.sh`
```bash
#!/bin/bash

# 1. Rename files (if needed)
for file in docs/MODULE_CENTRIC_*.md; do
  new_name=$(echo "$file" | sed 's|docs/MODULE_CENTRIC_|docs/DOC_MODULE_CENTRIC_|')
  if [ "$file" != "$new_name" ]; then
    mv "$file" "$new_name"
    echo "Renamed: $file -> $new_name"
  fi
done

# 2. Add front matter (if missing)
for file in docs/DOC_MODULE_CENTRIC_*.md; do
  if ! head -n 1 "$file" | grep -q "^---"; then
    cat << EOF > "$file.tmp"
---
status: draft
doc_type: guide
---

$(cat "$file")
EOF
    mv "$file.tmp" "$file"
    echo "Added front matter: $file"
  fi
done

# 3. Run batch mint
python batch_mint.py

# 4. Merge latest delta
latest_delta=$(ls -t doc_id/deltas/delta_*.jsonl | head -1)
python merge_deltas.py "$latest_delta"

# 5. Write to files
python write_doc_ids_to_files.py

# 6. Commit
git add -A
git commit -m "feat(doc_id): Batch assign IDs to module-centric docs"

echo "✅ Complete"
```

---

## Priority Order for Remaining Files

### High Priority (Assign Next)
1. **Module-centric docs** (docs/MODULE_CENTRIC_*.md) - ~5 files
2. **UET pattern docs** (UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/docs/*.md) - ~15 files
3. **Workstream plans** (workstreams/plans/**/*.md) - ~30 files

### Medium Priority
4. **Remaining docs/** files - ~40 files
5. **Module-local docs** (modules/**/DOC_*.md) - ~20 files

### Low Priority (Maybe Never)
6. **README.md files** - Navigation only, not canonical docs
7. **_DEV_* files** - Scratch notes, intentionally excluded
8. **Legacy/archive** - Historical, no IDs needed

---

## Example: Assigning IDs to UET Pattern Docs

### 1. Create Batch Spec

`doc_id/batches/batch_uet_patterns.yaml`:
```yaml
batch_id: DOCID-BATCH-UET-PATTERNS-001
description: Assign doc_ids to UET pattern documentation
category: patterns
items:
  - logical_name: IMPLEMENTATION_STATUS
    title: "UET Implementation Status"
    artifacts:
      - path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/docs/IMPLEMENTATION_STATUS.md
  - logical_name: IMPLEMENTATION_COMPLETE_SUMMARY
    title: "UET Implementation Complete Summary"
    artifacts:
      - path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/docs/IMPLEMENTATION_COMPLETE_SUMMARY.md
  - logical_name: PATTERN_AUTOMATION_MASTER_PLAN
    title: "Pattern Automation Master Plan"
    artifacts:
      - path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/docs/PATTERN_AUTOMATION_MASTER_PLAN.md
  # ... etc
tags:
  - type:pattern
  - category:uet
```

### 2. Run the Workflow

```bash
# Mint IDs
python batch_mint.py

# Merge (latest delta auto-selected)
python merge_deltas.py doc_id/deltas/delta_batch_mint_*.jsonl

# Update files
python write_doc_ids_to_files.py

# Commit
git add -A && git commit -m "feat(doc_id): Assign IDs to UET pattern docs (15 files)"
```

---

## One-Command Approach (Future Enhancement)

You could create a single command that does everything:

```bash
python scripts/batch_assign_ids.py --category patterns --pattern "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/docs/*.md"
```

This would:
1. Scan for matching files
2. Generate batch spec
3. Mint IDs
4. Merge deltas
5. Update files
6. Optionally commit

**Script**: `scripts/batch_assign_ids.py` (to be created)

---

## FAQ

### Q: Do I have to assign IDs to everything?
**A**: No. Only files that are:
- Canonical documentation (not scratch notes)
- In governed locations (docs/, adr/, modules/)
- Following naming conventions (DOC_*, PLAN_*)

### Q: What about files that are moved/renamed frequently?
**A**: The doc_id stays with the content, not the filename. When you move/rename:
1. Keep the doc_id in front matter
2. Update the `artifacts.path` in the registry
3. The doc_id remains the same

### Q: Can I assign IDs incrementally?
**A**: Yes! That's the whole point of the batch system. You can:
- Do 10 files today
- 20 files next week  
- 30 files next month

Each batch is independent.

### Q: What if I forget to add front matter first?
**A**: The `write_doc_ids_to_files.py` script will skip files without front matter. Just add it and re-run.

---

## Summary

**Remaining documents get IDs the same way Phase 3 docs did:**

1. ✅ Clean up (rename/move if needed)
2. ✅ Add front matter (if missing)
3. ✅ Create batch spec
4. ✅ Run `batch_mint.py`
5. ✅ Run `merge_deltas.py <delta_file>`
6. ✅ Run `write_doc_ids_to_files.py`
7. ✅ Commit

**You can process them in batches of any size, at any pace.**

The tools are ready. The workflow is proven. Just repeat the process for each category of documents you want to assign IDs to.

---

**Next Recommended Batch**: Module-centric docs (5 files, quick win)
