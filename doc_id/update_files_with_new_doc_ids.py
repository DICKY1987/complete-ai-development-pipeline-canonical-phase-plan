#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DOC_LINK: DOC-SCRIPT-UPDATE-FILES-WITH-NEW-DOC-IDS-005
"""
Update Files with New Doc_IDs

PURPOSE: Update files that had duplicate doc_ids with their new unique IDs from inventory
PATTERN: PAT-DOC-ID-UPDATE-FILES-001

This script:
1. Compares current file doc_ids with inventory doc_ids
2. Updates files where they differ
3. Handles all file types (Python, YAML, JSON, Markdown, Scripts)

USAGE:
    python doc_id/update_files_with_new_doc_ids.py --dry-run
    python doc_id/update_files_with_new_doc_ids.py --limit 50
    python doc_id/update_files_with_new_doc_ids.py
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).parent.parent
INVENTORY_PATH = REPO_ROOT / "docs_inventory.jsonl"


def extract_doc_id_from_file(file_path: Path) -> Optional[str]:
    """Extract current doc_id from file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        return None
    
    # Look for DOC- pattern
    matches = re.findall(r'DOC-[A-Z0-9]+-[A-Z0-9-]+(?:-\d{3})?', content)
    return matches[0] if matches else None


def update_doc_id_in_file(file_path: Path, old_doc_id: str, new_doc_id: str) -> Tuple[bool, str]:
    """Update doc_id in file. Returns (success, new_content_or_error)."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return False, str(e)
    
    # Replace all occurrences
    new_content = content.replace(old_doc_id, new_doc_id)
    
    if new_content == content:
        return False, "No changes (doc_id not found or already updated)"
    
    return True, new_content


def main():
    parser = argparse.ArgumentParser(description="Update Files with New Doc_IDs")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--limit', type=int, help='Limit number of files to update')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("UPDATING FILES WITH NEW DOC_IDS FROM INVENTORY")
    print("=" * 70)
    print()
    
    # Load inventory
    inventory = {}
    with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry.get('doc_id') and entry.get('status') == 'registered':
                inventory[entry['path']] = entry['doc_id']
    
    print(f"Loaded {len(inventory)} entries from inventory\n")
    
    # Check each file
    updates_needed = []
    
    for path_str, inventory_doc_id in inventory.items():
        file_path = REPO_ROOT / path_str
        
        if not file_path.exists():
            continue
        
        file_doc_id = extract_doc_id_from_file(file_path)
        
        if file_doc_id and file_doc_id != inventory_doc_id:
            updates_needed.append({
                'path': file_path,
                'old_id': file_doc_id,
                'new_id': inventory_doc_id
            })
    
    print(f"Found {len(updates_needed)} files needing updates\n")
    
    if not updates_needed:
        print("✅ All files already up-to-date!")
        return
    
    # Apply limit if specified
    if args.limit:
        updates_needed = updates_needed[:args.limit]
        print(f"Limiting to first {args.limit} files\n")
    
    # Apply updates
    success_count = 0
    error_count = 0
    errors = []
    
    for idx, update in enumerate(updates_needed, 1):
        file_path = update['path']
        old_id = update['old_id']
        new_id = update['new_id']
        
        success, result = update_doc_id_in_file(file_path, old_id, new_id)
        
        if success:
            if not args.dry_run:
                try:
                    file_path.write_text(result, encoding='utf-8')
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        errors.append(f"{file_path}: {e}")
            else:
                success_count += 1
            
            if idx % 20 == 0 or idx <= 10:
                rel_path = file_path.relative_to(REPO_ROOT)
                print(f"  [{idx}/{len(updates_needed)}] {rel_path}")
                print(f"      {old_id}")
                print(f"      → {new_id}")
        else:
            error_count += 1
            if error_count <= 5:
                errors.append(f"{file_path}: {result}")
    
    # Summary
    print()
    print("=" * 70)
    print(f"{'DRY RUN SUMMARY' if args.dry_run else 'SUMMARY'}")
    print("=" * 70)
    print(f"  Files checked:      {len(inventory)}")
    print(f"  Updates needed:     {len(updates_needed)}")
    print(f"  {'Would update' if args.dry_run else 'Updated'}:        {success_count}")
    print(f"  Errors:             {error_count}")
    
    if errors:
        print(f"\nFirst {len(errors)} errors:")
        for error in errors:
            print(f"  ⚠️  {error}")
    
    if args.dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Files updated!")
        print(f"\n📋 Next steps:")
        print(f"   1. Review changes: git diff")
        print(f"   2. Run: python doc_id/doc_id_scanner.py scan")
        print(f"   3. Run: python doc_id/sync_registries.py sync")
        print(f"   4. Run: pytest doc_id/test_doc_id_system.py -v")


if __name__ == '__main__':
    main()
