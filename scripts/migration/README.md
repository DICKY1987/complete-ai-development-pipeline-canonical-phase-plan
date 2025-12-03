---
doc_id: DOC-SCRIPT-README-339
---

# UET Consolidation Migration Scripts

**Purpose**: Consolidate 67% duplicate code into UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

**Execution Patterns**: EXEC-012, EXEC-013

---

## Scripts

### Phase 0: Discovery
- **`scan_duplicates.py`** - Find duplicate files by content hash
  - Pattern: EXEC-012 Phase 1
  - Output: `.migration/duplicate_registry.yaml`
  - Duration: ~90 minutes

### Phase 1: Analysis
- **`analyze_dependencies.py`** - Map Python import dependencies
  - Pattern: EXEC-013
  - Output: `.migration/dependency_report.json`
  - Duration: ~1 hour

### Phase 2: Planning
- **`create_migration_plan.py`** - Generate ordered migration batches
  - Pattern: EXEC-012 Phase 2
  - Output: `.migration/migration_plan.yaml`
  - Duration: ~1 hour

---

## Quick Start

```bash
# Execute all phases sequentially
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

# Phase 0: Scan for duplicates
python scripts/migration/scan_duplicates.py

# Phase 1: Analyze dependencies
python scripts/migration/analyze_dependencies.py

# Phase 2: Create migration plan
python scripts/migration/create_migration_plan.py

# Review outputs
cat .migration/duplicate_registry.yaml
cat .migration/dependency_report.json
cat .migration/migration_plan.yaml
```

---

## Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install pyyaml

# Ensure clean git state
git status
```

---

## Ground Truth Verification

```bash
# Verify duplicate registry created
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml && echo "✅ PASS" || echo "❌ FAIL"

# Verify dependency report created
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json && echo "✅ PASS" || echo "❌ FAIL"

# Verify migration plan created
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml && echo "✅ PASS" || echo "❌ FAIL"
```

---

## Output Structure

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
└── .migration/
    ├── README.md
    ├── duplicate_registry.yaml    # Hash-based duplicate detection
    ├── dependency_report.json     # Import dependency graph
    ├── migration_plan.yaml        # Ordered migration batches
    ├── migration_log.yaml         # Execution log (created during migration)
    └── backups/                   # Pre-migration backups
```

---

## Next Steps

After running these scripts:

1. Review the migration plan
2. Check for circular dependencies
3. Execute migration batches (Phase 3-4)
4. Run verification suite (Phase 5)
5. Archive old structure (Phase 6)

See: `../UET_CONSOLIDATION_MASTER_PLAN.md` for full details.

---

**Created**: 2025-11-29  
**Status**: Ready for execution  
**Pattern**: EXEC-012 + EXEC-013
