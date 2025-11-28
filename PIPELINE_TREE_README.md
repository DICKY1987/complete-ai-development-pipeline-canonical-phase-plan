# Pipeline Virtual Tree Generator

## Overview

This directory contains tools to generate a **virtual visualization** of how the current repository would be organized if restructured around the **PIPE-01 to PIPE-26 pipeline architecture**.

**Important**: This is a **mapping/visualization only** – no files are moved or renamed.

## Files Created

### 1. `pipe_mapping_config.yaml`
Configuration file that defines how current repository paths map to PIPE modules (PIPE-01 through PIPE-26).

**Structure**:
- `version`: Config format version
- `default_pipe_id`: Fallback PIPE for unmatched files
- `rules`: Ordered list of mapping rules (first match wins)

Each rule contains:
- `name`: Descriptive rule name
- `pipe_id`: Target PIPE module (e.g., `PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT`)
- `match`: Matching criteria
  - `path_prefix`: List of path prefixes (e.g., `core/engine/`)
  - `file_glob`: List of glob patterns (e.g., `*.py`, `scripts/*.sh`)

### 2. `.pipeignore`
Ignore patterns file (similar to `.gitignore`) that specifies files and directories to exclude from the virtual tree.

Default patterns include:
- `.git/`, `.pytest_cache/`, `__pycache__/`
- Virtual environments (`.venv/`, `venv/`)
- Build artifacts (`dist/`, `build/`, `*.pyc`)
- System files (`.DS_Store`, `Thumbs.db`)

### 3. `pipe_tree.py`
Python CLI tool that generates the virtual tree structure.

**Features**:
- Discovers all files in the repository
- Classifies each file into one of 26 PIPE modules based on mapping rules
- Builds a hierarchical tree structure with:
  - Root: `pipeline/`
  - 7 macro phases (A–G)
  - 26 PIPE module directories
  - Original file paths as leaf nodes
- Outputs ASCII tree to text file

### 4. `PIPELINE_VIRTUAL_TREE.txt`
Generated output file showing the virtual pipeline structure with 2,812+ files mapped.

## Usage

### Basic Usage
```bash
python pipe_tree.py
```

This generates `PIPELINE_VIRTUAL_TREE.txt` in the current directory.

### Advanced Usage
```bash
python pipe_tree.py \
  --root . \
  --mapping-config pipe_mapping_config.yaml \
  --ignore-file .pipeignore \
  --output PIPELINE_VIRTUAL_TREE.txt
```

### Command-Line Options
- `--root PATH` – Repository root directory (default: current directory)
- `--mapping-config PATH` – Path to mapping config YAML (default: `pipe_mapping_config.yaml`)
- `--ignore-file PATH` – Path to ignore patterns file (default: `.pipeignore`)
- `--output PATH` – Output file path (default: `PIPELINE_VIRTUAL_TREE.txt`)
- `--help` – Show help message

## Pipeline Structure

The virtual tree organizes files into **7 macro phases** and **26 PIPE modules**:

### A. INTAKE AND SPECS (PIPE-01 to PIPE-03)
- `PIPE-01_INTAKE_REQUEST` – PM intake, prompting, AI context
- `PIPE-02_DISCOVER_RELATED_SPECS` – OpenSpec, specifications
- `PIPE-03_NORMALIZE_REQUIREMENTS` – Spec tools, indexing

### B. WORKSTREAM AND CONFIG (PIPE-04 to PIPE-07)
- `PIPE-04_MATERIALIZE_WORKSTREAM_FILE` – Workstream definitions
- `PIPE-05_VALIDATE_WORKSTREAM_SCHEMA` – Schema validation
- `PIPE-06_RESOLVE_CONFIG_CASCADE` – Configuration files
- `PIPE-07_RESOLVE_CAPABILITIES_AND_REGISTRY` – Registry, capabilities, modules

### C. PATTERNS AND PLANNING (PIPE-08 to PIPE-12)
- `PIPE-08_SELECT_UET_PATTERNS` – Pattern registry
- `PIPE-09_SPECIALIZE_PATTERNS_WITH_CONTEXT` – Pattern templates
- `PIPE-10_VALIDATE_PATTERN_PLAN` – Pattern verification
- `PIPE-11_BUILD_TASK_GRAPH_DAG` – Task graph planning
- `PIPE-12_PERSIST_PLAN_IN_STATE` – State persistence

### D. WORKSPACE AND SCHEDULING (PIPE-13 to PIPE-15)
- `PIPE-13_PREPARE_WORKTREES_AND_CHECKPOINTS` – Worktree management
- `PIPE-14_ADMIT_READY_TASKS_TO_QUEUE` – Task queuing
- `PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS` – Priority scheduling

### E. EXECUTION AND VALIDATION (PIPE-16 to PIPE-18)
- `PIPE-16_ROUTE_TASK_TO_TOOL_ADAPTER` – AIM routing
- `PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT` – Tool execution (aider, Claude, etc.)
- `PIPE-18_RUN_POST_EXEC_TESTS_AND_CHECKS` – Test validation

### F. ERROR AND RECOVERY (PIPE-19 to PIPE-21)
- `PIPE-19_RUN_ERROR_PLUGINS_PIPELINE` – Error detection plugins
- `PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION` – Error classification
- `PIPE-21_APPLY_AUTOFIX_RETRY_AND_CIRCUIT_CONTROL` – Auto-fix and retry

### G. FINALIZATION AND LEARNING (PIPE-22 to PIPE-26)
- `PIPE-22_COMMIT_TASK_RESULTS_TO_STATE_AND_MODULES` – Result commits
- `PIPE-23_COMPLETE_WORKSTREAM_AND_ARCHIVE` – Archival
- `PIPE-24_UPDATE_METRICS_REPORTS_AND_SUMMARIES` – Metrics and reports
- `PIPE-25_SURFACE_TO_GUI_AND_TUI` – UI presentation
- `PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG` – Learning and feedback

## Output Format

The output file (`PIPELINE_VIRTUAL_TREE.txt`) shows:

```text
pipeline/
  A_INTAKE_AND_SPECS/
    PIPE-01_INTAKE_REQUEST/
      pm/epics/feature_123.yaml
      prompting/cli_intake_prompt.md
    PIPE-02_DISCOVER_RELATED_SPECS/
      openspec/specs/my_feature_spec.yaml
  B_WORKSTREAM_AND_CONFIG/
    PIPE-04_MATERIALIZE_WORKSTREAM_FILE/
      workstreams/ws-01-example.json
  ...
```

**Key Points**:
- Directories end with `/`
- Leaf nodes show **original relative paths** from current repo
- Files are **not** split into subdirectories (e.g., `core/engine/orchestrator.py` appears as one leaf label)
- Sorted alphabetically within each directory (directories first, then files)

## Customizing the Mapping

To adjust which files go to which PIPE modules, edit `pipe_mapping_config.yaml`:

1. **Add new rules** to the `rules` list
2. **Order matters** – first matching rule wins
3. **Match criteria**:
   - `path_prefix`: Matches paths starting with prefix (e.g., `core/engine/`)
   - `file_glob`: Matches glob patterns (e.g., `*.py`, `scripts/*.sh`)

Example:
```yaml
- name: my_custom_rule
  pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
  match:
    path_prefix:
      - "my_custom_dir/"
    file_glob:
      - "special_*.py"
```

## Statistics

**Current mapping results**:
- **Total files mapped**: 2,812
- **PIPE modules**: 26
- **Macro phases**: 7
- **Ignored patterns**: 23

## Implementation Notes

The tool follows the **PIPELINE_RESTRUCTURE_TREE_SPEC_V1** specification:

1. **No file operations** – Pure visualization, no actual moves/renames
2. **First-match-wins** – Rules evaluated in order
3. **Original paths preserved** – Leaf nodes show current paths, not new names
4. **Stable structure** – Fixed 7-phase, 26-PIPE hierarchy
5. **Extensible** – Easy to add new rules without changing code

## Requirements

- Python 3.7+
- PyYAML (`pip install pyyaml`)

## See Also

- **Specification**: `PIPELINE_RESTRUCTURE_TREE_SPEC_V1.md` (if available)
- **Mapping Config**: `pipe_mapping_config.yaml`
- **Output**: `PIPELINE_VIRTUAL_TREE.txt`
