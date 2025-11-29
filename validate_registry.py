#!/usr/bin/env python3
from pathlib import Path
import yaml

registry_path = Path('doc_id/specs/DOC_ID_REGISTRY.yaml')
if registry_path.exists():
    data = yaml.safe_load(registry_path.read_text(encoding='utf-8'))
    print('Registry loaded successfully')
    print(f'Total docs metadata: {data["metadata"]["total_docs"]}')
    print(f'Categories: {len(data["categories"])}')
    
    # Count actual docs
    actual_count = len(data.get('docs', []))
    print(f'Actual doc entries: {actual_count}')
    
    # Check for duplicates
    doc_ids = [d['doc_id'] for d in data.get('docs', [])]
    duplicates = [x for x in set(doc_ids) if doc_ids.count(x) > 1]
    if duplicates:
        print(f'Duplicate doc_ids: {len(duplicates)}')
        for dup in duplicates[:5]:
            print(f'  - {dup}')
    else:
        print('No duplicates')
    
    print('\nValidation complete')
else:
    print(f'Registry not found at {registry_path}')
