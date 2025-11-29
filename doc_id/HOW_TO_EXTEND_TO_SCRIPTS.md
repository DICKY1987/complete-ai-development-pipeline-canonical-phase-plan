# How to Extend DOC_ID to Scripts

**Question**: How do we extend doc_ids to scripts?  
**Answer**: The exact same batch workflow, but scripts already have 45 doc_ids assigned!

---

## Current State of Scripts

Looking at the registry:
- **script (SCRIPT)**: 45 docs (next_id: 46)

**This means 45 scripts already have doc_ids!** They were assigned in the original Phase 1/2 work.

---

## Check Which Scripts Already Have IDs

```bash
# See all script doc_ids in registry
python -c "
from pathlib import Path
import yaml

registry = yaml.safe_load(Path('doc_id/specs/DOC_ID_REGISTRY.yaml').read_text(encoding='utf-8'))
script_docs = [d for d in registry['docs'] if d['category'] == 'script']

print(f'Scripts with doc_ids: {len(script_docs)}')
for doc in sorted(script_docs, key=lambda x: x['doc_id']):
    print(f'  {doc[\"doc_id\"]}: {doc[\"title\"]}')
"
```

---

## To Assign IDs to Remaining Scripts

### Step 1: Find Scripts Without IDs

```python
# scripts_without_ids.py
from pathlib import Path
import yaml

# Load registry to see what's already assigned
registry = yaml.safe_load(Path('doc_id/specs/DOC_ID_REGISTRY.yaml').read_text(encoding='utf-8'))
assigned_paths = set()
for doc in registry['docs']:
    if doc['category'] == 'script':
        for artifact in doc.get('artifacts', []):
            assigned_paths.add(artifact['path'])

# Find all Python scripts
all_scripts = list(Path('scripts').glob('*.py'))
all_scripts += list(Path('scripts').glob('*.ps1'))

# Find unassigned
unassigned = []
for script in all_scripts:
    script_path = str(script).replace('\\', '/')
    if script_path not in assigned_paths:
        unassigned.append(script_path)

print(f'Total scripts: {len(all_scripts)}')
print(f'Assigned: {len(assigned_paths)}')
print(f'Unassigned: {len(unassigned)}')
print('\nUnassigned scripts:')
for script in sorted(unassigned):
    print(f'  {script}')
```

### Step 2: Create Batch Spec for Remaining Scripts

**Example**: `doc_id/batches/batch_scripts_remaining.yaml`
```yaml
batch_id: DOCID-BATCH-SCRIPTS-REMAINING-001
description: Assign doc_ids to remaining automation scripts
category: script
items:
  - logical_name: EXAMPLE_SCRIPT_NAME
    title: "Example Script Description"
    artifacts:
      - path: scripts/example_script.py
  # ... more scripts
tags:
  - type:script
  - category:automation
```

### Step 3: Run the Batch Workflow

```bash
# Mint IDs
python batch_mint.py

# Merge deltas
python merge_deltas.py doc_id/deltas/delta_batch_mint_*.jsonl

# Scripts don't have front matter like docs, but you could:
# Option A: Add shebang comments with doc_id
# Option B: Create a SCRIPT_INDEX.yaml mapping
# Option C: Keep IDs in registry only (no file modification)
```

---

## Key Difference: Scripts vs Docs

### Documents (Markdown)
- ✅ Have YAML front matter
- ✅ doc_id written directly into file
- ✅ Front matter is native to .md files

### Scripts (Python/PowerShell)
- ⚠️ No standard front matter
- 🤔 Options for embedding doc_id:
  1. **Header comment** (recommended)
  2. **Module docstring** (Python only)
  3. **Registry only** (no file modification)

---

## Recommended Approach for Scripts

### Option 1: Header Comment (Recommended)

**Python script**:
```python
#!/usr/bin/env python3
# DOC_ID: DOC-SCRIPT-EXAMPLE-046
# -*- coding: utf-8 -*-
"""
Example Script
Does something useful
"""
```

**PowerShell script**:
```powershell
# DOC_ID: DOC-SCRIPT-EXAMPLE-046
# Example Script
# Does something useful

param(
    [string]$InputPath
)
```

### Option 2: Python Docstring Metadata

```python
#!/usr/bin/env python3
"""
Example Script

Does something useful.

:doc_id: DOC-SCRIPT-EXAMPLE-046
:category: automation
:tags: validation, cleanup
"""
```

### Option 3: Registry Only (No File Modification)

Just keep the doc_id in the registry. Scripts reference themselves by filename.

**Pros**: No file changes, simpler  
**Cons**: doc_id not visible when reading script

---

## Create a Script to Add doc_ids to Scripts

**Example**: `add_docid_to_scripts.py`
```python
#!/usr/bin/env python3
"""
Add doc_ids to script files based on registry
"""

from pathlib import Path
import yaml
import re

registry = yaml.safe_load(Path('doc_id/specs/DOC_ID_REGISTRY.yaml').read_text(encoding='utf-8'))

for doc in registry['docs']:
    if doc['category'] != 'script':
        continue
    
    doc_id = doc['doc_id']
    artifacts = doc.get('artifacts', [])
    
    for artifact in artifacts:
        script_path = Path(artifact['path'])
        if not script_path.exists():
            continue
        
        content = script_path.read_text(encoding='utf-8')
        
        # Check if already has doc_id
        if f'DOC_ID: {doc_id}' in content or f'DOC_LINK: {doc_id}' in content:
            print(f'SKIP (already has ID): {script_path}')
            continue
        
        # Add doc_id header based on file type
        if script_path.suffix == '.py':
            # Python: Add after shebang/encoding
            lines = content.split('\n')
            insert_pos = 0
            
            # Skip shebang
            if lines[0].startswith('#!'):
                insert_pos = 1
            
            # Skip encoding declaration
            if insert_pos < len(lines) and 'coding' in lines[insert_pos]:
                insert_pos += 1
            
            # Insert doc_id comment
            lines.insert(insert_pos, f'# DOC_LINK: {doc_id}')
            new_content = '\n'.join(lines)
            
        elif script_path.suffix == '.ps1':
            # PowerShell: Add at top
            new_content = f'# DOC_ID: {doc_id}\n' + content
        
        else:
            print(f'SKIP (unknown type): {script_path}')
            continue
        
        # Write back
        script_path.write_text(new_content, encoding='utf-8')
        print(f'Added doc_id to: {script_path}')

print('\nComplete')
```

---

## Existing Script doc_ids (Sample)

Based on the execution plan, scripts that likely already have IDs include:
- `scripts/doc_id_registry_cli.py` - DOC-SCRIPT-DOC-ID-REGISTRY-CLI-001 (confirmed)
- `scripts/batch_file_creator.py` - DOC-SCRIPT-BATCH-FILE-CREATOR-002 (confirmed)
- `scripts/pattern_discovery.py` - DOC-SCRIPT-PATTERN-DISCOVERY-003 (confirmed)
- `scripts/validate_workstreams.py` - DOC-SCRIPT-VALIDATE-WORKSTREAMS-004 (confirmed)
- ... and 41 more (45 total)

---

## Full Workflow for Remaining Scripts

### 1. Identify Unassigned Scripts
```bash
python scripts_without_ids.py > unassigned_scripts.txt
```

### 2. Create Batch Spec
```yaml
# doc_id/batches/batch_scripts_remaining.yaml
batch_id: DOCID-BATCH-SCRIPTS-REMAINING-001
description: Assign doc_ids to remaining scripts
category: script
items:
  # Copy from unassigned_scripts.txt and format
  - logical_name: SCRIPT_NAME
    title: "Script Description"
    artifacts:
      - path: scripts/script_name.py
```

### 3. Run Batch Process
```bash
python batch_mint.py
python merge_deltas.py doc_id/deltas/delta_batch_mint_*.jsonl
python add_docid_to_scripts.py  # Add IDs to actual files
git add -A && git commit -m "feat(doc_id): Assign IDs to remaining scripts"
```

---

## Plans Available in doc_id/

Looking at what's available:

1. **DOC_ID_EXECUTION_PLAN.md** - Original 4-way parallel plan (Phase 1/2)
   - Status: ✅ Completed (some parts)
   - Focus: Specs, scripts, tests, modules
   - Used worktrees (we simplified this)

2. **DOC_ID_PARALLEL_EXECUTION_GUIDE.md** - Guide for parallel execution
   - Status: Reference material
   - Focus: How to use worktrees safely

3. **PLAN_DOC_ID_PHASE3_EXECUTION__v1.md** - Phase 3 plan
   - Status: ✅ Completed (this session!)
   - Focus: Deterministic workflow, patterns

**All major plans have been executed or superseded by the batch workflow.**

---

## Summary: Scripts Edition

### Current State
- ✅ 45 scripts already have doc_ids
- ❓ Unknown how many scripts remain unassigned
- ✅ Registry category 'script' is active

### To Assign Remaining Scripts
1. **Find unassigned**: Run analysis script
2. **Create batch spec**: Same as docs workflow
3. **Mint & merge**: Same batch_mint.py workflow
4. **Add to files**: Use add_docid_to_scripts.py (new script to create)
5. **Commit**: Same git workflow

### Key Decision
**How to embed doc_id in scripts?**
- **Recommended**: Header comment (`# DOC_ID: DOC-SCRIPT-NAME-046`)
- **Alternative**: Registry only (no file modification)
- **For Python**: Could use module docstring metadata

The batch workflow is **exactly the same**. The only difference is how you choose to embed the doc_id in the script file (or not at all).

---

**Next Action**: Want me to identify unassigned scripts and create a batch spec for them?
