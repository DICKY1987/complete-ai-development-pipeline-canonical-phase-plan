#!/usr/bin/env python3
"""
Safe cleanup script for deprecated and overlapping folders.
Creates an archive with full backup before removal.


DOC_ID: DOC-CORE-ROOT-SAFE-CLEANUP-DEPRECATED-FOLDERS-765
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path

# Safe to archive - no Python code, docs/planning only
SAFE_TO_ARCHIVE = {
    'Module-Centric': {
        'reason': 'Documentation migrated to docs/',
        'files': 34,
        'contains': 'Architecture docs, migration guides'
    },
    'REFACTOR_2': {
        'reason': 'Planning docs - archived',
        'files': 39,
        'contains': 'Planning and architecture documents'
    },
    'bring_back_docs_': {
        'reason': 'Recovery docs - should be in docs/',
        'files': 10,
        'contains': 'Recovered documentation'
    },
    'ToDo_Task': {
        'reason': 'Sandbox/experimental - archive',
        'files': 74,
        'contains': 'Task planning and tracking materials'
    },
    'AI_SANDBOX': {
        'reason': 'Experimental - minimal content',
        'files': 4,
        'contains': 'AI experimentation sandbox'
    },
    'ai-logs-analyzer': {
        'reason': 'Feature service - no Python code found',
        'files': 20,
        'contains': 'Config and scripts (no active code)'
    },
}

# Needs manual review - contains Python code
NEEDS_REVIEW = {
    'src': {
        'reason': 'Deprecated - 3 Python files still referenced',
        'files': 3,
        'action': 'Check imports before archiving',
        'references': [
            'aider/engine.py',
            'tests/test_path_registry.py',
            'scripts/auto_migrate_imports.py'
        ]
    },
    'abstraction': {
        'reason': 'Old workstream generation - 1 Python file',
        'files': 20,
        'action': 'Review implement_all_phases.py before archiving',
        'py_files': ['implement_all_phases.py']
    },
}

def create_archive_dir():
    """Create timestamped archive directory"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_dir = Path('archive') / f'{timestamp}_deprecated_folders_cleanup'
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir

def archive_folder(folder, archive_dir):
    """Move folder to archive with metadata"""
    src = Path(folder)
    if not src.exists():
        print(f'⚠️  Folder not found: {folder}')
        return False
    
    dest = archive_dir / folder
    print(f'📦 Archiving {folder}/ → {dest}/')
    
    try:
        shutil.move(str(src), str(dest))
        print(f'   ✅ Moved successfully')
        return True
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def create_archive_readme(archive_dir, archived, skipped):
    """Create README in archive explaining what was archived"""
    readme_content = f"""# Deprecated Folders Cleanup Archive

**Date**: {datetime.now().isoformat()}
**Purpose**: Remove deprecated/overlapping folders to reduce confusion

## Folders Archived ({len(archived)})

"""
    
    for folder, info in archived.items():
        readme_content += f"""### {folder}/
- **Reason**: {info['reason']}
- **Files**: {info['files']}
- **Contents**: {info['contains']}

"""
    
    if skipped:
        readme_content += f"""## Folders Skipped (Needs Review) ({len(skipped)})

"""
        for folder, info in skipped.items():
            readme_content += f"""### {folder}/
- **Reason**: {info['reason']}
- **Action Required**: {info['action']}
- **Files**: {info['files']}
"""
            if 'references' in info:
                readme_content += "- **Referenced by**:\n"
                for ref in info['references']:
                    readme_content += f"  - `{ref}`\n"
            if 'py_files' in info:
                readme_content += "- **Python files**:\n"
                for py in info['py_files']:
                    readme_content += f"  - `{py}`\n"
            readme_content += "\n"
    
    readme_content += """## Restoration

If you need to restore any folder:

```bash
# Restore specific folder
cp -r archive/{timestamp}_deprecated_folders_cleanup/{folder} ./

# Or use git if committed
git checkout HEAD~1 {folder}
```

## Background

These folders were identified as deprecated based on:
1. **FOLDER_OVERLAP_ANALYSIS.md** - UET migration analysis
2. **OLD_FOLDERS_CLEANUP_PLAN.md** - Cleanup recommendations
3. **FOLDER_CLASSIFICATION.yaml** - Module classification

The code is either:
- Migrated to UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
- Documentation moved to docs/
- Planning materials (no longer active)
- Experimental/sandbox content
"""
    
    readme_path = archive_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f'\n📄 Archive README created: {readme_path}')

def create_cleanup_summary(archive_dir, results):
    """Create JSON summary of cleanup"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'archive_location': str(archive_dir),
        'results': results
    }
    
    summary_path = archive_dir / 'cleanup_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f'📊 Cleanup summary: {summary_path}')

def main():
    print('🧹 Safe Cleanup of Deprecated Folders\n')
    print('=' * 60)
    
    # Create archive directory
    archive_dir = create_archive_dir()
    print(f'\n📁 Archive directory: {archive_dir}\n')
    
    # Archive safe folders
    print('📦 Archiving safe folders (no Python code)...\n')
    archived = {}
    
    for folder, info in SAFE_TO_ARCHIVE.items():
        if archive_folder(folder, archive_dir):
            archived[folder] = info
    
    # Report folders that need review
    print('\n⚠️  Folders needing manual review (skipped):\n')
    for folder, info in NEEDS_REVIEW.items():
        print(f'📁 {folder}/')
        print(f'   Reason: {info["reason"]}')
        print(f'   Action: {info["action"]}')
        print()
    
    # Create archive documentation
    print('\n📝 Creating archive documentation...\n')
    create_archive_readme(archive_dir, archived, NEEDS_REVIEW)
    
    results = {
        'archived': list(archived.keys()),
        'skipped': list(NEEDS_REVIEW.keys()),
        'archive_dir': str(archive_dir)
    }
    create_cleanup_summary(archive_dir, results)
    
    # Final summary
    print('\n' + '=' * 60)
    print('✅ CLEANUP COMPLETE\n')
    print(f'📊 Summary:')
    print(f'   Folders archived: {len(archived)}')
    print(f'   Folders skipped (need review): {len(NEEDS_REVIEW)}')
    print(f'   Archive location: {archive_dir}')
    print(f'\n📋 Next steps:')
    print(f'   1. Review skipped folders: {", ".join(NEEDS_REVIEW.keys())}')
    print(f'   2. Check imports from src/ (10 files reference it)')
    print(f'   3. Review abstraction/implement_all_phases.py')
    print(f'   4. Commit changes: git add . && git commit -m "chore: Archive deprecated folders"')

if __name__ == '__main__':
    main()
