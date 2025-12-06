#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DOC_LINK: DOC-SCRIPT-APPLY-DOC-ID-CHANGES-004
"""
Apply Doc_ID Changes to Files

PURPOSE: Update actual files with new doc_ids from inventory
PATTERN: PAT-DOC-ID-APPLY-CHANGES-001

USAGE:
    python doc_id/apply_doc_id_changes_to_files.py --dry-run
    python doc_id/apply_doc_id_changes_to_files.py
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent
INVENTORY_PATH = REPO_ROOT / "docs_inventory.jsonl"


def load_inventory() -> List[dict]:
    """Load inventory with all entries."""
    entries = []
    with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            entries.append(json.loads(line.strip()))
    return entries


def find_and_replace_doc_id(file_path: Path, old_doc_id: str, new_doc_id: str) -> Tuple[bool, str]:
    """Find and replace doc_id in file. Returns (success, error_message)."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    original_content = content
    
    # Try different patterns based on file type
    suffix = file_path.suffix.lower()
    
    if suffix == '.py':
        # Python: # DOC_ID: or DOC_LINK: or """DOC_ID:
        patterns = [
            (rf'# DOC_ID:\s*{re.escape(old_doc_id)}', f'# DOC_ID: {new_doc_id}'),
            (rf'# DOC_LINK:\s*{re.escape(old_doc_id)}', f'# DOC_LINK: {new_doc_id}'),
            (rf'DOC_ID:\s*{re.escape(old_doc_id)}', f'DOC_ID: {new_doc_id}'),
            (rf'DOC_LINK:\s*{re.escape(old_doc_id)}', f'DOC_LINK: {new_doc_id}'),
        ]
    elif suffix in ['.yaml', '.yml']:
        # YAML: doc_id: field
        patterns = [
            (rf'^doc_id:\s*{re.escape(old_doc_id)}', f'doc_id: {new_doc_id}', re.MULTILINE),
            (rf"^doc_id:\s*['\"]?{re.escape(old_doc_id)}['\"]?", f'doc_id: {new_doc_id}', re.MULTILINE),
        ]
    elif suffix == '.json':
        # JSON: "doc_id": field
        patterns = [
            (rf'"doc_id"\s*:\s*"{re.escape(old_doc_id)}"', f'"doc_id": "{new_doc_id}"'),
        ]
    elif suffix in ['.md', '.txt']:
        # Markdown: YAML frontmatter
        patterns = [
            (rf'^doc_id:\s*{re.escape(old_doc_id)}', f'doc_id: {new_doc_id}', re.MULTILINE),
        ]
    elif suffix in ['.ps1', '.sh']:
        # Scripts: # DOC_LINK:
        patterns = [
            (rf'# DOC_LINK:\s*{re.escape(old_doc_id)}', f'# DOC_LINK: {new_doc_id}'),
        ]
    else:
        # Generic: try common patterns
        patterns = [
            (rf'doc_id:\s*{re.escape(old_doc_id)}', f'doc_id: {new_doc_id}'),
            (rf'DOC_ID:\s*{re.escape(old_doc_id)}', f'DOC_ID: {new_doc_id}'),
            (rf'"doc_id"\s*:\s*"{re.escape(old_doc_id)}"', f'"doc_id": "{new_doc_id}"'),
        ]
    
    # Try each pattern
    replaced = False
    for pattern_data in patterns:
        if len(pattern_data) == 2:
            pattern, replacement = pattern_data
            flags = 0
        else:
            pattern, replacement, flags = pattern_data
        
        if re.search(pattern, content, flags):
            content = re.sub(pattern, replacement, content, flags=flags)
            replaced = True
            break
    
    if not replaced:
        return False, f"Could not find doc_id pattern in file"
    
    if content == original_content:
        return False, "No changes made (content identical)"
    
    return True, content


def apply_changes(dry_run: bool = True):
    """Apply doc_id changes from inventory to actual files."""
    print("=" * 70)
    print(f"APPLYING DOC_ID CHANGES TO FILES")
    print("=" * 70)
    print()
    
    # Load inventory
    entries = load_inventory()
    
    # Track changes needed
    changes_needed = []
    
    # Scan for entries that might have been updated
    # (We detect this by looking for entries with updated doc_ids that differ from file content)
    for entry in entries:
        file_path = REPO_ROOT / entry['path']
        doc_id = entry.get('doc_id')
        
        if not doc_id or not file_path.exists():
            continue
        
        # For now, we'll process all files and let the function determine if changes are needed
        # This is safe because we check if doc_id exists in file before replacing
        changes_needed.append({
            'path': file_path,
            'doc_id': doc_id,
            'entry': entry
        })
    
    print(f"Processing {len(changes_needed)} files...\n")
    
    # Apply changes
    success_count = 0
    skip_count = 0
    error_count = 0
    errors = []
    
    for idx, change in enumerate(changes_needed):
        file_path = change['path']
        new_doc_id = change['doc_id']
        
        # Try to read file and check if it needs updating
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check if file already has the new doc_id
            if new_doc_id in content:
                skip_count += 1
                continue
            
            # Try to find old doc_id in file
            # Look for any DOC- pattern
            old_doc_ids = re.findall(r'DOC-[A-Z0-9]+-[A-Z0-9-]+(?:-\d{3})?', content)
            
            if not old_doc_ids:
                skip_count += 1
                continue
            
            # Use the first found doc_id as the old one
            old_doc_id = old_doc_ids[0]
            
            if old_doc_id == new_doc_id:
                skip_count += 1
                continue
            
            # Apply replacement
            success, result = find_and_replace_doc_id(file_path, old_doc_id, new_doc_id)
            
            if success:
                if not dry_run:
                    file_path.write_text(result, encoding='utf-8')
                    if (idx + 1) % 10 == 0:
                        print(f"  ✓ Processed {idx + 1}/{len(changes_needed)} files...")
                success_count += 1
            else:
                error_count += 1
                if error_count <= 10:  # Show first 10 errors
                    errors.append(f"{file_path}: {result}")
        
        except Exception as e:
            error_count += 1
            if error_count <= 10:
                errors.append(f"{file_path}: {e}")
    
    print()
    print("=" * 70)
    print(f"{'DRY RUN SUMMARY' if dry_run else 'SUMMARY'}")
    print("=" * 70)
    print(f"  Files processed:  {len(changes_needed)}")
    print(f"  {'Would update' if dry_run else 'Updated'}:      {success_count}")
    print(f"  Skipped:          {skip_count} (already up-to-date)")
    print(f"  Errors:           {error_count}")
    
    if errors:
        print(f"\nFirst {len(errors)} errors:")
        for error in errors:
            print(f"  ⚠️  {error}")
    
    if dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Changes applied!")
        print(f"\n📋 Next steps:")
        print(f"   1. Review changes: git diff")
        print(f"   2. Run: python doc_id/doc_id_scanner.py scan")
        print(f"   3. Run: python doc_id/sync_registries.py sync")
        print(f"   4. Run: pytest doc_id/test_doc_id_system.py -v")


def main():
    parser = argparse.ArgumentParser(description="Apply Doc_ID Changes to Files")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    
    args = parser.parse_args()
    apply_changes(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
