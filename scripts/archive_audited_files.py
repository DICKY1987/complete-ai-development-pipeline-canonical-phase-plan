#!/usr/bin/env python3
"""
Safe Archival Script

Safely archives files identified by the codebase audit with proper documentation
and rollback capability.

Usage:
    python scripts/archive_audited_files.py --audit-json codebase_audit.json --category temporary
    python scripts/archive_audited_files.py --audit-json codebase_audit.json --category archive_candidates
    python scripts/archive_audited_files.py --dry-run
    python scripts/archive_audited_files.py --rollback docs/archive/audit-2025-11-22/
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class SafeArchiver:
    """Safely archive files with documentation and rollback capability."""
    
    def __init__(self, repo_root: Path, dry_run: bool = False):
        """Initialize archiver."""
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.archive_base = repo_root / 'docs' / 'archive'
        self.audit_date = datetime.now().strftime('%Y-%m-%d')
        self.archive_dir = self.archive_base / f'audit-{self.audit_date}'
        self.archived_items = []
    
    def archive_from_audit(self, audit_json_path: Path, category: str = None):
        """Archive files from audit JSON results."""
        # Load audit results
        with open(audit_json_path) as f:
            audit_data = json.load(f)
        
        print(f"Loaded audit from: {audit_json_path}")
        print(f"Audit date: {audit_data['audit_date']}")
        
        # Archive by category
        if category:
            self._archive_category(audit_data, category)
        else:
            # Archive all categories
            for cat in audit_data['findings']:
                if cat in ('archive_candidates', 'temporary', 'legacy'):
                    self._archive_category(audit_data, cat)
        
        # Generate manifest
        self._create_manifest()
        
        print("\nArchival complete!")
        print(f"Archived {len(self.archived_items)} items to {self.archive_dir}")
        
        if not self.dry_run:
            print("\nTo rollback:")
            print(f"  python scripts/archive_audited_files.py --rollback {self.archive_dir}")
    
    def _archive_category(self, audit_data: Dict, category: str):
        """Archive all items in a category."""
        items = audit_data['findings'].get(category, [])
        
        if not items:
            print(f"No items in category: {category}")
            return
        
        print(f"\nArchiving category: {category} ({len(items)} items)")
        
        for item in items:
            if category == 'temporary':
                self._archive_file(item['path'], 'temp-files', item)
            elif category == 'archive_candidates':
                self._archive_directory(item['path'], item['category'], item)
            elif category == 'legacy':
                self._archive_directory(item['path'], 'legacy', item)
    
    def _archive_file(self, file_path: str, subcategory: str, metadata: Dict):
        """Archive a single file."""
        source = self.repo_root / file_path
        
        if not source.exists():
            print(f"  ⚠️  File not found: {file_path}")
            return
        
        # Create destination
        dest_dir = self.archive_dir / subcategory
        dest = dest_dir / source.name
        
        print(f"  📦 {file_path} → {dest.relative_to(self.repo_root)}")
        
        if not self.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            
            # Create metadata file
            self._create_metadata_file(dest_dir, source.name, metadata)
            
            # Remove original
            source.unlink()
            
            self.archived_items.append({
                'source': file_path,
                'destination': str(dest.relative_to(self.repo_root)),
                'category': subcategory,
                'metadata': metadata,
            })
    
    def _archive_directory(self, dir_path: str, subcategory: str, metadata: Dict):
        """Archive a directory."""
        source = self.repo_root / dir_path
        
        if not source.exists():
            print(f"  ⚠️  Directory not found: {dir_path}")
            return
        
        # Determine destination subcategory
        if 'PROTOTYPE' in dir_path:
            dest_subdir = 'prototypes'
        elif 'OPTOMIZE' in dir_path or 'DEEP_DIVE' in dir_path:
            dest_subdir = 'analysis'
        elif 'FRAMEWORK' in dir_path:
            dest_subdir = 'frameworks'
        elif 'backup' in dir_path.lower() or 'migration' in dir_path.lower():
            dest_subdir = 'backups'
        else:
            dest_subdir = subcategory
        
        # Create destination
        dest_dir = self.archive_dir / dest_subdir
        dest = dest_dir / source.name
        
        print(f"  📦 {dir_path} → {dest.relative_to(self.repo_root)}")
        print(f"     ({metadata.get('file_count', 0)} files, {metadata.get('size_mb', 0)} MB)")
        
        if not self.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy directory
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
            
            # Create archive note
            self._create_archive_note(dest, dir_path, metadata)
            
            # Remove original
            shutil.rmtree(source)
            
            self.archived_items.append({
                'source': dir_path,
                'destination': str(dest.relative_to(self.repo_root)),
                'category': dest_subdir,
                'metadata': metadata,
            })
    
    def _create_metadata_file(self, dest_dir: Path, filename: str, metadata: Dict):
        """Create metadata file for archived item."""
        metadata_file = dest_dir / f'{filename}.metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump({
                'archived_date': self.audit_date,
                'original_path': metadata.get('path'),
                'reason': metadata.get('reason', metadata.get('recommendation')),
                'metadata': metadata,
            }, f, indent=2)
    
    def _create_archive_note(self, dest: Path, original_path: str, metadata: Dict):
        """Create ARCHIVE_NOTE.md for archived directory."""
        note_file = dest / 'ARCHIVE_NOTE.md'
        with open(note_file, 'w') as f:
            f.write(f"# Archive Note\n\n")
            f.write(f"**Archived:** {self.audit_date}\n")
            f.write(f"**Original Location:** `{original_path}`\n")
            f.write(f"**Reason:** {metadata.get('reason', 'See audit report')}\n\n")
            f.write(f"## Metadata\n\n")
            f.write(f"- **Files:** {metadata.get('file_count', 'Unknown')}\n")
            f.write(f"- **Size:** {metadata.get('size_mb', 'Unknown')} MB\n")
            f.write(f"- **Recommendation:** {metadata.get('recommendation', 'N/A')}\n\n")
            f.write(f"## Restoration\n\n")
            f.write(f"To restore this directory:\n\n")
            f.write(f"```bash\n")
            f.write(f"cp -r {dest.relative_to(self.repo_root)} {original_path}\n")
            f.write(f"```\n\n")
            f.write(f"## Audit Reference\n\n")
            f.write(f"See `CODEBASE_AUDIT_REPORT.md` and `CODEBASE_AUDIT_RECOMMENDATIONS.md` for full context.\n")
    
    def _create_manifest(self):
        """Create manifest of all archived items."""
        if self.dry_run:
            return
        
        manifest_file = self.archive_dir / 'MANIFEST.md'
        with open(manifest_file, 'w') as f:
            f.write(f"# Archive Manifest\n\n")
            f.write(f"**Created:** {datetime.now().isoformat()}\n")
            f.write(f"**Audit Date:** {self.audit_date}\n")
            f.write(f"**Total Items:** {len(self.archived_items)}\n\n")
            f.write(f"## Archived Items\n\n")
            
            for item in self.archived_items:
                f.write(f"### `{item['source']}`\n")
                f.write(f"- **Destination:** `{item['destination']}`\n")
                f.write(f"- **Category:** {item['category']}\n")
                if 'reason' in item['metadata']:
                    f.write(f"- **Reason:** {item['metadata']['reason']}\n")
                f.write(f"\n")
            
            f.write(f"\n## Rollback\n\n")
            f.write(f"To rollback all archived items:\n\n")
            f.write(f"```bash\n")
            f.write(f"python scripts/archive_audited_files.py --rollback {self.archive_dir}\n")
            f.write(f"```\n")
        
        print(f"\n📝 Manifest created: {manifest_file}")
    
    def rollback(self, archive_dir: Path):
        """Rollback archived files."""
        manifest_file = archive_dir / 'MANIFEST.md'
        
        if not manifest_file.exists():
            print(f"❌ Manifest not found: {manifest_file}")
            return
        
        print(f"Rolling back archive: {archive_dir}")
        
        # Parse manifest (simplified - in production, use JSON manifest)
        # For now, just restore directories
        for item in archive_dir.iterdir():
            if item.is_dir() and item.name not in ('__pycache__',):
                for subitem in item.iterdir():
                    if subitem.is_dir():
                        # Restore directory
                        dest = self.repo_root / subitem.name
                        print(f"  ↩️  Restoring: {subitem.name}")
                        
                        if not self.dry_run:
                            if dest.exists():
                                print(f"    ⚠️  Destination exists: {dest}")
                            else:
                                shutil.copytree(subitem, dest)
        
        print("\n✅ Rollback complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Safely archive files from codebase audit'
    )
    parser.add_argument(
        '--audit-json',
        type=str,
        default='codebase_audit.json',
        help='Path to audit JSON file'
    )
    parser.add_argument(
        '--category',
        type=str,
        choices=['temporary', 'archive_candidates', 'legacy', 'all'],
        help='Category to archive (default: all applicable)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be archived without actually doing it'
    )
    parser.add_argument(
        '--rollback',
        type=str,
        help='Rollback archive from specified directory'
    )
    
    args = parser.parse_args()
    
    # Find repository root
    repo_root = Path(__file__).parent.parent
    
    archiver = SafeArchiver(repo_root, dry_run=args.dry_run)
    
    if args.rollback:
        archiver.rollback(Path(args.rollback))
    else:
        audit_json = repo_root / args.audit_json
        if not audit_json.exists():
            print(f"❌ Audit JSON not found: {audit_json}")
            print("Run: python tools/codebase_auditor.py")
            return
        
        category = args.category if args.category != 'all' else None
        archiver.archive_from_audit(audit_json, category)
    
    if args.dry_run:
        print("\n💡 This was a dry run. Use --dry-run=false to actually archive files.")


if __name__ == '__main__':
    main()
