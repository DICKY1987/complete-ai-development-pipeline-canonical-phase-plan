#!/usr/bin/env python3
"""
Batch mint doc_ids from batch specifications
Generates deltas for later merge
"""
DOC_ID: DOC-PAT-BATCH-MINT-337
DOC_ID: DOC-PAT-BATCH-MINT-293
DOC_ID: DOC-PAT-BATCH-MINT-278
DOC_ID: DOC-PAT-BATCH-MINT-263

from pathlib import Path
import yaml
import json
import sys
from datetime import datetime

# Registry structure
REGISTRY_PATH = Path('doc_id/specs/DOC_ID_REGISTRY.yaml')
BATCHES_DIR = Path('doc_id/batches')
DELTAS_DIR = Path('doc_id/deltas')

DELTAS_DIR.mkdir(exist_ok=True)

# Load registry
registry_data = yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8'))

# Process all batch files
batch_files = sorted(BATCHES_DIR.glob('batch_*.yaml'))
all_deltas = []

for batch_file in batch_files:
    print(f'\nProcessing: {batch_file.name}')
    batch = yaml.safe_load(batch_file.read_text(encoding='utf-8'))
    
    category = batch['category']
    
    # Get category data
    if category not in registry_data['categories']:
        print(f'  ERROR: Unknown category {category}')
        continue
        
    cat_data = registry_data['categories'][category]
    prefix = cat_data['prefix']
    next_id = cat_data['next_id']
    
    batch_deltas = []
    
    for item in batch['items']:
        logical_name = item['logical_name']
        title = item['title']
        artifacts = item['artifacts']
        
        # Generate doc_id
        doc_id = f"DOC-{prefix}-{logical_name}-{next_id:03d}"
        
        # Create delta entry
        delta = {
            'doc_id': doc_id,
            'logical_name': logical_name,
            'title': title,
            'category': category,
            'artifacts': artifacts,
            'tags': batch.get('tags', []),
            'created': datetime.now().strftime('%Y-%m-%d'),
            'batch_id': batch['batch_id']
        }
        
        batch_deltas.append(delta)
        all_deltas.append(delta)
        
        print(f'  ✓ {doc_id}: {title}')
        
        next_id += 1
    
    # Update category counter (in-memory only)
    cat_data['next_id'] = next_id
    cat_data['count'] = cat_data.get('count', 0) + len(batch_deltas)

# Write all deltas to JSONL
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
delta_file = DELTAS_DIR / f'delta_batch_mint_{timestamp}.jsonl'

with open(delta_file, 'w', encoding='utf-8') as f:
    for delta in all_deltas:
        f.write(json.dumps(delta) + '\n')

print(f'\n✓ Generated {len(all_deltas)} doc_ids')
print(f'✓ Delta file: {delta_file}')
print(f'\nNext step: Merge deltas into registry')
print(f'  python merge_deltas.py {delta_file}')
