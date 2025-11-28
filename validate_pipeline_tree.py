#!/usr/bin/env python3
"""
Validate PIPELINE_VIRTUAL_TREE.txt structure

Checks that the generated tree has:
- All 7 macro phases (A-G)
- All 26 PIPE modules (PIPE-01 to PIPE-26)
- Proper hierarchy and structure
"""

import sys
from pathlib import Path


EXPECTED_PHASES = [
    "A_INTAKE_AND_SPECS",
    "B_WORKSTREAM_AND_CONFIG",
    "C_PATTERNS_AND_PLANNING",
    "D_WORKSPACE_AND_SCHEDULING",
    "E_EXECUTION_AND_VALIDATION",
    "F_ERROR_AND_RECOVERY",
    "G_FINALIZATION_AND_LEARNING",
]

EXPECTED_PIPES = [
    "PIPE-01_INTAKE_REQUEST",
    "PIPE-02_DISCOVER_RELATED_SPECS",
    "PIPE-03_NORMALIZE_REQUIREMENTS",
    "PIPE-04_MATERIALIZE_WORKSTREAM_FILE",
    "PIPE-05_VALIDATE_WORKSTREAM_SCHEMA",
    "PIPE-06_RESOLVE_CONFIG_CASCADE",
    "PIPE-07_RESOLVE_CAPABILITIES_AND_REGISTRY",
    "PIPE-08_SELECT_UET_PATTERNS",
    "PIPE-09_SPECIALIZE_PATTERNS_WITH_CONTEXT",
    "PIPE-10_VALIDATE_PATTERN_PLAN",
    "PIPE-11_BUILD_TASK_GRAPH_DAG",
    "PIPE-12_PERSIST_PLAN_IN_STATE",
    "PIPE-13_PREPARE_WORKTREES_AND_CHECKPOINTS",
    "PIPE-14_ADMIT_READY_TASKS_TO_QUEUE",
    "PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS",
    "PIPE-16_ROUTE_TASK_TO_TOOL_ADAPTER",
    "PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT",
    "PIPE-18_RUN_POST_EXEC_TESTS_AND_CHECKS",
    "PIPE-19_RUN_ERROR_PLUGINS_PIPELINE",
    "PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION",
    "PIPE-21_APPLY_AUTOFIX_RETRY_AND_CIRCUIT_CONTROL",
    "PIPE-22_COMMIT_TASK_RESULTS_TO_STATE_AND_MODULES",
    "PIPE-23_COMPLETE_WORKSTREAM_AND_ARCHIVE",
    "PIPE-24_UPDATE_METRICS_REPORTS_AND_SUMMARIES",
    "PIPE-25_SURFACE_TO_GUI_AND_TUI",
    "PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG",
]


def validate_tree(tree_file: Path) -> bool:
    """Validate the tree structure."""
    if not tree_file.exists():
        print(f"❌ Error: Tree file not found: {tree_file}")
        return False
    
    with open(tree_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    
    # Check root
    if not lines or lines[0] != "pipeline/":
        print("❌ Error: Tree does not start with 'pipeline/'")
        return False
    
    print("✅ Root node 'pipeline/' found")
    
    # Check phases
    found_phases = []
    for phase in EXPECTED_PHASES:
        if f"{phase}/" in content:
            found_phases.append(phase)
    
    if len(found_phases) == len(EXPECTED_PHASES):
        print(f"✅ All {len(EXPECTED_PHASES)} macro phases found")
    else:
        missing = set(EXPECTED_PHASES) - set(found_phases)
        print(f"❌ Error: Missing macro phases: {missing}")
        return False
    
    # Check PIPE modules
    found_pipes = []
    for pipe in EXPECTED_PIPES:
        if f"{pipe}/" in content:
            found_pipes.append(pipe)
    
    if len(found_pipes) == len(EXPECTED_PIPES):
        print(f"✅ All {len(EXPECTED_PIPES)} PIPE modules found")
    else:
        missing = set(EXPECTED_PIPES) - set(found_pipes)
        print(f"❌ Error: Missing PIPE modules: {missing}")
        return False
    
    # Count files
    file_count = 0
    for line in lines:
        # Files don't end with / and are not at the phase/pipe level
        if line.strip() and not line.strip().endswith('/'):
            # Check it's not a directory name
            if not any(phase in line for phase in EXPECTED_PHASES):
                if not any(pipe in line for pipe in EXPECTED_PIPES):
                    if line.strip() != "pipeline/":
                        file_count += 1
    
    print(f"✅ Total files mapped: {file_count}")
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Root node:       ✅")
    print(f"Macro phases:    ✅ {len(found_phases)}/{len(EXPECTED_PHASES)}")
    print(f"PIPE modules:    ✅ {len(found_pipes)}/{len(EXPECTED_PIPES)}")
    print(f"Files mapped:    ✅ {file_count}")
    print(f"Tree file:       {tree_file}")
    print("="*60)
    print("✅ VALIDATION PASSED")
    
    return True


def main():
    tree_file = Path("PIPELINE_VIRTUAL_TREE.txt")
    
    if len(sys.argv) > 1:
        tree_file = Path(sys.argv[1])
    
    success = validate_tree(tree_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
