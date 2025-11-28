# Pipeline Tree Visualizer – Quick Start

## What Is This?

A tool that shows **how your repository would look** if organized by the PIPE-01 to PIPE-26 pipeline structure – **without actually moving any files**.

## Quick Start (30 seconds)

```bash
# 1. Generate the virtual tree
python pipe_tree.py

# 2. View the output
cat PIPELINE_VIRTUAL_TREE.txt
# Or on Windows:
type PIPELINE_VIRTUAL_TREE.txt

# 3. Validate the structure
python validate_pipeline_tree.py
```

## What You Get

**Input**: Your current messy repository structure

**Output**: A clean visualization showing:
```
pipeline/
  A_INTAKE_AND_SPECS/
    PIPE-01_INTAKE_REQUEST/
      pm/epics/feature_123.yaml           ← original path
      prompting/cli_intake_prompt.md      ← original path
    PIPE-02_DISCOVER_RELATED_SPECS/
      openspec/specs/my_spec.yaml         ← original path
  ...
```

## Files Created

| File | Purpose |
|------|---------|
| `pipe_mapping_config.yaml` | Defines which files go to which PIPE modules |
| `.pipeignore` | Files/directories to exclude (like `.gitignore`) |
| `pipe_tree.py` | Main CLI tool (generates tree) |
| `validate_pipeline_tree.py` | Validation script |
| `PIPELINE_VIRTUAL_TREE.txt` | **Output** – the virtual tree (2,812 files mapped) |
| `PIPELINE_TREE_README.md` | Full documentation |

## Customization

Edit `pipe_mapping_config.yaml` to change mappings:

```yaml
rules:
  - name: my_rule
    pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
    match:
      path_prefix:
        - "my_custom_dir/"
      file_glob:
        - "*.special"
```

Then regenerate:
```bash
python pipe_tree.py
```

## Validation

```bash
# Check structure is valid
python validate_pipeline_tree.py

# Expected output:
# ✅ Root node 'pipeline/' found
# ✅ All 7 macro phases found
# ✅ All 26 PIPE modules found
# ✅ Total files mapped: 2812
# ✅ VALIDATION PASSED
```

## The 26 PIPE Modules

**A. INTAKE & SPECS** (1-3)
- Intake, spec discovery, normalization

**B. WORKSTREAM & CONFIG** (4-7)
- Workstreams, schemas, config, registry

**C. PATTERNS & PLANNING** (8-12)
- UET patterns, planning, DAG, state

**D. WORKSPACE & SCHEDULING** (13-15)
- Worktrees, queues, priorities

**E. EXECUTION & VALIDATION** (16-18)
- Routing, execution, tests

**F. ERROR & RECOVERY** (19-21)
- Error detection, classification, auto-fix

**G. FINALIZATION & LEARNING** (22-26)
- Commits, archival, metrics, GUI, learning

## Help

```bash
# Show all options
python pipe_tree.py --help

# Use custom config
python pipe_tree.py --mapping-config my_config.yaml

# Change output location
python pipe_tree.py --output /path/to/output.txt
```

## Important Notes

⚠️ **This is visualization only** – no files are moved or renamed  
✅ **Safe to run** – read-only operation  
📊 **Useful for** – understanding future structure, planning migrations  

## Next Steps

1. ✅ Review `PIPELINE_VIRTUAL_TREE.txt` to see where files are mapped
2. ✅ Adjust `pipe_mapping_config.yaml` if needed
3. ✅ Use this visualization to plan actual restructuring (if desired)

## Full Documentation

See `PIPELINE_TREE_README.md` for complete details.
