# Batches Directory

**Purpose**: Batch ID assignment files  
**Last Updated**: 2025-11-29

---

## Overview

This directory contains **batch assignment files** for minting multiple doc IDs at once. Batches are used for:

- Initial ID assignment to existing files
- Bulk assignment for new modules
- Organized ID allocation
- Coordinated parallel execution

---

## Batch File Format

### YAML Structure

```yaml
batch:
  name: "Descriptive batch name"
  date: "2025-11-29"
  author: "username"
  description: "What this batch does"

ids:
  - category: CORE
    name: MODULE-NAME
    file_path: "core/module_name.py"
    notes: "Optional notes"
  
  - category: ERROR
    name: PLUGIN-RUFF
    file_path: "error/plugins/ruff.py"
```

---

## Usage

### 1. Create Batch File

```bash
# Create new batch file
cat > batch_new_modules.yaml << 'EOF'
batch:
  name: "New core modules"
  date: "2025-11-29"
  author: "developer"

ids:
  - category: CORE
    name: ORCHESTRATOR
    file_path: "core/orchestrator.py"
  
  - category: CORE
    name: SCHEDULER
    file_path: "core/scheduler.py"
  
  - category: CORE
    name: EXECUTOR
    file_path: "core/executor.py"
EOF
```

---

### 2. Apply Batch

```bash
# Run batch mint
cd ../tools
python doc_id_registry_cli.py batch --file ../batches/batch_new_modules.yaml

# Output:
# ✅ Minted: DOC-CORE-ORCHESTRATOR-001
# ✅ Minted: DOC-CORE-SCHEDULER-002
# ✅ Minted: DOC-CORE-EXECUTOR-003
# 
# 3 IDs minted successfully
```

---

### 3. Update Files

After minting, update files with their doc IDs:

**For Python files**:
```python
# doc_id: DOC-CORE-ORCHESTRATOR-001

"""Orchestrator module."""
```

**For Markdown files**:
```markdown
---
doc_id: "DOC-CORE-ORCHESTRATOR-001"
---

# Orchestrator
```

---

### 4. Validate

```bash
cd ../tools
python doc_id_scanner.py scan
python doc_id_scanner.py validate
```

---

## Batch Naming Convention

### Filename Pattern

```
batch_<purpose>_<date>.yaml
```

**Examples**:
- `batch_core_modules_20251129.yaml`
- `batch_error_plugins_20251129.yaml`
- `batch_missing_ids_20251129.yaml`

---

## Common Batch Types

### 1. Module Batch

**Purpose**: Assign IDs to all files in a module

```yaml
batch:
  name: "Error detection module"
  date: "2025-11-29"

ids:
  - category: ERROR
    name: ENGINE
    file_path: "error/engine.py"
  
  - category: ERROR
    name: DETECTOR
    file_path: "error/detector.py"
  
  - category: ERROR
    name: REPORTER
    file_path: "error/reporter.py"
```

---

### 2. Category Batch

**Purpose**: Assign IDs across multiple modules in same category

```yaml
batch:
  name: "All SPEC files"
  date: "2025-11-29"

ids:
  - category: SPEC
    name: SCHEMA
    file_path: "specifications/schema.yaml"
  
  - category: SPEC
    name: CONTRACT
    file_path: "specifications/contract.yaml"
```

---

### 3. Missing IDs Batch

**Purpose**: Assign IDs to files found without them

```bash
# 1. Find missing
cd ../tools
python doc_id_scanner.py find-missing > missing_list.txt

# 2. Create batch from missing list
# (manual or scripted)

# 3. Apply batch
python doc_id_registry_cli.py batch --file ../batches/batch_missing.yaml
```

---

## Batch Best Practices

### DO ✅

- **Group related files** in same batch
- **Use descriptive names** for batch and IDs
- **Date your batches** for tracking
- **Validate after applying** batch
- **Keep batches small** (10-50 IDs per batch)

### DON'T ❌

- **Don't reuse batch files** after applying
- **Don't manually edit IDs** after minting
- **Don't skip validation** after batch
- **Don't create huge batches** (>100 IDs)

---

## Parallel Batch Execution

### Strategy

For large-scale ID assignment:

```bash
# 1. Split into multiple batch files
batch_core_001.yaml     # CORE modules
batch_error_001.yaml    # ERROR modules
batch_spec_001.yaml     # SPEC modules

# 2. Apply sequentially (registry is shared)
python doc_id_registry_cli.py batch --file batch_core_001.yaml
python doc_id_registry_cli.py batch --file batch_error_001.yaml
python doc_id_registry_cli.py batch --file batch_spec_001.yaml

# 3. Or use parallel script (if available)
../tools/parallel_batch_apply.ps1
```

**See**: `../plans/DOC_ID_PARALLEL_EXECUTION_GUIDE.md`

---

## Batch Tracking

### Active Batches

Track which batches have been applied:

```bash
# Create tracking file
cat > BATCHES_APPLIED.md << 'EOF'
# Batches Applied

| Batch File | Date Applied | IDs Minted | Status |
|------------|--------------|------------|--------|
| batch_core_001.yaml | 2025-11-29 | 15 | ✅ Complete |
| batch_error_001.yaml | 2025-11-29 | 8 | ✅ Complete |

EOF
```

---

## Archive Policy

### After Application

1. **Verify success**:
   ```bash
   python doc_id_scanner.py validate
   ```

2. **Move to archive** (optional):
   ```bash
   mkdir -p archive/2025-11
   mv batch_applied.yaml archive/2025-11/
   ```

3. **Update tracking**:
   ```bash
   echo "batch_applied.yaml - $(date)" >> BATCHES_APPLIED.md
   ```

---

## Template

Copy this template for new batches:

```yaml
batch:
  name: "CHANGE_ME: Descriptive name"
  date: "YYYY-MM-DD"
  author: "your_username"
  description: "What this batch assigns IDs to"
  
ids:
  # Example entry (delete this)
  - category: CATEGORY_NAME  # CORE, ERROR, SPEC, etc.
    name: MODULE-NAME        # Descriptive name in UPPERCASE-KEBAB
    file_path: "path/to/file.ext"
    notes: "Optional notes about this file"
  
  # Add more entries here
  # - category: ...
  #   name: ...
  #   file_path: "..."
```

Save as: `batch_<purpose>_$(date +%Y%m%d).yaml`

---

## Troubleshooting

### Batch Fails to Apply

```bash
# Error: Invalid YAML
python -c "import yaml; yaml.safe_load(open('batch_file.yaml'))"

# Error: Duplicate category/name
# Check ../specs/DOC_ID_REGISTRY.yaml for existing IDs

# Error: File path doesn't exist
# Verify paths are relative to repository root
```

---

### Partial Batch Application

```bash
# If batch partially applies before error:
# 1. Check registry for what was minted
cat ../specs/DOC_ID_REGISTRY.yaml | grep "DOC-CATEGORY-NAME"

# 2. Create new batch with remaining items

# 3. Apply remainder
python doc_id_registry_cli.py batch --file batch_remainder.yaml
```

---

## Related Documentation

- `../tools/README.md` - Tool usage for batch command
- `../specs/DOC_ID_FRAMEWORK.md` - ID format and categories
- `../plans/DOC_ID_PARALLEL_EXECUTION_GUIDE.md` - Parallel execution

---

**Template**: See above  
**Apply**: `python ../tools/doc_id_registry_cli.py batch --file <batch_file>.yaml`  
**Validate**: `python ../tools/doc_id_scanner.py validate`
