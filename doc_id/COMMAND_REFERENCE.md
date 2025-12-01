# DOC_ID System - Command Reference

**Quick reference for essential commands and workflows**

---

## Validation Commands

### Check Registry Health
```bash
# Validate DOC_ID_REGISTRY.yaml
python scripts/validate_registry.py

# Generate detailed report
python scripts/validate_registry.py --report validation.json
```

**Expected output**: `✓ PASS: Registry validation successful`

### Check Coverage
```bash
# Check with default 90% baseline
python scripts/validate_doc_id_coverage.py

# Custom baseline
python scripts/validate_doc_id_coverage.py --baseline 0.95

# Generate report
python scripts/validate_doc_id_coverage.py --report coverage.json
```

**Expected output**: `✓ PASS: Coverage 93.0% meets baseline 90%`

### Run Both Validations
```bash
python scripts/validate_registry.py && python scripts/validate_doc_id_coverage.py
```

---

## Coverage Tracking

### Save Snapshot
```bash
# Save current coverage snapshot
python scripts/doc_id_coverage_trend.py snapshot
```

**Use case**: Run daily/weekly to track trends

### View Trends
```bash
# Generate trend report
python scripts/doc_id_coverage_trend.py report
```

**Output includes**:
- Current coverage
- Change over time
- Milestones achieved
- Files needed for next milestone

---

## Module Management

### Preview Module Assignments
```bash
# Dry-run (don't modify registry)
python scripts/module_id_assigner.py --dry-run
```

**Outputs**:
- `doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md`
- `doc_id/reports/MODULE_ID_UNASSIGNED.jsonl`
- `doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json`

### Apply Module Assignments
```bash
# Apply changes to registry (creates backup)
python scripts/module_id_assigner.py --apply
```

**Note**: Creates automatic backup at `DOC_ID_REGISTRY.backup.yaml`

### Rebuild Module Map
```bash
# Regenerate MODULE_DOC_MAP.yaml
python scripts/build_module_map.py
```

**Output**: `modules/MODULE_DOC_MAP.yaml`

---

## CI/CD Workflows

### View Workflow Status
```bash
# List all workflows
gh workflow list

# View recent runs for specific workflow
gh run list --workflow=doc_id_validation.yml

# View run details
gh run view <run_id>
```

### Trigger Manual Run
```bash
# Trigger workflow manually
gh workflow run doc_id_validation.yml
```

### Check Workflow Files
```bash
# View workflow configuration
cat .github/workflows/doc_id_validation.yml
cat .github/workflows/registry_integrity.yml
cat .github/workflows/module_id_validation.yml
```

---

## Registry Management

### View Registry Stats
```bash
# Using Python
python -c "import yaml; r=yaml.safe_load(open('doc_id/specs/DOC_ID_REGISTRY.yaml')); print(f'Docs: {len(r[\"docs\"])}')"

# Using PowerShell
(Get-Content doc_id\specs\DOC_ID_REGISTRY.yaml | ConvertFrom-Yaml).docs.Count
```

### Search Registry
```bash
# Find doc by ID
grep "DOC-CORE-STATE-001" doc_id/specs/DOC_ID_REGISTRY.yaml -A 10

# Find all docs in a category
grep "category: core" doc_id/specs/DOC_ID_REGISTRY.yaml

# Find all docs for a module
grep "module_id: core.state" doc_id/specs/DOC_ID_REGISTRY.yaml
```

### Backup Registry
```bash
# Manual backup before changes
cp doc_id/specs/DOC_ID_REGISTRY.yaml \
   doc_id/specs/DOC_ID_REGISTRY.backup_$(date +%Y%m%d_%H%M).yaml
```

---

## Module Map Queries

### View Module Distribution
```bash
# Summary of all modules
python scripts/build_module_map.py
# (Prints summary during generation)
```

### Query Module Map
```bash
# Find all docs for a module
python -c "
import yaml
map_data = yaml.safe_load(open('modules/MODULE_DOC_MAP.yaml'))
module = 'core.state'
print(f'{module}: {map_data[\"modules\"][module][\"doc_count\"]} docs')
for doc in map_data['modules'][module]['docs']:
    print(f'  - {doc[\"doc_id\"]}: {doc[\"path\"]}')"
```

### Module Statistics
```bash
# Count docs per module
python -c "
import yaml
map_data = yaml.safe_load(open('modules/MODULE_DOC_MAP.yaml'))
for module_id in sorted(map_data['modules'].keys()):
    count = map_data['modules'][module_id]['doc_count']
    print(f'{module_id:30} {count:4} docs')"
```

---

## Troubleshooting

### Find Files Without Doc_IDs
```bash
# Generate report of missing doc_ids
python scripts/validate_doc_id_coverage.py --report missing.json

# View first 20 files
python -c "
import json
data = json.load(open('missing.json'))
for f in data['files_without_doc_id'][:20]:
    print(f)"
```

### Find Registry Errors
```bash
# Get detailed error report
python scripts/validate_registry.py --report errors.json

# View errors
python -c "
import json
data = json.load(open('errors.json'))
for err in data['errors']:
    print(err)"
```

### Check Unassigned Modules
```bash
# After dry-run, view unassigned docs
python scripts/module_id_assigner.py --dry-run

# View unassigned details
cat doc_id/reports/MODULE_ID_UNASSIGNED.jsonl | head -20
```

---

## Batch Operations

### Validate Everything
```bash
# Complete validation suite
python scripts/validate_registry.py && \
python scripts/validate_doc_id_coverage.py && \
echo "All validations passed!"
```

### Full Module Workflow
```bash
# Preview, apply, and rebuild
python scripts/module_id_assigner.py --dry-run
# Review output, then:
python scripts/module_id_assigner.py --apply
python scripts/build_module_map.py
```

### Daily Monitoring
```bash
# Save snapshot and validate
python scripts/doc_id_coverage_trend.py snapshot && \
python scripts/validate_registry.py && \
python scripts/validate_doc_id_coverage.py
```

---

## Git Integration

### Pre-Commit Check
```bash
# Run before committing registry changes
python scripts/validate_registry.py || echo "Fix errors before committing"
```

### View Registry Changes
```bash
# See what changed in registry
git diff doc_id/specs/DOC_ID_REGISTRY.yaml

# View module taxonomy changes
git diff doc_id/specs/module_taxonomy.yaml
```

### Revert Registry Changes
```bash
# Restore from backup
cp doc_id/specs/DOC_ID_REGISTRY.backup.yaml \
   doc_id/specs/DOC_ID_REGISTRY.yaml

# Or revert git changes
git checkout doc_id/specs/DOC_ID_REGISTRY.yaml
```

---

## Quick Diagnostics

### System Health Check
```bash
#!/bin/bash
echo "==> DOC_ID System Health Check"
echo ""

echo "1. Registry Validation:"
python scripts/validate_registry.py | grep -E "(PASS|FAIL)"

echo ""
echo "2. Coverage Check:"
python scripts/validate_doc_id_coverage.py | grep -E "Coverage|PASS|FAIL"

echo ""
echo "3. Latest Snapshot:"
python scripts/doc_id_coverage_trend.py report | grep "Current Coverage" -A 1

echo ""
echo "==> Health check complete"
```

### Coverage Summary
```bash
# One-line coverage check
python scripts/validate_doc_id_coverage.py 2>&1 | grep "Coverage"
```

### Module Count
```bash
# Count modules
python -c "import yaml; print(len(yaml.safe_load(open('doc_id/specs/module_taxonomy.yaml'))['module_taxonomy']))"
```

---

## Automation Scripts

### Daily Snapshot (Cron)
```bash
# Add to crontab for daily snapshots
# 0 0 * * * cd /path/to/repo && python scripts/doc_id_coverage_trend.py snapshot
```

### Weekly Validation
```bash
# Weekly full validation
# 0 0 * * 0 cd /path/to/repo && python scripts/validate_registry.py && python scripts/validate_doc_id_coverage.py
```

### CI Integration
```bash
# Run in CI pipeline
python scripts/validate_registry.py || exit 1
python scripts/validate_doc_id_coverage.py --baseline 0.90 || exit 1
```

---

## Advanced Queries

### Find All Python Source Docs
```bash
grep -A 5 "type: source" doc_id/specs/DOC_ID_REGISTRY.yaml | \
grep "path:.*\.py$"
```

### Count Docs by Category
```bash
grep "category:" doc_id/specs/DOC_ID_REGISTRY.yaml | \
sort | uniq -c | sort -rn
```

### List Deprecated Docs
```bash
grep -B 2 "status: deprecated" doc_id/specs/DOC_ID_REGISTRY.yaml | \
grep "doc_id:"
```

---

## Performance Tips

### Faster Validation
```bash
# Skip registry validation if only checking coverage
python scripts/validate_doc_id_coverage.py --skip-registry
# (Note: Flag not implemented yet, run separately)
```

### Parallel Checks
```bash
# Run validations in parallel
python scripts/validate_registry.py & \
python scripts/validate_doc_id_coverage.py & \
wait
```

---

## Common Workflows

### Adding New Documentation
1. Create/update file with doc_id embedded
2. Add entry to DOC_ID_REGISTRY.yaml
3. Assign module_id
4. Validate: `python scripts/validate_registry.py`
5. Commit changes

### Monthly Maintenance
1. Save snapshot: `python scripts/doc_id_coverage_trend.py snapshot`
2. View trends: `python scripts/doc_id_coverage_trend.py report`
3. Run validations: `python scripts/validate_registry.py && python scripts/validate_doc_id_coverage.py`
4. Review unassigned: `cat doc_id/reports/MODULE_ID_UNASSIGNED.jsonl`

### Before Major Refactor
1. Backup registry: `cp doc_id/specs/DOC_ID_REGISTRY.yaml ...`
2. Save snapshot: `python scripts/doc_id_coverage_trend.py snapshot`
3. Run validations: ensure baseline
4. Perform refactor
5. Re-validate: ensure no regression

---

## Help & Documentation

### Get Help
```bash
# Script help
python scripts/validate_registry.py --help
python scripts/validate_doc_id_coverage.py --help
python scripts/module_id_assigner.py --help
```

### View Documentation
- **System Overview**: `doc_id/DOC_ID_SYSTEM_OVERVIEW.md`
- **Main README**: `doc_id/README.md`
- **Framework Spec**: `doc_id/specs/DOC_ID_FRAMEWORK.md`
- **Documentation Index**: `doc_id/DOCUMENTATION_INDEX.md`

---

**Quick Links**:
- [System Overview](DOC_ID_SYSTEM_OVERVIEW.md)
- [Main README](README.md)
- [Documentation Index](DOCUMENTATION_INDEX.md)
- [Latest Session Summary](COMPLETE_SESSION_SUMMARY_2025-12-01.md)
