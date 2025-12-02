# PIPE Tools - Command Reference

Quick reference for pipeline restructuring tools.

## Generate Virtual Tree

```bash
# Basic generation
python scripts/pipe_tree.py

# With statistics
python scripts/pipe_tree.py --stats

# Custom output location
python scripts/pipe_tree.py --output MY_TREE.txt

# All options
python scripts/pipe_tree.py \
  --root . \
  --mapping-config pipe_mapping_config.yaml \
  --ignore-file .pipeignore \
  --output PIPELINE_VIRTUAL_TREE.txt \
  --stats
```

## Classify Files

```bash
# Single file
python scripts/pipe_classify.py engine/orchestrator/core.py

# Multiple files
python scripts/pipe_classify.py file1.py file2.py file3.py

# Verbose output
python scripts/pipe_classify.py --verbose modules/error-engine/error_engine.py

# Custom config
python scripts/pipe_classify.py \
  --mapping-config pipe_mapping_config.yaml \
  --verbose \
  engine/orchestrator/core.py
```

## PowerShell Helpers

```powershell
# Classify all Python files in a directory
Get-ChildItem -Path modules\core-engine -Filter *.py -Recurse | 
  ForEach-Object { python scripts\pipe_classify.py $_.FullName }

# Find all files in a specific PIPE module
python scripts\pipe_tree.py --output temp.txt
Select-String "PIPE-17_EXECUTE_TOOL" temp.txt -Context 0,100
Remove-Item temp.txt

# Count files per PIPE
python scripts\pipe_tree.py --stats 2>&1 | Select-String "PIPE-"
```

## Common Workflows

### 1. Initial Exploration
```bash
# Generate tree with stats
python scripts/pipe_tree.py --stats

# View specific sections
head -100 PIPELINE_VIRTUAL_TREE.txt
grep -A 20 "PIPE-17_EXECUTE" PIPELINE_VIRTUAL_TREE.txt
```

### 2. Verify File Classification
```bash
# Check where critical files belong
python scripts/pipe_classify.py --verbose \
  engine/orchestrator/core.py \
  modules/error-engine/error_engine.py \
  modules/core-state/db.py
```

### 3. Refine Mapping
```bash
# 1. Edit pipe_mapping_config.yaml
# 2. Re-generate tree
python scripts/pipe_tree.py --stats
# 3. Compare results
diff PIPELINE_VIRTUAL_TREE.txt PIPELINE_VIRTUAL_TREE.txt.bak
```

### 4. Find Misclassified Files
```bash
# Files in PIPE-26 (default bucket) - might need better rules
grep -A 1 "PIPE-26_LEARN" PIPELINE_VIRTUAL_TREE.txt | grep -v "PIPE-26" | head -50

# Files in PIPE-22 (might be too many)
grep -A 1 "PIPE-22_COMMIT" PIPELINE_VIRTUAL_TREE.txt | wc -l
```

## Output Formats

### Tree Output (PIPELINE_VIRTUAL_TREE.txt)
```
pipeline/
  A_INTAKE_AND_SPECS/
    PIPE-01_INTAKE_REQUEST/
      modules/pm-integrations/github_sync.py
      scripts/gh_epic_sync.py
```

### Classify Output (simple)
```
engine/orchestrator/core.py → PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS
```

### Classify Output (verbose)
```
File: engine/orchestrator/core.py
  Virtual location: pipeline/D_WORKSPACE_AND_SCHEDULING/PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS/
  Matched rule: priority_assignment
  Full path: pipeline/D_WORKSPACE_AND_SCHEDULING/PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS/engine/orchestrator/core.py
```

## Troubleshooting

### Python not found
```bash
# Use full path or activate venv
python3 scripts/pipe_tree.py --stats
.venv/Scripts/python scripts/pipe_tree.py --stats
```

### Missing PyYAML
```bash
pip install pyyaml
```

### File not classified correctly
1. Check `pipe_mapping_config.yaml` rules
2. Remember: **first match wins**
3. Add new rule **above** existing rules to override
4. Use `pipe_classify.py --verbose` to see which rule matched

### Too many files in default (PIPE-26)
1. Run: `grep "PIPE-26" PIPELINE_VIRTUAL_TREE.txt | head -20`
2. Find patterns in those paths
3. Add specific rules to `pipe_mapping_config.yaml`
4. Re-generate and verify

## Tips

- **Rule order matters** - Put specific rules before general rules
- **Use path_prefix** for directories - `"modules/error-engine/"`
- **Use file_glob** for patterns - `"*.md"` or `"scripts/test_*.py"`
- **Test incrementally** - Add one rule, regenerate, verify
- **Keep `.pipeignore` updated** - Exclude build artifacts

## See Also

- `PIPELINE_VIRTUAL_TREE_README.md` - Full documentation
- `PIPELINE_RESTRUCTURE_SUMMARY.md` - Analysis and recommendations
- `masssive mof.md` - Original specification
- `pipe_mapping_config.yaml` - Mapping configuration
