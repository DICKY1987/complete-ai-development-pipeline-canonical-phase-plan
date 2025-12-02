# Pipeline Virtual Tree - Quick Start

This directory contains tools to visualize how the repository would look if reorganized around the PIPE-01 to PIPE-26 pipeline structure.

## What You've Got

1. **`pipe_mapping_config.yaml`** - Configuration mapping current paths to PIPE modules
2. **`scripts/pipe_tree.py`** - Tool to generate the virtual tree
3. **`PIPELINE_VIRTUAL_TREE.txt`** - Generated virtual tree (2259 files mapped)
4. **`.pipeignore`** - Patterns for files to exclude from mapping

## Quick Commands

### Generate the virtual tree
```bash
python scripts/pipe_tree.py --output PIPELINE_VIRTUAL_TREE.txt
```

### With statistics
```bash
python scripts/pipe_tree.py --stats --output PIPELINE_VIRTUAL_TREE.txt
```

### Custom configuration
```bash
python scripts/pipe_tree.py \
  --root . \
  --mapping-config pipe_mapping_config.yaml \
  --ignore-file .pipeignore \
  --output PIPELINE_VIRTUAL_TREE.txt \
  --stats
```

## Current Statistics

**Total files mapped: 2,259**

### By Phase (A-G):
- **A_INTAKE_AND_SPECS**: 95 files
- **B_WORKSTREAM_AND_CONFIG**: 128 files  
- **C_PATTERNS_AND_PLANNING**: 59 files
- **D_WORKSPACE_AND_SCHEDULING**: 47 files
- **E_EXECUTION_AND_VALIDATION**: 189 files
- **F_ERROR_AND_RECOVERY**: 130 files
- **G_FINALIZATION_AND_LEARNING**: 1,611 files

### Top 5 PIPE Modules:
1. **PIPE-22** (Commit Results): 836 files
2. **PIPE-26** (Learn & Update): 708 files
3. **PIPE-18** (Post-Exec Tests): 119 files
4. **PIPE-19** (Error Plugins): 114 files
5. **PIPE-02** (Discover Specs): 78 files

## Understanding the Output

The virtual tree shows:
- **Structure**: How files would be organized under `pipeline/A_*/PIPE-XX_*/`
- **Leaf nodes**: Original relative paths from current repo
- **No file moves**: This is visualization only - no files are moved

### Example from PIPELINE_VIRTUAL_TREE.txt:
```
pipeline/
  E_EXECUTION_AND_VALIDATION/
    PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT/
      engine/orchestrator/core.py
      aider/prompts/code_edit.md
      modules/aim-environment/config.py
```

This means:
- `engine/orchestrator/core.py` belongs conceptually to PIPE-17
- In a restructured repo, it would live under that PIPE module
- Currently, it's still at `engine/orchestrator/core.py`

## Next Steps

### Phase 1: Review & Refine Mapping (You Are Here ✓)
- [x] Generate initial virtual tree
- [ ] Review `PIPELINE_VIRTUAL_TREE.txt`
- [ ] Adjust `pipe_mapping_config.yaml` if files are misclassified
- [ ] Re-run until mapping feels right

### Phase 2: Create Manifests
For each PIPE module, create a manifest like:
```yaml
# pipeline-manifests/PIPE-17_manifest.yaml
pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
name: Execute Tool and Capture Output
phase: E_EXECUTION_AND_VALIDATION
implementation_paths:
  - engine/orchestrator/
  - aider/
  - modules/aim-environment/
inputs:
  - PIPE-16 (adapter selection)
  - config/router_config.json
outputs:
  - logs/
  - .worktrees/
  - state/task_updates
```

### Phase 3: Gradual Migration (Optional)
Only if you want to physically restructure:
1. Pick one PIPE module (start with smallest)
2. Create actual `pipeline/E_*/PIPE-XX_*/` directory
3. Move files incrementally
4. Update imports
5. Test thoroughly
6. Repeat

## Adjusting the Mapping

### Add a new rule
Edit `pipe_mapping_config.yaml`:
```yaml
rules:
  - name: my_custom_rule
    pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
    match:
      path_prefix:
        - "my_custom_path/"
      file_glob:
        - "scripts/special_*.py"
```

### Change a file's classification
Find the rule that currently matches it and either:
1. Adjust that rule's `match` patterns, or
2. Add a new rule **above it** (first match wins)

### Ignore more files
Add patterns to `.pipeignore`:
```
# My custom ignores
*.tmp
temp/
scratch/
```

## Troubleshooting

### "No module named yaml"
```bash
pip install pyyaml
```

### Files in wrong PIPE module
Check `pipe_mapping_config.yaml` - rules are processed top-to-bottom, first match wins.

### Too many files in PIPE-26 (default bucket)
PIPE-26 is the fallback for unmatched files. Add more specific rules for those paths.

## Reference

See `masssive mof.md` for the full specification and design rationale:
- Section: "PIPELINE_RESTRUCTURE_TREE_SPEC_V1"
- Contains: 26 PIPE module definitions, algorithm details, mapping semantics

## Files

- `pipe_mapping_config.yaml` - 26 PIPE module mapping rules
- `scripts/pipe_tree.py` - Virtual tree generator (Python 3.7+)
- `.pipeignore` - Exclusion patterns
- `PIPELINE_VIRTUAL_TREE.txt` - Generated output (this file is regenerated each run)
- `PIPELINE_VIRTUAL_TREE_README.md` - This file
