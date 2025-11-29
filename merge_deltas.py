#!/usr/bin/env python3
"""
Merge delta files into the DOC_ID registry
"""

from pathlib import Path
import yaml
import json
import sys
from datetime import datetime

REGISTRY_PATH = Path('doc_id/specs/DOC_ID_REGISTRY.yaml')

if len(sys.argv) < 2:
    print('Usage: python merge_deltas.py <delta_file.jsonl>')
    sys.exit(1)

delta_file = Path(sys.argv[1])
if not delta_file.exists():
    print(f'Error: Delta file not found: {delta_file}')
    sys.exit(1)

# Load registry
print(f'Loading registry: {REGISTRY_PATH}')
registry_data = yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8'))

# Load deltas
deltas = []
with open(delta_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            deltas.append(json.loads(line))

print(f'Loaded {len(deltas)} deltas from {delta_file}')

# Track category updates
category_updates = {}

# Add each delta to docs
existing_doc_ids = {d['doc_id'] for d in registry_data.get('docs', [])}
added_count = 0
skipped_count = 0

for delta in deltas:
    doc_id = delta['doc_id']
    
    if doc_id in existing_doc_ids:
        print(f'  SKIP (duplicate): {doc_id}')
        skipped_count += 1
        continue
    
    # Add to docs list
    doc_entry = {
        'doc_id': doc_id,
        'category': delta['category'],
        'name': delta['logical_name'].lower().replace('_', '-'),
        'title': delta['title'],
        'status': 'active',
        'artifacts': delta['artifacts'],
        'created': delta['created'],
        'last_modified': delta['created'],
        'tags': delta.get('tags', [])
    }
    
    registry_data['docs'].append(doc_entry)
    existing_doc_ids.add(doc_id)
    
    # Track category count
    category = delta['category']
    category_updates[category] = category_updates.get(category, 0) + 1
    
    print(f'  ADD: {doc_id}')
    added_count += 1

# Update category counts and next_ids
for category, count in category_updates.items():
    if category in registry_data['categories']:
        cat_data = registry_data['categories'][category]
        cat_data['count'] = cat_data.get('count', 0) + count
        # next_id is already incremented in batch_mint.py logic
        # We need to find the max ID used and set next_id accordingly
        max_id = 0
        prefix = cat_data['prefix']
        for doc in registry_data['docs']:
            if doc['doc_id'].startswith(f'DOC-{prefix}-'):
                parts = doc['doc_id'].split('-')
                try:
                    num = int(parts[-1])
                    max_id = max(max_id, num)
                except (ValueError, IndexError):
                    pass
        cat_data['next_id'] = max_id + 1

# Update metadata
registry_data['metadata']['total_docs'] = len(registry_data['docs'])
registry_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

# Save registry
print(f'\nWriting updated registry to: {REGISTRY_PATH}')
with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
    yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f'\n✓ Merge complete')
print(f'  Added: {added_count}')
print(f'  Skipped (duplicates): {skipped_count}')
print(f'  Total docs now: {registry_data["metadata"]["total_docs"]}')
print(f'\nCategory updates:')
for category, count in sorted(category_updates.items()):
    cat_data = registry_data['categories'][category]
    print(f'  {category}: +{count} (total: {cat_data["count"]}, next_id: {cat_data["next_id"]})')
