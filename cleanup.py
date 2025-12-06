# DOC_LINK: DOC-CORE-ROOT-CLEANUP-764
import shutil
from pathlib import Path
from datetime import datetime

SAFE_TO_ARCHIVE = {
    'Module-Centric': 'Architecture docs',
    'REFACTOR_2': 'Planning docs',
    'bring_back_docs_': 'Recovery docs',
    'ToDo_Task': 'Sandbox',
    'AI_SANDBOX': 'Experimental',
    'ai-logs-analyzer': 'Config only',
    'abstraction': 'Old status script',
}

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
archive_dir = Path('archive') / f'{timestamp}_deprecated_folders'
archive_dir.mkdir(parents=True, exist_ok=True)

print(f'Archive: {archive_dir}\n')

archived = []
for folder in SAFE_TO_ARCHIVE:
    src = Path(folder)
    if src.exists():
        dest = archive_dir / folder
        print(f'{folder}/ -> archive/')
        shutil.move(str(src), str(dest))
        archived.append(folder)

print(f'\nDone! Archived {len(archived)} folders')
print('Kept: src/ (active code)')
