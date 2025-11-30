#!/usr/bin/env python3
"""
Write doc_ids from registry into actual files' front matter
"""
DOC_ID: DOC-PAT-WRITE-DOC-IDS-TO-FILES-349
DOC_ID: DOC-PAT-WRITE-DOC-IDS-TO-FILES-305
DOC_ID: DOC-PAT-WRITE-DOC-IDS-TO-FILES-290
DOC_ID: DOC-PAT-WRITE-DOC-IDS-TO-FILES-275

from pathlib import Path
import yaml
import re
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

REGISTRY_PATH = Path('doc_id/specs/DOC_ID_REGISTRY.yaml')

# Load registry
print(f'Loading registry: {REGISTRY_PATH}')
registry_data = yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8'))

updated_count = 0
error_count = 0

for doc in registry_data['docs']:
    doc_id = doc['doc_id']
    artifacts = doc.get('artifacts', [])
    
    for artifact in artifacts:
        if artifact.get('type') in ['doc', None]:  # None means default to doc
            file_path = Path(artifact['path'])
            
            if not file_path.exists():
                print(f'  SKIP (not found): {file_path}')
                error_count += 1
                continue
            
            # Read file
            content = file_path.read_text(encoding='utf-8')
            
            # Check if already has doc_id in front matter
            if content.startswith('---'):
                # Extract front matter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter_str = parts[1]
                    body = parts[2]
                    
                    # Parse YAML
                    try:
                        front_matter = yaml.safe_load(front_matter_str)
                        if front_matter is None:
                            front_matter = {}
                        
                        # Add or update doc_id
                        if front_matter.get('doc_id') != doc_id:
                            front_matter['doc_id'] = doc_id
                            
                            # Write back
                            new_front_matter = yaml.dump(front_matter, default_flow_style=False, sort_keys=False)
                            new_content = f'---\n{new_front_matter}---{body}'
                            file_path.write_text(new_content, encoding='utf-8')
                            
                            print(f'  OK {file_path}: {doc_id}')
                            updated_count += 1
                        else:
                            print(f'  SKIP {file_path}: {doc_id} (already set)')
                    except yaml.YAMLError as e:
                        print(f'  ERROR parsing YAML in {file_path}: {e}')
                        error_count += 1
                else:
                    print(f'  ERROR: Invalid front matter in {file_path}')
                    error_count += 1
            else:
                print(f'  SKIP (no front matter): {file_path}')
                error_count += 1

print(f'\nComplete')
print(f'  Updated: {updated_count}')
print(f'  Errors/Skipped: {error_count}')
