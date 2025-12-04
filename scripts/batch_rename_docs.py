#!/usr/bin/env python3
"""
Batch rename docs/ files to DOC_ naming convention
Per PAT-DOCID-TRIAGE-001
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-BATCH-RENAME-DOCS-194
# DOC_ID: DOC-SCRIPT-SCRIPTS-BATCH-RENAME-DOCS-131

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent

# Mapping: old_name -> new_name
RENAMES = {
    # Core guides
    "docs/ACS_USAGE_GUIDE.md": "docs/DOC_ACS_USAGE_GUIDE.md",
    "docs/ARCHITECTURE.md": "docs/DOC_ARCHITECTURE.md",
    "docs/CI_PATH_STANDARDS.md": "docs/DOC_CI_PATH_STANDARDS.md",
    "docs/CONFIGURATION_GUIDE.md": "docs/DOC_CONFIGURATION_GUIDE.md",
    "docs/COORDINATION_GUIDE.md": "docs/DOC_COORDINATION_GUIDE.md",
    "docs/DOCUMENTATION_INDEX.md": "docs/DOC_DOCUMENTATION_INDEX.md",
    # Engine references
    "docs/ENGINE_QUICK_REFERENCE.md": "docs/DOC_ENGINE_QUICK_REFERENCE.md",
    # File organization
    "docs/FILE_ORGANIZATION_QUICK_REF.md": "docs/DOC_FILE_ORGANIZATION_QUICK_REF.md",
    "docs/FILE_ORGANIZATION_SYSTEM.md": "docs/DOC_FILE_ORGANIZATION_SYSTEM.md",
    "docs/IMPLEMENTATION_LOCATIONS.md": "docs/DOC_IMPLEMENTATION_LOCATIONS.md",
    "docs/HARDCODED_PATH_INDEXER.md": "docs/DOC_HARDCODED_PATH_INDEXER.md",
    # Spec management
    "docs/SPEC_MANAGEMENT_CONTRACT.md": "docs/DOC_SPEC_MANAGEMENT_CONTRACT.md",
    "docs/SPEC_MIGRATION_GUIDE.md": "docs/DOC_SPEC_MIGRATION_GUIDE.md",
    # Workstream guides
    "docs/workstream_authoring_guide.md": "docs/DOC_WORKSTREAM_AUTHORING_GUIDE.md",
    "docs/workstream-prompt-structure.md": "docs/DOC_WORKSTREAM_PROMPT_STRUCTURE.md",
    # Plugin docs
    "docs/plugin-ecosystem-summary.md": "docs/DOC_PLUGIN_ECOSYSTEM_SUMMARY.md",
    "docs/plugin-quick-reference.md": "docs/DOC_PLUGIN_QUICK_REFERENCE.md",
    "docs/plugin-test-suite-summary.md": "docs/DOC_PLUGIN_TEST_SUITE_SUMMARY.md",
    # Patterns and strategies
    "docs/SAFE_RENAME_STRATEGY.md": "docs/DOC_SAFE_RENAME_STRATEGY.md",
    "docs/soft-sandbox-pattern.md": "docs/DOC_SOFT_SANDBOX_PATTERN.md",
    "docs/spec-tooling-consolidation.md": "docs/DOC_SPEC_TOOLING_CONSOLIDATION.md",
    "docs/state_machine.md": "docs/DOC_STATE_MACHINE.md",
    "docs/ZERO_TOUCH_SYNC_DESIGN.md": "docs/DOC_ZERO_TOUCH_SYNC_DESIGN.md",
    # AIM integration
    "docs/AIM_INTEGRATION_STATUS.md": "docs/DOC_AIM_INTEGRATION_STATUS.md",
    # Aider contract
    "docs/aider_contract.md": "docs/DOC_AIDER_CONTRACT.md",
    # Tools config
    "docs/tools-instructions-config.md": "docs/DOC_TOOLS_INSTRUCTIONS_CONFIG.md",
}

# Dev docs (move to developer/ as _DEV_)
DEV_MOVES = {
    "docs/.gitignore-recommendations.md": "developer/_DEV_GITIGNORE_RECOMMENDATIONS.md",
    "docs/ai-development-techniques.md": "developer/_DEV_AI_DEVELOPMENT_TECHNIQUES.md",
    "docs/README.md": "developer/_DEV_DOCS_README.md",  # Keep root README separate
}


def main():
    print("=== Batch Rename: docs/ files to DOC_ ===\n")

    renamed_count = 0
    moved_count = 0

    # Rename canonical docs
    print("Renaming canonical docs to DOC_ prefix:")
    for old_path_str, new_path_str in RENAMES.items():
        old_path = REPO_ROOT / old_path_str
        new_path = REPO_ROOT / new_path_str

        if old_path.exists():
            print(f"  {old_path.name} -> {new_path.name}")
            old_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"  [SKIP] Not found: {old_path}")

    # Move dev docs
    print("\nMoving dev docs to developer/ as _DEV_:")
    for old_path_str, new_path_str in DEV_MOVES.items():
        old_path = REPO_ROOT / old_path_str
        new_path = REPO_ROOT / new_path_str

        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"  {old_path.name} -> {new_path.name}")
            old_path.rename(new_path)
            moved_count += 1
        else:
            print(f"  [SKIP] Not found: {old_path}")

    print(f"\n=== Summary ===")
    print(f"Renamed: {renamed_count}")
    print(f"Moved to developer/: {moved_count}")
    print(f"Total processed: {renamed_count + moved_count}")


if __name__ == "__main__":
    main()
