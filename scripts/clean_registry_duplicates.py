#!/usr/bin/env python3
"""
Quick script to remove duplicate config entries from DOC_ID_REGISTRY.yaml
Keeps only the first occurrence of each config file (lowest sequence number)
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-CLEAN-REGISTRY-DUPLICATES-198
DOC_ID: DOC-SCRIPT-SCRIPTS-CLEAN-REGISTRY-DUPLICATES-135

import yaml
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "DOC_ID_REGISTRY.yaml"

def clean_duplicates():
    # Load registry
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Find config docs
    config_docs = [doc for doc in data['docs'] if doc['category'] == 'config']
    
    print(f"Found {len(config_docs)} config entries")
    
    # Group by name
    by_name = {}
    for doc in config_docs:
        name = doc['name']
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(doc)
    
    # Find duplicates
    duplicates_to_remove = []
    for name, docs in by_name.items():
        if len(docs) > 1:
            print(f"  {name}: {len(docs)} entries")
            # Keep first (lowest sequence), remove rest
            sorted_docs = sorted(docs, key=lambda d: int(d['doc_id'].split('-')[-1]))
            keep = sorted_docs[0]
            remove = sorted_docs[1:]
            print(f"    Keep: {keep['doc_id']}")
            for r in remove:
                print(f"    Remove: {r['doc_id']}")
                duplicates_to_remove.append(r['doc_id'])
    
    # Remove duplicates
    data['docs'] = [doc for doc in data['docs'] if doc['doc_id'] not in duplicates_to_remove]
    
    # Update counts
    config_count = len([doc for doc in data['docs'] if doc['category'] == 'config'])
    data['categories']['config']['count'] = config_count
    data['categories']['config']['next_id'] = config_count + 1
    
    # Update total
    data['metadata']['total_docs'] = len(data['docs'])
    
    print(f"\nCleaned registry:")
    print(f"  Removed {len(duplicates_to_remove)} duplicates")
    print(f"  Config count: {config_count}")
    print(f"  Total docs: {len(data['docs'])}")
    
    # Save
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n[OK] Registry cleaned and saved")

if __name__ == '__main__':
    clean_duplicates()
