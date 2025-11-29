# Tools Directory

**Purpose**: CLI tools, scripts, and utilities for Doc ID framework  
**Last Updated**: 2025-11-29

---

## Overview

This directory contains the **operational tools** for the Doc ID framework:

- Registry management CLI
- Document scanner
- Validation scripts
- Test suites

---

## Tools

### 1. Registry CLI (`doc_id_registry_cli.py`)

**Purpose**: Manage the Doc ID registry  
**Language**: Python 3.8+  
**Single Source of Truth**: Operates on `../specs/DOC_ID_REGISTRY.yaml`

#### Commands

```bash
# Mint new doc ID
python doc_id_registry_cli.py mint \
  --category CORE \
  --name MY-MODULE \
  --file-path "path/to/file.py"

# Mint batch from YAML file
python doc_id_registry_cli.py batch \
  --file ../batches/batch_001.yaml

# List all IDs
python doc_id_registry_cli.py list

# List IDs by category
python doc_id_registry_cli.py list --category CORE

# Validate registry
python doc_id_registry_cli.py validate

# Mark ID as retired
python doc_id_registry_cli.py retire \
  --doc-id DOC-CORE-OLD-001 \
  --reason "Functionality removed"

# Mark ID as superseded
python doc_id_registry_cli.py supersede \
  --doc-id DOC-CORE-OLD-002 \
  --superseded-by DOC-CORE-NEW-003 \
  --reason "Merged into new module"
```

#### Key Features

- ✅ Ensures unique ID assignment
- ✅ Validates ID format
- ✅ Tracks lifecycle (active, retired, superseded)
- ✅ Generates next sequence number
- ✅ Batch operations support
- ✅ Rollback on errors

---

### 2. Scanner (`doc_id_scanner.py`)

**Purpose**: Scan repository for doc IDs and assign to files  
**Language**: Python 3.8+  
**Output**: `../reports/docs_inventory.jsonl`

#### Commands

```bash
# Full scan
python doc_id_scanner.py scan

# Scan with verbose output
python doc_id_scanner.py scan --verbose

# Generate statistics
python doc_id_scanner.py stats

# Generate coverage report
python doc_id_scanner.py report

# Validate consistency
python doc_id_scanner.py validate

# Find files without IDs
python doc_id_scanner.py find-missing
```

#### Scan Process

1. **Scan eligible files**:
   - `.md`, `.py`, `.txt`, `.yaml`, etc.
   - Excludes: `.worktrees/`, `.state/`, `.git/`, etc.

2. **Extract doc IDs**:
   - From YAML frontmatter (markdown)
   - From top comments (code files)
   - From sidecar `.meta.json` (binary files)

3. **Build inventory**:
   - Write to `../reports/docs_inventory.jsonl`
   - One JSON object per line

4. **Generate report**:
   - Coverage statistics
   - Missing IDs
   - Conflicts (if any)

#### Exclusion Patterns

```python
EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".worktrees",     # Multi-agent worktrees
    "legacy",
    ".state",
    "refactor_paths.db",
    "*.db-shm",
    "*.db-wal",
]
```

**See**: `../analysis/README.md` for why `.worktrees` excluded

---

### 3. Validation Script (`validate_doc_id_consistency.ps1`)

**Purpose**: PowerShell script for consistency validation  
**Language**: PowerShell 5.1+

#### Usage

```powershell
# Run full validation
.\validate_doc_id_consistency.ps1

# Quick check only
.\validate_doc_id_consistency.ps1 -Quick

# Verbose output
.\validate_doc_id_consistency.ps1 -Verbose
```

#### Validation Checks

- ✅ Registry YAML syntax valid
- ✅ Inventory JSONL format valid
- ✅ No duplicate doc IDs
- ✅ No orphaned IDs (in inventory but not registry)
- ✅ Format compliance
- ✅ File paths exist

---

### 4. Compliance Test (`test_doc_id_compliance.py`)

**Purpose**: Automated test suite for Doc ID framework  
**Language**: Python 3.8+ with pytest

#### Usage

```bash
# Run all tests
pytest test_doc_id_compliance.py -v

# Run specific test class
pytest test_doc_id_compliance.py::TestIDFormat -v

# Run with coverage
pytest test_doc_id_compliance.py --cov=. --cov-report=html
```

#### Test Coverage

```python
class TestIDFormat:
    def test_valid_format()
    def test_invalid_format()
    def test_category_validation()

class TestRegistry:
    def test_mint_unique_id()
    def test_duplicate_prevention()
    def test_sequence_generation()

class TestScanner:
    def test_scan_files()
    def test_extract_from_frontmatter()
    def test_extract_from_comments()
    def test_exclusion_patterns()

class TestLifecycle:
    def test_retire_id()
    def test_supersede_id()
    def test_split_file()
```

---

### 5. Worktree Manager (`create_docid_worktrees.ps1`)

**Purpose**: Create worktrees for parallel ID assignment  
**Language**: PowerShell 5.1+

#### Usage

```powershell
# Create worktrees for batch assignment
.\create_docid_worktrees.ps1 -BatchFile ..\batches\batch_001.yaml
```

**See**: `../plans/DOC_ID_PARALLEL_EXECUTION_GUIDE.md`

---

## Common Workflows

### Workflow 1: Mint and Assign Single ID

```bash
# 1. Mint ID
python doc_id_registry_cli.py mint \
  --category CORE \
  --name NEW-MODULE \
  --file-path "core/new_module.py"

# Output: DOC-CORE-NEW-MODULE-001

# 2. Add to file header
echo "# doc_id: DOC-CORE-NEW-MODULE-001" | \
  cat - core/new_module.py > temp && \
  mv temp core/new_module.py

# 3. Update inventory
python doc_id_scanner.py scan

# 4. Validate
python doc_id_scanner.py validate
```

---

### Workflow 2: Batch Assignment

```bash
# 1. Create batch file
cat > ../batches/batch_new.yaml << EOF
batch:
  name: "New modules batch"
  date: "2025-11-29"

ids:
  - category: CORE
    name: MODULE-A
    file_path: "core/module_a.py"
  
  - category: CORE
    name: MODULE-B
    file_path: "core/module_b.py"
EOF

# 2. Apply batch
python doc_id_registry_cli.py batch --file ../batches/batch_new.yaml

# 3. Update files (manual or script)

# 4. Scan and validate
python doc_id_scanner.py scan
python doc_id_scanner.py validate
```

---

### Workflow 3: Coverage Check

```bash
# 1. Scan repository
python doc_id_scanner.py scan

# 2. Generate stats
python doc_id_scanner.py stats

# Example output:
# Total files: 1,234
# Files with doc_id: 1,150
# Coverage: 93.2%
# Missing: 84 files

# 3. Find missing
python doc_id_scanner.py find-missing > missing_ids.txt

# 4. Review and assign
cat missing_ids.txt

# 5. Create batch for missing files
# (edit batch_missing.yaml)

# 6. Apply batch
python doc_id_registry_cli.py batch --file ../batches/batch_missing.yaml
```

---

### Workflow 4: Pre-Refactor Validation

```bash
# 1. Full scan
python doc_id_scanner.py scan --verbose

# 2. Check coverage (must be 100% for refactor)
python doc_id_scanner.py stats

# 3. Validate consistency
powershell validate_doc_id_consistency.ps1

# 4. Run tests
pytest test_doc_id_compliance.py -v

# 5. Generate preflight report
python doc_id_scanner.py report > ../reports/preflight_$(date +%Y%m%d).md

# All checks pass? → Proceed with refactor
```

---

## Dependencies

### Python Requirements

```python
# Standard library only - no external packages
import yaml          # PyYAML (if not in stdlib)
import json
import re
import pathlib
import argparse
import datetime
```

### PowerShell Requirements

- PowerShell 5.1+
- No external modules required

---

## Configuration

### Scanner Configuration

Edit `doc_id_scanner.py` to modify:

```python
# File patterns to scan
SCAN_PATTERNS = [
    "**/*.md",
    "**/*.py",
    "**/*.txt",
    "**/*.yaml",
]

# Exclusion patterns (DO NOT remove .worktrees)
EXCLUDE_PATTERNS = [
    ".worktrees",  # ← CRITICAL - prevents race conditions
    ".state",
    ".git",
    # ... add more as needed
]
```

**WARNING**: Do not remove `.worktrees` from exclusions. See `../analysis/README.md` for why.

---

## Troubleshooting

### Issue: Duplicate IDs

```bash
# 1. Detect
python doc_id_scanner.py validate

# 2. Review conflicts
cat ../reports/id_conflicts_*.md

# 3. Resolve manually
# - Decide which file keeps ID
# - Mint new ID for other file
# - Update registry

# 4. Re-validate
python doc_id_scanner.py validate
```

### Issue: Registry Corruption

```bash
# 1. Backup
cp ../specs/DOC_ID_REGISTRY.yaml ../specs/DOC_ID_REGISTRY.backup.yaml

# 2. Validate YAML
python -c "import yaml; yaml.safe_load(open('../specs/DOC_ID_REGISTRY.yaml'))"

# 3. If invalid, restore from backup
cp ../specs/DOC_ID_REGISTRY.backup.yaml ../specs/DOC_ID_REGISTRY.yaml

# 4. Or rebuild from inventory (use with caution)
python doc_id_registry_cli.py rebuild-from-inventory
```

### Issue: Scanner Not Finding Files

```bash
# 1. Check exclusions
python doc_id_scanner.py scan --verbose 2>&1 | grep "Excluding"

# 2. Verify file patterns
python doc_id_scanner.py scan --verbose 2>&1 | grep "Scanning"

# 3. Test on single file
python doc_id_scanner.py scan --file "path/to/file.py"
```

---

## Development

### Adding New Tool

1. Create `new_tool.py` in this directory
2. Follow existing patterns:
   - Argparse for CLI
   - YAML for config
   - JSONL for data
3. Add tests to `test_doc_id_compliance.py`
4. Update this README

### Modifying Existing Tool

1. Edit tool file
2. Update tests
3. Run test suite: `pytest -v`
4. Update README if CLI changed
5. Commit with descriptive message

---

## Related Documentation

- `../specs/DOC_ID_FRAMEWORK.md` - Framework specification
- `../plans/DOC_ID_PARALLEL_EXECUTION_GUIDE.md` - Parallel execution
- `../analysis/CONFLICT_ANALYSIS_AND_RESOLUTION.md` - Conflict handling

---

**Primary Tools**: `doc_id_registry_cli.py`, `doc_id_scanner.py`  
**Test Before Use**: `pytest test_doc_id_compliance.py`  
**Backup Before Operations**: Always backup registry before major changes
