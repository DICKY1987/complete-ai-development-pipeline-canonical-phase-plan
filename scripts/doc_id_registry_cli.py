#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-DOC-ID-REGISTRY-CLI-001
"""
DOC_ID Registry CLI

PURPOSE: Manage doc_id assignments across the repository
USAGE:
    python scripts/doc_id_registry_cli.py mint --category CORE --name SCHEDULER
    python scripts/doc_id_registry_cli.py validate
    python scripts/doc_id_registry_cli.py search --pattern "CORE-.*"
    python scripts/doc_id_registry_cli.py stats
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
import yaml
from datetime import datetime

# Repository root
REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "DOC_ID_REGISTRY.yaml"
DOC_ID_REGEX = re.compile(r"^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$")


class DocIDRegistry:
    """Manage the central DOC_ID registry."""
    
    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self.registry_path = registry_path
        self.data = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Load registry from YAML file."""
        if not self.registry_path.exists():
            print(f"❌ Registry not found: {self.registry_path}")
            sys.exit(1)
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save_registry(self):
        """Save registry back to YAML file."""
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Registry updated: {self.registry_path}")
    
    def mint_doc_id(self, category: str, name: str, title: str = None, 
                    artifacts: List[Dict] = None, tags: List[str] = None) -> str:
        """
        Mint a new doc_id.
        
        Args:
            category: Category prefix (e.g., 'core', 'error', 'patterns')
            name: Name segments (e.g., 'orchestrator', 'python-ruff')
            title: Human-readable title
            artifacts: List of artifact dicts with 'type' and 'path'
            tags: List of tags
        
        Returns:
            The new doc_id
        """
        category_lower = category.lower()
        
        if category_lower not in self.data['categories']:
            print(f"❌ Unknown category: {category}")
            print(f"Available: {', '.join(self.data['categories'].keys())}")
            sys.exit(1)
        
        cat_data = self.data['categories'][category_lower]
        prefix = cat_data['prefix']
        next_num = cat_data['next_id']
        
        # Convert name to uppercase with dashes
        name_upper = name.upper().replace('_', '-').replace(' ', '-')
        
        # Construct doc_id
        doc_id = f"DOC-{prefix}-{name_upper}-{next_num:03d}"
        
        # Validate format
        if not DOC_ID_REGEX.match(doc_id):
            print(f"❌ Generated doc_id failed validation: {doc_id}")
            sys.exit(1)
        
        # Check for duplicates
        existing = [d['doc_id'] for d in self.data['docs']]
        if doc_id in existing:
            print(f"❌ doc_id already exists: {doc_id}")
            sys.exit(1)
        
        # Create doc entry
        doc_entry = {
            'doc_id': doc_id,
            'category': category_lower,
            'name': name.lower().replace('-', '_'),
            'title': title or name,
            'status': 'active',
            'artifacts': artifacts or [],
            'created': datetime.now().strftime("%Y-%m-%d"),
            'last_modified': datetime.now().strftime("%Y-%m-%d"),
            'tags': tags or []
        }
        
        # Add to registry
        self.data['docs'].append(doc_entry)
        cat_data['next_id'] = next_num + 1
        cat_data['count'] = cat_data['count'] + 1
        self.data['metadata']['total_docs'] = len(self.data['docs'])
        
        self._save_registry()
        
        print(f"\n✅ Minted new doc_id: {doc_id}")
        print(f"   Category: {category_lower}")
        print(f"   Name: {name}")
        if title:
            print(f"   Title: {title}")
        
        return doc_id
    
    def validate_format(self, doc_id: str) -> bool:
        """Validate doc_id format."""
        return DOC_ID_REGEX.match(doc_id) is not None
    
    def search(self, pattern: str = None, category: str = None, 
               status: str = None) -> List[Dict]:
        """
        Search for doc_ids.
        
        Args:
            pattern: Regex pattern to match doc_id
            category: Filter by category
            status: Filter by status
        
        Returns:
            List of matching doc entries
        """
        results = self.data['docs']
        
        if category:
            results = [d for d in results if d['category'] == category.lower()]
        
        if status:
            results = [d for d in results if d['status'] == status]
        
        if pattern:
            regex = re.compile(pattern)
            results = [d for d in results if regex.search(d['doc_id'])]
        
        return results
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            'total_docs': len(self.data['docs']),
            'total_categories': len(self.data['categories']),
            'by_category': {
                cat: cat_data['count']
                for cat, cat_data in self.data['categories'].items()
            },
            'by_status': self._count_by_field('status'),
            'last_updated': self.data['metadata']['last_updated']
        }
    
    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count docs by field value."""
        counts = {}
        for doc in self.data['docs']:
            value = doc.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def validate_all(self) -> Dict:
        """
        Validate all doc_ids in registry.
        
        Returns:
            Validation report with errors and warnings
        """
        errors = []
        warnings = []
        
        seen_ids = set()
        
        for doc in self.data['docs']:
            doc_id = doc['doc_id']
            
            # Check format
            if not self.validate_format(doc_id):
                errors.append(f"Invalid format: {doc_id}")
            
            # Check duplicates
            if doc_id in seen_ids:
                errors.append(f"Duplicate doc_id: {doc_id}")
            seen_ids.add(doc_id)
            
            # Check artifacts exist
            for artifact in doc.get('artifacts', []):
                path = REPO_ROOT / artifact['path']
                if not path.exists():
                    warnings.append(f"Missing artifact: {artifact['path']} for {doc_id}")
        
        return {
            'total_docs': len(self.data['docs']),
            'errors': errors,
            'warnings': warnings,
            'valid': len(errors) == 0
        }


def cmd_mint(args):
    """Mint a new doc_id."""
    registry = DocIDRegistry()
    
    artifacts = []
    if args.artifact:
        for artifact_spec in args.artifact:
            atype, path = artifact_spec.split(':', 1)
            artifacts.append({'type': atype, 'path': path})
    
    tags = args.tags.split(',') if args.tags else []
    
    doc_id = registry.mint_doc_id(
        category=args.category,
        name=args.name,
        title=args.title,
        artifacts=artifacts,
        tags=tags
    )
    
    print(f"\n📋 Next steps:")
    print(f"   1. Add 'doc_id: {doc_id}' or 'DOC_LINK: {doc_id}' to your files")
    print(f"   2. Run validation: python scripts/doc_id_registry_cli.py validate")


def cmd_search(args):
    """Search for doc_ids."""
    registry = DocIDRegistry()
    
    results = registry.search(
        pattern=args.pattern,
        category=args.category,
        status=args.status
    )
    
    if not results:
        print("❌ No matching doc_ids found")
        return
    
    print(f"\n📋 Found {len(results)} doc_id(s):\n")
    
    for doc in results:
        print(f"  {doc['doc_id']}")
        print(f"    Category: {doc['category']}")
        print(f"    Name: {doc['name']}")
        print(f"    Status: {doc['status']}")
        if doc.get('title'):
            print(f"    Title: {doc['title']}")
        if doc.get('artifacts'):
            print(f"    Artifacts: {len(doc['artifacts'])}")
        print()


def cmd_validate(args):
    """Validate all doc_ids."""
    registry = DocIDRegistry()
    
    print("🔍 Validating DOC_ID registry...\n")
    
    report = registry.validate_all()
    
    print(f"Total docs: {report['total_docs']}")
    
    if report['errors']:
        print(f"\n❌ Errors ({len(report['errors'])}):")
        for err in report['errors']:
            print(f"   - {err}")
    
    if report['warnings']:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        for warn in report['warnings']:
            print(f"   - {warn}")
    
    if report['valid'] and not report['warnings']:
        print("\n✅ All doc_ids are valid!")
        return 0
    elif report['valid']:
        print("\n✅ Format valid, but warnings present")
        return 0
    else:
        print("\n❌ Validation failed")
        return 1


def cmd_stats(args):
    """Show registry statistics."""
    registry = DocIDRegistry()
    
    stats = registry.get_stats()
    
    print("\n📊 DOC_ID Registry Statistics\n")
    print(f"Total docs: {stats['total_docs']}")
    print(f"Total categories: {stats['total_categories']}")
    print(f"Last updated: {stats['last_updated']}")
    
    print(f"\nBy category:")
    for cat, count in sorted(stats['by_category'].items()):
        print(f"  {cat:12} {count:4d}")
    
    print(f"\nBy status:")
    for status, count in sorted(stats['by_status'].items()):
        print(f"  {status:12} {count:4d}")


def cmd_list(args):
    """List all doc_ids."""
    registry = DocIDRegistry()
    
    docs = registry.data['docs']
    
    if args.category:
        docs = [d for d in docs if d['category'] == args.category.lower()]
    
    print(f"\n📋 {len(docs)} doc_id(s):\n")
    
    for doc in sorted(docs, key=lambda d: d['doc_id']):
        print(f"  {doc['doc_id']:<40} {doc['category']:10} {doc['status']:10}")


def main():
    parser = argparse.ArgumentParser(
        description="DOC_ID Registry CLI - Manage repository documentation identifiers"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Mint command
    mint_parser = subparsers.add_parser('mint', help='Mint a new doc_id')
    mint_parser.add_argument('--category', required=True, help='Category (core, error, patterns, etc.)')
    mint_parser.add_argument('--name', required=True, help='Name segments (e.g., orchestrator)')
    mint_parser.add_argument('--title', help='Human-readable title')
    mint_parser.add_argument('--artifact', action='append', help='Artifact spec (type:path)')
    mint_parser.add_argument('--tags', help='Comma-separated tags')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for doc_ids')
    search_parser.add_argument('--pattern', help='Regex pattern to match')
    search_parser.add_argument('--category', help='Filter by category')
    search_parser.add_argument('--status', help='Filter by status')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate all doc_ids')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all doc_ids')
    list_parser.add_argument('--category', help='Filter by category')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'mint': cmd_mint,
        'search': cmd_search,
        'validate': cmd_validate,
        'stats': cmd_stats,
        'list': cmd_list
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main() or 0)
