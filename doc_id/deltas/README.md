# Deltas Directory

**Purpose**: Incremental registry updates and delta records  
**Last Updated**: 2025-11-29

---

## Overview

This directory contains **delta files** that record incremental changes to the Doc ID registry. Deltas track:

- New IDs minted
- IDs retired
- IDs superseded
- Lifecycle changes

Deltas enable:
- **Incremental updates** without full re-scan
- **Audit trail** of registry changes
- **Rollback capability** if needed
- **Merge coordination** in parallel workflows

---

## Delta File Format

### YAML Structure

```yaml
delta:
  id: "DELTA-001"
  timestamp: "2025-11-29T10:00:00Z"
  author: "username"
  description: "What changed"
  
operations:
  - action: mint
    doc_id: "DOC-CORE-NEW-001"
    category: CORE
    name: NEW
    sequence: 1
    file_path: "core/new.py"
  
  - action: retire
    doc_id: "DOC-CORE-OLD-001"
    reason: "Functionality removed"
    retired_at: "2025-11-29T10:00:00Z"
  
  - action: supersede
    doc_id: "DOC-CORE-OLD-002"
    superseded_by: "DOC-CORE-NEW-003"
    reason: "Merged into new module"
```

---

## Delta Types

### 1. Mint Delta

**Purpose**: Record newly minted IDs

```yaml
delta:
  id: "DELTA-MINT-20251129-001"
  timestamp: "2025-11-29T10:00:00Z"
  
operations:
  - action: mint
    doc_id: "DOC-CORE-ORCHESTRATOR-001"
    category: CORE
    name: ORCHESTRATOR
    sequence: 1
    file_path: "core/orchestrator.py"
```

---

### 2. Retire Delta

**Purpose**: Record retired IDs

```yaml
delta:
  id: "DELTA-RETIRE-20251129-001"
  timestamp: "2025-11-29T10:00:00Z"
  
operations:
  - action: retire
    doc_id: "DOC-CORE-DEPRECATED-001"
    reason: "File deleted, functionality moved to new module"
    retired_at: "2025-11-29T10:00:00Z"
    last_known_path: "core/deprecated/old.py"
```

---

### 3. Supersede Delta

**Purpose**: Record ID supersession (merge/refactor)

```yaml
delta:
  id: "DELTA-SUPERSEDE-20251129-001"
  timestamp: "2025-11-29T10:00:00Z"
  
operations:
  - action: supersede
    doc_id: "DOC-CORE-OLD-001"
    superseded_by: "DOC-CORE-NEW-002"
    reason: "Files merged during refactor"
```

---

### 4. Move Delta

**Purpose**: Record file moves (ID unchanged)

```yaml
delta:
  id: "DELTA-MOVE-20251129-001"
  timestamp: "2025-11-29T10:00:00Z"
  
operations:
  - action: move
    doc_id: "DOC-CORE-STATE-001"
    old_path: "core/state/db.py"
    new_path: "modules/mod-core-state/db.py"
    moved_at: "2025-11-29T10:00:00Z"
```

---

## Usage

### 1. Generate Delta (Manual)

```bash
# Create delta file
cat > delta_new_modules.yaml << 'EOF'
delta:
  id: "DELTA-NEW-MODULES-20251129"
  timestamp: "2025-11-29T10:00:00Z"
  author: "developer"
  description: "Added new core modules"
  
operations:
  - action: mint
    doc_id: "DOC-CORE-ORCHESTRATOR-001"
    category: CORE
    name: ORCHESTRATOR
    sequence: 1
    file_path: "core/orchestrator.py"
EOF
```

---

### 2. Apply Delta

```bash
# Apply delta to registry
cd ../tools
python doc_id_registry_cli.py apply-delta --file ../deltas/delta_new_modules.yaml

# Output:
# ✅ Applied delta: DELTA-NEW-MODULES-20251129
# ✅ 1 operation applied
```

---

### 3. Generate Delta (Automatic)

```bash
# Scanner can generate deltas automatically
cd ../tools
python doc_id_scanner.py scan --generate-delta

# Generates: ../deltas/delta_scan_<timestamp>.yaml
```

---

## Delta Naming Convention

### Filename Pattern

```
delta_<action>_<date>_<seq>.yaml
```

**Examples**:
- `delta_mint_20251129_001.yaml`
- `delta_retire_20251129_002.yaml`
- `delta_move_20251129_003.yaml`
- `delta_scan_20251129T100000.yaml` (auto-generated)

---

## Workflow: Incremental Updates

### Standard Workflow

```bash
# 1. Make changes to files (move, delete, create)

# 2. Scan and generate delta
cd ../tools
python doc_id_scanner.py scan --generate-delta

# 3. Review delta
cat ../deltas/delta_scan_<timestamp>.yaml

# 4. Apply delta
python doc_id_registry_cli.py apply-delta \
  --file ../deltas/delta_scan_<timestamp>.yaml

# 5. Validate
python doc_id_scanner.py validate
```

---

### Parallel Workflow

```bash
# In worktree agent-1:
python doc_id_scanner.py scan --generate-delta \
  --output ../deltas/delta_agent1_<timestamp>.yaml

# In worktree agent-2:
python doc_id_scanner.py scan --generate-delta \
  --output ../deltas/delta_agent2_<timestamp>.yaml

# In main branch (after merge):
python doc_id_registry_cli.py merge-deltas \
  --files ../deltas/delta_agent1_*.yaml \
          ../deltas/delta_agent2_*.yaml \
  --output ../deltas/delta_merged_<timestamp>.yaml

# Apply merged delta
python doc_id_registry_cli.py apply-delta \
  --file ../deltas/delta_merged_<timestamp>.yaml
```

---

## Delta Merge Strategies

### 1. Sequential Merge

Apply deltas in order:

```bash
for delta in deltas/delta_*.yaml; do
  python doc_id_registry_cli.py apply-delta --file "$delta"
done
```

---

### 2. Conflict Detection

Before merging:

```bash
# Check for conflicts
python doc_id_registry_cli.py check-delta-conflicts \
  --files deltas/delta_1.yaml deltas/delta_2.yaml

# If conflicts:
# - Review conflict report
# - Manually resolve
# - Create resolved delta
```

---

### 3. Dry Run

Test delta before applying:

```bash
python doc_id_registry_cli.py apply-delta \
  --file deltas/delta_new.yaml \
  --dry-run

# Output: Shows what would change, doesn't modify registry
```

---

## Audit Trail

### Query Delta History

```bash
# List all deltas
ls -l deltas/

# Find deltas for specific doc ID
grep -r "DOC-CORE-STATE-001" deltas/

# View delta timeline
cat deltas/delta_*.yaml | \
  grep "timestamp:" | \
  sort
```

---

### Delta Log

Track applied deltas:

```bash
# Create/update delta log
cat > deltas/DELTAS_APPLIED.md << 'EOF'
# Delta Application Log

| Delta ID | Timestamp | Operations | Status |
|----------|-----------|------------|--------|
| DELTA-001 | 2025-11-29T10:00:00Z | 5 mint | ✅ Applied |
| DELTA-002 | 2025-11-29T11:00:00Z | 2 retire | ✅ Applied |

EOF
```

---

## Rollback

### Rollback Last Delta

```bash
# Backup registry
cp ../specs/DOC_ID_REGISTRY.yaml \
   ../specs/DOC_ID_REGISTRY.backup.yaml

# Rollback delta
python doc_id_registry_cli.py rollback-delta \
  --delta-id "DELTA-001"

# Or restore from backup
cp ../specs/DOC_ID_REGISTRY.backup.yaml \
   ../specs/DOC_ID_REGISTRY.yaml
```

---

## Best Practices

### DO ✅

- **Generate deltas automatically** when possible
- **Review before applying** (use --dry-run)
- **Keep deltas small** (one logical change)
- **Name descriptively** (action + date + seq)
- **Log applied deltas** for audit trail

### DON'T ❌

- **Don't manually edit applied deltas**
- **Don't skip validation** after applying
- **Don't apply same delta twice**
- **Don't delete deltas** (archive instead)

---

## Archive Policy

### After Application

```bash
# 1. Verify delta applied successfully
python doc_id_scanner.py validate

# 2. Move to archive
mkdir -p archive/2025-11
mv delta_applied_*.yaml archive/2025-11/

# 3. Update log
echo "delta_applied_*.yaml - $(date)" >> DELTAS_APPLIED.md
```

---

### Retention

- **Keep**: Last 90 days in main directory
- **Archive**: Older than 90 days → `archive/YYYY-MM/`
- **Purge**: Archived >1 year (or per policy)

---

## Integration with Tools

### Scanner Integration

```bash
# Scanner can auto-generate deltas
python doc_id_scanner.py scan --generate-delta

# Generates:
# - deltas/delta_scan_<timestamp>.yaml
```

---

### Registry CLI Integration

```bash
# Apply delta
python doc_id_registry_cli.py apply-delta --file delta.yaml

# Merge deltas
python doc_id_registry_cli.py merge-deltas --files *.yaml

# Rollback delta
python doc_id_registry_cli.py rollback-delta --delta-id DELTA-001
```

---

## Template

```yaml
delta:
  id: "DELTA-<ACTION>-<YYYYMMDD>-<SEQ>"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  author: "username"
  description: "What this delta does"
  
operations:
  # Mint operation
  - action: mint
    doc_id: "DOC-CATEGORY-NAME-###"
    category: CATEGORY
    name: NAME
    sequence: ###
    file_path: "path/to/file.ext"
  
  # Retire operation
  # - action: retire
  #   doc_id: "DOC-CATEGORY-OLD-###"
  #   reason: "Why retired"
  #   retired_at: "YYYY-MM-DDTHH:MM:SSZ"
  
  # Supersede operation
  # - action: supersede
  #   doc_id: "DOC-CATEGORY-OLD-###"
  #   superseded_by: "DOC-CATEGORY-NEW-###"
  #   reason: "Why superseded"
  
  # Move operation
  # - action: move
  #   doc_id: "DOC-CATEGORY-NAME-###"
  #   old_path: "old/path"
  #   new_path: "new/path"
  #   moved_at: "YYYY-MM-DDTHH:MM:SSZ"
```

---

## Related Documentation

- `../tools/README.md` - Delta application tools
- `../specs/DOC_ID_FRAMEWORK.md` - Lifecycle rules
- `../plans/DOC_ID_PARALLEL_EXECUTION_GUIDE.md` - Parallel delta merging

---

**Purpose**: Incremental registry updates  
**Apply**: `python ../tools/doc_id_registry_cli.py apply-delta --file <delta>.yaml`  
**Track**: Maintain `DELTAS_APPLIED.md` log
