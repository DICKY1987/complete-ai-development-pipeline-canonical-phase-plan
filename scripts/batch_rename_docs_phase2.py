#!/usr/bin/env python3
"""
Batch rename docs/ subdirectory files to DOC_ naming convention
Phase 2 of cleanup
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Diagrams
DIAGRAMS = {
    'docs/diagrams/ERROR_ESCALATION.md': 'docs/diagrams/DOC_ERROR_ESCALATION_DIAGRAM.md',
    'docs/diagrams/SPEC_INTEGRATION.md': 'docs/diagrams/DOC_SPEC_INTEGRATION_DIAGRAM.md',
    'docs/diagrams/SYSTEM_ARCHITECTURE.md': 'docs/diagrams/DOC_SYSTEM_ARCHITECTURE_DIAGRAM.md',
    'docs/diagrams/TASK_LIFECYCLE.md': 'docs/diagrams/DOC_TASK_LIFECYCLE_DIAGRAM.md',
    'docs/diagrams/TOOL_SELECTION.md': 'docs/diagrams/DOC_TOOL_SELECTION_DIAGRAM.md',
    'docs/diagrams/VISUAL_ARCHITECTURE_GUIDE.md': 'docs/diagrams/DOC_VISUAL_ARCHITECTURE_GUIDE.md',
}

# Examples (canonical examples, not dev scratch)
EXAMPLES = {
    'docs/examples/01_simple_task.md': 'docs/examples/DOC_EXAMPLE_01_SIMPLE_TASK.md',
    'docs/examples/02_parallel_execution.md': 'docs/examples/DOC_EXAMPLE_02_PARALLEL_EXECUTION.md',
    'docs/examples/03_error_handling.md': 'docs/examples/DOC_EXAMPLE_03_ERROR_HANDLING.md',
    'docs/examples/04_multi_phase.md': 'docs/examples/DOC_EXAMPLE_04_MULTI_PHASE.md',
    'docs/examples/05_saga_pattern.md': 'docs/examples/DOC_EXAMPLE_05_SAGA_PATTERN.md',
}

# Guidelines
GUIDELINES = {
    'docs/guidelines/AI_DEV_HYGIENE_GUIDELINES.md': 'docs/guidelines/DOC_AI_DEV_HYGIENE_GUIDELINES.md',
    'docs/guidelines/ANTI_PATTERNS.md': 'docs/guidelines/DOC_ANTI_PATTERNS.md',
    'docs/guidelines/TESTING_STRATEGY.md': 'docs/guidelines/DOC_TESTING_STRATEGY.md',
    'docs/guidelines/UET_DEVELOPMENT RULES DO and DONT.md': 'docs/guidelines/DOC_UET_DEVELOPMENT_RULES.md',
}

# Operations
OPERATIONS = {
    'docs/operations/AUDIT_RETENTION.md': 'docs/operations/DOC_AUDIT_RETENTION.md',
    'docs/operations/BACKUP_STRATEGY.md': 'docs/operations/DOC_BACKUP_STRATEGY.md',
    'docs/operations/DISASTER_RECOVERY.md': 'docs/operations/DOC_DISASTER_RECOVERY.md',
    'docs/operations/ERROR_ALERT_CONFIG.md': 'docs/operations/DOC_ERROR_ALERT_CONFIG.md',
    'docs/operations/MONITORING.md': 'docs/operations/DOC_MONITORING.md',
}

# Recipes
RECIPES = {
    'docs/recipes/BATCH_PROCESSING.md': 'docs/recipes/DOC_RECIPE_BATCH_PROCESSING.md',
    'docs/recipes/CUSTOM_ADAPTER.md': 'docs/recipes/DOC_RECIPE_CUSTOM_ADAPTER.md',
    'docs/recipes/ERROR_PLUGIN.md': 'docs/recipes/DOC_RECIPE_ERROR_PLUGIN.md',
    'docs/recipes/MIGRATE_LEGACY.md': 'docs/recipes/DOC_RECIPE_MIGRATE_LEGACY.md',
}

# Troubleshooting
TROUBLESHOOTING = {
    'docs/troubleshooting/CI_FAILURES.md': 'docs/troubleshooting/DOC_TROUBLESHOOTING_CI_FAILURES.md',
    'docs/troubleshooting/COMMON_ERRORS.md': 'docs/troubleshooting/DOC_TROUBLESHOOTING_COMMON_ERRORS.md',
    'docs/troubleshooting/DB_CORRUPTION.md': 'docs/troubleshooting/DOC_TROUBLESHOOTING_DB_CORRUPTION.md',
    'docs/troubleshooting/PATH_ISSUES.md': 'docs/troubleshooting/DOC_TROUBLESHOOTING_PATH_ISSUES.md',
    'docs/troubleshooting/TOOL_TIMEOUTS.md': 'docs/troubleshooting/DOC_TROUBLESHOOTING_TOOL_TIMEOUTS.md',
}

# Dev docs (READMEs → _DEV_)
DEV_MOVES = {
    'docs/forensics/README.md': 'developer/_DEV_FORENSICS_README.md',
    'docs/guidelines/README.md': 'developer/_DEV_GUIDELINES_README.md',
    'docs/maintenance/README.md': 'developer/_DEV_MAINTENANCE_README.md',
    'docs/maintenance/id file consolidation checker.md': 'developer/_DEV_ID_FILE_CONSOLIDATION_CHECKER.md',
}

ALL_RENAMES = {
    **DIAGRAMS,
    **EXAMPLES,
    **GUIDELINES,
    **OPERATIONS,
    **RECIPES,
    **TROUBLESHOOTING,
}

def main():
    print("=== Batch Rename Phase 2: docs/ subdirectories ===\n")
    
    renamed_count = 0
    moved_count = 0
    
    print("Renaming canonical docs:")
    for old_path_str, new_path_str in ALL_RENAMES.items():
        old_path = REPO_ROOT / old_path_str
        new_path = REPO_ROOT / new_path_str
        
        if old_path.exists():
            print(f"  {old_path.relative_to(REPO_ROOT / 'docs')} -> {new_path.name}")
            old_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"  [SKIP] Not found: {old_path.relative_to(REPO_ROOT / 'docs')}")
    
    print("\nMoving dev docs to developer/:")
    for old_path_str, new_path_str in DEV_MOVES.items():
        old_path = REPO_ROOT / old_path_str
        new_path = REPO_ROOT / new_path_str
        
        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"  {old_path.relative_to(REPO_ROOT / 'docs')} -> {new_path.name}")
            old_path.rename(new_path)
            moved_count += 1
        else:
            print(f"  [SKIP] Not found: {old_path.relative_to(REPO_ROOT / 'docs')}")
    
    print(f"\n=== Summary ===")
    print(f"Renamed: {renamed_count}")
    print(f"Moved to developer/: {moved_count}")
    print(f"Total processed: {renamed_count + moved_count}")

if __name__ == '__main__':
    main()
